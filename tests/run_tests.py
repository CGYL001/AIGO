#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试启动器 - 运行选定的测试套件
"""

import os
import sys
import argparse
from pathlib import Path
import importlib
import time
import unittest
import subprocess

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='CodeAssistant 测试启动器')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--unit', action='store_true', help='运行单元测试')
    parser.add_argument('--integration', action='store_true', help='运行集成测试')
    parser.add_argument('--prompt-engineering', action='store_true', help='运行提示工程测试')
    parser.add_argument('--model', action='store_true', help='运行模型服务测试')
    parser.add_argument('--knowledge-base', action='store_true', help='运行知识库测试')
    parser.add_argument('--mock', action='store_true', help='使用模拟服务运行测试')
    return parser.parse_args()

def print_header():
    """打印测试头信息"""
    print("="*50)
    print("CodeAssistant 测试套件")
    print("="*50)
    print("测试时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("测试环境:")
    print(f"- Python版本: {sys.version}")
    print(f"- 项目路径: {ROOT_DIR}")
    print("-"*50)

def run_test_module(module_name, use_mock=False):
    """运行指定的测试模块"""
    # 检查文件是否存在
    module_path = ROOT_DIR / "tests" / f"{module_name}.py"
    if not module_path.exists():
        print(f"错误: 测试模块文件不存在: {module_path}")
        return False
        
    try:
        # 对于支持--mock参数的模块，直接以子进程方式运行
        if module_name in ["test_model_services", "test_knowledge_base"]:
            print(f"\n运行测试模块: {module_name}" + (" (模拟模式)" if use_mock else ""))
            print("-"*50)
            
            cmd = [sys.executable, str(module_path)]
            if use_mock:
                cmd.append("--mock")
            
            # 运行测试子进程
            process = subprocess.run(cmd, check=False)
            success = process.returncode == 0
        else:
            # 对于其他模块，通过导入运行
            if use_mock:
                os.environ['USE_MOCK_SERVICES'] = 'true'
                
            print(f"\n运行测试模块: {module_name}")
            print("-"*50)
            
            module = importlib.import_module(f"tests.{module_name}")
            
            # 如果模块有run_tests函数，调用它
            if hasattr(module, "run_tests"):
                result = module.run_tests()
                success = result if isinstance(result, bool) else True
            # 否则直接运行模块
            else:
                print(f"警告: {module_name} 没有 run_tests 函数，使用unittest运行")
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(module)
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)
                success = result.wasSuccessful()
                
            # 清除环境变量
            if use_mock:
                os.environ.pop('USE_MOCK_SERVICES', None)
                
        print("\n")
        return success
    except ImportError as e:
        print(f"错误: 无法导入测试模块 '{module_name}': {str(e)}")
        return False
    except Exception as e:
        print(f"错误: 运行测试模块 '{module_name}' 失败: {str(e)}")
        return False

def main():
    """主函数"""
    args = parse_args()
    print_header()
    
    # 确定要运行的测试
    modules_to_run = []
    
    # 根据参数选择测试模块
    if args.all:
        modules_to_run = ["test_all", "test_prompt_engineering", "test_model_services", "test_knowledge_base"]
    else:
        if args.unit or args.integration or not any([args.prompt_engineering, args.model, args.knowledge_base]):
            modules_to_run.append("test_all")
        if args.prompt_engineering:
            modules_to_run.append("test_prompt_engineering")
        if args.model:
            modules_to_run.append("test_model_services")
        if args.knowledge_base:
            modules_to_run.append("test_knowledge_base")
    
    # 运行所选择的测试模块
    if not modules_to_run:
        print("错误: 未指定任何测试模块")
        return 1
        
    successes = []
    for module in modules_to_run:
        success = run_test_module(module, args.mock)
        successes.append(success)
    
    # 打印测试结果摘要
    print("="*50)
    print("测试结果摘要:")
    print("-"*50)
    for module, success in zip(modules_to_run, successes):
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{module}: {status}")
    print("-"*50)
    print(f"总体结果: {'✅ 全部通过' if all(successes) else '❌ 部分失败'}")
    print("="*50)
    
    # 如果有任何测试失败，返回非零退出码
    return 0 if all(successes) else 1

if __name__ == "__main__":
    sys.exit(main()) 