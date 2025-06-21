"""
记忆管理模块使用示例

此示例演示如何使用AIgo的记忆管理模块来管理对话上下文。
"""

import os
import sys
import json
import time
from pathlib import Path
import tempfile

# 确保aigo包在导入路径中
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from aigo.modules.memory.base import MemoryItem, MemoryType
from aigo.modules.memory.managers import (
    ConversationMemory,
    HierarchicalMemory
)
from aigo.modules.memory.optimizers import (
    ConversationSummarizer,
    ContextOptimizer
)


def demo_conversation_memory():
    """演示基本的对话记忆管理"""
    print("\n=== 对话记忆管理演示 ===")
    
    # 创建对话记忆管理器
    memory = ConversationMemory(max_items=5)
    
    # 添加一些记忆项
    print("添加记忆项...")
    items = [
        {
            "type": MemoryType.CONVERSATION,
            "content": {
                "role": "user",
                "message": "你好，我想了解如何使用AIgo。"
            }
        },
        {
            "type": MemoryType.CONVERSATION,
            "content": {
                "role": "assistant",
                "message": "你好！AIgo是一个模块化AI助手平台。你可以使用它连接不同的模型后端，如Ollama和OpenAI。"
            }
        },
        {
            "type": MemoryType.CONVERSATION,
            "content": {
                "role": "user",
                "message": "它支持哪些模型？"
            }
        },
        {
            "type": MemoryType.CONVERSATION,
            "content": {
                "role": "assistant",
                "message": "AIgo支持多种模型，包括Ollama本地模型和OpenAI API模型。你可以通过适配器使用文本生成、聊天和嵌入功能。"
            }
        }
    ]
    
    # 添加记忆
    item_ids = []
    for item_data in items:
        item_id = memory.add(item_data)
        item_ids.append(item_id)
        print(f"  添加记忆: ID={item_id}")
    
    # 检索记忆
    print("\n检索记忆...")
    result = memory.retrieve("使用AIgo", limit=3)
    print(f"  找到 {result.total_found} 条记忆")
    
    for i, item in enumerate(result.items):
        print(f"  记忆 #{i+1}:")
        print(f"    类型: {item.type.value}")
        print(f"    内容: {item.content}")
        print(f"    时间戳: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.timestamp))}")
        print()
    
    # 更新记忆
    print("更新记忆...")
    memory.update(item_ids[0], {
        "content": {
            "message": "你好，我想了解如何使用AIgo平台进行开发。"
        },
        "importance": 0.8
    })
    
    # 检查更新结果
    updated_item = memory.get(item_ids[0])
    print(f"  更新后: {updated_item.content}")
    print(f"  重要性: {updated_item.importance}")
    
    # 删除记忆
    print("\n删除记忆...")
    memory.remove(item_ids[0])
    print(f"  已删除记忆 ID={item_ids[0]}")
    
    # 验证删除
    if memory.get(item_ids[0]) is None:
        print("  验证: 记忆已成功删除")
    
    # 清除所有记忆
    count = memory.clear()
    print(f"\n已清除 {count} 条记忆")


def demo_hierarchical_memory():
    """演示层次化记忆管理"""
    print("\n=== 层次化记忆管理演示 ===")
    
    # 创建临时目录作为长期记忆存储
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录作为长期记忆存储: {temp_dir}")
        
        # 创建层次化记忆管理器
        memory = HierarchicalMemory(
            short_term_size=5,
            medium_term_size=10,
            long_term_path=temp_dir
        )
        
        # 添加一些记忆，包括不同重要性级别
        print("\n添加各种重要性级别的记忆...")
        
        # 普通重要性 (会进入短期记忆)
        item1 = MemoryItem(
            type=MemoryType.CONVERSATION,
            content={
                "role": "user",
                "message": "AIgo如何连接到Ollama模型？"
            },
            importance=0.3
        )
        
        # 中等重要性 (会进入短期和中期记忆)
        item2 = MemoryItem(
            type=MemoryType.CONVERSATION,
            content={
                "role": "assistant",
                "message": "你可以使用ModelConfig配置Ollama连接，指定provider='ollama'和模型名称，以及API地址，通常是http://localhost:11434。"
            },
            importance=0.6
        )
        
        # 高重要性 (会进入所有层次记忆)
        item3 = MemoryItem(
            type=MemoryType.FACT,
            content={
                "fact": "AIgo的安装命令是 pip install -e .",
                "context": "安装开发版本"
            },
            importance=0.9
        )
        
        # 添加记忆
        id1 = memory.add(item1)
        print(f"  添加普通重要性记忆 (0.3): ID={id1}")
        
        id2 = memory.add(item2)
        print(f"  添加中等重要性记忆 (0.6): ID={id2}")
        
        id3 = memory.add(item3)
        print(f"  添加高重要性记忆 (0.9): ID={id3}")
        
        # 验证记忆存储在不同层次
        print("\n验证记忆存储在不同层次...")
        
        # 检查短期记忆
        short_term_results = memory.short_term.retrieve("", limit=10)
        print(f"  短期记忆中有 {short_term_results.total_found} 条记忆")
        
        # 检查中期记忆
        medium_term_results = memory.medium_term.retrieve("", limit=10)
        print(f"  中期记忆中有 {medium_term_results.total_found} 条记忆")
        
        # 检查长期记忆
        long_term_files = list(Path(temp_dir).glob("*.json"))
        print(f"  长期记忆中有 {len(long_term_files)} 条记忆")
        
        if long_term_files:
            print("\n长期记忆示例:")
            with open(long_term_files[0], "r", encoding="utf-8") as f:
                data = json.load(f)
                print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 检索记忆
        print("\n从层次化记忆中检索...")
        results = memory.retrieve("安装", limit=2)
        print(f"  找到 {results.total_found} 条相关记忆")
        
        for i, item in enumerate(results.items):
            print(f"  记忆 #{i+1}:")
            print(f"    ID: {item.id}")
            print(f"    类型: {item.type.value}")
            print(f"    内容: {item.content}")
            print(f"    重要性: {item.importance}")
            print()


