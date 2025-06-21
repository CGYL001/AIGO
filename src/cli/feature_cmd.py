#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
特性命令行工具

提供命令行接口，用于启用和禁用特性
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("feature_cmd")

# 可用特性列表
AVAILABLE_FEATURES = {
    "model_restructuring": {
        "description": "模型重构系统，用于优化模型结构",
        "module": "src.modules.model_restructuring",
        "command": "model-restructure",
        "enabled_by_default": False
    },
    "code_translation": {
        "description": "代码翻译系统，用于在不同编程语言之间转换代码",
        "module": "src.modules.code_translation",
        "command": "translate-code",
        "enabled_by_default": True
    },
    "knowledge_base": {
        "description": "知识库系统，用于存储和检索知识",
        "module": "src.modules.knowledge_base",
        "command": "knowledge-base",
        "enabled_by_default": True
    }
}

def list_features(args):
    """列出所有可用特性"""
    logger.info("可用特性列表:")
    for name, info in AVAILABLE_FEATURES.items():
        status = "启用" if is_feature_enabled(name) else "禁用"
        logger.info(f"  - {name}: {info['description']} [{status}]")
    return 0

def enable_feature(args):
    """启用特性"""
    feature_name = args.feature
    if feature_name not in AVAILABLE_FEATURES:
        logger.error(f"未知特性: {feature_name}")
        return 1
    
    # 检查特性模块是否存在
    module_path = AVAILABLE_FEATURES[feature_name]["module"]
    module_dir = Path(module_path.replace(".", "/"))
    if not module_dir.exists():
        logger.error(f"特性模块不存在: {module_path}")
        logger.info(f"请先创建特性模块: {module_dir}")
        return 1
    
    # 更新配置
    config_path = Path("config/default/config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 确保features部分存在
            if "features" not in config:
                config["features"] = {}
            
            # 启用特性
            config["features"][feature_name] = True
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"已启用特性: {feature_name}")
            return 0
        except Exception as e:
            logger.error(f"启用特性时发生错误: {str(e)}")
            return 1
    else:
        logger.error(f"配置文件不存在: {config_path}")
        return 1

def disable_feature(args):
    """禁用特性"""
    feature_name = args.feature
    if feature_name not in AVAILABLE_FEATURES:
        logger.error(f"未知特性: {feature_name}")
        return 1
    
    # 更新配置
    config_path = Path("config/default/config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 确保features部分存在
            if "features" not in config:
                config["features"] = {}
            
            # 禁用特性
            config["features"][feature_name] = False
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"已禁用特性: {feature_name}")
            return 0
        except Exception as e:
            logger.error(f"禁用特性时发生错误: {str(e)}")
            return 1
    else:
        logger.error(f"配置文件不存在: {config_path}")
        return 1

def is_feature_enabled(feature_name):
    """检查特性是否启用"""
    # 获取默认值
    default_enabled = AVAILABLE_FEATURES.get(feature_name, {}).get("enabled_by_default", False)
    
    # 检查配置
    config_path = Path("config/default/config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查特性配置
            return config.get("features", {}).get(feature_name, default_enabled)
        except Exception:
            return default_enabled
    else:
        return default_enabled

def run_feature_command(args):
    """运行特性命令"""
    feature_name = args.feature
    if feature_name not in AVAILABLE_FEATURES:
        logger.error(f"未知特性: {feature_name}")
        return 1
    
    # 检查特性是否启用
    if not is_feature_enabled(feature_name):
        logger.error(f"特性未启用: {feature_name}")
        logger.info(f"请先启用特性: feature enable {feature_name}")
        return 1
    
    # 获取命令模块路径
    command_name = AVAILABLE_FEATURES[feature_name]["command"]
    module_path = f"src.cli.{command_name.replace('-', '_')}_cmd"
    
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
    parser = argparse.ArgumentParser(description="特性命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 列出特性命令
    list_parser = subparsers.add_parser("list", help="列出所有可用特性")
    
    # 启用特性命令
    enable_parser = subparsers.add_parser("enable", help="启用特性")
    enable_parser.add_argument("feature", choices=AVAILABLE_FEATURES.keys(), help="要启用的特性名称")
    
    # 禁用特性命令
    disable_parser = subparsers.add_parser("disable", help="禁用特性")
    disable_parser.add_argument("feature", choices=AVAILABLE_FEATURES.keys(), help="要禁用的特性名称")
    
    # 运行特性命令
    run_parser = subparsers.add_parser("run", help="运行特性命令")
    run_parser.add_argument("feature", choices=AVAILABLE_FEATURES.keys(), help="要运行的特性名称")
    run_parser.add_argument("args", nargs=argparse.REMAINDER, help="传递给特性命令的参数")
    
    args = parser.parse_args()
    
    if args.command == "list":
        return list_features(args)
    elif args.command == "enable":
        return enable_feature(args)
    elif args.command == "disable":
        return disable_feature(args)
    elif args.command == "run":
        return run_feature_command(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 