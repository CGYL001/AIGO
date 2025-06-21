#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化版训练测试脚本

测试自我纠正训练系统的基本功能，跳过调优步骤。
"""

import os
import sys
from pathlib import Path
import logging

# 添加项目根目录到路径
project_root = Path(os.path.dirname(os.path.abspath(__file__)))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_simple_training():
    """运行简化版训练测试"""
    try:
        from AIGO.models.training.self_correction.task import Task, TaskManager
        from AIGO.models.training.self_correction.trainer import SelfCorrectionTrainer, TrainingStatus
        from AIGO.models.training.self_correction.ui.model_factory import SimpleModel
        
        print("创建测试任务...")
        task = Task(
            id="math_test_01",
            content="求解方程：2x + 3 = 7",
            domain="数学",
            difficulty="初级",
            answer="x = 2",
            constraints=["必须给出完整的解题步骤", "需要进行验证"]
        )
        
        print("创建简单模型...")
        model = SimpleModel()
        
        print("创建训练器...")
        trainer = SelfCorrectionTrainer(
            model=model,
            storage_path="temp_training_memory",
            checkpoint_dir="temp_checkpoints"
        )
        
        # 手动生成解答并评估
        print("生成解答...")
        solution = model.generate(f"任务: {task.content}\n\n解答:")
        print(f"生成的解答: {solution[:100]}...")
        
        print("评估解答...")
        from AIGO.models.training.self_correction.evaluation import ModelBasedEvaluator, EvaluationResult
        
        # 创建一个简单的评估结果
        evaluation = EvaluationResult(
            task_id=task.id,
            solution_id=f"{task.id}_test",
            scores={"准确性": 0.8, "效率": 0.7, "创新性": 0.6},
            overall_score=0.75,
            feedback={"准确性": "解答正确", "效率": "解答效率一般", "创新性": "解答有一定创新性"},
            errors=[],
            correct=True,
            metadata={"evaluator": "测试评估器"}
        )
        
        print(f"评估结果: 分数={evaluation.overall_score}, 正确={evaluation.correct}")
        
        # 保存训练记录
        print("保存训练记录...")
        from AIGO.models.training.self_correction.memory import TrainingRecord
        
        record = TrainingRecord(
            id=f"{task.id}_test",
            task_id=task.id,
            solution=solution,
            evaluation=evaluation,
            iteration=1,
            metadata={"test": True, "params": {"temperature": 0.7, "top_p": 0.9}}
        )
        
        trainer.memory.store_record(record)
        print("训练记录已保存")
        
        # 获取训练状态
        status = trainer.get_status()
        print(f"训练器状态: {status['status']}")
        
        return True
    except Exception as e:
        logger.exception(f"训练测试失败: {e}")
        return False

if __name__ == "__main__":
    print("运行简化版训练测试...")
    success = run_simple_training()
    if success:
        print("简化版训练测试通过!")
    else:
        print("简化版训练测试失败!")
        sys.exit(1) 