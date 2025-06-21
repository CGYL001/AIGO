import os
import json
from pathlib import Path

def check_directory(path):
    print(f"检查目录: {path}")
    if os.path.exists(path):
        print(f"  目录存在")
        if os.path.isdir(path):
            contents = os.listdir(path)
            print(f"  包含 {len(contents)} 个项目:")
            for item in contents:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    print(f"    [目录] {item}")
                else:
                    size = os.path.getsize(item_path)
                    print(f"    [文件] {item} ({size} 字节)")
        else:
            print(f"  不是目录")
    else:
        print(f"  目录不存在")

def check_config_paths():
    print("\n检查配置文件中的路径:")
    try:
        config_path = "config/default/config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        models_config = config.get("models", {})
        download_dir = models_config.get("download_directory", "")
        registry_path = models_config.get("registry", "")
        custom_registry = models_config.get("custom_registry", "")
        
        print(f"  下载目录: {download_dir}")
        print(f"    存在: {os.path.exists(download_dir)}")
        
        print(f"  注册表路径: {registry_path}")
        print(f"    存在: {os.path.exists(registry_path)}")
        
        print(f"  自定义注册表: {custom_registry}")
        print(f"    存在: {os.path.exists(custom_registry)}")
    except Exception as e:
        print(f"  检查配置路径时出错: {e}")

# 检查主要目录
print("=== 目录检查 ===")
check_directory("models")
check_directory("models/registry")
check_directory("models/registry/models")
check_directory("models/downloads")

# 检查配置文件中的路径
check_config_paths()

# 检查.gitignore文件
print("\n检查.gitignore文件:")
try:
    with open(".gitignore", 'r', encoding='utf-8') as f:
        gitignore = f.read()
    
    patterns = [
        "models/registry/models/*",
        "models/registry/*.custom.json",
        "models/*.custom.json",
        "model_downloads/",
        ".model_cache/",
        "models/downloads/",
        "models/cache/",
        "temp_checkpoints/",
        "temp_training_memory/",
        "checkpoints/"
    ]
    
    for pattern in patterns:
        if pattern in gitignore:
            print(f"  ✓ 包含模式: {pattern}")
        else:
            print(f"  ✗ 缺少模式: {pattern}")
except Exception as e:
    print(f"  检查.gitignore时出错: {e}") 