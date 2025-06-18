"""
提示词优化器 - 用于在执行前对提示词进行优化和调整
"""

from typing import Dict, Any, List, Optional

class PromptOptimizer:
    """
    提示词优化器，用于在使用前对提示词进行增强和优化
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化提示词优化器
        
        参数:
            config: 优化器配置，包括优化参数和策略
        """
        self.config = config or {}
        self.optimization_history = []
    
    def optimize(self, prompt: str, task_type: str = None, 
                 context: Dict[str, Any] = None) -> str:
        """
        优化提示词
        
        参数:
            prompt: 原始提示词
            task_type: 任务类型，例如 "code_completion", "debug" 等
            context: 上下文信息
            
        返回:
            优化后的提示词
        """
        optimized_prompt = prompt
        
        # 记录优化前的提示词
        original_prompt = prompt
        
        # 应用各种优化策略
        optimized_prompt = self._add_instruction_clarity(optimized_prompt, task_type)
        optimized_prompt = self._add_examples(optimized_prompt, task_type)
        optimized_prompt = self._add_constraints(optimized_prompt, task_type, context)
        optimized_prompt = self._add_reflection_prompts(optimized_prompt, task_type)
        
        # 记录优化历史
        self._record_optimization(original_prompt, optimized_prompt, task_type)
        
        return optimized_prompt
    
    def _add_instruction_clarity(self, prompt: str, task_type: str = None) -> str:
        """增强指令清晰度"""
        if not task_type:
            return prompt
            
        # 针对不同任务类型添加清晰指令
        clarity_headers = {
            "code_completion": "\n请提供专业、符合最佳实践的代码补全，确保代码可以直接运行。\n",
            "debug": "\n请提供详细的错误诊断和最佳修复方案。\n",
            "code_review": "\n请按照安全性、性能和可维护性三个维度全面审查代码。\n",
            "refactoring": "\n请提供高度优化的重构方案，保持功能不变的同时改善代码质量。\n"
        }
        
        header = clarity_headers.get(task_type, "")
        if header:
            return header + prompt
            
        return prompt
    
    def _add_examples(self, prompt: str, task_type: str = None) -> str:
        """添加示例，帮助模型理解期望输出格式"""
        if not task_type or task_type not in ["code_completion", "debug"]:
            return prompt
            
        examples = {
            "code_completion": """
例如，如果我提供以下代码片段:
```
def calculate_average(numbers):
    # 计算列表中数字的平均值
    
```

你应该补全为:
```
def calculate_average(numbers):
    # 计算列表中数字的平均值
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```
            """,
            
            "debug": """
例如，如果代码和错误信息为:
```
def divide(a, b):
    return a / b

result = divide(5, 0)
```
错误: ZeroDivisionError: division by zero

你应该回答:
```
问题诊断:
- 在divide函数中，当b为0时尝试执行除法操作，导致ZeroDivisionError异常

修复方案:
def divide(a, b):
    if b == 0:
        return "错误: 不能除以零"
    return a / b
```
            """
        }
        
        example = examples.get(task_type, "")
        if example:
            return prompt + "\n" + example
            
        return prompt
    
    def _add_constraints(self, prompt: str, task_type: str = None, 
                       context: Dict[str, Any] = None) -> str:
        """添加约束条件"""
        if not context:
            return prompt
            
        # 根据上下文添加约束
        constraints = []
        
        # 根据语言添加约束
        language = context.get("language") if context else None
        if language:
            if language == "Python":
                constraints.append("- 遵循PEP8编码规范")
                constraints.append("- 使用类型提示增强代码可读性")
            elif language == "JavaScript" or language == "TypeScript":
                constraints.append("- 使用现代ES6+语法")
                constraints.append("- 避免使用var，优先使用const和let")
        
        # 根据项目特征添加约束
        project_features = context.get("project_features", []) if context else []
        if "test_driven" in project_features:
            constraints.append("- 确保代码有对应的测试用例")
        if "performance_critical" in project_features:
            constraints.append("- 性能优化是首要考虑因素")
        
        # 将约束添加到提示词中
        if constraints:
            constraint_text = "\n请在解决方案中遵循以下约束:\n" + "\n".join(constraints) + "\n"
            return prompt + constraint_text
            
        return prompt
    
    def _add_reflection_prompts(self, prompt: str, task_type: str = None) -> str:
        """添加反思提示，鼓励模型进行自我评估"""
        reflection_suffix = """

在提供解决方案前，请思考:
1. 这个解决方案是否涵盖了所有边缘情况？
2. 代码是否可能引入新的问题？
3. 是否符合给定上下文的最佳实践？
4. 是否有更简洁或更高效的方法？
"""
        
        # 根据配置决定是否添加反思提示
        if self.config.get("use_reflection", True) and task_type != "simple_query":
            return prompt + reflection_suffix
            
        return prompt
    
    def _record_optimization(self, original: str, optimized: str, task_type: str):
        """记录优化历史，用于后续分析和改进"""
        from datetime import datetime
        self.optimization_history.append({
            "task_type": task_type,
            "original_length": len(original),
            "optimized_length": len(optimized),
            "diff_size": len(optimized) - len(original),
            "timestamp": datetime.now().isoformat()
        })
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        if not self.optimization_history:
            return {"count": 0}
            
        total = len(self.optimization_history)
        avg_expansion = sum(entry["diff_size"] for entry in self.optimization_history) / total
        
        stats = {
            "count": total,
            "average_expansion": avg_expansion,
            "by_task_type": {}
        }
        
        # 按任务类型统计
        task_types = {}
        for entry in self.optimization_history:
            task_type = entry["task_type"] or "unknown"
            if task_type not in task_types:
                task_types[task_type] = []
            task_types[task_type].append(entry["diff_size"])
            
        for task_type, sizes in task_types.items():
            stats["by_task_type"][task_type] = {
                "count": len(sizes),
                "average_expansion": sum(sizes) / len(sizes)
            }
            
        return stats

