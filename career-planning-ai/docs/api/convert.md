# Convert API 使用文档

> 定位: 将用户表单（UserForm）转换为用于匹配/规划的“学生画像（StudentProfile）”结构化数据  
> 更新时间: 2026-04-16

---

## 一、API 端点总览

| 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|
| POST | `/convert/user_form_to_userprofile` | 将用户表单转换为用户画像 | 阻塞 |

> 所有接口均需认证: `Authorization: Bearer <token>`

---

## 二、通用参数说明

### 认证方式

```http
Authorization: Bearer <token>
```

Python 端通过 `validate_token` 依赖校验 Token：

- Header 缺失或格式错误会返回认证失败
- Token 无效或过期会返回 `code: 401`

### 统一响应格式

**成功：**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": { "...": "..." }
}
```

**失败：**
```json
{
  "code": 401,
  "state": false,
  "msg": "Token验证失败",
  "data": null
}
```

> 注意: HTTP status code 统一返回 200，业务结果以 body 内 `code/state` 判断。

### 常见错误码

| code | 说明 |
|------|------|
| 401 | Token 无效、过期或缺失 |
| 422 | 请求参数校验失败（JSON 结构不合法 / 字段类型错误） |
| 500 | 服务内部异常（LLM 调用失败、结构化失败等） |

---

## 三、接口详情

### 3.1 将用户表单转换为用户画像

```http
POST /convert/user_form_to_userprofile
Content-Type: application/json
Authorization: Bearer <token>
```

#### 3.1.1 请求参数（JSON Body）

请求体为 `UserForm`（见 [src/ai_service/models/user_form.py](../../src/ai_service/models/user_form.py)），字段尽量保持与前端表单一致（camelCase 为主），大部分字段允许为 `null`。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `education` | string \| null | 否 | 学历：高中/专科/本科/硕士/博士/其他 |
| `educationOther` | string \| null | 否 | education 选择“其他”时的补充 |
| `major` | string \| null | 否 | 专业类别 |
| `graduationDate` | string \| null | 否 | 毕业日期，YYYY-MM 格式 |
| `languages` | `LanguageDetail[]` \| null | 否 | 语言能力 |
| `certificates` | string[] \| null | 否 | 证书列表 |
| `certificatesOther` | string \| null | 否 | 证书“其他”补充 |
| `summary` | string \| null | 否 | AI 对用户整体情况的总结描述（黄金语料） |
| `strengths` | string[] \| null | 否 | 优势列表 |
| `weaknesses` | string[] \| null | 否 | 劣势列表 |
| `skills` | `SkillDetail[]` \| null | 否 | 技能列表 |
| `tools` | `ToolDetail[]` \| null | 否 | 工具列表 |
| `codeLinks` | string[] \| null | 否 | 代码仓库链接列表 |
| `projects` | `ProjectExperience[]` \| null | 否 | 项目经历列表 |
| `internships` | `InternshipExperience[]` \| null | 否 | 实习经历列表 |
| `quizDetail` | `QuizDetailItem[]` \| null | 否 | 测评详细（题目与用户答案） |
| `innovation` | string \| null | 否 | 创新表现描述 |
| `targetJob` | string \| null | 否 | 目标岗位 |
| `targetIndustries` | string[] \| null | 否 | 期望行业列表 |
| `priorities` | string[] \| null | 否 | 核心价值观优先级列表（如 技术成长/薪资/稳定） |

##### `LanguageDetail`

见 [src/ai_service/models/user_form_profile.py](../../src/ai_service/models/user_form_profile.py)。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 语种：英语/日语/其他 |
| `level` | string | 是 | 等级/描述（如 CET-6、JLPT N2） |
| `other` | string | 是 | 其他补充信息 |

##### `SkillDetail`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 技能名称 |
| `score` | number | 是 | 技能分数 |

##### `ToolDetail`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 工具名称 |
| `score` | number | 是 | 工具分数 |

##### `ProjectExperience`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `competition` | boolean | 是 | 是否竞赛（注意：该字段在模型中名为 `isCompetition`，但入参别名为 `competition`） |
| `name` | string | 是 | 项目/竞赛名称 |
| `desc` | string | 是 | 项目描述 |

##### `InternshipExperience`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `company` | string | 是 | 实习单位全称（若只有简称则保留简称，不臆造） |
| `role` | string | 是 | 实习岗位名称 |
| `date` | string[] | 否 | 实习日期范围（逻辑上应为 2 个元素：[开始, 结束]；后端会做解析与校验） |
| `desc` | string | 是 | 实习职责与产出（优先动作+结果） |

> `InternshipExperience.date` 在模型侧会尝试解析多种日期格式并归一化；若无法解析可能触发 422。

##### `QuizDetailItem`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 题目类型：`choice` / `open_ended` |
| `question` | string | 是 | 测评题目 |
| `answer` | string | 是 | 用户答案 |

---

#### 3.1.2 响应数据（`data`）

响应 `data` 为“学生画像”结构化结果，生成流程为：

1. 服务端将 `UserForm` 通过 `to_llm_context()` 组织为一段简历风格的文本上下文；
2. 调用 LLM 按 `StudentProfile` 模型进行结构化抽取；
3. 最终返回 `StudentProfile` 的 JSON（序列化字段名为 **snake_case**）。

对应模型：`StudentProfile`（见 [src/ai_service/models/struct_txt.py](../../src/ai_service/models/struct_txt.py)）。为避免遗漏，下列出**全部字段**。

##### `StudentProfile`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `basic_info` | `BasicRequirements` | 是 | 基础信息 |
| `skills` | `ProfessionalSkills` | 是 | 专业技能 |
| `literacy` | `ProfessionalLiteracy` | 是 | 职业素养 |
| `potential` | `DevelopmentPotential` | 是 | 发展潜力 |
| `constraints` | `SpecialConstraints` | 是 | 个人限制 |
| `experience` | `PracticalExperience` | 是 | 实践详情（原始经历证据文本） |

##### `BasicRequirements`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `degree` | string | 是 | 最高学历：专科/本科/硕士/博士 |
| `major` | string | 是 | 所学专业全称及类别 |
| `certificates` | string[] | 是 | 已获得的证书列表 |
| `internship_months` | int | 是 | 累计实习总月数（无则 0） |
| `status` | string | 是 | 求职状态：应届生/在校生/有工作经验 |

##### `ProfessionalSkills`

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `skill_tags` | string[] | 是 | — | 技术栈/核心技能关键词 |
| `tool_tags` | string[] | 是 | — | 工具/平台/软件列表 |
| `domain_knowledge` | int | 是 | 1~5 | 行业领域知识评分 |
| `language_skills` | string[] | 是 | — | 外语等级及口语描述 |
| `project_score` | int | 是 | 1~5 | 项目经验丰富度评分 |

##### `ProfessionalLiteracy`

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `communication` | int | 是 | 1~5 |
| `teamwork` | int | 是 | 1~5 |
| `stress_management` | int | 是 | 1~5 |
| `logic_thinking` | int | 是 | 1~5 |
| `ethics` | int | 是 | 1~5 |

##### `DevelopmentPotential`

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `learning_ability` | int | 是 | 1~5 | 学习能力评分 |
| `innovation` | int | 是 | 1~5 | 创新能力评分 |
| `leadership` | int | 是 | 1~5 | 领导力潜质评分 |
| `career_orientation` | string | 是 | — | 管理型/技术型/创意型/研究型 |
| `adaptability` | int | 是 | 1~5 | 环境适应性评分 |

##### `SpecialConstraints`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `physical_limit` | string \| null | 否 | 生理限制（无则可为 null 或 "无"） |
| `value_conflict` | string \| null | 否 | 价值观限制（如拒绝烟草行业） |
| `env_limit` | string \| null | 否 | 环境限制（如无法出差/加班） |
| `schedule_limit` | string \| null | 否 | 时间习惯限制（如拒绝夜班） |
| `personal_demands` | string \| null | 否 | 其他特殊要求（如必须在某城市） |

##### `PracticalExperience`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_details` | string | 是 | 项目经历详情（文本） |
| `intern_details` | string | 是 | 实习经历详情（文本） |
| `campus_activities` | string | 是 | 校园/实践活动（文本） |
| `competition_exp` | string | 是 | 竞赛获奖详情（文本） |

