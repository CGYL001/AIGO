# AIgo 安装指南

本文档提供详细的AIgo安装说明，包括基本安装、高级功能安装和常见问题解决方法。

## 环境需求

- **Python**: 3.9 或更高版本
- **操作系统**: Windows, Linux, macOS
- **GPU加速** (可选): NVIDIA GPU + CUDA 11.7 或更高版本

## 快速安装

使用我们的自动安装脚本可以简化安装流程：

```bash
# 下载并切换到项目目录
git clone https://github.com/yourusername/AIgo.git
cd AIgo

# 运行安装脚本 (默认安装核心功能)
python install.py

# 或指定安装模式
python install.py --mode all  # 安装所有功能
```

## 手动安装

如果您希望手动控制安装过程，请按照以下步骤操作：

### 1. 下载代码库

```bash
git clone https://github.com/yourusername/AIgo.git
cd AIgo
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

根据您的需求选择以下安装方式之一：

```bash
# 仅安装核心功能所需依赖
pip install -r requirements-core.txt
pip install -e .

# 安装API服务相关依赖
pip install -r requirements-api.txt
pip install -e .

# 安装机器学习和模型功能依赖
pip install -r requirements-ml.txt
pip install -e .

# 安装开发环境依赖
pip install -r requirements-dev.txt
pip install -e .

