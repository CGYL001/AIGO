#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识库测试模块 - 测试知识库功能和向量存储
"""

import sys
import os
import time
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# 导入项目模块
from src.modules.knowledge_base import KnowledgeBase
from src.modules.knowledge_base.storage.vector_store import VectorStore
from src.modules.knowledge_base.storage.metadata_store import MetadataStore

# 测试数据
TEST_DATA = [
    ("Python是一种面向对象的高级编程语言", {"source": "test", "type": "language"}),
    ("JavaScript是一种脚本语言，主要用于Web开发", {"source": "test", "type": "language"}),
    ("向量数据库是一种特殊的数据库，用于存储和检索向量数据", {"source": "test", "type": "database"}),
    ("机器学习是人工智能的一个子领域，专注于开发能够从数据中学习的算法", {"source": "test", "type": "ai"}),
    ("自然语言处理是计算机科学的一个领域，专注于使计算机能理解人类语言", {"source": "test", "type": "ai"})
]


class TestMetadataStore(unittest.TestCase):
    """测试元数据存储"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时测试目录
        self.test_dir = Path(ROOT_DIR) / "temp_test_metadata_store"
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建元数据存储
        self.db_path = self.test_dir / "test_metadata.sqlite"
        self.metadata_store = MetadataStore(str(self.db_path))
        
        # 测试数据
        self.documents = [
            {
                "id": "doc1",
                "source": "/path/to/file1.pdf",
                "type": "pdf",
                "title": "测试文档1",
                "description": "这是测试文档1的描述"
            },
            {
                "id": "doc2",
                "source": "/path/to/file2.md",
                "type": "markdown",
                "title": "测试文档2",
                "description": "这是测试文档2的描述"
            }
        ]
        
        self.chunks = [
            {
                "id": "chunk1",
                "document_id": "doc1",
                "text": "这是第一个文档的第一个块",
                "chunk_index": 0,
                "total_chunks": 2
            },
            {
                "id": "chunk2",
                "document_id": "doc1",
                "text": "这是第一个文档的第二个块",
                "chunk_index": 1,
                "total_chunks": 2
            },
            {
                "id": "chunk3",
                "document_id": "doc2",
                "text": "这是第二个文档的唯一块",
                "chunk_index": 0,
                "total_chunks": 1
            }
        ]
    
    def tearDown(self):
        """测试后清理"""
        # 关闭元数据存储
        self.metadata_store.close()
        
        # 删除临时测试目录
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_add_and_get_document(self):
        """测试添加和获取文档"""
        print("\n测试元数据存储添加和获取文档...")
        
        # 添加文档
        for doc in self.documents:
            success = self.metadata_store.add_document(doc["id"], doc)
            self.assertTrue(success, f"添加文档应成功: {doc['id']}")
        
        # 获取文档
        for doc in self.documents:
            result = self.metadata_store.get_document(doc["id"])
            self.assertIsNotNone(result, f"获取文档应成功: {doc['id']}")
            self.assertEqual(result["id"], doc["id"], "文档ID应匹配")
            self.assertEqual(result["title"], doc["title"], "文档标题应匹配")
        
        print("✓ 元数据存储添加和获取文档测试成功")
    
    def test_add_and_get_chunk(self):
        """测试添加和获取块"""
        print("\n测试元数据存储添加和获取块...")
        
        # 添加文档
        for doc in self.documents:
            self.metadata_store.add_document(doc["id"], doc)
        
        # 添加块
        for chunk in self.chunks:
            success = self.metadata_store.add_chunk(
                chunk["id"], 
                chunk["document_id"], 
                chunk["text"], 
                chunk["chunk_index"], 
                chunk["total_chunks"], 
                chunk
            )
            self.assertTrue(success, f"添加块应成功: {chunk['id']}")
        
        # 获取块
        for chunk in self.chunks:
            result = self.metadata_store.get_chunk(chunk["id"])
            self.assertIsNotNone(result, f"获取块应成功: {chunk['id']}")
            self.assertEqual(result["id"], chunk["id"], "块ID应匹配")
            self.assertEqual(result["text"], chunk["text"], "块内容应匹配")
        
        print("✓ 元数据存储添加和获取块测试成功")
    
    def test_get_chunks_by_document(self):
        """测试获取文档的所有块"""
        print("\n测试获取文档的所有块...")
        
        # 添加文档
        for doc in self.documents:
            self.metadata_store.add_document(doc["id"], doc)
        
        # 添加块
        for chunk in self.chunks:
            self.metadata_store.add_chunk(
                chunk["id"], 
                chunk["document_id"], 
                chunk["text"], 
                chunk["chunk_index"], 
                chunk["total_chunks"], 
                chunk
            )
        
        # 获取文档1的所有块
        doc1_chunks = self.metadata_store.get_chunks_by_document("doc1")
        self.assertEqual(len(doc1_chunks), 2, "文档1应有2个块")
        
        # 获取文档2的所有块
        doc2_chunks = self.metadata_store.get_chunks_by_document("doc2")
        self.assertEqual(len(doc2_chunks), 1, "文档2应有1个块")
        
        print("✓ 获取文档的所有块测试成功")
    
    def test_list_documents(self):
        """测试列出文档"""
        print("\n测试列出文档...")
        
        # 添加文档
        for doc in self.documents:
            self.metadata_store.add_document(doc["id"], doc)
        
        # 列出所有文档
        documents = self.metadata_store.list_documents()
        self.assertEqual(len(documents), 2, "应有2个文档")
        
        # 按类型过滤
        pdf_docs = self.metadata_store.list_documents({"type": "pdf"})
        self.assertEqual(len(pdf_docs), 1, "应有1个PDF文档")
        self.assertEqual(pdf_docs[0]["id"], "doc1", "PDF文档ID应为doc1")
        
        markdown_docs = self.metadata_store.list_documents({"type": "markdown"})
        self.assertEqual(len(markdown_docs), 1, "应有1个Markdown文档")
        self.assertEqual(markdown_docs[0]["id"], "doc2", "Markdown文档ID应为doc2")
        
        print("✓ 列出文档测试成功")
    
    def test_delete_document(self):
        """测试删除文档"""
        print("\n测试删除文档...")
        
        # 添加文档和块
        for doc in self.documents:
            self.metadata_store.add_document(doc["id"], doc)
        
        for chunk in self.chunks:
            self.metadata_store.add_chunk(
                chunk["id"], 
                chunk["document_id"], 
                chunk["text"], 
                chunk["chunk_index"], 
                chunk["total_chunks"], 
                chunk
            )
        
        # 删除文档1
        success = self.metadata_store.delete_document("doc1")
        self.assertTrue(success, "删除文档应成功")
        
        # 确认文档1已删除
        doc1 = self.metadata_store.get_document("doc1")
        self.assertIsNone(doc1, "文档1应已删除")
        
        # 确认文档1的块已删除
        doc1_chunks = self.metadata_store.get_chunks_by_document("doc1")
        self.assertEqual(len(doc1_chunks), 0, "文档1的块应已删除")
        
        # 确认文档2和其块未受影响
        doc2 = self.metadata_store.get_document("doc2")
        self.assertIsNotNone(doc2, "文档2不应受影响")
        
        doc2_chunks = self.metadata_store.get_chunks_by_document("doc2")
        self.assertEqual(len(doc2_chunks), 1, "文档2的块不应受影响")
        
        print("✓ 删除文档测试成功")
    
    def test_search_documents(self):
        """测试搜索文档"""
        print("\n测试搜索文档...")
        
        # 添加文档
        for doc in self.documents:
            self.metadata_store.add_document(doc["id"], doc)
        
        # 搜索标题
        results = self.metadata_store.search_documents("文档1")
        self.assertEqual(len(results), 1, "搜索'文档1'应返回1个结果")
        self.assertEqual(results[0]["id"], "doc1", "搜索结果应为doc1")
        
        # 搜索描述
        results = self.metadata_store.search_documents("描述")
        self.assertEqual(len(results), 2, "搜索'描述'应返回2个结果")
        
        print("✓ 搜索文档测试成功")

