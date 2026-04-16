# Matching API 使用文档

> 定位: 人岗匹配、单岗位匹配解释与岗位聚合能力，供 Java 服务端调用 Python AI 服务  
> 更新时间: 2026-04-14

---

## 一、API 端点总览

| 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|
| POST | `/matching/jobs` | 基于学生画像进行人岗匹配 + 深度差距分析 | 阻塞 |
| GET | `/matching/job_explain/{job_id}/{user_id}` | 基于岗位 ID 和用户 ID 返回单岗位详细匹配解释 | 阻塞 |
| POST | `/matching/job_merge` | 聚合原始岗位并生成标准岗位画像（含向量库同步） | 阻塞 |

> 所有接口均需认证: `Authorization: Bearer <token>`  
> `POST /matching/jobs` 与 `POST /matching/job_merge` 当前**不要求**业务层 `user_id` 参数。  
> `GET /matching/job_explain/{job_id}/{user_id}` 通过**路径参数**传入 `job_id` 和 `user_id`。

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
  "data": { ... }
}
```

**失败：**
```json
{
  "code": <错误码>,
  "state": false,
  "msg": "错误描述",
  "data": null
}
```

> 注意: HTTP status code 统一返回 200，业务结果以 body 内 `code/state` 判断。

### 常见错误码

| code | 说明 |
|------|------|
| 401 | Token 无效、过期或缺失 |
| 422 | 请求参数校验失败（字段缺失 / 类型错误 / 范围不合法） |
| 500 | 服务内部异常（如向量检索、模型分析、数据库处理失败） |

---

## 三、人岗匹配接口

### 3.1 人岗匹配（深度分析）

```http
POST /matching/jobs
Content-Type: application/json
Authorization: Bearer <token>
```

### 请求参数（JSON Body）

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| student_profile | object | 是 | — | 学生画像，结构见下文 |
| recall_top_k | int | 否 | 20 | 向量库初步召回数量 |
| final_top_k | int | 否 | 5 | LLM 深度分析后最终返回数量 |

#### `student_profile` 字段结构

`student_profile` 由 6 个一级模块组成（支持中文 alias 入参）：

| 一级字段 | 子结构说明 |
|----------|------------|
| `基础信息` (`basic_info`) | 学历、专业背景、证书、实习时长、求职状态 |
| `专业技能` (`skills`) | 核心技能标签、工具平台、行业知识评分、语言能力、项目经验评分 |
| `职业素养` (`literacy`) | 沟通、协作、抗压、逻辑、职业道德（1~5） |
| `发展潜力` (`potential`) | 学习、创新、领导力、职业倾向、适应性（1~5） |
| `个人限制` (`constraints`) | 生理限制、价值观限制、环境限制、时间习惯、其他要求 |
| `实践详情` (`experience`) | 项目经历、实习经历、校园实践、竞赛获奖 |

> 评分项存在范围校验（如 1~5），越界会触发 `422`。

### 请求示例

```json
{
  "student_profile": {
    "基础信息": {
      "学历": "本科",
      "专业背景": "软件工程",
      "证书": ["CET-6", "计算机二级"],
      "实习时长": 6,
      "求职状态": "应届生"
    },
    "专业技能": {
      "核心专业技能": ["Vue3", "Java", "Python", "RAG", "LLM", "TypeScript", "CSS3"],
      "工具与平台能力": ["Milvus", "MySQL", "SQLAlchemy", "Git", "Webpack", "Vite"],
      "行业领域知识评分": 4,
      "语言能力": ["CET-6 流利"],
      "项目经验丰富度": 4
    },
    "职业素养": {
      "沟通能力": 4,
      "团队协作": 5,
      "抗压能力": 4,
      "逻辑思维": 5,
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
      "价值观限制": "不接受博彩行业",
      "环境限制": "无",
      "时间习惯限制": "无",
      "其他特殊要求": "希望在西安或北京工作"
    },
    "实践详情": {
      "项目经历详情": "开发了一个基于 AI 的大学生职业规划 Agent 项目，负责全栈开发。",
      "实习经历详情": "在某科技公司实习 6 个月，负责后端数据库优化。",
      "校园/实践活动": "校学生会技术部部长",
      "竞赛获奖详情": "中国高校计算机大赛一等奖"
    }
  },
  "recall_top_k": 10,
  "final_top_k": 3
}
```

### 成功响应示例

```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": [
    {
      "job_id": "job_002",
      "score": 0.9074497818946838,
      "raw_data": {
        "job_id": "job_002",
        "job_name": "前端开发工程师",
        "profiles": {
          "basic_requirements": {
            "degree": "本科",
            "major": "不限",
            "certificates": "无",
            "internship_requirement": "无",
            "experience_years": "应届",
            "special_requirements": "无"
          }
        }
      },
      "deep_analysis": {
        "can_apply": true,
        "score": 92,
        "missing_key_skills": [],
        "gap_matrix": [
          {
            "dimension": "基础要求",
            "required": "本科，应届生，无实习硬性要求，专业不限，CET-4即可",
            "current": "本科软件工程专业，应届生，CET-6（高于要求），无实习限制，完全匹配",
            "gap_analysis": "学历、应届身份、语言证书均满足且优于岗位基础门槛；实习时长 6 个月属额外优势，非必需项",
            "adaptability": "高"
          }
        ],
        "actionable_advice": "重点突出前端架构设计、Vue3+TypeScript 工程实践及上线交付成果。",
        "all_analysis": "整体匹配度高，适合优先投递。"
      }
    }
  ]
}
```

### 返回结果说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `job_id` | string | 岗位唯一标识 |
| `score` | number | 向量召回相似度得分 |
| `raw_data` | object | 岗位画像原始内容 |
| `deep_analysis.can_apply` | boolean | 是否可投递（硬性条件判断） |
| `deep_analysis.score` | int | 综合匹配分（0~100） |
| `deep_analysis.missing_key_skills` | string[] | 关键缺失项 |
| `deep_analysis.gap_matrix` | object[] | 差距矩阵（维度、要求、现状、差距、适配度） |
| `deep_analysis.actionable_advice` | string | 一句话行动建议 |
| `deep_analysis.all_analysis` | string | 总体分析 |

---

### 3.2 单岗位匹配解释

```http
GET /matching/job_explain/{job_id}/{user_id}
Authorization: Bearer <token>
```

### 功能说明

该接口用于根据**岗位画像 ID** 与**用户 ID**，返回该用户对某一岗位的详细匹配解释。  
它适用于“点击岗位详情页后查看个人适配分析”“查看某个岗位为什么适合 / 不适合自己”这类场景。

### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| job_id | int | 是 | 岗位画像 ID |
| user_id | int | 是 | 用户 ID |

### 推荐接口实现

```python
from fastapi import Depends, Path

