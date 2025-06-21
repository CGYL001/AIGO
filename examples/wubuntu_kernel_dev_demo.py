#!/usr/bin/env python3
"""
Wubuntu内核开发演示 - 展示AIgo在Wubuntu系统环境中的内核开发功能

此示例演示了如何使用AIgo的平台工具来在Wubuntu环境中进行内核和操作系统级开发，
包括创建内核模块、设备驱动、系统服务等功能。
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.platform_utils import (
    # 平台检测
    is_wubuntu, get_platform_info,
    
    # Wubuntu内核开发功能
    wubuntu_kernel_dev
)

def print_section(title):
    """打印带有分隔线的节标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_json(data):
    """以格式化的JSON形式打印数据"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    """Wubuntu内核开发演示主函数"""
    print_section("Wubuntu内核开发演示")
    
    # 检查是否在Wubuntu环境中运行
    if not is_wubuntu():
        print("此演示需要在Wubuntu环境中运行。")
        print(f"当前平台: {get_platform_info()['os_type']}")
        return
    
    # 1. 显示内核信息
    print_section("内核信息")
    kernel_info = wubuntu_kernel_dev.get_kernel_info()
    print(f"内核版本: {kernel_info.get('version', 'Unknown')}")
    print(f"构建日期: {kernel_info.get('build_date', 'Unknown')}")
    print(f"架构: {kernel_info.get('architecture', 'Unknown')}")
    print(f"已加载模块数量: {kernel_info.get('loaded_modules_count', 0)}")
    
    # 2. 设置内核开发环境
    print_section("设置内核开发环境")
    print("注意: 此步骤需要sudo权限，可能需要一些时间...")
    setup_env = input("是否设置内核开发环境？(y/n): ")
    if setup_env.lower() == 'y':
        success = wubuntu_kernel_dev.setup_kernel_development_environment()
        if success:
            print("内核开发环境设置成功！")
        else:
            print("内核开发环境设置失败。")
    else:
        print("跳过环境设置。")
    
    # 3. 创建内核模块模板
    print_section("创建内核模块模板")
    create_module = input("是否创建内核模块模板？(y/n): ")
    if create_module.lower() == 'y':
        module_name = input("请输入模块名称 (默认: hello_module): ") or "hello_module"
        author = input("请输入作者名称 (默认: Wubuntu User): ") or "Wubuntu User"
        description = input("请输入模块描述 (默认: A simple kernel module): ") or "A simple kernel module"
        
        # 创建目标目录
        target_dir = os.path.join(os.getcwd(), module_name)
        
        success = wubuntu_kernel_dev.create_kernel_module_template(
            target_dir=target_dir,
            module_name=module_name,
            author=author,
            description=description
        )
        
        if success:
            print(f"内核模块模板已创建在 {target_dir}")
            print("模板包含以下文件:")
            print(f" - {module_name}.c")
            print(" - Makefile")
            print(" - README.md")
            
            # 显示编译指南
            print("\n要编译此模块，请运行:")
            print(f"cd {target_dir}")
            print("make")
            print("\n要安装此模块，请运行:")
            print(f"sudo insmod {module_name}.ko")
            print("\n要卸载此模块，请运行:")
            print(f"sudo rmmod {module_name}")
        else:
            print("内核模块模板创建失败。")
    else:
        print("跳过模块创建。")
    
    # 4. 创建设备驱动模板
    print_section("创建设备驱动模板")
    create_driver = input("是否创建设备驱动模板？(y/n): ")
    if create_driver.lower() == 'y':
        driver_name = input("请输入驱动名称 (默认: sample_driver): ") or "sample_driver"
        author = input("请输入作者名称 (默认: Wubuntu User): ") or "Wubuntu User"
        description = input("请输入驱动描述 (默认: A sample character device driver): ") or "A sample character device driver"
        
        # 创建目标目录
        target_dir = os.path.join(os.getcwd(), driver_name)
        
        success = wubuntu_kernel_dev.create_device_driver_template(
            target_dir=target_dir,
            driver_name=driver_name,
            author=author,
            description=description
        )
        
        if success:
            print(f"设备驱动模板已创建在 {target_dir}")
            print("模板包含以下文件:")
            print(f" - {driver_name}.c")
            print(" - Makefile")
            print(" - README.md")
            print(" - test_driver.sh")
            
            # 显示编译指南
            print("\n要编译此驱动，请运行:")
            print(f"cd {target_dir}")
            print("make")
            print("\n要测试此驱动，请运行:")
            print("./test_driver.sh")
        else:
            print("设备驱动模板创建失败。")
    else:
        print("跳过驱动创建。")
    
    # 5. 创建系统服务
    print_section("创建系统服务")
    create_service = input("是否创建系统服务示例？(y/n): ")
    if create_service.lower() == 'y':
        service_name = input("请输入服务名称 (默认: sample-service): ") or "sample-service"
        description = input("请输入服务描述 (默认: Sample Wubuntu Service): ") or "Sample Wubuntu Service"
        
        # 创建简单的服务脚本
        script_dir = os.path.join(os.getcwd(), "services")
        os.makedirs(script_dir, exist_ok=True)
        
        script_path = os.path.join(script_dir, f"{service_name}.py")
        with open(script_path, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
# {service_name} - {description}
import time
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('/tmp/{service_name}.log')]
)
logger = logging.getLogger('{service_name}')

def main():
    logger.info('服务启动')
    try:
        while True:
            logger.info('服务运行中...')
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info('服务停止')

if __name__ == '__main__':
    main()
""")
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        # 创建系统服务
        success = wubuntu_kernel_dev.create_system_service(
            service_name=service_name,
            exec_path=script_path,
            description=description,
            user=os.environ.get('USER', 'root'),
            working_directory=script_dir,
            environment_vars={"PYTHONUNBUFFERED": "1"}
        )
        
        if success:
            print(f"系统服务 '{service_name}' 创建成功！")
            
            # 询问是否启用服务
            enable_service = input("是否启用并启动此服务？(y/n): ")
            if enable_service.lower() == 'y':
                wubuntu_kernel_dev.enable_system_service(service_name, start=True)
                print(f"服务已启用并启动。")
                
                # 显示服务状态
                time.sleep(2)  # 等待服务启动
                status = wubuntu_kernel_dev.get_system_service_status(service_name)
                print("\n服务状态:")
                print_json(status)
                
                print("\n服务日志将写入到: /tmp/{service_name}.log")
                print(f"要停止服务，请运行: sudo systemctl stop {service_name}")
            else:
                print(f"服务已创建但未启动。要手动启动，请运行: sudo systemctl start {service_name}")
        else:
            print("系统服务创建失败。")
    else:
        print("跳过服务创建。")
    
    # 6. 列出已加载的内核模块
    print_section("已加载的内核模块")
    modules = wubuntu_kernel_dev.get_loaded_kernel_modules()
    print(f"系统中已加载 {len(modules)} 个内核模块。")
    
    show_modules = input("是否显示前10个模块？(y/n): ")
    if show_modules.lower() == 'y':
        for i, module in enumerate(modules[:10]):
            print(f"{i+1}. {module['name']} (大小: {module['size']})")
            if module['used_by']:
                print(f"   被以下模块使用: {module['used_by']}")
    
    print("\n演示完成！")

if __name__ == "__main__":
    main() 