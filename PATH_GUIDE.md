# AIgo 路径导航指南

此文档提供AIgo项目中所有关键路径的索引，帮助开发者和AI助手快速定位所需功能和资源。

## 核心目录结构

### 模型相关

- **`models/`** - 模型定义和配置目录
  - `registry/` - 已部署模型的注册表和元数据
  - `demo_model.json`, `optimized_model.json` - 模型配置示例
- **`model_manager.py`** - 模型管理工具，用于切换、下载和优化模型
- **`src/services/model_manager.py`** - 模型管理服务实现
- **`src/modules/model_restructuring/`** - 模型结构优化模块

### 配置相关

- **`config/default/`** - 默认配置文件目录
  - `config.json` - 主配置文件
  - `mcp_config.json` - MCP服务器配置文件
- **`config/models/`** - 模型特定配置目录
- **`config/user/`** - 用户自定义配置目录

### 核心服务与API

- **`src/main.py`** - 应用程序主入口
- **`src/mcp_server.py`** - MCP服务器实现
- **`src/api/`** - API接口定义
  - `app.py` - Web应用程序
  - `fastapi_app.py` - FastAPI应用程序
  - `auth_routes.py` - 认证相关路由

### 功能模块

- **`src/modules/`** - 功能模块目录
  - `code_analysis/` - 代码分析模块
  - `knowledge_base/` - 知识库模块
  - `prompt_engineering/` - 提示工程模块
  - `repo_integration/` - 仓库集成模块
  - `system_monitor/` - 系统监控模块

### IDE集成

- **`examples/ide_integration/`** - IDE集成示例
  - `cursor_extension/` - Cursor扩展实现
  - `vscode_extension/` - VSCode扩展实现

### 工具与实用程序

- **`src/utils/`** - 工具和实用程序
  - `async_utils.py` - 异步操作工具
  - `config_validator.py` - 配置验证工具

## 模型管理

模型管理相关功能路径：

- **模型定义**: `models/`目录
- **模型注册表**: `models/registry/`目录
- **模型管理工具**: `model_manager.py`
- **模型管理配置**: `config/default/config.json`的`models`部分
- **模型管理服务**: `src/services/model_manager.py`
- **模型API文档**: `docs/api/models.rst`

## 常用功能路径

- **启动应用**: `src/main.py`
- **启动MCP服务器**: `src/mcp_server.py`
- **模型切换**: `model_manager.py switch <模型名称>`
- **模型下载**: `model_manager.py download <模型名称>`
- **模型优化**: `model_manager.py optimize`
- **模型状态查看**: `model_manager.py show`
- **查看已有模型**: `model_manager.py list`

## 配置文件路径

主要配置文件：

- **主配置**: `config/default/config.json`
- **MCP配置**: `config/default/mcp_config.json`
- **模型配置**: `config/models/`目录中的配置文件
- **用户配置**: `config/user/`目录中的配置文件

## 文档与指南

- **API文档**: `docs/api/`目录
- **模型指南**: `MODEL_GUIDE.md`
- **安装指南**: `INSTALL_GUIDE.md`
- **贡献指南**: `CONTRIBUTING.md`

## 命令行工具

- **模型管理**: `model_manager.py`
- **安装向导**: `install_wizard.py`
- **AI助手启动**: `start_assistant.py`
- **MCP更新**: `update_mcp.py`

## 路径导航命令

使用新的路径导航工具快速定位资源：

```bash
# 查找特定功能相关文件
python tools/path_finder.py find --feature "模型管理"

# 查看特定目录结构
python tools/path_finder.py explore --directory "src/modules"

# 搜索特定关键词
python tools/path_finder.py search --keyword "模型优化"
```

## 导航提示

- 使用模型管理时，优先查看`model_manager.py`和`models/registry/`目录
- 配置相关修改，优先查看`config/default/`目录
- 开发新功能时，参考`src/modules/`中的相关模块
- IDE集成相关，查看`examples/ide_integration/`目录 