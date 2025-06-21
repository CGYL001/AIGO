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
import logging
import tempfile
import json
import threading
import psutil
import atexit
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple

# 确保可以正确导入模块
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.utils import config, logger
# 添加新的可视化模块支持
try:
    from AIGO.modules.visualization import VisualizationManager
    HAS_VISUALIZATION = True
    visualization_manager = VisualizationManager()
    logger.info("可视化模块加载成功")
    
    # 添加特性集成模块
    try:
        from AIGO.modules.integration import FeatureIntegrator
        feature_integrator = FeatureIntegrator()
        feature_integrator.set_visualization_manager(visualization_manager)
        HAS_FEATURE_INTEGRATION = True
        logger.info("特性集成模块加载成功")
    except ImportError:
        HAS_FEATURE_INTEGRATION = False
        feature_integrator = None
        logger.warning("特性集成模块加载失败，将禁用高级特性集成")
except ImportError:
    HAS_VISUALIZATION = False
    visualization_manager = None
    HAS_FEATURE_INTEGRATION = False
    feature_integrator = None
    logger.warning("可视化模块加载失败，将禁用可视化功能")

# 设置应用日志
log_dir = ROOT_DIR / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "startup.log"

# 设置日志格式
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

startup_logger = logging.getLogger("startup")
startup_logger.setLevel(logging.INFO)
startup_logger.addHandler(file_handler)
startup_logger.addHandler(console_handler)

# 全局变量，存储进程句柄和状态
ollama_process = None
codeassistant_process = None
processes = {}  # 用于跟踪所有启动的进程
stop_event = threading.Event()
health_thread = None

def is_windows():
    """检查是否是Windows系统"""
    return platform.system().lower() == "windows"

def is_process_running(pid):
    """检查进程是否在运行"""
    try:
        if pid is None:
            return False
        process = psutil.Process(pid)
        return process.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def check_ollama_installed():
    """检查Ollama是否已安装"""
    try:
        if is_windows():
            cmd = "where ollama"
        else:
            cmd = "which ollama"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        startup_logger.error(f"检查Ollama安装时出错: {e}")
        return False

