"""
Wubuntu平台适配器 - 为Wubuntu系统提供专用工具和功能

Wubuntu是Ubuntu的特殊版本，与Windows进行了深度集成的独立系统。
这个模块提供了专门针对这种环境的工具和功能。
"""

import os
import sys
import subprocess
import platform
import shutil
from typing import Dict, Any, Optional, List, Tuple

from .detection import is_wubuntu, is_windows, is_linux
from .paths import normalize_path, get_home_dir

def get_wubuntu_version() -> str:
    """
    获取Wubuntu版本信息
    
    返回:
        Wubuntu版本号，如果不是Wubuntu则返回空字符串
    """
    if not is_wubuntu():
        return ""
    
    # 从环境变量获取
    version = os.environ.get('WUBUNTU_VERSION')
    if version:
        return version
    
    # 从版本文件获取
    try:
        if os.path.exists('/etc/wubuntu-release'):
            with open('/etc/wubuntu-release', 'r') as f:
                return f.read().strip()
    except:
        pass
    
    return "Unknown"

def get_windows_path() -> str:
    """
    获取Wubuntu中Windows系统的路径
    
    返回:
        Windows系统的挂载路径
    """
    if not is_wubuntu():
        return ""
    
    # 标准挂载点
    standard_paths = [
        '/mnt/c',
        '/windows',
        '/win',
        '/windir'
    ]
    
    for path in standard_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return path
    
    # 尝试从配置文件获取
    try:
        if os.path.exists('/etc/wubuntu/config'):
            with open('/etc/wubuntu/config', 'r') as f:
                for line in f:
                    if line.startswith('WINDOWS_MOUNT='):
                        return line.split('=', 1)[1].strip()
    except:
        pass
    
    return "/mnt/c"  # 默认返回标准WSL挂载点

def get_ubuntu_path_from_windows() -> str:
    """
    从Windows视角获取Ubuntu文件系统的路径
    
    返回:
        Windows下Ubuntu文件系统的访问路径
    """
    if not is_wubuntu():
        return ""
    
    # 标准路径模式
    return "\\\\wsl$\\Wubuntu"

def convert_path(path: str, to_windows: bool = False) -> str:
    """
    在Wubuntu和Windows路径格式之间转换
    
    参数:
        path: 要转换的路径
        to_windows: 如果为True，则转换为Windows格式；否则转换为Wubuntu格式
        
    返回:
        转换后的路径
    """
    if not is_wubuntu():
        return path
    
    windows_root = get_windows_path()
    
    if to_windows:
        # Wubuntu路径转Windows路径
        if path.startswith('/'):
            if path.startswith(windows_root):
                # 已经是Windows路径的挂载点，转换为Windows格式
                rel_path = path[len(windows_root):].replace('/', '\\')
                return f"C:{rel_path}"
            else:
                # Ubuntu路径，转换为WSL$格式
                return f"\\\\wsl$\\Wubuntu{path}"
    else:
        # Windows路径转Wubuntu路径
        if path.startswith('\\\\wsl$\\Wubuntu'):
            # WSL$路径格式
            return path[len('\\\\wsl$\\Wubuntu'):]
        elif len(path) >= 2 and path[1] == ':':
            # 标准Windows路径 (C:\...)
            drive = path[0].lower()
            wsl_path = f"{windows_root}/{path[3:].replace('\\', '/')}"
            return wsl_path
    
    return path

def run_windows_command(
    command: str, 
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    capture_output: bool = False
) -> Tuple[int, str, str]:
    """
    在Wubuntu中运行Windows命令
    
    参数:
        command: 要执行的Windows命令
        cwd: 工作目录
        env: 环境变量
        capture_output: 是否捕获输出
        
    返回:
        元组 (返回码, 标准输出, 标准错误)
    """
    if not is_wubuntu():
        raise RuntimeError("This function can only be used in Wubuntu environment")
    
    # 使用cmd.exe执行Windows命令
    windows_root = get_windows_path()
    cmd_path = f"{windows_root}/Windows/System32/cmd.exe"
    
    if not os.path.exists(cmd_path):
        raise FileNotFoundError(f"Windows cmd.exe not found at {cmd_path}")
    
    # 如果提供了工作目录，转换为Windows格式
    if cwd:
        windows_cwd = convert_path(cwd, to_windows=True)
    else:
        windows_cwd = None
    
    # 构建完整命令
    full_cmd = [cmd_path, '/c', command]
    
    # 执行命令
    if capture_output:
        result = subprocess.run(
            full_cmd,
            cwd=windows_cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    else:
        result = subprocess.run(full_cmd, cwd=windows_cwd, env=env)
        return result.returncode, "", ""

def get_wubuntu_system_info() -> Dict[str, Any]:
    """
    获取Wubuntu系统的详细信息
    
    返回:
        包含Wubuntu系统信息的字典
    """
    if not is_wubuntu():
        return {"error": "Not running in Wubuntu environment"}
    
    info = {
        "version": get_wubuntu_version(),
        "windows_path": get_windows_path(),
        "ubuntu_version": "",
        "windows_version": "",
        "integration_features": []
    }
    
    # 获取Ubuntu版本
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('VERSION_ID='):
                    info['ubuntu_version'] = line.split('=')[1].strip().strip('"')
                    break
    except:
        pass
    
    # 获取Windows版本
    try:
        returncode, stdout, stderr = run_windows_command('ver', capture_output=True)
        if returncode == 0:
            info['windows_version'] = stdout.strip()
    except:
        pass
    
    # 检测集成特性
    if os.path.exists('/usr/bin/wslg'):
        info['integration_features'].append('WSLg')
    
    if os.path.exists('/usr/bin/wslview'):
        info['integration_features'].append('WSL Utilities')
    
    if os.path.exists('/usr/bin/wubuntu-integration'):
        info['integration_features'].append('Wubuntu Integration Tools')
    
    return info

def setup_wubuntu_integration() -> bool:
    """
    设置Wubuntu集成功能
    
    返回:
        如果成功设置集成则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    success = True
    
    # 创建配置目录
    config_dir = '/etc/wubuntu'
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, exist_ok=True)
        except:
            success = False
    
    # 设置环境变量
    try:
        with open(os.path.expanduser('~/.bashrc'), 'a') as f:
            f.write('\n# Wubuntu Integration\n')
            f.write('export WUBUNTU_ENABLED=1\n')
            f.write(f'export WUBUNTU_VERSION={get_wubuntu_version()}\n')
            f.write(f'export WINDOWS_PATH={get_windows_path()}\n')
    except:
        success = False
    
    # 创建Windows快速访问链接
    try:
        home = get_home_dir()
        windows_home = os.path.join(get_windows_path(), 'Users', os.environ.get('USER', 'Default'))
        
        if os.path.exists(windows_home):
            win_link = os.path.join(home, 'Windows')
            if not os.path.exists(win_link):
                os.symlink(windows_home, win_link)
    except:
        pass
    
    return success

def is_wubuntu_feature_enabled(feature: str) -> bool:
    """
    检查特定的Wubuntu功能是否启用
    
    参数:
        feature: 功能名称
        
    返回:
        如果功能已启用则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    # 检查配置文件
    try:
        if os.path.exists('/etc/wubuntu/features'):
            with open('/etc/wubuntu/features', 'r') as f:
                features = [line.strip() for line in f if line.strip()]
                return feature in features
    except:
        pass
    
    # 检查特定功能的标志文件
    feature_file = f'/etc/wubuntu/features.d/{feature}'
    if os.path.exists(feature_file):
        return True
    
    return False 