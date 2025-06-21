# AIgo 跨平台兼容性指南

AIgo 项目设计为可在多种操作系统上无缝运行，包括 Windows、Linux（各种发行版）和 macOS。本指南提供在不同平台上安装、配置和运行 AIgo 的详细说明。

## 支持的平台

AIgo 在以下平台上经过测试和支持：

### Windows
- Windows 10（1903或更新版本）
- Windows 11
- Windows Server 2019及以上

### Linux
- Ubuntu 20.04 LTS及以上
- Debian 10及以上
- CentOS 8/Stream及以上
- Fedora 34及以上
- Wubuntu（Ubuntu的定制变种）
- WSL2（Windows Subsystem for Linux 2）

### macOS
- macOS Catalina (10.15)及以上
- macOS 11 (Big Sur)及以上
- Apple Silicon (M1/M2)和Intel处理器均支持

## 系统要求

无论使用哪种平台，AIgo都需要以下基本配置：

- **Python**: 3.9或更高版本
- **内存**: 
  - 最低: 8GB RAM
  - 推荐: 16GB+ RAM（使用大型模型时）
- **存储**:
  - 最低: 2GB可用空间
  - 推荐: 10GB+可用空间（用于模型和数据存储）
- **处理器**: 
  - 最低: 双核处理器
  - 推荐: 四核或更多核心
- **网络**: 稳定的互联网连接（用于模型下载和API访问）

## 平台特定注意事项

### Windows 特定说明

1. **依赖安装**:
   - 某些机器学习库在Windows上有特殊版本，如`torch-directml`（替代`torch`）
   - `bitsandbytes`需要使用Windows特定版本`bitsandbytes-windows`
   - FAISS可以使用预编译的`faiss-cpu`或`faiss-gpu`

2. **路径处理**:
   - 使用`platform_utils.paths`模块处理路径，避免硬编码的反斜杠
   - 项目自动处理Windows路径转换

3. **Windows防火墙**:
   - 首次运行服务器时，Windows可能会显示防火墙提示，请允许访问

4. **PowerShell脚本执行策略**:
   - 可能需要调整PowerShell执行策略以运行项目脚本：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Linux 特定说明

1. **系统依赖**:
   - 某些功能可能需要系统级别的包，可使用以下命令安装：
     ```bash
     # Ubuntu/Debian
     sudo apt-get update && sudo apt-get install -y build-essential python3-dev
     
     # CentOS/Fedora
     sudo dnf install -y gcc gcc-c++ python3-devel
     ```

2. **权限设置**:
   - 确保运行AIgo的用户具有以下目录的适当权限：
     - 配置目录: `~/.config/aigo`
     - 数据目录: `~/.local/share/aigo`
     - 日志目录: `~/.local/share/aigo/logs`或`/var/log/aigo`（如果有权限）

3. **WSL注意事项**:
   - 在WSL中，项目可以自动转换Windows和Linux路径
   - 使用`platform_utils.paths.convert_wsl_path()`在WSL和Windows路径之间转换

### Wubuntu 特定说明

1. **系统依赖**:
   - Wubuntu需要安装特定的系统包：
     ```bash
     sudo apt-get update && sudo apt-get install -y build-essential python3-dev wubuntu-specific-package
     ```

2. **路径处理**:
   - Wubuntu可能使用特定的目录结构，AIgo会自动适配
   - 默认应用数据目录: `~/.local/share/aigo`
   - 默认配置目录: `~/.config/aigo`

3. **特殊配置**:
   - 如果您使用的是Wubuntu的特定功能，可能需要额外配置：
     ```bash
     # 启用Wubuntu特定功能
     python -m aigo.cli.__main__ config set --enable-wubuntu-features
     ```

4. **已知问题**:
   - 某些Wubuntu特定的系统库可能与标准库有冲突，如遇问题请参考故障排除部分

### macOS 特定说明

1. **Apple Silicon (M1/M2) 支持**:
   - 已针对Apple Silicon优化，利用原生ARM指令集
   - 某些依赖项（如PyTorch）会自动选择适合的版本

2. **Homebrew依赖**:
   - 建议使用Homebrew安装某些系统依赖：
     ```bash
     brew install cmake libomp
     ```

3. **路径和权限**:
   - macOS应用数据目录位于`~/Library/Application Support/aigo`
   - 配置目录位于`~/Library/Preferences/aigo`
   - 日志目录位于`~/Library/Logs/aigo`

