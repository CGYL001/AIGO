import re
from typing import List, Dict, Any, Optional, Tuple

class ErrorChecker:
    """
    代码错误检查模块，提供实时代码错误检测和修复建议
    """
    
    def __init__(self):
        """初始化错误检查模块"""
        # 常见错误模式定义
        self.error_patterns = {
            "python": [
                (r"NameError:\s*name '(\w+)' is not defined", "变量未定义错误", "确保在使用前定义变量 '{0}'"),
                (r"IndentationError:\s*(.*)", "缩进错误", "检查代码缩进，确保使用一致的缩进方式（空格或制表符）"),
                (r"SyntaxError:\s*(.*)", "语法错误", "检查语法错误: {0}"),
                (r"TypeError:\s*(.*)", "类型错误", "类型不匹配: {0}"),
                (r"ImportError:\s*No module named '(\w+)'", "导入错误", "缺少模块 '{0}'，请先安装"),
                (r"AttributeError:\s*'(\w+)' object has no attribute '(\w+)'", "属性错误", "'{0}' 对象没有 '{1}' 属性"),
                (r"IndexError:\s*(.*)", "索引错误", "索引超出范围: {0}"),
                (r"KeyError:\s*(.*)", "键错误", "字典中不存在此键: {0}"),
                (r"ZeroDivisionError", "除零错误", "不能除以零"),
                (r"FileNotFoundError:\s*(.*)", "文件未找到", "找不到文件: {0}")
            ],
            "javascript": [
                (r"ReferenceError:\s*(\w+) is not defined", "引用错误", "变量 '{0}' 未定义"),
                (r"SyntaxError:\s*(.*)", "语法错误", "JavaScript语法错误: {0}"),
                (r"TypeError:\s*(.*)", "类型错误", "类型错误: {0}"),
                (r"Uncaught RangeError:\s*(.*)", "范围错误", "范围错误: {0}")
            ],
            "java": [
                (r"cannot find symbol\s*symbol:\s*(\w+)", "符号未找到", "找不到符号 '{0}'"),
                (r"incompatible types", "类型不兼容", "类型转换错误，请检查变量类型")
            ],
            "cpp": [
                (r"'(\w+)' was not declared in this scope", "变量未声明", "变量 '{0}' 在此作用域中未声明")
            ]
            # 可添加更多语言的错误模式
        }
        
        # 静态分析规则
        self.static_rules = {
            "python": [
                (r"import\s+(\w+)", "检查导入模块可用性"),
                (r"except\s*:", "避免使用空的except子句"),
                (r"except\s+Exception", "避免捕获所有异常"),
                (r"print\s*\(", "生产代码中谨慎使用print语句")
            ],
            "javascript": [
                (r"==(?!=)", "考虑使用=== 而不是 =="),
                (r"console\.log", "生产代码中避免使用console.log")
            ],
            # 可添加更多语言的规则
        }
        
        self.linters = {
            "python": ["flake8", "pylint"],
            "javascript": ["eslint", "jshint"],
            # 可添加更多语言对应的linter
        }
        
        print("代码错误检查模块初始化完成")

    def check(self, code: str, language: str = "python") -> List[Dict[str, Any]]:
        """
        检查代码中的错误
        
        Args:
            code: 要检查的代码
            language: 编程语言
            
        Returns:
            List[Dict]: 错误列表，每个错误包含类型、位置、消息和修复建议
        """
        if not code or not code.strip():
            return []
            
        # 获取语言对应的错误模式
        patterns = self.error_patterns.get(language.lower(), [])
        if not patterns:
            print(f"警告: 不支持对 {language} 的错误检查，使用通用模式")
        
        # 同时进行错误检查和静态分析
        syntax_errors = self._check_syntax_errors(code, language)
        static_issues = self._check_static_rules(code, language)
        
        # 合并结果
        all_issues = syntax_errors + static_issues
        
        # 按行号排序
        all_issues.sort(key=lambda x: x.get("line", 0))
        
        return all_issues
        
    def _check_syntax_errors(self, code: str, language: str) -> List[Dict[str, Any]]:
        """检查语法错误"""
        errors = []
        
        # 模拟执行代码检查语法错误
        # 实际实现会使用语言特定的解析器或编译器
        # 这里使用示例错误
        if language == "python":
            # 示例：未闭合的括号
            if code.count("(") != code.count(")"):
                errors.append({
                    "type": "syntax",
                    "severity": "error",
                    "message": "括号不匹配，缺少闭合括号",
                    "line": self._find_line_with_error(code, "("),
                    "fix": "检查并添加缺少的闭合括号"
                })
                
            # 示例：缩进错误
            lines = code.split("\n")
            for i, line in enumerate(lines):
                if line.strip() and line.startswith(" ") and not lines[i-1].strip().endswith(":"):
                    if i > 0 and not lines[i-1].strip().endswith("\\"):
                        errors.append({
                            "type": "syntax",
                            "severity": "error",
                            "message": "可能的缩进错误",
                            "line": i + 1,
                            "fix": "检查此行的缩进"
                        })
                        
        elif language == "javascript":
            # 示例：缺少分号
            lines = code.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.endswith(";") and not line.endswith("{") and not line.endswith("}"):
                    if not line.startswith("//") and not line.startswith("/*"):
                        errors.append({
                            "type": "style",
                            "severity": "warning",
                            "message": "缺少分号",
                            "line": i + 1,
                            "fix": f"在行尾添加分号: {line};"
                        })
        
        return errors
        
    def _check_static_rules(self, code: str, language: str) -> List[Dict[str, Any]]:
        """检查静态规则"""
        issues = []
        
        # 获取语言对应的静态规则
        rules = self.static_rules.get(language.lower(), [])
        
        # 应用所有规则
        for pattern, message in rules:
            regex = re.compile(pattern)
            for match in regex.finditer(code):
                line = self._get_line_number(code, match.start())
                issues.append({
                    "type": "style",
                    "severity": "info",
                    "message": message,
                    "line": line,
                    "fix": f"考虑修改此处代码样式"
                })
                
        return issues
        
    def suggest_fix(self, error: Dict[str, Any], code: str) -> str:
        """
        为特定错误提供修复建议
        
        Args:
            error: 错误信息
            code: 原始代码
            
        Returns:
            str: 修复建议
        """
        if not error or "type" not in error:
            return "无法提供修复建议，错误信息不完整"
            
        error_type = error.get("type")
        message = error.get("message", "")
        
        # 根据错误类型和消息提供具体修复建议
        if "未定义" in message or "not defined" in message:
            var_name = re.search(r"'(\w+)'", message)
            if var_name:
                return f"变量 '{var_name.group(1)}' 未定义。请确保在使用前定义此变量。"
                
        elif "缩进" in message or "indentation" in message:
            return "检查代码缩进，确保使用一致的缩进方式（空格或制表符）。"
            
        elif "语法错误" in message or "syntax" in message:
            return "检查此处的语法错误，可能是缺少括号、逗号或其他语法元素。"
            
        # 如果有具体的修复建议，直接返回
        if "fix" in error:
            return error["fix"]
            
        return "无法提供具体修复建议，请仔细检查代码"
        
    def auto_fix(self, error: Dict[str, Any], code: str) -> Tuple[bool, str]:
        """
        尝试自动修复错误
        
        Args:
            error: 错误信息
            code: 原始代码
            
        Returns:
            Tuple[bool, str]: (是否成功修复, 修复后的代码)
        """
        # 实际实现会根据错误类型进行智能修复
        # 这里仅作示例
        print(f"尝试修复错误: {error.get('message', '')}")
        return False, code  # 默认不做修复
        
    def _find_line_with_error(self, code: str, pattern: str) -> int:
        """查找包含错误模式的行号"""
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if pattern in line:
                return i + 1
        return 1
        
    def _get_line_number(self, code: str, position: int) -> int:
        """根据字符位置获取行号"""
        line = code[:position].count("\n") + 1
        return line 