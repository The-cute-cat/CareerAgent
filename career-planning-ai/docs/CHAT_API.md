# 对话 API 使用文档

> 定位: 右下角小助手窗口，Java 服务端调用 Python AI 服务
> 更新时间: 2026-04-09

---

## 一、API 端点总览

| 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|
| POST | `/chat/message` | 纯文本对话 | 阻塞 |
| POST | `/chat/message/stream` | 纯文本流式对话 | SSE |
| POST | `/chat/files` | 仅文件上传对话 | 阻塞 |
| POST | `/chat/message-and-files` | 消息+文件对话 | 阻塞 |
| POST | `/chat/message-and-files/stream` | 消息+文件流式对话 | SSE |
| GET | `/chat/history/{session_id}` | 获取会话历史记录 | — |
| GET | `/chat/sessions` | 获取用户的会话列表 | — |
| PUT | `/chat/session/{session_id}/title` | 更新会话标题 | — |
| DELETE | `/chat/session/{session_id}` | 删除会话（含短期记忆） | — |
| GET | `/chat/memories` | 获取长期记忆列表 | — |
| DELETE | `/chat/memory/{memory_id}` | 删除单条长期记忆（需 user_id） | — |

> 所有接口均需认证: `Authorization: Bearer <token>`
> 所有接口均需要传入 `user_id` 参数

---

## 二、通用参数说明

### 认证方式

```
Authorization: Bearer <token>
```

Token 由 Java 服务端生成并传入，Python 端通过 `validate_token` 依赖项校验：
- 解析 token 提取 `user_id`
- 测试环境支持 `test123` 令牌（仅 debug 模式生效）

### 公共参数

| 参数名 | 类型 | 位置 | 必填 | 说明 |
|--------|------|------|------|------|
| user_id | string | Form / Query | **是** | 用户 ID，用于数据隔离和权限校验 |
| conversation_id | string | Form | 否 | 会话 ID，不传则使用 `"default_session"` |
| auto_extract_memory | boolean | Form | 否 | 是否自动提取长期记忆，默认 `true`（文件类接口默认 `false`） |
| show_thinking | boolean | Form | 否 | 是否显示思考过程，默认 `false`（仅流式接口支持） |

### 统一响应格式（非 SSE 接口）

**成功:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": { ... }
}
```

**失败:**
```json
{
  "code": <错误码>,
  "state": false,
  "msg": "错误描述",
  "data": null
}
```

> 注意: HTTP status code 始终返回 200，业务状态通过 body 中 `code` 和 `state` 字段判断。

### 常见错误码

| code | 说明 |
|------|------|
| 401 | Token 无效或过期 |
| 403 | 权限不足（如删除他人记忆） |
| 404 | 资源不存在 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |

---

## 三、对话接口

### 3.1 纯文本对话（阻塞方式）

```http
POST /chat/message
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数（Form）:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| message | string | 是 | — | 消息内容 |
| user_id | string | 是 | — | 用户 ID |
| conversation_id | string | 否 | null | 对话 ID，不传使用默认会话 |
| auto_extract_memory | boolean | 否 | true | 是否自动提取记忆 |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "message": "AI 的完整回复文本",
    "conversationId": "session_001"
  }
}
```

**示例:**
```bash
curl -X POST "http://localhost:8000/chat/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "message=你好，我想了解一下职业规划" \
  -F "user_id=user_001" \
  -F "conversation_id=session_001"
```

---

### 3.2 纯文本对话（流式方式 - SSE）

```http
POST /chat/message/stream
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数（Form）:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| message | string | 是 | — | 消息内容 |
| user_id | string | 是 | — | 用户 ID |
| conversation_id | string | 否 | null | 对话 ID |
| auto_extract_memory | boolean | 否 | true | 是否自动提取记忆 |
| show_thinking | boolean | 否 | false | 是否显示思考过程 |

**SSE 响应格式（标准 SSE 格式）:**
```
event: content
data: {"type":"content","text":"你好"}
id: 1

event: content
data: {"type":"content","text":"，我是你的职业规划助手"}
id: 2

event: done
data: {"status":"completed"}
id: 3
```

**SSE 事件说明:**

| event 类型 | data 格式 | 含义 |
|-----------|----------|------|
| `content` | `{"type":"content","text":"..."}` | AI 回复的文本片段 |
| `thinking` | `{"type":"thinking","text":"..."}` | AI 思考过程（仅当 `show_thinking=true` 时返回） |
| `done` | `{"status":"completed"}` | 流传输结束标记 |
| `error` | `{"error":"..."}` | 流传输过程中发生错误 |

