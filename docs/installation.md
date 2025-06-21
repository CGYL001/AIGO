# AIgo 安装指南

本文档提供了详细的 AIgo 安装步骤、环境要求和配置选项，帮助您快速设置 AIgo 开发或生产环境。

## 目录
- [系统要求](#系统要求)
- [安装方法](#安装方法)
  - [使用 pip 安装](#使用-pip-安装)
  - [从源码安装](#从源码安装)
  - [Docker 安装](#docker-安装)
- [模型后端设置](#模型后端设置)
  - [Ollama 设置](#ollama-设置)
  - [OpenAI 设置](#openai-设置)
- [验证安装](#验证安装)
- [环境配置](#环境配置)
- [常见问题](#常见问题)

## 系统要求

AIgo 适用于以下环境：

### 基本要求
- **Python**: 3.9 或更新版本
- **操作系统**:
  - Windows 10/11
  - macOS 10.15+
  - Ubuntu 20.04+ / Debian 11+ / CentOS 7+
  - 其他支持 Python 3.9+ 的 Linux 发行版

### 硬件要求
硬件需求主要取决于您计划使用的模型：

1. **最小配置** (使用小型模型或远程 API):
   - CPU: 双核处理器
   - RAM: 4GB
   - 存储: 2GB 可用空间

2. **推荐配置** (使用本地中型模型):
   - CPU: 4核+ 处理器
   - RAM: 16GB
   - 存储: 10GB+ 可用空间
   - GPU: 支持 CUDA 的 NVIDIA GPU (可选但推荐)

3. **高性能配置** (使用本地大型模型):
   - CPU: 8核+ 处理器
   - RAM: 32GB+
   - 存储: 20GB+ 可用空间
   - GPU: 8GB+ VRAM 的 NVIDIA GPU

## 安装方法

### 使用 pip 安装

最简单的安装方式是通过 pip 包管理器安装:

```bash
pip install aigo
```

安装特定版本:

```bash
pip install aigo==0.1.0
```

安装带有额外功能的版本:

```bash
# 安装全部功能
pip install aigo[all]

# 只安装 API 服务相关依赖
pip install aigo[api]

# 只安装开发相关依赖
pip install aigo[dev]
```

### 从源码安装

从源码安装可以获取最新的开发版本或自定义修改代码:

```bash
# 克隆代码仓库
git clone https://github.com/yourusername/AIgo.git
cd AIgo

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

如果您需要安装特定分支:

```bash
git clone -b develop https://github.com/yourusername/AIgo.git
cd AIgo
pip install -e .
```

### Docker 安装

AIgo 提供了 Docker 支持，可以在容器化环境中运行:

#### 使用预构建镜像

```bash
# 拉取最新镜像
docker pull yourusername/aigo:latest

# 运行容器
docker run -p 8000:8000 -v ./config:/app/config -v ./data:/app/data yourusername/aigo:latest
```

#### 构建自定义镜像

```bash
# 从源码构建镜像
git clone https://github.com/yourusername/AIgo.git
cd AIgo
docker build -t aigo:custom .

# 运行自定义镜像
docker run -p 8000:8000 -v ./config:/app/config -v ./data:/app/data aigo:custom
```

#### 使用 Docker Compose

AIgo 提供了 Docker Compose 配置，使服务编排更加简单:

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 模型后端设置

AIgo 支持多种模型后端，以下是如何配置最常用的两种:

### Ollama 设置

[Ollama](https://ollama.com/) 是 AIgo 默认的本地模型后端，支持在本地运行各种开源模型。

#### 安装 Ollama

1. **Windows**:
   从 [Ollama 官网](https://ollama.com/download) 下载并安装最新版本。

2. **macOS**:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

3. **Linux**:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

#### 下载模型

AIgo 默认使用 deepseek-r1:8b 作为推理模型，bge-m3 作为嵌入模型:

```bash
# 下载默认推理模型
ollama pull deepseek-r1:8b

# 下载默认嵌入模型
ollama pull bge-m3
```

您也可以下载其他模型:

```bash
# 下载其他模型
ollama pull llama2
ollama pull phi:latest
```

### OpenAI 设置

使用 OpenAI API 需要设置 API 密钥:

1. 获取 [OpenAI API 密钥](https://platform.openai.com/api-keys)

2. 设置环境变量:
   ```bash
   # Linux/macOS
   export OPENAI_API_KEY=your_api_key_here
   
   # Windows PowerShell
   $env:OPENAI_API_KEY="your_api_key_here"
   
   # Windows CMD
   set OPENAI_API_KEY=your_api_key_here
   ```

3. 或在配置文件中设置 (推荐):
   创建或编辑 `config/user/config.json`:
   ```json
   {
     "models": {
       "inference": {
         "provider": "openai",
         "name": "gpt-4-turbo",
         "api_key": "your_api_key_here"
       }
     }
   }
   ```

## 验证安装

安装完成后，可以运行以下命令验证安装是否成功:

```bash
# 检查 AIgo 版本
aigo --version

# 运行内置示例
aigo run --test

# 或者运行 Python 模块版本
python -m aigo.cli.__main__ --version
```

## 环境配置

### 环境变量

AIgo 支持通过环境变量进行配置:

| 环境变量 | 描述 | 示例值 |
|---------|------|--------|
| `AIGO_CONFIG_DIR` | 配置目录路径 | `/path/to/config` |
| `AIGO_MODEL` | 默认推理模型 | `deepseek-r1:13b` |
| `AIGO_MODEL_PROVIDER` | 默认模型提供商 | `ollama` |
| `AIGO_API_HOST` | API 服务主机 | `0.0.0.0` |
| `AIGO_API_PORT` | API 服务端口 | `8080` |
| `AIGO_DEBUG` | 调试模式 | `true` |
| `OPENAI_API_KEY` | OpenAI API密钥 | `sk-...` |

### 配置文件

完整的配置可以通过 JSON 配置文件设置:

1. **默认配置**:
   AIgo 会自动加载 `config/default/config.json` 作为默认配置。

2. **用户配置**:
   可以创建 `config/user/config.json` 覆盖默认配置。

3. **项目配置**:
   在项目目录下创建 `.aigo/config.json` 为特定项目设置配置。

配置示例:
```json
{
  "app": {
    "host": "localhost",
    "port": 8000,
    "debug": false,
    "log_level": "info"
  },
  "models": {
    "inference": {
      "name": "deepseek-r1:8b",
      "provider": "ollama",
      "api_base": "http://localhost:11434",
      "temperature": 0.7,
      "max_tokens": 2048,
      "timeout_seconds": 60
    },
    "embedding": {
      "name": "bge-m3",
      "provider": "ollama",
      "dimensions": 1024
    }
  }
}
```

## 常见问题

### 1. 安装错误: "Microsoft Visual C++ 14.0 or greater is required"

**解决方案**: 下载并安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/), 确保勾选"C++ 构建工具"。

### 2. 无法连接到 Ollama 服务

**解决方案**: 
- 确保 Ollama 服务已启动: `ollama serve`
- 检查端口是否被占用: `netstat -ano | findstr 11434`
- 检查防火墙设置是否阻止了连接

### 3. 模型下载很慢或失败

**解决方案**:
- 检查您的网络连接
- 尝试使用更小的模型
- 对于中国用户，可能需要设置代理

### 4. 找不到 aigo 命令

**解决方案**:
- 确保 Python 的 Scripts 目录在您的 PATH 中
- 尝试使用 `python -m aigo.cli.__main__` 代替

### 5. Docker 容器无法访问

**解决方案**:
- 检查端口映射是否正确: `-p 8000:8000`
- 查看容器日志: `docker logs aigo`
- 确保挂载了正确的卷: `-v ./config:/app/config` 