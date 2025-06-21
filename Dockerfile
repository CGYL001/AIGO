# 第一阶段: 基础构建镜像
FROM python:3.10-slim AS builder

# 设置工作目录
WORKDIR /build

# 设置环境变量以优化Python运行
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONHASHSEED=random \
    PIP_DEFAULT_TIMEOUT=100

# 安装系统依赖和构建工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .

# 安装依赖并创建虚拟环境
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 安装项目
RUN /venv/bin/pip install --no-cache-dir -e .

# 第二阶段: 运行时镜像
FROM python:3.10-slim AS runtime

# 设置非root用户
RUN groupadd -r aigo && useradd -r -g aigo -m -d /home/aigo aigo && \
    mkdir -p /app /app/data /app/logs /app/config/user && \
    chown -R aigo:aigo /app

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    PYTHONPATH=/app

# 复制虚拟环境
COPY --from=builder /venv /venv

# 复制应用代码
COPY --from=builder --chown=aigo:aigo /build /app

# 安装仅运行时需要的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && chmod -R 755 /app/run.py

# 切换到非root用户
USER aigo

# 暴露API端口
EXPOSE 8000
EXPOSE 5000

# 设置存储卷
VOLUME ["/app/data", "/app/logs", "/app/config/user"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# 设置启动命令
ENTRYPOINT ["python", "run.py"]
CMD ["--fastapi-only", "--host", "0.0.0.0", "--port", "8000"] 