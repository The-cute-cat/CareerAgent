# 接口文档汇总

> 基于前端项目静态扫描整理，覆盖 `src/api`、`src/utils/request.ts` 以及组件内直接配置的接口地址。  
> 当前开发环境 `.env.development` 中 `VITE_ENABLE_MOCK=true`，部分接口在 Mock 开关开启时不会请求后端。

## 1. 全局请求约定

### 1.1 基础地址与代理

- 前端 Axios 实例：`src/utils/request.ts`
- Axios `baseURL`：`/api`
- 开发代理：`vite.config.ts`
  - 前端请求：`/api/**`
  - 代理目标：`http://127.0.0.1:8080`
  - 代理重写：`path.replace(/^\/api/, '')`

因此大多数 API 模块里写的 `'/user/login'`，浏览器实际请求为：

```text
/api/user/login
```

后端实际收到的路径为：

```text
/user/login
```

### 1.2 鉴权

请求拦截器会从 Pinia `userStore.accessToken` 读取 token，并添加：

```http
Authorization: Bearer <accessToken>
```

当响应状态码为 `401` 时，会使用 `refreshToken` 请求：

```http
POST /api/user/refreshToken
```

请求体：

```json
{
  "refreshToken": "string"
}
```

刷新成功后前端期望响应结构：

```json
{
  "code": 200,
  "data": {
    "accessToken": "string",
    "refreshToken": "string"
  }
}
```

刷新失败会清空本地用户信息并跳转 `/login`。Mock 模式下会忽略 401 登出逻辑。

### 1.3 通用响应结构

项目多数接口按 `Result<T>` 使用：

```ts
interface Result<T = unknown> {
  code: number
  data?: T | null
  msg?: string | null
}
```

代码注释里约定：`code=200` 表示成功，`401` 表示失败或未授权。不过少量支付接口兼容 `code=0`。

### 1.4 Content-Type

- `POST` / `PUT` / `PATCH` 且请求体不是 `FormData`：自动设置 `Content-Type: application/json`
- `FormData`：由浏览器或单独配置处理，主要用于文件上传和流式接口

---

## 2. 用户模块

来源：

- `src/api/user/user.ts`
- `src/api/user/index.ts`

### 2.1 登录

```http
POST /api/user/login
```

后端路径：`POST /user/login`

请求体 `LoginFormDTO`：

```ts
{
  username?: string
  password?: string
  rememberMe?: boolean
  email?: string | null
  code?: string | null
  inviteCode?: string | null
  passwordConfirm?: string | null
}
```

前端期望响应：

```ts
{
  code: number
  message: string
  msg?: string
  data: {
    accessToken: string
    refreshToken: string
    userInfo: any
  }
}
```

### 2.2 注册

```http
POST /api/user/register
```

后端路径：`POST /user/register`

请求体：`LoginFormDTO`，常用字段包括 `username`、`password`、`passwordConfirm`、`email`、`code`、`inviteCode`。

### 2.3 忘记密码 / 重置密码

项目中存在两个相近路径，建议后端和前端统一：

```http
POST /api/user/forget-password
POST /api/user/forgot-password
```

后端路径：

```text
/user/forget-password
/user/forgot-password
```

请求体：`LoginFormDTO` 或任意对象，常用字段预计为 `email`、`code`、`password`、`passwordConfirm`。

### 2.4 发送注册验证码

```http
POST /api/user/send-code-register
```

后端路径：`POST /user/send-code-register`

请求体：`LoginFormDTO`，通常包含 `email`。

### 2.5 发送忘记密码验证码

```http
POST /api/user/send-code-forget
```

后端路径：`POST /user/send-code-forget`

请求体：`LoginFormDTO`，通常包含 `email`。

### 2.6 获取用户信息

```http
GET /api/user/get-user-info
```

后端路径：`GET /user/get-user-info`

前端期望响应：

```ts
{
  code: number
  data: {
    checkUser: {
      id: number
      nickname: string
      username: string
      avatar: string
      email: string
      info: string
      phone: string
      createTime: string
      updateTime: string
      accessToken?: string
      refreshToken?: string
      pointBalance?: number
      endTime?: string
    }
  }
}
```

### 2.7 获取用户基础档案

