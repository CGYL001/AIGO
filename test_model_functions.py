#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型功能测试脚本
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("test_model")

# 测试超时时间（秒）
TEST_TIMEOUT = 10

async def test_model_manager():
    """测试模型管理器"""
    try:
        # 导入模型管理器
        from src.services.model_manager import ModelManager
        logger.info("成功导入ModelManager")
        
        # 初始化模型管理器
        model_manager = ModelManager()
        logger.info("成功创建ModelManager实例")
        
        # 获取可用模型列表
        models = model_manager.get_available_models()
        logger.info(f"可用模型列表: {models}")
        
        return True
    except Exception as e:
        logger.error(f"测试模型管理器失败: {str(e)}")
        return False

async def test_knowledge_base():
    """测试知识库功能"""
    try:
        # 导入知识库模块
        from src.modules.knowledge_base.knowledge_base import KnowledgeBase
        logger.info("成功导入KnowledgeBase")
        
        # 创建临时知识库
        kb_path = Path("temp_test_kb")
        kb_path.mkdir(exist_ok=True)
        
        kb = KnowledgeBase(kb_path)
        logger.info("成功创建KnowledgeBase实例")
        
        # 添加一些测试数据
        test_data = [
            {"text": "人工智能是计算机科学的一个分支", "metadata": {"source": "test", "id": 1}},
            {"text": "机器学习是人工智能的一个子领域", "metadata": {"source": "test", "id": 2}},
            {"text": "深度学习是机器学习的一种方法", "metadata": {"source": "test", "id": 3}}
        ]
        
        for item in test_data:
            kb.add_text(item["text"], item["metadata"])
        
        logger.info("成功添加测试数据到知识库")
        
        # 搜索测试
        results = kb.search("人工智能", top_k=2)
        logger.info(f"搜索结果数量: {len(results)}")
        
        return True
    except Exception as e:
        logger.error(f"测试知识库功能失败: {str(e)}")
        return False

async def test_context_manager():
    """测试上下文管理器"""
    try:
        # 导入上下文管理器
        from src.modules.context_manager import ContextManager
        logger.info("成功导入ContextManager")
        
        # 初始化上下文管理器
        context_manager = ContextManager()
        logger.info("成功创建ContextManager实例")
        
        # 添加上下文
        context_manager.add_context("test", "这是一个测试上下文")
        logger.info("成功添加上下文")
        
        # 获取上下文
        context = context_manager.get_context("test")
        logger.info(f"获取上下文: {context is not None}")
        
        return True
    except Exception as e:
        logger.error(f"测试上下文管理器失败: {str(e)}")
        return False

async def test_with_timeout(test_func, timeout=TEST_TIMEOUT):
    """带超时的测试执行器"""
    try:
        # 创建任务
        task = asyncio.create_task(test_func())
        
        # 设置超时
        done, pending = await asyncio.wait([task], timeout=timeout)
        
        # 处理结果
        if task in done:
            return task.result()
        else:
            # 取消任务
            task.cancel()
            logger.error(f"测试超时: {test_func.__name__}")
            return False
    except Exception as e:
        logger.error(f"执行测试异常: {str(e)}")
        return False

async def main_async():
    """异步主函数"""
    logger.info("开始模型功能测试")
    
    tests = [
        ("模型管理器测试", test_model_manager),
        ("知识库测试", test_knowledge_base),
        ("上下文管理器测试", test_context_manager)
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"执行测试: {name}")
        try:
            result = await test_with_timeout(test_func)
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

def main():
    """主函数"""
    return asyncio.run(main_async())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 