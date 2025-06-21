#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基本功能测试脚本
"""

import os
import sys
import json
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("test_basic")

def test_config():
    """测试配置文件加载"""
    try:
        config_path = os.path.join("config", "default", "config.json")
        if not os.path.exists(config_path):
            logger.error(f"配置文件不存在: {config_path}")
            return False
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"成功加载配置文件: {config_path}")
            logger.info(f"应用名称: {config.get('app', {}).get('name')}")
            logger.info(f"应用版本: {config.get('app', {}).get('version')}")
            
        return True
    except Exception as e:
        logger.error(f"测试配置文件失败: {str(e)}")
        return False

def test_imports():
    """测试基本导入"""
    try:
        # 测试导入基本模块
        import src
        logger.info("成功导入src包")
        
        # 测试导入utils
        from src.utils import config_validator
        logger.info("成功导入config_validator模块")
        
        return True
    except Exception as e:
        logger.error(f"测试导入失败: {str(e)}")
        return False

def test_filesystem():
    """测试文件系统操作"""
    try:
        # 测试目录存在
        dirs_to_check = ["config", "data", "logs"]
        for d in dirs_to_check:
            if not os.path.exists(d):
                os.makedirs(d)
                logger.info(f"创建目录: {d}")
            else:
                logger.info(f"目录已存在: {d}")
                
        # 测试写入文件
        test_file = os.path.join("logs", "test_basic.log")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("测试写入文件成功\n")
        logger.info(f"成功写入测试文件: {test_file}")
        
        return True
    except Exception as e:
        logger.error(f"测试文件系统操作失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("开始基本功能测试")
    
    tests = [
        ("配置文件测试", test_config),
        ("导入测试", test_imports),
        ("文件系统测试", test_filesystem)
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"执行测试: {name}")
        try:
            result = test_func()
            results.append((name, result))
            logger.info(f"测试结果: {'通过' if result else '失败'}")
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