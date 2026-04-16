# AI 服务接口文档

> 更新时间: 2026-04-13
>
> 本文档涵盖除对话接口外的所有 AI 服务接口，对话接口请参考 [CHAT_API.md](./CHAT_API.md)

---

## 一、API 端点总览

| 模块 | 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|------|
| **人岗匹配** | POST | `/matching/jobs` | 基于人物画像进行人岗匹配与深度分析 | 阻塞 |
| | POST | `/matching/job_merge` | 合并岗位 | 阻塞 |
| **报告服务** | POST | `/report/plan` | 生成成长计划 | 阻塞 |
| | POST | `/report/check` | 报告完整性检查 | 阻塞 |
| | POST | `/report/polish` | 段落智能润色 | 阻塞 |
| **题目生成** | POST | `/question/generate` | 生成测试题 | 阻塞 |
| | POST | `/question/check_student_answer` | 检查学生答案 | 阻塞 |
| **文件解析** | POST | `/parse/file` | 解析单个文件 | 阻塞 |
| | POST | `/parse/files` | 解析多个文件 | 阻塞 |
| **知识导师** | POST | `/knowledge_tutor/analyze/stream` | 流式分析知识点对岗位的影响 | SSE |
| | POST | `/knowledge_tutor/explain/stream` | 流式解释知识点内容 | SSE |
| **职业路径** | POST | `/graph_path/promotion_path/single` | 获取垂直晋升路径 | 阻塞 |
| | POST | `/graph_path/transfer_path/single` | 获取换岗路径 | 阻塞 |
| | POST | `/graph_path/career_path/cross_industry` | 获取跨界跃迁路径 | 阻塞 |
| | POST | `/graph_path/goal_path/single` | 目标设定与职业路径规划 | 阻塞 |
| | GET | `/graph_path/health` | 健康检查 | - |
| **数据转换** | POST | `/convert/user_form_to_userprofile` | 用户表单转用户画像 | 阻塞 |
| **代码评估** | POST | `/code-ability/evaluate` | 代码能力评估 | 阻塞 |

> 所有接口均需认证: `Authorization: Bearer <token>`

---

## 二、通用说明

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

> HTTP status code 始终返回 200，业务状态通过 body 中 `code` 和 `state` 字段判断

---

## 三、人岗匹配模块 `/matching`

### 3.1 基于人物画像进行人岗匹配与深度分析

