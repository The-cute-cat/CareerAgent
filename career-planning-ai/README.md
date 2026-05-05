# AI 职业规划服务 (Career Planning AI)

基于 FastAPI 构建的智能职业规划 AI 后端服务，为大学生提供人岗匹配、职业路径规划、成长计划生成等全方位职业发展支持。

## 项目简介

本服务整合了多种 AI 能力，通过大语言模型、向量检索、知识图谱等技术，为学生提供个性化的职业规划建议。支持简历解析、人岗匹配分析、职业发展路径推荐、智能问答等核心功能。

## 核心功能

| 模块 | 功能描述 |
|------|---------|
| **人岗匹配** | 基于人物画像进行智能岗位推荐与深度匹配分析 |
| **职业路径** | 提供垂直晋升、换岗转型、跨界跃迁等职业发展路径规划 |
| **报告服务** | 生成个性化成长计划，支持报告完整性检查与智能润色 |
| **知识导师** | 知识点讲解与岗位影响分析（SSE 流式输出） |
| **题目生成** | 基于技能/工具智能生成测试题，自动评估学生答案 |
| **文件解析** | 支持 PDF、DOCX、图片等多种格式简历解析 |
| **数据转换** | 用户表单数据转换为标准化人物画像 |
| **代码评估** | GitHub/Gitee 代码仓库能力评估 |
| **智能对话** | 支持多轮对话的 AI 职业咨询服务 |

## 技术栈

- **框架**: FastAPI + Uvicorn
- **AI/LLM**: LangChain, OpenAI API, DashScope, LiteLLM
- **向量数据库**: Milvus, ChromaDB
- **图数据库**: Neo4j
- **缓存**: Redis
- **数据处理**: PyMuPDF, Python-Docx, Docling
- **机器学习**: Sentence-Transformers, Scikit-learn, UMAP, HDBSCAN

## API 文档

### 接口文档 (docs/api/)

| 文档 | 说明 |
|------|------|
| [chat.md](docs/api/chat.md) | 智能对话接口（多轮对话、SSE 流式输出） |
| [parse.md](docs/api/parse.md) | 文件解析接口（PDF/DOCX/图片/纯文本） |
| [code_ability.md](docs/api/code_ability.md) | 代码能力评估（GitHub/Gitee 仓库分析） |
| [knowledge_tutor.md](docs/api/knowledge_tutor.md) | 知识导师接口（SSE 流式输出） |
| [question.md](docs/api/question.md) | 题目生成与答案评估 |
| [report.md](docs/api/report.md) | 报告服务（成长计划、完整性检查、智能润色） |
| [matching.md](docs/api/matching.md) | 人岗匹配接口 |

### 设计文档 (docs/design/)

| 文档 | 说明 |
|------|------|
| [graph_design.md](docs/design/graph_design.md) | 知识图谱设计文档 |
| [graph_lineage.md](docs/design/graph_lineage.md) | 图谱血缘关系设计 |
| [matching_overview.md](docs/design/matching_overview.md) | 人岗匹配思路汇总（详细版） |
| [matching_summary.md](docs/design/matching_summary.md) | 人岗匹配思路简介（简洁版） |

## 项目结构

```
career-planning-ai/
├── main.py                 # FastAPI 应用入口
├── config.py               # 配置管理（Pydantic Settings）
├── config.yaml             # 非敏感配置文件
├── .env                    # 敏感配置文件（需自行创建）
├── pyproject.toml          # Poetry 依赖配置
├── Dockerfile              # Docker 构建文件
├── entrypoint.sh           # Docker 启动脚本（自动安装依赖）
├── src/
│   └── ai_service/         # 核心服务模块
│       ├── routers/        # API 路由定义
│       ├── services/       # 业务逻辑层
│       ├── schemas/        # Pydantic 数据模型
│       ├── utils/          # 工具函数
│       └── ...
├── data/                   # 数据文件（向量库、模型等，运行时挂载）
├── logs/                   # 日志文件
├── docs/                   # 项目文档
│   ├── api/                # API 接口文档
│   ├── design/             # 设计文档
│   └── docker.md           # Docker 部署指南
└── tests/                  # 测试文件
```

