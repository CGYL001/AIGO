#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
可视化模块演示脚本 - 不依赖MCP服务器

这个脚本展示了如何使用可视化模块的模拟实现，而不需要MCP服务器运行。
它使用MockVisualizationManager及其组件来模拟各种可视化功能。
"""

import time
import random
import os
import json
import argparse
from pathlib import Path
from test_visualization import (
    MockVisualizationManager, 
    MockDashboard,
    MockStructureVisualizer,
    MockRealtimeVisualizer,
    MockDataArtGenerator
)

# 默认配置
DEFAULT_CONFIG = {
    "output": {
        "save_html": True,
        "save_image": True,
        "output_dir": "output",
        "image_dir": "output/images"
    },
    "dashboard": {
        "width": 800,
        "height": 600,
        "theme": "light"
    },
    "structure": {
        "width": 1000,
        "height": 800,
        "theme": "dark"
    },
    "realtime": {
        "width": 800,
        "height": 600,
        "theme": "light",
        "animation_speed": 0.2
    },
    "art": {
        "width": 800,
        "height": 800,
        "theme": "dark"
    }
}

def load_config(config_file=None):
    """
    加载配置文件
    
    Args:
        config_file: 配置文件路径，如果为None，则使用默认配置
    
    Returns:
        dict: 配置字典
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # 合并配置
            for section, values in user_config.items():
                if section in config:
                    config[section].update(values)
                else:
                    config[section] = values
            
            print(f"已加载配置文件：{config_file}")
        except Exception as e:
            print(f"加载配置文件时出错：{e}")
    
    return config

