#!/usr/bin/env python
"""
开发环境设置脚本

此脚本帮助设置开发环境，包括：
1. 检查必要的依赖是否已安装
2. 创建必要的目录结构
3. 设置环境变量
4. 提供开发指南

用法：
    python scripts/setup_dev.py
"""

import sys
import os
import subprocess
import importlib.util
import platform
from pathlib import Path


def check_python_version():
    """检查Python版本是否满足要求"""
    print("检查Python版本...")
    
    major, minor, _ = sys.version_info[:3]
    if major < 3 or (major == 3 and minor < 9):
        print(f"[!] 警告: 当前Python版本 {major}.{minor} 低于推荐的3.9+")
        print("    某些功能可能无法正常工作。")
        return False
    
    print(f"[✓] Python版本 {major}.{minor} 满足要求")
    return True


def check_dependencies():
    """检查必要的依赖是否已安装"""
    print("\n检查依赖...")
    
    required_packages = [
        "typer",
        "requests",
    ]
    
    optional_packages = [
        "fastapi",
        "uvicorn",
        "pytest",
    ]
    
    missing_required = []
    missing_optional = []
    
    # 检查必须依赖
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_required.append(package)
        else:
            print(f"[✓] 已安装 {package}")
    
    # 检查可选依赖
    for package in optional_packages:
        if importlib.util.find_spec(package) is None:
            missing_optional.append(package)
        else:
            print(f"[✓] 已安装 {package}")
    
    # 报告缺失的依赖
    if missing_required:
        print(f"\n[!] 缺少必要依赖: {', '.join(missing_required)}")
        print("    请运行: pip install -r requirements.txt")
    
    if missing_optional:
        print(f"\n[!] 缺少可选依赖: {', '.join(missing_optional)}")
        print("    完整安装请运行: pip install -r requirements.txt")
    
    return len(missing_required) == 0


def setup_env_vars():
    """设置环境变量"""
    print("\n设置环境变量...")
    
    project_root = Path(__file__).resolve().parent.parent
    
    if platform.system() == "Windows":
        # Windows环境变量设置
        print("生成Windows环境变量设置脚本...")
        
        bat_path = project_root / "set_env.bat"
        with open(bat_path, "w") as f:
            f.write(f"@echo off\n")
            f.write(f"set PYTHONPATH={project_root}\n")
            f.write(f"echo 环境变量已设置！\n")
            f.write(f"echo PYTHONPATH = %PYTHONPATH%\n")
        
        print(f"[✓] 创建了环境变量设置脚本: {bat_path}")
        print(f"    使用方法: .\\set_env.bat")
        
    else:
        # Unix环境变量设置
        print("生成Unix环境变量设置脚本...")
        
        sh_path = project_root / "set_env.sh"
        with open(sh_path, "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"export PYTHONPATH={project_root}\n")
            f.write(f"echo 环境变量已设置！\n")
            f.write(f"echo PYTHONPATH = $PYTHONPATH\n")
        
        # 设置可执行权限
        os.chmod(sh_path, 0o755)
        
        print(f"[✓] 创建了环境变量设置脚本: {sh_path}")
        print(f"    使用方法: source ./set_env.sh")


def check_directory_structure():
    """检查并创建必要的目录结构"""
    print("\n检查目录结构...")
    
    project_root = Path(__file__).resolve().parent.parent
    
    # 检查核心目录
    directories = [
        project_root / "aigo" / "models" / "providers",
        project_root / "aigo" / "cli",
        project_root / "aigo" / "runtime",
        project_root / "aigo" / "adapters",
        project_root / "examples",
        project_root / "tests" / "unit",
        project_root / "tests" / "integration",
    ]
    
    for directory in directories:
        if not directory.exists():
            print(f"[+] 创建目录: {directory.relative_to(project_root)}")
            directory.mkdir(parents=True, exist_ok=True)
        else:
            print(f"[✓] 目录已存在: {directory.relative_to(project_root)}")


def check_installation():
    """检查AIgo包是否已安装"""
    print("\n检查AIgo包安装状态...")
    
    try:
        import aigo
        print(f"[✓] AIgo已安装，版本: {getattr(aigo, '__version__', '未知')}")
        print(f"    安装路径: {aigo.__file__}")
        return True
    except ImportError:
        print("[!] AIgo包未安装或无法导入")
        
        # 检查是否可以直接导入
        project_root = Path(__file__).resolve().parent.parent
        aigo_init = project_root / "aigo" / "__init__.py"
        
        if aigo_init.exists():
            print(f"[i] 找到AIgo包源码: {aigo_init}")
            print(f"[i] 推荐使用开发模式安装: pip install -e .")
        else:
            print(f"[!] 未找到AIgo包源码")
        
        return False


def print_development_guide():
    """打印开发指南"""
    print("\n开发指南")
    print("========")
    print("1. 设置环境变量:")
    if platform.system() == "Windows":
        print("   .\\set_env.bat")
    else:
        print("   source ./set_env.sh")
    
    print("\n2. 安装开发依赖:")
    print("   pip install -r requirements.txt")
    
    print("\n3. 开发模式安装:")
    print("   pip install -e .")
    
    print("\n4. 运行测试:")
    print("   pytest tests/")
    
    print("\n5. 运行AIgo:")
    print("   python run_aigo.py")
    
    print("\n6. 运行示例:")
    print("   python examples/run_simple.py")
    
    print("\n祝您开发愉快！")


def main():
    """主函数"""
    print("AIgo开发环境设置")
    print("===============\n")
    
    # 检查Python版本
    check_python_version()
    
    # 检查依赖
    check_dependencies()
    
    # 检查目录结构
    check_directory_structure()
    
    # 检查安装状态
    check_installation()
    
    # 设置环境变量
    setup_env_vars()
    
    # 打印开发指南
    print_development_guide()


if __name__ == "__main__":
    main() 