---

# 项目启动指南

> **⚠️ Git LFS 数据拉取（必须）**
>
> 本项目的初始化数据文件通过 Git LFS 管理，`git clone` 后仅为指针文件，
> **必须在首次使用前执行 `git lfs pull`** 下载实际内容，否则种子数据导入将失败。
>
> ```bash
> # 在项目根目录执行
> git lfs install   # 首次需初始化 LFS（如已配置可跳过）
> git lfs pull       # 拉取 ChromaDB 种子数据 (~170MB) 和 Milvus 种子数据
>
> # 验证：确认以下目录中的 JSON 文件大小正常（非几 KB 的指针文件）
> ls -lh career-planning-ai/data/init/chroma/*_seed.json
> ls -lh career-planning-backend/docs/init/mysql/career_backend.sql
> ```
>
> Docker 容器内无 `.git` 目录，无法自动执行此操作，请务必在宿主机上提前完成。

## 一、安装依赖

### 1. Python 依赖（使用 Poetry）

#### 首次安装或更新依赖
```bash
# 进入项目目录
cd d:/code/web/CareerAgent/career-planning-ai

# 安装所有Python依赖
poetry install

# 或者，如果想更新所有依赖到最新版本
poetry update
```

#### 指定Python版本（如果需要）
```bash
# 激活特定的Python环境
poetry env use D:\IDE\Python\3.12\python.exe

# 或使用系统默认Python
poetry env use python
```

#### 常用Poetry命令
```bash
# 查看已安装的依赖
poetry show

# 查看依赖树
poetry show --tree

# 添加新依赖
poetry add <package-name>

# 添加开发依赖
poetry add --group dev <package-name>

# 更新特定依赖
poetry update <package-name>
```

### 2. Node.js 依赖（如果需要）

```bash
# 安装package.json中的依赖
npm install

# 或使用淘宝镜像
npm install --registry=https://registry.npmmirror.com
```

## 二、配置环境

> **⚠️ 重要警示：.env 配置冲突**
>
> - **使用 Docker Compose 时**：请勿在 `career-planning-ai/.env` 中配置变量，应统一使用根目录 `.env`（AI 服务会通过 `env_file: .env` 加载根目录配置）
> - **单独运行 AI 服务时**：仅在 `career-planning-ai/.env` 中配置变量
> - **切勿同时配置**：根目录 `.env` 和 `career-planning-ai/.env` 中的相同变量，否则可能导致配置混乱

项目配置分为两部分：
- **`.env`**: 存储敏感信息（API Keys、密码、Token等）
- **`config.yaml`**: 存储非敏感配置（模型名称、超时时间、路径等）

### 1. 创建 .env 文件

在项目根目录创建 `.env` 文件，填入敏感配置：

```env
# ========== 数据库配置 ==========
DATABASE__USER=your_db_user
DATABASE__PASSWORD=your_db_password

# ========== 通信密钥 ==========
COMMUNICATION__TOKEN__SECRET=your_token_secret

# ========== LLM API 配置 ==========
LLM__API_KEY=your_llm_api_key
LLM__BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM__MODEL_NAME=qwen-max

# ========== Milvus 向量数据库 ==========
MILVUS__CLOUD__URL=your_milvus_url
MILVUS__CLOUD__TOKEN=your_milvus_token

# ========== Redis 缓存 ==========
REDIS__HOST=your_redis_host
REDIS__PORT=6379
REDIS__USERNAME=your_redis_username
REDIS__PASSWORD=your_redis_password

# ========== Neo4j 图数据库 ==========
NEO4J__PASSWORD=your_neo4j_password

# ========== GitHub/Gitee Token（代码评估功能）==========
CODE_ABILITY__GITHUB_TOKEN=your_github_token
CODE_ABILITY__GITEE_TOKEN=your_gitee_token

# ========== 对话 Agent 配置 ==========
CONVERSATION__AGENT__API_KEY=your_agent_api_key
```

