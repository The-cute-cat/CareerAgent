# Docker 部署指南

本项目支持 Docker 容器化部署，采用多阶段构建优化镜像大小。

## 环境要求

- Docker 20.10+
- Docker Compose (可选)
- 内存建议 2GB+

## 快速部署

### 1. 构建镜像

```bash
# 进入后端目录
cd career-planning-backend

# 构建镜像
docker build -t career-planning-backend .
```

### 2. 运行容器

```bash
# 运行容器
docker run -d -p 8080:8080 \
  --name career-backend \
  --restart unless-stopped \
  career-planning-backend
```

### 3. 验证部署

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs -f career-backend

# 测试接口
curl http://localhost:8080/actuator/health
```

## 环境变量配置

容器运行时可通过环境变量覆盖配置：

| 变量 | 说明 | 示例 |
|------|------|------|
| `SPRING_PROFILES_ACTIVE` | 激活的配置文件 | `dev`, `prod` |
| `MYSQL_HOST` | MySQL 主机地址 | `192.168.1.100` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_DATABASE` | 数据库名 | `career_db` |
| `MYSQL_USERNAME` | 数据库用户名 | `root` |
| `MYSQL_PASSWORD` | 数据库密码 | `password` |
| `REDIS_HOST` | Redis 主机地址 | `192.168.1.100` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `REDIS_PASSWORD` | Redis 密码 | `password` |
| `JWT_SECRET` | JWT 密钥 | `your-secret-key` |
| `AI_SERVICE_URL` | AI 服务地址 | `http://ai:9000` |
| `JAVA_OPTS` | JVM 参数 | `-Xmx512m` |

### 示例：完整配置启动

```bash
docker run -d -p 8080:8080 \
  --name career-backend \
  --restart unless-stopped \
  -e SPRING_PROFILES_ACTIVE=prod \
  -e MYSQL_HOST=192.168.1.100 \
  -e MYSQL_PORT=3306 \
  -e MYSQL_DATABASE=career_db \
  -e MYSQL_USERNAME=root \
  -e MYSQL_PASSWORD=your_password \
  -e REDIS_HOST=192.168.1.100 \
  -e REDIS_PORT=6379 \
  -e REDIS_PASSWORD=your_redis_password \
  -e JWT_SECRET=your_jwt_secret \
  -e AI_SERVICE_URL=http://ai:9000 \
  -e JAVA_OPTS="-Xmx512m -Xms256m" \
  career-planning-backend
```

## Docker Compose 部署

### 1. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    container_name: career-backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - MYSQL_HOST=mysql
      - MYSQL_PORT=3306
      - MYSQL_DATABASE=career_db
      - MYSQL_USERNAME=root
      - MYSQL_PASSWORD=your_password
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=your_redis_password
      - JWT_SECRET=your_jwt_secret
      - AI_SERVICE_URL=http://ai:9000
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    container_name: career-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=your_password
      - MYSQL_DATABASE=career_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: career-redis
    command: redis-server --requirepass your_redis_password
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

### 2. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

## 镜像加速配置

如果构建速度慢，可配置 Docker 镜像加速器。

### Linux

编辑 `/etc/docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://f0wic39v.mirror.aliyuncs.com"
  ]
}
```

重启 Docker：

```bash
sudo systemctl restart docker
```

### 验证加速是否生效

```bash
docker info | grep -A 10 "Registry Mirrors"
```

## 常用操作

### 进入容器调试

```bash
docker exec -it career-backend /bin/sh
```

### 重新构建

```bash
# 不使用缓存重新构建
docker build --no-cache -t career-planning-backend .

# 先删除旧容器和镜像
docker stop career-backend && docker rm career-backend
docker rmi career-planning-backend
```

### 迁移数据目录

```bash
# 导出镜像
docker save career-planning-backend > career-backend.tar

# 导入镜像
docker load < career-backend.tar
```

### 清理资源

```bash
# 删除未使用的镜像
docker image prune -f

# 删除已停止的容器
docker container prune -f

# 清理所有未使用资源
docker system prune -a
```

## 生产环境注意事项

1. **安全配置**
   - 务必修改默认密码和密钥
   - 使用 Docker Secrets 管理敏感信息
   - 限制容器网络访问权限

2. **资源限制**
   - 根据服务器资源合理配置 JVM 内存
   - 设置容器 CPU 和内存限制

   ```bash
   docker run -d -p 8080:8080 \
     --memory="1g" \
     --memory-swap="1g" \
     --cpus="2" \
     career-planning-backend
   ```

3. **日志管理**
   - 生产环境建议配置日志收集
   - 限制日志文件大小

4. **健康检查**
   - 使用 `--health-cmd` 配置健康检查
   - 配合 K8s 或 Docker Swarm 使用

## 常见问题

### Q: 容器启动失败，提示连接数据库失败

检查环境变量配置是否正确，确保 MySQL 和 Redis 已启动并可访问。

### Q: 构建失败，依赖下载超时

配置 Maven 镜像源，编辑 `/usr/share/maven/conf/settings.xml`：

```xml
<mirrors>
  <mirror>
    <id>aliyun</id>
    <mirrorOf>*</mirrorOf>
    <url>https://maven.aliyun.com/repository/public</url>
  </mirror>
</mirrors>
```

### Q: 内存不足，构建被杀死

增加 Docker 内存限制，或使用较小的 Alpine 基础镜像。
