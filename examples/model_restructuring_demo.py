#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型重构系统演示脚本

演示如何使用模型重构系统优化模型结构
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("model_restructuring_demo")

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def setup_demo_environment():
    """设置演示环境"""
    # 创建模型目录
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    # 创建输出目录
    output_dir = Path("output/model_restructuring")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 创建示例模型配置
    demo_model_config = {
        "name": "demo_model",
        "type": "transformer",
        "size": "7B",
        "layers": 32,
        "hidden_size": 4096,
        "attention_heads": 32,
        "intermediate_size": 11008,
        "vocab_size": 32000,
        "max_position_embeddings": 2048
    }
    
    # 保存示例模型配置
    demo_model_path = model_dir / "demo_model.json"
    with open(demo_model_path, 'w', encoding='utf-8') as f:
        json.dump(demo_model_config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"创建示例模型配置: {demo_model_path}")
    return str(demo_model_path)

def demonstrate_model_analysis(model_path):
    """演示模型分析"""
    from src.modules.model_restructuring.model_restructurer import ModelRestructurer
    
    logger.info("=" * 50)
    logger.info("模型分析演示")
    logger.info("=" * 50)
    
    # 创建模型重构器
    restructurer = ModelRestructurer()
    
    # 分析模型
    logger.info(f"开始分析模型: {model_path}")
    start_time = time.time()
    analysis = restructurer.analyze_model(model_path)
    elapsed = time.time() - start_time
    
    # 打印分析结果
    logger.info(f"模型分析完成，耗时: {elapsed:.2f}秒")
    logger.info(f"模型大小: {analysis['model_size']}")
    logger.info(f"模型层数: {analysis['layers']}")
    logger.info(f"注意力头数: {analysis['attention_heads']}")
    logger.info(f"前馈网络维度: {analysis['ffn_dim']}")
    
    # 打印瓶颈分析
    logger.info("模型瓶颈分析:")
    for bottleneck in analysis['bottlenecks']:
        logger.info(f"  - 层 {bottleneck['layer']}: {bottleneck['type']} 类型, 得分: {bottleneck['score']}")
    
    logger.info(f"优化潜力评分: {analysis['optimization_potential']}")
    
    return analysis

def demonstrate_model_optimization(model_path, analysis):
    """演示模型优化"""
    from src.modules.model_restructuring.model_restructurer import ModelRestructurer
    
    logger.info("\n" + "=" * 50)
    logger.info("模型优化演示")
    logger.info("=" * 50)
    
    # 创建模型重构器
    restructurer = ModelRestructurer()
    
    # 定义输出路径
    output_path = "output/model_restructuring/optimized_model"
    
    # 优化模型 - 级别1
    logger.info("执行级别1优化 (注意力层优化)")
    start_time = time.time()
    result_l1 = restructurer.optimize_model(model_path, f"{output_path}_l1", optimization_level=1)
    elapsed_l1 = time.time() - start_time
    logger.info(f"级别1优化完成，耗时: {elapsed_l1:.2f}秒")
    logger.info(f"尺寸减少: {result_l1['size_reduction']}")
    logger.info(f"速度提升: {result_l1['speed_improvement']}")
    logger.info(f"内存减少: {result_l1['memory_reduction']}")
    
    # 优化模型 - 级别2
    logger.info("\n执行级别2优化 (注意力层 + 前馈网络优化)")
    start_time = time.time()
    result_l2 = restructurer.optimize_model(model_path, f"{output_path}_l2", optimization_level=2)
    elapsed_l2 = time.time() - start_time
    logger.info(f"级别2优化完成，耗时: {elapsed_l2:.2f}秒")
    logger.info(f"尺寸减少: {result_l2['size_reduction']}")
    logger.info(f"速度提升: {result_l2['speed_improvement']}")
    logger.info(f"内存减少: {result_l2['memory_reduction']}")
    
    # 优化模型 - 级别3
    logger.info("\n执行级别3优化 (注意力层 + 前馈网络 + 整体结构优化)")
    start_time = time.time()
    result_l3 = restructurer.optimize_model(model_path, f"{output_path}_l3", optimization_level=3)
    elapsed_l3 = time.time() - start_time
    logger.info(f"级别3优化完成，耗时: {elapsed_l3:.2f}秒")
    logger.info(f"尺寸减少: {result_l3['size_reduction']}")
    logger.info(f"速度提升: {result_l3['speed_improvement']}")
    logger.info(f"内存减少: {result_l3['memory_reduction']}")
    
    return {
        "level1": result_l1,
        "level2": result_l2,
        "level3": result_l3
    }

def demonstrate_optimization_comparison(results):
    """演示优化结果比较"""
    logger.info("\n" + "=" * 50)
    logger.info("优化结果比较")
    logger.info("=" * 50)
    
    # 创建比较表格
    logger.info("不同优化级别的效果比较:")
    logger.info("| 优化级别 | 尺寸减少 | 速度提升 | 内存减少 | 应用的优化数量 |")
    logger.info("|----------|----------|----------|----------|----------------|")
    
    for level, result in [
        ("级别1 (注意力层)", results["level1"]),
        ("级别2 (+ 前馈网络)", results["level2"]),
        ("级别3 (+ 整体结构)", results["level3"])
    ]:
        opt_count = len(result["applied_optimizations"])
        logger.info(f"| {level} | {result['size_reduction']} | {result['speed_improvement']} | {result['memory_reduction']} | {opt_count} |")
    
    # 优化建议
    logger.info("\n基于比较结果的优化建议:")
    logger.info("1. 对于资源受限环境 (如移动设备): 使用级别3优化")
    logger.info("2. 对于平衡性能和质量: 使用级别2优化")
    logger.info("3. 对于保持高精度场景: 使用级别1优化")

def main():
    """主函数"""
    logger.info("开始模型重构系统演示")
    
    try:
        # 设置演示环境
        model_path = setup_demo_environment()
        
        # 演示模型分析
        analysis = demonstrate_model_analysis(model_path)
        
        # 演示模型优化
        results = demonstrate_model_optimization(model_path, analysis)
        
        # 演示优化结果比较
        demonstrate_optimization_comparison(results)
        
        logger.info("\n演示完成! 优化后的模型和分析结果保存在 output/model_restructuring/ 目录")
        return 0
    except ImportError:
        logger.error("导入模型重构模块失败，请先运行 test_model_restructurer.py 创建模块")
        return 1
    except Exception as e:
        logger.error(f"演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 