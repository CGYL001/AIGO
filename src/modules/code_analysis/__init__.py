"""
代码分析模块 - 提供代码结构分析、质量评估和优化建议
"""

from src.modules.code_analysis.analyzer import CodeAnalyzer
from src.modules.code_analysis.metrics import MetricsCalculator
from src.modules.code_analysis.structure import StructureAnalyzer
from src.modules.code_analysis.quality import QualityAnalyzer

__all__ = ["CodeAnalyzer", "MetricsCalculator", "StructureAnalyzer", "QualityAnalyzer"] 