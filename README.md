# AIgo: 模块化AI助手平台

<div align="center">

![AIgo Logo](docs/images/logo.png)

**智能应用开发的模块化框架**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

## 项目概述

AIgo是一个模块化的AI助手开发平台，专为构建智能应用而设计。它提供了与多种AI模型后端交互的统一接口，简化了开发流程，并支持灵活的扩展能力。无论您是要开发聊天机器人、代码助手还是其他AI驱动的应用，AIgo都能为您提供所需的基础设施。

### 设计理念

- **模型无关性**：通过适配器模式实现与具体模型的解耦，支持无缝切换不同的模型后端
- **模块化架构**：核心功能被拆分为独立模块，便于维护和扩展
- **统一接口**：提供一致的API，简化开发流程
- **可扩展性**：易于添加新的模型提供商、适配器和功能模块
- **便捷导航**：提供多种项目资源导航工具，便于快速定位功能和资源

## 主要特性

- **多模型支持**：
  - **Ollama**：支持本地运行的开源模型(Llama2, DeepSeek, Phi等)
  - **OpenAI**：支持GPT系列模型
  - **可扩展**：易于添加其他模型提供商

- **完整工具链**：
  - **命令行接口**：功能丰富的CLI
  - **REST API服务**：用于集成到其他应用
  - **流式输出**：支持实时流式响应
  - **配置管理**：灵活的配置系统
  - **Docker支持**：容器化部署
  - **项目导航**：多种导航工具，包括路径索引和可视化管理面板

- **开发友好**：
  - **类型注解**：完整的类型提示
  - **测试覆盖**：单元测试和集成测试
  - **详细文档**：全面的API和使用文档
  - **资源定位**：强大的项目路径和功能导航系统

- **跨平台支持**：
  - **Windows兼容**：在Windows 10/11上完全支持
  - **Linux优化**：为各种Linux发行版优化
  - **macOS支持**：支持Apple Silicon和Intel Mac
  - **平台工具**：提供跨平台路径、依赖和进程管理工具

- **高级功能**：
  - **多语言支持**：通过翻译中间件支持多语言交互
  - **模型优化**：自动优化模型以适应硬件限制
  - **模型编排**：协调多个模型进行协作推理和集成

## 系统架构

AIgo采用模块化分层架构，确保不同组件之间的清晰分离和责任划分：

```
+------------------+    +------------------+    +------------------+
|     接口层       |    |                  |    |                  |
|  CLI / REST API  |<-->|     核心层       |<-->|   适配器层       |
|  命令行 / Web服务 |    |  业务逻辑 / 流程 |    | 连接外部服务/模型 |
+------------------+    +------------------+    +------------------+
                              |      ^
                              v      |
                        +------------------+
                        |    基础设施层     |
                        | 配置/日志/工具类  |
                        +------------------+
```

### 核心组件

| 组件 | 描述 | 路径 |
|------|------|------|
| **Models** | 模型适配器和运行器 | `aigo/models/` |
| **Adapters** | 外部服务连接器 | `aigo/adapters/` |
| **Modules** | 核心功能模块 | `aigo/modules/` |
| **Runtime** | 运行时服务 | `aigo/runtime/` |
| **CLI** | 命令行工具 | `aigo/cli/` |

## 快速开始

### 安装

```bash
# 从PyPI安装（推荐）
pip install aigo

# 或从源码安装
git clone https://github.com/yourusername/AIgo.git
cd AIgo
pip install -e .
```

### 项目导航

AIgo提供了多种导航系统，帮助您快速定位项目资源：

1. **项目路径导航**
   - 查看 `PATH_GUIDE.md` 文件，获取项目结构和关键路径概览

2. **命令行导航工具**
   ```bash
   # 查找特定功能相关文件
   python tools/path_finder.py find --feature "模型管理"
   
   # 查看特定目录结构
   python tools/path_finder.py explore --directory "src/modules"
   
   # 搜索关键词
   python tools/path_finder.py search --keyword "模型优化"
   ```

3. **模型管理面板**
   ```bash
   # 启动模型管理可视化界面
   python tools/models_dashboard.py
   ```

