# CareerAgent - 智能职业规划 AI 系统

> **职引未来** —— 基于 AI 的全方位职业发展规划平台，为大学生提供智能对话、人岗匹配、职业路径规划、能力评估等一站式职业发展服务。

## 项目架构

```
CareerAgent/
├── career-planning-ai/          # AI 服务 (Python / FastAPI)
├── career-planning-backend/     # 业务后端 (Java / Spring Boot)
├── career-planning-frontend/    # 前端应用 (Vue 3 / TypeScript)
├── docker-compose.yml           # Docker Compose 编排（一键启动全部服务）
├── .env.example                 # 后端环境变量模板
├── .dockerignore                # Docker 构建排除规则
└── docs/                        # 项目文档
```

### 系统架构图

```
┌──────────────────────────────────────────┐
│          Frontend (Vue 3)                │
│          http://localhost:8081            │
└──────────────────┬───────────────────────┘
                   │ REST API
                   ▼
┌──────────────────────────────────────────┐
│       Backend (Spring Boot)              │
│          http://localhost:8080            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │Controller│→│ Service  │→│ MyBatis- │ │
│  │   层     │ │   层     │ │  Plus    │ │
│  └──────────┘ └────┬─────┘ └────┬─────┘ │
│                    │             │       │
│              ┌─────┴─────┐  ┌───┴───┐   │
│              │ AI Client │  │ MySQL │   │
│              └─────┬─────┘  └───────┘   │
└────────────────────┼─────────────────────┘
                     │ REST API + SSE
                     ▼
┌──────────────────────────────────────────┐
│        AI Service (FastAPI)              │
│          http://localhost:9000            │
│  ┌──────────┐ ┌──────────────────────┐  │
│  │ Routers  │→│ LangChain / Agents   │  │
│  └──────────┘ └──────────────────────┘  │
│       │                                  │
│  ┌────┴────┐ ┌───────┐ ┌───────┐       │
│  │Milvus/  │ │ Neo4j │ │ Redis │       │
│  │ChromaDB │ │       │ │       │       │
│  └─────────┘ └───────┘ └───────┘       │
└──────────────────────────────────────────┘
```

## 核心功能

| 功能模块 | 说明 |
|----------|------|
| **智能对话** | 基于 LLM 的多轮对话，支持 SSE 流式输出 |
| **人岗匹配** | 简历解析 + 岗位需求智能匹配分析 |
| **职业路径规划** | 基于知识图谱的晋升/换岗/跨界路径推荐 |
| **代码能力评估** | 对接 GitHub/Gitee 仓库进行代码质量分析 |
| **测试题生成** | 根据知识点自动生成测试题并评估答案 |
| **成长报告** | 生成个性化成长计划与报告润色 |
| **知识导师** | 知识点讲解与辅导 (SSE 流式输出) |
| **简历编辑** | 富文本编辑器 + Word/PDF 导出 |
| **文件解析** | 支持 PDF/DOCX/图片格式的简历解析 |

## 技术栈

### AI 服务 (`career-planning-ai`)

| 技术 | 说明 |
|------|------|
| FastAPI + Uvicorn | Web API 框架 |
| Python 3.12 | 运行环境 |
| Poetry | 依赖管理 |
| Docker | 容器化部署 |
| LangChain + OpenAI + DashScope | LLM 集成 (通义千问/DeepSeek) |
| Milvus / ChromaDB | 向量检索 |
| Neo4j | 知识图谱 |
| Redis | 缓存 |

### 业务后端 (`career-planning-backend`)

| 技术 | 说明 |
|------|------|
| Spring Boot 3.5.9 | Web 框架 |
| Java 21 | 运行环境 |
| MyBatis-Plus 3.5.15 | ORM 框架 |
| MySQL 8.0+ | 关系数据库 |
| Redis | 缓存 (验证码/会话) |
| RabbitMQ | 消息队列 |
| JWT (jjwt) | 认证授权 |
| 阿里云 OSS | 文件存储 |
| 支付宝 SDK | 支付集成 |
| POI-tl + OpenHTMLToPDF | 文档生成 |

### 前端应用 (`career-planning-frontend`)

| 技术 | 说明 |
|------|------|
| Vue 3.5 + TypeScript 5.9 | 前端框架 |
| Vite 7.3 | 构建工具 |
| Element Plus 2.13 | UI 组件库 |
| Pinia 3.0 | 状态管理 |
| ECharts 6 + AntV G6/X6 | 数据/图可视化 |
| Tiptap + WangEditor | 富文本编辑 |
| docx.js + jsPDF | 文档导出 |

## 快速开始

### 环境要求

| 环境 | 本地开发 | Docker 部署 |
|------|----------|------------|
| Java | 21+ | 由镜像提供 |
| Python | 3.12+ | 由镜像提供 |
| Node.js | 18+ | 由镜像提供 |
| MySQL | 8.0+ | 容器自动启动 |
| Redis | 6.0+ | 容器自动启动 |
| Neo4j | 5.0+ (可选) | 容器自动启动 |
| RabbitMQ | 3.x | 容器自动启动 |
| Milvus | 可选，向量检索 | 云端或自建 |