def check_ollama_running():
    """检查Ollama服务是否正在运行"""
    try:
        import requests
        api_base = config.get("models.inference.api_base", "http://localhost:11434")
        response = requests.get(f"{api_base}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        startup_logger.debug(f"Ollama服务检查失败: {e}")
        return False

def get_ollama_pid():
    """获取正在运行的Ollama进程PID"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if 'ollama' in proc.info['name'].lower():
                return proc.info['pid']
        return None
    except Exception as e:
        startup_logger.error(f"获取Ollama PID时出错: {e}")
        return None

def start_ollama_server() -> Tuple[bool, Optional[int]]:
    """启动Ollama服务，返回(成功状态, 进程ID)"""
    global ollama_process
    
    # 首先检查Ollama是否已经在运行
    if check_ollama_running():
        pid = get_ollama_pid()
        startup_logger.info(f"Ollama服务已经在运行 (PID: {pid})")
        return True, pid
        
    startup_logger.info("正在启动Ollama服务...")
    
    # 准备日志文件
    ollama_log = log_dir / "ollama.log"
    
    try:
        # 创建日志文件
        with open(ollama_log, 'w', encoding='utf-8') as f:
            f.write(f"启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if is_windows():
            # Windows下使用独立的进程启动
            startup_logger.info("在Windows上启动Ollama服务")
            
            # 创建启动批处理文件
            bat_file = tempfile.NamedTemporaryFile(suffix='.bat', delete=False)
            bat_path = bat_file.name
            
            # 写入批处理文件内容
            with open(bat_path, 'w') as f:
                f.write('@echo off\n')
                f.write(f'echo Ollama服务启动于 %time% > "{ollama_log}"\n')
                f.write(f'ollama serve >> "{ollama_log}" 2>&1\n')
            
            # 使用subprocess启动批处理文件
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0  # 隐藏窗口
            
            ollama_process = subprocess.Popen(
                bat_path,
                shell=True,
                startupinfo=si,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            
            # 记录启动的进程
            pid = ollama_process.pid
            processes["ollama"] = {"process": ollama_process, "pid": pid, "log": str(ollama_log)}
            startup_logger.info(f"Ollama进程已启动 (PID: {pid})")
        else:
            # Linux/Mac下启动服务
            ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=open(ollama_log, 'a'),
                stderr=subprocess.STDOUT
            )
            
            # 记录启动的进程
            pid = ollama_process.pid
            processes["ollama"] = {"process": ollama_process, "pid": pid, "log": str(ollama_log)}
            startup_logger.info(f"Ollama进程已启动 (PID: {pid})")
            
        # 等待服务启动
        max_retries = 10
        for i in range(max_retries):
            startup_logger.info(f"等待Ollama服务启动 ({i+1}/{max_retries})...")
            time.sleep(2)  # 增加等待时间，给服务更多启动时间
            if check_ollama_running():
                startup_logger.info("Ollama服务启动成功")
                return True, pid
                
        startup_logger.error("Ollama服务启动超时，查看日志获取详情")
        return False, None
    except Exception as e:
        startup_logger.error(f"启动Ollama服务失败: {str(e)}")
        return False, None

def check_api_health(host="localhost", port=8080):
    """检查CodeAssistant API是否健康"""
    try:
        import requests
        url = f"http://{host}:{port}/api/health"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        startup_logger.debug(f"API健康检查失败: {e}")
        return False

def start_codeassistant() -> Tuple[bool, Optional[int]]:
    """启动CodeAssistant，返回(成功状态, 进程ID)"""
    global codeassistant_process
    
    startup_logger.info("正在启动CodeAssistant...")
    
    # 准备日志文件
    api_log = log_dir / "codeassistant.log"
    
    try:
        # 创建日志文件
        with open(api_log, 'w', encoding='utf-8') as f:
            f.write(f"启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
        # 获取配置
        host = config.get("app.host", "localhost")
        port = config.get("app.port", 8080)
        debug = config.get("app.debug", False)
        
        # 准备环境变量
        env = os.environ.copy()
        env["HOST"] = host
        env["PORT"] = str(port)
        env["DEBUG"] = "1" if debug else "0"
                
        # 添加可视化支持的环境变量
        if HAS_VISUALIZATION:
            env["ENABLE_VISUALIZATION"] = "1"
        
        # 添加特性集成的环境变量
        if HAS_FEATURE_INTEGRATION:
            env["ENABLE_FEATURE_INTEGRATION"] = "1"
        
        # 准备启动命令
        cmd = [sys.executable, "-m", "src.main"]
        
        startup_logger.info(f"正在启动CodeAssistant服务 (地址: {host}:{port})...")
        
        # 启动CodeAssistant进程
        codeassistant_process = subprocess.Popen(
            cmd,
            env=env,
            stdout=open(api_log, 'a'),
            stderr=subprocess.STDOUT
        )
            
        # 记录启动的进程
        pid = codeassistant_process.pid
        processes["codeassistant"] = {"process": codeassistant_process, "pid": pid, "log": str(api_log)}
        startup_logger.info(f"CodeAssistant进程已启动 (PID: {pid})")
        
        # 等待服务启动
        max_retries = 10
        for i in range(max_retries):
            startup_logger.info(f"等待API服务启动 ({i+1}/{max_retries})...")
            time.sleep(2)
            if check_api_health(host, port):
                startup_logger.info(f"CodeAssistant服务启动成功，API地址: http://{host}:{port}")
                
                # 生成并显示系统资源监控仪表盘
                if HAS_VISUALIZATION and visualization_manager:
                    try:
                        startup_logger.info("正在生成系统资源监控仪表盘...")
                        # 收集系统信息
                        system_info = {
                            "hostname": platform.node(),
                            "os_name": platform.system(),
                            "os_version": platform.version(),
                            "cpu_model": platform.processor(),
                            "cpu_cores": psutil.cpu_count(logical=False),
                            "memory_total": psutil.virtual_memory().total // (1024 * 1024)
                        }
                        
                        # 收集当前指标
                        metrics = {
                            "cpu_usage": psutil.cpu_percent(),
                            "memory_usage": psutil.virtual_memory().percent,
                            "disk_usage": psutil.disk_usage("/").percent,
                            "network_activity": {
                                "current": sum(psutil.net_io_counters()[:2]) / 1024,
                                "previous": 0
                            }
                        }
                        
                        # 创建仪表盘数据
                        dashboard_data = {
                            "metrics": metrics,
                            "system_info": system_info
                        }
                        
                        # 生成仪表盘
                        dashboard_path = visualization_manager.dashboard.visualize(
                            "system_monitor", 
                            dashboard_data, 
                            title="AIgo系统启动监控"
                        )
                        
                        # 记录仪表盘路径，稍后展示
                        env["DASHBOARD_PATH"] = dashboard_path
                        startup_logger.info(f"系统监控仪表盘已生成: {dashboard_path}")
                        
                        # 集成特性并生成功能地图
                        if HAS_FEATURE_INTEGRATION and feature_integrator:
                            try:
                                startup_logger.info("正在集成高级特性...")
                                integration_results = feature_integrator.integrate_features()
                                
                                # 记录集成结果
                                integrated_count = sum(1 for v in integration_results.values() if v)
                                startup_logger.info(f"共集成了 {integrated_count}/{len(integration_results)} 个高级特性")
                                
                                # 创建功能结构图
                                if integrated_count > 0 and hasattr(visualization_manager.structure, "visualize"):
                                    # 构建特性数据
                                    features_data = []
                                    for feature_id, success in integration_results.items():
                                        if success:
                                            feature_info = feature_integrator.enabled_features.get(feature_id, {})
                                            features_data.append({
                                                "id": feature_id,
                                                "name": feature_info.get("name", feature_id),
                                                "enabled": True
                                            })
                                    
                                    # 生成功能地图
                                    map_path = visualization_manager.structure.visualize(
                                        "feature_map",
                                        {
                                            "title": "AIgo高级功能地图",
                                            "features": features_data
                                        },
                                        width=1000,
                                        height=600,
                                        theme="light"
                                    )
                                    
                                    # 记录地图路径
                                    env["FEATURE_MAP_PATH"] = map_path
                                    startup_logger.info(f"功能地图已生成: {map_path}")
                                    
                                    # 如果模型优化特性已集成，生成优化流程图
                                    if integration_results.get("model_optimization"):
                                        optimizer = feature_integrator.get_feature_integrator("model_optimization")
                                        if optimizer:
                                            startup_logger.info("模型优化工具已集成，生成示例可视化...")
                            except Exception as e:
                                startup_logger.error(f"集成高级特性失败: {e}")
                        
                    except Exception as e:
                        startup_logger.error(f"生成仪表盘失败: {e}")
                
                return True, pid
        
        startup_logger.error("CodeAssistant服务启动超时，查看日志获取详情")
        return False, None
        
    except Exception as e:
        startup_logger.error(f"启动CodeAssistant服务失败: {str(e)}")
        return False, None

def health_check_worker():
    """健康检查工作线程"""
    # 设置检查间隔
    check_interval = 10  # 10秒检查一次
    
    startup_logger.info("启动健康检查线程")
    
    try:
        while not stop_event.is_set():
            try:
                # 检查Ollama状态
                ollama_running = False
                if "ollama" in processes:
                    pid = processes["ollama"].get("pid")
                    ollama_running = is_process_running(pid)
                    
                    if not ollama_running and not stop_event.is_set():
                        startup_logger.warning(f"Ollama进程(PID: {pid})已终止，尝试重启")
                        success, new_pid = start_ollama_server()
                        if not success:
                            startup_logger.error("Ollama服务重启失败")
            
                # 检查CodeAssistant状态
                api_running = False
                if "codeassistant" in processes:
                    pid = processes["codeassistant"].get("pid")
                    api_running = is_process_running(pid)
                    
                    if not api_running and not stop_event.is_set():
                        startup_logger.warning(f"CodeAssistant进程(PID: {pid})已终止，尝试重启")
                        success, new_pid = start_codeassistant()
                        if not success:
                            startup_logger.error("CodeAssistant服务重启失败")
                
                # 可视化系统状态
                if HAS_VISUALIZATION and visualization_manager:
                    try:
                        # 每分钟更新一次系统监控可视化
                        if int(time.time()) % 60 < check_interval:
                            # 收集系统信息
                            system_info = {
                                "hostname": platform.node(),
                                "os_name": platform.system(),
                                "os_version": platform.version(),
                                "cpu_model": platform.processor(),
                                "cpu_cores": psutil.cpu_count(logical=False),
                                "memory_total": psutil.virtual_memory().total // (1024 * 1024)
                            }
                            
                            # 收集当前指标
                            metrics = {
                                "cpu_usage": psutil.cpu_percent(),
                                "memory_usage": psutil.virtual_memory().percent,
                                "disk_usage": psutil.disk_usage("/").percent,
                                "network_activity": {
                                    "current": sum(psutil.net_io_counters()[:2]) / 1024,
                                    "previous": 0
                                }
                            }
                            
                            # 创建仪表盘数据
                            dashboard_data = {
                                "metrics": metrics,
                                "system_info": system_info
                            }
                            
                            # 更新仪表盘
                            dashboard_path = visualization_manager.dashboard.visualize(
                                "system_monitor", 
                                dashboard_data, 
                                title="AIgo系统实时监控"
                            )
                            startup_logger.debug(f"系统监控仪表盘已更新")
                    except Exception as e:
                        startup_logger.debug(f"更新系统监控可视化失败: {e}")
            
            except Exception as e:
                startup_logger.error(f"健康检查线程出错: {str(e)}")
            
            # 等待下一次检查
            stop_event.wait(check_interval)
    
    except Exception as e:
        startup_logger.error(f"健康检查线程崩溃: {str(e)}")
    finally:
        startup_logger.info("健康检查线程已退出")

def check_models():
    """检查模型"""
    # 跳过离线检查
    if config.get("app.offline", False):
        startup_logger.info("离线模式，跳过模型检查")
        return True
    
    try:
        import requests
        api_base = config.get("models.inference.api_base", "http://localhost:11434")
        response = requests.get(f"{api_base}/api/tags", timeout=5)
        
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
                startup_logger.warning(f"以下模型尚未下载: {', '.join(missing_models)}")
                startup_logger.info("您可以使用以下命令下载模型:")
                for model in missing_models:
                    startup_logger.info(f"ollama pull {model}")
                    
                return False
            else:
                startup_logger.info("所有必要模型已就绪")
                
                # 添加模型可视化
                if HAS_VISUALIZATION and visualization_manager:
                    try:
                        # 收集模型信息
                        model_info = []
                        for model in response.json().get("models", []):
                            model_info.append({
                                "name": model["name"],
                                "size": model.get("size", 0) // (1024 * 1024), # 转换为MB
                                "modified": model.get("modified", ""),
                                "parameters": model.get("parameter_size", 0) // (1024 * 1024) if "parameter_size" in model else 0
                            })
                        
                        # 创建模型艺术可视化
                        if model_info:
                            startup_logger.info("正在生成模型可视化...")
                            art_data = {
                                "files": model_info
                            }
                            art_path = visualization_manager.art_generator.visualize(
                                "code_galaxy", 
                                art_data,
                                title="AIgo模型星系"
                            )
                            startup_logger.info(f"模型可视化已生成: {art_path}")
                            
                            # 如果模型优化特性已集成，生成优化建议
                            if HAS_FEATURE_INTEGRATION and feature_integrator:
                                if "model_optimization" in feature_integrator.enabled_features:
                                    try:
                                        optimizer = feature_integrator.get_feature_integrator("model_optimization")
                                        if optimizer:
                                            startup_logger.info("分析模型优化潜力...")
                                            # 这里可以根据模型信息生成优化可视化
                                    except Exception as e:
                                        startup_logger.debug(f"生成模型优化建议失败: {e}")
                    except Exception as e:
                        startup_logger.error(f"生成模型可视化失败: {e}")
                
                return True
    except Exception as e:
        startup_logger.error(f"检查模型失败: {str(e)}")
        return False

def clean_temp_files():
    """清理临时文件"""
    try:
        temp_dir = Path(tempfile.gettempdir())
        for file in temp_dir.glob("*.bat"):
            # 仅删除我们创建的批处理文件
            if file.exists() and file.is_file():
                try:
                    file.unlink()
                    startup_logger.debug(f"已删除临时文件: {file}")
                except Exception:
                    pass
    except Exception as e:
        startup_logger.error(f"清理临时文件时出错: {e}")

def stop_services():
    """停止所有服务"""
    global processes, stop_event
    
    startup_logger.info("正在关闭服务...")
    
    # 停止健康检查线程
    stop_event.set()
    if health_thread and health_thread.is_alive():
        health_thread.join(timeout=5)
    
    try:
        # 首先尝试优雅地停止进程
        for name, info in processes.items():
            process = info.get("process")
            pid = info.get("pid")
            
            if process:
                startup_logger.info(f"正在停止 {name} 进程 (PID: {pid})...")
                try:
                    if is_windows():
                        # Windows下使用taskkill
                        subprocess.run(["taskkill", "/F", "/PID", str(pid)], 
                                      stdout=subprocess.DEVNULL, 
                                      stderr=subprocess.DEVNULL)
                    else:
                        # Linux/Mac下使用SIGTERM
                        process.terminate()
                        process.wait(timeout=5)
                except Exception as e:
                    startup_logger.warning(f"优雅停止 {name} 失败: {e}")
            
            # 确认进程已停止
            if pid and is_process_running(pid):
                startup_logger.warning(f"{name} 进程 (PID: {pid}) 仍在运行，尝试强制终止")
                try:
                    if is_windows():
                        subprocess.run(["taskkill", "/F", "/PID", str(pid)], 
                                      stdout=subprocess.DEVNULL, 
                                      stderr=subprocess.DEVNULL)
                    else:
                        os.kill(pid, signal.SIGKILL)
                except Exception as e:
                    startup_logger.error(f"强制终止 {name} 失败: {e}")
        
        # 在Windows上，可能需要额外检查Ollama
        if is_windows():
            # 尝试通过名称终止Ollama
            try:
                subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
                startup_logger.info("已终止所有Ollama进程")
            except Exception:
                pass
                
        startup_logger.info("所有服务已停止")
    except Exception as e:
        startup_logger.error(f"停止服务时出错: {str(e)}")
    
    # 清理临时文件
    clean_temp_files()

def signal_handler(sig, frame):
    """处理退出信号"""
    startup_logger.info(f"收到信号 {sig}，准备关闭...")
    stop_services()
    sys.exit(0)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动CodeAssistant和Ollama服务')
    parser.add_argument('--no-ollama', action='store_true', help='不启动Ollama服务(假设已经运行)')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--host', type=str, help='指定主机名')
    parser.add_argument('--port', type=int, help='指定端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--no-health-check', action='store_true', help='禁用健康检查')
    parser.add_argument('--visualize', action='store_true', help='启用可视化功能')
    parser.add_argument('--enable-features', type=str, help='启用指定的高级特性，逗号分隔')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        startup_logger.setLevel(logging.DEBUG)
        startup_logger.debug("调试模式已启用")
    
    # 注册信号处理器，确保程序退出时能够关闭服务
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 确保退出时清理资源
    atexit.register(stop_services)
    
    # 检查Ollama是否已安装
    if not check_ollama_installed():
        startup_logger.error("未检测到Ollama安装，请先安装Ollama: https://ollama.com/download")
        return 1
        
    # 检查可视化支持
    if args.visualize and not HAS_VISUALIZATION:
        startup_logger.warning("请求启用可视化功能，但缺少必要的依赖库。请先安装以下库: matplotlib, plotly, networkx, graphviz")
    
    # 启用指定的高级特性
    if args.enable_features and HAS_FEATURE_INTEGRATION and feature_integrator:
        features = args.enable_features.split(',')
        startup_logger.info(f"尝试启用特性: {', '.join(features)}")
        results = feature_integrator.integrate_features(features)
        for feature_id, success in results.items():
            if success:
                startup_logger.info(f"已启用特性: {feature_id}")
            else:
                startup_logger.warning(f"启用特性失败: {feature_id}")
    
    # 设置配置参数
    if args.host:
        config.set("app.host", args.host)
    if args.port:
        config.set("app.port", args.port)
    if args.debug:
        config.set("app.debug", True)
    
    # 启动Ollama服务
    if not args.no_ollama:
        success, _ = start_ollama_server()
        if not success:
            startup_logger.error("启动Ollama服务失败，请手动启动Ollama后再试")
            return 1
    
    # 检查模型
    check_models()
    
    # 启动CodeAssistant
    success, _ = start_codeassistant()
    if not success:
        startup_logger.error("启动CodeAssistant失败")
        return 1
    
    # 启动健康检查线程
    if not args.no_health_check:
        global health_thread
        health_thread = threading.Thread(target=health_check_worker, daemon=True)
        health_thread.start()
        
    # 等待服务启动
    time.sleep(2)
    
    # 打开浏览器
    if not args.no_browser:
        host = config.get("app.host", "localhost")
        port = config.get("app.port", 8080)
        url = f"http://{host}:{port}"
        
        startup_logger.info(f"正在打开浏览器: {url}")
        webbrowser.open(url)
        
        # 如果生成了仪表盘，也打开它
        if HAS_VISUALIZATION and "DASHBOARD_PATH" in os.environ:
            dashboard_path = os.environ["DASHBOARD_PATH"]
            startup_logger.info(f"正在打开系统监控仪表盘: {dashboard_path}")
            webbrowser.open(f"file://{dashboard_path}")
            
        # 如果生成了功能地图，也打开它
        if HAS_VISUALIZATION and HAS_FEATURE_INTEGRATION and "FEATURE_MAP_PATH" in os.environ:
            map_path = os.environ["FEATURE_MAP_PATH"]
            startup_logger.info(f"正在打开功能地图: {map_path}")
            webbrowser.open(f"file://{map_path}")
    
    startup_logger.info("所有服务已启动，按 Ctrl+C 停止")
    
    # 阻止主线程退出
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        startup_logger.info("收到键盘中断，准备退出...")
        stop_services()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 