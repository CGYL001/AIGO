#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
全局测试脚本 - 测试核心模块的基本功能
"""

import os
import sys
import time
import unittest
from pathlib import Path

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# 导入项目模块
from src.modules.prompt_engineering import PromptEngineer
from src.modules.knowledge_base import KnowledgeBase
from src.services import ModelServiceFactory
from src.utils import config

class TestCoreModules(unittest.TestCase):
    """测试核心模块基本功能"""
    
    def setUp(self):
        """测试前准备"""
        # 统计测试时间
        self.start_time = time.time()
        
        # 创建服务和模块实例
        try:
            self.mock = os.environ.get('USE_MOCK_SERVICES', '').lower() == 'true'
            
            if self.mock:
                print("使用模拟服务进行测试")
                
            self.model_service = ModelServiceFactory.create_service()
            self.prompt_engineer = PromptEngineer()
            self.knowledge_base = KnowledgeBase()
        except Exception as e:
            print(f"初始化失败: {e}")
    
    def tearDown(self):
        """测试后清理"""
        elapsed = time.time() - self.start_time
        print(f"测试用时: {elapsed:.2f}秒")
    
    def test_prompt_engineering(self):
        """测试提示工程基本功能"""
        print("\n测试提示工程基本功能...")
        
        # 测试生成提示词
        code_fragment = "def fibonacci(n):"
        prompt = self.prompt_engineer.generate_prompt(
            "code_completion",
            code_fragment=code_fragment,
            language="Python"
        )
        
        self.assertIsNotNone(prompt, "提示词不应为None")
        self.assertIn(code_fragment, prompt, "提示词应包含代码片段")
        print("✓ 提示工程基本功能测试成功")
    
    def test_knowledge_base(self):
        """测试知识库基本功能"""
        print("\n测试知识库基本功能...")
        
        # 初始化向量存储
        test_dir = Path(ROOT_DIR) / "temp_test_kb"
        os.makedirs(test_dir, exist_ok=True)
        
        success = self.knowledge_base.init_vector_store(str(test_dir))
        self.assertTrue(success, "初始化向量存储应成功")
        
        # 添加测试数据
        text = "CodeAssistant是一个基于AI的编程助手"
        metadata = {"source": "test", "type": "description"}
        success = self.knowledge_base.add_text(text, metadata)
        
        self.assertTrue(success, "添加文本应成功")
        print("✓ 知识库基本功能测试成功")
        
        # 清理测试目录
        import shutil
        shutil.rmtree(test_dir)
    
    def test_model_service(self):
        """测试模型服务基本功能"""
        print("\n测试模型服务基本功能...")
        
        # 由于模型服务可能不可用，这里只做简单测试
        self.assertIsNotNone(self.model_service, "模型服务不应为None")
        
        # 测试是否具有必要的方法
        self.assertTrue(hasattr(self.model_service, 'generate') or hasattr(self.model_service, 'generate_text'), 
                       "模型服务应具有生成方法")
        self.assertTrue(hasattr(self.model_service, 'embed') or hasattr(self.model_service, 'embed_text'), 
                       "模型服务应具有嵌入方法")
                       
        print("✓ 模型服务基本功能测试成功")
    
    def test_config(self):
        """测试配置系统"""
        print("\n测试配置系统...")
        
        # 获取配置值
        model_name = config.get("models.inference.name")
        self.assertIsNotNone(model_name, "应能获取模型名称配置")
        
        # 测试默认值
        test_value = config.get("non_existent.key", "default_value")
        self.assertEqual(test_value, "default_value", "不存在的键应返回默认值")
        
        print("✓ 配置系统测试成功")


class TestIntegration(unittest.TestCase):
    """测试模块集成"""
    
    def setUp(self):
        """测试前准备"""
        self.mock = os.environ.get('USE_MOCK_SERVICES', '').lower() == 'true'
        self.prompt_engineer = PromptEngineer()
        self.knowledge_base = KnowledgeBase()
    
    def test_prompt_with_knowledge(self):
        """测试提示词与知识库集成"""
        print("\n测试提示词与知识库集成...")
        
        # 初始化向量存储并添加知识
        test_dir = Path(ROOT_DIR) / "temp_integration_test"
        os.makedirs(test_dir, exist_ok=True)
        
        self.knowledge_base.init_vector_store(str(test_dir))
        self.knowledge_base.add_text("Python是一种易学的编程语言", {"source": "test"})
        
        # 搜索知识
        results = self.knowledge_base.search("Python编程")
        
        # 如果有搜索结果，将其添加到提示词中
        if results:
            context = f"参考知识: {results[0]['text']}"
            prompt = self.prompt_engineer.generate_prompt(
                "code_completion",
                code_fragment="def hello_world():",
                language="Python",
                additional_context=context
            )
            
            self.assertIn("Python", prompt, "生成的提示词应包含知识库内容")
        else:
            # 即使没有结果，也应该能生成提示词
            prompt = self.prompt_engineer.generate_prompt(
                "code_completion",
                code_fragment="def hello_world():",
                language="Python"
            )
            self.assertIsNotNone(prompt, "即使没有知识库结果也应生成提示词")
        
        print("✓ 提示词与知识库集成测试成功")
        
        # 清理测试目录
        import shutil
        shutil.rmtree(test_dir)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTest(loader.loadTestsFromTestCase(TestCoreModules))
    suite.addTest(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试是否成功
    return result.wasSuccessful()

if __name__ == "__main__":
    print("="*50)
    print("CodeAssistant 全局集成测试")
    print("="*50)
    print("测试时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("-"*50)
    
    success = run_tests()
    sys.exit(0 if success else 1) 