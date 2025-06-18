#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型管理工具
用于切换和管理Ollama模型
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

CONFIG_PATH = ROOT_DIR / "config" / "default" / "config.json"

def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return None

def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"配置已保存到 {CONFIG_PATH}")
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False

def list_models():
    """列出所有已下载的模型"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("已下载的模型:")
            print(result.stdout)
        else:
            print(f"获取模型列表失败: {result.stderr}")
    except Exception as e:
        print(f"执行命令失败: {e}")

def switch_model(model_name):
    """切换默认推理模型"""
    config = load_config()
    if not config:
        return False
        
    current_model = config["models"]["inference"]["name"]
    if current_model == model_name:
        print(f"当前已经使用的是 {model_name} 模型")
        return True
        
    # 检查模型是否已下载
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"获取模型列表失败: {result.stderr}")
            return False
            
        if model_name not in result.stdout:
            print(f"模型 {model_name} 未下载，请先下载")
            return False
    except Exception as e:
        print(f"执行命令失败: {e}")
        return False
        
    # 更新配置
    config["models"]["inference"]["name"] = model_name
    print(f"默认推理模型已从 {current_model} 切换为 {model_name}")
    
    return save_config(config)

def download_model(model_name):
    """下载模型"""
    try:
        print(f"正在下载模型 {model_name}...")
        result = subprocess.run(["ollama", "pull", model_name], capture_output=False, text=True)
        if result.returncode == 0:
            print(f"模型 {model_name} 下载成功")
            return True
        else:
            print(f"模型下载失败")
            return False
    except Exception as e:
        print(f"执行命令失败: {e}")
        return False

def optimize_params(temperature=None, max_tokens=None, timeout=None):
    """优化模型参数"""
    config = load_config()
    if not config:
        return False
        
    if temperature is not None:
        config["models"]["inference"]["temperature"] = temperature
        print(f"温度参数已设置为 {temperature}")
        
    if max_tokens is not None:
        config["models"]["inference"]["max_tokens"] = max_tokens
        print(f"最大生成长度已设置为 {max_tokens}")
        
    if timeout is not None:
        config["models"]["inference"]["timeout_seconds"] = timeout
        print(f"超时时间已设置为 {timeout} 秒")
    
    return save_config(config)

def show_current_config():
    """显示当前配置"""
    config = load_config()
    if not config:
        return
        
    inference_config = config["models"]["inference"]
    embedding_config = config["models"]["embedding"]
    
    print("=== 当前模型配置 ===")
    print(f"推理模型: {inference_config['name']}")
    print(f"嵌入模型: {embedding_config['name']}")
    print("\n参数设置:")
    print(f"温度: {inference_config['temperature']}")
    print(f"最大生成长度: {inference_config['max_tokens']}")
    print(f"超时时间: {inference_config['timeout_seconds']} 秒")
    print(f"最大上下文长度: {inference_config['max_context_length']}")

def main():
    parser = argparse.ArgumentParser(description="模型管理工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # list命令
    list_parser = subparsers.add_parser("list", help="列出已下载的模型")
    
    # switch命令
    switch_parser = subparsers.add_parser("switch", help="切换默认推理模型")
    switch_parser.add_argument("model", help="模型名称")
    
    # download命令
    download_parser = subparsers.add_parser("download", help="下载模型")
    download_parser.add_argument("model", help="模型名称")
    
    # optimize命令
    optimize_parser = subparsers.add_parser("optimize", help="优化模型参数")
    optimize_parser.add_argument("--temperature", type=float, help="温度参数 (0.0-1.0)")
    optimize_parser.add_argument("--max-tokens", type=int, help="最大生成长度")
    optimize_parser.add_argument("--timeout", type=int, help="超时时间 (秒)")
    
    # show命令
    show_parser = subparsers.add_parser("show", help="显示当前配置")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_models()
    elif args.command == "switch":
        switch_model(args.model)
    elif args.command == "download":
        download_model(args.model)
    elif args.command == "optimize":
        optimize_params(args.temperature, args.max_tokens, args.timeout)
    elif args.command == "show":
        show_current_config()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 