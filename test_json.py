import json
import os

def test_json_file(file_path):
    print(f"测试文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"JSON格式正确")
            if "available_models" in data:
                print(f"包含 {len(data['available_models'])} 个模型")
                for i, model in enumerate(data['available_models']):
                    print(f"  {i+1}. {model.get('name', 'Unknown')} - {model.get('description', 'No description')}")
            return True
    except json.JSONDecodeError as e:
        print(f"JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"读取文件错误: {e}")
        return False

# 测试自定义模型列表
custom_models_path = "models/registry/available_models.custom.json"
test_json_file(custom_models_path)

# 测试配置文件
config_path = "config/default/config.json"
test_json_file(config_path) 