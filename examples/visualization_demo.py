#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AIgo可视化功能示例脚本
展示AIgo可视化模块的基本用法
"""

import os
import sys
import time
import logging
import webbrowser
import numpy as np
from pathlib import Path

# 确保可以正确导入模块
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("visualization_demo")

# 导入模拟组件
from test_visualization import MockVisualizationManager as VisualizationManager
logger.info("已加载模拟可视化组件")

def demo_dashboard():
    """演示仪表盘可视化"""
    logger.info("演示仪表盘可视化...")
    
    # 创建可视化管理器
    vis_manager = VisualizationManager()
    
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
        "cpu_history": [40 + np.random.randint(-10, 10) for _ in range(10)],
        "memory_history": [60 + np.random.randint(-10, 10) for _ in range(10)],
        "disk_history": [75 + np.random.randint(-5, 5) for _ in range(10)]
    }
    
    # 创建系统监控面板
    try:
        system_monitor_path = vis_manager.dashboard.visualize(
            "system_monitor",
            system_data,
            width=1000,
            height=600,
            theme="light",
            title="系统监控示例"
        )
        logger.info(f"系统监控面板生成成功: {system_monitor_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{system_monitor_path}")
    except Exception as e:
        logger.error(f"系统监控面板生成失败: {e}")
    
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
    try:
        model_perf_path = vis_manager.dashboard.visualize(
            "model_performance",
            model_data,
            width=1000,
            height=600,
            theme="dark",
            title="模型性能示例"
        )
        logger.info(f"模型性能面板生成成功: {model_perf_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{model_perf_path}")
    except Exception as e:
        logger.error(f"模型性能面板生成失败: {e}")

def demo_structure():
    """演示结构可视化"""
    logger.info("演示结构可视化...")
    
    # 创建可视化管理器
    vis_manager = VisualizationManager()
    
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
    try:
        code_structure_path = vis_manager.structure.visualize(
            "code_structure",
            code_structure,
            width=1200,
            height=800,
            theme="light",
            title="代码结构示例"
        )
        logger.info(f"代码结构图生成成功: {code_structure_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{code_structure_path}")
    except Exception as e:
        logger.error(f"代码结构图生成失败: {e}")
    
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
    try:
        graph_path = vis_manager.structure.visualize(
            "knowledge_graph",
            knowledge_graph,
            width=1200,
            height=800,
            theme="dark",
            title="知识图谱示例"
        )
        logger.info(f"知识图谱生成成功: {graph_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{graph_path}")
    except Exception as e:
        logger.error(f"知识图谱生成失败: {e}")

def demo_realtime():
    """演示实时可视化"""
    logger.info("演示实时可视化...")
    
    # 创建可视化管理器
    vis_manager = VisualizationManager()
    
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
    try:
        attention_path = vis_manager.realtime.visualize(
            "attention_flow",
            attention_data,
            width=1000,
            height=600,
            theme="dark",
            title="注意力流动示例"
        )
        logger.info(f"注意力流动动画生成成功: {attention_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{attention_path}")
    except Exception as e:
        logger.error(f"注意力流动动画生成失败: {e}")
    
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
    try:
        animation_id = "task_progress_demo"
        progress_path = vis_manager.realtime.visualize(
            "progress_animation",
            progress_data,
            width=800,
            height=400,
            theme="light",
            title="任务进度示例",
            animation_id=animation_id
        )
        logger.info(f"进度动画生成成功: {progress_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{progress_path}")
        
        # 等待3秒后更新进度
        logger.info("等待3秒后更新进度...")
        time.sleep(3)
        
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
        
        # 更新可视化
        try:
            vis_manager.realtime.update(animation_id, updated_progress_data)
            logger.info("进度动画更新成功")
        except Exception as e:
            logger.error(f"进度动画更新失败: {e}")
            
    except Exception as e:
        logger.error(f"进度动画生成失败: {e}")

def demo_art():
    """演示数据艺术生成"""
    logger.info("演示数据艺术生成...")
    
    # 创建可视化管理器
    vis_manager = VisualizationManager()
    
    # 准备文本数据
    text_data = {
        "text": "AIgo是一个强大的AI助手平台，提供多种功能和工具，帮助开发者更高效地完成工作。",
        "settings": {
            "complexity": 0.8,
            "color_scheme": "rainbow"
        }
    }
    
    # 创建文本指纹
    try:
        fingerprint_path = vis_manager.art_generator.visualize(
            "text_fingerprint",
            text_data,
            width=800,
            height=800,
            theme="dark",
            title="文本指纹示例"
        )
        logger.info(f"文本指纹生成成功: {fingerprint_path}")
        
        # 打开生成的图片文件
        webbrowser.open(f"file://{fingerprint_path}")
    except Exception as e:
        logger.error(f"文本指纹生成失败: {e}")
    
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
    try:
        galaxy_path = vis_manager.art_generator.visualize(
            "code_galaxy",
            code_data,
            width=1000,
            height=1000,
            theme="dark",
            title="代码星系示例"
        )
        logger.info(f"代码星系生成成功: {galaxy_path}")
        
        # 打开生成的图片文件
        webbrowser.open(f"file://{galaxy_path}")
    except Exception as e:
        logger.error(f"代码星系生成失败: {e}")

def main():
    """主函数"""
    logger.info("开始AIgo可视化功能演示...")
    
    # 演示仪表盘可视化
    demo_dashboard()
    
    # 演示结构可视化
    demo_structure()
    
    # 演示实时可视化
    demo_realtime()
    
    # 演示数据艺术生成
    demo_art()
    
    logger.info("AIgo可视化功能演示完成")

if __name__ == "__main__":
    main() 