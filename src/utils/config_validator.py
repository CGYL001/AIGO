#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置验证器模块

提供配置文件验证功能
"""

import os
import json
import logging
import jsonschema
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)

def validate_config(config: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> bool:
    """验证配置是否符合模式
    
    Args:
        config: 要验证的配置
        schema: JSON Schema模式
    
    Returns:
        bool: 验证是否通过
    """
    try:
        if schema is None:
            # 如果没有提供模式，则使用默认模式
            schema = get_default_schema()
        
        jsonschema.validate(instance=config, schema=schema)
        logger.info("配置验证通过")
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"配置验证失败: {e.message}")
        return False
    except Exception as e:
        logger.error(f"配置验证出错: {str(e)}")
        return False

def get_default_schema() -> Dict[str, Any]:
    """获取默认配置模式
    
    Returns:
        Dict[str, Any]: 默认配置模式
    """
    return {
        "type": "object",
        "required": ["app", "models"],
        "properties": {
            "app": {
                "type": "object",
                "required": ["name", "version"],
                "properties": {
                    "name": {"type": "string"},
                    "version": {"type": "string"}
                }
            },
            "models": {
                "type": "object",
                "required": ["default"],
                "properties": {
                    "default": {"type": "string"}
                }
            }
        }
    }

def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        Dict[str, Any]: 配置数据
    
    Raises:
        FileNotFoundError: 配置文件不存在
        json.JSONDecodeError: 配置文件格式错误
    """
    try:
        if not os.path.exists(config_path):
            logger.error(f"配置文件不存在: {config_path}")
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"已加载配置文件: {config_path}")
        return config
    except json.JSONDecodeError as e:
        logger.error(f"配置文件格式错误: {config_path}, {str(e)}")
        raise
    except Exception as e:
        logger.error(f"加载配置文件失败: {config_path}, {str(e)}")
        raise

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """保存配置文件
    
    Args:
        config: 配置数据
        config_path: 配置文件路径
    
    Returns:
        bool: 是否成功保存
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"已保存配置文件: {config_path}")
        return True
    except Exception as e:
        logger.error(f"保存配置文件失败: {config_path}, {str(e)}")
        return False

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """合并配置
    
    Args:
        base_config: 基础配置
        override_config: 覆盖配置
    
    Returns:
        Dict[str, Any]: 合并后的配置
    """
    result = base_config.copy()
    
    def _merge(target, source):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                _merge(target[key], value)
            else:
                target[key] = value
    
    _merge(result, override_config)
    return result

def get_nested_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
    """获取嵌套配置值
    
    Args:
        config: 配置数据
        path: 配置路径，使用点号分隔
        default: 默认值
    
    Returns:
        Any: 配置值
    """
    keys = path.split('.')
    current = config
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current

def set_nested_value(config: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """设置嵌套配置值
    
    Args:
        config: 配置数据
        path: 配置路径，使用点号分隔
        value: 要设置的值
    
    Returns:
        Dict[str, Any]: 更新后的配置
    """
    keys = path.split('.')
    current = config
    
    # 遍历路径中的所有键，除了最后一个
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    # 设置最后一个键的值
    current[keys[-1]] = value
    
    return config

# 添加到模块中的现有函数
# ... existing code ... 