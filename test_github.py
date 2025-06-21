"""
测试GitHub配置的简单脚本
"""

import os
import json
from pathlib import Path

# 打印GitHub凭据文件
creds_path = Path("data/credentials/github_token.json")
if creds_path.exists():
    try:
        with open(creds_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("GitHub凭据文件存在!")
            print(f"用户名: {data.get('user_info', {}).get('login', 'unknown')}")
            print(f"Token可用: {'是' if data.get('token') else '否'}")
    except Exception as e:
        print(f"读取凭据文件时出错: {e}")
else:
    print("GitHub凭据文件不存在!")

# 打印配置文件中的GitHub设置
config_path = Path("config/default/config.json")
if config_path.exists():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 检查配置
            if 'repository_integration' in data:
                print("\n仓库集成配置:")
                print(f"启用状态: {data['repository_integration'].get('enabled', False)}")
                
            if 'repo_integration' in data and 'github' in data['repo_integration']:
                github_config = data['repo_integration']['github']
                print("\nGitHub配置:")
                print(f"启用状态: {github_config.get('enabled', False)}")
                print(f"API URL: {github_config.get('api_url', '')}")
                print(f"Token配置: {'是' if github_config.get('token') else '否'}")
            else:
                print("\n配置文件中未找到GitHub配置!")
    except Exception as e:
        print(f"读取配置文件时出错: {e}")
else:
    print("配置文件不存在!")

print("\n配置检查完成!") 