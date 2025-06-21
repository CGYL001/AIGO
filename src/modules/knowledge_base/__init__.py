# Knowledge Base 包初始化文件
"""
知识库模块

提供知识库管理和检索功能，支持向量存储和语义搜索。
"""

# 导入主类
from src.modules.knowledge_base.knowledge_base import KnowledgeBase
from src.modules.knowledge_base.storage.vector_store import VectorStore
from src.modules.knowledge_base.storage.metadata_store import MetadataStore

# 为向后兼容保留旧实现的引用，但标记为已弃用
import warnings
import sys
import os

# 将旧模块路径加入到此包的命名空间中
# 这保证了使用旧路径的代码可以继续工作，但会收到警告
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 标记旧类为已弃用
class LegacyKnowledgeBase:
    def __new__(cls, *args, **kwargs):
        warnings.warn(
            "使用src.modules.knowledge_base直接导入的KnowledgeBase类已弃用，"
            "请改用 'from src.modules.knowledge_base import KnowledgeBase'",
            DeprecationWarning, 
            stacklevel=2
        )
        return KnowledgeBase(*args, **kwargs)

# 导出组件
__all__ = ["KnowledgeBase", "VectorStore", "MetadataStore"] 