```http
GET /api/user/get-basic-info
```

后端路径：`GET /user/get-basic-info`

前端未显式声明返回类型。

### 2.8 获取用户信息补充接口

```http
GET /api/user/info
```

后端路径：`GET /user/info`

当前函数名为 `getUserInfoService(id: number)`，但 `id` 参数没有拼到 URL 或查询参数里。

### 2.9 登出

```http
POST /api/user/logout
```

后端路径：`POST /user/logout`

### 2.10 修改头像

```http
POST /api/user/avatar
```

后端路径：`POST /user/avatar`

请求体：`multipart/form-data`

字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| avatar | File | 头像文件 |

返回：前端按 `string` 头像 URL 使用。

---

## 3. 职业表单 / 简历解析 / 问卷

来源：

- `src/api/career-form/resume.ts`
- `src/api/career-form/formdata.ts`
- `src/api/career-form/questions.ts`
- `src/api/career-form/codeAbility.ts`

### 3.1 上传并解析简历/资料文件

```http
POST /api/parse/file
```

后端路径：`POST /parse/file`

请求体：`multipart/form-data`

字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| files | File[] | 是 | 可上传多个文件，字段名重复追加 |
| user_id | string | 否 | 用户 ID |
| overwrite | string | 是 | `"true"` 或 `"false"` |

支持 `AbortSignal` 取消上传，支持上传进度回调。

返回：

```ts
Result<UploadResponse | UploadResponse[]>
```

`UploadResponse` 是 `CareerFormData` 的部分字段，用于自动填充表单：

```ts
{
  education?: string
  educationOther?: string
  major?: string[]
  graduationDate?: string
  languages?: { type: string; level: string; other: string }[]
  certificates?: string[]
  certificateOther?: string
  skills?: { name: string; score: number }[]
  tools?: { name: string; score: number }[]
  codeAbility?: { links: string }
  codeLinks?: string | string[]
  projects?: { isCompetition: boolean; name: string; desc: string }[]
  internships?: { company: string; role: string; date: Date[]; desc: string }[]
  innovation?: string
  targetJob?: string
  targetIndustries?: string[]
  priorities?: { value: 'tech' | 'salary' | 'stable'; label: string }[]
}
```

### 3.2 提交职业规划表单并获取岗位匹配结果

```http
POST /api/convert/user_form_to_userprofile
```

后端路径：`POST /convert/user_form_to_userprofile`

请求体 `CareerFormSubmitDTO`：

```ts
{
  education: string
  major: string
  graduationDate?: string
  languages: { type: string; level: string; other: string }[]
  certificates: string[]
  skills: { name: string; score: number }[]
  tools: { name: string; score: number }[]
  codeLinks?: string[]
  codeAbilityEval?: {
    platform?: 'github' | 'gitee'
    username?: string
    compositeScore?: number
    level?: 'S' | 'A' | 'B' | 'C' | 'D' | 'E'
    dimensions?: {
      projectScale?: number
      techBreadth?: number
      activity?: number
      engineering?: number
      influence?: number
    }
    summary?: string
    strengths?: string[]
    weaknesses?: string[]
  }
  projects: { isCompetition: boolean; name: string; desc: string }[]
  internships: { company: string; role: string; date: Date[]; desc: string }[]
  quizDetail?: { type: 'choice' | 'open_ended'; question: string; answer: string }[]
  innovation: string
  targetJob: string
  targetIndustries: string[]
  priorities: string[]
}
```

返回：

```ts
Result<JobMatchItem[]>
```

`JobMatchItem`：

```ts
{
  job_id: string
  score: number
  raw_data: {
    job_id: string
    job_name: string
    profiles: {
      basic_requirements: object
      professional_skills: object
      professional_literacy: object
      development_potential: object
      job_attributes: object
    }
  }
  deep_analysis: {
    can_apply: boolean
    score: number
    missing_key_skills: string[]
    gap_matrix: {
      dimension: string
      required: string
      current: string
      gap_analysis: string
    }[]
    actionable_advice: string
    all_analysis: string
  }
}
```

### 3.3 生成技能/工具测评题

```http
GET /api/question/generate
```

后端路径：`GET /question/generate`

