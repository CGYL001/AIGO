import os
import time
import shutil
import psutil
import subprocess
from typing import Dict, Any, Optional

from src.utils import logger

class HardwareInfo:
    """硬件信息获取类，用于监控系统资源使用情况"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(HardwareInfo, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        """初始化硬件信息获取器"""
        if self._initialized:
            return
            
        self._has_gpu = self._check_gpu_available()
        self._last_update = 0
        self._cache_timeout = 5  # 缓存5秒
        self._cached_info = {}
        
        self._initialized = True
    
    def _check_gpu_available(self) -> bool:
        """检查是否有可用的NVIDIA GPU"""
        try:
            result = subprocess.run(
                ["nvidia-smi"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """获取GPU信息"""
        if not self._has_gpu:
            return {
                "has_gpu": False,
                "gpu_name": "N/A",
                "gpu_percent": 0,
                "gpu_memory_total_gb": 0,
                "gpu_memory_used_gb": 0,
                "gpu_memory_free_gb": 0
            }
            
        try:
            # 获取GPU名称
            name_cmd = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                stdout=subprocess.PIPE,
                text=True
            )
            gpu_name = name_cmd.stdout.strip() if name_cmd.returncode == 0 else "Unknown"
            
            # 获取GPU内存使用情况
            mem_cmd = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"],
                stdout=subprocess.PIPE,
                text=True
            )
            
            if mem_cmd.returncode == 0:
                mem_values = mem_cmd.stdout.strip().split(",")
                total = int(mem_values[0].strip()) / 1024  # MB to GB
                used = int(mem_values[1].strip()) / 1024
                free = int(mem_values[2].strip()) / 1024
                
                # 获取GPU利用率
                util_cmd = subprocess.run(
                    ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                    stdout=subprocess.PIPE,
                    text=True
                )
                gpu_percent = int(util_cmd.stdout.strip()) if util_cmd.returncode == 0 else 0
                
                return {
                    "has_gpu": True,
                    "gpu_name": gpu_name,
                    "gpu_percent": gpu_percent,
                    "gpu_memory_total_gb": round(total, 2),
                    "gpu_memory_used_gb": round(used, 2),
                    "gpu_memory_free_gb": round(free, 2)
                }
        except Exception as e:
            logger.error(f"获取GPU信息失败: {str(e)}")
            
        return {
            "has_gpu": True,
            "gpu_name": "Unknown",
            "gpu_percent": 0,
            "gpu_memory_total_gb": 0,
            "gpu_memory_used_gb": 0,
            "gpu_memory_free_gb": 0
        }
    
    def get_hardware_info(self, force_update: bool = False) -> Dict[str, Any]:
        """
        获取系统硬件信息
        
        Args:
            force_update: 是否强制更新缓存
            
        Returns:
            Dict[str, Any]: 硬件信息字典
        """
        current_time = time.time()
        
        # 使用缓存，除非强制更新或缓存过期
        if not force_update and self._cached_info and (current_time - self._last_update) < self._cache_timeout:
            return self._cached_info
            
        try:
            # CPU信息
            cpu_count = psutil.cpu_count(logical=True)
            cpu_physical_count = psutil.cpu_count(logical=False)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存信息
            memory = psutil.virtual_memory()
            memory_total_gb = memory.total / (1024 * 1024 * 1024)
            memory_used_gb = memory.used / (1024 * 1024 * 1024)
            memory_free_gb = memory.available / (1024 * 1024 * 1024)
            memory_percent = memory.percent
            
            # 磁盘信息
            disk_usage = psutil.disk_usage(os.path.abspath(os.sep))
            disk_total_gb = disk_usage.total / (1024 * 1024 * 1024)
            disk_used_gb = disk_usage.used / (1024 * 1024 * 1024)
            disk_free_gb = disk_usage.free / (1024 * 1024 * 1024)
            disk_percent = disk_usage.percent
            
            # GPU信息
            gpu_info = self._get_gpu_info() if self._has_gpu else {
                "has_gpu": False,
                "gpu_name": "N/A",
                "gpu_percent": 0,
                "gpu_memory_total_gb": 0,
                "gpu_memory_used_gb": 0,
                "gpu_memory_free_gb": 0
            }
            
            # 组装结果
            result = {
                "cpu_count": cpu_count,
                "cpu_physical_count": cpu_physical_count,
                "cpu_percent": cpu_percent,
                
                "memory_total_gb": round(memory_total_gb, 2),
                "memory_used_gb": round(memory_used_gb, 2),
                "memory_free_gb": round(memory_free_gb, 2),
                "memory_percent": memory_percent,
                
                "disk_total_gb": round(disk_total_gb, 2),
                "disk_used_gb": round(disk_used_gb, 2),
                "disk_free_gb": round(disk_free_gb, 2),
                "disk_percent": disk_percent,
                
                # 合并GPU信息
                **gpu_info
            }
            
            # 更新缓存
            self._cached_info = result
            self._last_update = current_time
            
            return result
            
        except Exception as e:
            logger.error(f"获取硬件信息失败: {str(e)}")
            
            # 返回上次缓存或空结果
            return self._cached_info if self._cached_info else {}

# 创建实例以供导出
hardware_info = HardwareInfo() 