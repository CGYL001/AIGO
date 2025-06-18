"""
权限管理服务

管理用户操作权限验证、模式切换和权限状态跟踪
"""

import os
import json
import time
import uuid
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from src.utils import config

logger = logging.getLogger(__name__)

class AuthorizationService:
    """
    授权服务类
    
    提供权限验证、信任模式管理和权限状态持久化功能
    """
    
    def __init__(self):
        """初始化授权服务"""
        # 加载配置
        self._auth_config = config.get("authorization_settings", {})
        self._default_mode = self._auth_config.get("default_mode", "strict")
        self._sensitive_operations = self._auth_config.get("sensitive_operations", [])
        
        # 权限状态存储路径
        storage_path = self._auth_config.get("permission_storage_path", "data/permissions")
        self._storage_path = Path(storage_path)
        os.makedirs(self._storage_path, exist_ok=True)
        
        # 会话跟踪
        self._sessions = {}
        self._load_sessions()
        
    def _load_sessions(self):
        """加载权限会话状态"""
        session_file = self._storage_path / "sessions.json"
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 过滤掉已过期的会话
                    now = time.time()
                    for session_id, session in data.items():
                        if session.get('expires_at', 0) > now:
                            self._sessions[session_id] = session
                logger.info(f"已加载 {len(self._sessions)} 个有效权限会话")
            except Exception as e:
                logger.error(f"加载权限会话失败: {str(e)}")
                self._sessions = {}
    
    def _save_sessions(self):
        """保存权限会话状态"""
        session_file = self._storage_path / "sessions.json"
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self._sessions, f, ensure_ascii=False, indent=2)
            logger.debug("权限会话状态已保存")
        except Exception as e:
            logger.error(f"保存权限会话失败: {str(e)}")
    
    def create_session(self) -> str:
        """
        创建新的权限会话
        
        Returns:
            str: 会话ID
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            'mode': self._default_mode,
            'created_at': time.time(),
            'expires_at': time.time() + 24 * 60 * 60,  # 24小时后过期
            'confirm_count': 0,
            'trusted': False,
            'operations_history': []
        }
        self._save_sessions()
        return session_id
    
    def get_session(self, session_id: str) -> Dict:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            Dict: 会话信息，若不存在则返回空字典
        """
        return self._sessions.get(session_id, {})
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除权限会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否成功删除
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._save_sessions()
            return True
        return False
    
    def set_session_mode(self, session_id: str, mode: str) -> bool:
        """
        设置会话的权限模式
        
        Args:
            session_id: 会话ID
            mode: 权限模式 ('strict' 或 'trust')
            
        Returns:
            bool: 是否成功设置
        """
        if session_id in self._sessions and mode in self._auth_config.get("modes", {}):
            self._sessions[session_id]['mode'] = mode
            # 切换到严格模式时重置信任状态
            if mode == 'strict':
                self._sessions[session_id]['trusted'] = False
                self._sessions[session_id]['confirm_count'] = 0
            self._save_sessions()
            return True
        return False
    
    def check_authorization(self, session_id: str, operation: str, description: str = "") -> Tuple[bool, str]:
        """
        检查操作是否有权限执行
        
        Args:
            session_id: 会话ID
            operation: 操作类型
            description: 操作描述
            
        Returns:
            Tuple[bool, str]: (是否需要用户确认, 提示信息)
        """
        if session_id not in self._sessions:
            return True, "会话无效，请重新创建会话"
        
        session = self._sessions[session_id]
        
        # 检查会话是否过期
        if session.get('expires_at', 0) < time.time():
            return True, "会话已过期，请重新创建会话"
        
        # 非敏感操作直接通过
        if operation not in self._sensitive_operations:
            return False, "非敏感操作，无需确认"
        
        # 记录操作历史
        session['operations_history'].append({
            'operation': operation,
            'description': description,
            'timestamp': time.time()
        })
        
        # 严格模式下，所有敏感操作都需要确认
        if session['mode'] == 'strict':
            return True, f"需要确认敏感操作: {description}"
        
        # 信任模式下，检查是否已获得信任
        if session['mode'] == 'trust':
            if session.get('trusted', False):
                # 已信任，检查是否在有效期内
                trust_ttl = self._auth_config.get("modes", {}).get("trust", {}).get("trusted_session_ttl_minutes", 60)
                last_confirm_time = max([op.get('timestamp', 0) for op in session.get('operations_history', [])] or [session.get('created_at', 0)])
                
                if time.time() - last_confirm_time < trust_ttl * 60:
                    return False, "已获得信任，无需重复确认"
                else:
                    # 信任过期，需要重新确认
                    session['trusted'] = False
                    session['confirm_count'] = 0
                    self._save_sessions()
                    return True, f"信任已过期，需要重新确认: {description}"
            else:
                # 未获得信任，增加确认计数
                session['confirm_count'] += 1
                required_count = self._auth_config.get("modes", {}).get("trust", {}).get("confirm_count_required", 3)
                
                if session['confirm_count'] >= required_count:
                    session['trusted'] = True
                    self._save_sessions()
                    return False, f"已完成 {required_count} 次确认，获得信任状态"
                else:
                    self._save_sessions()
                    return True, f"需要确认敏感操作 ({session['confirm_count']}/{required_count}): {description}"
        
        return True, f"需要确认敏感操作: {description}"
    
    def confirm_operation(self, session_id: str, operation: str) -> bool:
        """
        确认执行敏感操作
        
        Args:
            session_id: 会话ID
            operation: 操作类型
            
        Returns:
            bool: 操作是否被确认
        """
        if session_id not in self._sessions:
            return False
            
        session = self._sessions[session_id]
        
        # 找到最后一个匹配的操作
        history = session.get('operations_history', [])
        for i in range(len(history) - 1, -1, -1):
            if history[i].get('operation') == operation:
                history[i]['confirmed'] = True
                history[i]['confirmed_at'] = time.time()
                self._save_sessions()
                return True
                
        return False
    
    def get_current_mode(self, session_id: str) -> str:
        """
        获取当前会话的权限模式
        
        Args:
            session_id: 会话ID
            
        Returns:
            str: 当前权限模式
        """
        if session_id not in self._sessions:
            return self._default_mode
        return self._sessions[session_id].get('mode', self._default_mode)
    
    def get_trust_status(self, session_id: str) -> Dict:
        """
        获取信任状态信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            Dict: 信任状态信息
        """
        if session_id not in self._sessions:
            return {
                'mode': self._default_mode,
                'trusted': False,
                'confirm_count': 0,
                'required_count': self._auth_config.get("modes", {}).get("trust", {}).get("confirm_count_required", 3)
            }
            
        session = self._sessions[session_id]
        return {
            'mode': session.get('mode', self._default_mode),
            'trusted': session.get('trusted', False),
            'confirm_count': session.get('confirm_count', 0),
            'required_count': self._auth_config.get("modes", {}).get("trust", {}).get("confirm_count_required", 3)
        }
    
    def cleanup_expired_sessions(self):
        """清理过期的会话"""
        now = time.time()
        expired = [sid for sid, session in self._sessions.items() if session.get('expires_at', 0) < now]
        
        for sid in expired:
            del self._sessions[sid]
            
        if expired:
            logger.info(f"已清理 {len(expired)} 个过期会话")
            self._save_sessions()

# 单例实例
_instance = None

def get_instance() -> AuthorizationService:
    """获取服务实例"""
    global _instance
    if _instance is None:
        _instance = AuthorizationService()
    return _instance 