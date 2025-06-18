#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""向量存储实现"""
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    
import os
import json
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import time

from src.utils import logger

class MockVectorStore:
    """
    简单的内存向量存储，用于在没有faiss库的情况下进行测试
    """
    
    def __init__(self, dimension=768):
        """初始化内存向量存储"""
        self.texts = []
        self.vectors = []
        self.metadatas = []
        self.dimension = dimension
        logger.info(f"初始化模拟向量存储，维度: {dimension}")
    
    def add(self, texts, vectors, metadatas=None):
        """添加向量到存储"""
        if not texts or not vectors:
            return
            
        if metadatas is None:
            metadatas = [{} for _ in texts]
            
        # 验证维度
        for i, vec in enumerate(vectors):
            if len(vec) != self.dimension:
                logger.warning(f"向量{i}维度不匹配: {len(vec)} != {self.dimension}，将调整")
                # 调整向量维度
                if len(vec) < self.dimension:
                    # 扩展向量
                    vectors[i] = vec + [0.0] * (self.dimension - len(vec))
                else:
                    # 截断向量
                    vectors[i] = vec[:self.dimension]
        
        # 添加到存储
        self.texts.extend(texts)
        self.vectors.extend(vectors)
        self.metadatas.extend(metadatas)
        
        logger.info(f"添加了{len(texts)}个向量到存储")
    
    def search(self, query_vector, top_k=5):
        """搜索向量"""
        if not self.vectors or not query_vector:
            return []
            
        # 计算余弦相似度
        similarities = []
        for i, vec in enumerate(self.vectors):
            similarity = self._cosine_similarity(query_vector, vec)
            similarities.append((i, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前top_k个结果
        results = []
        for i in range(min(top_k, len(similarities))):
            idx, score = similarities[i]
            results.append({
                "text": self.texts[idx],
                "score": float(score),
                "metadata": self.metadatas[idx]
            })
            
        return results
    
    def _cosine_similarity(self, vec1, vec2):
        """计算余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def delete(self, ids):
        """删除向量"""
        if not ids:
            return
            
        to_delete = set()
        for i, metadata in enumerate(self.metadatas):
            if metadata.get("id") in ids:
                to_delete.add(i)
                
        # 从后向前删除，避免索引变化
        for i in sorted(to_delete, reverse=True):
            del self.texts[i]
            del self.vectors[i]
            del self.metadatas[i]
            
        logger.info(f"删除了{len(to_delete)}个向量")
    
    def save(self, path):
        """保存向量存储"""
        # 创建目录
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # 保存到JSON文件
        data = {
            "texts": self.texts,
            "vectors": self.vectors,
            "metadatas": self.metadatas,
            "dimension": self.dimension
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
            
        logger.info(f"保存了{len(self.texts)}个向量到{path}")
    
    def load(self, path):
        """加载向量存储"""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self.texts = data.get("texts", [])
            self.vectors = data.get("vectors", [])
            self.metadatas = data.get("metadatas", [])
            self.dimension = data.get("dimension", self.dimension)
            
            logger.info(f"加载了{len(self.texts)}个向量从{path}")
    
    def close(self):
        """关闭向量存储"""
        # 清空数据
        self.texts = []
        self.vectors = []
        self.metadatas = []


class VectorStore:
    """
    高性能向量存储实现，支持语义相似度搜索
    使用SQLite作为底层存储，支持HNSW索引
    """
    
    def __init__(self, db_path: str, dimension: int = 768, index_type: str = "hnsw"):
        """
        初始化向量存储
        
        Args:
            db_path: 数据库路径
            dimension: 向量维度
            index_type: 索引类型，目前支持'hnsw'
        """
        self.db_path = db_path
        self.dimension = dimension
        self.index_type = index_type
        self.initialized = False
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化数据库
        self._init_db()
        
        logger.info(f"向量存储初始化完成，维度: {dimension}, 索引类型: {index_type}")
    
    def add(self, texts: List[str], embeddings: List[List[float]], 
           metadata: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        添加文本及其嵌入向量到存储
        
        Args:
            texts: 文本列表
            embeddings: 嵌入向量列表
            metadata: 元数据列表
            
        Returns:
            List[str]: 添加的文档ID列表
        """
        if not texts or not embeddings:
            return []
            
        if len(texts) != len(embeddings):
            raise ValueError(f"文本数量({len(texts)})和嵌入向量数量({len(embeddings)})不匹配")
            
        if metadata and len(texts) != len(metadata):
            raise ValueError(f"文本数量({len(texts)})和元数据数量({len(metadata)})不匹配")
        
        # 确保元数据不为None
        if not metadata:
            metadata = [{} for _ in texts]
        
        # 执行添加操作
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            document_ids = []
            
            for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
                # 检查嵌入向量维度
                if len(embedding) != self.dimension:
                    logger.warning(f"嵌入向量维度 {len(embedding)} 不匹配预期维度 {self.dimension}，跳过")
                    continue
                
                # 生成文档ID
                doc_id = f"doc_{int(time.time())}_{i}"
                
                # 存储文本和元数据
                cur.execute(
                    "INSERT INTO documents (id, text, metadata) VALUES (?, ?, ?)",
                    (doc_id, text, json.dumps(meta))
                )
                
                # 存储向量
                embedding_blob = self._vector_to_blob(embedding)
                cur.execute(
                    "INSERT INTO vectors (document_id, embedding) VALUES (?, ?)",
                    (doc_id, embedding_blob)
                )
                
                document_ids.append(doc_id)
            
            # 提交事务
            conn.commit()
            
            # 如果新增文档较多，重建索引
            if len(document_ids) > 100:
                self._rebuild_index(conn)
                
            logger.info(f"成功添加 {len(document_ids)} 条向量记录")
            return document_ids
        except Exception as e:
            conn.rollback()
            logger.error(f"添加向量记录失败: {str(e)}")
            return []
        finally:
            conn.close()
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        根据查询向量搜索最相似的文档
        
        Args:
            query_vector: 查询向量
            top_k: 返回的最大结果数
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        if len(query_vector) != self.dimension:
            raise ValueError(f"查询向量维度 {len(query_vector)} 不匹配预期维度 {self.dimension}")
        
        conn = self._get_connection()
        
        try:
            # 如果启用了HNSW索引，使用索引搜索
            if self.index_type == "hnsw" and self._check_index_exists():
                results = self._search_with_index(conn, query_vector, top_k)
            else:
                # 否则使用暴力搜索
                results = self._search_brute_force(conn, query_vector, top_k)
            
            # 格式化结果
            formatted_results = []
            for result in results:
                doc_id, text, metadata_str, score = result
                metadata = json.loads(metadata_str)
                formatted_results.append({
                    "id": doc_id,
                    "text": text,
                    "metadata": metadata,
                    "score": score
                })
                
            return formatted_results
        finally:
            conn.close()
    
    def search_by_text(self, query_text: str, embedding_function, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        通过文本搜索相似文档
        
        Args:
            query_text: 查询文本
            embedding_function: 嵌入函数，将文本转换为向量
            top_k: 返回的最大结果数
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        # 使用嵌入函数生成查询向量
        query_vector = embedding_function(query_text)
        if isinstance(query_vector, list) and len(query_vector) > 0 and isinstance(query_vector[0], list):
            query_vector = query_vector[0]  # 处理嵌套列表情况
        
        # 使用向量搜索
        return self.search(query_vector, top_k)
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定ID的文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            Optional[Dict[str, Any]]: 文档数据，如果不存在则返回None
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # 查询文档
            cur.execute(
                "SELECT id, text, metadata FROM documents WHERE id = ?",
                (doc_id,)
            )
            
            result = cur.fetchone()
            if not result:
                return None
                
            doc_id, text, metadata_str = result
            metadata = json.loads(metadata_str)
            
            return {
                "id": doc_id,
                "text": text,
                "metadata": metadata
            }
        finally:
            conn.close()
    
    def delete(self, doc_id: str) -> bool:
        """
        删除指定ID的文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            bool: 是否删除成功
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # 删除向量记录
            cur.execute("DELETE FROM vectors WHERE document_id = ?", (doc_id,))
            
            # 删除文档记录
            cur.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            
            # 提交事务
            conn.commit()
            
            return cur.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"删除文档失败: {str(e)}")
            return False
        finally:
            conn.close()
    
    def clear(self) -> bool:
        """
        清空所有数据
        
        Returns:
            bool: 是否清空成功
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # 清空表
            cur.execute("DELETE FROM vectors")
            cur.execute("DELETE FROM documents")
            
            # 提交事务
            conn.commit()
            
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"清空数据失败: {str(e)}")
            return False
        finally:
            conn.close()
    
    def count(self) -> int:
        """
        获取记录总数
        
        Returns:
            int: 记录总数
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT COUNT(*) FROM documents")
            return cur.fetchone()[0]
        finally:
            conn.close()
    
    def optimize(self) -> bool:
        """
        优化存储，重建索引
        
        Returns:
            bool: 是否优化成功
        """
        conn = self._get_connection()
        
        try:
            self._rebuild_index(conn)
            return True
        except Exception as e:
            logger.error(f"优化存储失败: {str(e)}")
            return False
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取存储统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # 记录总数
            cur.execute("SELECT COUNT(*) FROM documents")
            doc_count = cur.fetchone()[0]
            
            # 数据库文件大小
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            # 索引信息
            index_status = "已创建" if self._check_index_exists() else "未创建"
            
            return {
                "document_count": doc_count,
                "database_size_bytes": db_size,
                "vector_dimension": self.dimension,
                "index_type": self.index_type,
                "index_status": index_status
            }
        finally:
            conn.close()
    
    def _init_db(self) -> None:
        """初始化数据库表结构"""
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # 创建文档表
            cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 创建向量表
            cur.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                document_id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
            """)
            
            # 创建版本管理表
            cur.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """)
            
            # 记录数据库架构版本
            cur.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("schema_version", "1.0")
            )
            
            # 记录向量维度
            cur.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("vector_dimension", str(self.dimension))
            )
            
            # 提交事务
            conn.commit()
            
            # 标记为已初始化
            self.initialized = True
        finally:
            conn.close()
    
    def _vector_to_blob(self, vector: List[float]) -> bytes:
        """将向量转换为二进制数据"""
        return np.array(vector, dtype=np.float32).tobytes()
    
    def _blob_to_vector(self, blob: bytes) -> List[float]:
        """将二进制数据转换为向量"""
        return np.frombuffer(blob, dtype=np.float32).tolist()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
        return conn
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        vec1 = np.array(vec1, dtype=np.float32)
        vec2 = np.array(vec2, dtype=np.float32)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
            
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def _check_index_exists(self) -> bool:
        """检查索引是否存在"""
        # 目前仅实现了暴力搜索，未实现真正的索引
        # 在实际项目中，这里应该检查HNSW索引是否存在
        return False
    
    def _rebuild_index(self, conn: sqlite3.Connection) -> None:
        """重建索引"""
        # 目前仅实现了暴力搜索，未实现真正的索引
        # 在实际项目中，这里应该构建HNSW索引
        pass
    
    def _search_with_index(self, conn: sqlite3.Connection, query_vector: List[float], top_k: int) -> List[Tuple]:
        """使用索引搜索"""
        # 由于当前未实现真正的索引，使用暴力搜索代替
        return self._search_brute_force(conn, query_vector, top_k)
    
    def _search_brute_force(self, conn: sqlite3.Connection, query_vector: List[float], top_k: int) -> List[Tuple]:
        """暴力搜索最相似向量"""
        cur = conn.cursor()
        
        # 获取所有向量
        cur.execute("""
        SELECT v.document_id, d.text, d.metadata, v.embedding
        FROM vectors v
        JOIN documents d ON v.document_id = d.id
        """)
        
        results = []
        for row in cur.fetchall():
            doc_id, text, metadata_str, embedding_blob = row
            
            # 将二进制数据转换为向量
            embedding = self._blob_to_vector(embedding_blob)
            
            # 计算相似度
            score = self._cosine_similarity(query_vector, embedding)
            
            results.append((doc_id, text, metadata_str, score))
        
        # 按相似度排序并返回前top_k个结果
        results.sort(key=lambda x: x[3], reverse=True)
        return results[:top_k] 