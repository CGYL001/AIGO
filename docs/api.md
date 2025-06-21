# AIgo API 参考文档

本文档详细介绍了 AIgo 提供的 API 接口，包括 REST API 和 Python API。

## 目录

- [REST API](#rest-api)
  - [认证](#认证)
  - [端点概览](#端点概览)
  - [模型相关接口](#模型相关接口)
  - [文本生成接口](#文本生成接口)
  - [嵌入生成接口](#嵌入生成接口)
  - [聊天接口](#聊天接口)
  - [服务状态接口](#服务状态接口)
- [Python API](#python-api)
  - [模型运行器](#模型运行器)
  - [适配器](#适配器)
  - [工具类](#工具类)

## REST API

AIgo 提供了 RESTful API，可通过 HTTP 请求与模型进行交互。

### 认证

默认情况下，本地运行的 API 服务不需要认证。如需启用认证，请在配置文件中设置 API 密钥：

```json
{
  "api": {
    "auth_enabled": true,
    "api_key": "your-api-key-here"
  }
}
```

启用认证后，所有 API 请求需要在 HTTP 头部包含以下认证信息：

```
Authorization: Bearer your-api-key-here
```

### 端点概览

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/models` | GET | 列出所有可用模型 |
| `/api/v1/models/{model_id}` | GET | 获取特定模型的详情 |
| `/api/v1/generate` | POST | 生成文本 |
| `/api/v1/embed` | POST | 生成文本嵌入向量 |
| `/api/v1/chat` | POST | 聊天对话接口 |
| `/api/v1/chat/stream` | POST | 流式聊天对话接口 |
| `/api/v1/health` | GET | 检查服务健康状态 |

### 模型相关接口

#### 列出所有模型

```
GET /api/v1/models
```

**响应示例：**

```json
{
  "models": [
    {
      "id": "ollama:deepseek-r1:8b",
      "name": "DeepSeek R1 8B",
      "provider": "ollama",
      "capabilities": ["text_generation", "chat"],
      "parameters": {
        "max_tokens": 2048,
        "temperature": 0.7,
        "max_context_length": 4096
      }
    },
    {
      "id": "ollama:llama2:7b",
      "name": "Llama 2 7B",
      "provider": "ollama",
      "capabilities": ["text_generation", "chat"],
      "parameters": {
        "max_tokens": 2048,
        "temperature": 0.7,
        "max_context_length": 4096
      }
    }
  ]
}
```

#### 获取特定模型详情

```
GET /api/v1/models/{model_id}
```

**响应示例：**

```json
{
  "id": "ollama:deepseek-r1:8b",
  "name": "DeepSeek R1 8B",
  "description": "DeepSeek R1是中文与英文都支持的开源大型语言模型",
  "provider": "ollama",
  "capabilities": ["text_generation", "chat", "code"],
  "parameters": {
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_context_length": 4096,
    "stop_sequences": ["\n\n", "###"]
  },
  "metadata": {
    "context_window": 4096,
    "vocabulary_size": 32000,
    "training_corpus": "Web text, code, books",
    "architecture": "Transformer decoder",
    "parameter_count": "8 billion",
    "version": "1.0"
  }
}
```

### 文本生成接口

#### 生成文本

```
POST /api/v1/generate
```

**请求参数：**

```json
{
  "model": "ollama:deepseek-r1:8b",
  "prompt": "写一个计算两个数的最大公约数的Python函数",
  "max_tokens": 500,
  "temperature": 0.7,
  "stream": false,
  "stop": ["\n\n\n", "```\n\n"]
}
```

**响应示例：**

```json
{
  "text": "def gcd(a, b):\n    \"\"\"计算两个数的最大公约数\"\"\"\n    while b:\n        a, b = b, a % b\n    return a\n\n# 测试\nprint(gcd(48, 18))  # 输出 6",
  "model": "ollama:deepseek-r1:8b",
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 78,
    "total_tokens": 90
  },
  "finish_reason": "stop"
}
```

#### 流式生成文本

设置 `stream: true` 参数后，服务器将以 Server-Sent Events (SSE) 格式返回流式响应。

**响应示例（每一行都是一个 JSON 对象）：**

```
data: {"text":"def", "finish_reason": null}
data: {"text":" gcd", "finish_reason": null}
data: {"text":"(", "finish_reason": null}
...
data: {"text":")", "finish_reason": null}
data: {"text":"  # 输出 6", "finish_reason": "stop"}
```

### 嵌入生成接口

#### 生成文本嵌入

```
POST /api/v1/embed
```

**请求参数：**

```json
{
  "model": "ollama:bge-m3",
  "input": "这是一个示例文本",
  "dimensions": 1024
}
```

**响应示例：**

```json
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimensions": 1024,
  "model": "ollama:bge-m3",
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 5
  }
}
```

### 聊天接口

#### 聊天对话

```
POST /api/v1/chat
```

**请求参数：**

```json
{
  "model": "ollama:deepseek-r1:8b",
  "messages": [
    {"role": "system", "content": "你是一个有用的助手。"},
    {"role": "user", "content": "解释量子计算的基本原理。"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}
```

**响应示例：**

```json
{
  "message": {
    "role": "assistant",
    "content": "量子计算是一种利用量子力学原理进行信息处理的计算方式。与经典计算使用比特（0或1）不同，量子计算使用量子比特（qubit），它可以同时处于多个状态的叠加态。..."
  },
  "model": "ollama:deepseek-r1:8b",
  "usage": {
    "prompt_tokens": 35,
    "completion_tokens": 512,
    "total_tokens": 547
  },
  "finish_reason": "stop"
}
```

#### 流式聊天对话

流式聊天响应类似于流式生成文本，但会返回完整的消息对象：

```
POST /api/v1/chat/stream
```

**响应示例：**

```
data: {"delta":{"role":"assistant","content":"量"}, "finish_reason": null}
data: {"delta":{"content":"子"}, "finish_reason": null}
data: {"delta":{"content":"计"}, "finish_reason": null}
...
data: {"delta":{"content":"。"}, "finish_reason": "stop"}
```

### 服务状态接口

#### 健康检查

```
GET /api/v1/health
```

**响应示例：**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2023-11-15T12:34:56.789Z",
  "models_available": 5,
  "uptime_seconds": 3600
}
```

## Python API

AIgo 提供了丰富的 Python API，可以在您的应用程序中直接使用。

### 模型运行器

模型运行器是与底层模型交互的核心组件。

#### 基本用法

```python
from aigo.models import get_model_runner
from aigo.models.base import ModelConfig

# 创建模型配置
config = ModelConfig(
    provider="ollama",
    model_name="deepseek-r1:8b",
    temperature=0.7,
    max_tokens=2048
)

# 获取模型运行器
runner = get_model_runner(config)
runner.load()

# 文本生成
response = runner.generate("解释Python中的装饰器模式。")
print(response)

# 流式生成
for chunk in runner.stream_generate("请写一个快速排序算法。"):
    print(chunk, end="", flush=True)
```

#### 可用的模型运行器

AIgo 提供了多种模型运行器:

| 运行器类 | 提供商 | 描述 |
|---------|-------|------|
| `OllamaRunner` | Ollama | 连接到本地 Ollama 服务的运行器 |
| `OpenAIRunner` | OpenAI | 连接到 OpenAI API 的运行器 |
| `HuggingFaceRunner` | HuggingFace | 连接到 HuggingFace 模型的运行器 |
| `MixedModelRunner` | 多个 | 混合模型运行器，可以组合不同模型的能力 |

### 适配器

适配器是在模型运行器基础上提供更高级功能的组件。

#### 聊天适配器

```python
from aigo.models.adapters import ChatAdapter
from aigo.models.base import ModelConfig

# 创建配置
config = ModelConfig(provider="ollama", model_name="llama2")

# 创建聊天适配器
chat = ChatAdapter(config)

# 准备消息
messages = [
    {"role": "system", "content": "你是一个有用的助手。"},
    {"role": "user", "content": "什么是机器学习？"}
]

# 获取响应
response = chat.process(messages)
print(response)

# 添加新消息并继续对话
messages.append({"role": "assistant", "content": response})
messages.append({"role": "user", "content": "请详细解释监督学习和无监督学习的区别。"})

response = chat.process(messages)
print(response)
```

#### 文本生成适配器

```python
from aigo.models.adapters import TextGenerationAdapter
from aigo.models.base import ModelConfig

# 创建配置
config = ModelConfig(
    provider="ollama",
    model_name="deepseek-r1:8b",
    temperature=0.8
)

# 创建文本生成适配器
generator = TextGenerationAdapter(config)

# 生成文本
response = generator.generate(
    prompt="写一首关于人工智能的短诗。",
    max_tokens=200
)

print(response)
```

#### 嵌入适配器

```python
from aigo.models.adapters import EmbeddingAdapter
from aigo.models.base import ModelConfig

# 创建配置
config = ModelConfig(provider="ollama", model_name="bge-m3")

# 创建嵌入适配器
embedding = EmbeddingAdapter(config)

# 生成嵌入向量
vector = embedding.embed("这是一段示例文本。")
print(f"生成的向量维度: {len(vector)}")

# 计算相似度
texts = [
    "人工智能正在改变世界。",
    "深度学习是机器学习的一个分支。",
    "今天天气真好，我想去公园散步。"
]

vectors = embedding.embed_batch(texts)
similarities = embedding.compute_similarities("机器学习是什么？", texts)

for i, (text, sim) in enumerate(zip(texts, similarities)):
    print(f"{i+1}. {text} - 相似度: {sim:.4f}")
```

### 工具类

AIgo 提供了多种实用工具类。

#### 配置管理

```python
from aigo.utils.config import ConfigManager

# 加载配置
config = ConfigManager.load_config()

# 获取特定配置值
api_port = config.get("app.port", 8000)  # 默认值为 8000
model_name = config.get("models.inference.name")

# 设置配置值
config.set("models.inference.temperature", 0.8)

# 保存配置
config.save()
```

#### 记忆管理

```python
from aigo.modules.memory import ConversationMemory

# 创建对话记忆
memory = ConversationMemory(max_tokens=4000)

# 添加消息
memory.add_message("user", "你好，请介绍一下你自己。")
memory.add_message("assistant", "我是一个AI助手，可以帮助回答问题和完成各种任务。")

# 获取格式化上下文
formatted_context = memory.get_formatted_context()

# 获取消息历史
messages = memory.get_messages()

# 压缩记忆，移除不重要的旧消息以保持在token限制内
memory.compress()
```

#### 日志工具

```python
from aigo.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("my_module", log_level="INFO")

# 记录日志
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志，出现了问题: %s", "连接失败")

# 使用结构化日志
logger.info("用户操作", extra={
    "user_id": 123,
    "action": "login",
    "status": "success"
})
```

#### 向量存储

```python
from aigo.adapters.vector import VectorStore
from aigo.models.adapters import EmbeddingAdapter
from aigo.models.base import ModelConfig

# 创建嵌入适配器
config = ModelConfig(provider="ollama", model_name="bge-m3")
embedding_adapter = EmbeddingAdapter(config)

# 创建向量存储
vector_store = VectorStore(embedding_adapter, "data/vectors.db")

# 添加文档
documents = [
    {"id": "doc1", "text": "人工智能是计算机科学的一个分支", "metadata": {"source": "wiki"}},
    {"id": "doc2", "text": "机器学习是人工智能的核心技术之一", "metadata": {"source": "book"}},
    {"id": "doc3", "text": "深度学习是一种基于神经网络的机器学习方法", "metadata": {"source": "paper"}}
]

vector_store.add_documents(documents)

# 检索相似文档
results = vector_store.search("什么是机器学习", top_k=2)

# 打印结果
for result in results:
    print(f"文档ID: {result['id']}")
    print(f"文本: {result['text']}")
    print(f"相似度: {result['similarity']:.4f}")
    print(f"元数据: {result['metadata']}")
    print("---")
``` 