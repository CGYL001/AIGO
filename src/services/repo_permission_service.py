"""
仓库权限管理服务

管理代码仓库相关的权限控制、角色管理和操作审计
"""

import os
import json
import time
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.utils import config
from src.database.models import (
    get_session, User, Repository, UserPermission,
    TeamPermission, ProtectionRule, AuditLog, Team
)
from src.services.user_service import get_instance as get_user_service

logger = logging.getLogger(__name__)

class RepoPermissionService:
    """
    仓库权限管理服务
    
    提供仓库级别的权限管理功能，包括：
    - 角色权限控制（管理员、开发者、只读用户）
    - 操作审计日志
    - 仓库特定的权限设置
    - 保护规则管理
    """
    
    # 预定义角色及其权限
    ROLES = {
        "admin": {
            "description": "仓库管理员，拥有所有权限",
            "permissions": ["clone", "pull", "push", "delete", "modify_settings"]
        },
        "developer": {
            "description": "开发者，可以克隆、拉取和推送，但不能删除仓库或修改设置",
            "permissions": ["clone", "pull", "push"]
        },
        "reader": {
            "description": "只读用户，只能克隆和拉取代码",
            "permissions": ["clone", "pull"]
        }
    }
    
    # 操作类型
    OPERATIONS = {
        "clone": "克隆仓库",
        "pull": "拉取更新",
        "push": "推送更改",
        "delete": "删除仓库",
        "modify_settings": "修改仓库设置"
    }
    
    # 保护规则类型
    RULE_TYPES = {
        "require_review": "需要代码审查",
        "protected_branch": "保护分支",
        "block_force_push": "阻止强制推送"
    }
    
    def __init__(self):
        """初始化仓库权限服务"""
        # 加载配置
        self._repo_config = config.get("repository_integration", {})
        self._permission_config = self._repo_config.get("permissions", {})
        
        # 默认角色
        self._default_role = self._permission_config.get("default_role", "reader")
        
        # 仓库设置缓存
        self._repo_settings = {}
        
        # 用户服务
        self._user_service = get_user_service()
        
        # 初始化数据库（确保表已创建）
        self._init_database()
    
    def _init_database(self):
        """确保必要的数据库表已创建"""
        from src.database.models import init_database
        init_database()
        
    def get_repository_by_path(self, repo_path: str) -> Optional[Repository]:
        """根据仓库路径获取仓库信息"""
        try:
            with get_session() as session:
                return session.query(Repository).filter(Repository.repo_path == repo_path).first()
        except Exception as e:
            logger.error(f"获取仓库信息失败: {str(e)}")
            return None
    
    def get_repository_by_id(self, repo_id: str) -> Optional[Repository]:
        """根据仓库ID获取仓库信息"""
        try:
            with get_session() as session:
                return session.query(Repository).filter(Repository.repo_id == repo_id).first()
        except Exception as e:
            logger.error(f"获取仓库信息失败: {str(e)}")
            return None
    
    def register_repository(self, repo_path: str, name: str = None, description: str = None,
                           owner_id: int = None, platform: str = None, remote_url: str = None) -> Optional[Repository]:
        """
        注册仓库
        
        Args:
            repo_path: 仓库路径
            name: 仓库名称
            description: 描述
            owner_id: 拥有者用户ID
            platform: 代码平台
            remote_url: 远程URL
            
        Returns:
            Repository: 仓库对象
        """
        try:
            # 生成仓库ID
            repo_id = self.generate_repo_id(repo_path)
            
            # 仓库名称默认为目录名
            if not name:
                name = os.path.basename(repo_path)
            
            with get_session() as session:
                # 检查仓库是否已存在
                existing = session.query(Repository).filter(
                    or_(
                        Repository.repo_path == repo_path,
                        Repository.repo_id == repo_id
                    )
                ).first()
                
                if existing:
                    # 更新现有仓库信息
                    if name:
                        existing.name = name
                    if description:
                        existing.description = description
                    if platform:
                        existing.platform = platform
                    if remote_url:
                        existing.remote_url = remote_url
                    if owner_id and not existing.owner_id:
                        existing.owner_id = owner_id
                    
                    existing.updated_at = datetime.utcnow()
                    session.commit()
                    return existing
                
                # 创建新仓库
                new_repo = Repository(
                    repo_id=repo_id,
                    repo_path=repo_path,
                    name=name,
                    description=description,
                    owner_id=owner_id,
                    platform=platform,
                    remote_url=remote_url
                )
                
                session.add(new_repo)
                session.commit()
                
                # 如果指定了拥有者，自动授予管理员权限
                if owner_id:
                    self.assign_role(repo_id, owner_id, "admin")
                
                # 创建默认保护规则
                self._create_default_protection_rules(repo_id)
                
                return new_repo
        
        except Exception as e:
            logger.error(f"注册仓库失败: {str(e)}")
            return None
    
    def _create_default_protection_rules(self, repo_id: str):
        """创建默认保护规则"""
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return
                
            with get_session() as session:
                # 创建保护分支规则
                for branch in ["main", "master"]:
                    rule = ProtectionRule(
                        repository_id=repo.id,
                        rule_type="protected_branch",
                        target=branch,
                        enabled=True
                    )
                    session.add(rule)
                
                # 创建强制推送阻止规则
                rule = ProtectionRule(
                    repository_id=repo.id,
                    rule_type="block_force_push",
                    enabled=True
                )
                session.add(rule)
                
                # 创建代码审查规则
                rule = ProtectionRule(
                    repository_id=repo.id,
                    rule_type="require_review",
                    enabled=False
                )
                session.add(rule)
                
                session.commit()
        except Exception as e:
            logger.error(f"创建默认保护规则失败: {str(e)}")
    
    def generate_repo_id(self, repo_path: str) -> str:
        """
        生成仓库ID
        
        Args:
            repo_path: 仓库路径
            
        Returns:
            str: 仓库ID
        """
        import hashlib
        # 使用路径生成唯一ID
        md5 = hashlib.md5(repo_path.encode()).hexdigest()
        return md5[:12]  # 使用前12位作为ID
    
    def assign_role(self, repo_id: str, user_id: int, role: str) -> bool:
        """
        分配用户角色
        
        Args:
            repo_id: 仓库ID
            user_id: 用户ID
            role: 角色名称
            
        Returns:
            bool: 是否成功分配
        """
        if role not in self.ROLES:
            logger.error(f"无效的角色: {role}")
            return False
            
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return False
                
            with get_session() as session:
                # 检查是否已存在权限记录
                perm = session.query(UserPermission).filter(
                    and_(
                        UserPermission.repository_id == repo.id,
                        UserPermission.user_id == user_id
                    )
                ).first()
                
                if perm:
                    # 更新现有权限
                    perm.role = role
                else:
                    # 创建新权限
                    perm = UserPermission(
                        repository_id=repo.id,
                        user_id=user_id,
                        role=role
                    )
                    session.add(perm)
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"分配用户角色失败: {str(e)}")
            return False
    
    def assign_team_role(self, repo_id: str, team_id: int, role: str) -> bool:
        """
        分配团队角色
        
        Args:
            repo_id: 仓库ID
            team_id: 团队ID
            role: 角色名称
            
        Returns:
            bool: 是否成功分配
        """
        if role not in self.ROLES:
            logger.error(f"无效的角色: {role}")
            return False
            
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return False
                
            with get_session() as session:
                # 检查团队是否存在
                team = session.query(Team).filter(Team.id == team_id).first()
                if not team:
                    return False
                
                # 检查是否已存在权限记录
                perm = session.query(TeamPermission).filter(
                    and_(
                        TeamPermission.repository_id == repo.id,
                        TeamPermission.team_id == team_id
                    )
                ).first()
                
                if perm:
                    # 更新现有权限
                    perm.role = role
                else:
                    # 创建新权限
                    perm = TeamPermission(
                        repository_id=repo.id,
                        team_id=team_id,
                        role=role
                    )
                    session.add(perm)
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"分配团队角色失败: {str(e)}")
            return False
    
    def remove_user_role(self, repo_id: str, user_id: int) -> bool:
        """移除用户角色"""
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return False
                
            with get_session() as session:
                perm = session.query(UserPermission).filter(
                    and_(
                        UserPermission.repository_id == repo.id,
                        UserPermission.user_id == user_id
                    )
                ).first()
                
                if perm:
                    session.delete(perm)
                    session.commit()
                
                return True
        except Exception as e:
            logger.error(f"移除用户角色失败: {str(e)}")
            return False
    
    def remove_team_role(self, repo_id: str, team_id: int) -> bool:
        """移除团队角色"""
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return False
                
            with get_session() as session:
                perm = session.query(TeamPermission).filter(
                    and_(
                        TeamPermission.repository_id == repo.id,
                        TeamPermission.team_id == team_id
                    )
                ).first()
                
                if perm:
                    session.delete(perm)
                    session.commit()
                
                return True
        except Exception as e:
            logger.error(f"移除团队角色失败: {str(e)}")
            return False
    
    def get_user_role(self, repo_id: str, user_id: int) -> str:
        """
        获取用户在仓库中的角色
        
        Args:
            repo_id: 仓库ID
            user_id: 用户ID
            
        Returns:
            str: 角色名称
        """
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return self._default_role
                
            with get_session() as session:
                # 检查用户直接权限
                user_perm = session.query(UserPermission).filter(
                    and_(
                        UserPermission.repository_id == repo.id,
                        UserPermission.user_id == user_id
                    )
                ).first()
                
                if user_perm:
                    return user_perm.role
                
                # 检查用户所属团队权限
                team_perms = session.query(TeamPermission, Team).join(
                    Team, TeamPermission.team_id == Team.id
                ).filter(
                    TeamPermission.repository_id == repo.id
                ).all()
                
                # 获取用户的团队
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return self._default_role
                    
                # 如果用户在多个团队，选择权限最高的
                highest_role = self._default_role
                role_priority = {"admin": 3, "developer": 2, "reader": 1}
                
                for team_perm, team in team_perms:
                    if team in user.teams:
                        team_role = team_perm.role
                        if role_priority.get(team_role, 0) > role_priority.get(highest_role, 0):
                            highest_role = team_role
                
                return highest_role
                
        except Exception as e:
            logger.error(f"获取用户角色失败: {str(e)}")
            return self._default_role
    
    def get_team_role(self, repo_id: str, team_id: int) -> str:
        """获取团队在仓库中的角色"""
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return self._default_role
                
            with get_session() as session:
                perm = session.query(TeamPermission).filter(
                    and_(
                        TeamPermission.repository_id == repo.id,
                        TeamPermission.team_id == team_id
                    )
                ).first()
                
                if perm:
                    return perm.role
                    
                return self._default_role
                
        except Exception as e:
            logger.error(f"获取团队角色失败: {str(e)}")
            return self._default_role
    
    def list_user_permissions(self, repo_id: str) -> List[Dict]:
        """列出仓库的所有用户权限"""
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return []
                
            with get_session() as session:
                perms = session.query(UserPermission, User).join(
                    User, UserPermission.user_id == User.id
                ).filter(
                    UserPermission.repository_id == repo.id
                ).all()
                
                result = []
                for perm, user in perms:
                    result.append({
                        "user_id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "email": user.email,
                        "role": perm.role,
                        "custom_permissions": perm.get_custom_permissions()
                    })
                    
                return result
                
        except Exception as e:
            logger.error(f"列出用户权限失败: {str(e)}")
            return []
    
    def list_team_permissions(self, repo_id: str) -> List[Dict]:
        """列出仓库的所有团队权限"""
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return []
                
            with get_session() as session:
                perms = session.query(TeamPermission, Team).join(
                    Team, TeamPermission.team_id == Team.id
                ).filter(
                    TeamPermission.repository_id == repo.id
                ).all()
                
                result = []
                for perm, team in perms:
                    result.append({
                        "team_id": team.id,
                        "team_name": team.name,
                        "description": team.description,
                        "role": perm.role,
                        "custom_permissions": perm.get_custom_permissions(),
                        "member_count": len(team.members)
                    })
                    
                return result
                
        except Exception as e:
            logger.error(f"列出团队权限失败: {str(e)}")
            return []
    
    def has_permission(self, repo_id: str, user_id: int, operation: str) -> bool:
        """
        检查用户是否有权限执行操作
        
        Args:
            repo_id: 仓库ID
            user_id: 用户ID
            operation: 操作类型
            
        Returns:
            bool: 是否有权限
        """
        if operation not in self.OPERATIONS:
            logger.warning(f"未知的操作类型: {operation}")
            return False
            
        # 获取用户角色
        role = self.get_user_role(repo_id, user_id)
        
        # 检查角色是否有此操作权限
        if role in self.ROLES and operation in self.ROLES[role]["permissions"]:
            return True
            
        # 检查用户自定义权限
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return False
                
            with get_session() as session:
                # 检查用户直接权限
                user_perm = session.query(UserPermission).filter(
                    and_(
                        UserPermission.repository_id == repo.id,
                        UserPermission.user_id == user_id
                    )
                ).first()
                
                if user_perm and user_perm.custom_permissions:
                    custom_perms = user_perm.get_custom_permissions()
                    if operation in custom_perms:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查用户权限失败: {str(e)}")
            return False
    
    def set_custom_permission(self, repo_id: str, user_id: int, operation: str, granted: bool) -> bool:
        """
        设置用户自定义权限
        
        Args:
            repo_id: 仓库ID
            user_id: 用户ID
            operation: 操作类型
            granted: 是否授予权限
            
        Returns:
            bool: 是否成功设置
        """
        if operation not in self.OPERATIONS:
            logger.warning(f"未知的操作类型: {operation}")
            return False
            
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return False
                
            with get_session() as session:
                # 获取用户权限记录
                perm = session.query(UserPermission).filter(
                    and_(
                        UserPermission.repository_id == repo.id,
                        UserPermission.user_id == user_id
                    )
                ).first()
                
                if not perm:
                    # 如果用户没有权限记录，创建一个默认记录
                    perm = UserPermission(
                        repository_id=repo.id,
                        user_id=user_id,
                        role=self._default_role
                    )
                    session.add(perm)
                
                # 更新自定义权限
                custom_perms = perm.get_custom_permissions()
                
                if granted and operation not in custom_perms:
                    custom_perms.append(operation)
                elif not granted and operation in custom_perms:
                    custom_perms.remove(operation)
                
                perm.set_custom_permissions(custom_perms)
                session.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"设置自定义权限失败: {str(e)}")
            return False
    
    def check_operation_permission(self, session_id: str, repo_path: str, operation: str) -> Tuple[bool, str]:
        """
        检查会话是否有权限执行操作
        
        Args:
            session_id: 会话ID
            repo_path: 仓库路径
            operation: 操作类型
            
        Returns:
            (是否有权限, 消息)
        """
        # 验证会话
        valid, user_id = self._user_service.validate_session(session_id)
        
        if not valid:
            return False, "无效的会话，请重新登录"
            
        # 查找仓库
        repo = self.get_repository_by_path(repo_path)
        if not repo:
            # 如果仓库不存在，尝试注册
            repo = self.register_repository(repo_path)
            if not repo:
                return False, f"无法访问仓库: {repo_path}"
                
        # 检查权限
        if not self.has_permission(repo.repo_id, user_id, operation):
            role = self.get_user_role(repo.repo_id, user_id)
            return False, f"当前角色 '{role}' 没有权限执行 '{self.OPERATIONS.get(operation, operation)}' 操作"
        
        # 检查保护规则
        if operation == "push":
            # 推送时可能需要检查分支保护规则
            # 这里只是示例，实际需要根据参数知道要推送的分支
            can_push, msg = self.check_protection_rule(repo.repo_id, "block_force_push")
            if not can_push:
                return False, msg
        
        # 记录审计日志
        self.log_operation(repo.repo_id, user_id, operation)
        
        return True, "操作已授权"
    
    def log_operation(self, repo_id: str, user_id: int, operation: str, details: Dict = None, target: str = None) -> bool:
        """
        记录操作审计日志
        
        Args:
            repo_id: 仓库ID
            user_id: 用户ID
            operation: 操作类型
            details: 详细信息
            target: 操作目标（如分支名）
            
        Returns:
            bool: 是否成功记录
        """
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return False
                
            with get_session() as session:
                # 创建审计日志
                log = AuditLog(
                    user_id=user_id,
                    repository_id=repo.id,
                    operation=operation,
                    operation_description=self.OPERATIONS.get(operation, operation),
                    target=target
                )
                
                if details:
                    log.set_details(details)
                    
                session.add(log)
                session.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"记录审计日志失败: {str(e)}")
            return False
    
    def get_audit_logs(self, repo_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        获取仓库审计日志
        
        Args:
            repo_id: 仓库ID
            limit: 返回记录数量限制
            offset: 记录偏移量
            
        Returns:
            List[Dict]: 审计日志列表
        """
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return []
                
            with get_session() as session:
                # 查询审计日志，关联用户信息
                logs = session.query(AuditLog, User).outerjoin(
                    User, AuditLog.user_id == User.id
                ).filter(
                    AuditLog.repository_id == repo.id
                ).order_by(
                    AuditLog.created_at.desc()
                ).offset(offset).limit(limit).all()
                
                # 格式化结果
                result = []
                for log, user in logs:
                    log_data = log.to_dict()
                    if user:
                        log_data["user"] = {
                            "username": user.username,
                            "full_name": user.full_name
                        }
                    result.append(log_data)
                
                return result
                
        except Exception as e:
            logger.error(f"获取审计日志失败: {str(e)}")
            return []
    
    def set_protection_rule(self, repo_id: str, rule_type: str, 
                           enabled: bool = None, target: str = None,
                           config: Dict = None) -> bool:
        """
        设置保护规则
        
        Args:
            repo_id: 仓库ID
            rule_type: 规则类型
            enabled: 是否启用
            target: 目标（如分支名）
            config: 配置参数
            
        Returns:
            bool: 是否成功设置
        """
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return False
                
            with get_session() as session:
                # 查找现有规则
                query = session.query(ProtectionRule).filter(
                    and_(
                        ProtectionRule.repository_id == repo.id,
                        ProtectionRule.rule_type == rule_type
                    )
                )
                
                if target:
                    query = query.filter(ProtectionRule.target == target)
                    
                rule = query.first()
                
                if not rule:
                    # 创建新规则
                    rule = ProtectionRule(
                        repository_id=repo.id,
                        rule_type=rule_type,
                        target=target,
                        enabled=enabled if enabled is not None else True
                    )
                    session.add(rule)
                else:
                    # 更新现有规则
                    if enabled is not None:
                        rule.enabled = enabled
                    if target is not None:
                        rule.target = target
                
                # 更新配置
                if config:
                    current_config = rule.get_config()
                    current_config.update(config)
                    rule.set_config(current_config)
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"设置保护规则失败: {str(e)}")
            return False
    
    def get_protection_rules(self, repo_id: str) -> List[Dict]:
        """
        获取仓库保护规则
        
        Args:
            repo_id: 仓库ID
            
        Returns:
            List[Dict]: 保护规则列表
        """
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return []
                
            with get_session() as session:
                rules = session.query(ProtectionRule).filter(
                    ProtectionRule.repository_id == repo.id
                ).all()
                
                return [rule.to_dict() for rule in rules]
                
        except Exception as e:
            logger.error(f"获取保护规则失败: {str(e)}")
            return []
    
    def check_protection_rule(self, repo_id: str, rule_type: str, params: Dict = None) -> Tuple[bool, str]:
        """
        检查保护规则
        
        Args:
            repo_id: 仓库ID
            rule_type: 规则类型
            params: 参数（如分支名）
            
        Returns:
            (是否通过, 消息)
        """
        try:
            repo = self.get_repository_by_id(repo_id)
            if not repo:
                return True, "仓库不存在，跳过规则检查"
                
            with get_session() as session:
                # 查找特定类型的规则
                rules = session.query(ProtectionRule).filter(
                    and_(
                        ProtectionRule.repository_id == repo.id,
                        ProtectionRule.rule_type == rule_type,
                        ProtectionRule.enabled == True
                    )
                ).all()
                
                if not rules:
                    return True, "没有相关保护规则"
                
                # 处理不同类型的规则
                if rule_type == "protected_branch" and params and 'branch' in params:
                    branch = params['branch']
                    
                    for rule in rules:
                        if rule.target == branch:
                            return False, f"分支 '{branch}' 受保护，不允许直接推送"
                
                elif rule_type == "block_force_push" and params and 'force' in params:
                    if params['force']:
                        for rule in rules:
                            if rule.enabled:
                                return False, "强制推送已被禁止"
                
                elif rule_type == "require_review" and params and 'branch' in params:
                    branch = params['branch']
                    
                    for rule in rules:
                        if not rule.target or rule.target == branch:
                            return False, f"分支 '{branch}' 的更改需要代码审查"
                
                return True, "通过保护规则检查"
                
        except Exception as e:
            logger.error(f"检查保护规则失败: {str(e)}")
            return True, f"规则检查错误: {str(e)}"

# 单例实例
_instance = None

def get_instance() -> RepoPermissionService:
    """获取仓库权限服务实例"""
    global _instance
    if _instance is None:
        _instance = RepoPermissionService()
    return _instance 