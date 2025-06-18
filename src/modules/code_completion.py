import os
import re
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from src.services.model_manager import model_manager
from src.utils import config, logger

class CodeCompletion:
    """
    代码补全模块，提供智能代码补全和建议功能
    """
    
    def __init__(self, model_name: str = None):
        """
        初始化代码补全模块
        
        Args:
            model_name: 使用的模型名称，如果为None则使用配置中的默认值
        """
        self.model_name = model_name or config.get("models.inference.name", "codellama:7b-instruct-q4_K_M")
        self.temperature = config.get("code_completion.temperature", 0.2)
        self.context_window = config.get("code_completion.context_window", 4000)  # 上下文窗口大小
        self.max_new_tokens = config.get("code_completion.max_new_tokens", 256)  # 生成的最大token数
        
        # 缓存最近使用的文件内容，用于上下文感知补全
        self.context_cache = {}
        self.max_cache_items = 10
        
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "c", "cpp", 
            "csharp", "go", "rust", "php", "ruby", "kotlin", "swift"
        ]
        
        # 语言关键词映射
        self.language_keywords = {
            "python": ["def", "class", "if", "else", "elif", "for", "while", "import", "from", "try", "except"],
            "javascript": ["function", "const", "let", "var", "if", "else", "for", "while", "class", "import", "export"],
            "java": ["public", "private", "protected", "class", "interface", "enum", "if", "else", "for", "while"],
            "cpp": ["class", "struct", "enum", "void", "int", "bool", "for", "while", "if", "else", "switch"],
            "csharp": ["public", "private", "protected", "class", "interface", "enum", "void", "int", "bool", "using"],
            "go": ["func", "type", "struct", "interface", "package", "import", "if", "else", "for", "switch"],
            "rust": ["fn", "struct", "enum", "impl", "trait", "let", "mut", "if", "else", "match", "use"]
        }
        
        # 语言扩展名映射
        self.language_extensions = {
            "python": [".py"],
            "javascript": [".js", ".jsx"],
            "typescript": [".ts", ".tsx"],
            "java": [".java"],
            "c": [".c", ".h"],
            "cpp": [".cpp", ".hpp", ".cc", ".hh"],
            "csharp": [".cs"],
            "go": [".go"],
            "rust": [".rs"],
            "php": [".php"],
            "ruby": [".rb"],
            "kotlin": [".kt"],
            "swift": [".swift"]
        }
        
        logger.info(f"代码补全模块初始化完成，使用模型: {self.model_name}")
    
    def complete(self, code_context: str, language: str = None, 
                 max_tokens: int = None, cursor_position: int = None,
                 file_path: str = None) -> str:
        """
        根据上下文补全代码
        
        Args:
            code_context: 代码上下文
            language: 编程语言，如果为None则自动检测
            max_tokens: 最大生成token数，如果为None则使用默认值
            cursor_position: 光标位置，如果为None则使用文本末尾
            file_path: 文件路径，用于提供更好的上下文
            
        Returns:
            str: 补全的代码
        """
        if not code_context:
            return ""
        
        # 检测语言（如果未提供）
        if language is None:
            language = self.detect_language(code_context, file_path)
            logger.debug(f"自动检测到代码语言: {language}")
        
        if language not in self.supported_languages:
            logger.warning(f"不支持的语言: {language}，使用通用模式")
        
        # 处理光标位置
        if cursor_position is None:
            cursor_position = len(code_context)
        
        # 提取光标前后代码
        code_before = code_context[:cursor_position]
        code_after = code_context[cursor_position:]
        
        # 为保证上下文不超过限制，可能需要截断
        if len(code_before) > self.context_window:
            code_before = self._extract_relevant_context(code_before, self.context_window)
        
        # 获取项目上下文（如果有文件路径）
        project_context = ""
        if file_path and os.path.exists(file_path):
            project_context = self._get_project_context(file_path, language)
        
        # 准备提示词
        prompt = self._prepare_completion_prompt(code_before, code_after, language, project_context)
        
        # 调用模型生成补全
        try:
            max_tokens = max_tokens or self.max_new_tokens
            completion = model_manager.generate(
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=max_tokens
            )
            
            # 清理生成的结果，只保留实际代码部分
            completion = self._clean_completion(completion)
            
            logger.info(f"成功生成代码补全 ({len(completion)} 字符)")
            return completion
        except Exception as e:
            logger.error(f"代码补全生成失败: {str(e)}")
            return ""
    
    def complete_stream(self, code_context: str, language: str = None, 
                      max_tokens: int = None, cursor_position: int = None,
                      file_path: str = None):
        """
        流式生成代码补全
        
        Args:
            code_context: 代码上下文
            language: 编程语言，如果为None则自动检测
            max_tokens: 最大生成token数，如果为None则使用默认值
            cursor_position: 光标位置，如果为None则使用文本末尾
            file_path: 文件路径，用于提供更好的上下文
            
        Returns:
            Generator: 生成文本的流
        """
        if not code_context:
            return
            
        # 检测语言（如果未提供）
        if language is None:
            language = self.detect_language(code_context, file_path)
        
        # 处理光标位置
        if cursor_position is None:
            cursor_position = len(code_context)
        
        # 提取光标前后代码
        code_before = code_context[:cursor_position]
        code_after = code_context[cursor_position:]
        
        # 为保证上下文不超过限制，可能需要截断
        if len(code_before) > self.context_window:
            code_before = self._extract_relevant_context(code_before, self.context_window)
        
        # 获取项目上下文
        project_context = ""
        if file_path and os.path.exists(file_path):
            project_context = self._get_project_context(file_path, language)
        
        # 准备提示词
        prompt = self._prepare_completion_prompt(code_before, code_after, language, project_context)
        
        # 调用模型流式生成补全
        try:
            max_tokens = max_tokens or self.max_new_tokens
            buffer = ""
            
            for token in model_manager.generate_stream(
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=max_tokens
            ):
                buffer += token
                # 去除不必要的解释文本
                if "```" in buffer:
                    code_parts = buffer.split("```")
                    if len(code_parts) >= 3:  # 找到了代码块
                        code = code_parts[1]
                        if code.startswith(language):  # 去除语言标记
                            code = code[len(language):].lstrip()
                        yield code
                        buffer = ""  # 重置缓冲区
                        continue
                
                yield token
        except Exception as e:
            logger.error(f"流式代码补全生成失败: {str(e)}")
            yield f"错误: {str(e)}"
    
    def suggest_imports(self, code: str, language: str = None, file_path: str = None) -> List[str]:
        """
        根据代码内容建议需要导入的模块
        
        Args:
            code: 代码内容
            language: 编程语言，如果为None则自动检测
            file_path: 文件路径，用于提供更好的上下文
            
        Returns:
            List[str]: 导入建议列表
        """
        if language is None:
            language = self.detect_language(code, file_path)
        
        # 准备提示词
        prompt = f"""作为代码辅助工具，请分析下面的{language}代码，找出可能需要但尚未导入的模块/包/库，并以导入语句的形式列出。
只需返回导入语句，无需解释。如果没有需要导入的内容，请返回空列表 []。

```{language}
{code}
```"""
        
        try:
            # 调用模型生成建议
            response = model_manager.generate(
                prompt=prompt,
                temperature=0.1,  # 低温度，保持确定性
                max_tokens=256
            )
            
            # 解析响应
            import_statements = []
            
            # 提取代码块中的内容
            if "```" in response:
                code_blocks = response.split("```")
                if len(code_blocks) >= 3:
                    response = code_blocks[1]
                    if response.startswith(language):
                        response = response[len(language):].strip()
            
            # 提取导入语句
            lines = response.strip().split("\n")
            for line in lines:
                line = line.strip()
                if language == "python" and (line.startswith("import ") or line.startswith("from ")):
                    import_statements.append(line)
                elif language in ["javascript", "typescript"] and line.startswith("import "):
                    import_statements.append(line)
                elif language == "java" and line.startswith("import "):
                    import_statements.append(line)
                    
            return import_statements
        except Exception as e:
            logger.error(f"生成导入建议失败: {str(e)}")
            return []
    
    def suggest_function(self, function_name: str, params: List[str] = None,
                       language: str = "python", context: str = "") -> str:
        """
        根据函数名和参数建议函数实现
        
        Args:
            function_name: 函数名称
            params: 参数列表
            language: 编程语言
            context: 上下文代码
            
        Returns:
            str: 建议的函数实现
        """
        # 构建参数字符串
        params_str = ""
        if params:
            if language == "python":
                params_str = ", ".join(params)
            elif language in ["javascript", "typescript"]:
                params_str = ", ".join(params)
            elif language in ["java", "cpp", "csharp"]:
                # 为这些语言，参数通常包含类型
                params_str = ", ".join(params)
        
        # 准备提示词
        prompt = f"""作为代码辅助工具，请为以下函数名称和参数生成一个合理的{language}函数实现。
函数应该有详细的注释和文档字符串，功能实现应该考虑边界情况和异常处理。

函数名: {function_name}
参数列表: {params_str}
上下文代码:
```{language}
{context}
```

请仅返回函数实现，不要添加额外解释。"""

        try:
            # 调用模型生成函数
            response = model_manager.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=512
            )
            
            # 清理响应
            function_code = self._clean_completion(response)
            
            return function_code
        except Exception as e:
            logger.error(f"生成函数建议失败: {str(e)}")
            if language == "python":
                return f"def {function_name}({params_str}):\n    \"\"\"请在此添加函数文档\"\"\"\n    # 实现函数逻辑\n    pass"
            elif language in ["javascript", "typescript"]:
                return f"function {function_name}({params_str}) {{\n  // 实现函数逻辑\n}}"
            else:
                return ""
    
    def suggest_class(self, class_name: str, language: str = "python", context: str = "") -> str:
        """
        根据类名建议类实现
        
        Args:
            class_name: 类名称
            language: 编程语言
            context: 上下文代码
            
        Returns:
            str: 建议的类实现
        """
        # 准备提示词
        prompt = f"""作为代码辅助工具，请为以下类名生成一个合理的{language}类实现。
类应该有详细的注释和文档字符串，并包含适当的方法和属性。

类名: {class_name}
上下文代码:
```{language}
{context}
```

请仅返回类实现，不要添加额外解释。"""

        try:
            # 调用模型生成类
            response = model_manager.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=768
            )
            
            # 清理响应
            class_code = self._clean_completion(response)
            
            return class_code
        except Exception as e:
            logger.error(f"生成类建议失败: {str(e)}")
            if language == "python":
                return f"class {class_name}:\n    \"\"\"请在此添加类文档\"\"\"\n    \n    def __init__(self):\n        pass"
            elif language in ["javascript", "typescript"]:
                return f"class {class_name} {{\n  constructor() {{\n    // 初始化\n  }}\n}}"
            else:
                return ""
    
    def detect_language(self, code: str, file_path: str = None) -> str:
        """
        自动检测代码语言
        
        Args:
            code: 代码内容
            file_path: 文件路径
            
        Returns:
            str: 检测到的语言
        """
        # 首先根据文件扩展名判断
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            for lang, extensions in self.language_extensions.items():
                if ext in extensions:
                    return lang
        
        # 如果没有文件路径或无法通过扩展名判断，则根据关键词判断
        if not code:
            return "unknown"
            
        # 根据关键词判断
        max_matches = 0
        detected_lang = "unknown"
        
        for language, keywords in self.language_keywords.items():
            matched_keywords = 0
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, code):
                    matched_keywords += 1
            
            # 如果匹配了更多关键词，更新检测结果
            if matched_keywords > max_matches:
                max_matches = matched_keywords
                detected_lang = language
        
        # 只有在至少匹配了2个关键词的情况下才返回检测结果
        if max_matches >= 2:
            return detected_lang
        
        # 其他特征检测
        if "def " in code and ":" in code and "#" in code:
            return "python"
        elif "{" in code and "}" in code and "function" in code:
            return "javascript"
        elif "public class" in code or "private class" in code:
            return "java"
        
        return "unknown"
    
    def _prepare_completion_prompt(self, code_before: str, code_after: str, 
                                 language: str, project_context: str = "") -> str:
        """
        准备用于代码补全的提示词
        
        Args:
            code_before: 光标前代码
            code_after: 光标后代码
            language: 编程语言
            project_context: 项目上下文信息
            
        Returns:
            str: 格式化的提示词
        """
        # 根据语言定制系统提示词
        system_prompt = f"你是一个专业的{language}代码补全助手。提供准确、简洁、符合最佳实践的代码补全。代码应当可以直接运行，不需要额外修改。"
        
        # 构建提示词
        prompt = f"""系统: {system_prompt}

任务: 请在 [补全此处] 位置生成符合上下文的{language}代码补全。只需提供补全的代码，无需解释。

{f'项目上下文信息:\n{project_context}\n\n' if project_context else ''}代码:
```{language}
{code_before}[补全此处]{code_after}
```"""

        return prompt
    
    def _clean_completion(self, completion: str) -> str:
        """
        清理模型生成的补全结果，只保留代码部分
        
        Args:
            completion: 原始补全结果
            
        Returns:
            str: 清理后的代码
        """
        # 如果结果包含代码块标记，提取代码块内容
        if "```" in completion:
            parts = completion.split("```")
            if len(parts) >= 3:
                code_block = parts[1]
                # 如果代码块以语言标识符开头，移除它
                lines = code_block.splitlines()
                if lines and lines[0].strip() in self.supported_languages:
                    code_block = "\n".join(lines[1:])
                return code_block.strip()
        
        # 移除常见的非代码前缀
        prefixes = [
            "以下是补全的代码：", "补全的代码：", "这是补全的代码：",
            "代码补全：", "补全代码：", "代码如下：", "补全如下："
        ]
        for prefix in prefixes:
            if completion.startswith(prefix):
                completion = completion[len(prefix):].strip()
                break
        
        return completion.strip()
    
    def _extract_relevant_context(self, code: str, max_length: int) -> str:
        """
        从长代码中提取最相关的上下文
        
        Args:
            code: 完整代码
            max_length: 最大长度限制
            
        Returns:
            str: 提取的相关上下文
        """
        # 如果代码长度已经在限制内，直接返回
        if len(code) <= max_length:
            return code
        
        # 提取末尾部分（最相关的上下文）
        tail_length = int(max_length * 0.7)
        tail = code[-tail_length:]
        
        # 提取开头部分（包含导入和定义）
        head_length = max_length - tail_length
        head = code[:head_length]
        
        # 确保在合适的位置切分
        # 对于头部，尝试在完整语句或函数结束处切分
        if head:
            # 查找最后一个完整块的结束位置
            last_import = max(head.rfind("\nimport "), head.rfind("\nfrom "))
            last_def = max(head.rfind("\ndef "), head.rfind("\nclass "))
            last_statement = max(last_import, last_def)
            
            if last_statement > 0:
                # 找到这个语句块的结束位置
                end_pos = head.find("\n\n", last_statement)
                if end_pos > 0:
                    head = head[:end_pos]
        
        # 对于尾部，尝试在语句开始处切分
        if tail:
            # 查找第一个完整块的开始位置
            first_line = tail.find("\n")
            if first_line > 0:
                # 查找下一个缩进较少的行
                current_indent = len(tail) - len(tail.lstrip())
                for i, line in enumerate(tail.splitlines()):
                    if i > 0:
                        line_indent = len(line) - len(line.lstrip())
                        if line_indent <= current_indent and line.strip():
                            # 找到了一个新的代码块
                            tail = "\n".join(tail.splitlines()[i:])
                            break
        
        # 组合上下文
        return f"{head}\n\n# ... 省略部分代码 ...\n\n{tail}"
    
    def _get_project_context(self, file_path: str, language: str) -> str:
        """
        获取项目上下文信息，用于提供更好的补全
        
        Args:
            file_path: 文件路径
            language: 编程语言
            
        Returns:
            str: 项目上下文信息
        """
        try:
            # 获取当前文件所在目录
            file_dir = os.path.dirname(file_path)
            
            # 如果最近使用过此文件，从缓存获取信息
            if file_path in self.context_cache:
                return self.context_cache[file_path]
            
            # 提取项目信息的摘要
            context_info = []
            
            # 1. 分析当前文件的导入
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # 提取导入语句
                imports = []
                if language == "python":
                    import_pattern = r'^(?:from\s+[\w.]+\s+import\s+[\w.*,\s]+|import\s+[\w.,\s]+)'
                    imports = re.findall(import_pattern, content, re.MULTILINE)
                elif language in ["javascript", "typescript"]:
                    import_pattern = r'^(?:import\s+[\w{},\s*]+\s+from\s+[\'"][\w./]+[\'"]|const\s+\w+\s+=\s+require\([\'"][\w./]+[\'"])'
                    imports = re.findall(import_pattern, content, re.MULTILINE)
                
                if imports:
                    context_info.append("当前文件导入:")
                    for imp in imports[:10]:  # 限制数量
                        context_info.append(f"  {imp}")
            
            # 2. 查找同目录下的相关文件
            if os.path.isdir(file_dir):
                related_files = []
                for ext in self.language_extensions.get(language, []):
                    related_files.extend(Path(file_dir).glob(f"*{ext}"))
                
                if related_files:
                    context_info.append("\n相关文件:")
                    for rf in related_files[:5]:  # 限制数量
                        context_info.append(f"  {rf.name}")
            
            # 3. 检查项目配置文件
            config_files = {
                "python": ["requirements.txt", "setup.py", "pyproject.toml"],
                "javascript": ["package.json", "tsconfig.json"],
                "java": ["pom.xml", "build.gradle"],
                "rust": ["Cargo.toml"]
            }
            
            for cf in config_files.get(language, []):
                config_path = os.path.join(file_dir, cf)
                if os.path.exists(config_path):
                    context_info.append(f"\n找到项目配置文件: {cf}")
                    # 提取关键依赖信息
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            config_content = f.read()
                            
                        if cf == "package.json":
                            import json
                            data = json.loads(config_content)
                            if "dependencies" in data:
                                context_info.append("  主要依赖:")
                                for dep, ver in list(data["dependencies"].items())[:5]:
                                    context_info.append(f"    {dep}: {ver}")
                        elif cf == "requirements.txt":
                            lines = config_content.splitlines()
                            context_info.append("  主要依赖:")
                            for line in lines[:5]:
                                if line.strip() and not line.startswith("#"):
                                    context_info.append(f"    {line.strip()}")
                    except Exception as e:
                        logger.warning(f"解析配置文件失败: {str(e)}")
            
            # 缓存结果
            context_str = "\n".join(context_info)
            self.context_cache[file_path] = context_str
            
            # 限制缓存大小
            if len(self.context_cache) > self.max_cache_items:
                # 移除最旧的项
                self.context_cache.pop(next(iter(self.context_cache)))
                
            return context_str
        except Exception as e:
            logger.warning(f"获取项目上下文失败: {str(e)}")
            return "" 