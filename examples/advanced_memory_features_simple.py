"""
高级记忆功能简化示例

展示如何使用新创建的高级记忆管理组件。
"""

import os
import sys
import time
import numpy as np
from pathlib import Path
import tempfile

# 确保aigo包在导入路径中
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入高级记忆组件
from aigo.modules.memory.vector_store_advanced import ShardedVectorStore
from aigo.modules.memory.similarity import (
    HybridSimilarity, 
    cosine_similarity,
    euclidean_similarity
)
from aigo.modules.memory.adaptive_optimizer import (
    AdaptiveOptimizer,
    ContentSegment
)


class MockEmbeddingModel:
    """模拟嵌入模型，用于演示"""
    
    def process(self, text):
        """返回固定维度的随机向量，但对相似文本返回相似向量"""
        import hashlib
        # 使用文本的哈希生成种子，这样相似文本会产生相似向量
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash, 16) % (2**32)
        np.random.seed(seed)
        return np.random.normal(0, 1, 128).tolist()  # 使用128维向量以加快演示速度


def demo_sharded_vector_store():
    """演示分片向量存储功能"""
    print("\n=== 分片向量存储演示 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建分片向量存储
        print("创建分片向量存储...")
        vector_store = ShardedVectorStore(
            dimension=128,  # 使用较小的维度以加快演示速度
            chunk_size=100,  # 每个分片最多100个向量
            max_active_chunks=2,  # 同时最多2个活跃分片
            parallelism=2  # 2个并行线程
        )
        
        # 添加向量
        print(f"添加测试向量...")
        start_time = time.time()
        
        vectors_added = 0
        for i in range(100):  # 添加100个向量
            # 创建随机向量
            vector = np.random.normal(0, 1, 128).tolist()
            
            # 添加向量
            success = vector_store.add(
                id=f"item{i+1}",
                vector=vector,
                metadata={"text": f"这是第{i+1}个向量", "category": f"category{i%5}"}
            )
            
            if success:
                vectors_added += 1
        
        end_time = time.time()
        print(f"成功添加 {vectors_added} 个向量，耗时: {end_time - start_time:.2f}秒")
        
        # 获取存储统计信息
        stats = vector_store.get_stats()
        print(f"\n存储统计信息:")
        print(f"  总向量数: {stats['total_vectors']}")
        print(f"  分片数: {stats['chunks']['total']}")
        print(f"  活跃分片数: {stats['chunks']['active']}")
        
        # 执行搜索
        print("\n执行并行向量搜索...")
        query_vector = np.random.normal(0, 1, 128).tolist()
        
        start_time = time.time()
        results = vector_store.search(query_vector, limit=5)
        end_time = time.time()
        
        print(f"搜索耗时: {end_time - start_time:.4f}秒")
        print(f"找到 {len(results)} 个结果:")
        for id, score, metadata in results:
            print(f"  ID: {id}, 相似度分数: {score:.4f}, 类别: {metadata.get('category')}")


def demo_hybrid_similarity():
    """演示混合相似度功能"""
    print("\n=== 混合相似度演示 ===")
    
    # 创建混合相似度计算器
    hybrid_sim = HybridSimilarity(
        default_weights={
            "cosine": 0.7,
            "euclidean": 0.2,
            "angular": 0.1,
            "manhattan": 0.0,
        }
    )
    
    # 创建测试向量
    print("创建测试向量...")
    
    # 基向量
    base = [1.0, 0.0, 0.0, 0.0]
    
    # 相似向量（余弦相似度高）
    cosine_similar = [0.9, 0.1, 0.0, 0.0]
    
    # 欧几里得距离相似
    euclidean_similar = [1.1, 0.1, 0.0, 0.0]
    
    # 相对不相似
    dissimilar = [0.0, 0.0, 1.0, 0.0]
    
    # 计算各种相似度
    print("\n计算各种相似度分数:")
    
    # 余弦相似度
    print(f"余弦相似度:")
    print(f"  base 与 cosine_similar: {cosine_similarity(base, cosine_similar):.4f}")
    print(f"  base 与 euclidean_similar: {cosine_similarity(base, euclidean_similar):.4f}")
    print(f"  base 与 dissimilar: {cosine_similarity(base, dissimilar):.4f}")
    
    # 欧几里得相似度
    print(f"欧几里得相似度:")
    print(f"  base 与 cosine_similar: {euclidean_similarity(base, cosine_similar):.4f}")
    print(f"  base 与 euclidean_similar: {euclidean_similarity(base, euclidean_similar):.4f}")
    print(f"  base 与 dissimilar: {euclidean_similarity(base, dissimilar):.4f}")
    
    # 混合相似度
    print(f"混合相似度:")
    print(f"  base 与 cosine_similar: {hybrid_sim.compute(base, cosine_similar):.4f}")
    print(f"  base 与 euclidean_similar: {hybrid_sim.compute(base, euclidean_similar):.4f}")
    print(f"  base 与 dissimilar: {hybrid_sim.compute(base, dissimilar):.4f}")


def demo_adaptive_optimizer():
    """演示自适应上下文优化器"""
    print("\n=== 自适应上下文优化器演示 ===")
    
    # 创建自适应优化器
    optimizer = AdaptiveOptimizer(token_limit=500)  # 设置较小的限制以便演示
    
    # 创建测试内容段
    print("创建测试内容段...")
    
    segments = [
        ContentSegment(
            content="# 示例Python函数\n\ndef calculate_factorial(n):\n    \"\"\"计算阶乘\"\"\"\n    if n <= 1:\n        return 1\n    return n * calculate_factorial(n-1)\n\n# 测试函数\nresult = calculate_factorial(5)\nprint(f\"5的阶乘是: {result}\")",
            content_type="code",
            importance=0.8,
            token_count=120
        ),
        ContentSegment(
            content="用户: 如何在Python中实现递归函数?\n助手: 递归函数是调用自身的函数。在Python中，你可以像定义普通函数一样定义递归函数，但需要确保有一个基本情况来停止递归。例如，计算阶乘的递归函数。",
            content_type="conversation",
            importance=0.7,
            token_count=150
        ),
        ContentSegment(
            content="递归是一种解决问题的方法，它将问题分解为更小的子问题，直到这些子问题简单到可以直接解决。在编程中，递归通常通过函数调用自身来实现。递归函数必须有基本情况（停止条件）以防止无限递归。",
            content_type="fact",
            importance=0.6,
            token_count=140
        ),
        ContentSegment(
            content="# 递归与迭代的比较\n\n递归和迭代都是编程中的重要概念。递归通过函数调用自身来解决问题，而迭代通过循环结构来重复执行代码。\n\n递归的优点包括代码简洁、易于理解复杂问题。缺点包括可能导致栈溢出、效率较低。\n\n迭代的优点包括效率高、不会导致栈溢出。缺点是对于某些复杂问题，代码可能不如递归清晰。\n\n在实际编程中，应根据具体问题选择合适的方法。",
            content_type="document",
            importance=0.5,
            token_count=250
        ),
        ContentSegment(
            content="用户: 递归函数有什么缺点?\n助手: 递归函数的主要缺点包括:\n1. 可能导致栈溢出，特别是对于深度递归\n2. 通常比迭代实现效率低\n3. 占用更多内存\n4. 在某些语言中可能受到递归深度限制",
            content_type="conversation",
            importance=0.6,
            token_count=150
        )
    ]
    
    # 计算总token数
    total_tokens = sum(s.token_count for s in segments)
    print(f"总内容段数: {len(segments)}")
    print(f"总token数: {total_tokens}")
    print(f"Token限制: {optimizer.token_limit}")
    
    # 执行优化
    print("\n执行上下文优化...")
    optimized = optimizer.optimize_content(segments, context_type="coding")
    
    # 计算优化后的token数
    optimized_tokens = sum(s.token_count for s in optimized)
    print(f"优化后的内容段数: {len(optimized)}")
    print(f"优化后的token数: {optimized_tokens}")
    print(f"压缩率: {optimized_tokens / total_tokens:.2%}")
    
    # 展示优化后的内容
    print("\n优化后的内容片段:")
    for i, segment in enumerate(optimized):
        print(f"\n内容段 #{i+1}:")
        print(f"  类型: {segment.content_type}")
        print(f"  重要性: {segment.importance}")
        print(f"  Token数: {segment.token_count}")
        
        # 显示前50个字符
        preview = segment.content[:50] + "..." if len(segment.content) > 50 else segment.content
        print(f"  内容预览: {preview}")
        
        # 显示是否被压缩
        if segment.metadata.get("compressed"):
            print(f"  状态: 已压缩 (原始: {segment.metadata.get('original_tokens')} tokens)")
        else:
            print(f"  状态: 保持原样")


def main():
    """主函数"""
    print("AIgo高级记忆功能简化示例")
    print("=======================")
    
    # 演示分片向量存储
    demo_sharded_vector_store()
    
    # 演示混合相似度功能
    demo_hybrid_similarity()
    
    # 演示自适应上下文优化器
    demo_adaptive_optimizer()
    
    print("\n示例完成！")


if __name__ == "__main__":
    main() 