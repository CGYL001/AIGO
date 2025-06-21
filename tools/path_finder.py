#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路径查找工具

用于快速定位项目中的资源和功能
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# 忽略的目录
IGNORED_DIRS = [
    ".git", ".svn", "node_modules", "__pycache__", 
    ".venv", "venv", "env", "dist", "build", ".idea", 
    ".vscode", ".vs", "bin", "obj"
]

# 忽略的文件扩展名
IGNORED_EXTENSIONS = [
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", 
    ".bin", ".obj", ".o", ".a", ".lib", ".suo", 
    ".pdb", ".class", ".cache"
]

# 功能关键词映射
FEATURE_KEYWORDS = {
    "模型管理": ["model_manager", "model", "models", "registry", "register", "switch", "download"],
    "代码分析": ["code_analysis", "analyzer", "metrics", "code_analyzer"],
    "知识库": ["knowledge_base", "kb", "vector", "storage"],
    "仓库集成": ["repo_integration", "github", "gitee", "repository"],
    "系统监控": ["system_monitor", "resource_monitor", "performance"],
    "提示工程": ["prompt_engineering", "context_builder", "evaluator"],
    "IDE集成": ["ide_integration", "cursor_extension", "vscode_extension"]
}

class PathFinder:
    """路径查找工具类"""
    
    def __init__(self):
        """初始化"""
        self.project_root = ROOT_DIR
        self.index = {}
        self.features_index = {}
        self.build_index()
    
    def build_index(self):
        """构建项目索引"""
        print("正在构建项目索引...")
        self.index = self._scan_directory(self.project_root)
        self._build_features_index()
        print(f"索引构建完成，已扫描 {len(self.index)} 个文件")
    
    def _scan_directory(self, directory: Path) -> Dict[str, Dict]:
        """扫描目录，构建文件索引"""
        result = {}
        
        try:
            for item in directory.iterdir():
                rel_path = str(item.relative_to(self.project_root))
                
                # 检查是否是忽略的目录
                if item.is_dir():
                    if item.name in IGNORED_DIRS:
                        continue
                    
                    # 递归扫描子目录
                    sub_result = self._scan_directory(item)
                    result.update(sub_result)
                
                # 处理文件
                elif item.is_file():
                    # 检查是否是忽略的文件类型
                    if any(item.name.endswith(ext) for ext in IGNORED_EXTENSIONS):
                        continue
                    
                    # 提取文件信息
                    file_info = self._extract_file_info(item)
                    if file_info:
                        result[rel_path] = file_info
        except (PermissionError, OSError) as e:
            print(f"警告: 无法访问 {directory}: {e}")
        
        return result
    
    def _extract_file_info(self, file_path: Path) -> Dict[str, Any]:
        """提取文件信息"""
        info = {
            "path": str(file_path),
            "relative_path": str(file_path.relative_to(self.project_root)),
            "name": file_path.name,
            "extension": file_path.suffix,
            "size": file_path.stat().st_size,
            "keywords": [],
            "description": ""
        }
        
        # 尝试提取文件描述和关键词
        try:
            if file_path.suffix in [".py", ".js", ".ts"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read(4096)  # 只读取前4KB来分析
                    
                    # 提取文件描述
                    description_match = re.search(r'"""(.+?)"""', content, re.DOTALL) or \
                                      re.search(r"'''(.+?)'''", content, re.DOTALL) or \
                                      re.search(r'/\*\*(.+?)\*/', content, re.DOTALL)
                    if description_match:
                        info["description"] = description_match.group(1).strip()
                    
                    # 提取关键词
                    keywords = set()
                    for feature, feature_keywords in FEATURE_KEYWORDS.items():
                        for keyword in feature_keywords:
                            if keyword in content.lower():
                                keywords.add(keyword)
                    info["keywords"] = list(keywords)
        except (UnicodeDecodeError, PermissionError):
            pass
        
        return info
    
    def _build_features_index(self):
        """构建功能索引"""
        self.features_index = {}
        
        for feature, keywords in FEATURE_KEYWORDS.items():
            self.features_index[feature] = []
            
            for file_path, file_info in self.index.items():
                # 检查文件路径和关键词
                if any(keyword in file_path.lower() for keyword in keywords) or \
                   any(keyword in file_info["keywords"] for keyword in keywords):
                    self.features_index[feature].append(file_path)
    
    def find_by_feature(self, feature: str) -> List[str]:
        """根据功能查找相关文件"""
        # 尝试精确匹配
        if feature in self.features_index:
            return self.features_index[feature]
        
        # 尝试部分匹配
        matched_features = [f for f in self.features_index.keys() if feature.lower() in f.lower()]
        if matched_features:
            files = []
            for matched_feature in matched_features:
                files.extend(self.features_index[matched_feature])
            return files
        
        return []
    
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索关键词"""
        results = []
        
        for file_path, file_info in self.index.items():
            if keyword.lower() in file_path.lower() or \
               keyword.lower() in file_info.get("description", "").lower() or \
               keyword.lower() in " ".join(file_info.get("keywords", [])).lower():
                results.append(file_info)
        
        return results
    
    def explore_directory(self, directory: str) -> List[str]:
        """探索目录结构"""
        dir_path = Path(self.project_root) / directory
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        
        items = []
        try:
            for item in dir_path.iterdir():
                rel_path = str(item.relative_to(self.project_root))
                items.append(rel_path)
        except (PermissionError, OSError) as e:
            print(f"警告: 无法访问 {dir_path}: {e}")
        
        return sorted(items)

def print_results(title: str, items: List, description: Optional[str] = None):
    """格式化打印结果"""
    print("\n" + "=" * 80)
    print(f"{title} ({len(items)} 个结果)")
    print("=" * 80)
    
    if description:
        print(f"{description}\n")
    
    for item in items:
        if isinstance(item, dict):
            print(f"- {item['relative_path']}")
            if item.get('description'):
                print(f"  描述: {item['description'][:100]}")
            print()
        else:
            print(f"- {item}")
    
    if not items:
        print("未找到匹配的结果")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AIgo项目路径查找工具")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # find命令 - 查找特定功能
    find_parser = subparsers.add_parser("find", help="查找特定功能相关文件")
    find_parser.add_argument("--feature", "-f", required=True, help="功能名称")
    
    # explore命令 - 浏览目录结构
    explore_parser = subparsers.add_parser("explore", help="浏览目录结构")
    explore_parser.add_argument("--directory", "-d", required=True, help="目录路径")
    
    # search命令 - 搜索关键词
    search_parser = subparsers.add_parser("search", help="搜索关键词")
    search_parser.add_argument("--keyword", "-k", required=True, help="搜索关键词")
    
    # list-features命令 - 列出所有功能
    subparsers.add_parser("list-features", help="列出所有可用功能")
    
    args = parser.parse_args()
    
    # 创建路径查找工具
    finder = PathFinder()
    
    # 根据命令执行操作
    if args.command == "find":
        files = finder.find_by_feature(args.feature)
        print_results(f"功能 '{args.feature}' 相关文件", files, 
                      f"以下文件与功能 '{args.feature}' 相关，可用于查看或修改该功能")
    
    elif args.command == "explore":
        items = finder.explore_directory(args.directory)
        print_results(f"目录 '{args.directory}' 内容", items, 
                      f"'{args.directory}' 目录包含以下文件和子目录")
    
    elif args.command == "search":
        results = finder.search(args.keyword)
        print_results(f"关键词 '{args.keyword}' 搜索结果", results, 
                      f"以下文件包含关键词 '{args.keyword}'")
    
    elif args.command == "list-features":
        print_results("可用功能列表", list(FEATURE_KEYWORDS.keys()), 
                      "以下是可以使用'find'命令查找的功能列表")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 