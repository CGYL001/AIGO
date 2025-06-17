模块参考
========

AIgo由多个功能模块组成，每个模块负责不同的功能。本文档提供了各模块的详细说明、API参考和使用示例。

核心模块
-------

.. toctree::
   :maxdepth: 1

   code_analysis
   code_completion
   context_manager
   knowledge_base
   prompt_engineering

基础设施模块
----------

.. toctree::
   :maxdepth: 1

   system_monitor
   repo_integration
   network_proxy

用户界面模块
---------

.. toctree::
   :maxdepth: 1

   ui
   developer_preferences

模块依赖关系
----------

AIgo的模块之间存在一定的依赖关系，下图展示了主要模块之间的依赖：

.. code-block:: text

    +-------------------+     +------------------+     +-------------------+
    |  code_completion  | --> | context_manager  | <-- |  error_checker    |
    +-------------------+     +------------------+     +-------------------+
              |                       ^                        |
              v                       |                        v
    +-------------------+     +------------------+     +-------------------+
    | prompt_engineering| --> | knowledge_base   | <-- |  code_analyzer    |
    +-------------------+     +------------------+     +-------------------+
                                      ^
                                      |
                      +---------------+----------------+
                      |                                |
            +-------------------+             +------------------+
            | repo_integration  |             | system_monitor   |
            +-------------------+             +------------------+

模块开发指南
---------

如何开发新模块
^^^^^^^^^^^^

AIgo支持通过开发新模块来扩展功能。要创建新模块，请按照以下步骤：

1. 在 ``src/modules/`` 目录下创建新的Python包
2. 在包中创建一个主类，实现模块的核心功能
3. 在 ``src/modules/__init__.py`` 中导出新模块
4. 在 ``config/default/config.json`` 中添加模块配置

模块结构示例：

.. code-block:: text

    my_module/
    ├── __init__.py          # 导出主类和其他组件
    ├── my_module.py         # 主模块实现
    ├── utils.py             # 工具函数
    └── components/          # 子组件目录
        ├── __init__.py
        └── component1.py

模块接口要求
^^^^^^^^^^

每个AIgo模块应当实现以下基本接口：

.. code-block:: python

    class MyModule:
        def __init__(self, config=None):
            """初始化模块，接收配置参数"""
            self.config = config or {}
            
        def initialize(self):
            """初始化模块资源，返回是否成功"""
            return True
            
        def shutdown(self):
            """关闭模块，释放资源"""
            pass

测试与验证
^^^^^^^^

为模块编写测试是确保质量的重要步骤：

1. 在 ``tests/`` 目录下创建测试文件
2. 使用 pytest 编写单元测试和集成测试
3. 运行 ``pytest -xvs tests/test_my_module.py`` 执行测试 