---

#### 3.1.3 请求示例

```bash
curl -X POST "http://localhost:9000/convert/user_form_to_userprofile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "education": "本科",
    "major": "软件工程",
    "graduationDate": "2026-06",
    "skills": [{"name":"Python","score":0.8}],
    "tools": [{"name":"Git","score":0.7}],
    "targetJob": "后端开发工程师"
  }'
```

#### 3.1.4 成功响应示例（节选）

```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "basic_info": {
      "degree": "本科",
      "major": "软件工程",
      "certificates": ["CET-6"],
      "internship_months": 6,
      "status": "应届生"
    },
    "skills": {
      "skill_tags": ["Python", "Django"],
      "tool_tags": ["Git", "Docker"],
      "domain_knowledge": 3,
      "language_skills": ["CET-6"],
      "project_score": 4
    },
    "literacy": {
      "communication": 4,
      "teamwork": 4,
      "stress_management": 3,
      "logic_thinking": 4,
      "ethics": 5
    },
    "potential": {
      "learning_ability": 4,
      "innovation": 3,
      "leadership": 3,
      "career_orientation": "技术型",
      "adaptability": 4
    },
    "constraints": {
      "physical_limit": "无",
      "value_conflict": "不接受博彩行业",
      "env_limit": "无",
      "schedule_limit": "无",
      "personal_demands": "希望在西安或北京工作"
    },
    "experience": {
      "project_details": "...",
      "intern_details": "...",
      "campus_activities": "...",
      "competition_exp": "..."
    }
  }
}
```

---

## 四、注意事项

1. **该接口为 LLM 结构化抽取**：输出具有一定随机性（已将 temperature 设为 0.1 以降低波动），调用端建议允许重试与容错。
2. **字段命名差异**：入参 `UserForm` 多为 camelCase；出参 `StudentProfile` 为 snake_case。
3. **空值策略**：入参缺失字段不会阻塞请求（除非 JSON 结构错误）；但可能影响画像完整度与下游匹配效果。
