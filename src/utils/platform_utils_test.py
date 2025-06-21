#!/usr/bin/env python
"""
平台兼容性工具测试脚本

用于测试和演示平台工具的使用。
"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.platform_utils import (
    get_platform_info,
    is_windows, is_linux, is_macos, is_wsl, is_wubuntu,
    normalize_path, get_home_dir, get_app_data_dir, get_config_dir, get_logs_dir,
    convert_wsl_path,
    run_background_process, kill_process, is_process_running,
    check_platform_dependencies
)

def display_platform_info():
    """显示平台信息"""
    print("\n===== 平台信息 =====")
    info = get_platform_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print(f"\n当前系统: {'Windows' if is_windows() else 'Linux' if is_linux() else 'macOS' if is_macos() else '未知'}")
    if is_linux():
        print(f"是否为WSL: {is_wsl()}")
        print(f"是否为Wubuntu: {is_wubuntu()}")

def display_path_info():
    """显示路径信息"""
    print("\n===== 路径信息 =====")
    print(f"用户主目录: {get_home_dir()}")
    print(f"应用数据目录: {get_app_data_dir('aigo')}")
    print(f"配置目录: {get_config_dir('aigo')}")
    print(f"日志目录: {get_logs_dir('aigo')}")
    
    # 测试路径转换
    test_paths = []
    if is_windows():
        test_paths = ["C:\\Users\\user\\Desktop", "D:\\Projects\\aigo"]
    elif is_wsl():
        test_paths = ["/mnt/c/Users/user/Desktop", "/home/user/projects"]
    elif is_wubuntu():
        test_paths = ["/home/wubuntu/Desktop", "/opt/wubuntu/projects"]
    else:
        test_paths = ["/home/user/Desktop", "/usr/local/bin"]
    
    print("\n路径规范化示例:")
    for path in test_paths:
        print(f"  原始: {path}")
        print(f"  规范化: {normalize_path(path)}")
        
    if is_windows() or is_wsl():
        print("\nWSL路径转换示例:")
        for path in test_paths:
            print(f"  原始: {path}")
            print(f"  转换: {convert_wsl_path(path)}")

def test_process_management():
    """测试进程管理功能"""
    print("\n===== 进程管理测试 =====")
    
    # 在后台启动一个简单进程
    cmd = ["python", "-c", "import time; time.sleep(5)"]
    pid = run_background_process(cmd)
    
    print(f"启动后台进程，PID: {pid}")
    print(f"进程是否运行中: {is_process_running(pid)}")
    
    # 终止进程
    print(f"正在终止进程...")
    killed = kill_process(pid)
    print(f"进程终止结果: {'成功' if killed else '失败'}")
    print(f"进程是否仍在运行: {is_process_running(pid)}")

def check_dependencies():
    """检查依赖项"""
    print("\n===== 依赖项检查 =====")
    
    # 检查平台特定依赖
    ml_deps = check_platform_dependencies('ml')
    print("\n机器学习依赖项:")
    for dep, status in ml_deps.items():
        installed = status['installed']
        version = status['version'] or '未知'
        print(f"  {dep}: {'已安装' if installed else '未安装'} (版本: {version})")
    
    system_deps = check_platform_dependencies('system')
    print("\n系统依赖项:")
    for dep, status in system_deps.items():
        installed = status['installed']
        version = status['version'] or '未知'
        print(f"  {dep}: {'已安装' if installed else '未安装'} (版本: {version})")
    
    # 如果是wubuntu，显示wubuntu特定依赖
    if is_wubuntu():
        print("\nWubuntu特定依赖项:")
        print("  wubuntu-specific-package: 检查中...")
        try:
            import subprocess
            result = subprocess.run(["dpkg", "-l", "wubuntu-specific-package"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
            if result.returncode == 0:
                print("  wubuntu-specific-package: 已安装")
            else:
                print("  wubuntu-specific-package: 未安装")
        except:
            print("  wubuntu-specific-package: 检查失败")

def main():
    """主函数"""
    print("AIgo 跨平台兼容性工具测试")
    print("=" * 40)
    
    # 显示平台信息
    display_platform_info()
    
    # 显示路径信息
    display_path_info()
    
    # 测试进程管理
    test_process_management()
    
    # 检查依赖项
    check_dependencies()

if __name__ == "__main__":
    main() 