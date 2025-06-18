import os
import json
import time
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify, Response, stream_with_context

from src.utils import config, logger
from src.mcp_server import mcp_server
from src.modules.filesystem_analyzer import filesystem_analyzer
from src.modules.network_proxy import network_proxy
from src.modules.context_manager import context_manager


# 创建Blueprint
mcp_api = Blueprint('mcp_api', __name__)


@mcp_api.route('/mcp/version', methods=['GET'])
def get_version():
    """获取MCP版本信息"""
    return jsonify({
        "version": config.get("app.version", "0.1.0"),
        "name": config.get("app.name", "MCP"),
        "api_version": "1.0.0"
    })


@mcp_api.route('/mcp/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "timestamp": time.time()
    })


@mcp_api.route('/mcp/filesystem/scan', methods=['POST'])
def scan_filesystem():
    """扫描文件系统"""
    data = request.json
    directory = data.get("directory", ".")
    incremental = data.get("incremental", True)
    
    result = filesystem_analyzer.scan_directory(directory, incremental)
    return jsonify(result)


@mcp_api.route('/mcp/filesystem/find', methods=['POST'])
def find_files():
    """查找文件"""
    data = request.json
    directory = data.get("directory", ".")
    pattern = data.get("pattern", "*")
    recursive = data.get("recursive", True)
    
    files = filesystem_analyzer.find_files(directory, pattern, recursive)
    return jsonify({"files": files})


@mcp_api.route('/mcp/filesystem/info', methods=['POST'])
def get_file_info():
    """获取文件信息"""
    data = request.json
    file_path = data.get("file_path")
    
    if not file_path:
        return jsonify({"error": "缺少file_path参数"}), 400
    
    file_info = filesystem_analyzer.get_file_info(file_path)
    if not file_info:
        return jsonify({"error": f"文件不存在或无法访问: {file_path}"}), 404
    
    return jsonify(file_info)


@mcp_api.route('/mcp/network/request', methods=['POST'])
def network_request():
    """发送网络请求"""
    data = request.json
    url = data.get("url")
    method = data.get("method", "GET")
    headers = data.get("headers")
    params = data.get("params")
    body = data.get("body")
    json_data = data.get("json")
    use_cache = data.get("use_cache", True)
    
    if not url:
        return jsonify({"error": "缺少URL参数"}), 400
    
    result = network_proxy.request(
        url=url,
        method=method,
        headers=headers,
        params=params,
        data=body,
        json_data=json_data,
        use_cache=use_cache
    )
    
    return jsonify(result)


@mcp_api.route('/mcp/network/extract', methods=['POST'])
def extract_content():
    """从网页提取内容"""
    data = request.json
    url = data.get("url")
    selectors = data.get("selectors")
    
    if not url:
        return jsonify({"error": "缺少URL参数"}), 400
    
    result = network_proxy.extract_content(url, selectors)
    return jsonify(result)


@mcp_api.route('/mcp/context/create', methods=['POST'])
def create_context():
    """创建上下文"""
    data = request.json
    name = data.get("name")
    level = data.get("level", "file")
    content = data.get("content", "")
    metadata = data.get("metadata")
    
    if not name:
        return jsonify({"error": "缺少name参数"}), 400
    
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


@mcp_api.route('/mcp/context/<context_id>', methods=['GET'])
def get_context(context_id):
    """获取上下文"""
    context = context_manager.get_context(context_id)
    if not context:
        return jsonify({"error": f"上下文不存在: {context_id}"}), 404
    
    return jsonify(context)


@mcp_api.route('/mcp/context/<context_id>', methods=['PUT'])
def update_context(context_id):
    """更新上下文"""
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


@mcp_api.route('/mcp/context/<context_id>', methods=['DELETE'])
def delete_context(context_id):
    """删除上下文"""
    success = context_manager.delete_context(context_id)
    if not success:
        return jsonify({"error": f"删除上下文失败: {context_id}"}), 404
    
    return jsonify({"success": True})


@mcp_api.route('/mcp/context/search', methods=['POST'])
def search_contexts():
    """搜索上下文"""
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


@mcp_api.route('/mcp/context/compress/<context_id>', methods=['POST'])
def compress_context(context_id):
    """压缩上下文"""
    data = request.json
    max_length = data.get("max_length")
    
    success = context_manager.compress_context(
        context_id=context_id,
        max_length=max_length
    )
    
    if not success:
        return jsonify({"error": f"压缩上下文失败: {context_id}"}), 404
    
    return jsonify({"success": True})


