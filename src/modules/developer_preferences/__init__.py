"""
开发者偏好系统

负责管理开发者的编码风格、项目类型、功能需求等偏好设置，
并在代码生成、补全等功能中应用这些偏好。
"""

from .preference_manager import PreferenceManager
from .preference_models import CodeStyle, ProjectType, FeatureRequirement, DeveloperPreferences

__all__ = [
    'PreferenceManager',
    'CodeStyle',
    'ProjectType',
    'FeatureRequirement',
    'DeveloperPreferences'
] 