# 职业规划后端系统技术文档

## 项目概述

**项目名称**: career-planning-backend  
**项目类型**: Spring Boot REST API 后端服务  
**Java 版本**: 21  
**框架版本**: Spring Boot 3.5.9

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Spring Boot | 3.5.9 | Web 框架 |
| MyBatis-Plus | 3.5.15 | ORM 持久层框架 |
| MySQL | 9.6.0 | 关系型数据库 |
| Redis | - | 缓存数据库（验证码存储） |
| JWT | 0.11.5 | Token 认证 |
| Hutool | 5.8.40 | Java 工具包 |
| Aliyun OSS | 3.18.5 | 云存储（头像上传） |
| JavaMail | - | 邮件服务 |
| Lombok | 1.18.34 | 代码简化 |

## 项目结构

```
src/
├── main/
│   ├── java/com/backend/careerplanningbackend/
│   │   ├── CareerPlanningBackendApplication.java    # 启动类
│   │   ├── config/                                  # 配置类
│   │   │   ├── LoginInterceptor.java                # 登录拦截器
│   │   │   └── WebConfig.java                       # Web配置
│   │   ├── controller/                              # 控制器
│   │   │   └── UserController.java                  # 用户接口
│   │   ├── service/                                # 业务层
│   │   │   ├── UserService.java                     # 用户服务接口
│   │   │   └── impl/UserServiceImpl.java            # 用户服务实现
│   │   ├── mapper/                                  # 数据访问层
│   │   │   └── UserMapper.java                      # 用户Mapper
│   │   ├── domain/                                  # 域对象
│   │   │   ├── po/                                  # 实体类
│   │   │   │   ├── Result.java                      # 统一响应结果
│   │   │   │   ├── User.java                        # 用户实体
│   │   │   │   └── UserAuth.java                    # 用户认证实体
│   │   │   ├── dto/                                 # 数据传输对象
│   │   │   │   └── LoginFormDTO.java                # 登录表单DTO
│   │   │   └── vo/                                  # 视图对象
│   │   │       └── LoginVO.java                     # 登录返回VO
│   │   └── util/                                    # 工具类
│   │       ├── JwtUtil.java                         # JWT工具
│   │       ├── AITokenUtil.java                     # AI Token工具
│   │       ├── AliOSSUtils.java                      # 阿里云OSS上传
│   │       ├── PwdUtil.java                         # 密码加密工具
│   │       ├── VerificationCode.java                # 验证码生成
│   │       ├── RegexUtil.java                       # 正则校验工具
│   │       └── ThreadLocalUtil.java                  # 线程本地变量
│   └── resources/
│       └── application.yaml                         # 配置文件
└── test/                                            # 测试
```

## 核心功能模块

### 1. 用户认证模块

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 登录 | POST | `/user/login` | 用户登录 |
| 注册 | POST | `/user/register` | 用户注册 |
| 忘记密码 | PUT | `/user/forget-password` | 密码重置 |
| 发送注册验证码 | POST | `/user/send-code-register` | 注册邮箱验证码 |
| 发送忘记密码验证码 | POST | `/user/send-code-forget` | 忘记密码验证码 |
| 刷新Token | POST | `/user/refreshToken` | 刷新访问令牌 |

### 2. 用户信息模块

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取用户信息 | GET | `/user/info` | 获取当前用户信息 |
| 修改个人信息 | PUT | `/user/edit` | 更新用户资料 |
| 更换头像 | GET | `/user/avatar` | 上传头像到OSS |

## 统一响应格式

```java
// 成功响应
{
    "code": 200,
    "msg": null,
    "data": { ... }
}

// 失败响应
{
    "code": 401,
    "msg": "错误信息",
    "data": null
}
```

### Result 类方法

```java
Result.ok()                    // 无数据成功响应
Result.ok(data)                // 带数据成功响应
Result.ok(List<?> data)        // 列表数据成功响应
Result.fail("错误信息")         // 失败响应
Result.fail(401, "错误信息")    // 带状态码的失败响应
```

