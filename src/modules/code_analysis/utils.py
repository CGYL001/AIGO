"""
代码分析工具函数 - 提供通用工具方法
"""

from typing import Dict, Any, Optional

# 支持的编程语言扩展名映射
LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
    "cpp": [".cpp", ".cc", ".h", ".hpp"],
    "csharp": [".cs"],
    "go": [".go"],
    "ruby": [".rb"],
    "php": [".php"],
    "rust": [".rs"]
}

def detect_language_by_extension(extension: str) -> Optional[str]:
    """
    根据文件扩展名检测编程语言
    
    Args:
        extension: 文件扩展名
        
    Returns:
        Optional[str]: 检测到的语言，如果不支持则返回None
    """
    extension = extension.lower()
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if extension in extensions:
            return language
    return None

def generate_summary(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据分析结果生成文件摘要
    
    Args:
        analysis_result: 文件分析结果
        
    Returns:
        Dict[str, Any]: 摘要信息
    """
    metrics = analysis_result.get("metrics", {})
    structure = analysis_result.get("structure", {})
    
    # 计算代码/注释比例
    code_lines = metrics.get("non_blank_lines", 0)
    comment_lines = metrics.get("comment_lines", 0)
    
    if code_lines > 0:
        comment_ratio = comment_lines / code_lines * 100
    else:
        comment_ratio = 0
        
    # 复杂度评级
    cyclomatic = metrics.get("complexity", {}).get("cyclomatic", 0)
    if cyclomatic <= 10:
        complexity_rating = "良好"
    elif cyclomatic <= 20:
        complexity_rating = "中等"
    else:
        complexity_rating = "复杂"
        
    # 生成摘要
    return {
        "function_count": len(structure.get("functions", [])),
        "class_count": len(structure.get("classes", [])),
        "comment_ratio": f"{comment_ratio:.1f}%",
        "complexity_rating": complexity_rating,
        "has_issues": cyclomatic > 20 or comment_ratio < 10 or code_lines > 500
    }

def generate_project_summary(project_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据项目分析结果生成项目摘要
    
    Args:
        project_result: 项目分析结果
        
    Returns:
        Dict[str, Any]: 项目摘要信息
    """
    files = project_result.get("files", [])
    
    if not files:
        return {"message": "项目中没有可分析的文件"}
    
    # 统计总行数
    total_lines = sum(file.get("lines", 0) for file in files)
    
    # 统计各种复杂度指标
    complexity_sum = sum(file.get("metrics", {}).get("complexity", {}).get("cyclomatic", 0) for file in files)
    complexity_avg = complexity_sum / len(files) if files else 0
    
    # 统计函数和类的数量
    function_count = sum(len(file.get("structure", {}).get("functions", [])) for file in files)
    class_count = sum(len(file.get("structure", {}).get("classes", [])) for file in files)
    
    # 生成摘要
    return {
        "file_count": len(files),
        "total_lines": total_lines,
        "function_count": function_count,
        "class_count": class_count,
        "complexity_avg": f"{complexity_avg:.2f}",
        "primary_language": max(project_result.get("language_stats", {}).items(), key=lambda x: x[1])[0] if project_result.get("language_stats") else "未知",
        "created_at": project_result.get("created_at", ""),
        "updated_at": project_result.get("updated_at", "")
    }

def count_comment_lines(content: str, language: str) -> int:
    """
    计算代码中的注释行数
    
    Args:
        content: 代码内容
        language: 编程语言
        
    Returns:
        int: 注释行数
    """
    # 简单实现，实际中应该根据语言不同使用更精确的方法
    comment_lines = 0
    lines = content.split('\n')
    
    if language == "python":
        for line in lines:
            if line.strip().startswith('#'):
                comment_lines += 1
    elif language in ["javascript", "typescript", "java", "cpp", "csharp"]:
        in_block_comment = False
        for line in lines:
            stripped = line.strip()
            if in_block_comment:
                comment_lines += 1
                if "*/" in stripped:
                    in_block_comment = False
            elif stripped.startswith('//'):
                comment_lines += 1
            elif "/*" in stripped:
                comment_lines += 1
                if "*/" not in stripped[stripped.index("/*")+2:]:
                    in_block_comment = True
    
    return comment_lines 