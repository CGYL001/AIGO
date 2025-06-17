"""
直接测试仓库管理器
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接导入模块
from src.modules.repo_integration.repo_manager import RepoManager

def main():
    """主函数"""
    try:
        # 创建仓库管理器实例
        repo_manager = RepoManager()
        
        # 获取支持的平台
        platforms = repo_manager.get_platforms()
        print(f"支持的平台: {platforms}")
        
        print("测试成功!")
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    main() 