```http
POST /matching/jobs
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 (JSON):**

```json
{
  "student_profile": {
    "基础信息": {
      "学历": "本科",
      "专业背景": "计算机科学与技术",
      "证书": ["CET-6", "计算机二级"],
      "实习时长": 6,
      "求职状态": "应届生"
    },
    "专业技能": {
      "核心专业技能": ["Python", "Java", "SQL"],
      "工具与平台能力": ["Git", "Docker", "Linux"],
      "行业领域知识评分": 4,
      "语言能力": ["英语 CET-6"],
      "项目经验丰富度": 4
    },
    "职业素养": {
      "沟通能力": 4,
      "团队协作": 4,
      "抗压能力": 3,
      "逻辑思维": 4,
      "责任心与职业道德": 5
    },
    "发展潜力": {
      "学习能力": 5,
      "创新能力": 4,
      "领导力潜质": 3,
      "职业倾向性": "技术型",
      "环境适应性": 4
    },
    "个人限制": {
      "生理限制": "无",
      "价值观限制": null,
      "环境限制": null,
      "时间习惯限制": null,
      "其他特殊要求": null
    },
    "实践详情": {
      "项目经历详情": "在电商系统中担任后端开发，负责订单模块设计与开发",
      "实习经历详情": "在某科技公司实习，担任后端实习生",
      "校园_实践活动": "担任技术社团副社长",
      "竞赛获奖详情": "获得省级编程竞赛二等奖"
    }
  },
  "recall_top_k": 20,
  "final_top_k": 5
}
```

**参数说明:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| student_profile | object | **是** | — | 学生人物画像数据 |
| recall_top_k | int | 否 | 20 | 向量库初步召回数量 |
| final_top_k | int | 否 | 5 | Agent 最终深度分析返回数量 |

**学生画像字段说明:**

| 一级字段 | 二级字段 | 类型 | 说明 |
|---------|---------|------|------|
| 基础信息 | 学历 | string | 当前最高学历：专科/本科/硕士/博士 |
| | 专业背景 | string | 所学专业全称及类别 |
| | 证书 | string[] | 已获得的证书列表 |
| | 实习时长 | int | 累计实习总月数 |
| | 求职状态 | string | 应届生/在校生/有工作经验 |
| 专业技能 | 核心专业技能 | string[] | 掌握的技术栈关键词列表 |
| | 工具与平台能力 | string[] | 掌握的软件、工具、平台列表 |
| | 行业领域知识评分 | int | 对目标行业的了解程度评分 1-5 |
| | 语言能力 | string[] | 外语等级及口语水平描述 |
| | 项目经验丰富度 | int | 项目经验的复杂度与完整度评分 1-5 |
| 职业素养 | 沟通能力 | int | 沟通表达与协调能力评分 1-5 |
| | 团队协作 | int | 团队配合与协作精神评分 1-5 |
| | 抗压能力 | int | 面对压力时的情绪调节与执行力评分 1-5 |
| | 逻辑思维 | int | 分析问题与解决问题的逻辑性评分 1-5 |
| | 责任心与职业道德 | int | 工作态度与职业操守评分 1-5 |
| 发展潜力 | 学习能力 | int | 自学能力与知识迁移能力评分 1-5 |
| | 创新能力 | int | 打破常规与提出新方案的能力评分 1-5 |
| | 领导力潜质 | int | 组织能力与影响力潜质评分 1-5 |
| | 职业倾向性 | string | 管理型/技术型/创意型/研究型 |
| | 环境适应性 | int | 对新环境、新岗位的适应速度评分 1-5 |
| 个人限制 | 生理限制 | string | 特殊生理限制，无则填"无" |
| | 价值观限制 | string | 不能接受的行业或公司文化 |
| | 环境限制 | string | 无法接受的环境 |
| | 时间习惯限制 | string | 无法接受的时间安排 |
| | 其他特殊要求 | string | 其他特殊要求 |
| 实践详情 | 项目经历详情 | string | 详细描述项目经历 |
| | 实习经历详情 | string | 详细描述实习经历 |
| | 校园_实践活动 | string | 社团、志愿活动等描述 |
| | 竞赛获奖详情 | string | 参加过的比赛、获得的奖项 |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": [
    {
      "job_id": "job_001",
      "job_name": "后端开发工程师",
      "match_score": 0.85,
      "analysis": "该候选人与岗位匹配度较高..."
    }
  ]
}
```

---

### 3.2 合并岗位

```http
POST /matching/job_merge
Authorization: Bearer <token>
```

**说明:** 该接口用于合并重复或相似的岗位数据。

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": { "message": "岗位合并完成" }
}
```

---

## 四、报告服务模块 `/report`

### 4.1 生成成长计划

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
| cache_enabled | bool | 否 | true | 是否启用缓存 |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "plan_id": "plan_001",
    "stages": [
      {
        "stage": "短期（1-3个月）",
        "goals": ["掌握 Spring Boot 基础", "完成 2 个实战项目"],
        "actions": ["学习 Spring Boot 官方文档", "参与开源项目"]
      }
    ],
    "created_at": "2026-04-13T10:00:00"
  }
}
```

---

