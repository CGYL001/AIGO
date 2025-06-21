"""
高级记忆功能示例

展示如何使用AIgo的高级记忆管理组件，包括分片向量存储、混合相似度计算、
自适应上下文优化和异步记忆管理。
"""

import os
import sys
import time
import threading
import asyncio
from pathlib import Path
import tempfile
import numpy as np

# 确保aigo包在导入路径中
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入基础记忆组件
from aigo.modules.memory.base import MemoryItem, MemoryType, MemoryRetrievalResult
from aigo.modules.memory.managers import ConversationMemory

# 导入高级记忆组件
from aigo.modules.memory.vector_store_advanced import ShardedVectorStore, VectorStoreFactory
from aigo.modules.memory.similarity import (
    HybridSimilarity, 
    SemanticFilter, 
    ContextAwareRetrieval,
    cosine_similarity,
    euclidean_similarity
)
from aigo.modules.memory.adaptive_optimizer import (
    AdaptiveOptimizer,
    AdaptiveContextWindow,
    ContentSegment
)
from aigo.modules.memory.async_memory import AsyncMemory, TaskPriority


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
            chunk_size=500,  # 每个分片最多500个向量
            max_active_chunks=3,  # 同时最多3个活跃分片
            parallelism=4  # 4个并行线程
        )
        
        # 添加向量
        print(f"添加测试向量...")
        start_time = time.time()
        
        vectors_added = 0
        for i in range(1000):  # 添加1000个向量
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
        
        # 保存和加载测试
        store_path = os.path.join(temp_dir, "sharded_vectors")
        print(f"\n保存向量存储到 {store_path}...")
        save_start = time.time()
        vector_store.save(store_path)
        save_end = time.time()
        print(f"保存耗时: {save_end - save_start:.2f}秒")
        
        # 创建新存储并加载
        print("加载向量存储...")
        new_store = ShardedVectorStore(dimension=128)
        load_start = time.time()
        new_store.load(store_path)
        load_end = time.time()
        print(f"加载耗时: {load_end - load_start:.2f}秒")
        
        # 验证加载的存储
        new_stats = new_store.get_stats()
        print(f"加载后的统计信息:")
        print(f"  总向量数: {new_stats['total_vectors']}")
        print(f"  分片数: {new_stats['chunks']['total']}")
        print(f"  活跃分片数: {new_stats['chunks']['active']}")


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
    
    # 语义过滤演示
    print("\n语义过滤演示:")
    
    # 创建嵌入模型
    embedding_model = MockEmbeddingModel()
    
    # 创建语义过滤器
    semantic_filter = SemanticFilter(embedding_model)
    
    # 模拟向量搜索结果
    results = [
        ("id1", 0.8, {"content_summary": "Python是一种解释型高级编程语言"}),
        ("id2", 0.7, {"content_summary": "Java是一种广泛使用的编程语言"}),
        ("id3", 0.6, {"content_summary": "机器学习是人工智能的一个分支"}),
        ("id4", 0.5, {"content_summary": "自然语言处理用于理解人类语言"}),
        ("id5", 0.4, {"content_summary": "数据结构是计算机科学的基础"})
    ]
    
    # 进行文本过滤
    query = "编程语言的特点"
    filtered = semantic_filter.filter_by_text(results, query)
    
    print(f"查询: '{query}'")
    print(f"过滤后的结果:")
    for id, score, metadata in filtered[:3]:
        print(f"  ID: {id}, 组合分数: {score:.4f}, 内容: {metadata['content_summary']}")
    
    # 上下文感知检索演示
    print("\n上下文感知检索演示:")
    
    # 创建上下文感知检索器
    context_retrieval = ContextAwareRetrieval(
        embedding_model=embedding_model,
        context_weight=0.3
    )
    
    # 创建向量存储
    vector_store = ShardedVectorStore(dimension=128)
    
    # 添加测试向量
    texts = [
        "Python是一种面向对象的解释型计算机程序设计语言",
        "Java是一种广泛使用的编程语言，拥有跨平台、面向对象等特性",
        "C++是一种计算机高级程序设计语言，支持多种编程范式",
        "机器学习是人工智能的一个分支，专注于开发能够从数据中学习的算法",
        "深度学习是机器学习的子领域，使用多层神经网络进行学习",
        "自然语言处理是计算机科学和人工智能的一个领域，专注于理解人类语言",
        "数据结构是计算机存储、组织数据的方式，是算法的基础",
        "算法是解决问题的明确指令，是计算机科学的核心",
        "操作系统是管理计算机硬件和软件资源的系统软件",
        "数据库是按照数据结构来组织、存储和管理数据的仓库"
    ]
    
    for i, text in enumerate(texts):
        vector = embedding_model.process(text)
        vector_store.add(
            id=f"text{i+1}",
            vector=vector,
            metadata={"content_summary": text, "type": "text"}
        )
    
    # 执行上下文感知检索
    query = "编程语言"
    context = ["算法和数据结构是编程的基础"]
    
    print(f"查询: '{query}'")
    print(f"上下文: '{context[0]}'")
    
    # 不使用上下文的检索
    no_context_results = context_retrieval.retrieve(
        query, vector_store, context=None, limit=3
    )
    
    print(f"不使用上下文的结果:")
    for id, score, metadata in no_context_results[:3]:
        print(f"  ID: {id}, 分数: {score:.4f}, 内容: {metadata['content_summary']}")
    
    # 使用上下文的检索
    with_context_results = context_retrieval.retrieve(
        query, vector_store, context=context, limit=3
    )
    
    print(f"使用上下文的结果:")
    for id, score, metadata in with_context_results[:3]:
        print(f"  ID: {id}, 分数: {score:.4f}, 内容: {metadata['content_summary']}")


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
    
    # 自适应上下文窗口演示
    print("\n自适应上下文窗口演示:")
    
    # 创建自适应上下文窗口
    context_window = AdaptiveContextWindow(token_limit=500, context_type="coding")
    
    # 添加内容
    for i, segment in enumerate(segments):
        success = context_window.add_content(
            segment.content,
            segment.content_type,
            segment.importance
        )
        
        print(f"添加内容段 #{i+1} ({segment.content_type}): {'成功' if success else '触发优化'}")
        print(f"  当前token数: {context_window.total_tokens}/{context_window.token_limit}")
    
    # 获取上下文
    context = context_window.get_context()
    print(f"\n最终上下文大小: {context_window.total_tokens} tokens")
    print(f"最终上下文内容段数: {len(context_window.segments)}")