查询参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| type | `skill \| tool \| code \| communication \| stress \| learning` | 是 | 问卷类型 |
| name | string | skill/tool 必填 | 技能或工具名称，如 Java、Git |

返回：

```ts
{
  tool: string
  total_questions: number
  questions: Array<
    | {
        id: number
        type: 'choice'
        content: string
        options: string[]
        correct_answer: string
        difficulty: 'easy' | 'medium' | 'hard'
      }
    | {
        id: number
        type: 'fill_in'
        content: string
        options: null
        correct_answer: string
        difficulty: 'easy' | 'medium' | 'hard'
      }
    | {
        id: number
        type: 'open_ended'
        content: string
        options: null
        correct_answer: null
        evaluation_criteria: string
        difficulty: 'easy' | 'medium' | 'hard'
      }
  >
}
```

注意：该函数类型写的是 `request.get<QuizResponse>`，没有显式包一层 `Result`，但 Mock 返回的是 `{ code, msg, data }` 结构。建议与后端统一。

### 3.4 获取素质测评题

当前实现固定返回 Mock，不请求后端。

预留后端接口：

```http
GET /api/person_question/generate?type=communication
```

后端路径：`GET /person_question/generate`

查询参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| type | `code \| communication \| stress \| learning` | 测评类型 |

预期返回：

```ts
Result<{
  id: number
  type: 'choice' | 'open_ended'
  text: string
  options: string[] | null
}[]>
```

### 3.5 提交问答题进行 AI 评分

```http
POST /api/question/check_student_answer
```

后端路径：`POST /question/check_student_answer`

请求体：

```ts
{
  name?: string
  type: 'skill' | 'tool' | 'code' | 'communication' | 'stress' | 'learning'
  questions: string
  studentAnswer: string
  evaluationCriteria?: string
}
```

返回：

```ts
{
  score: number
  max_score: number
  score_details: {
    point: string
    max_point_score: number
    earned_score: number
    reason: string
  }[]
  comment: string
  suggestions: string
}
```

前端也兼容 `Result<OpenEndedScoreResult>`；并会把后端分数乘以 4 映射到前端 40 分制。

### 3.6 代码能力评估

```http
POST /api/codeAbility/evaluate
```

后端路径：`POST /codeAbility/evaluate`

请求体：

```ts
{
  url: string
  use_ai?: boolean
  cache_enabled?: boolean
}
```

返回：

```ts
Result<{
  platform: string
  username: string
  composite_score: number
  level: string
  features: {
    composite?: {
      total_score: number
      level: string
      dimension_scores: {
        project_scale: number
        tech_breadth: number
        activity: number
        engineering: number
        community: number
      }
      weights: object
      max_score: number
    }
    basic?: object
    repo?: object
    language?: object
    activity?: object
    quality?: object
  }
  ai_analysis?: {
    overall_assessment?: {
      concerns: string[]
      highlights: string[]
      level: string
      score: number
      summary: string
    }
    tech_stack_analysis?: object
    project_quality_analysis?: object
    activity_analysis?: object
    career_alignment?: object
    actionable_advice?: object[]
    error?: string
  }
}> & {
  state?: string
}
```

---

## 4. 聊天机器人

来源：`src/api/chatbot/index.ts`

### 4.1 流式发送纯文本消息

```http
POST /api/chat/stream/message
```

后端路径：`POST /chat/stream/message`

请求体：`multipart/form-data`

字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| message | string | 是 | 用户消息，前端最多截取 10000 字符；没有消息时默认 `Please analyze the uploaded file` |
| conversationId | string | 是 | 对话 ID；未传则前端生成 |
| auto_extract_memory | string boolean | 否 | 是否自动提取记忆 |
| show_thinking | string boolean | 否 | 是否显示思考过程 |

响应：`text` 流。前端兼容两类格式：

1. SSE：

```text
data: {"type":"content","content":"..."}

data: {"status":"completed"}

data: [DONE]
```

2. 连续 JSON 对象：

```json
{"type":"content","content":"..."}{"status":"completed"}
```

错误格式：

```json
{"type":"error","message":"error message"}
```

或：

```text
data: [ERROR] error message
```

### 4.2 流式发送消息和文件

```http
POST /api/chat/stream/message-and-files
```