### 4.2 报告完整性检查

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
1. 人岗匹配四维度量化分析（基础要求、职业技能、职业素养、发展潜力）
2. 职业发展路径规划（垂直晋升或换岗转型）
3. 分阶段行动计划（短期、中期）
4. 评估周期与指标

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "is_complete": true,
    "check_results": [
      {
        "dimension": "人岗匹配分析",
        "is_present": true,
        "description": "包含四维度量化分析",
        "suggestion": null
      },
      {
        "dimension": "职业发展路径",
        "is_present": true,
        "description": "包含垂直晋升路径规划",
        "suggestion": null
      }
    ],
    "missing_items": [],
    "overall_score": 85,
    "summary": "报告整体结构完整，内容详实，具备较强的可操作性"
  }
}
```

**失败响应 (内容过短):**
```json
{
  "code": 400,
  "state": false,
  "msg": "报告内容过短，至少需要50个字符",
  "data": null
}
```

---

### 4.3 段落智能润色

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
| match_analysis | 人岗匹配分析 | 强制四维度分析结构 |
| action_plan | 行动计划 | 确保 SMART 原则 |
| other | 通用润色 | 精炼、专业、有指导意义 |

**核心约束:**
- 防幻觉：不能捏造用户没有的技能、证书或经历
- 维度红线：匹配分析必须从 4 个维度进行
- 质量红线：内容必须具备可操作性和可解释性

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "original_content": "该候选人具有较强的编程能力，熟悉多种编程语言。",
    "polished_content": "该候选人在编程能力方面表现突出，精通 Python、Java 等主流编程语言，具备扎实的算法基础和良好的代码规范意识。",
    "report_type": "match_analysis",
    "length_before": 24,
    "length_after": 58
  }
}
```

---

## 五、题目生成模块 `/question`

### 5.1 生成测试题

```http
POST /question/generate
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| content | string | 否 | null | 技能或工具名称 |
| question_type | string | 否 | null | 题目类型：`skill` / `tool` |
| cache_enabled | bool | 否 | false | 是否启用缓存 |

**题目类型说明:**

| 类型 | 说明 |
|------|------|
| skill | 基于技能生成测试题 |
| tool | 基于工具生成测试题 |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": [
    {
      "question": "Python 中列表和元组的主要区别是什么？",
      "options": ["A. 列表可变，元组不可变", "B. 列表不可变，元组可变", "C. 没有区别", "D. 元组只能存储数字"],
      "answer": "A",
      "explanation": "列表是可变序列，元组是不可变序列..."
    }
  ]
}
```

---

### 5.2 检查学生答案

```http
POST /question/check_student_answer
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| questions | string | 否 | 题目内容（JSON 字符串） |
| evaluation_criteria | string | 否 | 评分标准 |
| student_answer | string | 否 | 学生答案 |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "total_score": 85,
    "details": [
      {
        "question_id": 1,
        "score": 20,
        "feedback": "回答正确，理解到位"
      }
    ],
    "summary": "整体表现良好，基础扎实"
  }
}
```

---

## 六、文件解析模块 `/parse`

### 6.1 解析单个文件

```http
POST /parse/file
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| file | file | **是** | — | 上传的文件 |
| cache_enabled | bool | 否 | true | 是否启用缓存 |

**支持的文件类型:** PDF、DOCX、PNG、JPG、JPEG

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "education": "本科",
    "major": "计算机科学与技术",
    "skills": ["Python", "Java", "SQL"],
    "experience": [
      {
        "company": "某科技公司",
        "position": "后端开发实习生",
        "duration": "2025.06 - 2025.12"
      }
    ]
  }
}
```

---

### 6.2 解析多个文件

```http
POST /parse/files
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| files | file[] | **是** | — | 上传的文件列表 |
| cache_enabled | bool | 否 | true | 是否启用缓存 |

**并发限制:** 最多 3 个文件同时处理

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": [
    {
      "file_name": "resume_1.pdf",
      "education": "本科",
      "major": "软件工程"
    },
    {
      "file_name": "resume_2.pdf",
      "education": "硕士",
      "major": "计算机科学"
    }
  ]
}
```

---

## 七、知识导师模块 `/knowledge_tutor`

### 7.1 流式分析知识点对岗位的影响（SSE）

```http
POST /knowledge_tutor/analyze/stream
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_node | string | **是** | 当前知识点名称 |
| job_id | int | **是** | 目标岗位 ID |
| user_id | int | **是** | 用户 ID |
| graph_context | string | 否 | 图谱关系（前置/后续/关联） |
| industry_data | string | 否 | 行业数据 |

**用途:** 用于"岗位影响"标签页

**SSE 响应格式:**
```
event: content
data: {"type":"content","text":"该知识点对岗位的影响分析..."}
id: 1

