# AIgo 可视化功能使用指南

AIgo的可视化模块提供了丰富的数据可视化功能，帮助您更直观地理解和分析模型性能、系统状态和数据结构。本指南将介绍如何使用这些可视化功能。

## 目录

1. [可视化模块概述](#可视化模块概述)
2. [基础使用方法](#基础使用方法)
3. [仪表盘可视化](#仪表盘可视化)
4. [结构可视化](#结构可视化)
5. [实时可视化](#实时可视化)
6. [数据艺术生成](#数据艺术生成)
7. [与其他模块集成](#与其他模块集成)
8. [常见问题解答](#常见问题解答)

## 可视化模块概述

AIgo的可视化模块由以下主要组件组成：

- **仪表盘可视化器 (Dashboard)**: 提供系统监控、模型性能等指标的可视化展示
- **结构可视化器 (StructureVisualizer)**: 用于展示代码结构、模型架构、知识图谱等静态结构
- **实时可视化器 (RealtimeVisualizer)**: 提供动态过程的实时可视化，如模型训练进度、注意力流动等
- **数据艺术生成器 (DataArtGenerator)**: 将数据转换为艺术化的视觉表现形式

## 基础使用方法

### 导入可视化模块

```python
from AIGO.modules.visualization import VisualizationManager

# 创建可视化管理器
vis_manager = VisualizationManager()
```

### 检查可用组件

```python
# 获取所有可用的可视化组件
components = vis_manager.get_available_components()
print(f"可用的可视化组件: {', '.join(components.keys())}")

# 检查仪表盘组件支持的可视化类型
if "dashboard" in components:
    dashboard_types = vis_manager.dashboard.get_available_types()
    print(f"仪表盘支持的可视化类型: {', '.join(dashboard_types.keys())}")
```

### 创建基本可视化

```python
# 创建系统监控仪表盘
dashboard_path = vis_manager.dashboard.visualize(
    "system_monitor",
    data={...},  # 系统监控数据
    width=1000,
    height=600,
    theme="light",
    title="系统监控"
)

# 打开生成的HTML文件
import webbrowser
webbrowser.open(f"file://{dashboard_path}")
```

## 仪表盘可视化

仪表盘可视化器提供了多种类型的可视化，用于展示系统状态和性能指标。

### 系统监控面板

```python
# 准备系统监控数据
system_data = {
    "metrics": {
        "cpu_usage": 45.7,
        "memory_usage": 62.3,
        "disk_usage": 78.1,
        "network_rx": 5.2,
        "network_tx": 2.1
    },
    "timestamps": [time.time() - i * 60 for i in range(10)],
    "cpu_history": [40, 42, 45, 43, 47, 44, 46, 45, 48, 45],
    "memory_history": [60, 62, 61, 63, 65, 64, 62, 63, 65, 62],
    "disk_history": [75, 75, 76, 76, 77, 77, 78, 78, 79, 78]
}

# 创建系统监控面板
dashboard_path = vis_manager.dashboard.visualize(
    "system_monitor",
    system_data,
    width=1000,
    height=600,
    theme="light",
    title="系统监控"
)
```

### 模型性能面板

```python
# 准备模型性能数据
model_data = {
    "models": [
        {
            "name": "llama2-7b",
            "latency": 120,
            "memory": 14000,
            "accuracy": 87.5
        },
        {
            "name": "llama2-7b-optimized",
            "latency": 75,
            "memory": 8500,
            "accuracy": 86.2
        }
    ],
    "metrics": {
        "latency_reduction": 37.5,
        "memory_reduction": 39.3,
        "accuracy_loss": 1.3
    }
}

# 创建模型性能面板
perf_path = vis_manager.dashboard.visualize(
    "model_performance",
    model_data,
    width=1000,
    height=600,
    theme="dark",
    title="模型性能比较"
)
```

### 多指标综合面板

```python
# 准备多指标数据
multi_metric_data = {
    "title": "模型优化性能对比",
    "categories": ["原始模型", "剪枝优化", "量化优化", "知识蒸馏"],
    "metrics": [
        {
            "name": "推理延迟(ms)",
            "values": [100, 85, 65, 55],
            "lower_is_better": True
        },
        {
            "name": "内存使用(MB)",
            "values": [500, 400, 300, 250],
            "lower_is_better": True
        },
        {
            "name": "准确率(%)",
            "values": [95, 93, 92, 90],
            "lower_is_better": False
        },
        {
            "name": "模型大小(MB)",
            "values": [350, 280, 200, 150],
            "lower_is_better": True
        }
    ]
}

# 创建多指标综合面板
multi_path = vis_manager.dashboard.visualize(
    "multi_metric",
    multi_metric_data,
    width=1000,
    height=600,
    theme="light",
    title="模型优化性能对比"
)
```

## 结构可视化

结构可视化器用于展示各类静态结构，如代码结构、模型架构等。

### 代码结构图

```python
# 准备代码结构数据
code_structure = {
    "name": "AIgo",
    "type": "project",
    "children": [
        {
            "name": "modules",
            "type": "directory",
            "children": [
                {"name": "visualization", "type": "module", "size": 120},
                {"name": "integration", "type": "module", "size": 80},
                {"name": "knowledge_base", "type": "module", "size": 150},
                {"name": "system_monitor", "type": "module", "size": 90}
            ]
        },
        {
            "name": "utils",
            "type": "directory",
            "children": [
                {"name": "config", "type": "module", "size": 50},
                {"name": "logger", "type": "module", "size": 30}
            ]
        },
        {"name": "start_assistant.py", "type": "file", "size": 200}
    ]
}

# 创建代码结构图
structure_path = vis_manager.structure.visualize(
    "code_structure",
    code_structure,
    width=1200,
    height=800,
    theme="light",
    title="代码结构图"
)
```

### 模型架构图

```python
# 准备模型架构数据
model_structure = {
    "name": "llama2-7b",
    "type": "model",
    "children": [
        {
            "name": "embedding",
            "type": "layer",
            "size": 100
        },
        {
            "name": "transformer",
            "type": "block",
            "children": [
                {"name": "layer_1", "type": "layer", "size": 200},
                {"name": "layer_2", "type": "layer", "size": 200},
                {"name": "layer_3", "type": "layer", "size": 200}
            ]
        },
        {
            "name": "output",
            "type": "layer",
            "size": 100
        }
    ]
}

# 创建模型架构图
model_path = vis_manager.structure.visualize(
    "model_structure",
    model_structure,
    width=1200,
    height=800,
    theme="dark",
    title="模型架构图: llama2-7b"
)
```

### 知识图谱

```python
# 准备知识图谱数据
knowledge_graph = {
    "nodes": [
        {"id": "concept1", "name": "人工智能", "type": "concept"},
        {"id": "concept2", "name": "机器学习", "type": "concept"},
        {"id": "concept3", "name": "深度学习", "type": "concept"},
        {"id": "concept4", "name": "神经网络", "type": "concept"},
        {"id": "concept5", "name": "自然语言处理", "type": "concept"},
        {"id": "concept6", "name": "计算机视觉", "type": "concept"}
    ],
    "edges": [
        {"from": "concept1", "to": "concept2", "type": "includes"},
        {"from": "concept1", "to": "concept5", "type": "includes"},
        {"from": "concept1", "to": "concept6", "type": "includes"},
        {"from": "concept2", "to": "concept3", "type": "includes"},
        {"from": "concept3", "to": "concept4", "type": "uses"}
    ]
}

# 创建知识图谱
graph_path = vis_manager.structure.visualize(
    "knowledge_graph",
    knowledge_graph,
    width=1200,
    height=800,
    theme="dark",
    title="知识图谱"
)
```

## 实时可视化

实时可视化器提供了动态过程的可视化展示，如模型训练进度、注意力流动等。

### 注意力流动动画

```python
# 准备注意力流动数据
attention_data = {
    "tokens": ["[START]", "今天", "天气", "真", "不错", "。", "[END]"],
    "attention_weights": [
        # 帧1
        [
            [0.8, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0],
            [0.4, 0.5, 0.1, 0.0, 0.0, 0.0, 0.0],
            [0.2, 0.3, 0.5, 0.0, 0.0, 0.0, 0.0],
            [0.1, 0.2, 0.3, 0.4, 0.0, 0.0, 0.0],
            [0.1, 0.1, 0.2, 0.2, 0.4, 0.0, 0.0],
            [0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.0],
            [0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.3]
        ],
        # 帧2
        [
            [0.7, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0],
            [0.3, 0.6, 0.1, 0.0, 0.0, 0.0, 0.0],
            [0.1, 0.2, 0.7, 0.0, 0.0, 0.0, 0.0],
            [0.1, 0.1, 0.2, 0.6, 0.0, 0.0, 0.0],
            [0.0, 0.1, 0.1, 0.2, 0.6, 0.0, 0.0],
            [0.0, 0.0, 0.1, 0.1, 0.2, 0.6, 0.0],
            [0.0, 0.0, 0.0, 0.1, 0.1, 0.2, 0.6]
        ]
    ]
}

# 创建注意力流动动画
attention_path = vis_manager.realtime.visualize(
    "attention_flow",
    attention_data,
    width=1000,
    height=600,
    theme="dark",
    title="注意力流动动画"
)
```

### 进度动画

```python
# 准备进度数据
progress_data = {
    "steps": [
        {"name": "数据加载", "status": "完成", "progress": 100},
        {"name": "预处理", "status": "完成", "progress": 100},
        {"name": "模型推理", "status": "进行中", "progress": 60},
        {"name": "后处理", "status": "等待中", "progress": 0},
        {"name": "结果保存", "status": "等待中", "progress": 0}
    ],
    "current_step": 2
}

# 创建进度动画
animation_id = "task_progress_1"
progress_path = vis_manager.realtime.visualize(
    "progress_animation",
    progress_data,
    width=800,
    height=400,
    theme="light",
    title="任务进度",
    animation_id=animation_id
)

# 更新进度
updated_progress_data = {
    "steps": [
        {"name": "数据加载", "status": "完成", "progress": 100},
        {"name": "预处理", "status": "完成", "progress": 100},
        {"name": "模型推理", "status": "完成", "progress": 100},
        {"name": "后处理", "status": "进行中", "progress": 30},
        {"name": "结果保存", "status": "等待中", "progress": 0}
    ],
    "current_step": 3
}
vis_manager.realtime.update(animation_id, updated_progress_data)
```

## 数据艺术生成

数据艺术生成器可以将数据转换为艺术化的视觉表现形式。

### 文本指纹

```python
# 准备文本数据
text_data = {
    "text": "AIgo是一个强大的AI助手平台，提供多种功能和工具，帮助开发者更高效地完成工作。",
    "settings": {
        "complexity": 0.8,
        "color_scheme": "rainbow"
    }
}

# 创建文本指纹
fingerprint_path = vis_manager.art_generator.visualize(
    "text_fingerprint",
    text_data,
    width=800,
    height=800,
    theme="dark",
    title="文本指纹"
)
```

### 代码星系

```python
# 准备代码数据
code_data = {
    "files": [
        {"path": "AIGO/modules/visualization/__init__.py", "size": 3600, "type": "python"},
        {"path": "AIGO/modules/visualization/dashboard.py", "size": 28000, "type": "python"},
        {"path": "AIGO/modules/visualization/structure.py", "size": 32000, "type": "python"},
        {"path": "AIGO/modules/visualization/realtime.py", "size": 30000, "type": "python"},
        {"path": "AIGO/modules/visualization/art.py", "size": 24000, "type": "python"}
    ],
    "settings": {
        "galaxy_type": "spiral",
        "color_by": "file_type"
    }
}

# 创建代码星系
galaxy_path = vis_manager.art_generator.visualize(
    "code_galaxy",
    code_data,
    width=1000,
    height=1000,
    theme="dark",
    title="代码星系"
)
```

## 与其他模块集成

可视化模块可以与AIgo的其他模块无缝集成，例如模型优化、系统监控等。

### 系统监控集成

```python
from AIGO.modules.system_monitor import SystemMonitor

# 创建系统监控器
system_monitor = SystemMonitor()

# 设置可视化管理器
system_monitor.set_visualization_manager(vis_manager)

# 收集系统指标
system_monitor.collect_metrics()

# 可视化系统指标
dashboard_path = system_monitor.visualize_metrics()
```

### 模型优化集成

```python
from AIGO.modules.integration import FeatureIntegrator

# 创建特性集成器
integrator = FeatureIntegrator()
integrator.set_visualization_manager(vis_manager)

# 集成模型优化特性
results = integrator.integrate_features(["model_optimization"])

if "model_optimization" in integrator.enabled_features:
    # 获取模型优化集成器
    optimizer = integrator.get_feature_integrator("model_optimization")
    
    # 优化模型并生成可视化
    result = optimizer.optimize_model_with_visualization(
        model_name="llama2-7b",
        optimization_type="quantization"
    )
    
    # 获取生成的可视化路径
    structure_vis = result.get("structure_visualization")
    performance_vis = result.get("performance_visualization")
    artistic_vis = result.get("artistic_visualization")
```

## 常见问题解答

### Q: 可视化模块需要哪些依赖库？

A: 可视化模块主要依赖以下库：
- matplotlib: 用于基础图表和静态可视化
- plotly: 用于交互式仪表盘和复杂可视化
- PIL (Pillow): 用于图像处理和某些数据艺术功能
- networkx: 用于图网络可视化
- graphviz: 用于流程图和结构图

您可以通过以下命令安装这些依赖：
```bash
pip install matplotlib plotly pillow networkx graphviz
```

### Q: 如何自定义可视化主题？

A: 所有可视化组件均支持以下主题：
- light: 适合浅色背景的明亮主题
- dark: 适合深色背景的暗黑主题
- blue: 蓝色基调的主题
- contrast: 高对比度主题，适合演示

您可以通过设置`theme`参数来选择主题：
```python
vis_manager.dashboard.visualize(
    "system_monitor",
    data,
    theme="dark"  # 使用暗黑主题
)
```

### Q: 可视化结果保存在哪里？

A: 默认情况下，可视化结果保存在临时目录中。每个可视化函数都会返回生成文件的路径，您可以使用该路径访问或移动文件。

如果您希望指定保存路径，可以使用`output_path`参数：
```python
vis_manager.dashboard.visualize(
    "system_monitor",
    data,
    output_path="/path/to/save/dashboard.html"
)
```

### Q: 如何在Web应用中嵌入可视化内容？

A: 对于生成HTML的可视化（如plotly图表），您可以将HTML文件内容嵌入到Web应用中。对于图像类型的可视化，您可以将图像文件作为静态资源提供。

此外，可视化模块还提供了`get_embed_code`方法，用于获取可嵌入的HTML代码：
```python
embed_code = vis_manager.dashboard.get_embed_code(
    "system_monitor",
    data
)
```

### Q: 如何创建自定义可视化？

A: 您可以通过扩展现有可视化组件或创建新的可视化组件来实现自定义可视化。请参考`AIGO/modules/visualization/README.md`中的开发指南。 