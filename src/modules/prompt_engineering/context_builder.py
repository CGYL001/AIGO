"""
上下文构建器 - 负责组装各种信息形成完整的提示词上下文
"""

import os
import sys
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.modules.prompt_engineering.templates import PromptTemplates


class ContextBuilder:
    """
    构建提示词上下文的工具类，负责将各种信息组装成完整的提示词
    """
    
    def __init__(self):
        self.templates = PromptTemplates()
    
    def build_code_completion_context(self, 
                                     code_fragment: str, 
                                     file_path: str = None,
                                     project_files: List[str] = None,
                                     language: str = None,
                                     code_history: List[Dict[str, Any]] = None) -> str:
        """
        构建代码补全的提示词上下文
        
        参数:
            code_fragment: 需要补全的代码片段
            file_path: 当前文件路径
            project_files: 相关项目文件列表
            language: 编程语言
            code_history: 用户之前的代码修改历史
            
        返回:
            完整的提示词字符串
        """
        # 构建上下文信息
        context = {
            "file_path": file_path or "未知文件",
            "language": language or self._infer_language(file_path, code_fragment),
            "project_structure": self._summarize_project_structure(project_files) if project_files else "未提供项目结构",
            "coding_history": self._summarize_coding_history(code_history) if code_history else "无历史记录"
        }
        
        # 使用模板填充
        context_str = f"""
文件路径: {context['file_path']}
编程语言: {context['language']}
项目结构概要: 
{context['project_structure']}

代码历史:
{context['coding_history']}
        """
        
        # 填充模板
        return self.templates.CODE_DEVELOPMENT["code_completion"].format(
            context=context_str,
            code_fragment=code_fragment
        )
    
    def build_problem_solving_context(self, 
                                    problem_type: str,
                                    code: str = None, 
                                    error_message: str = None,
                                    problem_description: str = None) -> str:
        """
        构建问题解决的提示词上下文
        
        参数:
            problem_type: 问题类型，例如 "debug" 或 "algorithm"
            code: 代码内容
            error_message: 错误信息
            problem_description: 问题描述
            
        返回:
            完整的提示词字符串
        """
        if problem_type == "debug":
            return self.templates.PROBLEM_SOLVING["debug"].format(
                code=code or "",
                error_message=error_message or "未提供错误信息"
            )
        elif problem_type == "algorithm":
            return self.templates.PROBLEM_SOLVING["algorithm"].format(
                problem_description=problem_description or "未提供问题描述"
            )
        else:
            raise ValueError(f"不支持的问题类型: {problem_type}")
    
    def build_reflection_context(self, 
                               reflection_type: str,
                               previous_response: str = None,
                               original_solution: str = None,
                               feedback: str = None) -> str:
        """
        构建自我反思的提示词上下文
        
        参数:
            reflection_type: 反思类型，例如 "self_evaluation" 或 "iterative_improvement"
            previous_response: 之前的回答
            original_solution: 原始解决方案
            feedback: 反馈
            
        返回:
            完整的提示词字符串
        """
        if reflection_type == "self_evaluation":
            return self.templates.REFLECTION["self_evaluation"].format(
                previous_response=previous_response or "未提供之前的回答"
            )
        elif reflection_type == "iterative_improvement":
            return self.templates.REFLECTION["iterative_improvement"].format(
                original_solution=original_solution or "未提供原始解决方案",
                feedback=feedback or "未提供反馈"
            )
        else:
            raise ValueError(f"不支持的反思类型: {reflection_type}")
    
    def _infer_language(self, file_path: Optional[str], code_fragment: str) -> str:
        """根据文件路径和代码片段推断编程语言"""
        if not file_path:
            # 简单的语言特征检测
            if "def " in code_fragment and ":" in code_fragment:
                return "Python"
            elif "{" in code_fragment and "}" in code_fragment and ";" in code_fragment:
                return "JavaScript/TypeScript/Java/C++"
            else:
                return "未知语言"
        
        # 根据文件扩展名推断
        ext_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java", 
            ".cpp": "C++",
            ".c": "C",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".cs": "C#",
            ".html": "HTML",
            ".css": "CSS",
            ".sql": "SQL"
        }
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext_map.get(ext, "未知语言")
    
    def _summarize_project_structure(self, project_files: List[str]) -> str:
        """总结项目结构"""
        if not project_files or len(project_files) == 0:
            return "未提供项目文件"
            
        # 简单总结项目文件结构
        summary = "项目包含以下关键文件:\n"
        
        # 仅包含最多10个最相关的文件
        relevant_files = project_files[:10]
        for file in relevant_files:
            summary += f"- {file}\n"
            
        if len(project_files) > 10:
            summary += f"... 以及其他 {len(project_files) - 10} 个文件\n"
            
        return summary
    
    def _summarize_coding_history(self, code_history: List[Dict[str, Any]]) -> str:
        """总结代码修改历史"""
        if not code_history or len(code_history) == 0:
            return "无历史记录"
            
        summary = "最近的代码修改:\n"
        
        # 仅包含最近5次修改
        recent_history = code_history[-5:]
        for entry in recent_history:
            action = entry.get("action", "未知操作")
            file = entry.get("file", "未知文件")
            summary += f"- {action} 在 {file}\n"
            
        return summary 