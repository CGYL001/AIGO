#!/usr/bin/env python3
"""
模型重构功能测试脚本
"""

import os
import sys
import json
from pathlib import Path

# 打印当前工作目录和Python路径
print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path)

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    # 创建必要的目录结构
    print("\n检查目录结构...")
    Path("AIGO/models/restructuring").mkdir(parents=True, exist_ok=True)
    print("目录结构已创建")
    
    # 检查文件是否存在
    print("\n检查关键文件...")
    required_files = [
        "AIGO/utils/feature_discovery.py",
        "AIGO/models/restructuring/__init__.py",
        "AIGO/models/restructuring/core.py",
        "AIGO/models/restructuring/analyzers.py",
        "AIGO/models/restructuring/optimizers.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path} 存在")
        else:
            print(f"  ✗ {file_path} 不存在")
    
    print("\n正在手动创建模型结构...")
    # 创建模拟模型结构
    model_structure = {
        "metadata": {
            "name": "test-model",
            "version": "1.0"
        },
        "components": {
            "attention": {
                "type": "self_attention",
                "num_heads": 32,
                "head_dim": 64
            },
            "feed_forward": {
                "type": "mlp",
                "hidden_dim": 4096
            }
        },
        "layers": [
            {"attention": {}, "feed_forward": {}} for _ in range(32)
        ]
    }
    
    print("\n分析模型性能...")
    # 直接导入并使用分析器
    from AIGO.models.restructuring.analyzers import PerformanceAnalyzer
    analyzer = PerformanceAnalyzer(model_structure)
    analysis = analyzer.analyze()
    
    print(f"\n分析完成！发现 {len(analysis['issues'])} 个潜在的性能问题")
    
    # 打印优化潜力
    potential = analysis['optimization_potential']
    print(f"\n优化潜力:")
    print(f"  总体评估: {potential['overall']}")
    print(f"  速度提升: {potential['speedup']}")
    print(f"  内存减少: {potential['memory_reduction']}")
    
    # 打印主要瓶颈
    print(f"\n主要瓶颈:")
    for i, bottleneck in enumerate(analysis['bottlenecks'], 1):
        print(f"  {i}. {bottleneck['component']}: {bottleneck['description']}")

except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已创建必要的模块并添加到Python路径中")
except Exception as e:
    import traceback
    print(f"运行时错误: {e}")
    traceback.print_exc()

print("\n测试完成!") 