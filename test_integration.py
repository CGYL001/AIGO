#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
可视化模块集成测试

这个模块提供了模拟的系统组件，用于测试可视化模块与其他系统组件的集成。
"""

import random
import time
from typing import Dict, List, Any

class MockSystemMonitor:
    """模拟系统监控器"""
    
    def __init__(self):
        """初始化系统监控器"""
        self.base_cpu_usage = random.uniform(20, 40)
        self.base_memory_usage = random.uniform(30, 50)
        self.base_disk_usage = random.uniform(40, 60)
    
    def get_system_metrics(self) -> Dict[str, float]:
        """
        获取系统指标
        
        Returns:
            Dict[str, float]: 系统指标字典
        """
        # 添加一些随机波动
        cpu_variation = random.uniform(-5, 5)
        memory_variation = random.uniform(-3, 3)
        disk_variation = random.uniform(-1, 1)
        
        # 确保值在合理范围内
        cpu_usage = max(0, min(100, self.base_cpu_usage + cpu_variation))
        memory_usage = max(0, min(100, self.base_memory_usage + memory_variation))
        disk_usage = max(0, min(100, self.base_disk_usage + disk_variation))
        
        return {
            "cpu_usage": round(cpu_usage, 1),
            "memory_usage": round(memory_usage, 1),
            "disk_usage": round(disk_usage, 1),
            "network_in": round(random.uniform(1, 5), 2),
            "network_out": round(random.uniform(0.5, 3), 2),
            "timestamp": time.time()
        }
    
    def get_process_metrics(self, process_id: int = None) -> Dict[str, Any]:
        """
        获取进程指标
        
        Args:
            process_id: 进程ID，如果为None，则返回所有进程
            
        Returns:
            Dict[str, Any]: 进程指标字典
        """
        if process_id is None:
            # 返回多个进程的指标
            processes = []
            for i in range(5):
                processes.append({
                    "pid": 1000 + i,
                    "name": f"process_{i}",
                    "cpu_usage": round(random.uniform(1, 10), 1),
                    "memory_usage": round(random.uniform(50, 200), 1),
                    "status": random.choice(["running", "sleeping", "waiting"])
                })
            return {"processes": processes}
        else:
            # 返回单个进程的指标
            return {
                "pid": process_id,
                "name": f"process_{process_id}",
                "cpu_usage": round(random.uniform(1, 10), 1),
                "memory_usage": round(random.uniform(50, 200), 1),
                "status": random.choice(["running", "sleeping", "waiting"]),
                "threads": random.randint(1, 10),
                "open_files": random.randint(5, 20)
            }

class MockModelManager:
    """模拟模型管理器"""
    
    def __init__(self):
        """初始化模型管理器"""
        self.models = [
            {
                "name": "text_generation",
                "type": "language_model",
                "version": "1.0.0",
                "size": "7B",
                "performance": {
                    "latency": random.uniform(100, 300),
                    "throughput": random.uniform(5, 15),
                    "error_rate": random.uniform(0.01, 0.1),
                    "success_rate": random.uniform(0.9, 0.99)
                }
            },
            {
                "name": "image_classification",
                "type": "vision_model",
                "version": "2.1.0",
                "size": "1.5B",
                "performance": {
                    "latency": random.uniform(50, 150),
                    "throughput": random.uniform(20, 40),
                    "error_rate": random.uniform(0.05, 0.15),
                    "success_rate": random.uniform(0.85, 0.95)
                }
            },
            {
                "name": "sentiment_analysis",
                "type": "nlp_model",
                "version": "1.2.0",
                "size": "350M",
                "performance": {
                    "latency": random.uniform(20, 80),
                    "throughput": random.uniform(50, 100),
                    "error_rate": random.uniform(0.02, 0.08),
                    "success_rate": random.uniform(0.92, 0.98)
                }
            }
        ]
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        获取模型列表
        
        Returns:
            List[Dict[str, Any]]: 模型列表
        """
        return self.models
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            Dict[str, Any]: 模型信息
        """
        for model in self.models:
            if model["name"] == model_name:
                return model
        return None
    
    def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型性能指标
        
        Args:
            model_name: 模型名称
            
        Returns:
            Dict[str, Any]: 模型性能指标
        """
        model = self.get_model_info(model_name)
        if model:
            # 添加一些随机波动
            performance = model["performance"].copy()
            performance["latency"] = round(performance["latency"] * random.uniform(0.9, 1.1), 1)
            performance["throughput"] = round(performance["throughput"] * random.uniform(0.9, 1.1), 1)
            performance["error_rate"] = round(performance["error_rate"] * random.uniform(0.9, 1.1), 3)
            performance["success_rate"] = round(1 - performance["error_rate"], 3)
            return performance
        return None
    
    def optimize_model(self, model_name: str, optimization_type: str) -> Dict[str, Any]:
        """
        优化模型
        
        Args:
            model_name: 模型名称
            optimization_type: 优化类型
            
        Returns:
            Dict[str, Any]: 优化结果
        """
        model = self.get_model_info(model_name)
        if model:
            # 模拟优化效果
            improvement = random.uniform(5, 15)
            
            # 更新模型性能
            model["performance"]["latency"] *= (1 - improvement / 100)
            model["performance"]["throughput"] *= (1 + improvement / 100)
            model["performance"]["error_rate"] *= (1 - improvement / 200)
            model["performance"]["success_rate"] = 1 - model["performance"]["error_rate"]
            
            return {
                "name": optimization_type,
                "model": model_name,
                "improvement": round(improvement, 1),
                "timestamp": time.time()
            }
        return None

