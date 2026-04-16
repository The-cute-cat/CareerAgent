# 职业演化图谱（Career Graph）详细设计文档

> 面向比赛提交的技术文档版本。
>
> 本文档描述本项目“职业演化图谱”的数据模型、离线构建流水线、关键算法与公式、证据（lineage）闭环、在线查询与验收方法。
>
> 约定：
> - **语义图**：`(Job)-[:REQUIRES]->(Competency)`，用于技能缺口与稀缺度解释。
> - **演化图**：`(Job)-[:EVOLVE_TO]->(Job)`，用于路径规划（如最短路/Dijkstra）。
> - **Run**：一次离线建图的全流程执行实例，对应图中的 `(:BuildRun {id})`。

---

## 1. 背景与目标

本项目用图谱把“岗位画像”组织成可计算、可回溯的结构，用于：

1. **职业路径规划**：基于 `EVOLVE_TO` 的有向加权图，在约束条件下寻找成本最低的路径（例如垂直晋升、同域横跳、跨界跃迁、指定目标岗位）。
2. **可解释的推荐**：不仅给出“结果路径”，还返回每一步跃迁边的证据快照（`lineage_json`）以及 Run 级别的参数与统计（`BuildRun.meta_json`）。
3. **技能缺口清单**：基于语义图的集合差集，输出每一步跃迁需要补齐的能力，并附带 IDF/覆盖率等“可复核的证据字段”。

核心设计原则：

- **纯证据模式（Evidence-first）**：线上返回的字段尽量来自图中可复核的数据（节点/边属性、Run 快照、可由图直接计算的集合差集）。
- **离线重算可控**：周期性重跑时只保留最新 Run 的演化边，避免历史拓扑污染在线最短路。
- **可扩展**：把“大对象”证据放在 `BuildRun.meta_json`，把“边级局部证据”放在 `EVOLVE_TO.lineage_json`，避免重复存储。

---

## 2. 图谱数据模型（Neo4j Schema）

### 2.1 节点（Node Labels）

#### 2.1.1 `:Job`（岗位节点）
来源：离线从岗位画像（Pydantic `JDAnalysisResult`）抽取并写入。结构化字段由 `GraphNodeJob` 约束。

常用属性（摘自 `GraphNodeJob`）：

- 标识：
  - `id`：岗位 ID（唯一）
  - `job_name`：岗位名称
- 社区标签（离线聚类产出）：
  - `macro_community_id`：宏观社区（第一次粗聚类）
  - `micro_community_id`：细分社区（第二次细聚类）
- 用于过滤/计算的数值化属性（便于 Cypher `WHERE` 与离线计算）：
  - `min_degree`（学历序数）
  - `min_experience`（最低年限）
  - `salary_rank`、`demand_rank`、`trend_rank`
  - `major`
- 文本属性（用于离线 embedding 与在线解释/展示）：
  - `comm_desc`、`team_desc`、`logic_desc`、`stress_desc`
  - `learn_desc`、`innov_desc`、`lead_desc`、`adapt_desc`、`ethics_desc`
  - `project_reqs`、`intern_reqs`、`special_reqs`
- 血缘字段（离线写入，用于定位最近一次构建）：
  - `last_build_run_id`、`last_build_ts`

#### 2.1.2 `:Competency`（能力节点）
来源：从岗位画像的若干字段抽取而来，结构由 `GraphNodeCompetency` 约束。

常用属性：

- `name`：能力名称（唯一）
- `category`：能力类目（如“核心专业技能/工具与平台能力/语言能力/证书要求”）
- 血缘字段：`last_build_run_id`、`last_build_ts`
- IDF 证据字段（离线回写）：
  - `idf_weight`：稀缺度权重
  - `df`：覆盖岗位数（出现于多少个不同 Job）
  - `total_jobs`：统计口径下岗位总数
  - `prevalence`：覆盖率 $df/total\_jobs$
  - `idf_run_id`、`idf_ts`

#### 2.1.3 `:BuildRun`（离线构建 Run 快照节点）
一次离线建图对应一个 `BuildRun` 节点，用于“全局参数/统计/阶段快照”的证据闭环。

常用属性（由 `GraphNodeBuildRun` 约束写入）：

- `id`：run_id（唯一）
- `status`：`running` / `completed` / `failed`（当前常见为 running、completed）
- `created_at` / `updated_at`
- `meta_json`：JSON 字符串，包含参数、统计与回归报表（详见第 5 节）
- 便于检索的标量：`jaccard_threshold`、`coarse_resolution`、`fine_resolution`

