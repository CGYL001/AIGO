#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大语言模型测试脚本
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.services import ModelServiceFactory

def test_text_generation():
    """测试文本生成功能"""
    print("=== 测试大语言模型 ===")
    
    # 创建模型服务
    print("初始化模型服务...")
    service = ModelServiceFactory.create_service()
    
    # 测试各种提示词
    prompts = [
        "用Python写一个计算斐波那契数列的函数",
        "解释REST API的主要原则",
        "总结向量数据库的优势和应用场景",
        "如何优化Python代码性能？请给出5个建议",
        "比较SQL和NoSQL数据库的异同"
    ]
    
    for i, prompt in enumerate(prompts):
        print(f"\n提示词 {i+1}: {prompt}")
        
        # 测试普通生成
        print("生成回答中...")
        start_time = time.time()
        response = service.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500
        )
        elapsed = time.time() - start_time
        
        print(f"生成完成 ({elapsed:.2f}秒):")
        print("-" * 50)
        print(response)
        print("-" * 50)

def test_streaming():
    """测试流式生成功能"""
    print("\n=== 测试流式生成 ===")
    
    # 创建模型服务
    service = ModelServiceFactory.create_service()
    
    prompt = "请写一篇关于人工智能在编程中应用的短文"
    
    print(f"\n提示词: {prompt}")
    print("流式生成中...")
    print("-" * 50)
    
    # 回调函数
    def print_token(token):
        print(token, end="", flush=True)
    
    # 流式生成
    start_time = time.time()
    for token in service.generate_stream(
        prompt=prompt,
        callback=print_token,
        temperature=0.7,
        max_tokens=300
    ):
        pass
    
    elapsed = time.time() - start_time
    print("\n" + "-" * 50)
    print(f"流式生成完成 ({elapsed:.2f}秒)")

def main():
    # 测试普通文本生成
    test_text_generation()
    
    # 测试流式生成
    test_streaming()

if __name__ == "__main__":
    main() 