import os
import re
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
import fnmatch

from src.utils import config, logger


class FilesystemAnalyzer:
    """
    文件系统分析器，提供项目结构分析和语义理解功能
    """
    
    def __init__(self):
        """初始化文件系统分析器"""
        # 文件缓存，存储文件内容的哈希值和最后修改时间
        self.file_cache: Dict[str, Dict[str, Any]] = {}
        
        # 项目结构缓存
        self.project_structure: Dict[str, Any] = {}
        
        # 配置
        self.ignored_dirs = config.get("filesystem_analyzer.ignored_dirs", 
                                      [".git", ".svn", "node_modules", "__pycache__", ".venv", "venv", "env"])
        self.ignored_extensions = config.get("filesystem_analyzer.ignored_extensions", 
                                           [".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin"])
        self.max_file_size_mb = config.get("filesystem_analyzer.max_file_size_mb", 10)
        self.content_cache_enabled = config.get("filesystem_analyzer.content_cache_enabled", True)
        self.content_cache_size = config.get("filesystem_analyzer.content_cache_size", 100)  # 缓存的最大文件数
        
        # 语言检测配置
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
            "swift": [".swift"],
            "html": [".html", ".htm"],
            "css": [".css"],
            "markdown": [".md", ".markdown"],
            "json": [".json"],
            "yaml": [".yml", ".yaml"],
            "xml": [".xml"],
            "sql": [".sql"],
            "shell": [".sh", ".bash", ".zsh"]
        }
        
        # 内容缓存
        self.content_cache: Dict[str, str] = {}
        self.content_cache_keys: List[str] = []  # 用于LRU缓存管理
        
        logger.info("文件系统分析器初始化完成")
    
    def scan_directory(self, directory_path: str, incremental: bool = True) -> Dict[str, Any]:
        """
        扫描目录，分析项目结构
        
        Args:
            directory_path: 要扫描的目录路径
            incremental: 是否增量扫描，只处理变化的文件
            
        Returns:
            Dict[str, Any]: 项目结构信息
        """
        start_time = time.time()
        directory_path = os.path.abspath(directory_path)
        
        if not os.path.exists(directory_path):
            logger.error(f"目录不存在: {directory_path}")
            return {"error": f"目录不存在: {directory_path}"}
        
        logger.info(f"开始扫描目录: {directory_path}")
        
        # 初始化项目结构
        structure = {
            "path": directory_path,
            "name": os.path.basename(directory_path),
            "type": "directory",
            "files": [],
            "directories": [],
            "file_count": 0,
            "directory_count": 0,
            "languages": {},
            "file_types": {},
            "total_size_bytes": 0,
            "last_modified": 0,
            "scan_time": time.time(),
            "changed_files": [],
            "new_files": [],
            "deleted_files": []
        }
        
        # 获取当前目录中的所有文件路径
        current_files = set()
        
        # 遍历目录
        for root, dirs, files in os.walk(directory_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            # 相对路径
            rel_path = os.path.relpath(root, directory_path)
            if rel_path == ".":
                rel_path = ""
            
            # 处理文件
            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.join(rel_path, file) if rel_path else file
                
                # 添加到当前文件集合
                current_files.add(rel_file_path)
                
                # 检查是否忽略该文件
                _, ext = os.path.splitext(file)
                if ext in self.ignored_extensions:
                    continue
                
                # 检查文件大小
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > self.max_file_size_mb * 1024 * 1024:
                        continue
                except Exception:
                    continue
                
                # 获取文件最后修改时间
                try:
                    last_modified = os.path.getmtime(file_path)
                except Exception:
                    last_modified = 0
                
                # 检查文件是否变化（增量扫描）
                file_changed = False
                if incremental and rel_file_path in self.file_cache:
                    cached_info = self.file_cache[rel_file_path]
                    if cached_info["last_modified"] == last_modified:
                        # 文件未变化，使用缓存信息
                        structure["files"].append(cached_info)
                        structure["file_count"] += 1
                        structure["total_size_bytes"] += cached_info["size"]
                        
                        # 更新语言统计
                        lang = cached_info.get("language")
                        if lang:
                            structure["languages"][lang] = structure["languages"].get(lang, 0) + 1
                        
                        # 更新文件类型统计
                        file_type = cached_info.get("type")
                        if file_type:
                            structure["file_types"][file_type] = structure["file_types"].get(file_type, 0) + 1
                        
                        continue
                    else:
                        file_changed = True
                
                # 处理新文件或已更改的文件
                file_info = self._analyze_file(file_path, rel_file_path)
                
                # 更新缓存
                self.file_cache[rel_file_path] = file_info
                
                # 添加到结构
                structure["files"].append(file_info)
                structure["file_count"] += 1
                structure["total_size_bytes"] += file_info["size"]
                
                # 更新语言统计
                lang = file_info.get("language")
                if lang:
                    structure["languages"][lang] = structure["languages"].get(lang, 0) + 1
                
                # 更新文件类型统计
                file_type = file_info.get("type")
                if file_type:
                    structure["file_types"][file_type] = structure["file_types"].get(file_type, 0) + 1
                
                # 记录变化
                if file_changed:
                    structure["changed_files"].append(rel_file_path)
                elif incremental and rel_file_path not in self.file_cache:
                    structure["new_files"].append(rel_file_path)
            
            # 处理目录
            structure["directory_count"] += len(dirs)
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                rel_dir_path = os.path.join(rel_path, dir_name) if rel_path else dir_name
                
                dir_info = {
                    "path": dir_path,
                    "relative_path": rel_dir_path,
                    "name": dir_name,
                    "type": "directory",
                    "last_modified": os.path.getmtime(dir_path)
                }
                structure["directories"].append(dir_info)
        
        # 检查删除的文件
        if incremental:
            cached_files = set(self.file_cache.keys())
            deleted_files = cached_files - current_files
            for del_file in deleted_files:
                structure["deleted_files"].append(del_file)
                self.file_cache.pop(del_file, None)
                self._remove_from_content_cache(del_file)
        
        # 更新项目结构缓存
        self.project_structure = structure
        
        # 计算扫描时间
        scan_duration = time.time() - start_time
        structure["scan_duration"] = scan_duration
        
        logger.info(f"目录扫描完成: {directory_path}, 耗时: {scan_duration:.2f}秒")
        logger.info(f"文件数: {structure['file_count']}, 目录数: {structure['directory_count']}")
        logger.info(f"新文件: {len(structure['new_files'])}, 变化文件: {len(structure['changed_files'])}, 删除文件: {len(structure['deleted_files'])}")
        
        return structure
    
    def _analyze_file(self, file_path: str, relative_path: str) -> Dict[str, Any]:
        """分析单个文件"""
        file_name = os.path.basename(file_path)
        _, ext = os.path.splitext(file_name)
        
        try:
            file_size = os.path.getsize(file_path)
            last_modified = os.path.getmtime(file_path)
            
            # 检测文件类型和语言
            file_type = "text" if self._is_text_file(file_path) else "binary"
            language = self._detect_language(file_path)
            
            # 计算文件哈希值
            file_hash = self._calculate_file_hash(file_path)
            
            # 提取导入语句和依赖关系
            imports = []
            dependencies = []
            if language and file_type == "text":
                imports = self._extract_imports(file_path, language)
                dependencies = self._extract_dependencies(file_path, language)
            
            file_info = {
                "path": file_path,
                "relative_path": relative_path,
                "name": file_name,
                "extension": ext,
                "size": file_size,
                "type": file_type,
                "language": language,
                "last_modified": last_modified,
                "hash": file_hash,
                "imports": imports,
                "dependencies": dependencies
            }
            
            return file_info
        except Exception as e:
            logger.error(f"分析文件失败: {file_path}, 错误: {str(e)}")
            return {
                "path": file_path,
                "relative_path": relative_path,
                "name": file_name,
                "extension": ext,
                "size": 0,
                "type": "unknown",
                "language": None,
                "last_modified": 0,
                "hash": "",
                "imports": [],
                "dependencies": [],
                "error": str(e)
            }
    
    def _is_text_file(self, file_path: str) -> bool:
        """判断文件是否为文本文件"""
        try:
            # 检查文件扩展名
            _, ext = os.path.splitext(file_path)
            
            # 常见文本文件扩展名
            text_extensions = [
                ".txt", ".md", ".py", ".js", ".ts", ".html", ".css", ".json", ".xml",
                ".yml", ".yaml", ".ini", ".cfg", ".conf", ".sh", ".bat", ".c", ".cpp",
                ".h", ".hpp", ".java", ".rb", ".php", ".go", ".rs", ".swift", ".kt"
            ]
            
            if ext.lower() in text_extensions:
                return True
            
            # 尝试读取文件前几行
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                
            # 检查是否包含空字节（二进制文件通常包含）
            return b'\x00' not in chunk
        except Exception:
            return False
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """检测文件的编程语言"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # 根据扩展名判断语言
        for language, extensions in self.language_extensions.items():
            if ext in extensions:
                return language
                
        return None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件的哈希值"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception:
            return ""
    
    def _extract_imports(self, file_path: str, language: str) -> List[str]:
        """提取文件中的导入语句"""
        imports = []
        
        try:
            # 读取文件内容
            content = self._get_file_content(file_path)
            if not content:
                return imports
            
            # 根据语言提取导入语句
            if language == "python":
                # 匹配Python的import语句
                import_patterns = [
                    r'^import\s+([\w\.]+)',
                    r'^from\s+([\w\.]+)\s+import'
                ]
                for pattern in import_patterns:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        imports.append(match.group(1))
            
            elif language in ["javascript", "typescript"]:
                # 匹配JS/TS的import语句
                import_patterns = [
                    r'import.*?from\s+[\'"]([^\'"]*)[\'"]\s*;?',
                    r'require\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)'
                ]
                for pattern in import_patterns:
                    for match in re.finditer(pattern, content):
                        imports.append(match.group(1))
            
            elif language in ["java", "kotlin"]:
                # 匹配Java/Kotlin的import语句
                import_pattern = r'^import\s+([\w\.]+);'
                for match in re.finditer(import_pattern, content, re.MULTILINE):
                    imports.append(match.group(1))
            
            # 去重
            imports = list(set(imports))
            
        except Exception as e:
            logger.error(f"提取导入语句失败: {file_path}, 错误: {str(e)}")
        
        return imports
    
    def _extract_dependencies(self, file_path: str, language: str) -> List[str]:
        """提取文件的依赖关系"""
        dependencies = []
        
        try:
            # 对于特定语言的项目配置文件，提取依赖信息
            file_name = os.path.basename(file_path)
            
            if file_name == "requirements.txt" and language == "python":
                # Python requirements.txt
                content = self._get_file_content(file_path)
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 提取包名，忽略版本号
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                        if package:
                            dependencies.append(package)
            
            elif file_name == "package.json" and language in ["javascript", "typescript"]:
                # JavaScript/TypeScript package.json
                content = self._get_file_content(file_path)
                try:
                    import json
                    package_data = json.loads(content)
                    # 合并常规依赖和开发依赖
                    deps = package_data.get("dependencies", {})
                    dev_deps = package_data.get("devDependencies", {})
                    all_deps = {**deps, **dev_deps}
                    dependencies = list(all_deps.keys())
                except json.JSONDecodeError:
                    pass
            
            elif file_name == "pom.xml" and language == "java":
                # Java Maven pom.xml
                content = self._get_file_content(file_path)
                # 简单提取，实际应该使用XML解析
                dependency_pattern = r'<dependency>.*?<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?</dependency>'
                for match in re.finditer(dependency_pattern, content, re.DOTALL):
                    group_id = match.group(1)
                    artifact_id = match.group(2)
                    dependencies.append(f"{group_id}:{artifact_id}")
            
        except Exception as e:
            logger.error(f"提取依赖关系失败: {file_path}, 错误: {str(e)}")
        
        return dependencies
    
    def _get_file_content(self, file_path: str) -> str:
        """获取文件内容，使用缓存减少磁盘I/O"""
        if not self.content_cache_enabled:
            # 缓存禁用，直接读取文件
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception:
                return ""
        
        # 使用缓存
        if file_path in self.content_cache:
            # 更新LRU缓存顺序
            self.content_cache_keys.remove(file_path)
            self.content_cache_keys.append(file_path)
            return self.content_cache[file_path]
        
        # 读取文件并缓存
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 管理缓存大小
            if len(self.content_cache_keys) >= self.content_cache_size:
                # 移除最久未使用的项
                oldest_key = self.content_cache_keys.pop(0)
                self.content_cache.pop(oldest_key, None)
            
            # 添加到缓存
            self.content_cache[file_path] = content
            self.content_cache_keys.append(file_path)
            
            return content
        except Exception:
            return ""
    
    def _remove_from_content_cache(self, relative_path: str) -> None:
        """从内容缓存中移除文件"""
        # 查找绝对路径
        for file_path in list(self.content_cache.keys()):
            if file_path.endswith(relative_path):
                self.content_cache.pop(file_path, None)
                if file_path in self.content_cache_keys:
                    self.content_cache_keys.remove(file_path)
                break
    
    def find_files(self, directory_path: str, pattern: str, recursive: bool = True) -> List[str]:
        """
        在目录中查找匹配模式的文件
        
        Args:
            directory_path: 要搜索的目录路径
            pattern: 文件名模式，支持通配符
            recursive: 是否递归搜索子目录
            
        Returns:
            List[str]: 匹配的文件路径列表
        """
        matches = []
        directory_path = os.path.abspath(directory_path)
        
        if not os.path.exists(directory_path):
            logger.error(f"目录不存在: {directory_path}")
            return matches
        
        if recursive:
            for root, dirnames, filenames in os.walk(directory_path):
                # 过滤忽略的目录
                dirnames[:] = [d for d in dirnames if d not in self.ignored_dirs]
                
                for filename in fnmatch.filter(filenames, pattern):
                    matches.append(os.path.join(root, filename))
        else:
            # 只在当前目录中搜索
            try:
                for item in os.listdir(directory_path):
                    full_path = os.path.join(directory_path, item)
                    if os.path.isfile(full_path) and fnmatch.fnmatch(item, pattern):
                        matches.append(full_path)
            except Exception as e:
                logger.error(f"列出目录内容失败: {directory_path}, 错误: {str(e)}")
        
        return matches
    
    def get_project_structure(self) -> Dict[str, Any]:
        """获取当前的项目结构信息"""
        return self.project_structure
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件的详细信息"""
        file_path = os.path.abspath(file_path)
        rel_path = None
        
        # 查找相对路径
        for cached_path in self.file_cache:
            if self.file_cache[cached_path]["path"] == file_path:
                rel_path = cached_path
                break
        
        if rel_path and rel_path in self.file_cache:
            return self.file_cache[rel_path]
        
        # 文件不在缓存中，分析它
        if os.path.exists(file_path):
            # 尝试确定相对路径
            project_path = self.project_structure.get("path", "")
            if project_path and file_path.startswith(project_path):
                rel_path = os.path.relpath(file_path, project_path)
            else:
                rel_path = os.path.basename(file_path)
            
            return self._analyze_file(file_path, rel_path)
        
        return None
    
    def clear_cache(self) -> None:
        """清除所有缓存"""
        self.file_cache.clear()
        self.content_cache.clear()
        self.content_cache_keys.clear()
        logger.info("文件系统分析器缓存已清除")


# 创建单例实例
filesystem_analyzer = FilesystemAnalyzer() 