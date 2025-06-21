"""模型重构器

负责协调模型结构优化过程
"""

import logging
from typing import Dict, List, Any, Optional

from .performance_analyzer import PerformanceAnalyzer
from .component_optimizer import ComponentOptimizer

logger = logging.getLogger(__name__)

class ModelRestructurer:
    """模型重构器类"""

    def __init__(self, config=None):
        """初始化模型重构器

        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.analyzer = PerformanceAnalyzer(self.config)
        self.optimizer = ComponentOptimizer(self.config)
        logger.info("模型重构器初始化完成")

    def analyze_model(self, model_path: str) -> Dict[str, Any]:
        """分析模型结构

        Args:
            model_path: 模型路径

        Returns:
            Dict[str, Any]: 分析结果
        """
        return self.analyzer.analyze_model(model_path)

    def optimize_model(self, model_path: str, output_path: str, optimization_level: int = 1) -> Dict[str, Any]:
        """优化模型结构

        Args:
            model_path: 模型路径
            output_path: 输出路径
            optimization_level: 优化级别

        Returns:
            Dict[str, Any]: 优化结果
        """
        # 分析模型
        analysis = self.analyzer.analyze_model(model_path)
        
        # 优化模型
        result = self.optimizer.optimize_model(model_path, output_path, analysis, optimization_level)
        
        return result
