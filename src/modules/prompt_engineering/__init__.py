"""
提示工程模块 - 为CodeAssistant提供高级提示词生成和优化功能
"""

from src.modules.prompt_engineering.templates import PromptTemplates
from src.modules.prompt_engineering.context_builder import ContextBuilder
from src.modules.prompt_engineering.optimizer import PromptOptimizer
from src.modules.prompt_engineering.evaluator import ResponseEvaluator
from src.modules.prompt_engineering.reflection import ReflectionEngine

# 导出所有组件
__all__ = [
    'PromptTemplates', 
    'ContextBuilder', 
    'PromptOptimizer', 
    'ResponseEvaluator', 
    'ReflectionEngine',
    'PromptEngineer'
]

class PromptEngineer:
    """
    提示工程师类 - 提供完整的提示词工程管理功能
    作为其他提示工程组件的统一入口
    """
    
    def __init__(self, config=None):
        """
        初始化提示工程师
        
        参数:
            config: 配置参数
        """
        self.config = config or {}
        
        # 初始化各组件
        self.templates = PromptTemplates()
        self.context_builder = ContextBuilder()
        self.optimizer = PromptOptimizer(config=self.config.get("optimizer"))
        self.evaluator = ResponseEvaluator(config=self.config.get("evaluator"))
        self.reflection_engine = ReflectionEngine(config=self.config.get("reflection"))
    
    def generate_prompt(self, task_type: str, **kwargs):
        """
        生成优化的提示词
        
        参数:
            task_type: 任务类型，如"code_completion", "debug"等
            **kwargs: 根据任务类型传递不同的参数
            
        返回:
            优化后的提示词字符串
        """
        # 构建上下文
        if task_type == "code_completion":
            context = self.context_builder.build_code_completion_context(
                code_fragment=kwargs.get("code_fragment", ""),
                file_path=kwargs.get("file_path"),
                project_files=kwargs.get("project_files"),
                language=kwargs.get("language"),
                code_history=kwargs.get("code_history")
            )
        elif task_type.startswith("problem_solving"):
            problem_subtype = task_type.split(".")[-1] if "." in task_type else "debug"
            context = self.context_builder.build_problem_solving_context(
                problem_type=problem_subtype,
                code=kwargs.get("code"),
                error_message=kwargs.get("error_message"),
                problem_description=kwargs.get("problem_description")
            )
        elif task_type.startswith("reflection"):
            reflection_subtype = task_type.split(".")[-1] if "." in task_type else "self_evaluation"
            context = self.context_builder.build_reflection_context(
                reflection_type=reflection_subtype,
                previous_response=kwargs.get("previous_response"),
                original_solution=kwargs.get("original_solution"),
                feedback=kwargs.get("feedback")
            )
        else:
            # 默认返回原始输入作为提示词
            context = kwargs.get("prompt", "")
        
        # 优化提示词
        optimized_prompt = self.optimizer.optimize(
            context, 
            task_type=task_type,
            context=kwargs
        )
        
        return optimized_prompt
    
    def evaluate_response(self, response: str, task_type: str, prompt: str = None, **kwargs):
        """
        评估模型回答质量
        
        参数:
            response: 模型回答
            task_type: 任务类型
            prompt: 原始提示词
            **kwargs: 其他上下文信息
            
        返回:
            评估结果，包括分数和反馈
        """
        return self.evaluator.evaluate(
            response, 
            task_type, 
            original_prompt=prompt,
            context=kwargs
        )
    
    def reflect_and_improve(self, response: str, task_type: str, **kwargs):
        """
        反思并改进模型回答
        
        参数:
            response: 原始回答
            task_type: 任务类型
            **kwargs: 其他上下文信息
            
        返回:
            反思结果，包括改进后的回答
        """
        return self.reflection_engine.reflect(
            response,
            task_type,
            context=kwargs
        )
    
    def get_stats(self):
        """获取提示工程性能统计信息"""
        return {
            "optimization": self.optimizer.get_optimization_stats() if hasattr(self.optimizer, "get_optimization_stats") else {},
            "evaluation": self.evaluator.get_evaluation_stats() if hasattr(self.evaluator, "get_evaluation_stats") else {},
            "reflection": self.reflection_engine.get_reflection_stats() if hasattr(self.reflection_engine, "get_reflection_stats") else {}
        } 