### 2.2 关系（Relationships）

#### 2.2.1 `(:Job)-[:REQUIRES]->(:Competency)`（语义边：岗位需要能力）
由 `GraphEdgeRequires` 描述。

常用属性：

- `weight`：用于计算/排序的权重（离线会被更新为 `idf_weight * local_weight`）
- `local_weight`：局部 TF 快照（按能力 `category` 给权重）
- `min_score`：最低要求强度（当前默认 1）
- `context`：上下文证据原文（用于语义复水/解释）
- 写入血缘：`build_run_id`、`build_ts`
- IDF 证据：`idf_weight`、`df`、`total_jobs`、`prevalence`、`idf_run_id`、`idf_ts`

#### 2.2.2 `(:Job)-[:EVOLVE_TO]->(:Job)`（演化边：岗位可演化/跃迁）
由 `GraphEdgeEvolve` 描述，是在线寻路的核心边。

常用属性：

- 指标（离线计算固化）：
  - `jaccard_high`：硬技能重合度（加权 Jaccard）
  - `cos_low`：背景相似度（文本 embedding + 结构化属性融合）
  - `salary_gain`：薪资增益（有向）
  - `transfer_cost`：迁移成本
- 路由权重（在线 Dijkstra 累加）：
  - `final_routing_cost`：最终路由成本（越小越优）
- Pareto/稀疏化证据：
  - `pareto_rank`（0 表示第一前沿）
  - `pareto_group_size`（同起点候选边数）
  - `pareto_front_size`（所在前沿边数）
- 跨社区证据：
  - `is_cross_macro`：是否跨宏观社区
  - `is_cross_micro`：是否跨细分社区
- 路由坍缩中间量（用于解释 final_routing_cost）：
  - `base_attraction`、`rank_penalty`、`cross_penalty`
- 证据闭环（lineage）：
  - `build_run_id`：生成该边的 Run
  - `lineage_json`：JSON 字符串，记录阈值/目标/社区/路由分解/guardrail 命中等

### 2.3 物理约束（Constraints）
离线初始化时会创建以下唯一约束（加速查询、保证主键一致性）：

- `(:Job {id})` 唯一
- `(:Competency {name})` 唯一
- `(:BuildRun {id})` 唯一

### 2.4 环境依赖与前置条件（复现必读）

- Neo4j 需要启用 **APOC**（因为在线最短路使用了 `apoc.algo.dijkstra`）。如果未安装/未允许该过程调用，`get_shortest_path()` 会报错。
- 离线建图算法依赖若干科学计算与图算法库（用于聚类与 Pareto 非支配排序等），例如：
  - `igraph`、`leidenalg`（Leiden 聚类）
  - `pymoo`（非支配排序）
  - `numpy`、`scikit-learn`（回归报表指标/相似度计算等）
- `cos_low` 语义部分会加载 `sentence-transformers` 模型 `all-MiniLM-L6-v2`：首次运行可能需要联网下载模型权重；若在离线环境参赛，建议提前缓存模型。

---

## 3. 数据来源与规范化（从岗位画像到图）

### 3.1 输入：岗位画像结构
离线建图的输入通常来自数据库中的岗位画像表（SQLAlchemy `JobPortrait`），其 `skills_req` 字段保存一份可被 `JDAnalysisResult` 校验的字典。

离线验收脚本会做两层校验：

1. **结构快速检查**：是否包含 `job_id/job_name/profiles`。
2. **Pydantic 校验**：`JDAnalysisResult.model_validate(payload)`。

### 3.2 `Job` 节点规范化
`GraphNodeJob.transform_job_to_graph_node()` 会把文本字段映射为数值/枚举：

- 学历：`degree_map = {不限:0, 专科:1, 本科:2, 硕士:3, 博士:4}`
- 薪资/需求：`level_map = {低:1, 中:2, 高:3}`
- 趋势：`trend_map = {萎缩:-1, 平稳:0, 朝阳:1}`
- 经验年限：从字符串抽数字取最小值（含“应届/不限”则为 0）
- 专业：尝试使用 `major_aligner` 做对齐，失败则保留原值

### 3.3 `Competency` 节点抽取
`GraphNodeCompetency.transform_competencies_to_graph_nodes()` 会从岗位画像的以下字段抽能力：

