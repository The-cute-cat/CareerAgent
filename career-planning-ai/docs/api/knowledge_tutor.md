# 知识导师 API 使用文档

> 定位: 知识图谱节点讲解接口
> 更新时间: 2026-04-16

---

## 一、API 端点总览

| 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|
| POST | `/knowledge_tutor/analyze/stream` | 流式分析知识点对岗位的影响 | SSE |
| POST | `/knowledge_tutor/explain/stream` | 流式解释知识点内容 | SSE |

> 所有接口均需认证: `Authorization: Bearer <token>`

---

## 二、通用参数说明

### 认证方式

```
Authorization: Bearer <token>
```

### 统一响应格式

**SSE 响应格式（标准 SSE 格式）:**
```
event: content
data: {"type":"content","text":"..."}
id: 1

event: done
data: {"status":"completed"}
id: 2
```

### SSE 事件说明

| event 类型 | data 格式 | 含义 |
|-----------|----------|------|
| `content` | `{"type":"content","text":"..."}` | 文本片段 |
| `done` | `{"status":"completed"}` | 流传输结束 |
| `error` | `{"error":"..."}` | 发生错误 |

---

## 三、接口详情

### 3.1 流式分析知识点对岗位的影响（SSE）

```http
POST /knowledge_tutor/analyze/stream
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**用途:** 用于"岗位影响"标签页，分析当前知识点对目标岗位的影响。

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| current_node | string | **是** | — | 当前知识点名称 |
| job_id | int | **是** | — | 目标岗位 ID |
| user_id | int | **是** | — | 用户 ID |
| graph_context | string | 否 | "" | 图谱关系（前置/后续/关联节点） |
| industry_data | string | 否 | "" | 行业数据（可选） |

**SSE 响应示例:**
```
event: content
data: {"type":"content","text":"该知识点在后端开发岗位中具有重要作用..."}
id: 1

event: content
data: {"type":"content","text":"掌握这个知识点可以帮助你更好地理解微服务架构..."}
id: 2

event: done
data: {"status":"completed"}
id: 3
```

**示例:**
```bash
curl -X POST "http://localhost:9000/knowledge_tutor/analyze/stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "current_node=Docker容器化" \
  -F "job_id=123" \
  -F "user_id=1001" \
  -F "graph_context=前置: Linux基础; 后续: Kubernetes"
```

---

### 3.2 流式解释知识点内容（SSE）

```http
POST /knowledge_tutor/explain/stream
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**用途:** 用于"知识精讲"标签页，详细解释知识点内容。

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| current_node | string | **是** | — | 当前知识点名称 |
| job_id | int | **是** | — | 目标岗位 ID |
| user_id | int | **是** | — | 用户 ID |
| graph_context | string | 否 | "" | 图谱关系（前置/后续/关联节点） |

**SSE 响应示例:**
```
event: content
data: {"type":"content","text":"Docker 是一个开源的容器化平台..."}
id: 1

event: content
data: {"type":"content","text":"它允许开发者将应用程序及其依赖打包到一个轻量级..."}
id: 2

event: done
data: {"status":"completed"}
id: 3
```

**示例:**
```bash
curl -X POST "http://localhost:9000/knowledge_tutor/explain/stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "current_node=Docker容器化" \
  -F "job_id=123" \
  -F "user_id=1001" \
  -F "graph_context=前置: Linux基础; 后续: Kubernetes"
```

---

## 四、内部处理流程

### 用户画像获取

接口内部会自动根据 `job_id` 和 `user_id` 调用 `get_profile_text()` 获取：

1. **岗位画像文本**: 基于岗位 ID 从数据库查询岗位要求
2. **用户画像文本**: 基于用户 ID 从数据库查询用户信息

### Agent 处理

两个接口分别调用 `knowledge_tutor_agent` 的不同方法：

| 接口 | Agent 方法 | 用途 |
|------|-----------|------|
| `/analyze/stream` | `analyze_knowledge_stream()` | 分析知识点对岗位的影响 |
| `/explain/stream` | `explain_knowledge_stream()` | 解释知识点内容 |

---

## 五、Java 调用示例

### 分析知识点对岗位的影响（流式）

```java
@Autowired
private AiServiceClient aiServiceClient;

// 构建请求参数
Map<String, Object> params = new HashMap<>();
params.put("current_node", "Docker容器化");
params.put("job_id", 123);
params.put("user_id", 1001L);
params.put("graph_context", "前置: Linux基础; 后续: Kubernetes");

// 调用流式接口
Flux<String> stream = aiServiceClient.chatWithOtherStream(
    "/knowledge_tutor/analyze/stream",
    params
);

// 订阅处理 SSE 流
stream.subscribe(event -> {
    if (event.startsWith("event: content")) {
        // 处理内容片段
    } else if (event.startsWith("event: done")) {
        // 流结束
    } else if (event.startsWith("event: error")) {
        // 错误处理
    }
});
```

### 解释知识点内容（流式）

```java
// 构建请求参数
Map<String, Object> params = new HashMap<>();
params.put("current_node", "Docker容器化");
params.put("job_id", 123);
params.put("user_id", 1001L);
params.put("graph_context", "前置: Linux基础");

// 调用流式接口
Flux<String> stream = aiServiceClient.chatWithOtherStream(
    "/knowledge_tutor/explain/stream",
    params
);

// 订阅处理 SSE 流
stream.subscribe(this::handleSseEvent);
```

---

## 六、注意事项

1. **流式响应**: 所有接口均为 SSE 流式响应，客户端需要支持 SSE 协议
2. **断连处理**: 客户端断开连接时，服务端会自动停止流式传输
3. **图谱上下文**: `graph_context` 参数可以提供知识点的前置/后续/关联关系，帮助 AI 生成更精准的内容
4. **画像自动获取**: 用户画像和岗位画像是自动从数据库查询的，无需前端传递
5. **两个标签页**: 分析和解释分别用于两个不同的标签页，内容侧重点不同
