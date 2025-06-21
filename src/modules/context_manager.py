import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set, Tuple
import uuid

from src.utils import config, logger


class ContextManager:
    """
    上下文管理器，提供多层次上下文管理和记忆功能
    """
    
    def __init__(self):
        """初始化上下文管理器"""
        # 配置
        self.storage_path = Path(config.get("context_manager.storage_path", "data/context"))
        self.max_context_size = config.get("context_manager.max_context_size", 10000)  # 每个上下文的最大字符数
        self.max_contexts = config.get("context_manager.max_contexts", 100)  # 最大上下文数量
        self.persistence_enabled = config.get("context_manager.persistence_enabled", True)  # 是否持久化上下文
        self.compression_enabled = config.get("context_manager.compression_enabled", True)  # 是否启用上下文压缩
        
        # 上下文层次
        self.levels = {
            "project": 0,  # 项目级别
            "file": 1,     # 文件级别
            "block": 2,    # 代码块级别
            "session": 3,  # 会话级别
            "memory": 4    # 长期记忆级别
        }
        
        # 上下文存储
        self.contexts: Dict[str, Dict[str, Any]] = {}
        
        # 会话映射
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # 创建存储目录
        os.makedirs(self.storage_path, exist_ok=True)
        
        # 加载持久化的上下文
        if self.persistence_enabled:
            self._load_contexts()
        
        logger.info("上下文管理器初始化完成")
    
    def create_context(self, name: str, level: Union[str, int], 
                     content: str = "", metadata: Dict[str, Any] = None) -> str:
        """
        创建新的上下文
        
        Args:
            name: 上下文名称
            level: 上下文级别，可以是字符串或整数
            content: 上下文内容
            metadata: 上下文元数据
            
        Returns:
            str: 上下文ID
        """
        # 生成唯一ID
        context_id = str(uuid.uuid4())
        
        # 解析级别
        if isinstance(level, str):
            if level not in self.levels:
                logger.warning(f"未知的上下文级别: {level}，使用默认级别: file")
                level = "file"
            level_num = self.levels[level]
        else:
            level_num = level
        
        # 创建上下文
        context = {
            "id": context_id,
            "name": name,
            "level": level_num,
            "level_name": next((k for k, v in self.levels.items() if v == level_num), "unknown"),
            "content": content[:self.max_context_size] if content else "",
            "metadata": metadata or {},
            "created_at": time.time(),
            "updated_at": time.time(),
            "access_count": 0,
            "last_accessed": time.time()
        }
        
        # 存储上下文
        self.contexts[context_id] = context
        
        # 管理上下文数量
        self._manage_contexts()
        
        # 持久化
        if self.persistence_enabled:
            self._save_context(context_id)
        
        logger.debug(f"创建上下文: {name} (ID: {context_id})")
        return context_id
    
    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """
        获取上下文
        
        Args:
            context_id: 上下文ID
            
        Returns:
            Optional[Dict[str, Any]]: 上下文信息，如果不存在则返回None
        """
        if context_id not in self.contexts:
            return None
        
        # 更新访问信息
        self.contexts[context_id]["access_count"] += 1
        self.contexts[context_id]["last_accessed"] = time.time()
        
        return self.contexts[context_id]
    
    def update_context(self, context_id: str, content: Optional[str] = None, 
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        更新上下文
        
        Args:
            context_id: 上下文ID
            content: 新的上下文内容，如果为None则不更新
            metadata: 新的上下文元数据，如果为None则不更新
            
        Returns:
            bool: 如果更新成功，则返回True
        """
        if context_id not in self.contexts:
            logger.warning(f"尝试更新不存在的上下文: {context_id}")
            return False
        
        # 更新内容
        if content is not None:
            self.contexts[context_id]["content"] = content[:self.max_context_size]
        
        # 更新元数据
        if metadata is not None:
            self.contexts[context_id]["metadata"].update(metadata)
        
        # 更新时间戳
        self.contexts[context_id]["updated_at"] = time.time()
        
        # 持久化
        if self.persistence_enabled:
            self._save_context(context_id)
        
        return True
    
    def delete_context(self, context_id: str) -> bool:
        """
        删除上下文
        
        Args:
            context_id: 上下文ID
            
        Returns:
            bool: 如果删除成功，则返回True
        """
        if context_id not in self.contexts:
            logger.warning(f"尝试删除不存在的上下文: {context_id}")
            return False
        
        # 删除上下文
        del self.contexts[context_id]
        
        # 删除持久化文件
        if self.persistence_enabled:
            context_file = self.storage_path / f"{context_id}.json"
            try:
                if context_file.exists():
                    context_file.unlink()
            except Exception as e:
                logger.error(f"删除上下文文件失败: {context_id}, 错误: {str(e)}")
        
        return True
    
    def search_contexts(self, query: str = None, level: Union[str, int] = None, 
                      metadata_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        搜索上下文
        
        Args:
            query: 搜索查询，匹配名称或内容
            level: 上下文级别过滤
            metadata_filter: 元数据过滤条件
            
        Returns:
            List[Dict[str, Any]]: 匹配的上下文列表
        """
        results = []
        
        # 解析级别
        level_num = None
        if level is not None:
            if isinstance(level, str):
                if level in self.levels:
                    level_num = self.levels[level]
                else:
                    logger.warning(f"未知的上下文级别: {level}")
                    return []
            else:
                level_num = level
        
        # 搜索上下文
        for context_id, context in self.contexts.items():
            # 级别过滤
            if level_num is not None and context["level"] != level_num:
                continue
            
            # 查询过滤
            if query is not None:
                query_lower = query.lower()
                name_match = query_lower in context["name"].lower()
                content_match = query_lower in context["content"].lower()
                if not (name_match or content_match):
                    continue
            
            # 元数据过滤
            if metadata_filter is not None:
                metadata = context["metadata"]
                match = True
                for key, value in metadata_filter.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                if not match:
                    continue
            
            # 添加到结果
            results.append(context)
        
        return results
    
    def create_session(self, name: str, metadata: Dict[str, Any] = None) -> str:
        """
        创建新的会话
        
        Args:
            name: 会话名称
            metadata: 会话元数据
            
        Returns:
            str: 会话ID
        """
        # 生成唯一ID
        session_id = str(uuid.uuid4())
        
        # 创建会话
        session = {
            "id": session_id,
            "name": name,
            "contexts": [],
            "metadata": metadata or {},
            "created_at": time.time(),
            "updated_at": time.time(),
            "last_accessed": time.time()
        }
        
        # 存储会话
        self.sessions[session_id] = session
        
        # 创建会话上下文
        context_id = self.create_context(
            name=f"Session: {name}",
            level="session",
            metadata={"session_id": session_id}
        )
        
        # 添加到会话
        self.sessions[session_id]["contexts"].append(context_id)
        
        logger.debug(f"创建会话: {name} (ID: {session_id})")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Dict[str, Any]]: 会话信息，如果不存在则返回None
        """
        if session_id not in self.sessions:
            return None
        
        # 更新访问时间
        self.sessions[session_id]["last_accessed"] = time.time()
        
        return self.sessions[session_id]
    
    def add_context_to_session(self, session_id: str, context_id: str) -> bool:
        """
        将上下文添加到会话
        
        Args:
            session_id: 会话ID
            context_id: 上下文ID
            
        Returns:
            bool: 如果添加成功，则返回True
        """
        if session_id not in self.sessions:
            logger.warning(f"尝试添加上下文到不存在的会话: {session_id}")
            return False
        
        if context_id not in self.contexts:
            logger.warning(f"尝试添加不存在的上下文: {context_id}")
            return False
        
        # 添加到会话
        if context_id not in self.sessions[session_id]["contexts"]:
            self.sessions[session_id]["contexts"].append(context_id)
        
        # 更新时间戳
        self.sessions[session_id]["updated_at"] = time.time()
        
        return True
    
    def remove_context_from_session(self, session_id: str, context_id: str) -> bool:
        """
        从会话中移除上下文
        
        Args:
            session_id: 会话ID
            context_id: 上下文ID
            
        Returns:
            bool: 如果移除成功，则返回True
        """
        if session_id not in self.sessions:
            logger.warning(f"尝试从不存在的会话中移除上下文: {session_id}")
            return False
        
        # 移除上下文
        if context_id in self.sessions[session_id]["contexts"]:
            self.sessions[session_id]["contexts"].remove(context_id)
            
            # 更新时间戳
            self.sessions[session_id]["updated_at"] = time.time()
            
            return True
        else:
            logger.warning(f"上下文不在会话中: {context_id} (会话: {session_id})")
            return False
    
    def get_session_contexts(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取会话中的所有上下文
        
        Args:
            session_id: 会话ID
            
        Returns:
            List[Dict[str, Any]]: 上下文列表
        """
        if session_id not in self.sessions:
            logger.warning(f"尝试获取不存在的会话的上下文: {session_id}")
            return []
        
        # 获取会话中的上下文
        contexts = []
        for context_id in self.sessions[session_id]["contexts"]:
            context = self.get_context(context_id)
            if context:
                contexts.append(context)
        
        return contexts
    
    def compress_context(self, context_id: str, max_length: int = None) -> bool:
        """
        压缩上下文内容
        
        Args:
            context_id: 上下文ID
            max_length: 最大长度，如果为None则使用默认值
            
        Returns:
            bool: 如果压缩成功，则返回True
        """
        if not self.compression_enabled:
            return False
            
        if context_id not in self.contexts:
            logger.warning(f"尝试压缩不存在的上下文: {context_id}")
            return False
        
        context = self.contexts[context_id]
        content = context["content"]
        
        # 如果内容已经足够短，则不需要压缩
        max_length = max_length or self.max_context_size // 2
        if len(content) <= max_length:
            return True
        
        # 简单的压缩策略：保留开头和结尾，省略中间部分
        if len(content) > max_length:
            head_size = max_length // 2
            tail_size = max_length - head_size
            compressed = content[:head_size] + f"\n...[省略 {len(content) - max_length} 个字符]...\n" + content[-tail_size:]
            
            # 更新上下文
            return self.update_context(
                context_id=context_id,
                content=compressed,
                metadata={"compressed": True, "original_length": len(content)}
            )
        
        return True
    
    def merge_contexts(self, context_ids: List[str], name: str, level: Union[str, int]) -> Optional[str]:
        """
        合并多个上下文
        
        Args:
            context_ids: 要合并的上下文ID列表
            name: 新上下文的名称
            level: 新上下文的级别
            
        Returns:
            Optional[str]: 新上下文的ID，如果合并失败则返回None
        """
        # 检查上下文是否存在
        contexts = []
        for context_id in context_ids:
            context = self.get_context(context_id)
            if context:
                contexts.append(context)
            else:
                logger.warning(f"尝试合并不存在的上下文: {context_id}")
        
        if not contexts:
            logger.warning("没有有效的上下文可合并")
            return None
        
        # 合并内容和元数据
        merged_content = "\n\n".join(context["content"] for context in contexts)
        
        # 合并元数据
        merged_metadata = {}
        for context in contexts:
            for key, value in context["metadata"].items():
                if key in merged_metadata:
                    if isinstance(merged_metadata[key], list):
                        if value not in merged_metadata[key]:
                            merged_metadata[key].append(value)
                    else:
                        if merged_metadata[key] != value:
                            merged_metadata[key] = [merged_metadata[key], value]
                else:
                    merged_metadata[key] = value
        
        # 添加合并信息
        merged_metadata["merged_from"] = context_ids
        merged_metadata["merged_at"] = time.time()
        
        # 创建新上下文
        return self.create_context(
            name=name,
            level=level,
            content=merged_content,
            metadata=merged_metadata
        )
    
    def _manage_contexts(self):
        """管理上下文数量，如果超过最大值则删除最旧的上下文"""
        if len(self.contexts) <= self.max_contexts:
            return
        
        # 按最后访问时间排序
        sorted_contexts = sorted(
            self.contexts.items(),
            key=lambda x: x[1]["last_accessed"]
        )
        
        # 删除最旧的上下文，直到数量符合要求
        contexts_to_delete = len(self.contexts) - self.max_contexts
        for i in range(contexts_to_delete):
            context_id, _ = sorted_contexts[i]
            self.delete_context(context_id)
    
    def _save_context(self, context_id: str) -> bool:
        """保存上下文到文件"""
        if not self.persistence_enabled:
            return False
            
        if context_id not in self.contexts:
            return False
        
        context = self.contexts[context_id]
        context_file = self.storage_path / f"{context_id}.json"
        
        try:
            with open(context_file, "w", encoding="utf-8") as f:
                json.dump(context, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存上下文失败: {context_id}, 错误: {str(e)}")
            return False
    
    def _load_contexts(self):
        """加载所有持久化的上下文"""
        try:
            # 查找所有上下文文件
            context_files = list(self.storage_path.glob("*.json"))
            
            for file_path in context_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        context = json.load(f)
                    
                    # 添加到内存中
                    context_id = context["id"]
                    self.contexts[context_id] = context
                    
                except Exception as e:
                    logger.error(f"加载上下文文件失败: {file_path}, 错误: {str(e)}")
            
            logger.info(f"已加载 {len(self.contexts)} 个上下文")
        except Exception as e:
            logger.error(f"加载上下文失败: {str(e)}")


# 创建单例实例
context_manager = ContextManager() 