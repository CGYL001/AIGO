#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识库模块测试 - 测试知识库的基本功能
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# 使用正确的导入路径
from src.modules.knowledge_base import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):
    """测试知识库基本功能"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp()
        self.kb = KnowledgeBase()
        
    def tearDown(self):
        """测试后清理"""
        # 清理测试目录
        shutil.rmtree(self.test_dir)
    
    def test_init_vector_store(self):
        """测试初始化向量存储"""
        kb_path = os.path.join(self.test_dir, "test_kb")
        success = self.kb.init_vector_store(kb_path)
        self.assertTrue(success, "初始化向量存储应成功")
        self.assertIsNotNone(self.kb.vector_store, "向量存储不应为None")
    
    def test_add_text(self):
        """测试添加文本"""
        kb_path = os.path.join(self.test_dir, "test_kb")
        self.kb.init_vector_store(kb_path)
        
        # 添加测试文本
        text = "这是一段用于测试的文本内容，应该被成功添加到知识库中。"
        metadata = {"source": "test", "type": "text"}
        success = self.kb.add_text(text, metadata)
        
        self.assertTrue(success, "添加文本应成功")
        
    def test_search(self):
        """测试搜索功能"""
        kb_path = os.path.join(self.test_dir, "test_kb")
        self.kb.init_vector_store(kb_path)
        
        # 添加测试数据
        self.kb.add_text("人工智能是计算机科学的一个分支", {"source": "test", "type": "definition"})
        self.kb.add_text("机器学习是人工智能的一个子领域", {"source": "test", "type": "definition"})
        self.kb.add_text("Python是一种流行的编程语言", {"source": "test", "type": "definition"})
        
        # 测试搜索
        results = self.kb.search("人工智能")
        self.assertTrue(len(results) > 0, "搜索结果不应为空")
        
    def test_save_and_load(self):
        """测试保存和加载功能"""
        # 初始化知识库并添加数据
        kb_path = os.path.join(self.test_dir, "test_kb")
        self.kb.init_vector_store(kb_path)
        self.kb.add_text("这是测试数据", {"source": "test"})
        
        # 保存知识库
        save_path = os.path.join(self.test_dir, "saved_kb")
        save_result = self.kb.save(save_path)
        self.assertTrue(save_result, "保存知识库应成功")
        
        # 创建新的知识库实例
        new_kb = KnowledgeBase()
        
        # 加载知识库
        load_result = new_kb.load(save_path)
        self.assertTrue(load_result, "加载知识库应成功")
        
        # 验证数据是否正确加载
        results = new_kb.search("测试数据")
        self.assertTrue(len(results) > 0, "加载后搜索结果不应为空")

if __name__ == "__main__":
    unittest.main() 