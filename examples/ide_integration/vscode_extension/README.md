# MCP VSCode Extension

这是一个VSCode扩展示例，用于演示如何将MCP系统集成到VSCode编辑器中。

## 功能

- 文件系统分析：扫描和分析项目结构
- 网络访问：安全地访问网络资源
- 上下文管理：管理代码上下文和记忆
- 模型调用：调用本地或远程AI模型

## 安装

1. 确保已安装MCP服务器并正在运行
2. 安装此扩展：
   - 从VSCode扩展市场安装
   - 或者使用VSIX文件手动安装

## 配置

在VSCode设置中配置MCP扩展：

```json
{
  "mcp.server.url": "http://localhost:8765/api",
  "mcp.server.authToken": "your_auth_token",
  "mcp.features.fileAnalysis": true,
  "mcp.features.networkAccess": true,
  "mcp.features.contextManagement": true
}
```

## 使用方法

1. 打开命令面板（Ctrl+Shift+P）
2. 输入"MCP:"可以看到所有可用命令
3. 选择需要的功能执行

### 文件系统分析

使用"MCP: 分析项目结构"命令扫描当前项目，分析文件之间的关系。

### 网络访问

使用"MCP: 网络请求"命令发送网络请求，获取外部资源。

### 上下文管理

使用"MCP: 创建上下文"命令将当前文件或选中的代码添加到上下文中。

### 模型调用

使用"MCP: 生成代码"命令调用AI模型生成代码。

## 开发

### 前提条件

- Node.js 14+
- VSCode扩展开发环境
- 运行中的MCP服务器

### 构建

```bash
# 安装依赖
npm install

# 编译
npm run compile

# 打包
npm run package
```

### 调试

1. 在VSCode中打开此项目
2. 按F5启动调试会话
3. 在新的VSCode窗口中测试扩展

## API集成

扩展通过HTTP API与MCP服务器通信，主要使用以下端点：

- `/mcp/filesystem/scan` - 扫描文件系统
- `/mcp/network/request` - 发送网络请求
- `/mcp/context/create` - 创建上下文
- `/mcp/model/generate` - 生成文本

## 许可证

MIT 