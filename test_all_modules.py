#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AIgo综合测试脚本

测试所有关键模块的基本功能
"""

import os
import sys
import json
import time
import logging
import importlib
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("test_all")

# 测试模块列表
TEST_MODULES = [
    "src.modules.code_analysis",
    "src.modules.knowledge_base",
    "src.modules.prompt_engineering",
    "src.modules.system_monitor",
    "src.services.model_manager",
    "src.utils.config_validator",
    "src.utils.async_utils"
]

def test_module_import(module_name):
    """测试模块导入"""
    try:
        module = importlib.import_module(module_name)
        logger.info(f"成功导入模块: {module_name}")
        return True
    except Exception as e:
        logger.error(f"导入模块失败: {module_name}, 错误: {str(e)}")
        return False

def test_config_files():
    """测试配置文件"""
    try:
        # 检查配置文件
        config_files = [
            "config/default/config.json",
            "config/default/mcp_config.json"
        ]
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                logger.error(f"配置文件不存在: {config_file}")
                return False
                
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"成功加载配置文件: {config_file}")
        
        return True
    except Exception as e:
        logger.error(f"测试配置文件失败: {str(e)}")
        return False

def test_directory_structure():
    """测试目录结构"""
    try:
        # 检查关键目录
        key_dirs = [
            "src",
            "src/modules",
            "src/services",
            "src/utils",
            "config",
            "data",
            "logs"
        ]
        
        for directory in key_dirs:
            if not os.path.exists(directory):
                logger.error(f"关键目录不存在: {directory}")
                return False
            logger.info(f"目录存在: {directory}")
        
        return True
    except Exception as e:
        logger.error(f"测试目录结构失败: {str(e)}")
        return False

def test_model_manager():
    """测试模型管理器"""
    try:
        from src.services.model_manager import ModelManager
        
        # 初始化模型管理器
        model_manager = ModelManager()
        logger.info("成功创建ModelManager实例")
        
        # 获取可用模型列表
        models = model_manager.get_available_models()
        logger.info(f"可用模型数量: {len(models)}")
        
        return True
    except Exception as e:
        logger.error(f"测试模型管理器失败: {str(e)}")
        return False

def test_system_monitor():
    """测试系统监控模块"""
    try:
        from src.modules.system_monitor.resource_monitor import ResourceMonitor
        
        # 初始化资源监控器，提供一个空的配置
        config = {
            "interval": 60,
            "history_size": 100,
            "log_level": "info"
        }
        monitor = ResourceMonitor(config)
        logger.info("成功创建ResourceMonitor实例")
        
        # 获取系统资源信息
        system_info = monitor.get_system_info()
        logger.info(f"系统信息: CPU核心数: {system_info['cpu']['logical_cores']}, "
                   f"内存: {system_info['memory']['total']}, "
                   f"可用内存: {system_info['memory']['available']}")
        
        # 检查系统信息是否包含关键字段
        required_fields = ['os', 'cpu', 'memory']
        all_fields_present = all(field in system_info for field in required_fields)
        
        if all_fields_present:
            logger.info("系统信息包含所有必要字段")
            return True
        else:
            logger.error("系统信息缺少必要字段")
            return False
    except Exception as e:
        logger.error(f"测试系统监控模块失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("开始AIgo综合测试")
    
    # 测试列表
    tests = [
        ("目录结构测试", test_directory_structure),
        ("配置文件测试", test_config_files),
        ("系统监控测试", test_system_monitor),
        ("模型管理器测试", test_model_manager)
    ]
    
    # 添加模块导入测试
    for module_name in TEST_MODULES:
        tests.append((f"模块导入测试: {module_name}", lambda m=module_name: test_module_import(m)))
    
    # 运行测试
    results = []
    for name, test_func in tests:
        logger.info(f"执行测试: {name}")
        try:
            start_time = time.time()
            result = test_func()
            elapsed = time.time() - start_time
            results.append((name, result))
            logger.info(f"测试结果: {'通过' if result else '失败'}, 耗时: {elapsed:.2f}秒")
        except Exception as e:
            logger.error(f"测试异常: {str(e)}")
            results.append((name, False))
    
    # 打印测试结果摘要
    logger.info("=" * 50)
    logger.info("测试结果摘要:")
    passed = 0
    for name, result in results:
        status = "通过" if result else "失败"
        logger.info(f"{name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"总计: {len(results)}个测试, 通过: {passed}, 失败: {len(results) - passed}")
    logger.info("=" * 50)
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 