#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
元数据存储模块 - 提供对知识库元数据的存储和管理
"""

import os
import json
import sqlite3
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from src.utils import logger

class MetadataStore:
    """
    元数据存储类，使用SQLite实现
    用于存储知识库文档和块的元数据信息
    """
    
    def __init__(self, db_path: str):
        """
        初始化元数据存储
        
        参数:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """初始化SQLite数据库"""
        try:
            # 创建目录
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # 连接数据库
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # 创建文档表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                source TEXT,
                type TEXT,
                title TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
            """)
            
            # 创建块表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                text TEXT,
                chunk_index INTEGER,
                total_chunks INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_id ON chunks(document_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_source ON documents(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_type ON documents(type)")
            
            self.conn.commit()
            logger.info(f"元数据存储初始化成功: {self.db_path}")
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
            if self.conn:
                self.conn.close()
                self.conn = None
    
    def add_document(self, doc_id: str, metadata: Dict[str, Any]) -> bool:
        """
        添加文档元数据
        
        参数:
            doc_id: 文档ID
            metadata: 元数据字典
            
        返回:
            是否成功添加
        """
        if not self.conn:
            logger.error("数据库未连接")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # 提取一些常用字段
            source = metadata.get("source", "")
            doc_type = metadata.get("type", "")
            title = metadata.get("title", "")
            description = metadata.get("description", "")
            
            # 存储整个元数据
            metadata_json = json.dumps(metadata)
            
            # 插入数据
            cursor.execute(
                """
                INSERT INTO documents (id, source, type, title, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                source=excluded.source,
                type=excluded.type,
                title=excluded.title,
                description=excluded.description,
                metadata=excluded.metadata
                """,
                (doc_id, source, doc_type, title, description, metadata_json)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"添加文档元数据失败: {e}")
            return False
    
    def add_chunk(self, chunk_id: str, doc_id: str, text: str, chunk_index: int,
                 total_chunks: int, metadata: Dict[str, Any]) -> bool:
        """
        添加块元数据
        
        参数:
            chunk_id: 块ID
            doc_id: 文档ID
            text: 文本内容
            chunk_index: 块索引
            total_chunks: 总块数
            metadata: 元数据字典
            
        返回:
            是否成功添加
        """
        if not self.conn:
            logger.error("数据库未连接")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # 存储元数据
            metadata_json = json.dumps(metadata)
            
            # 插入数据
            cursor.execute(
                """
                INSERT INTO chunks (id, document_id, text, chunk_index, total_chunks, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                document_id=excluded.document_id,
                text=excluded.text,
                chunk_index=excluded.chunk_index,
                total_chunks=excluded.total_chunks,
                metadata=excluded.metadata
                """,
                (chunk_id, doc_id, text, chunk_index, total_chunks, metadata_json)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"添加块元数据失败: {e}")
            return False
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        获取文档元数据
        
        参数:
            doc_id: 文档ID
            
        返回:
            文档元数据字典，如果不存在则返回None
        """
        if not self.conn:
            logger.error("数据库未连接")
            return None
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, source, type, title, description, created_at, metadata FROM documents WHERE id = ?",
                (doc_id,)
            )
            
            row = cursor.fetchone()
            if row:
                doc_id, source, doc_type, title, description, created_at, metadata_json = row
                
                # 解析元数据JSON
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                return {
                    "id": doc_id,
                    "source": source,
                    "type": doc_type,
                    "title": title,
                    "description": description,
                    "created_at": created_at,
                    **metadata
                }
            
            return None
        except Exception as e:
            logger.error(f"获取文档元数据失败: {e}")
            return None
    
    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        获取块元数据
        
        参数:
            chunk_id: 块ID
            
        返回:
            块元数据字典，如果不存在则返回None
        """
        if not self.conn:
            logger.error("数据库未连接")
            return None
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id, document_id, text, chunk_index, total_chunks, created_at, metadata
                FROM chunks WHERE id = ?
                """,
                (chunk_id,)
            )
            
            row = cursor.fetchone()
            if row:
                chunk_id, doc_id, text, chunk_index, total_chunks, created_at, metadata_json = row
                
                # 解析元数据JSON
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                return {
                    "id": chunk_id,
                    "document_id": doc_id,
                    "text": text,
                    "chunk_index": chunk_index,
                    "total_chunks": total_chunks,
                    "created_at": created_at,
                    **metadata
                }
            
            return None
        except Exception as e:
            logger.error(f"获取块元数据失败: {e}")
            return None
    
    def get_chunks_by_document(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        获取文档的所有块
        
        参数:
            doc_id: 文档ID
            
        返回:
            块元数据列表
        """
        if not self.conn:
            logger.error("数据库未连接")
            return []
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id, document_id, text, chunk_index, total_chunks, created_at, metadata
                FROM chunks WHERE document_id = ?
                ORDER BY chunk_index
                """,
                (doc_id,)
            )
            
            chunks = []
            for row in cursor.fetchall():
                chunk_id, doc_id, text, chunk_index, total_chunks, created_at, metadata_json = row
                
                # 解析元数据JSON
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                chunks.append({
                    "id": chunk_id,
                    "document_id": doc_id,
                    "text": text,
                    "chunk_index": chunk_index,
                    "total_chunks": total_chunks,
                    "created_at": created_at,
                    **metadata
                })
            
            return chunks
        except Exception as e:
            logger.error(f"获取文档块失败: {e}")
            return []
    
    def list_documents(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        列出文档
        
        参数:
            filters: 过滤条件，例如 {'type': 'pdf'}
            
        返回:
            文档元数据列表
        """
        if not self.conn:
            logger.error("数据库未连接")
            return []
            
        try:
            cursor = self.conn.cursor()
            
            # 构建查询
            query = "SELECT id, source, type, title, description, created_at, metadata FROM documents"
            params = []
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    if key in ["id", "source", "type", "title"]:
                        conditions.append(f"{key} = ?")
                        params.append(value)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, params)
            
            documents = []
            for row in cursor.fetchall():
                doc_id, source, doc_type, title, description, created_at, metadata_json = row
                
                # 解析元数据JSON
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                documents.append({
                    "id": doc_id,
                    "source": source,
                    "type": doc_type,
                    "title": title,
                    "description": description,
                    "created_at": created_at,
                    **metadata
                })
            
            return documents
        except Exception as e:
            logger.error(f"列出文档失败: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档及其所有块
        
        参数:
            doc_id: 文档ID
            
        返回:
            是否成功删除
        """
        if not self.conn:
            logger.error("数据库未连接")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # 删除文档的所有块
            cursor.execute("DELETE FROM chunks WHERE document_id = ?", (doc_id,))
            
            # 删除文档
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """
        删除块
        
        参数:
            chunk_id: 块ID
            
        返回:
            是否成功删除
        """
        if not self.conn:
            logger.error("数据库未连接")
            return False
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM chunks WHERE id = ?", (chunk_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"删除块失败: {e}")
            return False
    
    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索文档
        
        参数:
            query: 搜索查询
            
        返回:
            匹配的文档列表
        """
        if not self.conn:
            logger.error("数据库未连接")
            return []
            
        try:
            cursor = self.conn.cursor()
            
            # 构建查询 - 使用LIKE进行简单文本搜索
            search_term = f"%{query}%"
            cursor.execute(
                """
                SELECT id, source, type, title, description, created_at, metadata
                FROM documents 
                WHERE title LIKE ? OR description LIKE ?
                """,
                (search_term, search_term)
            )
            
            documents = []
            for row in cursor.fetchall():
                doc_id, source, doc_type, title, description, created_at, metadata_json = row
                
                # 解析元数据JSON
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                documents.append({
                    "id": doc_id,
                    "source": source,
                    "type": doc_type,
                    "title": title,
                    "description": description,
                    "created_at": created_at,
                    **metadata
                })
            
            return documents
        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
            except Exception as e:
                logger.error(f"关闭数据库连接失败: {e}") 