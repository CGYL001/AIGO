"""
路径处理工具

此模块提供跨平台路径处理函数，处理不同操作系统间的路径差异。
"""

import os
import sys
import platform
import tempfile
from pathlib import Path
from typing import Optional, Union, List

def normalize_path(path: str) -> str:
    """
    规范化路径，将反斜杠转换为正斜杠，并解析相对路径

    参数:
        path (str): 要规范化的路径

    返回:
        str: 规范化后的路径
    """
    # 将Windows反斜杠转换为正斜杠
    normalized = path.replace('\\', '/')
    # 解析相对路径
    return os.path.normpath(normalized)

def get_platform_path(path: str) -> str:
    """
    根据当前平台转换路径分隔符

    参数:
        path (str): 要转换的路径

    返回:
        str: 适合当前平台的路径
    """
    # 先规范化为统一格式
    normalized = normalize_path(path)
    # 根据平台使用适当的分隔符
    if platform.system() == "Windows":
        return normalized.replace('/', '\\')
    else:
        return normalized.replace('\\', '/')

def ensure_dir_exists(path: str) -> bool:
    """
    确保目录存在，如果不存在则创建

    参数:
        path (str): 目录路径

    返回:
        bool: 如果目录已存在或成功创建则返回True
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {path}, 错误: {e}")
        return False

def get_temp_dir(prefix: str = "aigo_") -> str:
    """
    获取临时目录路径

    参数:
        prefix (str): 临时目录前缀

    返回:
        str: 临时目录路径
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    return temp_dir

def get_user_home_dir() -> str:
    """
    获取用户主目录路径

    返回:
        str: 用户主目录路径
    """
    return str(Path.home())

def get_app_data_dir(app_name: str = "AIgo") -> str:
    """
    获取应用数据目录路径

    参数:
        app_name (str): 应用名称

    返回:
        str: 应用数据目录路径
    """
    home = get_user_home_dir()
    
    if platform.system() == "Windows":
        # Windows: %APPDATA%\AppName
        app_data = os.path.join(os.environ.get('APPDATA', os.path.join(home, 'AppData', 'Roaming')), app_name)
    elif platform.system() == "Darwin":
        # macOS: ~/Library/Application Support/AppName
        app_data = os.path.join(home, 'Library', 'Application Support', app_name)
    else:
        # Linux/Unix: ~/.local/share/AppName
        app_data = os.path.join(home, '.local', 'share', app_name.lower())
    
    # 确保目录存在
    ensure_dir_exists(app_data)
    return app_data

if __name__ == "__main__":
    """主函数，测试路径处理工具"""
    print("\n===== 路径处理工具测试 =====")
    
    # 测试路径规范化
    test_paths = [
        r"C:\Users\test\Documents",
        "/home/user/documents",
        r".\relative\path",
        "../parent/path",
        r"C:/mixed/slashes\in\path"
    ]
    
    print("\n路径规范化测试:")
    for path in test_paths:
        print(f"原始路径: {path}")
        print(f"规范化路径: {normalize_path(path)}")
        print(f"平台路径: {get_platform_path(path)}")
        print()
    
    # 测试目录创建
    test_dir = os.path.join(tempfile.gettempdir(), "aigo_test_dir")
    print(f"\n测试目录创建: {test_dir}")
    if ensure_dir_exists(test_dir):
        print(f"目录创建成功: {test_dir}")
    else:
        print(f"目录创建失败: {test_dir}")
    
    # 测试临时目录
    temp_dir = get_temp_dir()
    print(f"\n临时目录: {temp_dir}")
    
    # 测试用户主目录
    home_dir = get_user_home_dir()
    print(f"\n用户主目录: {home_dir}")
    
    # 测试应用数据目录
    app_data_dir = get_app_data_dir()
    print(f"\n应用数据目录: {app_data_dir}")
    
    print("\n===== 测试完成 =====") 