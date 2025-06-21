#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代码仓库管理器模块

提供代码仓库集成功能，支持GitHub、GitLab等平台
"""

import os
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class RepoManager:
    """代码仓库管理器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化代码仓库管理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.repo_path = self.config.get("repo_path", ".")
        self.platforms = {}
        
        # 初始化平台适配器
        self._init_platform_adapters()
        
        logger.info("代码仓库管理器初始化完成")
    
    def _init_platform_adapters(self):
        """初始化平台适配器"""
        try:
            # 尝试导入GitHub适配器
            from .platform.github_adapter import GitHubAdapter
            self.platforms["github"] = GitHubAdapter(self.config.get("github", {}))
            logger.info("已加载GitHub适配器")
        except ImportError:
            logger.warning("无法导入GitHub适配器")
        except Exception as e:
            logger.error(f"初始化GitHub适配器失败: {str(e)}")
        
        try:
            # 尝试导入GitLab适配器
            from .platform.gitlab_adapter import GitLabAdapter
            self.platforms["gitlab"] = GitLabAdapter(self.config.get("gitlab", {}))
            logger.info("已加载GitLab适配器")
        except ImportError:
            logger.warning("无法导入GitLab适配器")
        except Exception as e:
            logger.error(f"初始化GitLab适配器失败: {str(e)}")
        
        try:
            # 尝试导入Gitee适配器
            from .platform.gitee_adapter import GiteeAdapter
            self.platforms["gitee"] = GiteeAdapter(self.config.get("gitee", {}))
            logger.info("已加载Gitee适配器")
        except ImportError:
            logger.warning("无法导入Gitee适配器")
        except Exception as e:
            logger.error(f"初始化Gitee适配器失败: {str(e)}")
    
    def get_repo_info(self) -> Dict[str, Any]:
        """获取仓库信息
        
        Returns:
            Dict[str, Any]: 仓库信息
        """
        try:
            # 检查是否是Git仓库
            if not os.path.exists(os.path.join(self.repo_path, ".git")):
                logger.warning(f"路径不是Git仓库: {self.repo_path}")
                return {"error": "不是Git仓库"}
            
            # 获取远程仓库URL
            remote_url = self._run_git_command(["config", "--get", "remote.origin.url"])
            
            # 获取当前分支
            current_branch = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
            
            # 获取最近提交
            last_commit = self._run_git_command(["log", "-1", "--pretty=format:%H|%an|%ae|%s|%cd", "--date=iso"])
            commit_parts = last_commit.split("|")
            
            commit_info = {}
            if len(commit_parts) >= 5:
                commit_info = {
                    "hash": commit_parts[0],
                    "author": commit_parts[1],
                    "email": commit_parts[2],
                    "message": commit_parts[3],
                    "date": commit_parts[4]
                }
            
            # 获取未提交的更改数量
            status = self._run_git_command(["status", "--porcelain"])
            changes = len([line for line in status.split("\n") if line.strip()])
            
            return {
                "repo_path": self.repo_path,
                "remote_url": remote_url,
                "current_branch": current_branch,
                "last_commit": commit_info,
                "uncommitted_changes": changes
            }
        except Exception as e:
            logger.error(f"获取仓库信息失败: {str(e)}")
            return {"error": str(e)}
    
    def _run_git_command(self, args: List[str]) -> str:
        """运行Git命令
        
        Args:
            args: 命令参数
        
        Returns:
            str: 命令输出
        
        Raises:
            Exception: 命令执行失败
        """
        try:
            cmd = ["git"] + args
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                check=True,
                text=True,
                capture_output=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git命令失败: {e.stderr}")
            raise Exception(f"Git命令失败: {e.stderr}")
        except Exception as e:
            logger.error(f"执行Git命令时出错: {str(e)}")
            raise
    
    def get_file_history(self, file_path: str, max_entries: int = 10) -> List[Dict[str, Any]]:
        """获取文件历史
        
        Args:
            file_path: 文件路径
            max_entries: 最大条目数
        
        Returns:
            List[Dict[str, Any]]: 历史记录
        """
        try:
            # 获取文件的提交历史
            log_format = "--pretty=format:%H|%an|%ae|%s|%cd"
            log_cmd = ["log", log_format, "--date=iso", "-n", str(max_entries), "--", file_path]
            log_output = self._run_git_command(log_cmd)
            
            history = []
            for line in log_output.split("\n"):
                if not line.strip():
                    continue
                
                parts = line.split("|")
                if len(parts) >= 5:
                    history.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "message": parts[3],
                        "date": parts[4]
                    })
            
            return history
        except Exception as e:
            logger.error(f"获取文件历史失败: {str(e)}")
            return []
    
    def get_diff(self, file_path: str, commit_hash: Optional[str] = None) -> str:
        """获取文件差异
        
        Args:
            file_path: 文件路径
            commit_hash: 提交哈希，如果为None则获取工作区与最新提交的差异
        
        Returns:
            str: 差异内容
        """
        try:
            if commit_hash:
                # 获取指定提交与其父提交的差异
                diff_cmd = ["diff", f"{commit_hash}^", commit_hash, "--", file_path]
            else:
                # 获取工作区与最新提交的差异
                diff_cmd = ["diff", "HEAD", "--", file_path]
            
            return self._run_git_command(diff_cmd)
        except Exception as e:
            logger.error(f"获取差异失败: {str(e)}")
            return f"获取差异失败: {str(e)}"
    
    def get_blame(self, file_path: str) -> List[Dict[str, Any]]:
        """获取文件责任人信息
        
        Args:
            file_path: 文件路径
        
        Returns:
            List[Dict[str, Any]]: 责任人信息
        """
        try:
            # 获取文件的责任人信息
            blame_cmd = ["blame", "--line-porcelain", file_path]
            blame_output = self._run_git_command(blame_cmd)
            
            # 解析输出
            blame_info = []
            current_info = {}
            
            for line in blame_output.split("\n"):
                if not line.strip():
                    continue
                
                if line.startswith("author "):
                    current_info["author"] = line[7:]
                elif line.startswith("author-mail "):
                    current_info["email"] = line[12:]
                elif line.startswith("author-time "):
                    current_info["time"] = line[12:]
                elif line.startswith("summary "):
                    current_info["summary"] = line[8:]
                    blame_info.append(current_info.copy())
                    current_info = {}
            
            return blame_info
        except Exception as e:
            logger.error(f"获取责任人信息失败: {str(e)}")
            return []
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> bool:
        """创建分支
        
        Args:
            branch_name: 分支名称
            base_branch: 基础分支
        
        Returns:
            bool: 是否成功
        """
        try:
            # 确保基础分支是最新的
            self._run_git_command(["fetch", "origin", base_branch])
            
            # 创建新分支
            self._run_git_command(["checkout", "-b", branch_name, f"origin/{base_branch}"])
            
            logger.info(f"已创建分支: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"创建分支失败: {str(e)}")
            return False
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """提交更改
        
        Args:
            message: 提交消息
            files: 要提交的文件列表，如果为None则提交所有更改
        
        Returns:
            bool: 是否成功
        """
        try:
            # 添加文件
            if files:
                for file in files:
                    self._run_git_command(["add", file])
            else:
                self._run_git_command(["add", "."])
            
            # 提交更改
            self._run_git_command(["commit", "-m", message])
            
            logger.info(f"已提交更改: {message}")
            return True
        except Exception as e:
            logger.error(f"提交更改失败: {str(e)}")
            return False
    
    def push_changes(self, branch_name: Optional[str] = None) -> bool:
        """推送更改
        
        Args:
            branch_name: 分支名称，如果为None则使用当前分支
        
        Returns:
            bool: 是否成功
        """
        try:
            if branch_name:
                self._run_git_command(["push", "origin", branch_name])
            else:
                self._run_git_command(["push"])
            
            logger.info("已推送更改")
            return True
        except Exception as e:
            logger.error(f"推送更改失败: {str(e)}")
            return False

# 创建单例实例
repo_manager = RepoManager() 