更多导航帮助，请查看 `docs/navigation_guide.md`。

### 设置

AIgo默认使用Ollama作为模型后端，需要先安装Ollama:

```bash
# 安装Ollama (参考: https://ollama.com/download)

# 拉取默认模型
ollama pull deepseek-r1:8b
ollama pull bge-m3
```

### 基本使用

```bash
# 使用命令行运行
aigo run

# 或使用Python模块
python -m aigo.cli.__main__ run
```

## 使用示例

### 命令行使用

```bash
# 基本使用示例
aigo run --model llama2 --provider ollama

# 启动API服务
aigo serve --mode http --port 8000

# 配置管理
aigo config set --model deepseek-r1 --provider ollama
aigo config list
```

### Python API 使用

```python
from aigo.models import get_model_runner
from aigo.models.base import ModelConfig

# 配置模型
config = ModelConfig(
    provider="ollama",
    model_name="deepseek-r1:8b",
    device="auto"
)

# 使用模型
runner = get_model_runner(config)
runner.load()
response = runner.generate("请写一个Python函数，计算斐波那契数列。")
print(response)

# 流式输出
for chunk in runner.stream_generate("解释量子计算的基本原理。"):
    print(chunk, end="", flush=True)
```

### 适配器模式

```python
from aigo.models.adapters import ChatAdapter, create_adapter
from aigo.models.base import ModelConfig

# 创建聊天适配器
config = ModelConfig(provider="ollama", model_name="llama2")
chat = ChatAdapter(config)

# 聊天对话
messages = [
    {"role": "system", "content": "你是一个有用的助手。"},
    {"role": "user", "content": "解释一下Python的装饰器是什么？"}
]
response = chat.process(messages)
print(response)
```

### 多语言支持

```python
from aigo.adapters import create_translator, TranslationMiddleware

# 创建翻译中间件
translator = create_translator(type="offline")
middleware = TranslationMiddleware(
    translator=translator,
    user_lang="zh",  # 用户使用中文
    model_lang="en"  # 模型使用英文
)

# 用户输入中文，自动翻译给模型
user_input = "人工智能的未来发展趋势是什么？"
model_input = middleware.translate_to_model(user_input)

# 模型生成英文回复，自动翻译回中文
model_output = model.generate(model_input)
user_output = middleware.translate_from_model(model_output)
print(user_output)
```

### 代码语言转换

```python
from aigo import get_translator

# 获取Python到JavaScript的转换器
translator = get_translator('python', 'javascript')

# 转换代码
python_code = """
def greet(name):
    return f"Hello, {name}!"

result = greet("World")
print(result)
"""

js_code = translator.translate(python_code)
print(js_code.translated_code)
```

### 隐藏功能发现与启用

AIgo包含一些高级功能，这些功能默认是隐藏的，但可以通过特性发现工具找到并启用。

```python
from aigo import discover_feature, enable_feature, get_all_hidden_features

# 查看所有隐藏功能
hidden_features = get_all_hidden_features()
for feature in hidden_features:
    print(f"{feature['name']}: {feature['description']}")

# 通过关键词发现功能
feature = discover_feature("有没有可以优化模型性能的工具?")
if feature:
    print(f"发现功能: {feature['name']}")
    print(f"描述: {feature['description']}")

# 启用隐藏功能
if enable_feature("model_optimization"):
    print("模型优化功能已启用")

# 现在可以导入并使用模型优化功能
from aigo.models.optimization import optimize_model, OptimizationConfig
```

也可以使用命令行工具管理隐藏功能:

```bash
# 列出所有隐藏功能
python -m aigo.cli.feature_cmd list

# 发现功能
python -m aigo.cli.feature_cmd discover "系统优化"

# 启用功能
python -m aigo.cli.feature_cmd enable system_optimization

# 检查功能状态
python -m aigo.cli.feature_cmd status model_restructuring
```

### 模型优化

