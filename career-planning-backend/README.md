# Career Planning Backend

职业规划后端服务，基于 Spring Boot 3.5.9 + Java 21 构建，为 CareerAgent 系统提供业务逻辑、数据管理和外部服务集成。

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Spring Boot | 3.5.9 |
| 语言 | Java | 21 |
| ORM | MyBatis-Plus | 3.5.15 |
| 数据库 | MySQL Connector/J | 9.6.0 |
| 缓存 | Spring Data Redis / Jedis | - |
| 消息队列 | RabbitMQ (Spring AMQP) | 3.x |
| 认证 | JWT (jjwt) | 0.13.0 |
| 密码加密 | BCrypt (jbcrypt) | 0.4 |
| 文件存储 | 阿里云 OSS SDK | 3.18.5 |
| 支付 | 支付宝 SDK | 4.28.ALL |
| 文档导出 | POI-tl / OpenHTMLToPDF | 1.12.2 / 1.0.10 |
| 模板引擎 | Thymeleaf | - |
| HTTP 客户端 | RestTemplate + WebClient | 调用 AI Service |
| 工具库 | Hutool / Lombok | 5.8.40 |
| 日志 | Logback + Logstash Encoder | 7.4 |

## 主要功能

| 模块 | 功能 | 接口示例 |
|------|------|----------|
| **用户认证** | 登录/注册/邮箱验证码/忘记密码 (JWT) | `/user/login`, `/user/register` |
| **AI 聊天** | 多轮对话、SSE 流式转发、会话管理 | `/chat/message`, `/chat/stream/*` |
| **文件解析** | PDF/DOCX/图片上传与解析 | `/file/upload` |
| **简历管理** | JSON Resume 标准、编辑器、Word/PDF 导出 | `/resume/*` |
| **人岗匹配** | 基于向量检索 + LLM 的深度匹配 | `/matching/*` |
| **职业路径** | 知识图谱晋升/换岗/跨界路径规划 | `/graph_path/*` |
| **成长报告** | AI 生成计划、完整性检查、润色、编辑 | `/report/*` |
| **代码评估** | GitHub/Gitee 仓库质量分析与评分 | `/code-ability/*` |
| **测试题** | 技能相关题目生成与答案评估 | `/question/*` |
| **知识导师** | 知识点讲解与岗位影响分析 | `/knowledge_tutor/*` |
| **支付订阅** | 支付宝沙箱/正式环境切换 | `/pay/*` |
| **积分系统** | 积分消费确认、充值、会员变更 | `/points/*` |
| **会员套餐** | 套餐配置查询与管理 | `/member/*`, `/package/*` |
| **交易记录** | 用户交易流水查询 | `/transaction/*` |
| **数据转换** | 用户表单标准化格式转换 | `/convert/*` |
| **知识图谱** | 图谱关系查询与可视化 | `/knowledge-graph/*` |
| **全文搜索** | 全文检索服务 | `/search/*` |
| **用户反馈** | 反馈提交与管理 | `/feedback/*` |
| **面试管理** | AI 面试记录、日历、报告查看 | `/interview/*` |
| **管理后台** | 反馈处理、用量统计 | `/admin/*` |

## 项目结构

```
src/main/java/com/backend/careerplanningbackend/
├── CareerPlanningBackendApplication.java  # 应用入口
├── config/                                 # 配置类
│   ├── WebConfig.java                      # Web 配置 (CORS/拦截器)
│   ├── InterceptorConfig.java              # 拦截器配置
│   ├── AIConfig.java                       # AI 服务配置
│   ├── AlipayConfig.java                   # 支付宝配置
│   └── MailConfig.java                     # 邮件服务配置
├── controller/                             # 控制器层 (18 个)
│   ├── UserController.java                 # 用户认证
│   ├── ChatController.java                  # AI 聊天 (SSE 流式)
│   ├── ResumeController.java                # 简历管理
│   ├── ResumeExportController.java          # 简历导出 (Word/PDF)
│   ├── ReportController.java                # 报告管理
│   ├── MatchJobController.java              # 人岗匹配
│   ├── QuestionController.java              # 测试题管理
│   ├── PayController.java                   # 支付宝支付
│   ├── PointsReferController.java           # 积分系统
│   ├── MemberController.java                # 会员管理
│   ├── PackageController.java               # 套餐配置
│   ├── TransactionController.java           # 交易记录
│   ├── FeedbackController.java              # 用户反馈
│   ├── CodeAbilityController.java           # 代码能力评估
│   ├── ConvertController.java               # 数据转换
│   ├── KnowledgeGraphController.java        # 知识图谱查询
│   ├── SearchController.java                # 全文搜索
│   └── AdminController.java                 # 管理后台
├── service/                                # 业务逻辑层 (接口 + 实现)
│   ├── UserService.java
│   ├── ChatService.java
│   └── ...
├── mapper/                                 # MyBatis Mapper (14 个)
│   ├── UserMapper.java
│   └── ...
├── domain/                                 # 域对象
│   ├── po/                                 # 持久化对象
│   ├── dto/                                # 数据传输对象
│   └── vo/                                 # 视图对象
├── util/                                   # 工具类
│   ├── JwtUtil.java                        # JWT 工具
│   ├── AliOSSUtil.java                     # OSS 上传
│   ├── AIHttpClient.java                   # AI 服务调用
│   ├── RedisUtil.java                      # Redis 缓存
│   └── ...
├── http/                                   # HTTP 客户端
│   └── AIClient.java                       # Python AI 服务客户端
└── listeners/                              # MQ 消息监听器
```

