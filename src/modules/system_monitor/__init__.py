"""
系统资源监控模块

负责检测系统硬件资源和配置，为模型选择提供依据
"""

from .resource_monitor import ResourceMonitor

__all__ = ['ResourceMonitor'] 