# 安装所有功能的依赖
pip install -r requirements-all.txt
pip install -e .
```

## 依赖模块说明

AIgo的依赖已按功能模块分组，方便您按需安装：

### 核心依赖 (requirements-core.txt)

基本功能所需的核心依赖：
- **typer**: 命令行接口
- **requests/httpx**: HTTP客户端
- **psutil**: 系统监控
- **pyyaml**: 配置文件支持
- **numpy**: 数值计算
- **sqlalchemy**: 数据库ORM
- **flask**: Web框架
- **jinja2/werkzeug**: Web模板和工具

### API服务依赖 (requirements-api.txt)

用于REST API服务的依赖：
- **fastapi**: API框架
- **uvicorn**: ASGI服务器
- **pydantic**: 数据验证

### 机器学习依赖 (requirements-ml.txt)

用于模型、翻译和知识库功能：
- **torch**: PyTorch框架
- **optimum/accelerate**: 模型优化
- **faiss-cpu**: 向量检索(非Windows)
- **argostranslate**: 离线翻译
- **fasttext**: 文本分类(非Windows)

### 开发依赖 (requirements-dev.txt)

用于开发和测试：
- **pytest**: 测试框架
- **black/isort/ruff**: 代码格式化和检查
- **sphinx**: 文档生成
- **mypy**: 类型检查
- **pre-commit**: Git hooks管理

## 平台特定说明

### Windows

Windows平台有一些依赖需要特殊处理：

1. **faiss-cpu**: Windows需要手动安装
   ```bash
   # 下载地址: https://github.com/kyamagu/faiss-wheels/releases
   # 下载后手动安装:
   pip install faiss_cpu-1.7.0-cp39-cp39-win_amd64.whl  # 根据Python版本选择合适的wheel文件
   ```

2. **bitsandbytes**: Windows需要特殊版本
   ```bash
   # 下载地址: https://github.com/jllllll/bitsandbytes-windows-webui/releases
   pip install bitsandbytes-0.38.0-py3-none-win_amd64.whl
   ```

3. **aiohttp**: Windows上可能有问题，我们默认安装httpx作为替代

### macOS (Apple Silicon)

M1/M2/M3芯片需要特殊版本的PyTorch：

```bash
pip install torch==2.0.0 
```

## 配置Ollama

AIgo可以与Ollama一起使用以获得本地模型推理能力：

1. 从[Ollama官网](https://ollama.com/download)下载并安装
2. 拉取所需模型：
   ```bash
   ollama pull deepseek-r1:8b
   ollama pull bge-m3
   ```

## 验证安装

安装完成后，可通过以下方式验证：

1. 检查AIgo版本：
   ```bash
   python -c "from AIGO import __version__; print(f'AIgo {__version__} 已安装')"
   ```

2. 运行示例：
   ```bash
   python simple_example.py
   ```

3. 查看项目导航：
   ```bash
   cat PATH_GUIDE.md
   ```

4. 启动模型管理面板：
   ```bash
   python tools/models_dashboard.py
   ```

## 使用项目导航系统

AIgo提供了多种导航系统，帮助您快速定位项目资源：

1. **查看路径索引**:
   ```bash
   cat PATH_GUIDE.md
   ```

2. **使用路径查找工具**:
   ```bash
   # 列出所有可用功能
   python tools/path_finder.py list-features
   
   # 查找特定功能的文件
   python tools/path_finder.py find --feature "模型管理"
   ```

3. **启动模型管理面板**:
   ```bash
   python tools/models_dashboard.py
   ```

## 模型配置

AIgo使用模型注册表来管理模型元数据和配置，而不是直接在代码库中存储模型文件。这样可以减小项目体积，并允许用户根据自己的需求选择和配置模型。

### 清理示例模型元数据

项目中包含的模型元数据文件仅作为示例，建议在安装后清理这些文件：

```bash
# 保留README.md和模板文件，删除示例配置
rm -rf models/registry/models/*
```

### 配置个人模型

1. 创建个人模型配置目录：
   ```bash
   mkdir -p models/registry/models/my_models
   ```

2. 创建自定义模型列表：
   ```bash
   cp models/registry/available_models.json models/registry/available_models.custom.json
   # 编辑 available_models.custom.json 添加您自己的模型
   ```

3. 在配置文件中指定使用自定义模型列表和下载目录：
   ```bash
   # 编辑 config.json
   # 添加以下配置
   {
     "models": {
       "registry": "models/registry/available_models.custom.json",
       "download_directory": "/path/to/your/model/storage"
     }
   }
   ```

### 模型下载

AIgo支持按需下载模型，您可以使用以下命令下载模型：

```bash
python model_manager.py download --name "model_name"
```

或者在首次使用时自动下载。

## 减小项目体积

如果您希望减小项目体积，可以执行以下操作：

1. 清理Git历史（如果不需要完整历史）：
   ```bash
   git clone --depth 1 https://github.com/your-repo/AIgo.git
   # 或者对现有仓库
   git gc --aggressive --prune=now
   ```

2. 删除临时文件和缓存：
   ```bash
   rm -rf temp_checkpoints/ temp_training_memory/ cache/ __pycache__/ output/
   ```

3. 移除不必要的虚拟环境（如果存在多个）：
   ```bash
   rm -rf venv/ .venv/
   ```

4. 使用.gitignore排除大型文件和个性化配置。

## 故障排除

### 通用问题

1. **ModuleNotFoundError**: 检查是否已安装依赖
   ```bash
   pip install -r requirements-core.txt
   ```

2. **服务启动超时**：检查Ollama服务是否运行
   ```bash
   # 启动Ollama
   ollama serve
   
   # 或跳过Ollama
   python start_assistant.py --no-ollama
   ```

### Windows特定问题

1. **aiohttp安装失败**：使用httpx替代
   ```bash
   pip install httpx
   ```

2. **无法安装faiss-cpu**：尝试手动安装wheel文件
   ```bash
   # 下载并安装预编译的wheel文件
   # 从 https://github.com/kyamagu/faiss-wheels/releases 下载
   ```

3. **venv激活失败**：使用PowerShell时可能需要修改执行策略
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### macOS特定问题

1. **PyTorch兼容性问题**：在Apple Silicon上使用兼容版本
   ```bash
   pip install torch==2.0.0 
   ```

## 获取帮助

如果您遇到其他安装问题：

1. 查看[项目文档](docs/)
2. 查看[故障排除指南](docs/troubleshooting.md)
3. 提交[GitHub Issue](https://github.com/yourusername/AIgo/issues) 