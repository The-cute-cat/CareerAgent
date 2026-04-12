# 构建阶段
FROM python:3.12-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==2.3.1

COPY pyproject.toml poetry.lock poetry.toml ./
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi --only main --no-root

# 运行阶段
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# ✅ 关键：设置 PYTHONPATH 包含 src 目录
ENV PYTHONPATH="/app/src:/app"

COPY main.py config.py config.yaml ./
COPY src ./src

RUN mkdir -p /app/data /app/logs

EXPOSE 9000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
