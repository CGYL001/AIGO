代码分析模块
============

概述
----

代码分析模块提供代码质量评估、结构分析和优化建议功能。该模块使用静态分析技术，支持多种编程语言，可以帮助开发者提高代码质量和可维护性。

特性
----

* 代码复杂度分析（圈复杂度、嵌套深度）
* 代码结构识别（函数、类、导入等）
* 代码风格和质量检查
* 代码重复检测
* 优化建议生成

架构
----

代码分析模块由以下组件构成：

.. code-block:: text

    code_analysis/
    ├── __init__.py          # 模块入口
    ├── analyzer.py          # 主分析器类
    ├── metrics.py           # 度量计算器
    ├── structure.py         # 结构分析器
    ├── quality.py           # 质量分析器
    └── utils.py             # 通用工具函数

组件说明
-------

1. **CodeAnalyzer** - 主分析器类，协调其他组件
2. **MetricsCalculator** - 计算代码度量指标，如复杂度、行数等
3. **StructureAnalyzer** - 分析代码结构，识别函数和类
4. **QualityAnalyzer** - 评估代码质量和风格，提供改进建议

使用方法
-------

基本用法
^^^^^^^

.. code-block:: python

    from src.modules.code_analysis import CodeAnalyzer
    
    # 创建分析器实例
    analyzer = CodeAnalyzer()
    
    # 分析单个文件
    result = analyzer.analyze_file("path/to/file.py")
    
    # 输出结果
    print(f"文件复杂度: {result['metrics']['complexity']['cyclomatic']}")
    print(f"函数数量: {len(result['structure']['functions'])}")
    print(f"质量评分: {result['quality']['style']['score']}")
    
    # 获取改进建议
    suggestions = analyzer.suggest_improvements(result)
    for suggestion in suggestions:
        print(f"{suggestion['severity']}: {suggestion['message']}")

项目分析
^^^^^^^

.. code-block:: python

    # 分析整个项目
    project_result = analyzer.analyze_project("path/to/project")
    
    # 查看复杂度最高的文件
    top_complex = project_result["top_complex_files"]
    for file_info in top_complex:
        print(f"{file_info['file']}: 复杂度 {file_info['metrics']['complexity']['cyclomatic']}")

API参考
------

CodeAnalyzer类
^^^^^^^^^^^^^

.. py:class:: CodeAnalyzer(max_file_size=1_000_000)

   代码分析模块的主类，提供代码分析功能。

   :param max_file_size: 最大文件大小限制（字节）

   .. py:method:: analyze_file(file_path)

      分析单个文件。

      :param file_path: 要分析的文件路径
      :return: 包含分析结果的字典

   .. py:method:: analyze_project(project_dir, exclude_dirs=None)

      分析整个项目目录。

      :param project_dir: 项目目录路径
      :param exclude_dirs: 要排除的目录列表
      :return: 包含项目分析结果的字典

   .. py:method:: suggest_improvements(analysis_result)

      基于分析结果提供改进建议。

      :param analysis_result: 分析结果（由analyze_file或analyze_project方法返回）
      :return: 改进建议列表

示例
----

复杂度分析示例
^^^^^^^^^^^^

.. code-block:: python

    from src.modules.code_analysis import CodeAnalyzer
    
    analyzer = CodeAnalyzer()
    
    # 分析单个文件
    result = analyzer.analyze_file("main.py")
    
    # 提取复杂度信息
    complexity = result["metrics"]["complexity"]
    print(f"圈复杂度: {complexity['cyclomatic']}")
    print(f"嵌套深度: {complexity['nesting_depth']}")
    
    # 复杂度评级
    if complexity['cyclomatic'] <= 10:
        print("复杂度评级: 良好")
    elif complexity['cyclomatic'] <= 20:
        print("复杂度评级: 中等")
    else:
        print("复杂度评级: 复杂")

代码质量检查示例
^^^^^^^^^^^^^

.. code-block:: python

    # 质量检查
    quality = result["quality"]
    
    print(f"质量评分: {quality['style']['score']}/100")
    
    # 显示问题
    print("\n代码问题:")
    for issue in quality["issues"]:
        print(f"第{issue['line']}行: {issue['message']} ({issue['severity']})")
    
    # 显示改进建议
    print("\n改进建议:")
    for suggestion in quality["style"]["suggestions"]:
        print(f"- {suggestion}")

配置选项
-------

代码分析器提供多种配置选项，可以通过config.json文件进行设置：

.. code-block:: json

    {
      "code_analyzer": {
        "max_file_size": 1000000,
        "exclude_patterns": ["node_modules", "venv", "__pycache__"],
        "complexity_thresholds": {
          "function_lines": {
            "good": 30,
            "warning": 50,
            "critical": 100
          },
          "cyclomatic": {
            "good": 10,
            "warning": 20,
            "critical": 30
          }
        }
      }
    } 