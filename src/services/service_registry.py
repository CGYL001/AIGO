"""
服务注册器

用于在应用启动时注册所有服务到依赖容器
"""

import logging
from src.utils.dependency_container import get_container
from src.services.model_service import ModelService
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.services.repo_permission_service import RepoPermissionService
from src.modules.repo_integration.repo_manager import RepoManager
from src.modules.code_completion import CodeCompletion
from src.modules.knowledge_base.knowledge_base import KnowledgeBase
from src.modules.code_analysis.analyzer import CodeAnalyzer
from src.modules.error_checker import ErrorChecker
from src.modules.context_manager import ContextManager
from src.modules.network_proxy import NetworkProxy
from src.modules.ui import UI
from src.modules.prompt_engineering.optimizer import PromptEngineer

logger = logging.getLogger(__name__)

def register_services():
    """
    注册所有服务到依赖容器
    
    此函数应在应用启动时调用，用于注册所有服务
    """
    container = get_container()
    
    # 注册核心服务
    logger.info("注册核心服务...")
    container.register(ModelService)
    container.register(AuthService)
    container.register(UserService)
    container.register(RepoPermissionService)
    
    # 注册模块
    logger.info("注册功能模块...")
    container.register(RepoManager)
    container.register(CodeCompletion)
    container.register(KnowledgeBase)
    container.register(CodeAnalyzer)
    container.register(ErrorChecker)
    container.register(ContextManager)
    container.register(NetworkProxy)
    container.register(UI)
    container.register(PromptEngineer)
    
    logger.info("服务注册完成")
    
def get_service(service_type):
    """
    获取服务实例
    
    Args:
        service_type: 服务类型
        
    Returns:
        服务实例
    """