@router.get("/job_explain/{job_id}/{user_id}", summary="根据岗位ID和用户ID返回岗位匹配解释")
async def job_explain(
    job_id: int = Path(..., description="岗位画像ID", ge=1),
    user_id: int = Path(..., description="用户ID", ge=1),
    _: bool = Depends(validate_token),
):
    """
    根据岗位画像ID和用户ID，返回该用户与目标岗位的详细匹配解释。
    """
    try:
        log.info(f"--- 开始单岗位匹配解释: job_id={job_id}, user_id={user_id} ---")

        result = await analyze_user_job_match(
            job_id=job_id,
            user_id=user_id,
        )

        if "error" in result:
            log.warning(
                f"单岗位匹配解释失败: job_id={job_id}, user_id={user_id}, error={result['error']}"
            )
            return error_msg(f"岗位匹配解释失败: {result['error']}")

        log.info(f"单岗位匹配解释成功: job_id={job_id}, user_id={user_id}")
        return success(result)

    except Exception as e:
        log.error(f"单岗位匹配解释接口异常: {e}", exc_info=True)
        return error_msg(f"单岗位匹配解释接口异常: {str(e)}")
```

### 请求示例

```http
GET /matching/job_explain/65/1
Authorization: Bearer <token>
```

其中：

- `65` 表示岗位画像 ID
- `1` 表示用户 ID

### 成功响应示例

```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "job_profile_text": "{...岗位画像JSON...}",
    "user_profile_text": "{...用户画像JSON...}",
    "analysis": {
      "总体评价总结": "该用户与目标岗位整体匹配度中等偏上，具备一定技术基础，但在项目深度和岗位核心要求上仍有差距。",
      "匹配等级": "中",
      "优势分析": {
        "技术基础": "掌握岗位所需的部分核心技能",
        "学习能力": "具备较强学习潜力"
      },
      "不足分析": {
        "项目经验": "缺少与目标岗位高度相关的完整项目",
        "岗位深度": "部分核心技能停留在基础使用层面"
      },
      "改进建议": {
        "技能补齐": "补充岗位核心技术栈",
        "项目提升": "增加一个高相关项目案例"
      },
      "面试风险点": {
        "项目追问": "可能会被追问项目细节深度",
        "技能深挖": "核心技能可能经不起深入提问"
      },
      "最终建议": "建议先补齐关键技能并准备项目案例后再重点投递。"
    }
  }
}
```

### 精简返回建议

如果前端只需要解释结果，不需要 `job_profile_text` 和 `user_profile_text`，可以把接口中的：

```python
return success(result)
```

改为：

```python
return success(result.get("analysis", {}))
```

这样返回的 `data` 就只有解释内容本身，更适合直接渲染详情页。

### 失败响应示例

```json
{
  "code": 500,
  "state": false,
  "msg": "岗位匹配解释失败：未找到岗位画像，job_id=999",
  "data": null
}
```

### 返回结果说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `job_profile_text` | string | 序列化后的岗位画像原文（调试 / 展示可选） |
| `user_profile_text` | string | 序列化后的用户画像原文（调试 / 展示可选） |
| `analysis.总体评价总结` | string | 对用户与岗位整体匹配关系的总结 |
| `analysis.匹配等级` | string | 匹配等级，如高 / 中 / 低 |
| `analysis.优势分析` | object | 用户与岗位相匹配的优势点 |
| `analysis.不足分析` | object | 用户与岗位之间的主要差距 |
| `analysis.改进建议` | object | 用户后续可以补齐的方向 |
| `analysis.面试风险点` | object | 面试和投递时的风险项 |
| `analysis.最终建议` | string | 综合建议 |

---

## 四、岗位聚合接口

### 4.1 聚合岗位并刷新向量库

```http
POST /matching/job_merge
Authorization: Bearer <token>
```

> 当前接口无请求体参数。

### 处理流程

1. 对岗位数据做聚类（过滤噪声簇和过小簇）
2. 并发调用模型提炼岗位画像
3. 入库 `job_portrait` 并回写岗位关联
4. 从数据库加载画像并同步到向量检索库

### 成功响应示例

```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "message": "岗位合并完成！创建 12 个岗位画像，处理 346 个岗位",
    "portrait_count": 12,
    "processed_jobs": 346,
    "noise_jobs": 28
  }
}
```

### 失败响应示例

```json
{
  "code": 500,
  "state": false,
  "msg": "批量创建岗位画像失败：xxx",
  "data": null
}
```

---

## 五、与 Java AiServiceClient 对应关系

### 5.1 通用调用方式

Matching 接口可通过 `AiServiceClient` 的通用请求方法调用。

| Python 接口 | Java 侧建议调用 | 说明 |
|-------------|----------------|------|
| `POST /matching/jobs` | `postRequest("/matching/jobs", body, "人岗匹配", retry)` | `body` 需包含 `student_profile / recall_top_k / final_top_k` |
| `GET /matching/job_explain/{job_id}/{user_id}` | `getRequest("/matching/job_explain/" + jobId + "/" + userId, Map.of(), "岗位匹配解释", retry)` | 路径参数传 `job_id` 与 `user_id` |
| `POST /matching/job_merge` | `postRequest("/matching/job_merge", Map.of(), "岗位聚合", retry)` | 无业务参数，需带 Bearer Token |

### 5.2 Java 调用示例（示意）

#### 人岗匹配

```java
Map<String, Object> body = new HashMap<>();
body.put("student_profile", studentProfileMap);
body.put("recall_top_k", 20);
body.put("final_top_k", 5);

