# Docker 部署指南

本文档介绍如何使用 Docker 容器化部署 CareerAgent 前端应用。

## 文件说明

| 文件 | 说明 |
|------|------|
| `Dockerfile` | 多阶段构建，构建阶段使用 Node.js 编译，生产阶段使用 Nginx 托管 |
| `nginx.conf` | Nginx 配置，含 SPA 路由 fallback、API 代理、gzip 压缩、静态资源缓存 |
| `.dockerignore` | 排除不需要进入构建上下文的文件（node_modules、dist、.git 等） |

## 快速开始

### 构建镜像

```bash
docker build -t career-planning-frontend .
```

### 运行容器

```bash
docker run -d -p 8081:80 --name frontend career-planning-frontend
```

浏览器访问 `http://localhost:8081` 即可。

### 查看日志

```bash
docker logs frontend
```

### 停止并删除容器

```bash
docker stop frontend && docker rm frontend
```

## 构建流程

Dockerfile 采用**多阶段构建**：

1. **构建阶段**（`node:22-alpine`）
   - 使用淘宝 npm 镜像安装依赖
   - 执行 `npm run build-only`（即 `vite build`）生成 `dist/`
   - 跳过 TypeScript 类型检查以避免构建中断

2. **生产阶段**（`nginx:alpine`）
   - 仅拷贝 `dist/` 到 Nginx 静态资源目录
   - 拷贝自定义 `nginx.conf`
   - 最终镜像体积小，不含 Node.js 和源码

## Nginx 配置说明

### SPA 路由 Fallback

Vue Router 使用 history 模式，所有未匹配的路径均返回 `index.html`：

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### API 代理

`/api/` 请求代理到后端服务，使用变量延迟解析避免后端未启动时 Nginx 崩溃：

```nginx
location /api/ {
    resolver 127.0.0.11 valid=30s;
    set $backend_host backend;
    proxy_pass http://$backend_host:8080/;
}
```

> `127.0.0.11` 是 Docker 内置 DNS，`backend` 为后端容器服务名。

### 静态资源缓存

Vite 构建产物中 `/assets/` 下的文件自带内容哈希，设置长缓存：

```nginx
location /assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 与后端联调

### Docker 网络方式

创建共享网络，前后端容器加入同一网络后可通过服务名互访：

```bash
# 创建网络
docker network create career-net

# 启动后端
docker run -d --network career-net --name backend career-planning-backend

# 启动前端
docker run -d -p 8081:80 --network career-net --name frontend career-planning-frontend
```

### Docker Compose 方式

示例 `docker-compose.yml`：

```yaml
services:
  frontend:
    build: ./career-planning-frontend
    ports:
      - "8081:80"
    depends_on:
      - backend

  backend:
    build: ./career-planning-backend
    ports:
      - "8080:8080"
```

启动：

```bash
docker compose up -d
```

## 常见问题

### 构建时类型检查报错

`npm run build` 会并行执行类型检查和 Vite 构建，项目中存在的 TypeScript 类型错误会中断构建。Dockerfile 中使用 `npm run build-only` 跳过类型检查，仅执行 `vite build`。

### Nginx 启动报错 `host not found in upstream`

原因是 Nginx 启动时无法解析 `backend` 主机名。已在 `nginx.conf` 中使用变量 + `resolver` 延迟解析，确保即使后端未启动，Nginx 也能正常启动。

### 清理 Docker 缓存

```bash
docker builder prune          # 清理构建缓存
docker system prune -a        # 清理所有未使用资源（镜像、容器、网络、缓存）
docker system df              # 查看磁盘占用
docker system prune -a -f
```
