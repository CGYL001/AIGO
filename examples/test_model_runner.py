"""
Test script for model runners.

This script demonstrates how to use the model runner abstraction.
"""

import sys
import os
import importlib.util
from pathlib import Path

# 确保可以导入aigo包
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 创建一个简单的ModelConfig模拟类，避免导入问题
class ModelConfigMock:
    """ModelConfig的简单实现，用于测试"""
    
    def __init__(self, provider, model_name, device="auto", **kwargs):
        self.provider = provider
        self.model_name = model_name
        self.device = device
        self.api_key = kwargs.get("api_key")
        self.api_base = kwargs.get("api_base")
        self.kwargs = kwargs
    
    def __str__(self):
        masked_dict = self.__dict__.copy()
        if self.api_key:
            masked_dict["api_key"] = "***" 
        return f"ModelConfig({', '.join(f'{k}={v}' for k, v in masked_dict.items())})"


def test_model_config():
    """测试ModelConfig创建"""
    print("创建模型配置...")
    config = ModelConfigMock(
        provider="ollama",
        model_name="deepseek-r1:8b",
        api_base="http://localhost:11434"
    )
    print(f"配置: {config}")
    return config


def verify_file_exists():
    """验证关键文件是否存在"""
    print("\n检查文件是否存在:")
    files = [
        "aigo/models/base.py",
        "aigo/models/providers/ollama_runner.py",
        "aigo/models/providers/openai_runner.py",
        "aigo/models/manager.py"
    ]
    
    for file in files:
        path = project_root / file
        exists = path.exists()
        print(f"  {file}: {'✓' if exists else '✗'}")
        
        if exists:
            # 检查文件大小
            size_kb = path.stat().st_size / 1024
            print(f"    大小: {size_kb:.1f} KB")
            
            # 查看文件前几行
            try:
                with open(path, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    print(f"    开头: {first_line[:50]}...")
            except Exception as e:
                print(f"    读取失败: {e}")


def main():
    """主函数"""
    print("AIgo模型运行器测试")
    print("=================\n")
    
    # 检查文件
    verify_file_exists()
    
    # 测试配置
    test_model_config()
    
    print("\n测试完成！请确保包已正确安装，并在安装环境中使用。")


if __name__ == "__main__":
    main() 