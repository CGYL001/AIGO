import requests
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Generator, Callable

from src.utils import config, logger


class ModelService(ABC):
    """
    模型服务抽象基类，定义了与AI模型交互的接口
    """
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            str: 生成的文本
        """
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, callback: Callable[[str], None] = None, **kwargs) -> Generator[str, None, None]:
        """
        流式生成文本
        
        Args:
            prompt: 提示词
            callback: 每生成一段文本时的回调函数
            **kwargs: 其他参数
            
        Returns:
            Generator[str, None, None]: 生成文本的生成器
        """
        pass
    
    @abstractmethod
    def embed(self, texts: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """
        生成文本嵌入向量
        
        Args:
            texts: 单个文本或文本列表
            **kwargs: 其他参数
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """
        检查模型服务健康状态
        
        Returns:
            bool: 服务是否健康
        """
        pass

    def is_available(self):
        """
        检查模型服务是否可用
        
        Returns:
            bool: 模型服务是否可用
        """
        try:
            # 尝试简单请求以检查服务状态
            if self.provider == "ollama":
                import requests
                response = requests.get(f"{self.api_base}/api/tags", timeout=2)
                return response.status_code == 200
            elif self.provider == "openai":
                # 不实际调用API，只检查是否有token
                return bool(self.api_key)
            else:
                # 对于其他提供商添加类似的检查
                return True
        except Exception as e:
            logger.warning(f"模型服务检查失败: {str(e)}")
            return False


