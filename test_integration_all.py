#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AIgo系统全面集成测试脚本

从项目根目录开始，测试整个系统的所有关键功能，包括：
- 基础功能测试
- 模型加载和运行测试
- 自我纠正训练系统测试
- 多模态功能测试
- 科研级性能分析测试
- Web界面测试
- 数据存储和加载测试

这个脚本确保所有组件能够正确协同工作，防止跨模块问题和依赖关系错误。
"""

import os
import sys
import time
import logging
import unittest
import tempfile
import shutil
from pathlib import Path
import importlib
import threading
import requests
import json
import subprocess
from contextlib import contextmanager

# 添加项目根目录到Python路径
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(ROOT_DIR, 'test_integration_all.log'), mode='w')
    ]
)
logger = logging.getLogger(__name__)

# 测试配置
TEST_CONFIG = {
    'temp_dir': os.path.join(ROOT_DIR, 'temp_test'),
    'web_host': '127.0.0.1',
    'web_port': 5050,  # 使用不常用的端口避免冲突
    'timeout': 30,  # 操作超时时间（秒）
}

@contextmanager
def web_server():
    """启动Web服务器的上下文管理器"""
    process = None
    try:
        # 导入Web应用模块
        from AIGO.models.training.self_correction.ui.web.app import app
        
        # 在后台线程中启动服务器
        def run_server():
            app.run(
                host=TEST_CONFIG['web_host'],
                port=TEST_CONFIG['web_port'],
                debug=False,  # 禁用调试模式
                use_reloader=False  # 禁用重载器
            )
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # 等待服务器启动
        server_url = f"http://{TEST_CONFIG['web_host']}:{TEST_CONFIG['web_port']}/"
        start_time = time.time()
        while time.time() - start_time < TEST_CONFIG['timeout']:
            try:
                response = requests.get(server_url, timeout=1)
                if response.status_code == 200:
                    logger.info(f"Web服务器已启动: {server_url}")
                    break
            except requests.RequestException:
                time.sleep(0.5)
        else:
            raise TimeoutError("Web服务器启动超时")
        
        # 返回服务器URL
        yield server_url
    
    finally:
        # 清理资源
        if process:
            process.terminate()
            process.wait()
            logger.info("Web服务器已关闭")

class TestAIgoIntegration(unittest.TestCase):
    """AIgo系统集成测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        logger.info("开始AIgo系统集成测试")
        
        # 创建临时测试目录
        os.makedirs(TEST_CONFIG['temp_dir'], exist_ok=True)
        
        # 检查项目结构
        cls._check_project_structure()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 清理临时测试目录
        if os.path.exists(TEST_CONFIG['temp_dir']):
            shutil.rmtree(TEST_CONFIG['temp_dir'])
        
        logger.info("AIgo系统集成测试完成")
    
    @classmethod
    def _check_project_structure(cls):
        """检查项目结构"""
        logger.info("检查项目结构...")
        
        # 检查关键目录
        required_dirs = [
            'AIGO',
            'AIGO/models',
            'AIGO/models/training',
            'AIGO/models/training/self_correction',
            'AIGO/models/training/self_correction/ui',
            'AIGO/models/training/self_correction/ui/web',
            'AIGO/models/training/self_correction/multimodal',
            'AIGO/models/training/self_correction/utils',
        ]
        
        # 检查关键文件
        required_files = [
            'AIGO/start_web_ui.py',
            'AIGO/models/training/self_correction/ui/web/app.py',
            'AIGO/models/training/self_correction/multimodal/image_task.py',
            'AIGO/models/training/self_correction/utils/performance_comparison.py',
            'AIGO/test_multimodal_features.py',
        ]
        
        missing_items = []
        
        for dir_path in required_dirs:
            if not os.path.isdir(os.path.join(ROOT_DIR, dir_path)):
                missing_items.append(f"目录: {dir_path}")
        
        for file_path in required_files:
            if not os.path.isfile(os.path.join(ROOT_DIR, file_path)):
                missing_items.append(f"文件: {file_path}")
        
        if missing_items:
            logger.error("项目结构检查失败，缺少以下项目:")
            for item in missing_items:
                logger.error(f"  - {item}")
            raise FileNotFoundError(f"项目结构不完整，缺少 {len(missing_items)} 个项目")
        
        logger.info("项目结构检查通过")
    
    def test_01_imports(self):
        """测试模块导入"""
        logger.info("测试模块导入...")
        
        # 测试导入关键模块
        modules = [
            'AIGO',
            'AIGO.models.training.self_correction.trainer',
            'AIGO.models.training.self_correction.task',
            'AIGO.models.training.self_correction.memory',
            'AIGO.models.training.self_correction.multimodal.image_task',
            'AIGO.models.training.self_correction.utils.performance_comparison',
            'AIGO.models.training.self_correction.ui.web.app',
        ]
        
        for module_name in modules:
            try:
                module = importlib.import_module(module_name)
                logger.info(f"成功导入模块: {module_name}")
            except ImportError as e:
                logger.error(f"导入模块 {module_name} 失败: {e}")
                raise
    
    def test_02_image_task(self):
        """测试图像任务功能"""
        logger.info("测试图像任务功能...")
        
        from AIGO.models.training.self_correction.multimodal.image_task import ImageTask, ImageTaskManager
        
        # 创建测试目录
        test_dir = os.path.join(TEST_CONFIG['temp_dir'], 'image_tasks')
        os.makedirs(test_dir, exist_ok=True)
        
        # 创建任务管理器
        task_manager = ImageTaskManager(storage_path=test_dir)
        
        # 创建图像任务
        task = task_manager.create_image_task(
            content="识别图像中的物体",
            domain="图像识别",
            difficulty="中级",
            metadata={"category": "测试任务"}
        )
        
        # 验证任务创建
        self.assertIsNotNone(task.id)
        self.assertEqual(task.content, "识别图像中的物体")
        self.assertEqual(task.domain, "图像识别")
        self.assertEqual(task.difficulty, "中级")
        self.assertEqual(task.metadata.get("category"), "测试任务")
        
        # 测试序列化和反序列化
        task_dict = task.to_dict()
        restored_task = ImageTask.from_dict(task_dict)
        
        self.assertEqual(restored_task.id, task.id)
        self.assertEqual(restored_task.content, task.content)
        self.assertEqual(restored_task.domain, task.domain)
        self.assertEqual(restored_task.difficulty, task.difficulty)
        
        # 测试任务管理器
        tasks = task_manager.list_tasks()
        self.assertGreater(len(tasks), 0)
        self.assertIn(task.id, [t.id for t in tasks])
        
        logger.info("图像任务功能测试通过")
    
    def test_03_performance_comparison(self):
        """测试性能比较工具"""
        logger.info("测试性能比较工具...")
        
        from AIGO.models.training.self_correction.utils.performance_comparison import PerformanceComparison
        import pandas as pd
        import numpy as np
        
        # 创建性能比较工具
        performance_analyzer = PerformanceComparison()
        
        # 创建模拟数据
        def create_mock_dataframe(trainer_id):
            np.random.seed(42)  # 确保可重复性
            
            # 创建任务和迭代数据
            task_ids = [f"task_{i}" for i in range(1, 6)]
            iterations = list(range(1, 6))
            
            data = []
            for task_id in task_ids:
                base_score = np.random.uniform(0.3, 0.6)
                for iteration in iterations:
                    # 模拟分数随迭代提高
                    improvement = min(0.1 * iteration, 0.4)
                    score = min(base_score + improvement + np.random.uniform(-0.05, 0.05), 1.0)
                    
                    data.append({
                        'trainer_id': trainer_id,
                        'task_id': task_id,
                        'iteration': iteration,
                        'score': score,
                        'correct': 1 if score > 0.7 else 0,
                        'timestamp': pd.Timestamp.now() - pd.Timedelta(days=5-iteration)
                    })
            
            return pd.DataFrame(data)
        
        # 模拟两个训练器的数据
        df1 = create_mock_dataframe('trainer_1')
        df2 = create_mock_dataframe('trainer_2')
        df2['score'] = df2['score'] * 0.9  # 让第二个训练器性能稍差
        
        # 存储模拟数据
        performance_analyzer.analysis_cache = {
            'trainer_1': {'df': df1},
            'trainer_2': {'df': df2}
        }
        
        # 测试基本统计
        stats1 = performance_analyzer.get_basic_stats('trainer_1')
        self.assertIsNotNone(stats1)
        self.assertIn('avg_score', stats1)
        self.assertIn('correct_rate', stats1)
        
        # 测试高级统计
        stats2 = performance_analyzer.get_advanced_stats('trainer_1')
        self.assertIsNotNone(stats2)
        self.assertIn('avg_improvement', stats2)
        
        # 测试图表生成
        fig1 = performance_analyzer.create_learning_curve_plot('trainer_1')
        self.assertIsNotNone(fig1)
        
        fig2 = performance_analyzer.create_task_comparison_plot('trainer_1')
        self.assertIsNotNone(fig2)
        
        fig3 = performance_analyzer.create_heatmap_plot('trainer_1')
        self.assertIsNotNone(fig3)
        
        # 测试训练器比较
        comparison, fig4 = performance_analyzer.compare_trainers(['trainer_1', 'trainer_2'])
        self.assertIsNotNone(comparison)
        self.assertIsNotNone(fig4)
        self.assertIn('trainer_1', comparison)
        self.assertIn('trainer_2', comparison)
        
        # 保存测试图表
        test_output_dir = os.path.join(TEST_CONFIG['temp_dir'], 'performance_charts')
        os.makedirs(test_output_dir, exist_ok=True)
        
        fig1.savefig(os.path.join(test_output_dir, "learning_curve.png"))
        fig2.savefig(os.path.join(test_output_dir, "task_comparison.png"))
        fig3.savefig(os.path.join(test_output_dir, "heatmap.png"))
        fig4.savefig(os.path.join(test_output_dir, "trainer_comparison.png"))
        
        logger.info("性能比较工具测试通过")
    
    def test_04_web_interface(self):
        """测试Web界面"""
        logger.info("测试Web界面...")
        
        try:
            with web_server() as server_url:
                # 测试首页
                response = requests.get(server_url)
                self.assertEqual(response.status_code, 200)
                self.assertIn('自我纠正训练系统', response.text)
                
                # 测试训练器列表页面
                response = requests.get(f"{server_url}trainers")
                self.assertEqual(response.status_code, 200)
                
                # 测试创建训练器页面
                response = requests.get(f"{server_url}create_trainer")
                self.assertEqual(response.status_code, 200)
                
                # 测试性能分析页面
                response = requests.get(f"{server_url}analysis/performance")
                self.assertEqual(response.status_code, 200)
                
                logger.info("Web界面测试通过")
        except Exception as e:
            logger.error(f"Web界面测试失败: {e}")
            raise
    
    def test_05_integration_test_script(self):
        """测试集成测试脚本"""
        logger.info("测试集成测试脚本...")
        
        # 测试多模态功能测试脚本
        test_script_path = os.path.join(ROOT_DIR, 'AIGO', 'test_multimodal_features.py')
        
        # 检查脚本是否存在
        self.assertTrue(os.path.exists(test_script_path), f"测试脚本不存在: {test_script_path}")
        
        # 尝试导入脚本
        spec = importlib.util.spec_from_file_location("test_module", test_script_path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        # 检查脚本中的函数
        self.assertTrue(hasattr(test_module, 'test_image_task'))
        self.assertTrue(hasattr(test_module, 'test_performance_analysis'))
        
        logger.info("集成测试脚本测试通过")
    
    def test_06_start_script(self):
        """测试启动脚本"""
        logger.info("测试启动脚本...")
        
        # 测试Web界面启动脚本
        start_script_path = os.path.join(ROOT_DIR, 'AIGO', 'start_web_ui.py')
        
        # 检查脚本是否存在
        self.assertTrue(os.path.exists(start_script_path), f"启动脚本不存在: {start_script_path}")
        
        # 尝试导入脚本
        spec = importlib.util.spec_from_file_location("start_module", start_script_path)
        start_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(start_module)
        
        # 检查脚本中的函数
        self.assertTrue(hasattr(start_module, 'main'))
        
        logger.info("启动脚本测试通过")
    
    def test_07_readme_documentation(self):
        """测试README文档"""
        logger.info("测试README文档...")
        
        # 检查README文件
        readme_path = os.path.join(ROOT_DIR, 'AIGO', 'README.md')
        self.assertTrue(os.path.exists(readme_path), f"README文件不存在: {readme_path}")
        
        # 读取README内容
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键内容
        required_sections = [
            "多模态",
            "科研级性能分析",
            "自我纠正",
            "训练",
            "安装",
            "使用"
        ]
        
        for section in required_sections:
            self.assertIn(section, content, f"README中缺少'{section}'相关内容")
        
        logger.info("README文档测试通过")

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 按顺序添加测试
    test_cases = [
        'test_01_imports',
        'test_02_image_task',
        'test_03_performance_comparison',
        'test_04_web_interface',
        'test_05_integration_test_script',
        'test_06_start_script',
        'test_07_readme_documentation',
    ]
    
    for test_case in test_cases:
        suite.addTest(TestAIgoIntegration(test_case))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 