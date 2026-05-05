# 部署指南

## 环境要求

### 基础环境
- **Python**: 3.12.x (>=3.12, <3.13)
- **Poetry**: >= 2.0.0
- **Docker**: >= 20.10（可选）
- **Node.js**: >= 20.x（推荐 ^20.19.0 或 >=22.12.0，如需前端）

### 外部服务
- **MySQL**: 5.7+ / 8.0+
- **Redis**: 6.0+
- **Neo4j**: 4.x / 5.x (含 APOC 插件)
- **RabbitMQ**: 3.x (含管理界面)
- **Milvus**: 2.4+ (Standalone 模式，向量检索)
- **ChromaDB**: 本地内嵌运行

---

## 本地开发部署

### AI 服务 (career-planning-ai)

#### 1. 克隆项目

```bash
git clone <repository_url>
cd CareerAgent/career-planning-ai
```

#### 2. 拉取 Git LFS 大文件数据（**必须！**）

> **本项目使用 Git LFS 管理大体积初始化数据文件。**
> `git clone` 后这些文件仅为指针（几 KB），**必须手动拉取实际内容**，否则种子数据导入会失败。

```bash
# 在项目根目录 CareerAgent/ 下执行
git lfs install   # 首次使用需初始化 LFS（如已配置可跳过）
git lfs pull       # 拉取所有 LFS 追踪的实际内容

# 包含的数据文件：
#   - career-planning-ai/data/init/chroma/*_seed.json    (~170MB, ChromaDB 种子)
#   - career-planning-backend/docs/init/mysql/*.sql        (MySQL 初始化)
#   - career-planning-ai/data/init/milvus/*_seed.json      (Milvus 种子)

# 验证：确认 JSON 文件大小正常（应数十~百 MB，而非几 KB）
ls -lh data/init/chroma/*_seed.json
```

#### 3. 安装依赖

```bash
# 安装 Poetry（如未安装）
pip install poetry

# 配置国内镜像源（可选）
poetry config repositories.tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/

# 安装依赖
poetry install
```

#### 4. 配置环境

编辑 `config.yaml` 和 `.env` 文件：

```yaml
# config.yaml 必须配置项
database:
  host: your_mysql_host
  port: 3306
  database: career_backend
  user: your_username
  password: your_password

communication:
  token:
    secret: your_secret_key  # 与Java端保持一致

redis:
  host: your_redis_host
  port: 6379
  password: your_redis_password

neo4j:
  url: neo4j://your_neo4j_host:7687
  username: neo4j
  password: your_neo4j_password
```

`.env` 中填入敏感信息（API Keys 等）：
```env
LLM__API_KEY=your_dashscope_api_key
CONVERSATION__AGENT__API_KEY=your_deepseek_api_key
COMMUNICATION__TOKEN__SECRET=your_token_secret
```

#### 5. 启动服务

```bash
# 开发模式（带热重载）
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --reload

# 生产模式
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
```

#### 6. 验证服务

访问 http://localhost:9000/

预期响应：
```json
{
  "code": 200,
  "state": true,
  "msg": null,
  "data": "Emptiness is also an attitude!(=^･ω･^=)"
}
```

---

### 后端服务 (career-planning-backend)

```bash
cd career-planning-backend

# 1. 配置数据库连接
# 编辑 src/main/resources/application-dev.yaml

# 2. 使用 Maven 启动（需 JDK 21+）
mvn spring-boot:run -Dspring-boot.run.profiles=dev
# 服务运行在 http://localhost:8080
```

**环境要求**: JDK 21+, Maven 3.8+, MySQL 8.0+, Redis 6.0+, RabbitMQ 3.x

---

### 前端应用 (career-planning-frontend)

```bash
cd career-planning-frontend

# 安装依赖 (需要 Node.js ^20.19.0 或 >=22.12.0)
npm install

# 启动开发服务器
npm run dev
# 应用运行在 http://localhost:8081，API 代理到 localhost:8080
```

---

## Docker 部署

### 方式 A：Docker Compose 一键部署（推荐，完整项目）

项目根目录提供了完整的 `docker-compose.yml`，一键启动全部 **9 个服务**（5 个基础设施 + 3 个应用）：

**服务清单：**

| 服务 | 端口 | 说明 |
|------|------|------|
| mysql | 3306 | 关系数据库 |
| redis | 6379 | 缓存 (密码保护, 256MB) |
| neo4j | 7474 / 7687 | 知识图谱 (含 APOC) |
| rabbitmq | 5672 / 15672 | 消息队列 (含管理界面) |
| milvus | 19530 / 9091 | 向量数据库 (Standalone) |
| ai-service | 9000 (内部) | AI 服务 (Python/FastAPI) |
| backend | 8080 | 业务后端 (Spring Boot) |
| frontend | 8081→80 | 前端应用 (Vue/Nginx) |

**部署步骤：**

```bash
# 1. 进入项目根目录
cd CareerAgent

# 2. 拉取 Git LFS 大文件数据（必须！约 170MB）
git lfs install && git lfs pull

# 3. 配置环境变量（根目录 .env.example 已包含后端和 AI 服务全部配置）
cp .env.example .env
# 编辑 .env，填入实际密码、API Keys 等敏感信息

# 4. 一键构建并启动（首次约 5~15 分钟，取决于网速）
docker compose up -d --build

# 5. 查看服务状态
docker compose ps

# 6. 访问服务
#   前端:         http://localhost:8081
#   后端 API:     http://localhost:8080
#   RabbitMQ管理: http://localhost:15672
#   Neo4j浏览器:  http://localhost:7474
#   Milvus管理:   http://localhost:9091

# 7. 停止服务
docker compose down
```

