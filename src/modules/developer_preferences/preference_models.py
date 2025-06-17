"""
开发者偏好数据模型

定义开发者偏好的数据结构、验证规则和默认值
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from datetime import datetime

class CodeStyleType(Enum):
    """代码风格类型"""
    STANDARD = "standard"             # 标准风格，遵循语言规范
    CONCISE = "concise"               # 简洁风格，最小化代码行数
    DESCRIPTIVE = "descriptive"       # 描述性风格，注重命名和注释
    FUNCTIONAL = "functional"         # 函数式风格，强调不可变性和纯函数
    OBJECT_ORIENTED = "oop"           # 面向对象风格，强调封装和继承
    PROCEDURAL = "procedural"         # 过程式风格，以流程和步骤为主

class CommentLevel(Enum):
    """代码注释级别"""
    MINIMAL = "minimal"              # 最小注释，仅关键点
    MODERATE = "moderate"            # 适度注释，主要函数和复杂逻辑
    COMPREHENSIVE = "comprehensive"  # 全面注释，详细说明

class ProjectDomain(Enum):
    """项目领域"""
    WEB_FRONTEND = "web_frontend"    # Web前端
    WEB_BACKEND = "web_backend"      # Web后端
    DESKTOP_APP = "desktop_app"      # 桌面应用
    MOBILE_APP = "mobile_app"        # 移动应用
    DATA_SCIENCE = "data_science"    # 数据科学
    DEVOPS = "devops"                # DevOps
    EMBEDDED = "embedded"            # 嵌入式系统
    GAME_DEV = "game_dev"            # 游戏开发
    BLOCKCHAIN = "blockchain"        # 区块链
    AI_ML = "ai_ml"                  # 人工智能/机器学习
    IOT = "iot"                      # 物联网
    API = "api"                      # API服务
    CLI = "cli"                      # 命令行工具
    OTHER = "other"                  # 其他

class TestingStrategy(Enum):
    """测试策略"""
    TDD = "tdd"                      # 测试驱动开发
    BDD = "bdd"                      # 行为驱动开发
    UNIT_TESTING = "unit_testing"    # 单元测试
    INTEGRATION_TESTING = "integration_testing"  # 集成测试
    MINIMAL_TESTING = "minimal_testing"  # 最小测试
    NO_TESTING = "no_testing"        # 不包含测试

class FrameworkPreference(Enum):
    """框架偏好类型"""
    LIGHTWEIGHT = "lightweight"      # 轻量级框架
    FULL_FEATURED = "full_featured"  # 全功能框架
    MODERN = "modern"                # 现代框架
    STABLE = "stable"                # 稳定框架
    POPULAR = "popular"              # 流行框架
    NO_FRAMEWORK = "no_framework"    # 无框架

@dataclass
class CodeStyle:
    """代码风格偏好"""
    style_type: CodeStyleType = CodeStyleType.STANDARD
    comment_level: CommentLevel = CommentLevel.MODERATE
    line_length: int = 80
    use_tabs: bool = False
    tab_width: int = 4
    prefer_single_quotes: bool = False
    trailing_commas: bool = True
    bracket_spacing: bool = True
    arrow_parens: bool = True
    semicolons: bool = True
    always_use_explicit_types: bool = False
    custom_rules: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """将对象转换为字典"""
        return {
            "style_type": self.style_type.value,
            "comment_level": self.comment_level.value,
            "line_length": self.line_length,
            "use_tabs": self.use_tabs,
            "tab_width": self.tab_width,
            "prefer_single_quotes": self.prefer_single_quotes,
            "trailing_commas": self.trailing_commas,
            "bracket_spacing": self.bracket_spacing,
            "arrow_parens": self.arrow_parens,
            "semicolons": self.semicolons,
            "always_use_explicit_types": self.always_use_explicit_types,
            "custom_rules": self.custom_rules
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CodeStyle':
        """从字典创建对象"""
        return cls(
            style_type=CodeStyleType(data.get("style_type", CodeStyleType.STANDARD.value)),
            comment_level=CommentLevel(data.get("comment_level", CommentLevel.MODERATE.value)),
            line_length=data.get("line_length", 80),
            use_tabs=data.get("use_tabs", False),
            tab_width=data.get("tab_width", 4),
            prefer_single_quotes=data.get("prefer_single_quotes", False),
            trailing_commas=data.get("trailing_commas", True),
            bracket_spacing=data.get("bracket_spacing", True),
            arrow_parens=data.get("arrow_parens", True),
            semicolons=data.get("semicolons", True),
            always_use_explicit_types=data.get("always_use_explicit_types", False),
            custom_rules=data.get("custom_rules", {})
        )

@dataclass
class ProjectType:
    """项目类型偏好"""
    domain: ProjectDomain = ProjectDomain.WEB_BACKEND
    testing_strategy: TestingStrategy = TestingStrategy.UNIT_TESTING
    framework_preference: FrameworkPreference = FrameworkPreference.MODERN
    preferred_languages: List[str] = field(default_factory=lambda: ["python", "javascript"])
    preferred_frameworks: Dict[str, List[str]] = field(default_factory=lambda: {
        "python": ["flask", "django"],
        "javascript": ["react", "express"]
    })
    architecture_patterns: List[str] = field(default_factory=lambda: ["MVC", "REST API"])
    database_preference: str = "PostgreSQL"
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """将对象转换为字典"""
        return {
            "domain": self.domain.value,
            "testing_strategy": self.testing_strategy.value,
            "framework_preference": self.framework_preference.value,
            "preferred_languages": self.preferred_languages,
            "preferred_frameworks": self.preferred_frameworks,
            "architecture_patterns": self.architecture_patterns,
            "database_preference": self.database_preference,
            "custom_settings": self.custom_settings
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ProjectType':
        """从字典创建对象"""
        return cls(
            domain=ProjectDomain(data.get("domain", ProjectDomain.WEB_BACKEND.value)),
            testing_strategy=TestingStrategy(data.get("testing_strategy", TestingStrategy.UNIT_TESTING.value)),
            framework_preference=FrameworkPreference(data.get("framework_preference", FrameworkPreference.MODERN.value)),
            preferred_languages=data.get("preferred_languages", ["python", "javascript"]),
            preferred_frameworks=data.get("preferred_frameworks", {
                "python": ["flask", "django"],
                "javascript": ["react", "express"]
            }),
            architecture_patterns=data.get("architecture_patterns", ["MVC", "REST API"]),
            database_preference=data.get("database_preference", "PostgreSQL"),
            custom_settings=data.get("custom_settings", {})
        )

@dataclass
class FeatureRequirement:
    """功能需求偏好"""
    authentication: bool = False
    authorization: bool = False
    data_validation: bool = True
    error_handling: bool = True
    logging: bool = True
    caching: bool = False
    internationalization: bool = False
    performance_optimization: bool = False
    security_features: bool = True
    monitoring: bool = False
    analytics: bool = False
    search_functionality: bool = False
    file_handling: bool = False
    email_integration: bool = False
    payment_processing: bool = False
    social_integration: bool = False
    custom_features: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """将对象转换为字典"""
        return {
            "authentication": self.authentication,
            "authorization": self.authorization,
            "data_validation": self.data_validation,
            "error_handling": self.error_handling,
            "logging": self.logging,
            "caching": self.caching,
            "internationalization": self.internationalization,
            "performance_optimization": self.performance_optimization,
            "security_features": self.security_features,
            "monitoring": self.monitoring,
            "analytics": self.analytics,
            "search_functionality": self.search_functionality,
            "file_handling": self.file_handling,
            "email_integration": self.email_integration,
            "payment_processing": self.payment_processing,
            "social_integration": self.social_integration,
            "custom_features": self.custom_features
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'FeatureRequirement':
        """从字典创建对象"""
        return cls(
            authentication=data.get("authentication", False),
            authorization=data.get("authorization", False),
            data_validation=data.get("data_validation", True),
            error_handling=data.get("error_handling", True),
            logging=data.get("logging", True),
            caching=data.get("caching", False),
            internationalization=data.get("internationalization", False),
            performance_optimization=data.get("performance_optimization", False),
            security_features=data.get("security_features", True),
            monitoring=data.get("monitoring", False),
            analytics=data.get("analytics", False),
            search_functionality=data.get("search_functionality", False),
            file_handling=data.get("file_handling", False),
            email_integration=data.get("email_integration", False),
            payment_processing=data.get("payment_processing", False),
            social_integration=data.get("social_integration", False),
            custom_features=data.get("custom_features", {})
        )

@dataclass
class DeveloperPreferences:
    """开发者完整偏好设置"""
    id: str = ""  # 用户ID或项目ID
    name: str = "默认偏好"
    description: str = "默认开发者偏好配置"
    code_style: CodeStyle = field(default_factory=CodeStyle)
    project_type: ProjectType = field(default_factory=ProjectType)
    feature_requirements: FeatureRequirement = field(default_factory=FeatureRequirement)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True
    custom_preferences: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """将对象转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "code_style": self.code_style.to_dict(),
            "project_type": self.project_type.to_dict(),
            "feature_requirements": self.feature_requirements.to_dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
            "custom_preferences": self.custom_preferences
        }

    def to_json(self) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict) -> 'DeveloperPreferences':
        """从字典创建对象"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", "默认偏好"),
            description=data.get("description", "默认开发者偏好配置"),
            code_style=CodeStyle.from_dict(data.get("code_style", {})),
            project_type=ProjectType.from_dict(data.get("project_type", {})),
            feature_requirements=FeatureRequirement.from_dict(data.get("feature_requirements", {})),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            is_active=data.get("is_active", True),
            custom_preferences=data.get("custom_preferences", {})
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'DeveloperPreferences':
        """从JSON字符串创建对象"""
        return cls.from_dict(json.loads(json_str))

    def update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.now().isoformat()

    def generate_context_prompt(self) -> str:
        """生成上下文提示，用于指导AI代码生成"""
        code_style = self.code_style
        project = self.project_type
        features = self.feature_requirements
        
        # 构建风格描述
        style_desc = f"编码风格: {code_style.style_type.value}, "
        style_desc += f"注释级别: {code_style.comment_level.value}, "
        style_desc += f"{'使用Tab' if code_style.use_tabs else '使用空格'}, "
        style_desc += f"行长度限制: {code_style.line_length}字符"
        
        # 构建项目描述
        project_desc = f"项目类型: {project.domain.value}, "
        project_desc += f"测试策略: {project.testing_strategy.value}, "
        project_desc += f"偏好语言: {', '.join(project.preferred_languages)}, "
        project_desc += f"架构模式: {', '.join(project.architecture_patterns)}"
        
        # 构建功能描述
        feature_list = []
        for key, value in features.to_dict().items():
            if isinstance(value, bool) and value and key != "custom_features":
                feature_list.append(key.replace('_', ' '))
        
        if features.custom_features:
            for feature_name in features.custom_features.keys():
                feature_list.append(feature_name)
                
        feature_desc = "需要的功能: " + ", ".join(feature_list) if feature_list else "无特定功能需求"
        
        # 组合提示
        prompt = f"""
作为AI编码助手，请按照以下开发者偏好生成代码:

{style_desc}

{project_desc}

{feature_desc}

请确保生成的代码符合上述风格和需求。
"""
        return prompt.strip() 