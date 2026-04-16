# 代码能力评估 API 使用文档

> 定位: GitHub/Gitee 代码能力评估接口
> 更新时间: 2026-04-16

---

## 一、API 端点总览

| 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|
| POST | `/code-ability/evaluate` | 代码能力评估 | 阻塞 |

> 所有接口均需认证: `Authorization: Bearer <token>`

---

## 二、通用参数说明

### 认证方式

```
Authorization: Bearer <token>
```

Token 由 Java 服务端生成并传入，Python 端通过 `validate_token` 依赖项校验。

### 统一响应格式

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
| 400 | 请求参数错误（如 URL 无效） |
| 401 | Token 无效或过期 |
| 500 | 服务器内部错误 |

---

## 三、接口详情

### 3.1 代码能力评估

```http
POST /code-ability/evaluate
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 (JSON):**

```json
{
  "url": "https://github.com/torvalds",
  "use_ai": true,
  "cache_enabled": true
}
```

**参数说明:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| url | string | **是** | — | GitHub 或 Gitee 主页 URL |
| use_ai | boolean | 否 | true | 是否使用 AI 大模型进行深度分析 |
| cache_enabled | boolean | 否 | true | 是否使用缓存 |

**URL 格式要求:**
- GitHub: `https://github.com/{username}`
- Gitee: `https://gitee.com/{username}`

**耗时说明:**
- 基础评分：约 3-5 秒
- 开启 AI 分析：约 8-15 秒

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "platform": "github",
    "username": "torvalds",
    "composite_score": 92,
    "level": "专家",
    "features": {
      "total_repos": 8,
      "total_stars": 185000,
      "total_forks": 58000,
      "languages": ["C", "Assembly"],
      "contribution_frequency": "高",
      "code_quality": "优秀"
    },
    "ai_analysis": "该开发者在开源社区具有极高的影响力，尤其擅长系统级编程..."
  }
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| platform | string | 平台标识：`github` / `gitee` |
| username | string | 用户名 |
| composite_score | int | 综合评分（0-100） |
| level | string | 能力等级：`初级` / `中级` / `高级` / `专家` |
| features | object | 特征数据对象 |
| features.total_repos | int | 仓库总数 |
| features.total_stars | int | Star 总数 |
| features.total_forks | int | Fork 总数 |
| features.languages | string[] | 主要编程语言列表 |
| features.contribution_frequency | string | 贡献频率 |
| features.code_quality | string | 代码质量评估 |
| ai_analysis | string | AI 深度分析报告（仅 `use_ai=true` 时返回） |

**失败响应 (URL 无效):**
```json
{
  "code": 400,
  "state": false,
  "msg": "无效的 GitHub/Gitee URL",
  "data": null
}
```

**示例:**
```bash
curl -X POST "http://localhost:9000/code-ability/evaluate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/torvalds",
    "use_ai": true,
    "cache_enabled": true
  }'
```

---

## 四、缓存机制

### 缓存键生成

缓存基于请求参数的 JSON 序列化文本指纹（Fingerprint）生成，确保相同请求参数可复用缓存结果。

### 缓存生命周期

缓存超时时间由配置文件 `settings.redis.cache_timeout.code_ability` 控制。

### 缓存策略

| 场景 | 行为 |
|------|------|
| `cache_enabled=true` | 优先读取缓存，缓存不存在则重新计算并异步保存 |
| `cache_enabled=false` | 跳过缓存，直接计算 |

---

## 五、Java 调用示例

```java
@Autowired
private AiServiceClient aiServiceClient;

// 构建 JSON 请求体
Map<String, Object> requestBody = new HashMap<>();
requestBody.put("url", "https://github.com/torvalds");
requestBody.put("use_ai", true);
requestBody.put("cache_enabled", true);

// 发送请求（JSON 格式）
AiChatResponse response = aiServiceClient.chatWithOtherJson(
    "/code-ability/evaluate",
    requestBody,
    false  // enableRetry
);

// 解析响应
if (response.isSuccess()) {
    Map<String, Object> data = response.getData();
    int score = (int) data.get("composite_score");
    String level = (String) data.get("level");
    String aiAnalysis = (String) data.get("ai_analysis");
}
```

---

## 六、注意事项

1. **URL 格式**: 必须是有效的 GitHub 或 Gitee 用户主页 URL
2. **公开资料**: 只能分析公开的代码仓库和贡献记录
3. **网络依赖**: 需要能够访问目标平台的 API
4. **AI 分析**: 开启 `use_ai` 会增加响应时间，但提供更深度的分析报告
5. **缓存复用**: 对于相同的评估请求，建议开启缓存以提升响应速度