> 详细说明请参考根目录 [README.md](../README.md) 的「Docker Compose 编排详解」章节。

---

### 方式 B：仅部署 AI 服务（独立部署）

```bash
cd career-planning-ai

# 构建镜像
docker build -t career-planning-ai:latest .

# 运行容器
docker run -d \
  --name career-ai \
  -p 9000:9000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  career-planning-ai:latest
```

> 完整的 Docker 部署指南请参考 [career-planning-ai/docs/docker.md](../career-planning-ai/docs/docker.md)。

---

## 生产环境部署

### 1. 系统优化

```bash
# 增加文件描述符限制
ulimit -n 65535

# 优化内核参数
sysctl -w net.core.somaxconn=65535
sysctl -w net.ipv4.tcp_max_syn_backlog=65535
```

### 2. Nginx 反向代理

生产环境推荐使用 Nginx 作为统一入口，反向代理三层服务：

```nginx
# ============ 后端 API ============
upstream career_backend {
    server 127.0.0.1:8080;   # Spring Boot
    keepalive 32;
}

# ============ AI 服务 (仅内网访问) ============
upstream career_ai {
    server 127.0.0.1:9000;   # FastAPI
    keepalive 16;
}

# ============ 前端 + API 统一入口 ============
server {
    listen 80;
    server_name career.example.com;

    # 前端静态文件 (SPA)
    root /opt/career-agent/frontend/dist;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理到后端
    location /api/ {
        proxy_pass http://career_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # SSE 流式支持（AI 对话、知识导师等）
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        proxy_set_header Accept-Encoding "";   # 禁用 gzip 以支持 SSE

        # 文件上传大小时限制
        client_max_body_size 50M;
    }
}
```

### 3. Supervisor 进程管理（三层服务）

```ini
# ============ AI 服务 (FastAPI) ============
[program:career-ai]
command=/opt/career-agent/ai/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
directory=/opt/career-agent/career-planning-ai
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/career/ai-access.log
stderr_logfile=/var/log/career/ai-error.log
environment=PYTHONPATH="/opt/career-agent/career-planning-ai/src:/opt/career-agent/career-planning-ai"

# ============ 后端服务 (Spring Boot) ============
[program:career-backend]
command=java -Xmx512m -jar /opt/career-agent/career-planning-backend/target/*.jar --spring.profiles.active=prod
directory=/opt/career-agent/career-planning-backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/career/backend-access.log
stderr_logfile=/var/log/career/backend-error.log
```

### 4. Systemd 服务（三层服务）

**AI 服务：**
```ini
[Unit]
Description=Career AI Service (FastAPI)
After=network.target mysql.service redis.service neo4j.service milvus.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/career-agent/career-planning-ai
Environment="PYTHONPATH=/opt/career-agent/career-planning-ai/src:/opt/career-agent/career-planning-ai"
ExecStart=/opt/career-agent/ai/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**后端服务：**
```ini
[Unit]
Description=Career Backend Service (Spring Boot)
After=network.target mysql.service redis.service rabbitmq.service career-ai.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/career-agent/career-planning-backend
ExecStart=/usr/bin/java -Xmx512m -jar /opt/career-agent/career-planning-backend/target/career-planning-backend.jar --spring.profiles.active=prod
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 常见问题

### 1. 端口被占用

```bash
# Windows
netstat -ano | findstr :9000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :9000
kill -9 <PID>
```

### 2. Windows 保留端口问题

```bash
# 查看保留端口
netsh interface ipv4 show excludedportrange protocol=tcp

# 重启 NAT 服务（管理员权限）
net stop winnat
net start winnat
```

### 3. Poetry 环境问题

```bash
# 清除缓存
poetry cache clear pypi --all

# 重建虚拟环境
poetry env remove <env-name>
poetry install
```

### 4. 依赖冲突

```bash
# 更新 lock 文件
poetry lock
poetry install
```

### 5. Neo4j 连接失败

- 检查防火墙设置
- 确认 Neo4j 服务状态
- 验证用户名密码

### 6. Redis 连接超时

- 检查 Redis 服务状态
- 确认网络连通性
- 调整 `connect_timeout` 配置

### 7. Milvus 启动缓慢

Milvus 首次启动较慢（约 30~60 秒），属于正常现象。

---

## 监控与日志

### 日志位置

| 服务 | 日志位置 |
|------|---------|
| AI 服务 | `career-planning-ai/logs/` 或 Docker 容器日志 |
| 后端 | Spring Boot 控制台输出或日志文件 |
| 前端 | Nginx 访问/错误日志 |

### 健康检查

```bash
# AI 服务基础检查
curl http://localhost:9000/

# 后端健康检查
curl http://localhost:8080/actuator/health

# 图路径服务检查
curl http://localhost:9000/graph_path/health
```

### 性能监控

建议使用：
- Prometheus + Grafana（指标监控）
- ELK Stack（日志聚合）
- APM 工具（如 Sentry）（性能追踪）

---

## 扩展部署

### Kubernetes 部署

参考 K8s 部署配置：
- Deployment
- Service
- ConfigMap
- Secret
- Ingress

### 高可用部署

- 多实例负载均衡
- Redis 集群/Sentinel
- MySQL 主从复制
- Neo4j Cluster/Causal Clustering
- Milvus 分布式集群
