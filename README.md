# CareerAgent - 智能职业规划 AI 系统

> **职引未来** —— 基于 AI 的全方位职业发展规划平台，为大学生提供智能对话、人岗匹配、职业路径规划、能力评估等一站式职业发展服务。

## 项目架构

```
CareerAgent/
├── career-planning-ai/          # AI 服务 (Python / FastAPI)
├── career-planning-backend/     # 业务后端 (Java / Spring Boot)
├── career-planning-frontend/    # 前端应用 (Vue 3 / TypeScript)
├── docker-compose.yml           # Docker Compose 编排（一键启动全部服务）
├── .env.example                 # 后端 + AI 服务环境变量模板（统一配置）
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
| **职业路径规划** | 基于知识图谱的晋升/换岗/跨界路径推荐 (Pareto 最优) |
| **代码能力评估** | 对接 GitHub/Gitee 仓库进行代码质量分析 |
| **测试题生成** | 根据知识点自动生成测试题并评估答案 |
| **成长报告** | 生成个性化成长计划与报告润色 |
| **知识导师** | 知识点讲解与辅导 (SSE 流式输出) |
| **AI 智能面试** | 基于 Live2D 虚拟形象的 AI 面试官模拟面试 |
| **简历编辑** | 富文本编辑器 + Word/PDF 导出 |
| **文件解析** | 支持 PDF/DOCX/图片格式的简历解析 |
| **数据转换** | 用户表单数据标准化格式转换 |
| **积分与会员** | 积分消费系统、会员套餐、支付宝支付集成 |
| **邀请返利** | 邀请好友获得积分奖励 |

## 技术栈

### AI 服务 (`career-planning-ai`)

| 技术 | 说明 |
|------|------|
| FastAPI + Uvicorn | Web API 框架 |
| Python 3.12 | 运行环境 (>=3.12, <3.13) |
| Poetry | 依赖管理 |
| Docker | 容器化部署 |
| LangChain + OpenAI + DashScope + LiteLLM | LLM 集成 (通义千问/DeepSeek/GLM-5) |
| Milvus / ChromaDB | 向量检索 |
| Neo4j (APOC) | 知识图谱 |
| Redis | 缓存 |
| scikit-learn / HDBSCAN / UMAP | 聚类/分类/降维 |
| NetworkX / igraph / leidenalg | 图算法 |
| pymoo | 多目标优化 (Pareto 路径规划) |
| PyMuPDF / python-docx / docling | 文件解析 |

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
| Element Plus 2.13 + Bootstrap 5 | UI 组件库 |
| Pinia 3.0 + persist插件 | 状态管理 (持久化) |
| ECharts 6 + AntV G6/X6 | 数据/图可视化 |
| Vue Flow | 流程图可视化 |
| Tiptap + WangEditor | 富文本编辑 |
| docx.js + jsPDF | 文档导出 |
| Pixi.js + Live2D | 虚拟形象 (AI 面试) |
| Axios | HTTP 客户端 |
| Vee-Validate + Yup | 表单验证 |
| Sass | CSS 预处理 |

## 快速开始

### 环境要求

| 环境 | 本地开发 | Docker 部署 |
|------|----------|------------|
| Java | 21+ | 由镜像提供 |
| Python | 3.12+ | 由镜像提供 |
| Node.js | ^20.19.0 或 >=22.12.0 | 由镜像提供 |
| MySQL | 8.0+ | 容器自动启动 |
| Redis | 6.0+ | 容器自动启动 |
| Neo4j | 5.0+ (可选) | 容器自动启动 |
| RabbitMQ | 3.x | 容器自动启动 |
| Milvus | 2.4+ (Standalone) | 容器自动启动 |

### 方式一：Docker Compose 一键部署（推荐）

一键启动全部服务（基础设施 + 应用），无需手动安装依赖：

```bash
# 1. 克隆项目
git clone <repo-url>
cd CareerAgent

# 2. ⚠️ 拉取 Git LFS 大文件数据（必须！）
#    项目中的 ChromaDB/Milvus 种子数据等大文件通过 Git LFS 管理，
#    clone 后仅为指针文件，需手动拉取实际内容（约 170MB）
git lfs install   # 首次使用需初始化 LFS（如已配置可跳过）
git lfs pull       # 拉取所有 LFS 追踪的实际文件内容

# 3. 配置环境变量（根目录 .env.example 已包含后端和 AI 服务全部配置）
cp .env.example .env
# 编辑 .env，填入实际密码、API Keys 等敏感信息

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

> **⚠️ 首次克隆后请务必执行 `git lfs pull` 拉取种子数据（约 170MB），详见上方 Docker 部署步骤说明。**

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
├── config.py                 # 配置管理 (Pydantic Settings, ~624行)
├── config.yaml               # 非敏感配置
├── .env                      # 敏感配置 (API Keys)
├── pyproject.toml            # Poetry 依赖配置 (~70个依赖包)
├── Dockerfile                # Docker 构建文件 (Python 3.12-slim)
├── entrypoint.sh             # 容器启动脚本 (动态装依赖+种子初始化)
└── src/ai_service/
    ├── routers/              # API 路由 (9 个模块)
    ├── services/             # 业务逻辑层
    ├── agents/               # AI 智能体 (含记忆系统, 11 个 Agent)
    ├── engine/               # 核心引擎 (状态机/AI 引擎)
    ├── repository/           # 数据访问层 (Neo4j/MySQL/Chroma/Milvus)
    ├── models/               # 数据模型
    ├── prompts/              # Prompt 模板 (20+ 个)
    ├── schemas/              # Pydantic 数据校验
    ├── scripts/              # 数据爬取/清洗/导入脚本
    └── utils/                # 工具类