def save_default_config(config_file):
    """
    保存默认配置到文件
    
    Args:
        config_file: 配置文件路径
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        print(f"已保存默认配置到：{config_file}")
    except Exception as e:
        print(f"保存默认配置时出错：{e}")

# 添加保存可视化结果的函数
def save_visualization(html_path, output_dir=None, save_name=None):
    """
    保存可视化结果到指定目录
    
    Args:
        html_path: HTML文件路径
        output_dir: 输出目录，如果为None，则使用当前目录下的output目录
        save_name: 保存的文件名，如果为None，则使用原文件名
    
    Returns:
        str: 保存后的文件路径
    """
    if not os.path.exists(html_path):
        print(f"错误：文件不存在 - {html_path}")
        return None
    
    # 创建输出目录
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "output")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取文件名
    if save_name is None:
        save_name = os.path.basename(html_path)
    
    # 确保文件名有.html后缀
    if not save_name.endswith(".html"):
        save_name += ".html"
    
    # 构建目标路径
    target_path = os.path.join(output_dir, save_name)
    
    # 复制文件（使用二进制模式）
    with open(html_path, "rb") as src_file:
        content = src_file.read()
        
    with open(target_path, "wb") as dst_file:
        dst_file.write(content)
    
    print(f"可视化结果已保存到：{target_path}")
    return target_path

# 添加保存图像的函数
def save_visualization_as_image(html_path, output_dir=None, save_name=None):
    """
    将HTML可视化结果保存为图像（模拟实现）
    
    Args:
        html_path: HTML文件路径
        output_dir: 输出目录，如果为None，则使用当前目录下的output/images目录
        save_name: 保存的文件名，如果为None，则使用原文件名
    
    Returns:
        str: 保存后的文件路径
    """
    if not os.path.exists(html_path):
        print(f"错误：文件不存在 - {html_path}")
        return None
    
    # 创建输出目录
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "output", "images")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取文件名
    if save_name is None:
        save_name = os.path.basename(html_path).replace(".html", ".png")
    
    # 确保文件名有.png后缀
    if not save_name.endswith(".png"):
        save_name += ".png"
    
    # 构建目标路径
    target_path = os.path.join(output_dir, save_name)
    
    # 模拟将HTML转换为图像
    print(f"模拟将HTML转换为图像：{html_path} -> {target_path}")
    
    # 创建一个简单的模拟图像文件
    with open(target_path, "w", encoding="utf-8") as img_file:
        img_file.write(f"This is a simulated image file for {os.path.basename(html_path)}")
    
    print(f"可视化图像已保存到：{target_path}")
    return target_path

def demo_dashboard(vis_manager, output_dir=None, config=None):
    """演示仪表盘可视化功能"""
    print("\n===== 仪表盘可视化演示 =====")
    
    # 使用配置
    if config is None:
        config = DEFAULT_CONFIG
    
    dashboard_config = config.get("dashboard", {})
    output_config = config.get("output", {})
    
    # 模拟系统监控指标
    system_metrics = {
        "cpu_usage": 45.2,
        "memory_usage": 3.7,
        "disk_usage": 67.8,
        "network_in": 2.3,
        "network_out": 1.5
    }
    
    # 模拟模型性能指标
    model_metrics = {
        "throughput": 12.5,
        "latency": 237,
        "error_rate": 0.05,
        "success_rate": 0.95
    }
    
    # 创建仪表盘可视化
    print("创建系统监控仪表盘...")
    dashboard_id = vis_manager.dashboard.visualize(
        "system_monitor",
        system_metrics,
        title="系统监控仪表盘",
        width=dashboard_config.get("width", 800),
        height=dashboard_config.get("height", 600),
        theme=dashboard_config.get("theme", "light")
    )
    print(f"系统监控仪表盘已创建，ID: {dashboard_id}")
    
    # 保存可视化结果
    if output_dir:
        if output_config.get("save_html", True):
            save_visualization(dashboard_id, output_dir, "system_monitor.html")
        if output_config.get("save_image", True):
            save_visualization_as_image(dashboard_id, output_config.get("image_dir", output_dir), "system_monitor.png")
    
    print("\n创建模型性能仪表盘...")
    perf_id = vis_manager.dashboard.visualize(
        "model_performance",
        model_metrics,
        title="模型性能仪表盘",
        width=dashboard_config.get("width", 800),
        height=dashboard_config.get("height", 600),
        theme=dashboard_config.get("theme", "light")
    )
    print(f"模型性能仪表盘已创建，ID: {perf_id}")
    
    # 保存可视化结果
    if output_dir:
        if output_config.get("save_html", True):
            save_visualization(perf_id, output_dir, "model_performance.html")
        if output_config.get("save_image", True):
            save_visualization_as_image(perf_id, output_config.get("image_dir", output_dir), "model_performance.png")
    
    print("\n创建资源使用趋势图...")
    trend_data = {
        "time": list(range(10)),
        "cpu": [random.uniform(30, 60) for _ in range(10)],
        "memory": [random.uniform(2.5, 4.5) for _ in range(10)]
    }
    trend_id = vis_manager.dashboard.visualize(
        "resource_trend",
        trend_data,
        title="资源使用趋势",
        width=dashboard_config.get("width", 800),
        height=dashboard_config.get("height", 600),
        theme=dashboard_config.get("theme", "light")
    )
    print(f"资源使用趋势图已创建，ID: {trend_id}")
    
    # 保存可视化结果
    if output_dir:
        if output_config.get("save_html", True):
            save_visualization(trend_id, output_dir, "resource_trend.html")
        if output_config.get("save_image", True):
            save_visualization_as_image(trend_id, output_config.get("image_dir", output_dir), "resource_trend.png")
    
    # 在实际应用中，这些ID可以用来更新或删除可视化
    print("\n在实际MCP环境中，可以使用这些ID来更新或删除可视化")
    
    return [dashboard_id, perf_id, trend_id]

def demo_structure_visualizer(vis_manager, output_dir=None):
    """演示结构可视化器功能"""
    print("\n===== 结构可视化演示 =====")
    
    # 模拟代码结构数据
    code_structure = {
        "name": "project_root",
        "type": "directory",
        "children": [
            {
                "name": "src",
                "type": "directory",
                "children": [
                    {"name": "main.py", "type": "file", "size": 1024},
                    {"name": "utils.py", "type": "file", "size": 2048},
                    {
                        "name": "modules",
                        "type": "directory",
                        "children": [
                            {"name": "module1.py", "type": "file", "size": 512},
                            {"name": "module2.py", "type": "file", "size": 768}
                        ]
                    }
                ]
            },
            {"name": "README.md", "type": "file", "size": 256}
        ]
    }
    
    # 模拟模型架构数据
    model_architecture = {
        "name": "Sequential Model",
        "layers": [
            {"type": "Input", "shape": [28, 28, 1]},
            {"type": "Conv2D", "filters": 32, "kernel_size": 3},
            {"type": "MaxPooling2D", "pool_size": 2},
            {"type": "Flatten"},
            {"type": "Dense", "units": 128, "activation": "relu"},
            {"type": "Dropout", "rate": 0.5},
            {"type": "Dense", "units": 10, "activation": "softmax"}
        ]
    }
    
    # 创建代码结构可视化
    print("创建代码结构可视化...")
    code_viz_id = vis_manager.structure.visualize(
        "code_structure",
        code_structure,
        title="代码结构可视化"
    )
    print(f"代码结构可视化已创建，ID: {code_viz_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(code_viz_id, output_dir, "code_structure.html")
        save_visualization_as_image(code_viz_id, output_dir, "code_structure.png")
    
    print("\n创建模型架构可视化...")
    model_viz_id = vis_manager.structure.visualize(
        "model_architecture",
        model_architecture,
        title="模型架构可视化"
    )
    print(f"模型架构可视化已创建，ID: {model_viz_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(model_viz_id, output_dir, "model_architecture.html")
        save_visualization_as_image(model_viz_id, output_dir, "model_architecture.png")
    
    print("\n创建知识图谱可视化...")
    knowledge_graph = {
        "nodes": [
            {"id": "1", "label": "Python", "group": 1},
            {"id": "2", "label": "Machine Learning", "group": 2},
            {"id": "3", "label": "Deep Learning", "group": 2},
            {"id": "4", "label": "TensorFlow", "group": 3},
            {"id": "5", "label": "PyTorch", "group": 3}
        ],
        "edges": [
            {"from": "1", "to": "2", "label": "used in"},
            {"from": "2", "to": "3", "label": "includes"},
            {"from": "3", "to": "4", "label": "implemented by"},
            {"from": "3", "to": "5", "label": "implemented by"},
            {"from": "1", "to": "4", "label": "supports"},
            {"from": "1", "to": "5", "label": "supports"}
        ]
    }
    knowledge_viz_id = vis_manager.structure.visualize(
        "knowledge_graph",
        knowledge_graph,
        title="知识图谱可视化"
    )
    print(f"知识图谱可视化已创建，ID: {knowledge_viz_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(knowledge_viz_id, output_dir, "knowledge_graph.html")
        save_visualization_as_image(knowledge_viz_id, output_dir, "knowledge_graph.png")
    
    return [code_viz_id, model_viz_id, knowledge_viz_id]

def demo_realtime_visualizer(vis_manager, output_dir=None):
    """演示实时可视化器功能"""
    print("\n===== 实时可视化演示 =====")
    
    # 创建模型流程动画
    print("创建模型流程动画...")
    flow_data = [
        {"step": "输入数据", "status": "completed"},
        {"step": "预处理", "status": "completed"},
        {"step": "特征提取", "status": "in_progress"},
        {"step": "模型推理", "status": "pending"},
        {"step": "后处理", "status": "pending"},
        {"step": "输出结果", "status": "pending"}
    ]
    flow_id = vis_manager.realtime.visualize(
        "model_flow_animation",
        flow_data,
        title="模型流程动画"
    )
    print(f"模型流程动画已创建，ID: {flow_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(flow_id, output_dir, "model_flow_animation.html")
        save_visualization_as_image(flow_id, output_dir, "model_flow_animation.png")
    
    # 模拟更新动画
    print("\n更新模型流程动画...")
    updated_flow_data = [
        {"step": "输入数据", "status": "completed"},
        {"step": "预处理", "status": "completed"},
        {"step": "特征提取", "status": "completed"},
        {"step": "模型推理", "status": "in_progress"},
        {"step": "后处理", "status": "pending"},
        {"step": "输出结果", "status": "pending"}
    ]
    vis_manager.realtime.update(flow_id, updated_flow_data)
    print("模型流程动画已更新")
    
    # 保存更新后的可视化结果
    if output_dir:
        save_visualization(flow_id, output_dir, "model_flow_animation_updated.html")
        save_visualization_as_image(flow_id, output_dir, "model_flow_animation_updated.png")
    
    # 创建计算热图
    print("\n创建计算热图...")
    heatmap_data = []
    for i in range(10):
        row = []
        for j in range(10):
            row.append(random.uniform(0, 1))
        heatmap_data.append(row)
    
    heatmap_id = vis_manager.realtime.visualize(
        "computation_heatmap",
        heatmap_data,
        title="计算热图"
    )
    print(f"计算热图已创建，ID: {heatmap_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(heatmap_id, output_dir, "computation_heatmap.html")
        save_visualization_as_image(heatmap_id, output_dir, "computation_heatmap.png")
    
    # 创建进度动画
    print("\n创建进度动画...")
    progress_data = {
        "task": "模型训练",
        "progress": 0
    }
    progress_id = vis_manager.realtime.visualize(
        "progress_animation",
        progress_data,
        title="训练进度"
    )
    print(f"进度动画已创建，ID: {progress_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(progress_id, output_dir, "progress_animation_0.html")
        save_visualization_as_image(progress_id, output_dir, "progress_animation_0.png")
    
    # 模拟进度更新
    final_progress_id = progress_id
    for i in range(1, 11):
        progress = i * 10
        print(f"更新进度: {progress}%")
        vis_manager.realtime.update(progress_id, {"progress": progress})
        time.sleep(0.2)  # 模拟延迟
        
        # 每次更新保存一个快照（仅保存最后一个状态）
        if i == 10 and output_dir:
            save_visualization(progress_id, output_dir, "progress_animation_100.html")
            save_visualization_as_image(progress_id, output_dir, "progress_animation_100.png")
    
    return [flow_id, heatmap_id, final_progress_id]

def demo_data_art_generator(vis_manager, output_dir=None):
    """演示数据艺术生成器功能"""
    print("\n===== 数据艺术生成演示 =====")
    
    # 创建文本指纹
    print("创建文本指纹...")
    text_data = {
        "text": "这是一段示例文本，用于生成文本指纹可视化。",
        "settings": {
            "complexity": 0.8,
            "color_scheme": "rainbow"
        }
    }
    fingerprint_id = vis_manager.art_generator.visualize(
        "text_fingerprint",
        text_data,
        title="文本指纹"
    )
    print(f"文本指纹已创建，ID: {fingerprint_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(fingerprint_id, output_dir, "text_fingerprint.html")
        save_visualization_as_image(fingerprint_id, output_dir, "text_fingerprint.png")
    
    # 创建代码星系
    print("\n创建代码星系...")
    code_files = [
        {"name": "main.py", "size": 1024, "changes": 15},
        {"name": "utils.py", "size": 2048, "changes": 7},
        {"name": "config.py", "size": 512, "changes": 3},
        {"name": "models/user.py", "size": 768, "changes": 10},
        {"name": "models/product.py", "size": 640, "changes": 5}
    ]
    galaxy_id = vis_manager.art_generator.visualize(
        "code_galaxy",
        code_files,
        title="代码星系"
    )
    print(f"代码星系已创建，ID: {galaxy_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(galaxy_id, output_dir, "code_galaxy.html")
        save_visualization_as_image(galaxy_id, output_dir, "code_galaxy.png")
    
    # 创建数据流艺术
    print("\n创建数据流艺术...")
    data_points = [random.uniform(-1, 1) for _ in range(100)]
    flow_art_id = vis_manager.art_generator.visualize(
        "data_flow_art",
        data_points,
        title="数据流艺术"
    )
    print(f"数据流艺术已创建，ID: {flow_art_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(flow_art_id, output_dir, "data_flow_art.html")
        save_visualization_as_image(flow_art_id, output_dir, "data_flow_art.png")
    
    # 创建AI思维地图
    print("\n创建AI思维地图...")
    thoughts = [
        {"thought": "分析问题", "connections": [1, 2]},
        {"thought": "查找相关信息", "connections": [3]},
        {"thought": "考虑解决方案", "connections": [3, 4]},
        {"thought": "评估方案", "connections": [4]},
        {"thought": "生成最终答案", "connections": []}
    ]
    mindmap_id = vis_manager.art_generator.visualize(
        "ai_mindmap",
        thoughts,
        title="AI思维地图"
    )
    print(f"AI思维地图已创建，ID: {mindmap_id}")
    
    # 保存可视化结果
    if output_dir:
        save_visualization(mindmap_id, output_dir, "ai_mindmap.html")
        save_visualization_as_image(mindmap_id, output_dir, "ai_mindmap.png")
    
    return [fingerprint_id, galaxy_id, flow_art_id, mindmap_id]

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="可视化模块演示（不依赖MCP服务器）")
    parser.add_argument("--output-dir", "-o", type=str, default=None,
                        help="可视化结果输出目录")
    parser.add_argument("--save", "-s", action="store_true",
                        help="是否保存可视化结果")
    parser.add_argument("--demo", "-d", type=str, choices=["all", "dashboard", "structure", "realtime", "art"],
                        default="all", help="要运行的演示类型")
    parser.add_argument("--config", "-c", type=str, default=None,
                        help="配置文件路径")
    parser.add_argument("--generate-config", "-g", type=str, default=None,
                        help="生成默认配置文件")
    args = parser.parse_args()
    
    # 生成默认配置文件
    if args.generate_config:
        save_default_config(args.generate_config)
        return
    
    # 加载配置
    config = load_config(args.config)
    
    # 确定输出目录
    output_dir = args.output_dir if args.output_dir else config["output"]["output_dir"] if args.save else None
    
    print("=== 可视化模块演示 (不依赖MCP服务器) ===")
    print("注意: 这个演示使用模拟实现，实际可视化效果将在集成到MCP后呈现")
    
    if args.config:
        print(f"使用配置文件：{args.config}")
    
    if output_dir:
        print(f"可视化结果将保存到：{os.path.abspath(output_dir)}")
    
    # 创建可视化管理器
    vis_manager = MockVisualizationManager()
    
    # 根据选择运行不同的演示
    results = {}
    
    if args.demo in ["all", "dashboard"]:
        results["dashboard"] = demo_dashboard(vis_manager, output_dir, config)
    
    if args.demo in ["all", "structure"]:
        results["structure"] = demo_structure_visualizer(vis_manager, output_dir)
    
    if args.demo in ["all", "realtime"]:
        results["realtime"] = demo_realtime_visualizer(vis_manager, output_dir)
    
    if args.demo in ["all", "art"]:
        results["art"] = demo_data_art_generator(vis_manager, output_dir)
    
    print("\n=== 演示完成 ===")
    
    # 如果保存了结果，显示摘要
    if output_dir:
        print(f"\n已生成的可视化文件保存在：{os.path.abspath(output_dir)}")
        print(f"生成的HTML文件数量：{sum(len(ids) for ids in results.values())}")
    
    print("在实际MCP环境中，这些可视化将通过Web界面或IDE插件呈现")
    print("要集成到MCP，请参考docs/visualization_guide.md中的说明")

if __name__ == "__main__":
    main() 