class TestVectorStore(unittest.TestCase):
    """测试向量存储"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时测试目录
        self.test_dir = Path(ROOT_DIR) / "temp_test_vector_store"
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建向量存储
        self.db_path = self.test_dir / "test_db.sqlite"
        self.vector_store = VectorStore(str(self.db_path), dimension=3)
        
        # 测试数据
        self.texts = ["文本1", "文本2", "文本3"]
        self.vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
        self.metadatas = [
            {"id": "1", "type": "test"}, 
            {"id": "2", "type": "test"}, 
            {"id": "3", "type": "test"}
        ]
    
    def tearDown(self):
        """测试后清理"""
        # 关闭向量存储
        self.vector_store.close()
        
        # 删除临时测试目录
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_add_and_search(self):
        """测试添加和搜索功能"""
        print("\n测试向量存储添加和搜索...")
        
        # 添加向量
        self.vector_store.add(self.texts, self.vectors, self.metadatas)
        
        # 搜索
        query_vector = [0.2, 0.3, 0.4]
        results = self.vector_store.search(query_vector, top_k=2)
        
        self.assertIsNotNone(results, "搜索结果不应为None")
        self.assertEqual(len(results), 2, "应返回2条结果")
        self.assertIn("score", results[0], "结果应包含相似度分数")
        self.assertIn("text", results[0], "结果应包含文本")
        print("✓ 向量存储添加和搜索测试成功")
    
    def test_delete(self):
        """测试删除功能"""
        print("\n测试向量存储删除...")
        
        # 添加向量
        self.vector_store.add(self.texts, self.vectors, self.metadatas)
        
        # 删除一个向量
        ids_to_delete = ["1"]
        self.vector_store.delete(ids_to_delete)
        
        # 搜索，确认已删除
        query_vector = [0.1, 0.2, 0.3]
        results = self.vector_store.search(query_vector, top_k=3)
        
        self.assertEqual(len(results), 2, "删除后应只返回2条结果")
        
        # 确认删除的ID不在结果中
        result_ids = [r.get("metadata", {}).get("id") for r in results]
        self.assertNotIn("1", result_ids, "已删除的ID不应出现在结果中")
        print("✓ 向量存储删除测试成功")


class TestKnowledgeBase(unittest.TestCase):
    """测试知识库"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时测试目录
        self.test_dir = Path(ROOT_DIR) / "temp_test_kb"
        self.test_dir.mkdir(exist_ok=True)
        
        # 初始化知识库
        self.kb = KnowledgeBase()
        self.kb_name = "test_kb"
        self.kb_dir = self.test_dir / self.kb_name
        self.kb_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时测试目录
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_init_vector_store(self):
        """测试初始化向量存储"""
        print("\n测试初始化向量存储...")
        
        success = self.kb.init_vector_store(str(self.kb_dir))
        
        self.assertTrue(success, "初始化向量存储应成功")
        self.assertIsNotNone(self.kb.vector_store, "向量存储不应为None")
        self.assertIsNotNone(self.kb.metadata_store, "元数据存储不应为None")
        print("✓ 初始化向量存储和元数据存储测试成功")
    
    def test_add_text_and_search(self):
        """测试添加文本和搜索"""
        print("\n测试添加文本和搜索...")
        
        # 初始化向量存储
        self.kb.init_vector_store(str(self.kb_dir))
        
        # 添加测试数据
        for text, metadata in TEST_DATA:
            success = self.kb.add_text(text, metadata)
            self.assertTrue(success, f"添加文本应成功: {text}")
        
        # 测试搜索
        queries = ["Python编程", "机器学习", "数据库"]
        
        for query in queries:
            results = self.kb.search(query, top_k=2)
            self.assertIsNotNone(results, "搜索结果不应为None")
            self.assertGreater(len(results), 0, f"查询'{query}'应返回结果")
            print(f"✓ 查询'{query}'返回{len(results)}条结果")
    
    def test_save_and_load(self):
        """测试保存和加载知识库"""
        print("\n测试保存和加载知识库...")
        
        # 初始化向量存储并添加数据
        self.kb.init_vector_store(self.kb_name)
        for text, metadata in TEST_DATA[:2]:  # 只添加部分数据
            self.kb.add_text(text, metadata)
        
        # 保存知识库
        save_dir = self.test_dir / "saved_kb"
        success = self.kb.save(str(save_dir))
        self.assertTrue(success, "保存知识库应成功")
        
        # 创建新知识库并加载
        new_kb = KnowledgeBase()
        load_success = new_kb.load(str(save_dir))
        
        self.assertTrue(load_success, "加载知识库应成功")
        self.assertIsNotNone(new_kb.vector_store, "加载后向量存储不应为None")
        self.assertIsNotNone(new_kb.metadata_store, "加载后元数据存储不应为None")
        
        # 验证加载后的搜索功能
        results = new_kb.search("Python", top_k=1)
        self.assertGreater(len(results), 0, "加载后应能搜索到结果")
        print("✓ 保存和加载知识库测试成功")
    
    def test_list_documents(self):
        """测试列出文档"""
        print("\n测试列出知识库文档...")
        
        # 初始化向量存储并添加数据
        self.kb.init_vector_store(str(self.kb_dir))
        
        # 添加测试数据
        for text, metadata in TEST_DATA:
            self.kb.add_text(text, metadata.copy())
        
        # 列出所有文档
        documents = self.kb.list_documents()
        self.assertEqual(len(documents), 5, "应有5个文档")
        
        # 按类型过滤
        ai_docs = self.kb.list_documents({"type": "ai"})
        self.assertEqual(len(ai_docs), 2, "应有2个AI类型文档")
        
        print("✓ 列出知识库文档测试成功")
    
    @patch('src.modules.knowledge_base.KnowledgeBase._get_embeddings')
    def test_chunking(self, mock_get_embeddings):
        """测试文本分块功能"""
        print("\n测试文本分块...")
        
        # 模拟嵌入函数
        mock_get_embeddings.return_value = [[0.1, 0.2, 0.3]]
        
        # 测试较长文本的分块
        long_text = "这" * 1000  # 1000个字符
        
        chunks = self.kb._chunk_text(long_text, chunk_size=200, overlap=50)
        
        self.assertGreater(len(chunks), 1, "长文本应被分成多个块")
        self.assertLessEqual(len(chunks[0]), 200, "每个块不应超过指定大小")
        print(f"✓ 文本分块测试成功，分成了{len(chunks)}个块")
    
    @patch('src.modules.knowledge_base.KnowledgeBase._get_embeddings')
    def test_calculate_similarity(self, mock_get_embeddings):
        """测试相似度计算"""
        print("\n测试相似度计算...")
        
        # 测试向量
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        vec3 = [1, 1, 0]  # 与vec1和vec2都有一定相似度
        
        # 计算相似度
        sim1_2 = self.kb._calculate_similarity(vec1, vec2)
        sim1_3 = self.kb._calculate_similarity(vec1, vec3)
        sim2_3 = self.kb._calculate_similarity(vec2, vec3)
        
        # 验证结果
        self.assertLess(sim1_2, sim1_3, "vec1与vec3的相似度应大于与vec2的相似度")
        self.assertLess(sim1_2, sim2_3, "vec2与vec3的相似度应大于与vec1的相似度")
        print("✓ 相似度计算测试成功")


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTest(loader.loadTestsFromTestCase(TestMetadataStore))
    suite.addTest(loader.loadTestsFromTestCase(TestVectorStore))
    suite.addTest(loader.loadTestsFromTestCase(TestKnowledgeBase))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    print("="*50)
    print("知识库测试")
    print("="*50)
    print("测试时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("-"*50)
    
    run_tests() 