event: content
data: {"type":"content","text":"在求职过程中..."}
id: 2

event: done
data: {"status":"completed"}
id: 3
```

**SSE 事件说明:**

| event 类型 | data 格式 | 含义 |
|-----------|----------|------|
| `content` | `{"type":"content","text":"..."}` | 文本片段 |
| `done` | `{"status":"completed"}` | 流传输结束 |
| `error` | `{"error":"..."}` | 发生错误 |

---

### 7.2 流式解释知识点内容（SSE）

```http
POST /knowledge_tutor/explain/stream
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current_node | string | **是** | 当前知识点名称 |
| job_id | int | **是** | 目标岗位 ID |
| user_id | int | **是** | 用户 ID |
| graph_context | string | 否 | 图谱关系 |

**用途:** 用于"知识精讲"标签页

**SSE 响应格式:** 同 7.1

---

## 八、职业路径模块 `/graph_path`

### 8.1 获取垂直晋升路径

```http
POST /graph_path/promotion_path/single
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 (JSON):**
```json
{
  "job_id": "job_001"
}
```

**参数说明:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| job_id | string | **是** | 起点岗位 ID |

**说明:** 垂直晋升路径为同一微赛道内深挖技能与跃迁（每跳不跨微/宏社区，salary_gain>0），支持 1-5 跳。

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "start_job_id": "job_001",
    "start_job_name": "初级后端工程师",
    "paths": [
      {
        "path_id": "path_001",
        "path_type": "vertical",
        "total_steps": 2,
        "total_routing_cost": 0.35,
        "steps": [
          {
            "step_index": 1,
            "from_job_id": "job_001",
            "from_job_name": "初级后端工程师",
            "to_job_id": "job_002",
            "to_job_name": "中级后端工程师",
            "jaccard_high": 0.85,
            "cos_low": 0.75,
            "salary_gain": 0.25,
            "skill_gaps": [
              {
                "gap_key": "hard:微服务架构",
                "gap_type": "hard_skill",
                "gap_name": "微服务架构",
                "category": "架构设计",
                "target_score": 4
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

### 8.2 获取换岗路径

```http
POST /graph_path/transfer_path/single
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 (JSON):**
```json
{
  "job_id": "job_001"
}
```

**说明:** 换岗路径为同一宏观行业内不同微赛道（每跳跨微社区且不跨宏社区），支持 1-2 跳。

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "start_job_id": "job_001",
    "start_job_name": "前端工程师",
    "paths": [
      {
        "path_id": "path_002",
        "path_type": "lateral",
        "total_steps": 1,
        "total_routing_cost": 0.45,
        "steps": [
          {
            "step_index": 1,
            "from_job_id": "job_001",
            "from_job_name": "前端工程师",
            "to_job_id": "job_003",
            "to_job_name": "Node.js 后端工程师",
            "jaccard_high": 0.65,
            "cos_low": 0.70,
            "salary_gain": 0.15,
            "skill_gaps": []
          }
        ]
      }
    ]
  }
}
```

**失败响应 (未找到路径):**
```json
{
  "code": 500,
  "detail": "未找到符合换岗条件的路径"
}
```

---

### 8.3 获取跨界跃迁路径

```http
POST /graph_path/career_path/cross_industry
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 (JSON):**
```json
{
  "job_id": "job_001"
}
```

**说明:** 跨界跃迁路径中至少一跳跨宏观社区（is_cross_macro=true），支持 1-2 跳。

**成功响应:** 结构同 8.1，`path_type` 为 `cross_industry`

---

### 8.4 目标设定与职业路径规划

```http
POST /graph_path/goal_path/single
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 (JSON):**
```json
{
  "start_job_id": "job_001",
  "target_job_id": "job_010",
  "limit_paths": 10
}
```

**参数说明:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| start_job_id | string | **是** | — | 起点岗位 ID |
| target_job_id | string | **是** | — | 目标岗位 ID |
| limit_paths | int | 否 | 10 | 返回最大候选路径条数（1~50） |

**说明:** 给定起点岗位与目标岗位，返回多条候选发展路径（总成本低的优先）。

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "start_job_id": "job_001",
    "start_job_name": "初级后端工程师",
    "paths": [
      {
        "path_id": "path_003",
        "path_type": "vertical",
        "total_steps": 3,
        "total_routing_cost": 0.55,
        "steps": [...]
      }
    ]
  }
}
```

