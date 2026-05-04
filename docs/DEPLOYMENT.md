# 部署指南

## 环境要求

### 基础环境
- **Python**: 3.12.x
- **Poetry**: >= 2.0.0
- **Docker**: >= 20.10（可选）
- **Node.js**: >= 18.x（如需前端）

### 外部服务
- **MySQL**: 5.7+ / 8.0+
- **Redis**: 6.0+
- **Neo4j**: 4.x / 5.x
- **Milvus**: 2.x（可选）
- **ChromaDB**: 本地运行

---

## 本地开发部署

### 1. 克隆项目

```bash
git clone <repository_url>
cd CareerAgent/career-planning-ai
```

### 1.5. 拉取 Git LFS 大文件数据（**必须！**）

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

### 2. 安装依赖

```bash
# 安装 Poetry（如未安装）
pip install poetry

# 配置国内镜像源（可选）
poetry config repositories.tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/

# 安装依赖
poetry install
```

### 3. 配置环境

编辑 `config.yaml` 文件：

```yaml
# 必须配置项
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

### 4. 启动服务

```bash
# 开发模式（带热重载）
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --reload

# 生产模式
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
```

### 5. 验证服务

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

## Docker 部署

### 1. 构建镜像

```bash
cd career-planning-ai
docker build -t career-planning-ai:latest .
```

### 2. 运行容器

```bash
docker run -d \
  --name career-ai \
  -p 9000:9000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  career-planning-ai:latest
```

### 3. Docker Compose（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  career-ai:
    build: ./career-planning-ai
    ports:
      - "9000:9000"
    volumes:
      - ./career-planning-ai/config.yaml:/app/config.yaml
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app/src:/app
    restart: unless-stopped
    depends_on:
      - redis
      - neo4j

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/your_password
    volumes:
      - neo4j_data:/data
    restart: unless-stopped

volumes:
  redis_data:
  neo4j_data:
```

启动：
```bash
docker-compose up -d
```

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

```nginx
upstream career_ai {
    server 127.0.0.1:9000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://career_ai;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }
}
```

### 3. Supervisor 进程管理

```ini
[program:career-ai]
command=/path/to/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
directory=/path/to/career-planning-ai
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/career-ai/access.log
stderr_logfile=/var/log/career-ai/error.log
environment=PYTHONPATH="/path/to/career-planning-ai/src:/path/to/career-planning-ai"
```

### 4. Systemd 服务

```ini
[Unit]
Description=Career AI Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/career-planning-ai
Environment="PYTHONPATH=/path/to/career-planning-ai/src:/path/to/career-planning-ai"
ExecStart=/path/to/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
Restart=always
RestartSec=3

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

---

## 监控与日志

### 日志位置

- 应用日志：`logs/` 目录
- 临时文件：`temp/` 目录

### 健康检查

```bash
# 基础检查
curl http://localhost:9000/

# 图路径服务检查
curl http://localhost:9000/graph_path/health
```

### 性能监控

建议使用：
- Prometheus + Grafana
- ELK Stack（日志）
- APM 工具（如 Sentry）

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
- Redis 集群
- MySQL 主从
- Neo4j 集群
