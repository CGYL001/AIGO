#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AIgo 配置更新工具

此脚本用于管理AIgo的配置文件，可以从环境变量更新配置，
或生成默认配置文件和环境变量示例文件。
"""

import os
import sys
import json
import argparse
from pathlib import Path
import shutil
from typing import Dict, Any, Optional, List, Union

# 默认配置路径
CONFIG_DIR = Path("config")
DEFAULT_CONFIG_DIR = CONFIG_DIR / "default"
USER_CONFIG_DIR = CONFIG_DIR / "user"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"
USER_CONFIG_FILE = USER_CONFIG_DIR / "config.json"
ENV_EXAMPLE_FILE = Path(".env.example")

# 环境变量映射到配置的路径
ENV_TO_CONFIG_MAPPING = {
    "APP_ENV": "app.environment",
    "APP_DEBUG": "app.debug",
    "APP_HOST": "app.host",
    "APP_PORT": "app.port",
    "OLLAMA_API_BASE": "models.inference.api_base",
    "OPENAI_API_KEY": "ai_integration.api_key",
    "OPENAI_API_BASE": "ai_integration.provider_base_url",
    "DB_TYPE": "storage.type",
    "DB_PATH": "storage.path",
    "JWT_SECRET_KEY": "security.jwt.secret_key",
    "ADMIN_USERNAME": "user_management.default_admin_username",
    "ADMIN_PASSWORD": "user_management.default_admin_password",
    "ADMIN_EMAIL": "user_management.default_admin_email",
    "MONITORING_ENABLED": "system_monitor.enabled",
    "CHECK_INTERVAL_SECONDS": "system_monitor.check_interval_seconds",
    "LOG_LEVEL": "logging.level", 
    "LOG_FILE": "logging.file"
}

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AIgo 配置管理工具")
    parser.add_argument("--create-default", action="store_true", help="创建默认配置文件")
    parser.add_argument("--create-env-example", action="store_true", help="创建环境变量示例文件")
    parser.add_argument("--update-from-env", action="store_true", help="从环境变量更新配置")
    parser.add_argument("--check", action="store_true", help="检查配置有效性")
    return parser.parse_args()

def ensure_directories():
    """确保必要的目录存在"""
    USER_CONFIG_DIR.mkdir(exist_ok=True, parents=True)
    
def load_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        Dict[str, Any]: 加载的JSON对象
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON解析错误
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_config(config_file: Path) -> Dict[str, Any]:
    """加载配置文件"""
    if not config_file.exists():
        print(f"错误: 配置文件不存在: {config_file}")
        return {}
        
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"错误: 配置文件格式不正确: {config_file}")
        return {}
    except Exception as e:
        print(f"错误: 读取配置文件时出错: {e}")
        return {}

def save_config(config: Dict[str, Any], config_file: Path) -> bool:
    """保存配置文件"""
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"配置已保存至: {config_file}")
        return True
    except Exception as e:
        print(f"错误: 保存配置文件时出错: {e}")
        return False

def get_from_nested_dict(d: Dict[str, Any], path: str) -> Any:
    """从嵌套字典中获取值"""
    keys = path.split(".")
    result = d
    for key in keys:
        if key in result:
            result = result[key]
        else:
            return None
    return result

def set_in_nested_dict(d: Dict[str, Any], path: str, value: Any) -> None:
    """在嵌套字典中设置值"""
    keys = path.split(".")
    current = d
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value

def create_default_config():
    """创建默认配置文件"""
    if not DEFAULT_CONFIG_FILE.exists():
        print(f"错误: 默认配置文件不存在: {DEFAULT_CONFIG_FILE}")
        return False
        
    # 复制默认配置到用户配置
    try:
        shutil.copy(DEFAULT_CONFIG_FILE, USER_CONFIG_FILE)
        print(f"已创建用户配置文件: {USER_CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"错误: 创建用户配置文件时出错: {e}")
        return False

def create_env_example():
    """创建环境变量示例文件"""
    env_content = """# AIgo 环境变量配置示例
# 复制此文件为 .env 并根据自己的环境进行配置

