#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件映射管理器
管理上传文件名与嵌入缓存的对应关系
"""
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

class FileManager:
    """文件映射管理器"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = cache_dir
        self.mapping_file = os.path.join(cache_dir, "file_mapping.json")
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 加载现有映射
        self.mappings = self._load_mappings()
        
        # 迁移旧格式缓存文件
        self.migrate_old_cache_format()
    
    def _load_mappings(self) -> Dict:
        """加载文件映射"""
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载文件映射失败: {e}")
                return {}
        return {}
    
    def _save_mappings(self):
        """保存文件映射"""
        os.makedirs(self.cache_dir, exist_ok=True)
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.mappings, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存文件映射失败: {e}")
    
    def generate_file_hash(self, filename: str, content: str) -> str:
        """生成文件hash，结合文件名和内容"""
        combined = f"{filename}_{content}"
        return hashlib.md5(combined.encode("utf-8")).hexdigest()[:12]
    
    def add_file_mapping(self, original_filename: str, plan_content: str, 
                        embedding_model: str, chunks_count: int) -> str:
        """添加文件映射，为每个文档创建独立文件夹"""
        file_hash = self.generate_file_hash(original_filename, plan_content)
        
        # 创建文档专用文件夹
        doc_folder = os.path.join(self.cache_dir, file_hash)
        os.makedirs(doc_folder, exist_ok=True)
        
        mapping_info = {
            "original_filename": original_filename,
            "file_hash": file_hash,
            "upload_time": datetime.now().isoformat(),
            "text_length": len(plan_content),
            "chunks_count": chunks_count,
            "embedding_model": embedding_model,
            "doc_folder": doc_folder,
            "cache_files": {
                "chunks": os.path.join(doc_folder, "chunks.txt"),
                "embeddings": os.path.join(doc_folder, "embeddings.npy"),
                "faiss_index": os.path.join(doc_folder, "faiss.idx"),
                "metadata": os.path.join(doc_folder, "metadata.json")
            }
        }
        
        # 保存元数据到文档文件夹
        metadata = {
            "original_filename": original_filename,
            "file_hash": file_hash,
            "upload_time": mapping_info["upload_time"],
            "text_length": len(plan_content),
            "chunks_count": chunks_count,
            "embedding_model": embedding_model,
            "content_preview": plan_content[:500] + "..." if len(plan_content) > 500 else plan_content
        }
        
        metadata_path = mapping_info["cache_files"]["metadata"]
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存元数据失败: {e}")
        
        self.mappings[file_hash] = mapping_info
        self._save_mappings()
        
        return file_hash
    
    def get_file_info(self, file_hash: str) -> Optional[Dict]:
        """获取文件信息"""
        return self.mappings.get(file_hash)
    
    def get_all_files(self) -> List[Dict]:
        """获取所有文件列表"""
        return list(self.mappings.values())
    
    def delete_file_mapping(self, file_hash: str) -> bool:
        """删除文件映射和相关缓存文件夹"""
        if file_hash not in self.mappings:
            return False
        
        mapping_info = self.mappings[file_hash]
        
        # 删除整个文档文件夹
        doc_folder = mapping_info.get("doc_folder")
        if doc_folder and os.path.exists(doc_folder):
            try:
                import shutil
                shutil.rmtree(doc_folder)
                print(f"删除文档文件夹: {doc_folder}")
            except OSError as e:
                print(f"删除文档文件夹失败: {e}")
                # 如果删除文件夹失败，尝试删除单个文件
                for cache_type, file_path in mapping_info.get("cache_files", {}).items():
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            print(f"删除缓存文件: {file_path}")
                        except OSError as e2:
                            print(f"删除缓存文件失败: {e2}")
        
        # 删除映射记录
        del self.mappings[file_hash]
        self._save_mappings()
        
        return True
    
    def find_by_filename(self, filename: str) -> Optional[Dict]:
        """根据文件名查找映射"""
        for file_hash, info in self.mappings.items():
            if info.get("original_filename") == filename:
                return info
        return None
    
    def cleanup_orphaned_cache(self):
        """清理孤立的缓存文件和文件夹"""
        if not os.path.exists(self.cache_dir):
            return
        
        # 获取所有有效的文档hash
        valid_hashes = set(self.mappings.keys())
        
        # 检查缓存目录中的内容
        for item in os.listdir(self.cache_dir):
            if item == "file_mapping.json":
                continue
            
            item_path = os.path.join(self.cache_dir, item)
            
            # 如果是文件夹且不在有效hash列表中，删除它
            if os.path.isdir(item_path) and item not in valid_hashes:
                try:
                    import shutil
                    shutil.rmtree(item_path)
                    print(f"清理孤立缓存文件夹: {item_path}")
                except OSError as e:
                    print(f"清理文件夹失败: {e}")
            
            # 如果是文件且不是映射文件，也删除它（兼容旧格式）
            elif os.path.isfile(item_path):
                # 检查是否是旧格式的缓存文件
                is_old_cache = any(
                    item.startswith(hash_val) and 
                    (item.endswith('_chunks.txt') or 
                     item.endswith('_embeds.npy') or 
                     item.endswith('_faiss.idx'))
                    for hash_val in valid_hashes
                )
                
                if not is_old_cache:
                    try:
                        os.remove(item_path)
                        print(f"清理孤立缓存文件: {item_path}")
                    except OSError as e:
                        print(f"清理文件失败: {e}")
    
    def migrate_old_cache_format(self):
        """迁移旧的缓存格式到新的文件夹结构"""
        if not os.path.exists(self.cache_dir):
            return
        
        print("检查是否需要迁移旧的缓存格式...")
        
        # 查找旧格式的文件
        old_files = {}
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path) and filename != "file_mapping.json":
                # 检查是否是旧格式的缓存文件
                if '_chunks.txt' in filename:
                    hash_val = filename.replace('_chunks.txt', '')
                    if hash_val not in old_files:
                        old_files[hash_val] = {}
                    old_files[hash_val]['chunks'] = file_path
                elif '_embeds.npy' in filename:
                    hash_val = filename.replace('_embeds.npy', '')
                    if hash_val not in old_files:
                        old_files[hash_val] = {}
                    old_files[hash_val]['embeddings'] = file_path
                elif '_faiss.idx' in filename:
                    hash_val = filename.replace('_faiss.idx', '')
                    if hash_val not in old_files:
                        old_files[hash_val] = {}
                    old_files[hash_val]['faiss'] = file_path
        
        # 迁移旧文件到新文件夹结构
        for hash_val, files in old_files.items():
            if hash_val in self.mappings:
                doc_folder = os.path.join(self.cache_dir, hash_val)
                os.makedirs(doc_folder, exist_ok=True)
                
                # 移动文件
                for file_type, old_path in files.items():
                    if file_type == 'chunks':
                        new_path = os.path.join(doc_folder, 'chunks.txt')
                    elif file_type == 'embeddings':
                        new_path = os.path.join(doc_folder, 'embeddings.npy')
                    elif file_type == 'faiss':
                        new_path = os.path.join(doc_folder, 'faiss.idx')
                    else:
                        continue
                    
                    try:
                        import shutil
                        shutil.move(old_path, new_path)
                        print(f"迁移文件: {old_path} -> {new_path}")
                    except OSError as e:
                        print(f"迁移文件失败: {e}")
                
                # 更新映射信息
                mapping_info = self.mappings[hash_val]
                mapping_info["doc_folder"] = doc_folder
                mapping_info["cache_files"] = {
                    "chunks": os.path.join(doc_folder, "chunks.txt"),
                    "embeddings": os.path.join(doc_folder, "embeddings.npy"),
                    "faiss_index": os.path.join(doc_folder, "faiss.idx"),
                    "metadata": os.path.join(doc_folder, "metadata.json")
                }
        
        if old_files:
            self._save_mappings()
            print(f"迁移完成，共处理 {len(old_files)} 个文档的缓存文件") 