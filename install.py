#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AIgo自动安装脚本
用于简化依赖安装和环境配置
"""

import os
import sys
import platform
import subprocess
import argparse
from pathlib import Path

# 定义颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# 定义安装模式
INSTALLATION_MODES = {
    "core": "仅安装核心依赖",
    "api": "安装API服务依赖",
    "ml": "安装机器学习依赖",
    "dev": "安装开发环境依赖", 
    "all": "安装全部依赖",
    "wubuntu": "安装Wubuntu特定依赖"
}

def print_header(text):
    """打印带颜色的标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.END}\n")

def print_success(text):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    """打印信息消息"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def run_command(command, error_message=None):
    """运行Shell命令"""
    try:
        process = subprocess.run(
            command, 
            shell=True, 
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return True, process.stdout
    except subprocess.CalledProcessError as e:
        if error_message:
            print_error(f"{error_message}: {e}")
        return False, e.stderr

def check_python_version():
    """检查Python版本"""
    print_info(f"检查Python版本...")
    
    major, minor, _ = platform.python_version_tuple()
    version_str = f"{major}.{minor}"
    
    if int(major) < 3 or (int(major) == 3 and int(minor) < 9):
        print_error(f"Python版本过低: {version_str}。需要Python 3.9+")
        return False
    
    print_success(f"Python版本兼容: {version_str}")
    return True

def check_pip():
    """检查pip是否可用"""
    print_info("检查pip...")
    
    success, output = run_command("pip --version", "pip未安装或不在PATH中")
    
    if not success:
        print_error("pip检查失败")
        return False
    
    print_success("pip可用")
    return True

def create_virtual_env():
    """创建虚拟环境"""
    print_header("创建虚拟环境")
    
    if os.path.exists("venv"):
        print_info("虚拟环境已存在，跳过创建步骤")
        return True
    
    success, _ = run_command("python -m venv venv", "创建虚拟环境失败")
    
    if not success:
        print_error("无法创建虚拟环境")
        return False
    
    print_success("虚拟环境已创建")
    return True

def activate_venv():
    """激活虚拟环境"""
    print_info("激活虚拟环境...")
    
    if sys.platform.startswith("win"):
        activate_script = "venv\\Scripts\\activate"
        print_warning(f"请手动激活虚拟环境: {activate_script}")
    else:
        activate_script = "source venv/bin/activate"
        print_warning(f"请手动激活虚拟环境: {activate_script}")
    
    return True

def install_dependencies(mode="core"):
    """安装依赖"""
    print_header(f"安装{INSTALLATION_MODES[mode]}...")
    
    requirements_file = f"requirements-{mode}.txt"
    
    if not os.path.exists(requirements_file):
        print_error(f"依赖文件不存在: {requirements_file}")
        return False
    
    success, output = run_command(f"pip install -r {requirements_file}", f"安装{mode}依赖失败")
    
    if not success:
        print_error(f"{mode}依赖安装失败")
        return False
    
    print_success(f"{mode}依赖安装成功")
    return True

def install_package():
    """安装项目包"""
    print_header("安装AIgo包...")
    
    success, output = run_command("pip install -e .", "安装项目失败")
    
    if not success:
        print_error("AIgo包安装失败")
        return False
    
    print_success("AIgo包安装成功")
    return True

def detect_platform():
    """检测平台特定信息"""
    print_header("检测平台信息")
    
    system = platform.system()
    machine = platform.machine()
    
    print_info(f"操作系统: {system}")
    print_info(f"架构: {machine}")
    
    # 检查是否为Wubuntu
    is_wubuntu = False
    if system == "Linux":
        try:
            # 检查是否存在wubuntu特定文件
            if os.path.exists('/etc/wubuntu-release'):
                is_wubuntu = True
                print_info("检测到Wubuntu系统")
            # 检查lsb-release文件
            elif os.path.exists('/etc/lsb-release'):
                with open('/etc/lsb-release', 'r') as f:
                    content = f.read().lower()
                    if 'wubuntu' in content:
                        is_wubuntu = True
                        print_info("检测到Wubuntu系统")
        except:
            pass
        
        if is_wubuntu:
            print_warning("Wubuntu平台需要特殊注意:")
            print_warning("- 需要安装wubuntu特定依赖")
            print_warning("- 建议使用 --wubuntu 安装选项")
    
    if system == "Windows":
        print_warning("Windows平台需要特殊注意:")
        print_warning("- 某些依赖可能需要手动安装(faiss-cpu, bitsandbytes)")
        print_warning("- 请查看requirements-ml.txt中的Windows注释")
    
    elif system == "Darwin" and machine == "arm64":
        print_warning("Apple Silicon (M1/M2/M3 Mac) 需要特殊注意:")
        print_warning("- 确保使用适配的PyTorch版本")
    
    return system, machine, is_wubuntu

def setup_config():
    """设置基本配置"""
    print_header("设置配置")
    
    # 创建必要的目录
    directories = ["data", "logs", "models/registry/models"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print_success(f"创建目录: {directory}")
    
    # 检查配置文件
    config_path = "config/default/config.json"
    if os.path.exists(config_path):
        print_success(f"配置文件已存在: {config_path}")
    else:
        print_warning(f"配置文件不存在: {config_path}")
        print_warning("请确保配置文件存在并正确设置")
    
    return True

def show_post_install_message():
    """显示安装后消息"""
    print_header("安装完成")
    
    print_info("AIgo安装已完成，您现在可以:")
    print("1. 激活虚拟环境:")
    if sys.platform.startswith("win"):
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. 验证安装:")
    print("   python -c \"from AIGO import __version__; print(f'AIgo {__version__} 已成功安装')\"")
    
    print("\n3. 运行简单示例:")
    print("   python simple_example.py")
    
    print("\n4. 查看项目导航:")
    print("   cat PATH_GUIDE.md")
    
    print("\n5. 使用路径查找工具:")
    print("   python tools/path_finder.py list-features")
    
    print("\n6. 运行模型管理面板:")
    print("   python tools/models_dashboard.py")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}感谢使用AIgo!{Colors.END}")
    print(f"{Colors.BLUE}如有问题，请查阅文档或联系项目维护者{Colors.END}")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AIgo安装脚本")
    
    parser.add_argument("--mode", choices=list(INSTALLATION_MODES.keys()), default="core",
                       help="安装模式: core(仅核心), api(API服务), ml(机器学习), dev(开发环境), all(全部依赖), wubuntu(Wubuntu特定依赖)")
    
    parser.add_argument("--no-venv", action="store_true",
                       help="不创建虚拟环境")
    
    parser.add_argument("--update", action="store_true",
                       help="更新已安装的依赖")
    
    parser.add_argument("--wubuntu", action="store_true",
                       help="安装Wubuntu特定依赖")
    
    return parser.parse_args()

def main():
    """主函数"""
    print_header("AIgo安装助手")
    
    args = parse_args()
    
    # 检查环境
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # 检测平台
    system, machine, is_wubuntu = detect_platform()
    
    # 如果检测到Wubuntu系统或用户指定了--wubuntu选项，则设置模式为wubuntu
    if is_wubuntu or args.wubuntu:
        if args.mode == "core" and not args.wubuntu:
            print_warning("检测到Wubuntu系统，建议使用 --wubuntu 选项安装Wubuntu特定依赖")
        if args.wubuntu:
            args.mode = "wubuntu"
            print_info("将安装Wubuntu特定依赖")
    
    # 创建和激活虚拟环境
    if not args.no_venv:
        if not create_virtual_env():
            sys.exit(1)
        activate_venv()
    
    # 安装依赖
    if args.update:
        pip_cmd = "pip install -U -r"
        print_info("更新模式: 将更新已安装的依赖")
    else:
        pip_cmd = "pip install -r"
    
    # 安装依赖
    if not install_dependencies(args.mode):
        sys.exit(1)
    
    # 如果是wubuntu模式，还需要安装系统特定包
    if args.mode == "wubuntu" or args.wubuntu:
        print_info("安装Wubuntu特定系统包...")
        print_warning("请确保您有sudo权限")
        print_warning("如需手动安装，请运行: sudo apt-get install -y wubuntu-specific-package")
        try:
            run_command("sudo apt-get update", "更新包索引失败")
            success, _ = run_command("sudo apt-get install -y wubuntu-specific-package", "安装Wubuntu特定包失败")
            if success:
                print_success("Wubuntu特定系统包安装成功")
            else:
                print_warning("Wubuntu特定系统包安装失败，请手动安装")
        except:
            print_warning("无法自动安装系统包，请手动安装")
    
    # 安装项目包
    if not install_package():
        sys.exit(1)
    
    # 设置配置
    setup_config()
    
    # 显示安装后消息
    show_post_install_message()

if __name__ == "__main__":
    main() 