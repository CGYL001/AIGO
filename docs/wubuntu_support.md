# AIgo对Wubuntu的支持

## 什么是Wubuntu？

Wubuntu是一个独立的操作系统，是Ubuntu的特殊版本，它与Windows进行了深度集成。与基于WSL的解决方案不同，Wubuntu是一个完整的独立系统，提供了更深度的Windows集成和更完善的跨平台功能。

## AIgo的Wubuntu支持

AIgo项目现已添加对Wubuntu环境的全面支持，提供了一系列工具和功能，使开发者能够充分利用这种混合环境的优势。

### 主要功能

1. **平台检测**
   - 自动检测Wubuntu环境
   - 识别Wubuntu版本和特性
   - 获取详细的系统信息

2. **路径处理**
   - Windows和Linux路径格式自动转换
   - 跨系统文件访问支持
   - 统一的路径API

3. **跨平台命令执行**
   - 在Wubuntu中执行Windows命令
   - 捕获Windows命令输出
   - 无缝跨系统操作

4. **依赖管理**
   - 管理Linux侧依赖
   - 管理Windows侧依赖
   - 自动安装Wubuntu特定包

5. **系统集成**
   - 设置Wubuntu集成环境
   - 创建跨系统快捷方式
   - 配置开发环境

## 使用方法

### 基本检测

```python
from src.utils.platform_utils import is_wubuntu, get_wubuntu_version

if is_wubuntu():
    print(f"运行在Wubuntu {get_wubuntu_version()} 上")
else:
    print("非Wubuntu环境")
```

### 路径转换

```python
from src.utils.platform_utils import convert_path, get_windows_path

# 获取Windows挂载路径
win_path = get_windows_path()  # 通常为 /mnt/c

# Linux路径转Windows路径
linux_path = "/home/user/document.txt"
windows_path = convert_path(linux_path, to_windows=True)
print(f"Windows路径: {windows_path}")  # \\wsl$\Wubuntu\home\user\document.txt

# Windows路径转Linux路径
win_file = "C:\\Users\\Public\\document.txt"
linux_file = convert_path(win_file, to_windows=False)
print(f"Linux路径: {linux_file}")  # /mnt/c/Users/Public/document.txt
```

### 执行Windows命令

```python
from src.utils.platform_utils import run_windows_command

# 执行Windows命令并捕获输出
returncode, stdout, stderr = run_windows_command("systeminfo", capture_output=True)
if returncode == 0:
    print(stdout)
else:
    print(f"命令执行失败: {stderr}")
```

### 依赖管理

```python
from src.utils.platform_utils import (
    check_wubuntu_dependencies, 
    install_wubuntu_dependencies,
    check_windows_dependencies,
    install_windows_dependencies
)

# 检查Wubuntu核心依赖
core_deps = check_wubuntu_dependencies(category='core')
print(core_deps)

# 安装开发工具
install_wubuntu_dependencies(category='development')

# 检查Windows依赖
win_deps = check_windows_dependencies(category='wsl')
print(win_deps)

# 安装Windows侧依赖
install_windows_dependencies(category='core')
```

### 环境设置

```python
from src.utils.platform_utils import (
    setup_wubuntu_integration,
    setup_wubuntu_development_environment,
    get_wubuntu_dependency_status
)

# 设置基本集成
setup_wubuntu_integration()

# 设置完整开发环境
setup_wubuntu_development_environment()

# 获取依赖状态报告
status = get_wubuntu_dependency_status()
print(status)
```

## 演示脚本

AIgo项目包含一个完整的Wubuntu集成演示脚本，位于 `examples/wubuntu_integration_demo.py`。此脚本展示了如何使用AIgo的Wubuntu支持功能，包括：

- 系统信息检测
- 路径转换
- 依赖检查
- Windows命令执行
- 集成功能检查
- 依赖状态报告

要运行此演示，请在Wubuntu环境中执行：

```bash
python examples/wubuntu_integration_demo.py
```

## 注意事项

1. Wubuntu支持功能仅在Wubuntu环境中可用
2. 某些功能可能需要管理员权限
3. Windows命令执行功能需要访问Windows系统分区
4. 依赖安装可能需要sudo权限

## 未来计划

1. 添加更多Wubuntu特定优化
2. 增强图形界面集成
3. 提供更多跨平台开发工具
4. 支持更多Windows-Linux混合环境场景 