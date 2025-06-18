#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CodeAssistant一键启动脚本
自动启动Ollama服务和CodeAssistant Web界面
"""

import os
import sys
import time
import signal
import subprocess
import argparse
import platform
import webbrowser
from pathlib import Path

# 确保可以正确导入模块
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.utils import config, logger
from src.services import ModelServiceFactory, model_manager

# 全局变量，存储进程句柄
ollama_process = None
codeassistant_process = None

def is_windows():
    """检查是否是Windows系统"""
    return platform.system().lower() == "windows"

def check_ollama_installed():
    """检查Ollama是否已安装"""
    try:
        if is_windows():
            cmd = "where ollama"
        else:
            cmd = "which ollama"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def check_ollama_running():
    """检查Ollama服务是否正在运行"""
    try:
        import requests
        api_base = config.get("models.inference.api_base", "http://localhost:11434")
        response = requests.get(f"{api_base}/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

def start_ollama_server():
    """启动Ollama服务"""
    global ollama_process
    
    if check_ollama_running():
        logger.info("Ollama服务已经在运行")
        return True
        
    logger.info("正在启动Ollama服务...")
    
    try:
        if is_windows():
            # Windows下使用start命令启动新窗口
            ollama_process = subprocess.Popen(
                "start cmd.exe /c ollama serve", 
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux/Mac下启动服务
            ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
        # 等待服务启动
        max_retries = 10
        for i in range(max_retries):
            logger.info(f"等待Ollama服务启动 ({i+1}/{max_retries})...")
            time.sleep(1)
            if check_ollama_running():
                logger.info("Ollama服务启动成功")
                return True
                
        logger.error("Ollama服务启动超时")
        return False
    except Exception as e:
        logger.error(f"启动Ollama服务失败: {str(e)}")
        return False

def start_codeassistant():
    """启动CodeAssistant"""
    global codeassistant_process
    
    logger.info("正在启动CodeAssistant...")
    
    try:
        host = config.get("app.host", "localhost")
        port = config.get("app.port", 8080)
        debug = config.get("app.debug", False)
        
        if is_windows():
            # Windows下使用start命令启动新窗口
            cmd = f"start cmd.exe /c python run.py --host {host} --port {port}"
            if debug:
                cmd += " --debug"
                
            codeassistant_process = subprocess.Popen(
                cmd, 
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux/Mac下启动服务
            cmd = ["python", "run.py", "--host", host, "--port", port]
            if debug:
                cmd.append("--debug")
                
            codeassistant_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
        logger.info(f"CodeAssistant启动中，将在 http://{host}:{port} 运行")
        return True
    except Exception as e:
        logger.error(f"启动CodeAssistant失败: {str(e)}")
        return False

def check_models():
    """检查和预加载模型"""
    try:
        import requests
        api_base = config.get("models.inference.api_base", "http://localhost:11434")
        
        response = requests.get(f"{api_base}/api/tags")
        if response.status_code == 200:
            available_models = set(m["name"].split(":")[0] for m in response.json().get("models", []))
            
            # 检查所需模型
            required_models = [
                config.get("models.inference.name", "deepseek-r1:8b"),
                config.get("models.embedding.name", "bge-m3")
            ]
            
            missing_models = []
            for model in required_models:
                model_base = model.split(":")[0]
                if model_base not in available_models:
                    missing_models.append(model)
            
            # 提示下载缺失的模型
            if missing_models:
                logger.warning(f"以下模型尚未下载: {', '.join(missing_models)}")
                logger.info("您可以使用以下命令下载模型:")
                for model in missing_models:
                    logger.info(f"ollama pull {model}")
                    
                return False
            else:
                logger.info("所有必要模型已就绪")
                return True
    except Exception as e:
        logger.error(f"检查模型失败: {str(e)}")
        return False

def signal_handler(sig, frame):
    """处理退出信号"""
    logger.info("正在关闭服务...")
    
    try:
        if codeassistant_process:
            codeassistant_process.terminate()
        
        # 在Windows下，使用taskkill来杀掉Ollama进程
        if is_windows() and ollama_process:
            subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"])
        elif ollama_process:
            ollama_process.terminate()
            
        logger.info("服务已停止")
    except Exception as e:
        logger.error(f"停止服务时出错: {str(e)}")
        
    sys.exit(0)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动CodeAssistant和Ollama服务')
    parser.add_argument('--no-ollama', action='store_true', help='不启动Ollama服务(假设已经运行)')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--host', type=str, help='指定主机名')
    parser.add_argument('--port', type=int, help='指定端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    # 注册信号处理器，确保程序退出时能够关闭服务
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查Ollama是否已安装
    if not check_ollama_installed():
        logger.error("未检测到Ollama安装，请先安装Ollama: https://ollama.com/download")
        return 1
        
    # 设置配置参数
    if args.host:
        config.set("app.host", args.host)
    if args.port:
        config.set("app.port", args.port)
    if args.debug:
        config.set("app.debug", True)
    
    # 启动Ollama服务
    if not args.no_ollama:
        if not start_ollama_server():
            logger.error("启动Ollama服务失败，请手动启动Ollama后再试")
            return 1
    
    # 检查模型
    check_models()
    
    # 启动CodeAssistant
    if not start_codeassistant():
        logger.error("启动CodeAssistant失败")
        return 1
        
    # 等待服务启动
    time.sleep(2)
    
    # 打开浏览器
    if not args.no_browser:
        host = config.get("app.host", "localhost")
        port = config.get("app.port", 8080)
        url = f"http://{host}:{port}"
        
        logger.info(f"正在打开浏览器: {url}")
        webbrowser.open(url)
    
    logger.info("所有服务已启动，按 Ctrl+C 停止")
    
    # 保持脚本运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 