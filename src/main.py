import os
import sys
import argparse
from pathlib import Path

# 确保可以正确导入模块
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from src.utils import config, logger
from src.api.app import start_web_app
from src.services import ModelServiceFactory
from src.modules.system_monitor import ResourceMonitor

# 全局资源监控实例
resource_monitor = None

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='CodeAssistant - 本地AI编程助手')
    parser.add_argument('--host', type=str, help='Web服务器主机名')
    parser.add_argument('--port', type=int, help='Web服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--env', type=str, choices=['development', 'production'], help='运行环境')
    parser.add_argument('--mode', type=str, choices=['balanced', 'performance'], help='运行模式：平衡或性能优先')
    
    return parser.parse_args()

def setup_environment(args):
    """设置环境变量和配置"""
    # 设置环境
    if args.env:
        os.environ['CODEASSISTANT_ENV'] = args.env
    
    # 如果指定了配置文件，复制到本地配置
    if args.config and os.path.exists(args.config):
        local_config_path = Path(ROOT_DIR) / "config" / "local.json"
        try:
            import shutil
            shutil.copy(args.config, local_config_path)
            logger.info(f"已加载自定义配置: {args.config}")
        except Exception as e:
            logger.error(f"加载自定义配置失败: {str(e)}")

def setup_system_monitor():
    """初始化系统资源监控模块"""
    global resource_monitor
    
    monitor_config = config.get("system_monitor", {})
    if not monitor_config.get("enabled", True):
        logger.info("系统资源监控已禁用")
        return None
        
    try:
        check_interval = monitor_config.get("check_interval_seconds", 300)
        
        # 创建资源监控实例
        resource_monitor = ResourceMonitor(config.get_all(), check_interval)
        
        # 设置默认运行模式
        default_mode = monitor_config.get("default_mode", "balanced")
        resource_monitor.set_mode(default_mode)
        
        # 如果配置为自动推荐模型，则应用推荐结果
        if monitor_config.get("auto_recommend_models", True):
            recommended_models = resource_monitor.get_recommended_models()
            if recommended_models.get("inference"):
                inference_model = recommended_models["inference"]["name"]
                config.set("models.inference.name", inference_model)
                logger.info(f"已将推理模型设置为系统推荐的: {inference_model}")
                
            if recommended_models.get("embedding"):
                embedding_model = recommended_models["embedding"]["name"]
                config.set("models.embedding.name", embedding_model)
                logger.info(f"已将嵌入模型设置为系统推荐的: {embedding_model}")
        
        # 启动监控线程
        resource_monitor.start_monitoring()
        logger.info(f"系统资源监控已启动，检测间隔: {check_interval}秒，运行模式: {default_mode}")
        
        return resource_monitor
    except Exception as e:
        logger.error(f"初始化系统资源监控失败: {str(e)}")
        return None

def check_dependencies():
    """检查依赖项"""
    try:
        # 检查Ollama服务
        import requests
        api_base = config.get("models.inference.api_base", "http://localhost:11434")
        
        try:
            response = requests.get(f"{api_base}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                logger.info(f"Ollama服务正常，发现{len(models)}个模型")
                
                # 检查所需模型是否可用
                inference_model = config.get("models.inference.name", "deepseek-r1:8b")
                embedding_model = config.get("models.embedding.name", "bge-m3")
                
                model_names = [m.get("name", "").split(":")[0] for m in models]
                
                if not any(inference_model.split(":")[0] in name for name in model_names):
                    logger.warning(f"未找到推理模型: {inference_model}，请使用 'ollama pull {inference_model}' 下载")
                    
                if not any(embedding_model.split(":")[0] in name for name in model_names):
                    logger.warning(f"未找到嵌入模型: {embedding_model}，请使用 'ollama pull {embedding_model}' 下载")
            else:
                logger.warning(f"Ollama服务响应异常: {response.status_code}")
        except Exception as e:
            logger.warning(f"无法连接到Ollama服务({api_base}): {str(e)}")
            logger.warning("请确保Ollama服务已启动")
            
        # 检查核心依赖库
        import flask
        logger.info("Flask依赖检查通过")
        
        # 检查系统监控依赖
        import psutil
        logger.info("系统监控依赖检查通过")
        
        # 检查文件目录结构
        data_dir = Path(ROOT_DIR) / "data"
        if not data_dir.exists():
            logger.warning(f"数据目录不存在: {data_dir}，将自动创建")
            data_dir.mkdir(parents=True, exist_ok=True)
            
        kb_dir = data_dir / "knowledge_bases"
        if not kb_dir.exists():
            kb_dir.mkdir(parents=True, exist_ok=True)
        
        logs_dir = Path(ROOT_DIR) / "logs"
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=True)
            
    except ImportError as e:
        logger.error(f"缺少必要的依赖: {str(e)}")
        logger.error("请运行 'pip install -r requirements.txt' 安装依赖")
        sys.exit(1)

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置环境
    setup_environment(args)
    
    # 检查依赖
    check_dependencies()
    
    # 初始化系统监控
    resource_monitor = setup_system_monitor()
    
    # 如果命令行指定了运行模式，则覆盖默认设置
    if args.mode and resource_monitor:
        resource_monitor.set_mode(args.mode)
        logger.info(f"已通过命令行参数设置运行模式: {args.mode}")
    
    # 打印欢迎信息
    app_name = config.get("app.name", "CodeAssistant")
    version = config.get("app.version", "0.1.0")
    logger.info(f"启动 {app_name} v{version}")
    
    # 启动Web应用
    host = args.host or config.get("app.host", "localhost")
    port = args.port or config.get("app.port", 8080)
    debug = args.debug if args.debug is not None else config.get("app.debug", True)
    
    logger.info(f"Web界面将在 http://{host}:{port} 运行")
    
    try:
        # 将资源监控实例传递给Web应用
        start_web_app(host, port, debug, resource_monitor)
    except KeyboardInterrupt:
        logger.info("收到中断信号，程序退出")
        # 停止资源监控
        if resource_monitor:
            resource_monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        # 停止资源监控
        if resource_monitor:
            resource_monitor.stop_monitoring()
        sys.exit(1)

if __name__ == "__main__":
    main() 