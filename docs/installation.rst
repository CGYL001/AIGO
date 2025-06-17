安装指南
========

系统要求
-------

AIgo可在Windows、Linux和macOS上运行，需要满足以下条件：

* **操作系统:**
  * Windows 10/11
  * Ubuntu 20.04+/Debian 11+/CentOS 8+
  * macOS Big Sur (11.0) 或更新版本

* **Python:** 3.8 或更高版本

* **硬件:**
  * CPU: 4核心或更多
  * 内存: 至少8GB RAM
  * 存储: 至少2GB可用空间
  * GPU: 可选，但推荐用于本地AI模型 (CUDA或ROCm支持)

安装方法
-------

从源码安装
^^^^^^^^

1. 克隆代码库：

   .. code-block:: bash

      git clone https://github.com/yourusername/AIgo.git
      cd AIgo

2. 安装依赖：

   .. code-block:: bash

      # 安装基本依赖
      pip install -r requirements.txt

      # 如需GPU支持，请安装GPU版本依赖
      # pip install -r requirements-gpu.txt

3. 设置环境：

   .. code-block:: bash

      # Windows
      .\dev-setup.ps1

      # Linux/macOS
      ./dev-setup.sh

4. 运行应用：

   .. code-block:: bash

      python run.py

使用Docker安装
^^^^^^^^^^^

我们提供了Docker镜像，便于快速部署：

1. 拉取镜像：

   .. code-block:: bash

      docker pull aigo/aigo:latest

2. 运行容器：

   .. code-block:: bash

      docker run -d -p 8000:8000 -v /path/to/config:/app/config --name aigo aigo/aigo:latest

3. 或者使用docker-compose:

   .. code-block:: bash

      docker-compose up -d

自定义安装
^^^^^^^^

对于特定需求，可以自定义安装：

1. 创建虚拟环境：

   .. code-block:: bash

      # 使用venv
      python -m venv venv
      source venv/bin/activate  # Linux/macOS
      venv\Scripts\activate    # Windows

2. 选择性安装组件：

   .. code-block:: bash

      # 仅安装核心功能
      pip install -r requirements-core.txt

      # 安装特定模块所需依赖
      pip install -r requirements-modules/knowledge_base.txt

配置
----

基本配置
^^^^^^

AIgo的配置文件位于 ``config/`` 目录下，主要包括：

1. **默认配置:** ``config/default/config.json``
2. **用户配置:** ``config/user/config.json``
3. **模型配置:** ``config/models/[model_name].json``

如需修改配置，建议修改用户配置文件而非默认配置。

模型配置
^^^^^^

AIgo支持多种AI模型，包括本地模型和远程API：

1. **OpenAI模型:**

   .. code-block:: json

      {
        "name": "gpt-3.5-turbo",
        "provider": "openai",
        "api_key": "your_api_key",
        "endpoint": "https://api.openai.com/v1",
        "parameters": {
          "temperature": 0.7,
          "max_tokens": 2048
        }
      }

2. **本地模型:**

   .. code-block:: json

      {
        "name": "llama2-7b",
        "provider": "ollama",
        "endpoint": "http://localhost:11434/api/generate",
        "parameters": {
          "temperature": 0.7,
          "max_tokens": 2048
        }
      }

高级配置
^^^^^^

对于高级用户，可通过以下方式进一步自定义:

1. **环境变量:**

   设置环境变量可覆盖配置文件中的值：

   .. code-block:: bash

      # Windows
      set AIGO_PORT=9000
      set AIGO_LOG_LEVEL=DEBUG

      # Linux/macOS
      export AIGO_PORT=9000
      export AIGO_LOG_LEVEL=DEBUG

2. **命令行参数:**

   运行时可通过命令行参数覆盖配置：

   .. code-block:: bash

      python run.py --port 9000 --log-level DEBUG

故障排除
-------

常见问题
^^^^^^

1. **无法启动应用:**

   * 检查Python版本是否满足要求
   * 确认所有依赖都已正确安装
   * 检查日志文件 ``logs/aigo.log``

2. **模型调用失败:**

   * 检查API密钥是否正确配置
   * 确认网络连接正常
   * 查看模型服务是否可用

3. **内存占用过高:**

   * 调整 ``config.json`` 中的 ``max_memory_usage``
   * 关闭不必要的模块
   * 使用更小的模型或参数

获取帮助
^^^^^^

如果遇到安装或配置问题，可通过以下方式获取帮助：

* **项目仓库:** 在GitHub仓库中提交Issue
* **文档:** 查阅完整的在线文档
* **社区:** 加入我们的Discord或论坛获取支持 