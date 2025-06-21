#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
异步操作工具

提供异步操作相关的工具函数和装饰器，如重试机制、并发控制等
"""

import asyncio
import functools
import logging
import time
from typing import Callable, TypeVar, Any, Optional, Dict, List, Union, Tuple, Coroutine, cast

logger = logging.getLogger(__name__)

T = TypeVar('T')

def retry(max_attempts: int = 3, 
          delay: float = 1.0, 
          backoff_factor: float = 2.0,
          exceptions: Tuple[Exception, ...] = (Exception,),
          logger_name: Optional[str] = None):
    """
    异步函数重试装饰器
    
    Args:
        max_attempts: 最大尝试次数
        delay: 初始重试延迟(秒)
        backoff_factor: 退避因子，每次重试后延迟时间乘以此因子
        exceptions: 需要捕获的异常类型
        logger_name: 日志记录器名称，如果为None则使用默认日志记录器
    
    Returns:
        装饰器函数
    """
    local_logger = logging.getLogger(logger_name) if logger_name else logger
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        local_logger.warning(
                            f"尝试 {attempt}/{max_attempts} 失败: {str(e)}. "
                            f"{current_delay:.1f}秒后重试..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        local_logger.error(
                            f"所有 {max_attempts} 次尝试均失败: {str(e)}"
                        )
            
            # 所有尝试都失败
            raise last_exception
        
        return wrapper
    
    return decorator

def sync_retry(max_attempts: int = 3, 
              delay: float = 1.0, 
              backoff_factor: float = 2.0,
              exceptions: Tuple[Exception, ...] = (Exception,),
              logger_name: Optional[str] = None):
    """
    同步函数重试装饰器
    
    Args:
        max_attempts: 最大尝试次数
        delay: 初始重试延迟(秒)
        backoff_factor: 退避因子，每次重试后延迟时间乘以此因子
        exceptions: 需要捕获的异常类型
        logger_name: 日志记录器名称，如果为None则使用默认日志记录器
    
    Returns:
        装饰器函数
    """
    local_logger = logging.getLogger(logger_name) if logger_name else logger
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        local_logger.warning(
                            f"尝试 {attempt}/{max_attempts} 失败: {str(e)}. "
                            f"{current_delay:.1f}秒后重试..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        local_logger.error(
                            f"所有 {max_attempts} 次尝试均失败: {str(e)}"
                        )
            
            # 所有尝试都失败
            raise last_exception
        
        return wrapper
    
    return decorator

async def gather_with_concurrency(n: int, *tasks):
    """
    控制并发数量的异步任务收集器
    
    Args:
        n: 最大并发数
        tasks: 要执行的异步任务列表
    
    Returns:
        任务结果列表
    """
    semaphore = asyncio.Semaphore(n)
    
    async def sem_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(*(sem_task(task) for task in tasks))

class AsyncBatch:
    """异步批处理工具类"""
    
    def __init__(self, batch_size: int = 10, max_concurrency: int = 5):
        """
        初始化批处理工具
        
        Args:
            batch_size: 每批处理的项目数
            max_concurrency: 最大并发数
        """
        self.batch_size = batch_size
        self.max_concurrency = max_concurrency
    
    async def process(self, items: List[Any], process_func: Callable[[Any], Any]) -> List[Any]:
        """
        批量处理项目
        
        Args:
            items: 要处理的项目列表
            process_func: 处理单个项目的异步函数
        
        Returns:
            处理结果列表
        """
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_tasks = [process_func(item) for item in batch]
            batch_results = await gather_with_concurrency(self.max_concurrency, *batch_tasks)
            results.extend(batch_results)
        
        return results

async def with_timeout(coro, timeout: float, default=None):
    """
    为异步操作添加超时控制
    
    Args:
        coro: 异步协程
        timeout: 超时时间(秒)
        default: 超时时返回的默认值
    
    Returns:
        协程的结果或超时时的默认值
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"操作超时 ({timeout}秒)")
        return default 

def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """运行异步协程
    
    Args:
        coro: 要运行的协程
    
    Returns:
        T: 协程的返回值
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # 如果没有事件循环，创建一个新的
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def async_timeout(timeout: float):
    """异步超时装饰器
    
    Args:
        timeout: 超时时间（秒）
    
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout)
            except asyncio.TimeoutError:
                logger.warning(f"函数 {func.__name__} 执行超时 (>{timeout}秒)")
                raise TimeoutError(f"函数 {func.__name__} 执行超时")
        return wrapper
    return decorator

async def retry_async(func, *args, retries=3, delay=1.0, backoff=2.0, **kwargs):
    """带重试的异步函数执行器
    
    Args:
        func: 要执行的异步函数
        *args: 函数参数
        retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟时间的增长因子
        **kwargs: 函数关键字参数
    
    Returns:
        Any: 函数的返回值
    
    Raises:
        Exception: 如果所有重试都失败，则抛出最后一个异常
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(retries + 1):
        try:
            if attempt > 0:
                logger.info(f"重试 {attempt}/{retries}，延迟 {current_delay:.2f}秒")
                await asyncio.sleep(current_delay)
                current_delay *= backoff
            
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logger.warning(f"尝试 {attempt + 1}/{retries + 1} 失败: {str(e)}")
    
    raise last_exception

def sync_to_async(func: Callable) -> Callable:
    """将同步函数转换为异步函数
    
    Args:
        func: 同步函数
    
    Returns:
        Callable: 异步包装函数
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

def timed_async(func: Callable) -> Callable:
    """异步函数计时装饰器
    
    Args:
        func: 要计时的异步函数
    
    Returns:
        Callable: 装饰后的函数
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.debug(f"函数 {func.__name__} 执行耗时: {elapsed:.4f}秒")
        return result
    return wrapper 