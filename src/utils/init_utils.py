"""
初始化实用工具

提供各种初始化功能，如创建必要的目录结构、检查环境等
"""

import os
import logging
from pathlib import Path

from src.utils import config

logger = logging.getLogger(__name__)

def ensure_directories():
    """
    确保所有必要的数据目录已创建
    
    根据配置文件中指定的路径，检查并创建所有必要的目录
    """
    dirs_to_create = [
        # 仓库相关目录
        config.get("repository_integration.local_repo_path", "data/repositories"),
        config.get("repository_integration.settings_path", "data/repositories/settings"),
        config.get("repository_integration.audit_log_path", "data/repositories/audit"),
        
        # 权限相关目录
        config.get("authorization_settings.permission_storage_path", "data/permissions"),
        
        # 知识库相关目录
        config.get("knowledge_base.storage_path", "data/knowledge_bases"),
        
        # 日志目录
        os.path.dirname(config.get("logging.file", "logs/mcp.log")),
        
        # 存储目录
        os.path.dirname(config.get("storage.path", "data/user_data/codeassistant.db")),
        config.get("storage.backup_path", "data/backups"),
        
        # 缓存目录
        config.get("network.cache_dir", "cache/network"),
        config.get("context.persistence_dir", "cache/context"),
        
        # 上传目录
        "data/uploads",
        
        # 其他可能的数据目录
        "data/temp",
        "data/exports"
    ]
    
    # 确保所有目录都存在
    for dir_path in dirs_to_create:
        if not dir_path:
            continue
            
        path = Path(dir_path)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建目录: {dir_path}")
            except Exception as e:
                logger.error(f"创建目录 {dir_path} 失败: {str(e)}")
                
    logger.info("已完成数据目录结构初始化") 