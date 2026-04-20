# 报告服务 API 使用文档

> 定位: 成长计划生成与报告辅助接口
> 更新时间: 2026-04-16

---

## 一、API 端点总览

| 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|
| POST | `/report/plan` | 生成成长计划 | 阻塞 |
| POST | `/report/check` | 报告完整性检查 | 阻塞 |
| POST | `/report/polish` | 段落智能润色 | 阻塞 |

> 所有接口均需认证: `Authorization: Bearer <token>`

---

## 二、通用参数说明

### 认证方式

```
Authorization: Bearer <token>
```

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

### 常见错误码

| code | 说明 |
|------|------|
| 400 | 请求参数错误（如内容过短） |
| 401 | Token 无效或过期 |
| 404 | 资源不存在 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |

---

## 三、接口详情

### 3.1 生成成长计划

```http
POST /report/plan
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| job_id | int | 否 | 0 | 目标岗位 ID |
| user_id | int | 否 | 0 | 用户 ID |
| cache_enabled | boolean | 否 | true | 是否启用缓存 |

**处理流程:**

1. **缓存检查**: 检查是否有相同 `job_id` + `user_id` 组合的缓存
2. **获取画像**: 根据参数获取岗位画像和用户画像
3. **人岗匹配分析**: 调用 `analyze_user_job_match()` 进行能力差距分析
4. **生成成长计划**: 基于分析结果调用 `growth_plan_agent.generate_growth_plan()`
5. **缓存保存**: 异步保存结果到 Redis
6. **返回结果**: 返回成长计划

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "plan_id": "plan_001",
    "target_position": "后端开发工程师",
    "current_level": "初级",
    "target_level": "中级",
    "stages": [
      {
        "stage": "短期（1-3个月）",
        "goals": [
          "掌握 Spring Boot 基础",
          "完成 2 个实战项目",
          "学习 MySQL 数据库优化"
        ],
        "actions": [
          "学习 Spring Boot 官方文档",
          "参与开源项目贡献",
          "完成数据库优化课程"
        ],
        "resources": [
          "Spring Boot 官方文档",
          "《高性能 MySQL》"
        ]
      },
      {
        "stage": "中期（3-6个月）",
        "goals": [
          "掌握微服务架构",
          "独立负责项目模块"
        ],
        "actions": [
          "学习 Spring Cloud",
          "参与微服务项目开发"
        ],
        "resources": [
          "Spring Cloud 官方文档",
          "《微服务设计》"
        ]
      }
    ],
    "skill_gaps": [
      {
        "skill": "微服务架构",
        "current_level": "了解",
        "target_level": "熟练",
        "priority": "高"
      },
      {
        "skill": "数据库优化",
        "current_level": "熟悉",
        "target_level": "熟练",
        "priority": "中"
      }
    ],
    "created_at": "2026-04-16T10:00:00"
  }
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| plan_id | string | 计划 ID |
| target_position | string | 目标岗位名称 |
| current_level | string | 当前能力等级 |
| target_level | string | 目标能力等级 |
| stages | array | 分阶段计划列表 |
| stages[].stage | string | 阶段名称 |
| stages[].goals | string[] | 该阶段目标列表 |
| stages[].actions | string[] | 具体行动列表 |
| stages[].resources | string[] | 学习资源列表 |
| skill_gaps | array | 技能差距列表 |
| skill_gaps[].skill | string | 技能名称 |
| skill_gaps[].current_level | string | 当前水平 |
| skill_gaps[].target_level | string | 目标水平 |
| skill_gaps[].priority | string | 优先级：高/中/低 |
| created_at | string | 创建时间（ISO 8601 格式） |

**失败响应（人岗匹配失败）:**
```json
{
  "code": 200,
  "state": false,
  "msg": "人岗匹配分析失败：用户画像不存在",
  "data": null
}
```

**示例:**
```bash
curl -X POST "http://localhost:9000/report/plan" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "job_id=123" \
  -F "user_id=1001" \
  -F "cache_enabled=true"
```

---

### 3.2 报告完整性检查

```http
POST /report/check
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 (JSON):**

