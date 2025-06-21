"""
使用AIGO生成内容并将结果写入桌面
同时演示使用多个模型对比的能力
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# 确保可以导入AIGO模块
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

import AIGO
from AIGO.models.base import ModelConfig, get_model_runner

def main():
    # 获取桌面路径
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_file = os.path.join(desktop_path, "aigo_models_comparison.txt")
    visualization_file = os.path.join(desktop_path, "aigo_models_performance.json")
    
    print(f"AIGO版本: {AIGO.__version__}")
    print(f"输出文件将保存到: {output_file}")
    print(f"模型性能数据将保存到: {visualization_file}")
    
    # 默认内容 - 如果Ollama未运行
    content = [
        "# AIGO测试输出",
        "这是一个由AIGO生成的测试文件。",
        "",
        "如果您看到这个文本，说明基本的文件写入功能正常工作，",
        "但没有使用AI模型生成内容。要使用AI生成内容，请确保Ollama已安装并运行。",
        "",
        f"AIGO版本: {AIGO.__version__}"
    ]
    
    model_results = {}
    model_performance = {}
    
    try:
        # 尝试生成AI内容 - 定义多个不同的模型配置
        print("尝试连接AI模型...")
        
        # 定义三个不同的模型配置
        models = [
            {
                "name": "模型1 (高创造性)", 
                "config": ModelConfig(
                    provider="ollama",
                    model_name="llama2:7b-chat-q4_K_M",
                    api_base="http://localhost:11434",
                    temperature=0.8,
                    max_tokens=300
                )
            },
            {
                "name": "模型2 (中等创造性)",
                "config": ModelConfig(
                    provider="ollama",
                    model_name="llama2:7b-chat-q4_K_M",
                    api_base="http://localhost:11434",
                    temperature=0.5,
                    max_tokens=300
                )
            },
            {
                "name": "模型3 (低创造性)",
                "config": ModelConfig(
                    provider="ollama",
                    model_name="llama2:7b-chat-q4_K_M",
                    api_base="http://localhost:11434",
                    temperature=0.2,
                    max_tokens=300
                )
            }
        ]
        
        # 生成内容
        prompt = "请写一篇关于人工智能的短文，包括其历史、现状和未来发展。限制在300字以内。"
        
        # 对每个模型生成内容
        for model_info in models:
            print(f"使用{model_info['name']}生成内容...")
            
            try:
                # 获取模型运行器
                runner = get_model_runner(model_info["config"])
                runner.load()
                print(f"{model_info['name']} 已加载")
                
                # 记录开始时间
                start_time = time.time()
                
                # 生成内容
                response = runner.generate(prompt)
                
                # 计算生成时间
                generation_time = time.time() - start_time
                
                # 存储结果
                model_results[model_info["name"]] = {
                    "response": response,
                    "time": generation_time,
                    "temperature": model_info["config"].temperature
                }
                
                # 存储性能数据
                model_performance[model_info["name"]] = {
                    "response_time": generation_time,
                    "temperature": model_info["config"].temperature,
                    "tokens": len(response.split())
                }
                
                print(f"{model_info['name']}内容已生成，耗时: {generation_time:.2f}秒")
            except Exception as e:
                print(f"使用{model_info['name']}时出错: {e}")
                model_results[model_info["name"]] = {
                    "response": f"生成失败: {str(e)}",
                    "time": 0,
                    "temperature": model_info["config"].temperature
                }
        
        # 将性能数据保存为JSON文件供可视化使用
        try:
            with open(visualization_file, "w", encoding="utf-8") as f:
                json.dump(model_performance, f, indent=2, ensure_ascii=False)
            print(f"性能数据已保存到: {visualization_file}")
        except Exception as e:
            print(f"保存性能数据失败: {e}")
        
        # 更新内容
        content = [
            "# AIGO多模型对比实验",
            "",
            "提示: " + prompt,
            "",
        ]
        
        # 添加每个模型的结果
        for model_name, result in model_results.items():
            content.extend([
                f"## {model_name} (temperature={result['temperature']})",
                result["response"],
                "",
                f"生成时间: {result['time']:.2f}秒",
                "",
                "---",
                ""
            ])
        
        # 添加性能比较
        content.extend([
            "# 性能比较",
            "",
            "| 模型 | 温度参数 | 响应时间(秒) |",
            "| ---- | -------- | ---------- |",
        ])
        
        for model_name, result in model_results.items():
            content.append(f"| {model_name} | {result['temperature']} | {result['time']:.2f} |")
        
        content.extend([
            "",
            "---",
            f"性能数据已保存到: {os.path.basename(visualization_file)}",
            "",
            f"由AIGO v{AIGO.__version__}生成"
        ])
        
        print("内容已生成")
        
    except Exception as e:
        print(f"使用AI模型时出错: {e}")
        print("将使用默认内容")
    
    # 写入文件
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(f"内容已成功写入: {output_file}")
    except Exception as e:
        print(f"写入文件时出错: {e}")

if __name__ == "__main__":
    main() 