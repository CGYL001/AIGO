#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提示工程模块测试脚本 - 深入测试提示工程模块的各个组件
"""

import sys
import os
from pathlib import Path
import unittest

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from src.modules.prompt_engineering import (
    PromptEngineer, 
    PromptTemplates,
    ContextBuilder,
    PromptOptimizer,
    ResponseEvaluator,
    ReflectionEngine
)

class TestPromptTemplates(unittest.TestCase):
    """测试提示词模板"""
    
    def setUp(self):
        self.templates = PromptTemplates()
    
    def test_code_development_templates(self):
        """测试代码开发类模板"""
        print("\n测试代码开发类模板...")
        
        # 检查模板是否存在
        self.assertIn("code_completion", self.templates.CODE_DEVELOPMENT)
        self.assertIn("code_review", self.templates.CODE_DEVELOPMENT)
        self.assertIn("refactoring", self.templates.CODE_DEVELOPMENT)
        
        # 检查模板是否可以正常格式化
        code_template = self.templates.CODE_DEVELOPMENT["code_completion"]
        formatted = code_template.format(
            context="测试上下文", 
            code_fragment="def test():"
        )
        
        self.assertIn("测试上下文", formatted)
        self.assertIn("def test():", formatted)
        print("✓ 代码开发类模板测试成功")
    
    def test_problem_solving_templates(self):
        """测试问题解决类模板"""
        print("\n测试问题解决类模板...")
        
        # 检查模板是否存在
        self.assertIn("debug", self.templates.PROBLEM_SOLVING)
        self.assertIn("algorithm", self.templates.PROBLEM_SOLVING)
        
        # 检查模板是否可以正常格式化
        debug_template = self.templates.PROBLEM_SOLVING["debug"]
        formatted = debug_template.format(
            code="def test():", 
            error_message="测试错误"
        )
        
        self.assertIn("def test():", formatted)
        self.assertIn("测试错误", formatted)
        print("✓ 问题解决类模板测试成功")


class TestContextBuilder(unittest.TestCase):
    """测试上下文构建器"""
    
    def setUp(self):
        self.builder = ContextBuilder()
    
    def test_build_code_completion_context(self):
        """测试代码补全上下文构建"""
        print("\n测试代码补全上下文构建...")
        
        # 基本参数
        code_fragment = "def calculate_sum(a, b):"
        
        # 测试最小参数
        context = self.builder.build_code_completion_context(code_fragment)
        self.assertIn(code_fragment, context)
        self.assertIn("未知文件", context)
        
        # 测试完整参数
        context = self.builder.build_code_completion_context(
            code_fragment=code_fragment,
            file_path="test.py",
            language="Python",
            project_files=["main.py", "utils.py"],
            code_history=[{"action": "edit", "file": "test.py"}]
        )
        
        self.assertIn(code_fragment, context)
        self.assertIn("test.py", context)
        self.assertIn("Python", context)
        self.assertIn("main.py", context)
        self.assertIn("utils.py", context)
        self.assertIn("edit", context)
        print("✓ 代码补全上下文构建测试成功")
    
    def test_build_problem_solving_context(self):
        """测试问题解决上下文构建"""
        print("\n测试问题解决上下文构建...")
        
        # 测试debug类型
        context = self.builder.build_problem_solving_context(
            problem_type="debug",
            code="def test():",
            error_message="测试错误"
        )
        
        self.assertIn("def test():", context)
        self.assertIn("测试错误", context)
        
        # 测试algorithm类型
        context = self.builder.build_problem_solving_context(
            problem_type="algorithm",
            problem_description="实现快速排序算法"
        )
        
        self.assertIn("实现快速排序算法", context)
        print("✓ 问题解决上下文构建测试成功")


class TestPromptOptimizer(unittest.TestCase):
    """测试提示词优化器"""
    
    def setUp(self):
        self.optimizer = PromptOptimizer()
    
    def test_optimize(self):
        """测试优化功能"""
        print("\n测试优化功能...")
        
        # 基本提示词
        prompt = "编写一个函数计算两个数的和"
        
        # 测试不同任务类型的优化
        for task_type in ["code_completion", "debug", "code_review"]:
            optimized = self.optimizer.optimize(prompt, task_type)
            self.assertIsNotNone(optimized)
            self.assertGreater(len(optimized), len(prompt))
            print(f"✓ {task_type}类型优化成功")
    
    def test_optimization_stats(self):
        """测试优化统计"""
        print("\n测试优化统计...")
        
        # 优化几个提示词
        self.optimizer.optimize("测试1", "code_completion")
        self.optimizer.optimize("测试2", "debug")
        
        # 获取统计信息
        stats = self.optimizer.get_optimization_stats()
        
        self.assertIsNotNone(stats)
        self.assertIn("count", stats)
        self.assertGreaterEqual(stats["count"], 2)
        print(f"✓ 优化统计测试成功，记录了{stats['count']}次优化")


class TestResponseEvaluator(unittest.TestCase):
    """测试响应评估器"""
    
    def setUp(self):
        self.evaluator = ResponseEvaluator()
    
    def test_evaluate_code_response(self):
        """测试代码响应评估"""
        print("\n测试代码响应评估...")
        
        # 测试代码
        code_response = """