后端路径：`POST /chat/stream/message-and-files`

请求体：`multipart/form-data`

字段在 4.1 基础上增加：

| 字段 | 类型 | 说明 |
|---|---|---|
| files | File[] | 多文件上传，单文件最大 10MB，总大小最大 50MB，超限文件前端会跳过 |

响应格式同 4.1。

---

## 5. 知识图谱流式分析

来源：`src/api/knowledge-graph/index.ts`

### 5.1 分析知识点对岗位的影响

```http
POST /api/knowledge-graph/analyze/stream
```

后端路径：`POST /knowledge-graph/analyze/stream`

请求体：`multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| currentNode | string | 是 | 当前知识点或节点 ID |
| jobId | string/number | 是 | 目标岗位 ID |
| graphContext | string | 否 | 图谱上下文 |
| industryData | string | 否 | 行业数据 |

响应：`text` 流，兼容 SSE 或连续 JSON，内容字段为 `content`。

### 5.2 解释知识点内容

```http
POST /api/knowledge-graph/explain/stream
```

后端路径：`POST /knowledge-graph/explain/stream`

请求字段和响应格式同 5.1。

---

## 6. 职业报告

来源：`src/api/report/index.ts`

### 6.1 生成/获取成长计划报告

```http
POST /api/report/plan
```

后端路径：`POST /report/plan`

请求体：`null`

查询参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| job_id | string/number | 是 | 岗位 ID |
| cache_enabled | boolean | 否 | 是否启用缓存，默认 `true` |

返回：

```ts
Result<GrowthPlanData>
```

主要字段：

```ts
{
  student_summary: string
  target_position: string
  target_position_profile_summary?: string
  current_gap: string
  short_term_plan: {
    duration: string
    goal: string
    focus_areas: string[]
    milestones: Milestone[]
    quick_wins: string[]
  }
  mid_term_plan: {
    duration: string
    goal: string
    skill_roadmap: string[]
    milestones: Milestone[]
    career_progression: string
    recommended_internships: InternshipItem[]
  }
  action_checklist: string[]
  tips: string[]
}
```

### 6.2 检查报告完整性

```http
POST /api/report/check
```

后端路径：`POST /report/check`

请求体：

```ts
{
  report_content: string
  job_title?: string
}
```

返回：

```ts
Result<{
  is_complete: boolean
  check_results: {
    dimension: string
    is_present: boolean
    description: string
    suggestion?: string | null
  }[]
  missing_items: string[]
  overall_score: number
  summary: string
}>
```

### 6.3 润色报告段落

```http
POST /api/report/polish
```

后端路径：`POST /report/polish`

请求体：

```ts
{
  original_content: string
  report_type: 'match_analysis' | 'action_plan' | 'other'
  context?: Record<string, unknown>
}
```

返回：

```ts
Result<{
  original_content: string
  polished_content: string
  report_type: 'match_analysis' | 'action_plan' | 'other'
  length_before: number
  length_after: number
}>
```

---

## 7. 积分与会员

来源：

- `src/api/points/index.ts`
- `src/api/points/invite.ts`

### 7.1 获取账户积分

```http
GET /api/points/account/{id}
```

后端路径：`GET /points/account/{id}`

路径参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| id | number | 用户 ID |

返回：

```ts
Result<{
  userId: number
  pointsBalance: number
  totalConsumed: number
  updateTime: string
  referralCount: number
  referralRewardTotal: number
}>
```

### 7.2 消费积分

```http
POST /api/points/consume
```

后端路径：`POST /points/consume`

请求体：

```ts
{
  userId: number
  amount: number
  type: number
  description?: string
  status?: number
  vip?: number
  [property: string]: any
}
```

返回：

```ts
Result<{
  id: number
  userId: number
  pointsBalance: number
  PointsRemainAmount: number
  status: number
  totalConsumed: number
  endTime: string
  ActivityEndTime: string
  createTime: string
  updateTime: string
}>
```

### 7.3 充值积分 / 变更会员

```http
POST /api/points/recharge
```

后端路径：`POST /points/recharge`

请求体：

```ts
{
  userId: number
  amount: number
  type: number
  vip?: number
  status?: number
  description?: string
}
```

返回：`Result<any>`

### 7.4 按类型获取套餐

```http
GET /api/package/list/type/{type}
```

后端路径：`GET /package/list/type/{type}`

路径参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| type | number | 套餐类型 |

返回：

```ts
Result<{
  id: number
  name: string
  price: number
  points?: number
  type: number
  description?: string
  status?: number
  [key: string]: any
}[]>
```

### 7.5 获取邀请码

```http
GET /api/points/invite
```

后端路径：`GET /points/invite`

返回：`Result<string>`

### 7.6 注册成为邀请大使

```http
POST /api/points/invite
```

后端路径：`POST /points/invite`

返回：`Result<string>`

---

## 8. 支付

来源：`src/api/payment/index.ts`

### 8.1 创建支付订单

```http
POST /api/member/pay/order
```

后端路径：`POST /member/pay/order`

请求体：

```ts
{
  amount: number
  pointsGranted: number
  payType: number
  purpose: number
  memberLevel?: number
}
```

字段说明：

| 字段 | 说明 |
|---|---|
| amount | 金额，单位：元 |
| pointsGranted | 赠送积分 |
| payType | `1` 微信，`2` 支付宝 |
| purpose | `1` 积分充值，`2` 会员购买 |
| memberLevel | 会员等级，如 `1` 月度、`2` 季度、`3` 年度 |

响应兼容两种：

1. HTML：支付宝表单页面，前端会新开窗口写入 HTML。
2. JSON：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "orderId": "string",
    "payUrl": "string"
  }
}
```

