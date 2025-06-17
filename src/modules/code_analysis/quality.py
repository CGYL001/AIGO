"""
代码质量分析器 - 负责分析代码质量、风格规范和潜在问题
"""

import re
from typing import Dict, Any, List

class QualityAnalyzer:
    """代码质量分析器，负责分析代码质量、风格规范和潜在问题"""
    
    def __init__(self):
        """初始化质量分析器"""
        # 代码风格规则
        self.style_rules = {
            "python": [
                {"name": "line_length", "max": 80, "description": "行长度超过限制"},
                {"name": "snake_case", "pattern": r"^[a-z][a-z0-9_]*$", "description": "变量名应使用蛇形命名法"},
                {"name": "docstring", "pattern": r'""".*?"""', "description": "缺少文档字符串"}
            ],
            "javascript": [
                {"name": "line_length", "max": 80, "description": "行长度超过限制"},
                {"name": "camelCase", "pattern": r"^[a-z][a-zA-Z0-9]*$", "description": "变量名应使用驼峰命名法"},
                {"name": "semicolon", "pattern": r";$", "description": "缺少分号"}
            ]
        }
        
        # 常见代码问题
        self.common_issues = {
            "python": [
                {"pattern": r"print\(", "description": "生产代码中不应有直接打印语句"},
                {"pattern": r"except\s*:", "description": "过于宽泛的异常捕获"},
                {"pattern": r"import\s+\*", "description": "应避免使用通配符导入"},
                {"pattern": r"global\s+", "description": "应避免使用全局变量"}
            ],
            "javascript": [
                {"pattern": r"console\.log\(", "description": "生产代码中不应有控制台日志"},
                {"pattern": r"==(?!=)", "description": "应使用严格等于(===)"},
                {"pattern": r"var\s+", "description": "应使用let或const代替var"},
                {"pattern": r"try\s*{.*}\s*catch\s*\(\s*\)\s*{", "description": "过于宽泛的异常捕获"}
            ]
        }
    
    def analyze(self, content: str, language: str) -> Dict[str, Any]:
        """
        分析代码质量
        
        Args:
            content: 代码内容
            language: 编程语言
            
        Returns:
            Dict[str, Any]: 代码质量分析结果
        """
        if not content:
            return {"issues": [], "style": {"score": 0}, "problems": []}
            
        # 检查样式问题
        style_issues = self._check_style(content, language)
        
        # 检查潜在问题
        potential_problems = self._check_issues(content, language)
        
        # 检查代码重复
        duplicates = self._check_duplicates(content)
        
        # 计算质量分数
        quality_score = self._calculate_quality_score(content, style_issues, potential_problems, duplicates)
        
        return {
            "issues": style_issues + potential_problems,
            "style": {
                "score": quality_score,
                "issues": len(style_issues),
                "suggestions": self._get_suggestions(style_issues)
            },
            "problems": {
                "count": len(potential_problems),
                "duplicates": len(duplicates),
                "suggestions": self._get_suggestions(potential_problems)
            }
        }
    
    def _check_style(self, content: str, language: str) -> List[Dict[str, Any]]:
        """
        检查代码风格问题
        
        Args:
            content: 代码内容
            language: 编程语言
            
        Returns:
            List[Dict[str, Any]]: 风格问题列表
        """
        issues = []
        
        # 获取当前语言的风格规则
        rules = self.style_rules.get(language, [])
        if not rules:
            return issues
            
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_number = i + 1
            
            # 检查行长度
            for rule in rules:
                if rule["name"] == "line_length" and len(line) > rule["max"]:
                    issues.append({
                        "line": line_number,
                        "message": f"行长度 ({len(line)}) 超过 {rule['max']} 字符的限制",
                        "type": "style",
                        "severity": "warning"
                    })
        
        # 检查命名规范（变量、函数）
        if language == "python":
            # 简单的变量和函数定义匹配
            var_pattern = r"([a-zA-Z0-9_]+)\s*="
            func_pattern = r"def\s+([a-zA-Z0-9_]+)\s*\("
            
            for pattern in [var_pattern, func_pattern]:
                for match in re.finditer(pattern, content):
                    name = match.group(1)
                    if name.startswith('__') or name.startswith('_'):
                        continue  # 跳过特殊和私有名称
                        
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # 检查蛇形命名法
                    snake_rule = next((r for r in rules if r["name"] == "snake_case"), None)
                    if snake_rule and not re.match(snake_rule["pattern"], name):
                        issues.append({
                            "line": line_number,
                            "message": f"'{name}' 不符合蛇形命名法规范",
                            "type": "style",
                            "severity": "warning"
                        })
        
        elif language in ["javascript", "typescript"]:
            # 检查变量命名
            var_pattern = r"(?:var|let|const)\s+([a-zA-Z0-9_$]+)\s*="
            func_pattern = r"function\s+([a-zA-Z0-9_$]+)\s*\("
            
            for pattern in [var_pattern, func_pattern]:
                for match in re.finditer(pattern, content):
                    name = match.group(1)
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # 检查驼峰命名法
                    camel_rule = next((r for r in rules if r["name"] == "camelCase"), None)
                    if camel_rule and not re.match(camel_rule["pattern"], name):
                        issues.append({
                            "line": line_number,
                            "message": f"'{name}' 不符合驼峰命名法规范",
                            "type": "style",
                            "severity": "warning"
                        })
        
        # 检查文档字符串
        if language == "python":
            # 简单检查函数和类是否有文档字符串
            func_pattern = r"def\s+[a-zA-Z0-9_]+\s*\([^)]*\):\s*(?:\n\s*(?!\"\"\")|$)"
            for match in re.finditer(func_pattern, content):
                line_number = content[:match.end()].count('\n') + 1
                issues.append({
                    "line": line_number,
                    "message": "函数缺少文档字符串",
                    "type": "style",
                    "severity": "info"
                })
        
        return issues
    
    def _check_issues(self, content: str, language: str) -> List[Dict[str, Any]]:
        """
        检查代码中的潜在问题
        
        Args:
            content: 代码内容
            language: 编程语言
            
        Returns:
            List[Dict[str, Any]]: 潜在问题列表
        """
        issues = []
        
        # 获取当前语言的常见问题规则
        rules = self.common_issues.get(language, [])
        if not rules:
            return issues
            
        # 检查每条规则
        for rule in rules:
            for match in re.finditer(rule["pattern"], content):
                line_number = content[:match.start()].count('\n') + 1
                issues.append({
                    "line": line_number,
                    "message": rule["description"],
                    "type": "issue",
                    "severity": "warning"
                })
        
        # 检查其他常见问题
        if language == "python":
            # 检查大量连续注释但无代码的区域
            comment_blocks = re.finditer(r"((?:(?:\s*#[^\n]*\n)+))", content)
            for match in comment_blocks:
                block = match.group(1)
                lines = block.count('\n')
                if lines > 5:  # 超过5行连续注释
                    line_number = content[:match.start()].count('\n') + 1
                    issues.append({
                        "line": line_number,
                        "message": f"大段注释代码 ({lines} 行)，考虑重构或清理",
                        "type": "issue",
                        "severity": "info"
                    })
        
        elif language in ["javascript", "typescript"]:
            # 检查网络请求后没有错误处理
            fetch_pattern = r"fetch\([^)]+\)\.then\([^)]+\)(?!\s*\.catch)"
            for match in re.finditer(fetch_pattern, content):
                line_number = content[:match.start()].count('\n') + 1
                issues.append({
                    "line": line_number,
                    "message": "网络请求缺少错误处理 (.catch)",
                    "type": "issue",
                    "severity": "warning"
                })
        
        return issues
    
    def _check_duplicates(self, content: str) -> List[Dict[str, Any]]:
        """
        检查代码重复
        
        Args:
            content: 代码内容
            
        Returns:
            List[Dict[str, Any]]: 重复代码列表
        """
        duplicates = []
        lines = content.split('\n')
        
        # 简单的代码重复检测（查找连续5行以上的重复）
        min_duplicate_lines = 5
        line_hash = {}
        
        for i in range(len(lines) - min_duplicate_lines + 1):
            # 计算片段哈希
            chunk = '\n'.join(lines[i:i+min_duplicate_lines])
            if len(chunk.strip()) < 20:  # 忽略太短的片段
                continue
                
            if chunk in line_hash:
                # 已经发现重复
                duplicates.append({
                    "first_occurrence": line_hash[chunk] + 1,  # 1-based line number
                    "second_occurrence": i + 1,  # 1-based line number
                    "lines": min_duplicate_lines,
                    "message": f"重复代码块 ({min_duplicate_lines} 行)"
                })
            else:
                line_hash[chunk] = i
        
        return duplicates
    
    def _calculate_quality_score(self, content: str, style_issues: List[Dict[str, Any]], 
                                potential_problems: List[Dict[str, Any]], duplicates: List[Dict[str, Any]]) -> float:
        """
        计算代码质量分数
        
        Args:
            content: 代码内容
            style_issues: 样式问题列表
            potential_problems: 潜在问题列表
            duplicates: 重复代码列表
            
        Returns:
            float: 质量分数 (0-100)
        """
        # 基础分为100
        score = 100.0
        
        # 计算行数
        lines = content.count('\n') + 1
        
        # 每个样式问题扣除一定分数，但根据代码行数调整
        if lines > 0:
            # 样式问题权重
            style_weight = min(1.0, 50.0 / lines)  # 代码越长，单个样式问题的权重越小
            score -= len(style_issues) * style_weight
            
            # 潜在问题权重（比样式问题高）
            problem_weight = min(2.0, 100.0 / lines)
            score -= len(potential_problems) * problem_weight
            
            # 代码重复权重（最高）
            duplicate_weight = min(5.0, 200.0 / lines)
            score -= len(duplicates) * duplicate_weight
        
        # 确保分数在0-100范围内
        return max(0, min(100, score))
    
    def _get_suggestions(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        根据问题生成改进建议
        
        Args:
            issues: 问题列表
            
        Returns:
            List[str]: 建议列表
        """
        if not issues:
            return []
            
        # 根据问题类型分组
        by_type = {}
        for issue in issues:
            msg = issue["message"]
            if msg in by_type:
                by_type[msg].append(issue["line"])
            else:
                by_type[msg] = [issue["line"]]
        
        # 生成建议
        suggestions = []
        for msg, lines in by_type.items():
            if len(lines) > 3:
                # 如果问题出现多次，统一建议
                suggestions.append(f"{msg} (出现 {len(lines)} 次，例如在第 {', '.join(map(str, lines[:3]))} 行)")
            else:
                # 如果问题较少，单独列出
                suggestions.append(f"{msg} (在第 {', '.join(map(str, lines))} 行)")
        
        return suggestions 