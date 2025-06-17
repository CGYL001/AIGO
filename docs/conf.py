"""
Sphinx配置文件 - AIgo文档生成
"""

import os
import sys
import datetime

# 将项目根目录添加到路径
sys.path.insert(0, os.path.abspath('..'))

# 项目信息
project = 'AIgo'
copyright = f'{datetime.datetime.now().year}, AIgo Team'
author = 'AIgo Team'

# 版本信息
version = '0.1.0'
release = '0.1.0'

# 扩展
extensions = [
    'sphinx.ext.autodoc',     # 自动文档生成
    'sphinx.ext.viewcode',    # 查看源码链接
    'sphinx.ext.napoleon',    # 支持Google风格的文档
    'sphinx.ext.intersphinx', # 链接到其他文档
    'autoapi.extension',      # 自动API文档生成
    'sphinxcontrib.httpdomain', # HTTP API文档
]

# AutoAPI设置
autoapi_type = 'python'
autoapi_dirs = ['../src']
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',
    'imported-members',
]

# 主题配置
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
}

# HTML输出设置
html_static_path = ['_static']
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# 语言设置
language = 'zh_CN'

# 参考文献扩展
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'flask': ('https://flask.palletsprojects.com/en/2.0.x/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
}

# Autodoc配置
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# Napoleon配置 - 支持Google风格文档
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_custom_sections = None

# 添加自定义CSS
html_css_files = [
    'custom.css',
] 