"""
仓库集成功能测试

测试仓库管理和权限功能的各项功能
"""

import os
import sys
import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# 确保可以导入src模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.repo_integration.repo_manager import RepoManager
from src.services import auth_service
from src.services.repo_permission_service import RepoPermissionService

class TestRepoIntegration:
    """仓库集成功能测试"""
    
    @pytest.fixture
    def repo_manager(self):
        """创建RepoManager实例"""
        with patch('src.modules.repo_integration.repo_manager.GitHubAdapter') as mock_github:
            with patch('src.modules.repo_integration.repo_manager.GitLabAdapter') as mock_gitlab:
                with patch('src.modules.repo_integration.repo_manager.GiteeAdapter') as mock_gitee:
                    # 设置模拟适配器
                    mock_github.return_value.get_platform_name.return_value = "GitHub"
                    mock_github.return_value.get_api_url.return_value = "https://api.github.com"
                    mock_github.return_value.get_auth_method.return_value = "token"
                    mock_github.return_value.is_authenticated.return_value = True
                    
                    mock_gitlab.return_value.get_platform_name.return_value = "GitLab"
                    mock_gitlab.return_value.get_api_url.return_value = "https://gitlab.com/api/v4"
                    mock_gitlab.return_value.get_auth_method.return_value = "token"
                    mock_gitlab.return_value.is_authenticated.return_value = False
                    
                    mock_gitee.return_value.get_platform_name.return_value = "Gitee"
                    mock_gitee.return_value.get_api_url.return_value = "https://gitee.com/api/v5"
                    mock_gitee.return_value.get_auth_method.return_value = "token"
                    mock_gitee.return_value.is_authenticated.return_value = False
                    
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
                                    
                                    # 模拟会话设置
                                    session_id = "test_session_123"
                                    manager.set_session(session_id)
                                    
                                    yield manager
                        finally:
                            # 测试完成后清理临时目录
                            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def auth_service_mock(self):
        """模拟权限服务"""
        with patch('src.services.auth_service.AuthorizationService') as mock_auth:
            # 设置默认返回值
            instance = mock_auth.return_value
            instance.check_authorization.return_value = (False, "操作已授权")
            instance.get_current_mode.return_value = "strict"
            instance.get_trust_status.return_value = {
                "trusted": False,
                "confirm_count": 0,
                "required_count": 3
            }
            
            yield instance
    
    @pytest.mark.asyncio
    async def test_get_platforms(self, repo_manager):
        """测试获取支持的平台列表"""
        platforms = repo_manager.get_platforms()
        assert len(platforms) == 3
        assert "github" in platforms
        assert "gitlab" in platforms
        assert "gitee" in platforms
        
    @pytest.mark.asyncio
    async def test_is_platform_supported(self, repo_manager):
        """测试检查平台是否支持"""
        assert repo_manager.is_platform_supported("github") == True
        assert repo_manager.is_platform_supported("gitlab") == True
        assert repo_manager.is_platform_supported("bitbucket") == False
        
    @pytest.mark.asyncio
    async def test_get_platform_info(self, repo_manager):
        """测试获取平台信息"""
        github_info = repo_manager.get_platform_info("github")
        assert github_info["name"] == "GitHub"
        assert github_info["api_url"] == "https://api.github.com"
        assert github_info["auth_method"] == "token"
        assert github_info["authenticated"] == True
        
        # 对于未认证的平台
        gitlab_info = repo_manager.get_platform_info("gitlab")
        assert gitlab_info["authenticated"] == False
        
    @pytest.mark.asyncio
    async def test_authenticate(self, repo_manager):
        """测试平台认证"""
        adapter = repo_manager._adapters["github"]
        adapter.authenticate = AsyncMock(return_value=(True, "认证成功"))
        
        success, message = await repo_manager.authenticate("github", {"token": "test_token"})
        assert success == True
        assert message == "认证成功"
        adapter.authenticate.assert_called_once_with({"token": "test_token"})
        
        # 测试不支持的平台
        success, message = await repo_manager.authenticate("bitbucket", {})
        assert success == False
        assert "不支持的平台" in message
        
    @pytest.mark.asyncio
    async def test_list_repositories(self, repo_manager):
        """测试获取仓库列表"""
        adapter = repo_manager._adapters["github"]
        sample_repos = [
            {"name": "repo1", "full_name": "user/repo1", "description": "Test repo 1"},
            {"name": "repo2", "full_name": "user/repo2", "description": "Test repo 2"}
        ]
        adapter.list_repositories = AsyncMock(return_value=sample_repos)
        
        repos = await repo_manager.list_repositories("github")
        assert repos == sample_repos
        adapter.list_repositories.assert_called_once_with(None)
        
        # 指定用户名
        await repo_manager.list_repositories("github", "testuser")
        adapter.list_repositories.assert_called_with("testuser")
        
        # 未认证的平台
        adapter.is_authenticated.return_value = False
        repos = await repo_manager.list_repositories("github")
        assert repos == []
        
    @pytest.mark.asyncio
    async def test_clone_repository(self, repo_manager, auth_service_mock):
        """测试克隆仓库"""
        # 模拟仓库信息返回
        adapter = repo_manager._adapters["github"]
        adapter.get_repository = AsyncMock(return_value={
            "name": "testrepo",
            "full_name": "user/testrepo",
            "description": "Test repository",
            "clone_url": "https://github.com/user/testrepo.git"
        })
        
        # 模拟权限服务
        with patch('src.modules.repo_integration.repo_manager.get_repo_permission_service') as mock_permission:
            permission_instance = mock_permission.return_value
            permission_instance.generate_repo_id.return_value = "test_repo_id"
            permission_instance.register_repository.return_value = None
            
            # 模拟git克隆成功
            with patch('subprocess.run') as mock_run:
                with patch.object(Path, 'exists', return_value=True):
                    success, result = await repo_manager.clone_repository("github", "user/testrepo")
                    assert success == True
                    assert "testrepo" in result
                    
            # 模拟git克隆失败
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = Exception("模拟Git克隆错误")
                with patch.object(Path, 'exists', return_value=False):
                    success, result = await repo_manager.clone_repository("github", "user/testrepo")
                    assert success == False
                    assert "错误" in result

    @pytest.mark.asyncio
    async def test_push_repository_with_protection_rules(self, repo_manager, auth_service_mock):
        """测试带有保护规则的仓库推送"""
        with patch('src.modules.repo_integration.repo_manager.get_repo_permission_service') as mock_permission:
            permission_instance = mock_permission.return_value
            permission_instance.generate_repo_id.return_value = "test_repo_id"
            
            # 模拟保护规则检查
            permission_instance.check_protection_rule.side_effect = [
                (False, "分支受保护"),  # 第一次调用失败
                (True, "通过"),        # 第二次调用成功
                (True, "通过")         # 第三次调用成功
            ]
            
            # 模拟仓库存在
            with patch.object(Path, 'exists', return_value=True):
                with patch.object(Path, 'is_dir', return_value=True):
                    # 第一次调用应该因为分支保护而失败
                    success, result = await repo_manager.push_repository("/fake/repo/path", "测试提交", "main")
                    assert success == False
                    assert "分支受保护" in result
                    
                    # 重置保护规则检查的mock以便第二次测试
                    permission_instance.check_protection_rule.side_effect = [
                        (True, "通过"),  # 分支保护
                        (True, "通过"),  # 代码审查
                        (True, "通过")   # 强制推送保护
                    ]
                    
                    # 模拟git命令执行
                    with patch('subprocess.run') as mock_run:
                        success, result = await repo_manager.push_repository("/fake/repo/path", "测试提交", "main")
                        mock_run.assert_called()


def run_tests():
    """运行测试"""
    pytest.main(['-xvs', __file__])

if __name__ == "__main__":
    run_tests() 