- 核心专业技能：`profiles.professional_skills.core_skills`
- 工具与平台能力：`profiles.professional_skills.tool_capabilities`
- 语言能力：`profiles.professional_skills.language_requirements`
- 证书要求：`profiles.basic_requirements.certificates`

并过滤掉无意义占位（如“无/未提及/不限”）。

### 3.4 `REQUIRES` 边的上下文与 TF 权重
`JobCompetency.transform_jobs_to_graph_payload()` 在生成 `REQUIRES` 边时会：

- 写入 `context`（从画像字段中挑选与该类目最相关的原文；无原文时给结构化兜底句）
- 给出 `local_weight`（TF 等效权重）：
  - 以 `Competency.category` 为 key，从 `config.yaml -> graph_build.tf.category_weights` 读取
  - 未命中时使用 `graph_build.tf.default_weight`

注意：离线流水线后续会把 `weight` 更新为 `idf_weight * local_weight`，所以 `weight` 不应被假定在 $[0,1]$。

---

## 4. 离线建图流水线（Offline Build Pipeline）

离线入口：`GraphRepository.build_graph_from_jobs(jobs)`。

### 4.1 总览流程图

```mermaid
flowchart TD
  A[输入: jobs (JDAnalysisResult列表)] --> B[创建 BuildRun: status=running]
  B --> C[抽取 Job/Competency/REQUIRES payload]
  C --> D[批量写入: Job/Competency/REQUIRES]
  D --> E[统计 IDF: df/total/prevalence/idf_weight]
  E --> F[回写 IDF 到 REQUIRES 与 Competency]
  F --> G[计算加权Jaccard: Job-Job 候选对]
  G --> H[计算边指标: cos_low/salary_gain/transfer_cost]
  H --> I[粗聚类 Leiden: macro_community_id]
  I --> J[Pareto 稀疏化: 保留前沿边]
  J --> K[跨社区保边 guardrail]
  K --> L[路由坍缩: final_routing_cost]
  L --> M[细聚类 Leiden: micro_community_id]
  M --> N[生成 lineage_json / 跨社区标识]
  N --> O[批量写入 EVOLVE_TO]
  O --> P[清理旧 EVOLVE_TO (仅保留本Run)]
  P --> Q[生成报表+更新 BuildRun: status=completed]
```

### 4.2 Run 生成与写入（BuildRun）
- `build_run_id = uuid.uuid4().hex`
- `build_started_at = datetime.now().isoformat(timespec="seconds")`
- `upsert_build_run(status="running", meta={stage: "save_job_competencies"}, ts=build_started_at)`

`BuildRun.meta_json` 在 `completed` 时会被更新为包含参数、统计、聚类/pareto 统计与回归报表的完整快照（见第 5 节）。

### 4.3 阶段 1：写入语义图（Job / Competency / REQUIRES）
- `JobCompetency.transform_jobs_to_graph_payload(jobs)` 生成写入 payload
- `save_job_competencies(payload, build_run_id, build_ts)` 批量写入
  - `MERGE (j:Job {id})`，并写入 `last_build_run_id/last_build_ts`
  - `MERGE (c:Competency {name})`，并写入 `last_build_run_id/last_build_ts`
  - `MERGE (j)-[r:REQUIRES]->(c)` 并写入边属性

重要口径：当前实现中 `Job` 节点是由 `REQUIRES` 的批量写入“顺带创建”的。如果某个岗位抽取不到任何 `Competency`，则不会写入任何 `JobCompetency` 记录，从而**不会进入 Neo4j 的 Job 节点集合**。

### 4.4 阶段 2：IDF（稀缺度）统计与回写

#### 4.4.1 统计口径
- 数据来源：`fetch_counts_for_idf()` 只取 `(job_id, comp_name)`
- 统计：
  - `total_jobs = |{job_id}|`
  - `df(comp) = |{job_id: comp 出现在该 job 的 REQUIRES}|`
  - `prevalence = df/total_jobs`

#### 4.4.2 IDF 公式
`GraphAlgorithms.get_idf_weights()` 采用平滑 IDF：

$$
\mathrm{idf}(c) = \log\left(\frac{N}{df(c)}\right) + 1
$$

其中 $N=total\_jobs$。

#### 4.4.3 回写策略
`update_idf_weights()` 会：

- 把 `idf_weight/df/total_jobs/prevalence/idf_run_id/idf_ts` 写到 `REQUIRES` 与 `Competency`
- 更新用于后续 Jaccard 的边权重：

