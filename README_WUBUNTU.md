# AIgo对Wubuntu系统的支持

## Wubuntu系统简介

Wubuntu是Ubuntu的特殊版本，与Windows进行了深度集成的独立系统。它提供了两个系统的优势，同时保持了完整的系统功能和独立性。

与基于WSL的解决方案不同，Wubuntu作为一个完整的独立系统运行，但提供了与Windows更深层次的集成和互操作性。

## AIgo的Wubuntu支持特性

AIgo项目为Wubuntu系统提供了全面的支持，包括：

### 1. 系统检测与识别

- 自动检测Wubuntu环境
- 获取Wubuntu版本和系统信息
- 识别Wubuntu特有功能和集成点

### 2. 跨系统文件访问

- Windows和Linux路径格式自动转换
- 统一的路径处理API
- 简化跨系统文件操作

### 3. 跨平台命令执行

- 在Wubuntu中无缝执行Windows命令
- 捕获和处理Windows命令输出
- 支持工作目录和环境变量设置

### 4. 依赖管理

- 管理Wubuntu特有的依赖包
- 处理Windows侧依赖
- 自动安装和配置开发环境

### 5. 系统集成

- 设置Wubuntu与Windows的集成环境
- 创建跨系统快捷方式
- 配置开发工具链

### 6. 内核与操作系统级开发

- 内核模块开发支持
- 设备驱动创建工具
- 系统服务管理
- 内核信息获取与分析

## 快速开始

### 安装

确保已安装AIgo及其依赖：

```bash
pip install -r requirements-wubuntu.txt
```

### 基本使用

```python
from src.utils.platform_utils import (
    is_wubuntu, 
    get_wubuntu_version,
    convert_path,
    run_windows_command
)

# 检查是否在Wubuntu环境中
if is_wubuntu():
    print(f"运行在Wubuntu {get_wubuntu_version()} 上")
    
    # 路径转换示例
    linux_path = "/home/user/document.txt"
    windows_path = convert_path(linux_path, to_windows=True)
    print(f"Windows路径: {windows_path}")
    
    # 执行Windows命令
    returncode, stdout, stderr = run_windows_command("systeminfo", capture_output=True)
    if returncode == 0:
        print(f"Windows系统信息: {stdout[:100]}...")
```

### 运行演示

AIgo提供了完整的Wubuntu集成演示：

```bash
# 基本集成演示
python examples/wubuntu_integration_demo.py

# 内核开发演示
python examples/wubuntu_kernel_dev_demo.py
```

## 配置与设置

### 设置Wubuntu集成环境

```python
from src.utils.platform_utils import setup_wubuntu_integration

# 设置基本集成环境
setup_wubuntu_integration()
```

### 设置开发环境

```python
from src.utils.platform_utils import setup_wubuntu_development_environment

# 设置完整开发环境
setup_wubuntu_development_environment()
```

### 检查依赖状态

```python
from src.utils.platform_utils import get_wubuntu_dependency_status

# 获取依赖状态报告
status = get_wubuntu_dependency_status()
print(status)
```

### 内核开发功能

```python
from src.utils.platform_utils import wubuntu_kernel_dev

# 设置内核开发环境
wubuntu_kernel_dev.setup_kernel_development_environment()

# 创建内核模块模板
wubuntu_kernel_dev.create_kernel_module_template(
    target_dir="/path/to/module",
    module_name="hello_module",
    author="Your Name",
    description="A simple kernel module"
)

# 创建设备驱动模板
wubuntu_kernel_dev.create_device_driver_template(
    target_dir="/path/to/driver",
    driver_name="sample_driver",
    author="Your Name",
    description="A sample character device driver"
)

# 创建系统服务
wubuntu_kernel_dev.create_system_service(
    service_name="my-service",
    exec_path="/path/to/executable",
    description="My Custom Service",
    user="username",
    working_directory="/path/to/workdir"
)

# 获取内核信息
kernel_info = wubuntu_kernel_dev.get_kernel_info()
print(kernel_info)
```

## 注意事项

1. Wubuntu支持功能仅在Wubuntu环境中可用
2. 某些功能可能需要管理员权限
3. Windows命令执行功能需要访问Windows系统分区
4. 依赖安装可能需要sudo权限
5. 内核开发功能需要安装额外的开发工具包

## 文档

更详细的文档请参考：

- [Wubuntu支持文档](docs/wubuntu_support.md)
- [API参考](docs/api/index.rst)
- [基本示例](examples/wubuntu_integration_demo.py)
- [内核开发示例](examples/wubuntu_kernel_dev_demo.py)

## 贡献

我们欢迎对Wubuntu支持功能的改进和扩展。请参考[贡献指南](CONTRIBUTING.md)了解如何参与项目开发。 