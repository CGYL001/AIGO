import json
import os

try:
    # MCP配置文件路径
    config_path = r'C:\Users\14179\.cursor\mcp.json'
    
    # 读取当前配置
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # 添加AIgo模型管理器配置
    config['mcpServers']['AIgo-model-manager'] = {
        'command': 'python',
        'args': ['D:/AIgo/http_server.py'],
        'timeout': 300,
        'autoApprove': ['model_switch', 'model_optimize']
    }
    
    # 保存更新后的配置
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("配置已成功添加")
except Exception as e:
    print(f"出错了: {e}") 