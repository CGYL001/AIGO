import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

def launch_ui(port: int = 8080, 
             kb=None, 
             code_completion=None, 
             error_checker=None, 
             code_analyzer=None) -> None:
    """
    启动Web UI界面
    
    Args:
        port: 服务端口
        kb: 知识库实例
        code_completion: 代码补全实例
        error_checker: 错误检查实例
        code_analyzer: 代码分析实例
    """
    print(f"正在启动UI界面，端口：{port}")
    print("Web界面: http://localhost:{port}")
    print("可用模块:")
    if kb:
        print("  - 知识库")
    if code_completion:
        print("  - 代码补全")
    if error_checker:
        print("  - 错误检查")
    if code_analyzer:
        print("  - 代码分析")
    
    # 实际项目中，这里会启动Flask或FastAPI服务器
    print("在实际实现中，将在此处启动Web服务器")
    print("按Ctrl+C停止服务...")
    
    try:
        # 模拟服务器运行
        while True:
            pass
    except KeyboardInterrupt:
        print("\n服务已停止")

def render_template(template_name: str, **context) -> str:
    """
    渲染HTML模板
    
    Args:
        template_name: 模板名称
        **context: 模板上下文数据
        
    Returns:
        str: 渲染后的HTML
    """
    # 实际实现会使用Jinja2或其他模板引擎
    return f"<html><body><h1>CodeAssistant - {template_name}</h1></body></html>"
    
def get_static_url(filename: str) -> str:
    """
    获取静态资源URL
    
    Args:
        filename: 静态文件名
        
    Returns:
        str: 静态资源URL
    """
    return f"/static/{filename}"
    
def create_api_response(data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
    """
    创建API响应格式
    
    Args:
        data: 响应数据
        success: 是否成功
        message: 响应消息
        
    Returns:
        Dict[str, Any]: 格式化的API响应
    """
    return {
        "success": success,
        "message": message,
        "data": data
    } 