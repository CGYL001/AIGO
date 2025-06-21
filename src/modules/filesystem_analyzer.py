#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件系统分析器模块

提供文件系统分析功能，包括目录结构分析、文件类型统计等
"""

import os
import logging
import mimetypes
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

logger = logging.getLogger(__name__)

class FilesystemAnalyzer:
    """文件系统分析器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化文件系统分析器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.ignore_dirs = self.config.get("ignore_dirs", [".git", "__pycache__", "venv", ".venv", "node_modules"])
        self.ignore_files = self.config.get("ignore_files", [".DS_Store", "Thumbs.db"])
        self.max_file_size = self.config.get("max_file_size", 10 * 1024 * 1024)  # 默认10MB
        
        # 初始化MIME类型
        mimetypes.init()
        
        logger.info("文件系统分析器初始化完成")
    
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """分析目录结构
        
        Args:
            directory_path: 目录路径
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        logger.info(f"分析目录: {directory_path}")
        
        if not os.path.isdir(directory_path):
            logger.error(f"目录不存在: {directory_path}")
            return {"error": "目录不存在"}
        
        # 统计数据
        stats = {
            "file_count": 0,
            "dir_count": 0,
            "total_size": 0,
            "file_types": {},
            "file_extensions": {},
            "largest_files": [],
            "newest_files": [],
            "deepest_dirs": []
        }
        
        # 文件和目录列表
        files = []
        directories = []
        
        # 遍历目录
        for root, dirs, filenames in os.walk(directory_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            # 计算当前目录深度
            rel_path = os.path.relpath(root, directory_path)
            depth = 0 if rel_path == "." else len(rel_path.split(os.sep))
            
            # 添加目录信息
            dir_info = {
                "path": root,
                "name": os.path.basename(root),
                "depth": depth
            }
            directories.append(dir_info)
            stats["dir_count"] += 1
            
            # 添加深度信息
            if depth > 0:
                stats["deepest_dirs"].append((root, depth))
                stats["deepest_dirs"] = sorted(stats["deepest_dirs"], key=lambda x: x[1], reverse=True)[:10]
            
            # 处理文件
            for filename in filenames:
                if filename in self.ignore_files:
                    continue
                
                file_path = os.path.join(root, filename)
                
                try:
                    # 获取文件信息
                    file_stat = os.stat(file_path)
                    file_size = file_stat.st_size
                    file_mtime = file_stat.st_mtime
                    
                    # 跳过过大的文件
                    if file_size > self.max_file_size:
                        logger.warning(f"跳过大文件: {file_path} ({file_size / 1024 / 1024:.2f} MB)")
                        continue
                    
                    # 获取文件类型
                    file_ext = os.path.splitext(filename)[1].lower()
                    mime_type, _ = mimetypes.guess_type(file_path)
                    mime_type = mime_type or "application/octet-stream"
                    
                    # 更新统计信息
                    stats["file_count"] += 1
                    stats["total_size"] += file_size
                    
                    # 更新文件类型统计
                    file_type = mime_type.split('/')[0]
                    stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
                    
                    # 更新文件扩展名统计
                    if file_ext:
                        stats["file_extensions"][file_ext] = stats["file_extensions"].get(file_ext, 0) + 1
                    
                    # 添加文件信息
                    file_info = {
                        "path": file_path,
                        "name": filename,
                        "size": file_size,
                        "modified": file_mtime,
                        "type": mime_type,
                        "extension": file_ext
                    }
                    files.append(file_info)
                    
                    # 更新最大文件列表
                    stats["largest_files"].append((file_path, file_size))
                    stats["largest_files"] = sorted(stats["largest_files"], key=lambda x: x[1], reverse=True)[:10]
                    
                    # 更新最新文件列表
                    stats["newest_files"].append((file_path, file_mtime))
                    stats["newest_files"] = sorted(stats["newest_files"], key=lambda x: x[1], reverse=True)[:10]
                    
                except Exception as e:
                    logger.error(f"处理文件失败: {file_path}, 错误: {str(e)}")
        
        # 格式化最大文件列表
        stats["largest_files"] = [
            {"path": path, "size": size, "size_mb": size / 1024 / 1024}
            for path, size in stats["largest_files"]
        ]
        
        # 格式化最新文件列表
        stats["newest_files"] = [
            {"path": path, "modified": mtime}
            for path, mtime in stats["newest_files"]
        ]
        
        # 格式化最深目录列表
        stats["deepest_dirs"] = [
            {"path": path, "depth": depth}
            for path, depth in stats["deepest_dirs"]
        ]
        
        # 计算平均文件大小
        if stats["file_count"] > 0:
            stats["avg_file_size"] = stats["total_size"] / stats["file_count"]
        else:
            stats["avg_file_size"] = 0
        
        # 格式化总大小
        stats["total_size_mb"] = stats["total_size"] / 1024 / 1024
        
        return {
            "directory": directory_path,
            "stats": stats,
            "files": files,
            "directories": directories
        }
    
    def find_duplicate_files(self, directory_path: str) -> Dict[str, List[str]]:
        """查找重复文件
        
        Args:
            directory_path: 目录路径
        
        Returns:
            Dict[str, List[str]]: 重复文件列表，按文件内容哈希分组
        """
        logger.info(f"查找重复文件: {directory_path}")
        
        import hashlib
        
        # 按大小分组文件
        files_by_size = {}
        
        # 遍历目录
        for root, dirs, filenames in os.walk(directory_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for filename in filenames:
                if filename in self.ignore_files:
                    continue
                
                file_path = os.path.join(root, filename)
                
                try:
                    # 获取文件大小
                    file_size = os.path.getsize(file_path)
                    
                    # 跳过过大的文件
                    if file_size > self.max_file_size:
                        continue
                    
                    # 按大小分组
                    if file_size not in files_by_size:
                        files_by_size[file_size] = []
                    
                    files_by_size[file_size].append(file_path)
                    
                except Exception as e:
                    logger.error(f"处理文件失败: {file_path}, 错误: {str(e)}")
        
        # 查找重复文件
        duplicates = {}
        
        # 对每个大小组计算哈希
        for size, files in files_by_size.items():
            if len(files) < 2:
                continue
            
            # 按文件哈希分组
            files_by_hash = {}
            
            for file_path in files:
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash not in files_by_hash:
                        files_by_hash[file_hash] = []
                    
                    files_by_hash[file_hash].append(file_path)
                    
                except Exception as e:
                    logger.error(f"计算文件哈希失败: {file_path}, 错误: {str(e)}")
            
            # 添加重复文件
            for file_hash, paths in files_by_hash.items():
                if len(paths) > 1:
                    duplicates[file_hash] = paths
        
        logger.info(f"找到 {len(duplicates)} 组重复文件")
        return duplicates
    
    def analyze_file_types(self, directory_path: str) -> Dict[str, Any]:
        """分析文件类型分布
        
        Args:
            directory_path: 目录路径
        
        Returns:
            Dict[str, Any]: 文件类型统计
        """
        logger.info(f"分析文件类型: {directory_path}")
        
        result = self.analyze_directory(directory_path)
        
        # 提取文件类型统计
        file_types = result["stats"]["file_types"]
        file_extensions = result["stats"]["file_extensions"]
        
        # 计算百分比
        total_files = result["stats"]["file_count"]
        
        type_percentages = {}
        for file_type, count in file_types.items():
            type_percentages[file_type] = (count / total_files) * 100 if total_files > 0 else 0
        
        extension_percentages = {}
        for ext, count in file_extensions.items():
            extension_percentages[ext] = (count / total_files) * 100 if total_files > 0 else 0
        
        return {
            "directory": directory_path,
            "total_files": total_files,
            "file_types": file_types,
            "file_type_percentages": type_percentages,
            "file_extensions": file_extensions,
            "file_extension_percentages": extension_percentages
        }
    
    def export_directory_structure(self, directory_path: str, output_file: str) -> bool:
        """导出目录结构
        
        Args:
            directory_path: 目录路径
            output_file: 输出文件路径
        
        Returns:
            bool: 是否成功导出
        """
        logger.info(f"导出目录结构: {directory_path} -> {output_file}")
        
        try:
            result = self.analyze_directory(directory_path)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"目录结构已导出: {output_file}")
            return True
        except Exception as e:
            logger.error(f"导出目录结构失败: {str(e)}")
            return False 