#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代码分析器模块

提供代码分析功能，包括函数和类的提取、依赖分析等
"""

import os
import ast
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """代码分析器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化代码分析器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        logger.info("代码分析器初始化完成")
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        logger.info(f"分析文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.analyze_code(content, file_path)
        except Exception as e:
            logger.error(f"分析文件失败: {file_path}, 错误: {str(e)}")
            return {
                "error": str(e),
                "file_path": file_path
            }
    
    def analyze_code(self, code: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """分析代码
        
        Args:
            code: 代码字符串
            file_path: 可选的文件路径
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            # 解析AST
            tree = ast.parse(code)
            
            # 提取导入
            imports = self._extract_imports(tree)
            
            # 提取函数
            functions = self._extract_functions(tree)
            
            # 提取类
            classes = self._extract_classes(tree)
            
            # 提取变量
            variables = self._extract_variables(tree)
            
            # 计算复杂度
            complexity = self._calculate_complexity(tree)
            
            # 构建结果
            result = {
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "complexity": complexity
            }
            
            if file_path:
                result["file_path"] = file_path
            
            return result
        except Exception as e:
            logger.error(f"分析代码失败: {str(e)}")
            return {
                "error": str(e),
                "file_path": file_path
            }
    
    def analyze_directory(self, directory_path: str, file_extensions: List[str] = None) -> Dict[str, Any]:
        """分析目录中的所有代码文件
        
        Args:
            directory_path: 目录路径
            file_extensions: 要分析的文件扩展名列表
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        logger.info(f"分析目录: {directory_path}")
        
        results = {}
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    results[file_path] = self.analyze_file(file_path)
        
        return {
            "directory_path": directory_path,
            "file_count": len(results),
            "files": results
        }
    
    def _extract_imports(self, tree: ast.Module) -> List[Dict[str, str]]:
        """提取导入语句
        
        Args:
            tree: AST树
        
        Returns:
            List[Dict[str, str]]: 导入语句列表
        """
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        "type": "import",
                        "name": name.name,
                        "alias": name.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    imports.append({
                        "type": "from",
                        "module": module,
                        "name": name.name,
                        "alias": name.asname
                    })
        
        return imports
    
    def _extract_functions(self, tree: ast.Module) -> List[Dict[str, Any]]:
        """提取函数定义
        
        Args:
            tree: AST树
        
        Returns:
            List[Dict[str, Any]]: 函数定义列表
        """
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 获取函数参数
                args = []
                for arg in node.args.args:
                    args.append(arg.arg)
                
                # 获取函数文档字符串
                docstring = ast.get_docstring(node)
                
                functions.append({
                    "name": node.name,
                    "args": args,
                    "docstring": docstring,
                    "line": node.lineno,
                    "end_line": node.end_lineno
                })
        
        return functions
    
    def _extract_classes(self, tree: ast.Module) -> List[Dict[str, Any]]:
        """提取类定义
        
        Args:
            tree: AST树
        
        Returns:
            List[Dict[str, Any]]: 类定义列表
        """
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 获取基类
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                
                # 获取类文档字符串
                docstring = ast.get_docstring(node)
                
                # 获取类方法
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                
                classes.append({
                    "name": node.name,
                    "bases": bases,
                    "methods": methods,
                    "docstring": docstring,
                    "line": node.lineno,
                    "end_line": node.end_lineno
                })
        
        return classes
    
    def _extract_variables(self, tree: ast.Module) -> List[Dict[str, str]]:
        """提取变量定义
        
        Args:
            tree: AST树
        
        Returns:
            List[Dict[str, str]]: 变量定义列表
        """
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append({
                            "name": target.id,
                            "line": node.lineno
                        })
        
        return variables
    
    def _calculate_complexity(self, tree: ast.Module) -> Dict[str, Union[int, float]]:
        """计算代码复杂度
        
        Args:
            tree: AST树
        
        Returns:
            Dict[str, Union[int, float]]: 复杂度指标
        """
        # 计算循环和条件语句数量
        loops = 0
        conditions = 0
        function_count = 0
        class_count = 0
        line_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                loops += 1
            elif isinstance(node, (ast.If, ast.IfExp)):
                conditions += 1
            elif isinstance(node, ast.FunctionDef):
                function_count += 1
            elif isinstance(node, ast.ClassDef):
                class_count += 1
        
        # 计算行数
        if hasattr(tree, 'end_lineno'):
            line_count = tree.end_lineno
        
        # 计算圈复杂度
        cyclomatic_complexity = 1 + conditions
        
        return {
            "loops": loops,
            "conditions": conditions,
            "functions": function_count,
            "classes": class_count,
            "lines": line_count,
            "cyclomatic_complexity": cyclomatic_complexity
        } 