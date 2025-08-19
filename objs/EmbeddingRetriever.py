import os
import json
import pickle
import hashlib
import numpy as np
import faiss
from tqdm import tqdm
from sklearn.neighbors import NearestNeighbors
from typing import Union, List
from openai import OpenAI

class EmbeddingRetriever:
    """
    统一接口支持 OpenAI 嵌入模型（包括通过OpenAI接口调用Ollama）
    """

    def __init__(
            self,
            embedding_model: str,
            openai_api_key: str = None,
            openai_api_base: str = None
    ):
        self.embedding_model = embedding_model
        self.openai_api_key = openai_api_key
        self.openai_api_base = openai_api_base
        self.client = OpenAI(base_url=self.openai_api_base, api_key=self.openai_api_key)
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        for text in tqdm(texts, desc='OpenAI embedding', ncols=80):
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model,
            )
            embeddings.append(response.data[0].embedding)
        return np.array(embeddings, dtype=np.float32)
    
    def generate_text(self, messages, model="qwen2.5:7b", temperature=0.1):
        """
        调用大模型生成文本（用于智能判断）
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"大模型调用失败: {e}")
            return f"模型调用失败: {str(e)}"

    def generate_text_stream(self, messages, model="qwen2.5:7b", temperature=0.1):
        """
        调用大模型生成文本（流式输出）
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"模型调用失败: {str(e)}"
