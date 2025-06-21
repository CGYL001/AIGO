"""
平台检测工具

此模块提供用于检测操作系统、硬件和软件环境的工具函数。
支持Windows、Linux、macOS和Wubuntu(Ubuntu特殊版本)平台。
"""

import os
import sys
import platform
import subprocess
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

def check_command_exists(name: str) -> bool:
    """
    检查系统中是否安装了指定的命令行工具

    参数:
        name (str): 要检查的命令名称

    返回:
        bool: 如果命令存在则返回True
    """
    # 检查命令是否存在
    if sys.platform == "win32":
        # Windows上使用where命令
        try:
            result = subprocess.run(['where', name], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   check=False)
            return result.returncode == 0
        except:
            return False
    else:
        # Linux/macOS上使用which命令
        try:
            result = subprocess.run(['which', name], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   check=False)
            return result.returncode == 0
        except:
            return False

def get_platform_info() -> Dict[str, Any]:
    """
    获取当前平台的详细信息

    返回:
        Dict[str, Any]: 包含平台信息的字典
    """
    info = {
        "os": get_os_name(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }
    
    # 检测WSL
    if is_wsl():
        info["wsl"] = True
        info["wsl_version"] = get_wsl_version()
    else:
        info["wsl"] = False
    
    # 检测Wubuntu
    if is_wubuntu():
        info["wubuntu"] = True
        info["wubuntu_version"] = get_wubuntu_version()
    else:
        info["wubuntu"] = False
    
    # 检测GPU
    gpu_info = get_gpu_info()
    if gpu_info:
        info["gpu"] = gpu_info
    
    return info

def get_os_name() -> str:
    """
    获取操作系统名称

    返回:
        str: 操作系统名称 (Windows, Linux, Darwin, Wubuntu)
    """
    os_name = platform.system()
    
    # 检测Wubuntu
    if os_name == "Linux" and is_wubuntu():
        return "Wubuntu"
    
    return os_name

def is_windows() -> bool:
    """
    检查当前操作系统是否为Windows

    返回:
        bool: 如果是Windows则返回True
    """
    return platform.system() == "Windows"

def is_linux() -> bool:
    """
    检查当前操作系统是否为Linux

    返回:
        bool: 如果是Linux则返回True
    """
    return platform.system() == "Linux"

def is_macos() -> bool:
    """
    检查当前操作系统是否为macOS

    返回:
        bool: 如果是macOS则返回True
    """
    return platform.system() == "Darwin"

def is_wsl() -> bool:
    """
    检查当前环境是否为Windows Subsystem for Linux (WSL)

    返回:
        bool: 如果是WSL则返回True
    """
    if not is_linux():
        return False
    
    # 检查/proc/version中是否包含Microsoft或WSL
    try:
        with open('/proc/version', 'r') as f:
            version_info = f.read().lower()
            return 'microsoft' in version_info or 'wsl' in version_info
    except:
        pass
    
    # 检查环境变量
    return 'WSL_DISTRO_NAME' in os.environ

def get_wsl_version() -> Optional[int]:
    """
    获取WSL版本(1或2)

    返回:
        Optional[int]: WSL版本，如果不是WSL则返回None
    """
    if not is_wsl():
        return None
    
    try:
        # 检查/proc/version中是否包含WSL2
        with open('/proc/version', 'r') as f:
            version_info = f.read().lower()
            if 'wsl2' in version_info:
                return 2
        
        # 默认为WSL1
        return 1
    except:
        return 1  # 默认假设为WSL1

def is_wubuntu() -> bool:
    """
    检查当前环境是否为Wubuntu
    
    Wubuntu是一个与Windows深度集成的Ubuntu特殊版本，
    它是一个完整的独立系统，而非WSL子系统。

    返回:
        bool: 如果是Wubuntu则返回True
    """
    # 检查特定的Wubuntu标识文件
    wubuntu_marker = '/etc/wubuntu-release'
    if is_linux() and os.path.exists(wubuntu_marker):
        return True
    
    # 检查环境变量
    if 'WUBUNTU_VERSION' in os.environ:
        return True
    
    return False

def get_wubuntu_version() -> Optional[str]:
    """
    获取Wubuntu版本

    返回:
        Optional[str]: Wubuntu版本，如果不是Wubuntu则返回None
    """
    if not is_wubuntu():
        return None
    
    # 从环境变量获取版本
    if 'WUBUNTU_VERSION' in os.environ:
        return os.environ['WUBUNTU_VERSION']
    
    # 从标识文件获取版本
    try:
        with open('/etc/wubuntu-release', 'r') as f:
            return f.read().strip()
    except:
        pass
    
    # 尝试从lsb_release获取
    try:
        result = subprocess.run(['lsb_release', '-d'], 
                               stdout=subprocess.PIPE, 
                               text=True, 
                               check=True)
        output = result.stdout.lower()
        if 'wubuntu' in output:
            # 提取版本号
            import re
            match = re.search(r'wubuntu\s+(\d+\.\d+)', output)
            if match:
                return match.group(1)
    except:
        pass
    
    return "Unknown"

def get_gpu_info() -> List[Dict[str, str]]:
    """
    获取系统GPU信息

    返回:
        List[Dict[str, str]]: GPU信息列表，每个GPU包含名称、内存等信息
    """
    gpus = []
    
    # 检查NVIDIA GPU
    if check_command_exists('nvidia-smi'):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', 
                                    '--format=csv,noheader'], 
                                   stdout=subprocess.PIPE, 
                                   text=True, 
                                   check=True)
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        gpus.append({
                            "name": parts[0],
                            "memory": parts[1],
                            "driver": parts[2],
                            "type": "NVIDIA"
                        })
        except:
            pass
    
    # 检查AMD GPU (Linux)
    if is_linux() and check_command_exists('rocm-smi'):
        try:
            result = subprocess.run(['rocm-smi', '--showproductname', '--showmeminfo'], 
                                   stdout=subprocess.PIPE, 
                                   text=True, 
                                   check=True)
            
            # 解析rocm-smi输出
            # 这里简化处理，实际上需要更复杂的解析
            for line in result.stdout.strip().split('\n'):
                if 'GPU' in line and 'Memory' in line:
                    gpus.append({
                        "name": line.split(':')[1].strip(),
                        "type": "AMD"
                    })
        except:
            pass
    
    # Windows上检测GPU
    if is_windows():
        try:
            import wmi
            w = wmi.WMI()
            for gpu in w.Win32_VideoController():
                gpus.append({
                    "name": gpu.Name,
                    "adapter_ram": str(int(gpu.AdapterRAM) if gpu.AdapterRAM else 0),
                    "driver_version": gpu.DriverVersion,
                    "type": "Unknown"
                })
        except:
            # 如果WMI模块不可用，尝试使用PowerShell
            try:
                cmd = "powershell \"Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion\""
                result = subprocess.run(cmd, 
                                       stdout=subprocess.PIPE, 
                                       text=True, 
                                       shell=True, 
                                       check=True)
                
                lines = result.stdout.strip().split('\n')
                current_gpu = {}
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        if current_gpu and 'name' in current_gpu:
                            gpus.append(current_gpu)
                            current_gpu = {}
                    elif ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key == 'name':
                            current_gpu['name'] = value
                        elif key == 'adapterram':
                            current_gpu['adapter_ram'] = value
                        elif key == 'driverversion':
                            current_gpu['driver_version'] = value
                
                if current_gpu and 'name' in current_gpu:
                    gpus.append(current_gpu)
            except:
                pass
    
    return gpus

