#!/bin/bash
echo "开始执行Git操作..."

# 切换到正确的目录
cd /d/AIgo

# 清理模型元数据文件
echo "清理模型元数据文件..."
if [ -d "models/registry/models" ]; then
    rm -rf models/registry/models
    mkdir -p models/registry/models/my_models
fi

# 清理下载的模型文件
echo "清理下载的模型文件..."
if [ -d "models/downloads" ]; then
    rm -rf models/downloads
    mkdir -p models/downloads
fi

# 清理缓存文件
echo "清理缓存文件..."
if [ -d "cache" ]; then
    rm -rf cache
    mkdir -p cache
fi
if [ -d "temp_checkpoints" ]; then
    rm -rf temp_checkpoints
    mkdir -p temp_checkpoints
fi
if [ -d "temp_training_memory" ]; then
    rm -rf temp_training_memory
    mkdir -p temp_training_memory
fi

# 执行Git操作
echo "执行Git操作..."
git add .
git commit -m "修复跨平台兼容性问题和清理个性化模型元数据"
git push origin main

echo "操作完成！"
read -p "按任意键继续..." 