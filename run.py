#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.utils import config, logger
from src.mcp_server import mcp_server


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="MCP - 模型控制协议服务器")
    
    parser.add_argument(
        "--host", 
        type=str, 
        help="API服务器主机地址"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        help="API服务器端口"
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="启用调试模式"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 加载配置
    if args.config:
        config.load_config(args.config)
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # 设置API服务器主机和端口
    if args.host:
        mcp_server.api_host = args.host
    
    if args.port:
        mcp_server.api_port = args.port
    
    # 打印启动信息
    logger.info("=" * 50)
    logger.info("MCP服务器启动")
    logger.info(f"版本: {config.get('app.version', '0.1.0')}")
    logger.info(f"API服务器: {mcp_server.api_host}:{mcp_server.api_port}")
    logger.info(f"调试模式: {'开启' if args.debug else '关闭'}")
    logger.info("=" * 50)
    
    try:
        # 启动MCP服务器
        mcp_server.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 