def get_cpu_info() -> Dict[str, Any]:
    """
    获取CPU信息

    返回:
        Dict[str, Any]: CPU信息
    """
    info = {
        "processor": platform.processor(),
        "architecture": platform.architecture(),
        "machine": platform.machine()
    }
    
    # Linux上获取更详细的CPU信息
    if is_linux():
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
            
            # 解析处理器型号
            for line in cpuinfo.split('\n'):
                if 'model name' in line:
                    info["model"] = line.split(':', 1)[1].strip()
                    break
            
            # 计算核心数
            info["cores"] = cpuinfo.count('processor\t:')
        except:
            pass
    
    # Windows上获取CPU信息
    elif is_windows():
        try:
            cmd = "powershell \"Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors\""
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   text=True, 
                                   shell=True, 
                                   check=True)
            
            lines = result.stdout.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Name'):
                    info["model"] = line.split(':', 1)[1].strip()
                elif line.startswith('NumberOfCores'):
                    info["physical_cores"] = int(line.split(':', 1)[1].strip())
                elif line.startswith('NumberOfLogicalProcessors'):
                    info["logical_cores"] = int(line.split(':', 1)[1].strip())
        except:
            pass
    
    return info

def get_ram_info() -> Dict[str, Any]:
    """
    获取内存信息

    返回:
        Dict[str, Any]: 内存信息
    """
    info = {}
    
    # Linux上获取内存信息
    if is_linux():
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            for line in meminfo.split('\n'):
                if 'MemTotal' in line:
                    total = int(line.split(':')[1].strip().split()[0])
                    info["total"] = f"{total // 1024} MB"
                elif 'MemFree' in line:
                    free = int(line.split(':')[1].strip().split()[0])
                    info["free"] = f"{free // 1024} MB"
        except:
            pass
    
    # Windows上获取内存信息
    elif is_windows():
        try:
            cmd = "powershell \"Get-WmiObject Win32_ComputerSystem | Select-Object TotalPhysicalMemory\""
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   text=True, 
                                   shell=True, 
                                   check=True)
            
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('TotalPhysicalMemory'):
                    total = int(line.split(':', 1)[1].strip())
                    info["total"] = f"{total // (1024*1024)} MB"
        except:
            pass
    
    return info

