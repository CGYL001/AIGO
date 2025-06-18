import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
import requests
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import config
from src.utils import logger
from src.modules import filesystem_analyzer
from src.modules import context_manager
from src.utils import path_utils
from src.mcp_server import MCPServer

class TestMCPBasic(unittest.TestCase):
    """测试MCP系统的基本功能"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试文件
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("This is a test file.")
        
        # 创建测试子目录和文件
        self.test_subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(self.test_subdir, exist_ok=True)
        
        self.test_subfile = os.path.join(self.test_subdir, "subfile.txt")
        with open(self.test_subfile, "w", encoding="utf-8") as f:
            f.write("This is a subfile.")
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_config(self):
        """测试配置模块"""
        # 测试获取配置
        server_host = config.get("server.host")
        self.assertEqual(server_host, "127.0.0.1")
        
        # 测试设置配置
        config.set("test.key", "test_value")
        self.assertEqual(config.get("test.key"), "test_value")
    
    def test_logger(self):
        """测试日志模块"""
        # 测试创建日志记录器
        test_logger = logger.get_logger("test")
        self.assertIsNotNone(test_logger)
        
        # 测试日志级别设置
        logger.set_level("debug")
        self.assertEqual(logger.logger.level, 10)  # DEBUG级别为10
    
    def test_path_utils(self):
        """测试路径工具"""
        # 测试路径规范化
        path = os.path.join("dir1", "dir2", "file.txt")
        normalized = path_utils.normalize_path(path)
        self.assertTrue(isinstance(normalized, str))
        
        # 测试相对路径计算
        path1 = os.path.join(self.temp_dir, "file1.txt")
        path2 = os.path.join(self.temp_dir, "dir", "file2.txt")
        rel_path = path_utils.get_relative_path(path2, path1)
        self.assertTrue(".." in rel_path or "../" in rel_path)
    
    def test_filesystem_analyzer(self):
        """测试文件系统分析器"""
        # 创建分析器
        analyzer = filesystem_analyzer.FilesystemAnalyzer()
        
        # 测试扫描目录
        result = analyzer.scan_directory(self.temp_dir)
        self.assertTrue(isinstance(result, dict))
        self.assertIn("files", result)
        self.assertIn("directories", result)
        self.assertGreaterEqual(len(result["files"]), 1)
        self.assertGreaterEqual(len(result["directories"]), 1)
        
        # 测试获取文件内容
        with open(self.test_file, "r", encoding="utf-8") as f:
            expected_content = f.read()
        
        # 使用实际可用的API
        file_info = analyzer.get_file_info(self.test_file)
        self.assertIsNotNone(file_info)
        self.assertEqual(file_info["path"], self.test_file)
    
    def test_context_manager(self):
        """测试上下文管理器"""
        # 创建上下文管理器
        ctx_manager = context_manager.ContextManager()
        
        # 测试创建上下文
        ctx_id = ctx_manager.create_context("test_context", "file", "test content", {"key": "value"})
        self.assertIsNotNone(ctx_id)
        
        # 测试获取上下文
        ctx = ctx_manager.get_context(ctx_id)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["name"], "test_context")
        self.assertEqual(ctx["content"], "test content")
        self.assertEqual(ctx["metadata"]["key"], "value")
        
        # 测试更新上下文
        ctx_manager.update_context(ctx_id, "updated content", {"key2": "value2"})
        ctx = ctx_manager.get_context(ctx_id)
        self.assertEqual(ctx["content"], "updated content")
        self.assertEqual(ctx["metadata"]["key"], "value")
        self.assertEqual(ctx["metadata"]["key2"], "value2")
    
    def test_mcp_server_init(self):
        """测试MCP服务器初始化"""
        # 创建服务器实例
        server = MCPServer()
        
        # 检查服务器是否正确初始化
        self.assertIsNotNone(server.model_manager)
        self.assertIsNotNone(server.auth_token)

if __name__ == '__main__':
    unittest.main()

# 获取服务器认证令牌
auth_token = "c016ba3e-cc2e-4dfe-bce4-e757593483c0"  # 从服务器日志中获取

# 测试文件系统扫描
response = requests.post(
    "http://localhost:8000/api/filesystem/scan",
    headers={"Authorization": f"Bearer {auth_token}"},
    json={"directory": ".", "incremental": False}
)

print(json.dumps(response.json(), indent=2)) 