## 认证机制

### JWT Token

- **AccessToken**: 短期令牌，有效期 30 分钟
- **RefreshToken**: 长期令牌，用于刷新 AccessToken
- **Secret**: 通过环境变量 `${<SECRET>}` 配置

### 认证流程

1. 用户登录 -> 生成 AccessToken + RefreshToken
2. 每次请求携带 AccessToken（在 Header 或参数中）
3. AccessToken 过期时，使用 RefreshToken 刷新

## 数据模型

### User 实体

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 主键ID |
| username | String | 用户名（登录账号） |
| password | String | 加密后的密码 |
| nickname | String | 昵称 |
| email | String | 邮箱 |
| avatar | String | 头像URL |
| status | Integer | 账号状态（1正常/0禁用） |
| createTime | LocalDateTime | 创建时间 |
| updateTime | LocalDateTime | 更新时间 |

### LoginFormDTO

| 字段 | 类型 | 说明 |
|------|------|------|
| username | String | 用户名 |
| password | String | 密码 |
| passwordConfirm | String | 确认密码 |
| email | String | 邮箱 |
| code | String | 验证码 |

### LoginVO

| 字段 | 类型 | 说明 |
|------|------|------|
| accessToken | String | 访问令牌 |
| refreshToken | String | 刷新令牌 |
| user | UserDTO | 用户信息 |

## 配置文件说明

### application.yaml 核心配置

```yaml
server:
  port: 8080                    # 服务端口

spring:
  datasource:                   # MySQL 数据源
    url: jdbc:mysql://host:port/dbname
    username: username
    password: password
  
  data:
    redis:                      # Redis 配置
      host: redis_host
      port: 6379
      username: username
      password: password
  
  mail:                         # 邮件配置
    host: smtp.xx.com
    username: xxx@xx.com
    password: xxx
  
  servlet:
    multipart:
      max-file-size: 10MB       # 单文件大小限制
      max-request-size: 100MB  # 请求大小限制

aliyun:
  oss:                          # 阿里云OSS配置
    endpoint: xxx
    access-key-id: xxx
    access-key-secret: xxx
    bucket-name: xxx

communication:
  token:
    secret: ${<SECRET>}        # JWT密钥
    expire: 1800                # Token过期时间(秒)

mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true  # 下划线转驼峰
```

### 环境变量

| 变量名               | 说明         |
|-------------------|------------|
| host              | MySQL 主机地址 |
| post              | MySQL 端口   |
| database_name     | 数据库名称      |
| database_username | 数据库用户名     |
| database_password | 数据库密码      |
| redis_host        | Redis 主机地址 |
| redis_post        | Redis 端口   |
| redis_username    | Redis 用户名  |
| redis_password    | Redis 密码   |
| email_host        | 邮件服务器地址    |
| email_post        | 邮件服务器端口    |
| MAIL_USERNAME_QQ  | QQ邮箱账号     |
| MAIL_PASSWORD_QQ  | QQ邮箱授权码    |
| ALY_OSS_*         | 阿里云OSS配置   |
| SECRET            | JWT 密钥     |

## 扩展说明

### Python AI 服务转接

项目预留了与 Python AI 服务对接的接口，可通过以下方式实现：

1. 创建 `PythonApiClient` HTTP 客户端类
2. 在 Service 层注入并调用 Python API
3. 统一处理请求/响应格式转换

详见 `PythonApiClient.java` 模板文件。

### 支付功能

已集成支付宝支付相关配置（app-id, private-key, public-key 等），可扩展支付功能。

## 启动说明

```bash
# 打包项目
mvn clean package -DskipTests

# 运行项目
java -jar career-planning-backend-0.0.1-SNAPSHOT.jar
```

## 注意事项

1. 所有密码使用 BCrypt 加密存储
2. 验证码存储在 Redis 中，有效期 5 分钟
3. 同一邮箱/用户名 60 秒内只能发送一次验证码
4. 防止账号枚举攻击：登录失败返回统一错误信息