> **错误处理:** 流式传输中途失败时，已写入的用户消息会自动回滚，不会产生"孤儿"消息导致后续上下文混乱。

**Java 调用方式:**
```java
// 阻塞方式
aiServiceClient.chatWithMessage("/chat/message", userId, message, conversationId, true);

// 流式方式
Flux<String> stream = aiServiceClient.chatWithMessageStream("/chat/message/stream", userId, message, conversationId);
stream.subscribe(chunk -> {
    // 处理每个 SSE 文本片段（JSON 格式）
});
```

---

### 3.3 仅文件上传对话（阻塞方式）

```http
POST /chat/files
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数（Form）:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| files | file[] | 是 | — | 文件列表 |
| user_id | string | 是 | — | 用户 ID |
| conversation_id | string | 否 | null | 对话 ID |
| auto_extract_memory | boolean | 否 | **false** | 是否自动提取记忆（默认关闭） |

**支持的文件类型:** PDF、DOCX、PNG、JPG、JPEG（基于魔数检测真实类型）

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "message": "AI 对文件分析后的回复",
    "conversationId": "session_001",
    "fileCount": 1
  }
}
```

**示例:**
```bash
curl -X POST "http://localhost:8000/chat/files" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@resume.pdf" \
  -F "user_id=user_001"
```

---

### 3.4 消息 + 文件对话（阻塞方式）

```http
POST /chat/message-and-files
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数（Form）:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| message | string | 是 | 消息内容 |
| files | file[] | 是 | 文件列表 |
| user_id | string | 是 | 用户 ID |
| conversation_id | string | 否 | 对话 ID |
| auto_extract_memory | boolean | 否 | 是否自动提取记忆，默认 `false` |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "message": "AI 回复",
    "conversationId": "session_001",
    "fileCount": 2
  }
}
```

**Java 调用方式:**
```java
// File 列表
AiChatResponse resp = aiServiceClient.chatWithMessageAndFiles(
    "/chat/message-and-files", userId, message, files, conversationId, true);

// MultipartFile（前端直接上传）
AiChatResponse resp = aiServiceClient.chatWithMessageAndMultipartFiles(
    "/chat/message-and-files", userId, message, multipartFiles, conversationId, true);
```

---

### 3.5 消息 + 文件流式对话（SSE）

```http
POST /chat/message-and-files/stream
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数（Form）:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| message | string | 是 | — | 消息内容 |
| files | file[] | 是 | — | 文件列表 |
| user_id | string | 是 | — | 用户 ID |
| conversation_id | string | 否 | — | 对话 ID |
| auto_extract_memory | boolean | 否 | true | 是否自动提取记忆 |
| show_thinking | boolean | 否 | false | 是否显示思考过程 |

**SSE 响应格式:** 同 3.2

**Java 调用方式:**
```java
Flux<String> stream = aiServiceClient.chatWithMessageAndFilesStream(
    "/chat/message-and-files/stream", userId, message, files, conversationId);
```

---

## 四、会话管理

### 4.1 获取会话历史记录

```http
GET /chat/history/{session_id}?user_id={user_id}&limit={limit}
Authorization: Bearer <token>
```

**查询参数:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| user_id | string | **是** | — | 用户 ID |
| limit | int | 否 | 全部 | 返回的消息条数限制 |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "sessionId": "session_001",
    "userId": "user_001",
    "history": [
      { "role": "human", "content": "你好" },
      { "role": "ai", "content": "你好！有什么可以帮助你的？" }
    ],
    "count": 10
  }
}
```

**Java 调用方式（通用方法）:**
```java
Map<String, Object> params = Map.of("user_id", userId, "limit", 20);
AiChatResponse resp = aiServiceClient.getRequest("/chat/history/" + sessionId, params, "获取会话历史", false);
```

---

### 4.2 获取用户的会话列表

```http
GET /chat/sessions?user_id={user_id}&page={page}&page_size={page_size}
Authorization: Bearer <token>
```

