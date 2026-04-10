# AGENTS.md - AI 代码代理指南

## 项目概述
**职业规划后端** 是一个基于 Spring Boot 3.5.9 的 REST API 服务（Java 21），旨在提供 AI 驱动的职业指导、职位匹配和用户管理。系统集成了多个外部服务，包括支付宝支付、阿里云 OSS 存储、AI 服务和 RabbitMQ 消息队列。

## 架构与关键数据流

### 核心组件
- **控制器层** (`controller/`): REST 端点，处理 HTTP 请求，统一响应格式
- **服务层** (`service/impl/`): 业务逻辑编排，事务边界管理
- **映射层** (`mapper/`): MyBatis-Plus BaseMapper 接口，数据库操作
- **域层** (`domain/`): PO（实体）、DTO（输入）、VO（输出）类型安全数据流
- **工具层** (`util/`): JWT 令牌、Redis 缓存、密码加密、文件上传、邮件发送

### 关键数据流

**用户认证流程**:
1. `UserController.login()` → `UserService.login()` → `UserMapper.selectByEmail()`
2. 成功: JWT 令牌（访问令牌+刷新令牌）存储在 `Result` 响应中 + 用户数据存储在 Redis
3. 令牌验证: `LoginInterceptor` 从请求头提取 JWT，通过 `JwtUtil.parseToken()` 验证，将用户 ID 存储在 `ThreadLocalUtil`

**AI 集成流程**:
1. 控制器（`ChatController`、`QuestionController`）→ `AiServiceClient`（基于 WebFlux 的 HTTP 客户端）
2. 支持流式响应（Flux）和通过 `AliOSSMultipartFileUtil` 上传文件
3. 示例: `/resume-upload-chat` 接受多部分文件，上传到阿里云 OSS，传递给 Python AI 服务

**支付流程**:
1. `PayController.orderNoPay()` → `PayService` → 创建 `PaymentOrder` → 重定向到支付宝收银台
2. 支付宝回调: `PayController.returns()` → 验证签名 → 更新订单状态
3. 通过 `PayService` 在 `PointsTransaction` 表中记录交易日志

**消息队列模式** (RabbitMQ):
- 错误恢复: `ErrorConfiguration` 配置死信交换机处理失败消息
- Jackson 消息转换器在 `CareerPlanningBackendApplication` bean 中配置
- 消费者重试: `application.yaml` 设置 `listener.simple.retry.enabled: true` 带指数退避

## 规范与模式

### 响应格式（通用标准）
所有端点返回 `Result<T>` 包装器：
```java
// 成功: code=200, msg=null, data=<数据>
Result.ok(data)
Result.ok()
Result.ok("message", dataList)

// 失败: code=401（或自定义）, msg=<错误>, data=null
Result.fail("error message")
Result.fail(404, "Not found")
```
异常处理: `GlobalExceptionHandler` 捕获所有异常，返回状态码为 401/500 的 `Result.fail()`。

### 数据库层规范
- **映射器**: 继承 MyBatis-Plus 的 `BaseMapper<Entity>`
- **自定义查询**: 在映射器 XML 文件或 `@Mapper` 接口方法中定义（例如 `UserMapper.selectByEmail()`）
- **ID 生成**: 雪花算法（由 MyBatis-Plus 自动生成）
- **事务**: 在修改数据的服务方法上使用 `@Transactional`（添加、更新、删除）
- **分页**: 使用 `IPage<T>` 进行列表查询

### 实体命名与分层
- **PO（持久化对象）**: `domain/po/*.java` - 直接数据库映射，使用 `@TableName`、`@TableId` 注解
- **DTO（数据传输对象）**: `domain/dto/*.java` - 请求/响应数据，使用 `@Valid` 验证注解
- **VO（视图对象）**: `domain/vo/*.java` - 前端响应对象（例如 `LoginVO` 排除敏感字段）

### 身份验证与授权
- 令牌存储: JWT 验证成功后，用户 ID 存储在 `ThreadLocalUtil`
- 当前用户访问: `ThreadLocalUtil.getCurrentUserId()` - 未登录时抛出 RuntimeException
- `WebConfig.addInterceptors()` 中的排除端点: `/user/login`, `/user/register`, `/user/send-code-*`, `/alipay/pay/*`

### 配置管理
- **环境变量**: 数据库、Redis、邮件、支付宝凭证存储在 `application-prod.yaml`
- **配置文件切换**: `application.yaml` 设置 `spring.profiles.active: prod`（待改进：为不同环境切换）
- **外部服务**:
  - 阿里云 OpenAI（通义千问）: base-url、api-key、model 在 `application-prod.yaml`
  - 支付宝 SDK: 在 `PayController` 中初始化
  - 阿里云 OSS: `AliOSSProperties` bean 配置

## 开发者工作流

### 构建与运行
```bash
# 清理构建（编译、运行测试、打包）
mvn clean package

# 使用 Spring Boot Maven 插件运行
mvn spring-boot:run

# 或直接运行 JAR
java -jar target/career-planning-backend-0.0.1-SNAPSHOT.jar
```

### 测试模式
- 测试文件在 `src/test/java/` - 示例: `careerplanningbackend.java`、`ces.java`
- 集成测试使用 `@SpringBootTest`
- 通过 `@Autowired` 在测试中注入依赖

