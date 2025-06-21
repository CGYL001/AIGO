"""
AIgo 模块包

此包包含AIgo系统的核心功能模块，包括代码分析、知识库、提示工程等。
"""

# 导入核心模块
from src.modules.code_analyzer import CodeAnalyzer
from src.modules.code_completion import CodeCompletion
from src.modules.knowledge_base import KnowledgeBase
from src.modules.context_manager import ContextManager
from src.modules.error_checker import ErrorChecker

# 导入子包
from src.modules.code_analysis import *
from src.modules.knowledge_base import *
from src.modules.prompt_engineering import *
from src.modules.repo_integration import *
from src.modules.developer_preferences import *
from src.modules.system_monitor import *

# 创建模块实例
filesystem_analyzer = None
network_proxy = None
context_manager = ContextManager()

# 初始化模块实例
try:
    from src.modules.filesystem_analyzer import FilesystemAnalyzer
    filesystem_analyzer = FilesystemAnalyzer()
except ImportError:
    # 如果模块不存在，创建一个空的模块
    class DummyFilesystemAnalyzer:
        def scan_directory(self, *args, **kwargs):
            return {"error": "模块未加载"}
        
        def find_files(self, *args, **kwargs):
            return {"files": []}
            
    filesystem_analyzer = DummyFilesystemAnalyzer()

try:
    from src.modules.network_proxy import NetworkProxy
    network_proxy = NetworkProxy()
except ImportError:
    # 如果模块不存在，创建一个空的模块
    class DummyNetworkProxy:
        def request(self, *args, **kwargs):
            return {"error": "模块未加载"}
            
    network_proxy = DummyNetworkProxy()

__all__ = [
    'CodeAnalyzer',
    'CodeCompletion',
    'KnowledgeBase',
    'ContextManager',
    'ErrorChecker',
    'filesystem_analyzer',
    'network_proxy',
    'context_manager'
]

# CodeAssistant 核心模块
__version__ = "0.1.0"

from src.modules.prompt_engineering import PromptEngineer 