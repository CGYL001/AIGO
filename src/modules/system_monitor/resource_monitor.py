"""
系统资源监控模块

负责实时监控系统资源使用情况，检测硬件配置，并根据系统状况推荐合适的模型
"""

import os
import time
import psutil
import platform
import threading
import logging
from typing import Dict, List, Optional, Tuple
import json
import subprocess
import traceback

logger = logging.getLogger(__name__)

class ResourceMonitor:
    """系统资源监控类，负责检测和监控系统资源使用情况"""
    
    def __init__(self, config: Dict, check_interval: int = 300):
        """
        初始化资源监控器
        
        Args:
            config: 应用配置
            check_interval: 资源检测间隔（秒）
        """
        self.config = config
        self.check_interval = check_interval
        self.available_models = self._get_available_models()
        self.system_info = {}
        self.recommended_models = {}
        self.monitoring = False
        self.monitor_thread = None
        self.running_mode = "balanced"  # balanced 或 performance
        self.last_check_time = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        try:
            # 立即执行一次系统检测
            self.check_system()
            # 重置错误计数
            self.consecutive_errors = 0
        except Exception as e:
            logger.error(f"初始化系统检测失败: {str(e)}")
            logger.debug(traceback.format_exc())
            # 设置基本系统信息
            self._set_fallback_system_info()
            self.consecutive_errors += 1
    
    def _set_fallback_system_info(self):
        """设置基本的系统信息，作为检测失败时的后备方案"""
        try:
            self.system_info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "cpu": {
                    "physical_cores": psutil.cpu_count(logical=False) or 1,
                    "logical_cores": psutil.cpu_count(logical=True) or 2,
                    "cpu_percent": 0,
                },
                "memory": {
                    "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                    "percent_used": psutil.virtual_memory().percent,
                },
                "note": "这是备用系统信息，由于检测失败而使用"
            }
        except Exception as fallback_error:
            logger.error(f"设置备用系统信息也失败: {str(fallback_error)}")
            # 使用最小系统信息
            self.system_info = {
                "os": platform.system(),
                "note": "系统信息检测失败"
            }
    
    def _get_available_models(self) -> Dict:
        """从配置中获取可用的模型列表"""
        models = {}
        
        try:
            # 获取推理模型
            if "models" in self.config and "inference" in self.config["models"]:
                models["inference"] = self.config["models"]["inference"].get("available_models", [])
                
            # 获取嵌入模型
            if "models" in self.config and "embedding" in self.config["models"]:
                models["embedding"] = self.config["models"]["embedding"].get("available_models", [])
        except Exception as e:
            logger.error(f"获取可用模型列表失败: {str(e)}")
            models = {"inference": [], "embedding": []}
            
        return models
    
    def check_system(self) -> Dict:
        """
        检测系统硬件配置并更新系统信息
        
        Returns:
            Dict: 系统信息字典
        """
        logger.info("正在检测系统资源...")
        self.last_check_time = time.time()
        
        try:
            # 基本系统信息
            self.system_info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
            }
            
            # CPU信息
            try:
                cpu_info = {
                    "physical_cores": psutil.cpu_count(logical=False) or 1,
                    "logical_cores": psutil.cpu_count(logical=True) or 2,
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "cpu_freq": self._get_cpu_freq(),
                }
                self.system_info["cpu"] = cpu_info
            except Exception as e:
                logger.error(f"获取CPU信息失败: {str(e)}")
                self.system_info["cpu"] = {
                    "physical_cores": 1,
                    "logical_cores": 2,
                    "cpu_percent": 0,
                    "error": str(e)
                }
            
            # 内存信息
            try:
                memory = psutil.virtual_memory()
                memory_info = {
                    "total": self._format_bytes(memory.total),
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available": self._format_bytes(memory.available),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent_used": memory.percent,
                }
                self.system_info["memory"] = memory_info
            except Exception as e:
                logger.error(f"获取内存信息失败: {str(e)}")
                self.system_info["memory"] = {
                    "total_gb": 4,
                    "available_gb": 2,
                    "percent_used": 50,
                    "error": str(e)
                }
            
            # 虚拟内存/页面文件信息
            try:
                swap = psutil.swap_memory()
                swap_info = {
                    "total": self._format_bytes(swap.total),
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used": self._format_bytes(swap.used),
                    "free": self._format_bytes(swap.free),
                    "percent_used": swap.percent,
                }
                self.system_info["virtual_memory"] = swap_info
            except Exception as e:
                logger.error(f"获取虚拟内存信息失败: {str(e)}")
                self.system_info["virtual_memory"] = {
                    "total_gb": 2,
                    "percent_used": 0,
                    "error": str(e)
                }
            
            # 检测GPU信息
            try:
                gpu_info = self._detect_gpu()
                if gpu_info:
                    self.system_info["gpu"] = gpu_info
            except Exception as e:
                logger.error(f"获取GPU信息失败: {str(e)}")
                self.system_info["gpu"] = []
            
            # 根据系统配置推荐模型
            self._recommend_models()
            
            # 重置错误计数
            self.consecutive_errors = 0
            
            logger.info(f"系统检测完成")
            return self.system_info
            
        except Exception as e:
            logger.error(f"系统检测过程中发生错误: {str(e)}")
            logger.debug(traceback.format_exc())
            self.consecutive_errors += 1
            
            # 如果连续多次失败，设置为基本信息
            if self.consecutive_errors >= 3:
                self._set_fallback_system_info()
                
            return self.system_info
    
    def _get_cpu_freq(self) -> Dict:
        """获取CPU频率信息"""
        freq = psutil.cpu_freq()
        if freq:
            return {
                "current_mhz": freq.current,
                "min_mhz": freq.min if hasattr(freq, "min") else None,
                "max_mhz": freq.max if hasattr(freq, "max") else None,
            }
        return {}
    
    def _detect_gpu(self) -> List[Dict]:
        """
        检测系统的GPU信息
        
        Returns:
            List[Dict]: GPU信息列表
        """
        gpus = []
        
        # 尝试检测NVIDIA GPU
        try:
            # 使用subprocess调用nvidia-smi
            nvidia_output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,memory.used", "--format=csv,noheader,nounits"],
                universal_newlines=True
            )
            
            for i, line in enumerate(nvidia_output.strip().split("\n")):
                parts = line.split(", ")
                if len(parts) >= 4:
                    name, total, free, used = parts[:4]
                    gpus.append({
                        "index": i,
                        "name": name,
                        "vendor": "NVIDIA",
                        "total_memory_mb": float(total),
                        "free_memory_mb": float(free),
                        "used_memory_mb": float(used),
                        "total_vram_gb": round(float(total) / 1024, 2),
                        "free_vram_gb": round(float(free) / 1024, 2)
                    })
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.debug("未检测到NVIDIA GPU或nvidia-smi工具")
            
            # 对于Windows，尝试使用WMI
            if platform.system() == "Windows":
                try:
                    import wmi
                    w = wmi.WMI()
                    for i, gpu in enumerate(w.Win32_VideoController()):
                        # 部分GPU可能无法正确报告内存
                        vram_mb = getattr(gpu, "AdapterRAM", 0)
                        if vram_mb:
                            vram_mb = vram_mb / (1024 * 1024)  # 转换为MB
                            
                        gpus.append({
                            "index": i,
                            "name": gpu.Name,
                            "vendor": gpu.VideoProcessor if hasattr(gpu, "VideoProcessor") else "Unknown",
                            "total_memory_mb": vram_mb,
                            "total_vram_gb": round(vram_mb / 1024, 2) if vram_mb else None
                        })
                except ImportError:
                    logger.debug("WMI模块不可用，无法检测Windows GPU")
        
        return gpus
    
    def _format_bytes(self, bytes_value: int) -> str:
        """将字节数格式化为人类可读的格式"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} PB"
    
    def _recommend_models(self) -> Dict:
        """
        根据系统配置推荐最适合的模型
        
        Returns:
            Dict: 推荐模型信息
        """
        try:
            recommended = {
                "inference": None,
                "embedding": None
            }
            
            # 获取系统可用内存（GB）
            available_ram = self.system_info.get("memory", {}).get("available_gb", 0)
            
            # 获取系统可用显存（如果有GPU）
            available_vram = 0
            if "gpu" in self.system_info and self.system_info["gpu"]:
                # 选择可用显存最多的GPU
                max_vram_gpu = max(self.system_info["gpu"], 
                                  key=lambda g: g.get("free_vram_gb", 0) if g.get("free_vram_gb") is not None else 0)
                available_vram = max_vram_gpu.get("free_vram_gb", 0) or 0
            
            # 运行模式系数：性能模式使用更多资源，平衡模式预留资源
            mode_coefficient = 0.9 if self.running_mode == "performance" else 0.65
            
            effective_ram = available_ram * mode_coefficient
            effective_vram = available_vram * mode_coefficient
            
            # 计算系统得分
            if available_vram > 0:  # 有独立显卡
                score = (effective_ram + effective_vram * 2) / 3  # 显存权重更高
            else:
                score = effective_ram
            
            logger.info(f"系统计算得分: {score:.2f}，可用内存: {available_ram}GB，可用显存: {available_vram}GB，运行模式: {self.running_mode}")
            
            # 获取最小系统需求
            min_requirements = self.config.get("system_monitor", {}).get("minimum_requirements", {})
            min_ram = float(min_requirements.get("ram_gb", 4))
            
            # 检查是否满足最低要求
            if effective_ram < min_ram:
                logger.warning(f"系统可用内存不足，无法推荐模型。最低要求: {min_ram}GB，当前可用: {effective_ram:.2f}GB")
                return recommended
            
            # 选择推理模型
            inference_models = sorted(
                self.available_models.get("inference", []),
                key=lambda m: (
                    # 首先过滤掉内存需求大于有效内存的模型
                    float(m.get("ram_required", "0").replace("GB", "")) <= effective_ram,
                    # 然后按照模型大小从大到小排序
                    float(m.get("ram_required", "0").replace("GB", ""))
                ),
                reverse=True
            )
            
            # 选择嵌入模型
            embedding_models = sorted(
                self.available_models.get("embedding", []),
                key=lambda m: (
                    float(m.get("ram_required", "0").replace("GB", "")) <= effective_ram * 0.3,  # 嵌入模型分配较少内存
                    float(m.get("ram_required", "0").replace("GB", ""))
                ),
                reverse=True
            )
            
            # 选择符合条件的最好的模型
            if inference_models:
                recommended["inference"] = inference_models[0]
                
            if embedding_models:
                recommended["embedding"] = embedding_models[0]
                
            self.recommended_models = recommended
            
            logger.info(f"推荐模型: 推理模型 - {recommended['inference']['name'] if recommended['inference'] else '无适合模型'}, "
                      f"嵌入模型 - {recommended['embedding']['name'] if recommended['embedding'] else '无适合模型'}")
            
            return recommended
        
        except Exception as e:
            logger.error(f"推荐模型时发生错误: {str(e)}")
            logger.debug(traceback.format_exc())
            return {"inference": None, "embedding": None}
    
    def start_monitoring(self):
        """启动资源监控线程"""
        if self.monitoring:
            logger.warning("资源监控已在运行中")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("系统资源监控已启动")
    
    def stop_monitoring(self):
        """停止资源监控线程"""
        if not self.monitoring:
            return
            
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            self.monitor_thread = None
        logger.info("系统资源监控已停止")
    
    def _monitor_loop(self):
        """资源监控循环"""
        while self.monitoring:
            try:
                # 检查自上次检测以来是否已经过去了足够的时间
                elapsed = time.time() - self.last_check_time
                if elapsed >= self.check_interval:
                    # 检查系统资源
                    self.check_system()
                
                # 每5秒检查一次是否该退出
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"资源监控循环过程中发生错误: {str(e)}")
                logger.debug(traceback.format_exc())
                self.consecutive_errors += 1
                
                # 如果连续错误太多，暂停更长时间
                if self.consecutive_errors >= self.max_consecutive_errors:
                    logger.error(f"资源监控连续{self.consecutive_errors}次失败，暂停监控5分钟")
                    time.sleep(300)
                    # 重置错误计数
                    self.consecutive_errors = 0
                else:
                    time.sleep(60)  # 发生错误后短暂休眠
    
    def set_mode(self, mode: str) -> bool:
        """
        设置运行模式
        
        Args:
            mode: 模式名称 ("balanced" 或 "performance")
            
        Returns:
            bool: 设置是否成功
        """
        if mode not in ["balanced", "performance"]:
            logger.error(f"无效的运行模式: {mode}")
            return False
            
        self.running_mode = mode
        logger.info(f"已将运行模式设置为: {mode}")
        
        # 重新执行检测和推荐
        try:
            self.check_system()
            return True
        except Exception as e:
            logger.error(f"切换模式后检测系统资源失败: {str(e)}")
            return False
    
    def get_recommended_models(self) -> Dict:
        """获取当前推荐的模型"""
        return self.recommended_models
    
    def get_system_info(self) -> Dict:
        """获取最近一次检测的系统信息"""
        # 检查是否需要重新检测（如果数据过旧）
        current_time = time.time()
        if current_time - self.last_check_time > 600:  # 如果超过10分钟没有检测
            logger.info("系统信息已过期，重新检测")
            try:
                self.check_system()
            except Exception as e:
                logger.error(f"重新检测系统信息失败: {str(e)}")
        
        return self.system_info 