也兼容 `data.id`、`data.outTradeNo`、`data.qrCode`。

### 8.2 根据订单号重新发起支付

工具函数构造：

```text
{VITE_SERVER}/member/pay/{orderNo}
```

默认：

```text
http://localhost:8080/member/pay/{orderNo}
```

说明：这个接口通过 `window.open` 直接访问后端，不走 Axios `/api` 代理。

### 8.3 查询订单支付状态

当前代码：

```http
GET /api/api/member/order/status/{orderNo}
```

因为 `queryPaymentStatusService` 写的是：

```ts
request.get(`/api/member/order/status/${orderNo}`)
```

而 Axios `baseURL` 已经是 `/api`，所以浏览器会请求 `/api/api/member/order/status/{orderNo}`。代理重写后后端实际收到：

```text
/api/member/order/status/{orderNo}
```

如果后端真实路径是 `/member/order/status/{orderNo}`，这里应改成：

```ts
request.get(`/member/order/status/${orderNo}`)
```

前端期望返回：

```ts
Result<{
  orderId: string
  status: 'pending' | 'paid' | 'expired' | 'cancelled'
  amount?: number
  paidAt?: string
}>
```

### 8.4 组件内直接跳转的支付接口

`src/components/CProfile_Component/MemberPlanPanel.vue` 中存在：

```text
/api/alipay/pay/{orderNo}
```

这是 `window.location.href` 直接跳转，不经过 Axios。需要确认后端是否仍支持该旧路径；支付 API 模块里新路径是 `/member/pay/{orderNo}`。

---

## 9. 反馈

来源：`src/api/feedback/index.ts`

### 9.1 提交反馈

```http
POST /api/feedback/submit
```

后端路径：`POST /feedback/submit`

请求体：

```ts
{
  id?: number
  userId?: number
  content: string
  type: string
  contact?: string
  images?: string
  createTime?: string
  updateTime?: string
  status?: number
  response?: string
}
```

返回：`Result<boolean>`

状态约定：

| status | 说明 |
|---|---|
| 0 | 待处理 |
| 1 | 已回复 |
| 2 | 已关闭 |

### 9.2 查询用户反馈历史

```http
GET /api/feedback/user/{userId}/history?pageNum=1&pageSize=10
```

后端路径：`GET /feedback/user/{userId}/history`

返回：`Result<any>`

### 9.3 查询反馈详情

```http
GET /api/feedback/{id}
```

后端路径：`GET /feedback/{id}`

返回：`Result<Feedback>`

### 9.4 更新反馈

```http
PUT /api/feedback/update
```

后端路径：`PUT /feedback/update`

请求体：`Feedback`

返回：`Result<boolean>`

