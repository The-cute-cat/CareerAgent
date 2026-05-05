# API接口完整清单

## 接口统计

| 模块 | 接口数量 |
|------|---------|
| 用户管理 | 11个 |
| 聊天对话 | 10个 |
| 用户数据转换 | 1个 |
| 职位匹配 | 1个 |
| 成长规划 | 3个 |
| 代码能力 | 1个 |
| 知识图谱 | 2个 |
| 简历导出 | 1个 |
| 文件解析 | 1个 |
| 问卷测评 | 2个 |
| 支付系统 | 3个 |
| 积分系统 | 7个 |
| 会员管理 | 4个 |
| 交易记录 | 4个 |
| 用户反馈 | 8个 |
| 搜索服务 | 1个 |
| **合计** | **63个** |

---

## 详细接口清单

### 1️⃣ 用户管理模块（11个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/user/register` | POST | 用户注册 |
| `/user/login` | POST | 用户登录 |
| `/user/send-code-register` | POST | 发送注册验证码 |
| `/user/send-code-forget` | POST | 发送重置密码验证码 |
| `/user/forget-password` | POST | 修改密码 |
| `/user/info` | GET | 获取用户信息 |
| `/user/edit` | PUT | 编辑个人资料 |
| `/user/avatar` | POST | 上传头像 |
| `/user/get-basic-info` | GET | 获取用户基础档案信息 |
| `/user/refreshToken` | POST | 刷新Token（双Token机制） |

---

### 2️⃣ 聊天对话模块（10个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/chat/message` | POST | 发送聊天消息（阻塞方式） |
| `/chat/stream/message` | POST | 流式聊天消息 |
| `/chat/stream/message-and-files` | POST | 流式聊天（包含文件上传） |
| `/chat/get-chat-history` | GET | 获取对话历史记录 |
| `/chat/get-user-sessions` | GET | 获取用户对话列表 |
| `/chat/get-session-title` | GET | 获取对话标题 |
| `/chat/clear-session` | DELETE | 清除对话记录 |
| `/chat/update-session-title` | PUT | 更新对话标题 |
| `/chat/get-user-memories` | GET | 获取用户记忆 |
| `/chat/delete-memory` | DELETE | 删除记忆 |

---

### 3️⃣ 用户数据转换模块（1个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/convert/user_form_to_userprofile` | POST | 将用户表单数据转换为用户画像并匹配职位 |

---

### 4️⃣ 职位匹配模块（1个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/matching/job` | POST | 根据用户画像智能推荐职位 |

---

### 5️⃣ 成长规划模块（3个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/report/plan` | POST | 获取个性化成长计划 |
| `/report/check` | POST | 报告完整性检查 |
| `/report/polish` | POST | 内容智能润色 |

---

### 6️⃣ 代码能力评估模块（1个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/codeAbility/evaluate` | POST | 评估GitHub仓库代码能力 |

---

### 7️⃣ 知识图谱模块（2个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/knowledge-graph/analyze/stream` | POST | 流式分析知识点对岗位的影响 |
| `/knowledge-graph/explain/stream` | POST | 流式讲解知识点详细内容 |

---

### 8️⃣ 简历导出模块（1个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/api/resume/export/{format}` | POST | 导出简历（word/pdf/markdown） |

---

### 9️⃣ 文件解析模块（1个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/parse/file` | POST | 解析上传的文件 |

---

### 🔟 问卷测评模块（2个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/question/generate` | GET | 生成职业测评题目 |
| `/question/check_student_answer` | POST | 检查并评估答案 |

---

### 1️⃣1️⃣ 支付系统模块（3个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/alipay/pay/order` | POST | 创建支付订单 |
| `/alipay/pay/{orderNumber}` | GET | 页面支付（跳转支付宝） |
| `/alipay/notify` | POST | 支付宝异步通知回调 |

---

### 1️⃣2️⃣ 积分系统模块（7个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/points/account/{id}` | GET | 获取账户积分余额 |
| `/points/register` | POST | 新用户注册赠送积分 |
| `/points/invite` | POST | 邀请好友获得积分 |
| `/points/register/student` | POST | 学生认证赠送积分 |
| `/points/recharge` | POST | 充值积分 |
| `/points/consume` | POST | 消耗积分 |
| `/points/delete` | POST | 删除/扣除积分 |

---

### 1️⃣3️⃣ 会员管理模块（4个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/member/insert` | POST | 新用户充值会员注册 |
| `/member/insert/new` | POST | 新用户会员首次支付 |
| `/member/{id}` | GET | 获取会员信息 |
| `/member/update/{id}` | GET | 会员续费 |

---

### 1️⃣4️⃣ 交易记录模块（4个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/transaction/{id}` | GET | 获取单条交易记录 |
| `/transaction/list/{id}` | GET | 获取用户所有交易列表 |
| `/transaction/list/points/{id}` | GET | 获取积分交易记录 |
| `/transaction/list/member/{id}` | GET | 获取会员交易记录 |

---

### 1️⃣5️⃣ 用户反馈模块（8个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/feedback/submit` | POST | 用户提交反馈 |
| `/feedback/list` | GET | 查询反馈列表（分页） |
| `/feedback/user/{userId}/history` | GET | 查询用户反馈历史 |
| `/feedback/{id}` | GET | 查询反馈详情 |
| `/feedback/{id}/reply` | POST | 管理员回复反馈 |
| `/feedback/{id}` | DELETE | 删除反馈 |
| `/feedback/type/{type}` | GET | 查询指定类型反馈 |
| `/feedback/update` | PUT | 更新反馈信息 |

---

### 1️⃣6️⃣ 搜索服务模块（1个）

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/search/{keyword}` | GET | 关键词搜索 |

---

## 接口特点分析

### 按HTTP方法分类

| 方法 | 数量 | 说明 |
|------|------|------|
| GET | 18个 | 查询类操作 |
| POST | 35个 | 创建/执行类操作 |
| PUT | 5个 | 更新类操作 |
| DELETE | 5个 | 删除类操作 |

### 按功能特性分类

| 特性 | 接口数 | 说明 |
|------|--------|------|
| 流式响应 | 4个 | SSE流式推送（知识图谱、聊天） |
| 文件上传 | 3个 | 头像、简历、文件解析 |
| 分页查询 | 2个 | 反馈列表、对话列表 |
| 异步回调 | 1个 | 支付宝通知 |
| AI调用 | 12个 | 对接Python AI服务 |

---

## 更新日期

- **生成日期**: 2026-04-16
- **总接口数**: 63个
- **最后更新**: 2026-04-16

