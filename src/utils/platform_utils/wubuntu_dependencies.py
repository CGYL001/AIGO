"""
Wubuntu依赖管理工具 - 处理Wubuntu系统环境下的依赖安装和管理

Wubuntu是Ubuntu的特殊版本，与Windows进行了深度集成的独立系统。
这个模块提供了在Wubuntu环境中安装和管理依赖项的工具。
"""

import os
import sys
import subprocess
import json
import platform
import shutil
from typing import List, Dict, Any, Optional, Union, Tuple, Set

from .detection import is_wubuntu
from .wubuntu import run_windows_command, get_windows_path
from .dependencies import check_platform_dependencies, install_platform_dependencies

# Wubuntu特定依赖配置
WUBUNTU_DEPENDENCIES = {
    'core': [
        'wubuntu-core',
        'wubuntu-utils',
        'wubuntu-integration'
    ],
    'ml': [
        'torch',
        'onnxruntime',
        'tensorflow'
    ],
    'graphics': [
        'wubuntu-gui',
        'wslg-support'
    ],
    'development': [
        'build-essential',
        'python3-dev',
        'wubuntu-dev-tools'
    ],
    'windows_bridge': [
        'wslu',
        'wubuntu-win-bridge'
    ]
}

# Windows侧依赖项
WINDOWS_DEPENDENCIES = {
    'core': [
        'Microsoft.VCLibs.140.00',
        'Microsoft.WindowsAppRuntime.1.1'
    ],
    'development': [
        'Microsoft.VisualStudio.BuildTools',
        'Git.Git'
    ],
    'wsl': [
        'Microsoft.WSL',
        'Microsoft.WSLg'
    ]
}

def check_wubuntu_dependencies(category: Optional[str] = None) -> Dict[str, Dict[str, bool]]:
    """
    检查Wubuntu特定依赖项的安装状态
    
    参数:
        category: 依赖项类别，如果为None则检查所有类别
        
    返回:
        包含依赖项检查结果的字典，{'依赖名': {'installed': 布尔值, 'version': 字符串}}
    """
    if not is_wubuntu():
        return {"error": "Not running in Wubuntu environment"}
    
    results = {}
    
    # 确定要检查的依赖
    deps_to_check = []
    if category:
        if category in WUBUNTU_DEPENDENCIES:
            deps_to_check = WUBUNTU_DEPENDENCIES[category]
    else:
        for cat in WUBUNTU_DEPENDENCIES:
            deps_to_check.extend(WUBUNTU_DEPENDENCIES[cat])
    
    # 检查Linux侧依赖
    for dep in deps_to_check:
        is_installed = False
        version = None
        
        # 使用apt检查包是否已安装
        try:
            result = subprocess.run(
                ['dpkg-query', '-W', '-f=${Status} ${Version}', dep],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if 'install ok installed' in result.stdout:
                is_installed = True
                version = result.stdout.split(' ')[-1]
        except:
            pass
        
        # 如果没找到，尝试使用pip检查
        if not is_installed:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'show', dep],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    is_installed = True
                    for line in result.stdout.splitlines():
                        if line.startswith('Version:'):
                            version = line.split(':', 1)[1].strip()
                            break
            except:
                pass
        
        results[dep] = {
            'installed': is_installed,
            'version': version
        }
    
    return results

def check_windows_dependencies(category: Optional[str] = None) -> Dict[str, Dict[str, bool]]:
    """
    检查Wubuntu中Windows侧依赖项的安装状态
    
    参数:
        category: 依赖项类别，如果为None则检查所有类别
        
    返回:
        包含依赖项检查结果的字典，{'依赖名': {'installed': 布尔值, 'version': 字符串}}
    """
    if not is_wubuntu():
        return {"error": "Not running in Wubuntu environment"}
    
    results = {}
    
    # 确定要检查的依赖
    deps_to_check = []
    if category:
        if category in WINDOWS_DEPENDENCIES:
            deps_to_check = WINDOWS_DEPENDENCIES[category]
    else:
        for cat in WINDOWS_DEPENDENCIES:
            deps_to_check.extend(WINDOWS_DEPENDENCIES[cat])
    
    # 检查Windows侧依赖
    for dep in deps_to_check:
        # 使用PowerShell检查Windows应用
        ps_command = f"Get-AppxPackage -Name {dep} | Select-Object -Property Name,Version | ConvertTo-Json"
        
        try:
            returncode, stdout, stderr = run_windows_command(
                f"powershell -Command \"{ps_command}\"", 
                capture_output=True
            )
            
            if returncode == 0 and stdout.strip():
                try:
                    app_info = json.loads(stdout)
                    results[dep] = {
                        'installed': True,
                        'version': app_info.get('Version', 'Unknown')
                    }
                    continue
                except:
                    pass
        except:
            pass
        
        # 如果上面的方法失败，设置为未安装
        results[dep] = {
            'installed': False,
            'version': None
        }
    
    return results