class OllamaService(ModelService):
    """
    Ollama模型服务实现
    """
    
    def __init__(self, model_name: str = None):
        """
        初始化Ollama服务
        
        Args:
            model_name: 使用的模型名称，如果为None则从配置中获取
        """
        self.inference_model = model_name or config.get("models.inference.name", "codellama:7b-instruct-q4_K_M")
        self.embedding_model = config.get("models.embedding.name", "nomic-embed-text")
        self.api_base = config.get("models.inference.api_base", "http://localhost:11434")
        self.generate_endpoint = f"{self.api_base}/api/generate"
        self.embeddings_endpoint = f"{self.api_base}/api/embeddings"
        self.chat_endpoint = f"{self.api_base}/api/chat"
        self.max_retries = config.get("models.inference.max_retries", 3)
        self.retry_delay = config.get("models.inference.retry_delay_seconds", 1)
        
        logger.info(f"初始化Ollama模型服务，推理模型: {self.inference_model}，嵌入模型: {self.embedding_model}")
    
    def generate(self, prompt: str, 
                model: str = None, 
                temperature: float = None, 
                max_tokens: int = None,
                system_message: str = None,
                timeout: int = None) -> str:
        """
        使用Ollama生成文本
        
        Args:
            prompt: 提示词
            model: 模型名称，如果不指定则使用配置中的默认模型
            temperature: 温度参数，控制生成随机性
            max_tokens: 生成的最大token数
            system_message: 系统消息
            timeout: 请求超时时间(秒)
            
        Returns:
            str: 生成的文本
        """
        model = model or self.inference_model
        temperature = temperature or config.get("models.inference.temperature", 0.2)
        timeout = timeout or config.get("models.inference.timeout_seconds", 30)
        
        # 准备请求数据
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature
        }
        
        # 添加可选参数
        if max_tokens:
            data["max_tokens"] = max_tokens
        if system_message:
            data["system"] = system_message
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"发送生成请求到模型 {model}: {prompt[:50]}...")
                response = requests.post(self.generate_endpoint, json=data, timeout=timeout)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt+1}/{self.max_retries})")
                time.sleep(self.retry_delay)
            except requests.exceptions.ConnectionError:
                logger.warning(f"连接错误 (尝试 {attempt+1}/{self.max_retries})")
                time.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"生成请求失败: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    return f"生成失败: {str(e)}"
        
        return "模型请求失败: 超过最大重试次数"
    
    def generate_stream(self, prompt: str, 
                       callback: Callable[[str], None] = None,
                       model: str = None, 
                       temperature: float = None, 
                       max_tokens: int = None,
                       system_message: str = None,
                       timeout: int = None) -> Generator[str, None, None]:
        """
        使用Ollama流式生成文本
        
        Args:
            prompt: 提示词
            callback: 每生成一段文本时的回调函数
            model: 模型名称，如果不指定则使用配置中的默认模型
            temperature: 温度参数，控制生成随机性
            max_tokens: 生成的最大token数
            system_message: 系统消息
            timeout: 请求超时时间(秒)
            
        Yields:
            str: 生成的文本片段
        """
        model = model or self.inference_model
        temperature = temperature or config.get("models.inference.temperature", 0.2)
        timeout = timeout or config.get("models.inference.timeout_seconds", 60)
        
        # 准备请求数据
        data = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "temperature": temperature
        }
        
        # 添加可选参数
        if max_tokens:
            data["max_tokens"] = max_tokens
        if system_message:
            data["system"] = system_message
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"发送流式生成请求到模型 {model}: {prompt[:50]}...")
                response = requests.post(
                    self.generate_endpoint, 
                    json=data, 
                    stream=True,
                    timeout=timeout
                )
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            line_data = json.loads(line)
                            token = line_data.get("response", "")
                            if token:
                                if callback:
                                    callback(token)
                                yield token
                        except json.JSONDecodeError:
                            logger.warning(f"无法解析流式响应: {line}")
                
                break  # 成功完成，退出重试循环
            except requests.exceptions.Timeout:
                logger.warning(f"流式请求超时 (尝试 {attempt+1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    yield "流式生成失败: 请求超时"
            except requests.exceptions.ConnectionError:
                logger.warning(f"连接错误 (尝试 {attempt+1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    yield "流式生成失败: 连接错误"
            except Exception as e:
                logger.error(f"流式生成请求失败: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    yield f"流式生成失败: {str(e)}"
    
    def embed(self, texts: Union[str, List[str]], model: str = None, timeout: int = None) -> List[List[float]]:
        """
        使用Ollama生成嵌入向量
        
        Args:
            texts: 单个文本或文本列表
            model: 嵌入模型名称，如果不指定则使用配置中的默认嵌入模型
            timeout: 请求超时时间(秒)
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        model = model or self.embedding_model
        timeout = timeout or config.get("models.embedding.timeout_seconds", 30)
        
        # 确保texts是列表
        if isinstance(texts, str):
            texts = [texts]
            
        results = []
        
        for text in texts:
            data = {
                "model": model,
                "prompt": text
            }
            
            # 重试机制
            for attempt in range(self.max_retries):
                try:
                    logger.debug(f"发送嵌入请求到模型 {model}: {text[:30]}...")
                    response = requests.post(self.embeddings_endpoint, json=data, timeout=timeout)
                    response.raise_for_status()
                    result = response.json()
                    embedding = result.get("embedding", [])
                    results.append(embedding)
                    break  # 成功后跳出重试循环
                except requests.exceptions.Timeout:
                    logger.warning(f"嵌入请求超时 (尝试 {attempt+1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                except requests.exceptions.ConnectionError:
                    logger.warning(f"连接错误 (尝试 {attempt+1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                except Exception as e:
                    logger.error(f"嵌入请求失败: {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                    else:
                        # 在失败的情况下返回空向量
                        results.append([])
                        
        return results
    
    def health_check(self) -> bool:
        """
        检查Ollama服务健康状态
        
        Returns:
            bool: 服务是否健康
        """
        try:
            # 检查API是否可访问
            response = requests.get(f"{self.api_base}/api/tags", timeout=5)
            
            if response.status_code != 200:
                logger.warning(f"Ollama健康检查失败，状态码: {response.status_code}")
                return False
                
            # 检查是否有可用模型
            models = response.json().get("models", [])
            if not models:
                logger.warning("Ollama健康检查: 未找到可用模型")
                return False
                
            # 检查推理模型是否可用
            inference_base_name = self.inference_model.split(":")[0]
            embedding_base_name = self.embedding_model.split(":")[0]
            
            model_names = [m.get("name", "").split(":")[0] for m in models]
            
            if not any(inference_base_name == name for name in model_names):
                logger.warning(f"Ollama健康检查: 未找到推理模型 {inference_base_name}")
                return False
                
            if not any(embedding_base_name == name for name in model_names):
                logger.warning(f"Ollama健康检查: 未找到嵌入模型 {embedding_base_name}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Ollama健康检查异常: {str(e)}")
            return False


class ModelServiceFactory:
    """
    模型服务工厂，根据配置创建适当的模型服务
    """
    
    @staticmethod
    def create_service(provider: str = None, model_name: str = None) -> ModelService:
        """
        创建模型服务
        
        Args:
            provider: 服务提供商，默认从配置中获取
            model_name: 模型名称，如果不指定则从配置中获取
            
        Returns:
            ModelService: 创建的模型服务
        """
        provider = provider or config.get("models.inference.provider", "ollama")
        
        if provider.lower() == "ollama":
            return OllamaService(model_name)
        # 可以添加其他提供商的支持
        else:
            logger.warning(f"不支持的模型提供商: {provider}，使用Ollama作为备选")
            return OllamaService(model_name) 