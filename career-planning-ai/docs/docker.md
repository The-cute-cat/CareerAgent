# Docker 部署指南

本文档介绍如何使用 Docker 部署 Career Planning AI 服务。

## 目录

- [快速开始](#快速开始)
- [镜像构建](#镜像构建)
- [容器运行](#容器运行)
- [数据持久化](#数据持久化)
- [配置管理](#配置管理)
- [日志查看](#日志查看)
- [镜像分享](#镜像分享)
- [常见问题](#常见问题)

---

## 快速开始

### 一键构建并运行

```bash
# 构建镜像
docker build -t career-planning-ai .

# 运行容器
docker run -d \
  --name career-ai \
  -p 9000:9000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  career-planning-ai

# 查看日志
docker logs -f career-ai
```

> **说明**：首次运行时，容器会自动安装 Python 依赖（约 2-3GB），可能需要 5-10 分钟。后续运行秒级启动。

---

## 镜像构建

### 标准构建

```bash
docker build -t career-planning-ai .
```

### 带标签的构建

```bash
docker build -t career-planning-ai:latest .
docker build -t career-planning-ai:v1.0.0 .
```

### 构建参数说明

| 参数 | 说明 |
|------|------|
| `-t career-planning-ai` | 镜像名称 |
| `.` | 构建上下文（当前目录） |

---

## 容器运行

### 基本运行

```bash
docker run -d \
  --name career-ai \
  -p 9000:9000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  career-planning-ai
```

### Windows 命令提示符 (CMD)

```bash
docker run -d --name career-ai -p 9000:9000 -v %cd%\.env:/app/.env -v %cd%\data:/app/data -v %cd%\logs:/app/logs career-planning-ai
```

### Windows PowerShell

```bash
docker run -d --name career-ai -p 9000:9000 -v ${PWD}\.env:/app/.env -v ${PWD}\data:/app/data -v ${PWD}\logs:/app/logs career-planning-ai
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `-d` | 后台运行 |
| `--name career-ai` | 容器名称 |
| `-p 9000:9000` | 端口映射（宿主机:容器） |
| `-v .../data:/app/data` | 挂载数据目录 |
| `-v .../logs:/app/logs` | 挂载日志目录 |
| `-v .../.env:/app/.env` | 挂载环境变量文件 |

---

## 数据持久化

### 目录说明

| 宿主机目录 | 容器目录 | 说明 |
|-----------|----------|------|
| `./data` | `/app/data` | 向量库、模型文件等数据 |
| `./logs` | `/app/logs` | 应用日志 |
| `./.env` | `/app/.env` | 环境变量（API密钥等） |

### 注意事项

- **data 目录**：包含向量数据库、模型文件等，首次运行后请保留
- **logs 目录**：包含运行日志，便于排查问题
- **data 目录不打包**：构建镜像时不包含 data 目录，需要运行时挂载

---

## 配置管理

### 环境变量文件 (.env)

创建 `.env` 文件，包含敏感配置：

```env
# 数据库配置
DATABASE__USER=your_db_user
DATABASE__PASSWORD=your_db_password

# LLM API 配置
LLM__API_KEY=your_api_key
LLM__BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM__MODEL_NAME=qwen-max

# Redis 配置
REDIS__HOST=your_redis_host
REDIS__PORT=6379
REDIS__PASSWORD=your_redis_password

# Neo4j 配置
NEO4J__PASSWORD=your_neo4j_password

# Milvus 配置
MILVUS__CLOUD__URL=your_milvus_url
MILVUS__CLOUD__TOKEN=your_milvus_token
```

### 修改配置后重启

```bash
# 编辑 .env 文件后
docker restart career-ai
```

### 使用环境变量覆盖

也可以不使用 .env 文件，直接通过 `-e` 传递环境变量：

```bash
docker run -d \
  --name career-ai \
  -p 9000:9000 \
  -e LLM__API_KEY=your_api_key \
  -e DATABASE__PASSWORD=your_password \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  career-planning-ai
```

---

## 日志查看

### 实时查看日志

```bash
docker logs -f career-ai
```

### 查看最近 100 行日志

```bash
docker logs --tail 100 career-ai
```

### 查看完整日志

```bash
docker logs career-ai
```

### 导出日志到文件

```bash
docker logs career-ai > app.log 2>&1
```

---

## 镜像分享

### 导出镜像为 tar 文件

```bash
# 导出镜像
docker save -o career-planning-ai.tar career-planning-ai

# 压缩镜像（可选）
gzip career-planning-ai.tar
```

### 导入镜像

```bash
# 解压（如果压缩过）
gunzip career-planning-ai.tar.gz

# 导入镜像
docker load -i career-planning-ai.tar
```

### 推送到镜像仓库

```bash
# 登录镜像仓库
docker login your-registry.com

# 打标签
docker tag career-planning-ai your-registry.com/career-planning-ai:latest

# 推送
docker push your-registry.com/career-planning-ai:latest
```

---

## 容器管理

### 启动容器

```bash
docker start career-ai
```

### 停止容器

```bash
docker stop career-ai
```

### 重启容器

```bash
docker restart career-ai
```

### 进入容器（调试）

```bash
docker exec -it career-ai /bin/bash
```

### 删除容器

```bash
# 先停止
docker stop career-ai

# 再删除
docker rm career-ai
```

### 一键删除重建

```bash
docker rm -f career-ai && docker run -d \
  --name career-ai \
  -p 9000:9000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  career-planning-ai
```

---

## 常见问题

### Q1: 首次运行很慢？

首次运行时需要下载和安装 Python 依赖（约 2-3GB），请耐心等待。后续运行会跳过安装步骤。

### Q2: 编译失败 (manimpango / pycairo)？

确保镜像构建时正确安装了编译依赖。如果遇到此类错误，请重新构建镜像。

### Q3: 容器内找不到模块？

已配置 `PYTHONPATH=/app/src:/app`，如果仍有问题，检查是否正确挂载了 `.env` 文件。

### Q4: 如何确认服务正常运行？

容器启动后，访问服务根目录：

```bash
curl http://localhost:9000/
```

预期响应：
```json
{
  "code": 200,
  "state": true,
  "msg": null,
  "data": "Emptiness is also an attitude!(=^･ω･^=)"
}
```

如果返回上述 JSON，说明服务已正常启动。

### Q5: 如何在不安装依赖的情况下测试？

本地开发可以使用 Poetry：

```bash
poetry install
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

### Q6: SSL / 网络错误？

已配置阿里云 pip 镜像源。如仍有问题，检查宿主机网络连接。

### Q7: 端口被占用？

```bash
# Windows 查看端口占用
netstat -ano | findstr :9000

# 杀掉进程（替换 PID）
taskkill /PID <PID> /F
```

---

## 生产环境建议

1. **使用 docker-compose**：方便管理多容器部署
2. **配置健康检查**：添加 healthcheck 配置
3. **限制资源**：添加 `--memory` 参数限制内存使用
4. **配置日志轮转**：避免日志文件过大
5. **使用私有镜像仓库**：便于版本管理和回滚
