# Graph Lineage（离线计算 → 在线推理 的证据闭环）

本项目的图不仅存“事实”，还存“事实被选中的理由（Lineage）”。

## 1. Run 级快照：`:BuildRun`
离线建图每次会生成一个 `run_id`，并在图里固化为一个节点：

- Label：`BuildRun`
- 主键：`id`
- 常用字段：
  - `status`: `running` / `completed`
  - `created_at` / `updated_at`
  - `meta_json`: JSON 字符串（包含参数、统计、阶段快照）
  - `jaccard_threshold`, `coarse_resolution`, `fine_resolution`：便于检索的标量

> `meta_json` 用于存储“全局且体量较大”的证据，避免每条边重复存。

## 2. 边级理由快照：`[:EVOLVE_TO]`
在线推理最常用的是 `EVOLVE_TO` 边上的“决策快照”：

- 必要指标（原有）：`jaccard_high`, `cos_low`, `salary_gain`, `transfer_cost`, `final_routing_cost`, `pareto_rank`
- 新增血缘字段：
  - `build_run_id`: 对应 `BuildRun.id`
  - `lineage_json`: JSON 字符串（不可嵌套属性用 JSON 固化）
  - `base_attraction`, `rank_penalty`, `cross_penalty`
  - `pareto_group_size`, `pareto_front_size`

### 多次离线重跑的版本清理（重要）
实际业务中图谱会周期性重算（例如每月重跑 Jaccard/Pareto）。如果旧 `EVOLVE_TO` 不清理，会残留历史路线，导致在线寻路（Dijkstra）被旧边/新边混杂污染。

当前策略：默认“只保留最新一次 Run 产出的精英演化路线”。在一次新的 `build_run_id` 落库完毕后，会执行清理：

```cypher
MATCH ()-[e:EVOLVE_TO]->()
WHERE e.build_run_id IS NULL OR e.build_run_id <> $keep_run_id
DELETE e
```

这保证任意时刻图中只存在一个版本的演化拓扑，寻路稳定且可解释。

### `lineage_json` 的结构（示例）
```json
{
  "selected_by": "pareto_sparsification",
  "thresholds": {"jaccard_threshold": 0.1},
  "pareto": {
    "rank": 0,
    "group_size": 50,
    "front_size": 6,
    "keep_fronts": 2,
    "objectives": {"jaccard_high":"max","cos_low":"max","salary_gain":"max","transfer_cost":"min","cross_community_penalty":"min"},
    "is_cross_community": false,
    "cross_community_penalty": 0.5
  },
  "routing": {
    "base_attraction": 0.73,
    "components": {"jaccard_high":0.5,"cos_low":0.3,"salary_gain":0.2},
    "rank_penalty": 0.0,
    "cross_penalty": 0.0,
    "transfer_cost": 0.12,
    "final_routing_cost": 0.39
  },
  "communities": {
    "coarse": {"from": 1, "to": 1},
    "fine": {"from": 12, "to": 12}
  }
}
```

## 3. 技能稀缺度证据：`Competency` / `REQUIRES`
IDF 回写时，会额外固化“覆盖率证据”（用于在线解释“行业里有多少岗位需要它”）：

- `(:Competency)` 和 `[:REQUIRES]` 上都会写入：
  - `idf_weight`
  - `df`（覆盖岗位数）
  - `total_jobs`
  - `prevalence`（覆盖率，$df/total\_jobs$）
  - `idf_run_id`, `idf_ts`

并尽量保留旧权重血缘：
- `[:REQUIRES].local_weight` 会在原 `weight` 非 0 且 `local_weight` 为空时缓存。

## 4. 在线查询模板（Cypher）

### 4.1 取一条演化边的“被选中理由” + Run 快照
```cypher
MATCH (a:Job {id: $from})-[e:EVOLVE_TO]->(b:Job {id: $to})
OPTIONAL MATCH (r:BuildRun {id: e.build_run_id})
RETURN a.job_name, b.job_name,
       e.jaccard_high, e.cos_low, e.salary_gain, e.transfer_cost, e.final_routing_cost,
       e.pareto_rank, e.pareto_group_size, e.pareto_front_size,
       e.lineage_json,
       r.status, r.meta_json;
```

### 4.2 取某个技能的行业覆盖证据
```cypher
MATCH (c:Competency {name: $skill})
RETURN c.idf_weight, c.df, c.total_jobs, c.prevalence, c.idf_run_id;
```

### 4.3 取一条路径的所有边快照（用于解释整条路径）
```cypher
MATCH p=(s:Job {id: $start})-[:EVOLVE_TO*1..5]->(t:Job {id: $end})
RETURN relationships(p) AS edges;
```
