#!/usr/bin/env python
"""
AIgo 启动脚本

这个脚本是一个便捷的入口点，用于启动AIgo的各种功能。
不依赖于包安装，可以直接从项目根目录运行。
"""
import sys
import os
import importlib
from pathlib import Path

# 确保可以直接导入aigo包
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# 尝试直接导入CLI应用
try:
    # 首先尝试标准导入
    from aigo.cli.__main__ import app
    has_app = True
except ImportError:
    has_app = False
    print("Warning: Could not import aigo package normally, trying direct import...")
    
    # 检查aigo目录结构
    if not (project_root / "aigo").exists():
        print(f"Error: aigo directory not found at {project_root / 'aigo'}")
        sys.exit(1)
        
    # 尝试直接导入模块
    try:
        # 动态导入CLI模块
        spec = importlib.util.spec_from_file_location(
            "cli_main", 
            project_root / "aigo" / "cli" / "__main__.py"
        )
        cli_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli_main)
        
        # 获取app对象
        app = getattr(cli_main, "app", None)
        if app is None:
            print("Error: Could not find app object in aigo.cli.__main__")
            sys.exit(1)
        has_app = True
    except Exception as e:
        print(f"Error importing CLI module: {e}")
        sys.exit(1)


def main():
    """主入口函数"""
    # 显示欢迎信息
    try:
        # 尝试获取版本
        version = "0.1.0"  # 默认版本
        try:
            from aigo import __version__
            version = __version__
        except ImportError:
            pass
            
        print(f"AIgo v{version}")
        print("=" * 40)
        print("AI助手平台 - 支持多种模型的通用接口")
        print("=" * 40)
        
        # 显示可用命令
        print("\n可用命令:")
        print("  run        运行模型生成")
        print("  serve      启动服务器")
        print("  config     管理配置")
        print("  version    查看版本信息")
        print("\n使用 --help 参数查看详细帮助")
        print("=" * 40)
    except Exception as e:
        print(f"Warning: {e}")
    
    # 启动CLI
    if has_app:
        app()
    else:
        print("Error: Could not start AIgo CLI")
        sys.exit(1)


if __name__ == "__main__":
    main() 