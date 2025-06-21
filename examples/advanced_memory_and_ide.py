"""
高级记忆管理和IDE集成示例

展示如何使用AIgo的高级记忆管理系统和IDE集成功能。
"""

import os
import sys
import time
from pathlib import Path
import tempfile

# 确保aigo包在导入路径中
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入记忆管理组件
from aigo.modules.memory.vector_store import VectorStoreFactory
from aigo.modules.memory.enhanced_vector import EnhancedVectorMemory
from aigo.modules.memory.multimodal import MultiModalMemory
from aigo.modules.memory.context_window import (
    ContextWindow,
    DynamicContextBuilder,
    ContextBlock
)

# 导入IDE适配器
from aigo.adapters.ide.base import FileContext, ProjectContext
from aigo.adapters.ide.cursor_adapter import CursorAdapter, setup_cursor_integration

# 导入模型适配器
from aigo.models.base import ModelConfig
from aigo.models.adapters import (
    TextGenerationAdapter,
    ChatAdapter,
    EmbeddingAdapter
)


class MockEmbeddingModel:
    """模拟嵌入模型，用于演示"""
    
    def process(self, text):
        """返回固定维度的随机向量"""
        import random
        return [random.random() for _ in range(1536)]


class MockChatModel:
    """模拟聊天模型，用于演示"""
    
    def process(self, prompt):
        """返回简单响应"""
        return f"这是对'{prompt[:50]}...'的模拟响应。实际集成时会使用真实的AI模型。"


