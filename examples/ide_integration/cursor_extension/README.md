# MCP Cursor Extension

这是一个Cursor编辑器扩展示例，用于演示如何将MCP系统集成到Cursor中，增强AI编程助手的能力。

## 功能

- 增强文件系统理解：提供项目结构的语义分析
- 安全网络访问：允许AI助手安全地获取网络资源
- 上下文管理：提供多层次上下文记忆
- 本地模型调用：使用本地部署的模型减少API调用

## 安装

1. 确保已安装MCP服务器并正在运行
2. 安装此扩展：
   - 从Cursor扩展市场安装
   - 或者手动安装开发版本

## 配置

在Cursor设置中配置MCP扩展：

```json
{
  "mcp.server.url": "http://localhost:8765/api",
  "mcp.server.authToken": "your_auth_token",
  "mcp.aiAssistant.enhancedContext": true,
  "mcp.aiAssistant.networkAccess": true,
  "mcp.aiAssistant.localModels": true
}
```

## 使用方法

### 增强AI助手

安装扩展后，Cursor的AI助手将自动获得以下增强能力：

1. **更好的项目理解**：AI助手能够理解项目的整体结构和文件之间的关系
2. **网络访问**：AI助手可以查询文档、搜索信息和获取API参考
3. **长期记忆**：AI助手可以记住之前的对话和上下文
4. **本地模型**：使用本地部署的模型减少API调用和延迟

### 命令

在命令面板中可以使用以下命令：

- `MCP: 扫描项目` - 分析当前项目结构
- `MCP: 创建上下文` - 将当前文件添加到上下文
- `MCP: 使用本地模型` - 切换到本地模型
- `MCP: 查看记忆` - 查看AI助手的记忆

## 与AI助手交互

可以使用以下提示让AI助手使用MCP功能：

- "分析这个项目的结构"
- "搜索关于X的文档"
- "记住这段代码，稍后我们会用到"
- "使用本地模型生成代码"

## 开发

### 前提条件

- Node.js 14+
- Cursor扩展开发环境
- 运行中的MCP服务器

### 构建

```bash
# 安装依赖
npm install

# 编译
npm run build

# 打包
npm run package
```

### 调试

1. 在开发模式下启动Cursor
2. 加载未打包的扩展
3. 查看开发者控制台日志

## API集成

扩展通过HTTP API与MCP服务器通信，主要使用以下端点：

- `/mcp/filesystem/scan` - 扫描文件系统
- `/mcp/network/request` - 发送网络请求
- `/mcp/context/create` - 创建上下文
- `/mcp/model/generate` - 生成文本

## 与其他扩展的区别

与VSCode扩展相比，Cursor扩展更加注重AI助手的增强：

- 更深度集成到AI助手的工作流程中
- 提供更多AI相关的功能
- 专注于提高AI编程助手的效率

## 许可证

MIT 