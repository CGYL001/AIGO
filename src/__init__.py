# 初始化src包
# 注释掉以下重定向代码，直接使用src模块

# # Auto-generated compatibility shim.
# import importlib, types, sys as _sys

# # Redirect the top-level 'src' package to 'aigo'
# _aigo = importlib.import_module('aigo')
# _sys.modules[__name__] = _aigo

# # Also expose 'src.modules' -> 'aigo.modules' for backward compatibility
# _sys.modules['src.modules'] = importlib.import_module('aigo.modules')

# 直接初始化
__version__ = '0.1.0'
