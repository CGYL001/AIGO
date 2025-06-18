#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提示工程演示脚本 - 展示如何使用PromptEngineer模块
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from src.modules.prompt_engineering import PromptEngineer
from src.services import ModelServiceFactory

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='提示工程模块演示')
    parser.add_argument('--dry-run', action='store_true', help='演示模式，不调用模型服务')
    return parser.parse_args()

def main():
    """提示工程演示主函数"""
    # 解析命令行参数
    args = parse_args()
    
    print("="*50)
    print("提示工程模块演示")
    print("="*50)
    
    # 初始化提示工程师
    prompt_engineer = PromptEngineer({
        "optimizer": {
            "use_reflection": True
        },
        "reflection": {
            "reflection_enabled": True,
            "max_iterations": 1
        }
    })
    
    # 初始化模型服务
    model_service = None
    if not args.dry_run:
        model_service = ModelServiceFactory.create_service()
    
    # 演示1：代码补全提示词生成
    print("\n演示1：代码补全提示词生成")
    print("-"*50)
    
    code_fragment = """
def calculate_fibonacci(n):
    \"\"\"计算斐波那契数列第n个数
    
    Args:
        n: 位置索引，从0开始
    \"\"\"
    """
    
    prompt = prompt_engineer.generate_prompt(
        "code_completion",
        code_fragment=code_fragment,
        language="Python",
        project_files=["utils.py", "math_helpers.py"]
    )
    
    print("生成的提示词:")
    print(prompt[:300] + "...")  # 只显示前300个字符
    
    # 调用模型获取补全
    if not args.dry_run:
        try:
            completion_response = model_service.generate(prompt, max_tokens=200)
            print("\n模型返回的代码补全:")
            print(completion_response)
            
            # 评估回答质量
            evaluation = prompt_engineer.evaluate_response(
                completion_response, 
                "code_completion",
                prompt=prompt
            )
            
            print("\n回答质量评估:")
            print(f"总分: {evaluation['total_score']:.2f}")
            print(f"总体反馈: {evaluation['overall_feedback']}")
            
            # 反思并改进
            reflection = prompt_engineer.reflect_and_improve(
                completion_response,
                "code_completion"
            )
            
            if reflection["needs_improvement"]:
                print("\n改进后的回答:")
                print(reflection["improved_response"])
        except Exception as e:
            print(f"调用模型服务失败: {str(e)}")
    else:
        print("\n演示模式：跳过模型调用")
        # 模拟模型响应
        mock_response = """
def calculate_fibonacci(n):
    \"\"\"计算斐波那契数列第n个数
    
    Args:
        n: 位置索引，从0开始
    \"\"\"
    if n < 0:
        raise ValueError("输入必须是非负整数")
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        if not args.dry_run:
            print("\n模型返回的代码补全:")
            print(mock_response)
    
    # 演示2：问题解决提示词生成
    print("\n\n演示2：问题解决提示词生成")
    print("-"*50)
    
    bug_code = """
def divide_values(data):
    result = []
    for i in range(len(data)):
        result.append(10 / data[i])
    return result
    
# 使用函数
values = [5, 10, 0, 20]
output = divide_values(values)
print(output)
"""
    
    error_message = "ZeroDivisionError: division by zero"
    
    prompt = prompt_engineer.generate_prompt(
        "problem_solving.debug",
        code=bug_code,
        error_message=error_message
    )
    
    print("生成的提示词:")
    print(prompt[:300] + "...")  # 只显示前300个字符
    
    # 调用模型获取问题解决方案
    if not args.dry_run:
        try:
            debug_response = model_service.generate(prompt, max_tokens=300)
            print("\n模型返回的调试方案:")
            print(debug_response)
            
            # 评估回答质量
            evaluation = prompt_engineer.evaluate_response(
                debug_response, 
                "debug",
                prompt=prompt
            )
            
            print("\n回答质量评估:")
            print(f"总分: {evaluation['total_score']:.2f}")
            print(f"总体反馈: {evaluation['overall_feedback']}")
        except Exception as e:
            print(f"调用模型服务失败: {str(e)}")
    else:
        print("\n演示模式：跳过模型调用")
    
    # 演示3：反思和迭代改进
    print("\n\n演示3：反思和迭代改进")
    print("-"*50)
    
    original_solution = """
def find_max(numbers):
    max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value
"""
    
    feedback = "代码没有处理空列表情况，会导致IndexError"
    
    prompt = prompt_engineer.generate_prompt(
        "reflection.iterative_improvement",
        original_solution=original_solution,
        feedback=feedback
    )
    
    print("生成的提示词:")
    print(prompt[:300] + "...")  # 只显示前300个字符
    
    print("\n提示工程统计:")
    stats = prompt_engineer.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n演示完成!")

if __name__ == "__main__":
    main() 