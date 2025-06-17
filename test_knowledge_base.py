#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识库测试脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.modules.knowledge_base import KnowledgeBase
from src.services import ModelServiceFactory

def main():
    print("=== 知识库测试 ===")
    
    # 创建知识库目录
    kb_dir = "test_kb_demo"
    os.makedirs(kb_dir, exist_ok=True)
    
    # 初始化知识库
    print("初始化知识库...")
    kb = KnowledgeBase()
    kb.init_vector_store(kb_dir, dimension=1024)
    
    # 添加测试文本
    print("\n添加测试文本...")
    texts = [
        "Python是一种易于学习、功能强大的编程语言。它具有高效的高级数据结构，并且能够用简单有效的方式进行面向对象编程。",
        "向量数据库是一种专门用于存储和检索向量嵌入的数据库系统。它们通常用于构建语义搜索、推荐系统和其他机器学习应用。",
        "知识库系统是一种存储、组织和检索知识的系统。它们可以用于辅助决策、问答系统和信息管理。",
        "大语言模型是基于Transformer架构的深度学习模型，通过大规模预训练和微调，能够生成连贯、相关的文本内容。",
        "向量嵌入是将文本、图像等数据转换为高维向量的过程，使得语义相似的内容在向量空间中距离更近。"
    ]
    
    metadata = [
        {"source": "测试", "title": "Python简介", "type": "language"},
        {"source": "测试", "title": "向量数据库简介", "type": "database"},
        {"source": "测试", "title": "知识库系统简介", "type": "system"},
        {"source": "测试", "title": "大语言模型简介", "type": "ai"},
        {"source": "测试", "title": "向量嵌入简介", "type": "ai"}
    ]
    
    for i, (text, meta) in enumerate(zip(texts, metadata)):
        print(f"添加文本 {i+1}: {meta['title']}")
        kb.add_text(text, meta)
    
    # 测试搜索
    print("\n测试搜索...")
    queries = [
        "Python编程语言的特点",
        "向量数据库的用途",
        "什么是知识库",
        "大语言模型的工作原理",
        "向量嵌入与语义搜索"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        results = kb.search(query, top_k=2)
        
        print(f"找到 {len(results)} 条结果:")
        for i, result in enumerate(results):
            print(f"结果 {i+1} (分数: {result['score']:.4f}):")
            print(f"  标题: {result.get('metadata', {}).get('title', '未知')}")
            print(f"  内容: {result['text']}")
    
    print("\n知识库测试完成")

if __name__ == "__main__":
    main() 