## 跨平台工具

AIgo提供了专门的跨平台兼容性工具，可以轻松处理不同操作系统之间的差异：

### 平台检测

```python
from src.utils.platform_utils import is_windows, is_linux, is_macos, is_wsl, is_wubuntu

if is_windows():
    # Windows特定代码
elif is_linux():
    # Linux特定代码
    if is_wsl():
        # WSL特定代码
    elif is_wubuntu():
        # Wubuntu特定代码
elif is_macos():
    # macOS特定代码
```

### 跨平台路径处理

```python
from src.utils.platform_utils.paths import normalize_path, get_app_data_dir, get_config_dir

# 获取规范化路径
path = normalize_path("~/projects/data")

# 获取平台特定的应用数据目录
app_data = get_app_data_dir("aigo")

# 获取平台特定的配置目录
config_path = get_config_dir("aigo")
```

### 依赖管理

```python
from src.utils.platform_utils.dependencies import check_platform_dependencies, install_platform_dependencies

# 检查平台特定依赖
deps_status = check_platform_dependencies("ml")

# 安装平台特定依赖
install_results = install_platform_dependencies("ml")
```

## 安装和部署

每个平台的安装过程略有不同，请按照平台特定的说明进行操作：

### 使用自动安装脚本

AIgo提供了跨平台自动安装脚本，可以自动检测平台并安装所需依赖：

```bash
# 标准安装
python install.py

# 带有机器学习支持的安装
python install.py --ml

# 开发环境安装
python install.py --dev

# Wubuntu特定安装
python install.py --wubuntu
```

### 使用Docker（所有平台通用）

AIgo提供了Docker支持，这是确保在任何平台上一致性执行的最简单方法：

```bash
# 构建Docker镜像
docker build -t aigo .

# 运行Docker容器
docker run -p 8000:8000 -v ./config:/app/config -v ./data:/app/data aigo
```

或使用docker-compose：

```bash
docker-compose up -d
```

## 故障排除

### 常见问题

1. **导入错误**:
   - 检查是否已安装所有平台特定依赖
   - 运行`python src/utils/platform_utils_test.py`以验证平台兼容性

2. **性能问题**:
   - Windows上的深度学习功能可能比Linux/macOS慢
   - 考虑使用WSL2在Windows上运行Linux版本
   - 对于大型模型，在资源有限的系统上使用量化版本

3. **路径错误**:
   - 使用项目的`platform_utils.paths`模块而不是直接处理路径
   - 避免硬编码绝对路径

### 平台特定问题解决

#### Windows

- **DLL加载失败**:
  - 确保已安装最新的Visual C++ Redistributable
  - 使用`PATH`环境变量指向正确的DLL目录

- **长路径问题**:
  - 启用Windows 10/11的长路径支持
  - 避免在深度嵌套目录中安装

#### Linux

- **共享库错误**:
  - 安装缺少的系统库：`sudo apt-get install libgomp1 libopenblas-dev`
  - 使用`LD_LIBRARY_PATH`指向自定义库位置

- **GPU支持问题**:
  - 确保已安装正确版本的CUDA和cuDNN
  - 验证GPU驱动程序兼容性

#### Wubuntu

- **特定包冲突**:
  - 如果遇到`wubuntu-specific-package`冲突，尝试：
    ```bash
    sudo apt-get remove --purge wubuntu-specific-package
    sudo apt-get install wubuntu-specific-package=<兼容版本>
    ```

- **路径问题**:
  - 如果Wubuntu使用非标准路径，可以手动指定：
    ```bash
    python -m aigo.cli.__main__ config set --data-dir /path/to/data --config-dir /path/to/config
    ```

#### macOS

- **PyTorch错误**:
  - 确保安装了正确的PyTorch版本（Apple Silicon或Intel）
  - 对于M1/M2芯片，使用`-mmacosx-version-min=11.0`编译标志

- **权限问题**:
  - 使用`sudo` 安装系统级依赖
  - 检查目录权限：`chmod -R 755 ~/Library/Application\ Support/aigo`

## 更多信息

- 请参阅`INSTALL_GUIDE.md`获取详细的安装说明
- 检查`requirements-*.txt`文件了解各平台的依赖细节
- 使用`python src/utils/platform_utils_test.py`测试平台兼容性

如有其他问题，请提交问题到项目的问题追踪器。 