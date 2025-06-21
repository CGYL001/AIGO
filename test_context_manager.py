#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
上下文管理器测试脚本
"""

import os
import sys
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("test_context")

def test_context_manager_import():
    """测试导入上下文管理器模块"""
    try:
        # 导入上下文管理器模块
        from src.modules.context_manager import ContextManager
        logger.info("成功导入ContextManager类")
        
        # 检查类的属性和方法
        methods = [m for m in dir(ContextManager) if not m.startswith('_')]
        logger.info(f"ContextManager类的公共方法: {methods}")
        
        return True
    except Exception as e:
        logger.error(f"导入上下文管理器模块失败: {str(e)}")
        return False

def test_context_manager_instance():
    """测试上下文管理器实例化"""
    try:
        # 导入上下文管理器
        from src.modules.context_manager import ContextManager
        
        # 创建实例
        context_manager = ContextManager()
        logger.info("成功创建ContextManager实例")
        
        # 检查实例属性
        instance_attrs = [a for a in dir(context_manager) if not a.startswith('_')]
        logger.info(f"ContextManager实例的属性: {instance_attrs}")
        
        return True
    except Exception as e:
        logger.error(f"创建上下文管理器实例失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("开始上下文管理器测试")
    
    tests = [
        ("上下文管理器导入测试", test_context_manager_import),
        ("上下文管理器实例化测试", test_context_manager_instance)
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