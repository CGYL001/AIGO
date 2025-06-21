#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
授权服务模块

提供用户认证和授权功能
"""

import os
import json
import time
import logging
import hashlib
import hmac
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AuthorizationService:
    """授权服务类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化授权服务
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.token_cache = {}
        self.credentials_dir = Path("data/credentials")
        self.credentials_dir.mkdir(exist_ok=True, parents=True)
        self.token_file = self.credentials_dir / "tokens.json"
        self._load_tokens()
        logger.info("授权服务初始化完成")
    
    def _load_tokens(self):
        """加载令牌数据"""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    self.token_cache = json.load(f)
                logger.info(f"已加载 {len(self.token_cache)} 个令牌")
            except Exception as e:
                logger.error(f"加载令牌失败: {str(e)}")
                self.token_cache = {}
    
    def _save_tokens(self):
        """保存令牌数据"""
        try:
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(self.token_cache, f, indent=2)
            logger.info(f"已保存 {len(self.token_cache)} 个令牌")
        except Exception as e:
            logger.error(f"保存令牌失败: {str(e)}")
    
    def create_token(self, user_id: str, permissions: list = None, expires_in: int = 86400) -> str:
        """创建新令牌
        
        Args:
            user_id: 用户ID
            permissions: 权限列表
            expires_in: 过期时间（秒）
        
        Returns:
            str: 生成的令牌
        """
        # 创建令牌数据
        token_data = {
            "user_id": user_id,
            "permissions": permissions or ["basic"],
            "created_at": time.time(),
            "expires_at": time.time() + expires_in
        }
        
        # 生成令牌
        token = self._generate_token(user_id)
        
        # 存储令牌
        self.token_cache[token] = token_data
        self._save_tokens()
        
        return token
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """验证令牌
        
        Args:
            token: 要验证的令牌
        
        Returns:
            Dict[str, Any]: 验证结果，包含有效性和用户信息
        """
        # 检查令牌是否存在
        if token not in self.token_cache:
            logger.warning(f"令牌不存在: {token[:8]}...")
            return {"valid": False, "reason": "invalid_token"}
        
        # 获取令牌数据
        token_data = self.token_cache[token]
        
        # 检查令牌是否过期
        if token_data["expires_at"] < time.time():
            logger.warning(f"令牌已过期: {token[:8]}...")
            return {"valid": False, "reason": "expired_token"}
        
        # 令牌有效
        return {
            "valid": True,
            "user_id": token_data["user_id"],
            "permissions": token_data["permissions"]
        }
    
    def revoke_token(self, token: str) -> bool:
        """撤销令牌
        
        Args:
            token: 要撤销的令牌
        
        Returns:
            bool: 是否成功撤销
        """
        if token in self.token_cache:
            del self.token_cache[token]
            self._save_tokens()
            logger.info(f"已撤销令牌: {token[:8]}...")
            return True
        else:
            logger.warning(f"令牌不存在，无法撤销: {token[:8]}...")
            return False
    
    def check_permission(self, token: str, required_permission: str) -> bool:
        """检查令牌是否具有指定权限
        
        Args:
            token: 要检查的令牌
            required_permission: 所需权限
        
        Returns:
            bool: 是否具有权限
        """
        # 验证令牌
        result = self.validate_token(token)
        if not result["valid"]:
            return False
        
        # 检查权限
        permissions = result["permissions"]
        if "admin" in permissions or required_permission in permissions:
            return True
        
        return False
    
    def _generate_token(self, user_id: str) -> str:
        """生成令牌
        
        Args:
            user_id: 用户ID
        
        Returns:
            str: 生成的令牌
        """
        # 使用当前时间和用户ID生成令牌
        timestamp = str(time.time())
        secret = self.config.get("secret_key", "default_secret_key")
        
        # 使用HMAC生成令牌
        message = f"{user_id}:{timestamp}".encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()
        
        return f"{user_id}:{timestamp}:{signature}" 