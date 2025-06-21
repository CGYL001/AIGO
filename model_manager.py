#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型管理工具
用于切换、管理和下载Ollama模型
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
import requests
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("model_manager")

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

# 支持通过环境变量配置路径
DEFAULT_CONFIG_DIR = os.environ.get(
    "AIGO_CONFIG_DIR", 
    str(ROOT_DIR / "config" / "default")
)
CONFIG_PATH = Path(os.environ.get(
    "AIGO_CONFIG_FILE", 
    str(Path(DEFAULT_CONFIG_DIR) / "config.json")
))

# 重试设置
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # 指数退避的基数

# 添加新的路径
REGISTRY_PATH = ROOT_DIR / "models" / "registry"
DEFAULT_DOWNLOAD_DIR = ROOT_DIR / "models" / "downloads"

class ConfigError(Exception):
    """配置相关错误"""
    pass

class ModelError(Exception):
    """模型相关错误"""
    pass

def ensure_config_dir():
    """确保配置目录存在"""
    config_dir = CONFIG_PATH.parent
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建配置目录失败: {e}")
        return False

def load_config() -> Dict[str, Any]:
    """加载配置文件，如果不存在则创建默认配置"""
    ensure_config_dir()
    
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 创建默认配置
            default_config = {
                "models": {
                    "inference": {
                        "name": "deepseek-r1:8b",
                        "provider": "ollama",
                        "api_base": "http://localhost:11434",
                        "temperature": 0.7,
                        "max_tokens": 2048,
                        "timeout_seconds": 60,
                        "max_context_length": 4096
                    },
                    "embedding": {
                        "name": "bge-m3",
                        "provider": "ollama",
                        "api_base": "http://localhost:11434",
                        "dimensions": 1024
                    }
                }
            }
            save_config(default_config)
            logger.info(f"已创建默认配置文件: {CONFIG_PATH}")
            return default_config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        raise ConfigError(f"无法加载配置文件: {e}")

def save_config(config: Dict[str, Any]) -> bool:
    """保存配置文件"""
    ensure_config_dir()
    
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logger.info(f"配置已保存到 {CONFIG_PATH}")
        return True
    except Exception as e:
        logger.error(f"保存配置文件失败: {e}")
        raise ConfigError(f"无法保存配置文件: {e}")

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """使用重试机制进行API请求"""
    config = load_config()
    api_base = config["models"]["inference"]["api_base"]
    url = f"{api_base}/api/{endpoint}"
    
    retries = 0
    last_error = None
    
    while retries < MAX_RETRIES:
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            else:  # POST
                response = requests.post(url, json=data, timeout=10)
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            last_error = e
            wait_time = RETRY_BACKOFF ** retries
            logger.warning(f"API请求失败，将在{wait_time}秒后重试: {e}")
            time.sleep(wait_time)
            retries += 1
    
    # 所有重试都失败
    error_msg = f"API请求在{MAX_RETRIES}次尝试后失败: {last_error}"
    logger.error(error_msg)
    raise ModelError(error_msg)

def list_models() -> List[Dict[str, str]]:
    """列出所有已下载的模型并返回模型列表"""
    try:
        # 优先使用API获取
        try:
            result = make_api_request("tags")
            models = result.get("models", [])
            
            if models:
                logger.info(f"已下载的模型: {len(models)}个")
                # 打印模型信息
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0) // (1024 * 1024)  # 转换为MB
                    modified = model.get("modified_at", "unknown")
                    print(f"- {name} ({size}MB, 修改时间: {modified})")
                return models
        except Exception as e:
            logger.warning(f"通过API获取模型列表失败，将使用命令行: {e}")
        
        # 回退到命令行
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info("已下载的模型:")
            print(output)
            
            # 解析命令行输出，转换为统一格式
            models = []
            for line in output.splitlines()[1:]:  # 跳过标题行
                parts = line.split()
                if len(parts) >= 2:
                    models.append({"name": parts[0], "size": parts[1]})
            return models
        else:
            error_msg = f"获取模型列表失败: {result.stderr}"
            logger.error(error_msg)
            raise ModelError(error_msg)
    except Exception as e:
        logger.error(f"列出模型时出错: {e}")
        print(f"错误: {e}")
        return []