def calculate_sum(a, b):
    \"\"\"计算两个数的和\"\"\"
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("输入必须是数字")
    return a + b
"""
        
        # 评估
        result = self.evaluator.evaluate(code_response, "code_completion")
        
        self.assertIsNotNone(result)
        self.assertIn("total_score", result)
        self.assertIn("scores", result)
        self.assertIn("overall_feedback", result)
        print(f"✓ 代码响应评估测试成功，评分：{result['total_score']:.2f}")
    
    def test_evaluate_debug_response(self):
        """测试调试响应评估"""
        print("\n测试调试响应评估...")
        
        # 测试调试响应
        debug_response = """
问题诊断:
代码中在处理输入为0的情况时会触发除零错误。

修复方案:
```
def divide(a, b):
    if b == 0:
        return "错误: 不能除以零"
    return a / b
```

解释:
需要在函数开始处添加对b是否为0的判断，避免除零错误。
"""
        
        # 评估
        result = self.evaluator.evaluate(debug_response, "debug")
        
        self.assertIsNotNone(result)
        self.assertIn("total_score", result)
        self.assertIn("scores", result)
        print(f"✓ 调试响应评估测试成功，评分：{result['total_score']:.2f}")


class TestReflectionEngine(unittest.TestCase):
    """测试反思引擎"""
    
    def setUp(self):
        self.reflection = ReflectionEngine({
            "reflection_enabled": True,
            "max_iterations": 1
        })
    
    def test_reflect(self):
        """测试反思功能"""
        print("\n测试反思功能...")
        
        # 测试代码响应
        code_response = """
def find_max(numbers):
    max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value
"""
        
        # 反思
        result = self.reflection.reflect(code_response, "code_completion")
        
        self.assertIsNotNone(result)
        self.assertIn("reflection_performed", result)
        self.assertIn("needs_improvement", result)
        
        if result["needs_improvement"]:
            self.assertIn("improved_response", result)
            print(f"✓ 反思引擎测试成功，需要改进，并提供了改进后的响应")
        else:
            print(f"✓ 反思引擎测试成功，认为响应不需要改进")


class TestPromptEngineer(unittest.TestCase):
    """测试提示工程师主类"""
    
    def setUp(self):
        self.engineer = PromptEngineer()
    
    def test_generate_prompt(self):
        """测试提示词生成"""
        print("\n测试提示词生成...")
        
        # 测试不同类型的提示词生成
        code_prompt = self.engineer.generate_prompt(
            "code_completion",
            code_fragment="def factorial(n):",
            language="Python"
        )
        
        self.assertIsNotNone(code_prompt)
        self.assertIn("def factorial(n):", code_prompt)
        self.assertIn("Python", code_prompt)
        print("✓ 代码补全提示词生成测试成功")
        
        # 测试问题解决提示词
        debug_prompt = self.engineer.generate_prompt(
            "problem_solving.debug",
            code="def test(): return 1/0",
            error_message="ZeroDivisionError"
        )
        
        self.assertIsNotNone(debug_prompt)
        self.assertIn("def test()", debug_prompt)
        self.assertIn("ZeroDivisionError", debug_prompt)
        print("✓ 问题解决提示词生成测试成功")
    
    def test_e2e_workflow(self):
        """测试端到端工作流"""
        print("\n测试端到端工作流...")
        
        # 端到端测试工作流
        code_fragment = "def reverse_list(lst):"
        
        # 1. 生成提示词
        prompt = self.engineer.generate_prompt(
            "code_completion",
            code_fragment=code_fragment,
            language="Python"
        )
        
        # 模拟模型响应
        response = """
def reverse_list(lst):
    return lst[::-1]
"""
        
        # 2. 评估响应
        evaluation = self.engineer.evaluate_response(
            response, 
            "code_completion", 
            prompt=prompt
        )
        
        # 3. 反思并改进
        reflection = self.engineer.reflect_and_improve(
            response,
            "code_completion"
        )
        
        # 验证结果
        self.assertIsNotNone(prompt)
        self.assertIsNotNone(evaluation)
        self.assertIsNotNone(reflection)
        
        print("✓ 端到端工作流测试成功")
        print(f"  - 评估分数: {evaluation['total_score']:.2f}")
        print(f"  - 是否需要改进: {reflection['needs_improvement']}")


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTest(loader.loadTestsFromTestCase(TestPromptTemplates))
    suite.addTest(loader.loadTestsFromTestCase(TestContextBuilder))
    suite.addTest(loader.loadTestsFromTestCase(TestPromptOptimizer))
    suite.addTest(loader.loadTestsFromTestCase(TestResponseEvaluator))
    suite.addTest(loader.loadTestsFromTestCase(TestReflectionEngine))
    suite.addTest(loader.loadTestsFromTestCase(TestPromptEngineer))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    print("="*50)
    print("提示工程模块单元测试")
    print("="*50)
    
    run_tests() 