```

### 业务后端

```
career-planning-backend/
├── pom.xml                   # Maven 依赖配置
├── README.md                 # 后端文档
├── Dockerfile                # 多阶段构建 (Maven → JRE)
├── docs/                     # 后端相关文档 (10+ 个文档)
└── src/main/
    ├── java/com/backend/careerplanningbackend/
    │   ├── config/           # 配置类 (拦截器/Web/AI服务/支付宝)
    │   ├── controller/       # 控制器 (18 个)
    │   ├── service/          # 业务层 (接口 + 实现)
    │   ├── mapper/           # 数据访问层 (14 个 Mapper)
    │   ├── domain/           # 域对象 (po/dto/vo)
    │   ├── util/             # 工具类 (JWT/OSS/AI Client/Redis)
    │   ├── http/             # HTTP 客户端 (调用 Python API)
    │   └── listeners/        # MQ 消息监听器
    └── resources/
        ├── application.yaml          # 主配置
        ├── application-dev.yaml      # 开发环境
        ├── application-prod.yaml     # 生产环境
        └── application-docker.yaml   # Docker 环境（主机地址用服务名）
```

### 前端应用

```
career-planning-frontend/
├── package.json              # npm 依赖配置 (~60个依赖包)
├── vite.config.ts            # Vite 构建配置 (代理到 8080)
├── Dockerfile                # 多阶段构建 (Node → Nginx)
├── nginx.conf                # Nginx 配置（API代理/SSE/缓存/gzip）
├── README.md                 # 前端文档
├── docs/                     # 前端相关文档
└── src/
    ├── main.ts               # 应用入口
    ├── App.vue               # 根组件
    ├── api/                  # API 请求层 (按模块划分)
    ├── components/           # 公共组件 (50+ 个组件)
    ├── views/                # 页面视图 (20+ 个页面)
    ├── router/               # 路由配置 (~25 个路由)
    ├── stores/               # Pinia 状态管理 (含持久化)
    ├── composables/          # 组合式函数
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
| 用户认证 | `POST /user/login`, `/user/register` | 登录/注册/验证码/忘记密码 |
| 聊天 | `POST /chat/message`, `/chat/stream/*` | AI 对话 (SSE 流式) |
| 文件 | `POST /file/upload` | 文件上传/解析 |
| 简历 | `POST /resume/*` | 简历编辑/导出 (Word/PDF) |
| 报告 | `GET/POST /report/*` | 成长报告管理/编辑 |
| 匹配 | `POST /matching/*` | 人岗匹配分析 |
| 面试 | `GET/POST /interview/*` | AI 面试管理 |
| 代码评估 | `GET /code-ability/*` | 代码能力评估结果 |
| 积分 | `POST /points/*` | 积分消费/充值/会员变更 |
| 会员 | `GET/POST /member/*` | 会员套餐管理 |
| 套餐 | `GET /package/*` | 套餐配置查询 |
| 交易 | `GET /transaction/*` | 交易记录查询 |
| 支付 | `POST /pay/*` | 支付宝支付 |
| 反馈 | `POST /feedback/*` | 用户反馈 |
| 转换 | `POST /convert/*` | 数据格式转换 |
| 知识图谱 | `GET /knowledge/*` | 知识图谱查询 |
| 搜索 | `GET /search/*` | 全文搜索 |
| 管理 | `GET/POST /admin/*` | 管理后台 (反馈/用量) |

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
| redis | redis:7-alpine | 6379 | 缓存 (密码保护, 256MB限制) |
| neo4j | neo4j:5-community | 7474/7687 | 知识图谱 (含 APOC 插件) |
| rabbitmq | rabbitmq:3-management-alpine | 5672/15672 | 消息队列 (含管理界面) |
| **milvus** | **milvusdb/milvus:v2.4-latest** | **19530/9091** | **向量数据库 (Standalone 模式)** |
| ai-service | Dockerfile 构建 | 9000 (内部) | AI 服务 (Python/FastAPI) |
| backend | Dockerfile 构建 | 8080 | 业务后端 (Spring Boot) |
| frontend | Dockerfile 构建 | 8081→80 | 前端应用 (Vue/Nginx) |

### 环境变量

| 文件 | 用途 | 必填项 |
|------|------|--------|
| `.env` (根目录) | **后端 Spring Boot + AI 服务** 统一配置（端口/密码/API Keys 等） | 密码、OSS Key、JWT Secret、**DashScope API Key** |
| `career-planning-ai/.env` | 仅**单独运行 AI 服务**时使用（独立于 Docker Compose） | 同上 |

### 网络与服务发现

所有服务通过 `career-network` bridge 网络互联，容器间使用**服务名**作为主机名通信：

```
backend → mysql:3306      # 数据库
backend → redis:6379      # 缓存
backend → rabbitmq:5672   # 消息队列
backend → ai-service:9000 # AI 服务
ai-service → redis:6379  # 缓存
ai-service → neo4j:7687  # 知识图谱
ai-service → milvus:19530 # 向量数据库
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
| `career-milvus-data` | Milvus 向量数据 |

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
