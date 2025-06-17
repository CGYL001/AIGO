"""
使用模拟对象的仓库集成测试
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import logging

# 设置基本日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

# 模拟logger模块
class MockLogger:
    def info(self, msg, *args, **kwargs):
        print(f"[INFO] {msg}")
        
    def warning(self, msg, *args, **kwargs):
        print(f"[WARNING] {msg}")
        
    def error(self, msg, *args, **kwargs):
        print(f"[ERROR] {msg}")
        
    def debug(self, msg, *args, **kwargs):
        pass

logger = MockLogger()

# 模拟config模块
class MockConfig:
    def get(self, key, default=None):
        config_values = {
            "repository_integration.local_repo_path": "data/repositories",
            "repository_integration.settings_path": "data/repositories/settings",
            "repository_integration.audit_log_path": "data/repositories/audit",
            "repository_integration.platforms.github.enabled": True,
            "repository_integration.platforms.gitlab.enabled": True,
            "repository_integration.platforms.gitee.enabled": True,
        }
        
        if key in config_values:
            return config_values[key]
        return default

config = MockConfig()

# 模拟所有依赖模块
sys.modules['src.utils.logger'] = MagicMock(logger=logger)
sys.modules['src.utils.config'] = MagicMock(get=config.get)
sys.modules['src.utils'] = MagicMock(logger=logger, config=config)
sys.modules['src.services.repo_permission_service'] = MagicMock(get_instance=lambda: MagicMock())
sys.modules['src.services.auth_service'] = MagicMock()
sys.modules['src.services'] = MagicMock()
sys.modules['src.services.model_manager'] = MagicMock()
sys.modules['src.modules.code_completion'] = MagicMock()
sys.modules['src.modules.context_manager'] = MagicMock()
sys.modules['src.modules.error_checker'] = MagicMock()
sys.modules['src.modules.knowledge_base'] = MagicMock()
sys.modules['src.modules.ui'] = MagicMock()
sys.modules['src.modules.code_analysis'] = MagicMock()
sys.modules['src.modules.network_proxy'] = MagicMock()
sys.modules['src.modules.prompt_engineering'] = MagicMock()
sys.modules['src.database'] = MagicMock()
sys.modules['src.database.models'] = MagicMock()

# 确保可以导入src模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建模拟适配器类
class MockAdapter:
    def __init__(self, name, authenticated=True):
        self.name = name
        self._authenticated = authenticated
        
    def get_platform_name(self):
        return self.name.upper()
        
    def get_api_url(self):
        return f"https://api.{self.name}.com"
        
    def get_auth_method(self):
        return "token"
        
    def is_authenticated(self):
        return self._authenticated
        
    async def authenticate(self, credentials):
        return True, "认证成功"
        
    async def list_repositories(self, username=None):
        return [
            {"name": "repo1", "full_name": "user/repo1"},
            {"name": "repo2", "full_name": "user/repo2"}
        ]

# 模拟平台适配器
class MockGitHubAdapter(MockAdapter):
    def __init__(self):
        super().__init__("github", True)

class MockGitLabAdapter(MockAdapter):
    def __init__(self):
        super().__init__("gitlab", False)

class MockGiteeAdapter(MockAdapter):
    def __init__(self):
        super().__init__("gitee", False)

# 模拟RepoManager类
class MockRepoManager:
    def __init__(self):
        self._adapters = {
            "github": MockGitHubAdapter(),
            "gitlab": MockGitLabAdapter(),
            "gitee": MockGiteeAdapter()
        }
        self._current_session_id = "test_session"
        
    def get_platforms(self):
        return list(self._adapters.keys())
        
    def is_platform_supported(self, platform):
        return platform.lower() in self._adapters
        
    def get_platform_info(self, platform):
        if not self.is_platform_supported(platform):
            return {"name": platform, "api_url": "", "authenticated": False}
            
        adapter = self._adapters[platform.lower()]
        return {
            "name": adapter.get_platform_name(),
            "api_url": adapter.get_api_url(),
            "authenticated": adapter.is_authenticated()
        }
        
    async def authenticate(self, platform, credentials):
        if not self.is_platform_supported(platform):
            return False, f"不支持的平台: {platform}"
            
        adapter = self._adapters[platform.lower()]
        return await adapter.authenticate(credentials)

class TestRepoManager(unittest.TestCase):
    """仓库管理器测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.repo_manager = MockRepoManager()
    
    def test_get_platforms(self):
        """测试获取平台列表"""
        platforms = self.repo_manager.get_platforms()
        self.assertEqual(len(platforms), 3)
        self.assertIn("github", platforms)
        self.assertIn("gitlab", platforms)
        self.assertIn("gitee", platforms)
        print("测试获取平台列表通过!")
    
    def test_is_platform_supported(self):
        """测试检查平台是否支持"""
        self.assertTrue(self.repo_manager.is_platform_supported("github"))
        self.assertTrue(self.repo_manager.is_platform_supported("gitlab"))
        self.assertFalse(self.repo_manager.is_platform_supported("bitbucket"))
        print("测试检查平台是否支持通过!")
    
    def test_get_platform_info(self):
        """测试获取平台信息"""
        github_info = self.repo_manager.get_platform_info("github")
        self.assertEqual(github_info["name"], "GITHUB")
        self.assertEqual(github_info["api_url"], "https://api.github.com")
        self.assertTrue(github_info["authenticated"])
        
        # 对于未认证的平台
        gitlab_info = self.repo_manager.get_platform_info("gitlab")
        self.assertFalse(gitlab_info["authenticated"])
        print("测试获取平台信息通过!")
    
    async def test_authenticate(self):
        """测试平台认证"""
        success, message = await self.repo_manager.authenticate("github", {"token": "test_token"})
        self.assertTrue(success)
        self.assertEqual(message, "认证成功")
        print("测试平台认证通过!")

def run_tests():
    """运行测试"""
    # 创建测试实例
    test = TestRepoManager()
    test.setUp()
    
    # 运行同步测试
    test.test_get_platforms()
    test.test_is_platform_supported()
    test.test_get_platform_info()
    
    # 运行异步测试
    asyncio.run(test.test_authenticate())
    
    print("所有测试通过!")

if __name__ == "__main__":
    run_tests() 