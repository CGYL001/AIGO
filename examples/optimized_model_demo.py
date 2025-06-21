#!/usr/bin/env python3
"""
优化模型使用演示

展示如何使用经过重构和优化的模型进行推理。
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 激活模型重构特性
try:
    from AIGO.utils.feature_discovery import enable_feature
    enable_feature("model_restructuring")
except ImportError:
    print("注意: 无法导入AIGO模块，使用模拟数据继续演示")
    # 定义一个空的enable_feature函数以避免错误
    def enable_feature(name):
        print(f"模拟启用特性: {name}")

def print_header(text):
    """打印带有装饰的标题"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "-"))
    print("=" * 80 + "\n")

def load_and_compare_models(original_model="deepseek-r1:8b", optimized_model="deepseek-r1:8b_optimized"):
    """加载并比较原始模型和优化后的模型"""
    print_header(f"比较模型: {original_model} vs {optimized_model}")
    
    # 在实际实现中，这里会加载真实的模型
    # 这里我们使用模拟数据演示功能
    
    print("加载原始模型...")
    time.sleep(1)  # 模拟加载时间
    
    print("加载优化后的模型...")
    time.sleep(0.5)  # 模拟更快的加载时间
    
    # 模拟的模型参数
    original_params = {
        "模型大小": "7.73 GB",
        "参数数量": "8B",
        "量化位数": "16位浮点数",
        "注意力实现": "标准注意力",
        "激活函数": "GELU",
        "层数": "32"
    }
    
    optimized_params = {
        "模型大小": "2.14 GB",
        "参数数量": "8B",
        "量化位数": "8位整数",
        "注意力实现": "Flash Attention V2",
        "激活函数": "GELU近似版",
        "层数": "32"
    }
    
    # 打印比较结果
    print("\n模型参数比较:")
    print(f"{'参数':<15} {'原始模型':<20} {'优化模型':<20} {'节省/改进':<15}")
    print("-" * 70)
    
    for key in original_params:
        orig = original_params[key]
        opt = optimized_params[key]
        
        # 计算改进
        improvement = ""
        if key == "模型大小":
            orig_size = float(orig.split()[0])
            opt_size = float(opt.split()[0])
            reduction = (orig_size - opt_size) / orig_size * 100
            improvement = f"{reduction:.1f}%"
        elif key == "量化位数" or key == "注意力实现" or key == "激活函数":
            improvement = "优化"
            
        print(f"{key:<15} {orig:<20} {opt:<20} {improvement:<15}")
    
    return original_params, optimized_params

def benchmark_inference(num_iterations=5):
    """对比基准测试"""
    print_header("推理性能基准测试")
    
    sample_texts = [
        "请解释量子计算的基本原理",
        "写一个Python函数计算斐波那契数列",
        "总结《三体》的主要情节",
        "解释深度学习中的反向传播算法",
        "写一篇关于气候变化的短文"
    ]
    
    print(f"运行 {num_iterations} 次推理测试...")
    
    # 原始模型基准测试
    print("\n原始模型推理:")
    original_times = []
    for i, text in enumerate(sample_texts[:num_iterations], 1):
        start_time = time.time()
        
        # 模拟推理延迟
        delay = 2.5 + (len(text) * 0.01)  # 模拟更复杂的提示需要更长时间
        time.sleep(delay)
        
        end_time = time.time()
        elapsed = end_time - start_time
        original_times.append(elapsed)
        print(f"  查询 {i}: {elapsed:.2f} 秒")
    
    # 优化模型基准测试
    print("\n优化模型推理:")
    optimized_times = []
    for i, text in enumerate(sample_texts[:num_iterations], 1):
        start_time = time.time()
        
        # 模拟优化后的更快推理延迟
        delay = (2.5 + (len(text) * 0.01)) * 0.6  # 优化后大约快40%
        time.sleep(delay)
        
        end_time = time.time()
        elapsed = end_time - start_time
        optimized_times.append(elapsed)
        print(f"  查询 {i}: {elapsed:.2f} 秒")
    
    # 计算并打印统计数据
    avg_original = sum(original_times) / len(original_times)
    avg_optimized = sum(optimized_times) / len(optimized_times)
    improvement = (avg_original - avg_optimized) / avg_original * 100
    
    print("\n性能对比:")
    print(f"  原始模型平均推理时间: {avg_original:.2f} 秒")
    print(f"  优化模型平均推理时间: {avg_optimized:.2f} 秒")
    print(f"  性能提升: {improvement:.1f}%")
    
    return {
        "original_avg": avg_original,
        "optimized_avg": avg_optimized,
        "improvement": improvement
    }

def memory_usage_comparison():
    """内存使用对比"""
    print_header("内存使用对比")
    
    # 模拟内存使用数据
    memory_data = {
        "peak_original": 8.2,  # GB
        "peak_optimized": 3.8,  # GB
        "idle_original": 7.5,  # GB
        "idle_optimized": 2.1,  # GB
    }
    
    reduction_peak = (memory_data["peak_original"] - memory_data["peak_optimized"]) / memory_data["peak_original"] * 100
    reduction_idle = (memory_data["idle_original"] - memory_data["idle_optimized"]) / memory_data["idle_original"] * 100
    
    print("内存使用情况:")
    print(f"  原始模型峰值内存: {memory_data['peak_original']:.1f} GB")
    print(f"  优化模型峰值内存: {memory_data['peak_optimized']:.1f} GB")
    print(f"  峰值内存减少: {reduction_peak:.1f}%")
    print()
    print(f"  原始模型空闲内存: {memory_data['idle_original']:.1f} GB")
    print(f"  优化模型空闲内存: {memory_data['idle_optimized']:.1f} GB")
    print(f"  空闲内存减少: {reduction_idle:.1f}%")
    
    return memory_data

def main():
    """主函数"""
    print_header("优化模型使用演示")
    
    print("本演示将展示经过重构和优化的深度学习模型的性能提升")
    print("注意: 为了演示目的，这里使用模拟数据")
    
    # 步骤1: 比较模型参数
    original_params, optimized_params = load_and_compare_models()
    
    # 步骤2: 运行基准测试
    benchmark_results = benchmark_inference(num_iterations=3)
    
    # 步骤3: 对比内存使用
    memory_results = memory_usage_comparison()
    
    # 总结结果
    print_header("优化结果总结")
    print(f"1. 模型大小减少: {(1 - float(optimized_params['模型大小'].split()[0])/float(original_params['模型大小'].split()[0])) * 100:.1f}%")
    print(f"2. 推理速度提升: {benchmark_results['improvement']:.1f}%")
    print(f"3. 峰值内存减少: {(memory_results['peak_original'] - memory_results['peak_optimized']) / memory_results['peak_original'] * 100:.1f}%")
    print("\n总体评价: 通过模型重构和优化，我们实现了更高效的推理性能和更低的资源消耗，")
    print("          同时保持模型的功能和准确性不变。")
    
    print("\n实际应用中的优势:")
    print("- 在更低端的硬件上运行高级模型")
    print("- 降低云服务成本")
    print("- 提高用户体验速度")
    print("- 减少电力消耗")

if __name__ == "__main__":
    main() 