@mcp_api.route('/mcp/context/merge', methods=['POST'])
def merge_contexts():
    """合并上下文"""
    data = request.json
    context_ids = data.get("context_ids", [])
    name = data.get("name")
    level = data.get("level", "file")
    
    if not context_ids:
        return jsonify({"error": "缺少context_ids参数"}), 400
    
    if not name:
        return jsonify({"error": "缺少name参数"}), 400
    
    merged_id = context_manager.merge_contexts(
        context_ids=context_ids,
        name=name,
        level=level
    )
    
    if not merged_id:
        return jsonify({"error": "合并上下文失败"}), 400
    
    return jsonify({
        "context_id": merged_id,
        "name": name,
        "level": level
    })


@mcp_api.route('/mcp/session/create', methods=['POST'])
def create_session():
    """创建会话"""
    data = request.json
    name = data.get("name", "未命名会话")
    metadata = data.get("metadata", {})
    
    session_id = context_manager.create_session(
        name=name,
        metadata=metadata
    )
    
    return jsonify({
        "session_id": session_id,
        "name": name
    })


@mcp_api.route('/mcp/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取会话"""
    session = context_manager.get_session(session_id)
    if not session:
        return jsonify({"error": f"会话不存在: {session_id}"}), 404
    
    return jsonify(session)


@mcp_api.route('/mcp/session/<session_id>/contexts', methods=['GET'])
def get_session_contexts(session_id):
    """获取会话中的上下文"""
    contexts = context_manager.get_session_contexts(session_id)
    return jsonify({"contexts": contexts})


@mcp_api.route('/mcp/session/<session_id>/add/<context_id>', methods=['POST'])
def add_context_to_session(session_id, context_id):
    """将上下文添加到会话"""
    success = context_manager.add_context_to_session(session_id, context_id)
    if not success:
        return jsonify({"error": f"添加上下文到会话失败: {context_id} -> {session_id}"}), 404
    
    return jsonify({"success": True})


@mcp_api.route('/mcp/session/<session_id>/remove/<context_id>', methods=['POST'])
def remove_context_from_session(session_id, context_id):
    """从会话中移除上下文"""
    success = context_manager.remove_context_from_session(session_id, context_id)
    if not success:
        return jsonify({"error": f"从会话中移除上下文失败: {context_id} -> {session_id}"}), 404
    
    return jsonify({"success": True})


@mcp_api.route('/mcp/model/generate', methods=['POST'])
def generate_text():
    """生成文本"""
    data = request.json
    prompt = data.get("prompt")
    model_name = data.get("model")
    temperature = data.get("temperature")
    max_tokens = data.get("max_tokens")
    system_message = data.get("system_message")
    
    if not prompt:
        return jsonify({"error": "缺少prompt参数"}), 400
    
    result = mcp_server.model_manager.generate(
        prompt=prompt,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        system_message=system_message
    )
    
    return jsonify({"text": result})


@mcp_api.route('/mcp/model/generate_stream', methods=['POST'])
def generate_text_stream():
    """流式生成文本"""
    data = request.json
    prompt = data.get("prompt")
    model_name = data.get("model")
    temperature = data.get("temperature")
    max_tokens = data.get("max_tokens")
    system_message = data.get("system_message")
    
    if not prompt:
        return jsonify({"error": "缺少prompt参数"}), 400
    
    def generate():
        for token in mcp_server.model_manager.generate_stream(
            prompt=prompt,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            system_message=system_message
        ):
            yield json.dumps({"token": token}) + "\n"
    
    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')


@mcp_api.route('/mcp/model/embed', methods=['POST'])
def embed_text():
    """生成文本嵌入向量"""
    data = request.json
    texts = data.get("texts")
    model_name = data.get("model")
    
    if not texts:
        return jsonify({"error": "缺少texts参数"}), 400
    
    # 确保texts是列表
    if isinstance(texts, str):
        texts = [texts]
    
    embeddings = mcp_server.model_manager.embed(
        texts=texts,
        model_name=model_name
    )
    
    return jsonify({"embeddings": embeddings})


def register_mcp_api(app):
    """注册MCP API到Flask应用"""
    app.register_blueprint(mcp_api, url_prefix='/api')
    logger.info("已注册MCP API") 