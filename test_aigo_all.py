#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AIgo全面测试脚本

测试AIgo项目中所有可测试的模块和功能
"""

import os
import sys
import json
import time
import logging
import importlib
import unittest
import subprocess
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("test_aigo_all")

# 测试超时时间（秒）
TEST_TIMEOUT = 30

class AIgoTestSuite:
    """AIgo全面测试套件"""
    
    def __init__(self):
        """初始化测试套件"""
        self.results = []
        self.start_time = time.time()
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        
        # 创建必要的目录
        os.makedirs("logs", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        os.makedirs("data", exist_ok=True)
    
    def run_test(self, test_name, test_func, *args, **kwargs):
        """运行测试"""
        self.test_count += 1
        logger.info(f"执行测试 [{self.test_count}]: {test_name}")
        
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            elapsed = time.time() - start_time
            status = "通过" if result else "失败"
            if result:
                self.pass_count += 1
            else:
                self.fail_count += 1
            logger.info(f"测试结果: {status}, 耗时: {elapsed:.2f}秒")
            self.results.append((test_name, result, elapsed))
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            self.fail_count += 1
            self.results.append((test_name, False, elapsed))
            return False
    
    def print_summary(self):
        """打印测试结果摘要"""
        total_time = time.time() - self.start_time
        
        logger.info("=" * 70)
        logger.info(f"AIgo全面测试结果摘要 (总耗时: {total_time:.2f}秒)")
        logger.info("=" * 70)
        
        # 按类别分组打印结果
        categories = {}
        for name, result, elapsed in self.results:
            category = name.split(":")[0] if ":" in name else "其他"
            if category not in categories:
                categories[category] = []
            categories[category].append((name, result, elapsed))
        
        # 打印每个类别的结果
        for category, tests in categories.items():
            logger.info(f"\n{category} 测试结果:")
            logger.info("-" * 50)
            category_pass = sum(1 for _, result, _ in tests if result)
            category_total = len(tests)
            for name, result, elapsed in tests:
                status = "✅ 通过" if result else "❌ 失败"
                test_name = name.split(":", 1)[1] if ":" in name else name
                logger.info(f"{status} {test_name} ({elapsed:.2f}秒)")
            logger.info(f"小计: {category_pass}/{category_total} 通过")
        
        # 打印总结
        logger.info("\n" + "=" * 70)
        logger.info(f"总计: {self.test_count}个测试, 通过: {self.pass_count}, 失败: {self.fail_count}")
        logger.info(f"通过率: {(self.pass_count / self.test_count * 100):.1f}%")
        logger.info("=" * 70)
        
        return self.pass_count == self.test_count

    def test_directory_structure(self):
        """测试项目目录结构"""
        required_dirs = [
            "src",
            "src/modules",
            "src/services",
            "src/utils",
            "config",
            "data",
            "logs"
        ]
        
        for directory in required_dirs:
            if not os.path.isdir(directory):
                logger.error(f"目录不存在: {directory}")
                return False
            logger.info(f"目录存在: {directory}")
        
        return True
    
    def test_config_files(self):
        """测试配置文件"""
        config_files = [
            "config/default/config.json",
            "config/default/mcp_config.json"
        ]
        
        for config_file in config_files:
            if not os.path.isfile(config_file):
                logger.error(f"配置文件不存在: {config_file}")
                return False
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"成功加载配置文件: {config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {config_file}, 错误: {str(e)}")
                return False
        
        return True
    
    def test_module_imports(self):
        """测试所有模块的导入"""
        modules_to_test = [
            # 核心模块
            "src.modules.code_analysis",
            "src.modules.knowledge_base",
            "src.modules.prompt_engineering",
            "src.modules.system_monitor",
            "src.modules.model_restructuring",
            
            # 服务模块
            "src.services.model_manager",
            "src.services.authorization_service",
            
            # 工具模块
            "src.utils.config_validator",
            "src.utils.async_utils",
            "src.utils.logger",
            
            # CLI模块
            "src.cli.feature_cmd",
            "src.cli.model_restructure_cmd"
        ]
        
        all_passed = True
        for module_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                logger.info(f"成功导入模块: {module_name}")
            except ImportError as e:
                logger.warning(f"模块导入失败: {module_name}, 错误: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_system_monitor(self):
        """测试系统监控模块"""
        try:
            from src.modules.system_monitor.resource_monitor import ResourceMonitor
            
            # 初始化资源监控器
            config = {
                "interval": 60,
                "history_size": 100,
                "log_level": "info"
            }
            monitor = ResourceMonitor(config)
            logger.info("成功创建ResourceMonitor实例")
            
            # 获取系统信息
            system_info = monitor.get_system_info()
            logger.info(f"系统信息: CPU核心数: {system_info['cpu']['logical_cores']}, "
                       f"内存: {system_info['memory']['total']}, "
                       f"可用内存: {system_info['memory']['available']}")
            
            # 检查系统信息是否包含关键字段
            required_fields = ['os', 'cpu', 'memory']
            all_fields_present = all(field in system_info for field in required_fields)
            
            if all_fields_present:
                logger.info("系统信息包含所有必要字段")
            else:
                logger.error("系统信息缺少必要字段")
                return False
            
            return True
        except Exception as e:
            logger.error(f"测试系统监控模块失败: {str(e)}")
            return False
    
    def test_model_manager(self):
        """测试模型管理器"""
        try:
            from src.services.model_manager import ModelManager
            
            # 初始化模型管理器
            model_manager = ModelManager()
            logger.info("成功创建ModelManager实例")
            
            # 获取可用模型列表
            models = model_manager.get_available_models()
            logger.info(f"可用模型数量: {len(models)}")
            
            return True
        except Exception as e:
            logger.error(f"测试模型管理器失败: {str(e)}")
            return False
    
    def test_knowledge_base(self):
        """测试知识库模块"""
        try:
            # 导入知识库模块
            from src.modules.knowledge_base.knowledge_base import KnowledgeBase
            logger.info("成功导入KnowledgeBase类")
            
            # 尝试创建知识库实例
            kb = KnowledgeBase(config={
                "storage_type": "memory",
                "index_name": "test_index",
                "embedding_dimension": 384
            })
            logger.info("成功创建KnowledgeBase实例")
            
            # 初始化向量存储
            kb_path = "data/test_kb"
            kb.init_vector_store(kb_path, dimension=384)
            logger.info("成功初始化向量存储")
            
            # 测试添加和检索文档
            test_docs = [
                {"text": "这是测试文档1", "metadata": {"source": "test", "id": "1"}},
                {"text": "这是测试文档2", "metadata": {"source": "test", "id": "2"}},
                {"text": "这是另一个不同的文档", "metadata": {"source": "test", "id": "3"}}
            ]
            
            # 添加文档
            kb.add_documents(test_docs)
            logger.info("成功添加测试文档")
            
            # 检索文档
            results = kb.search("测试文档", limit=2)
            logger.info(f"检索到 {len(results)} 个文档")
            
            if len(results) > 0:
                return True
            else:
                logger.warning("知识库检索未返回结果")
                return False
        except Exception as e:
            logger.error(f"测试知识库模块失败: {str(e)}")
            return False
    
    def test_code_analysis(self):
        """测试代码分析模块"""
        try:
            # 导入代码分析模块
            from src.modules.code_analysis.code_analyzer import CodeAnalyzer
            logger.info("成功导入CodeAnalyzer类")
            
            # 创建测试文件
            test_file = "test_code.py"
            with open(test_file, "w") as f:
                f.write("""
