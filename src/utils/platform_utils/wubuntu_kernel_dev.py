"""
Wubuntu内核开发支持 - 为Wubuntu系统提供操作系统级和内核级代码开发工具

Wubuntu是Ubuntu的特殊版本，与Windows进行了深度集成的独立系统。
这个模块提供了在Wubuntu环境中进行内核和操作系统级开发的工具和功能。
"""

import os
import sys
import subprocess
import shutil
import platform
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union

from .detection import is_wubuntu
from .wubuntu import run_windows_command, get_windows_path, convert_path
from .wubuntu_dependencies import install_wubuntu_dependencies

# 内核开发工具包依赖
KERNEL_DEV_DEPENDENCIES = [
    'build-essential',
    'kernel-package',
    'fakeroot',
    'libncurses5-dev',
    'libssl-dev',
    'ccache',
    'bison',
    'flex',
    'libelf-dev',
    'dwarves',
    'bc',
    'kmod'
]

# 内核源码路径
DEFAULT_KERNEL_SOURCE_PATH = '/usr/src/linux'

def setup_kernel_development_environment() -> bool:
    """
    设置Wubuntu内核开发环境
    
    安装必要的内核开发工具和依赖
    
    返回:
        如果成功设置环境则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    success = True
    
    # 安装内核开发依赖
    try:
        # 更新包索引
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        
        # 安装内核开发工具包
        result = install_wubuntu_dependencies(deps=KERNEL_DEV_DEPENDENCIES)
        if not all(result.values()):
            success = False
            
        # 安装内核头文件
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'linux-headers-$(uname -r)'], 
                      shell=True, check=True)
    except Exception as e:
        print(f"设置内核开发环境时出错: {e}")
        success = False
    
    return success

def download_kernel_source(version: Optional[str] = None) -> str:
    """
    下载Linux内核源码
    
    参数:
        version: 内核版本，如果为None则下载当前版本
        
    返回:
        内核源码路径，如果下载失败则返回空字符串
    """
    if not is_wubuntu():
        return ""
    
    # 如果未指定版本，获取当前内核版本
    if not version:
        try:
            version = subprocess.check_output(['uname', '-r'], 
                                            text=True).strip()
        except Exception as e:
            print(f"获取内核版本时出错: {e}")
            return ""
    
    # 创建目标目录
    target_dir = f"/usr/src/linux-{version}"
    if os.path.exists(target_dir):
        return target_dir
    
    try:
        # 下载内核源码
        major_version = '.'.join(version.split('.')[:2])
        url = f"https://cdn.kernel.org/pub/linux/kernel/v{major_version}/linux-{version}.tar.xz"
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 下载源码
            subprocess.run(['wget', url, '-O', f"{temp_dir}/linux.tar.xz"], check=True)
            
            # 解压源码
            subprocess.run(['sudo', 'mkdir', '-p', target_dir], check=True)
            subprocess.run(['sudo', 'tar', 'xf', f"{temp_dir}/linux.tar.xz", 
                          '-C', '/usr/src/'], check=True)
            
            # 创建符号链接
            if os.path.exists(DEFAULT_KERNEL_SOURCE_PATH):
                subprocess.run(['sudo', 'rm', DEFAULT_KERNEL_SOURCE_PATH], check=True)
            subprocess.run(['sudo', 'ln', '-s', target_dir, DEFAULT_KERNEL_SOURCE_PATH], check=True)
            
            # 设置权限
            subprocess.run(['sudo', 'chown', '-R', f"{os.getuid()}:{os.getgid()}", target_dir], check=True)
            
            return target_dir
    except Exception as e:
        print(f"下载内核源码时出错: {e}")
        return ""

def compile_kernel_module(
    source_path: str,
    module_name: str,
    kernel_source_path: Optional[str] = None
) -> bool:
    """
    编译内核模块
    
    参数:
        source_path: 模块源码路径
        module_name: 模块名称
        kernel_source_path: 内核源码路径，如果为None则使用默认路径
        
    返回:
        如果成功编译则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    if not kernel_source_path:
        kernel_source_path = DEFAULT_KERNEL_SOURCE_PATH
    
    if not os.path.exists(kernel_source_path):
        print(f"内核源码路径不存在: {kernel_source_path}")
        return False
    
    try:
        # 准备Makefile
        makefile_content = f"""
obj-m += {module_name}.o

all:
\tmake -C {kernel_source_path} M=$(PWD) modules

clean:
\tmake -C {kernel_source_path} M=$(PWD) clean
"""
        
        # 写入Makefile
        with open(os.path.join(source_path, 'Makefile'), 'w') as f:
            f.write(makefile_content)
        
        # 编译模块
        result = subprocess.run(['make', '-C', source_path], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
        
        if result.returncode != 0:
            print(f"编译内核模块失败:\n{result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"编译内核模块时出错: {e}")
        return False

def create_kernel_module_template(
    target_dir: str,
    module_name: str,
    author: str = "",
    description: str = ""
) -> bool:
    """
    创建内核模块模板
    
    参数:
        target_dir: 目标目录
        module_name: 模块名称
        author: 作者信息
        description: 模块描述
        
    返回:
        如果成功创建则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    try:
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)
        
        # 创建模块源文件
        module_content = f"""
/*
 * {module_name}.c - Kernel module template
 *
 * {description}
 *
 * Author: {author}
 * License: GPL
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("{author}");
MODULE_DESCRIPTION("{description}");
MODULE_VERSION("0.1");

static int __init {module_name}_init(void)
{{
    printk(KERN_INFO "{module_name}: Module loaded\\n");
    return 0;
}}

static void __exit {module_name}_exit(void)
{{
    printk(KERN_INFO "{module_name}: Module unloaded\\n");
}}

module_init({module_name}_init);
module_exit({module_name}_exit);
"""
        
        with open(os.path.join(target_dir, f"{module_name}.c"), 'w') as f:
            f.write(module_content)
        
        # 创建Makefile
        makefile_content = f"""
obj-m += {module_name}.o

all:
\tmake -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
\tmake -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
"""
        
        with open(os.path.join(target_dir, 'Makefile'), 'w') as f:
            f.write(makefile_content)
        
        # 创建README
        readme_content = f"""
# {module_name} Kernel Module

{description}

## 编译

运行以下命令编译模块：

```bash
make
```

## 安装

编译后运行以下命令安装模块：

```bash
sudo insmod {module_name}.ko
```

## 卸载

运行以下命令卸载模块：

```bash
sudo rmmod {module_name}
```

## 检查模块状态

运行以下命令查看模块日志：

```bash
dmesg | tail
```

## 作者

{author}
"""
        
        with open(os.path.join(target_dir, 'README.md'), 'w') as f:
            f.write(readme_content)
        
        return True
    except Exception as e:
        print(f"创建内核模块模板时出错: {e}")
        return False

def install_kernel_module(module_path: str) -> bool:
    """
    安装内核模块
    
    参数:
        module_path: 模块路径(.ko文件)
        
    返回:
        如果成功安装则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    if not os.path.exists(module_path):
        print(f"模块文件不存在: {module_path}")
        return False
    
    try:
        # 安装模块
        result = subprocess.run(['sudo', 'insmod', module_path], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
        
        if result.returncode != 0:
            print(f"安装内核模块失败:\n{result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"安装内核模块时出错: {e}")
        return False

def remove_kernel_module(module_name: str) -> bool:
    """
    卸载内核模块
    
    参数:
        module_name: 模块名称
        
    返回:
        如果成功卸载则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    try:
        # 卸载模块
        result = subprocess.run(['sudo', 'rmmod', module_name], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
        
        if result.returncode != 0:
            print(f"卸载内核模块失败:\n{result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"卸载内核模块时出错: {e}")
        return False

def get_loaded_kernel_modules() -> List[Dict[str, str]]:
    """
    获取已加载的内核模块列表
    
    返回:
        已加载模块的列表，每个模块包含名称、大小和使用计数
    """
    if not is_wubuntu():
        return []
    
    modules = []
    
    try:
        # 获取模块列表
        result = subprocess.run(['lsmod'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
        
        if result.returncode != 0:
            print(f"获取模块列表失败:\n{result.stderr}")
            return []
        
        # 解析输出
        lines = result.stdout.strip().split('\n')
        for i, line in enumerate(lines):
            if i == 0:  # 跳过标题行
                continue
                
            parts = line.split()
            if len(parts) >= 3:
                modules.append({
                    'name': parts[0],
                    'size': parts[1],
                    'used_by': ' '.join(parts[3:]) if len(parts) > 3 else ''
                })
        
        return modules
    except Exception as e:
        print(f"获取已加载模块列表时出错: {e}")
        return []

def create_system_service(
    service_name: str,
    exec_path: str,
    description: str = "",
    user: str = "root",
    working_directory: str = "",
    environment_vars: Dict[str, str] = {},
    restart: str = "on-failure"
) -> bool:
    """
    创建系统服务
    
    参数:
        service_name: 服务名称
        exec_path: 可执行文件路径
        description: 服务描述
        user: 运行服务的用户
        working_directory: 工作目录
        environment_vars: 环境变量
        restart: 重启策略
        
    返回:
        如果成功创建则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    try:
        # 创建服务文件内容
        service_content = "[Unit]\n"
        service_content += f"Description={description}\n"
        service_content += "After=network.target\n\n"
        
        service_content += "[Service]\n"
        service_content += f"Type=simple\n"
        service_content += f"User={user}\n"
        
        if working_directory:
            service_content += f"WorkingDirectory={working_directory}\n"
        
        # 添加环境变量
        for key, value in environment_vars.items():
            service_content += f"Environment=\"{key}={value}\"\n"
        
        service_content += f"ExecStart={exec_path}\n"
        service_content += f"Restart={restart}\n\n"
        
        service_content += "[Install]\n"
        service_content += "WantedBy=multi-user.target\n"
        
        # 写入服务文件
        service_path = f"/etc/systemd/system/{service_name}.service"
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(service_content)
            temp_path = temp_file.name
        
        # 复制到系统目录
        subprocess.run(['sudo', 'cp', temp_path, service_path], check=True)
        os.unlink(temp_path)
        
        # 重新加载systemd
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        
        return True
    except Exception as e:
        print(f"创建系统服务时出错: {e}")
        return False

def enable_system_service(service_name: str, start: bool = True) -> bool:
    """
    启用系统服务
    
    参数:
        service_name: 服务名称
        start: 是否立即启动服务
        
    返回:
        如果成功启用则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    try:
        # 启用服务
        subprocess.run(['sudo', 'systemctl', 'enable', f"{service_name}.service"], check=True)
        
        if start:
            # 启动服务
            subprocess.run(['sudo', 'systemctl', 'start', f"{service_name}.service"], check=True)
        
        return True
    except Exception as e:
        print(f"启用系统服务时出错: {e}")
        return False

def get_system_service_status(service_name: str) -> Dict[str, Any]:
    """
    获取系统服务状态
    
    参数:
        service_name: 服务名称
        
    返回:
        服务状态信息
    """
    if not is_wubuntu():
        return {"error": "Not running in Wubuntu environment"}
    
    try:
        # 获取服务状态
        result = subprocess.run(['systemctl', 'show', service_name, 
                               '--no-page', '--property=ActiveState,SubState,LoadState,UnitFileState'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
        
        if result.returncode != 0:
            return {"error": f"获取服务状态失败: {result.stderr}"}
        
        # 解析输出
        status = {}
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                status[key] = value
        
        return status
    except Exception as e:
        return {"error": f"获取服务状态时出错: {e}"}

def create_device_driver_template(
    target_dir: str,
    driver_name: str,
    author: str = "",
    description: str = ""
) -> bool:
    """
    创建设备驱动模板
    
    参数:
        target_dir: 目标目录
        driver_name: 驱动名称
        author: 作者信息
        description: 驱动描述
        
    返回:
        如果成功创建则返回True，否则返回False
    """
    if not is_wubuntu():
        return False
    
    try:
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)
        
        # 创建驱动源文件
        driver_content = f"""
/*
 * {driver_name}.c - Character device driver template
 *
 * {description}
 *
 * Author: {author}
 * License: GPL
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>

#define DEVICE_NAME "{driver_name}"
#define CLASS_NAME "{driver_name}_class"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("{author}");
MODULE_DESCRIPTION("{description}");
MODULE_VERSION("0.1");

static int major_number;
static struct class* device_class = NULL;
static struct device* device_device = NULL;
static struct cdev device_cdev;

// 设备打开函数
static int device_open(struct inode *inode, struct file *file)
{{
    printk(KERN_INFO "{driver_name}: Device opened\\n");
    return 0;
}}

// 设备释放函数
static int device_release(struct inode *inode, struct file *file)
{{
    printk(KERN_INFO "{driver_name}: Device closed\\n");
    return 0;
}}

// 设备读取函数
static ssize_t device_read(struct file *file, char *buffer, size_t length, loff_t *offset)
{{
    char message[] = "Hello from {driver_name} driver!\\n";
    size_t message_len = strlen(message);
    
    if (*offset >= message_len)
        return 0;
    
    if (length > message_len - *offset)
        length = message_len - *offset;
    
    if (copy_to_user(buffer, message + *offset, length))
        return -EFAULT;
    
    *offset += length;
    return length;
}}

// 设备写入函数
static ssize_t device_write(struct file *file, const char *buffer, size_t length, loff_t *offset)
{{
    printk(KERN_INFO "{driver_name}: Received %zu characters from user\\n", length);
    return length;
}}

// 定义文件操作结构体
static struct file_operations fops = {{
    .open = device_open,
    .release = device_release,
    .read = device_read,
    .write = device_write,
}};

// 初始化函数
static int __init {driver_name}_init(void)
{{
    // 动态分配主设备号
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {{
        printk(KERN_ALERT "{driver_name}: Failed to register a major number\\n");
        return major_number;
    }}
    printk(KERN_INFO "{driver_name}: Registered with major number %d\\n", major_number);
    
    // 注册设备类
    device_class = class_create(THIS_MODULE, CLASS_NAME);
    if (IS_ERR(device_class)) {{
        unregister_chrdev(major_number, DEVICE_NAME);
        printk(KERN_ALERT "{driver_name}: Failed to register device class\\n");
        return PTR_ERR(device_class);
    }}
    printk(KERN_INFO "{driver_name}: Device class registered\\n");
    
    // 注册设备驱动
    device_device = device_create(device_class, NULL, MKDEV(major_number, 0), NULL, DEVICE_NAME);
    if (IS_ERR(device_device)) {{
        class_destroy(device_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        printk(KERN_ALERT "{driver_name}: Failed to create device\\n");
        return PTR_ERR(device_device);
    }}
    printk(KERN_INFO "{driver_name}: Device created\\n");
    
    // 初始化字符设备
    cdev_init(&device_cdev, &fops);
    device_cdev.owner = THIS_MODULE;
    
    // 添加字符设备
    if (cdev_add(&device_cdev, MKDEV(major_number, 0), 1) < 0) {{
        device_destroy(device_class, MKDEV(major_number, 0));
        class_destroy(device_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        printk(KERN_ALERT "{driver_name}: Failed to add cdev\\n");
        return -1;
    }}
    
    printk(KERN_INFO "{driver_name}: Device driver initialized\\n");
    return 0;
}}

// 退出函数
static void __exit {driver_name}_exit(void)
{{
    cdev_del(&device_cdev);
    device_destroy(device_class, MKDEV(major_number, 0));
    class_destroy(device_class);
    unregister_chrdev(major_number, DEVICE_NAME);
    printk(KERN_INFO "{driver_name}: Device driver removed\\n");
}}

module_init({driver_name}_init);
module_exit({driver_name}_exit);
"""
        
        with open(os.path.join(target_dir, f"{driver_name}.c"), 'w') as f:
            f.write(driver_content)
        
        # 创建Makefile
        makefile_content = f"""
obj-m += {driver_name}.o

all:
\tmake -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
\tmake -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
"""
        
        with open(os.path.join(target_dir, 'Makefile'), 'w') as f:
            f.write(makefile_content)
        
        # 创建README
        readme_content = f"""
# {driver_name} 字符设备驱动

{description}

## 编译

运行以下命令编译驱动：

```bash
make
```

## 安装

编译后运行以下命令安装驱动：

```bash
sudo insmod {driver_name}.ko
```

## 创建设备节点

安装后运行以下命令创建设备节点（通常由udev自动完成）：

```bash
sudo mknod /dev/{driver_name} c $(cat /proc/devices | grep {driver_name} | cut -d' ' -f1) 0
sudo chmod 666 /dev/{driver_name}
```

## 测试驱动

读取设备：

```bash
cat /dev/{driver_name}
```

写入设备：

```bash
echo "Hello" > /dev/{driver_name}
```

## 卸载

运行以下命令卸载驱动：

```bash
sudo rmmod {driver_name}
```

## 作者

{author}
"""
        
        with open(os.path.join(target_dir, 'README.md'), 'w') as f:
            f.write(readme_content)
        
        # 创建测试脚本
        test_script_content = f"""#!/bin/bash
# 测试{driver_name}驱动的脚本

# 加载驱动
sudo insmod {driver_name}.ko

# 获取主设备号
MAJOR=$(cat /proc/devices | grep {driver_name} | cut -d' ' -f1)

# 创建设备节点
sudo mknod /dev/{driver_name} c $MAJOR 0
sudo chmod 666 /dev/{driver_name}

# 读取设备
echo "读取设备:"
cat /dev/{driver_name}

# 写入设备
echo "写入设备:"
echo "Hello, {driver_name}!" > /dev/{driver_name}

# 查看内核日志
echo "内核日志:"
dmesg | tail -n 10

# 清理
echo "按Enter键卸载驱动..."
read
sudo rm /dev/{driver_name}
sudo rmmod {driver_name}
"""
        
        with open(os.path.join(target_dir, 'test_driver.sh'), 'w') as f:
            f.write(test_script_content)
        os.chmod(os.path.join(target_dir, 'test_driver.sh'), 0o755)
        
        return True
    except Exception as e:
        print(f"创建设备驱动模板时出错: {e}")
        return False

def get_kernel_info() -> Dict[str, Any]:
    """
    获取内核信息
    
    返回:
        内核相关信息
    """
    if not is_wubuntu():
        return {"error": "Not running in Wubuntu environment"}
    
    info = {}
    
    try:
        # 获取内核版本
        info['version'] = subprocess.check_output(['uname', '-r'], 
                                                text=True).strip()
        
        # 获取内核构建信息
        info['build_date'] = subprocess.check_output(['uname', '-v'], 
                                                   text=True).strip()
        
        # 获取架构
        info['architecture'] = subprocess.check_output(['uname', '-m'], 
                                                     text=True).strip()
        
        # 获取内核配置
        if os.path.exists('/boot/config-' + info['version']):
            config_path = '/boot/config-' + info['version']
            config = {}
            with open(config_path, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config[key] = value
            info['config'] = config
        
        # 获取已加载模块数量
        modules = get_loaded_kernel_modules()
        info['loaded_modules_count'] = len(modules)
        
        return info
    except Exception as e:
        return {"error": f"获取内核信息时出错: {e}"} 