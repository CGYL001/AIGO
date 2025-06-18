# AIgo与Cursor集成设置指南

本指南将帮助你将AIgo智能代码助手配置到Cursor IDE中，以增强其AI编程能力。

## 第1步：安装AIgo服务器

首先，确保你已经安装并运行了AIgo服务器：

1. 克隆AIgo仓库（如果尚未克隆）
   ```bash
   git clone https://github.com/your-username/AIgo.git
   cd AIgo
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 启动AIgo服务器
   ```bash
   python run.py
   ```

服务器默认运行在`http://localhost:8080`。

## 第2步：构建Cursor扩展

接下来，构建Cursor扩展：

1. 进入Cursor扩展目录
   ```bash
   cd examples/ide_integration/cursor_extension
   ```

2. 安装Node.js依赖
   ```bash
   npm install
   ```

3. 构建扩展
   ```bash
   npm run build
   ```

4. 打包扩展
   ```bash
   npm run package
   ```

这将生成一个`aigo-cursor-extension-0.1.0.vsix`文件。

## 第3步：在Cursor中安装扩展

1. 打开Cursor IDE
2. 按下`Ctrl+Shift+X`打开扩展视图
3. 点击右上角的"..."按钮
4. 选择"从VSIX安装..."
5. 浏览并选择刚刚生成的`.vsix`文件

## 第4步：配置扩展

安装扩展后，配置它以连接到AIgo服务器：

1. 打开Cursor设置（`Ctrl+,`）
2. 搜索"AIgo"
3. 设置以下选项：
   - `aigo.server.url`: 设置为`http://localhost:8080/api`（或你的自定义服务器URL）
   - `aigo.server.authToken`: 如果你的服务器需要认证，请设置认证令牌
   - `aigo.aiAssistant.enhancedContext`: 设置为`true`以启用增强上下文
   - `aigo.aiAssistant.networkAccess`: 设置为`true`以允许网络访问
   - `aigo.aiAssistant.localModels`: 如果你有本地模型，设置为`true`

## 第5步：连接到AIgo服务器

1. 按下`F1`打开命令面板
2. 输入"AIgo: 连接到服务器"并执行
3. 如果连接成功，你将看到一条成功消息

## 第6步：使用增强的AI助手

现在，你可以使用增强的AI助手功能：

1. **扫描项目**：使用命令面板中的"AIgo: 扫描项目"命令，让AI助手了解你的项目结构
2. **创建上下文**：打开一个文件，然后使用"AIgo: 创建上下文"命令，将该文件添加到AI助手的上下文中
3. **使用本地模型**：如果你有本地模型，可以使用"AIgo: 使用本地模型"命令切换到本地模型
4. **查看记忆**：使用"AIgo: 查看记忆"命令查看AI助手的记忆

## 提示与技巧

- 在使用AI助手之前，先扫描项目，让它了解你的代码库
- 对于复杂的代码生成任务，先将相关文件添加到上下文中
- 如果遇到网络问题，可以切换到本地模型（如果可用）
- 定期查看记忆，了解AI助手记住了哪些内容

## 故障排除

如果遇到问题：

1. 确保AIgo服务器正在运行
2. 检查服务器URL配置是否正确
3. 查看Cursor开发者工具中的控制台日志（`Ctrl+Shift+I`）
4. 尝试重新连接服务器
5. 重启Cursor IDE

如需更多帮助，请参阅AIgo文档或提交问题。
