#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型管理面板

用于可视化查看和管理项目中的模型
"""

import os
import sys
import json
import time
import datetime
import argparse
import webbrowser
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import http.server
import socketserver
from functools import partial

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# 模型注册表路径
REGISTRY_DIR = ROOT_DIR / "models" / "registry"
MODELS_DIR = REGISTRY_DIR / "models"
AVAILABLE_MODELS_PATH = REGISTRY_DIR / "available_models.json"
MODEL_CATEGORIES_PATH = REGISTRY_DIR / "model_categories.json"

# 模型管理工具路径
MODEL_MANAGER_PATH = ROOT_DIR / "model_manager.py"

# 确保目录存在
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class ModelDashboard:
    """模型管理面板类"""
    
    def __init__(self):
        """初始化"""
        self.registry_dir = REGISTRY_DIR
        self.available_models = self._load_available_models()
        self.model_categories = self._load_model_categories()
        self.current_model = self._get_current_model()
    
    def _load_available_models(self) -> Dict[str, Any]:
        """加载可用模型列表"""
        if AVAILABLE_MODELS_PATH.exists():
            try:
                with open(AVAILABLE_MODELS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"警告: 无法解析可用模型文件: {e}")
        
        # 返回空数据
        return {"last_updated": "", "available_models": []}
    
    def _load_model_categories(self) -> Dict[str, Any]:
        """加载模型分类信息"""
        if MODEL_CATEGORIES_PATH.exists():
            try:
                with open(MODEL_CATEGORIES_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"警告: 无法解析模型分类文件: {e}")
        
        # 返回空数据
        return {}
    
    def _get_current_model(self) -> str:
        """获取当前使用的模型"""
        config_path = ROOT_DIR / "config" / "default" / "config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("models", {}).get("inference", {}).get("name", "unknown")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"警告: 无法解析配置文件: {e}")
        
        return "unknown"
    
    def _get_model_status(self, model_name: str) -> Dict[str, Any]:
        """获取模型状态"""
        # 尝试运行model_manager.py list命令获取已下载的模型
        try:
            result = subprocess.run(
                [sys.executable, str(MODEL_MANAGER_PATH), "list"],
                capture_output=True, text=True
            )
            output = result.stdout
            
            # 检查模型是否已下载
            downloaded = model_name in output
            
            # 检查是否是当前模型
            is_current = model_name == self.current_model
            
            return {
                "downloaded": downloaded,
                "is_current": is_current
            }
        except Exception as e:
            print(f"警告: 无法获取模型状态: {e}")
            return {"downloaded": False, "is_current": False}
    
    def generate_html_report(self) -> str:
        """生成HTML报告"""
        models = self.available_models.get("available_models", [])
        last_updated = self.available_models.get("last_updated", "未知")
        
        # 为每个模型添加状态信息
        for model in models:
            model_status = self._get_model_status(model["name"])
            model.update(model_status)
        
        # 按类型分组模型
        inference_models = [m for m in models if m.get("type") == "inference"]
        embedding_models = [m for m in models if m.get("type") == "embedding"]
        other_models = [m for m in models if m.get("type") not in ["inference", "embedding"]]
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIgo模型管理面板</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2980b9;
            margin-top: 30px;
        }}
        .model-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .model-card {{
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            transition: all 0.3s ease;
            position: relative;
        }}
        .model-card:hover {{
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .current-model {{
            border: 2px solid #27ae60;
            background-color: #e8f8f5;
        }}
        .current-badge {{
            position: absolute;
            top: -10px;
            right: 10px;
            background-color: #27ae60;
            color: white;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
        }}
        .not-downloaded {{
            opacity: 0.7;
        }}
        .model-name {{
            font-weight: bold;
            font-size: 1.2em;
            margin-bottom: 5px;
            color: #2c3e50;
        }}
        .model-description {{
            margin-bottom: 10px;
            color: #555;
        }}
        .model-meta {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 10px;
        }}
        .tag {{
            display: inline-block;
            background-color: #e1f0fa;
            color: #3498db;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-bottom: 5px;
        }}
        .tag-container {{
            margin-top: 10px;
        }}
        .buttons {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }}
        .btn {{
            padding: 5px 10px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s ease;
        }}
        .btn-primary {{
            background-color: #3498db;
            color: white;
        }}
        .btn-success {{
            background-color: #2ecc71;
            color: white;
        }}
        .btn-secondary {{
            background-color: #95a5a6;
            color: white;
        }}
        .btn:hover {{
            opacity: 0.8;
        }}
        footer {{
            margin-top: 40px;
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AIgo模型管理面板</h1>
        
        <p>该面板提供对系统中可用模型的总览和管理功能。当前系统正在使用 <strong>{self.current_model}</strong> 模型。</p>
        <p>最后更新时间: {last_updated}</p>
        
        <h2>推理模型</h2>
        <div class="model-grid">
"""
        
        # 添加推理模型卡片
        for model in inference_models:
            html += self._generate_model_card(model)
        
        html += """
        </div>
        
        <h2>嵌入模型</h2>
        <div class="model-grid">
"""
        
        # 添加嵌入模型卡片
        for model in embedding_models:
            html += self._generate_model_card(model)
        
        if other_models:
            html += """
            </div>
            
            <h2>其他模型</h2>
            <div class="model-grid">
    """
            
            # 添加其他模型卡片
            for model in other_models:
                html += self._generate_model_card(model)
        
        html += """
        </div>
        
        <footer>
            <p>AIgo模型管理面板 &copy; 2023</p>
        </footer>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_model_card(self, model: Dict[str, Any]) -> str:
        """生成模型卡片HTML"""
        model_name = model.get("name", "未知")
        description = model.get("description", "无描述")
        model_type = model.get("type", "未知")
        model_size = model.get("size", "未知")
        tags = model.get("tags", [])
        is_current = model.get("is_current", False)
        downloaded = model.get("downloaded", False)
        
        card_class = "model-card"
        if is_current:
            card_class += " current-model"
        if not downloaded:
            card_class += " not-downloaded"
        
        current_badge = ""
        if is_current:
            current_badge = '<span class="current-badge">当前</span>'
        
        download_or_switch_btn = ""
        if downloaded:
            if not is_current:
                download_or_switch_btn = f'<button class="btn btn-primary" onclick="alert(\'请运行: python model_manager.py switch {model_name}\')">切换到此模型</button>'
        else:
            download_or_switch_btn = f'<button class="btn btn-secondary" onclick="alert(\'请运行: python model_manager.py download {model_name}\')">下载</button>'
        
        tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in tags])
        
        return f"""
        <div class="{card_class}">
            {current_badge}
            <div class="model-name">{model_name}</div>
            <div class="model-description">{description}</div>
            <div class="model-meta">类型: {model_type} | 大小: {model_size}</div>
            <div class="tag-container">
                {tags_html}
            </div>
            <div class="buttons">
                {download_or_switch_btn}
                <button class="btn btn-secondary" onclick="alert('查看模型详情')">详情</button>
            </div>
        </div>
        """
    
    def start_server(self, host: str = "localhost", port: int = 8000):
        """启动HTTP服务器显示报告"""
        report_html = self.generate_html_report()
        
        # 创建临时目录并保存HTML文件
        temp_dir = Path(ROOT_DIR) / "temp" / "models_dashboard"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        html_path = temp_dir / "index.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(report_html)
        
        # 创建HTTP服务器
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(temp_dir))
        
        try:
            with socketserver.TCPServer((host, port), handler) as httpd:
                url = f"http://{host}:{port}"
                print(f"模型管理面板已启动: {url}")
                
                # 尝试在浏览器中打开
                try:
                    webbrowser.open(url)
                except:
                    print("无法自动打开浏览器，请手动访问上述URL")
                
                print("按Ctrl+C停止服务器...")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("服务器已停止")
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"端口 {port} 已被占用，请尝试其他端口")
            else:
                print(f"启动服务器时出错: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AIgo模型管理面板")
    
    parser.add_argument("--host", type=str, default="localhost",
                      help="服务器主机名")
    parser.add_argument("--port", type=int, default=8000,
                      help="服务器端口")
    
    args = parser.parse_args()
    
    # 创建模型面板
    dashboard = ModelDashboard()
    
    # 启动服务器
    dashboard.start_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main() 