def demo_vector_store():
    """演示向量存储功能"""
    print("\n=== 向量存储演示 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建向量存储
        print("创建内存向量存储...")
        vector_store = VectorStoreFactory.create("memory", dimension=4)
        
        # 添加向量
        print("添加测试向量...")
        vector_store.add("item1", [1.0, 0.0, 0.0, 0.0], {"text": "这是第一个向量"})
        vector_store.add("item2", [0.0, 1.0, 0.0, 0.0], {"text": "这是第二个向量"})
        vector_store.add("item3", [0.0, 0.0, 1.0, 0.0], {"text": "这是第三个向量"})
        
        # 搜索向量
        print("\n执行向量搜索...")
        results = vector_store.search([0.5, 0.5, 0.0, 0.0], limit=2)
        
        print(f"找到 {len(results)} 个结果:")
        for id, score, metadata in results:
            print(f"  ID: {id}, 相似度分数: {score:.4f}, 元数据: {metadata}")
        
        # 保存向量存储
        store_path = os.path.join(temp_dir, "test_vectors")
        print(f"\n保存向量存储到 {store_path}...")
        vector_store.save(store_path)
        
        # 加载向量存储
        print("加载向量存储...")
        new_store = VectorStoreFactory.create("memory", dimension=4)
        new_store.load(store_path)
        
        # 验证加载
        print("验证加载的向量存储...")
        loaded_results = new_store.search([0.5, 0.5, 0.0, 0.0], limit=2)
        
        print(f"加载后找到 {len(loaded_results)} 个结果:")
        for id, score, metadata in loaded_results:
            print(f"  ID: {id}, 相似度分数: {score:.4f}, 元数据: {metadata}")


def demo_enhanced_vector_memory():
    """演示增强版向量记忆管理器"""
    print("\n=== 增强版向量记忆管理器演示 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        store_path = os.path.join(temp_dir, "vector_memory")
        
        # 创建嵌入模型
        embedding_model = MockEmbeddingModel()
        
        # 创建增强版向量记忆管理器
        print("创建增强版向量记忆管理器...")
        memory = EnhancedVectorMemory(
            embedding_model=embedding_model,
            vector_store_path=store_path,
            dimension=1536
        )
        
        # 添加一些记忆项
        print("添加记忆项...")
        memory.add({
            "type": "code",
            "content": {
                "code": "def hello_world():\n    print('Hello, world!')",
                "language": "python",
                "description": "一个简单的Python函数"
            },
            "importance": 0.7
        })
        
        memory.add({
            "type": "fact",
            "content": {
                "fact": "Python是一种解释型高级编程语言",
                "context": "编程语言",
                "source": "示例"
            },
            "importance": 0.8
        })
        
        # 检索记忆
        print("\n检索记忆...")
        results = memory.retrieve("Python函数")
        
        print(f"找到 {results.total_found} 条相关记忆:")
        for i, item in enumerate(results.items):
            print(f"  记忆 #{i+1}:")
            print(f"    类型: {item.type.value}")
            print(f"    内容: {item.content}")
            print(f"    重要性: {item.importance}")
            print()


def demo_multimodal_memory():
    """演示多模态记忆管理器"""
    print("\n=== 多模态记忆管理器演示 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        vector_path = os.path.join(temp_dir, "vectors")
        hierarchical_path = os.path.join(temp_dir, "hierarchical")
        
        # 创建嵌入模型
        embedding_model = MockEmbeddingModel()
        
        # 创建多模态记忆管理器
        print("创建多模态记忆管理器...")
        memory = MultiModalMemory(
            embedding_model=embedding_model,
            vector_store_path=vector_path,
            hierarchical_path=hierarchical_path
        )
        
        # 添加文本记忆
        print("\n添加各种类型的记忆...")
        memory.add_text("我想了解Python的函数定义", role="user")
        memory.add_text(
            "在Python中，函数使用def关键字定义，参数列表在括号内，函数体缩进。"
            "例如: def hello(name): print(f'Hello, {name}!')",
            role="assistant"
        )
        
        # 添加代码记忆
        memory.add_code(
            code="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            language="python",
            description="递归计算斐波那契数列"
        )
        
        memory.add_code(
            code="function greeting(name) {\n    return `Hello, ${name}!`;\n}",
            language="javascript",
            description="JavaScript问候函数"
        )
        
        # 添加事实记忆
        memory.add_fact(
            fact="Python是由Guido van Rossum在1989年创建的",
            context="编程语言历史",
            source="示例"
        )
        
        # 模拟图像记忆
        memory.add_image(
            image_path="/path/to/example.png",
            description="Python logo"
        )
        
        # 检索代码记忆
        print("\n检索代码记忆...")
        code_results = memory.search_code("fibonacci", language="python")
        
        print(f"找到 {len(code_results)} 条Python代码记忆:")
        for i, code in enumerate(code_results):
            print(f"  代码 #{i+1}:")
            print(f"    描述: {code.get('description', '')}")
            print(f"    语言: {code.get('language', '')}")
            print(f"    代码:\n{code.get('code', '')}")
            print()
        
        # 检索事实记忆
        print("\n检索事实记忆...")
        fact_results = memory.search_facts("Python历史")
        
        print(f"找到 {len(fact_results)} 条相关事实:")
        for i, fact in enumerate(fact_results):
            print(f"  事实 #{i+1}: {fact.get('fact', '')}")
            print(f"    上下文: {fact.get('context', '')}")
            print()
        
        # 获取对话历史
        print("\n获取对话历史...")
        conversation = memory.get_conversation_history(limit=5)
        
        print(f"对话历史（{len(conversation)}条消息）:")
        for i, message in enumerate(conversation):
            role = message.get("role", "").capitalize()
            content = message.get("content", "")
            print(f"  {role}: {content[:50]}{'...' if len(content) > 50 else ''}")


def demo_context_window():
    """演示上下文窗口管理"""
    print("\n=== 上下文窗口管理演示 ===")
    
    # 创建上下文窗口管理器
    print("创建上下文窗口管理器（token限制：1000）...")
    context_window = ContextWindow(token_limit=1000)
    
    # 添加不同类别的块
    print("\n添加各种类别的上下文块...")
    
    # 系统指令
    context_window.add_block(
        "你是一个有用的AI助手，专注于提供准确的编程相关信息。",
        category="system",
        importance=1.0
    )
    
    # 代码片段
    context_window.add_block(
        "```python\ndef hello_world():\n    print('Hello, world!')\n```",
        category="code",
        importance=0.7
    )
    
    # 对话历史
    context_window.add_block(
        "User: 如何在Python中定义函数？",
        category="conversation",
        importance=0.6
    )
    
    context_window.add_block(
        "Assistant: 在Python中，使用def关键字定义函数，后跟函数名和括号中的参数列表。函数体需要缩进。例如：\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n```",
        category="conversation",
        importance=0.6
    )
    
    # 检查token使用情况
    tokens_by_category = context_window.get_tokens_by_category()
    print("\n各类别token使用情况:")
    for category, tokens in tokens_by_category.items():
        print(f"  {category}: {tokens} tokens")
    
    print(f"总token数: {context_window.total_tokens}")
    print(f"可用token数: {context_window.get_available_tokens()}")
    
    # 添加大块内容触发优化
    print("\n添加大块内容触发优化...")
    large_code = "```python\n" + "\n".join([f"# Line {i}\nprint('This is line {i}')" for i in range(1, 50)]) + "\n```"
    
    result = context_window.add_block(
        large_code,
        category="code",
        importance=0.5
    )
    
    print(f"添加大块内容{'成功' if result else '失败（触发优化）'}")
    print(f"优化后总token数: {context_window.total_tokens}")
    print(f"优化后可用token数: {context_window.get_available_tokens()}")
    
    # 获取完整上下文
    print("\n获取优化后的上下文（截断显示）...")
    context = context_window.get_context()
    print(context[:200] + "..." + context[-200:])


def demo_dynamic_context_builder():
    """演示动态上下文构建器"""
    print("\n=== 动态上下文构建器演示 ===")
    
    # 创建嵌入模型
    embedding_model = MockEmbeddingModel()
    
    # 创建多模态记忆管理器
    with tempfile.TemporaryDirectory() as temp_dir:
        memory = MultiModalMemory(
            embedding_model=embedding_model,
            vector_store_path=os.path.join(temp_dir, "vectors")
        )
        
        # 添加一些记忆
        memory.add_code(
            code="def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
            language="python",
            description="递归计算阶乘"
        )
        
        memory.add_fact(
            fact="递归是一种函数调用自身的编程技术",
            context="编程概念"
        )
        
        # 创建动态上下文构建器
        print("创建动态上下文构建器...")
        context_builder = DynamicContextBuilder(
            token_limit=2000,
            memory_manager=memory
        )
        
        # 准备示例数据
        system_message = "你是一个编程助手，擅长解释代码和编程概念。"
        
        code_snippets = [
            {
                "language": "python",
                "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "description": "递归版斐波那契"
            }
        ]
        
        conversation_history = [
            {"role": "user", "content": "递归函数是什么？"},
            {"role": "assistant", "content": "递归函数是调用自身的函数。它通常用于解决可以分解为相似子问题的问题。"}
        ]
        
        # 构建上下文
        print("\n为查询构建上下文...")
        query = "如何优化递归斐波那契函数？"
        
        context = context_builder.build_context_for_query(
            query=query,
            system_message=system_message,
            code_snippets=code_snippets,
            conversation_history=conversation_history
        )
        
        print("\n构建的上下文（截断显示）:")
        if len(context) > 500:
            print(context[:250] + "...\n...\n..." + context[-250:])
        else:
            print(context)
        
        # 使用模拟模型生成响应
        chat_model = MockChatModel()
        prompt = f"{context}\n\n用户: {query}\n\n助手:"
        response = chat_model.process(prompt)
        
        print("\n模拟响应:")
        print(response)


def demo_cursor_integration():
    """演示Cursor IDE集成"""
    print("\n=== Cursor IDE集成演示 ===")
    
    # 创建模拟模型
    embedding_model = MockEmbeddingModel()
    chat_model = MockChatModel()
    
    # 创建临时目录作为项目根目录
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = temp_dir
        
        # 创建示例文件
        os.makedirs(os.path.join(project_root, "src"), exist_ok=True)
        
        with open(os.path.join(project_root, "src", "example.py"), "w") as f:
            f.write("""
def fibonacci(n):
    \"\"\"计算斐波那契数列的第n个数\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    print(fibonacci(10))

if __name__ == "__main__":
    main()
            """.strip())
        
        # 设置Cursor集成
        print("设置Cursor集成...")
        memory_path = os.path.join(project_root, ".aigo_memory")
        os.makedirs(memory_path, exist_ok=True)
        
        # 创建项目上下文
        project = ProjectContext(
            root_path=project_root,
            active_files=[os.path.join(project_root, "src", "example.py")],
            open_files=[os.path.join(project_root, "src", "example.py")]
        )
        
        # 创建文件上下文
        with open(os.path.join(project_root, "src", "example.py"), "r") as f:
            file_content = f.read()
            
        file_context = FileContext(
            file_path=os.path.join(project_root, "src", "example.py"),
            content=file_content,
            language="python",
            cursor_position=len(file_content)
        )
        
        # 创建Cursor适配器
        cursor_adapter = CursorAdapter(
            memory_manager=MultiModalMemory(
                embedding_model=embedding_model,
                vector_store_path=os.path.join(memory_path, "vectors"),
                hierarchical_path=os.path.join(memory_path, "hierarchical")
            ),
            model_adapter=chat_model,
            project_root=project_root
        )
        
        # 模拟连接
        print("模拟连接到Cursor...")
        cursor_adapter.connected = True
        cursor_adapter.project = project
        cursor_adapter.current_file_context = file_context
        
        # 保存文件到记忆系统
        print("将当前文件保存到记忆系统...")
        cursor_adapter.save_to_memory()
        
        # 处理代码查询
        print("\n处理代码查询...")
        query = "如何优化斐波那契函数以避免重复计算？"
        
        response = cursor_adapter.process_code_query(
            query=query,
            include_current_file=True,
            include_related_files=True,
            use_memory=True
        )
        
        print("\n查询响应:")
        print(response)
        
        # 查找文档
        print("\n查找文档...")
        docs = cursor_adapter.lookup_documentation("fibonacci", "python")
        
        print("\n文档结果:")
        print(docs)


def main():
    """主函数"""
    print("AIgo高级记忆管理和IDE集成示例")
    print("===============================")
    
    # 演示向量存储
    demo_vector_store()
    
    # 演示增强版向量记忆管理器
    demo_enhanced_vector_memory()
    
    # 演示多模态记忆管理器
    demo_multimodal_memory()
    
    # 演示上下文窗口管理
    demo_context_window()
    
    # 演示动态上下文构建器
    demo_dynamic_context_builder()
    
    # 演示Cursor集成
    demo_cursor_integration()
    
    print("\n示例完成！")


if __name__ == "__main__":
    main() 