import os
import sys
import re
from pathlib import Path
from typing import Union, List, Optional, Tuple

from src.utils import logger


def normalize_path(path: Union[str, Path]) -> str:
    """
    规范化路径，统一处理不同操作系统的路径格式
    
    Args:
        path: 输入路径，可以是字符串或Path对象
        
    Returns:
        str: 规范化后的路径字符串
    """
    if isinstance(path, Path):
        path = str(path)
    
    # 将路径分隔符统一为系统默认分隔符
    path = path.replace('\\', os.sep).replace('/', os.sep)
    
    # 处理相对路径
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    
    # 规范化路径（解析 .. 和 . 等）
    path = os.path.normpath(path)
    
    return path


def is_subpath(path: Union[str, Path], base_path: Union[str, Path]) -> bool:
    """
    检查路径是否是基础路径的子路径
    
    Args:
        path: 要检查的路径
        base_path: 基础路径
        
    Returns:
        bool: 如果path是base_path的子路径，则返回True
    """
    path = normalize_path(path)
    base_path = normalize_path(base_path)
    
    # 确保base_path以分隔符结尾，以便正确匹配子目录
    if not base_path.endswith(os.sep):
        base_path += os.sep
    
    return path.startswith(base_path)


def is_safe_path(path: Union[str, Path], base_path: Union[str, Path]) -> bool:
    """
    检查路径是否安全（不包含路径遍历攻击）
    
    Args:
        path: 要检查的路径
        base_path: 基础路径
        
    Returns:
        bool: 如果路径安全，则返回True
    """
    # 规范化路径
    path = normalize_path(path)
    base_path = normalize_path(base_path)
    
    # 检查是否是子路径
    return is_subpath(path, base_path)


def ensure_directory(path: Union[str, Path]) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        bool: 如果目录已存在或成功创建，则返回True
    """
    path = normalize_path(path)
    
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败: {path}, 错误: {str(e)}")
        return False


def get_relative_path(path: Union[str, Path], base_path: Union[str, Path]) -> str:
    """
    获取相对于基础路径的相对路径
    
    Args:
        path: 目标路径
        base_path: 基础路径
        
    Returns:
        str: 相对路径
    """
    path = normalize_path(path)
    base_path = normalize_path(base_path)
    
    try:
        return os.path.relpath(path, base_path)
    except ValueError:
        # 如果路径在不同的驱动器上（Windows），则返回原始路径
        return path


def join_paths(*paths: Union[str, Path]) -> str:
    """
    连接多个路径部分
    
    Args:
        *paths: 路径部分
        
    Returns:
        str: 连接后的路径
    """
    # 转换所有路径为字符串
    str_paths = [str(p) for p in paths]
    
    # 使用os.path.join连接路径
    return os.path.join(*str_paths)


def split_path(path: Union[str, Path]) -> Tuple[str, str]:
    """
    分割路径为目录和文件名
    
    Args:
        path: 输入路径
        
    Returns:
        Tuple[str, str]: (目录, 文件名)
    """
    path = normalize_path(path)
    return os.path.split(path)


def get_file_extension(path: Union[str, Path]) -> str:
    """
    获取文件扩展名
    
    Args:
        path: 文件路径
        
    Returns:
        str: 文件扩展名（包含点，如.txt）
    """
    _, ext = os.path.splitext(str(path))
    return ext.lower()


def convert_to_platform_path(path: str) -> str:
    """
    将路径转换为当前平台的格式
    
    Args:
        path: 输入路径
        
    Returns:
        str: 转换后的路径
    """
    # 将所有分隔符转换为当前系统的分隔符
    return path.replace('\\', os.sep).replace('/', os.sep)


def convert_to_unix_path(path: str) -> str:
    """
    将路径转换为Unix格式（使用正斜杠）
    
    Args:
        path: 输入路径
        
    Returns:
        str: 转换后的路径
    """
    return path.replace('\\', '/')


def convert_to_windows_path(path: str) -> str:
    """
    将路径转换为Windows格式（使用反斜杠）
    
    Args:
        path: 输入路径
        
    Returns:
        str: 转换后的路径
    """
    return path.replace('/', '\\')


def is_same_file(path1: Union[str, Path], path2: Union[str, Path]) -> bool:
    """
    检查两个路径是否指向同一个文件
    
    Args:
        path1: 第一个路径
        path2: 第二个路径
        
    Returns:
        bool: 如果两个路径指向同一个文件，则返回True
    """
    try:
        return os.path.samefile(normalize_path(path1), normalize_path(path2))
    except FileNotFoundError:
        # 如果文件不存在，则比较规范化后的路径
        return normalize_path(path1) == normalize_path(path2)
    except Exception as e:
        logger.error(f"比较文件路径失败: {path1} vs {path2}, 错误: {str(e)}")
        return False


def get_workspace_relative_path(path: Union[str, Path], workspace_root: Union[str, Path]) -> str:
    """
    获取相对于工作区根目录的路径
    
    Args:
        path: 目标路径
        workspace_root: 工作区根目录
        
    Returns:
        str: 相对于工作区的路径
    """
    path = normalize_path(path)
    workspace_root = normalize_path(workspace_root)
    
    if is_subpath(path, workspace_root):
        return get_relative_path(path, workspace_root)
    else:
        # 如果不是子路径，则返回原始路径
        return path


def safe_file_operations(func):
    """
    装饰器，用于确保文件操作安全
    
    Args:
        func: 要装饰的函数
        
    Returns:
        函数: 装饰后的函数
    """
    def wrapper(path, *args, **kwargs):
        base_path = kwargs.pop('base_path', None)
        
        # 如果提供了基础路径，则检查路径是否安全
        if base_path and not is_safe_path(path, base_path):
            logger.error(f"不安全的路径操作: {path} 不在 {base_path} 内")
            raise ValueError(f"不安全的路径操作: {path}")
        
        return func(path, *args, **kwargs)
    
    return wrapper


@safe_file_operations
def safe_read_file(path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    安全地读取文件内容
    
    Args:
        path: 文件路径
        encoding: 文件编码
        
    Returns:
        str: 文件内容
    """
    path = normalize_path(path)
    
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取文件失败: {path}, 错误: {str(e)}")
        raise


