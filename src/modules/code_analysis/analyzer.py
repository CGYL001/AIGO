"""
代码分析器主模块 - 协调其他分析组件，提供统一接口
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.modules.code_analysis.metrics import MetricsCalculator
from src.modules.code_analysis.structure import StructureAnalyzer
from src.modules.code_analysis.quality import QualityAnalyzer
from src.modules.code_analysis.utils import detect_language_by_extension, generate_summary, generate_project_summary

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
        self.metrics_calculator = MetricsCalculator()
        self.structure_analyzer = StructureAnalyzer()
        self.quality_analyzer = QualityAnalyzer()
        
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
        language = detect_language_by_extension(path.suffix)
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
                "metrics": self.metrics_calculator.calculate_metrics(content, language),
                "structure": self.structure_analyzer.analyze(content, language),
                "quality": self.quality_analyzer.analyze(content, language),
                "summary": {},  # 将在最后填充
            }
            
            # 生成摘要
            result["summary"] = generate_summary(result)
            
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
                language = detect_language_by_extension(Path(file).suffix)
                
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
        results["summary"] = generate_project_summary(results)
        
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