### 2. config.yaml 配置说明

`config.yaml` 包含非敏感的运行时配置，主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `debug` | 调试模式 | `true` |
| `llm.timeout` | LLM 请求超时时间（秒） | `120` |
| `llm.max_retries` | 最大重试次数 | `3` |
| `llm.max_concurrent_requests` | 最大并发请求数 | `3` |
| `path_config.temp.expire` | 临时文件过期时间（秒） | `900` |
| `redis.cache_timeout.default` | Redis 默认缓存时间（秒） | `86400` |
| `conversation.memory.short.max_messages` | 短期记忆最大消息数 | `20` |

### 3. 重要配置说明

#### Token 密钥配置
**必须确保 Python 和 Java 的 token secret 一致！**

- **Python 配置**: `.env` 中的 `COMMUNICATION__TOKEN__SECRET`
- **Java 配置**: `application.yaml` 中的 `communication.token.secret`

#### 路径配置
路径配置支持自动回退，如果配置的路径不存在或为 `<xxx_PATH>` 占位符，将自动使用项目目录：
- 临时文件: `<项目根目录>/temp`
- 日志文件: `<项目根目录>/logs`
- 数据文件: `<项目根目录>/data`

#### 可选服务配置
以下服务如果未配置，会自动降级或跳过：
- **Redis**: 未配置时禁用缓存功能
- **Neo4j**: 未配置时禁用图数据库功能
- **GitHub/Gitee Token**: 未配置时可能受 API 速率限制影响

### 4. 配置注意事项

#### 配置加载优先级

配置加载顺序（优先级从高到低）：

```
环境变量 → .env 文件 → config.yaml
```

**具体规则：**
- 环境变量优先级最高，会覆盖 `.env` 和 `config.yaml` 中的同名配置
- `.env` 文件优先级高于 `config.yaml`
- `config.yaml` 作为默认配置，定义非敏感参数

**示例：**
```bash
# 环境变量方式（优先级最高）
export LLM__API_KEY=sk-xxx

# .env 文件方式（优先级次之）
LLM__API_KEY=sk-xxx

# config.yaml 中的配置会被覆盖
llm:
  api_key: <API_KEY>  # 占位符，实际值来自 .env 或环境变量
```

**多级配置示例：**
```bash
# .env 文件中配置 conversation.agent 的 api_key
CONVERSATION__AGENT__API_KEY=sk-deepseek-xxx

# config.yaml 中 conversation.agent 未配置 api_key
# 最终使用 .env 中的值
conversation:
  agent:
    model_name: deepseek-reasoner
    base_url: https://api.deepseek.com
    # api_key 未配置，从 .env 加载
```

#### AI 模型配置自动继承

项目中存在多个 AI 模型配置模块（如 `pdf`、`image`、`test_question`、`growth_plan_agent`、`code_ability` 等），这些模块的配置支持**自动继承机制**：

```
┌─────────────────────────────────────────────────────────────┐
│                      llm (基础配置)                          │
│  api_key, base_url, model_name, timeout, max_retries...    │
└─────────────────────────────────────────────────────────────┘
          ↓ 自动继承（如未单独配置）
┌─────────────────────────────────────────────────────────────┐
│  pdf / image / test_question / code_ability / ...          │
│  各模块可覆盖特定字段（如 model_name、temperature）           │
└─────────────────────────────────────────────────────────────┘
```

**继承规则：**
- 各模块独立判断每个字段：**字段未配置时继承，已配置则使用自身值**
- 例如：仅配置 `model_name`，则 `api_key`、`base_url`、`timeout` 等仍从 `llm` 继承
- 例如：配置了 `api_key`，则使用自身的 `api_key`，不会继承 `llm.api_key`