class MockKnowledgeBaseManager:
    """模拟知识库管理器"""
    
    def __init__(self):
        """初始化知识库管理器"""
        self.total_documents = random.randint(1000, 5000)
        self.total_embeddings = self.total_documents * random.randint(5, 15)
        
        # 模拟知识图谱
        self.knowledge_graph = self._generate_knowledge_graph()
    
    def _generate_knowledge_graph(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        生成模拟知识图谱
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 知识图谱
        """
        # 创建节点
        nodes = []
        node_types = ["概念", "实体", "属性", "关系"]
        domains = ["医疗", "教育", "科技", "金融", "法律"]
        
        for i in range(20):
            node_type = random.choice(node_types)
            domain = random.choice(domains)
            nodes.append({
                "id": str(i),
                "label": f"{domain}_{node_type}_{i}",
                "type": node_type,
                "domain": domain,
                "weight": random.randint(1, 10)
            })
        
        # 创建边
        edges = []
        edge_types = ["包含", "关联", "属于", "影响"]
        
        for i in range(30):
            source = random.randint(0, 19)
            target = random.randint(0, 19)
            if source != target:
                edges.append({
                    "id": f"e{i}",
                    "source": str(source),
                    "target": str(target),
                    "label": random.choice(edge_types),
                    "weight": random.uniform(0.1, 1.0)
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            "total_documents": self.total_documents,
            "total_embeddings": self.total_embeddings,
            "avg_embeddings_per_doc": round(self.total_embeddings / self.total_documents, 2),
            "domains": {
                "医疗": random.randint(100, 1000),
                "教育": random.randint(100, 1000),
                "科技": random.randint(100, 1000),
                "金融": random.randint(100, 1000),
                "法律": random.randint(100, 1000)
            },
            "last_updated": time.time() - random.randint(0, 86400)
        }
    
    def get_knowledge_graph(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取知识图谱
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 知识图谱
        """
        return self.knowledge_graph
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 查询字符串
            
        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        # 模拟搜索结果
        result_count = random.randint(3, 10)
        results = []
        
        for i in range(result_count):
            results.append({
                "id": f"doc_{random.randint(1, 1000)}",
                "title": f"文档 {i+1} - 关于{query}的研究",
                "snippet": f"这是一个关于{query}的文档摘要，包含了相关的研究内容和结论...",
                "relevance": round(random.uniform(0.5, 1.0), 2),
                "source": random.choice(["内部知识库", "公开论文", "网络资源", "专家意见"])
            })
        
        # 按相关性排序
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        return results 