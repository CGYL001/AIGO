"""
配置验证工具

提供配置文件验证功能，确保配置文件的正确性
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigValidator:
    """
    配置验证器
    
    验证配置文件的正确性，确保必要的配置项存在且类型正确
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化配置验证器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config_path = config_path or "config/default/config.json"
        self.schema_path = "config/default/schema.json"
        self.errors = []
        self.warnings = []
        
    def validate(self) -> bool:
        """
        验证配置文件
        
        Returns:
            bool: 验证是否通过
        """
        self.errors = []
        self.warnings = []
        
        # 检查配置文件是否存在
        if not os.path.exists(self.config_path):
            self.errors.append(f"配置文件不存在: {self.config_path}")
            return False
        
        # 读取配置文件
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"配置文件格式错误: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"读取配置文件失败: {str(e)}")
            return False
        
        # 读取模式文件（如果存在）
        schema = None
        if os.path.exists(self.schema_path):
            try:
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
            except Exception as e:
                self.warnings.append(f"读取模式文件失败: {str(e)}")
        
        # 验证必要的配置项
        self._validate_required_fields(config)
        
        # 验证配置项类型
        self._validate_types(config)
        
        # 验证路径配置
        self._validate_paths(config)
        
        # 验证模型配置
        self._validate_model_config(config)
        
        # 验证仓库集成配置
        self._validate_repo_integration(config)
        
        # 如果有模式文件，进行模式验证
        if schema:
            self._validate_against_schema(config, schema)
        
        # 返回验证结果
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """
        获取验证错误信息
        
        Returns:
            List[str]: 错误信息列表
        """
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """
        获取验证警告信息
        
        Returns:
            List[str]: 警告信息列表
        """
        return self.warnings
    
    def _validate_required_fields(self, config: Dict[str, Any]):
        """
        验证必要的配置项
        
        Args:
            config: 配置字典
        """
        required_fields = [
            "app.host",
            "app.port",
            "models.inference.name",
            "models.embedding.name",
            "knowledge_base.storage_path"
        ]
        
        for field in required_fields:
            parts = field.split(".")
            current = config
            
            for part in parts:
                if not isinstance(current, dict) or part not in current:
                    self.errors.append(f"缺少必要的配置项: {field}")
                    break
                current = current[part]
    
    def _validate_types(self, config: Dict[str, Any]):
        """
        验证配置项类型
        
        Args:
            config: 配置字典
        """
        type_checks = [
            ("app.host", str),
            ("app.port", int),
            ("app.debug", bool),
            ("models.inference.name", str),
            ("models.embedding.name", str),
            ("knowledge_base.storage_path", str),
            ("repository_integration.local_repo_path", str)
        ]
        
        for field, expected_type in type_checks:
            parts = field.split(".")
            current = config
            
            try:
                for part in parts[:-1]:
                    if not isinstance(current, dict) or part not in current:
                        break
                    current = current[part]
                
                if isinstance(current, dict) and parts[-1] in current:
                    value = current[parts[-1]]
                    if not isinstance(value, expected_type):
                        self.errors.append(
                            f"配置项 {field} 类型错误，期望 {expected_type.__name__}，"
                            f"实际为 {type(value).__name__}"
                        )
            except Exception as e:
                self.warnings.append(f"验证配置项 {field} 类型时出错: {str(e)}")
    
    def _validate_paths(self, config: Dict[str, Any]):
        """
        验证路径配置
        
        Args:
            config: 配置字典
        """
        path_fields = [
            "knowledge_base.storage_path",
            "repository_integration.local_repo_path",
            "repository_integration.settings_path",
            "repository_integration.audit_log_path"
        ]
        
        for field in path_fields:
            parts = field.split(".")
            current = config
            
            try:
                for part in parts[:-1]:
                    if not isinstance(current, dict) or part not in current:
                        break
                    current = current[part]
                
                if isinstance(current, dict) and parts[-1] in current:
                    path = current[parts[-1]]
                    if not isinstance(path, str):
                        self.errors.append(f"路径配置项 {field} 必须为字符串")
                    elif path.startswith("/"):
                        # 检查绝对路径是否存在
                        if not os.path.exists(path):
                            self.warnings.append(f"路径 {path} 不存在，将在运行时创建")
            except Exception as e:
                self.warnings.append(f"验证路径配置项 {field} 时出错: {str(e)}")
    
    def _validate_model_config(self, config: Dict[str, Any]):
        """
        验证模型配置
        
        Args:
            config: 配置字典
        """
        if "models" not in config:
            self.errors.append("缺少模型配置")
            return
        
        models_config = config["models"]
        
        # 检查推理模型配置
        if "inference" not in models_config:
            self.errors.append("缺少推理模型配置")
        elif "name" not in models_config["inference"]:
            self.errors.append("缺少推理模型名称")
        
        # 检查嵌入模型配置
        if "embedding" not in models_config:
            self.errors.append("缺少嵌入模型配置")
        elif "name" not in models_config["embedding"]:
            self.errors.append("缺少嵌入模型名称")
    
    def _validate_repo_integration(self, config: Dict[str, Any]):
        """
        验证仓库集成配置
        
        Args:
            config: 配置字典
        """
        if "repository_integration" not in config:
            self.warnings.append("缺少仓库集成配置，将使用默认配置")
            return
        
        repo_config = config["repository_integration"]
        
        # 检查平台配置
        if "platforms" not in repo_config:
            self.warnings.append("缺少平台配置，将使用默认配置")
        else:
            platforms = repo_config["platforms"]
            
            # 检查各平台配置
            for platform in ["github", "gitlab", "gitee"]:
                if platform not in platforms:
                    self.warnings.append(f"缺少 {platform} 平台配置，将使用默认配置")
                elif "enabled" not in platforms[platform]:
                    self.warnings.append(f"缺少 {platform} 平台启用状态配置，将默认启用")
                elif "api_url" not in platforms[platform]:
                    self.warnings.append(f"缺少 {platform} 平台API URL配置，将使用默认URL")
    
    def _validate_against_schema(self, config: Dict[str, Any], schema: Dict[str, Any]):
        """
        根据模式验证配置
        
        Args:
            config: 配置字典
            schema: 模式字典
        """
        try:
            import jsonschema
            jsonschema.validate(config, schema)
        except ImportError:
            self.warnings.append("缺少jsonschema库，无法进行模式验证")
        except jsonschema.exceptions.ValidationError as e:
            self.errors.append(f"配置不符合模式: {e.message}")
        except Exception as e:
            self.errors.append(f"模式验证失败: {str(e)}")

def validate_config(config_path: str = None) -> Tuple[bool, List[str], List[str]]:
    """
    验证配置文件
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        Tuple[bool, List[str], List[str]]: (验证是否通过, 错误信息列表, 警告信息列表)
    """
    validator = ConfigValidator(config_path)
    is_valid = validator.validate()
    return is_valid, validator.get_errors(), validator.get_warnings()

if __name__ == "__main__":
    # 如果直接运行此脚本，则验证默认配置文件
    is_valid, errors, warnings = validate_config()
    
    if is_valid:
        print("配置验证通过!")
    else:
        print("配置验证失败:")
        for error in errors:
            print(f"- 错误: {error}")
    
    if warnings:
        print("\n警告:")
        for warning in warnings:
            print(f"- 警告: {warning}") 