# AIgo 开发环境快速搭建脚本
# 作用：初始化项目结构、创建必要目录并设置Docker环境

# 显示欢迎信息
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "            AIgo 开发环境快速搭建工具              " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# 检查当前目录是否为项目根目录
if (-not (Test-Path "requirements.txt" -PathType Leaf)) {
    Write-Host "错误: 当前目录不是AIgo项目根目录！" -ForegroundColor Red
    Write-Host "请在AIgo项目根目录运行此脚本。" -ForegroundColor Red
    exit 1
}

# 创建必要的目录
$directories = @(
    "data",
    "data/knowledge_bases",
    "data/user_data",
    "data/backups",
    "logs",
    "cache",
    "config/user"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory | Out-Null
        Write-Host "✅ 创建目录: $dir" -ForegroundColor Green
    } else {
        Write-Host "➡️ 目录已存在: $dir" -ForegroundColor Yellow
    }
}

# 创建Docker环境文件
$dockerComposeContent = @"
version: '3'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    restart: unless-stopped
    networks:
      - aigo-network

  aigo:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: aigo
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    ports:
      - "8080:8080"
    depends_on:
      - ollama
    environment:
      - OLLAMA_API_BASE=http://ollama:11434
    restart: unless-stopped
    networks:
      - aigo-network

networks:
  aigo-network:
    driver: bridge

volumes:
  ollama_data:
"@

$dockerfileContent = @"
FROM python:3.9-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt ./

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 创建必要的目录
RUN mkdir -p data/knowledge_bases logs cache config/user

# 暴露端口
EXPOSE 8080

# 启动应用
CMD ["python", "start_assistant.py"]
"@

$dockerIgnoreContent = @"
# Git
.git
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Project data
data/knowledge_bases/
data/repositories/
data/user_data/
data/backups/

# Logs
logs/
*.log

# Cache
cache/
.pytest_cache/

# Models
models/

# Test directories
tests/
test_kb/
temp_test_kb/
test_kb_demo/
"@

# 创建Docker配置文件
Set-Content -Path "docker-compose.yml" -Value $dockerComposeContent
Write-Host "✅ 创建文件: docker-compose.yml" -ForegroundColor Green

Set-Content -Path "Dockerfile" -Value $dockerfileContent
Write-Host "✅ 创建文件: Dockerfile" -ForegroundColor Green

Set-Content -Path ".dockerignore" -Value $dockerIgnoreContent
Write-Host "✅ 创建文件: .dockerignore" -ForegroundColor Green

# 创建虚拟环境（如果不存在）
if (-not (Test-Path "venv")) {
    Write-Host "正在创建Python虚拟环境..." -ForegroundColor Cyan
    try {
        python -m venv venv
        Write-Host "✅ 虚拟环境创建成功" -ForegroundColor Green
    } catch {
        Write-Host "❌ 创建虚拟环境失败: $_" -ForegroundColor Red
    }
} else {
    Write-Host "➡️ 虚拟环境已存在" -ForegroundColor Yellow
}

# 提示安装依赖
Write-Host ""
Write-Host "请运行以下命令安装依赖:" -ForegroundColor Cyan
Write-Host "    venv\Scripts\activate" -ForegroundColor White
Write-Host "    pip install -r requirements.txt" -ForegroundColor White

# 提示Docker使用方法
Write-Host ""
Write-Host "使用Docker运行AIgo:" -ForegroundColor Cyan
Write-Host "    docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "不使用Docker直接运行AIgo:" -ForegroundColor Cyan
Write-Host "    python start_assistant.py" -ForegroundColor White

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "            AIgo 开发环境设置完成!                  " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
