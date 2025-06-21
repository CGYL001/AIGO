#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自我纠正训练系统测试脚本

测试自我纠正训练系统的各个组件是否正常工作。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(os.path.dirname(os.path.abspath(__file__)))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 测试导入
def test_imports():
    """测试导入是否正常"""
    print("测试导入...")
    
    try:
        # 导入任务相关模块
        from AIGO.models.training.self_correction.task import Task, TaskManager
        print("✓ 成功导入任务模块")
        
        # 导入评估相关模块
        from AIGO.models.training.self_correction.evaluation import EvaluationResult, ModelBasedEvaluator
        print("✓ 成功导入评估模块")
        
        # 导入反馈相关模块
        from AIGO.models.training.self_correction.feedback import FeedbackProcessor
        print("✓ 成功导入反馈模块")
        
        # 导入记忆相关模块
        from AIGO.models.training.self_correction.memory import TrainingRecord, MemoryModule
        print("✓ 成功导入记忆模块")
        
        # 导入奖励相关模块
        from AIGO.models.training.self_correction.reward import RewardSystem
        print("✓ 成功导入奖励模块")
        
        # 导入调优相关模块
        from AIGO.models.training.self_correction.tuner import AdaptiveTuner
        print("✓ 成功导入调优模块")
        
        # 导入训练器
        from AIGO.models.training.self_correction.trainer import SelfCorrectionTrainer
        print("✓ 成功导入训练器模块")
        
        # 导入多模态支持
        from AIGO.models.training.self_correction.multimodal.image_task import ImageTask
        from AIGO.models.training.self_correction.multimodal.multimodal_evaluator import MultimodalEvaluator
        print("✓ 成功导入多模态支持模块")
        
        # 导入UI相关模块
        from AIGO.models.training.self_correction.ui.model_factory import get_model, SimpleModel
        print("✓ 成功导入模型工厂模块")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

# 测试任务创建和管理
def test_task_management():
    """测试任务创建和管理功能"""
    print("\n测试任务管理...")
    
    try:
        from AIGO.models.training.self_correction.task import Task, TaskManager
        
        # 创建任务
        task = Task(
            id="test_task_01",
            content="这是一个测试任务",
            domain="测试",
            difficulty="中级",
            answer="这是参考答案"
        )
        print(f"✓ 成功创建任务: {task}")
        
        # 创建任务管理器
        task_manager = TaskManager()
        
        # 添加任务
        task_id = task_manager.add_task(task)
        print(f"✓ 成功添加任务，ID: {task_id}")
        
        # 获取任务
        retrieved_task = task_manager.get_task(task_id)
        if retrieved_task and retrieved_task.id == task_id:
            print(f"✓ 成功获取任务: {retrieved_task}")
        else:
            print("✗ 获取任务失败")
        
        return True
    except Exception as e:
        print(f"✗ 任务管理测试失败: {e}")
        return False

# 测试简单模型
def test_simple_model():
    """测试简单模型"""
    print("\n测试简单模型...")
    
    try:
        from AIGO.models.training.self_correction.ui.model_factory import SimpleModel
        
        # 创建模型
        model = SimpleModel(name="测试模型")
        print(f"✓ 成功创建模型: {model.name}")
        
        # 测试生成
        prompt = "这是一个任务，请解答编程问题"
        response = model.generate(prompt)
        print(f"✓ 模型生成成功，生成了 {len(response)} 个字符")
        print(f"  生成内容片段: {response[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ 简单模型测试失败: {e}")
        return False

# 测试训练器基本功能
def test_trainer_basic():
    """测试训练器基本功能"""
    print("\n测试训练器基本功能...")
    
    try:
        from AIGO.models.training.self_correction.trainer import SelfCorrectionTrainer
        from AIGO.models.training.self_correction.ui.model_factory import SimpleModel
        
        # 创建模型
        model = SimpleModel()
        
        # 创建训练器
        trainer = SelfCorrectionTrainer(
            model=model,
            storage_path="temp_training_memory",
            checkpoint_dir="temp_checkpoints"
        )
        print(f"✓ 成功创建训练器")
        
        # 获取状态
        status = trainer.get_status()
        print(f"✓ 成功获取状态: {status['status']}")
        
        return True
    except Exception as e:
        print(f"✗ 训练器基本功能测试失败: {e}")
        return False

# 运行所有测试
def run_all_tests():
    """运行所有测试"""
    print("开始测试自我纠正训练系统...\n")
    
    results = []
    
    # 测试导入
    results.append(("导入测试", test_imports()))
    
    # 测试任务管理
    results.append(("任务管理测试", test_task_management()))
    
    # 测试简单模型
    results.append(("简单模型测试", test_simple_model()))
    
    # 测试训练器基本功能
    results.append(("训练器基本功能测试", test_trainer_basic()))
    
    # 打印测试结果摘要
    print("\n===== 测试结果摘要 =====")
    all_passed = True
    for name, passed in results:
        status = "通过" if passed else "失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n所有测试通过! 系统可以正常工作。")
    else:
        print("\n部分测试失败，请检查上面的错误信息。")

if __name__ == "__main__":
    run_all_tests() 