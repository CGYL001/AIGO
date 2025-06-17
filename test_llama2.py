#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Llama2模型
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.services import ModelServiceFactory

def main():
    print("=== 测试Llama2模型 ===")
    
    # 创建模型服务，明确指定使用llama2模型
    print("初始化模型服务...")
    service = ModelServiceFactory.create_service(model_name="llama2:7b-chat-q4_K_M")
    
    # 测试提示词
    prompt = "用Python写一个简单的Hello World程序"
    
    print(f"提示词: {prompt}")
    print("生成回答中...")
    
    start_time = time.time()
    response = service.generate(
        prompt=prompt,
        model="llama2:7b-chat-q4_K_M",  # 明确指定模型
        max_tokens=200
    )
    elapsed = time.time() - start_time
    
    print(f"生成完成 ({elapsed:.2f}秒):")
    print("-" * 50)
    print(response)
    print("-" * 50)

if __name__ == "__main__":
    main() 