### 9.5 上传反馈图片

当前代码：

```http
POST /api/api/upload
```

因为 `uploadImageService` 写的是：

```ts
request.post('/api/upload', formData)
```

而 Axios `baseURL` 已经是 `/api`，所以浏览器会请求 `/api/api/upload`。代理重写后后端实际收到：

```text
/api/upload
```

如果后端真实路径是 `/upload`，这里应改成：

```ts
request.post('/upload', formData)
```

请求体：`multipart/form-data`

返回：前端未严格声明，Mock 期望：

```ts
Result<{ url: string }>
```

### 9.6 查询所有反馈列表（管理端）

```http
GET /api/feedback/list?pageNum=1&pageSize=10&status=0
```

后端路径：`GET /feedback/list`

查询参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageNum | number | 否 | 默认 1 |
| pageSize | number | 否 | 默认 10 |
| status | number | 否 | 反馈状态 |

返回：`Result<any>`

---

## 10. 管理端

来源：`src/api/admin/usage.ts`

### 10.1 查询全局使用记录

```http
GET /api/admin/usage/records?pageNum=1&pageSize=20&userId=100
```

后端路径：`GET /admin/usage/records`

查询参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageNum | number | 否 | 默认 1 |
| pageSize | number | 否 | 默认 20 |
| userId | number | 否 | 按用户过滤 |

返回：

```ts
Result<{
  list: {
    id: number
    userId: number
    username?: string
    actionType: string
    actionName: string
    pointsConsumed: number
    createTime: string
    details?: string
  }[]
  total: number
}>
```

---

## 11. 富文本编辑器上传

来源：`src/components/Person_Report/WangEditor.vue`

### 11.1 编辑器图片上传

```http
POST /api/upload
```

说明：这是 WangEditor 的 `server: '/api/upload'` 配置，直接由编辑器发起请求，不走项目 Axios 实例，因此浏览器实际请求就是 `/api/upload`。开发代理重写后，后端收到：

```text
/upload
```

这与反馈图片上传服务里的 `request.post('/api/upload')` 行为不同，建议统一上传接口路径。

---

## 12. 需要后端确认或建议修正的点

1. **双 `/api` 问题**
   - `src/api/payment/index.ts`：`/api/member/order/status/{orderNo}`
   - `src/api/feedback/index.ts`：`/api/upload`
   - 这两个通过 Axios 实例调用时会叠加成 `/api/api/**`。

2. **支付路径不一致**
   - API 模块：`/member/pay/{orderNo}`
   - 组件跳转：`/api/alipay/pay/{orderNo}`
   - 建议确认保留哪一个。

3. **忘记密码路径不一致**
   - `src/api/user/user.ts`：`/user/forget-password`
   - `src/api/user/index.ts`：`/user/forgot-password`
   - 建议统一为一个。

4. **题目生成返回结构不一致**
   - 类型写法倾向直接返回 `QuizResponse`
   - Mock 与其他接口倾向 `Result<QuizResponse>`
   - 建议统一为 `Result<QuizResponse>` 或更新前端解包逻辑。

5. **素质测评题接口当前被 Mock 固定拦截**
   - `getPersonQuizApi` 目前无论 `VITE_ENABLE_MOCK` 都返回本地 Mock。
   - 若要联调后端，需要恢复 `/person_question/generate` 请求。

6. **环境变量编码显示异常**
   - 多个源码注释和 `.env.development` 中文显示为乱码，但不影响接口路径扫描。
   - 建议统一文件编码为 UTF-8，便于后续维护。

---

## 13. 接口总览表

