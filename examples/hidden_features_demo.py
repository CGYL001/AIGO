#!/usr/bin/env python3
"""
AIgo隐藏功能演示

本示例演示如何发现和启用AIgo中的隐藏功能。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

import aigo
from aigo import discover_feature, enable_feature, get_all_hidden_features

def print_header(text):
    """打印带有装饰的标题"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "-"))
    print("=" * 80 + "\n")

def print_feature_info(feature):
    """打印功能信息"""
    print(f"名称: {feature['name']}")
    print(f"描述: {feature['description']}")
    print(f"状态: {'已启用' if feature['enabled'] else '未启用'}")
    print()

def list_all_hidden_features():
    """列出所有隐藏功能"""
    print_header("AIgo隐藏功能列表")
    features = get_all_hidden_features()
    
    if not features:
        print("未发现隐藏功能")
        return
    
    print(f"发现 {len(features)} 个隐藏功能:\n")
    
    for i, feature in enumerate(features, 1):
        print(f"{i}. {feature['name']}")
        print(f"   描述: {feature['description']}")
        print(f"   状态: {'已启用' if feature['enabled'] else '未启用'}")
        print()

def discover_features_demo():
    """功能发现演示"""
    print_header("功能发现演示")
    
    # 通用隐藏功能查询
    print("== 通用隐藏功能查询 ==\n")
    general_queries = [
        "有没有隐藏功能?",
        "系统里有什么高级功能吗?",
        "有什么特殊功能?"
    ]
    
    for query in general_queries:
        print(f"查询: {query}")
        feature = discover_feature(query)
        
        if feature and feature.get("is_summary", False):
            print(f"发现: {feature['name']}")
            print(f"描述: {feature['description']}")
            print(f"包含 {len(feature['features'])} 个隐藏功能")
            print()
        else:
            print("未发现相关功能\n")
    
    # 特定功能查询
    print("\n== 特定功能查询 ==\n")
    specific_queries = [
        "有没有可以优化模型性能的工具?",
        "我想分析一下系统状态",
        "能不能让多个模型协同工作?",
        "有没有自动调优系统的功能?",
        "模型结构怎么重构?",
        "有没有系统模拟器?"
    ]
    
    print("尝试使用不同的查询发现特定隐藏功能:\n")
    
    for i, query in enumerate(specific_queries, 1):
        print(f"查询 {i}: {query}")
        feature = discover_feature(query)
        
        if feature and not feature.get("is_summary", False):
            print(f"发现功能: {feature['name']}")
            print(f"描述: {feature['description']}")
            print(f"模块: {feature['module']}")
            print()
        else:
            print("未发现相关功能\n")

def enable_features_demo():
    """启用功能演示"""
    print_header("启用功能演示")
    
    feature_ids = [
        "model_optimization",
        "system_analysis",
        "model_coordination",
        "system_optimization",
        "model_restructuring",
        "system_simulation"
    ]
    
    print("尝试启用隐藏功能:\n")
    
    for feature_id in feature_ids:
        print(f"启用功能: {feature_id}")
        success = enable_feature(feature_id)
        
        if success:
            print("启用成功!")
        else:
            print("启用失败")
            
        print()
    
    # 显示启用后的状态
    print("启用后的功能状态:")
    features = get_all_hidden_features()
    
    for feature in features:
        print(f"{feature['id']}: {'已启用' if feature['enabled'] else '未启用'}")

def main():
    """主函数"""
    print_header("AIgo隐藏功能演示")
    
    # 列出所有隐藏功能
    list_all_hidden_features()
    
    # 功能发现演示
    discover_features_demo()
    
    # 启用功能演示
    enable_features_demo()
    
    print("\n演示完成!")

if __name__ == "__main__":
    main() 