# 简历上传接口对接文档

## 接口概述

前端简历上传后，后端解析简历并返回表单数据，前端自动填充表单并提醒用户补充缺失字段。

---

## 接口信息

| 项目 | 内容 |
|------|------|
| 接口地址 | `POST /resume/upload` |
| Content-Type | `multipart/form-data` |
| 请求方式 | POST |

---

## 请求参数

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `file` | File | ✅ | 简历文件（支持 PDF、Word、图片格式） |
| `user_id` | string | ❌ | 用户ID，用于权限验证和存储关联 |
| `overwrite` | string | ❌ | 是否覆盖已有简历，`"true"` 或 `"false"` |

---

## 响应数据结构

```typescript
{
  "code": 200,                    // 状态码：200成功，其他失败
  "message": "简历解析成功",      // 提示信息
  "data": {
    "file_id": "file_xxx",        // 文件存储ID
    "parse_status": "completed",  // 解析状态：pending/processing/completed/failed
    "task_id": "task_xxx",        // 异步任务ID（可选，若解析耗时较长）
    
    // ===========================================
    // 核心新增字段：AI解析后的表单数据
    // ===========================================
    "formData": {
      "education": "本科",                      // 学历
      "educationOther": "",                     // 学历其他说明（当选择"其他"时）
      "major": ["计算机类", "软件工程"],         // 专业（级联数组）
      "graduationDate": "2025-06",              // 预计毕业日期（YYYY-MM）
      
      "languages": [                            // 外语能力列表
        { "type": "英语", "level": "CET-6", "other": "" }
      ],
      
      "certificates": ["CET-6", "软件设计师"],    // 证书列表
      "certificateOther": "",                   // 证书其他说明
      
      "skills": [                               // 技能列表
        { "name": "Java", "credibility": 85 },
        { "name": "Spring Boot", "credibility": 80 }
      ],
      
      "tools": [                                // 工具掌握列表
        { "name": "Git", "proficiency": "熟练" },
        { "name": "Docker", "proficiency": "了解" }
      ],
      
      "codeAbility": {                          // 代码能力
        "links": "https://github.com/xxx"
      },
      
      "projects": [                             // 项目经历
        {
          "isCompetition": false,               // 是否为竞赛项目
          "name": "电商平台后端系统",            // 项目名称
          "desc": "负责订单模块的设计与开发..."  // 项目描述
        }
      ],
      
      "internships": [                          // 实习经历
        {
          "company": "ABC科技有限公司",          // 公司名称
          "role": "Java开发工程师",              // 担任岗位
          "date": [],                           // 实习日期范围（可选）
          "desc": "参与核心业务系统开发..."       // 工作内容描述
        }
      ],
      
      "innovation": "通过引入Redis缓存优化...",  // 创新案例描述
      "targetJob": "后端工程师",                 // 目标岗位（可留空）
      "targetIndustries": ["互联网", "软件开发"] // 期望行业列表（可留空）
    }
  }
}
```

---

## 字段详细说明

### 1. 基本信息

| 字段 | 类型 | 可选值/格式 | 说明 |
|------|------|-------------|------|
| `education` | string | 高中/专科/本科/硕士/博士/其他 | 学历层次 |
| `educationOther` | string | - | 当学历为"其他"时的补充说明 |
| `major` | string[] | 如 `["计算机类", "软件工程"]` | 专业级联选择，第一项为大类 |
| `graduationDate` | string | `YYYY-MM` 格式 | 预计毕业日期 |

### 2. 技能与证书

| 字段 | 类型 | 说明 |
|------|------|------|
| `languages` | array | 每项包含 `type`(语种)、`level`(等级)、`other`(其他说明) |
| `certificates` | string[] | 证书名称列表，如 `["CET-4", "PMP"]` |
| `certificateOther` | string | 当证书选择"其他"时的补充说明 |
| `skills` | array | 每项包含 `name`(技能名)、`credibility`(熟练度 0-100) |
| `tools` | array | 每项包含 `name`(工具名)、`proficiency`(了解/熟练/精通) |
| `codeAbility.links` | string | GitHub/Gitee 仓库链接，多个用逗号分隔 |

### 3. 经历与项目

| 字段 | 类型 | 说明 |
|------|------|------|
| `projects` | array | 项目经历，每项包含 `isCompetition`(是否竞赛)、`name`(名称)、`desc`(描述) |
| `internships` | array | 实习经历，每项包含 `company`(公司)、`role`(岗位)、`date`(日期)、`desc`(描述) |

### 4. 职业意向

| 字段 | 类型 | 说明 |
|------|------|------|
| `targetJob` | string | 目标岗位，如"后端工程师"（解析不出可留空） |
| `targetIndustries` | string[] | 期望行业列表，如 `["互联网", "金融科技"]`（可留空） |
| `innovation` | string | 创新案例描述，从项目经历中提取亮点 |

---

## 后端实现建议

### 1. 字段解析策略

