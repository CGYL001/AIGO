# AIgo Cursor扩展安装指南

本文档将指导您如何将AIgo扩展安装到Cursor IDE中。

## 前提条件

1. 已安装Cursor IDE
2. 已安装并运行AIgo服务器
3. Node.js 14.0+和npm 6.0+

## 安装步骤

### 方法1：从源代码构建

1. 克隆AIgo仓库（如果尚未克隆）
   ```bash
   git clone https://github.com/your-username/AIgo.git
   cd AIgo
   ```

2. 进入Cursor扩展目录
   ```bash
   cd examples/ide_integration/cursor_extension
   ```

3. 安装依赖
   ```bash
   npm install
   ```

4. 构建扩展
   ```bash
   npm run build
   ```

5. 打包扩展
   ```bash
   npm run package
   ```
   这将生成一个`.vsix`文件。

6. 在Cursor中安装扩展
   - 打开Cursor IDE
   - 按下`Ctrl+Shift+X`打开扩展视图
   - 点击右上角的"..."按钮
   - 选择"从VSIX安装..."
   - 浏览并选择刚刚生成的`.vsix`文件

### 方法2：使用开发模式

1. 进入Cursor扩展目录
   ```bash
   cd examples/ide_integration/cursor_extension
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 在Cursor中以开发模式加载扩展
   - 打开Cursor IDE
   - 按下`F1`打开命令面板
   - 输入并选择"Developer: Open Extension Folder"
   - 选择AIgo扩展目录

## 配置扩展

安装扩展后，您需要配置它以连接到AIgo服务器：

1. 打开Cursor设置（`Ctrl+,`）
2. 搜索"AIgo"
3. 设置以下选项：
   - `aigo.server.url`: AIgo服务器的URL（默认为`http://localhost:8080/api`）
   - `aigo.server.authToken`: 认证令牌（如果需要）
   - `aigo.aiAssistant.enhancedContext`: 是否启用增强上下文（建议启用）
   - `aigo.aiAssistant.networkAccess`: 是否允许网络访问（建议启用）
   - `aigo.aiAssistant.localModels`: 是否使用本地模型（如果有可用的本地模型）

## 验证安装

要验证扩展是否正确安装和配置：

1. 打开命令面板（`F1`）
2. 输入"AIgo: 连接到服务器"并执行
3. 如果连接成功，您将看到一条成功消息

## 使用扩展

安装并配置扩展后，您可以使用以下命令：

- `AIgo: 连接到服务器` - 连接到AIgo服务器
- `AIgo: 扫描项目` - 扫描当前项目结构
- `AIgo: 创建上下文` - 将当前文件添加到上下文
- `AIgo: 使用本地模型` - 切换本地模型使用
- `AIgo: 查看记忆` - 查看AI助手的记忆

## 故障排除

如果遇到问题：

1. 确保AIgo服务器正在运行
2. 检查服务器URL配置是否正确
3. 查看Cursor开发者工具中的控制台日志（`Ctrl+Shift+I`）
4. 尝试重新连接服务器
5. 重启Cursor IDE

如需更多帮助，请参阅AIgo文档或提交问题。