### 方式一：Docker Compose 一键部署（推荐）

一键启动全部 7 个服务（4 个基础设施 + 3 个应用），无需手动安装依赖：

```bash
# 1. 克隆项目
git clone <repo-url>
cd CareerAgent

# 2. 配置环境变量
cp .env.example .env                                    # 后端配置（端口、密码等）
cp career-planning-ai/.env.example career-planning-ai/.env  # AI 服务 API Keys
# 编辑这两个文件，填入实际密码和 DashScope API Key

# 3. 一键构建并启动（首次约 5-10 分钟，取决于网速）
docker compose up -d --build

# 4. 查看服务状态
docker compose ps

# 5. 访问服务
#   前端:         http://localhost:8081
#   后端 API:     http://localhost:8080
#   RabbitMQ管理: http://localhost:15672
#   Neo4j浏览器:  http://localhost:7474

# 6. 查看日志
docker compose logs -f backend
docker compose logs -f ai-service

# 7. 停止所有服务
docker compose down
```

> 详细说明请参考 [Docker Compose 编排详解](#docker-compose-编排详解) 及各子项目 Docker 文档。

### 方式二：本地开发

#### 1. AI 服务

##### 方式一：本地运行

```bash
cd career-planning-ai

# 安装依赖 (Poetry)
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Keys 等敏感配置

# 启动服务
poetry run python main.py
# 服务运行在 http://localhost:9000
```

##### 方式二：Docker 单独部署

```bash
cd career-planning-ai

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Keys 等敏感配置

# 构建并运行容器
docker build -t career-planning-ai .
docker run -d \
  --name career-ai \
  -p 9000:9000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  career-planning-ai

# 查看日志
docker logs -f career-ai
# 服务运行在 http://localhost:9000
```

> Docker 部署详情请参考 [career-planning-ai/docs/docker.md](career-planning-ai/docs/docker.md)

#### 2. 业务后端

```bash
cd career-planning-backend

# 配置数据库等
# 编辑 src/main/resources/application-dev.yaml

# 使用 Maven 启动
mvn spring-boot:run -Dspring-boot.run.profiles=dev
# 服务运行在 http://localhost:8080
```

#### 3. 前端应用

```bash
cd career-planning-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 应用运行在 http://localhost:8081
```

## 项目结构详解

### AI 服务

```
career-planning-ai/
├── main.py                   # FastAPI 应用入口
├── config.py                 # 配置管理 (Pydantic Settings)
├── config.yaml               # 非敏感配置
├── .env                      # 敏感配置 (API Keys)
├── pyproject.toml            # Poetry 依赖配置
├── Dockerfile                # Docker 构建文件
└── src/ai_service/
    ├── routers/              # API 路由 (9 个模块)
    ├── services/             # 业务逻辑层
    ├── agents/               # AI 智能体
    ├── engine/               # 核心引擎
    ├── repository/           # 数据访问层
    ├── models/               # 数据模型
    ├── prompts/              # Prompt 模板
    └── schemas/              # Pydantic 数据模型
```

### 业务后端

```
career-planning-backend/
├── pom.xml                   # Maven 依赖配置
├── README.md                 # 后端文档
├── Dockerfile                # Docker 构建文件
├── docs/                     # 后端相关文档
└── src/main/
    ├── java/com/backend/careerplanningbackend/
    │   ├── config/           # 配置类 (拦截器/Web/AI服务/支付宝)
    │   ├── controller/       # 控制器 (18 个)
    │   ├── service/          # 业务层
    │   ├── mapper/           # 数据访问层 (14 个 Mapper)
    │   ├── domain/           # 域对象 (po/dto/vo)
    │   ├── util/             # 工具类 (AI Client/JWT/OSS)
    │   └── http/             # HTTP 客户端 (Python API 调用)
    └── resources/
        ├── application.yaml          # 主配置
        ├── application-dev.yaml      # 开发环境
        ├── application-prod.yaml     # 生产环境
        └── application-docker.yaml   # Docker 环境（主机地址用服务名）
```

### 前端应用

```
career-planning-frontend/
├── package.json              # npm 依赖配置
├── vite.config.ts            # Vite 配置
├── Dockerfile                # 多阶段构建 (Node → Nginx)
├── nginx.conf                # Nginx 配置（API代理/SSE/缓存）
├── README.md                 # 前端文档
├── docs/                     # 前端相关文档
└── src/
    ├── main.ts               # 应用入口
    ├── App.vue               # 根组件
    ├── api/                  # API 请求层
    ├── components/           # 公共组件
    ├── views/                # 页面视图 (17 个)
    ├── router/               # 路由配置
    ├── stores/               # Pinia 状态管理
    ├── utils/                # 工具函数
    ├── types/                # TypeScript 类型定义
    └── assets/               # 静态资源
```

## API 概览

### AI 服务端点

| 路径前缀 | 功能 |
|----------|------|
| `/chat` | 智能对话 |
| `/parse` | 文件解析 |
| `/matching` | 人岗匹配 |
| `/graph_path` | 职业路径规划 |
| `/code-ability` | 代码能力评估 |
| `/question` | 测试题生成 |
| `/report` | 报告生成 |
| `/knowledge_tutor` | 知识导师 |
| `/convert` | 数据转换 |

### 业务后端端点

| 模块 | 接口 | 说明 |
|------|------|------|
| 用户认证 | `POST /user/login`, `/user/register` | 登录/注册/验证码 |
| 聊天 | `POST /chat/message`, `/chat/stream/*` | AI 对话 |
| 文件 | `POST /file/upload` | 文件上传 |
| 简历 | `POST /resume/*` | 简历编辑/导出 |
| 报告 | `GET/POST /report/*` | 成长报告管理 |
| 支付 | `POST /pay/*` | 支付宝支付 |

## 配置说明

### 服务间通信

Backend 与 AI Service 通过 HTTP REST API + SSE 通信，需确保两端的通信 Token 一致：

```yaml
# Backend (application.yaml)
communication:
  token:
    secret: CareerAgent

# AI Service (.env)
COMMUNICATION__TOKEN__SECRET=CareerAgent
```

### 前端代理

前端通过 Vite 代理将 `/api/*` 请求转发至后端：

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8080',
    changeOrigin: true
  }
}
```

> 详细配置说明请参考 [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

## Docker Compose 编排详解

### 服务清单

| 服务 | 镜像/构建 | 端口 | 说明 |
|------|-----------|------|------|
| mysql | mysql:8.0 | 3306 | 关系数据库 |
| redis | redis:7-alpine | 6379 | 缓存 |
| neo4j | neo4j:5-community | 7474/7687 | 知识图谱 (含 APOC 插件) |
| rabbitmq | rabbitmq:3-management-alpine | 5672/15672 | 消息队列 (含管理界面) |
| ai-service | Dockerfile 构建 | 9000 (内部) | AI 服务 (Python/FastAPI) |
| backend | Dockerfile 构建 | 8080 | 业务后端 (Spring Boot) |
| frontend | Dockerfile 构建 | 8081→80 | 前端应用 (Vue/Nginx) |

### 环境变量

| 文件 | 用途 | 必填项 |
|------|------|--------|
| `.env` | 后端 Spring Boot + 基础设施密码 | 密码、OSS Key、JWT Secret |
| `career-planning-ai/.env` | AI 服务 Pydantic Settings | **DashScope API Key** (必填) |

### 网络与服务发现

所有服务通过 `career-network` bridge 网络互联，容器间使用**服务名**作为主机名通信：

```
backend → mysql:3306      # 数据库
backend → redis:6379      # 缓存
backend → rabbitmq:5672   # 消息队列
backend → ai-service:9000 # AI 服务
ai-service → redis:6379  # 缓存
ai-service → neo4j:7687  # 知识图谱
frontend → backend:8080  # API 反向代理
```

### 数据持久化

所有数据库数据通过命名卷持久化，`docker compose down` 不会丢失数据：

| 卷名 | 用途 |
|------|------|
| `career-mysql-data` | MySQL 数据文件 |
| `career-redis-data` | Redis 快照 |
| `career-neo4j-data` | Neo4j 图数据 |
| `career-rabbitmq-data` | RabbitMQ 队列消息 |
| `career-ai-data` | AI 服务向量库/模型缓存 |
| `career-ai-logs` | AI 服务日志 |

### 常用运维命令

```bash
# 查看日志
docker compose logs -f                    # 全部服务
docker compose logs -f backend            # 仅后端
docker compose logs -f ai-service --tail 100  # 最近 100 行