# 应用配置
APP_ENV=development  # development, production
APP_DEBUG=true
APP_HOST=localhost
APP_PORT=8080

# 模型服务配置
OLLAMA_API_BASE=http://localhost:11434
OPENAI_API_KEY=your_openai_api_key  # 如果使用OpenAI模型
OPENAI_API_BASE=https://api.openai.com/v1  # 可选，用于自定义API地址

# 数据库配置
DB_TYPE=sqlite  # sqlite, mysql, postgresql
DB_PATH=data/user_data/codeassistant.db  # 仅用于SQLite
DB_HOST=localhost  # MySQL/PostgreSQL
DB_PORT=3306  # MySQL默认端口
DB_NAME=aigo  # 数据库名
DB_USER=dbuser  # 数据库用户
DB_PASSWORD=dbpassword  # 数据库密码

# 安全配置
JWT_SECRET_KEY=change_this_to_a_random_string  # 用于JWT令牌签名
ADMIN_USERNAME=admin  # 默认管理员用户名
ADMIN_PASSWORD=change_this_password  # 默认管理员密码
ADMIN_EMAIL=admin@example.com  # 默认管理员邮箱

# 系统监控配置
MONITORING_ENABLED=true
CHECK_INTERVAL_SECONDS=300

# 日志配置
LOG_LEVEL=info  # debug, info, warning, error, critical
LOG_FILE=logs/aigo.log
"""

    try:
        with open(ENV_EXAMPLE_FILE, "w", encoding="utf-8") as f:
            f.write(env_content)
        print(f"已创建环境变量示例文件: {ENV_EXAMPLE_FILE}")
        return True
    except Exception as e:
        print(f"错误: 创建环境变量示例文件时出错: {e}")
        return False

def update_config_from_env():
    """从环境变量更新配置"""
    # 确保用户配置存在
    if not USER_CONFIG_FILE.exists():
        create_default_config()
        
    # 加载用户配置
    config = load_config(USER_CONFIG_FILE)
    if not config:
        return False
        
    # 从环境变量更新配置
    updated = False
    for env_var, config_path in ENV_TO_CONFIG_MAPPING.items():
        if env_var in os.environ:
            # 获取环境变量值
            env_value = os.environ[env_var]
            
            # 转换类型
            current_value = get_from_nested_dict(config, config_path)
            if current_value is not None:
                if isinstance(current_value, bool):
                    env_value = env_value.lower() in ("true", "yes", "1")
                elif isinstance(current_value, int):
                    env_value = int(env_value)
                elif isinstance(current_value, float):
                    env_value = float(env_value)
            
            # 设置值
            set_in_nested_dict(config, config_path, env_value)
            updated = True
            print(f"从环境变量 {env_var} 更新配置: {config_path} = {env_value}")
    
    # 保存配置
    if updated:
        save_config(config, USER_CONFIG_FILE)
        print("已从环境变量更新配置")
        return True
    else:
        print("未找到相关环境变量，配置未更改")
        return False

def check_config():
    """检查配置有效性"""
    # 加载配置
    default_config = load_config(DEFAULT_CONFIG_FILE)
    if not default_config:
        print("错误: 无法加载默认配置")
        return False
        
    user_config = load_config(USER_CONFIG_FILE)
    if not user_config:
        print("警告: 无法加载用户配置，将使用默认配置")
    
    # 检查必要的配置项
    essential_keys = ["app.name", "app.version", "models.inference.provider"]
    for key in essential_keys:
        value = get_from_nested_dict(user_config, key) or get_from_nested_dict(default_config, key)
        if not value:
            print(f"警告: 缺少必要的配置项: {key}")
    
    print("配置检查完成")
    return True

def main():
    """主函数"""
    args = parse_args()
    
    # 确保目录存在
    ensure_directories()
    
    if args.create_default:
        create_default_config()
    elif args.create_env_example:
        create_env_example()
    elif args.update_from_env:
        update_config_from_env()
    elif args.check:
        check_config()
    else:
        print("请指定操作参数。使用 --help 查看帮助信息。")

if __name__ == "__main__":
    main() 