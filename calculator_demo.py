#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
优化版计算器示例
整合了多个计算器实现，提供模块化设计和完整的测试覆盖。
"""

import os
import sys
import math
import logging
import argparse
import statistics
from enum import Enum
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("calculator")

class CalculatorMode(Enum):
    """计算器模式枚举"""
    BASIC = "basic"          # 基本计算功能
    SCIENTIFIC = "scientific"  # 科学计算功能
    ADVANCED = "advanced"    # 高级功能

class CalculatorError(Exception):
    """计算器错误类型"""
    pass

class CalculatorMemory:
    """计算器内存管理类"""
    
    def __init__(self):
        """初始化内存"""
        self.value = 0
        self.history = []
        self.variables = {}
    
    def store(self, value: float) -> float:
        """存储值到内存"""
        self.value = value
        return value
    
    def recall(self) -> float:
        """从内存中读取值"""
        return self.value
    
    def clear(self) -> None:
        """清除内存"""
        old_value = self.value
        self.value = 0
        return old_value
    
    def add_to_memory(self, value: float) -> float:
        """将值加到内存中"""
        self.value += value
        return self.value
    
    def subtract_from_memory(self, value: float) -> float:
        """从内存中减去值"""
        self.value -= value
        return self.value
    
    def set_variable(self, name: str, value: float) -> float:
        """设置变量"""
        self.variables[name] = value
        return value
    
    def get_variable(self, name: str) -> float:
        """获取变量值"""
        if name not in self.variables:
            raise CalculatorError(f"变量 '{name}' 未定义")
        return self.variables[name]

class Calculator:
    """统一计算器类，支持基本、科学和高级模式"""
    
    def __init__(self, mode: CalculatorMode = CalculatorMode.BASIC):
        """初始化计算器"""
        self.mode = mode
        self.memory = CalculatorMemory()
        self.last_result = 0
        self.history = []
        self.register_standard_operations()
        logger.info(f"计算器已初始化，模式: {mode.value}")
    
    def register_standard_operations(self):
        """注册标准操作"""
        # 基本操作
        self._operations = {
            # 基本算术
            "add": self.add,
            "subtract": self.subtract,
            "multiply": self.multiply,
            "divide": self.divide,
            
            # 内存操作
            "memory_store": self.memory_store,
            "memory_recall": self.memory_recall,
            "memory_clear": self.memory_clear,
            "memory_add": self.memory_add,
            "memory_subtract": self.memory_subtract,
            
            # 科学计算
            "power": self.power,
            "square_root": self.square_root,
            "sin": self.sin,
            "cos": self.cos,
            "tan": self.tan,
            "log10": self.log10,
            "ln": self.ln,
            "factorial": self.factorial,
            
            # 统计函数
            "mean": self.mean,
            "median": self.median,
            "std_dev": self.std_dev,
            
            # 杂项
            "reset": self.reset,
        }
    
    def validate_mode(self, required_mode: CalculatorMode):
        """验证当前模式是否满足要求"""
        if self.mode == CalculatorMode.BASIC and required_mode != CalculatorMode.BASIC:
            raise CalculatorError(f"此操作需要 {required_mode.value} 模式，当前模式为 {self.mode.value}")
    
    def record_operation(self, operation_str: str):
        """记录操作到历史记录"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append(f"[{timestamp}] {operation_str}")
        logger.debug(f"记录操作: {operation_str}")
    
    def get_operation(self, name: str) -> Callable:
        """获取操作函数"""
        if name not in self._operations:
            raise CalculatorError(f"未知操作: {name}")
        return self._operations[name]
    
    def call(self, operation: str, *args, **kwargs) -> float:
        """调用指定操作"""
        func = self.get_operation(operation)
        result = func(*args, **kwargs)
        self.last_result = result
        return result
    
    # 基本操作
    def add(self, a: float, b: Optional[float] = None) -> float:
        """加法"""
        if b is None:
            b = self.last_result
        
        result = a + b
        self.record_operation(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: Optional[float] = None) -> float:
        """减法"""
        if b is None:
            b = a
            a = self.last_result
        
        result = a - b
        self.record_operation(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: float, b: Optional[float] = None) -> float:
        """乘法"""
        if b is None:
            b = a
            a = self.last_result
        
        result = a * b
        self.record_operation(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: float, b: Optional[float] = None) -> float:
        """除法"""
        if b is None:
            b = a
            a = self.last_result
        
        if b == 0:
            error_msg = f"{a} / {b} = 错误: 除以零"
            self.record_operation(error_msg)
            raise CalculatorError("不能除以零")
        
        result = a / b
        self.record_operation(f"{a} / {b} = {result}")
        return result
    
    # 内存操作
    def memory_store(self) -> float:
        """存储结果到内存"""
        result = self.memory.store(self.last_result)
        self.record_operation(f"M+ = {result}")
        return result
    
    def memory_recall(self) -> float:
        """从内存中读取值"""
        result = self.memory.recall()
        self.record_operation(f"MR = {result}")
        self.last_result = result
        return result
    
    def memory_clear(self) -> float:
        """清除内存"""
        old_value = self.memory.clear()
        self.record_operation(f"MC (was {old_value})")
        return 0
    
    def memory_add(self, value: Optional[float] = None) -> float:
        """向内存中添加值"""
        if value is None:
            value = self.last_result
        
        result = self.memory.add_to_memory(value)
        self.record_operation(f"M+ {value} = {result}")
        return result
    
    def memory_subtract(self, value: Optional[float] = None) -> float:
        """从内存中减去值"""
        if value is None:
            value = self.last_result
        
        result = self.memory.subtract_from_memory(value)
        self.record_operation(f"M- {value} = {result}")
        return result
    
    # 科学计算函数
    def power(self, base: float, exponent: Optional[float] = None) -> float:
        """幂运算"""
        self.validate_mode(CalculatorMode.SCIENTIFIC)
        
        if exponent is None:
            exponent = base
            base = self.last_result
        
        try:
            result = math.pow(base, exponent)
            self.record_operation(f"{base} ^ {exponent} = {result}")
            return result
        except Exception as e:
            error_msg = f"{base} ^ {exponent} = 错误: {str(e)}"
            self.record_operation(error_msg)
            raise CalculatorError(f"幂运算错误: {str(e)}")
    
    def square_root(self, value: Optional[float] = None) -> float:
        """平方根"""
        self.validate_mode(CalculatorMode.SCIENTIFIC)
        
        if value is None:
            value = self.last_result
        
        if value < 0:
            error_msg = f"sqrt({value}) = 错误: 负数输入"
            self.record_operation(error_msg)
            raise CalculatorError("不能计算负数的平方根")
        
        result = math.sqrt(value)
        self.record_operation(f"sqrt({value}) = {result}")
        return result
    
    def sin(self, angle_degrees: Optional[float] = None) -> float:
        """正弦函数"""
        self.validate_mode(CalculatorMode.SCIENTIFIC)
        
        if angle_degrees is None:
            angle_degrees = self.last_result
        
        angle_rad = math.radians(angle_degrees)
        result = math.sin(angle_rad)
        self.record_operation(f"sin({angle_degrees}°) = {result}")
        return result
    
    def cos(self, angle_degrees: Optional[float] = None) -> float:
        """余弦函数"""
        self.validate_mode(CalculatorMode.SCIENTIFIC)
        
        if angle_degrees is None:
            angle_degrees = self.last_result
        
        angle_rad = math.radians(angle_degrees)
        result = math.cos(angle_rad)
        self.record_operation(f"cos({angle_degrees}°) = {result}")
        return result
    
    def tan(self, angle_degrees: Optional[float] = None) -> float:
        """正切函数"""
        self.validate_mode(CalculatorMode.SCIENTIFIC)
        
        if angle_degrees is None:
            angle_degrees = self.last_result
        
        # 检查是否在无效值附近
        if abs(angle_degrees % 180 - 90) < 1e-10:
            error_msg = f"tan({angle_degrees}°) = 错误: 无定义"
            self.record_operation(error_msg)
            raise CalculatorError("正切在90°、270°等处无定义")
        
        angle_rad = math.radians(angle_degrees)
        result = math.tan(angle_rad)
        self.record_operation(f"tan({angle_degrees}°) = {result}")
        return result
    
    def log10(self, value: Optional[float] = None) -> float:
        """常用对数"""
        self.validate_mode(CalculatorMode.SCIENTIFIC)
        
        if value is None:
            value = self.last_result
        
        if value <= 0:
            error_msg = f"log10({value}) = 错误: 非正输入"
            self.record_operation(error_msg)
            raise CalculatorError("不能计算非正数的对数")
        
        result = math.log10(value)
        self.record_operation(f"log10({value}) = {result}")
        return result
    
    def ln(self, value: Optional[float] = None) -> float:
        """自然对数"""
        self.validate_mode(CalculatorMode.SCIENTIFIC)
        
        if value is None:
            value = self.last_result
        
        if value <= 0:
            error_msg = f"ln({value}) = 错误: 非正输入"
            self.record_operation(error_msg)
            raise CalculatorError("不能计算非正数的对数")
        
        result = math.log(value)
        self.record_operation(f"ln({value}) = {result}")
        return result
    
    def factorial(self, n: Optional[int] = None) -> float:
        """阶乘"""
        self.validate_mode(CalculatorMode.SCIENTIFIC)
        
        if n is None:
            n = int(self.last_result)
        
        if not isinstance(n, int) or n < 0:
            error_msg = f"{n}! = 错误: 无效输入"
            self.record_operation(error_msg)
            raise CalculatorError("阶乘只对非负整数有定义")
        
        result = math.factorial(n)
        self.record_operation(f"{n}! = {result}")
        return result
    
    # 统计函数
    def mean(self, values: List[float]) -> float:
        """计算平均值"""
        self.validate_mode(CalculatorMode.ADVANCED)
        
        if not values:
            raise CalculatorError("不能计算空列表的平均值")
        
        result = statistics.mean(values)
        self.record_operation(f"mean{values} = {result}")
        return result
    
    def median(self, values: List[float]) -> float:
        """计算中位数"""
        self.validate_mode(CalculatorMode.ADVANCED)
        
        if not values:
            raise CalculatorError("不能计算空列表的中位数")
        
        result = statistics.median(values)
        self.record_operation(f"median{values} = {result}")
        return result
    
    def std_dev(self, values: List[float]) -> float:
        """计算标准差"""
        self.validate_mode(CalculatorMode.ADVANCED)
        
        if not values or len(values) < 2:
            raise CalculatorError("标准差至少需要两个值")
        
        result = statistics.stdev(values)
        self.record_operation(f"std_dev{values} = {result}")
        return result
    
    # 工具函数
    def reset(self) -> float:
        """重置计算器"""
        old_result = self.last_result
        self.last_result = 0
        self.record_operation(f"重置 (上一结果: {old_result})")
        return 0
    
    def get_history(self, last_n: Optional[int] = None) -> List[str]:
        """获取历史记录"""
        if last_n is not None and last_n > 0:
            return self.history[-last_n:]
        return self.history
    
    def clear_history(self) -> None:
        """清除历史记录"""
        self.history = []
        self.record_operation("历史记录已清除")
    
    def set_mode(self, mode: CalculatorMode) -> None:
        """设置计算器模式"""
        old_mode = self.mode
        self.mode = mode
        self.record_operation(f"模式已从 {old_mode.value} 更改为 {mode.value}")
        logger.info(f"计算器模式已更改: {old_mode.value} -> {mode.value}")

