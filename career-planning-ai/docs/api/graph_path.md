# Graph Path API 使用文档

> 定位: 职业路径（基于 Neo4j 职业图）的路径检索与目标路径规划接口  
> 更新时间: 2026-04-16

---

## 一、API 端点总览

| 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|
| POST | `/graph_path/promotion_path/single` | 获取垂直晋升路径（1-5 跳） | 阻塞 |
| POST | `/graph_path/transfer_path/single` | 获取换岗路径（1-2 跳） | 阻塞 |
| POST | `/graph_path/career_path/cross_industry` | 获取跨界跃迁路径（1-2 跳） | 阻塞 |
| POST | `/graph_path/goal_path/single` | 目标设定与职业路径规划（start→target，多路径） | 阻塞 |
| GET | `/graph_path/health` | 健康检查 | — |

### 认证说明

> 所有接口均需认证: `Authorization: Bearer <token>`

- `graph_path` 路由已在路由级别强制注入 `validate_token`，因此**必须**携带 `Authorization` Header。
- Header 缺失、格式错误或 Token 无效/过期时会返回 `code: 401`。

---

## 二、通用说明

### 统一响应格式

本模块所有接口最终都返回统一包裹结构（即使 FastAPI/Starlette 层抛出异常，HTTP status 也会被统一处理为 200，业务状态以 body 为准）：

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
  "code": 404,
  "state": false,
  "msg": "未找到符合换岗条件的路径",
  "data": null
}
```

### 常见错误码

| code | 说明 |
|------|------|
| 401 | Token 无效、过期或缺失 |
| 404 | 未找到路径（仅部分接口会对空结果主动返回 404） |
| 422 | 请求参数校验失败（字段缺失 / 类型错误 / 范围不合法） |
| 500 | 服务内部错误（Neo4j/查询/构造数据失败等） |

---

## 三、数据结构（返回 `data`）

`data` 字段为 `CareerPathBundle`（见 [src/ai_service/models/career_graph.py](../../src/ai_service/models/career_graph.py)）。为了避免前端/Java 端遗漏字段，下面按层级列出**全部字段**。

> 说明：字段的 “可空/可缺省” 由 Pydantic 模型决定；当图数据未写入对应属性时，相关字段可能为 `null`（或数值字段在部分步骤中被兜底为 `0.0`）。

### 3.1 `CareerPathBundle`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `start_job_id` | string | 是 | 起点岗位 ID（来自请求中的 `job_id` 或 `start_job_id`） |
| `start_job_name` | string \| null | 否 | 起点岗位名称（来自 Neo4j `Job.job_name`，查不到则为 null） |
| `paths` | `CareerPath[]` | 否 | 候选路径列表（可能为空数组） |

### 3.2 `CareerPath`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path_id` | string | 是 | 路径唯一 Key（当前实现为随机生成，如 `path_1a2b3c4d`，**不同调用不稳定**） |
| `path_type` | string | 是 | 路径类型：`vertical` / `lateral` / `cross_industry` |
| `total_steps` | int | 是 | 跳跃次数（等于 `steps.length`） |
| `total_routing_cost` | number | 是 | 路径总成本（sum(每条边 `final_routing_cost`)） |
| `steps` | `TransitionStep[]` | 是 | 路径步骤列表（每一步对应一条 `EVOLVE_TO` 边） |
| `build_run_evidence` | `BuildRunEvidence` \| null | 否 | 离线构图 Run 的证据快照（若边上没有 `build_run_id` 则为 null） |

#### `path_type` 取值口径

- `vertical`：垂直晋升（通常不跨 micro/macro 社区，且 `salary_gain > 0`）
- `lateral`：横向转岗（通常同 macro 不同 micro，且每跳跨 micro 不跨 macro）
- `cross_industry`：跨界跃迁（路径中至少一跳跨 macro）

> 对“跨界”的最终证据以 `steps[].edge_evidence.is_cross_micro/is_cross_macro` 为准。

