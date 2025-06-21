#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基本训练测试脚本

测试自我纠正训练系统的基本训练功能。
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
        logging.StreamHandler(),
        logging.FileHandler("training_test.log")
    ]
)

logger = logging.getLogger(__name__)

def run_basic_training():
    """运行基本训练测试"""
    try:
        from AIGO.models.training.self_correction.task import Task, TaskManager
        from AIGO.models.training.self_correction.trainer import SelfCorrectionTrainer
        from AIGO.models.training.self_correction.ui.model_factory import SimpleModel
        
        print("创建测试任务...")
        tasks = [
            Task(
                id="math_test_01",
                content="求解方程：2x + 3 = 7",
                domain="数学",
                difficulty="初级",
                answer="x = 2",
                constraints=["必须给出完整的解题步骤", "需要进行验证"]
            ),
            Task(
                id="code_test_01",
                content="编写一个函数计算斐波那契数列的第n个数",
                domain="编程",
                difficulty="中级",
                constraints=["函数必须高效", "必须处理边界情况", "需要添加注释"]
            ),
            Task(
                id="writing_test_01",
                content="写一篇关于人工智能的短文，不少于100字",
                domain="写作",
                difficulty="初级",
                constraints=["内容必须准确", "结构需要清晰", "需要包含AI的分类"]
            )
        ]
        
        print("创建简单模型...")
        model = SimpleModel()
        
        print("创建训练器...")
        trainer = SelfCorrectionTrainer(
            model=model,
            storage_path="temp_training_memory",
            checkpoint_dir="temp_checkpoints"
        )
        
        # 注册回调
        def on_iteration_start(task, iteration, params):
            print(f"开始第 {iteration} 次迭代，任务: {task.domain}")
            
        def on_iteration_end(task, iteration, solution, evaluation, improvement):
            print(f"完成第 {iteration} 次迭代，评分: {evaluation.overall_score:.2f}, 提升: {improvement:.2f}")
            
        def on_training_complete(results):
            print("训练完成!")
            print(f"成功任务数: {len(results['completed_tasks'])}")
            print(f"失败任务数: {len(results['failed_tasks'])}")
            print(f"平均分数提升: {results['improvement']:.2f}")
        
        trainer.register_callback("on_iteration_start", on_iteration_start)
        trainer.register_callback("on_iteration_end", on_iteration_end)
        trainer.register_callback("on_training_complete", on_training_complete)
        
        print("开始训练...")
        result = trainer.train(tasks=tasks)
        
        if result["success"]:
            print("\n===== 训练结果摘要 =====")
            print(f"任务总数: {len(tasks)}")
            print(f"成功任务数: {len(result['results']['completed_tasks'])}")
            print(f"平均分数提升: {result['results']['improvement']:.2f}")
            print(f"训练时间: {result['results']['training_time']:.1f}秒")
            print("========================\n")
            return True
        else:
            print(f"训练失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        logger.exception(f"训练测试失败: {e}")
        return False

if __name__ == "__main__":
    print("运行基本训练测试...")
    success = run_basic_training()
    if success:
        print("基本训练测试通过!")
    else:
        print("基本训练测试失败!")
        sys.exit(1) 