from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pathlib import Path
from typing import List, Dict, Any
import json

from src.utils import config

# 创建基础模型
Base = declarative_base()

# 用户团队关联表（多对多）
user_team_association = Table(
    'user_team_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('team_id', Integer, ForeignKey('teams.id'))
)

# 定义数据模型
class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    full_name = Column(String(100))
    avatar_url = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # 关系
    teams = relationship("Team", secondary=user_team_association, back_populates="members")
    permissions = relationship("UserPermission", back_populates="user")
    owned_repositories = relationship("Repository", back_populates="owner")
    api_keys = relationship("ApiKey", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
        
    def __repr__(self) -> str:
        return f"<User {self.username}>"

class Team(Base):
    """团队表"""
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    members = relationship("User", secondary=user_team_association, back_populates="teams")
    permissions = relationship("TeamPermission", back_populates="team")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "member_count": len(self.members)
        }
    
    def __repr__(self) -> str:
        return f"<Team {self.name}>"

class Repository(Base):
    """仓库表"""
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    repo_path = Column(String(512), unique=True, nullable=False)
    repo_id = Column(String(50), unique=True)  # MD5哈希ID
    platform = Column(String(50))  # github, gitlab, gitee, etc.
    remote_url = Column(String(256))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'))
    
    # 关系
    owner = relationship("User", back_populates="owned_repositories")
    user_permissions = relationship("UserPermission", back_populates="repository")
    team_permissions = relationship("TeamPermission", back_populates="repository")
    protection_rules = relationship("ProtectionRule", back_populates="repository")
    audit_logs = relationship("AuditLog", back_populates="repository")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "name": self.name,
            "repo_path": self.repo_path,
            "repo_id": self.repo_id,
            "platform": self.platform,
            "remote_url": self.remote_url,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "owner": self.owner.username if self.owner else None
        }
    
    def __repr__(self) -> str:
        return f"<Repository {self.name}>"

