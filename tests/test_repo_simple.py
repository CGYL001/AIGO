"""
仓库集成功能的简化测试
"""

import os
import sys
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# 确保可以导入src模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_repo_manager_basic():
    """测试仓库管理器的基本功能"""
    from src.modules.repo_integration.repo_manager import RepoManager
    
    with patch('src.modules.repo_integration.repo_manager.GitHubAdapter') as mock_github:
        with patch('src.modules.repo_integration.repo_manager.GitLabAdapter') as mock_gitlab:
            with patch('src.modules.repo_integration.repo_manager.GiteeAdapter') as mock_gitee:
                # 设置模拟适配器
                mock_github.return_value.get_platform_name.return_value = "GitHub"
                mock_github.return_value.get_api_url.return_value = "https://api.github.com"
                mock_github.return_value.get_auth_method.return_value = "token"
                mock_github.return_value.is_authenticated.return_value = True
                
                # 创建临时目录作为仓库存储路径
                with patch('src.utils.config.get') as mock_config:
                    mock_config.return_value = {
                        "platforms": {
                            "github": {"enabled": True, "api_url": "https://api.github.com"},
                            "gitlab": {"enabled": True, "api_url": "https://gitlab.com/api/v4"},
                            "gitee": {"enabled": True, "api_url": "https://gitee.com/api/v5"}
                        }
                    }
                    
                    # 创建测试用临时目录
                    temp_dir = tempfile.mkdtemp(prefix="test_repo_")
                    
                    try:
                        # 覆盖本地仓库路径
                        with patch.object(Path, 'mkdir'):
                            with patch.object(RepoManager, '_local_repo_path', Path(temp_dir)):
                                manager = RepoManager()
                                manager._adapters["github"] = mock_github.return_value
                                manager._adapters["gitlab"] = mock_gitlab.return_value
                                manager._adapters["gitee"] = mock_gitee.return_value
                                
                                # 测试获取平台列表
                                platforms = manager.get_platforms()
                                assert len(platforms) == 3
                                assert "github" in platforms
                                assert "gitlab" in platforms
                                assert "gitee" in platforms
                                
                                # 测试检查平台是否支持
                                assert manager.is_platform_supported("github") == True
                                assert manager.is_platform_supported("bitbucket") == False
                                
                                # 测试获取平台信息
                                github_info = manager.get_platform_info("github")
                                assert github_info["name"] == "GitHub"
                                assert github_info["api_url"] == "https://api.github.com"
                                assert github_info["authenticated"] == True
                    finally:
                        # 测试完成后清理临时目录
                        shutil.rmtree(temp_dir)

async def test_repo_manager_async():
    """测试仓库管理器的异步功能"""
    from src.modules.repo_integration.repo_manager import RepoManager
    
    with patch('src.modules.repo_integration.repo_manager.GitHubAdapter') as mock_github:
        adapter = MagicMock()
        adapter.authenticate = AsyncMock(return_value=(True, "认证成功"))
        mock_github.return_value = adapter
        
        with patch('src.utils.config.get') as mock_config:
            mock_config.return_value = {
                "platforms": {
                    "github": {"enabled": True, "api_url": "https://api.github.com"}
                }
            }
            
            with patch.object(Path, 'mkdir'):
                manager = RepoManager()
                manager._adapters["github"] = adapter
                
                # 测试认证
                success, message = await manager.authenticate("github", {"token": "test_token"})
                assert success == True
                assert message == "认证成功"
                adapter.authenticate.assert_called_once_with({"token": "test_token"})

def run_tests():
    """运行测试"""
    # 运行同步测试
    test_repo_manager_basic()
    
    # 运行异步测试
    asyncio.run(test_repo_manager_async())
    
    print("所有测试通过!")

if __name__ == "__main__":
    run_tests() 