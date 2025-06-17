"""
代码结构分析器 - 负责分析代码的结构信息（类、函数等）
"""

import re
from typing import Dict, Any, List

class StructureAnalyzer:
    """代码结构分析器，负责分析代码的结构信息（类、函数等）"""
    
    def __init__(self):
        """初始化结构分析器"""
        pass
    
    def analyze(self, content: str, language: str) -> Dict[str, Any]:
        """
        分析代码结构
        
        Args:
            content: 代码内容
            language: 编程语言
            
        Returns:
            Dict[str, Any]: 代码结构信息
        """
        if language == "python":
            return self._analyze_python(content)
        elif language in ["javascript", "typescript"]:
            return self._analyze_javascript(content)
        elif language == "java":
            return self._analyze_java(content)
        elif language in ["cpp", "csharp"]:
            return self._analyze_c_style(content)
        else:
            # 默认分析方式
            return {
                "functions": [],
                "classes": [],
                "imports": []
            }
    
    def _analyze_python(self, content: str) -> Dict[str, Any]:
        """分析Python代码结构"""
        functions = []
        classes = []
        imports = []
        
        # 分析导入语句
        import_pattern = r'^import\s+([a-zA-Z0-9_.,\s]+)|^from\s+([a-zA-Z0-9_.]+)\s+import\s+([a-zA-Z0-9_.,\s\*]+)'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            if match.group(1):  # import x
                imports.append({"type": "import", "module": match.group(1).strip()})
            elif match.group(2) and match.group(3):  # from x import y
                imports.append({"type": "from", "module": match.group(2).strip(), "names": match.group(3).strip()})
        
        # 分析类定义
        class_pattern = r'class\s+([a-zA-Z0-9_]+)\s*(?:\([^)]*\))?:'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            class_start = match.start()
            
            # 获取类的起始行
            line_number = content[:class_start].count('\n') + 1
            
            # 简单计算代码块结束的位置（通过缩进）
            lines = content[class_start:].split('\n')
            
            # 第一行是类定义，跳过
            lines = lines[1:]
            
            # 获取类定义的缩进级别
            if lines and lines[0]:
                class_indent = len(lines[0]) - len(lines[0].lstrip())
            else:
                class_indent = 0
            
            # 找到类的结束位置
            class_end_line = 0
            for i, line in enumerate(lines, 1):
                if line.strip() and len(line) - len(line.lstrip()) <= class_indent:
                    class_end_line = line_number + i - 1
                    break
            
            if class_end_line == 0:  # 如果没找到结束位置，假设到文件末尾
                class_end_line = content.count('\n') + 1
            
            # 计算类长度
            class_length = class_end_line - line_number
            
            classes.append({
                "name": class_name,
                "line": line_number,
                "end_line": class_end_line,
                "lines": class_length
            })
        
        # 分析函数定义
        function_pattern = r'def\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*:'
        for match in re.finditer(function_pattern, content):
            function_name = match.group(1)
            function_start = match.start()
            
            # 获取函数的起始行
            line_number = content[:function_start].count('\n') + 1
            
            # 简单计算代码块结束的位置（通过缩进）
            lines = content[function_start:].split('\n')
            
            # 第一行是函数定义，跳过
            lines = lines[1:]
            
            # 获取函数定义的缩进级别
            if lines and lines[0]:
                function_indent = len(lines[0]) - len(lines[0].lstrip())
            else:
                function_indent = 0
            
            # 找到函数的结束位置
            function_end_line = 0
            for i, line in enumerate(lines, 1):
                if line.strip() and len(line) - len(line.lstrip()) <= function_indent:
                    function_end_line = line_number + i - 1
                    break
            
            if function_end_line == 0:  # 如果没找到结束位置，假设到文件末尾
                function_end_line = content.count('\n') + 1
            
            # 计算函数长度
            function_length = function_end_line - line_number
            
            # 判断是否是类方法
            is_method = False
            for cls in classes:
                if line_number > cls["line"] and function_end_line <= cls["end_line"]:
                    is_method = True
                    break
            
            functions.append({
                "name": function_name,
                "line": line_number,
                "end_line": function_end_line,
                "lines": function_length,
                "is_method": is_method
            })
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports
        }
    
    def _analyze_javascript(self, content: str) -> Dict[str, Any]:
        """分析JavaScript/TypeScript代码结构"""
        functions = []
        classes = []
        imports = []
        
        # 分析导入语句
        import_pattern = r'import\s+(?:{[^}]*}|[a-zA-Z0-9_*]+)\s+from\s+[\'"]([^\'"]*)[\'"](;)?|require\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)'
        for match in re.finditer(import_pattern, content):
            module = match.group(1) or match.group(3)
            if module:
                imports.append({"module": module.strip()})
        
        # 分析类定义
        class_pattern = r'class\s+([a-zA-Z0-9_]+)\s*(?:extends\s+[a-zA-Z0-9_.]+\s*)?{'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            class_start = match.start()
            
            # 获取类的起始行
            line_number = content[:class_start].count('\n') + 1
            
            # 找到对应的右花括号
            brace_count = 1
            class_end = class_start + match.end(0) - match.start(0)
            for i in range(class_end, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break
            
            # 计算类的结束行
            class_end_line = content[:class_end].count('\n') + 1
            
            # 计算类长度
            class_length = class_end_line - line_number
            
            classes.append({
                "name": class_name,
                "line": line_number,
                "end_line": class_end_line,
                "lines": class_length
            })
        
        # 分析函数定义
        # 考虑多种函数定义方式：
        # - 普通函数：function name() {}
        # - 箭头函数：const name = () => {}
        # - 方法：name() {}
        function_patterns = [
            r'function\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*{',  # 普通函数
            r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>\s*{',  # 箭头函数
            r'(?:async\s+)?([a-zA-Z0-9_]+)\s*\([^)]*\)\s*{'  # 方法或函数表达式
        ]
        
        for pattern in function_patterns:
            for match in re.finditer(pattern, content):
                function_name = match.group(1)
                function_start = match.start()
                
                # 获取函数的起始行
                line_number = content[:function_start].count('\n') + 1
                
                # 找到对应的右花括号
                brace_count = 1
                function_end = function_start + match.end(0) - match.start(0)
                for i in range(function_end, len(content)):
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            function_end = i
                            break
                
                # 计算函数的结束行
                function_end_line = content[:function_end].count('\n') + 1
                
                # 计算函数长度
                function_length = function_end_line - line_number
                
                # 判断是否是类方法
                is_method = False
                for cls in classes:
                    if line_number > cls["line"] and function_end_line <= cls["end_line"]:
                        is_method = True
                        break
                
                functions.append({
                    "name": function_name,
                    "line": line_number,
                    "end_line": function_end_line,
                    "lines": function_length,
                    "is_method": is_method
                })
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports
        }
    
    def _analyze_java(self, content: str) -> Dict[str, Any]:
        """分析Java代码结构"""
        # 简化的Java代码分析，实际需要更复杂的解析
        functions = []
        classes = []
        imports = []
        
        # 分析导入语句
        import_pattern = r'import\s+([a-zA-Z0-9_.]+(?:\.[*])?);'
        for match in re.finditer(import_pattern, content):
            imports.append({"module": match.group(1).strip()})
        
        # 分析类定义
        class_pattern = r'(?:public|private|protected)?\s*(?:abstract|final)?\s*(?:class|interface|enum)\s+([a-zA-Z0-9_]+)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            class_start = match.start()
            
            # 获取类的起始行
            line_number = content[:class_start].count('\n') + 1
            
            # 简单找到类体的开始
            class_body_start = content.find('{', class_start)
            if class_body_start == -1:
                continue
            
            # 找到类体的结束
            brace_count = 1
            class_end = class_body_start + 1
            for i in range(class_end, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break
            
            # 计算类的结束行
            class_end_line = content[:class_end].count('\n') + 1
            
            # 计算类长度
            class_length = class_end_line - line_number
            
            classes.append({
                "name": class_name,
                "line": line_number,
                "end_line": class_end_line,
                "lines": class_length
            })
        
        # 分析方法定义
        method_pattern = r'(?:public|private|protected)?\s*(?:static|final|abstract)?\s*(?:[a-zA-Z0-9_<>[\],\s]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*(?:throws\s+[a-zA-Z0-9_,\s]+)?\s*{'
        for match in re.finditer(method_pattern, content):
            method_name = match.group(1)
            method_start = match.start()
            
            # 获取方法的起始行
            line_number = content[:method_start].count('\n') + 1
            
            # 找到方法体的开始
            method_body_start = content.find('{', method_start)
            if method_body_start == -1:
                continue
            
            # 找到方法体的结束
            brace_count = 1
            method_end = method_body_start + 1
            for i in range(method_end, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        method_end = i
                        break
            
            # 计算方法的结束行
            method_end_line = content[:method_end].count('\n') + 1
            
            # 计算方法长度
            method_length = method_end_line - line_number
            
            # 判断是否是类方法
            is_method = False
            for cls in classes:
                if line_number > cls["line"] and method_end_line <= cls["end_line"]:
                    is_method = True
                    break
            
            functions.append({
                "name": method_name,
                "line": line_number,
                "end_line": method_end_line,
                "lines": method_length,
                "is_method": is_method
            })
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports
        }
    
    def _analyze_c_style(self, content: str) -> Dict[str, Any]:
        """分析C风格语言（C++, C#）代码结构"""
        functions = []
        classes = []
        includes = []
        
        # 分析包含语句
        include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
        for match in re.finditer(include_pattern, content):
            includes.append({"module": match.group(1).strip()})
        
        # 分析类定义
        class_pattern = r'(?:public|private|protected|internal)?\s*(?:abstract|sealed|static)?\s*class\s+([a-zA-Z0-9_]+)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            class_start = match.start()
            
            # 获取类的起始行
            line_number = content[:class_start].count('\n') + 1
            
            # 简单找到类体的开始
            class_body_start = content.find('{', class_start)
            if class_body_start == -1:
                continue
            
            # 找到类体的结束
            brace_count = 1
            class_end = class_body_start + 1
            for i in range(class_end, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break
            
            # 计算类的结束行
            class_end_line = content[:class_end].count('\n') + 1
            
            # 计算类长度
            class_length = class_end_line - line_number
            
            classes.append({
                "name": class_name,
                "line": line_number,
                "end_line": class_end_line,
                "lines": class_length
            })
        
        # 分析函数定义
        function_pattern = r'(?:public|private|protected|internal)?\s*(?:static|virtual|override)?\s*(?:[a-zA-Z0-9_<>[\]*,\s]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*(?:const)?\s*{'
        for match in re.finditer(function_pattern, content):
            function_name = match.group(1)
            function_start = match.start()
            
            # 获取函数的起始行
            line_number = content[:function_start].count('\n') + 1
            
            # 简单找到函数体的开始
            function_body_start = content.find('{', function_start)
            if function_body_start == -1:
                continue
            
            # 找到函数体的结束
            brace_count = 1
            function_end = function_body_start + 1
            for i in range(function_end, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        function_end = i
                        break
            
            # 计算函数的结束行
            function_end_line = content[:function_end].count('\n') + 1
            
            # 计算函数长度
            function_length = function_end_line - line_number
            
            # 判断是否是类方法
            is_method = False
            for cls in classes:
                if line_number > cls["line"] and function_end_line <= cls["end_line"]:
                    is_method = True
                    break
            
            functions.append({
                "name": function_name,
                "line": line_number,
                "end_line": function_end_line,
                "lines": function_length,
                "is_method": is_method
            })
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": includes
        } 