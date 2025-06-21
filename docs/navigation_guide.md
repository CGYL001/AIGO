# AIgo 项目导航系统使用指南

AIgo项目导航系统旨在解决大型项目中常见的资源定位和功能导航问题，帮助开发者和AI助手快速找到所需功能和资源，提高开发效率。

## 导航系统组件

AIgo项目导航系统包括以下主要组件：

1. **PATH_GUIDE.md** - 主路径索引文件
2. **模型注册表** - 模型管理和分类系统
3. **路径查找工具** - 命令行工具，用于查找项目资源
4. **模型管理面板** - 用于可视化查看和管理模型

## 使用路径索引文件

`PATH_GUIDE.md` 是项目的主要导航文件，包含项目中所有关键路径和功能的说明。

使用方法：

1. 打开项目根目录下的 `PATH_GUIDE.md` 文件
2. 浏览目录结构和功能分类
3. 根据需求查找相应的路径和功能

例如，如果您需要查找模型管理相关功能，可以查看"模型管理"部分，了解所有相关的文件和路径。

## 使用路径查找工具

路径查找工具 `tools/path_finder.py` 提供了命令行界面，用于快速查找项目资源。

### 安装和设置

无需特殊安装，只需确保您已经安装了项目的依赖项：

```bash
# 确保在项目根目录下
pip install -r requirements.txt
```

### 基本用法

1. **查找特定功能的相关文件**:

```bash
python tools/path_finder.py find --feature "模型管理"
```

2. **浏览指定目录的结构**:

```bash
python tools/path_finder.py explore --directory "src/modules"
```

3. **搜索特定关键词**:

```bash
python tools/path_finder.py search --keyword "模型优化"
```

4. **列出所有可用功能**:

```bash
python tools/path_finder.py list-features
```

### 高级用法

1. **按文件类型搜索**:

```bash
python tools/path_finder.py search --keyword ".py 模型"
```

2. **组合搜索**:

```bash
python tools/path_finder.py find --feature "代码分析" | grep "metrics"
```

## 使用模型注册表

模型注册表位于 `models/registry` 目录，提供了统一的模型管理和元数据存储。

### 目录结构

```
models/registry/
├── README.md               # 使用说明
├── model_metadata.json     # 模型元数据模板
├── available_models.json   # 所有可用模型列表
├── model_categories.json   # 模型分类信息
└── models/                 # 各模型的详细配置目录
```

### 查看已注册模型

1. 通过文件查看：

```bash
cat models/registry/available_models.json
```

2. 使用模型管理工具：

```bash
python model_manager.py list --registry
```

### 添加新模型

1. 使用模型管理工具：

```bash
python model_manager.py register --name "model_name" --type "model_type" --description "模型描述"
```

2. 手动添加：
   - 在 `models/registry/models` 目录下创建新模型目录
   - 添加模型元数据文件
   - 更新 `available_models.json` 文件

## 使用模型管理面板

模型管理面板提供了可视化界面，用于查看和管理项目中的模型。

### 启动面板

```bash
python tools/models_dashboard.py
```

默认情况下，面板将在 http://localhost:8000 启动。

### 自定义启动选项

```bash
# 指定主机和端口
python tools/models_dashboard.py --host 0.0.0.0 --port 8080
```

### 面板功能

1. **查看模型信息** - 查看所有已注册模型的详细信息
2. **模型状态** - 显示模型是否已下载及是否为当前使用的模型
3. **模型操作** - 提供下载和切换模型的操作

## 从IDE中使用导航系统

### Cursor IDE集成

AIgo项目提供与Cursor IDE的集成，可以在编码过程中获得路径和功能提示：

1. 安装Cursor扩展：
   - 参考 `examples/ide_integration/cursor_extension/INSTALL.md` 
   - 安装 `examples/ide_integration/cursor_extension` 目录中的扩展

2. 使用Cursor扩展：
   - 在编辑器中，输入 `//aigo:` 前缀来触发路径提示
   - 例如：`//aigo:模型管理` 将列出所有模型管理相关的文件

### VSCode集成

同样支持VSCode集成：

1. 安装VSCode扩展：
   - 参考 `examples/ide_integration/vscode_extension/README.md`

2. 使用VSCode扩展：
   - 使用命令面板 (Ctrl+Shift+P) 并输入 "AIgo: 查找资源"
   - 或在状态栏点击 "AIgo" 图标

## 最佳实践

1. **使用PATH_GUIDE.md作为入口**：
   - 开始新任务时，先查看PATH_GUIDE.md了解相关路径

2. **使用命令行工具快速定位**：
   - 使用path_finder.py快速查找特定功能

3. **使用模型管理面板**：
   - 使用models_dashboard.py可视化查看和管理模型

4. **IDE集成**：
   - 在开发过程中利用IDE扩展获得路径提示

5. **更新和维护**：
   - 添加新功能时，更新PATH_GUIDE.md
   - 添加新模型时，注册到模型注册表

## 故障排除

1. **路径查找工具无法正常工作**：
   - 确保Python路径正确
   - 检查是否位于项目根目录

2. **模型管理面板无法启动**：
   - 检查端口是否被占用
   - 确保已安装所有依赖

3. **无法查找到特定功能**：
   - 尝试使用不同的关键词
   - 查看FEATURE_KEYWORDS映射是否包含相关关键词

4. **IDE扩展无法工作**：
   - 检查扩展是否正确安装
   - 确保项目路径已在扩展配置中设置正确

## 贡献和扩展

欢迎为导航系统贡献改进和扩展：

1. 添加新的功能关键词：
   - 编辑 `tools/path_finder.py` 中的 `FEATURE_KEYWORDS` 字典

2. 扩展模型分类：
   - 更新 `models/registry/model_categories.json` 文件

3. 改进路径索引：
   - 更新 `PATH_GUIDE.md` 文件 