@safe_file_operations
def safe_write_file(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """
    安全地写入文件内容
    
    Args:
        path: 文件路径
        content: 要写入的内容
        encoding: 文件编码
        
    Returns:
        bool: 如果写入成功，则返回True
    """
    path = normalize_path(path)
    
    # 确保目录存在
    directory = os.path.dirname(path)
    ensure_directory(directory)
    
    try:
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"写入文件失败: {path}, 错误: {str(e)}")
        return False


def get_common_base_path(paths: List[Union[str, Path]]) -> str:
    """
    获取多个路径的共同基础路径
    
    Args:
        paths: 路径列表
        
    Returns:
        str: 共同基础路径
    """
    if not paths:
        return ""
    
    # 规范化所有路径
    normalized_paths = [normalize_path(p) for p in paths]
    
    # 将路径转换为列表形式，以便比较
    path_parts = [p.split(os.sep) for p in normalized_paths]
    
    # 找出最短路径的长度
    min_length = min(len(parts) for parts in path_parts)
    
    # 找出共同的前缀
    common_parts = []
    for i in range(min_length):
        part = path_parts[0][i]
        if all(parts[i] == part for parts in path_parts):
            common_parts.append(part)
        else:
            break
    
    # 如果没有共同前缀，则返回根目录
    if not common_parts:
        return os.sep
    
    # 构建共同基础路径
    common_base = os.sep.join(common_parts)
    
    # 确保路径以分隔符开头（对于绝对路径）
    if normalized_paths[0].startswith(os.sep) and not common_base.startswith(os.sep):
        common_base = os.sep + common_base
    
    # 在Windows上处理驱动器号
    if sys.platform == "win32" and ":" in normalized_paths[0]:
        drive = normalized_paths[0].split(os.sep)[0]
        if not common_base.startswith(drive):
            common_base = drive + common_base if common_base.startswith(os.sep) else drive + os.sep + common_base
    
    return common_base 