def demo_memory_optimization():
    """演示记忆优化工具"""
    print("\n=== 记忆优化工具演示 ===")
    
    # 创建一个模拟对话
    conversation = [
        {"role": "user", "content": "你好，我想了解AIgo项目。"},
        {"role": "assistant", "content": "你好！AIgo是一个模块化AI助手平台，支持连接不同的模型后端，如Ollama和OpenAI。"},
        {"role": "user", "content": "我该如何安装它？"},
        {"role": "assistant", "content": "你可以通过以下步骤安装AIgo：\n1. 克隆仓库 `git clone https://github.com/yourusername/AIgo.git`\n2. 进入目录 `cd AIgo`\n3. 安装依赖 `pip install -r requirements.txt`\n4. 开发模式安装 `pip install -e .`"},
        {"role": "user", "content": "如何使用Ollama模型？"},
        {"role": "assistant", "content": "要使用Ollama模型，你需要先安装并启动Ollama服务。然后在AIgo中配置模型：\n```python\nfrom aigo.models.base import ModelConfig\nfrom aigo.models.adapters import TextGenerationAdapter\n\nconfig = ModelConfig(\n    provider=\"ollama\",\n    model_name=\"deepseek-r1:8b\",\n    api_base=\"http://localhost:11434\"\n)\n\nadapter = TextGenerationAdapter(config)\nresponse = adapter.process(\"写一首短诗\")\nprint(response)\n```"},
        {"role": "user", "content": "还有什么其他重要功能？"},
        {"role": "assistant", "content": "AIgo的其他重要功能包括：\n1. 多种模型适配器（文本生成、聊天、嵌入）\n2. CLI接口\n3. REST API服务\n4. 模型管理系统\n5. 向量存储集成\n\n这些功能让你可以灵活地在不同场景中使用AI模型。"}
    ]
    
    # 创建对话摘要器
    print("\n对话摘要示例...")
    summarizer = ConversationSummarizer()
    summary = summarizer.summarize(conversation)
    print("对话摘要:")
    print(summary)
    
    # 提取关键点
    print("\n提取关键点示例...")
    key_points = summarizer.extract_key_points(conversation)
    print("提取的关键点:")
    for i, point in enumerate(key_points):
        print(f"{i+1}. {point}")
    
    # 上下文优化
    print("\n上下文优化示例...")
    optimizer = ContextOptimizer(token_limit=500)  # 设置较小的token限制用于演示
    
    # 添加更多消息使其超过token限制
    long_conversation = conversation.copy()
    for i in range(5):
        long_conversation.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"这是一条额外的{'问题' if i % 2 == 0 else '回答'}，用于测试上下文优化功能。" * 5
        })
    
    # 优化上下文
    optimized = optimizer.optimize_context(long_conversation)
    print(f"原始消息数: {len(long_conversation)}")
    print(f"优化后消息数: {len(optimized)}")
    
    # 显示第一条摘要消息
    if optimized and optimized[0].get("role") == "system":
        print("\n优化后的第一条消息 (摘要):")
        print(optimized[0].get("content"))
    
    # 展示聚焦上下文
    print("\n聚焦上下文示例...")
    focused = optimizer.focus_context(
        long_conversation,
        "如何使用Ollama模型？",
        relevant_context=["Ollama是一个本地运行的大语言模型服务"]
    )
    print(f"聚焦后消息数: {len(focused)}")
    
    # 显示相关消息
    print("\n聚焦后的相关消息:")
    for i, msg in enumerate(focused):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        # 截断显示
        content_preview = content[:50] + "..." if len(content) > 50 else content
        print(f"{i+1}. [{role}] {content_preview}")


def main():
    """主函数"""
    print("AIgo记忆管理模块示例")
    print("====================")
    
    # 演示基本对话记忆
    demo_conversation_memory()
    
    # 演示层次化记忆
    demo_hierarchical_memory()
    
    # 演示记忆优化
    demo_memory_optimization()
    
    print("\n示例完成！")


if __name__ == "__main__":
    main() 