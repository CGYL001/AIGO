# 贡献指南

感谢您考虑为AIgo项目做出贡献！本文档提供了参与贡献的指南和最佳实践。

## 开发环境设置

1. **克隆仓库**

```bash
git clone https://github.com/yourusername/AIgo.git
cd AIgo
```

2. **设置开发环境**

```bash
# 运行开发环境设置脚本
python scripts/setup_dev.py

# 安装开发依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

3. **设置环境变量**

在Windows上:
```
.\set_env.bat
```

在Unix/Linux/Mac上:
```
source ./set_env.sh
```

## 代码风格

我们使用以下工具来保持代码质量和一致性：

- **Black**: 代码格式化
- **isort**: 导入排序
- **ruff**: 代码质量检查

在提交代码前，请运行：

```bash
# 格式化代码
black aigo tests examples
isort aigo tests examples

# 代码质量检查
ruff check aigo tests examples
```

## 项目结构

```
aigo/                  # 主包
  ├── adapters/        # 外部服务适配器
  ├── models/          # 模型适配器和管理
  │   ├── base.py      # 模型抽象接口
  │   ├── adapters.py  # 高级模型适配器
  │   └── providers/   # 各种模型提供商实现
  ├── modules/         # 核心功能模块
  ├── runtime/         # 运行时服务
  └── cli/             # 命令行接口
```

## 添加新功能

### 添加新的模型提供商

1. 在 `aigo/models/providers/` 目录下创建新的模型运行器文件，例如 `my_provider_runner.py`
2. 实现 `BaseModelRunner` 接口
3. 使用 `@register_model` 装饰器注册模型运行器
4. 在 `aigo/models/__init__.py` 中导入新的运行器

示例:

```python
from aigo.models.base import BaseModelRunner, ModelConfig, register_model

@register_model("my-provider")
class MyProviderRunner(BaseModelRunner):
    name = "my-provider"
    
    @classmethod
    def supports(cls, config: ModelConfig) -> bool:
        return config.provider.lower() == "my-provider"
        
    def load(self) -> None:
        # 实现加载逻辑
        pass
        
    def generate(self, prompt: str, **kwargs) -> str:
        # 实现生成逻辑
        pass
```

### 添加新的适配器类型

1. 在 `aigo/models/adapters.py` 中创建新的适配器类
2. 实现 `ModelAdapter` 接口
3. 在 `create_adapter` 工厂函数中添加新的适配器类型
4. 在 `aigo/__init__.py` 中导出新的适配器

## 测试

我们使用pytest进行测试。在提交代码前，请确保所有测试通过：

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行特定测试文件
pytest tests/unit/test_model_base.py
```

### 添加测试

1. 在 `tests/unit/` 或 `tests/integration/` 目录下创建测试文件
2. 使用pytest fixtures和mock对象进行测试
3. 确保测试覆盖新功能的主要场景和边缘情况

## 提交代码

1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

2. 提交更改
```bash
git add .
git commit -m "feat: 添加新功能"
```

我们使用[约定式提交](https://www.conventionalcommits.org/)格式：
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更改
- `style:` 不影响代码含义的更改（空格、格式化等）
- `refactor:` 既不修复bug也不添加功能的代码更改
- `test:` 添加或修正测试
- `chore:` 对构建过程或辅助工具的更改

3. 推送分支并创建Pull Request
```bash
git push origin feature/your-feature-name
```

## 文档

请为所有新功能添加适当的文档：

- 函数和类的docstring（使用Google风格）
- 必要时更新README.md
- 为复杂功能添加示例代码

## 许可证

通过提交代码，您同意您的贡献将在项目的许可证下提供。
