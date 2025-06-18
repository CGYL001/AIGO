"""
偏好管理器

负责开发者偏好的存储、检索、更新和应用
"""

import os
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import shutil
from datetime import datetime

from .preference_models import DeveloperPreferences, CodeStyleType, CommentLevel, ProjectDomain, TestingStrategy, FrameworkPreference

logger = logging.getLogger(__name__)

class PreferenceManager:
    """
    管理开发者偏好的存储和检索
    """
    
    def __init__(self, storage_path: str = None):
        """
        初始化偏好管理器
        
        Args:
            storage_path: 偏好文件存储路径，默认为 data/preferences
        """
        # 设置存储路径
        if storage_path is None:
            self.storage_path = Path("data") / "preferences"
        else:
            self.storage_path = Path(storage_path)
            
        # 确保存储目录存在
        os.makedirs(self.storage_path, exist_ok=True)
        
        # 当前活跃偏好
        self.active_preference: Optional[DeveloperPreferences] = None
        
        # 加载默认偏好
        self._initialize_default_preference()
    
    def _initialize_default_preference(self):
        """初始化默认偏好设置"""
        default_pref_path = self.storage_path / "default.json"
        
        # 如果默认偏好文件不存在，创建一个
        if not default_pref_path.exists():
            default_pref = DeveloperPreferences(
                id="default",
                name="默认偏好",
                description="系统默认偏好配置"
            )
            self.save_preference(default_pref)
        
        # 加载默认偏好作为当前活跃偏好
        try:
            self.active_preference = self.load_preference("default")
        except Exception as e:
            logger.error(f"加载默认偏好设置失败: {e}")
            # 创建一个新的默认偏好
            self.active_preference = DeveloperPreferences(
                id="default",
                name="默认偏好",
                description="系统默认偏好配置"
            )
    
    def create_preference(self, name: str, description: str = "") -> DeveloperPreferences:
        """
        创建新的偏好设置
        
        Args:
            name: 偏好名称
            description: 偏好描述
            
        Returns:
            新创建的偏好设置
        """
        pref_id = str(uuid.uuid4())
        preference = DeveloperPreferences(
            id=pref_id,
            name=name,
            description=description,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.save_preference(preference)
        self.active_preference = preference
        return preference
    
    def save_preference(self, preference: DeveloperPreferences) -> bool:
        """
        保存偏好设置到文件
        
        Args:
            preference: 要保存的偏好设置
            
        Returns:
            保存是否成功
        """
        try:
            # 更新时间戳
            preference.update_timestamp()
            
            # 确保有ID
            if not preference.id:
                preference.id = str(uuid.uuid4())
                
            # 保存到文件
            file_path = self.storage_path / f"{preference.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(preference.to_json())
                
            logger.info(f"偏好设置 '{preference.name}' (ID: {preference.id}) 已保存")
            return True
        except Exception as e:
            logger.error(f"保存偏好设置失败: {e}")
            return False
    
    def load_preference(self, preference_id: str) -> Optional[DeveloperPreferences]:
        """
        从文件加载偏好设置
        
        Args:
            preference_id: 偏好设置ID
            
        Returns:
            加载的偏好设置，如果加载失败则返回None
        """
        try:
            file_path = self.storage_path / f"{preference_id}.json"
            if not file_path.exists():
                logger.warning(f"偏好设置文件不存在: {file_path}")
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
                
            preference = DeveloperPreferences.from_json(json_data)
            return preference
        except Exception as e:
            logger.error(f"加载偏好设置失败 (ID: {preference_id}): {e}")
            return None
    
    def delete_preference(self, preference_id: str) -> bool:
        """
        删除偏好设置
        
        Args:
            preference_id: 偏好设置ID
            
        Returns:
            删除是否成功
        """
        try:
            # 不允许删除默认偏好
            if preference_id == "default":
                logger.warning("不能删除默认偏好设置")
                return False
                
            file_path = self.storage_path / f"{preference_id}.json"
            if not file_path.exists():
                logger.warning(f"偏好设置文件不存在: {file_path}")
                return False
                
            # 删除文件
            os.remove(file_path)
            
            # 如果删除的是当前活跃偏好，切换到默认偏好
            if self.active_preference and self.active_preference.id == preference_id:
                self.active_preference = self.load_preference("default")
                
            logger.info(f"偏好设置 (ID: {preference_id}) 已删除")
            return True
        except Exception as e:
            logger.error(f"删除偏好设置失败 (ID: {preference_id}): {e}")
            return False
    
    def list_preferences(self) -> List[Dict]:
        """
        列出所有偏好设置的基本信息
        
        Returns:
            偏好设置基本信息列表
        """
        preferences = []
        try:
            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        preferences.append({
                            "id": data.get("id", ""),
                            "name": data.get("name", ""),
                            "description": data.get("description", ""),
                            "created_at": data.get("created_at", ""),
                            "updated_at": data.get("updated_at", ""),
                            "is_active": data.get("is_active", False)
                        })
                except Exception as e:
                    logger.warning(f"读取偏好设置文件失败: {file_path}, 错误: {e}")
        except Exception as e:
            logger.error(f"列出偏好设置失败: {e}")
            
        return preferences
    
    def set_active_preference(self, preference_id: str) -> bool:
        """
        设置当前活跃的偏好设置
        
        Args:
            preference_id: 偏好设置ID
            
        Returns:
            设置是否成功
        """
        preference = self.load_preference(preference_id)
        if preference:
            self.active_preference = preference
            logger.info(f"活跃偏好设置已更改为: {preference.name} (ID: {preference.id})")
            return True
        return False
    
    def get_active_preference(self) -> DeveloperPreferences:
        """
        获取当前活跃的偏好设置
        
        Returns:
            当前活跃偏好设置，如果没有则返回默认偏好
        """
        if not self.active_preference:
            self._initialize_default_preference()
        return self.active_preference
    
    def update_preference(self, preference_id: str, update_data: Dict) -> Optional[DeveloperPreferences]:
        """
        更新偏好设置
        
        Args:
            preference_id: 要更新的偏好设置ID
            update_data: 更新数据
            
        Returns:
            更新后的偏好设置，如果更新失败则返回None
        """
        preference = self.load_preference(preference_id)
        if not preference:
            logger.warning(f"偏好设置不存在 (ID: {preference_id})")
            return None
            
        try:
            # 更新基本属性
            for key in ["name", "description", "is_active"]:
                if key in update_data:
                    setattr(preference, key, update_data[key])
            
            # 更新代码风格
            if "code_style" in update_data:
                preference.code_style = preference.code_style.from_dict(update_data["code_style"])
                
            # 更新项目类型
            if "project_type" in update_data:
                preference.project_type = preference.project_type.from_dict(update_data["project_type"])
                
            # 更新功能需求
            if "feature_requirements" in update_data:
                preference.feature_requirements = preference.feature_requirements.from_dict(update_data["feature_requirements"])
                
            # 更新自定义偏好
            if "custom_preferences" in update_data:
                preference.custom_preferences.update(update_data["custom_preferences"])
                
            # 保存更新后的偏好
            if self.save_preference(preference):
                # 如果更新的是活跃偏好，重新加载
                if self.active_preference and self.active_preference.id == preference_id:
                    self.active_preference = preference
                return preference
        except Exception as e:
            logger.error(f"更新偏好设置失败 (ID: {preference_id}): {e}")
            
        return None
    
    def export_preference(self, preference_id: str, export_path: str) -> bool:
        """
        导出偏好设置到指定路径
        
        Args:
            preference_id: 偏好设置ID
            export_path: 导出路径
            
        Returns:
            导出是否成功
        """
        try:
            src_path = self.storage_path / f"{preference_id}.json"
            if not src_path.exists():
                logger.warning(f"偏好设置文件不存在: {src_path}")
                return False
                
            # 确保导出目录存在
            export_dir = os.path.dirname(export_path)
            if export_dir:
                os.makedirs(export_dir, exist_ok=True)
                
            # 复制文件
            shutil.copy2(src_path, export_path)
            logger.info(f"偏好设置已导出到: {export_path}")
            return True
        except Exception as e:
            logger.error(f"导出偏好设置失败: {e}")
            return False
    
    def import_preference(self, import_path: str, new_id: str = None) -> Optional[DeveloperPreferences]:
        """
        从文件导入偏好设置
        
        Args:
            import_path: 导入文件路径
            new_id: 新的偏好设置ID，为空则使用生成的UUID
            
        Returns:
            导入的偏好设置，如果导入失败则返回None
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
                
            preference = DeveloperPreferences.from_json(json_data)
            
            # 设置新ID
            if new_id:
                preference.id = new_id
            else:
                preference.id = str(uuid.uuid4())
                
            # 更新时间戳
            preference.update_timestamp()
            
            # 保存到系统
            if self.save_preference(preference):
                return preference
        except Exception as e:
            logger.error(f"导入偏好设置失败: {e}")
            
        return None
    
    def generate_prompt_context(self) -> str:
        """
        生成当前活跃偏好的提示上下文
        
        Returns:
            提示上下文字符串
        """
        preference = self.get_active_preference()
        return preference.generate_context_prompt() if preference else ""
    
    def create_preference_from_template(self, template_type: str, name: str, description: str = "") -> Optional[DeveloperPreferences]:
        """
        从预定义模板创建偏好设置
        
        Args:
            template_type: 模板类型: 'web_app', 'cli', 'data_science', 'api', 'desktop_app'
            name: 偏好名称
            description: 偏好描述
            
        Returns:
            创建的偏好设置，如果创建失败则返回None
        """
        preference = None
        pref_id = str(uuid.uuid4())
        
        try:
            # 创建基础偏好
            preference = DeveloperPreferences(
                id=pref_id,
                name=name,
                description=description,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # 根据模板类型设置项目类型和功能需求
            if template_type == "web_app":
                preference.project_type.domain = ProjectDomain.WEB_BACKEND
                preference.project_type.preferred_languages = ["javascript", "typescript", "python"]
                preference.project_type.preferred_frameworks = {
                    "javascript": ["react", "vue", "express"],
                    "typescript": ["angular", "next.js", "nest.js"],
                    "python": ["django", "flask"]
                }
                preference.project_type.architecture_patterns = ["MVC", "REST API", "SPA"]
                
                preference.feature_requirements.authentication = True
                preference.feature_requirements.authorization = True
                preference.feature_requirements.data_validation = True
                preference.feature_requirements.security_features = True
                preference.feature_requirements.file_handling = True
                
            elif template_type == "cli":
                preference.project_type.domain = ProjectDomain.CLI
                preference.project_type.preferred_languages = ["python", "javascript", "go", "rust"]
                preference.project_type.preferred_frameworks = {
                    "python": ["click", "typer", "argparse"],
                    "javascript": ["commander", "yargs"],
                    "go": ["cobra", "cli"],
                    "rust": ["clap", "structopt"]
                }
                preference.project_type.architecture_patterns = ["Command Pattern", "Module-based"]
                preference.project_type.testing_strategy = TestingStrategy.UNIT_TESTING
                
                preference.code_style.comment_level = CommentLevel.MODERATE
                preference.code_style.style_type = CodeStyleType.CONCISE
                
                preference.feature_requirements.error_handling = True
                preference.feature_requirements.logging = True
                preference.feature_requirements.file_handling = True
                
            elif template_type == "data_science":
                preference.project_type.domain = ProjectDomain.DATA_SCIENCE
                preference.project_type.preferred_languages = ["python", "r", "julia"]
                preference.project_type.preferred_frameworks = {
                    "python": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"],
                    "r": ["tidyverse", "caret", "ggplot2"],
                    "julia": ["DataFrames.jl", "Flux.jl"]
                }
                preference.project_type.architecture_patterns = ["Notebook-based", "Pipeline", "Module-based"]
                preference.project_type.testing_strategy = TestingStrategy.MINIMAL_TESTING
                
                preference.code_style.comment_level = CommentLevel.COMPREHENSIVE
                preference.code_style.style_type = CodeStyleType.DESCRIPTIVE
                
                preference.feature_requirements.data_validation = True
                preference.feature_requirements.logging = True
                preference.feature_requirements.file_handling = True
                preference.feature_requirements.analytics = True
                preference.feature_requirements.performance_optimization = True
                
            elif template_type == "api":
                preference.project_type.domain = ProjectDomain.API
                preference.project_type.preferred_languages = ["python", "javascript", "typescript", "go"]
                preference.project_type.preferred_frameworks = {
                    "python": ["fastapi", "flask", "django-rest-framework"],
                    "javascript": ["express", "koa", "hapi"],
                    "typescript": ["nest.js", "express", "fastify"],
                    "go": ["gin", "echo", "fiber"]
                }
                preference.project_type.architecture_patterns = ["REST API", "GraphQL", "Microservices"]
                preference.project_type.testing_strategy = TestingStrategy.INTEGRATION_TESTING
                preference.project_type.database_preference = "PostgreSQL or MongoDB"
                
                preference.code_style.comment_level = CommentLevel.MODERATE
                preference.code_style.style_type = CodeStyleType.STANDARD
                
                preference.feature_requirements.authentication = True
                preference.feature_requirements.authorization = True
                preference.feature_requirements.data_validation = True
                preference.feature_requirements.error_handling = True
                preference.feature_requirements.logging = True
                preference.feature_requirements.security_features = True
                preference.feature_requirements.monitoring = True
                preference.feature_requirements.caching = True
                
            elif template_type == "desktop_app":
                preference.project_type.domain = ProjectDomain.DESKTOP_APP
                preference.project_type.preferred_languages = ["python", "javascript", "c#", "java"]
                preference.project_type.preferred_frameworks = {
                    "python": ["pyqt", "tkinter", "wxpython"],
                    "javascript": ["electron", "nw.js"],
                    "c#": ["wpf", "winforms"],
                    "java": ["javafx", "swing"]
                }
                preference.project_type.architecture_patterns = ["MVP", "MVVM", "MVC"]
                preference.project_type.testing_strategy = TestingStrategy.UNIT_TESTING
                
                preference.code_style.comment_level = CommentLevel.MODERATE
                preference.code_style.style_type = CodeStyleType.OBJECT_ORIENTED
                
                preference.feature_requirements.error_handling = True
                preference.feature_requirements.logging = True
                preference.feature_requirements.file_handling = True
                preference.feature_requirements.performance_optimization = True
            
            # 保存偏好设置
            self.save_preference(preference)
            self.active_preference = preference
            
        except Exception as e:
            logger.error(f"从模板创建偏好设置失败: {e}")
            preference = None
            
        return preference 