```python
from aigo.models import get_model_runner, OptimizationConfig, optimize_model

# 创建模型
config = ModelConfig(provider="ollama", model_name="llama2:7b")
model = get_model_runner(config)

# 优化配置
opt_config = OptimizationConfig(
    use_8bit_quantization=True,
    use_flash_attention=True,
    kv_cache_enabled=True
)

# 应用优化
optimized_model = optimize_model(model, opt_config)
response = optimized_model.generate("写一个快速排序算法")
```

### 多模型协作

```python
from aigo.models import get_coordinator, ModelConfig

# 获取模型协调器
coordinator = get_coordinator()

# 添加不同模型
coordinator.add_model("coder", ModelConfig(provider="ollama", model_name="codellama:7b"))
coordinator.add_model("reasoner", ModelConfig(provider="ollama", model_name="llama2:7b"))

# 协作解决问题
solution = coordinator.collaborative_reasoning(
    problem="设计一个高效的文件搜索算法",
    model_names=["reasoner", "coder"],
    max_iterations=3
)
print(solution)
```

## 项目结构

```
aigo/                  # 主包
  ├── adapters/        # 外部服务适配器
  │   ├── storage/     # 存储适配器(文件系统、数据库等)
  │   ├── vector/      # 向量数据库适配器
  │   ├── translation.py # 翻译适配器
  │   └── web/         # Web服务适配器
  ├── models/          # 模型适配器和管理
  │   ├── base.py      # 模型抽象接口
  │   ├── adapters.py  # 高级模型适配器(聊天、文本生成等)
  │   ├── optimization.py # 模型优化工具
  │   ├── coordinator.py # 多模型协调器
  │   └── providers/   # 各种模型提供商实现
  ├── modules/         # 核心功能模块
  │   ├── memory/      # 记忆和上下文管理
  │   └── processor/   # 数据处理器
  ├── runtime/         # 运行时服务
  │   ├── api_server.py # REST API服务
  │   └── scheduler.py  # 任务调度器
  └── cli/             # 命令行接口
      ├── __main__.py  # CLI入口点
      └── commands/    # CLI命令
```

## 配置管理

AIgo使用分层配置系统，可以通过以下方式进行配置：

1. **默认配置文件** (`config/default/config.json`)
2. **环境变量** (例如 `AIGO_MODEL=deepseek-r1`)
3. **命令行参数** (例如 `--model deepseek-r1`)

主要配置选项：

| 配置项 | 描述 | 默认值 |
|-------|------|-------|
| `models.inference.name` | 推理模型名称 | `deepseek-r1:8b` |
| `models.inference.provider` | 模型提供商 | `ollama` |
| `models.embedding.name` | 嵌入模型名称 | `bge-m3` |
| `app.host` | API服务主机 | `localhost` |
| `app.port` | API服务端口 | `8000` |
| `optimization.enabled` | 是否启用自动优化 | `true` |
| `optimization.level` | 优化级别 (basic/advanced) | `basic` |

## 高级功能

### 模型管理

AIgo提供了一个模型管理工具，用于管理Ollama模型：

```bash
# 查看当前模型配置
python model_manager.py show

# 列出所有已下载的模型
python model_manager.py list

# 切换默认推理模型
python model_manager.py switch deepseek-r1:13b

# 优化模型参数
python model_manager.py optimize --temperature 0.7 --max-tokens 2000
```

### 模型优化器

AIgo提供了自动模型优化功能，可根据硬件限制自动调整模型性能：

```bash
# 运行优化示例
python examples/advanced_features.py

# 使用特定优化配置
python model_manager.py run --optimize --quantize 8bit --flash-attn
```

### 多模型协同

AIgo支持多模型协同工作，实现更复杂的任务处理：

```bash
# 启动多模型协同实例
aigo run --multi-model --models llama2,codellama,phi2

# 使用模型集成来提高推理质量
aigo run --ensemble --models llama2,phi2 --ensemble-method voting
```

### Docker支持

AIgo提供了Docker支持，可以通过以下命令构建和运行Docker容器：

```bash
# 构建Docker镜像
docker build -t aigo .

# 运行Docker容器
docker run -p 8000:8000 -v ./config:/app/config -v ./data:/app/data aigo
```

