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
import time
import functools
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime

from src.utils import config
from src.services import auth_service
from src.services.repo_permission_service import get_instance as get_repo_permission_service
from src.utils.async_utils import retry

# 导入平台适配器
from .platform.github_adapter import GitHubAdapter
from .platform.gitlab_adapter import GitLabAdapter
from .platform.gitee_adapter import GiteeAdapter

logger = logging.getLogger(__name__)

class RepoManager:
    """
    仓库管理器
    
    管理代码仓库的克隆、拉取、推送等操作
    """
    
    def __init__(self, auth_service=None, repo_permission_service=None):
        """
        初始化仓库管理器
        
        Args:
            auth_service: 认证服务，如果为None则使用默认服务
            repo_permission_service: 仓库权限服务，如果为None则使用默认服务
        """
        self._auth_service = auth_service or auth_service
        self._repo_permission_service = repo_permission_service or get_repo_permission_service()
        
        # 设置仓库本地存储路径
        self._local_repo_path = Path(config.get("repository_integration.local_repo_path", "data/repositories"))
        self._settings_path = Path(config.get("repository_integration.settings_path", "data/repositories/settings"))
        self._audit_log_path = Path(config.get("repository_integration.audit_log_path", "data/repositories/audit"))
        
        # 确保目录存在
        self._local_repo_path.mkdir(parents=True, exist_ok=True)
        self._settings_path.mkdir(parents=True, exist_ok=True)
        self._audit_log_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化平台适配器
        self._adapters = {}
        self._init_adapters()
        
        # 当前会话ID，用于权限管理
        self._current_session_id = None
        
        logger.info(f"仓库管理器初始化完成，支持的平台: {', '.join(self._adapters.keys())}")
    
    def _init_adapters(self):
        """初始化平台适配器"""
        # 获取平台配置
        platforms_config = config.get("repository_integration.platforms", {})
        
        # 初始化GitHub适配器
        if platforms_config.get("github", {}).get("enabled", True):
            self._adapters["github"] = GitHubAdapter()
        
        # 初始化GitLab适配器
        if platforms_config.get("gitlab", {}).get("enabled", True):
            self._adapters["gitlab"] = GitLabAdapter()
        
        # 初始化Gitee适配器
        if platforms_config.get("gitee", {}).get("enabled", True):
            self._adapters["gitee"] = GiteeAdapter()
    
    def set_session_id(self, session_id: str):
        """
        设置当前会话ID
        
        Args:
            session_id: 会话ID
        """
        self._current_session_id = session_id
    
    def get_platforms(self) -> List[str]:
        """
        获取支持的平台列表
        
        Returns:
            List[str]: 平台列表
        """
        return list(self._adapters.keys())
    
    def is_platform_supported(self, platform: str) -> bool:
        """
        检查平台是否支持
        
        Args:
            platform: 平台名称
            
        Returns:
            bool: 是否支持
        """
        return platform.lower() in self._adapters
    
    def get_platform_info(self, platform: str) -> Dict[str, Any]:
        """
        获取平台信息
        
        Args:
            platform: 平台名称
            
        Returns:
            Dict[str, Any]: 平台信息
        """
        if not self.is_platform_supported(platform):
            return {"name": platform, "api_url": "", "authenticated": False}
            
        adapter = self._adapters[platform.lower()]
        return {
            "name": adapter.get_platform_name(),
            "api_url": adapter.get_api_url(),
            "authenticated": adapter.is_authenticated()
        }
    
    @retry(max_attempts=3, delay=2)
    async def authenticate(self, platform: str, credentials: Dict[str, str]) -> Tuple[bool, str]:
        """
        平台认证
        
        Args:
            platform: 平台名称
            credentials: 认证凭据
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        if not self.is_platform_supported(platform):
            return False, f"不支持的平台: {platform}"
            
        adapter = self._adapters[platform.lower()]
        return await adapter.authenticate(credentials)
    
    @retry(max_attempts=3, delay=2)
    async def list_repositories(self, platform: str, username: Optional[str] = None) -> Tuple[bool, Any]:
        """
        列出仓库
        
        Args:
            platform: 平台名称
            username: 用户名，如果为None则列出当前用户的仓库
            
        Returns:
            Tuple[bool, Any]: (是否成功, 仓库列表或错误信息)
        """
        if not self.is_platform_supported(platform):
            return False, f"不支持的平台: {platform}"
            
        adapter = self._adapters[platform.lower()]
        
        if not adapter.is_authenticated():
            return False, f"未认证平台: {platform}"
        
        try:
            repos = await adapter.list_repositories(username)
            return True, repos
        except Exception as e:
            logger.error(f"列出仓库失败: {str(e)}")
            return False, f"列出仓库失败: {str(e)}"
    
    @retry(max_attempts=3, delay=2)
    async def clone_repository(self, platform: str, repo_name: str, branch: str = None) -> Tuple[bool, str]:
        """
        克隆仓库
        
        Args:
            platform: 平台名称
            repo_name: 仓库名称 (格式: 用户名/仓库名)
            branch: 分支名，不指定则使用默认分支
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息或仓库路径)
        """
        if not self.is_platform_supported(platform):
            return False, f"不支持的平台: {platform}"
            
        adapter = self._adapters[platform.lower()]
        
        if not adapter.is_authenticated():
            return False, f"未认证平台: {platform}"
        
        # 获取仓库信息
        repo_info = await adapter.get_repository(repo_name)
        if not repo_info:
            return False, f"获取仓库 {repo_name} 信息失败"
        
        # 检查权限
        if not self._check_permission("clone_repository"):
            return False, "权限不足，无法克隆仓库"
        
        # 生成本地路径
        local_path = self._local_repo_path / platform / repo_name.replace("/", "_")
        
        # 如果目录已存在，先删除
        if local_path.exists():
            shutil.rmtree(local_path)
        
        # 创建父目录
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 获取克隆URL
        clone_url = repo_info.get("clone_url")
        if not clone_url:
            return False, f"无法获取仓库 {repo_name} 的克隆URL"
        
        # 构建克隆命令
        cmd = ["git", "clone", clone_url, str(local_path)]
        if branch:
            cmd.extend(["--branch", branch])
        
        try:
            # 执行克隆命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"克隆仓库失败: {stderr}")
                return False, f"克隆仓库失败: {stderr}"
            
            # 记录审计日志
            self._log_audit_event("clone_repository", {
                "platform": platform,
                "repo_name": repo_name,
                "branch": branch,
                "local_path": str(local_path)
            })
            
            return True, str(local_path)
        except Exception as e:
            logger.error(f"克隆仓库异常: {str(e)}")
            return False, f"克隆仓库异常: {str(e)}"
    
    @retry(max_attempts=3, delay=2)
    async def pull_repository(self, repo_path: str) -> Tuple[bool, str]:
        """
        拉取仓库更新
        
        Args:
            repo_path: 仓库路径
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        # 检查路径是否存在
        if not os.path.exists(repo_path):
            return False, f"仓库路径不存在: {repo_path}"
        
        # 检查是否为Git仓库
        if not os.path.exists(os.path.join(repo_path, ".git")):
            return False, f"不是有效的Git仓库: {repo_path}"
        
        # 检查权限
        if not self._check_permission("pull_repository"):
            return False, "权限不足，无法拉取仓库更新"
        
        try:
            # 执行拉取命令
            process = subprocess.Popen(
                ["git", "pull"],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"拉取仓库更新失败: {stderr}")
                return False, f"拉取仓库更新失败: {stderr}"
            
            # 记录审计日志
            self._log_audit_event("pull_repository", {
                "repo_path": repo_path,
                "result": stdout
            })
            
            return True, stdout
        except Exception as e:
            logger.error(f"拉取仓库更新异常: {str(e)}")
            return False, f"拉取仓库更新异常: {str(e)}"
    
    @retry(max_attempts=3, delay=2)
    async def push_repository(self, repo_path: str, commit_message: str = None) -> Tuple[bool, str]:
        """
        推送仓库更改
        
        Args:
            repo_path: 仓库路径
            commit_message: 提交信息，如果为None则使用默认信息
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        # 检查路径是否存在
        if not os.path.exists(repo_path):
            return False, f"仓库路径不存在: {repo_path}"
        
        # 检查是否为Git仓库
        if not os.path.exists(os.path.join(repo_path, ".git")):
            return False, f"不是有效的Git仓库: {repo_path}"
        
        # 检查权限
        if not self._check_permission("push_repository"):
            return False, "权限不足，无法推送仓库更改"
        
        # 设置默认提交信息
        if not commit_message:
            commit_message = f"更新于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            # 添加所有更改
            add_process = subprocess.Popen(
                ["git", "add", "."],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            add_stdout, add_stderr = add_process.communicate()
            
            if add_process.returncode != 0:
                logger.error(f"添加更改失败: {add_stderr}")
                return False, f"添加更改失败: {add_stderr}"
            
            # 提交更改
            commit_process = subprocess.Popen(
                ["git", "commit", "-m", commit_message],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            commit_stdout, commit_stderr = commit_process.communicate()
            
            # 如果没有更改，则直接返回
            if "nothing to commit" in commit_stderr:
                return True, "没有更改需要提交"
            
            if commit_process.returncode != 0 and "nothing to commit" not in commit_stderr:
                logger.error(f"提交更改失败: {commit_stderr}")
                return False, f"提交更改失败: {commit_stderr}"
            
            # 推送更改
            push_process = subprocess.Popen(
                ["git", "push"],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            push_stdout, push_stderr = push_process.communicate()
            
            if push_process.returncode != 0:
                logger.error(f"推送更改失败: {push_stderr}")
                return False, f"推送更改失败: {push_stderr}"
            
            # 记录审计日志
            self._log_audit_event("push_repository", {
                "repo_path": repo_path,
                "commit_message": commit_message
            })
            
            return True, "推送更改成功"
        except Exception as e:
            logger.error(f"推送仓库更改异常: {str(e)}")
            return False, f"推送仓库更改异常: {str(e)}"
    
    async def delete_repository(self, repo_path: str) -> Tuple[bool, str]:
        """
        删除本地仓库
        
        Args:
            repo_path: 仓库路径
            
        Returns:
            Tuple[bool, str]: (是否成功, 提示信息)
        """
        # 检查路径是否存在
        if not os.path.exists(repo_path):
            return False, f"仓库路径不存在: {repo_path}"
        
        # 检查是否为Git仓库
        if not os.path.exists(os.path.join(repo_path, ".git")):
            return False, f"不是有效的Git仓库: {repo_path}"
        
        # 检查权限
        if not self._check_permission("delete_repository"):
            return False, "权限不足，无法删除仓库"
        
        try:
            # 删除仓库目录
            shutil.rmtree(repo_path)
            
            # 记录审计日志
            self._log_audit_event("delete_repository", {
                "repo_path": repo_path
            })
            
            return True, "删除仓库成功"
        except Exception as e:
            logger.error(f"删除仓库异常: {str(e)}")
            return False, f"删除仓库异常: {str(e)}"
    
    async def list_local_repositories(self) -> List[Dict[str, Any]]:
        """
        列出本地仓库
        
        Returns:
            List[Dict[str, Any]]: 本地仓库列表
        """
        result = []
        
        # 遍历平台目录
        for platform_dir in self._local_repo_path.iterdir():
            if platform_dir.is_dir():
                platform = platform_dir.name
                
                # 遍历仓库目录
                for repo_dir in platform_dir.iterdir():
                    if repo_dir.is_dir() and (repo_dir / ".git").exists():
                        # 获取仓库信息
                        repo_info = {
                            "platform": platform,
                            "name": repo_dir.name,
                            "path": str(repo_dir),
                            "last_modified": datetime.fromtimestamp(repo_dir.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # 获取远程URL
                        try:
                            process = subprocess.Popen(
                                ["git", "config", "--get", "remote.origin.url"],
                                cwd=str(repo_dir),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            stdout, stderr = process.communicate()
                            
                            if process.returncode == 0:
                                repo_info["remote_url"] = stdout.strip()
                        except Exception:
                            pass
                        
                        result.append(repo_info)
        
        return result
    
    def _check_permission(self, operation: str) -> bool:
        """
        检查权限
        
        Args:
            operation: 操作名称
            
        Returns:
            bool: 是否有权限
        """
        if not self._current_session_id:
            logger.warning("未设置会话ID，无法检查权限")
            return False
            
        return self._repo_permission_service.check_permission(self._current_session_id, operation)
    
    def _log_audit_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        记录审计事件
        
        Args:
            event_type: 事件类型
            event_data: 事件数据
        """
        # 创建事件记录
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "session_id": self._current_session_id,
            "data": event_data
        }
        
        # 生成日志文件名
        log_file = self._audit_log_path / f"{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            # 读取现有日志
            events = []
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
            
            # 添加新事件
            events.append(event)
            
            # 写入日志文件
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"记录审计事件失败: {str(e)}")
    
    def get_audit_logs(self, start_date: datetime = None, end_date: datetime = None, 
                      event_type: str = None) -> List[Dict[str, Any]]:
        """
        获取审计日志
        
        Args:
            start_date: 开始日期，如果为None则不限制
            end_date: 结束日期，如果为None则使用当前日期
            event_type: 事件类型，如果为None则不限制
            
        Returns:
            List[Dict[str, Any]]: 审计日志列表
        """
        # 设置默认结束日期
        if end_date is None:
            end_date = datetime.now()
            
        # 如果未指定开始日期，则使用结束日期前30天
        if start_date is None:
            start_date = end_date - datetime.timedelta(days=30)
            
        # 获取日期范围内的所有日志文件
        log_files = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            log_file = self._audit_log_path / f"{current_date.strftime('%Y%m%d')}.json"
            if log_file.exists():
                log_files.append(log_file)
            current_date += datetime.timedelta(days=1)
            
        # 读取并过滤日志
        results = []
        for log_file in log_files:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
                    
                    for event in events:
                        # 解析时间戳
                        timestamp = datetime.fromisoformat(event["timestamp"])
                        
                        # 检查时间范围
                        if start_date <= timestamp <= end_date:
                            # 检查事件类型
                            if event_type is None or event["type"] == event_type:
                                results.append(event)
            except Exception as e:
                logger.error(f"读取审计日志失败: {str(e)}")
                
        return results

# 单例实例
_instance = None

def get_instance() -> RepoManager:
    """获取仓库管理器实例"""
    global _instance
    if _instance is None:
        _instance = RepoManager()
    return _instance 