def demo_async_memory():
    """演示异步记忆管理"""
    print("\n=== 异步记忆管理演示 ===")
    
    # 创建基础记忆存储
    base_memory = ConversationMemory()
    
    # 创建异步记忆
    async_memory = AsyncMemory(
        memory_backend=base_memory,
        max_workers=4,
        queue_size=100
    )
    
    # 定义任务完成回调
    def on_task_complete(result, error):
        if error:
            print(f"  任务失败: {error}")
        else:
            print(f"  任务完成: {result}")
    
    # 异步添加记忆项
    print("异步添加记忆项...")
    
    # 高优先级任务
    high_task = async_memory.add_async(
        {
            "type": "conversation",
            "content": {"message": "这是高优先级消息", "role": "user"},
            "importance": 0.8
        },
        priority=TaskPriority.HIGH
    )
    
    # 普通优先级任务
    normal_task = async_memory.add_async(
        {
            "type": "fact",
            "content": {"fact": "这是普通优先级事实"},
            "importance": 0.6
        },
        priority=TaskPriority.NORMAL
    )
    
    # 低优先级任务
    low_task = async_memory.add_async(
        {
            "type": "code",
            "content": {"code": "print('Hello, World!')", "language": "python"},
            "importance": 0.5
        },
        priority=TaskPriority.LOW
    )
    
    # 等待所有任务完成
    print("等待任务完成...")
    high_task.wait()
    normal_task.wait()
    low_task.wait()
    
    # 检查结果
    print("\n任务结果:")
    print(f"高优先级任务: {'成功' if high_task.result else '失败'}")
    print(f"普通优先级任务: {'成功' if normal_task.result else '失败'}")
    print(f"低优先级任务: {'成功' if low_task.result else '失败'}")
    
    # 批量添加记忆项
    print("\n批量添加记忆项...")
    batch_items = []
    for i in range(5):
        batch_items.append({
            "type": "conversation",
            "content": {"message": f"批量消息 #{i+1}", "role": "user"},
            "importance": 0.5
        })
    
    batch_task = async_memory.batch_add(batch_items)
    batch_task.wait()
    
    print(f"批量添加结果: {len(batch_task.result)} 个项目已添加")
    
    # 异步检索
    print("\n异步检索记忆...")
    retrieve_task = async_memory.retrieve_async("消息")
    retrieve_task.wait()
    
    result = retrieve_task.result
    print(f"找到 {result.total_found} 条相关记忆:")
    for i, item in enumerate(result.items[:3]):
        print(f"  记忆 #{i+1}: {item.content.get('message', '')}")
    
    # 添加到批处理队列
    print("\n添加到批处理队列...")
    for i in range(3):
        async_memory.add_to_batch(
            {
                "type": "fact",
                "content": {"fact": f"批处理事实 #{i+1}"},
                "importance": 0.4
            },
            max_batch_size=3,
            max_wait_time=1.0
        )
    
    # 等待批处理完成
    print("等待批处理完成...")
    time.sleep(2)  # 等待批处理任务执行
    
    # 检查结果
    retrieve_task = async_memory.retrieve_async("事实")
    retrieve_task.wait()
    
    result = retrieve_task.result
    print(f"找到 {result.total_found} 条事实记忆:")
    for i, item in enumerate(result.items[:3]):
        print(f"  事实 #{i+1}: {item.content.get('fact', '')}")
    
    # 关闭异步处理
    print("\n关闭异步记忆管理器...")
    async_memory.shutdown()


def main():
    """主函数"""
    print("AIgo高级记忆功能示例")
    print("=======================")
    
    # 演示分片向量存储
    demo_sharded_vector_store()
    
    # 演示混合相似度功能
    demo_hybrid_similarity()
    
    # 演示自适应上下文优化器
    demo_adaptive_optimizer()
    
    # 演示异步记忆管理
    demo_async_memory()
    
    print("\n示例完成！")


if __name__ == "__main__":
    main() 