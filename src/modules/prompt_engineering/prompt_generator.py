#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提示生成器模块

根据上下文和任务类型生成优化的提示
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class PromptGenerator:
    """提示生成器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化提示生成器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.templates_dir = os.path.join("data", "prompt_templates")
        self.templates = self._load_templates()
        logger.info("提示生成器初始化完成")
    
    def _load_templates(self) -> Dict[str, str]:
        """加载提示模板
        
        Returns:
            Dict[str, str]: 模板字典
        """
        templates = {}
        
        # 确保模板目录存在
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # 加载默认模板
        default_templates = {
            "code_explanation": "请解释以下{language}代码的功能:\n\n```{language}\n{code}\n```",
            "code_generation": "请使用{language}编写一个{task}的函数。{requirements}",
            "code_review": "请审查以下{language}代码，指出潜在的问题和改进建议:\n\n```{language}\n{code}\n```",
            "code_completion": "请完成以下{language}代码:\n\n```{language}\n{code}\n```",
            "error_diagnosis": "我的{language}代码出现了以下错误，请帮我诊断问题:\n\n```{language}\n{code}\n```\n\n错误信息:\n```\n{error}\n```",
            "general_question": "{user_query}"
        }
        
        # 保存默认模板到文件
        for name, template in default_templates.items():
            template_path = os.path.join(self.templates_dir, f"{name}.txt")
            if not os.path.exists(template_path):
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(template)
        
        # 从文件加载所有模板
        for file in os.listdir(self.templates_dir):
            if file.endswith('.txt'):
                template_name = os.path.splitext(file)[0]
                template_path = os.path.join(self.templates_dir, file)
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        templates[template_name] = f.read()
                except Exception as e:
                    logger.error(f"加载模板失败: {template_path}, 错误: {str(e)}")
        
        logger.info(f"已加载 {len(templates)} 个提示模板")
        return templates
    
    def generate(self, context: Dict[str, Any]) -> str:
        """生成提示
        
        Args:
            context: 上下文数据
        
        Returns:
            str: 生成的提示
        """
        # 获取任务类型
        task_type = context.get('task', 'general_question')
        
        # 获取对应模板
        template = self.templates.get(task_type, self.templates.get('general_question'))
        
        # 使用上下文填充模板
        try:
            prompt = template.format(**context)
            return prompt
        except KeyError as e:
            logger.warning(f"模板填充失败，缺少键: {e}")
            # 回退到通用模板
            return context.get('user_query', '请提供更多信息')
    
    def add_template(self, name: str, template: str) -> bool:
        """添加新模板
        
        Args:
            name: 模板名称
            template: 模板内容
        
        Returns:
            bool: 是否成功添加
        """
        try:
            # 保存到文件
            template_path = os.path.join(self.templates_dir, f"{name}.txt")
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template)
            
            # 添加到内存中的模板字典
            self.templates[name] = template
            
            logger.info(f"已添加模板: {name}")
            return True
        except Exception as e:
            logger.error(f"添加模板失败: {name}, 错误: {str(e)}")
            return False
    
    def get_template(self, name: str) -> Optional[str]:
        """获取模板
        
        Args:
            name: 模板名称
        
        Returns:
            Optional[str]: 模板内容
        """
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """列出所有模板
        
        Returns:
            List[str]: 模板名称列表
        """
        return list(self.templates.keys())
    
    def generate_system_prompt(self, system_config: Dict[str, Any]) -> str:
        """生成系统提示
        
        Args:
            system_config: 系统配置
        
        Returns:
            str: 系统提示
        """
        # 构建系统提示
        system_prompt = "你是一个AI助手"
        
        if system_config.get('name'):
            system_prompt = f"你是{system_config['name']}"
        
        if system_config.get('description'):
            system_prompt += f"，{system_config['description']}"
        
        if system_config.get('capabilities'):
            capabilities = system_config['capabilities']
            system_prompt += "。你能够："
            for capability in capabilities:
                system_prompt += f"\n- {capability}"
        
        if system_config.get('constraints'):
            constraints = system_config['constraints']
            system_prompt += "\n\n你的限制："
            for constraint in constraints:
                system_prompt += f"\n- {constraint}"
        
        return system_prompt 