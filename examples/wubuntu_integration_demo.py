#!/usr/bin/env python3
"""
Wubuntu集成演示 - 展示AIgo在Wubuntu系统环境中的功能

Wubuntu是Ubuntu的特殊版本，与Windows进行了深度集成的独立系统。
此示例演示了如何使用AIgo的平台工具来识别和利用Wubuntu环境的特性，
包括跨系统文件访问、依赖管理和系统集成功能。
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.platform_utils import (
    # 平台检测
    is_wubuntu, get_platform_info,
    
    # Wubuntu特定功能
    get_wubuntu_version, get_windows_path, get_ubuntu_path_from_windows,
    convert_path, run_windows_command, get_wubuntu_system_info,
    setup_wubuntu_integration, is_wubuntu_feature_enabled,
    
    # Wubuntu依赖管理
    check_wubuntu_dependencies, check_windows_dependencies,
    install_wubuntu_dependencies, install_windows_dependencies,
    setup_wubuntu_development_environment, get_wubuntu_dependency_status
)

def print_section(title):
    """打印带有分隔线的节标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_json(data):
    """以格式化的JSON形式打印数据"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    """Wubuntu集成演示主函数"""
    print_section("Wubuntu集成演示")
    
    # 检查是否在Wubuntu环境中运行
    if not is_wubuntu():
        print("此演示需要在Wubuntu环境中运行。")
        print(f"当前平台: {get_platform_info()['os_type']}")
        return
    
    # 1. 显示Wubuntu系统信息
    print_section("Wubuntu系统信息")
    wubuntu_info = get_wubuntu_system_info()
    print_json(wubuntu_info)
    
    # 2. 路径转换演示
    print_section("路径转换演示")
    
    # 获取Windows路径
    windows_path = get_windows_path()
    print(f"Windows挂载路径: {windows_path}")
    
    # 演示路径转换
    test_paths = [
        "/home/user/documents/file.txt",
        f"{windows_path}/Users/Public/Documents/file.txt",
        "C:\\Users\\Public\\Documents\\file.txt"
    ]
    
    for path in test_paths:
        win_path = convert_path(path, to_windows=True)
        linux_path = convert_path(path, to_windows=False)
        print(f"\n原始路径: {path}")
        print(f"Windows格式: {win_path}")
        print(f"Linux格式: {linux_path}")
    
    # 3. 依赖检查
    print_section("依赖检查")
    
    # 检查Wubuntu核心依赖
    print("\nWubuntu核心依赖:")
    core_deps = check_wubuntu_dependencies(category='core')
    print_json(core_deps)
    
    # 检查Windows依赖
    print("\nWindows核心依赖:")
    win_deps = check_windows_dependencies(category='core')
    print_json(win_deps)
    
    # 4. Windows命令执行
    print_section("Windows命令执行")
    
    try:
        # 执行Windows系统信息命令
        print("\n执行Windows系统信息命令:")
        returncode, stdout, stderr = run_windows_command("systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\"", capture_output=True)
        if returncode == 0:
            print(stdout)
        else:
            print(f"命令执行失败: {stderr}")
        
        # 执行Windows目录列表命令
        print("\n执行Windows目录列表命令:")
        returncode, stdout, stderr = run_windows_command("dir %USERPROFILE%\\Documents", capture_output=True)
        if returncode == 0:
            print(stdout)
        else:
            print(f"命令执行失败: {stderr}")
    except Exception as e:
        print(f"执行Windows命令时出错: {e}")
    
    # 5. 集成功能检查
    print_section("集成功能检查")
    
    # 检查WSLg支持
    print(f"WSLg支持: {'已启用' if is_wubuntu_feature_enabled('wslg') else '未启用'}")
    
    # 检查Wubuntu桥接工具
    print(f"Wubuntu桥接工具: {'已安装' if is_wubuntu_feature_enabled('win-bridge') else '未安装'}")
    
    # 6. 依赖状态报告
    print_section("依赖状态报告")
    
    status = get_wubuntu_dependency_status()
    print(f"集成状态: {status.get('integration_status', 'unknown')}")
    
    # 7. 设置建议
    print_section("设置建议")
    
    if status.get('integration_status') != "fully_integrated":
        print("建议执行以下操作以完善Wubuntu集成:")
        print("1. 运行 setup_wubuntu_integration() 设置基本集成")
        print("2. 运行 setup_wubuntu_development_environment() 设置开发环境")
        print("3. 安装缺失的依赖项")
    else:
        print("您的Wubuntu环境已完全集成，无需额外设置。")
    
    print("\n演示完成！")

if __name__ == "__main__":
    main() 