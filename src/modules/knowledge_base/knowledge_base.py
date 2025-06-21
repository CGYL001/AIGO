#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识库模块 - 提供文档管理和向量检索功能
"""

import os
import json
import shutil
import uuid
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path

from src.utils import logger
from src.modules.knowledge_base.storage.vector_store import VectorStore
from src.modules.knowledge_base.storage.metadata_store import MetadataStore
from src.services import ModelServiceFactory

class KnowledgeBase:
    """知识库类，提供文档管理和向量检索功能"""
    
    def __init__(self, config=None, embedding_model=None):
        """
        初始化知识库
        
        参数:
            config: 配置参数
            embedding_model: 嵌入模型名称
        """
        self.config = config or {}
        self.vector_store = None
        self.metadata_store = None
        self.embedding_model = None
        self.chunk_size = self.config.get("chunk_size", 500)
        self.chunk_overlap = self.config.get("chunk_overlap", 100)
        self.embedding_model_name = embedding_model
        
        # 初始化嵌入模型
        self._init_embedding_model()
        
    def _init_embedding_model(self):
        """初始化嵌入模型"""
        try:
            # 创建模型服务
            model_service = ModelServiceFactory.create_service()
            
            # 如果指定了嵌入模型名称，记录信息
            if self.embedding_model_name:
                logger.info(f"使用指定的嵌入模型: {self.embedding_model_name}")
            
            # 直接使用模型服务，不调用可能不存在的方法
            self.embedding_model = model_service
                
        except Exception as e:
            logger.warning(f"初始化嵌入模型失败: {e}")
            self.embedding_model = None
    
    def init_vector_store(self, kb_path: str, dimension: int = 768) -> bool:
        """
        初始化向量存储和元数据存储
        
        参数:
            kb_path: 知识库路径
            dimension: 向量维度
            
        返回:
            是否成功初始化
        """
        try:
            # 确保目录存在
            os.makedirs(kb_path, exist_ok=True)
            
            # 初始化向量存储
            vector_db_path = os.path.join(kb_path, "vector_store.sqlite")
            self.vector_store = VectorStore(vector_db_path, dimension=dimension)
            
            # 初始化元数据存储
            metadata_db_path = os.path.join(kb_path, "metadata_store.sqlite")
            self.metadata_store = MetadataStore(metadata_db_path)
            
            logger.info(f"已初始化知识库: {kb_path}")
            return True
        except Exception as e:
            logger.error(f"初始化知识库失败: {e}")
            return False
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        获取文本的嵌入向量
        
        参数:
            texts: 文本列表
            
        返回:
            嵌入向量列表
        """
        if not texts:
            return []
            
        try:
            if self.embedding_model:
                embeddings = self.embedding_model.embed(texts)
                
                # 检查维度是否匹配
                dimension = self.config.get("embedding_dimension", 384)
                if embeddings and len(embeddings[0]) != dimension:
                    logger.warning(f"嵌入向量维度 {len(embeddings[0])} 不匹配预期维度 {dimension}，使用随机向量")
                    # 返回与预期维度匹配的随机向量
                    return [list(np.random.uniform(-1, 1, dimension)) for _ in texts]
                
                return embeddings
            else:
                # 生成随机向量（测试用）
                dimension = self.config.get("embedding_dimension", 384)
                return [list(np.random.uniform(-1, 1, dimension)) for _ in texts]
        except Exception as e:
            logger.error(f"获取嵌入向量失败: {e}")
            # 返回随机向量
            dimension = self.config.get("embedding_dimension", 384)
            return [list(np.random.uniform(-1, 1, dimension)) for _ in texts]
    
    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        将文本分块
        
        参数:
            text: 要分块的文本
            chunk_size: 块大小（字符数）
            overlap: 重叠大小（字符数）
            
        返回:
            文本块列表
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        if len(text) <= chunk_size:
            return [text]
            
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks
    
    def add_document(self, file_path: str, metadata: Dict = None) -> bool:
        """
        添加文档到知识库
        
        参数:
            file_path: 文档路径
            metadata: 元数据
            
        返回:
            是否成功添加
        """
        # 这里应该添加文档解析逻辑，根据文件类型不同调用不同的解析器
        # 例如：PDF、Word、Markdown等
        # 简化版：直接读取文本
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 更新元数据
            doc_metadata = metadata or {}
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_path)[1][1:]  # 获取文件扩展名
            
            # 生成文档ID
            doc_id = doc_metadata.get("id", f"doc_{uuid.uuid4().hex[:8]}")
            
            doc_metadata.update({
                "id": doc_id,
                "source": file_path,
                "type": file_ext,
                "title": file_name,
                "description": f"从{file_path}导入的{file_ext}文档"
            })
            
            # 添加文档元数据
            if self.metadata_store:
                self.metadata_store.add_document(doc_id, doc_metadata)
            
            # 添加文本
            return self.add_text(text, doc_metadata)
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False
    
    def add_text(self, text: str, metadata: Dict = None) -> bool:
        """
        添加文本到知识库
        
        参数:
            text: 要添加的文本
            metadata: 元数据
            
        返回:
            是否成功添加
        """
        if not self.vector_store:
            logger.error("向量存储未初始化")
            return False
            
        try:
            # 确保有文档ID
            metadata = metadata or {}
            doc_id = metadata.get("id", f"doc_{uuid.uuid4().hex[:8]}")
            metadata["id"] = doc_id
            
            # 添加文档元数据（如果尚未添加）
            if self.metadata_store and not metadata.get("_skip_doc_metadata", False):
                self.metadata_store.add_document(doc_id, metadata)
            
            # 分块
            chunks = self._chunk_text(text)
            
            # 获取嵌入向量
            embeddings = self._get_embeddings(chunks)
            
            # 创建元数据列表和添加块元数据
            metadatas = []
            for i, chunk in enumerate(chunks):
                # 为每个块创建唯一ID
                chunk_id = f"{doc_id}_chunk_{i}"
                
                # 创建块元数据
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "id": chunk_id,
                    "document_id": doc_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                
                # 添加到元数据存储
                if self.metadata_store:
                    self.metadata_store.add_chunk(
                        chunk_id=chunk_id,
                        doc_id=doc_id,
                        text=chunk,
                        chunk_index=i,
                        total_chunks=len(chunks),
                        metadata=chunk_metadata
                    )
                
                metadatas.append(chunk_metadata)
            
            # 添加到向量存储
            self.vector_store.add(chunks, embeddings, metadatas)
            logger.info(f"添加了文档(ID:{doc_id})，共{len(chunks)}个文本块")
            return True
        except Exception as e:
            logger.error(f"添加文本失败: {e}")
            return False
    
    def search(self, query: str, limit: int = 5, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """搜索文档
        
        Args:
            query: 查询文本
            limit: 返回结果数量限制
            filter_criteria: 过滤条件
        
        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        if not self.vector_store:
            logger.warning("向量存储未初始化，无法搜索")
            return []
        
        try:
            # 获取查询向量
            query_embedding = self._get_embeddings([query])[0]
            
            # 使用向量存储搜索，移除filter_criteria参数
            results = self.vector_store.search(query_embedding, top_k=limit)
            
            # 如果有元数据存储，补充元数据信息
            if self.metadata_store:
                for result in results:
                    chunk_id = result.get("id")
                    if chunk_id:
                        chunk_metadata = self.metadata_store.get_chunk(chunk_id)
                        if chunk_metadata:
                            result.update(chunk_metadata)
            
            # 应用过滤条件
            if filter_criteria:
                filtered_results = []
                for result in results:
                    if all(result.get(k) == v or result.get("metadata", {}).get(k) == v for k, v in filter_criteria.items()):
                        filtered_results.append(result)
                results = filtered_results
            
            logger.info(f"查询: '{query}'，找到 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"搜索文档失败: {str(e)}")
            return []
    
    def delete(self, ids: List[str]) -> bool:
        """
        删除知识库中的文档或块
        
        参数:
            ids: 文档或块ID列表
            
        返回:
            是否成功删除
        """
        if not self.vector_store:
            logger.error("向量存储未初始化")
            return False
            
        try:
            # 删除向量存储中的数据
            self.vector_store.delete(ids)
            
            # 删除元数据存储中的数据
            if self.metadata_store:
                for id_str in ids:
                    # 尝试作为文档ID删除
                    self.metadata_store.delete_document(id_str)
                    
                    # 尝试作为块ID删除
                    self.metadata_store.delete_chunk(id_str)
                    
            return True
        except Exception as e:
            logger.error(f"删除知识库数据失败: {e}")
            return False
    
    def save(self, path: str) -> bool:
        """
        保存知识库
        
        参数:
            path: 保存路径
            
        返回:
            是否成功保存
        """
        try:
            # 确保目录存在
            os.makedirs(path, exist_ok=True)
            
            # 保存向量存储
            if self.vector_store:
                vector_db_path = os.path.join(path, "vector_store.sqlite")
                self.vector_store.save(vector_db_path)
                
            # 保存元数据存储
            if self.metadata_store:
                metadata_db_path = os.path.join(path, "metadata_store.sqlite")
                
                # 为了简单起见，这里关闭并复制数据库文件
                # 实际应用中可能需要更复杂的导出/导入逻辑
                self.metadata_store.close()
                
                # 获取原始数据库路径
                original_path = self.metadata_store.db_path
                
                # 复制文件
                if os.path.exists(original_path):
                    shutil.copy2(original_path, metadata_db_path)
                
                # 重新初始化元数据存储
                self.metadata_store = MetadataStore(original_path)
            
            logger.info(f"知识库已保存到: {path}")
            return True
        except Exception as e:
            logger.error(f"保存知识库失败: {e}")
            return False
    
    def load(self, path: str) -> bool:
        """
        加载知识库
        
        参数:
            path: 加载路径
            
        返回:
            是否成功加载
        """
        try:
            # 检查路径是否存在
            if not os.path.exists(path):
                logger.error(f"知识库路径不存在: {path}")
                return False
                
            # 加载向量存储
            vector_db_path = os.path.join(path, "vector_store.sqlite")
            if os.path.exists(vector_db_path):
                if not self.vector_store:
                    # 初始化向量存储
                    self.vector_store = VectorStore(vector_db_path)
                else:
                    # 加载向量存储
                    self.vector_store.load(vector_db_path)
            
            # 加载元数据存储
            metadata_db_path = os.path.join(path, "metadata_store.sqlite")
            if os.path.exists(metadata_db_path):
                # 关闭现有连接
                if self.metadata_store:
                    self.metadata_store.close()
                
                # 初始化元数据存储
                self.metadata_store = MetadataStore(metadata_db_path)
            
            logger.info(f"知识库已加载: {path}")
            return True
        except Exception as e:
            logger.error(f"加载知识库失败: {e}")
            return False
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算两个向量的余弦相似度
        
        参数:
            vec1: 向量1
            vec2: 向量2
            
        返回:
            相似度（0-1之间）
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)
    
    def list_documents(self, filters: Dict = None) -> List[Dict]:
        """
        列出知识库中的文档
        
        参数:
            filters: 过滤条件
            
        返回:
            文档列表
        """
        if not self.metadata_store:
            logger.error("元数据存储未初始化")
            return []
            
        try:
            return self.metadata_store.list_documents(filters)
        except Exception as e:
            logger.error(f"列出文档失败: {e}")
            return []
    
    def search_documents(self, query: str) -> List[Dict]:
        """
        搜索文档（基于元数据，而非向量）
        
        参数:
            query: 搜索关键词
            
        返回:
            匹配的文档列表
        """
        if not self.metadata_store:
            logger.error("元数据存储未初始化")
            return []
            
        try:
            return self.metadata_store.search_documents(query)
        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            return []
    
    def get_document_content(self, doc_id: str) -> str:
        """
        获取文档完整内容（合并所有块）
        
        参数:
            doc_id: 文档ID
            
        返回:
            文档内容
        """
        if not self.metadata_store:
            logger.error("元数据存储未初始化")
            return ""
            
        try:
            # 获取文档的所有块
            chunks = self.metadata_store.get_chunks_by_document(doc_id)
            
            # 按块索引排序
            chunks.sort(key=lambda x: x.get("chunk_index", 0))
            
            # 合并文本
            content = "".join(chunk.get("text", "") for chunk in chunks)
            
            return content
        except Exception as e:
            logger.error(f"获取文档内容失败: {e}")
            return ""
    
    def close(self):
        """关闭知识库连接"""
        try:
            # 关闭向量存储
            if self.vector_store:
                self.vector_store.close()
                self.vector_store = None
                
            # 关闭元数据存储
            if self.metadata_store:
                self.metadata_store.close()
                self.metadata_store = None
                
            logger.info("知识库连接已关闭")
        except Exception as e:
            logger.error(f"关闭知识库连接失败: {e}")

    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """批量添加文档
        
        Args:
            documents: 文档列表，每个文档包含text和metadata字段
        
        Returns:
            List[str]: 文档ID列表
        """
        doc_ids = []
        for document in documents:
            # 确保文档有text字段
            if "text" not in document:
                logger.warning(f"文档缺少text字段，跳过")
                continue
                
            # 获取或生成文档ID
            metadata = document.get("metadata", {})
            doc_id = metadata.get("id", f"doc_{uuid.uuid4().hex[:8]}")
            
            # 添加文本
            success = self.add_text(document["text"], metadata)
            if success:
                doc_ids.append(doc_id)
        
        logger.info(f"批量添加了 {len(doc_ids)} 个文档")
        return doc_ids 