def switch_model(model_name: str) -> bool:
    """切换默认推理模型"""
    try:
        config = load_config()
        current_model = config["models"]["inference"]["name"]
        
        if current_model == model_name:
            logger.info(f"当前已经使用的是 {model_name} 模型")
            return True
            
        # 检查模型是否已下载
        available_models = [m.get("name", "").split(":")[0] for m in list_models()]
        model_base = model_name.split(":")[0]
        
        if model_base not in available_models and model_name not in available_models:
            logger.warning(f"模型 {model_name} 未下载，请先下载")
            return False
            
        # 更新配置
        config["models"]["inference"]["name"] = model_name
        logger.info(f"默认推理模型已从 {current_model} 切换为 {model_name}")
        
        return save_config(config)
    except Exception as e:
        logger.error(f"切换模型时出错: {e}")
        return False

def download_model(model_name: str) -> bool:
    """下载模型，使用进度指示"""
    try:
        logger.info(f"正在下载模型 {model_name}...")
        
        # 使用subprocess来启动下载并实时显示输出
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时显示下载进度
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
            
        # 等待进程完成
        return_code = process.wait()
        
        if return_code == 0:
            logger.info(f"模型 {model_name} 下载成功")
            return True
        else:
            logger.error(f"模型下载失败，返回代码: {return_code}")
            return False
    except Exception as e:
        logger.error(f"下载模型时出错: {e}")
        return False

def optimize_params(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    timeout: Optional[int] = None,
    context_length: Optional[int] = None
) -> bool:
    """优化模型参数"""
    try:
        config = load_config()
        
        changes = []
        if temperature is not None:
            if not 0 <= temperature <= 1:
                logger.warning(f"温度参数应在0-1范围内，已收到: {temperature}")
                return False
            
            config["models"]["inference"]["temperature"] = temperature
            changes.append(f"温度参数: {temperature}")
            
        if max_tokens is not None:
            if max_tokens <= 0:
                logger.warning(f"最大生成长度应为正数，已收到: {max_tokens}")
                return False
                
            config["models"]["inference"]["max_tokens"] = max_tokens
            changes.append(f"最大生成长度: {max_tokens}")
            
        if timeout is not None:
            if timeout <= 0:
                logger.warning(f"超时时间应为正数，已收到: {timeout}")
                return False
                
            config["models"]["inference"]["timeout_seconds"] = timeout
            changes.append(f"超时时间: {timeout}秒")
            
        if context_length is not None:
            if context_length <= 0:
                logger.warning(f"上下文长度应为正数，已收到: {context_length}")
                return False
                
            config["models"]["inference"]["max_context_length"] = context_length
            changes.append(f"最大上下文长度: {context_length}")
        
        if not changes:
            logger.info("没有参数需要更改")
            return True
            
        logger.info("已更新以下参数: " + ", ".join(changes))
        return save_config(config)
    except Exception as e:
        logger.error(f"优化参数时出错: {e}")
        return False

def show_current_config():
    """显示当前配置"""
    try:
        config = load_config()
            
        inference_config = config["models"]["inference"]
        embedding_config = config["models"]["embedding"]
        
        print("\n=== 当前模型配置 ===")
        print(f"配置文件位置: {CONFIG_PATH}")
        print(f"\n推理模型: {inference_config['name']}")
        print(f"提供商: {inference_config.get('provider', 'ollama')}")
        print(f"API地址: {inference_config.get('api_base', 'http://localhost:11434')}")
        
        print("\n参数设置:")
        print(f"温度: {inference_config.get('temperature', 0.7)}")
        print(f"最大生成长度: {inference_config.get('max_tokens', 2048)}")
        print(f"超时时间: {inference_config.get('timeout_seconds', 60)} 秒")
        print(f"最大上下文长度: {inference_config.get('max_context_length', 4096)}")
        
        print(f"\n嵌入模型: {embedding_config['name']}")
        print(f"提供商: {embedding_config.get('provider', 'ollama')}")
        print(f"维度: {embedding_config.get('dimensions', 1024)}")
    except Exception as e:
        logger.error(f"显示配置时出错: {e}")
        print(f"错误: 无法显示配置 - {e}")

