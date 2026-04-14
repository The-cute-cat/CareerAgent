# AI 服务 API 文档

## 基础信息

- **服务地址**: `http://localhost:9000`
- **认证方式**: Bearer Token
- **请求格式**: `application/x-www-form-urlencoded` 或 `application/json`
- **响应格式**: `application/json`

## 统一响应格式

```json
{
  "code": 200,
  "state": true,
  "msg": null,
  "data": { ... }
}
```

---

## 1. 智能对话接口 (Chat)

### 1.1 普通对话（阻塞方式）

**POST** `/chat/message`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 消息内容 |
| user_id | int | 是 | 用户ID |
| conversation_id | string | 否 | 对话ID |
| auto_extract_memory | bool | 否 | 是否自动提取记忆（默认true） |

**响应示例**:
```json
{
  "code": 200,
  "state": true,
  "data": {
    "message": "AI回复内容",
    "conversationId": "session_id"
  }
}
```

### 1.2 流式对话（SSE）

**POST** `/chat/message/stream`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 消息内容 |
| user_id | int | 是 | 用户ID |
| conversation_id | string | 否 | 对话ID |
| auto_extract_memory | bool | 否 | 是否自动提取记忆 |
| show_thinking | bool | 否 | 是否显示思考过程 |

**响应**: SSE 事件流

### 1.3 文件对话

**POST** `/chat/files`

上传文件进行分析对话。

**POST** `/chat/message-and-files`

文本消息 + 文件对话。

### 1.4 会话管理

**GET** `/chat/conversations`
获取用户会话列表

**DELETE** `/chat/conversation/{conversation_id}`
删除指定会话

**PUT** `/chat/conversation/title`
更新会话标题

---

## 2. 文件解析接口 (Parse)

### 2.1 单文件解析

**POST** `/parse/file`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 上传的文件 |
| cache_enabled | bool | 否 | 是否启用缓存（默认true） |

**支持格式**: PDF, Word (docx), 图片 (JPG, PNG, BMP, GIF)

**响应示例**:
```json
{
  "code": 200,
  "state": true,
  "data": {
    "name": "张三",
    "education": [...],
    "skills": [...],
    "experience": [...]
  }
}
```

### 2.2 批量文件解析

**POST** `/parse/files`

支持同时上传多个文件进行解析。

---

## 3. 人岗匹配接口 (Matching)

### 3.1 岗位匹配分析

**POST** `/matching/jobs`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_profile | object | 是 | 学生人物画像 |
| recall_top_k | int | 否 | 向量召回数量（默认20） |
| final_top_k | int | 否 | 最终返回数量（默认5） |

**请求体示例**:
```json
{
  "student_profile": {
    "name": "张三",
    "education": {...},
    "skills": [...],
    "experience": [...]
  },
  "recall_top_k": 20,
  "final_top_k": 5
}
```

**响应**: 匹配的岗位列表，包含匹配度分析和能力差距评估。

---

## 4. 职业路径规划接口 (Graph Path)

### 4.1 垂直晋升路径

**POST** `/graph_path/promotion_path/single`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| job_id | string | 是 | 起点岗位ID |

返回同赛道内的晋升路径（1-5跳）。

### 4.2 换岗路径

**POST** `/graph_path/transfer_path/single`

返回同行业不同赛道的换岗路径（1-2跳）。

### 4.3 跨界跃迁路径

**POST** `/graph_path/career_path/cross_industry`

返回跨行业的职业发展路径。

### 4.4 目标导向路径规划

**POST** `/graph_path/goal_path/single`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_job_id | string | 是 | 起点岗位ID |
| target_job_id | string | 是 | 目标岗位ID |
| limit_paths | int | 否 | 返回路径数量（默认10） |

---

## 5. 代码能力评估接口 (Code Ability)

### 5.1 代码能力评估

**POST** `/code-ability/evaluate`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | GitHub/Gitee 主页URL |
| use_ai | bool | 否 | 是否使用AI深度分析（默认true） |
| cache_enabled | bool | 否 | 是否使用缓存（默认true） |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "platform": "github",
    "username": "torvalds",
    "composite_score": 95,
    "level": "Expert",
    "features": {...},
    "ai_analysis": "..."
  }
}
```

---

## 6. 测试题生成接口 (Question)

### 6.1 生成测试题

**POST** `/question/generate`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 技能/工具名称 |
| question_type | string | 是 | 题目类型：skill/tool |
| cache_enabled | bool | 否 | 是否启用缓存 |

### 6.2 评估学生答案

**POST** `/question/check_student_answer`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| questions | string | 是 | 题目内容 |
| evaluation_criteria | string | 是 | 评分标准 |
| student_answer | string | 是 | 学生答案 |

---

## 7. 报告生成接口 (Report)

### 7.1 成长计划生成

**POST** `/report/plan`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| job_id | int | 是 | 岗位ID |
| user_id | int | 是 | 用户ID |
| cache_enabled | bool | 否 | 是否启用缓存 |

### 7.2 报告完整性检查

**POST** `/report/check`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| report_content | string | 是 | 报告内容 |
| user_id | int | 是 | 用户ID |
| job_title | string | 否 | 岗位名称 |

检查项：
- 人岗匹配四维度量化分析
- 职业发展路径规划
- 分阶段行动计划
- 评估周期与指标

### 7.3 段落智能润色

**POST** `/report/polish`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| paragraph | string | 是 | 待润色段落 |
| report_type | string | 是 | 报告类型 |
| context | string | 否 | 上下文信息 |

---

## 8. 知识导师接口 (Knowledge Tutor)

### 8.1 知识点岗位影响分析（流式）

**POST** `/knowledge_tutor/analyze/stream`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| current_node | string | 是 | 当前知识点名称 |
| job_id | int | 是 | 目标岗位ID |
| user_id | int | 是 | 用户ID |
| graph_context | string | 否 | 图谱关系 |
| industry_data | string | 否 | 行业数据 |

**响应**: SSE 事件流

### 8.2 知识点详细解释（流式）

**POST** `/knowledge_tutor/explain/stream`

参数同上，返回知识点的详细解释。

---

## 9. 数据转换接口 (Convert)

### 9.1 用户表单转用户画像

**POST** `/convert/user_form_to_userprofile`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_form | object | 是 | 用户表单数据 |

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/Token无效 |
| 404 | 资源不存在 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |
