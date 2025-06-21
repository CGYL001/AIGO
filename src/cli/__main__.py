#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AIgo命令行工具入口点

提供命令行接口，用于访问AIgo的所有功能
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("aigo_cli")

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 可用命令列表
AVAILABLE_COMMANDS = {
    "feature": {
        "description": "特性管理命令",
        "module": "src.cli.feature_cmd"
    },
    "model-restructure": {
        "description": "模型重构命令",
        "module": "src.cli.model_restructure_cmd"
    }
}

def run_command(args):
    """运行命令"""
    command_name = args.command
    if command_name not in AVAILABLE_COMMANDS:
        logger.error(f"未知命令: {command_name}")
        return 1
    
    # 获取命令模块路径
    module_path = AVAILABLE_COMMANDS[command_name]["module"]
    
    try:
        # 动态导入命令模块
        command_module = __import__(module_path, fromlist=["main"])
        
        # 运行命令
        return command_module.main()
    except ImportError:
        logger.error(f"导入命令模块失败: {module_path}")
        return 1
    except Exception as e:
        logger.error(f"运行命令时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AIgo命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 添加可用命令
    for name, info in AVAILABLE_COMMANDS.items():
        subparsers.add_parser(name, help=info["description"])
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        args = parser.parse_args([sys.argv[1]])
        remaining_args = sys.argv[2:]
        
        # 运行命令
        if args.command:
            # 将剩余参数传递给子命令
            sys.argv = [sys.argv[0]] + remaining_args
            return run_command(args)
    
    # 如果没有提供命令或命令无效，显示帮助信息
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main()) 