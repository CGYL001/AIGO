# AIgo

AIgo 是一个本地AI编程助手，基于Ollama模型，提供代码生成、语义搜索和知识库功能。

## 功能特点

- 使用Ollama本地模型，保护隐私及代码安全
- 支持代码生成、补全和优化
- 提供语义搜索和知识库功能
- 支持多种编程语言（Python、JavaScript、Java等）
- 可自定义模型和参数
- 代码分析和质量评估

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

## 系统要求

- Python 3.8+
- 内存: 至少8GB (推荐16GB以上)
- 支持Windows、macOS和Linux

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交Issue和Pull Request！