# 重启单个服务
docker compose restart backend

# 重新构建并重启
docker compose up -d --build backend

# 进入容器调试
docker compose exec backend sh
docker compose exec ai-service bash

# 查看资源占用
docker stats --no-stream

# 清理（保留数据卷）
docker compose down

# 清理（删除数据卷，慎用！）
docker compose down -v

# 完全重建（清除镜像+缓存）
docker compose down -v --rmi all
docker builder prune -f
```

## 文档

| 文档 | 说明 |
|------|------|
| [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) | 项目概述 |
| [docs/AI_SERVICE_API.md](docs/AI_SERVICE_API.md) | AI 服务 API 文档 |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | 配置详解 |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | 部署指南 |
| [career-planning-ai/docs/docker.md](career-planning-ai/docs/docker.md) | AI 服务 Docker 部署指南 |
| [career-planning-backend/docs/docker.md](career-planning-backend/docs/docker.md) | 后端 Docker 部署指南 |
| [career-planning-frontend/docs/DOCKER.md](career-planning-frontend/docs/DOCKER.md) | 前端 Docker 部署指南 |
| [career-planning-backend/README.md](career-planning-backend/README.md) | 后端详细文档 |
| [career-planning-frontend/README.md](career-planning-frontend/README.md) | 前端详细文档 |
| [career-planning-ai/README.md](career-planning-ai/README.md) | AI 服务详细文档 |

## 贡献指南

欢迎提交 Pull Request 或 Issue！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## License

Private - All Rights Reserved