$$
\mathrm{REQUIRES.weight} = \mathrm{idf\_weight} \times \mathrm{local\_weight}
$$

其中 `local_weight` 为 TF 等效权重（来自能力类目）。

### 4.5 阶段 3：加权 Jaccard 生成候选对（Job-Job）

数据来源：`fetch_all_for_jaccard()` 读取 `(job_id, comp_name, r.weight)`。

加权 Jaccard 使用 Min/Max（对权重取交并比）：

- 交集权重：$\sum_c \min(w_{a,c}, w_{b,c})$
- 并集权重：$\sum w_a + \sum w_b - \sum \min(...)$

得分：

$$
J(a,b) = \frac{\sum_c \min(w_{a,c}, w_{b,c})}{\sum w_a + \sum w_b - \sum_c \min(w_{a,c}, w_{b,c})}
$$

阈值：`config.yaml -> graph_build.jaccard.threshold`。

性能策略：当岗位数 $\ge$ `blocking_min_jobs`（默认 3000）时启用 blocking：
- 每个岗位取 top_m（默认 20）个最高权重技能作为 blocking key
- 仅对共享至少一个 key 的候选集合做精确 Jaccard，避免 $O(N^2)$ 全对全

### 4.6 阶段 4：候选边多指标计算（cos_low / salary_gain / transfer_cost）

在 `build_evolve_edges(job_data, jaccard_map)` 中完成。

#### 4.6.1 cos_low（背景相似度）
cos_low 融合两类信号：

1. 文本语义相似：
   - 拼接文本：`comm_desc + team_desc + logic_desc + learn_desc`
   - embedding：`SentenceTransformer("all-MiniLM-L6-v2")`
   - 余弦：先向量归一化，再点积
2. 结构化属性相似：
   - 维度：`min_degree/min_experience/salary_rank`
   - 归一化上界：`MAX_DEGREE=4, MAX_EXP=10, MAX_SALARY_RANK=3`
   - 相似度：

$$
attr\_sim = 1 - mean(|x_a - x_b|)
$$

最终：

$$
cos\_low = text\_cos \cdot w_{text} + attr\_sim \cdot w_{attr}
$$

权重来自 `config.yaml -> graph_build.cos_low.text_weight/attr_weight`（会归一化）。

#### 4.6.2 salary_gain（有向）
对每个无向候选对 $(a,b)$ 生成两条有向候选边：

- `a -> b`：

$$
salary\_gain_{a\to b} = \frac{\max(salary\_rank_b - salary\_rank_a, 0)}{2}
$$

- `b -> a` 同理。

#### 4.6.3 transfer_cost（迁移成本）
由三项差异组成（双向一致）：

- `exp_diff = |min_experience_a - min_experience_b|`
- `degree_diff = |min_degree_a - min_degree_b|`
- `major_diff`：
  - 若任一专业未知（空/未提及/未知），取 1
  - 否则相同为 0，不同为 1

$$
transfer\_cost = \frac{exp\_diff + degree\_diff + major\_diff}{10}
$$

#### 4.6.4 degree=0 兜底补边（避免孤点）
如果某岗位在 Jaccard 阈值下没有任何候选边，会导致聚类碎片化、跨社区保边无从谈起。

实现：对无向度为 0 的岗位，按 embedding 相似度取 TopK 近邻补充候选边（`graph_build.degree_zero_fallback.top_k`，默认 3），并将其 `jaccard_high` 置为 0.0（表示未通过硬筛选，仅作为可走兜底边）。

### 4.7 阶段 5：第一次 Leiden 粗聚类（macro_community_id）

`GraphAlgorithms.run_clustering(edge_score_map=jaccard_map, ...)`：

- 图：无向图（igraph）
- 算法：Leiden（`leidenalg`）
- 输入边权：默认 `weight_transform_fn=lambda x: x**2`（增强强边）
- 参数：
  - `coarse_resolution`（默认 0.1）
  - `coarse_isolation_threshold`（默认 0.1）
- 孤立点合并机制：当孤立比例超过阈值时，把孤立点合并到“已连接邻居里权重最高的非孤立社区”

输出：`community_map[job_id] -> community_id`，注入为 `Job.macro_community_id`。

### 4.8 阶段 6：局部 Pareto 稀疏化（保留高质量出边）

`GraphAlgorithms.run_pareto_sparsification()` 在“同起点 from_job 的出边集合”内做多目标非支配排序：

