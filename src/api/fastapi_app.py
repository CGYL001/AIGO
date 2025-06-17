"""
AIgo FastAPI应用 - 提供现代化HTTP API和自动文档生成
"""

import os
import json
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, Depends, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.services.model_service import ModelService
from src.services.auth_service import AuthService, get_current_user
from src.api.mcp_api import MCPService

# 初始化日志
logger = setup_logger(__name__)

# 配置
config = load_config()
api_config = config.get("api", {})
api_version = api_config.get("version", "v1")
debug_mode = api_config.get("debug", False)

# 初始化FastAPI应用
app = FastAPI(
    title="AIgo API",
    description="AIgo智能编程助手API",
    version=api_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url=f"/api/openapi.json",
    debug=debug_mode
)

# 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=api_config.get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/{api_version}/auth/token")
api_key_header = APIKeyHeader(name="X-API-Key")

# 初始化服务
model_service = ModelService(config=config)
auth_service = AuthService(config=config)
mcp_service = MCPService(model_service)

# 数据模型
class CompletionRequest(BaseModel):
    prompt: str = Field(..., description="发送给模型的提示文本")
    model: str = Field(..., description="要使用的模型名称")
    max_tokens: Optional[int] = Field(None, description="回复的最大令牌数")
    temperature: Optional[float] = Field(0.7, description="模型温度，控制随机性(0.0-1.0)")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")

class CompletionResponse(BaseModel):
    completion: str = Field(..., description="模型生成的补全文本")
    model: str = Field(..., description="使用的模型名称")
    usage: Dict[str, Any] = Field(..., description="令牌使用情况")

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

# 辅助函数
async def get_auth_token(
    token: str = Depends(oauth2_scheme), 
    api_key: Optional[str] = Depends(api_key_header)
) -> str:
    """获取认证令牌，支持JWT或API密钥"""
    if token:
        return token
    elif api_key:
        return api_key
    raise HTTPException(
        status_code=401,
        detail="需要认证",
        headers={"WWW-Authenticate": "Bearer"},
    )

# 路由定义
@app.get("/api/health")
async def health_check():
    """API健康检查端点"""
    return {"status": "healthy", "version": api_version}

@app.post(
    f"/api/{api_version}/mcp/completion", 
    response_model=CompletionResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        400: {"model": ErrorResponse, "description": "无效请求"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
    tags=["MCP API"],
    summary="获取模型补全回复",
    description="发送补全请求给AI模型，获取模型回复"
)
async def completion(
    request: CompletionRequest,
    current_user: Dict = Depends(get_current_user),
):
    """发送补全请求给AI模型，获取模型回复"""
    try:
        result = await mcp_service.get_completion(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            context=request.context,
            user_id=current_user.get("id", "anonymous")
        )
        return result
    except Exception as e:
        logger.error(f"Completion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "completion_failed", "message": f"补全请求失败: {str(e)}"}
        )

@app.get(
    f"/api/{api_version}/models",
    tags=["Models"],
    summary="获取可用模型列表",
    description="获取当前可用的AI模型列表及其配置"
)
async def get_models(
    current_user: Dict = Depends(get_current_user),
):
    """获取可用模型列表"""
    try:
        models = model_service.get_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "models_retrieval_failed", "message": f"获取模型列表失败: {str(e)}"}
        )

@app.post(
    f"/api/{api_version}/mcp/context",
    tags=["MCP API"],
    summary="更新会话上下文",
    description="更新或创建指定会话的上下文信息"
)
async def update_context(
    session_id: str,
    context: Dict[str, Any] = Body(...),
    current_user: Dict = Depends(get_current_user),
):
    """更新会话上下文"""
    try:
        updated_context = await mcp_service.update_context(
            session_id, 
            context, 
            user_id=current_user.get("id", "anonymous")
        )
        return {"session_id": session_id, "context": updated_context}
    except Exception as e:
        logger.error(f"Context update error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "context_update_failed", "message": f"上下文更新失败: {str(e)}"}
        )

@app.get(
    f"/api/{api_version}/mcp/context",
    tags=["MCP API"],
    summary="获取会话上下文",
    description="获取指定会话的当前上下文信息"
)
async def get_context(
    session_id: str,
    current_user: Dict = Depends(get_current_user),
):
    """获取会话上下文"""
    try:
        context = await mcp_service.get_context(
            session_id, 
            user_id=current_user.get("id", "anonymous")
        )
        if not context:
            raise HTTPException(
                status_code=404,
                detail={"error": "context_not_found", "message": f"未找到会话ID: {session_id}的上下文"}
            )
        return {"session_id": session_id, "context": context}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Context retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "context_retrieval_failed", "message": f"上下文获取失败: {str(e)}"}
        )

def get_fastapi_app():
    """获取配置好的FastAPI应用实例"""
    return app

if __name__ == "__main__":
    import uvicorn
    port = api_config.get("port", 8000)
    host = api_config.get("host", "127.0.0.1")
    uvicorn.run(app, host=host, port=port) 