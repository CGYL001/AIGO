MCP API参考
==========

概述
----

MCP (Model Communication Protocol) API是AIgo的核心接口，提供与AI模型交互的能力。通过MCP API，你可以发送请求给AI模型、接收回复、获取上下文信息等。

基础端点
-------

.. http:post:: /api/v1/mcp/completion

   发送补全请求给AI模型，获取模型回复。

   **请求示例:**

   .. sourcecode:: http

      POST /api/v1/mcp/completion HTTP/1.1
      Host: localhost:8000
      Content-Type: application/json
      Authorization: Bearer {token}
      
      {
        "prompt": "def fibonacci(n):",
        "model": "gpt-3.5-turbo", 
        "max_tokens": 150,
        "temperature": 0.7,
        "context": {
          "language": "python",
          "file_type": ".py",
          "current_file": "math_utils.py"
        }
      }

   **参数说明:**

   :<json string prompt: 发送给模型的提示文本
   :<json string model: 要使用的模型名称
   :<json integer max_tokens: (可选) 回复的最大令牌数
   :<json float temperature: (可选) 模型温度，控制随机性 (0.0-1.0)
   :<json object context: (可选) 上下文信息

   **响应示例:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json
      
      {
        "completion": "def fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
        "model": "gpt-3.5-turbo",
        "usage": {
          "prompt_tokens": 6,
          "completion_tokens": 79,
          "total_tokens": 85
        }
      }

   :>json string completion: 模型生成的补全文本
   :>json string model: 使用的模型名称
   :>json object usage: 令牌使用情况

   :statuscode 200: 请求成功
   :statuscode 400: 请求参数无效
   :statuscode 401: 未授权访问
   :statuscode 500: 服务器错误

流式补全
-------

.. http:post:: /api/v1/mcp/stream_completion

   以流式方式发送补全请求，逐步接收模型回复。

   **请求示例:**

   .. sourcecode:: http

      POST /api/v1/mcp/stream_completion HTTP/1.1
      Host: localhost:8000
      Content-Type: application/json
      Authorization: Bearer {token}
      
      {
        "prompt": "解释什么是递归算法",
        "model": "gpt-3.5-turbo",
        "stream": true,
        "temperature": 0.7
      }

   **参数说明:**

   :<json string prompt: 发送给模型的提示文本
   :<json string model: 要使用的模型名称
   :<json boolean stream: 必须为true
   :<json float temperature: (可选) 模型温度 (0.0-1.0)

   **响应:**

   服务器发送的是一系列事件流 (Server-Sent Events)，每个事件包含部分完成的文本：

   .. sourcecode:: text

      event: completion
      data: {"text": "递归算法是", "finish_reason": null}
      
      event: completion
      data: {"text": "一种通过", "finish_reason": null}
      
      event: completion
      data: {"text": "调用函数自身", "finish_reason": null}
      
      // ... 更多事件 ...
      
      event: completion
      data: {"text": "。", "finish_reason": "stop"}
      
      event: done
      data: {"usage": {"prompt_tokens": 8, "completion_tokens": 120, "total_tokens": 128}}

上下文管理
--------

.. http:post:: /api/v1/mcp/context

   更新或获取当前对话的上下文信息。

   **获取上下文 (GET):**

   .. sourcecode:: http

      GET /api/v1/mcp/context?session_id=abc123 HTTP/1.1
      Host: localhost:8000
      Authorization: Bearer {token}

   **更新上下文 (POST):**

   .. sourcecode:: http

      POST /api/v1/mcp/context HTTP/1.1
      Host: localhost:8000
      Content-Type: application/json
      Authorization: Bearer {token}
      
      {
        "session_id": "abc123",
        "context": {
          "language": "javascript",
          "file_type": ".js",
          "current_file": "app.js",
          "project_type": "web",
          "additional_info": {
            "framework": "react"
          }
        }
      }

   **参数说明:**

   :<json string session_id: 会话ID
   :<json object context: 要更新的上下文信息

对话历史
-------

.. http:get:: /api/v1/mcp/history/(session_id)

   获取指定会话的对话历史记录。

   **请求示例:**

   .. sourcecode:: http

      GET /api/v1/mcp/history/abc123 HTTP/1.1
      Host: localhost:8000
      Authorization: Bearer {token}

   **响应示例:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json
      
      {
        "session_id": "abc123",
        "messages": [
          {
            "role": "user",
            "content": "如何使用JavaScript实现一个简单的计数器?",
            "timestamp": "2023-06-15T10:30:45Z"
          },
          {
            "role": "assistant",
            "content": "你可以这样实现一个简单的JavaScript计数器:\n\n```javascript\nlet count = 0;\n\nfunction increment() {\n  count++;\n  document.getElementById('counter').innerText = count;\n}\n\nfunction decrement() {\n  count--;\n  document.getElementById('counter').innerText = count;\n}\n```\n\n在HTML中，你需要这样使用:\n\n```html\n<div id=\"counter\">0</div>\n<button onclick=\"increment()\">+</button>\n<button onclick=\"decrement()\">-</button>\n```",
            "timestamp": "2023-06-15T10:30:48Z"
          }
        ]
      }

   :>json string session_id: 会话ID
   :>json array messages: 对话消息数组

   :statuscode 200: 请求成功
   :statuscode 404: 会话不存在
   :statuscode 401: 未授权访问

模型评估
-------

.. http:post:: /api/v1/mcp/evaluate

   评估模型的响应质量。

   **请求示例:**

   .. sourcecode:: http

      POST /api/v1/mcp/evaluate HTTP/1.1
      Host: localhost:8000
      Content-Type: application/json
      Authorization: Bearer {token}
      
      {
        "prompt": "写一个二分查找算法",
        "completion": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
        "criteria": ["correctness", "efficiency", "readability"],
        "reference": "标准二分查找实现"
      }

   **参数说明:**

   :<json string prompt: 原始提示
   :<json string completion: 要评估的补全文本
   :<json array criteria: (可选) 评估标准
   :<json string reference: (可选) 参考实现或描述

   **响应示例:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json
      
      {
        "scores": {
          "overall": 0.92,
          "correctness": 0.95,
          "efficiency": 0.9,
          "readability": 0.91
        },
        "feedback": "代码正确实现了二分查找算法，时间复杂度为O(log n)。代码结构清晰，变量命名合理。可以考虑添加函数文档字符串和边界条件检查。"
      }

   :>json object scores: 不同维度的评分
   :>json string feedback: 详细的评估反馈

WebSocket API
-----------

除了HTTP API外，MCP还提供WebSocket接口用于实时交互：

WebSocket端点: ``ws://localhost:8000/ws/mcp/{session_id}``

**连接示例:**

.. sourcecode:: javascript

    // 客户端JavaScript代码
    const ws = new WebSocket(`ws://localhost:8000/ws/mcp/abc123?token=${jwt_token}`);
    
    ws.onopen = () => {
      console.log('Connected to MCP WebSocket');
      // 发送请求
      ws.send(JSON.stringify({
        type: 'completion',
        data: {
          prompt: 'def sort_array(arr):',
          model: 'gpt-3.5-turbo'
        }
      }));
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'completion') {
        console.log('Received completion chunk:', message.data.text);
      }
    };

**消息类型:**

1. **completion** - 代码补全请求和响应
2. **context_update** - 上下文更新
3. **error** - 错误消息
4. **system** - 系统消息 