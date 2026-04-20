#!/bin/bash
set -e

cd /app || exit 1

# 配置阿里云pip源（避免SSL下载错误）
poetry config virtualenvs.in-project true
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 安装项目依赖（每次运行都执行）
echo "Installing project dependencies with poetry..."
poetry lock && poetry install --no-interaction --no-ansi --only main && poetry update --no-interaction --no-ansi

# 启动应用
echo "Starting application..."
exec /app/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 9000
