@echo off
echo 开始执行Git操作...

:: 切换到正确的目录
cd /d D:\AIgo

:: 清理模型元数据文件
echo 清理模型元数据文件...
if exist models\registry\models (
    rmdir /s /q models\registry\models
    mkdir models\registry\models\my_models
)

:: 清理下载的模型文件
echo 清理下载的模型文件...
if exist models\downloads (
    rmdir /s /q models\downloads
    mkdir models\downloads
)

:: 清理缓存文件
echo 清理缓存文件...
if exist cache (
    rmdir /s /q cache
    mkdir cache
)
if exist temp_checkpoints (
    rmdir /s /q temp_checkpoints
    mkdir temp_checkpoints
)
if exist temp_training_memory (
    rmdir /s /q temp_training_memory
    mkdir temp_training_memory
)

:: 执行Git操作
echo 执行Git操作...
git add .
git commit -m "修复跨平台兼容性问题和清理个性化模型元数据"
git push origin main

echo 操作完成！
pause 