| 模块 | 方法 | 前端路径 | 后端收到路径 | 说明 |
|---|---:|---|---|---|
| 用户 | POST | `/api/user/login` | `/user/login` | 登录 |
| 用户 | POST | `/api/user/register` | `/user/register` | 注册 |
| 用户 | POST | `/api/user/forget-password` | `/user/forget-password` | 忘记密码 |
| 用户 | POST | `/api/user/forgot-password` | `/user/forgot-password` | 忘记密码，另一处封装 |
| 用户 | POST | `/api/user/send-code-register` | `/user/send-code-register` | 注册验证码 |
| 用户 | POST | `/api/user/send-code-forget` | `/user/send-code-forget` | 忘记密码验证码 |
| 用户 | GET | `/api/user/get-user-info` | `/user/get-user-info` | 获取用户信息 |
| 用户 | GET | `/api/user/get-basic-info` | `/user/get-basic-info` | 获取基础档案 |
| 用户 | GET | `/api/user/info` | `/user/info` | 用户信息补充接口 |
| 用户 | POST | `/api/user/logout` | `/user/logout` | 登出 |
| 用户 | POST | `/api/user/avatar` | `/user/avatar` | 上传头像 |
| 职业表单 | POST | `/api/parse/file` | `/parse/file` | 简历/资料解析 |
| 职业表单 | POST | `/api/convert/user_form_to_userprofile` | `/convert/user_form_to_userprofile` | 表单提交和岗位匹配 |
| 问卷 | GET | `/api/question/generate` | `/question/generate` | 生成技能/工具题 |
| 问卷 | GET | `/api/person_question/generate` | `/person_question/generate` | 素质测评题，当前预留 |
| 问卷 | POST | `/api/question/check_student_answer` | `/question/check_student_answer` | 问答题评分 |
| 代码能力 | POST | `/api/codeAbility/evaluate` | `/codeAbility/evaluate` | GitHub/Gitee 能力评估 |
| 聊天 | POST | `/api/chat/stream/message` | `/chat/stream/message` | 纯文本流式聊天 |
| 聊天 | POST | `/api/chat/stream/message-and-files` | `/chat/stream/message-and-files` | 文件流式聊天 |
| 知识图谱 | POST | `/api/knowledge-graph/analyze/stream` | `/knowledge-graph/analyze/stream` | 知识点影响分析 |
| 知识图谱 | POST | `/api/knowledge-graph/explain/stream` | `/knowledge-graph/explain/stream` | 知识点解释 |
| 报告 | POST | `/api/report/plan` | `/report/plan` | 生成成长计划 |
| 报告 | POST | `/api/report/check` | `/report/check` | 报告完整性检查 |
| 报告 | POST | `/api/report/polish` | `/report/polish` | 段落润色 |
| 积分 | GET | `/api/points/account/{id}` | `/points/account/{id}` | 获取积分 |
| 积分 | POST | `/api/points/consume` | `/points/consume` | 消费积分 |
| 积分 | POST | `/api/points/recharge` | `/points/recharge` | 充值/会员变更 |
| 积分 | GET | `/api/package/list/type/{type}` | `/package/list/type/{type}` | 获取套餐 |
| 邀请 | GET | `/api/points/invite` | `/points/invite` | 获取邀请码 |
| 邀请 | POST | `/api/points/invite` | `/points/invite` | 注册邀请大使 |
| 支付 | POST | `/api/member/pay/order` | `/member/pay/order` | 创建支付订单 |
| 支付 | GET | `http://localhost:8080/member/pay/{orderNo}` | `/member/pay/{orderNo}` | 重新支付，不走代理 |
| 支付 | GET | `/api/api/member/order/status/{orderNo}` | `/api/member/order/status/{orderNo}` | 查询订单状态，疑似多一层 `/api` |
| 反馈 | POST | `/api/feedback/submit` | `/feedback/submit` | 提交反馈 |
| 反馈 | GET | `/api/feedback/user/{userId}/history` | `/feedback/user/{userId}/history` | 用户反馈历史 |
| 反馈 | GET | `/api/feedback/{id}` | `/feedback/{id}` | 反馈详情 |
| 反馈 | PUT | `/api/feedback/update` | `/feedback/update` | 更新反馈 |
| 反馈 | POST | `/api/api/upload` | `/api/upload` | 反馈图片上传，疑似多一层 `/api` |
| 反馈 | GET | `/api/feedback/list` | `/feedback/list` | 反馈列表 |
| 管理 | GET | `/api/admin/usage/records` | `/admin/usage/records` | 使用记录 |
| 编辑器 | POST | `/api/upload` | `/upload` | WangEditor 图片上传，不走 Axios |
| 支付旧跳转 | GET | `/api/alipay/pay/{orderNo}` | `/alipay/pay/{orderNo}` | 组件内直接跳转，需确认 |