**示例：**
```yaml
llm:
  api_key: <DASHSCOPE_API_KEY>
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
  model_name: qwen-max
  timeout: 120
  max_retries: 3
  max_concurrent_requests: 3
  extra:
    temperature: 0.7

# pdf 模块仅配置了 model_name 和 extra.temperature
# 其他字段（api_key、base_url、timeout 等）均继承 llm
pdf:
  model_name: qwen-vl-plus
  extra:
    temperature: 0.1

# conversation.agent 使用不同的 API 提供商
# config.yaml 中配置 base_url、model_name、extra.temperature
# api_key 通过 .env 文件配置（CONVERSATION__AGENT__API_KEY）
# timeout、max_retries 等未配置，继承 llm 对应字段
conversation:
  agent:
    model_name: deepseek-reasoner
    base_url: https://api.deepseek.com
    # api_key 在 .env 中配置，优先级高于继承
    extra:
      temperature: 0.7
```

#### Milvus 本地/云端切换

```yaml
milvus:
  force_local: false  # true=强制本地模式，false=自动故障转移
  local:
    host: 49.235.164.243
    port: 19530
  cloud:
    url: <url>
    token: <token>
```

- `force_local: true` - 强制使用本地 Milvus
- `force_local: false` - 本地不可用时自动切换到云端

#### 临时文件自动清理

```yaml
path_config:
  temp:
    exit_is_clean: true    # 程序退出时清理临时文件
    run_is_clean: false    # 运行时定期清理（谨慎开启）
    expire: 900            # 文件过期时间（秒）
    cleanup_interval: 60   # 清理间隔（秒）
```

- `run_is_clean: true` 会启动后台清理任务，适合生产环境
- 开发环境建议 `run_is_clean: false`，避免调试时文件被清理

#### 对话记忆管理

```yaml
conversation:
  memory:
    short:
      max_messages: 20              # 短期记忆最大消息数
      max_tokens: 10000             # 最大 token 数
      compression_trigger_raito: 0.8 # 压缩触发阈值（80%时压缩）
      keep_recent_messages: 8        # 压缩时保留最近消息数
    long:
      max_memory_count: 50          # 长期记忆最大条数
      min_score: 0.6                # 记忆检索最低分数
```

- 短期记忆达到 `max_tokens * compression_trigger_raito` 时触发压缩
- 长期记忆通过向量检索召回，低于 `min_score` 的记忆不会被召回

#### HTTPS 证书验证

```yaml
other:
  ssl_verify: false  # 关闭 SSL 验证（开发环境）
```

- 生产环境建议开启或配置有效证书路径
- 关闭验证可能存在安全风险

## 三、启动服务

### 方法1: 使用Poetry启动（推荐）

```bash
# 开发模式（带热重载）
poetry run uvicorn main:app --host 127.0.0.1 --port 9000 --reload

# 生产模式
poetry run uvicorn main:app --host 127.0.0.1 --port 9000

# 指定workers数量（生产环境）
poetry run uvicorn main:app --host 127.0.0.1 --port 9000 --workers 4
```

### 方法2: 直接使用Python

```bash
# 确保已激活虚拟环境
poetry shell

# 然后启动服务
python -m uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

### 方法3: 直接运行（不推荐）

```bash
# 不使用Poetry环境
python -m uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

### 方法4: Docker 部署

详细文档请参考 [Docker 部署指南](docs/docker.md)。

#### 方式 A：Docker Compose（推荐）

使用根目录 `docker-compose.yml` 一键启动，AI 服务会自动连接同网络中的 Redis 和 Neo4j：

```bash
# 在项目根目录执行
cd ..
docker compose up -d --build ai-service
```

环境变量覆盖规则：`docker-compose.yml` 中的 `environment` 会覆盖 `.env` 中的 Redis/Neo4j 主机地址为 Docker 服务名，API Key 等敏感配置仍从 `career-planning-ai/.env` 读取。

#### 方式 B：单独运行容器

**快速开始：**

```bash
# 1. 构建镜像
docker build -t career-planning-ai .

# 2. 运行容器（首次运行自动安装依赖，约5-10分钟）
docker run -d \
  --name career-ai \
  -p 9000:9000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  career-planning-ai

# 3. 查看日志
docker logs -f career-ai
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `.env` | 环境变量文件（API密钥等敏感配置） |
| `data` | 数据目录（向量库、模型文件） |
| `logs` | 日志目录 |

**常用命令：**

```bash
# 停止容器
docker stop career-ai

