# Career Planning Backend

职业规划后端服务，基于 Spring Boot 3.5.9 + Java 21 构建，为 CareerAgent 系统提供业务逻辑、数据管理和外部服务集成。

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Spring Boot | 3.5.9 |
| 语言 | Java | 21 |
| ORM | MyBatis-Plus | 3.5.15 |
| 数据库 | MySQL | 8.0+ |
| 缓存 | Redis | 6.0+ |
| 消息队列 | RabbitMQ | - |
| 认证 | JWT (jjwt) | - |
| 文件存储 | 阿里云 OSS | - |
| 支付 | 支付宝 SDK | - |
| 文档生成 | POI-tl / OpenHTMLToPDF | - |
| 工具库 | Hutool / Lombok | - |

## 主要功能

| 模块 | 功能 | 接口示例 |
|------|------|----------|
| **用户认证** | 登录/注册/验证码/忘记密码 | `/user/login`, `/user/register` |
| **AI 聊天** | 智能对话、SSE 流式输出 | `/chat/message`, `/chat/stream/*` |
| **简历管理** | 简历上传/解析/编辑/导出 | `/resume/*`, `/file/upload` |
| **人岗匹配** | 简历与职位智能匹配 | `/matching/*` |
| **职业路径** | 知识图谱路径规划 | `/graph_path/*` |
| **成长报告** | 报告生成与编辑 | `/report/*` |
| **代码评估** | GitHub/Gitee 代码分析 | `/code-ability/*` |
| **支付订阅** | 支付宝支付集成 | `/pay/*` |
| **积分系统** | 积分获取与消费 | `/points/*` |
| **知识库** | 职位知识管理 | `/knowledge/*` |
| **面试管理** | 面试记录与提醒 | `/interview/*` |

## 项目结构

```
src/main/java/com/backend/careerplanningbackend/
├── CareerPlanningBackendApplication.java  # 应用入口
├── config/                                 # 配置类
│   ├── WebConfig.java                      # Web 配置 (CORS/拦截器)
│   ├── InterceptorConfig.java              # 拦截器配置
│   ├── AIConfig.java                       # AI 服务配置
│   ├── AlipayConfig.java                   # 支付宝配置
│   └── SwaggerConfig.java                   # API 文档配置
├── controller/                             # 控制器层 (18个)
│   ├── UserController.java                 # 用户认证
│   ├── ChatController.java                  # AI 聊天
│   ├── ResumeController.java                # 简历管理
│   ├── ReportController.java                # 报告管理
│   ├── PaymentController.java               # 支付
│   └── ...
├── service/                                # 业务逻辑层
│   ├── UserService.java
│   ├── ChatService.java
│   └── ...
├── mapper/                                 # MyBatis Mapper (14个)
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
│   └── ...
└── http/                                   # HTTP 客户端
    └── AIClient.java                       # Python AI 服务客户端
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
# 开发环境
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# 生产环境
mvn spring-boot:run -Dspring-boot.run.profiles=prod

# 打包
mvn clean package -DskipTests

# 运行 JAR
java -jar target/career-planning-backend-*.jar --spring.profiles.active=prod
```

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

## 端口

默认运行在 `8080` 端口。
