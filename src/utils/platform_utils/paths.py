"""
跨平台路径工具 - 处理不同操作系统的路径差异

提供统一的路径处理API，确保在不同操作系统间路径表示一致。
"""

import os
import sys
import pathlib
import platform
from typing import Union, Optional

from .detection import is_windows, is_linux, is_macos, is_wsl

def normalize_path(path: str) -> str:
    """
    规范化路径格式，使其符合当前操作系统格式
    
    参数:
        path: 需要规范化的路径
        
    返回:
        规范化后的路径
    """
    # 转换为Path对象并返回规范化的字符串
    return str(pathlib.Path(path).expanduser().resolve())

def get_home_dir() -> str:
    """
    获取当前用户的主目录
    
    返回:
        用户主目录的完整路径
    """
    return str(pathlib.Path.home())

def get_app_data_dir(app_name: str, create: bool = True) -> str:
    """
    获取应用数据目录，根据不同平台返回适当的位置
    
    参数:
        app_name: 应用名称
        create: 如果目录不存在，是否创建
        
    返回:
        应用数据目录的完整路径
    """
    path = None
    
    if is_windows():
        # Windows: %LOCALAPPDATA%\app_name
        path = os.path.join(os.environ.get('LOCALAPPDATA', ''), app_name)
    elif is_macos():
        # macOS: ~/Library/Application Support/app_name
        path = os.path.join(get_home_dir(), 'Library', 'Application Support', app_name)
    else:
        # Linux/Unix: ~/.local/share/app_name
        xdg_data_home = os.environ.get('XDG_DATA_HOME', '')
        if not xdg_data_home:
            xdg_data_home = os.path.join(get_home_dir(), '.local', 'share')
        path = os.path.join(xdg_data_home, app_name)
    
    if create and path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        
    return path

def get_temp_dir() -> str:
    """
    获取临时文件目录
    
    返回:
        临时文件目录的完整路径
    """
    return str(pathlib.Path(os.environ.get('TEMP', '') or os.environ.get('TMP', '') or '/tmp'))

def get_config_dir(app_name: str, create: bool = True) -> str:
    """
    获取配置文件目录，根据不同平台返回适当的位置
    
    参数:
        app_name: 应用名称
        create: 如果目录不存在，是否创建
        
    返回:
        配置文件目录的完整路径
    """
    path = None
    
    if is_windows():
        # Windows: %APPDATA%\app_name
        path = os.path.join(os.environ.get('APPDATA', ''), app_name)
    elif is_macos():
        # macOS: ~/Library/Preferences/app_name
        path = os.path.join(get_home_dir(), 'Library', 'Preferences', app_name)
    else:
        # Linux/Unix: ~/.config/app_name
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME', '')
        if not xdg_config_home:
            xdg_config_home = os.path.join(get_home_dir(), '.config')
        path = os.path.join(xdg_config_home, app_name)
    
    if create and path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        
    return path

def get_logs_dir(app_name: str, create: bool = True) -> str:
    """
    获取日志文件目录，根据不同平台返回适当的位置
    
    参数:
        app_name: 应用名称
        create: 如果目录不存在，是否创建
        
    返回:
        日志文件目录的完整路径
    """
    path = None
    
    if is_windows():
        # Windows: %LOCALAPPDATA%\app_name\Logs
        path = os.path.join(os.environ.get('LOCALAPPDATA', ''), app_name, 'Logs')
    elif is_macos():
        # macOS: ~/Library/Logs/app_name
        path = os.path.join(get_home_dir(), 'Library', 'Logs', app_name)
    else:
        # Linux/Unix: ~/.local/share/app_name/logs (或 /var/log/app_name 如果有权限)
        if os.access('/var/log', os.W_OK):
            path = os.path.join('/var/log', app_name)
        else:
            path = os.path.join(get_app_data_dir(app_name, False), 'logs')
    
    if create and path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        
    return path

def convert_wsl_path(path: str) -> str:
    """
    将WSL路径转换为Windows路径，反之亦然
    
    参数:
        path: 需要转换的路径
        
    返回:
        转换后的路径
    """
    if is_wsl():
        # WSL路径转Windows路径
        if path.startswith('/mnt/'):
            # /mnt/c/... -> C:\...
            drive = path[5].upper()
            return f"{drive}:{path[6:].replace('/', '\\')}"
        else:
            # 使用wslpath转换其他路径
            try:
                import subprocess
                result = subprocess.check_output(['wslpath', '-w', path]).decode('utf-8').strip()
                return result
            except:
                return path
    elif is_windows():
        # Windows路径转WSL路径
        if len(path) >= 2 and path[1] == ':':
            # C:\... -> /mnt/c/...
            drive = path[0].lower()
            return f"/mnt/{drive}/{path[3:].replace('\\', '/')}"
        else:
            return path
    
    return path

def ensure_dir_exists(path: str) -> str:
    """
    确保目录存在，如果不存在则创建
    
    参数:
        path: 目录路径
        
    返回:
        规范化后的目录路径
    """
    path = normalize_path(path)
    os.makedirs(path, exist_ok=True)
    return path

def is_path_writable(path: str) -> bool:
    """
    检查路径是否可写
    
    参数:
        path: 需要检查的路径
        
    返回:
        如果路径可写则返回True，否则返回False
    """
    if os.path.exists(path):
        return os.access(path, os.W_OK)
    
    # 如果路径不存在，检查父目录
    parent = os.path.dirname(path)
    if not parent:
        parent = '.'
    return os.access(parent, os.W_OK) 