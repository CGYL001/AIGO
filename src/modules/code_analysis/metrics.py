"""
代码度量计算器 - 负责计算各种代码度量指标
"""

import re
from typing import Dict, Any

from src.modules.code_analysis.utils import count_comment_lines

class MetricsCalculator:
    """代码度量计算器，负责计算各种代码度量指标"""
    
    def __init__(self):
        """初始化度量计算器"""
        pass
    
    def calculate_metrics(self, content: str, language: str) -> Dict[str, Any]:
        """
        计算代码度量指标
        
        Args:
            content: 代码内容
            language: 编程语言
            
        Returns:
            Dict[str, Any]: 度量指标结果
        """
        lines = content.count('\n') + 1
        non_blank_lines = len([line for line in content.split('\n') if line.strip()])
        comment_lines = count_comment_lines(content, language)
        
        # 计算复杂度
        complexity = self.calculate_complexity(content, language)
        
        # 计算其他指标
        halstead = self.calculate_halstead_metrics(content, language)
        maintainability = self.calculate_maintainability_index(complexity, halstead, lines)
        
        return {
            "lines": lines,
            "non_blank_lines": non_blank_lines,
            "comment_lines": comment_lines,
            "comment_percentage": (comment_lines / non_blank_lines * 100) if non_blank_lines > 0 else 0,
            "complexity": complexity,
            "halstead": halstead,
            "maintainability": maintainability
        }
    
    def calculate_complexity(self, content: str, language: str) -> Dict[str, Any]:
        """
        计算代码复杂度指标
        
        Args:
            content: 代码内容
            language: 编程语言
            
        Returns:
            Dict[str, Any]: 复杂度指标
        """
        # 计算圈复杂度：决策点 + 1
        decision_points = 0
        
        if language == "python":
            # Python的决策点
            decision_points = len(re.findall(r'\bif\b|\bfor\b|\bwhile\b|\belif\b|\bwith\b|\band\b|\bor\b', content))
        elif language in ["javascript", "typescript", "java", "cpp", "csharp"]:
            # C风格语言的决策点
            decision_points = len(re.findall(r'\bif\b|\bfor\b|\bwhile\b|\b&&\b|\b\|\|\b|\b\?\b|\bcatch\b|\bcase\b', content))
        elif language == "go":
            # Go语言的决策点
            decision_points = len(re.findall(r'\bif\b|\bfor\b|\bselect\b|\bswitch\b|\bcase\b', content))
        
        # 圈复杂度
        cyclomatic_complexity = decision_points + 1
        
        # 巢状深度
        nesting_depth = self._calculate_nesting_depth(content, language)
        
        return {
            "cyclomatic": cyclomatic_complexity,
            "nesting_depth": nesting_depth
        }
    
    def _calculate_nesting_depth(self, content: str, language: str) -> int:
        """
        计算代码的巢状深度
        
        Args:
            content: 代码内容
            language: 编程语言
            
        Returns:
            int: 巢状深度
        """
        # 简化的巢状深度计算
        lines = content.split('\n')
        max_depth = 0
        current_depth = 0
        
        if language == "python":
            # Python使用缩进表示嵌套
            indentation_stack = [0]  # 初始无缩进
            
            for line in lines:
                if not line.strip():  # 跳过空行
                    continue
                    
                # 计算当前行的缩进
                indentation = len(line) - len(line.lstrip())
                
                # 如果缩进增加，说明深度增加
                if indentation > indentation_stack[-1]:
                    indentation_stack.append(indentation)
                    current_depth += 1
                # 如果缩进减少，说明深度减少
                elif indentation < indentation_stack[-1]:
                    while indentation_stack and indentation < indentation_stack[-1]:
                        indentation_stack.pop()
                        current_depth -= 1
                    # 确保栈不为空
                    if not indentation_stack:
                        indentation_stack.append(0)
                
                max_depth = max(max_depth, current_depth)
                
        else:
            # 基于花括号的语言
            for line in lines:
                # 计算左花括号增加的深度
                current_depth += line.count('{')
                # 计算右花括号减少的深度
                current_depth -= line.count('}')
                # 更新最大深度
                max_depth = max(max_depth, current_depth)
        
        return max_depth
    
    def calculate_halstead_metrics(self, content: str, language: str) -> Dict[str, Any]:
        """
        计算Halstead度量指标
        
        Args:
            content: 代码内容
            language: 编程语言
            
        Returns:
            Dict[str, Any]: Halstead度量结果
        """
        # 简化的Halstead度量计算
        # 实际实现中，应该根据不同语言精确识别操作符和操作数
        
        # 假设操作符包括：+, -, *, /, =, ==, !=, <, >, <=, >=, (, ), [, ], {, }, and, or, not等
        # 简化的实现，仅计算部分常见操作符
        operators = re.findall(r'[\+\-\*/=<>!&\|%\^\(\)\[\]\{\}]|and\b|or\b|not\b|if\b|for\b|while\b', content)
        
        # 假设操作数包括变量名、常量值等
        # 简化的实现，使用非空白非操作符的连续字符作为操作数
        operands = re.findall(r'[a-zA-Z0-9_]+', content)
        
        # 统计不同的操作符和操作数
        n1 = len(set(operators))  # 不同操作符的数量
        n2 = len(set(operands))   # 不同操作数的数量
        N1 = len(operators)       # 操作符出现的总次数
        N2 = len(operands)        # 操作数出现的总次数
        
        # 防止除零错误
        if n1 == 0 or n2 == 0:
            return {
                "vocabulary": 0,
                "length": 0,
                "volume": 0,
                "difficulty": 0,
                "effort": 0
            }
        
        # 计算Halstead度量
        vocabulary = n1 + n2                          # 词汇量
        length = N1 + N2                              # 程序长度
        volume = length * (2 if length > 0 else 0)    # 程序体积 (简化)
        difficulty = (n1 / 2) * (N2 / n2)             # 难度
        effort = difficulty * volume                  # 实现工作量
        
        return {
            "vocabulary": vocabulary,
            "length": length,
            "volume": volume,
            "difficulty": difficulty,
            "effort": effort
        }
    
    def calculate_maintainability_index(self, complexity: Dict[str, Any], halstead: Dict[str, Any], lines: int) -> float:
        """
        计算可维护性指标
        
        Args:
            complexity: 复杂度指标
            halstead: Halstead度量
            lines: 代码行数
            
        Returns:
            float: 可维护性指标 (0-100)
        """
        # 可维护性指标计算公式
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # 其中 V 是Halstead体积，G是圈复杂度，LOC是代码行数
        
        cyclomatic = complexity.get("cyclomatic", 1)
        volume = halstead.get("volume", 0)
        
        # 防止取对数错误
        if volume <= 0:
            volume = 1
        if lines <= 0:
            lines = 1
            
        import math
        maintainability = 171 - 5.2 * math.log(volume) - 0.23 * cyclomatic - 16.2 * math.log(lines)
        
        # 标准化到0-100
        maintainability = max(0, min(100, maintainability))
        
        return maintainability 