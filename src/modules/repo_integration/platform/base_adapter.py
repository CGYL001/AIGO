"""
仓库平台适配器基类

为不同代码托管平台提供统一的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any

class BaseRepoAdapter(ABC):
    """
    代码仓库平台适配器基类
    
    定义与代码托管平台交互的通用接口
    各平台特定的适配器需继承此类并实现相应方法
    """
    
    def __init__(self, config: Dict):
        """
        初始化适配器
        
        Args:
            config: 平台特定配置参数
        """
        self._config = config
        self._authenticated = False
        self._user_info = {}
        
    @abstractmethod
    async def authenticate(self, credentials: Dict) -> Tuple[bool, str]:
        """
        认证平台
        
        Args:
            credentials: 认证凭据信息
            
        Returns:
            Tuple[bool, str]: (是否认证成功, 消息)
        """
        pass
        
    @abstractmethod
    async def list_repositories(self, username: str = None) -> List[Dict]:
        """
        获取仓库列表
        
        Args:
            username: 指定用户名，不指定则获取已认证用户的仓库
            
        Returns:
            List[Dict]: 仓库信息列表
        """
        pass
        
    @abstractmethod
    async def get_repository(self, repo_name: str) -> Dict:
        """
        获取仓库详情
        
        Args:
            repo_name: 仓库名称 (格式: 用户名/仓库名)
            
        Returns:
            Dict: 仓库详细信息
        """
        pass
        
    def get_platform_name(self) -> str:
        """
        获取平台名称
        
        Returns:
            str: 平台名称
        """
        return self._config.get("name", "Unknown")
        
    def get_api_url(self) -> str:
        """
        获取API URL
        
        Returns:
            str: 平台API URL
        """
        return self._config.get("api_url", "")
        
    def get_auth_method(self) -> str:
        """
        获取认证方式
        
        Returns:
            str: 认证方式
        """
        return self._config.get("auth_method", "")
        
    def is_authenticated(self) -> bool:
        """
        检查是否已认证
        
        Returns:
            bool: 是否已认证
        """
        return self._authenticated
        
    def get_user_info(self) -> Dict:
        """
        获取认证用户信息
        
        Returns:
            Dict: 用户信息
        """
        return self._user_info 