### 3.3 `TransitionStep`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `step_index` | int | 是 | 步骤序号（从 1 开始） |
| `from_job_id` | string | 是 | 起点岗位 ID |
| `from_job_name` | string | 是 | 起点岗位名称（可能为空字符串） |
| `to_job_id` | string | 是 | 目标岗位 ID |
| `to_job_name` | string | 是 | 目标岗位名称（可能为空字符串） |
| `jaccard_high` | number | 是 | 技能重合度指标（来自边属性 `jaccard_high`，缺失时兜底为 `0.0`） |
| `cos_low` | number | 是 | 文本/背景相似度指标（来自边属性 `cos_low`，缺失时兜底为 `0.0`） |
| `salary_gain` | number | 是 | 薪资增益指标（来自边属性 `salary_gain`，缺失时兜底为 `0.0`） |
| `from_job_snapshot` | `JobSnapshot` \| null | 否 | 起点岗位节点快照（通常存在） |
| `to_job_snapshot` | `JobSnapshot` \| null | 否 | 目标岗位节点快照（通常存在） |
| `skill_gaps` | `UniversalGapInfo[]` | 否 | 为完成该步跃迁需要补齐的硬技能缺口列表（可能为空数组） |
| `edge_evidence` | `EvolveEdgeEvidence` \| null | 否 | 对应 `EVOLVE_TO` 边的证据快照（通常存在） |

### 3.4 `UniversalGapInfo`（技能缺口，纯证据）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `gap_key` | string | 否 | 缺口唯一 Key（当前实现为 `hard:{competency_name}`） |
| `gap_type` | string | 否 | 缺口类型：`hard_skill`（当前实现只输出该值） |
| `gap_name` | string | 否 | 缺口名称（能力名，来自 `Competency.name`） |
| `category` | string | 否 | 能力分类（来自 `Competency.category`，可能为空字符串） |
| `target_score` | int | 否 | 岗位对该能力的最低评分要求（来自 `REQUIRES.min_score`，缺失则为 0） |
| `original_context` | string | 否 | 岗位 JD 原话/上下文证据（来自 `REQUIRES.context`，可能为空字符串） |
| `importance_weight` | number \| null | 否 | 重要性权重（来自 `REQUIRES.weight`） |
| `local_weight` | number \| null | 否 | 局部权重快照（来自 `REQUIRES.local_weight`） |
| `idf_weight` | number \| null | 否 | 全局 IDF 权重（来自 `REQUIRES.idf_weight`） |
| `df` | int \| null | 否 | 覆盖岗位数（来自 `REQUIRES.df`） |
| `total_jobs` | int \| null | 否 | 统计口径岗位总数（来自 `REQUIRES.total_jobs`） |
| `prevalence` | number \| null | 否 | 覆盖率 `df/total_jobs`（来自 `REQUIRES.prevalence`） |
| `idf_run_id` | string \| null | 否 | IDF 证据来自的离线 Run（来自 `REQUIRES.idf_run_id`） |

### 3.5 `BuildRunEvidence`（Run 级证据）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `run_id` | string | 是 | 离线构图 Run ID（来自 `BuildRun.id`） |
| `status` | string \| null | 否 | Run 状态（如 running/completed，来自 `BuildRun.status`） |
| `meta_json` | string \| null | 否 | Run 元数据原文（JSON 字符串，来自 `BuildRun.meta_json`） |

