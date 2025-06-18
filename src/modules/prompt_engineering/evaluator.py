"""
提示词评估器 - 负责评估AI输出的质量并提供反馈
"""

from typing import Dict, Any, List, Optional, Tuple

class ResponseEvaluator:
    """提示词响应评估器，评估AI回答质量并提供反馈"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化评估器
        
        参数:
            config: 评估配置
        """
        self.config = config or {}
        self.evaluation_history = []
        
        # 评估维度及其权重
        self.dimensions = {
            "correctness": 0.35,     # 正确性
            "completeness": 0.20,    # 完整性
            "efficiency": 0.15,      # 效率
            "readability": 0.15,     # 可读性
            "best_practices": 0.15   # 最佳实践
        }
    
    def evaluate(self, response: str, task_type: str, 
                original_prompt: str = None, 
                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        评估AI回答质量
        
        参数:
            response: AI的回答
            task_type: 任务类型，如"code_completion"、"debug"等
            original_prompt: 原始提示词
            context: 上下文信息
            
        返回:
            评估结果，包含分数和反馈
        """
        # 根据不同任务类型评估
        if task_type.startswith("code_"):
            result = self._evaluate_code_response(response, task_type, context)
        elif task_type == "debug":
            result = self._evaluate_debug_response(response, context)
        else:
            result = self._evaluate_general_response(response, task_type)
            
        # 记录评估结果
        self._record_evaluation(result, task_type, len(response) if response else 0)
        
        return result
    
    def _evaluate_code_response(self, code_response: str, 
                              task_type: str, 
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """评估代码相关回答"""
        scores = {}
        feedback = {}
        
        # 评估代码正确性
        correctness_score, correctness_feedback = self._evaluate_code_correctness(
            code_response, context
        )
        scores["correctness"] = correctness_score
        feedback["correctness"] = correctness_feedback
        
        # 评估代码完整性
        completeness_score, completeness_feedback = self._evaluate_code_completeness(
            code_response, context
        )
        scores["completeness"] = completeness_score
        feedback["completeness"] = completeness_feedback
        
        # 评估代码效率
        efficiency_score, efficiency_feedback = self._evaluate_code_efficiency(
            code_response, context
        )
        scores["efficiency"] = efficiency_score
        feedback["efficiency"] = efficiency_feedback
        
        # 评估代码可读性
        readability_score, readability_feedback = self._evaluate_code_readability(
            code_response, context
        )
        scores["readability"] = readability_score
        feedback["readability"] = readability_feedback
        
        # 评估代码最佳实践
        best_practices_score, best_practices_feedback = self._evaluate_code_best_practices(
            code_response, context
        )
        scores["best_practices"] = best_practices_score
        feedback["best_practices"] = best_practices_feedback
        
        # 计算加权总分
        total_score = sum(scores[dim] * self.dimensions[dim] for dim in scores)
        
        # 生成整体反馈
        overall_feedback = self._generate_overall_feedback(scores, feedback)
        
        return {
            "scores": scores,
            "total_score": total_score,
            "feedback": feedback,
            "overall_feedback": overall_feedback
        }
    
    def _evaluate_debug_response(self, debug_response: str, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """评估调试相关回答"""
        scores = {}
        feedback = {}
        
        # 评估诊断清晰度
        diagnosis_score, diagnosis_feedback = self._evaluate_diagnosis_clarity(
            debug_response
        )
        scores["diagnosis"] = diagnosis_score
        feedback["diagnosis"] = diagnosis_feedback
        
        # 评估解决方案有效性
        solution_score, solution_feedback = self._evaluate_solution_effectiveness(
            debug_response, context
        )
        scores["solution"] = solution_score
        feedback["solution"] = solution_feedback
        
        # 评估解释质量
        explanation_score, explanation_feedback = self._evaluate_explanation_quality(
            debug_response
        )
        scores["explanation"] = explanation_score
        feedback["explanation"] = explanation_feedback
        
        # 计算总分 (权重分配: 诊断30%, 解决方案50%, 解释20%)
        total_score = (
            scores["diagnosis"] * 0.3 + 
            scores["solution"] * 0.5 + 
            scores["explanation"] * 0.2
        )
        
        # 生成整体反馈
        overall_feedback = f"诊断清晰度: {diagnosis_feedback}\n"
        overall_feedback += f"解决方案有效性: {solution_feedback}\n"
        overall_feedback += f"解释质量: {explanation_feedback}"
        
        return {
            "scores": scores,
            "total_score": total_score,
            "feedback": feedback,
            "overall_feedback": overall_feedback
        }
    
    def _evaluate_general_response(self, response: str, 
                                 task_type: str) -> Dict[str, Any]:
        """评估一般回答"""
        # 简单评估，基于回答长度和关键词
        length_score = min(1.0, len(response) / 500) if response else 0
        
        # 关键词检测 (示例)
        keywords = ["具体步骤", "详细说明", "例子", "示例", "原理", "解释"]
        keyword_score = sum(1 for kw in keywords if kw in response) / len(keywords)
        
        total_score = (length_score * 0.3) + (keyword_score * 0.7)
        
        feedback = "回答较为全面" if total_score > 0.7 else "回答可以更加详细"
        
        return {
            "scores": {
                "length": length_score,
                "keywords": keyword_score
            },
            "total_score": total_score,
            "feedback": {"general": feedback},
            "overall_feedback": feedback
        }
    
    def _evaluate_code_correctness(self, code: str, 
                                context: Dict[str, Any] = None) -> Tuple[float, str]:
        """
        评估代码正确性
        
        这里提供一个示例实现，实际项目中可能需要更复杂的静态分析或单元测试
        """
        # 这里应该包含实际的代码分析逻辑，例如:
        # 1. 语法检查
        # 2. 类型检查
        # 3. 边缘情况处理
        # 4. 简单的执行测试
        
        # 示例实现
        syntax_errors = self._check_syntax_errors(code)
        
        if syntax_errors:
            return 0.3, f"代码存在语法错误: {syntax_errors}"
            
        # 检查是否处理了常见边缘情况
        edge_cases_handled = self._check_edge_cases_handled(code, context)
        
        if not edge_cases_handled:
            return 0.7, "代码功能正确，但未处理一些边缘情况"
            
        return 0.95, "代码功能正确，并处理了主要边缘情况"
    
    def _evaluate_code_completeness(self, code: str, 
                                 context: Dict[str, Any] = None) -> Tuple[float, str]:
        """评估代码完整性"""
        # 检查代码是否包含必要的组件
        # 1. 导入语句
        # 2. 必要的函数/类定义
        # 3. 必要的错误处理
        
        # 示例实现
        has_imports = "import " in code or "from " in code
        has_error_handling = "try" in code or "except" in code or "if" in code
        
        if not has_imports and context and context.get("requires_imports", False):
            return 0.6, "代码缺少必要的导入语句"
            
        if not has_error_handling and context and context.get("requires_error_handling", False):
            return 0.7, "代码缺少必要的错误处理"
            
        return 0.9, "代码包含大部分必要的组件"
    
    def _evaluate_code_efficiency(self, code: str, 
                               context: Dict[str, Any] = None) -> Tuple[float, str]:
        """评估代码效率"""
        # 检查效率问题
        # 1. 算法复杂度
        # 2. 不必要的计算
        # 3. 资源使用
        
        # 示例实现 (非常简化)
        inefficient_patterns = [
            "for i in range(len(", 
            ".copy()", 
            "+ '*'" # 字符串重复使用加法而不是乘法
        ]
        
        found_patterns = [p for p in inefficient_patterns if p in code]
        
        if found_patterns:
            return 0.7, f"代码可能存在效率问题: {', '.join(found_patterns)}"
            
        return 0.9, "代码效率良好"
    
    def _evaluate_code_readability(self, code: str, 
                                context: Dict[str, Any] = None) -> Tuple[float, str]:
        """评估代码可读性"""
        # 检查可读性
        # 1. 变量命名
        # 2. 代码格式
        # 3. 注释
        
        # 示例实现
        has_comments = "#" in code or '"""' in code or "'''" in code
        has_good_var_names = not any(vn in code for vn in ["x", "y", "z", "i", "j", "k", "foo", "bar"])
        
        if not has_comments:
            return 0.6, "代码缺少注释，影响可读性"
            
        if not has_good_var_names:
            return 0.7, "代码使用了过于简单的变量名，可读性较差"
            
        return 0.9, "代码可读性良好"
    
    def _evaluate_code_best_practices(self, code: str, 
                                    context: Dict[str, Any] = None) -> Tuple[float, str]:
        """评估代码是否符合最佳实践"""
        # 检查最佳实践
        # 1. 设计模式使用
        # 2. 代码风格
        # 3. 行业标准
        
        # 示例实现
        language = context.get("language") if context else None
        
        if language == "Python":
            bad_practices = [
                "global ", 
                "exec(", 
                "__magic__"
            ]
            
            found_bad = [p for p in bad_practices if p in code]
            
            if found_bad:
                return 0.5, f"代码使用了不推荐的实践: {', '.join(found_bad)}"
        
        return 0.85, "代码大体符合最佳实践"
    
    def _generate_overall_feedback(self, scores: Dict[str, float], 
                                feedback: Dict[str, str]) -> str:
        """生成整体反馈"""
        # 找出得分最低的维度
        min_dimension = min(scores.items(), key=lambda x: x[1])
        
        weakest_area = min_dimension[0]
        weakest_score = min_dimension[1]
        
        if weakest_score < 0.6:
            overall = f"主要改进点: {weakest_area} - {feedback.get(weakest_area, '')}"
        elif sum(scores.values()) / len(scores) > 0.8:
            overall = "总体评价: 解决方案质量很高"
        else:
            overall = "总体评价: 解决方案质量一般，有改进空间"
            
        return overall
    
    def _check_syntax_errors(self, code: str) -> str:
        """
        检查代码中的语法错误
        
        这是一个简化的实现，实际中可能需要使用语言特定的解析器
        """
        # 简单检查一些常见语法错误
        if "def " in code and ":" not in code:
            return "函数定义缺少冒号"
            
        # 括号匹配检查
        if code.count("(") != code.count(")"):
            return "括号不匹配"
            
        if code.count("[") != code.count("]"):
            return "方括号不匹配"
            
        if code.count("{") != code.count("}"):
            return "花括号不匹配"
            
        # 引号匹配检查 (非常简化)
        if code.count('"') % 2 != 0 and code.count("'") % 2 != 0:
            return "引号不匹配"
            
        return ""
    
    def _check_edge_cases_handled(self, code: str, 
                               context: Dict[str, Any] = None) -> bool:
        """
        检查代码是否处理了边缘情况
        
        这是一个简化的实现，实际中需要更复杂的分析
        """
        # 检查一些常见的边缘情况处理
        has_null_check = "None" in code and "is None" in code
        has_empty_check = "len(" in code or "not " in code or "empty" in code
        has_zero_check = " == 0" in code or " != 0" in code
        
        return has_null_check or has_empty_check or has_zero_check
    
    def _record_evaluation(self, result: Dict[str, Any], 
                        task_type: str, response_length: int):
        """记录评估结果，用于后续分析和改进"""
        self.evaluation_history.append({
            "task_type": task_type,
            "total_score": result.get("total_score", 0),
            "response_length": response_length,
            "dimension_scores": result.get("scores", {})
        })
    
    def _evaluate_diagnosis_clarity(self, response: str) -> Tuple[float, str]:
        """评估诊断清晰度"""
        # 检查是否明确指出问题
        if "问题" in response and "原因" in response:
            return 0.9, "诊断明确，清晰指出了问题和根本原因"
        elif "问题" in response or "错误" in response:
            return 0.7, "诊断基本明确，但根本原因分析不足"
        else:
            return 0.4, "缺少明确的问题诊断"
    
    def _evaluate_solution_effectiveness(self, response: str, 
                                      context: Dict[str, Any] = None) -> Tuple[float, str]:
        """评估解决方案有效性"""
        # 检查是否提供了具体解决方案
        if "解决方案" in response and ("代码" in response or "```" in response):
            return 0.9, "提供了具体可行的解决方案"
        elif "修改" in response or "更改" in response:
            return 0.7, "提供了解决思路，但缺少具体实现"
        else:
            return 0.4, "缺少明确的解决方案"
    
    def _evaluate_explanation_quality(self, response: str) -> Tuple[float, str]:
        """评估解释质量"""
        # 检查解释的详细程度
        if "因为" in response and "这样" in response and len(response) > 200:
            return 0.9, "解释详细，逻辑清晰"
        elif "因为" in response or "原因是" in response:
            return 0.7, "提供了基本解释"
        else:
            return 0.5, "解释不足或缺失"
    
    def get_evaluation_stats(self) -> Dict[str, Any]:
        """获取评估统计信息"""
        if not self.evaluation_history:
            return {"count": 0}
            
        total = len(self.evaluation_history)
        avg_score = sum(entry["total_score"] for entry in self.evaluation_history) / total
        
        stats = {
            "count": total,
            "average_score": avg_score,
            "by_task_type": {}
        }
        
        # 按任务类型统计
        task_types = {}
        for entry in self.evaluation_history:
            task_type = entry["task_type"]
            if task_type not in task_types:
                task_types[task_type] = []
            task_types[task_type].append(entry["total_score"])
            
        for task_type, scores in task_types.items():
            stats["by_task_type"][task_type] = {
                "count": len(scores),
                "average_score": sum(scores) / len(scores)
            }
            
        return stats 