"""
跨平台依赖管理工具 - 处理不同操作系统的依赖安装和检查

提供统一的依赖管理API，确保在不同平台上正确安装和配置依赖项。
"""

import os
import sys
import subprocess
import logging
import platform
from typing import List, Dict, Any, Optional, Union, Tuple, Set

# 警告：pkg_resources已被标记为弃用，计划在2025-11-30移除
import pkg_resources

logger = logging.getLogger(__name__)

# 常见平台特定依赖项
PLATFORM_DEPENDENCIES = {
    'windows': {
        'ml': ['torch-directml', 'torch-cuda', 'onnxruntime-directml'],
        'system': ['pywin32', 'winrt'],
        'alternatives': {
            'faiss-cpu': ['faiss-cpu', 'faiss-gpu'],
            'bitsandbytes': ['bitsandbytes-windows']
        }
    },
    'linux': {
        'ml': ['torch', 'onnxruntime'],
        'system': ['python3-dev', 'build-essential'],
        'alternatives': {}
    },
    'wubuntu': {  # Wubuntu特定依赖
        'ml': ['torch', 'onnxruntime'],
        'system': ['python3-dev', 'build-essential', 'wubuntu-specific-package'],
        'alternatives': {
            'faiss-cpu': ['faiss-cpu'],
            'bitsandbytes': ['bitsandbytes']
        }
    },
    'darwin': {  # macOS
        'ml': ['torch', 'onnxruntime'],
        'system': [],
        'alternatives': {
            'faiss-cpu': ['faiss-cpu'],
            'bitsandbytes': ['bitsandbytes-darwin']
        }
    }
}

def check_platform_dependencies(category: Optional[str] = None) -> Dict[str, Dict[str, bool]]:
    """
    检查平台特定依赖项的安装状态
    
    参数:
        category: 依赖项类别（如'ml', 'system'），如果为None则检查所有类别
        
    返回:
        包含依赖项检查结果的字典，{'依赖名': {'installed': 布尔值, 'version': 字符串}}
    """
    platform_type = _get_platform_type()
    deps_to_check = {}
    
    if platform_type in PLATFORM_DEPENDENCIES:
        platform_deps = PLATFORM_DEPENDENCIES[platform_type]
        
        if category:
            if category in platform_deps:
                deps_to_check = platform_deps[category]
        else:
            for cat in platform_deps:
                if cat != 'alternatives':  # 不直接检查替代项
                    deps_to_check.update({dep: None for dep in platform_deps[cat]})
    
    results = {}
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    
    for dep in deps_to_check:
        is_installed = False
        version = None
        
        # 直接检查包是否已安装
        if dep.lower() in installed_packages:
            is_installed = True
            version = installed_packages[dep.lower()]
        else:
            # 检查替代项
            alt_installed = False
            if 'alternatives' in PLATFORM_DEPENDENCIES[platform_type]:
                alternatives = PLATFORM_DEPENDENCIES[platform_type]['alternatives'].get(dep, [])
                for alt in alternatives:
                    if alt.lower() in installed_packages:
                        is_installed = True
                        version = installed_packages[alt.lower()]
                        alt_installed = True
                        break
            
            # 尝试使用importlib检查
            if not alt_installed and not is_installed:
                try:
                    module_name = dep.split('[')[0]  # 处理类似 'package[extra]' 的格式
                    module = importlib.import_module(module_name)
                    is_installed = True
                    version = getattr(module, '__version__', None)
                except ImportError:
                    pass
        
        results[dep] = {
            'installed': is_installed,
            'version': version
        }
    
    return results

def install_platform_dependencies(
    category: Optional[str] = None, 
    deps: Optional[List[str]] = None, 
    upgrade: bool = False,
    python_executable: Optional[str] = None
) -> Dict[str, bool]:
    """
    安装平台特定依赖项
    
    参数:
        category: 依赖项类别（如'ml', 'system'），如果为None则安装指定的deps
        deps: 要安装的依赖项列表，如果为None则根据category安装
        upgrade: 是否升级已安装的包
        python_executable: Python解释器路径，默认使用当前解释器
        
    返回:
        包含安装结果的字典，{'依赖名': 是否安装成功}
    """
    if python_executable is None:
        python_executable = sys.executable
    
    platform_type = _get_platform_type()
    deps_to_install = []
    
    # 确定要安装的依赖项
    if deps:
        deps_to_install = deps
    elif category and platform_type in PLATFORM_DEPENDENCIES:
        platform_deps = PLATFORM_DEPENDENCIES[platform_type]
        if category in platform_deps:
            deps_to_install = platform_deps[category]
    
    results = {}
    
    # 对于每个依赖，检查是否有平台特定替代项
    for dep in deps_to_install:
        real_dep = dep
        
        # 检查是否有替代依赖
        if (platform_type in PLATFORM_DEPENDENCIES and 
            'alternatives' in PLATFORM_DEPENDENCIES[platform_type] and 
            dep in PLATFORM_DEPENDENCIES[platform_type]['alternatives']):
            alternatives = PLATFORM_DEPENDENCIES[platform_type]['alternatives'][dep]
            if alternatives:
                real_dep = alternatives[0]  # 使用第一个替代项
        
        # 构建pip命令
        cmd = [python_executable, '-m', 'pip', 'install']
        if upgrade:
            cmd.append('--upgrade')
        cmd.append(real_dep)
        
        try:
            # 执行安装
            subprocess.check_call(cmd)
            results[dep] = True
        except subprocess.CalledProcessError:
            results[dep] = False
    
    return results

