AIgo - 智能编程助手
====================

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python: 3.8+

欢迎来到AIgo文档！
------------------

AIgo是一个智能编程助手，它结合了多种AI模型，为开发者提供代码补全、错误检查、知识库和更多功能。本文档提供了项目的技术细节、API参考和使用指南。

特性
----

* 代码补全和智能提示
* 多模型支持和切换
* 本地知识库管理
* 仓库集成（GitHub、GitLab、Gitee）
* 代码分析和优化建议
* 系统资源监控
* 用户偏好管理

快速开始
-------

.. code-block:: bash

   # 安装依赖
   pip install -r requirements.txt
   
   # 配置环境变量
   # Windows
   .\dev-setup.ps1
   
   # 启动AIgo
   python run.py

系统架构
-------

AIgo采用模块化设计，主要组件包括：

* **模块系统** - 核心功能模块的管理和调度
* **知识库** - 本地文档和代码知识的管理
* **API服务** - 提供HTTP接口给外部应用调用
* **模型集成** - 支持多种AI模型的统一调用接口

.. toctree::
   :maxdepth: 2
   :caption: 内容:

   installation
   configuration
   api/index
   modules/index
   development
   faq

模块参考
-------

.. toctree::
   :maxdepth: 2
   :caption: 模块:
   
   modules/code_analysis
   modules/code_completion
   modules/context_manager
   modules/knowledge_base
   modules/repo_integration
   modules/prompt_engineering
   modules/system_monitor

API参考
------

.. toctree::
   :maxdepth: 2
   :caption: API:
   
   api/mcp_api
   api/auth
   api/models
   api/preferences
   api/repository

索引和表格
--------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 