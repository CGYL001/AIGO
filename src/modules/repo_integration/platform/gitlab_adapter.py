"""
GitLab平台适配器

提供与GitLab平台交互的适配器实现
"""

import os
import json
import logging
import aiohttp
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from .base_adapter import BaseRepoAdapter

logger = logging.getLogger(__name__)

class GitLabAdapter(BaseRepoAdapter):
    """
    GitLab平台适配器
    
    实现与GitLab API的交互功能
    """
    
    def __init__(self, config: Dict):
        """初始化GitLab适配器"""
        super().__init__(config)
        self._api_url = config.get("api_url", "https://gitlab.com/api/v4")
        self._token = None
        self._token_file = Path("data") / "credentials" / "gitlab_token.json"
        self._load_token()
        
    def _load_token(self):
        """从文件加载令牌"""
        if self._token_file.exists():
            try:
                with open(self._token_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._token = data.get("token")
                    if self._token:
                        self._authenticated = True
                        self._user_info = data.get("user_info", {})
                        logger.info("已从文件加载GitLab令牌")
            except Exception as e:
                logger.error(f"加载GitLab令牌失败: {str(e)}")
    
    def _save_token(self):
        """保存令牌到文件"""
        os.makedirs(self._token_file.parent, exist_ok=True)
        try:
            with open(self._token_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "token": self._token,
                    "user_info": self._user_info
                }, f, ensure_ascii=False, indent=2)
            logger.info("已保存GitLab令牌")
        except Exception as e:
            logger.error(f"保存GitLab令牌失败: {str(e)}")
    
    async def authenticate(self, credentials: Dict) -> Tuple[bool, str]:
        """
        认证GitLab平台
        
        Args:
            credentials: 认证凭据，包含token字段
            
        Returns:
            Tuple[bool, str]: (是否认证成功, 消息)
        """
        token = credentials.get("token")
        if not token:
            return False, "未提供访问令牌"
            
        # 验证令牌
        headers = {
            "PRIVATE-TOKEN": token
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self._api_url}/user", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self._token = token
                        self._authenticated = True
                        self._user_info = {
                            "id": user_data.get("id"),
                            "username": user_data.get("username"),
                            "name": user_data.get("name"),
                            "avatar_url": user_data.get("avatar_url"),
                            "web_url": user_data.get("web_url")
                        }
                        self._save_token()
                        return True, f"认证成功，欢迎 {self._user_info.get('name', self._user_info.get('username'))}"
                    else:
                        error_msg = await response.text()
                        return False, f"认证失败: {response.status} - {error_msg}"
        except Exception as e:
            logger.error(f"GitLab认证请求失败: {str(e)}")
            return False, f"认证请求失败: {str(e)}"
    
    async def list_repositories(self, username: str = None) -> List[Dict]:
        """
        获取仓库列表
        
        Args:
            username: 指定用户名，不指定则获取已认证用户的仓库
            
        Returns:
            List[Dict]: 仓库信息列表
        """
        if not self._authenticated:
            logger.error("未认证GitLab平台")
            return []
            
        headers = {
            "PRIVATE-TOKEN": self._token
        }
        
        url = f"{self._api_url}/projects"
        params = {"membership": True}
        
        if username:
            params["username"] = username
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        repos_data = await response.json()
                        # 转换为标准格式
                        return [
                            {
                                "id": repo.get("id"),
                                "name": repo.get("name"),
                                "full_name": repo.get("path_with_namespace"),
                                "description": repo.get("description"),
                                "url": repo.get("web_url"),
                                "clone_url": repo.get("http_url_to_repo"),
                                "ssh_url": repo.get("ssh_url_to_repo"),
                                "default_branch": repo.get("default_branch"),
                                "owner": {
                                    "login": repo.get("namespace", {}).get("path"),
                                    "avatar_url": repo.get("owner", {}).get("avatar_url"),
                                    "url": repo.get("namespace", {}).get("web_url")
                                },
                                "stars": repo.get("star_count"),
                                "forks": repo.get("forks_count"),
                                "language": repo.get("languages", [None])[0],
                                "updated_at": repo.get("last_activity_at")
                            }
                            for repo in repos_data
                        ]
                    else:
                        error_msg = await response.text()
                        logger.error(f"获取仓库列表失败: {response.status} - {error_msg}")
                        return []
        except Exception as e:
            logger.error(f"获取GitLab仓库列表失败: {str(e)}")
            return []
    
    async def get_repository(self, repo_name: str) -> Dict:
        """
        获取仓库详情
        
        Args:
            repo_name: 仓库名称 (格式: 用户名/仓库名)
            
        Returns:
            Dict: 仓库详细信息
        """
        if not self._authenticated:
            logger.error("未认证GitLab平台")
            return {}
            
        headers = {
            "PRIVATE-TOKEN": self._token
        }
        
        # GitLab API需要URL编码的项目路径
        encoded_repo_name = repo_name.replace("/", "%2F")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self._api_url}/projects/{encoded_repo_name}", headers=headers) as response:
                    if response.status == 200:
                        repo = await response.json()
                        return {
                            "id": repo.get("id"),
                            "name": repo.get("name"),
                            "full_name": repo.get("path_with_namespace"),
                            "description": repo.get("description"),
                            "url": repo.get("web_url"),
                            "clone_url": repo.get("http_url_to_repo"),
                            "ssh_url": repo.get("ssh_url_to_repo"),
                            "default_branch": repo.get("default_branch"),
                            "owner": {
                                "login": repo.get("namespace", {}).get("path"),
                                "avatar_url": repo.get("owner", {}).get("avatar_url"),
                                "url": repo.get("namespace", {}).get("web_url")
                            },
                            "stars": repo.get("star_count"),
                            "forks": repo.get("forks_count"),
                            "language": repo.get("languages", [None])[0],
                            "updated_at": repo.get("last_activity_at"),
                            "topics": repo.get("topics", []),
                            "license": repo.get("license", {}).get("name"),
                            "private": not repo.get("public", True)
                        }
                    else:
                        error_msg = await response.text()
                        logger.error(f"获取仓库详情失败: {response.status} - {error_msg}")
                        return {}
        except Exception as e:
            logger.error(f"获取GitLab仓库详情失败: {str(e)}")
            return {}
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return "GitLab" 