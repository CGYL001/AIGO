"""仓库集成平台适配器包，提供不同代码托管平台的适配接口"""

from .base_adapter import BaseRepoAdapter
from .github_adapter import GitHubAdapter
from .gitlab_adapter import GitLabAdapter
from .gitee_adapter import GiteeAdapter
