"""
平台工具模块

此包提供用于跨平台兼容性的工具函数和类。
包括平台检测、依赖管理和路径处理等功能。
"""

# 先导入基础模块
from .detection import (
    get_platform_info, 
    is_windows, 
    is_linux, 
    is_macos, 
    is_wsl, 
    is_wubuntu,
    get_os_name,
    get_wsl_version,
    get_wubuntu_version,
    get_gpu_info,
    get_cpu_info,
    get_ram_info,
    get_disk_info,
    get_network_info,
    is_docker
)

# 再导入依赖于基础模块的功能
from .dependencies import (
    check_dependency,
    check_python_package,
    get_package_version,
    check_dependencies,
    check_python_dependencies,
    install_python_package
)

# 导入路径处理工具
from .path_utils import (
    normalize_path,
    get_platform_path,
    ensure_dir_exists,
    get_temp_dir,
    get_user_home_dir,
    get_app_data_dir
)

__all__ = [
    # 平台检测
    'get_platform_info', 
    'is_windows', 
    'is_linux', 
    'is_macos', 
    'is_wsl', 
    'is_wubuntu',
    'get_os_name',
    'get_wsl_version',
    'get_wubuntu_version',
    'get_gpu_info',
    'get_cpu_info',
    'get_ram_info',
    'get_disk_info',
    'get_network_info',
    'is_docker',
    
    # 依赖管理
    'check_dependency',
    'check_python_package',
    'get_package_version',
    'check_dependencies',
    'check_python_dependencies',
    'install_python_package',
    
    # 路径处理
    'normalize_path',
    'get_platform_path',
    'ensure_dir_exists',
    'get_temp_dir',
    'get_user_home_dir',
    'get_app_data_dir'
] 