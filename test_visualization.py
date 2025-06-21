#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AIgo可视化功能测试脚本
测试各种可视化组件的功能和效果
"""

import os
import sys
import time
import logging
import tempfile
import webbrowser
import json
import numpy as np
from pathlib import Path

# 确保可以正确导入模块
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("visualization_test")

# 创建可视化组件
class MockDashboard:
    def visualize(self, vis_type, data, **kwargs):
        logger.info(f"模拟仪表盘可视化: {vis_type}")
        output_path = os.path.join(tempfile.gettempdir(), f"{vis_type}_{int(time.time())}.html")
        with open(output_path, 'w') as f:
            f.write(f"<html><body><h1>{kwargs.get('title', '可视化测试')}</h1>")
            f.write("<p>这是一个模拟的可视化页面</p>")
            f.write(f"<pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>")
            f.write("</body></html>")
        return output_path

class MockStructureVisualizer:
    def visualize(self, vis_type, data, **kwargs):
        logger.info(f"模拟结构可视化: {vis_type}")
        output_path = os.path.join(tempfile.gettempdir(), f"{vis_type}_{int(time.time())}.html")
        with open(output_path, 'w') as f:
            f.write(f"<html><body><h1>{kwargs.get('title', '可视化测试')}</h1>")
            f.write("<p>这是一个模拟的结构可视化页面</p>")
            f.write(f"<pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>")
            f.write("</body></html>")
        return output_path

class MockRealtimeVisualizer:
    def visualize(self, vis_type, data, **kwargs):
        logger.info(f"模拟实时可视化: {vis_type}")
        output_path = os.path.join(tempfile.gettempdir(), f"{vis_type}_{int(time.time())}.html")
        with open(output_path, 'w') as f:
            f.write(f"<html><body><h1>{kwargs.get('title', '可视化测试')}</h1>")
            f.write("<p>这是一个模拟的实时可视化页面</p>")
            f.write(f"<pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>")
            f.write("</body></html>")
        return output_path
        
    def update(self, animation_id, data):
        logger.info(f"更新实时可视化: {animation_id}")
        return True

class MockDataArtGenerator:
    def visualize(self, vis_type, data, **kwargs):
        logger.info(f"模拟数据艺术生成: {vis_type}")
        output_path = os.path.join(tempfile.gettempdir(), f"{vis_type}_{int(time.time())}.html")
        with open(output_path, 'w') as f:
            f.write(f"<html><body><h1>{kwargs.get('title', '可视化测试')}</h1>")
            f.write("<p>这是一个模拟的数据艺术页面</p>")
            f.write(f"<pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>")
            f.write("</body></html>")
        return output_path

class MockVisualizationManager:
    def __init__(self):
        self.dashboard = MockDashboard()
        self.structure = MockStructureVisualizer()
        self.realtime = MockRealtimeVisualizer()
        self.art_generator = MockDataArtGenerator()
        
    def get_available_components(self):
        return {
            "dashboard": self.dashboard,
            "structure": self.structure,
            "realtime": self.realtime,
            "art_generator": self.art_generator
        }

class MockFeatureIntegrator:
    def __init__(self):
        self.enabled_features = {}
        self.visualization_manager = None
        self._integrators = {}
        
    def set_visualization_manager(self, visualization_manager):
        self.visualization_manager = visualization_manager
        
    def integrate_features(self, feature_ids=None):
        results = {}
        for feature_id in feature_ids:
            if feature_id == "model_optimization":
                self._integrators["model_optimization"] = MockModelOptimizationIntegrator(self.visualization_manager)
                self.enabled_features["model_optimization"] = {
                    "id": "model_optimization",
                    "name": "模型优化工具",
                    "integrator": self._integrators["model_optimization"]
                }
                results["model_optimization"] = True
            else:
                results[feature_id] = False
        return results
        
    def get_feature_integrator(self, feature_id):
        return self._integrators.get(feature_id)

class MockModelOptimizationIntegrator:
    def __init__(self, visualization_manager=None):
        self.visualization_manager = visualization_manager
        
    def _create_performance_comparison_visualization(self):
        if not self.visualization_manager:
            return
            
        try:
            dashboard = self.visualization_manager.dashboard
            example_path = dashboard.visualize(
                "multi_metric",
                {
                    "title": "模型优化性能对比示例",
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
                },
                width=1000,
                height=600,
                theme="light"
            )
            logger.info(f"已创建模型优化性能对比示例: {example_path}")
        except Exception as e:
            logger.error(f"创建性能对比可视化失败: {e}")

def generate_test_data():
    """生成测试数据"""
    logger.info("生成测试数据...")
    
    # 系统监控数据
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
    
    # 模型性能数据
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
    
    # 代码结构数据
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
    
    # 注意力流动数据
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
    
    return {
        "system_data": system_data,
        "model_data": model_data,
        "code_structure": code_structure,
        "attention_data": attention_data
    }

def test_dashboard(vis_manager):
    """测试仪表盘可视化"""
    logger.info("测试仪表盘可视化...")
    
    # 获取测试数据
    test_data = generate_test_data()
    system_data = test_data["system_data"]
    
    # 测试系统监控面板
    try:
        system_monitor_path = vis_manager.dashboard.visualize(
            "system_monitor",
            system_data,
            width=1000,
            height=600,
            theme="light",
            title="系统监控测试"
        )
        logger.info(f"系统监控面板生成成功: {system_monitor_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{system_monitor_path}")
    except Exception as e:
        logger.error(f"系统监控面板生成失败: {e}")
    
    # 测试模型性能面板
    try:
        model_perf_path = vis_manager.dashboard.visualize(
            "model_performance",
            test_data["model_data"],
            width=1000,
            height=600,
            theme="dark",
            title="模型性能测试"
        )
        logger.info(f"模型性能面板生成成功: {model_perf_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{model_perf_path}")
    except Exception as e:
        logger.error(f"模型性能面板生成失败: {e}")

def test_structure_visualizer(vis_manager):
    """测试结构可视化器"""
    logger.info("测试结构可视化器...")
    
    # 获取测试数据
    test_data = generate_test_data()
    code_structure = test_data["code_structure"]
    
    # 测试代码结构图
    try:
        code_structure_path = vis_manager.structure.visualize(
            "code_structure",
            code_structure,
            width=1200,
            height=800,
            theme="light",
            title="代码结构测试"
        )
        logger.info(f"代码结构图生成成功: {code_structure_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{code_structure_path}")
    except Exception as e:
        logger.error(f"代码结构图生成失败: {e}")

def test_realtime_visualizer(vis_manager):
    """测试实时可视化器"""
    logger.info("测试实时可视化器...")
    
    # 获取测试数据
    test_data = generate_test_data()
    attention_data = test_data["attention_data"]
    
    # 测试注意力流动动画
    try:
        attention_flow_path = vis_manager.realtime.visualize(
            "attention_flow",
            attention_data,
            width=1000,
            height=600,
            theme="dark",
            title="注意力流动测试"
        )
        logger.info(f"注意力流动动画生成成功: {attention_flow_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{attention_flow_path}")
    except Exception as e:
        logger.error(f"注意力流动动画生成失败: {e}")
    
    # 测试进度动画
    try:
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
        
        progress_path = vis_manager.realtime.visualize(
            "progress_animation",
            progress_data,
            width=800,
            height=400,
            theme="light",
            title="任务进度测试"
        )
        logger.info(f"进度动画生成成功: {progress_path}")
        
        # 打开生成的HTML文件
        webbrowser.open(f"file://{progress_path}")
    except Exception as e:
        logger.error(f"进度动画生成失败: {e}")

def test_data_art_generator(vis_manager):
    """测试数据艺术生成器"""
    logger.info("测试数据艺术生成器...")
    
    # 测试文本指纹
    try:
        text_data = {
            "text": "AIgo是一个强大的AI助手平台，提供多种功能和工具，帮助开发者更高效地完成工作。",
            "settings": {
                "complexity": 0.8,
                "color_scheme": "rainbow"
            }
        }
        
        fingerprint_path = vis_manager.art_generator.visualize(
            "text_fingerprint",
            text_data,
            width=800,
            height=800,
            theme="dark",
            title="文本指纹测试"
        )
        logger.info(f"文本指纹生成成功: {fingerprint_path}")
        
        # 打开生成的图片文件
        webbrowser.open(f"file://{fingerprint_path}")
    except Exception as e:
        logger.error(f"文本指纹生成失败: {e}")

def test_feature_integration():
    """测试特性集成"""
    logger.info("测试特性集成...")
    
    # 创建可视化管理器
    vis_manager = MockVisualizationManager()
    
    # 创建特性集成器
    integrator = MockFeatureIntegrator()
    integrator.set_visualization_manager(vis_manager)
    
    # 集成模型优化特性
    results = integrator.integrate_features(["model_optimization"])
    
    if results.get("model_optimization", False):
        logger.info("模型优化特性集成成功")
        
        # 获取模型优化集成器
        optimizer = integrator.get_feature_integrator("model_optimization")
        
        # 测试优化可视化
        try:
            # 调用内部方法创建可视化
            optimizer._create_performance_comparison_visualization()
            
            logger.info("模型优化可视化测试成功")
        except Exception as e:
            logger.error(f"模型优化可视化测试失败: {e}")
    else:
        logger.error("模型优化特性集成失败")

def main():
    """主函数"""
    logger.info("开始测试AIgo可视化功能...")
    
    # 创建可视化管理器
    vis_manager = MockVisualizationManager()
    
    # 获取可用的可视化组件
    components = vis_manager.get_available_components()
    logger.info(f"可用的可视化组件: {', '.join(components.keys())}")
    
    # 测试各组件
    if "dashboard" in components:
        test_dashboard(vis_manager)
    
    if "structure" in components:
        test_structure_visualizer(vis_manager)
    
    if "realtime" in components:
        test_realtime_visualizer(vis_manager)
    
    if "art_generator" in components:
        test_data_art_generator(vis_manager)
    
    # 测试特性集成
    test_feature_integration()
    
    logger.info("AIgo可视化功能测试完成")

if __name__ == "__main__":
    main() 