def clean_model_metadata():
    """清理模型元数据，保留必要的模板文件"""
    try:
        # 清理models/registry/models目录
        models_dir = REGISTRY_PATH / "models"
        if models_dir.exists():
            for item in models_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
            print(f"已清理 {models_dir} 目录")
            
        # 创建个人模型目录
        personal_dir = models_dir / "my_models"
        personal_dir.mkdir(exist_ok=True)
        print(f"已创建个人模型目录: {personal_dir}")
        
        # 创建自定义模型列表
        available_models = REGISTRY_PATH / "available_models.json"
        custom_models = REGISTRY_PATH / "available_models.custom.json"
        
        if available_models.exists() and not custom_models.exists():
            shutil.copy(available_models, custom_models)
            print(f"已创建自定义模型列表: {custom_models}")
            
        return True
    except Exception as e:
        print(f"清理模型元数据时出错: {e}")
        return False

def setup_model_directory(download_dir=None):
    """设置模型下载目录"""
    config = load_config()
    if not config:
        return False
        
    if download_dir:
        download_path = Path(download_dir)
    else:
        download_path = DEFAULT_DOWNLOAD_DIR
        
    # 创建下载目录
    download_path.mkdir(exist_ok=True, parents=True)
    
    # 更新配置
    if "models" not in config:
        config["models"] = {}
        
    config["models"]["download_directory"] = str(download_path)
    config["models"]["registry"] = str(REGISTRY_PATH / "available_models.custom.json")
    
    print(f"模型下载目录已设置为: {download_path}")
    print(f"模型注册表已设置为: {config['models']['registry']}")
    
    return save_config(config)

def main():
    parser = argparse.ArgumentParser(description="AIgo模型管理工具")
    parser.add_argument("--config", help="指定配置文件路径")
    parser.add_argument("--debug", action="store_true", help="启用调试日志")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
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
    optimize_parser.add_argument("--max-tokens", type=int, help="最大令牌数")
    optimize_parser.add_argument("--timeout", type=int, help="超时时间(秒)")
    
    # show命令
    show_parser = subparsers.add_parser("show", help="显示当前配置")
    
    # clean命令
    clean_parser = subparsers.add_parser("clean", help="清理模型元数据，保留必要的模板文件")
    
    # setup命令
    setup_parser = subparsers.add_parser("setup", help="设置模型下载目录")
    setup_parser.add_argument("--download-dir", help="模型下载目录路径")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # 设置自定义配置文件
    if args.config:
        global CONFIG_PATH
        CONFIG_PATH = Path(args.config)
        logger.info(f"使用自定义配置文件: {CONFIG_PATH}")
    
    try:
        if args.command == "list":
            list_models()
        elif args.command == "switch":
            if switch_model(args.model):
                print(f"已成功切换到模型: {args.model}")
            else:
                print(f"切换到模型 {args.model} 失败")
                sys.exit(1)
        elif args.command == "download":
            if download_model(args.model):
                print(f"已成功下载模型: {args.model}")
            else:
                print(f"下载模型 {args.model} 失败")
                sys.exit(1)
        elif args.command == "optimize":
            if optimize_params(args.temperature, args.max_tokens, args.timeout):
                print("模型参数优化成功")
            else:
                print("模型参数优化失败")
                sys.exit(1)
        elif args.command == "show":
            show_current_config()
        elif args.command == "clean":
            clean_model_metadata()
        elif args.command == "setup":
            setup_model_directory(args.download_dir)
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"执行命令时出错: {e}")
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 