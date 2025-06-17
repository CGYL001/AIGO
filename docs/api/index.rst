API参考文档
===========

AIgo提供多种API接口，支持与外部应用集成、扩展功能。本文档详细说明了API的使用方法、参数选项和响应格式。

REST API
--------

AIgo提供了RESTful API，可以通过HTTP访问系统的核心功能。API遵循REST设计原则，使用标准的HTTP方法和状态码。

认证
^^^^

大多数API调用都需要认证，我们支持两种认证方式：

1. **API密钥认证** - 在请求头中添加 ``X-API-Key`` 字段
2. **JWT令牌认证** - 在请求头中添加 ``Authorization: Bearer {token}`` 字段

请求示例:

.. code-block:: bash

    # 使用API密钥
    curl -X GET "http://localhost:8000/api/v1/models" \
         -H "X-API-Key: your_api_key"
    
    # 使用JWT令牌
    curl -X GET "http://localhost:8000/api/v1/models" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

错误处理
^^^^^^^

API使用标准的HTTP状态码表示请求结果，同时在响应体中提供详细的错误信息。

.. list-table::
   :widths: 15 70
   :header-rows: 1

   * - 状态码
     - 说明
   * - 200
     - 请求成功
   * - 201
     - 资源创建成功
   * - 400
     - 请求无效，通常是缺少参数或参数类型错误
   * - 401
     - 未认证或认证失败
   * - 403
     - 无权限访问该资源
   * - 404
     - 资源不存在
   * - 500
     - 服务器内部错误

错误响应格式:

.. code-block:: json

    {
      "error": "错误类型",
      "message": "详细错误信息",
      "details": {
        "字段名": ["具体错误信息"]
      }
    }

API端点
^^^^^^^

.. toctree::
   :maxdepth: 2
   
   mcp_api
   auth
   models
   preferences
   repository
   
WebSocket API
------------

AIgo同时提供了WebSocket API，用于实时交互和流式处理。

连接
^^^^

通过以下URL连接WebSocket服务:

``ws://localhost:8000/ws/{session_id}``

需要在URL参数中提供认证信息:

``ws://localhost:8000/ws/{session_id}?token=your_jwt_token``

消息格式
^^^^^^^

WebSocket消息使用JSON格式传输:

.. code-block:: json

    {
      "type": "message_type",
      "data": {
        "content": "消息内容",
        "additional_fields": "其他字段"
      }
    }

事件类型
^^^^^^^

.. list-table::
   :widths: 20 60
   :header-rows: 1

   * - 事件类型
     - 说明
   * - completion
     - 代码补全请求/响应
   * - context_update
     - 上下文更新通知
   * - error
     - 错误信息
   * - system
     - 系统消息 