```json
{
  "user_id": 1001,
  "report_content": "职业规划报告正文内容...",
  "job_title": "后端开发工程师"
}
```

**参数说明:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | int | **是** | 用户 ID（用于自动查询用户画像） |
| report_content | string | **是** | 报告文本内容（至少 50 字符） |
| job_title | string | 否 | 目标岗位名称 |

**检查维度:**

| 维度 | 说明 |
|------|------|
| 人岗匹配分析 | 包含四维度量化分析（基础要求、职业技能、职业素养、发展潜力） |
| 职业发展路径 | 包含垂直晋升或换岗转型路径规划 |
| 分阶段行动计划 | 包含短期、中期行动计划 |
| 评估周期与指标 | 包含评估周期与关键指标 |

> 注意：用户画像会根据 `user_id` 自动从数据库查询，无需前端传递

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "is_complete": true,
    "check_results": [
      {
        "dimension": "人岗匹配分析",
        "is_present": true,
        "description": "包含四维度量化分析，数据详实",
        "suggestion": null
      },
      {
        "dimension": "职业发展路径",
        "is_present": true,
        "description": "包含垂直晋升路径规划，路径清晰",
        "suggestion": null
      },
      {
        "dimension": "分阶段行动计划",
        "is_present": true,
        "description": "包含短期和中期行动计划，具备可操作性",
        "suggestion": null
      },
      {
        "dimension": "评估周期与指标",
        "is_present": true,
        "description": "包含评估周期和关键指标",
        "suggestion": null
      }
    ],
    "missing_items": [],
    "overall_score": 85,
    "summary": "报告整体结构完整，内容详实，具备较强的可操作性"
  }
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| is_complete | boolean | 报告是否完整 |
| check_results | array | 各维度检查结果 |
| check_results[].dimension | string | 维度名称 |
| check_results[].is_present | boolean | 该维度是否存在 |
| check_results[].description | string | 维度内容描述 |
| check_results[].suggestion | string | 改进建议（如果缺失） |
| missing_items | string[] | 缺失项列表 |
| overall_score | int | 整体评分（0-100） |
| summary | string | 整体评价摘要 |

**失败响应（内容过短）:**
```json
{
  "code": 400,
  "state": false,
  "msg": "报告内容过短，至少需要50个字符",
  "data": null
}
```

**示例:**
```bash
curl -X POST "http://localhost:9000/report/check" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1001,
    "report_content": "职业规划报告正文内容...",
    "job_title": "后端开发工程师"
  }'
```

---

### 3.3 段落智能润色

```http
POST /report/polish
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 (JSON):**

```json
{
  "original_content": "该候选人具有较强的编程能力，熟悉多种编程语言。",
  "report_type": "match_analysis",
  "context": {
    "job_title": "后端开发工程师",
    "candidate_name": "张三"
  }
}
```

**参数说明:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| original_content | string | **是** | 原始文本内容（至少 20 字符） |
| report_type | string | **是** | 报告类型：`match_analysis` / `action_plan` / `other` |
| context | object | 否 | 上下文信息（如岗位名称、用户信息等） |

**报告类型说明:**

| 类型 | 说明 | 润色策略 |
|------|------|---------|
| `match_analysis` | 人岗匹配分析 | 强制四维度分析结构 |
| `action_plan` | 行动计划 | 确保 SMART 原则 |
| `other` | 通用润色 | 精炼、专业、有指导意义 |

**核心约束:**
- **防幻觉**: 不能捏造用户没有的技能、证书或经历
- **维度红线**: 匹配分析必须从 4 个维度进行
- **质量红线**: 内容必须具备可操作性和可解释性

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "original_content": "该候选人具有较强的编程能力，熟悉多种编程语言。",
    "polished_content": "该候选人在编程能力方面表现突出，精通 Python、Java 等主流编程语言，具备扎实的算法基础和良好的代码规范意识。在过往项目中展现出优秀的代码设计能力和问题解决能力。",
    "report_type": "match_analysis",
    "length_before": 24,
    "length_after": 78
  }
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| original_content | string | 原始内容 |
| polished_content | string | 润色后的内容 |
| report_type | string | 报告类型 |
| length_before | int | 润色前长度 |
| length_after | int | 润色后长度 |

**失败响应（类型无效）:**
```json
{
  "code": 400,
  "state": false,
  "msg": "无效的报告类型：invalid_type，有效值为：match_analysis, action_plan, other",
  "data": null
}
```

**失败响应（内容过短）:**
```json
{
  "code": 400,
  "state": false,
  "msg": "原始内容过短，至少需要20个字符",
  "data": null
}
```

**示例:**
```bash
curl -X POST "http://localhost:9000/report/polish" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "original_content": "该候选人具有较强的编程能力，熟悉多种编程语言。",
    "report_type": "match_analysis",
    "context": {
      "job_title": "后端开发工程师"
    }
  }'