### 3.6 `EvolveEdgeEvidence`（边级证据，全量快照）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `from_job_id` | string | 是 | 边起点岗位 ID |
| `to_job_id` | string | 是 | 边终点岗位 ID |
| `final_routing_cost` | number \| null | 否 | 综合路由成本（边权重，来自 `EVOLVE_TO.final_routing_cost`） |
| `transfer_cost` | number \| null | 否 | 换岗成本分量（来自 `EVOLVE_TO.transfer_cost`） |
| `salary_gain` | number \| null | 否 | 薪资增益（来自 `EVOLVE_TO.salary_gain`） |
| `jaccard_high` | number \| null | 否 | 技能重合度（来自 `EVOLVE_TO.jaccard_high`） |
| `cos_low` | number \| null | 否 | 相似度（来自 `EVOLVE_TO.cos_low`） |
| `pareto_rank` | int \| null | 否 | 帕累托前沿层级（来自 `EVOLVE_TO.pareto_rank`） |
| `pareto_group_size` | int \| null | 否 | 候选边集合规模（来自 `EVOLVE_TO.pareto_group_size`） |
| `pareto_front_size` | int \| null | 否 | 当前前沿边数（来自 `EVOLVE_TO.pareto_front_size`） |
| `is_cross_macro` | boolean \| null | 否 | 是否跨宏观社区（来自 `EVOLVE_TO.is_cross_macro`） |
| `is_cross_micro` | boolean \| null | 否 | 是否跨微观社区（来自 `EVOLVE_TO.is_cross_micro`） |
| `base_attraction` | number \| null | 否 | 基础吸引力（来自 `EVOLVE_TO.base_attraction`） |
| `rank_penalty` | number \| null | 否 | 帕累托等级惩罚分量（来自 `EVOLVE_TO.rank_penalty`） |
| `cross_penalty` | number \| null | 否 | 跨界惩罚分量（来自 `EVOLVE_TO.cross_penalty`） |
| `build_run_id` | string \| null | 否 | 该边来自哪个离线构图 Run（来自 `EVOLVE_TO.build_run_id`） |
| `lineage_json` | string \| null | 否 | 离线决策快照原文（JSON 字符串，来自 `EVOLVE_TO.lineage_json`） |

### 3.7 `JobSnapshot`（岗位快照）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `job_id` | string | 是 | 岗位 ID（来自 `Job.id`） |
| `job_name` | string \| null | 否 | 岗位名称（来自 `Job.job_name`） |
| `attributes` | `GraphNodeJob` | 是 | 岗位节点结构化属性快照（见下文） |

### 3.8 `GraphNodeJob`（岗位节点属性，完整字段）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 岗位ID，唯一标识 |
| `job_name` | string | 岗位名称 |
| `macro_community_id` | int | 宏观行业社区标签 |
| `micro_community_id` | int | 细分职业社区标签 |
| `min_degree` | int | 最低学历要求（数值化） |
| `demand_rank` | int | 市场需求程度（序数化） |
| `trend_rank` | int | 行业趋势（序数化） |
| `salary_rank` | int | 薪资竞争力等级（序数化） |
| `min_experience` | int | 最低工作经验年限 |
| `major` | string | 专业要求 |
| `industry` | string | 所属行业 |
| `career_orientation` | string | 职业发展方向 |
| `comm_desc` | string | 沟通能力描述 |
| `team_desc` | string | 团队合作能力描述 |
| `stress_desc` | string | 抗压能力描述 |
| `logic_desc` | string | 逻辑思维能力描述 |
| `learn_desc` | string | 学习能力描述 |
| `innov_desc` | string | 创新能力描述 |
| `lead_desc` | string | 领导能力描述 |
| `adapt_desc` | string | 适应能力描述 |
| `ethics_desc` | string | 职业道德描述 |
| `project_reqs` | string | 项目需求描述 |
| `intern_reqs` | string | 实习需求描述 |
| `special_reqs` | string | 特殊要求描述 |
| `last_build_run_id` | string \| null | 最后一次构建图的 Run ID |
| `last_build_ts` | string \| null | 最后一次构建图的时间戳 |

---

## 四、接口详情

### 4.1 获取垂直晋升路径（1-5跳）

```http
POST /graph_path/promotion_path/single
Content-Type: application/json
Authorization: Bearer <token>
```

**请求参数（JSON Body）：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `job_id` | string | 是 | 起点岗位 ID |

**约束口径（来自 Neo4j 查询条件）：**

- 路径长度：1~5 跳（`EVOLVE_TO*1..5`）
- 目标岗位与起点岗位属于**同 micro 社区**（`target.micro_community_id = start.micro_community_id`）
- 路径上每条边满足：
  - `is_cross_micro = false`
  - `is_cross_macro = false`
  - `salary_gain > 0`
- 排序：按 `total_cost = sum(final_routing_cost)` 升序

**响应 `data`：**`CareerPathBundle`

> 注意：该接口即使没有找到任何路径，也会返回 `code=200` 且 `paths=[]`（不会返回 404）。

