"""
用户服务

管理用户账号、认证和API密钥
"""

import os
import time
import uuid
import secrets
import logging
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.utils import config
from src.database.models import User, ApiKey, get_session

logger = logging.getLogger(__name__)

class UserService:
    """
    用户服务
    
    提供用户账户管理、身份验证和API密钥管理功能
    """
    
    def __init__(self):
        """初始化用户服务"""
        self._user_config = config.get("user_management", {})
        
        # 会话缓存
        self._sessions = {}
        
    def create_user(self, username: str, email: str, password: str, full_name: str = None,
                    is_admin: bool = False) -> Tuple[bool, str, Optional[User]]:
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 电子邮件
            password: 密码（明文，将被加密）
            full_name: 全名
            is_admin: 是否为管理员
            
        Returns:
            (成功, 消息, 用户对象(如果成功))
        """
        try:
            with get_session() as session:
                # 检查用户名或邮箱是否已存在
                existing_user = session.query(User).filter(
                    or_(
                        User.username == username,
                        User.email == email
                    )
                ).first()
                
                if existing_user:
                    if existing_user.username == username:
                        return False, f"用户名 '{username}' 已被使用", None
                    return False, f"邮箱 '{email}' 已被使用", None
                    
                # 创建新用户
                password_hash = self._hash_password(password)
                
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    full_name=full_name,
                    is_admin=is_admin
                )
                
                session.add(new_user)
                session.commit()
                
                logger.info(f"创建新用户: {username}")
                return True, "用户创建成功", new_user
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            return False, f"创建用户失败: {str(e)}", None
    
    def authenticate(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户认证
        
        Args:
            username_or_email: 用户名或邮箱
            password: 密码
            
        Returns:
            (成功, 消息, 用户对象(如果成功))
        """
        try:
            with get_session() as session:
                # 查找用户
                user = session.query(User).filter(
                    or_(
                        User.username == username_or_email,
                        User.email == username_or_email
                    )
                ).first()
                
                if not user:
                    return False, "用户名或密码错误", None
                    
                # 检查用户状态
                if not user.is_active:
                    return False, "账户已被禁用", None
                
                # 验证密码
                if not self._verify_password(password, user.password_hash):
                    return False, "用户名或密码错误", None
                
                # 更新最后登录时间
                user.last_login = datetime.utcnow()
                session.commit()
                
                return True, "认证成功", user
        except Exception as e:
            logger.error(f"用户认证失败: {str(e)}")
            return False, f"认证失败: {str(e)}", None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """获取用户信息"""
        try:
            with get_session() as session:
                return session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            return None
            
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户信息"""
        try:
            with get_session() as session:
                return session.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> Tuple[bool, str]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段
            
        Returns:
            (成功, 消息)
        """
        allowed_fields = {'email', 'full_name', 'avatar_url', 'is_active', 'is_admin'}
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_data:
            return False, "没有提供有效的更新字段"
            
        try:
            with get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return False, f"用户ID {user_id} 不存在"
                
                # 如果要更新邮箱，检查是否已存在
                if 'email' in update_data:
                    existing = session.query(User).filter(
                        User.email == update_data['email'],
                        User.id != user_id
                    ).first()
                    
                    if existing:
                        return False, f"邮箱 '{update_data['email']}' 已被使用"
                
                # 更新用户字段
                for key, value in update_data.items():
                    setattr(user, key, value)
                
                session.commit()
                return True, "用户信息已更新"
        except Exception as e:
            logger.error(f"更新用户信息失败: {str(e)}")
            return False, f"更新失败: {str(e)}"
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改用户密码
        
        Args:
            user_id: 用户ID
            current_password: 当前密码
            new_password: 新密码
            
        Returns:
            (成功, 消息)
        """
        try:
            with get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return False, f"用户ID {user_id} 不存在"
                
                # 验证当前密码
                if not self._verify_password(current_password, user.password_hash):
                    return False, "当前密码错误"
                
                # 更新密码
                password_hash = self._hash_password(new_password)
                user.password_hash = password_hash
                
                session.commit()
                return True, "密码已更改"
        except Exception as e:
            logger.error(f"修改密码失败: {str(e)}")
            return False, f"修改密码失败: {str(e)}"
    
    def reset_password(self, user_id: int, new_password: str) -> Tuple[bool, str]:
        """
        重置用户密码（管理员操作）
        
        Args:
            user_id: 用户ID
            new_password: 新密码
            
        Returns:
            (成功, 消息)
        """
        try:
            with get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return False, f"用户ID {user_id} 不存在"
                
                # 更新密码
                password_hash = self._hash_password(new_password)
                user.password_hash = password_hash
                
                session.commit()
                return True, "密码已重置"
        except Exception as e:
            logger.error(f"重置密码失败: {str(e)}")
            return False, f"重置密码失败: {str(e)}"
    
    def list_users(self, offset: int = 0, limit: int = 100, query: str = None) -> List[User]:
        """
        获取用户列表
        
        Args:
            offset: 偏移量
            limit: 限制数量
            query: 搜索关键词
            
        Returns:
            用户列表
        """
        try:
            with get_session() as session:
                query_obj = session.query(User)
                
                if query:
                    query_obj = query_obj.filter(
                        or_(
                            User.username.ilike(f"%{query}%"),
                            User.email.ilike(f"%{query}%"),
                            User.full_name.ilike(f"%{query}%") if User.full_name else False
                        )
                    )
                
                return query_obj.order_by(User.username).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            return []
    
    def create_session(self, user_id: int) -> str:
        """
        创建用户会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            会话ID
        """
        session_id = str(uuid.uuid4())
        session_ttl = self._user_config.get("session_ttl_minutes", 60*24)  # 默认24小时
        
        self._sessions[session_id] = {
            'user_id': user_id,
            'created_at': time.time(),
            'expires_at': time.time() + session_ttl * 60
        }
        
        return session_id
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[int]]:
        """
        验证会话是否有效
        
        Args:
            session_id: 会话ID
            
        Returns:
            (有效, 用户ID)
        """
        if session_id not in self._sessions:
            return False, None
            
        session = self._sessions[session_id]
        
        # 检查会话是否过期
        if session.get('expires_at', 0) < time.time():
            del self._sessions[session_id]
            return False, None
            
        # 更新过期时间
        session_ttl = self._user_config.get("session_ttl_minutes", 60*24)
        session['expires_at'] = time.time() + session_ttl * 60
        
        return True, session.get('user_id')
    
    def logout(self, session_id: str) -> bool:
        """
        用户登出
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功删除会话
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def create_api_key(self, user_id: int, key_name: str, permissions: List[str] = None,
                      expires_days: int = None) -> Tuple[bool, str, Optional[str]]:
        """
        创建API密钥
        
        Args:
            user_id: 用户ID
            key_name: 密钥名称
            permissions: 权限列表
            expires_days: 过期天数
            
        Returns:
            (成功, 消息, API密钥(仅在成功时返回))
        """
        try:
            # 生成API密钥
            api_key = f"codeassist_{secrets.token_hex(24)}"
            key_hash = self._hash_api_key(api_key)
            key_prefix = api_key[:16]
            
            # 计算过期时间
            expires_at = None
            if expires_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_days)
            
            with get_session() as session:
                # 检查同名密钥是否已存在
                existing = session.query(ApiKey).filter(
                    ApiKey.user_id == user_id,
                    ApiKey.key_name == key_name,
                    ApiKey.is_active == True
                ).first()
                
                if existing:
                    return False, f"名称为 '{key_name}' 的API密钥已存在", None
                
                # 创建新密钥
                new_key = ApiKey(
                    user_id=user_id,
                    key_name=key_name,
                    key_hash=key_hash,
                    key_prefix=key_prefix,
                    expires_at=expires_at,
                    is_active=True
                )
                
                if permissions:
                    new_key.set_permissions(permissions)
                
                session.add(new_key)
                session.commit()
                
                logger.info(f"为用户ID {user_id} 创建API密钥: {key_name}")
                
                # 仅在此处返回完整密钥，之后不再可见
                return True, "API密钥已创建", api_key
        except Exception as e:
            logger.error(f"创建API密钥失败: {str(e)}")
            return False, f"创建API密钥失败: {str(e)}", None
    
    def verify_api_key(self, api_key: str) -> Tuple[bool, Optional[ApiKey]]:
        """
        验证API密钥
        
        Args:
            api_key: API密钥
            
        Returns:
            (有效, API密钥对象)
        """
        try:
            if not api_key or not api_key.startswith("codeassist_"):
                return False, None
                
            with get_session() as session:
                # 根据前缀查询可能的密钥
                key_prefix = api_key[:16]
                possible_keys = session.query(ApiKey).filter(
                    ApiKey.key_prefix == key_prefix,
                    ApiKey.is_active == True
                ).all()
                
                if not possible_keys:
                    return False, None
                
                # 验证完整密钥
                for key in possible_keys:
                    if self._verify_api_key(api_key, key.key_hash):
                        # 检查是否过期
                        if key.is_expired():
                            return False, None
                        
                        # 更新最后使用时间
                        key.last_used_at = datetime.utcnow()
                        session.commit()
                        
                        return True, key
                
                return False, None
        except Exception as e:
            logger.error(f"验证API密钥失败: {str(e)}")
            return False, None
    
    def list_api_keys(self, user_id: int) -> List[ApiKey]:
        """
        获取用户API密钥列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            API密钥列表
        """
        try:
            with get_session() as session:
                return session.query(ApiKey).filter(ApiKey.user_id == user_id).order_by(ApiKey.created_at.desc()).all()
        except Exception as e:
            logger.error(f"获取API密钥列表失败: {str(e)}")
            return []
    
    def revoke_api_key(self, key_id: int, user_id: int) -> Tuple[bool, str]:
        """
        撤销API密钥
        
        Args:
            key_id: 密钥ID
            user_id: 用户ID（用于验证所有权）
            
        Returns:
            (成功, 消息)
        """
        try:
            with get_session() as session:
                key = session.query(ApiKey).filter(
                    ApiKey.id == key_id,
                    ApiKey.user_id == user_id
                ).first()
                
                if not key:
                    return False, "API密钥不存在或您没有权限"
                
                key.is_active = False
                session.commit()
                
                return True, "API密钥已撤销"
        except Exception as e:
            logger.error(f"撤销API密钥失败: {str(e)}")
            return False, f"撤销失败: {str(e)}"
    
    def _hash_password(self, password: str) -> str:
        """密码加密"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    def _hash_api_key(self, api_key: str) -> str:
        """API密钥加密"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _verify_api_key(self, api_key: str, hashed: str) -> bool:
        """验证API密钥"""
        current_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return current_hash == hashed

# 单例实例
_instance = None

def get_instance() -> UserService:
    """获取用户服务实例"""
    global _instance
    if _instance is None:
        _instance = UserService()
    return _instance 