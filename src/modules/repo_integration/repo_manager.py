"""
仓库管理器

管理代码仓库的克隆、拉取、推送等操作
与各代码托管平台集成
"""

import os
import json
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from src.utils import config
from src.services import auth_service
from src.services.repo_permission_service import get_instance as get_repo_permission_service

# 导入平台适配器
from .platform.github_adapter import GitHubAdapter
from .platform.gitlab_adapter import GitLabAdapter
from .platform.gitee_adapter import GiteeAdapter

logger = logging.getLogger(__name__)

class RepoManager:
    """
    代码仓库管理器
    
    负责代码仓库的克隆、拉取、推送等操作
    管理与不同代码托管平台的集成
    """
    
    def __init__(self):
        """初始化仓库管理器"""
        # 加载配置
        self._repo_config = config.get("repository_integration", {})
        
        # 本地仓库存储路径
        local_path = self._repo_config.get("local_repo_path", "data/repositories")
        self._local_repo_path = Path(local_path)
        os.makedirs(self._local_repo_path, exist_ok=True)
        
        # 默认分支
        self._default_branch = self._repo_config.get("default_branch", "main")
        
        # 平台适配器
        self._adapters = {}
        self._initialize_adapters()
        
        # 权限服务
        self._auth_service = auth_service.get_instance()
        self._permission_service = get_repo_permission_service()
        
        # 当前会话ID
        self._current_session_id = None
        
    def _initialize_adapters(self):
        """初始化平台适配器"""
        # 获取平台配置
        platforms_config = self._repo_config.get("platforms", {})
        
        # 初始化启用的平台适配器
        if platforms_config.get("github", {}).get("enabled", False):
            self._adapters["github"] = GitHubAdapter(platforms_config["github"])
            
        if platforms_config.get("gitlab", {}).get("enabled", False):
            self._adapters["gitlab"] = GitLabAdapter(platforms_config["gitlab"])
            
        if platforms_config.get("gitee", {}).get("enabled", False):
            self._adapters["gitee"] = GiteeAdapter(platforms_config["gitee"])
        
        logger.info(f"已初始化 {len(self._adapters)} 个代码托管平台适配器")
        
    def set_session(self, session_id: str):
        """设置当前会话ID"""
        self._current_session_id = session_id
        
    def get_platforms(self) -> List[str]:
        """获取支持的平台列表"""
        return list(self._adapters.keys())
        
    def is_platform_supported(self, platform: str) -> bool:
        """检查平台是否被支持"""
        return platform.lower() in self._adapters
        
    def get_platform_info(self, platform: str) -> Dict:
        """获取平台信息"""
        if not self.is_platform_supported(platform):
            return {}
            
        adapter = self._adapters[platform.lower()]
        return {
            'name': adapter.get_platform_name(),
            'api_url': adapter.get_api_url(),
            'auth_method': adapter.get_auth_method(),
            'authenticated': adapter.is_authenticated()
        }
        
    async def authenticate(self, platform: str, credentials: Dict) -> Tuple[bool, str]:
        """
        平台认证
        
        Args:
            platform: 平台名称
            credentials: 认证信息
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        if not self.is_platform_supported(platform):
            return False, f"不支持的平台: {platform}"
            
        adapter = self._adapters[platform.lower()]
        success, message = await adapter.authenticate(credentials)
        
        return success, message
        
    async def list_repositories(self, platform: str, username: str = None) -> List[Dict]:
        """
        获取仓库列表
        
        Args:
            platform: 平台名称
            username: 用户名，不指定则获取已认证用户的仓库
            
        Returns:
            List[Dict]: 仓库列表
        """
        if not self.is_platform_supported(platform):
            logger.error(f"不支持的平台: {platform}")
            return []
            
        adapter = self._adapters[platform.lower()]
        
        if not adapter.is_authenticated():
            logger.error(f"未认证平台: {platform}")
            return []
            
        repos = await adapter.list_repositories(username)
        return repos
        
    async def get_repository(self, platform: str, repo_name: str) -> Dict:
        """
        获取仓库详情
        
        Args:
            platform: 平台名称
            repo_name: 仓库名称 (格式: 用户名/仓库名)
            
        Returns:
            Dict: 仓库信息
        """
        if not self.is_platform_supported(platform):
            logger.error(f"不支持的平台: {platform}")
            return {}
            
        adapter = self._adapters[platform.lower()]
        
        if not adapter.is_authenticated():
            logger.error(f"未认证平台: {platform}")
            return {}
            
        repo_info = await adapter.get_repository(repo_name)
        return repo_info
        
    def get_local_repositories(self) -> List[Dict]:
        """
        获取本地克隆的仓库列表
        
        Returns:
            List[Dict]: 本地仓库列表
        """
        local_repos = []
        
        # 搜索本地仓库目录
        for item in self._local_repo_path.iterdir():
            if not item.is_dir():
                continue
                
            # 检查是否为git仓库
            git_dir = item / ".git"
            if not git_dir.is_dir():
                continue
                
            # 读取仓库信息
            repo_info = self._get_local_repo_info(item)
            if repo_info:
                # 添加仓库ID
                repo_info['repo_id'] = self._permission_service.generate_repo_id(str(item))
                local_repos.append(repo_info)
                
        return local_repos
        
    def _get_local_repo_info(self, repo_path: Path) -> Dict:
        """获取本地仓库信息"""
        try:
            # 获取远程仓库URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            
            remote_url = result.stdout.strip()
            
            # 获取当前分支
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            
            current_branch = result.stdout.strip() or self._default_branch
            
            # 获取最后提交信息
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%an|%at|%s"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            
            last_commit = {}
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split("|", 3)
                if len(parts) >= 4:
                    last_commit = {
                        "hash": parts[0],
                        "author": parts[1],
                        "date": datetime.fromtimestamp(int(parts[2])).isoformat(),
                        "message": parts[3]
                    }
            
            # 确定平台类型
            platform = "unknown"
            if "github.com" in remote_url:
                platform = "github"
            elif "gitlab.com" in remote_url:
                platform = "gitlab"
            elif "gitee.com" in remote_url:
                platform = "gitee"
            
            # 解析仓库名称
            repo_name = repo_path.name
            
            return {
                "name": repo_name,
                "path": str(repo_path),
                "platform": platform,
                "remote_url": remote_url,
                "current_branch": current_branch,
                "last_commit": last_commit
            }
        except Exception as e:
            logger.error(f"获取本地仓库信息失败: {str(e)}")
            return {}
            
    async def clone_repository(self, platform: str, repo_name: str, branch: str = None) -> Tuple[bool, str]:
        """
        克隆仓库
        
        Args:
            platform: 平台名称
            repo_name: 仓库名称 (格式: 用户名/仓库名)
            branch: 分支名，默认为主分支
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        if not self._current_session_id:
            return False, "未设置会话ID"
            
        # 获取仓库信息
        repo_info = await adapter.get_repository(repo_name)
        if not repo_info:
            return False, f"仓库不存在: {repo_name}"
            
        # 获取克隆URL
        clone_url = repo_info.get("clone_url", "")
        if not clone_url:
            return False, "无法获取克隆URL"
            
        # 确定目标目录
        repo_name_simple = repo_name.split("/")[-1]
        target_dir = self._local_repo_path / repo_name_simple
        
        # 检查目录是否已存在
        if target_dir.exists():
            return False, f"目标目录已存在: {target_dir}"
        
        # 权限检查（使用新的权限服务）
        has_permission, message = self._permission_service.check_operation_permission(
            self._current_session_id, 
            str(target_dir), 
            "clone"
        )
        
        if not has_permission:
            return False, message
            
        if not self.is_platform_supported(platform):
            return False, f"不支持的平台: {platform}"
            
        adapter = self._adapters[platform.lower()]
        
        if not adapter.is_authenticated():
            return False, f"未认证平台: {platform}"
            
        # 执行克隆
        try:
            cmd = ["git", "clone"]
            
            # 指定分支
            if branch:
                cmd.extend(["-b", branch])
                
            cmd.extend([clone_url, str(target_dir)])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False, f"克隆失败: {result.stderr}"
            
            # 设置用户为管理员角色
            repo_id = self._permission_service.generate_repo_id(str(target_dir))
            self._permission_service.assign_role(repo_id, self._current_session_id, "admin")
                
            return True, f"仓库已克隆到 {target_dir}"
        except Exception as e:
            logger.error(f"克隆仓库失败: {str(e)}")
            # 清理失败的克隆
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)
            return False, f"克隆操作失败: {str(e)}"
            
    async def pull_repository(self, repo_path: str, branch: str = None) -> Tuple[bool, str]:
        """
        拉取仓库更新
        
        Args:
            repo_path: 本地仓库路径
            branch: 分支名，默认为当前分支
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        if not self._current_session_id:
            return False, "未设置会话ID"
            
        repo_path = Path(repo_path)
        if not repo_path.is_dir() or not (repo_path / ".git").is_dir():
            return False, f"无效的Git仓库: {repo_path}"
            
        # 权限检查（使用新的权限服务）
        has_permission, message = self._permission_service.check_operation_permission(
            self._current_session_id, 
            str(repo_path), 
            "pull"
        )
        
        if not has_permission:
            return False, message
            
        try:
            cmd = ["git", "pull"]
            
            # 指定分支
            if branch:
                cmd.extend(["origin", branch])
                
            result = subprocess.run(
                cmd,
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False, f"拉取失败: {result.stderr}"
                
            return True, f"仓库已更新: {result.stdout}"
        except Exception as e:
            logger.error(f"拉取仓库更新失败: {str(e)}")
            return False, f"拉取更新失败: {str(e)}"
            
    async def push_repository(self, repo_path: str, message: str, branch: str = None) -> Tuple[bool, str]:
        """
        提交并推送更改
        
        Args:
            repo_path: 本地仓库路径
            message: 提交信息
            branch: 分支名，默认为当前分支
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        if not self._current_session_id:
            return False, "未设置会话ID"
            
        repo_path = Path(repo_path)
        if not repo_path.is_dir() or not (repo_path / ".git").is_dir():
            return False, f"无效的Git仓库: {repo_path}"

        # 权限检查（使用新的权限服务）
        has_permission, permission_message = self._permission_service.check_operation_permission(
            self._current_session_id, 
            str(repo_path), 
            "push"
        )
        
        if not has_permission:
            return False, permission_message
        
        # 获取当前分支，用于分支保护规则检查
        current_branch = ""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                current_branch = result.stdout.strip()
        except Exception:
            pass
        
        # 如果指定了分支，使用指定的分支
        use_branch = branch or current_branch
        
        # 检查分支保护规则
        repo_id = self._permission_service.generate_repo_id(str(repo_path))
        is_protected, rule_message = self._permission_service.check_protection_rule(
            repo_id, 
            "protected_branches", 
            {"branch": use_branch}
        )
        
        if not is_protected:
            # 检查用户是否为管理员，如果是管理员则可以绕过保护规则
            role = self._permission_service.get_user_role(repo_id, self._current_session_id)
            if role != "admin":
                return False, rule_message
            
        try:
            # 添加所有更改
            result = subprocess.run(
                ["git", "add", "."],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False, f"添加文件失败: {result.stderr}"
                
            # 提交更改
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0 and "nothing to commit" not in result.stderr:
                return False, f"提交更改失败: {result.stderr}"
                
            # 推送更改
            cmd = ["git", "push"]
            
            # 指定分支
            if branch:
                cmd.extend(["origin", branch])
                
            result = subprocess.run(
                cmd,
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False, f"推送失败: {result.stderr}"
                
            return True, "更改已成功推送"
        except Exception as e:
            logger.error(f"推送仓库更改失败: {str(e)}")
            return False, f"推送更改失败: {str(e)}"
            
    def delete_local_repository(self, repo_path: str) -> Tuple[bool, str]:
        """
        删除本地仓库
        
        Args:
            repo_path: 本地仓库路径
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        if not self._current_session_id:
            return False, "未设置会话ID"

        repo_path = Path(repo_path)
        if not repo_path.is_dir() or not (repo_path / ".git").is_dir():
            return False, f"无效的Git仓库: {repo_path}"
            
        # 确保路径在本地仓库目录内
        if not str(repo_path).startswith(str(self._local_repo_path)):
            return False, "无法删除非本地仓库目录中的仓库"

        # 权限检查（使用新的权限服务）
        has_permission, message = self._permission_service.check_operation_permission(
            self._current_session_id, 
            str(repo_path), 
            "delete"
        )
        
        if not has_permission:
            return False, message
            
        try:
            shutil.rmtree(repo_path)
            return True, f"已删除本地仓库: {repo_path.name}"
        except Exception as e:
            logger.error(f"删除本地仓库失败: {str(e)}")
            return False, f"删除仓库失败: {str(e)}"
    
    def get_repo_permissions(self, repo_path: str) -> Dict:
        """
        获取仓库权限信息
        
        Args:
            repo_path: 本地仓库路径
            
        Returns:
            Dict: 仓库权限信息
        """
        if not repo_path:
            return {}
            
        repo_id = self._permission_service.generate_repo_id(repo_path)
        
        # 获取仓库设置
        settings = self._permission_service.get_repo_settings(repo_id)
        
        # 获取保护规则
        protection_rules = self._permission_service.get_protection_rules(repo_id)
        
        # 获取审计日志
        audit_logs = self._permission_service.get_audit_logs(repo_id, limit=20)
        
        return {
            "repo_id": repo_id,
            "role_assignments": settings.get("role_assignments", {}),
            "protection_rules": protection_rules,
            "audit_logs": audit_logs
        }
    
    def update_repo_protection(self, repo_path: str, rules: Dict) -> Tuple[bool, str]:
        """
        更新仓库保护规则
        
        Args:
            repo_path: 本地仓库路径
            rules: 保护规则
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        if not self._current_session_id:
            return False, "未设置会话ID"
            
        repo_id = self._permission_service.generate_repo_id(repo_path)
        
        # 检查是否有管理员权限
        if self._permission_service.get_user_role(repo_id, self._current_session_id) != "admin":
            return False, "只有管理员可以修改仓库保护规则"
        
        # 更新保护规则
        success = True
        for rule_name, rule_value in rules.items():
            if not self._permission_service.set_protection_rule(repo_id, rule_name, rule_value):
                success = False
        
        return success, "保护规则已更新" if success else "部分保护规则更新失败"
    
    def update_user_role(self, repo_path: str, user_id: str, role: str) -> Tuple[bool, str]:
        """
        更新用户角色
        
        Args:
            repo_path: 本地仓库路径
            user_id: 用户ID
            role: 角色名称
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        if not self._current_session_id:
            return False, "未设置会话ID"
            
        repo_id = self._permission_service.generate_repo_id(repo_path)
        
        # 检查是否有管理员权限
        if self._permission_service.get_user_role(repo_id, self._current_session_id) != "admin":
            return False, "只有管理员可以修改用户角色"
        
        # 更新用户角色
        if self._permission_service.assign_role(repo_id, user_id, role):
            return True, f"用户角色已更新为 {role}"
        else:
            return False, "用户角色更新失败"

# 单例实例
_instance = None

def get_instance() -> RepoManager:
    """获取仓库管理器实例"""
    global _instance
    if _instance is None:
        _instance = RepoManager()
    return _instance 