```

---

## 四、缓存机制

### 成长计划缓存

缓存基于岗位画像文本 + 用户画像文本的 JSON 序列化文本指纹生成。

```python
json_profile_text = {
    "job_profile_text": job_profile_text,
    "user_profile_text": user_profile_text
}
fingerprint = text_fingerprint(json.dumps(json_profile_text, ...))
```

### 缓存生命周期

缓存超时时间由配置文件 `settings.redis.cache_timeout.report` 控制。

---

## 五、Java 调用示例

### 生成成长计划

```java
@Autowired
private AiServiceClient aiServiceClient;

// 构建请求参数（Form 表单格式）
Map<String, Object> params = new HashMap<>();
params.put("job_id", 123);
params.put("user_id", 1001);
params.put("cache_enabled", true);

AiChatResponse response = aiServiceClient.chatWithOther(
    "/report/plan",
    params,
    false  // enableRetry
);

if (response.isSuccess()) {
    Map<String, Object> data = response.getData();
    String planId = (String) data.get("plan_id");
    List<Map<String, Object>> stages = (List<Map<String, Object>>) data.get("stages");
}
```

### 报告完整性检查

```java
// 构建请求体（JSON 格式）
Map<String, Object> requestBody = new HashMap<>();
requestBody.put("user_id", 1001);
requestBody.put("report_content", "职业规划报告正文内容...");
requestBody.put("job_title", "后端开发工程师");

AiChatResponse response = aiServiceClient.chatWithOtherJson(
    "/report/check",
    requestBody,
    false  // enableRetry
);

if (response.isSuccess()) {
    Map<String, Object> data = response.getData();
    boolean isComplete = (boolean) data.get("is_complete");
    int overallScore = (int) data.get("overall_score");
    String summary = (String) data.get("summary");
    List<Map<String, Object>> checkResults = (List<Map<String, Object>>) data.get("check_results");
}
```

### 段落智能润色

```java
// 构建请求体（JSON 格式）
Map<String, Object> requestBody = new HashMap<>();
requestBody.put("original_content", "该候选人具有较强的编程能力，熟悉多种编程语言。");
requestBody.put("report_type", "match_analysis");
requestBody.put("context", Map.of("job_title", "后端开发工程师", "candidate_name", "张三"));

AiChatResponse response = aiServiceClient.chatWithOtherJson(
    "/report/polish",
    requestBody,
    false  // enableRetry
);

if (response.isSuccess()) {
    Map<String, Object> data = response.getData();
    String polishedContent = (String) data.get("polished_content");
    int lengthAfter = (int) data.get("length_after");
}
```

---

## 六、注意事项

1. **报告内容长度**: 检查接口要求至少 50 字符，润色接口要求至少 20 字符
2. **报告类型**: 润色接口的 `report_type` 必须为 `match_analysis`、`action_plan` 或 `other`
3. **用户画像自动获取**: 检查接口会根据 `user_id` 自动查询用户画像，无需前端传递
4. **润色约束**: 润色时会严格防止捏造内容，确保内容真实可靠
5. **缓存建议**: 对于相同的岗位和用户组合，建议开启缓存以提升响应速度
6. **分阶段计划**: 成长计划通常包含短期（1-3个月）和中期（3-6个月）两个阶段