# 启动容器
docker start career-ai

# 删除容器
docker rm -f career-ai

# 一键重建
docker rm -f career-ai && docker run -d --name career-ai -p 9000:9000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  career-planning-ai
```

**镜像分享（离线部署）：**

```bash
# 导出镜像
docker save career-planning-ai | gzip > career-planning-ai.tar.gz

# 导入镜像（部署机器上）
gunzip -c career-planning-ai.tar.gz | docker load
```

## 四、验证服务

### 1. 检查服务是否启动
访问: http://localhost:9000/

预期响应:
```json
{
  "code": 200,
  "state": true,
  "msg": null,
  "data": "Emptiness is also an attitude!(=^･ω･^=)"
}
```

### 2. 测试聊天接口

#### 使用HTTP文件测试
打开 `test_chat.http` 文件，点击 "Send Request" 测试

#### 使用curl测试
```bash
curl -X POST "http://localhost:9000/chat/message" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Bearer <token>" \
  -d "message=你好&conversationId=123"
```

#### 通过Java后端测试
```bash
curl -X POST "http://localhost:8080/chat/message" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=你好&conversationId=123"
```

## 五、常见问题

### 1. 模块导入错误
**错误**: `ModuleNotFoundError: No module named 'ai_service'`

**解决**: 确保所有导入路径使用 `from src.ai_service.xxx` 格式

### 2. Poetry环境问题
**错误**: `The lock file is not up to date with the latest changes in pyproject.toml`

**解决**:
```bash
# 更新lock文件
poetry lock

# 然后重新安装
poetry install
```

### 3. 端口被占用
**错误**: `Address already in use: ('0.0.0.0', 9000)`

**解决**:
```bash
# Windows - 查找占用端口的进程
netstat -ano | findstr :9000

# 杀掉进程（替换PID为实际进程ID）
taskkill /PID <PID> /F

# 或使用其他端口
poetry run uvicorn main:app --host 0.0.0.0 --port 9001
```

**错误**:
```text
ERROR:    [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。
```
**解决**:
```shell
# 其他同上
# 检查 Windows 保留端口，Windows 可能会保留某些端口范围
netsh interface ipv4 show excludedportrange protocol=tcp
# 如果 9000 在保留范围内，重启 Windows NAT 服务，释放 Windows 保留的端口（需要管理员权限）
net stop winnat
net start winnat
```

### 4. 依赖冲突
**解决**:
```bash
# 清除Poetry缓存
poetry cache clear pypi --all

# 删除虚拟环境重新创建
poetry env remove <env-name>
poetry install
```

## 六、开发建议

### 1. 使用虚拟环境
始终在Poetry虚拟环境中开发，避免污染全局Python环境

### 2. 依赖更新策略
- 开发环境可以定期 `poetry update` 更新依赖
- 生产环境应该锁定版本，使用 `poetry install` 而不是 `poetry update`

### 3. IDE配置
确保IDE使用Poetry创建的虚拟环境：
- VSCode: 选择正确的Python解释器
- PyCharm: 设置Poetry虚拟环境为项目解释器

### 4. 日志调试
查看服务日志，定位问题：
```bash
# 日志会输出到控制台
# 也可以配置日志文件路径
```

## 七、完整启动流程

```bash
# 1. 进入项目目录
cd d:/code/web/CareerAgent/career-planning-ai

# 2. 安装/更新依赖
poetry install

# 3. 配置环境
# 复制 .env.example 为 .env，填入敏感配置
# 检查 config.yaml 中的非敏感配置

# 4. 启动服务
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --reload

# 5. 验证服务
# 浏览器访问 http://localhost:9000/
```

## 八、停止服务

- 开发模式: 在终端按 `Ctrl + C`
- 如果在后台运行，使用 `taskkill` 命令（Windows）或 `kill` 命令（Linux/Mac）
