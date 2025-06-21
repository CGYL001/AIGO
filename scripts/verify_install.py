#!/usr/bin/env python
"""
验证AIgo安装是否正确的脚本。

此脚本尝试导入AIgo包并验证其功能。
"""

import sys
import os
import importlib
from pathlib import Path

def check_import():
    """检查是否可以导入AIgo包"""
    print("检查AIgo包导入...")
    
    try:
        import aigo
        print(f"✓ 成功导入AIgo包，版本：{aigo.__version__}")
        print(f"  安装路径：{aigo.__file__}")
        return True
    except ImportError as e:
        print(f"✗ 导入AIgo包失败：{e}")
        return False


def check_submodules():
    """检查AIgo子模块导入"""
    print("\n检查AIgo子模块导入...")
    
    modules = [
        "aigo.models.base",
        "aigo.models.manager",
        "aigo.models.adapters",
        "aigo.models.providers.ollama_runner",
        "aigo.models.providers.openai_runner",
        "aigo.cli.__main__",
        "aigo.runtime.api_server"
    ]
    
    success = True
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            print(f"✓ 成功导入 {module_name}")
        except ImportError as e:
            print(f"✗ 导入 {module_name} 失败：{e}")
            success = False
    
    return success


def check_functionality():
    """检查基本功能"""
    print("\n检查基本功能...")
    
    try:
        from aigo.models.base import ModelConfig
        
        # 创建配置
        config = ModelConfig(
            provider="ollama",
            model_name="test-model"
        )
        
        print(f"✓ 成功创建ModelConfig实例：{config}")
        return True
    except Exception as e:
        print(f"✗ 功能检查失败：{e}")
        return False


def check_package_structure():
    """检查包结构"""
    print("\n检查包结构...")
    
    try:
        import aigo
        package_dir = Path(aigo.__file__).parent
        
        # 检查关键文件
        files = [
            "__init__.py",
            "models/__init__.py",
            "models/base.py",
            "models/manager.py",
            "models/providers/__init__.py",
            "cli/__init__.py",
            "runtime/__init__.py"
        ]
        
        for file in files:
            path = package_dir / file
            if path.exists():
                print(f"✓ 文件存在：{file}")
            else:
                print(f"✗ 文件缺失：{file}")
        
        return True
    except Exception as e:
        print(f"✗ 包结构检查失败：{e}")
        return False


def check_installation_method():
    """检查安装方式"""
    print("\n检查安装方式...")
    
    try:
        import aigo
        import site
        
        package_dir = Path(aigo.__file__).parent
        site_packages = [Path(p) for p in site.getsitepackages()]
        
        # 检查是否在site-packages中
        in_site_packages = any(package_dir.is_relative_to(p) for p in site_packages)
        
        if in_site_packages:
            print(f"✓ AIgo作为包安装在：{package_dir}")
        else:
            print(f"✓ AIgo作为开发模式安装：{package_dir}")
            
        return True
    except Exception as e:
        print(f"✗ 安装方式检查失败：{e}")
        return False


def main():
    """主函数"""
    print("AIgo安装验证")
    print("============\n")
    
    # 检查Python版本
    print(f"Python版本：{sys.version}")
    print(f"Python路径：{sys.executable}")
    print(f"工作目录：{os.getcwd()}")
    print()
    
    # 运行检查
    import_ok = check_import()
    
    if import_ok:
        modules_ok = check_submodules()
        func_ok = check_functionality()
        struct_ok = check_package_structure()
        install_ok = check_installation_method()
        
        # 总结
        print("\n验证结果")
        print("========")
        print(f"导入检查：{'通过' if import_ok else '失败'}")
        print(f"子模块检查：{'通过' if modules_ok else '失败'}")
        print(f"功能检查：{'通过' if func_ok else '失败'}")
        print(f"结构检查：{'通过' if struct_ok else '失败'}")
        print(f"安装检查：{'通过' if install_ok else '失败'}")
        
        if all([import_ok, modules_ok, func_ok, struct_ok, install_ok]):
            print("\n✓ AIgo安装验证通过！")
            return 0
        else:
            print("\n✗ AIgo安装验证失败。请检查上述错误。")
            return 1
    else:
        print("\n✗ 无法导入AIgo包，验证终止。")
        
        # 提供解决方案
        print("\n可能的解决方案：")
        print("1. 确保已安装AIgo：pip install -e .")
        print("2. 检查PYTHONPATH环境变量是否包含项目根目录")
        print("3. 尝试创建或修复setup.py文件")
        print("4. 检查是否所有必要的__init__.py文件都存在")
        
        return 1


if __name__ == "__main__":
    sys.exit(main()) 