| 字段 | 解析来源 | 置信度策略 |
|------|----------|-----------|
| education | 简历中的"学历"、"学位"栏 | 高（关键词匹配） |
| major | 简历中的"专业"、"主修"栏 | 高（关键词匹配） |
| graduationDate | "毕业时间"、"预计毕业" | 中（日期提取） |
| languages | "英语六级"、"CET-6"、"雅思7.0"等 | 中（正则提取） |
| certificates | "证书"、"资格认证"栏 | 中（关键词+正则） |
| skills | "技能"、"技术栈"、项目描述中的技术名词 | 中（NER+关键词） |
| tools | 项目描述中的工具名 | 低（NER识别） |
| projects | "项目经历"栏 | 高（段落分割） |
| internships | "实习经历"、"工作经历"栏 | 高（段落分割） |
| innovation | 项目描述中的量化成果 | 低（文本生成） |
| targetJob | "求职意向"、"应聘岗位" | 中（关键词匹配） |

### 2. 字段置信度标记（可选扩展）

如需提示用户哪些字段是AI推测的，可添加置信度：

```json
{
  "formData": { ... },
  "formDataConfidence": {
    "education": 0.95,
    "major": 0.92,
    "skills": 0.78,
    "innovation": 0.65
  }
}
```

### 3. 解析失败降级

若简历解析失败或某字段无法识别：

```json
{
  "code": 200,
  "message": "简历上传成功，但部分字段解析失败",
  "data": {
    "file_id": "file_xxx",
    "parse_status": "completed",
    "formData": {
      // 只返回成功解析的字段
      "education": "本科",
      "major": ["计算机类", "软件工程"],
      // 其他字段省略
    }
  }
}
```

### 4. 异步解析模式

若简历解析耗时较长（>5秒），使用异步模式：

```json
{
  "code": 200,
  "message": "简历上传成功，正在解析中",
  "data": {
    "file_id": "file_xxx",
    "parse_status": "processing",
    "task_id": "task_resume_xxx",
    "formData": null  // 解析中暂无数据
  }
}
```

前端将通过 `task_id` 轮询 `/resume/status/{taskId}` 和 `/resume/report/{taskId}` 获取结果。

---

## 前端处理逻辑

1. **上传简历** → 调用 `POST /resume/upload`
2. **接收响应** → 提取 `data.formData`
3. **自动填充** → 将 `formData` 映射到表单各字段
4. **必填检测** → 检查以下必填项是否缺失：
   - 基本信息：学历、专业、预计毕业日期
   - 技能证书：外语能力、专业技能
   - 职业意向：目标岗位、期望行业
5. **提醒用户** → 弹出缺失字段列表，引导补充
6. **用户确认** → 补充完必填项后，通过表单接口提交

---

## 联调检查清单

- [ ] 接口地址和请求方式正确
- [ ] 文件上传使用 `multipart/form-data`
- [ ] 响应中包含 `data.formData` 字段
- [ ] `formData` 中的字段命名与文档一致
- [ ] 数组类型字段（major、skills、projects等）返回数组格式
- [ ] 解析失败时返回空对象或部分数据而非报错
- [ ] 异步解析时返回 `task_id` 供轮询

---

## 示例：完整响应

```json
{
  "code": 200,
  "message": "简历解析成功",
  "data": {
    "file_id": "file_20250319123456",
    "parse_status": "completed",
    "task_id": "task_resume_abc123",
    "formData": {
      "education": "本科",
      "educationOther": "",
      "major": ["计算机类", "软件工程"],
      "graduationDate": "2025-06",
      "languages": [
        { "type": "英语", "level": "CET-6", "other": "" }
      ],
      "certificates": ["CET-6", "软件设计师"],
      "certificateOther": "",
      "skills": [
        { "name": "Java", "credibility": 85 },
        { "name": "Spring Boot", "credibility": 80 },
        { "name": "MySQL", "credibility": 75 },
        { "name": "Redis", "credibility": 70 },
        { "name": "Vue.js", "credibility": 65 },
        { "name": "Docker", "credibility": 60 }
      ],
      "tools": [
        { "name": "Git", "proficiency": "熟练" },
        { "name": "IntelliJ IDEA", "proficiency": "精通" },
        { "name": "VS Code", "proficiency": "熟练" }
      ],
      "codeAbility": {
        "links": "https://github.com/zhangsan"
      },
      "projects": [
        {
          "isCompetition": false,
          "name": "电商平台后端系统",
          "desc": "负责订单模块的设计与开发，使用Spring Boot + MySQL + Redis技术栈，支持高并发场景"
        },
        {
          "isCompetition": true,
          "name": "校园二手交易平台",
          "desc": "获得校级创新创业大赛二等奖，负责整体架构设计和核心功能开发"
        }
      ],
      "internships": [
        {
          "company": "ABC科技有限公司",
          "role": "Java开发工程师",
          "date": [],
          "desc": "参与公司核心业务系统开发，负责订单管理模块的设计与实现"
        }
      ],
      "innovation": "通过引入Redis缓存和数据库索引优化，将系统查询性能提升30%",
      "targetJob": "",
      "targetIndustries": ["互联网", "软件开发"]
    }
  }
}
```

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2025-03-19 | v1.0 | 初始版本，新增 `formData` 字段用于简历解析后自动填充表单 |
