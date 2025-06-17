"""
依赖注入容器

提供依赖注入功能，用于管理服务依赖，降低组件间的耦合度
"""

import inspect
from typing import Dict, Any, Callable, Optional, Type, TypeVar, get_type_hints

T = TypeVar('T')

class DependencyContainer:
    """
    依赖注入容器
    
    管理应用程序中的服务依赖，提供依赖注入功能
    """
    
    def __init__(self):
        """初始化依赖容器"""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[..., Any]] = {}
        self._singletons: Dict[str, bool] = {}
    
    def register(self, interface: Type[T], implementation: Optional[Type[T]] = None, 
                singleton: bool = True, factory: Optional[Callable[..., T]] = None) -> None:
        """
        注册服务
        
        Args:
            interface: 服务接口或类型
            implementation: 服务实现类，如果为None则使用interface作为实现
            singleton: 是否为单例
            factory: 自定义工厂函数，用于创建服务实例
        """
        if not implementation and not factory:
            implementation = interface
            
        service_key = self._get_key(interface)
        
        if factory:
            self._factories[service_key] = factory
        else:
            self._factories[service_key] = self._create_factory(implementation)
            
        self._singletons[service_key] = singleton
    
    def get(self, interface: Type[T]) -> T:
        """
        获取服务实例
        
        Args:
            interface: 服务接口或类型
            
        Returns:
            服务实例
            
        Raises:
            KeyError: 如果请求的服务未注册
        """
        service_key = self._get_key(interface)
        
        # 检查服务是否已注册
        if service_key not in self._factories:
            raise KeyError(f"服务 '{service_key}' 未注册")
        
        # 对于单例服务，检查是否已有实例
        if self._singletons.get(service_key, False):
            if service_key not in self._services:
                self._services[service_key] = self._factories[service_key](self)
            return self._services[service_key]
        
        # 非单例服务每次都创建新实例
        return self._factories[service_key](self)
    
    def _get_key(self, interface: Type) -> str:
        """
        获取服务键名
        
        Args:
            interface: 服务接口或类型
            
        Returns:
            服务键名
        """
        if hasattr(interface, "__name__"):
            return interface.__name__
        return str(interface)
    
    def _create_factory(self, implementation: Type[T]) -> Callable[..., T]:
        """
        创建服务工厂函数
        
        Args:
            implementation: 服务实现类
            
        Returns:
            工厂函数
        """
        def factory(container):
            # 获取构造函数参数类型
            try:
                type_hints = get_type_hints(implementation.__init__)
                # 移除返回值类型提示
                if 'return' in type_hints:
                    del type_hints['return']
                    
                # 获取参数名称
                signature = inspect.signature(implementation.__init__)
                params = signature.parameters
                
                # 跳过self参数
                param_names = list(params.keys())[1:]
                
                kwargs = {}
                for name in param_names:
                    if name in type_hints:
                        # 尝试从容器中解析依赖
                        try:
                            kwargs[name] = container.get(type_hints[name])
                        except KeyError:
                            # 如果参数有默认值，则使用默认值
                            if params[name].default is not inspect.Parameter.empty:
                                kwargs[name] = params[name].default
                            else:
                                raise KeyError(f"无法解析 '{implementation.__name__}' 的依赖 '{name}'")
                
                return implementation(**kwargs)
            except (AttributeError, TypeError):
                # 如果无法获取类型提示或构造函数，则尝试直接实例化
                return implementation()
                
        return factory
    
    def clear(self) -> None:
        """清除所有注册的服务"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()

# 创建全局依赖容器实例
container = DependencyContainer()

def get_container() -> DependencyContainer:
    """
    获取全局依赖容器实例
    
    Returns:
        依赖容器实例
    """
    return container 