**示例：**
```bash
curl -X POST "http://localhost:9000/graph_path/promotion_path/single" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"job_001"}'
```

---

### 4.2 获取换岗路径（1-2跳）

```http
POST /graph_path/transfer_path/single
Content-Type: application/json
Authorization: Bearer <token>
```

**请求参数（JSON Body）：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `job_id` | string | 是 | 起点岗位 ID |

**约束口径：**

- 路径长度：1~2 跳
- 目标岗位与起点岗位属于**同 macro 社区**且 **micro 不同**：
  - `target.macro_community_id = start.macro_community_id`
  - `target.micro_community_id <> start.micro_community_id`
- 路径上每条边满足：
  - `is_cross_micro = true`
  - `is_cross_macro = false`
- 排序：按 `total_cost` 升序

**空结果处理：**

- 若未找到路径：返回 `code=404`，`msg="未找到符合换岗条件的路径"`。

**示例：**
```bash
curl -X POST "http://localhost:9000/graph_path/transfer_path/single" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"job_001"}'
```

---

### 4.3 获取跨界跃迁路径（1-2跳）

```http
POST /graph_path/career_path/cross_industry
Content-Type: application/json
Authorization: Bearer <token>
```

**请求参数（JSON Body）：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `job_id` | string | 是 | 起点岗位 ID |

**约束口径：**

- 路径长度：1~2 跳
- 目标岗位与起点岗位属于**不同 macro 社区**：`target.macro_community_id <> start.macro_community_id`
- 路径中至少存在一条边满足：`is_cross_macro = true`
- 排序：按 `total_cost` 升序

**空结果处理：**

- 若未找到路径：返回 `code=404`，`msg="未找到符合跨界条件的路径"`。

---

### 4.4 目标设定与职业路径规划（start→target，多路径）

```http
POST /graph_path/goal_path/single
Content-Type: application/json
Authorization: Bearer <token>
```

**请求参数（JSON Body）：**

| 参数名 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|--------|------|------|--------|------|------|
| `start_job_id` | string | 是 | — | — | 起点岗位 ID |
| `target_job_id` | string | 是 | — | — | 目标岗位 ID |
| `limit_paths` | int | 否 | 10 | 1~50 | 返回最大候选路径条数 |

**规划口径：**

- 路径长度：1~10 跳（查询侧 max_hops=10，内部上限可能被服务端限制）
- 仅沿 `EVOLVE_TO` 方向
- 约束 simple path：路径内节点不重复（避免环）
- 返回多条候选路径，按 `total_cost` 升序
- `path_type`：根据路径边属性推断：
  - 任意边 `is_cross_macro=true` → `cross_industry`
  - 否则任意边 `is_cross_micro=true` → `lateral`
  - 否则 → `vertical`

**空结果处理：**

- 若未找到从起点到目标的可达路径：返回 `code=404`，`msg="未找到从起点到目标的可达路径"`。

**示例：**
```bash
curl -X POST "http://localhost:9000/graph_path/goal_path/single" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_job_id":"job_001",
    "target_job_id":"job_999",
    "limit_paths":10
  }'
```

---

### 4.5 健康检查

```http
GET /graph_path/health
Authorization: Bearer <token>
```

**成功响应：**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "status": "healthy",
    "service": "graph_path"
  }
}
```

---

## 五、补充说明（实现细节口径）

1. **技能缺口的累计基线**：对只提供 `job_id` 的接口，服务端以“起点岗位的 REQUIRES 技能集合”为 baseline，并在路径推进中把每一站目标岗位的 REQUIRES 也加入 `known_skills`，从而使后续步骤的 `skill_gaps` 更接近“循序渐进补齐”的结果。
2. **起点/终点岗位属性快照**：`from_job_snapshot/to_job_snapshot.attributes` 优先从 Neo4j 读取完整 `Job` 节点属性并映射为 `GraphNodeJob`；查不到时会只回填 `id/job_name`，其余字段为默认值。
3. **404 与空数组差异**：
   - `promotion_path/single`：不主动抛 404，可能返回 `paths=[]`。
   - `transfer_path/single` / `career_path/cross_industry` / `goal_path/single`：空结果会转为 404。
