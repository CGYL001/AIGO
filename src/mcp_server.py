import os
import sys
import json
import time
import logging
import threading
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
import uuid

from src.utils import config, logger
from src.modules.filesystem_analyzer import filesystem_analyzer
from src.modules.network_proxy import network_proxy
from src.modules.context_manager import context_manager
from src.services.model_manager import ModelManager


class MCPServer:
    """
    MCP服务器，作为编程IDE和AI模型之间的桥梁
    """
    
    def __init__(self):
        """初始化MCP服务器"""
        # 配置
        self.plugins_dir = Path(config.get("mcp_server.plugins_dir", "plugins"))
        self.api_host = config.get("mcp_server.api_host", "localhost")
        self.api_port = config.get("mcp_server.api_port", 8765)
        self.auth_enabled = config.get("mcp_server.auth_enabled", True)
        self.auth_token = config.get("mcp_server.auth_token", self._generate_auth_token())
        
        # 模块实例
        self.model_manager = ModelManager()
        
        # 插件系统
        self.plugins: Dict[str, Any] = {}
        self.plugin_routes: Dict[str, Callable] = {}
        
        # 会话管理
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # 创建插件目录
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # 加载插件
        self._load_plugins()
        
        logger.info("MCP服务器初始化完成")
    
    def start(self):
        """启动MCP服务器"""
        try:
            from flask import Flask, request, jsonify
            
            app = Flask("MCPServer")
            
            @app.route("/api/health", methods=["GET"])
            def health_check():
                """健康检查接口"""
                return jsonify({
                    "status": "ok",
                    "version": config.get("app.version", "0.1.0"),
                    "timestamp": time.time()
                })
            
            @app.route("/api/filesystem/scan", methods=["POST"])
            def scan_filesystem():
                """扫描文件系统"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                data = request.json
                directory = data.get("directory", ".")
                incremental = data.get("incremental", True)
                
                result = filesystem_analyzer.scan_directory(directory, incremental)
                return jsonify(result)
            
            @app.route("/api/filesystem/find", methods=["POST"])
            def find_files():
                """查找文件"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                data = request.json
                directory = data.get("directory", ".")
                pattern = data.get("pattern", "*")
                recursive = data.get("recursive", True)
                
                files = filesystem_analyzer.find_files(directory, pattern, recursive)
                return jsonify({"files": files})
            
            @app.route("/api/network/request", methods=["POST"])
            def network_request():
                """发送网络请求"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                data = request.json
                url = data.get("url")
                method = data.get("method", "GET")
                headers = data.get("headers")
                params = data.get("params")
                body = data.get("body")
                json_data = data.get("json")
                
                if not url:
                    return jsonify({"error": "缺少URL参数"}), 400
                
                result = network_proxy.request(
                    url=url,
                    method=method,
                    headers=headers,
                    params=params,
                    data=body,
                    json_data=json_data
                )
                
                return jsonify(result)
            
            @app.route("/api/context/create", methods=["POST"])
            def create_context():
                """创建上下文"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                data = request.json
                name = data.get("name")
                level = data.get("level", "file")
                content = data.get("content", "")
                metadata = data.get("metadata")
                
                if not name:
                    return jsonify({"error": "缺少名称参数"}), 400
                
                context_id = context_manager.create_context(
                    name=name,
                    level=level,
                    content=content,
                    metadata=metadata
                )
                
                return jsonify({
                    "context_id": context_id,
                    "name": name,
                    "level": level
                })
            
            @app.route("/api/context/get/<context_id>", methods=["GET"])
            def get_context(context_id):
                """获取上下文"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                context = context_manager.get_context(context_id)
                if not context:
                    return jsonify({"error": f"上下文不存在: {context_id}"}), 404
                
                return jsonify(context)
            
            @app.route("/api/context/update/<context_id>", methods=["POST"])
            def update_context(context_id):
                """更新上下文"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                data = request.json
                content = data.get("content")
                metadata = data.get("metadata")
                
                success = context_manager.update_context(
                    context_id=context_id,
                    content=content,
                    metadata=metadata
                )
                
                if not success:
                    return jsonify({"error": f"更新上下文失败: {context_id}"}), 404
                
                return jsonify({"success": True})
            
            @app.route("/api/context/search", methods=["POST"])
            def search_contexts():
                """搜索上下文"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                data = request.json
                query = data.get("query")
                level = data.get("level")
                metadata_filter = data.get("metadata_filter")
                
                contexts = context_manager.search_contexts(
                    query=query,
                    level=level,
                    metadata_filter=metadata_filter
                )
                
                return jsonify({"contexts": contexts})
            
            @app.route("/api/model/generate", methods=["POST"])
            def generate_text():
                """生成文本"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                data = request.json
                prompt = data.get("prompt")
                model = data.get("model")
                temperature = data.get("temperature")
                max_tokens = data.get("max_tokens")
                
                if not prompt:
                    return jsonify({"error": "缺少prompt参数"}), 400
                
                result = self.model_manager.generate(
                    prompt=prompt,
                    model_name=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return jsonify({"text": result})
            
            @app.route("/api/session/create", methods=["POST"])
            def create_session():
                """创建会话"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                data = request.json
                client_id = data.get("client_id")
                name = data.get("name", "未命名会话")
                metadata = data.get("metadata", {})
                
                if not client_id:
                    return jsonify({"error": "缺少client_id参数"}), 400
                
                # 创建会话
                session_id = str(uuid.uuid4())
                self.sessions[session_id] = {
                    "id": session_id,
                    "client_id": client_id,
                    "name": name,
                    "created_at": time.time(),
                    "last_active": time.time(),
                    "metadata": metadata
                }
                
                # 创建上下文会话
                context_id = context_manager.create_session(
                    name=name,
                    metadata={"client_id": client_id, "session_id": session_id}
                )
                
                self.sessions[session_id]["context_id"] = context_id
                
                return jsonify({
                    "session_id": session_id,
                    "name": name,
                    "context_id": context_id
                })
            
            @app.route("/api/session/<session_id>/ping", methods=["POST"])
            def ping_session(session_id):
                """更新会话活跃时间"""
                if not self._check_auth(request):
                    return jsonify({"error": "未授权"}), 401
                
                if session_id not in self.sessions:
                    return jsonify({"error": f"会话不存在: {session_id}"}), 404
                
                self.sessions[session_id]["last_active"] = time.time()
                return jsonify({"success": True})
            
            # 添加插件路由
            for route, handler in self.plugin_routes.items():
                app.route(route)(handler)
            
            # 启动服务器
            logger.info(f"MCP服务器启动，监听 {self.api_host}:{self.api_port}")
            app.run(host=self.api_host, port=self.api_port)
            
        except ImportError:
            logger.error("缺少Flask库，无法启动MCP服务器")
            raise
        except Exception as e:
            logger.error(f"启动MCP服务器失败: {str(e)}")
            raise
    
    def _check_auth(self, request):
        """检查请求认证"""
        if not self.auth_enabled:
            return True
        
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return False
        
        try:
            auth_type, token = auth_header.split(" ", 1)
            if auth_type.lower() != "bearer":
                return False
            
            return token == self.auth_token
        except Exception:
            return False
    
    def _generate_auth_token(self) -> str:
        """生成认证令牌"""
        token = config.get("mcp_server.auth_token")
        if token:
            return token
        
        # 生成随机令牌
        token = str(uuid.uuid4())
        logger.info(f"生成MCP服务器认证令牌: {token}")
        return token
    
    def _load_plugins(self):
        """加载插件"""
        if not self.plugins_dir.exists():
            return
        
        # 查找所有插件目录
        plugin_dirs = [d for d in self.plugins_dir.iterdir() if d.is_dir() and (d / "__init__.py").exists()]
        
        for plugin_dir in plugin_dirs:
            plugin_name = plugin_dir.name
            
            try:
                # 构建模块路径
                module_path = f"plugins.{plugin_name}"
                
                # 添加插件目录到Python路径
                if str(self.plugins_dir.parent) not in sys.path:
                    sys.path.insert(0, str(self.plugins_dir.parent))
                
                # 导入插件模块
                plugin_module = importlib.import_module(module_path)
                
                # 检查插件是否有register函数
                if hasattr(plugin_module, "register"):
                    # 注册插件
                    plugin_info = plugin_module.register(self)
                    self.plugins[plugin_name] = plugin_info
                    logger.info(f"加载插件: {plugin_name}")
                else:
                    logger.warning(f"插件缺少register函数: {plugin_name}")
                
            except Exception as e:
                logger.error(f"加载插件失败: {plugin_name}, 错误: {str(e)}")
    
    def register_route(self, route: str, handler: Callable):
        """注册API路由"""
        if route in self.plugin_routes:
            logger.warning(f"路由已存在，将被覆盖: {route}")
        
        self.plugin_routes[route] = handler
        logger.debug(f"注册路由: {route}")


# 创建单例实例
mcp_server = MCPServer() 