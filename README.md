# CareerAgent - 智能职业规划 AI 系统

> **职引未来** —— 基于 AI 的全方位职业发展规划平台，为大学生提供智能对话、人岗匹配、职业路径规划、能力评估等一站式职业发展服务。

## 项目架构

```
CareerAgent/
├── career-planning-ai/          # AI 服务 (Python / FastAPI)
├── career-planning-backend/     # 业务后端 (Java / Spring Boot)
├── career-planning-frontend/    # 前端应用 (Vue 3 / TypeScript)
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
| MySQL 9.6.0 | 关系数据库 |
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

- **Java** 21+
- **Python** 3.12+
- **Node.js** 18+
- **MySQL** 8.0+
- **Redis** 6.0+
- **Neo4j** 5.0+ (可选，用于知识图谱功能)
- **Milvus** 或 Zilliz Cloud 账号 (可选，用于向量检索)

### 1. AI 服务

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

### 2. 业务后端

```bash
cd career-planning-backend

# 配置数据库等
# 编辑 src/main/resources/application-dev.yaml

# 使用 Maven 启动
mvn spring-boot:run
# 服务运行在 http://localhost:8080
```

### 3. 前端应用

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
        └── application-prod.yaml     # 生产环境
```

### 前端应用

```
career-planning-frontend/
├── package.json              # npm 依赖配置
├── vite.config.ts            # Vite 配置
├── src/
│   ├── main.ts               # 应用入口
│   ├── App.vue               # 根组件
│   ├── api/                  # API 请求层
│   ├── components/           # 公共组件
│   ├── views/                # 页面视图 (17 个)
│   ├── router/               # 路由配置
│   ├── stores/               # Pinia 状态管理
│   ├── utils/                # 工具函数
│   ├── types/                # TypeScript 类型定义
│   └── assets/               # 静态资源
└── public/                   # 公共静态资源
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

## 文档

| 文档 | 说明 |
|------|------|
| [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) | 项目概述 |
| [docs/AI_SERVICE_API.md](docs/AI_SERVICE_API.md) | AI 服务 API 文档 |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | 配置详解 |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | 部署指南 |
| [career-planning-ai/README.md](career-planning-ai/README.md) | AI 服务详细文档 |
| [career-planning-backend/docs/BACKEND_DOC.md](career-planning-backend/docs/BACKEND_DOC.md) | 后端技术文档 |
| [career-planning-frontend/README.md](career-planning-frontend/README.md) | 前端文档 |

## License

Private - All Rights Reserved