def install_wubuntu_dependencies(
    category: Optional[str] = None,
    deps: Optional[List[str]] = None,
    upgrade: bool = False
) -> Dict[str, bool]:
    """
    安装Wubuntu特定依赖项
    
    参数:
        category: 依赖项类别，如果为None则安装指定的deps
        deps: 要安装的依赖项列表，如果为None则根据category安装
        upgrade: 是否升级已安装的包
        
    返回:
        包含安装结果的字典，{'依赖名': 是否安装成功}
    """
    if not is_wubuntu():
        return {"error": "Not running in Wubuntu environment"}
    
    # 确定要安装的依赖
    deps_to_install = []
    if deps:
        deps_to_install = deps
    elif category and category in WUBUNTU_DEPENDENCIES:
        deps_to_install = WUBUNTU_DEPENDENCIES[category]
    
    results = {}
    
    # 添加Wubuntu特定仓库（如果存在）
    try:
        if os.path.exists('/etc/apt/sources.list.d/wubuntu.list'):
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
    except:
        pass
    
    # 安装依赖
    for dep in deps_to_install:
        # 首先尝试使用apt安装
        try:
            cmd = ['sudo', 'apt-get', 'install', '-y']
            if upgrade:
                cmd.append('--upgrade')
            cmd.append(dep)
            
            subprocess.run(cmd, check=True)
            results[dep] = True
            continue
        except:
            pass
        
        # 如果apt失败，尝试使用pip安装
        try:
            cmd = [sys.executable, '-m', 'pip', 'install']
            if upgrade:
                cmd.append('--upgrade')
            cmd.append(dep)
            
            subprocess.run(cmd, check=True)
            results[dep] = True
        except:
            results[dep] = False
    
    return results

def install_windows_dependencies(
    category: Optional[str] = None,
    deps: Optional[List[str]] = None
) -> Dict[str, bool]:
    """
    安装Wubuntu中Windows侧依赖项
    
    参数:
        category: 依赖项类别，如果为None则安装指定的deps
        deps: 要安装的依赖项列表，如果为None则根据category安装
        
    返回:
        包含安装结果的字典，{'依赖名': 是否安装成功}
    """
    if not is_wubuntu():
        return {"error": "Not running in Wubuntu environment"}
    
    # 确定要安装的依赖
    deps_to_install = []
    if deps:
        deps_to_install = deps
    elif category and category in WINDOWS_DEPENDENCIES:
        deps_to_install = WINDOWS_DEPENDENCIES[category]
    
    results = {}
    
    # 安装Windows依赖
    for dep in deps_to_install:
        # 使用PowerShell和Microsoft Store安装应用
        ps_command = f"Add-AppxPackage -RegisterByFamilyName -MainPackage {dep}"
        
        try:
            returncode, stdout, stderr = run_windows_command(
                f"powershell -Command \"{ps_command}\"", 
                capture_output=True
            )
            
            results[dep] = (returncode == 0)
        except:
            results[dep] = False
    
    return results

def setup_wubuntu_development_environment() -> bool:
    """
    设置完整的Wubuntu开发环境
    
    返回:
        如果成功设置环境则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    success = True
    
    # 1. 安装基础Wubuntu依赖
    linux_deps_result = install_wubuntu_dependencies(category='core')
    if not all(linux_deps_result.values()):
        success = False
    
    # 2. 安装开发工具
    dev_deps_result = install_wubuntu_dependencies(category='development')
    if not all(dev_deps_result.values()):
        success = False
    
    # 3. 安装Windows桥接组件
    bridge_deps_result = install_wubuntu_dependencies(category='windows_bridge')
    if not all(bridge_deps_result.values()):
        success = False
    
    # 4. 安装Windows侧依赖
    win_deps_result = install_windows_dependencies(category='core')
    if not all(win_deps_result.values()):
        success = False
    
    # 5. 设置环境变量
    try:
        with open(os.path.expanduser('~/.bashrc'), 'a') as f:
            f.write('\n# Wubuntu Development Environment\n')
            f.write('export WUBUNTU_DEV=1\n')
            f.write('export PATH=$PATH:/usr/local/wubuntu/bin\n')
    except:
        success = False
    
    # 6. 创建符号链接
    try:
        windows_path = get_windows_path()
        os.makedirs('/usr/local/wubuntu/bin', exist_ok=True)
        
        # 创建wubuntu-cmd脚本
        with open('/usr/local/wubuntu/bin/wubuntu-cmd', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write(f'{windows_path}/Windows/System32/cmd.exe /c "$@"\n')
        
        # 设置执行权限
        os.chmod('/usr/local/wubuntu/bin/wubuntu-cmd', 0o755)
    except:
        success = False
    
    return success

def get_wubuntu_dependency_status() -> Dict[str, Any]:
    """
    获取Wubuntu依赖项的完整状态报告
    
    返回:
        包含依赖项状态的详细报告
    """
    if not is_wubuntu():
        return {"error": "Not running in Wubuntu environment"}
    
    status = {
        "linux_dependencies": {},
        "windows_dependencies": {},
        "integration_status": "unknown"
    }
    
    # 检查Linux侧依赖
    for category in WUBUNTU_DEPENDENCIES:
        status["linux_dependencies"][category] = check_wubuntu_dependencies(category)
    
    # 检查Windows侧依赖
    for category in WINDOWS_DEPENDENCIES:
        status["windows_dependencies"][category] = check_windows_dependencies(category)
    
    # 检查集成状态
    try:
        integration_score = 0
        max_score = 3
        
        # 检查WSL集成
        if os.path.exists('/usr/bin/wslg'):
            integration_score += 1
        
        # 检查Wubuntu桥接工具
        bridge_check = check_wubuntu_dependencies(category='windows_bridge')
        if all(item.get('installed', False) for item in bridge_check.values()):
            integration_score += 1
        
        # 检查Windows集成组件
        win_check = check_windows_dependencies(category='wsl')
        if all(item.get('installed', False) for item in win_check.values()):
            integration_score += 1
        
        # 确定集成状态
        if integration_score == 0:
            status["integration_status"] = "not_integrated"
        elif integration_score < max_score:
            status["integration_status"] = "partially_integrated"
        else:
            status["integration_status"] = "fully_integrated"
    except:
        pass
    
    return status 