- 目标（当前实现）：
  - 最大化：`jaccard_high`, `cos_low`, `salary_gain`
  - 最小化：`transfer_cost`
  - 额外最小化维度：跨社区惩罚（`cross_community_penalty`）
- 输出：保留前 `keep_fronts` 层前沿（默认 2）

边会被注入：
- `pareto_rank`、`pareto_group_size`、`pareto_front_size`
- `cross_community_penalty`

### 4.9 阶段 6.1：跨社区保边 guardrail（避免社区断联）

由于 Pareto 会对跨社区边增加惩罚维度，可能出现“某些社区对本来存在跨社区候选边，但最终被全部剪掉”。

guardrail 策略：

- 对每个“存在跨社区候选边的宏观社区对”，若 Pareto 输出未保留任何边，则补回 1 条跨社区边
- 选择标准：用同一套路由坍缩公式估计 `provisional_cost`，选择成本最低的一条
- 对 guardrail 补边：
  - `pareto_rank = keep_fronts`
  - `selected_by = "cross_community_guardrail"`（仅用于 lineage_json）

### 4.10 阶段 7：路由坍缩（把多指标压成 final_routing_cost）

`final_routing_cost` 是在线寻路（Dijkstra）累加的边权。

1) 基础吸引力：

$$
base\_attraction = w_J\cdot jaccard\_high + w_C\cdot cos\_low + w_S\cdot salary\_gain
$$

其中权重来自 `graph_build.routing.attraction_weights`（默认 0.5/0.3/0.2）。

2) 惩罚项：

- `rank_penalty = pareto_rank * rank_penalty_per_rank`（默认每 rank 0.15）
- `cross_penalty = cross_penalty`（默认 0.5）
  - 仅当该边被标识为跨社区（粗社区不同）时启用

3) 成本坍缩（越小越容易走）：

$$
final\_routing\_cost = \max\left(1 - base\_attraction + transfer\_cost + rank\_penalty + cross\_penalty,\ 0.001\right)
$$

离线会把 `base_attraction/rank_penalty/cross_penalty/build_run_id` 一并固化在边上用于解释。

### 4.11 阶段 8：第二次 Leiden 细聚类（micro_community_id）

细聚类输入来自 Pareto 后的边，但聚类是**无向**的。当前实现先把有向边聚合为无向对，并取两向中更强连接（成本更低）作为无向 cost。

随后把 cost 变换为“相似度权重”再聚类：

$$
weight = \left(\frac{1}{cost + offset}\right)^{power}
$$

其中 `offset/power` 来自：
- `graph_build.clustering.fine_weight_transform_offset`（默认 0.1）
- `graph_build.clustering.fine_weight_transform_power`（默认 2.0）

输出注入为 `Job.micro_community_id`。

### 4.12 阶段 9：生成边级 lineage_json 与跨社区标识
对每条保留边：

- `is_cross_macro = (macro_community_id from != to)`
- `is_cross_micro = (micro_community_id from != to)`
- 生成 `lineage_json`（JSON 字符串）包含：
  - `selected_by`（pareto_sparsification 或 cross_community_guardrail）
  - `thresholds`（如 jaccard_threshold）
  - `pareto`（rank、group_size、front_size、objectives、cross_community_penalty）
  - `routing`（base_attraction、组件权重、rank_penalty、cross_penalty、transfer_cost、final_routing_cost）
  - `communities`（coarse/fine 的 from/to）

该结构与 [docs/GRAPH_LINEAGE.md](graph_lineage.md) 保持一致。

### 4.13 阶段 10：写入 EVOLVE_TO 与版本清理

- `save_job_evolve(job_evolve_list)` 批量写入：
  - `MERGE` 保证 Job 节点存在并更新属性（含社区标签）
  - `MERGE (from)-[EVOLVE_TO]->(to)` 并写入边属性
- `cleanup_old_evolve_edges(keep_run_id)` 删除旧 Run 的 `EVOLVE_TO`：

```cypher
MATCH ()-[e:EVOLVE_TO]->()
WHERE e.build_run_id IS NULL OR e.build_run_id <> $keep_run_id
DELETE e
```

该策略保证在线寻路不被历史边污染。

---

## 5. 证据闭环（Lineage & Evidence）

本项目的证据闭环分两层：

