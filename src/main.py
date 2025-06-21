"""
AIgo主程序入口

负责初始化和启动整个应用程序
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 导入工具模块
from src.utils import config
from src.utils.init_utils import ensure_directories
from src.utils.config_validator import validate_config
from src.utils.dependency_container import get_container

# 导入服务
from src.services.model_service import ModelService
from src.services.auth_service import AuthorizationService as AuthService
from src.api.app import start_web_app

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AIgo - 智能代码助手")
    
    parser.add_argument("--config", type=str, default="config/default/config.json",
                      help="配置文件路径")
    parser.add_argument("--host", type=str, default=None,
                      help="Web服务器主机地址")
    parser.add_argument("--port", type=int, default=None,
                      help="Web服务器端口")
    parser.add_argument("--debug", action="store_true",
                      help="是否启用调试模式")
    parser.add_argument("--no-browser", action="store_true",
                      help="不自动打开浏览器")
    parser.add_argument("--no-ollama", action="store_true",
                      help="不使用Ollama模型服务")
    
    return parser.parse_args()

def init_services(args):
    """初始化服务"""
    logger.info("开始初始化服务...")
    
    # 获取依赖容器
    container = get_container()
    
    # 注册服务
    from src.services.service_registry import register_services
    register_services()
    
    # 初始化模型服务
    model_service = container.get(ModelService)
    if not args.no_ollama:
        model_service.init_ollama()
    
    # 初始化认证服务
    auth_service = container.get(AuthService)
    auth_service.init()
    
    # 初始化系统监控
    try:
        from src.modules.system_monitor.resource_monitor import ResourceMonitor
        system_monitor = ResourceMonitor()
        system_monitor.start()
    except ImportError:
        logger.warning("未找到系统监控模块，将不会启用资源监控")
        system_monitor = None
    
    logger.info("服务初始化完成")
    return system_monitor

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 加载配置
    config.load_config(args.config)
    
    # 验证配置
    is_valid, errors, warnings = validate_config(args.config)
    if not is_valid:
        logger.error("配置验证失败:")
        for error in errors:
            logger.error(f"- {error}")
        if warnings:
            logger.warning("配置警告:")
            for warning in warnings:
                logger.warning(f"- {warning}")
        sys.exit(1)
    elif warnings:
        logger.warning("配置警告:")
        for warning in warnings:
            logger.warning(f"- {warning}")
    
    # 确保必要的目录存在
    ensure_directories()
    
    # 初始化服务
    system_monitor = init_services(args)
    
    # 启动Web应用
    start_web_app(
        host=args.host,
        port=args.port,
        debug=args.debug,
        system_monitor=system_monitor
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"程序异常退出: {str(e)}")
        sys.exit(1) 