**查询参数:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| user_id | string | **是** | — | 用户 ID |
| page | int | 否 | 1 | 页码（>= 1） |
| page_size | int | 否 | 20 | 每页数量（1 ~ 100） |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "total": 15,
    "items": [
      {
        "id": 1,
        "sessionId": "session_001",
        "userId": "user_001",
        "title": "职业规划咨询",
        "messageCount": 24,
        "createdAt": "2026-04-07T10:30:00",
        "updatedAt": "2026-04-07T11:00:00"
      }
    ],
    "page": 1,
    "page_size": 20
  }
}
```

**Java 调用方式（通用方法）:**
```java
Map<String, Object> params = new HashMap<>();
params.put("user_id", userId);
params.put("page", 1);
params.put("page_size", 20);
AiChatResponse resp = aiServiceClient.getRequest("/chat/sessions", params, "获取会话列表", false);
```

---

### 4.3 更新会话标题

```http
PUT /chat/session/{session_id}/title
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数（Form）:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | **是** | 用户 ID |
| title | string | **是** | 新的会话标题 |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": { "message": "会话标题已更新" }
}
```

**失败响应（404）:**
```json
{
  "code": 404,
  "state": false,
  "msg": "会话不存在",
  "data": null
}
```

**Java 调用方式（通用方法）:**
```java
Map<String, Object> params = Map.of("user_id", userId, "title", "新标题");
AiChatResponse resp = aiServiceClient.putRequest(
    "/chat/session/" + sessionId + "/title", params, "更新会话标题", false);
```

---

### 4.4 删除会话

```http
DELETE /chat/session/{session_id}?user_id={user_id}
Authorization: Bearer <token>
```

**查询参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | **是** | 用户 ID |

**行为:** 清除该会话在 Redis 中的短期记忆 + 软删除数据库中的持久化记录。**长期记忆不受影响。**

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": { "message": "会话 session_001 已清除" }
}
```

**Java 调用方式（通用方法）:**
```java
Map<String, Object> params = Map.of("user_id", userId);
AiChatResponse resp = aiServiceClient.deleteRequest(
    "/chat/session/" + sessionId, params, "清除会话", false);
```

---

## 五、长期记忆管理

### 5.1 获取记忆列表

```http
GET /chat/memories?user_id={user_id}&limit={limit}&min_score={min_score}
Authorization: Bearer <token>
```

**查询参数:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| user_id | string | **是** | — | 用户 ID |
| limit | int | 否 | 20 | 返回数量（1 ~ 100） |
| min_score | float | 否 | null | 最低分数过滤（0 ~ 1），不传不过滤 |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "userId": "user_001",
    "memories": [
      {
        "id": 42,
        "sessionId": "session_001",
        "content": "用户是 Python 开发者，有 3 年后端经验",
        "memoryType": "skill",
        "importanceScore": 0.85,
        "relevanceScore": 0.72,
        "recencyScore": 0.90,
        "uniquenessScore": 0.65,
        "totalScore": 0.78,
        "createdAt": "2026-04-07T10:30:00"
      }
    ],
    "count": 5
  }
}
```

**记忆字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 记忆主键 ID |
| sessionId | string | 来源会话 ID |
| content | string | 记忆内容摘要 |
| memoryType | string | 记忆类型（如 skill/preference/goal 等） |
| importanceScore | float | 重要性评分（0~1） |
| relevanceScore | float | 相关性评分（0~1） |
| recencyScore | float | 时效性评分（0~1） |
| uniquenessScore | float | 唯一性评分（0~1） |
| totalScore | float | 综合加权评分（0~1） |
| createdAt | string | 创建时间 ISO 格式 |

---

### 5.2 删除单条记忆

```http
DELETE /chat/memory/{memory_id}?user_id={user_id}
Authorization: Bearer <token>
```

**路径与查询参数:**

| 参数名 | 类型 | 位置 | 必填 | 说明 |
|--------|------|------|------|------|
| memory_id | int | path | **是** | 记忆 ID |
| user_id | string | query | **是** | 用户 ID（用于权限校验） |

**安全机制:** 只能删除属于当前 `user_id` 且状态为激活的记忆。越权操作（尝试删除他人记忆）返回 `code: 404`（不暴露存在性）。

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": { "message": "记忆 42 已删除" }
}
```

**失败响应:**
```json
// 记忆不属于当前用户 或 已被软删除
{ "code": 404, "state": false, "msg": "记忆不存在", "data": null }
```

**Java 调用方式（通用方法）:**
```java
Map<String, Object> params = Map.of("user_id", userId);
AiChatResponse resp = aiServiceClient.deleteRequest(
    "/chat/memory/" + memoryId, params, "删除记忆", false);
```

---

## 六、特性说明

### 6.1 双层记忆系统

| 层级 | 存储介质 | 容量 | 说明 |
|------|---------|------|------|
| **短期记忆** | Redis | 最近 20 条 | 当前会话上下文，Key 格式 `short_memory:{user_id}:{session_id}` |
| **长期记忆** | MySQL + ChromaDB | 最多 50 条/用户 | 跨会话持久化，后台异步提取，自动去重 |