1. **Run 级证据**：`(:BuildRun)` 节点。
   - `meta_json` 存全局参数、阶段统计、聚类/Pareto 统计与回归报表。
2. **边级证据**：`[:EVOLVE_TO]`。
   - `lineage_json` 存该边为何被保留（阈值、目标、Pareto 排名、路由分解、guardrail 等）。

建议在提交文档中同时附上：

- Run 级 meta_json 样例（截取 params/counts/report）
- 任意一条 EVOLVE_TO 的 lineage_json 样例

更细的说明与示例见：

- [docs/GRAPH_LINEAGE.md](graph_lineage.md)

---

## 6. 在线查询与路径规划（Online Query）

在线侧主要读取 `EVOLVE_TO.final_routing_cost` 作为边权，并带回边级证据。

### 6.1 在线路径接口的图论约束
当前 `CareerRepository` 提供四类查询（均按 `sum(final_routing_cost)` 升序取最优）：

1. **垂直晋升**：同 `micro_community_id`，每跳不跨 micro/macro，且 `salary_gain > 0`。
2. **横向转岗**：同 `macro` 不同 `micro`，且每跳跨 micro 不跨 macro。
3. **跨界跃迁**：目标 `macro` 不同，且路径中至少一跳 `is_cross_macro = true`。
4. **目标路径规划**：给定起点与目标，枚举 simple path（节点不重复）并排序。

重要工程约束：Neo4j 变长关系模式 `[:EVOLVE_TO*1..N]` 的 `N` 不能使用参数，因此实现上会把 hop 上限作为字面量内联，并对其做范围 clamp（避免注入风险）。

### 6.2 Dijkstra 最短路
`CareerRepository.get_shortest_path()` 使用 APOC：

- 只允许沿 `EVOLVE_TO>` 方向
- 权重字段：`final_routing_cost`

会返回：
- `path_sequence`：节点序列（含 job_name、macro/micro）
- `edge_metrics`：每条边的证据字段（含 lineage_json）
- `total_cost`：路径总成本

### 6.3 GraphPlanner：把查询结果封装为“纯证据返回模型”
`GraphPlanner` 会把路径结果封装为 `CareerPath`：

- 每一步 `TransitionStep`：
  - 节点快照（from/to 的 `GraphNodeJob` 属性）
  - 边证据快照（`EvolveEdgeEvidence`，包含 lineage_json）
  - 技能缺口列表（见下一节）
- 可选 Run 级证据：通过 `edge_metrics[0].build_run_id -> BuildRun` 回溯

### 6.4 技能缺口（Gap）计算
每一步跃迁的缺口来自语义图的集合差集：

- 取目标岗位 `to_job` 的 `REQUIRES` 技能集合
- 用 `known_skills`（起点岗位技能基线，并沿路径逐站累积）做去重与差集

缺口对象携带 IDF/覆盖率证据（来自 `REQUIRES` 的离线固化字段），用于解释“为什么优先学这个”。

---

## 7. 离线验收与复现（推荐用于比赛提交）

离线验收脚本：`tests/graph_builder.py`。

### 7.1 运行方式
脚本支持从数据库读取岗位画像，并连接 Neo4j 执行离线建图与最小验证。

常用方式（非交互模式）：

```bash
python tests/graph_builder.py --yes --preview 5
```

参数说明：

- `--max-jobs N`：最多取 N 条画像（0 表示不限制）
- `--preview N`：预览输出 N 条
- `--yes`：自动通过离线流水线中的 `manual_confirm`（CI/非交互环境用）
- `--purge`：建图前清空 Neo4j（危险操作）
- `--delete-after`：脚本结束后清空 Neo4j（危险操作）
- `--skip-build`：只做输入校验与图统计验证（不触发 build）
- Neo4j 连接：
  - `--neo4j-uri/--neo4j-user/--neo4j-password`
  - 或环境变量 `NEO4J_URI/NEO4J_USERNAME/NEO4J_PASSWORD`

### 7.2 验收口径（脚本检查点）
脚本会输出：

- 节点/边计数：Job/Competency/REQUIRES/EVOLVE_TO/BuildRun
- 最近一次 completed 的 BuildRun（用于对齐证据字段）
- EVOLVE_TO 跨社区统计：cross_macro/cross_micro
- guardrail 命中边数（lineage_json 包含 `cross_community_guardrail`）
- 旧边残留检测：是否存在非本次 Run 的 EVOLVE_TO
- 证据完整性：
  - EVOLVE_TO：`final_routing_cost` 与 `lineage_json` 是否缺失
  - REQUIRES：`idf_weight` 与 `idf_run_id` 是否缺失
