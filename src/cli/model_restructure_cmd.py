#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型重构命令行工具

提供命令行接口，用于分析和优化模型结构
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("model_restructure_cmd")

def analyze_model(args):
    """分析模型结构"""
    try:
        from src.modules.model_restructuring.model_restructurer import ModelRestructurer
        
        logger.info(f"分析模型: {args.model_path}")
        
        # 创建模型重构器
        restructurer = ModelRestructurer()
        
        # 分析模型
        start_time = time.time()
        analysis = restructurer.analyze_model(args.model_path)
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
        
        # 保存分析结果
        if args.output:
            output_path = args.output
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"分析结果已保存到: {output_path}")
        
        return 0
    except ImportError:
        logger.error("导入模型重构模块失败，请先运行 test_model_restructurer.py 创建模块")
        return 1
    except Exception as e:
        logger.error(f"分析模型时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

def optimize_model(args):
    """优化模型结构"""
    try:
        from src.modules.model_restructuring.model_restructurer import ModelRestructurer
        
        logger.info(f"优化模型: {args.model_path}")
        logger.info(f"优化级别: {args.level}")
        
        # 创建模型重构器
        restructurer = ModelRestructurer()
        
        # 优化模型
        start_time = time.time()
        result = restructurer.optimize_model(args.model_path, args.output, optimization_level=args.level)
        elapsed = time.time() - start_time
        
        # 打印优化结果
        logger.info(f"模型优化完成，耗时: {elapsed:.2f}秒")
        logger.info(f"尺寸减少: {result['size_reduction']}")
        logger.info(f"速度提升: {result['speed_improvement']}")
        logger.info(f"内存减少: {result['memory_reduction']}")
        logger.info(f"应用的优化数量: {len(result['applied_optimizations'])}")
        
        # 打印应用的优化
        logger.info("应用的优化:")
        for i, opt in enumerate(result['applied_optimizations'], 1):
            logger.info(f"  {i}. {opt['type']}")
        
        logger.info(f"优化结果已保存到: {args.output}")
        logger.info(f"优化元数据已保存到: {args.output}.json")
        
        return 0
    except ImportError:
        logger.error("导入模型重构模块失败，请先运行 test_model_restructurer.py 创建模块")
        return 1
    except Exception as e:
        logger.error(f"优化模型时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="模型重构命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 分析命令
    analyze_parser = subparsers.add_parser("analyze", help="分析模型结构")
    analyze_parser.add_argument("model_path", help="模型路径")
    analyze_parser.add_argument("-o", "--output", help="分析结果输出路径")
    
    # 优化命令
    optimize_parser = subparsers.add_parser("optimize", help="优化模型结构")
    optimize_parser.add_argument("model_path", help="模型路径")
    optimize_parser.add_argument("output", help="优化后的模型输出路径")
    optimize_parser.add_argument("-l", "--level", type=int, choices=[1, 2, 3], default=1, 
                               help="优化级别: 1=注意力层优化, 2=注意力层+前馈网络优化, 3=全面优化")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        return analyze_model(args)
    elif args.command == "optimize":
        return optimize_model(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 