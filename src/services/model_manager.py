import os
import time
import json
import threading
import subprocess
import importlib
from typing import Dict, List, Any, Optional, Set, Tuple
import psutil
from pathlib import Path

from src.utils import config, logger
from src.services.model_service import ModelService, OllamaService, ModelServiceFactory

# 创建日志记录器
log = logger.get_logger("model_manager")

class ModelManager:
    """
    模型管理器，负责模型的生命周期管理、加载卸载策略和智能选择
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化模型管理器"""
        if self._initialized:
            return
            
        # 加载配置
        self.models_dir = Path(config.get("models.directory", "models"))
        self.model_configs_dir = Path(config.get("models.configs_directory", "config/models"))
        self.default_model = config.get("models.default", "gpt-3.5-turbo")
        self.max_concurrent_models = config.get("models.max_concurrent", 2)
        self.model_timeout = config.get("models.timeout_seconds", 60)
        
        # 模型实例缓存
        self._models: Dict[str, Any] = {}
        self._model_locks: Dict[str, threading.Lock] = {}
        self._model_last_used: Dict[str, float] = {}
        self._model_configs: Dict[str, Dict[str, Any]] = {}
        
        # 加载模型配置
        self._load_model_configs()
        
        # 创建模型目录
        os.makedirs(self.models_dir, exist_ok=True)
        
        # 启动模型清理线程
        self._cleanup_thread = threading.Thread(target=self._cleanup_task, daemon=True)
        self._stop_cleanup = threading.Event()
        self._cleanup_thread.start()
        
        log.info(f"ModelManager initialized with {len(self._model_configs)} model configurations")
        
        # 模型服务实例缓存
        self._model_services: Dict[str, ModelService] = {}
        
        # 加载的模型名称集合
        self._loaded_models: Set[str] = set()
        
        # 自动卸载定时器
        self._unload_timer = None
        
        # 锁，用于线程安全
        self._lock = threading.Lock()
        
        # 配置
        self._auto_select = config.get("model_management.auto_select", True)
        self._auto_unload = config.get("model_management.auto_unload", True)
        self._unload_timeout = config.get("model_management.unload_timeout_minutes", 10) * 60  # 转换为秒
        self._prefer_gpu = config.get("model_management.prefer_gpu", True)
        
        # 可用模型信息
        inference_models = config.get("models.inference.available_models", [])
        embedding_models = config.get("models.embedding.available_models", [])
        self._available_models = {m.get("name"): m for m in inference_models + embedding_models}
        
        # 检查模型服务和可用模型
        self._check_model_service()
        
        # 开始自动卸载定时器
        if self._auto_unload:
            self._start_unload_timer()
        
        # 创建模型服务
        self.model_service = ModelServiceFactory.create_service()
        
        # 模型性能监控
        self.request_history = []
        self.max_history_length = 100  # 保留最近的请求历史
        
        # 系统负载阈值
        self.cpu_threshold = config.get("system_monitor.cpu_threshold", 80)  # CPU使用率阈值(%)
        self.memory_threshold = config.get("system_monitor.memory_threshold", 70)  # 内存使用率阈值(%)
        
        # 自适应参数配置
        self.adaptive_params_enabled = config.get("models.adaptive_params.enabled", True)
        self.performance_mode = config.get("models.adaptive_params.performance_mode", "balanced")  # balanced, speed, quality
        
        # 模型类型到参数的映射
        self.model_type_params = self._load_model_type_params()
        
        # 当前模型参数
        self.current_params = self._get_default_params()
        
        logger.info("模型管理器初始化完成")
        
        self._initialized = True
    
    def _load_model_configs(self) -> None:
        """加载所有模型配置"""
        self._model_configs = {}
        
        # 确保配置目录存在
        os.makedirs(self.model_configs_dir, exist_ok=True)
        
        # 加载所有JSON配置文件
        for config_file in self.model_configs_dir.glob("*.json"):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    model_config = json.load(f)
                
                model_id = model_config.get("id") or config_file.stem
                self._model_configs[model_id] = model_config
                log.debug(f"Loaded model config: {model_id}")
                
            except Exception as e:
                log.error(f"Error loading model config {config_file}: {str(e)}")
    
    def _cleanup_task(self) -> None:
        """清理未使用的模型"""
        while not self._stop_cleanup.wait(60):  # 每分钟检查一次
            try:
                self._cleanup_models()
            except Exception as e:
                log.error(f"Error in model cleanup task: {str(e)}")
    
    def _cleanup_models(self) -> None:
        """释放长时间未使用的模型"""
        now = time.time()
        models_to_unload = []
        
        # 找出长时间未使用的模型
        for model_id, last_used in self._model_last_used.items():
            # 如果模型超过10分钟未使用，释放它
            if now - last_used > 600:  # 10分钟
                models_to_unload.append(model_id)
        
        # 释放模型
        for model_id in models_to_unload:
            self.unload_model(model_id)
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        获取所有可用模型的信息
        
        Returns:
            List[Dict[str, Any]]: 模型信息列表
        """
        return [
            {
                "id": model_id,
                "name": config.get("name", model_id),
                "description": config.get("description", ""),
                "type": config.get("type", "unknown"),
                "loaded": model_id in self._models
            }
            for model_id, config in self._model_configs.items()
        ]
    
    def load_model(self, model_id: str) -> Any:
        """
        加载模型
        
        Args:
            model_id: 模型ID
            
        Returns:
            Any: 模型实例
            
        Raises:
            ValueError: 如果模型不存在
            RuntimeError: 如果模型加载失败
        """
        # 检查模型是否已加载
        if model_id in self._models:
            # 更新最后使用时间
            self._model_last_used[model_id] = time.time()
            return self._models[model_id]
        
        # 检查模型配置是否存在
        if model_id not in self._model_configs:
            raise ValueError(f"Model not found: {model_id}")
        
        # 获取模型配置
        model_config = self._model_configs[model_id]
        
        # 创建模型锁（如果不存在）
        if model_id not in self._model_locks:
            self._model_locks[model_id] = threading.Lock()
        
        # 使用锁确保线程安全
        with self._model_locks[model_id]:
            # 再次检查模型是否已加载（可能在获取锁的过程中被其他线程加载）
            if model_id in self._models:
                self._model_last_used[model_id] = time.time()
                return self._models[model_id]
            
            # 检查是否超过最大并发模型数
            if len(self._models) >= self.max_concurrent_models:
                # 卸载最久未使用的模型
                self._unload_least_recently_used()
            
            try:
                # 加载模型
                log.info(f"Loading model: {model_id}")
                
                # 根据模型类型加载
                model_type = model_config.get("type", "unknown")
                
                if model_type == "openai":
                    model = self._load_openai_model(model_config)
                elif model_type == "huggingface":
                    model = self._load_huggingface_model(model_config)
                elif model_type == "local":
                    model = self._load_local_model(model_config)
                else:
                    raise ValueError(f"Unsupported model type: {model_type}")
                
                # 缓存模型
                self._models[model_id] = model
                self._model_last_used[model_id] = time.time()
                
                log.info(f"Model loaded successfully: {model_id}")
                return model
                
            except Exception as e:
                log.error(f"Error loading model {model_id}: {str(e)}")
                raise RuntimeError(f"Failed to load model {model_id}: {str(e)}")
    
    def _load_openai_model(self, model_config: Dict[str, Any]) -> Any:
        """加载OpenAI模型"""
        try:
            import openai
            
            # 配置API密钥
            api_key = model_config.get("api_key") or config.get("openai.api_key")
            if not api_key:
                raise ValueError("OpenAI API key not found")
            
            # 创建客户端
            client = openai.OpenAI(api_key=api_key)
            
            # 返回客户端和模型名称
            return {
                "client": client,
                "model": model_config.get("model", "gpt-3.5-turbo")
            }
            
        except ImportError:
            raise ImportError("OpenAI package not installed. Please install it with 'pip install openai'")
    
    def _load_huggingface_model(self, model_config: Dict[str, Any]) -> Any:
        """加载HuggingFace模型"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            # 获取模型路径
            model_path = model_config.get("path")
            if not model_path:
                raise ValueError("Model path not specified")
            
            # 检查是否需要下载模型
            local_path = self.models_dir / model_path
            if not local_path.exists():
                log.info(f"Downloading model: {model_path}")
                
                # 下载模型
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True
                )
                
                # 保存模型到本地
                os.makedirs(local_path, exist_ok=True)
                tokenizer.save_pretrained(local_path)
                model.save_pretrained(local_path)
            else:
                # 从本地加载模型
                tokenizer = AutoTokenizer.from_pretrained(local_path)
                model = AutoModelForCausalLM.from_pretrained(
                    local_path,
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True
                )
            
            # 移动模型到适当的设备
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device)
            
            return {
                "model": model,
                "tokenizer": tokenizer,
                "device": device
            }
            
        except ImportError:
            raise ImportError("Transformers package not installed. Please install it with 'pip install transformers torch'")
    
    def _load_local_model(self, model_config: Dict[str, Any]) -> Any:
        """加载本地模型"""
        # 获取模型类和参数
        model_module = model_config.get("module")
        model_class = model_config.get("class")
        model_args = model_config.get("args", {})
        
        if not model_module or not model_class:
            raise ValueError("Model module and class must be specified for local models")
        
        try:
            # 导入模型模块
            module = importlib.import_module(model_module)
            
            # 获取模型类
            ModelClass = getattr(module, model_class)
            
            # 创建模型实例
            model = ModelClass(**model_args)
            
            return model
            
        except ImportError:
            raise ImportError(f"Module {model_module} not found")
        except AttributeError:
            raise AttributeError(f"Class {model_class} not found in module {model_module}")
    
    def _unload_least_recently_used(self) -> None:
        """卸载最久未使用的模型"""
        if not self._model_last_used:
            return
        
        # 找出最久未使用的模型
        lru_model = min(self._model_last_used.items(), key=lambda x: x[1])[0]
        
        # 卸载模型
        self.unload_model(lru_model)
    
    def unload_model(self, model_id: str) -> None:
        """
        卸载模型
        
        Args:
            model_id: 模型ID
        """
        if model_id not in self._models:
            return
        
        # 使用锁确保线程安全
        if model_id in self._model_locks:
            with self._model_locks[model_id]:
                if model_id in self._models:
                    log.info(f"Unloading model: {model_id}")
                    
                    # 从缓存中移除
                    del self._models[model_id]
                    if model_id in self._model_last_used:
                        del self._model_last_used[model_id]
                    
                    # 强制垃圾回收
                    import gc
                    gc.collect()
    
    def _check_model_service(self):
        """检查模型服务状态和可用模型"""
        try:
            api_base = config.get("models.inference.api_base", "http://localhost:11434")
            import requests
            
            try:
                response = requests.get(f"{api_base}/api/tags")
                if response.status_code == 200:
                    models_data = response.json().get("models", [])
                    loaded_models = {m.get("name", "").split(":")[0] for m in models_data}
                    logger.info(f"检测到已加载模型: {', '.join(loaded_models)}")
                    
                    # 更新已加载模型集合
                    for model in loaded_models:
                        if any(model in avail_model for avail_model in self._available_models.keys()):
                            self._loaded_models.add(model)
                            self._model_last_used[model] = time.time()
                else:
                    logger.warning(f"Ollama服务响应异常: {response.status_code}")
            except Exception as e:
                logger.warning(f"无法连接到Ollama服务({api_base}): {str(e)}")
                
        except ImportError:
            logger.error("缺少请求库: requests")
    
    def _start_unload_timer(self):
        """启动自动卸载定时器"""
        def check_and_unload():
            while self._auto_unload:
                time.sleep(60)  # 每分钟检查一次
                self._check_unused_models()
        
        self._unload_timer = threading.Thread(target=check_and_unload, daemon=True)
        self._unload_timer.start()
    
    def _check_unused_models(self):
        """检查并卸载未使用的模型"""
        with self._lock:
            current_time = time.time()
            models_to_unload = []
            
            for model, last_used in self._model_last_used.items():
                if current_time - last_used > self._unload_timeout:
                    models_to_unload.append(model)
            
            for model in models_to_unload:
                self._unload_model(model)
    
    def _unload_model(self, model_name: str):
        """卸载指定模型"""
        try:
            # 从Ollama卸载模型
            subprocess.run(["ollama", "rm", model_name], capture_output=True)
            
            # 更新状态
            if model_name in self._loaded_models:
                self._loaded_models.remove(model_name)
            if model_name in self._model_last_used:
                del self._model_last_used[model_name]
            if model_name in self._model_services:
                del self._model_services[model_name]
                
            logger.info(f"已卸载模型: {model_name}")
        except Exception as e:
            logger.error(f"卸载模型失败: {str(e)}")
    
    def _load_model(self, model_name: str) -> bool:
        """加载指定模型"""
        if model_name in self._loaded_models:
            # 更新使用时间
            self._model_last_used[model_name] = time.time()
            return True
            
        try:
            # 检查是否需要卸载其他模型来释放资源
            if len(self._loaded_models) >= self._max_concurrent_models:
                # 找到最久未使用的模型
                oldest_model = min(self._model_last_used.items(), key=lambda x: x[1])[0]
                self._unload_model(oldest_model)
            
            # 通过Ollama加载模型
            logger.info(f"开始加载模型: {model_name}")
            subprocess.run(["ollama", "pull", model_name], capture_output=True)
            
            # 更新状态
            self._loaded_models.add(model_name)
            self._model_last_used[model_name] = time.time()
            
            logger.info(f"成功加载模型: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            return False
    
    def _check_hardware_compatibility(self, model_name: str) -> bool:
        """检查硬件兼容性"""
        if model_name not in self._available_models:
            return True  # 未知模型，假设兼容
            
        model_info = self._available_models[model_name]
        
        # 检查RAM
        ram_required_str = model_info.get("ram_required", "4GB").replace("GB", "")
        try:
            ram_required_gb = float(ram_required_str)
            system_ram_gb = psutil.virtual_memory().total / (1024 * 1024 * 1024)
            if system_ram_gb < ram_required_gb:
                logger.warning(f"系统内存不足: 需要{ram_required_gb}GB，可用{system_ram_gb:.1f}GB")
                return False
        except (ValueError, AttributeError):
            pass
            
        # 检查VRAM（如果选择GPU）
        if self._prefer_gpu:
            vram_required_str = model_info.get("vram_required", "4GB").replace("GB", "")
            try:
                vram_required_gb = float(vram_required_str)
                
                # 简单检测GPU内存（实际应用中可能需要更复杂的检测）
                gpu_info = self._get_gpu_info()
                if not gpu_info or gpu_info.get("free_memory_gb", 0) < vram_required_gb:
                    logger.warning(f"GPU显存不足: 需要{vram_required_gb}GB")
                    return False
            except (ValueError, AttributeError):
                pass
                
        return True
    
    def _get_gpu_info(self) -> Optional[Dict[str, Any]]:
        """获取GPU信息"""
        try:
            # 尝试使用nvidia-smi获取GPU信息
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total,memory.free,memory.used", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                output = result.stdout.strip().split(",")
                if len(output) >= 3:
                    total = float(output[0]) / 1024  # 转换为GB
                    free = float(output[1]) / 1024
                    used = float(output[2]) / 1024
                    return {
                        "total_memory_gb": total,
                        "free_memory_gb": free,
                        "used_memory_gb": used
                    }
        except Exception:
            pass
            
        return None
    
    def select_best_model(self, task_type: str) -> str:
        """
        为指定任务选择最佳模型
        
        Args:
            task_type: 任务类型，如code_completion, code_optimization等
            
        Returns:
            str: 最佳模型名称
        """
        if not self._auto_select:
            # 如果不自动选择，返回默认模型
            return config.get("models.inference.name")
            
        suitable_models = []
        for name, info in self._available_models.items():
            if task_type in info.get("best_for", []) and self._check_hardware_compatibility(name):
                suitable_models.append((name, info))
        
        if not suitable_models:
            # 没有特别适合的模型，返回默认模型
            default_model = config.get("models.inference.name")
            logger.info(f"未找到适合任务 {task_type} 的模型，使用默认模型: {default_model}")
            return default_model
            
        # 按照RAM/VRAM需求排序，选择最小的满足需求的模型
        sorted_models = sorted(
            suitable_models, 
            key=lambda x: float(x[1].get("ram_required", "999GB").replace("GB", ""))
        )
        
        selected_model = sorted_models[0][0]
        logger.info(f"为任务 {task_type} 选择了最佳模型: {selected_model}")
        return selected_model
    
    def get_model_service(self, model_name: Optional[str] = None, task_type: Optional[str] = None) -> ModelService:
        """
        获取模型服务实例
        
        Args:
            model_name: 模型名称，如果为None则自动选择
            task_type: 任务类型，用于自动选择模型
            
        Returns:
            ModelService: 模型服务实例
        """
        # 确定要使用的模型
        if model_name is None:
            if task_type:
                model_name = self.select_best_model(task_type)
            else:
                model_name = config.get("models.inference.name")
        
        with self._lock:
            # 如果模型服务已经创建，直接返回
            if model_name in self._model_services:
                # 更新使用时间
                self._model_last_used[model_name] = time.time()
                return self._model_services[model_name]
            
            # 确保模型已加载
            self._load_model(model_name)
            
            # 创建新的模型服务实例
            model_service = OllamaService(model_name)
            self._model_services[model_name] = model_service
            self._model_last_used[model_name] = time.time()
            
            return model_service
    
    def get_embedding_model_service(self, model_name: Optional[str] = None) -> ModelService:
        """
        获取嵌入模型服务
        
        Args:
            model_name: 模型名称，如果为None则使用配置的默认嵌入模型
            
        Returns:
            ModelService: 模型服务实例
        """
        # 使用默认嵌入模型
        if model_name is None:
            model_name = config.get("models.embedding.name")
            
        return self.get_model_service(model_name)
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        return list(self._available_models.values())

    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本，带参数自适应和性能监控
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            str: 生成的文本
        """
        # 合并默认参数和自定义参数
        params = self._optimize_params(kwargs)
        
        # 记录请求开始时间
        start_time = time.time()
        
        try:
            # 调用模型服务生成文本
            result = self.model_service.generate(prompt, **params)
            
            # 记录请求信息
            end_time = time.time()
            self._record_request(
                prompt_length=len(prompt),
                response_length=len(result),
                execution_time=end_time - start_time,
                success=True
            )
            
            return result
        except Exception as e:
            # 记录失败的请求
            end_time = time.time()
            self._record_request(
                prompt_length=len(prompt),
                response_length=0,
                execution_time=end_time - start_time,
                success=False
            )
            logger.error(f"生成文本失败: {str(e)}")
            return f"生成文本失败: {str(e)}"
    
    def generate_stream(self, prompt: str, **kwargs) -> Any:
        """
        流式生成文本，带参数自适应和性能监控
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            Generator: 生成文本的流
        """
        # 合并默认参数和自定义参数
        params = self._optimize_params(kwargs)
        
        # 无法直接监控流式响应的时间，这里只记录开始时间
        start_time = time.time()
        
        # 创建回调函数来收集响应长度
        response_length = [0]
        
        def callback(token: str):
            response_length[0] += len(token)
        
        # 添加回调参数
        params["callback"] = callback
        
        try:
            # 返回生成器
            return self.model_service.generate_stream(prompt, **params)
        except Exception as e:
            # 记录失败的请求
            end_time = time.time()
            self._record_request(
                prompt_length=len(prompt),
                response_length=0,
                execution_time=end_time - start_time,
                success=False
            )
            logger.error(f"流式生成文本失败: {str(e)}")
            raise e
    
    def embed(self, texts: Any, **kwargs) -> List[List[float]]:
        """
        生成嵌入向量，带性能监控
        
        Args:
            texts: 文本或文本列表
            **kwargs: 其他参数
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        start_time = time.time()
        
        try:
            # 调用模型服务生成嵌入向量
            result = self.model_service.embed(texts, **kwargs)
            
            # 记录请求信息
            end_time = time.time()
            self._record_request(
                prompt_length=len(texts) if isinstance(texts, str) else sum(len(t) for t in texts),
                response_length=len(result),
                execution_time=end_time - start_time,
                success=True,
                request_type="embedding"
            )
            
            return result
        except Exception as e:
            # 记录失败的请求
            end_time = time.time()
            self._record_request(
                prompt_length=len(texts) if isinstance(texts, str) else sum(len(t) for t in texts),
                response_length=0,
                execution_time=end_time - start_time,
                success=False,
                request_type="embedding"
            )
            logger.error(f"生成嵌入向量失败: {str(e)}")
            return []
    
    def switch_model(self, model_name: str) -> bool:
        """
        切换到不同的模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 是否切换成功
        """
        try:
            # 创建新的模型服务
            new_service = ModelServiceFactory.create_service(model_name=model_name)
            
            # 检查新模型服务是否健康
            if not new_service.health_check():
                logger.error(f"模型切换失败: {model_name} 服务不可用")
                return False
            
            # 更新模型服务
            self.model_service = new_service
            
            # 更新配置
            config.set("models.inference.name", model_name)
            
            # 重置参数
            self.current_params = self._get_default_params()
            
            logger.info(f"已切换到模型: {model_name}")
            return True
        except Exception as e:
            logger.error(f"模型切换失败: {str(e)}")
            return False
    
    def set_performance_mode(self, mode: str) -> bool:
        """
        设置性能模式
        
        Args:
            mode: 性能模式 (balanced, speed, quality)
            
        Returns:
            bool: 设置是否成功
        """
        if mode not in ["balanced", "speed", "quality"]:
            logger.warning(f"无效的性能模式: {mode}，应为 balanced, speed, quality 之一")
            return False
        
        self.performance_mode = mode
        config.set("models.adaptive_params.performance_mode", mode)
        
        # 更新当前参数
        self.current_params = self._get_default_params()
        
        logger.info(f"已设置性能模式为: {mode}")
        return True
    
    def check_service_health(self) -> bool:
        """
        检查模型服务健康状态
        
        Returns:
            bool: 服务是否健康
        """
        return self.model_service.health_check()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Returns:
            Dict[str, Any]: 性能统计信息
        """
        if not self.request_history:
            return {
                "avg_response_time": 0,
                "success_rate": 100.0,
                "total_requests": 0
            }
        
        # 计算统计信息
        success_count = sum(1 for req in self.request_history if req.get("success", False))
        total = len(self.request_history)
        success_rate = (success_count / total) * 100 if total > 0 else 0
        
        # 计算平均响应时间
        response_times = [req.get("execution_time", 0) for req in self.request_history if req.get("success", False)]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "avg_response_time": avg_response_time,
            "success_rate": success_rate,
            "total_requests": total
        }
    
    def _record_request(self, prompt_length: int, response_length: int, 
                       execution_time: float, success: bool,
                       request_type: str = "generation") -> None:
        """记录请求信息"""
        self.request_history.append({
            "timestamp": time.time(),
            "prompt_length": prompt_length,
            "response_length": response_length,
            "execution_time": execution_time,
            "success": success,
            "type": request_type
        })
        
        # 限制历史记录长度
        if len(self.request_history) > self.max_history_length:
            self.request_history = self.request_history[-self.max_history_length:]
    
    def _optimize_params(self, user_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据系统状态和历史性能优化模型参数
        
        Args:
            user_params: 用户指定的参数
            
        Returns:
            Dict[str, Any]: 优化后的参数
        """
        # 如果禁用自适应参数，则直接使用用户参数和默认参数的合并
        if not self.adaptive_params_enabled:
            return {**self.current_params, **user_params}
        
        # 获取系统负载
        system_load = self._get_system_load()
        cpu_load = system_load.get("cpu", 0)
        memory_load = system_load.get("memory", 0)
        
        # 根据系统负载和性能模式调整参数
        optimized_params = self.current_params.copy()
        
        # 系统负载高，降低参数
        if cpu_load > self.cpu_threshold or memory_load > self.memory_threshold:
            if self.performance_mode != "quality":  # 在速度或平衡模式下才考虑降低质量
                # 降低温度
                optimized_params["temperature"] = min(0.1, optimized_params.get("temperature", 0.2))
                
                # 如果有max_tokens，可以适当降低
                if "max_tokens" in optimized_params:
                    optimized_params["max_tokens"] = int(optimized_params["max_tokens"] * 0.8)
                
                logger.debug(f"系统负载高 (CPU: {cpu_load}%, 内存: {memory_load}%)，调整模型参数以降低负载")
        
        # 根据性能模式进一步调整
        if self.performance_mode == "speed":
            # 速度优先模式
            optimized_params["temperature"] = min(0.1, optimized_params.get("temperature", 0.2))
            optimized_params["timeout"] = max(10, optimized_params.get("timeout", 30) * 0.7)
            
            # 如果有max_tokens，可以降低以加快速度
            if "max_tokens" in optimized_params:
                optimized_params["max_tokens"] = int(optimized_params["max_tokens"] * 0.7)
                
        elif self.performance_mode == "quality":
            # 质量优先模式
            optimized_params["temperature"] = max(0.3, optimized_params.get("temperature", 0.2))
            optimized_params["timeout"] = optimized_params.get("timeout", 30) * 1.5  # 增加超时时间
            
        # 合并用户参数（用户参数优先级最高）
        return {**optimized_params, **user_params}
    
    def _get_default_params(self) -> Dict[str, Any]:
        """
        获取当前模型的默认参数
        
        Returns:
            Dict[str, Any]: 默认参数
        """
        model_name = self.model_service.inference_model
        model_type = self._get_model_type(model_name)
        
        # 获取模型类型的默认参数
        default_params = self.model_type_params.get(model_type, {}).copy()
        
        # 根据性能模式调整参数
        if self.performance_mode == "speed":
            # 速度优先，降低质量参数
            if "temperature" in default_params:
                default_params["temperature"] = min(0.1, default_params["temperature"])
            if "max_tokens" in default_params:
                default_params["max_tokens"] = int(default_params["max_tokens"] * 0.7)
        elif self.performance_mode == "quality":
            # 质量优先，提高质量参数
            if "temperature" in default_params:
                default_params["temperature"] = max(0.3, default_params["temperature"])
        
        return default_params
    
    def _get_model_type(self, model_name: str) -> str:
        """
        根据模型名称获取模型类型
        
        Args:
            model_name: 模型名称
            
        Returns:
            str: 模型类型
        """
        model_name_lower = model_name.lower()
        
        if "llama" in model_name_lower:
            return "llama"
        elif "deepseek" in model_name_lower:
            return "deepseek"
        elif "mistral" in model_name_lower:
            return "mistral"
        elif "qwen" in model_name_lower:
            return "qwen"
        elif "yi" in model_name_lower:
            return "yi"
        else:
            return "default"
    
    def _load_model_type_params(self) -> Dict[str, Dict[str, Any]]:
        """
        加载模型类型参数
        
        Returns:
            Dict[str, Dict[str, Any]]: 模型类型到参数的映射
        """
        # 默认参数设置
        default_params = {
            "llama": {
                "temperature": 0.2,
                "max_tokens": 2048,
                "timeout": 30
            },
            "deepseek": {
                "temperature": 0.1,  # DeepSeek默认温度低一些，提高精度
                "max_tokens": 4096,
                "timeout": 40
            },
            "mistral": {
                "temperature": 0.2,
                "max_tokens": 2048,
                "timeout": 30
            },
            "qwen": {
                "temperature": 0.3,
                "max_tokens": 8192,  # 通义千问支持更长上下文
                "timeout": 45
            },
            "yi": {
                "temperature": 0.2,
                "max_tokens": 4096,
                "timeout": 35
            },
            "default": {
                "temperature": 0.2,
                "max_tokens": 2048,
                "timeout": 30
            }
        }
        
        # 尝试从配置中加载
        config_params = config.get("models.type_params", {})
        
        # 合并配置参数和默认参数
        for model_type, params in config_params.items():
            if model_type in default_params:
                default_params[model_type].update(params)
            else:
                default_params[model_type] = params
        
        return default_params
    
    def _get_system_load(self) -> Dict[str, float]:
        """
        获取系统负载
        
        Returns:
            Dict[str, float]: 系统负载信息
        """
        try:
            import psutil
            
            # 获取CPU和内存使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            return {
                "cpu": cpu_percent,
                "memory": memory_percent
            }
        except ImportError:
            logger.warning("未安装psutil，无法获取系统负载")
            return {"cpu": 0, "memory": 0}
        except Exception as e:
            logger.error(f"获取系统负载失败: {str(e)}")
            return {"cpu": 0, "memory": 0}
    
    def _get_model_details(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型详细信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            Dict[str, Any]: 模型详情
        """
        # 从模型名称提取基本信息
        model_parts = model_name.split(":")
        base_name = model_parts[0]
        version = model_parts[1] if len(model_parts) > 1 else ""
        
        # 根据模型名称判断类型和特性
        model_type = self._get_model_type(base_name)
        
        # 模型参数估计
        params = "未知"
        if "7b" in model_name.lower():
            params = "7B"
        elif "13b" in model_name.lower():
            params = "13B"
        elif "34b" in model_name.lower():
            params = "34B"
        elif "70b" in model_name.lower():
            params = "70B"
        
        # 量化信息
        quantization = "未知"
        if "q4" in model_name.lower():
            quantization = "4-bit"
        elif "q5" in model_name.lower():
            quantization = "5-bit"
        elif "q8" in model_name.lower():
            quantization = "8-bit"
            
        return {
            "base_name": base_name,
            "version": version,
            "type": model_type,
            "parameters": params,
            "quantization": quantization
        }

# 创建一个模型管理器实例供使用
model_manager = ModelManager() 