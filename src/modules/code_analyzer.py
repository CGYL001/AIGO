import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

class CodeAnalyzer:
    """
    代码分析模块，提供代码结构分析、质量评估和优化建议
    """
    
    def __init__(self, max_file_size: int = 1_000_000):
        """
        初始化代码分析模块
        
        Args:
            max_file_size: 最大文件大小限制(字节)
        """
        self.max_file_size = max_file_size
        self.language_extensions = {
            "python": [".py"],
            "javascript": [".js", ".jsx", ".ts", ".tsx"],
            "java": [".java"],
            "cpp": [".cpp", ".cc", ".h", ".hpp"],
            "csharp": [".cs"],
            "go": [".go"],
            "ruby": [".rb"],
            "php": [".php"],
            "rust": [".rs"]
        }
        
        # 复杂度阈值
        self.complexity_thresholds = {
            "function_lines": {
                "good": 30,  # 30行以下为好
                "warning": 50,  # 30-50行为警告
                "critical": 100  # 50行以上为问题
            },
            "cyclomatic": {
                "good": 10,  # 10以下为好
                "warning": 20,  # 10-20为警告
                "critical": 30  # 20以上为问题
            }
        }
        
        print("代码分析模块初始化完成")
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        分析单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return {"error": f"文件不存在: {file_path}"}
            
        # 检查文件大小
        file_size = path.stat().st_size
        if file_size > self.max_file_size:
            return {"error": f"文件过大 ({file_size} 字节), 超过限制 ({self.max_file_size} 字节)"}
            
        # 确定文件语言
        language = self._detect_language_by_extension(path.suffix)
        if not language:
            return {"error": f"不支持的文件类型: {path.suffix}"}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 进行文件分析
            result = {
                "file": str(path),
                "language": language,
                "size": file_size,
                "lines": content.count('\n') + 1,
                "metrics": self._calculate_metrics(content, language),
                "structure": self._analyze_structure(content, language),
                "quality": self._analyze_quality(content, language),
                "summary": {},  # 将在最后填充
            }
            
            # 生成摘要
            result["summary"] = self._generate_summary(result)
            
            return result
            
        except Exception as e:
            return {"error": f"分析文件时出错: {str(e)}"}
    
    def analyze_project(self, project_dir: str, exclude_dirs: List[str] = None) -> Dict[str, Any]:
        """
        分析整个项目目录
        
        Args:
            project_dir: 项目目录
            exclude_dirs: 要排除的目录列表
            
        Returns:
            Dict[str, Any]: 项目分析结果
        """
        exclude_dirs = exclude_dirs or ["node_modules", "venv", "__pycache__", ".git"]
        path = Path(project_dir)
        if not path.exists() or not path.is_dir():
            return {"error": f"目录不存在: {project_dir}"}
            
        results = {
            "project": str(path),
            "file_count": 0,
            "language_stats": {},
            "files": [],
            "summary": {},
            "top_complex_files": [],
            "top_large_files": []
        }
        
        # 分析项目中的每个文件
        for root, dirs, files in os.walk(project_dir):
            # 排除指定目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                language = self._detect_language_by_extension(Path(file).suffix)
                
                if language:  # 只分析支持的文件类型
                    file_result = self.analyze_file(file_path)
                    if "error" not in file_result:
                        results["files"].append(file_result)
                        results["file_count"] += 1
                        
                        # 更新语言统计
                        if language in results["language_stats"]:
                            results["language_stats"][language] += 1
                        else:
                            results["language_stats"][language] = 1
        
        # 生成项目摘要
        results["summary"] = self._generate_project_summary(results)
        
        # 找出最复杂的文件和最大的文件
        sorted_by_complexity = sorted(results["files"], 
                                     key=lambda x: x["metrics"].get("complexity", {}).get("cyclomatic", 0), 
                                     reverse=True)
        results["top_complex_files"] = sorted_by_complexity[:5]
        
        sorted_by_size = sorted(results["files"], key=lambda x: x["size"], reverse=True)
        results["top_large_files"] = sorted_by_size[:5]
        
        return results
    
    def suggest_improvements(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于分析结果提供改进建议
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            List[Dict[str, Any]]: 改进建议列表
        """
        if "error" in analysis_result:
            return [{"message": "无法提供建议，分析出错"}]
            
        suggestions = []
        
        # 单文件分析
        if "file" in analysis_result:
            # 检查文件大小
            if analysis_result["size"] > 50000:  # 50KB
                suggestions.append({
                    "type": "structure",
                    "severity": "medium",
                    "message": f"文件过大 ({analysis_result['size'] / 1000:.1f}KB)，考虑拆分为多个小文件"
                })
                
            # 检查复杂度
            cyclomatic = analysis_result.get("metrics", {}).get("complexity", {}).get("cyclomatic", 0)
            if cyclomatic > self.complexity_thresholds["cyclomatic"]["warning"]:
                suggestions.append({
                    "type": "complexity",
                    "severity": "high" if cyclomatic > self.complexity_thresholds["cyclomatic"]["critical"] else "medium",
                    "message": f"代码复杂度过高 ({cyclomatic})，考虑重构以降低复杂度"
                })
                
            # 检查函数长度
            long_functions = [f for f in analysis_result.get("structure", {}).get("functions", []) 
                             if f.get("lines", 0) > self.complexity_thresholds["function_lines"]["warning"]]
            for func in long_functions[:3]:  # 最多显示3个
                suggestions.append({
                    "type": "function_length",
                    "severity": "medium",
                    "message": f"函数 '{func.get('name', 'unknown')}' 过长 ({func.get('lines', 0)}行)，考虑拆分"
                })
                
        # 项目分析
        elif "project" in analysis_result:
            # 代码重复检查
            if len(analysis_result.get("files", [])) > 10:
                suggestions.append({
                    "type": "duplication",
                    "severity": "medium",
                    "message": "大型项目应检查代码重复情况，考虑使用代码重复检测工具"
                })
                
            # 项目结构建议
            if analysis_result.get("file_count", 0) > 50:
                suggestions.append({
                    "type": "structure",
                    "severity": "low",
                    "message": "大型项目应考虑模块化结构，确保遵循良好的项目组织原则"
                })
                
        return suggestions
    
    def _detect_language_by_extension(self, extension: str) -> Optional[str]:
        """根据文件扩展名检测语言"""
        extension = extension.lower()
        for language, extensions in self.language_extensions.items():
            if extension in extensions:
                return language
        return None
    
    def _calculate_metrics(self, content: str, language: str) -> Dict[str, Any]:
        """计算代码度量指标"""
        # 这里是简化的度量计算
        # 实际实现中会根据语言特性进行更精确的计算
        
        lines = content.count('\n') + 1
        non_blank_lines = len([line for line in content.split('\n') if line.strip()])
        comment_lines = self._count_comment_lines(content, language)
        
        # 简化的圈复杂度计算
        if language == "python":
            decision_points = len(re.findall(r'\bif\b|\bfor\b|\bwhile\b|\belif\b|\bwith\b|\band\b|\bor\b', content))
        elif language in ["javascript", "typescript", "java", "cpp", "csharp"]:
            decision_points = len(re.findall(r'\bif\b|\bfor\b|\bwhile\b|\b&&\b|\b\|\|\b|\b\?\b|\bcatch\b|\bcase\b', content))
        else:
            decision_points = 0
            
        # 简单的圈复杂度：决策点 + 1
        cyclomatic_complexity = decision_points + 1
        
        return {
            "lines": lines,
            "non_blank_lines": non_blank_lines,
            "comment_lines": comment_lines,
            "comment_ratio": comment_lines / non_blank_lines if non_blank_lines > 0 else 0,
            "complexity": {
                "cyclomatic": cyclomatic_complexity,
                "decision_points": decision_points
            }
        }
    
    def _analyze_structure(self, content: str, language: str) -> Dict[str, Any]:
        """分析代码结构"""
        structure = {
            "functions": [],
            "classes": [],
            "imports": []
        }
        
        if language == "python":
            # 查找函数定义
            for match in re.finditer(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content):
                name = match.group(1)
                start_pos = match.start()
                line_number = content[:start_pos].count('\n') + 1
                
                # 简单估计函数长度
                function_content = content[start_pos:]
                next_def = function_content.find('\ndef ')
                if next_def == -1:
                    next_def = len(function_content)
                function_lines = function_content[:next_def].count('\n') + 1
                
                structure["functions"].append({
                    "name": name,
                    "line": line_number,
                    "lines": function_lines
                })
                
            # 查找类定义
            for match in re.finditer(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content):
                name = match.group(1)
                line_number = content[:match.start()].count('\n') + 1
                structure["classes"].append({
                    "name": name,
                    "line": line_number
                })
                
            # 查找导入语句
            for match in re.finditer(r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)|(from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import)', content):
                imp = match.group(0)
                line_number = content[:match.start()].count('\n') + 1
                structure["imports"].append({
                    "statement": imp,
                    "line": line_number
                })
                
        elif language in ["javascript", "typescript"]:
            # JavaScript/TypeScript结构分析
            # 函数定义(包括常规、箭头和方法)
            function_patterns = [
                r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(', # 普通函数
                r'(const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function', # 函数表达式
                r'(const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\([^)]*\)\s*=>', # 箭头函数
                r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*{' # 可能是方法
            ]
            
            for pattern in function_patterns:
                for match in re.finditer(pattern, content):
                    name = match.group(1) if pattern != function_patterns[1] and pattern != function_patterns[2] else match.group(2)
                    if name:  # 确保提取到了名称
                        line_number = content[:match.start()].count('\n') + 1
                        structure["functions"].append({
                            "name": name,
                            "line": line_number,
                            "lines": 0  # 为简化，此处未计算函数长度
                        })
            
            # 类定义
            for match in re.finditer(r'class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', content):
                name = match.group(1)
                line_number = content[:match.start()].count('\n') + 1
                structure["classes"].append({
                    "name": name,
                    "line": line_number
                })
                
            # 导入语句
            for match in re.finditer(r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]', content):
                source = match.group(1)
                line_number = content[:match.start()].count('\n') + 1
                structure["imports"].append({
                    "source": source,
                    "line": line_number
                })
        
        # 其他语言可以继续添加...
        
        return structure
    
    def _analyze_quality(self, content: str, language: str) -> Dict[str, Any]:
        """分析代码质量"""
        quality = {
            "issues": []
        }
        
        # 检查代码气味
        if language == "python":
            # 检查过长的行
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if len(line) > 100:  # PEP8建议最大行长度
                    quality["issues"].append({
                        "type": "line_length",
                        "severity": "low",
                        "message": f"行{i+1}超过推荐的最大长度(100个字符)",
                        "line": i+1
                    })
                    
            # 检查多重嵌套
            indent_levels = []
            for i, line in enumerate(lines):
                if line.strip():  # 非空行
                    indent = len(line) - len(line.lstrip())
                    indent_levels.append(indent)
                    
                    if len(indent_levels) >= 4 and all(level > 0 for level in indent_levels[-4:]):
                        quality["issues"].append({
                            "type": "deep_nesting",
                            "severity": "medium",
                            "message": f"行{i+1}处有深度嵌套，考虑重构以减少嵌套层级",
                            "line": i+1
                        })
            
            # 检查裸异常
            if re.search(r'except\s*:', content):
                quality["issues"].append({
                    "type": "bare_except",
                    "severity": "medium",
                    "message": "使用了裸except子句，应指定具体异常类型"
                })
                
        elif language in ["javascript", "typescript"]:
            # 检查console.log语句
            for i, match in enumerate(re.finditer(r'console\.log\(', content)):
                line_number = content[:match.start()].count('\n') + 1
                quality["issues"].append({
                    "type": "console_log",
                    "severity": "low",
                    "message": f"行{line_number}有console.log语句，正式代码中应避免",
                    "line": line_number
                })
                
            # 检查==而不是===
            for i, match in enumerate(re.finditer(r'[^=]=[^=]', content)):
                line_number = content[:match.start()].count('\n') + 1
                quality["issues"].append({
                    "type": "equality_check",
                    "severity": "medium",
                    "message": f"行{line_number}可能使用了==而非===，推荐使用===进行严格相等比较",
                    "line": line_number
                })
        
        return quality
    
    def _count_comment_lines(self, content: str, language: str) -> int:
        """计算注释行数"""
        if language == "python":
            # 简化: 只计算#开头的注释行
            return len([line for line in content.split('\n') if line.strip().startswith('#')])
        elif language in ["javascript", "typescript", "java", "cpp", "csharp"]:
            # 简化计算: 只计算//开头的注释行
            return len([line for line in content.split('\n') if line.strip().startswith('//')])
        else:
            return 0
    
    def _generate_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成文件分析摘要"""
        metrics = analysis_result.get("metrics", {})
        structure = analysis_result.get("structure", {})
        
        # 评估代码质量
        quality_score = 100  # 满分100
        
        # 根据复杂度降低分数
        cyclomatic = metrics.get("complexity", {}).get("cyclomatic", 0)
        if cyclomatic > self.complexity_thresholds["cyclomatic"]["critical"]:
            quality_score -= 30
        elif cyclomatic > self.complexity_thresholds["cyclomatic"]["warning"]:
            quality_score -= 15
            
        # 根据注释率评分
        comment_ratio = metrics.get("comment_ratio", 0)
        if comment_ratio < 0.1:  # 注释不足10%
            quality_score -= 10
            
        # 根据问题数量评分
        issue_count = len(analysis_result.get("quality", {}).get("issues", []))
        quality_score -= issue_count * 2  # 每个问题扣2分
        
        # 确保分数在有效范围内
        quality_score = max(0, min(100, quality_score))
        
        return {
            "quality_score": quality_score,
            "quality_level": "优秀" if quality_score >= 90 else "良好" if quality_score >= 70 else "一般" if quality_score >= 50 else "较差",
            "function_count": len(structure.get("functions", [])),
            "class_count": len(structure.get("classes", [])),
            "issues_count": issue_count
        }
    
    def _generate_project_summary(self, project_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成项目分析摘要"""
        files = project_result.get("files", [])
        if not files:
            return {"error": "没有可分析的文件"}
            
        # 计算平均质量分数
        quality_scores = [f.get("summary", {}).get("quality_score", 0) for f in files]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # 计算平均圈复杂度
        complexities = [f.get("metrics", {}).get("complexity", {}).get("cyclomatic", 0) for f in files]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        
        # 总问题数
        total_issues = sum(len(f.get("quality", {}).get("issues", [])) for f in files)
        
        return {
            "avg_quality_score": avg_quality,
            "quality_level": "优秀" if avg_quality >= 90 else "良好" if avg_quality >= 70 else "一般" if avg_quality >= 50 else "较差",
            "avg_complexity": avg_complexity,
            "total_issues": total_issues,
            "total_files": len(files),
            "most_used_language": max(project_result.get("language_stats", {}).items(), key=lambda x: x[1])[0] if project_result.get("language_stats") else "未知"
        } 