class UserPermission(Base):
    """用户仓库权限表"""
    __tablename__ = 'user_permissions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    role = Column(String(50), nullable=False)  # admin, developer, reader
    custom_permissions = Column(Text)  # 自定义权限，JSON字符串
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="permissions")
    repository = relationship("Repository", back_populates="user_permissions")
    
    def get_custom_permissions(self) -> List[str]:
        """获取自定义权限列表"""
        if not self.custom_permissions:
            return []
        try:
            return json.loads(self.custom_permissions)
        except:
            return []
    
    def set_custom_permissions(self, permissions: List[str]):
        """设置自定义权限列表"""
        self.custom_permissions = json.dumps(permissions)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "repository_id": self.repository_id,
            "role": self.role,
            "custom_permissions": self.get_custom_permissions(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f"<UserPermission user_id={self.user_id} repo_id={self.repository_id} role={self.role}>"

class TeamPermission(Base):
    """团队仓库权限表"""
    __tablename__ = 'team_permissions'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    role = Column(String(50), nullable=False)  # admin, developer, reader
    custom_permissions = Column(Text)  # 自定义权限，JSON字符串
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    team = relationship("Team", back_populates="permissions")
    repository = relationship("Repository", back_populates="team_permissions")
    
    def get_custom_permissions(self) -> List[str]:
        """获取自定义权限列表"""
        if not self.custom_permissions:
            return []
        try:
            return json.loads(self.custom_permissions)
        except:
            return []
    
    def set_custom_permissions(self, permissions: List[str]):
        """设置自定义权限列表"""
        self.custom_permissions = json.dumps(permissions)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "team_id": self.team_id,
            "repository_id": self.repository_id,
            "role": self.role,
            "custom_permissions": self.get_custom_permissions(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f"<TeamPermission team_id={self.team_id} repo_id={self.repository_id} role={self.role}>"

class ProtectionRule(Base):
    """仓库保护规则表"""
    __tablename__ = 'protection_rules'
    
    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    rule_type = Column(String(50), nullable=False)  # require_review, protected_branch, block_force_push
    target = Column(String(100))  # 针对的分支，文件模式等
    enabled = Column(Boolean, default=True)
    config = Column(Text)  # 配置参数，JSON字符串
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    repository = relationship("Repository", back_populates="protection_rules")
    
    def get_config(self) -> Dict[str, Any]:
        """获取规则配置"""
        if not self.config:
            return {}
        try:
            return json.loads(self.config)
        except:
            return {}
    
    def set_config(self, config: Dict[str, Any]):
        """设置规则配置"""
        self.config = json.dumps(config)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "rule_type": self.rule_type,
            "target": self.target,
            "enabled": self.enabled,
            "config": self.get_config(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f"<ProtectionRule repo_id={self.repository_id} rule_type={self.rule_type}>"

class AuditLog(Base):
    """审计日志表"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    operation = Column(String(50), nullable=False)
    operation_description = Column(String(256))
    target = Column(String(256))  # 操作的目标（文件、分支等）
    details = Column(Text)  # 详细信息，JSON字符串
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="audit_logs")
    repository = relationship("Repository", back_populates="audit_logs")
    
    def get_details(self) -> Dict[str, Any]:
        """获取详细信息"""
        if not self.details:
            return {}
        try:
            return json.loads(self.details)
        except:
            return {}
    
    def set_details(self, details: Dict[str, Any]):
        """设置详细信息"""
        self.details = json.dumps(details)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user": self.user.username if self.user else None,
            "repository_id": self.repository_id,
            "operation": self.operation,
            "operation_description": self.operation_description,
            "target": self.target,
            "details": self.get_details(),
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f"<AuditLog user_id={self.user_id} operation={self.operation} created_at={self.created_at}>"

class ApiKey(Base):
    """API密钥表"""
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    key_name = Column(String(100), nullable=False)
    key_hash = Column(String(256), nullable=False)
    key_prefix = Column(String(16), nullable=False)  # 密钥前缀，用于标识展示
    permissions = Column(Text)  # 权限范围，JSON字符串
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # 关系
    user = relationship("User", back_populates="api_keys")
    
    def get_permissions(self) -> List[str]:
        """获取权限范围"""
        if not self.permissions:
            return []
        try:
            return json.loads(self.permissions)
        except:
            return []
    
    def set_permissions(self, permissions: List[str]):
        """设置权限范围"""
        self.permissions = json.dumps(permissions)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "key_name": self.key_name,
            "key_prefix": self.key_prefix,
            "permissions": self.get_permissions(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "is_active": self.is_active,
            "is_expired": self.is_expired()
        }
    
    def __repr__(self) -> str:
        return f"<ApiKey key_name={self.key_name} user_id={self.user_id}>"

# 保持原有的模型
class KnowledgeBaseEntry(Base):
    """知识库条目表"""
    __tablename__ = 'knowledge_base_entries'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    source = Column(String(256))
    metadata = Column(Text)  # 存储为JSON字符串
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CodeSnippet(Base):
    """代码片段表，用于存储代码补全历史"""
    __tablename__ = 'code_snippets'
    
    id = Column(Integer, primary_key=True)
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    completion = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CodeAnalysisResult(Base):
    """代码分析结果表"""
    __tablename__ = 'code_analysis_results'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String(512), nullable=False)
    language = Column(String(50))
    metrics = Column(Text)  # JSON存储指标数据
    quality_score = Column(Float)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
class CodeIssue(Base):
    """代码问题记录表"""
    __tablename__ = 'code_issues'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String(512), nullable=False)
    line_number = Column(Integer)
    column = Column(Integer)
    severity = Column(String(20))  # error, warning, info
    message = Column(Text)
    code = Column(String(50))  # 问题代码
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis_id = Column(Integer, ForeignKey('code_analysis_results.id'))
    
    analysis = relationship("CodeAnalysisResult")

class UserSettings(Base):
    """用户设置表"""
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 数据库工厂
def get_engine():
    """获取数据库引擎"""
    db_type = config.get("storage.type", "sqlite")
    
    if db_type == "sqlite":
        db_path = config.get("storage.path", "data/user_data/codeassistant.db")
        # 确保目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return create_engine(f"sqlite:///{db_path}")
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")

def get_session():
    """获取数据库会话"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_database():
    """初始化数据库"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    return engine 