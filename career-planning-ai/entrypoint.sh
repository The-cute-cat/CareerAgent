#!/bin/bash
set -e

cd /app || exit 1

# 配置阿里云pip源（避免SSL下载错误）
poetry config virtualenvs.in-project true
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 安装项目依赖（幂等操作：仅在 .venv 不存在或 pyproject.toml 更新时执行）
echo "Installing project dependencies with poetry..."
if [ -f /app/.venv/pyvenv.cfg ] && [ /app/.venv/pyvenv.cfg -nt /app/pyproject.toml ]; then
    echo "✅ Virtual environment already exists and is up-to-date, skipping install"
else
    echo "📦 Installing dependencies for the first time or after pyproject.toml update..."
    poetry lock --no-update 2>/dev/null || true
    poetry install --no-interaction --no-ansi --only main
fi


# ==================== ChromaDB 种子数据初始化（幂等）====================
CHROMA_INIT_SCRIPT="/app/data/init/chroma/init_chroma_seed.py"
if [ -f "$CHROMA_INIT_SCRIPT" ]; then
    echo "Initializing ChromaDB seed data..."
    /app/.venv/bin/python "$CHROMA_INIT_SCRIPT" || echo "⚠️  ChromaDB seed import failed or skipped (non-fatal)"
else
    echo "ℹ️  No Chroma init script found, skipping seed import"
fi

# ==================== Milvus 种子数据初始化（幂等）====================
INIT_MILVUS_SCRIPT="/app/data/init/milvus/init_milvus_seed.py"
if [ -f "$INIT_MILVUS_SCRIPT" ]; then
    echo "Checking Milvus seed data..."
    /app/.venv/bin/python "$INIT_MILVUS_SCRIPT" || echo "⚠️  Milvus seed import failed or skipped (non-fatal)"
else
    echo "ℹ️  No Milvus init script found, skipping seed import"
fi

# 启动应用
echo "Starting application..."
exec /app/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 9000