### 数据库设置
1. 执行 SQL 初始化脚本（如 `package_init.sql`）创建表
2. 凭证从环境变量加载: `database_username`、`database_password`、`database_name`
3. 架构详情在 `BACKEND_DOC.md` 和 `PACKAGE_IMPLEMENTATION.md`

### 调试与日志
- **日志配置**: `logback.xml`（生产）、`logback-study.xml`、`logback-temp.xml`
- **事务调试**: SLF4J 日志级别 `org.springframework.jdbc.support.JdbcTransactionManager: debug`（在 `application.yaml` 中配置）
- **AI 服务调试**: `org.springframework.ai: debug` 级别
- **日志输出**: `logs/career-planning-backend.log` 和 `logs/career-planning-backend-error.log`

### 新增功能步骤模式
1. **定义实体**: 在 `domain/po/` 创建 `PO`，使用 MyBatis-Plus 注解
2. **创建映射器**: 在 `mapper/` 中继承 `BaseMapper<Entity>`（自动 CRUD）
3. **定义 DTO/VO**: 在 `domain/` 中创建输入验证 DTO + 响应 VO
4. **编写服务**: 接口 + 实现，使用 `@Transactional`，注入映射器
5. **创建控制器**: `@RestController`、`@RequestMapping`，返回 `Result<T>`
6. **注册映射器**: 已通过应用启动时的 `@MapperScan("com.backend.careerplanningbackend.mapper")` 自动扫描
7. **测试**: 创建测试类，注入服务，通过 API 调用验证

## 项目特定依赖

### 关键库
- **Spring Boot 3.5.9**: Web、AMQP、Mail、Data Redis、WebFlux、Validation
- **MyBatis-Plus 3.5.15**: ORM 与 BaseMapper、自动 CRUD、雪花 ID
- **MySQL 9.6.0**: JDBC 驱动（JDK 21 兼容）
- **JWT (jjwt 0.13.0)**: 使用 HMAC-SHA 的令牌创建/解析
- **阿里云 SDK**: OSS (3.18.5) 用于文件上传、OpenAI API 集成
- **Hutool 5.8.40**: 工具函数（StringUtil、DateUtil 等）
- **Lombok 1.18.34**: `@Data`、`@RequiredArgsConstructor`、`@Slf4j` 注解
- **支付宝 SDK 4.9.28**: 支付集成
- **POI-tl 1.12.2**: Word 文档导出模板
- **OpenHTMLToPDF 1.0.10**: HTML 转 PDF 生成
- **RabbitMQ (AMQP)**: 消息队列与发布者确认、消费者重试

### 工具类（可复用模式）
- `ThreadLocalUtil`: 存储/检索每个请求的用户 ID
- `JwtUtil`: 创建访问/刷新令牌（30 分钟 / 7 天过期），解析和验证
- `MailUtil`: 通过 JavaMail 发送验证码
- `AliOSSUtils`: 上传文件到阿里云对象存储
- `PwdUtil`: Bcrypt 密码哈希
- `VerificationCode`: 生成随机验证码
- `RedisIdWorker`: 雪花 ID 生成
- `AiServiceClient`: 用于 Python AI 服务调用的 WebFlux HTTP 客户端

## 集成点

### 外部服务
1. **支付宝**: `PayController` 中的 REST API、XML 解析器响应（Jackson XML 支持）
2. **阿里云 OSS**: 通过 `AliOSSUtils` 上传文件，凭证在属性中
3. **Python AI 服务**: `AiServiceClient` 中基于 WebFlux 的异步客户端
4. **Redis**: 会话缓存、验证码存储（键在 `RedisConstant` 中）
5. **RabbitMQ**: 异步消息处理与死信队列回退
6. **MySQL 数据库**: 带连接池的事务操作

### 跨组件通信
- 控制器调用服务，服务查询映射器
- 服务可能发出 RabbitMQ 消息进行异步任务
- `ThreadLocalUtil` 连接拦截器 → 控制器层用于认证状态
- `Result<T>` 确保所有端点的一致 API 契约

## 代码质量与标准
- **注解**: 使用 `@Slf4j` 记录日志、`@RequiredArgsConstructor` 进行依赖注入、`@Valid` 进行验证
- **命名**: 控制器以 `Controller` 结尾、服务以 `Service` 结尾、映射器以 `Mapper` 结尾
- **事务处理**: 修改数据的服务方法标记 `@Transactional` 以保证 ACID 特性
- **错误处理**: 在服务中捕获异常，包装在 `Result.fail()`，通过 SLF4J 记录日志
- **文件结构**: 按角色严格组织（controller/service/mapper/domain/util/config/exception）

## 故障排除提示
- **令牌过期?** 检查 `JwtUtil` 过期时间；刷新令牌有 7 天窗口
- **数据库连接失败?** 验证 `application-prod.yaml` 中的凭证和 database_* 环境变量
- **RabbitMQ 死信消息?** 检查 `ErrorConfiguration` 队列，检查 `error.queue` 中失败的任务
- **文件上传失败?** 验证 `AliOSSProperties` 中的阿里云 OSS 凭证，检查 `application.yaml` 中的 10MB 请求大小限制
- **AI 服务调用超时?** `AiServiceClient` 中的 WebFlux 重试逻辑，检查 base-url 处的 Python 服务健康状态