def get_missing_dependencies(requirements_file: str) -> List[str]:
    """
    检查requirements文件，获取缺失的依赖项
    
    参数:
        requirements_file: requirements文件路径
        
    返回:
        缺失的依赖项列表
    """
    missing = []
    
    try:
        # 读取requirements文件
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 移除版本规范和平台标记
                    req_name = line.split('#')[0].strip()  # 移除注释
                    req_name = req_name.split(';')[0].strip()  # 移除平台标记
                    req_name = req_name.split('==')[0].strip()  # 移除精确版本
                    req_name = req_name.split('>=')[0].strip()  # 移除最低版本
                    req_name = req_name.split('>')[0].strip()  # 移除版本比较
                    req_name = req_name.split('<')[0].strip()  # 移除版本比较
                    req_name = req_name.split('[')[0].strip()  # 移除额外选项
                    
                    if req_name:
                        requirements.append(req_name)
        
        # 获取已安装的包
        installed_packages = {pkg.key: pkg for pkg in pkg_resources.working_set}
        
        # 检查每个依赖项是否已安装
        for req in requirements:
            req_key = req.lower()
            if req_key not in installed_packages:
                # 检查是否可以导入（可能以不同名称安装）
                try:
                    importlib.import_module(req_key)
                except ImportError:
                    missing.append(req)
                    
    except Exception as e:
        print(f"检查依赖项时出错: {e}")
    
    return missing

def has_compatible_pip_version() -> bool:
    """
    检查pip版本是否足够新，以支持现代安装功能
    
    返回:
        如果pip版本足够新则返回True，否则返回False
    """
    try:
        # 检查pip版本
        result = subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 解析版本信息 (格式如: "pip 21.0.1 from ...")
        version_str = result.stdout.split(' ')[1]
        major, minor, *_ = map(int, version_str.split('.'))
        
        # pip 20.0或更高版本具有我们需要的功能
        return major >= 20
    except Exception:
        return False

def update_pip() -> bool:
    """
    更新pip到最新版本
    
    返回:
        如果更新成功则返回True，否则返回False
    """
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ])
        return True
    except Exception:
        return False

# 内部辅助函数
def _get_platform_type() -> str:
    """获取标准化的平台类型字符串"""
    # 首先检查是否为wubuntu
    if is_wubuntu():
        return 'wubuntu'
    
    # 然后检查常规平台
    system = platform.system().lower()
    if system == 'darwin':
        return 'darwin'
    elif system == 'linux':
        return 'linux'
    elif system == 'windows':
        return 'windows'
    else:
        return 'unknown'

def check_dependency(name: str) -> bool:
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

def check_python_package(package_name: str) -> bool:
    """
    检查是否安装了指定的Python包

    参数:
        package_name (str): 包名称

    返回:
        bool: 如果包已安装则返回True
    """
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def get_package_version(package_name: str) -> Optional[str]:
    """
    获取已安装的Python包版本

    参数:
        package_name (str): 包名称

    返回:
        Optional[str]: 包版本，如果未安装则返回None
    """
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return None

def check_dependencies(dependencies: List[str]) -> Dict[str, bool]:
    """
    检查多个依赖项

    参数:
        dependencies (List[str]): 依赖项列表

    返回:
        Dict[str, bool]: 依赖项状态字典
    """
    results = {}
    for dep in dependencies:
        results[dep] = check_dependency(dep)
    return results

def check_python_dependencies(dependencies: List[str]) -> Dict[str, Any]:
    """
    检查多个Python包依赖项

    参数:
        dependencies (List[str]): Python包名称列表

    返回:
        Dict[str, Any]: 包含安装状态和版本的字典
    """
    results = {}
    for dep in dependencies:
        installed = check_python_package(dep)
        version = get_package_version(dep) if installed else None
        results[dep] = {
            "installed": installed,
            "version": version
        }
    return results

def install_python_package(package_name: str, version: Optional[str] = None) -> bool:
    """
    安装指定的Python包

    参数:
        package_name (str): 包名称
        version (Optional[str]): 指定版本，如果为None则安装最新版本

    返回:
        bool: 安装成功返回True
    """
    try:
        pkg_spec = f"{package_name}=={version}" if version else package_name
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg_spec])
        return True
    except subprocess.CalledProcessError:
        logger.error(f"安装包 {package_name} 失败")
        return False
    except Exception as e:
        logger.error(f"安装包 {package_name} 时出错: {e}")
        return False 