也可以使用docker-compose：

```bash
docker-compose up -d
```

## 详细文档

更详细的文档请参考：

- [完整安装指南](docs/installation.md)
- [配置参考](docs/configuration.md)
- [API文档](docs/api.md)
- [模型指南](MODEL_GUIDE.md)
- [开发者指南](CONTRIBUTING.md)
- [示例集合](docs/examples.md)
- [故障排除](docs/troubleshooting.md)
- [企业级部署指南](docs/enterprise_deployment.md)
- [科研级使用指南](docs/scientific_usage.md)
- [AI规则配置系统](docs/ai_rules.md)
- [高级特性指南](docs/advanced_features.md)
- [多语言支持](docs/multilingual.md)
- [模型优化指南](docs/model_optimization.md)
- [跨平台兼容性指南](docs/cross_platform_guide.md)

## 系统要求

- **Python**: 3.9+
- **内存**: 根据使用的模型而定
  - 最小: 4GB RAM (使用小型模型)
  - 推荐: 16GB+ RAM (使用中大型模型)
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+

## 贡献

我们欢迎各种形式的贡献：

- 提交问题和建议
- 贡献代码
- 改进文档

请阅读[贡献指南](CONTRIBUTING.md)了解详情。

## 许可证

AIgo采用[MIT许可证](LICENSE)。

## 致谢

- [Ollama](https://ollama.com/) - 为开源模型提供本地运行支持
- [OpenAI](https://openai.com/) - 提供先进的AI模型
- [Argostranslate](https://github.com/argosopentech/argos-translate) - 提供离线翻译能力
- [PyTorch](https://pytorch.org/) - 提供深度学习支持
- 所有开源贡献者和社区成员

---

<div align="center">
  <strong>AIgo - 让AI应用开发更简单、更强大</strong>
</div>

AIgo 是一个本地AI编程助手，基于Ollama模型，提供代码生成、语义搜索、知识库功能和代码语言转换功能。

## 功能特点

- 使用Ollama本地模型，保护隐私及代码安全
- 支持代码生成、补全和优化
- 提供语义搜索和知识库功能
- 支持多种编程语言（Python、JavaScript、Java等）
- 可自定义模型和参数
- 代码分析和质量评估
- 代码语言转换器（支持Python到JavaScript转换）

## 安装说明

1. 克隆仓库
```bash
git clone <仓库URL>
cd AIgo
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 安装Ollama
访问 [Ollama官网](https://ollama.com/download) 下载并安装Ollama

4. 下载所需模型
```bash
ollama pull llama2:7b-chat-q4_K_M
ollama pull bge-m3
```

## 使用方法

1. 启动Ollama服务
```bash
ollama serve
```

2. 启动AIgo
```bash
python start_assistant.py
```

3. 在浏览器中访问
```
http://localhost:8080
```

## 模型管理

我们提供了模型管理工具，可以方便地切换和配置模型：

```bash
# 查看当前模型配置
python model_manager.py show

# 列出已下载的模型
python model_manager.py list

# 切换模型
python model_manager.py switch <模型名称>
```

详细说明请参考 [模型管理指南](MODEL_GUIDE.md)。

## 示例

测试大语言模型：
```bash
python test_llama2.py
```

测试知识库功能：
```bash
python test_knowledge_base.py
```

测试代码语言转换功能：
```bash
python examples/code_translation_demo.py
```

## 代码语言转换器

AIgo提供了代码语言转换功能，目前支持Python到JavaScript的转换。使用示例：

```python
from aigo import get_translator

# 获取Python到JavaScript的转换器
translator = get_translator('python', 'javascript')

# 转换代码
python_code = """
def greet(name):
    return f"Hello, {name}!"

result = greet("World")
print(result)
"""

js_code = translator.translate(python_code)
print(js_code.translated_code)
```

更多示例请参考 `examples/code_translation_demo.py`。

## 系统要求

- Python 3.8+
- 内存: 至少8GB (推荐16GB以上)
- 支持Windows、macOS和Linux

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交Issue和Pull Request！
