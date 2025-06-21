#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
可视化模块集成演示脚本

这个脚本展示了如何将可视化模块与系统的其他部分集成，
包括系统监控、模型管理器和知识库管理器等。
"""

import os
import time
import random
import json
import argparse
from pathlib import Path
from test_visualization import MockVisualizationManager
from test_integration import (
    MockSystemMonitor,
    MockModelManager,
    MockKnowledgeBaseManager
)

class IntegrationDemo:
    """集成演示类"""
    
    def __init__(self, config=None):
        """初始化集成演示"""
        # 加载配置
        self.config = config or {}
        
        # 创建模拟组件
        self.vis_manager = MockVisualizationManager()
        self.system_monitor = MockSystemMonitor()
        self.model_manager = MockModelManager()
        self.kb_manager = MockKnowledgeBaseManager()
        
        # 输出目录
        self.output_dir = self.config.get("output_dir", "output/integration")
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("集成演示初始化完成")
    
    def demo_system_monitoring(self):
        """演示系统监控集成"""
        print("\n===== 系统监控集成演示 =====")
        
        # 获取系统指标
        system_metrics = self.system_monitor.get_system_metrics()
        print(f"获取到系统指标: CPU {system_metrics['cpu_usage']}%, 内存 {system_metrics['memory_usage']}%")
        
        # 创建系统监控仪表盘
        dashboard_id = self.vis_manager.dashboard.visualize(
            "system_monitor",
            system_metrics,
            title="实时系统监控"
        )
        print(f"系统监控仪表盘已创建，ID: {dashboard_id}")
        
        # 模拟实时更新
        print("\n模拟实时更新系统监控...")
        for i in range(5):
            # 获取更新的系统指标
            updated_metrics = self.system_monitor.get_system_metrics()
            print(f"更新 #{i+1}: CPU {updated_metrics['cpu_usage']}%, 内存 {updated_metrics['memory_usage']}%")
            
            # 在实际实现中，这里会更新仪表盘
            # 为了演示，我们只是打印信息
            print(f"更新仪表盘: {dashboard_id}")
            
            # 等待一秒
            time.sleep(1)
        
        return dashboard_id
    
    def demo_model_performance(self):
        """演示模型性能监控集成"""
        print("\n===== 模型性能监控集成演示 =====")
        
        # 获取模型列表
        models = self.model_manager.list_models()
        print(f"获取到 {len(models)} 个模型:")
        for model in models:
            print(f"  - {model['name']} ({model['type']})")
        
        # 选择一个模型进行性能分析
        model_name = models[0]["name"]
        print(f"\n对模型 {model_name} 进行性能分析...")
        
        # 获取模型性能指标
        performance = self.model_manager.get_model_performance(model_name)
        print(f"获取到模型性能指标: 延迟 {performance['latency']}ms, 吞吐量 {performance['throughput']} req/s")
        
        # 创建模型性能仪表盘
        perf_id = self.vis_manager.dashboard.visualize(
            "model_performance",
            performance,
            title=f"模型性能 - {model_name}"
        )
        print(f"模型性能仪表盘已创建，ID: {perf_id}")
        
        # 模拟模型优化
        print("\n模拟模型优化过程...")
        for i in range(3):
            # 执行优化
            optimization = self.model_manager.optimize_model(model_name, f"optimization_{i+1}")
            print(f"优化 #{i+1}: {optimization['name']} - 性能提升 {optimization['improvement']}%")
            
            # 获取优化后的性能
            new_performance = self.model_manager.get_model_performance(model_name)
            print(f"优化后性能: 延迟 {new_performance['latency']}ms (-{performance['latency'] - new_performance['latency']}ms)")
            
            # 在实际实现中，这里会更新性能仪表盘
            # 为了演示，我们只是打印信息
            print(f"更新性能仪表盘: {perf_id}")
            
            # 保存当前性能作为下一次比较的基准
            performance = new_performance
            
            # 等待一秒
            time.sleep(1)
        
        return perf_id
    
    def demo_knowledge_visualization(self):
        """演示知识库可视化集成"""
        print("\n===== 知识库可视化集成演示 =====")
        
        # 获取知识库统计信息
        kb_stats = self.kb_manager.get_statistics()
        print(f"知识库统计: {kb_stats['total_documents']} 文档, {kb_stats['total_embeddings']} 嵌入向量")
        
        # 创建知识库统计仪表盘
        stats_id = self.vis_manager.dashboard.visualize(
            "kb_statistics",
            kb_stats,
            title="知识库统计"
        )
        print(f"知识库统计仪表盘已创建，ID: {stats_id}")
        
        # 获取知识图谱
        print("\n获取知识图谱...")
        knowledge_graph = self.kb_manager.get_knowledge_graph()
        print(f"获取到知识图谱: {len(knowledge_graph['nodes'])} 节点, {len(knowledge_graph['edges'])} 边")
        
        # 创建知识图谱可视化
        graph_id = self.vis_manager.structure.visualize(
            "knowledge_graph",
            knowledge_graph,
            title="知识图谱"
        )
        print(f"知识图谱可视化已创建，ID: {graph_id}")
        
        # 模拟知识库查询
        print("\n模拟知识库查询...")
        query = "人工智能在医疗领域的应用"
        print(f"查询: {query}")
        
        # 执行查询
        results = self.kb_manager.search(query)
        print(f"找到 {len(results)} 个相关文档")
        
        # 创建查询结果可视化
        results_id = self.vis_manager.structure.visualize(
            "search_results",
            {
                "query": query,
                "results": results
            },
            title="知识库查询结果"
        )
        print(f"查询结果可视化已创建，ID: {results_id}")
        
        return [stats_id, graph_id, results_id]
    
    def run_all_demos(self):
        """运行所有演示"""
        results = {}
        
        # 运行系统监控演示
        results["system_monitoring"] = self.demo_system_monitoring()
        
        # 运行模型性能监控演示
        results["model_performance"] = self.demo_model_performance()
        
        # 运行知识库可视化演示
        results["knowledge_visualization"] = self.demo_knowledge_visualization()
        
        return results

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="可视化模块集成演示")
    parser.add_argument("--output-dir", "-o", type=str, default="output/integration",
                        help="输出目录")
    parser.add_argument("--demo", "-d", type=str, 
                        choices=["all", "system", "model", "knowledge"],
                        default="all", help="要运行的演示类型")
    args = parser.parse_args()
    
    # 创建配置
    config = {
        "output_dir": args.output_dir
    }
    
    # 创建演示实例
    demo = IntegrationDemo(config)
    
    print("=== 可视化模块集成演示 ===")
    print("注意: 这个演示使用模拟实现，实际效果将在集成到真实系统后呈现")
    
    # 根据选择运行不同的演示
    results = {}
    
    if args.demo in ["all", "system"]:
        results["system"] = demo.demo_system_monitoring()
    
    if args.demo in ["all", "model"]:
        results["model"] = demo.demo_model_performance()
    
    if args.demo in ["all", "knowledge"]:
        results["knowledge"] = demo.demo_knowledge_visualization()
    
    print("\n=== 演示完成 ===")
    print("在实际系统中，这些可视化将与真实数据源集成，提供实时的可视化效果")

if __name__ == "__main__":
    main() 