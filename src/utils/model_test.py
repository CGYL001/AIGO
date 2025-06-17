"""
模型集成测试工具
用于测试与本地Ollama模型的连接和功能
"""

import sys
import os
from pathlib import Path
import time
import argparse

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from src.services import ModelServiceFactory, model_manager
from src.modules.knowledge_base import KnowledgeBase
from src.modules.code_completion import CodeCompletion
from src.utils import config, logger

def test_model_connection():
    """测试模型连接"""
    print("=== 测试模型连接 ===")
    try:
        import requests
        api_base = config.get("models.inference.api_base", "http://localhost:11434")
        
        print(f"连接到模型服务: {api_base}")
        response = requests.get(f"{api_base}/api/tags")
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ 连接成功，发现 {len(models)} 个模型:")
            for model in models:
                name = model.get("name", "未知")
                modified = model.get("modified", 0)
                size = model.get("size", 0) // (1024 * 1024)  # 转换为MB
                print(f"  - {name} ({size} MB)")
        else:
            print(f"❌ 连接失败: HTTP {response.status_code}")
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")

def test_text_generation(model_name=None):
    """测试文本生成"""
    print("\n=== 测试文本生成 ===")
    model_name = model_name or config.get("models.inference.name", "deepseek-r1:8b")
    
    print(f"使用模型: {model_name}")
    try:
        service = ModelServiceFactory.create_service(model_name=model_name)
        
        prompts = [
            "用Python写一个简单的Hello World程序",
            "解释一下什么是向量数据库?",
            "CodeAssistant项目的主要功能是什么?"
        ]
        
        for prompt in prompts:
            print(f"\n提示词: {prompt}")
            start_time = time.time()
            response = service.generate(prompt, max_tokens=100)
            elapsed = time.time() - start_time
            
            print(f"响应 ({elapsed:.2f}秒):")
            print(f"{response[:300]}..." if len(response) > 300 else response)
            
        print("✅ 文本生成测试完成")
    except Exception as e:
        print(f"❌ 文本生成失败: {str(e)}")

def test_embeddings(model_name=None):
    """测试文本嵌入"""
    print("\n=== 测试文本嵌入 ===")
    model_name = model_name or config.get("models.embedding.name", "bge-m3")
    
    print(f"使用模型: {model_name}")
    try:
        service = ModelServiceFactory.create_service(model_name=model_name)
        
        texts = [
            "Python是一种解释型高级编程语言",
            "向量数据库用于存储和检索向量嵌入",
            "知识库系统可以帮助存储和检索信息"
        ]
        
        print(f"嵌入 {len(texts)} 个文本...")
        start_time = time.time()
        embeddings = service.embed(texts)
        elapsed = time.time() - start_time
        
        print(f"✅ 嵌入生成完成 ({elapsed:.2f}秒)")
        for i, embedding in enumerate(embeddings):
            print(f"  文本 {i+1}: {len(embedding)} 维向量")
            
        # 测试相似性计算
        if all(len(emb) > 0 for emb in embeddings):
            import numpy as np
            
            print("\n计算文本相似度:")
            for i in range(len(texts)):
                for j in range(i+1, len(texts)):
                    vec1 = np.array(embeddings[i])
                    vec2 = np.array(embeddings[j])
                    
                    # 计算余弦相似度
                    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    print(f"  文本 {i+1} 和文本 {j+1} 的相似度: {similarity:.4f}")
    except Exception as e:
        print(f"❌ 嵌入测试失败: {str(e)}")

def test_knowledge_base():
    """测试知识库功能"""
    print("\n=== 测试知识库 ===")
    try:
        kb = KnowledgeBase()
        
        # 初始化向量存储
        print("初始化向量存储...")
        kb.init_vector_store("test_kb")
        
        # 添加文本
        print("添加测试文本...")
        kb.add_text("Python是一种易于学习、功能强大的编程语言。它具有高效的高级数据结构，并且能够用简单有效的方式进行面向对象编程。", 
                   {"source": "测试", "title": "Python简介"})
        
        kb.add_text("向量数据库是一种专门用于存储和检索向量嵌入的数据库系统。它们通常用于构建语义搜索、推荐系统和其他机器学习应用。", 
                   {"source": "测试", "title": "向量数据库简介"})
        
        kb.add_text("知识库系统是一种存储、组织和检索知识的系统。它们可以用于辅助决策、问答系统和信息管理。", 
                   {"source": "测试", "title": "知识库系统简介"})
        
        # 测试搜索
        print("\n测试搜索...")
        queries = [
            "Python编程语言的特点",
            "向量数据库的用途",
            "什么是知识库"
        ]
        
        for query in queries:
            print(f"\n查询: {query}")
            results = kb.search(query, top_k=2)
            
            print(f"找到 {len(results)} 条结果:")
            for i, result in enumerate(results):
                print(f"结果 {i+1} (分数: {result['score']:.4f}):")
                print(f"  {result['text']}")
                
        # 保存知识库
        print("\n保存知识库...")
        kb.save("data/knowledge_bases/test_kb")
        
        # 清空并加载
        print("重新加载知识库...")
        new_kb = KnowledgeBase()
        new_kb.load("data/knowledge_bases/test_kb")
        
        # 验证加载后的搜索
        print("\n验证加载后的搜索...")
        results = new_kb.search("Python语言", top_k=1)
        if results:
            print("✅ 知识库测试成功")
        else:
            print("❌ 知识库加载后搜索失败")
            
    except Exception as e:
        print(f"❌ 知识库测试失败: {str(e)}")

def test_code_completion():
    """测试代码补全"""
    print("\n=== 测试代码补全 ===")
    try:
        code_completion = CodeCompletion()
        
        test_cases = [
            ("def factorial(n):\n    ", "python"),
            ("function calculateSum(arr) {\n    ", "javascript"),
            ("class MyClass {\n    ", "java")
        ]
        
        for code, lang in test_cases:
            print(f"\n语言: {lang}")
            print(f"代码: {code}")
            
            completion = code_completion.complete(code, language=lang)
            print(f"补全结果:\n{completion}")
            
        print("✅ 代码补全测试完成")
    except Exception as e:
        print(f"❌ 代码补全测试失败: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="模型集成测试工具")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--connection", action="store_true", help="测试模型连接")
    parser.add_argument("--generation", action="store_true", help="测试文本生成")
    parser.add_argument("--embedding", action="store_true", help="测试文本嵌入")
    parser.add_argument("--knowledge-base", action="store_true", help="测试知识库")
    parser.add_argument("--completion", action="store_true", help="测试代码补全")
    parser.add_argument("--model", type=str, help="指定要测试的模型名称")
    
    args = parser.parse_args()
    
    # 如果没有指定任何测试，则运行所有测试
    run_all = args.all or not any([
        args.connection, args.generation, args.embedding, 
        args.knowledge_base, args.completion
    ])
    
    if run_all or args.connection:
        test_model_connection()
        
    if run_all or args.generation:
        test_text_generation(args.model)
        
    if run_all or args.embedding:
        test_embeddings(args.model)
        
    if run_all or args.knowledge_base:
        test_knowledge_base()
        
    if run_all or args.completion:
        test_code_completion()

if __name__ == "__main__":
    main() 