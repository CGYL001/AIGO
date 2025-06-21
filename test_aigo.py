"""
测试AIGO基础功能
"""

import AIGO
from AIGO.models.base import ModelConfig

def main():
    print(f"AIGO版本: {AIGO.__version__}")
    
    # 创建模型配置
    config = ModelConfig(
        provider="ollama",
        model_name="llama2:7b-chat-q4_K_M",
        api_base="http://localhost:11434"
    )
    print(f"模型配置: {config}")
    
    # 注意：要运行以下代码，需要先安装并启动Ollama服务
    
    # # 创建模型运行器
    # from AIGO.models.base import get_model_runner
    # runner = get_model_runner(config)
    # print(f"模型运行器: {runner.__class__.__name__}")
    
    # # 加载模型
    # runner.load()
    # print("模型已加载")
    
    # # 生成文本
    # response = runner.generate("你好，请介绍一下自己。")
    # print(f"模型响应: {response}")
    
if __name__ == "__main__":
    main() 