# 运行阶段：精简镜像，依赖通过启动脚本动态安装
FROM python:3.12-slim

WORKDIR /app

# 安装运行时和编译所需的系统依赖
RUN sed -i 's|https://deb.debian.org|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/*.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ \
    libgl1 libglib2.0-0 libgomp1 \
    libcairo2-dev libpango1.0-dev pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry（官方方式）
RUN curl -sSL https://install.python-poetry.org | python3 - --version 2.3.1 && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# 复制启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 复制核心文件（不包含data目录，运行时挂载）
COPY main.py config.py config.yaml pyproject.toml poetry.toml ./
COPY src ./src

# 创建必要目录结构
RUN mkdir -p /app/data /app/logs

# 设置 PYTHONPATH，让 Python 能找到 src 目录下的模块
ENV PYTHONPATH="/app/src:/app"

# 暴露端口
EXPOSE 9000

# 使用启动脚本动态安装依赖
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
