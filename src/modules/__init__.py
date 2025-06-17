"""
AIgo核心模块包
"""

from src.modules.code_completion import CodeCompletion
from src.modules.context_manager import ContextManager
from src.modules.error_checker import ErrorChecker
from src.modules.knowledge_base import KnowledgeBase
from src.modules.ui import UI
from src.modules.code_analysis import CodeAnalyzer
from src.modules.network_proxy import NetworkProxy
from src.modules.repo_integration.repo_manager import RepoManager

__all__ = [
    'CodeCompletionModule',
    'ContextManager',
    'ErrorChecker',
    'KnowledgeBase',
    'UI',
    'CodeAnalyzer',
    'NetworkProxy',
    'RepoManager'
]

# CodeAssistant 核心模块
__version__ = "0.1.0"

from src.modules.prompt_engineering import PromptEngineer 