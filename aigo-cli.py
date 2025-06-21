#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AIgo命令行工具启动脚本

提供命令行接口，用于访问AIgo的所有功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # 导入CLI入口点
    from src.cli.__main__ import main
    
    # 运行CLI
    sys.exit(main()) 