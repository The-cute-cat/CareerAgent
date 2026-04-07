# 对话 API 使用文档

基于 Java 端 `AiServiceClient.java` 实现的对话接口。

## API 端点总览

| 端点 | 方法 | 说明 | 对应 Java 方法 |
|------|------|------|---------------|
| `/chat/message` | POST | 纯文本消息对话（阻塞） | `chatWithMessage` |
| `/chat/message/stream` | POST | 纯文本消息对话（流式） | `chatWithMessageStream` |
| `/chat/files` | POST | 文件上传对话（阻塞） | `chatWithFiles` |
| `/chat/message-and-files` | POST | 消息+文件对话（阻塞） | `chatWithMessageAndFiles` |
| `/chat/message-and-files/stream` | POST | 消息+文件对话（流式） | `chatWithMessageAndFilesStream` |
| `/chat/history/{session_id}` | GET | 获取会话历史 | - |
| `/chat/session/{session_id}` | DELETE | 清除会话记忆 | - |

---

## 1. 纯文本消息对话（阻塞方式）

### 请求

```http
POST /chat/message
Content-Type: multipart/form-data
```

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| message | string | 是 | 消息内容 |
| conversationId | string | 否 | 对话 ID（不提供则使用默认值） |
| auto_extract_memory | boolean | 否 | 是否自动提取记忆（默认 true） |

### 示例

**请求：**
```bash
curl -X POST "http://localhost:8000/chat/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "message=你好，我是Python开发者" \
  -F "conversationId=session_001"
```

**响应：**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "message": "你好！很高兴认识你...",
    "conversationId": "session_001"
  }
}
```

---

## 2. 纯文本消息对话（流式方式）

### 请求

```http
POST /chat/message/stream
Content-Type: multipart/form-data
```

### 参数

同上

### 示例

**JavaScript (EventSource):**
```javascript
const formData = new FormData();
formData.append('message', '介绍一下AI工程师的发展路径');
formData.append('conversationId', 'session_001');

fetch('http://localhost:8000/chat/message/stream', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: formData
}).then(response => {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  function read() {
    reader.read().then(({ done, value }) => {
      if (done) return;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      lines.forEach(line => {
        if (line.startsWith('data: ')) {
          const data = line.substring(6);
          if (data === '[DONE]') {
            console.log('Stream finished');
          } else if (data.startsWith('[ERROR]')) {
            console.error('Error:', data);
          } else {
            console.log('Received:', data);
          }
        }
      });
      
      read();
    });
  }
  
  read();
});
```

**响应格式（SSE）：**
```
data: 你好！

data: 我是

data: AI助手

data: [DONE]
```

---

## 3. 文件上传对话（阻塞方式）

### 请求

```http
POST /chat/files
Content-Type: multipart/form-data
```

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| files | file[] | 是 | 文件列表 |
| conversationId | string | 否 | 对话 ID |

### 示例

```bash
curl -X POST "http://localhost:8000/chat/files" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document.pdf" \
  -F "files=@image.png" \
  -F "conversationId=session_002"
```

**响应：**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "message": "成功上传 2 个文件",
    "conversationId": "session_002",
    "files": [
      {
        "filename": "document.pdf",
        "content_type": "application/pdf",
        "size": 12345
      },
      {
        "filename": "image.png",
        "content_type": "image/png",
        "size": 67890
      }
    ]
  }
}
```

---

## 4. 消息和文件同时上传对话（阻塞方式）

### 请求

```http
POST /chat/message-and-files
Content-Type: multipart/form-data
```

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| message | string | 是 | 消息内容 |
| files | file[] | 否 | 文件列表（可空） |
| conversationId | string | 否 | 对话 ID |

### 示例

```bash
curl -X POST "http://localhost:8000/chat/message-and-files" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "message=请帮我分析这个简历" \
  -F "files=@resume.pdf" \
  -F "conversationId=session_003"
```

---

## 5. 消息和文件同时上传对话（流式方式）

### 请求

```http
POST /chat/message-and-files/stream
Content-Type: multipart/form-data
```

### 参数

同上

### 示例

参考纯文本流式对话的 JavaScript 示例。

---

## 6. 获取会话历史记录

### 请求

```http
GET /chat/history/{session_id}
```

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | path | 是 | 会话 ID |
| limit | query | 否 | 限制返回数量 |

### 示例

```bash
curl -X GET "http://localhost:8000/chat/history/session_001?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "sessionId": "session_001",
    "history": [
      {
        "role": "user",
        "content": "你好，我是Python开发者",
        "timestamp": "2026-01-15T10:30:00"
      },
      {
        "role": "assistant",
        "content": "你好！很高兴认识你...",
        "timestamp": "2026-01-15T10:30:01"
      }
    ],
    "count": 2
  }
}
```

---

## 7. 清除会话记忆

### 请求

```http
DELETE /chat/session/{session_id}
```

### 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | path | 是 | 会话 ID |

### 示例

```bash
curl -X DELETE "http://localhost:8000/chat/session/session_001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "message": "会话 session_001 已清除"
  }
}
```

---

## 认证

所有接口都需要在请求头中携带 Authorization token：

```http
Authorization: Bearer YOUR_TOKEN
```

Token 通过 `validate_token` 依赖项进行验证。

---

## 错误处理

所有错误响应遵循统一格式：

```json
{
  "code": 500,
  "state": false,
  "msg": "错误描述",
  "data": null
}
```

常见错误码：
- `400` - 请求参数错误
- `401` - 认证失败
- `403` - 权限不足
- `500` - 服务器内部错误

---

## 特性说明

### 1. 自动记忆提取

- 默认启用（`auto_extract_memory=true`）
- 在后台异步提取，不阻塞响应
- 提取的记忆点存储到长期记忆（MySQL + ChromaDB）
- 自动去重和容量管理（最多50条）

### 2. 流式响应

- 使用 Server-Sent Events (SSE) 协议
- 实时返回 AI 响应片段
- 支持客户端断开检测
- 自动发送结束标记 `[DONE]`

### 3. 会话管理

- 使用 Redis 存储短期记忆（最近20条消息）
- 自动压缩过长对话
- 支持跨请求保持会话上下文

---

## 与 Java 端对应关系

| Python 接口 | Java 方法 | 功能 |
|-------------|-----------|------|
| `POST /chat/message` | `chatWithMessage()` | 纯文本对话（阻塞） |
| `POST /chat/message/stream` | `chatWithMessageStream()` | 纯文本对话（流式） |
| `POST /chat/files` | `chatWithFiles()` | 文件上传对话（阻塞） |
| `POST /chat/message-and-files` | `chatWithMessageAndFiles()` | 消息+文件对话（阻塞） |
| `POST /chat/message-and-files/stream` | `chatWithMessageAndFilesStream()` | 消息+文件对话（流式） |

---

## 测试

使用 `test_chat.http` 文件进行接口测试（VS Code REST Client 插件）。

或运行 FastAPI 自动文档：
```bash
python main.py
```
访问：http://localhost:8000/docs
