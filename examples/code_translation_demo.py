#!/usr/bin/env python3
"""
代码语言转换器演示

本示例演示如何使用AIgo的代码语言转换器功能来转换不同编程语言之间的代码。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from aigo.adapters.code_translation import (
    get_translator,
    list_available_translators,
    TranslationConfig
)

def print_header(text):
    """打印带有装饰的标题"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "-"))
    print("=" * 80 + "\n")

def display_available_translators():
    """显示所有可用的代码转换器"""
    print_header("可用的代码转换器")
    translators = list_available_translators()
    
    if not translators:
        print("当前没有可用的代码转换器")
        return
    
    print(f"找到 {len(translators)} 个代码转换器:")
    for i, (src, target) in enumerate(translators, 1):
        print(f"{i}. {src} -> {target}")
    print()

def python_to_javascript_demo():
    """Python到JavaScript代码转换示例"""
    print_header("Python到JavaScript代码转换")
    
    # 获取Python到JavaScript的转换器
    translator = get_translator('python', 'javascript')
    
    if not translator:
        print("未找到Python到JavaScript的转换器")
        return
    
    # 设置转换配置
    config = TranslationConfig(
        preserve_comments=True,
        preserve_formatting=True,
        use_language_idioms=True,
        custom_settings={"style": "modern"}  # 使用现代JavaScript语法（ES6+）
    )
    
    # 示例Python代码
    python_code = '''
# 一个简单的Python类示例
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        """返回问候语"""
        return f"你好，我是{self.name}，今年{self.age}岁"
    
    def is_adult(self):
        return self.age >= 18

# 创建实例并使用
person = Person("张三", 30)
greeting = person.greet()
print(greeting)

if person.is_adult():
    print(f"{person.name}是成年人")
else:
    print(f"{person.name}是未成年人")
'''
    
    # 转换代码
    result = translator.translate(python_code)
    
    # 显示结果
    print("原始Python代码:")
    print("-" * 40)
    print(python_code)
    print("-" * 40)
    print("\n转换后的JavaScript代码:")
    print("-" * 40)
    print(result.translated_code)
    print("-" * 40)
    
    # 显示警告和注意事项
    if result.warnings:
        print("\n转换警告:")
        for warning in result.warnings:
            print(f"- {warning}")

def main():
    """主函数"""
    print_header("AIgo代码语言转换器演示")
    
    # 显示所有可用的转换器
    display_available_translators()
    
    # 演示Python到JavaScript的转换
    python_to_javascript_demo()
    
    print("\n演示完成！")

if __name__ == "__main__":
    main() 