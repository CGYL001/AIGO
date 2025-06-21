#!/usr/bin/env python
"""
AIgo 智能安装向导

此脚本提供了交互式安装体验，引导用户完成AIgo的安装过程，
包括环境检测、依赖安装、模型下载和配置设置。

用法:
    python install_wizard.py [--advanced]

选项:
    --advanced    启用高级安装选项
"""

import os
import sys
import platform
import subprocess
import json
import shutil
import argparse
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union

# 颜色输出支持
class Colors:
    """终端颜色代码"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Windows终端颜色支持
if platform.system() == "Windows":
    os.system('color')

def print_header(text: str) -> None:
    """打印带颜色的标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")

def print_step(step: str, text: str) -> None:
    """打印步骤信息"""
    print(f"{Colors.BLUE}[{step}]{Colors.ENDC} {text}")

def print_success(text: str) -> None:
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str) -> None:
    """打印警告信息"""
    print(f"{Colors.YELLOW}! {text}{Colors.ENDC}")

def print_error(text: str) -> None:
    """打印错误信息"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def run_command(cmd: List[str], silent: bool = False) -> Tuple[int, str, str]:
    """
    运行命令并返回结果
    
    Args:
        cmd: 要执行的命令列表
        silent: 是否静默执行
        
    Returns:
        (返回码, 标准输出, 标准错误)
    """
    if not silent:
        print(f"执行: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        return -1, "", str(e)

def check_python_version() -> bool:
    """
    检查Python版本是否满足要求
    
    Returns:
        是否满足版本要求
    """
    print_step("1", "检查Python版本")
    
    major, minor, _ = sys.version_info[:3]
    if major < 3 or (major == 3 and minor < 9):
        print_error(f"Python版本 {major}.{minor} 不满足要求")
        print_warning("AIgo需要Python 3.9或更高版本")
        print_warning("请安装更新的Python版本: https://www.python.org/downloads/")
        return False
    
    print_success(f"Python版本 {major}.{minor} 满足要求")
    return True

def check_pip() -> bool:
    """
    检查pip是否可用
    
    Returns:
        pip是否可用
    """
    print_step("2", "检查pip可用性")
    
    returncode, stdout, stderr = run_command([sys.executable, "-m", "pip", "--version"], silent=True)
    if returncode != 0:
        print_error("pip未安装或不可用")
        print_warning("请安装pip: https://pip.pypa.io/en/stable/installation/")
        return False
    
    print_success(f"pip可用: {stdout.strip()}")
    return True

def check_dependencies() -> List[str]:
    """
    检查必要的依赖是否已安装
    
    Returns:
        缺失的依赖列表
    """
    print_step("3", "检查依赖")
    
    required_packages = [
        "typer",
        "requests",
        "pydantic",
        "fastapi",
        "uvicorn",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            print_warning(f"未安装: {package}")
            missing_packages.append(package)
        else:
            print_success(f"已安装: {package}")
    
    return missing_packages

def install_dependencies(packages: List[str]) -> bool:
    """
    安装缺失的依赖
    
    Args:
        packages: 要安装的包列表
        
    Returns:
        安装是否成功
    """
    if not packages:
        return True
    
    print_step("4", f"安装缺失的依赖: {', '.join(packages)}")
    
    returncode, stdout, stderr = run_command(
        [sys.executable, "-m", "pip", "install"] + packages
    )
    
    if returncode != 0:
        print_error(f"依赖安装失败: {stderr}")
        return False
    
    print_success("依赖安装成功")
    return True

def check_ollama() -> bool:
    """
    检查Ollama是否已安装
    
    Returns:
        Ollama是否已安装
    """
    print_step("5", "检查Ollama安装")
    
    # 检查ollama命令是否可用
    if platform.system() == "Windows":
        returncode, stdout, stderr = run_command(["where", "ollama"], silent=True)
    else:
        returncode, stdout, stderr = run_command(["which", "ollama"], silent=True)
    
    if returncode != 0:
        print_warning("Ollama未安装或不在PATH中")
        return False
    
    # 检查ollama服务是否运行
    if platform.system() == "Windows":
        # Windows上检查服务
        returncode, stdout, stderr = run_command(["tasklist", "/fi", "imagename eq ollama.exe"], silent=True)
        if "ollama.exe" not in stdout:
            print_warning("Ollama服务未运行")
            return False
    else:
        # Linux/macOS上检查服务
        returncode, stdout, stderr = run_command(["pgrep", "ollama"], silent=True)
        if returncode != 0:
            print_warning("Ollama服务未运行")
            return False
    
    print_success("Ollama已安装并运行")
    return True

def install_ollama() -> bool:
    """
    引导用户安装Ollama
    
    Returns:
        是否成功引导安装
    """
    print_step("6", "安装Ollama")
    
    system = platform.system()
    
    print("Ollama是AIgo的默认模型后端，需要先安装。")
    
    if system == "Windows":
        print("请从以下链接下载并安装Ollama:")
        print("https://ollama.com/download/windows")
    elif system == "Darwin":  # macOS
        print("请运行以下命令安装Ollama:")
        print("curl -fsSL https://ollama.com/install.sh | sh")
    elif system == "Linux":
        print("请运行以下命令安装Ollama:")
        print("curl -fsSL https://ollama.com/install.sh | sh")
    else:
        print_error(f"不支持的操作系统: {system}")
        return False
    
    input("\n安装完成后按回车键继续...")
    return check_ollama()

def download_models() -> bool:
    """
    下载默认模型
    
    Returns:
        下载是否成功
    """
    print_step("7", "下载默认模型")
    
    if not check_ollama():
        print_error("Ollama未安装或未运行，无法下载模型")
        return False
    
    models = [
        "deepseek-r1:8b",  # 默认推理模型
        "bge-m3"           # 默认嵌入模型
    ]
    
    success = True
    for model in models:
        print(f"下载模型: {model}")
        returncode, stdout, stderr = run_command(["ollama", "pull", model])
        if returncode != 0:
            print_error(f"模型 {model} 下载失败: {stderr}")
            success = False
        else:
            print_success(f"模型 {model} 下载成功")
    
    return success

def install_aigo() -> bool:
    """
    安装AIgo包
    
    Returns:
        安装是否成功
    """
    print_step("8", "安装AIgo")
    
    # 检查是否在AIgo目录中
    current_dir = Path.cwd()
    setup_py = current_dir / "setup.py"
    
    if setup_py.exists():
        # 从源码安装
        print("检测到AIgo源码，从源码安装...")
        returncode, stdout, stderr = run_command(
            [sys.executable, "-m", "pip", "install", "-e", "."]
        )
    else:
        # 从PyPI安装
        print("从PyPI安装AIgo...")
        returncode, stdout, stderr = run_command(
            [sys.executable, "-m", "pip", "install", "aigo"]
        )
    
    if returncode != 0:
        print_error(f"AIgo安装失败: {stderr}")
        return False
    
    print_success("AIgo安装成功")
    return True

def create_config() -> bool:
    """
    创建基本配置文件
    
    Returns:
        创建是否成功
    """
    print_step("9", "创建配置文件")
    
    # 确定配置目录
    if platform.system() == "Windows":
        config_dir = Path(os.environ.get("APPDATA", "")) / "aigo" / "config"
    else:
        config_dir = Path.home() / ".config" / "aigo"
    
    # 创建配置目录
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建默认配置
    config = {
        "app": {
            "host": "localhost",
            "port": 8000,
            "debug": False,
            "log_level": "info"
        },
        "models": {
            "inference": {
                "name": "deepseek-r1:8b",
                "provider": "ollama",
                "api_base": "http://localhost:11434",
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "embedding": {
                "name": "bge-m3",
                "provider": "ollama",
                "dimensions": 1024
            }
        }
    }
    
    # 写入配置文件
    config_file = config_dir / "config.json"
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print_success(f"配置文件已创建: {config_file}")
        return True
    except Exception as e:
        print_error(f"配置文件创建失败: {e}")
        return False

def verify_installation() -> bool:
    """
    验证AIgo安装
    
    Returns:
        验证是否成功
    """
    print_step("10", "验证安装")
    
    try:
        import aigo
        print_success(f"AIgo导入成功，版本: {getattr(aigo, '__version__', '未知')}")
        
        # 尝试创建一个基本的模型配置
        from aigo.models.base import ModelConfig
        config = ModelConfig(
            provider="ollama",
            model_name="deepseek-r1:8b"
        )
        print_success(f"模型配置创建成功: {config}")
        
        return True
    except ImportError as e:
        print_error(f"AIgo导入失败: {e}")
        return False
    except Exception as e:
        print_error(f"验证失败: {e}")
        return False

def setup_cursor_integration() -> bool:
    """
    设置与Cursor编辑器的集成
    
    Returns:
        设置是否成功
    """
    print_step("11", "设置Cursor集成")
    
    print("Cursor是一个AI驱动的代码编辑器，可以与AIgo无缝集成。")
    choice = input("是否要设置与Cursor的集成？(y/n): ").lower()
    
    if choice != 'y':
        print("跳过Cursor集成设置")
        return True
    
    # 检查Cursor是否已安装
    cursor_paths = []
    if platform.system() == "Windows":
        cursor_paths = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Cursor" / "Cursor.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "Cursor" / "Cursor.exe"
        ]
    elif platform.system() == "Darwin":  # macOS
        cursor_paths = [
            Path("/Applications/Cursor.app/Contents/MacOS/Cursor")
        ]
    elif platform.system() == "Linux":
        cursor_paths = [
            Path("/usr/bin/cursor"),
            Path("/usr/local/bin/cursor")
        ]
    
    cursor_installed = any(path.exists() for path in cursor_paths)
    
    if not cursor_installed:
        print_warning("未检测到Cursor安装")
        print("请从以下链接下载并安装Cursor:")
        print("https://cursor.sh/")
        return False
    
    print_success("检测到Cursor安装")
    
    # 创建Cursor集成配置
    cursor_config_dir = Path.home() / ".cursor" / "extensions"
    cursor_config_dir.mkdir(parents=True, exist_ok=True)
    
    cursor_config = {
        "aiProvider": "local",
        "localAIPath": "aigo",
        "enableAIAssistant": True
    }
    
    cursor_config_file = cursor_config_dir / "aigo-integration.json"
    try:
        with open(cursor_config_file, "w") as f:
            json.dump(cursor_config, f, indent=2)
        print_success(f"Cursor集成配置已创建: {cursor_config_file}")
        return True
    except Exception as e:
        print_error(f"Cursor集成配置创建失败: {e}")
        return False

def show_completion_message() -> None:
    """显示安装完成信息"""
    print_header("AIgo安装完成！")
    
    print("\n基本使用:")
    print("  aigo run                   # 启动交互式会话")
    print("  aigo serve                 # 启动API服务")
    print("  aigo config list           # 查看配置")
    
    print("\n文档:")
    print("  https://github.com/yourusername/AIgo/blob/main/README.md")
    
    print("\n如需帮助:")
    print("  aigo --help                # 显示帮助信息")
    print("  python -m aigo.cli --help  # 显示详细帮助")

def main() -> int:
    """
    主函数
    
    Returns:
        退出代码 (0表示成功)
    """
    parser = argparse.ArgumentParser(description="AIgo 智能安装向导")
    parser.add_argument("--advanced", action="store_true", help="启用高级安装选项")
    args = parser.parse_args()
    
    print_header("AIgo 智能安装向导")
    print("此向导将引导您完成AIgo的安装过程。")
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 检查pip
    if not check_pip():
        return 1
    
    # 检查依赖
    missing_packages = check_dependencies()
    
    # 安装依赖
    if missing_packages and not install_dependencies(missing_packages):
        return 1
    
    # 检查Ollama
    ollama_installed = check_ollama()
    
    # 安装Ollama
    if not ollama_installed and not install_ollama():
        print_warning("Ollama安装未完成，但将继续安装AIgo")
    
    # 下载模型
    if ollama_installed and not download_models():
        print_warning("模型下载未完成，但将继续安装AIgo")
    
    # 安装AIgo
    if not install_aigo():
        return 1
    
    # 创建配置
    if not create_config():
        print_warning("配置创建失败，将使用默认配置")
    
    # 验证安装
    if not verify_installation():
        print_error("AIgo安装验证失败")
        return 1
    
    # 高级选项：Cursor集成
    if args.advanced:
        setup_cursor_integration()
    
    # 显示完成信息
    show_completion_message()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 