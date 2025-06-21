#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web界面测试脚本

测试自我纠正训练系统的Web界面。
"""

import os
import sys
from pathlib import Path
import logging
import threading
import time
import webbrowser

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

def run_web_server():
    """运行Web服务器"""
    try:
        from AIGO.models.training.self_correction.ui.web.app import app
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        logger.exception(f"运行Web服务器失败: {e}")

def prepare_test_data():
    """准备测试数据"""
    try:
        from AIGO.models.training.self_correction.task import Task, TaskManager
        from AIGO.models.training.self_correction.trainer import SelfCorrectionTrainer
        from AIGO.models.training.self_correction.ui.model_factory import SimpleModel
        from AIGO.models.training.self_correction.memory import TrainingRecord
        from AIGO.models.training.self_correction.evaluation import EvaluationResult
        
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
        
        # 为每个任务创建一些训练记录
        for task in tasks:
            print(f"为任务 {task.id} 创建训练记录...")
            
            # 生成解答
            solution = model.generate(f"任务: {task.content}\n\n解答:")
            
            # 创建评估结果
            evaluation = EvaluationResult(
                task_id=task.id,
                solution_id=f"{task.id}_1",
                scores={"准确性": 0.7, "效率": 0.6, "创新性": 0.5},
                overall_score=0.65,
                feedback={"准确性": "解答基本正确", "效率": "解答效率一般", "创新性": "解答创新性一般"},
                errors=[],
                correct=True,
                metadata={"evaluator": "测试评估器"}
            )
            
            # 创建训练记录
            record1 = TrainingRecord(
                id=f"{task.id}_1",
                task_id=task.id,
                solution=solution,
                evaluation=evaluation,
                iteration=1,
                metadata={"test": True, "params": {"temperature": 0.7, "top_p": 0.9}}
            )
            
            # 创建第二次迭代的评估结果（分数提高）
            evaluation2 = EvaluationResult(
                task_id=task.id,
                solution_id=f"{task.id}_2",
                scores={"准确性": 0.8, "效率": 0.7, "创新性": 0.6},
                overall_score=0.75,
                feedback={"准确性": "解答正确", "效率": "解答效率提高", "创新性": "解答创新性提高"},
                errors=[],
                correct=True,
                metadata={"evaluator": "测试评估器"}
            )
            
            # 创建第二次迭代的训练记录
            record2 = TrainingRecord(
                id=f"{task.id}_2",
                task_id=task.id,
                solution=solution + "\n\n(改进后的解答)",
                evaluation=evaluation2,
                iteration=2,
                metadata={"test": True, "params": {"temperature": 0.8, "top_p": 0.95}}
            )
            
            # 保存训练记录
            trainer.memory.store_record(record1)
            trainer.memory.store_record(record2)
            
        print("测试数据准备完成")
        return True
    except Exception as e:
        logger.exception(f"准备测试数据失败: {e}")
        return False

def main():
    """主函数"""
    # 准备测试数据
    if not prepare_test_data():
        print("准备测试数据失败，退出测试")
        return False
    
    # 在单独的线程中运行Web服务器
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 等待服务器启动
    print("启动Web服务器...")
    time.sleep(2)
    
    # 打开浏览器
    url = "http://localhost:5000"
    print(f"打开浏览器访问: {url}")
    webbrowser.open(url)
    
    # 等待用户手动关闭
    print("\n按 Ctrl+C 停止测试...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n测试结束")
    
    return True

if __name__ == "__main__":
    print("运行Web界面测试...")
    success = main()
    if success:
        print("Web界面测试完成")
    else:
        print("Web界面测试失败")
        sys.exit(1) 