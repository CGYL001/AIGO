"""
跨平台进程管理工具 - 处理不同操作系统的进程操作

提供统一的进程管理API，处理不同操作系统间的差异。
"""

import os
import sys
import signal
import subprocess
import time
from typing import List, Dict, Any, Optional, Union, Tuple

from .detection import is_windows, is_linux, is_macos

def run_background_process(
    command: Union[str, List[str]],
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None
) -> int:
    """
    在后台运行进程
    
    参数:
        command: 要执行的命令（字符串或参数列表）
        cwd: 工作目录
        env: 环境变量
        stdout: 标准输出重定向路径
        stderr: 标准错误重定向路径
        
    返回:
        进程ID
    """
    # 合并当前环境变量和指定的环境变量
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    
    # 准备标准输出和标准错误的重定向
    stdout_file = None
    stderr_file = None
    
    try:
        if stdout:
            stdout_file = open(stdout, 'w')
        if stderr:
            stderr_file = open(stderr, 'w')
        
        # 在Windows上运行
        if is_windows():
            # 使用subprocess.PIPE避免控制台窗口出现
            startupinfo = None
            if hasattr(subprocess, 'STARTUPINFO'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE
            
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=process_env,
                stdout=stdout_file or subprocess.PIPE,
                stderr=stderr_file or subprocess.PIPE,
                stdin=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        # 在类Unix系统上运行
        else:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=process_env,
                stdout=stdout_file or subprocess.PIPE,
                stderr=stderr_file or subprocess.PIPE,
                stdin=subprocess.PIPE,
                start_new_session=True  # 在新会话中启动以便与父进程分离
            )
            
        return process.pid
        
    finally:
        # 清理文件句柄
        if stdout_file:
            stdout_file.close()
        if stderr_file:
            stderr_file.close()

def kill_process(pid: int, force: bool = False) -> bool:
    """
    终止指定的进程
    
    参数:
        pid: 进程ID
        force: 是否强制终止
        
    返回:
        如果成功终止进程则返回True，否则返回False
    """
    try:
        if is_windows():
            # Windows上使用taskkill
            if force:
                subprocess.check_call(['taskkill', '/F', '/PID', str(pid)])
            else:
                subprocess.check_call(['taskkill', '/PID', str(pid)])
        else:
            # 在Unix/Linux上使用kill
            os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)
            
        # 等待进程终止
        max_wait = 5  # 最多等待5秒
        while max_wait > 0:
            try:
                # 尝试查询进程状态，如果进程不存在将引发异常
                if is_windows():
                    subprocess.check_call(
                        ['tasklist', '/FI', f'PID eq {pid}'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE
                    )
                else:
                    os.kill(pid, 0)  # 信号0用于检查进程是否存在
                # 如果没有异常，进程还在运行，等待一段时间
                time.sleep(0.5)
                max_wait -= 0.5
            except (subprocess.CalledProcessError, ProcessLookupError, OSError):
                # 进程已经终止
                return True
                
        # 如果经过等待后进程仍然存在，尝试强制终止
        if not force:
            return kill_process(pid, force=True)
        
        return False
    except Exception:
        return False

def is_process_running(pid: int) -> bool:
    """
    检查进程是否仍在运行
    
    参数:
        pid: 进程ID
        
    返回:
        如果进程正在运行则返回True，否则返回False
    """
    try:
        if is_windows():
            # Windows上使用tasklist检查进程
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}', '/NH'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return str(pid) in result.stdout
        else:
            # Unix/Linux上使用信号0检查进程
            os.kill(pid, 0)
            return True
    except (subprocess.SubprocessError, ProcessLookupError, OSError):
        return False

def get_process_info(pid: int) -> Optional[Dict[str, Any]]:
    """
    获取进程信息
    
    参数:
        pid: 进程ID
        
    返回:
        包含进程信息的字典，如果进程不存在则返回None
    """
    if not is_process_running(pid):
        return None
    
    info = {'pid': pid}
    
    try:
        if is_windows():
            # Windows上使用wmic获取详细信息
            result = subprocess.run(
                ['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 'CommandLine,ExecutablePath,Name,WorkingSetSize', '/format:csv'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:  # 跳过标题行
                parts = lines[1].split(',')
                if len(parts) >= 5:
                    info['command'] = parts[1]
                    info['executable'] = parts[2]
                    info['name'] = parts[3]
                    info['memory'] = int(parts[4]) if parts[4].strip() else 0
        else:
            # Unix/Linux上读取/proc文件系统
            if os.path.exists(f'/proc/{pid}'):
                # 读取命令行
                with open(f'/proc/{pid}/cmdline', 'rb') as f:
                    cmdline = f.read().decode('utf-8', errors='replace').replace('\x00', ' ').strip()
                    info['command'] = cmdline
                
                # 读取可执行文件路径
                if os.path.exists(f'/proc/{pid}/exe'):
                    try:
                        info['executable'] = os.readlink(f'/proc/{pid}/exe')
                    except:
                        pass
                
                # 读取进程名
                with open(f'/proc/{pid}/comm', 'r') as f:
                    info['name'] = f.read().strip()
                
                # 读取内存使用情况
                with open(f'/proc/{pid}/status', 'r') as f:
                    for line in f:
                        if line.startswith('VmRSS:'):
                            # 物理内存使用量（kB）
                            memory_kb = int(line.split()[1])
                            info['memory'] = memory_kb * 1024
                            break
    except Exception:
        pass
        
    return info 