## 数据库配置

在 `src/main/resources/application-dev.yaml` 中配置：

```yaml
spring:
  datasource:
    url: jdbc:mysql://${host}:${port}/${database_name}?useUnicode=true&characterEncoding=utf-8
    username: ${database_username}
    password: ${database_password}
  redis:
    host: ${redis_host}
    port: ${redis_port}
    username: ${redis_username}
    password: ${redis_password}
```

### 主要配置项

| 变量 | 说明 |
|------|------|
| `host`, `port`, `database_name` | MySQL 连接信息 |
| `database_username`, `database_password` | 数据库账号密码 |
| `redis_host`, `redis_port` | Redis 连接信息 |
| `email_host`, `email_port`, `MAIL_USERNAME_QQ`, `MAIL_PASSWORD_QQ` | 邮件服务 (QQ邮箱) |
| `ALY_OSS_*` | 阿里云 OSS 配置 |
| `JWT_SECRET` | JWT 密钥 |
| `SECRET` | 服务间通信密钥 |
| `AI_SERVICE_URL` | AI 服务地址 |

## 开发指南

### 环境要求

- JDK 21+
- Maven 3.8+
- MySQL 8.0+
- Redis 6.0+
- RabbitMQ 3.x (消息队列)

### 快速启动

```bash
# 1. 克隆并进入后端目录
cd career-planning-backend

# 2. 配置数据库连接
# 编辑 src/main/resources/application-dev.yaml

# 3. 安装依赖并启动
mvn clean install
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# 服务运行在 http://localhost:8080
```

### 多环境运行

```bash
# 开发环境（本地数据库）
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# 生产环境（远程服务器/云数据库）
mvn spring-boot:run -Dspring-boot.run.profiles=prod

# Docker 环境（使用 docker-compose 启动时自动激活，主机地址为 Docker 服务名）
mvn spring-boot:run -Dspring-boot.run.profiles=docker

# 打包
mvn clean package -DskipTests

# 运行 JAR
java -jar target/career-planning-backend-*.jar --spring.profiles.active=prod
```

> **Profile 说明**：
> - `dev` — 本地开发，连接本地 MySQL/Redis/RabbitMQ
> - `prod` — 生产部署，连接远程服务器（配置硬编码在 `application-prod.yaml`）
> - `docker` — 容器化部署，所有主机地址替换为 Docker 服务名（mysql、redis、rabbitmq、ai-service），密码从 `.env` 环境变量读取

### API 文档

启动服务后访问 Swagger UI：
- 开发环境: `http://localhost:8080/swagger-ui.html`
- 生产环境: `http://localhost:8080/doc.html` (Knife4j)

## 与 AI 服务通信

后端通过 HTTP 调用 AI 服务 (career-planning-ai)：

```java
// AIHttpClient.java
@Configuration
public class AIConfig {
    @Value("${ai.service.url}")
    private String aiServiceUrl;
    
    @Value("${communication.token.secret}")
    private String secret;
}

// 调用示例
POST http://localhost:9000/chat
Header: Authorization: Bearer {secret}
Body: { "message": "你好", "userId": "xxx" }
```

## 相关文档

- [后端技术文档](docs/BACKEND_DOC.md)
- [API 接口文档](../docs/AI_SERVICE_API.md)
- [项目配置详解](../docs/CONFIGURATION.md)
- [Docker 部署指南](docs/docker.md)

## Docker 部署

项目支持 Docker 容器化部署，详细指南请查看 [Docker 部署指南](docs/docker.md)。

### 快速部署

```bash
# 构建镜像
docker build -t career-planning-backend .

# 运行容器
docker run -d -p 8080:8080 --name career-backend career-planning-backend
```

### 使用 Docker Compose

```bash
docker-compose up -d
```

## 端口

默认运行在 `8080` 端口。
