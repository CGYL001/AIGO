import os
import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from src.utils import config

# 日志级别映射
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# 默认日志格式
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 创建日志目录
log_dir = Path(config.get("logging.file", "logs/mcp.log")).parent
os.makedirs(log_dir, exist_ok=True)

# 创建日志器
logger = logging.getLogger("mcp")

# 设置日志级别
log_level_name = config.get("logging.level", "info").lower()
log_level = LOG_LEVELS.get(log_level_name, logging.INFO)
logger.setLevel(log_level)

# 创建控制台处理器
if config.get("logging.console_enabled", True):
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT))
    logger.addHandler(console_handler)

# 创建文件处理器
log_file = config.get("logging.file", "logs/mcp.log")
if log_file:
    max_size = config.get("logging.max_size_mb", 10) * 1024 * 1024  # 转换为字节
    backup_count = config.get("logging.backup_count", 5)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT))
    logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取命名日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger: 日志器实例
    """
    return logging.getLogger(f"mcp.{name}")


def set_level(level: str) -> None:
    """
    设置日志级别
    
    Args:
        level: 日志级别名称
    """
    if level.lower() in LOG_LEVELS:
        logger.setLevel(LOG_LEVELS[level.lower()])


def debug(msg: str, *args, **kwargs) -> None:
    """记录调试级别日志"""
    logger.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """记录信息级别日志"""
    logger.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """记录警告级别日志"""
    logger.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """记录错误级别日志"""
    logger.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """记录严重错误级别日志"""
    logger.critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs) -> None:
    """记录异常信息"""
    logger.exception(msg, *args, **kwargs)


def setLevel(level) -> None:
    """设置日志级别（兼容标准库API）"""
    logger.setLevel(level) 