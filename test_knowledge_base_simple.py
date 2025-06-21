#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识库简单测试脚本
"""

import os
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("test_kb")

def test_knowledge_base_import():
    """测试导入知识库模块"""
    try:
        # 导入知识库模块
        import src.modules.knowledge_base
        logger.info("成功导入知识库包")
        
        # 尝试导入知识库类
        from src.modules.knowledge_base.knowledge_base import KnowledgeBase
        logger.info("成功导入KnowledgeBase类")
        
        return True
    except Exception as e:
        logger.error(f"导入知识库模块失败: {str(e)}")
        return False

def test_knowledge_base_storage():
    """测试知识库存储模块"""
    try:
        # 导入存储模块
        from src.modules.knowledge_base.storage.vector_store import VectorStore
        from src.modules.knowledge_base.storage.metadata_store import MetadataStore
        
        logger.info("成功导入存储模块")
        return True
    except Exception as e:
        logger.error(f"导入存储模块失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("开始知识库简单测试")
    
    tests = [
        ("知识库导入测试", test_knowledge_base_import),
        ("知识库存储测试", test_knowledge_base_storage)
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