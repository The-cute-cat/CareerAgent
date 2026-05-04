# CareerAgent 项目概述

## 项目简介

CareerAgent 是一个智能职业规划 AI 系统，旨在帮助用户进行职业发展规划、人岗匹配分析、能力评估等。系统采用前后端分离架构，包含三个主要模块：

- **career-planning-ai**：AI 服务后端（Python/FastAPI）
- **career-planning-backend**：业务后端（Java/Spring Boot）
- **career-planning-frontend**：前端应用

## 技术栈

### AI 服务后端 (career-planning-ai)
- **框架**: FastAPI + Uvicorn
- **Python版本**: 3.12
- **AI/LLM**: LangChain, OpenAI API, 通义千问 (Qwen), DeepSeek
- **向量数据库**: Milvus, ChromaDB
- **图数据库**: Neo4j
- **缓存**: Redis
- **关系数据库**: MySQL
- **依赖管理**: Poetry

### 核心依赖
```
fastapi==0.135.1
langchain>=1.2.7
langchain-openai>=1.1.10
chromadb>=1.5.5
neo4j>=6.1.0
redis>=7.4.0
sentence-transformers>=5.3.0
pymilvus>=2.6.10
```

## 项目结构

```
CareerAgent/
├── career-planning-ai/          # AI服务后端
│   ├── src/
│   │   └── ai_service/
│   │       ├── agents/          # AI智能体
│   │       ├── engine/          # 核心引擎
│   │       ├── models/          # 数据模型
│   │       ├── prompts/         # Prompt模板
│   │       ├── repository/      # 数据访问层
│   │       ├── response/        # 响应处理
│   │       ├── routers/         # API路由
│   │       ├── schemas/         # 数据结构
│   │       ├── services/        # 业务服务
│   │       └── utils/           # 工具类
│   ├── config.yaml              # 配置文件
│   ├── main.py                  # 入口文件
│   └── pyproject.toml           # 依赖配置
├── career-planning-backend/     # Java业务后端
├── career-planning-frontend/    # 前端应用
└── docs/                        # 项目文档
```

## 核心功能模块

### 1. 智能对话 (Chat)
- 支持阻塞式和流式（SSE）对话
- 支持文件上传与分析
- 会话管理（列表、删除、更新）
- 长短期记忆管理

### 2. 文件解析 (Parse)
- 支持多种文件格式（PDF、Word、图片等）
- 智能文本提取与结构化
- Redis 缓存加速

### 3. 人岗匹配 (Matching)
- 基于向量检索的岗位召回
- LLM Agent 深度匹配分析
- 能力差距评估

### 4. 职业路径规划 (Graph Path)
- 垂直晋升路径推荐
- 横向换岗路径分析
- 跨行业跃迁规划
- 目标导向路径规划

### 5. 代码能力评估 (Code Ability)
- GitHub/Gitee 代码分析
- 多维度能力评分
- AI 深度分析报告

### 6. 测试题生成 (Question)
- 技能相关测试题生成
- 工具使用测试题生成
- 学生答案评估

### 7. 报告生成 (Report)
- 成长计划生成
- 报告完整性检查
- 段落智能润色

### 8. 知识导师 (Knowledge Tutor)
- 知识点岗位影响分析
- 知识点详细解释

## 配置说明

> **Git LFS 注意事项**
>
> 项目中的大文件（ChromaDB/Milvus 种子数据、SQL 初始化脚本）通过 [Git LFS](https://git-lfs.com/) 管理。
> 克隆仓库后，这些文件默认为指针文件，**必须执行 `git lfs pull`** 才能获取实际内容：
>
> ```bash
> git lfs install && git lfs pull
> ```
>
> 未拉取时，种子数据初始化脚本会因找不到有效数据而跳过导入。

主要配置项位于 `config.yaml`：

| 配置项 | 说明 |
|--------|------|
| `database` | MySQL 数据库连接配置 |
| `llm` | 大语言模型配置（Qwen） |
| `vector` | 向量模型配置 |
| `milvus` | Milvus 向量数据库配置 |
| `chroma_config` | ChromaDB 配置 |
| `neo4j` | Neo4j 图数据库配置 |
| `redis` | Redis 缓存配置 |
| `conversation` | 对话记忆配置 |

## 部署方式

### Docker 部署
```bash
docker build -t career-planning-ai .
docker run -p 9000:9000 career-planning-ai
```

### 本地运行
```bash
cd career-planning-ai
poetry install
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

## API 端点

| 路径前缀 | 功能模块 |
|----------|----------|
| `/chat` | 智能对话 |
| `/parse` | 文件解析 |
| `/matching` | 人岗匹配 |
| `/graph_path` | 职业路径规划 |
| `/code-ability` | 代码能力评估 |
| `/question` | 测试题生成 |
| `/report` | 报告生成 |
| `/knowledge_tutor` | 知识导师 |
| `/convert` | 数据转换 |

## 安全认证

系统采用 Bearer Token 认证方式，需在请求头中携带：
```
Authorization: Bearer <token>
```

Token 密钥需与 Java 后端保持一致。

## 相关文档

- [AI 服务 API 文档](./AI_SERVICE_API.md)
- [配置详解](./CONFIGURATION.md)
- [部署指南](./DEPLOYMENT.md)