AiChatResponse resp = aiServiceClient.postRequest(
    "/matching/jobs", body, "人岗匹配", false
);
```

#### 单岗位匹配解释

```java
AiChatResponse resp = aiServiceClient.getRequest(
    "/matching/job_explain/" + jobId + "/" + userId,
    Map.of(),
    "岗位匹配解释",
    false
);
```

---

## 六、注意事项

1. `recall_top_k` 建议大于等于 `final_top_k`，否则深度分析候选不足。
2. `student_profile` 建议使用完整字段，缺失会降低召回与分析质量。
3. `job_explain` 接口依赖岗位画像表和用户画像表中均存在对应数据，若任一侧不存在，将返回业务错误。
4. `job_merge` 会触发聚类、画像生成、数据库写入、向量库同步，属于重操作接口，建议在管理端异步触发。
5. 接口虽然返回 HTTP 200，但仍需严格根据 `code/state` 判定成功与失败。
6. 若 Token 校验失败或请求体不符合模型约束，分别返回 `401` / `422`（在响应体中体现）。

---

## 七、测试

### FastAPI 自动文档

启动服务后访问：

```bash
python main.py
```

打开：`http://localhost:9000/docs`

在 Swagger 中定位 `match` 分组，测试：

- `POST /matching/jobs`
- `GET /matching/job_explain/{job_id}/{user_id}`
- `POST /matching/job_merge`