def get_disk_info() -> List[Dict[str, Any]]:
    """
    获取磁盘信息

    返回:
        List[Dict[str, Any]]: 磁盘信息列表
    """
    disks = []
    
    if is_windows():
        try:
            cmd = "powershell \"Get-WmiObject Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace\""
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   text=True, 
                                   shell=True, 
                                   check=True)
            
            lines = result.stdout.strip().split('\n')
            current_disk = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_disk and 'device' in current_disk:
                        disks.append(current_disk)
                        current_disk = {}
                elif ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'deviceid':
                        current_disk['device'] = value
                    elif key == 'size':
                        current_disk['total'] = f"{int(value) // (1024*1024*1024)} GB"
                    elif key == 'freespace':
                        current_disk['free'] = f"{int(value) // (1024*1024*1024)} GB"
            
            if current_disk and 'device' in current_disk:
                disks.append(current_disk)
        except:
            pass
    elif is_linux():
        try:
            result = subprocess.run(['df', '-h'], 
                                   stdout=subprocess.PIPE, 
                                   text=True, 
                                   check=True)
            
            lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            for line in lines:
                parts = line.split()
                if len(parts) >= 6:
                    disks.append({
                        "device": parts[0],
                        "total": parts[1],
                        "used": parts[2],
                        "free": parts[3],
                        "mount": parts[5]
                    })
        except:
            pass
    
    return disks

def is_docker() -> bool:
    """
    检查当前环境是否为Docker容器

    返回:
        bool: 如果是Docker容器则返回True
    """
    # 检查/.dockerenv文件
    if os.path.exists('/.dockerenv'):
        return True
    
    # 检查cgroup
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return 'docker' in f.read()
    except:
        pass
    
    return False

def get_network_info() -> Dict[str, Any]:
    """
    获取网络信息

    返回:
        Dict[str, Any]: 网络信息
    """
    info = {}
    
    # 获取主机名
    info["hostname"] = platform.node()
    
    # 尝试获取IP地址
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info["ip"] = s.getsockname()[0]
        s.close()
    except:
        info["ip"] = "Unknown"
    
    return info

def get_python_packages() -> List[Tuple[str, str]]:
    """
    获取已安装的Python包列表

    返回:
        List[Tuple[str, str]]: 包名和版本的元组列表
    """
    packages = []
    
    try:
        import pkg_resources
        for package in pkg_resources.working_set:
            packages.append((package.key, package.version))
    except:
        pass
    
    return packages

if __name__ == "__main__":
    """主函数，显示当前系统的平台信息"""
    # 配置日志
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 获取并显示平台信息
    info = get_platform_info()
    
    print("\n===== 平台信息 =====")
    print(f"操作系统: {info['os']} {info['os_release']} {info['os_version']}")
    print(f"架构: {info['architecture'][0]} ({info['machine']})")
    print(f"处理器: {info['processor']}")
    print(f"Python: {info['python_version']} ({info['python_implementation']})")
    
    if info['wsl']:
        print(f"WSL: 版本 {info['wsl_version']}")
    
    if info['wubuntu']:
        print(f"Wubuntu: 版本 {info['wubuntu_version']}")
    
    # 显示GPU信息
    if 'gpu' in info and info['gpu']:
        print("\n===== GPU信息 =====")
        for i, gpu in enumerate(info['gpu']):
            print(f"GPU {i+1}: {gpu.get('name', 'Unknown')}")
            if 'memory' in gpu:
                print(f"  内存: {gpu['memory']}")
            if 'driver' in gpu:
                print(f"  驱动: {gpu['driver']}")
            if 'type' in gpu:
                print(f"  类型: {gpu['type']}")
    
    # 显示CPU信息
    cpu_info = get_cpu_info()
    print("\n===== CPU信息 =====")
    if 'model' in cpu_info:
        print(f"型号: {cpu_info['model']}")
    if 'physical_cores' in cpu_info:
        print(f"物理核心: {cpu_info['physical_cores']}")
    if 'logical_cores' in cpu_info:
        print(f"逻辑处理器: {cpu_info['logical_cores']}")
    elif 'cores' in cpu_info:
        print(f"核心数: {cpu_info['cores']}")
    
    # 显示内存信息
    ram_info = get_ram_info()
    if ram_info:
        print("\n===== 内存信息 =====")
        if 'total' in ram_info:
            print(f"总内存: {ram_info['total']}")
        if 'free' in ram_info:
            print(f"可用内存: {ram_info['free']}")
    
    # 显示磁盘信息
    disk_info = get_disk_info()
    if disk_info:
        print("\n===== 磁盘信息 =====")
        for disk in disk_info:
            print(f"设备: {disk.get('device', 'Unknown')}")
            if 'total' in disk:
                print(f"  总容量: {disk['total']}")
            if 'free' in disk:
                print(f"  可用空间: {disk['free']}")
            if 'mount' in disk:
                print(f"  挂载点: {disk['mount']}")
    
    # 显示网络信息
    net_info = get_network_info()
    print("\n===== 网络信息 =====")
    print(f"主机名: {net_info.get('hostname', 'Unknown')}")
    print(f"IP地址: {net_info.get('ip', 'Unknown')}")
    
    # 检查是否在Docker中运行
    if is_docker():
        print("\n当前在Docker容器中运行") 