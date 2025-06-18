"""
测试系统资源监控模块功能
"""

import os
import sys
import unittest
import time
from unittest.mock import patch, MagicMock
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from src.modules.system_monitor import ResourceMonitor

class TestResourceMonitor(unittest.TestCase):
    """测试ResourceMonitor类"""
    
    def setUp(self):
        """测试前准备"""
        # 模拟配置数据
        self.mock_config = {
            "models": {
                "inference": {
                    "available_models": [
                        {
                            "name": "small-model",
                            "ram_required": "4GB",
                            "vram_required": "2GB"
                        },
                        {
                            "name": "medium-model",
                            "ram_required": "8GB",
                            "vram_required": "4GB"
                        },
                        {
                            "name": "large-model",
                            "ram_required": "16GB",
                            "vram_required": "8GB"
                        }
                    ]
                },
                "embedding": {
                    "available_models": [
                        {
                            "name": "small-embed",
                            "ram_required": "2GB",
                            "vram_required": "1GB"
                        },
                        {
                            "name": "large-embed",
                            "ram_required": "4GB",
                            "vram_required": "2GB"
                        }
                    ]
                }
            },
            "system_monitor": {
                "enabled": True,
                "check_interval_seconds": 10,
                "default_mode": "balanced",
                "auto_recommend_models": True,
                "minimum_requirements": {
                    "ram_gb": 4,
                    "vram_gb": 0
                }
            }
        }
    
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.swap_memory')
    @patch('platform.system')
    @patch('platform.version')
    @patch('platform.machine')
    @patch('platform.processor')
    def test_resource_monitor_init(self, mock_processor, mock_machine, 
                                mock_version, mock_system, 
                                mock_swap, mock_vm, mock_cpu_percent, mock_cpu_count):
        """测试ResourceMonitor初始化"""
        # 设置模拟返回值
        mock_system.return_value = "Test OS"
        mock_version.return_value = "1.0"
        mock_machine.return_value = "x86_64"
        mock_processor.return_value = "Test CPU"
        
        # 物理核心和逻辑核心
        def cpu_count_side_effect(logical=True):
            return 8 if logical else 4
            
        mock_cpu_count.side_effect = cpu_count_side_effect
        mock_cpu_percent.return_value = 10.5
        
        # 模拟内存信息
        mock_vm_obj = MagicMock()
        mock_vm_obj.total = 16 * 1024 * 1024 * 1024  # 16GB
        mock_vm_obj.available = 8 * 1024 * 1024 * 1024  # 8GB
        mock_vm_obj.percent = 50.0
        mock_vm.return_value = mock_vm_obj
        
        # 模拟虚拟内存信息
        mock_swap_obj = MagicMock()
        mock_swap_obj.total = 8 * 1024 * 1024 * 1024  # 8GB
        mock_swap_obj.used = 2 * 1024 * 1024 * 1024  # 2GB
        mock_swap_obj.free = 6 * 1024 * 1024 * 1024  # 6GB
        mock_swap_obj.percent = 25.0
        mock_swap.return_value = mock_swap_obj
        
        # 使用模拟检测GPU函数以避免实际硬件依赖
        with patch.object(ResourceMonitor, '_detect_gpu', return_value=[]):
            # 创建ResourceMonitor实例
            monitor = ResourceMonitor(self.mock_config, check_interval=10)
            
            # 验证基本属性
            self.assertEqual(monitor.running_mode, "balanced")
            self.assertEqual(monitor.check_interval, 10)
            self.assertFalse(monitor.monitoring)
            
            # 验证系统信息是否正确获取
            self.assertEqual(monitor.system_info["os"], "Test OS")
            self.assertEqual(monitor.system_info["cpu"]["physical_cores"], 4)
            self.assertEqual(monitor.system_info["cpu"]["logical_cores"], 8)
            
            # 验证内存信息
            self.assertEqual(monitor.system_info["memory"]["total_gb"], 16.0)
            self.assertEqual(monitor.system_info["memory"]["available_gb"], 8.0)
            
            # 验证是否推荐了模型
            self.assertIsNotNone(monitor.recommended_models.get("inference"))
            self.assertIsNotNone(monitor.recommended_models.get("embedding"))
            
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.swap_memory')
    def test_mode_switching(self, mock_swap, mock_vm, mock_cpu_percent, mock_cpu_count):
        """测试模式切换"""
        # 物理核心和逻辑核心
        def cpu_count_side_effect(logical=True):
            return 8 if logical else 4
            
        mock_cpu_count.side_effect = cpu_count_side_effect
        mock_cpu_percent.return_value = 10.5
        
        # 模拟内存信息
        mock_vm_obj = MagicMock()
        mock_vm_obj.total = 16 * 1024 * 1024 * 1024  # 16GB
        mock_vm_obj.available = 8 * 1024 * 1024 * 1024  # 8GB
        mock_vm_obj.percent = 50.0
        mock_vm.return_value = mock_vm_obj
        
        # 模拟虚拟内存信息
        mock_swap_obj = MagicMock()
        mock_swap_obj.total = 8 * 1024 * 1024 * 1024  # 8GB
        mock_swap_obj.used = 2 * 1024 * 1024 * 1024  # 2GB
        mock_swap_obj.free = 6 * 1024 * 1024 * 1024  # 6GB
        mock_swap_obj.percent = 25.0
        mock_swap.return_value = mock_swap_obj
        
        # 使用模拟检测GPU函数以避免实际硬件依赖
        with patch.object(ResourceMonitor, '_detect_gpu', return_value=[]):
            # 创建ResourceMonitor实例
            monitor = ResourceMonitor(self.mock_config)
            
            # 记录平衡模式下的建议
            balanced_recommendation = monitor.get_recommended_models()
            
            # 切换到性能模式
            success = monitor.set_mode("performance")
            self.assertTrue(success)
            self.assertEqual(monitor.running_mode, "performance")
            
            # 获取性能模式下的建议
            performance_recommendation = monitor.get_recommended_models()
            
            # 切换回平衡模式
            success = monitor.set_mode("balanced")
            self.assertTrue(success)
            self.assertEqual(monitor.running_mode, "balanced")
            
            # 测试无效模式名称
            success = monitor.set_mode("invalid_mode")
            self.assertFalse(success)
            self.assertEqual(monitor.running_mode, "balanced")
    
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.swap_memory')
    def test_error_handling(self, mock_swap, mock_vm, mock_cpu_percent, mock_cpu_count):
        """测试错误处理"""
        # 设置模拟数据
        mock_cpu_count.side_effect = Exception("CPU计数错误")
        mock_cpu_percent.return_value = 10.5
        
        # 模拟内存信息
        mock_vm_obj = MagicMock()
        mock_vm_obj.total = 16 * 1024 * 1024 * 1024  # 16GB
        mock_vm_obj.available = 8 * 1024 * 1024 * 1024  # 8GB
        mock_vm_obj.percent = 50.0
        mock_vm.return_value = mock_vm_obj
        
        # 模拟虚拟内存信息
        mock_swap_obj = MagicMock()
        mock_swap_obj.total = 8 * 1024 * 1024 * 1024  # 8GB
        mock_swap_obj.used = 2 * 1024 * 1024 * 1024  # 2GB
        mock_swap_obj.free = 6 * 1024 * 1024 * 1024  # 6GB
        mock_swap_obj.percent = 25.0
        mock_swap.return_value = mock_swap_obj
        
        # 使用模拟检测GPU函数以避免实际硬件依赖
        with patch.object(ResourceMonitor, '_detect_gpu', return_value=[]):
            # 创建ResourceMonitor实例
            monitor = ResourceMonitor(self.mock_config)
            
            # 即使有错误，也应该能获取系统信息
            system_info = monitor.get_system_info()
            self.assertIsNotNone(system_info)
            
            # CPU信息应包含错误信息
            self.assertIn("error", system_info["cpu"])
    
    def test_format_bytes(self):
        """测试字节格式化函数"""
        monitor = ResourceMonitor(self.mock_config)
        
        # 测试不同单位的格式化
        self.assertEqual(monitor._format_bytes(500), "500.00 B")
        self.assertEqual(monitor._format_bytes(1500), "1.46 KB")
        self.assertEqual(monitor._format_bytes(1500000), "1.43 MB")
        self.assertEqual(monitor._format_bytes(1500000000), "1.40 GB")
        self.assertEqual(monitor._format_bytes(1500000000000), "1.36 TB")
        
if __name__ == '__main__':
    unittest.main() 