def hello_world():
    print("Hello, World!")
    
class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
""")
            
            # 分析代码
            analyzer = CodeAnalyzer()
            result = analyzer.analyze_file(test_file)
            logger.info(f"代码分析结果: {result}")
            
            # 清理测试文件
            os.remove(test_file)
            
            if "functions" in result and "classes" in result:
                return True
            else:
                logger.warning("代码分析结果缺少必要字段")
                return False
        except Exception as e:
            logger.error(f"测试代码分析模块失败: {str(e)}")
            return False
    
    def test_prompt_engineering(self):
        """测试提示工程模块"""
        try:
            # 导入提示工程模块
            from src.modules.prompt_engineering.prompt_generator import PromptGenerator
            logger.info("成功导入PromptGenerator类")
            
            # 创建提示生成器
            generator = PromptGenerator()
            
            # 测试生成提示
            context = {
                "user_query": "如何使用Python读取文件?",
                "language": "python",
                "task": "code_explanation"
            }
            
            prompt = generator.generate(context)
            logger.info(f"生成的提示: {prompt[:50]}...")
            
            if prompt and len(prompt) > 0:
                return True
            else:
                logger.warning("生成的提示为空")
                return False
        except Exception as e:
            logger.error(f"测试提示工程模块失败: {str(e)}")
            return False
    
    def test_model_restructuring(self):
        """测试模型重构模块"""
        try:
            # 导入模型重构模块
            from src.modules.model_restructuring.model_restructurer import ModelRestructurer
            from src.modules.model_restructuring.performance_analyzer import PerformanceAnalyzer
            from src.modules.model_restructuring.component_optimizer import ComponentOptimizer
            
            logger.info("成功导入模型重构模块")
            
            # 创建模型目录
            os.makedirs("models", exist_ok=True)
            
            # 创建示例模型配置
            demo_model_path = "models/demo_model.json"
            demo_model_config = {
                "name": "demo_model",
                "type": "transformer",
                "size": "7B",
                "layers": 32,
                "hidden_size": 4096,
                "attention_heads": 32,
                "intermediate_size": 11008,
                "vocab_size": 32000,
                "max_position_embeddings": 2048
            }
            
            with open(demo_model_path, 'w', encoding='utf-8') as f:
                json.dump(demo_model_config, f, indent=2, ensure_ascii=False)
            
            # 创建模型重构器
            restructurer = ModelRestructurer()
            logger.info("成功创建ModelRestructurer实例")
            
            # 分析模型
            analysis = restructurer.analyze_model(demo_model_path)
            logger.info(f"模型分析结果: 大小={analysis['model_size']}, 层数={analysis['layers']}")
            
            # 优化模型
            output_path = "output/optimized_model"
            result = restructurer.optimize_model(demo_model_path, output_path, optimization_level=2)
            logger.info(f"模型优化结果: 尺寸减少={result['size_reduction']}, 速度提升={result['speed_improvement']}")
            
            return True
        except Exception as e:
            logger.error(f"测试模型重构模块失败: {str(e)}")
            return False
    
    def test_authorization_service(self):
        """测试授权服务"""
        try:
            # 导入授权服务
            from src.services.authorization_service import AuthorizationService
            logger.info("成功导入AuthorizationService类")
            
            # 创建授权服务
            auth_service = AuthorizationService()
            logger.info("成功创建AuthorizationService实例")
            
            # 测试令牌验证
            test_token = "test_token"
            result = auth_service.validate_token(test_token)
            logger.info(f"令牌验证结果: {result}")
            
            return True
        except Exception as e:
            logger.error(f"测试授权服务失败: {str(e)}")
            return False
    
    def test_async_utils(self):
        """测试异步工具模块"""
        try:
            # 导入异步工具
            from src.utils.async_utils import run_async, async_timeout
            import asyncio
            logger.info("成功导入异步工具模块")
            
            # 测试异步运行
            async def test_async_func():
                await asyncio.sleep(0.1)
                return "success"
            
            result = run_async(test_async_func())
            logger.info(f"异步运行结果: {result}")
            
            # 测试异步超时
            @async_timeout(0.2)
            async def test_timeout_func():
                await asyncio.sleep(0.1)
                return "success"
            
            result = run_async(test_timeout_func())
            logger.info(f"异步超时测试结果: {result}")
            
            return result == "success"
        except Exception as e:
            logger.error(f"测试异步工具模块失败: {str(e)}")
            return False
    
    def test_config_validator(self):
        """测试配置验证器"""
        try:
            # 导入配置验证器
            from src.utils.config_validator import validate_config
            logger.info("成功导入配置验证器")
            
            # 测试配置验证
            test_config = {
                "app": {
                    "name": "AIgo",
                    "version": "1.0.0"
                },
                "models": {
                    "default": "test_model"
                }
            }
            
            schema = {
                "type": "object",
                "required": ["app", "models"],
                "properties": {
                    "app": {
                        "type": "object",
                        "required": ["name", "version"],
                        "properties": {
                            "name": {"type": "string"},
                            "version": {"type": "string"}
                        }
                    },
                    "models": {
                        "type": "object",
                        "required": ["default"],
                        "properties": {
                            "default": {"type": "string"}
                        }
                    }
                }
            }
            
            result = validate_config(test_config, schema)
            logger.info(f"配置验证结果: {result}")
            
            return result
        except Exception as e:
            logger.error(f"测试配置验证器失败: {str(e)}")
            return False
    
    def test_cli_tools(self):
        """测试命令行工具"""
        try:
            # 测试aigo-cli.py是否存在
            if not os.path.isfile("aigo-cli.py"):
                logger.error("CLI工具不存在: aigo-cli.py")
                return False
            
            # 测试CLI帮助命令
            result = subprocess.run(
                [sys.executable, "aigo-cli.py", "--help"],
                capture_output=True,
                text=True,
                timeout=TEST_TIMEOUT
            )
            
            if result.returncode != 0:
                logger.error(f"CLI帮助命令失败: {result.stderr}")
                return False
            
            logger.info("CLI帮助命令成功")
            logger.info(f"CLI帮助输出: {result.stdout[:100]}...")
            
            return True
        except Exception as e:
            logger.error(f"测试命令行工具失败: {str(e)}")
            return False
    
    def test_repo_integration(self):
        """测试代码仓库集成"""
        try:
            # 导入代码仓库管理器
            from src.modules.repo_integration.repo_manager import RepoManager
            logger.info("成功导入RepoManager类")
            
            # 创建代码仓库管理器
            repo_manager = RepoManager()
            logger.info("成功创建RepoManager实例")
            
            # 测试获取仓库信息
            repo_info = repo_manager.get_repo_info()
            logger.info(f"仓库信息: {repo_info}")
            
            return True
        except Exception as e:
            logger.error(f"测试代码仓库集成失败: {str(e)}")
            return False
    
    def test_filesystem_analyzer(self):
        """测试文件系统分析器"""
        try:
            # 导入文件系统分析器
            from src.modules.filesystem_analyzer import FilesystemAnalyzer
            logger.info("成功导入FilesystemAnalyzer类")
            
            # 创建文件系统分析器
            analyzer = FilesystemAnalyzer()
            logger.info("成功创建FilesystemAnalyzer实例")
            
            # 测试分析目录
            result = analyzer.analyze_directory(".")
            logger.info(f"目录分析结果: 文件数量={len(result['files'])}, 目录数量={len(result['directories'])}")
            
            return True
        except Exception as e:
            logger.error(f"测试文件系统分析器失败: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        # 基础测试
        self.run_test("基础:目录结构", self.test_directory_structure)
        self.run_test("基础:配置文件", self.test_config_files)
        self.run_test("基础:模块导入", self.test_module_imports)
        
        # 核心模块测试
        self.run_test("核心:系统监控", self.test_system_monitor)
        self.run_test("核心:模型管理器", self.test_model_manager)
        self.run_test("核心:知识库", self.test_knowledge_base)
        self.run_test("核心:代码分析", self.test_code_analysis)
        self.run_test("核心:提示工程", self.test_prompt_engineering)
        self.run_test("核心:模型重构", self.test_model_restructuring)
        
        # 服务模块测试
        self.run_test("服务:授权服务", self.test_authorization_service)
        
        # 工具模块测试
        self.run_test("工具:异步工具", self.test_async_utils)
        self.run_test("工具:配置验证器", self.test_config_validator)
        
        # 集成测试
        self.run_test("集成:命令行工具", self.test_cli_tools)
        self.run_test("集成:代码仓库集成", self.test_repo_integration)
        self.run_test("集成:文件系统分析器", self.test_filesystem_analyzer)
        
        # 打印测试结果摘要
        return self.print_summary()

def main():
    """主函数"""
    logger.info("开始AIgo全面测试")
    
    # 创建测试套件
    test_suite = AIgoTestSuite()
    
    # 运行所有测试
    success = test_suite.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 