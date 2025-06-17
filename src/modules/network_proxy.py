import os
import re
import json
import time
import hashlib
import urllib.parse
from typing import Dict, List, Any, Optional, Union, Tuple
import requests
from pathlib import Path
import threading

from src.utils import config, logger

# 创建日志记录器
log = logger.get_logger("network_proxy")

class NetworkProxy:
    """
    网络代理模块，提供安全的网络请求和内容提取功能
    """
    
    def __init__(self):
        """初始化网络代理模块"""
        # 配置
        self.cache_enabled = config.get("network_proxy.cache_enabled", True)
        self.cache_ttl = config.get("network_proxy.cache_ttl_seconds", 3600)  # 缓存有效期，默认1小时
        self.max_cache_size = config.get("network_proxy.max_cache_size", 100) * 1024 * 1024  # 转换为字节
        self.timeout = config.get("network_proxy.timeout_seconds", 10)  # 请求超时时间
        self.max_retries = config.get("network_proxy.max_retries", 3)  # 最大重试次数
        self.user_agent = config.get("network_proxy.user_agent", 
                                   "Mozilla/5.0 MCP-Agent/1.0")  # 请求的User-Agent
        
        # 安全配置
        self.allowed_domains = config.get("network_proxy.allowed_domains", [
            "github.com", "raw.githubusercontent.com", "gitlab.com",
            "stackoverflow.com", "docs.python.org", "developer.mozilla.org",
            "api.github.com", "api.openai.com", "api.anthropic.com"
        ])
        self.allowed_schemes = config.get("network_proxy.allowed_schemes", ["https"])
        self.blocked_content_types = config.get("network_proxy.blocked_content_types", [
            "application/octet-stream", "application/x-msdownload", "application/x-executable"
        ])
        self.max_response_size_mb = config.get("network_proxy.max_response_size_mb", 10)
        
        # 缓存
        self.cache_dir = Path(config.get("network_proxy.cache_dir", "data/network_cache"))
        self.cache_index: Dict[str, Dict[str, Any]] = {}
        self.cache_keys: List[str] = []  # 用于LRU缓存管理
        
        # 创建缓存目录
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 加载缓存索引
        self._load_cache_index()
        
        # 创建会话
        self.session = requests.Session()
        
        # 缓存清理线程
        self._cleanup_thread = None
        self._stop_cleanup = threading.Event()
        
        # 启动缓存清理线程
        self._start_cleanup_thread()
        
        log.info("网络代理模块初始化完成")
    
    def _start_cleanup_thread(self) -> None:
        """启动缓存清理线程"""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._stop_cleanup.clear()
            self._cleanup_thread = threading.Thread(
                target=self._cache_cleanup_task,
                daemon=True
            )
            self._cleanup_thread.start()
            log.debug("Cache cleanup thread started")
    
    def _cache_cleanup_task(self) -> None:
        """缓存清理任务"""
        while not self._stop_cleanup.wait(3600):  # 每小时检查一次
            try:
                self._cleanup_cache()
            except Exception as e:
                log.error(f"Error in cache cleanup task: {str(e)}")
    
    def _cleanup_cache(self) -> None:
        """清理过期和超大的缓存"""
        log.debug("Starting cache cleanup")
        
        # 获取当前时间
        now = time.time()
        
        # 收集所有缓存文件信息
        cache_files = []
        total_size = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                # 获取文件信息
                stat = cache_file.stat()
                file_size = stat.st_size
                total_size += file_size
                
                # 读取缓存元数据
                with open(cache_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                
                # 检查是否过期
                expires_at = metadata.get("expires_at", 0)
                is_expired = expires_at < now
                
                cache_files.append({
                    "path": cache_file,
                    "size": file_size,
                    "expires_at": expires_at,
                    "is_expired": is_expired,
                    "last_access": metadata.get("last_access", 0)
                })
            except Exception as e:
                log.warning(f"Error processing cache file {cache_file}: {str(e)}")
        
        # 删除过期文件
        for cache_file in cache_files:
            if cache_file["is_expired"]:
                try:
                    cache_file["path"].unlink()
                    total_size -= cache_file["size"]
                    log.debug(f"Deleted expired cache file: {cache_file['path']}")
                except Exception as e:
                    log.warning(f"Error deleting cache file {cache_file['path']}: {str(e)}")
        
        # 如果总大小仍然超过限制，删除最旧的文件
        if total_size > self.max_cache_size:
            # 按最后访问时间排序
            remaining_files = [f for f in cache_files if not f["is_expired"]]
            remaining_files.sort(key=lambda x: x["last_access"])
            
            # 删除文件直到总大小低于限制
            for cache_file in remaining_files:
                if total_size <= self.max_cache_size:
                    break
                
                try:
                    cache_file["path"].unlink()
                    total_size -= cache_file["size"]
                    log.debug(f"Deleted old cache file to reduce cache size: {cache_file['path']}")
                except Exception as e:
                    log.warning(f"Error deleting cache file {cache_file['path']}: {str(e)}")
        
        log.debug(f"Cache cleanup completed. Current cache size: {total_size / 1024 / 1024:.2f} MB")
    
    def _is_url_allowed(self, url: str) -> bool:
        """
        检查URL是否在白名单中
        
        Args:
            url: 要检查的URL
            
        Returns:
            bool: 如果URL在白名单中，则返回True
        """
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # 检查域名是否在白名单中
            return domain in self.allowed_domains
        except Exception as e:
            log.warning(f"Error checking URL whitelist for {url}: {str(e)}")
            return False
    
    def _filter_content(self, content: str, url: str) -> str:
        """
        应用内容过滤规则
        
        Args:
            content: 要过滤的内容
            url: 内容的URL
            
        Returns:
            str: 过滤后的内容
        """
        filtered_content = content
        
        for filter_rule in self.blocked_content_types:
            try:
                # 检查规则是否适用于此URL
                url_pattern = filter_rule.get("url_pattern")
                if url_pattern and url_pattern not in url:
                    continue
                
                # 应用替换规则
                pattern = filter_rule.get("pattern")
                replacement = filter_rule.get("replacement", "")
                
                if pattern:
                    import re
                    filtered_content = re.sub(pattern, replacement, filtered_content)
            except Exception as e:
                log.warning(f"Error applying content filter: {str(e)}")
        
        return filtered_content
    
    def _get_cache_path(self, url: str) -> Path:
        """
        获取URL的缓存文件路径
        
        Args:
            url: URL
            
        Returns:
            Path: 缓存文件路径
        """
        # 使用URL的哈希作为缓存文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.json"
    
    def _get_from_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """
        从缓存中获取响应
        
        Args:
            url: URL
            
        Returns:
            Optional[Dict[str, Any]]: 缓存的响应或None
        """
        cache_path = self._get_cache_path(url)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期
            if cache_data.get("expires_at", 0) < time.time():
                log.debug(f"Cache expired for URL: {url}")
                return None
            
            # 更新最后访问时间
            cache_data["last_access"] = time.time()
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f)
            
            log.debug(f"Cache hit for URL: {url}")
            return cache_data
        except Exception as e:
            log.warning(f"Error reading cache for URL {url}: {str(e)}")
            return None
    
    def _save_to_cache(self, url: str, response_data: Dict[str, Any]) -> None:
        """
        保存响应到缓存
        
        Args:
            url: URL
            response_data: 响应数据
        """
        cache_path = self._get_cache_path(url)
        
        try:
            # 添加缓存元数据
            cache_data = {
                **response_data,
                "expires_at": time.time() + self.cache_ttl,
                "last_access": time.time(),
                "url": url
            }
            
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f)
            
            log.debug(f"Saved response to cache for URL: {url}")
        except Exception as e:
            log.warning(f"Error saving cache for URL {url}: {str(e)}")
    
    def request(self, url: str, method: str = "GET", 
               headers: Dict[str, str] = None, 
               params: Dict[str, Any] = None,
               data: Any = None,
               json_data: Dict[str, Any] = None,
               timeout: int = None,
               use_cache: bool = True) -> Dict[str, Any]:
        """
        发送网络请求
        
        Args:
            url: 请求URL
            method: 请求方法，如GET、POST
            headers: 请求头
            params: URL参数
            data: 请求体数据
            json_data: JSON格式的请求体数据
            timeout: 请求超时时间
            use_cache: 是否使用缓存
            
        Returns:
            Dict[str, Any]: 响应结果，包含状态码、内容等信息
        """
        # 安全检查
        security_check = self._security_check(url, method)
        if not security_check["allowed"]:
            return {
                "success": False,
                "status_code": 403,
                "content": None,
                "error": security_check["reason"],
                "headers": {},
                "url": url
            }
        
        # 准备请求参数
        timeout = timeout or self.timeout
        headers = headers or {}
        if "User-Agent" not in headers:
            headers["User-Agent"] = self.user_agent
        
        # 生成缓存键
        cache_key = self._generate_cache_key(url, method, headers, params, data, json_data)
        
        # 检查缓存
        if method == "GET" and use_cache and self.cache_enabled:
            cached_response = self._get_from_cache(url)
            if cached_response:
                log.debug(f"从缓存获取响应: {url}")
                return cached_response
        
        # 发送请求
        try:
            log.debug(f"发送{method}请求: {url}")
            
            for attempt in range(self.max_retries):
                try:
                    response = requests.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        data=data,
                        json=json_data,
                        timeout=timeout,
                        stream=True  # 流式下载，用于检查响应大小
                    )
                    
                    # 检查响应大小
                    content_length = int(response.headers.get("Content-Length", 0))
                    max_size_bytes = self.max_response_size_mb * 1024 * 1024
                    
                    if content_length > max_size_bytes:
                        response.close()
                        return {
                            "success": False,
                            "status_code": 413,
                            "content": None,
                            "error": f"响应大小超过限制: {content_length} 字节",
                            "headers": dict(response.headers),
                            "url": response.url
                        }
                    
                    # 检查内容类型
                    content_type = response.headers.get("Content-Type", "")
                    if any(blocked_type in content_type for blocked_type in self.blocked_content_types):
                        response.close()
                        return {
                            "success": False,
                            "status_code": 415,
                            "content": None,
                            "error": f"不允许的内容类型: {content_type}",
                            "headers": dict(response.headers),
                            "url": response.url
                        }
                    
                    # 读取内容（限制大小）
                    content = b""
                    for chunk in response.iter_content(chunk_size=8192):
                        content += chunk
                        if len(content) > max_size_bytes:
                            response.close()
                            return {
                                "success": False,
                                "status_code": 413,
                                "content": None,
                                "error": f"响应大小超过限制: {len(content)} 字节",
                                "headers": dict(response.headers),
                                "url": response.url
                            }
                    
                    # 尝试解码内容
                    try:
                        text_content = content.decode("utf-8")
                    except UnicodeDecodeError:
                        text_content = None
                    
                    result = {
                        "success": response.status_code < 400,
                        "status_code": response.status_code,
                        "content": text_content,
                        "binary_content": content if text_content is None else None,
                        "headers": dict(response.headers),
                        "url": response.url
                    }
                    
                    # 缓存成功的GET请求
                    if method == "GET" and response.status_code < 400 and self.cache_enabled and use_cache:
                        self._save_to_cache(url, result)
                    
                    return result
                    
                except requests.exceptions.Timeout:
                    log.warning(f"请求超时 (尝试 {attempt+1}/{self.max_retries}): {url}")
                    if attempt == self.max_retries - 1:
                        return {
                            "success": False,
                            "status_code": 408,
                            "content": None,
                            "error": "请求超时",
                            "headers": {},
                            "url": url
                        }
                except requests.exceptions.ConnectionError:
                    log.warning(f"连接错误 (尝试 {attempt+1}/{self.max_retries}): {url}")
                    if attempt == self.max_retries - 1:
                        return {
                            "success": False,
                            "status_code": 503,
                            "content": None,
                            "error": "连接错误",
                            "headers": {},
                            "url": url
                        }
                
                # 重试前等待
                time.sleep(1)
                
        except Exception as e:
            log.error(f"请求失败: {url}, 错误: {str(e)}")
            return {
                "success": False,
                "status_code": 500,
                "content": None,
                "error": str(e),
                "headers": {},
                "url": url
            }
    
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送GET请求"""
        return self.request(url, method="GET", **kwargs)
    
    def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送POST请求"""
        return self.request(url, method="POST", **kwargs)
    
    def extract_content(self, url: str, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """
        从网页中提取内容
        
        Args:
            url: 网页URL
            selectors: CSS选择器字典，键为内容名称，值为CSS选择器
            
        Returns:
            Dict[str, Any]: 提取的内容
        """
        # 获取网页内容
        response = self.get(url)
        if not response["success"]:
            return {
                "success": False,
                "error": response.get("error", "请求失败"),
                "url": url
            }
        
        content = response["content"]
        if not content:
            return {
                "success": False,
                "error": "网页内容为空",
                "url": url
            }
        
        # 如果没有提供选择器，则返回完整内容
        if not selectors:
            return {
                "success": True,
                "content": content,
                "url": url
            }
        
        # 使用BeautifulSoup提取内容
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")
            
            result = {
                "success": True,
                "url": url,
                "extracted": {}
            }
            
            for name, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    # 如果找到多个元素，返回列表
                    if len(elements) > 1:
                        result["extracted"][name] = [elem.get_text().strip() for elem in elements]
                    else:
                        result["extracted"][name] = elements[0].get_text().strip()
                else:
                    result["extracted"][name] = None
            
            return result
            
        except ImportError:
            log.error("缺少BeautifulSoup库，无法提取内容")
            return {
                "success": False,
                "error": "缺少BeautifulSoup库，无法提取内容",
                "url": url
            }
        except Exception as e:
            log.error(f"提取内容失败: {url}, 错误: {str(e)}")
            return {
                "success": False,
                "error": f"提取内容失败: {str(e)}",
                "url": url
            }
    
    def _security_check(self, url: str, method: str) -> Dict[str, Any]:
        """
        安全检查
        
        Args:
            url: 请求URL
            method: 请求方法
            
        Returns:
            Dict[str, Any]: 检查结果，包含是否允许和原因
        """
        try:
            # 解析URL
            parsed_url = urllib.parse.urlparse(url)
            
            # 检查协议
            if parsed_url.scheme not in self.allowed_schemes:
                return {
                    "allowed": False,
                    "reason": f"不允许的协议: {parsed_url.scheme}"
                }
            
            # 检查域名
            domain = parsed_url.netloc.lower()
            if not any(domain.endswith(allowed_domain) for allowed_domain in self.allowed_domains):
                return {
                    "allowed": False,
                    "reason": f"不允许的域名: {domain}"
                }
            
            # 只允许GET和POST方法
            if method not in ["GET", "POST"]:
                return {
                    "allowed": False,
                    "reason": f"不允许的请求方法: {method}"
                }
            
            return {
                "allowed": True,
                "reason": "通过安全检查"
            }
            
        except Exception as e:
            log.error(f"安全检查失败: {url}, 错误: {str(e)}")
            return {
                "allowed": False,
                "reason": f"安全检查失败: {str(e)}"
            }
    
    def _generate_cache_key(self, url: str, method: str, 
                          headers: Dict[str, str], params: Dict[str, Any],
                          data: Any, json_data: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 创建包含请求信息的字典
        cache_info = {
            "url": url,
            "method": method,
            "headers": headers,
            "params": params,
            "data": data,
            "json": json_data
        }
        
        # 序列化并计算哈希值
        cache_str = json.dumps(cache_info, sort_keys=True, default=str)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _load_cache_index(self) -> None:
        """加载缓存索引"""
        index_file = self.cache_dir / "index.json"
        try:
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    index_data = json.load(f)
                    self.cache_index = index_data.get("index", {})
                    self.cache_keys = index_data.get("keys", [])
                    
                    # 验证缓存文件是否存在
                    valid_keys = []
                    for key in self.cache_keys:
                        cache_file = self.cache_dir / f"{key}.json"
                        if cache_file.exists():
                            valid_keys.append(key)
                    
                    self.cache_keys = valid_keys
                    self.cache_index = {k: v for k, v in self.cache_index.items() if k in valid_keys}
        except Exception as e:
            log.error(f"加载缓存索引失败: {str(e)}")
            self.cache_index = {}
            self.cache_keys = []
    
    def _save_cache_index(self) -> None:
        """保存缓存索引"""
        index_file = self.cache_dir / "index.json"
        try:
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump({
                    "index": self.cache_index,
                    "keys": self.cache_keys
                }, f)
        except Exception as e:
            log.error(f"保存缓存索引失败: {str(e)}")
    
    def close(self) -> None:
        """关闭网络代理"""
        # 停止缓存清理线程
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._stop_cleanup.set()
            self._cleanup_thread.join(timeout=1)
        
        # 关闭会话
        self.session.close()
        log.info("NetworkProxy closed")


# 创建单例实例
network_proxy = NetworkProxy()