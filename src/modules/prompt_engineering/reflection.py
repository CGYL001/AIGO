"""
自我反思模块 - 帮助AI进行自我评估和输出质量改进
"""

from typing import Dict, Any, List, Optional, Tuple

class ReflectionEngine:
    """
    反思引擎，用于帮助AI进行自我评估和改进
    实现"思考-反思-改进"闭环
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化反思引擎
        
        参数:
            config: 配置参数
        """
        self.config = config or {
            "reflection_enabled": True,
            "max_iterations": 2,
            "reflection_threshold": 0.7
        }
        self.reflection_history = []
        
    def reflect(self, original_response: str, task_type: str, 
              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        对AI回答进行自我反思
        
        参数:
            original_response: AI的原始回答
            task_type: 任务类型
            context: 上下文信息
            
        返回:
            反思结果，包括建议的改进
        """
        if not self.config.get("reflection_enabled", True):
            return {
                "reflection_performed": False,
                "needs_improvement": False,
                "improved_response": original_response,
                "reflection_notes": "反思功能已禁用"
            }
        
        # 执行自我反思
        reflection_result = self._perform_reflection(original_response, task_type, context)
        
        # 记录反思历史
        self._record_reflection(reflection_result, task_type)
        
        return reflection_result
    
    def _perform_reflection(self, response: str, task_type: str, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行自我反思过程"""
        # 分析回答
        analysis = self._analyze_response(response, task_type)
        
        # 确定是否需要改进
        needs_improvement = analysis["score"] < self.config.get("reflection_threshold", 0.7)
        
        if not needs_improvement:
            return {
                "reflection_performed": True,
                "needs_improvement": False,
                "improved_response": response,
                "analysis": analysis,
                "reflection_notes": "回答质量符合要求，无需改进"
            }
        
        # 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(
            response, analysis, task_type
        )
        
        # 基于建议改进回答
        improved_response = self._improve_response(
            response, improvement_suggestions, task_type, context
        )
        
        return {
            "reflection_performed": True,
            "needs_improvement": True,
            "original_response": response,
            "improved_response": improved_response,
            "analysis": analysis,
            "improvement_suggestions": improvement_suggestions,
            "reflection_notes": "已根据反思结果改进回答"
        }
    
    def _analyze_response(self, response: str, task_type: str) -> Dict[str, Any]:
        """分析回答质量"""
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "score": 0.0
        }
        
        # 根据任务类型进行分析
        if task_type.startswith("code_"):
            analysis = self._analyze_code_response(response)
        elif task_type == "debug":
            analysis = self._analyze_debug_response(response)
        else:
            analysis = self._analyze_general_response(response)
        
        return analysis
    
    def _analyze_code_response(self, code: str) -> Dict[str, Any]:
        """分析代码回答"""
        strengths = []
        weaknesses = []
        
        # 代码长度检查
        if len(code) < 50:
            weaknesses.append("代码过短，可能不够完整")
        else:
            strengths.append("代码长度适中")
        
        # 代码结构检查
        if "def " in code or "class " in code:
            strengths.append("包含函数或类定义")
        else:
            weaknesses.append("缺少函数或类的结构化定义")
        
        # 注释检查
        if "#" in code or "'''" in code or '"""' in code:
            strengths.append("包含注释说明")
        else:
            weaknesses.append("缺少注释说明")
        
        # 错误处理检查
        if "try" in code and "except" in code:
            strengths.append("包含异常处理")
        else:
            weaknesses.append("缺少异常处理")
        
        # 计算总分
        score = (len(strengths) / (len(strengths) + len(weaknesses))) if (len(strengths) + len(weaknesses)) > 0 else 0.5
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "score": score
        }
    
    def _analyze_debug_response(self, debug_response: str) -> Dict[str, Any]:
        """分析调试回答"""
        strengths = []
        weaknesses = []
        
        # 问题诊断检查
        if "问题" in debug_response and "原因" in debug_response:
            strengths.append("明确诊断了问题和原因")
        else:
            weaknesses.append("缺少明确的问题诊断")
        
        # 解决方案检查
        if "解决" in debug_response and "```" in debug_response:
            strengths.append("提供了代码级解决方案")
        elif "修改" in debug_response or "更改" in debug_response:
            strengths.append("提供了解决思路")
        else:
            weaknesses.append("缺少具体解决方案")
        
        # 解释清晰度检查
        if len(debug_response) > 200 and ("因为" in debug_response or "所以" in debug_response):
            strengths.append("提供了详细解释")
        else:
            weaknesses.append("解释不够详细")
        
        # 计算总分
        score = (len(strengths) / (len(strengths) + len(weaknesses))) if (len(strengths) + len(weaknesses)) > 0 else 0.5
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "score": score
        }
    
    def _analyze_general_response(self, response: str) -> Dict[str, Any]:
        """分析一般回答"""
        strengths = []
        weaknesses = []
        
        # 长度检查
        if len(response) > 500:
            strengths.append("回答详尽")
        elif len(response) < 100:
            weaknesses.append("回答过短，可能不够详细")
        else:
            strengths.append("回答长度适中")
        
        # 结构检查
        if response.count("\n") > 5:
            strengths.append("回答结构清晰")
        else:
            weaknesses.append("回答结构可能不够清晰")
        
        # 关键词检查
        keywords = ["例如", "比如", "具体来说", "总结", "总的来说"]
        found_keywords = [kw for kw in keywords if kw in response]
        
        if found_keywords:
            strengths.append(f"使用了说明性词语: {', '.join(found_keywords)}")
        else:
            weaknesses.append("缺少说明性词语，可能不够具体")
        
        # 计算总分
        score = (len(strengths) / (len(strengths) + len(weaknesses))) if (len(strengths) + len(weaknesses)) > 0 else 0.5
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "score": score
        }
    
    def _generate_improvement_suggestions(self, response: str, 
                                       analysis: Dict[str, Any], 
                                       task_type: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于弱点给出建议
        for weakness in analysis.get("weaknesses", []):
            if "过短" in weakness:
                if task_type.startswith("code_"):
                    suggestions.append("扩展代码实现，添加必要的辅助函数和错误处理")
                else:
                    suggestions.append("提供更多详细信息和具体例子")
            
            elif "注释" in weakness:
                suggestions.append("添加代码注释，解释关键逻辑和复杂部分")
            
            elif "异常处理" in weakness or "错误处理" in weakness:
                suggestions.append("添加适当的异常/错误处理机制")
            
            elif "结构" in weakness:
                if task_type.startswith("code_"):
                    suggestions.append("重构代码，使用更清晰的函数/类结构")
                else:
                    suggestions.append("使用标题、段落和列表改善回答结构")
            
            elif "问题诊断" in weakness:
                suggestions.append("明确指出问题的根本原因和影响")
            
            elif "解决方案" in weakness:
                suggestions.append("提供具体、可操作的解决步骤或代码示例")
            
            elif "解释" in weakness:
                suggestions.append("添加更详细的解释，阐述原理和逻辑")
            
            elif "具体" in weakness:
                suggestions.append("添加具体示例或用例说明")
        
        return suggestions
    
    def _improve_response(self, original_response: str, 
                       suggestions: List[str], 
                       task_type: str,
                       context: Dict[str, Any] = None) -> str:
        """基于建议改进回答"""
        improved_response = original_response
        
        # 这里是示例改进逻辑，实际项目中可能需要调用大语言模型来生成改进后的回答
        # 例如，可以构建提示词，让模型基于原始回答和改进建议生成新的回答
        
        # 简单的改进逻辑示例
        if not suggestions:
            return original_response
            
        # 添加反思和改进说明
        reflection_note = "\n\n【自我反思与改进】\n"
        reflection_note += "在回顾原始回答后，我注意到以下需要改进的方面：\n"
        
        for i, suggestion in enumerate(suggestions):
            reflection_note += f"{i+1}. {suggestion}\n"
            
        reflection_note += "\n下面是改进后的回答：\n\n"
        
        # 在实际项目中，这里应该使用更高级的逻辑来改进回答
        # 例如，可以调用另一个模型实例来基于原始回答和建议生成改进后的回答
        # 这里简单地添加反思说明作为示例
        
        improved_response = reflection_note + improved_response
        
        return improved_response
    
    def _record_reflection(self, reflection_result: Dict[str, Any], task_type: str):
        """记录反思历史，用于后续分析和改进"""
        self.reflection_history.append({
            "task_type": task_type,
            "performed": reflection_result.get("reflection_performed", False),
            "needed_improvement": reflection_result.get("needs_improvement", False),
            "analysis_score": reflection_result.get("analysis", {}).get("score", 0),
            "suggestion_count": len(reflection_result.get("improvement_suggestions", [])),
            "response_length_diff": (
                len(reflection_result.get("improved_response", "")) - 
                len(reflection_result.get("original_response", ""))
            ) if reflection_result.get("needs_improvement", False) else 0
        })
    
    def get_reflection_stats(self) -> Dict[str, Any]:
        """获取反思统计信息"""
        if not self.reflection_history:
            return {"count": 0}
            
        total = len(self.reflection_history)
        improvement_count = sum(1 for entry in self.reflection_history if entry["needed_improvement"])
        
        stats = {
            "count": total,
            "improvement_needed_rate": improvement_count / total if total > 0 else 0,
            "average_score_before_reflection": sum(entry["analysis_score"] for entry in self.reflection_history) / total if total > 0 else 0,
            "by_task_type": {}
        }
        
        # 按任务类型统计
        task_types = {}
        for entry in self.reflection_history:
            task_type = entry["task_type"]
            if task_type not in task_types:
                task_types[task_type] = {"count": 0, "needed_improvement": 0}
            
            task_types[task_type]["count"] += 1
            if entry["needed_improvement"]:
                task_types[task_type]["needed_improvement"] += 1
        
        for task_type, data in task_types.items():
            improvement_rate = (
                data["needed_improvement"] / data["count"] 
                if data["count"] > 0 else 0
            )
            stats["by_task_type"][task_type] = {
                "count": data["count"],
                "improvement_needed_rate": improvement_rate
            }
        
        return stats 