- Job 节点抽样存在性验证

注意口径：脚本会先过滤“能抽取到至少 1 个 Competency 的岗位”作为期望 Job 集合（原因见 4.3）。

---

## 8. 关键超参（config.yaml）与调参建议

配置位置：`config.yaml -> graph_build`。

- `tf.category_weights/default_weight`：控制 `REQUIRES.local_weight`（不同能力类目在技能重合度中的贡献强弱）
- `cos_low.text_weight/attr_weight`：背景相似度中“文本 vs 结构化”的权重
- `jaccard.threshold`：硬筛选阈值，影响候选网稠密度
- `jaccard.blocking_min_jobs/blocking_top_m`：大规模时的候选生成策略
- `clustering.*`：两次 Leiden 的 resolution 与孤立点阈值
- `pareto.keep_fronts/cross_community_penalty`：稀疏化强度与跨社区惩罚
- `routing.attraction_weights/rank_penalty_per_rank/cross_penalty`：多指标坍缩为成本的权重与惩罚
- `degree_zero_fallback.top_k`：无候选边岗位的兜底近邻数

调参建议（提交文档可按需要精简）：

- 若图过稀疏、社区断联：降低 `jaccard.threshold` 或增大 `degree_zero_fallback.top_k`。
- 若跨界边过少：降低 `routing.cross_penalty` 或 `pareto.cross_community_penalty`。
- 若路径质量不稳定：检查是否执行了 `cleanup_old_evolve_edges`，以及 `BuildRun.status` 是否为 completed。

---

## 9. 常见问题与排障清单

1. **为什么 Neo4j 中 Job 节点数量少于数据库画像数？**
   - 当前实现依赖 `REQUIRES` 批量导入“顺带创建 Job”；抽取不到任何 Competency 的岗位不会写入 Job。

2. **为什么抽取到的 Competency 很少？**
   - 检查岗位画像 JSON 的键是否与 Pydantic 字段别名一致（例如英文键是否能被 populate）；否则核心技能字段可能被忽略。

3. **为什么在线最短路结果混乱/不稳定？**
   - 检查是否存在旧 Run 的 `EVOLVE_TO` 残留；离线构建结束应执行版本清理，仅保留最新 run。

4. **为什么查询变长路径时报语法错？**
   - Neo4j 不支持 `[:EVOLVE_TO*1..$max_hops]` 这种参数化写法；实现上需要把 hop 上限内联为字面量并 clamp。

5. **为什么 BuildRun 找不到 completed？**
   - 说明离线流程可能在中途退出（被人工终止或确认阶段返回）；检查离线日志与 manual_confirm。

---

## 10. 附录：常用 Cypher（复核用）

### 10.1 统计节点/边规模
```cypher
MATCH (j:Job) WITH count(j) AS jobs
MATCH (c:Competency) WITH jobs, count(c) AS comps
MATCH ()-[r:REQUIRES]->() WITH jobs, comps, count(r) AS requires
MATCH ()-[e:EVOLVE_TO]->() WITH jobs, comps, requires, count(e) AS evolves
MATCH (br:BuildRun) WITH jobs, comps, requires, evolves, count(br) AS runs
RETURN jobs, comps, requires, evolves, runs
```

### 10.2 获取最近一次 completed 的 BuildRun
```cypher
MATCH (r:BuildRun)
WHERE r.status = 'completed'
RETURN r.id AS run_id, r.updated_at AS updated_at
ORDER BY r.updated_at DESC
LIMIT 1
```

### 10.3 抽样查看一条 EVOLVE_TO 的 lineage_json
```cypher
MATCH (a:Job)-[e:EVOLVE_TO]->(b:Job)
RETURN a.id, a.job_name, b.id, b.job_name, e.final_routing_cost, e.lineage_json
LIMIT 5
```

### 10.4 查看某能力的覆盖率证据
```cypher
MATCH (c:Competency {name: $skill})
RETURN c.idf_weight, c.df, c.total_jobs, c.prevalence, c.idf_run_id
```

---

## 11. 与其它文档的关系

- 证据闭环与字段示例：
  - [docs/GRAPH_LINEAGE.md](graph_lineage.md)
- 若需要把“路径接口”作为提交材料的一部分，可结合项目的 API 文档补充接口输入/输出。