**失败响应 (未找到路径):**
```json
{
  "code": 500,
  "detail": "未找到从起点到目标的可达路径"
}
```

---

### 8.5 健康检查

```http
GET /graph_path/health
Authorization: Bearer <token>
```

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "status": "healthy",
    "service": "graph_path"
  }
}
```

---

## 九、数据转换模块 `/convert`

### 9.1 用户表单转用户画像

```http
POST /convert/user_form_to_userprofile
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体 (JSON):**
```json
{
  "education": "本科",
  "major": "计算机科学与技术",
  "graduationDate": "2026-06",
  "languages": [
    {"name": "英语", "level": "CET-6"}
  ],
  "certificates": ["计算机二级", "软考中级"],
  "skills": [
    {"name": "Python", "level": "熟练", "years": 2}
  ],
  "tools": [
    {"name": "Git", "level": "熟练"}
  ],
  "codeLinks": ["https://github.com/user/project"],
  "projects": [
    {
      "name": "电商系统",
      "role": "后端开发",
      "description": "负责订单模块开发"
    }
  ],
  "internships": [
    {
      "company": "某科技公司",
      "position": "后端实习生",
      "duration": "6个月"
    }
  ],
  "targetJob": "后端开发工程师",
  "targetIndustries": ["互联网", "金融科技"],
  "priorities": ["技术成长", "薪资", "稳定"]
}
```

**UserForm 字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| education | string | 学历：高中/专科/本科/硕士/博士/其他 |
| major | string | 专业类别 |
| graduationDate | string | 毕业日期，YYYY-MM 格式 |
| languages | array | 语言能力列表 |
| certificates | string[] | 证书列表 |
| skills | array | 技能列表 |
| tools | array | 工具列表 |
| codeLinks | string[] | 代码仓库链接列表 |
| projects | array | 项目经历列表 |
| internships | array | 实习经历列表 |
| quizDetail | array | 测评详细信息 |
| innovation | string | 创新表现描述 |
| targetJob | string | 目标岗位 |
| targetIndustries | string[] | 期望行业列表 |
| priorities | string[] | 核心价值观优先级列表 |
| summary | string | AI 对用户整体情况的总结 |
| strengths | string[] | 优势列表 |
| weaknesses | string[] | 劣势列表 |

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "data": {
    "profile_id": "profile_001",
    "basic_info": {
      "education": "本科",
      "major": "计算机科学与技术"
    },
    "skills": ["Python", "Java", "SQL"],
    "experience_level": "中级",
    "career_orientation": "技术型"
  }
}
```

---

## 十、代码能力评估模块 `/code-ability`

### 10.1 代码能力评估

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
| use_ai | bool | 否 | true | 是否使用 AI 大模型进行深度分析 |
| cache_enabled | bool | 否 | true | 是否使用缓存 |

**耗时说明:**
- 基础评分：约 3-5 秒
- 开启 AI 分析：约 8-15 秒

**成功响应:**
```json
{
  "code": 200,
  "state": true,
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

**失败响应 (URL 无效):**
```json
{
  "code": 400,
  "state": false,
  "msg": "无效的 GitHub/Gitee URL",
  "data": null
}
```

---

## 十一、常见错误码

| code | 说明 |
|------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | Token 无效或过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |

---

## 十二、注意事项

1. **缓存机制**: 多个接口支持 `cache_enabled` 参数，开启后可显著提升响应速度
2. **并发限制**: 文件解析接口最多同时处理 3 个文件
3. **SSE 连接**: 流式接口在客户端断连时会自动停止传输并释放资源
4. **时间格式**: 所有时间字段使用 ISO 8601 格式（如 `2026-04-13T10:30:00`）
5. **文件类型**: 支持的文件类型通过魔数检测真实类型，防止文件伪装攻击
