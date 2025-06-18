import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union

# 默认配置路径
DEFAULT_CONFIG_DIR = Path("config/default")
USER_CONFIG_DIR = Path("config/user")

# 配置缓存
_config_cache: Dict[str, Any] = {}
_loaded_files: Dict[str, float] = {}  # 文件路径 -> 最后修改时间


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，如果为None则加载默认配置
        
    Returns:
        Dict[str, Any]: 配置字典
    """
    global _config_cache, _loaded_files
    
    # 清除缓存
    _config_cache = {}
    _loaded_files = {}
    
    # 加载默认配置
    if os.path.exists(DEFAULT_CONFIG_DIR):
        for file_path in DEFAULT_CONFIG_DIR.glob("*.json"):
            _load_config_file(file_path)
        
        for file_path in DEFAULT_CONFIG_DIR.glob("*.yaml"):
            _load_config_file(file_path)
        
        for file_path in DEFAULT_CONFIG_DIR.glob("*.yml"):
            _load_config_file(file_path)
    
    # 加载用户配置（覆盖默认配置）
    if os.path.exists(USER_CONFIG_DIR):
        for file_path in USER_CONFIG_DIR.glob("*.json"):
            _load_config_file(file_path)
        
        for file_path in USER_CONFIG_DIR.glob("*.yaml"):
            _load_config_file(file_path)
        
        for file_path in USER_CONFIG_DIR.glob("*.yml"):
            _load_config_file(file_path)
    
    # 加载指定配置（覆盖默认和用户配置）
    if config_path and os.path.exists(config_path):
        _load_config_file(Path(config_path))
    
    return _config_cache


def _load_config_file(file_path: Path) -> None:
    """
    加载单个配置文件
    
    Args:
        file_path: 配置文件路径
    """
    global _config_cache, _loaded_files
    
    try:
        # 检查文件是否存在
        if not file_path.exists():
            return
        
        # 检查文件是否已加载且未修改
        mtime = file_path.stat().st_mtime
        if str(file_path) in _loaded_files and _loaded_files[str(file_path)] == mtime:
            return
        
        # 加载配置
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.suffix.lower() == ".json":
                config_data = json.load(f)
            elif file_path.suffix.lower() in [".yaml", ".yml"]:
                config_data = yaml.safe_load(f)
            else:
                return
        
        # 更新缓存
        _update_config_cache(config_data)
        _loaded_files[str(file_path)] = mtime
        
    except Exception as e:
        print(f"加载配置文件失败: {file_path}, 错误: {str(e)}")


def _update_config_cache(config_data: Dict[str, Any], prefix: str = "") -> None:
    """
    更新配置缓存
    
    Args:
        config_data: 配置数据
        prefix: 键前缀
    """
    global _config_cache
    
    for key, value in config_data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            # 递归处理嵌套字典
            _update_config_cache(value, full_key)
        else:
            # 存储值
            _config_cache[full_key] = value


def get(key: str, default: Any = None) -> Any:
    """
    获取配置值
    
    Args:
        key: 配置键
        default: 默认值
        
    Returns:
        Any: 配置值，如果不存在则返回默认值
    """
    global _config_cache
    
    # 如果缓存为空，加载默认配置
    if not _config_cache:
        load_config()
    
    return _config_cache.get(key, default)


def set(key: str, value: Any) -> None:
    """
    设置配置值
    
    Args:
        key: 配置键
        value: 配置值
    """
    global _config_cache
    
    # 如果缓存为空，加载默认配置
    if not _config_cache:
        load_config()
    
    _config_cache[key] = value


def save_user_config() -> bool:
    """
    保存用户配置
    
    Returns:
        bool: 如果保存成功，则返回True
    """
    global _config_cache
    
    try:
        # 确保用户配置目录存在
        os.makedirs(USER_CONFIG_DIR, exist_ok=True)
        
        # 将扁平配置转换为嵌套字典
        nested_config = {}
        for key, value in _config_cache.items():
            parts = key.split(".")
            current = nested_config
            
            # 创建嵌套结构
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    current[part] = value
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
        
        # 保存配置
        user_config_path = USER_CONFIG_DIR / "config.json"
        with open(user_config_path, "w", encoding="utf-8") as f:
            json.dump(nested_config, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"保存用户配置失败: {str(e)}")
        return False


def reset() -> None:
    """重置配置缓存"""
    global _config_cache, _loaded_files
    _config_cache = {}
    _loaded_files = {}


# 初始加载配置
load_config() 