#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识库测试 - 快速测试知识库功能
"""

import sys
import os
from pathlib import Path

# 确保可以正确导入模块
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

# 使用正确的导入路径
from src.modules.knowledge_base import KnowledgeBase

def test_knowledge_base():
    """测试知识库功能"""
    print("="*50)
    print("知识库功能测试")
    print("="*50)
    
    # 创建临时测试目录
    test_dir = Path("test_kb_demo")
    os.makedirs(test_dir, exist_ok=True)
    
    # 初始化知识库
    kb = KnowledgeBase()
    print("初始化知识库...")
    
    # 初始化向量存储
    success = kb.init_vector_store(str(test_dir))
    if success:
        print("✓ 向量存储初始化成功")
    else:
        print("× 向量存储初始化失败")
        return
    
    # 添加测试数据
    test_texts = [
        "Python是一种面向对象的高级编程语言",
        "机器学习是人工智能的一个子领域",
        "向量数据库用于高效存储和检索向量数据",
        "大语言模型基于Transformer架构",
        "知识库可以增强大语言模型的能力",
    ]
    
    print("\n添加测试数据...")
    for i, text in enumerate(test_texts):
        metadata = {"source": "test", "id": f"doc{i+1}"}
        success = kb.add_text(text, metadata)
        if success:
            print(f"✓ 添加成功: {text[:20]}...")
        else:
            print(f"× 添加失败: {text[:20]}...")
    
    # 测试搜索
    print("\n测试搜索功能...")
    queries = ["Python编程", "机器学习", "向量搜索", "大语言模型"]
    
    for query in queries:
        print(f"\n搜索: '{query}'")
        results = kb.search(query, top_k=2)
        
        if results:
            print(f"找到 {len(results)} 条结果:")
            for i, result in enumerate(results):
                print(f"  {i+1}. {result['text']}")
                if 'metadata' in result:
                    print(f"     来源: {result['metadata'].get('source', '未知')}")
                if 'score' in result:
                    print(f"     相似度: {result['score']:.4f}")
        else:
            print("未找到相关结果")
    
    print("\n知识库功能测试完成")
    return True

if __name__ == "__main__":
    test_knowledge_base() 