### 6.2 自动记忆提取

- 每轮对话结束后异步执行，**不阻塞响应**
- 使用独立数据库连接，不影响主请求
- 提取结果存入 MySQL（结构化索引）+ ChromaDB（向量检索）
- 已存在的相似记忆自动去重（基于语义相似度）
- 可通过 `auto_extract_memory=false` 关闭（适用于纯文件解析场景）

### 6.3 文件处理流程

1. **安全检测**: 上传 → 基于魔数识别真实类型 → 防止文件伪装攻击
2. **临时存储**: 通过验证的文件存入临时目录（TTL 15 分钟）
3. **文本提取**: PDF/DOCX/图片 OCR → 纯文本
4. **AI 分析**: 拼接为消息发送给 LLM
5. **自动清理**: 后台任务定期清理过期临时文件

**支持格式:** PDF、DOCX、PNG、JPG、JPEG
**清理策略:** 由配置 `run_is_clean` 控制，默认关闭（可按环境开启）

### 6.4 数据隔离保障

| 维度 | 实现方式 |
|------|---------|
| 会话隔离 | SessionRepository 基于 `(user_id, session_id)` 联合查询 |
| Redis 隔离 | Key 包含 `user_id` 前缀，多用户互不影响 |
| 记忆校验 | 删除操作强制校验 `user_id` 所属权 |
| 流式回滚 | LLM 生成失败时自动移除已写入的用户消息 |

---

## 七、与 Java AiServiceClient 对应关系

### 专用方法（直接可用）

| Python 接口 | Java 方法 | 返回类型 |
|-------------|-----------|----------|
| `POST /chat/message` | `chatWithMessage(url, userId, msg, convId, retry)` | `AiChatResponse` |
| `POST /chat/message/stream` | `chatWithMessageStream(url, userId, msg, convId)` | `Flux<String>` |
| `POST /chat/files` | `chatWithFiles(url, userId, files, convId, retry)` | `AiChatResponse` |
| `POST /chat/files` | `chatWithMultipartFiles(url, userId, mFiles, convId, retry)` | `AiChatResponse` |
| `POST /chat/message-and-files` | `chatWithMessageAndFiles(url, userId, msg, files, convId, retry)` | `AiChatResponse` |
| `POST /chat/message-and-files` | `chatWithMessageAndMultipartFiles(url, userId, msg, mFiles, convId, retry)` | `AiChatResponse` |
| `POST /chat/message-and-files/stream` | `chatWithMessageAndFilesStream(url, userId, msg, files, convId)` | `Flux<String>` |
| `POST /chat/message-and-files/stream` | `chatWithMessageAndMultipartFilesStream(url, userId, msg, mFiles, convId)` | `Flux<String>` |

### 通用方法（需自行拼接参数）

| Python 接口 | Java 方法 | 注意事项 |
|-------------|-----------|----------|
| `GET /chat/history/{sid}` | `getRequest(url, params, name, retry)` | queryParam 含 `user_id`, `limit` |
| `GET /chat/sessions` | `getRequest(url, params, name, retry)` | queryParam 含 `user_id`, `page`, `page_size` |
| `PUT /chat/session/{sid}/title` | `putRequest(url, params, name, retry)` | form 含 `user_id`, `title` |
| `DELETE /chat/session/{sid}` | `deleteRequest(url, params, name, retry)` | params 含 `user_id` |
| `GET /chat/memories` | `getRequest(url, params, name, retry)` | queryParam 含 `user_id`, `limit`, `min_score` |
| `DELETE /chat/memory/{mid}` | `deleteRequest(url, params, name, retry)` | params 含 `user_id` |

---

## 八、测试

### FastAPI 自动文档

启动服务后访问:
```bash
python main.py
```
打开 http://localhost:9000/docs （Swagger UI）

### VS Code REST Client

使用插件打开项目根目录下的 `test_chat.http` 文件进行接口测试。

---

## 九、注意事项

1. **conversation_id 为空时** 会自动使用 `"default_session"` 作为默认会话 ID
2. **流式接口** 在客户端断连时会自动停止传输并释放资源
3. **文件大小限制** 由服务端配置和 Nginx 双重控制
4. **所有时间字段** 使用 ISO 8601 格式（如 `2026-04-07T10:30:00`）
5. **分页参数** `page` 从 1 开始，不是从 0