def run_demo(mode: str = "scientific"):
    """运行计算器演示"""
    print("\n========================================")
    print(f"     计算器演示 ({mode.upper()} 模式)")
    print("========================================")
    
    # 确定模式
    try:
        calc_mode = CalculatorMode(mode.lower())
    except ValueError:
        print(f"错误: 无效的模式 '{mode}'，使用默认的科学模式")
        calc_mode = CalculatorMode.SCIENTIFIC
    
    # 创建计算器
    calc = Calculator(calc_mode)
    
    # 执行演示操作
    try:
        print("\n--- 基本操作 ---")
        print(f"加法: 5 + 3 = {calc.add(5, 3)}")
        print(f"减法: 10 - 4 = {calc.subtract(10, 4)}")
        print(f"乘法: 6 * 7 = {calc.multiply(6, 7)}")
        print(f"除法: 20 / 4 = {calc.divide(20, 4)}")
        
        print("\n--- 链式操作 ---")
        print(f"起始值: {calc.last_result}")
        print(f"加10: {calc.add(10)}")
        print(f"乘以2: {calc.multiply(2)}")
        print(f"减5: {calc.subtract(5)}")
        print(f"除以3: {calc.divide(3)}")
        
        if calc_mode != CalculatorMode.BASIC:
            print("\n--- 科学运算 ---")
            print(f"幂运算: 2^3 = {calc.power(2, 3)}")
            print(f"平方根: sqrt(16) = {calc.square_root(16)}")
            print(f"正弦: sin(30°) = {calc.sin(30)}")
            print(f"余弦: cos(60°) = {calc.cos(60)}")
            print(f"正切: tan(45°) = {calc.tan(45)}")
            print(f"常用对数: log10(100) = {calc.log10(100)}")
            print(f"自然对数: ln(e) = {calc.ln(math.e)}")
            print(f"阶乘: 5! = {calc.factorial(5)}")
        
        if calc_mode == CalculatorMode.ADVANCED:
            print("\n--- 统计运算 ---")
            data = [4, 7, 2, 9, 6, 3, 5]
            print(f"样本数据: {data}")
            print(f"平均值: {calc.mean(data)}")
            print(f"中位数: {calc.median(data)}")
            print(f"标准差: {calc.std_dev(data)}")
        
        print("\n--- 内存操作 ---")
        calc.add(42, 0)  # 设置 last_result 为 42
        print(f"存入内存: {calc.memory_store()}")
        calc.add(10, 20)
        print(f"当前结果: {calc.last_result}")
        print(f"从内存读取: {calc.memory_recall()}")
        print(f"读取后，last_result = {calc.last_result}")
        print(f"向内存加5: {calc.memory_add(5)}")
        print(f"从内存减2: {calc.memory_subtract(2)}")
        print(f"清除内存: {calc.memory_clear()}")
        
        print("\n--- 错误处理 ---")
        try:
            print("尝试除以零:")
            calc.divide(10, 0)
        except CalculatorError as e:
            print(f"  捕获错误: {e}")
        
        try:
            print("尝试计算负数的平方根:")
            calc.square_root(-1)
        except CalculatorError as e:
            print(f"  捕获错误: {e}")
        
        try:
            print("尝试计算90度的正切值:")
            calc.tan(90)
        except CalculatorError as e:
            print(f"  捕获错误: {e}")
        
        print("\n--- 历史记录 ---")
        print("最后10条操作:")
        for i, entry in enumerate(calc.get_history(10), 1):
            print(f"{i}. {entry}")
        
    except Exception as e:
        print(f"演示过程中出错: {e}")
    
    print("\n演示完成!")
    return calc  # 返回计算器对象，方便在交互式环境中进一步探索

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="计算器演示程序")
    parser.add_argument(
        "--mode", 
        choices=["basic", "scientific", "advanced"],
        default="scientific",
        help="计算器模式 (默认: scientific)"
    )
    parser.add_argument(
        "--output",
        help="将输出保存到文件"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="启用详细日志"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 如果需要保存到文件，重定向标准输出
    if args.output:
        original_stdout = sys.stdout
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                sys.stdout = f
                run_demo(args.mode)
            sys.stdout = original_stdout
            print(f"输出已保存到 {args.output}")
        except Exception as e:
            sys.stdout = original_stdout
            print(f"保存输出时出错: {e}")
    else:
        run_demo(args.mode)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 