import hashlib
import os
import json
import pickle
import numpy as np
import faiss
from tqdm import tqdm
from sklearn.neighbors import NearestNeighbors
from typing import Union, List
from openai import OpenAI
from .EmbeddingRetriever import EmbeddingRetriever
from .FileManager import FileManager

class PlanAuditor:
    """
    施工方案审核器，使用OpenAI接口进行文本嵌入和检索
    """

    def __init__(
            self,
            plan_content: str,
            check_list_file: str,
            embedding_model: str = "text-embedding-3-small",
            openai_api_key: str = None,
            openai_api_base: str = None,
            cache_dir: str = "./cache",
            original_filename: str = None
    ):
        self.plan_content = plan_content
        self.check_list_file = check_list_file
        self.cache_dir = cache_dir
        self.original_filename = original_filename
        self.embedding_model = embedding_model

        # 初始化文件管理器
        self.file_manager = FileManager(cache_dir)

        # 初始化嵌入器
        self.embedder = EmbeddingRetriever(
            embedding_model=embedding_model,
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base
        )

        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)

        # 加载检查项
        self.check_items = self.load_check_items()

        # 初始化嵌入
        self.chunks = []
        self.chunk_embeddings = None
        self.faiss_index = None
        self.file_hash = None

    def load_check_items(self):
        """
        读取 JSONL 文件，返回包含所有检查项的列表，每个检查项为一个字典
        """
        items = []
        with open(self.check_list_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line.strip())
                    items.append(item)
        return items

    def get_hash(self):
        """用文件名和内容 hash 区分不同方案文本"""
        if self.file_hash is None:
            filename = self.original_filename or "unknown_file"
            self.file_hash = self.file_manager.generate_file_hash(filename, self.plan_content)
        return self.file_hash

    def split_text(self, text, max_length=300):
        """将文本分割成块，增加错误处理"""
        import re
        
        # 检查输入文本
        if not text or not text.strip():
            return ["空文档"]
        
        try:
            # 按句子分割
            sentences = re.split(r'(?<=[。！？\.\!\?])', text)
            
            # 过滤空句子
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return [text.strip()]
            
            chunks, chunk = [], ""
            for sent in sentences:
                # 检查单个句子是否过长
                if len(sent) > max_length:
                    # 如果当前chunk不为空，先添加到chunks
                    if chunk:
                        chunks.append(chunk.strip())
                        chunk = ""
                    # 将长句子按字符强制分割
                    for i in range(0, len(sent), max_length):
                        chunks.append(sent[i:i+max_length])
                else:
                    # 正常处理
                    if len(chunk) + len(sent) > max_length and chunk:
                        chunks.append(chunk.strip())
                        chunk = ""
                    chunk += sent
            
            # 添加最后一个chunk
            if chunk and chunk.strip():
                chunks.append(chunk.strip())
            
            # 确保至少有一个chunk
            if not chunks:
                chunks = [text[:max_length] if len(text) > max_length else text]
            
            return chunks
            
        except Exception as e:
            print(f"文本分割错误: {e}")
            # 降级处理：按固定长度分割
            if len(text) <= max_length:
                return [text]
            else:
                chunks = []
                for i in range(0, len(text), max_length):
                    chunks.append(text[i:i+max_length])
                return chunks

    def build_or_load_embeddings(self, use_cache=True):
        """
        构建或加载文本嵌入，使用新的文件夹结构
        """
        hash_prefix = self.get_hash()
        
        # 检查是否有现有映射信息
        file_info = self.file_manager.get_file_info(hash_prefix)
        if file_info:
            # 使用文件映射中的路径
            cache_files = file_info.get("cache_files", {})
            chunk_file = cache_files.get("chunks")
            emb_file = cache_files.get("embeddings")
            faiss_file = cache_files.get("faiss_index")
        else:
            # 创建新的文档文件夹结构
            doc_folder = os.path.join(self.cache_dir, hash_prefix)
            os.makedirs(doc_folder, exist_ok=True)
            
            chunk_file = os.path.join(doc_folder, "chunks.txt")
            emb_file = os.path.join(doc_folder, "embeddings.npy")
            faiss_file = os.path.join(doc_folder, "faiss.idx")

        # 检查缓存
        if use_cache and chunk_file and emb_file and faiss_file and \
           os.path.exists(chunk_file) and os.path.exists(emb_file) and os.path.exists(faiss_file):
            print(f"加载嵌入缓存: {hash_prefix}")
            self.load_embeddings(chunk_file, emb_file, faiss_file)
            return hash_prefix

        print("首次生成嵌入...")
        # 分割文本
        self.chunks = self.split_text(self.plan_content)
        print(f"共分割为 {len(self.chunks)} 个文本块")

        if not self.chunks:
            raise ValueError("文本分割失败，没有生成任何文本块")

        # 生成嵌入
        print("文本块嵌入中...")
        self.chunk_embeddings = self.embedder.encode(self.chunks)

        # 构建 FAISS 索引
        dim = self.chunk_embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dim)
        # 确保嵌入向量是正确的数据类型和连续性
        embeddings_float32 = np.ascontiguousarray(self.chunk_embeddings.astype(np.float32))
        print(f"嵌入向量形状: {embeddings_float32.shape}, 数据类型: {embeddings_float32.dtype}")
        self.faiss_index.add(embeddings_float32)

        # 确保目录存在（如果是新文件）
        if chunk_file:
            os.makedirs(os.path.dirname(chunk_file), exist_ok=True)
            
        # 保存到缓存
        self.save_embeddings(chunk_file, emb_file, faiss_file)
        
        # 添加文件映射（如果还没有）
        if self.original_filename and not file_info:
            hash_prefix = self.file_manager.add_file_mapping(
                original_filename=self.original_filename,
                plan_content=self.plan_content,
                embedding_model=self.embedding_model,
                chunks_count=len(self.chunks)
            )
        
        print("嵌入保存成功。")
        return hash_prefix

    def save_embeddings(self, chunk_file, emb_file, faiss_file):
        """保存嵌入到文件"""
        # 保存 chunk 文本
        with open(chunk_file, "w", encoding="utf-8") as f:
            for c in self.chunks:
                f.write(c.replace("\n", " ") + "\n")
        # 保存 embedding
        np.save(emb_file, self.chunk_embeddings)
        # 保存 faiss index
        faiss.write_index(self.faiss_index, faiss_file)

    def load_embeddings(self, chunk_file, emb_file, faiss_file):
        """从文件加载嵌入"""
        # 加载 chunk 文本
        with open(chunk_file, "r", encoding="utf-8") as f:
            self.chunks = [line.strip() for line in f if line.strip()]
        # 加载 embedding
        self.chunk_embeddings = np.load(emb_file)
        # 加载 faiss index
        self.faiss_index = faiss.read_index(faiss_file)

    def search_similar_chunks(self, query: str, top_k: int = 5):
        """
        根据查询检索最相似的文本块
        """
        if self.faiss_index is None:
            raise ValueError("请先调用 build_or_load_embeddings() 初始化嵌入")

        query_vec = self.embedder.encode([query])
        distances, indices = self.faiss_index.search(query_vec, top_k)

        results = []
        for i in range(top_k):
            if i < len(indices[0]):
                idx = indices[0][i]
                distance = distances[0][i]
                similarity = 1 / (1 + distance)  # 转换为相似度
                results.append({
                    "text": self.chunks[idx],
                    "index": int(idx),
                    "similarity": float(similarity),
                    "distance": float(distance)
                })
        return results

    def response_user_query(self, query: str, top_k: int = 5):
        """
        根据查询条件，从方案文本中检索出相关的内容
        """
        results = self.search_similar_chunks(query, top_k)
        return results

    def check_category_scenario(self, category: str, scenario: str, top_k: int = 5):
        """
        根据类别和场景，检索相关的检查项和方案内容
        """
        # 组合查询
        combined_query = f"类别：{category} 场景：{scenario}"

        # 从方案内容中检索
        plan_results = self.search_similar_chunks(combined_query, top_k)

        # 从检查项中检索相关项
        relevant_checks = []
        for item in self.check_items:
            # 假设检查项有 category 和 scenario 字段
            if (category.lower() in str(item).lower() or
                    scenario.lower() in str(item).lower()):
                relevant_checks.append(item)

        return {
            "plan_content": plan_results,
            "check_items": relevant_checks[:top_k]
        }

    def generate_with_retrieval(self, query: str, gen_model_api, top_k: int = 5):
        """
        结合检索结果生成回答
        """
        context_chunks = self.search_similar_chunks(query, top_k)
        context = "\n".join([c["text"] for c in context_chunks])
        result = gen_model_api(query, context)
        return result
