# CodeAssistant 模型管理指南

本指南将帮助您管理和配置 CodeAssistant 中使用的 Ollama 模型。

## 已配置的模型

CodeAssistant 目前配置了以下模型：

1. **推理模型**：`llama2:7b-chat-q4_K_M` - 用于生成文本、回答问题和代码生成
2. **嵌入模型**：`bge-m3` - 用于文本向量化和语义搜索

## 模型管理工具

我们提供了一个简单的模型管理工具 `model_manager.py`，用于帮助您管理模型。

### 查看当前配置

```bash
python model_manager.py show
```

这将显示当前使用的模型和参数设置。

### 列出已下载的模型

```bash
python model_manager.py list
```

这将显示所有已下载的 Ollama 模型。

### 下载新模型

```bash
python model_manager.py download <模型名称>
```

例如：
```bash
python model_manager.py download phi:latest
```

### 切换默认推理模型


例如，切换回 deepseek-r1:8b 模型：
```bash
python model_manager.py switch deepseek-r1:8b
```

### 优化模型参数

```bash
python model_manager.py optimize --temperature <值> --max-tokens <值> --timeout <值>
```

例如：
```bash
python model_manager.py optimize --temperature 0.5 --max-tokens 1500 --timeout 90
```

参数说明：
- `temperature`：控制生成文本的随机性，范围 0.0-1.0，值越低生成的文本越确定
- `max-tokens`：控制生成文本的最大长度
- `timeout`：请求超时时间（秒）

## 模型推荐

根据不同的使用场景，我们推荐以下模型：

1. **日常使用**：`llama2:7b-chat-q4_K_M` - 平衡速度和质量
2. **代码生成**：`deepseek-r1:8b` - 更高质量的代码生成，但响应较慢
3. **快速回答**：如果您需要更快的响应，可以尝试下载更小的模型如 `phi:latest`

## 故障排除

1. **模型响应超时**：
   - 尝试减小 `max-tokens` 参数
   - 降低 `temperature` 参数
   - 切换到更小的模型

2. **模型下载失败**：
   - 检查网络连接
   - 确认模型名称正确
   - 查看 Ollama 官方库中是否有该模型

3. **模型加载错误**：
   - 确保您的系统内存足够
   - 重启 Ollama 服务：`ollama serve`

## 进阶使用

如果您需要更多高级功能，可以直接使用 Ollama 命令行工具：

```bash
# 运行特定模型
ollama run <模型名称>

# 查看模型详情
ollama show <模型名称>

# 删除模型
ollama rm <模型名称>
```

更多信息请参考 [Ollama 官方文档](https://github.com/ollama/ollama)。
