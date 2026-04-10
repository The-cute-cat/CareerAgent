from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from ai_service.models.graph import GraphNodeJob


class PathType(str, Enum):
    """路径类型枚举（服务端分类标签）。

    来历：该字段不是图数据库直接存储的属性，而是服务端在构造
    `CareerPath` 时对整条路径进行的类型归类，用于对外 API 做产品化区分。

    口径（与当前三类路径接口的图论约束一致）：
    - vertical：垂直晋升；通常要求每跳不跨 micro/macro 社区且 salary_gain>0。
    - lateral：横向转岗；通常要求同 macro 不同 micro，且每跳跨 micro 不跨 macro。
    - cross_industry：跨界跃迁；要求至少一跳跨 macro 社区。

    边级跨界证据以 `TransitionStep.edge_evidence.is_cross_micro/is_cross_macro` 为准。
    """

    VERTICAL = "vertical"  # 垂直晋升 (如: 前端 -> 资深前端)
    LATERAL = "lateral"  # 横向转岗 (如: 前端 -> Node后端)
    CROSS_INDUSTRY = "cross_industry"  # 跨界跃迁 (可选：用于高难度高回报推荐)


# ==========================================
# 1. 缺口分析 (语义图的投影) - 供前端展示"学习清单"
# ==========================================


class GapType(str, Enum):
    """通用缺口类型枚举（纯证据输出的类别标签）。

    来历：用于标识 `UniversalGapInfo` 的来源类型。
    - hard_skill：来自图中 (Job)-[:REQUIRES]->(Competency) 的集合差集计算。
    - soft_trait：预留类型；如果未来实现可复核的“文本证据对比”链路再启用。
    """

    HARD_SKILL = "hard_skill"  # 硬技能/专业能力（来自 REQUIRES 差集）
    SOFT_TRAIT = "soft_trait"  # 软素质/胜任力（预留类型，当前不输出）


class UniversalGapInfo(BaseModel):
    """通用缺口对象（纯证据模式）。

    仅保留“可从图中直接取回/计算得到且可复核”的字段：
    - REQUIRES/Competency 的硬技能缺口（集合差集）
    - IDF/df/prevalence 等稀缺度证据（离线固化）
    """

    gap_key: str = Field(
        default="",
        description=(
            "缺口唯一 Key，用于去重与前端稳定渲染。"
            "硬技能缺口建议使用 `hard:{competency_name}`（competency_name 来自 "
            "(Competency.name)）；"
            "软素质缺口（预留）可使用 `soft:{field_name}`。"
        ),
    )
    gap_type: GapType = Field(
        default=GapType.HARD_SKILL,
        description=(
            "缺口类型标签。当前三类路径接口只输出 hard_skill；"
            "soft_trait 为预留类型，不代表当前已实现的证据生产链路。"
        ),
    )
    gap_name: str = Field(
        default="",
        description=(
            "缺口名称。硬技能缺口时等于 (Competency.name)；"
            "软素质缺口（预留）时可填维度名（如 comm_desc/logic_desc）。"
        ),
    )

    # 硬技能缺口（兼容 REQUIRES 差集）
    category: str = Field(
        default="",
        description=(
            "能力分类/类目。来自 (Competency.category) 或等价字段（若图中存在）；"
            "若离线未写入分类则为空字符串。"
        ),
    )
    target_score: int = Field(
        default=0,
        description=(
            "目标岗位对该能力的最低评分要求。来自关系"
            " (Job)-[r:REQUIRES]->(Competency) 的 r.min_score。"
        ),
    )
    original_context: str = Field(
        default="",
        description=(
            "岗位 JD 原话/上下文证据。来自关系"
            " (Job)-[r:REQUIRES]->(Competency) 的 r.context。"
        ),
    )

    # --- 证据字段：技能稀缺度/覆盖率（来自 REQUIRES/Competency 的 IDF 固化） ---
    importance_weight: Optional[float] = Field(
        default=None,
        description=(
            "重要性权重（用于缺口排序/优先级）。来自 r.weight；"
            "该值通常为离线构图后的最终权重（可能已融合 IDF/归一化等处理）。"
        ),
    )
    local_weight: Optional[float] = Field(
        default=None,
        description=(
            "局部权重快照（血缘证据）。来自 r.local_weight；"
            "用于保留 IDF 回写/归一化前的原始权重口径（若离线流水线有写入）。"
        ),
    )
    idf_weight: Optional[float] = Field(
        default=None,
        description=(
            "全局 IDF 权重（稀缺度证据）。来自 r.idf_weight（离线统计固化），"
            "用于衡量能力的稀缺程度；不由在线推理生成。"
        ),
    )
    df: Optional[int] = Field(
        default=None,
        description=(
            "覆盖岗位数 df：该能力在统计口径内出现在多少个岗位的 REQUIRES 中。"
            "来自 r.df（离线统计固化）。"
        ),
    )
    total_jobs: Optional[int] = Field(
        default=None,
        description=(
            "统计口径内岗位总数（IDF 统计分母）。来自 r.total_jobs（离线统计固化），"
            "用于解释 prevalence=df/total_jobs。"
        ),
    )
    prevalence: Optional[float] = Field(
        default=None,
        description=(
            "覆盖率 prevalence=df/total_jobs。来自 r.prevalence（离线统计固化）。"
        ),
    )
    idf_run_id: Optional[str] = Field(
        default=None,
        description=(
            "该 IDF 证据来自哪个离线 Run。来自 r.idf_run_id（离线固化）；"
            "其值应对应图中 (BuildRun.id)。"
        ),
    )


class BuildRunEvidence(BaseModel):
    """离线建图 Run 的证据快照（Run级别）。"""

    run_id: str = Field(
        ...,
        description="离线构图 Run 的唯一标识。来自节点 (BuildRun.id)。",
    )
    status: Optional[str] = Field(
        default=None,
        description=(
            "离线流水线状态。来自节点 (BuildRun.status)；常见值如 running/completed。"
        ),
    )
    meta_json: Optional[str] = Field(
        default=None,
        description=(
            "离线 Run 元数据原文（JSON 字符串）。来自 (BuildRun.meta_json)，"
            "用于复核该次构图的参数、统计口径、阶段快照等。"
        ),
    )


class EvolveEdgeEvidence(BaseModel):
    """一次跃迁边（EVOLVE_TO）的全量证据快照。"""

    from_job_id: str = Field(
        ...,
        description=(
            "起点岗位 ID。来自路径中边 (start)-[EVOLVE_TO]->(end) 的起点节点 (Job.id)。"
        ),
    )
    to_job_id: str = Field(
        ...,
        description=(
            "终点岗位 ID。来自路径中边 (start)-[EVOLVE_TO]->(end) 的终点节点 (Job.id)。"
        ),
    )

    # 核心指标
    final_routing_cost: Optional[float] = Field(
        default=None,
        description=(
            "综合路由成本（边权重）。来自关系 (Job)-[r:EVOLVE_TO]->(Job) 的 "
            "r.final_routing_cost；"
            "在线最短路/路径排序对该字段做累加。"
        ),
    )
    transfer_cost: Optional[float] = Field(
        default=None,
        description=(
            "换岗成本分量。来自 r.transfer_cost（离线路由坍缩中间量/或等价字段）。"
        ),
    )
    salary_gain: Optional[float] = Field(
        default=None,
        description=(
            "薪资增益证据。来自 r.salary_gain（离线估计/固化），用于路径约束或排序展示。"
        ),
    )
    jaccard_high: Optional[float] = Field(
        default=None,
        description=(
            "技能重合度证据。来自 r.jaccard_high（离线计算固化），通常为技能集合的加权 Jaccard。"
        ),
    )
    cos_low: Optional[float] = Field(
        default=None,
        description=(
            "背景/文本相似度证据。来自 r.cos_low（离线计算固化），通常为文本向量余弦相似度等指标。"
        ),
    )

    # Pareto/社区证据
    pareto_rank: Optional[int] = Field(
        default=None,
        description=(
            "帕累托前沿层级（越小越优）。来自 r.pareto_rank（离线 Pareto 稀疏化固化）。"
        ),
    )
    pareto_group_size: Optional[int] = Field(
        default=None,
        description=(
            "同一起点岗位下的候选边集合规模。来自 r.pareto_group_size（离线固化）。"
        ),
    )
    pareto_front_size: Optional[int] = Field(
        default=None,
        description=(
            "当前 pareto_rank 对应前沿的边数量。来自 r.pareto_front_size（离线固化）。"
        ),
    )
    is_cross_macro: Optional[bool] = Field(
        default=None,
        description=(
            "是否跨宏观社区（macro 社区）。来自 r.is_cross_macro（离线社区划分后固化）。"
        ),
    )
    is_cross_micro: Optional[bool] = Field(
        default=None,
        description=(
            "是否跨微观社区（micro 社区）。来自 r.is_cross_micro（离线社区划分后固化）。"
        ),
    )

    # 路由坍缩中间量
    base_attraction: Optional[float] = Field(
        default=None,
        description=(
            "基础吸引力/基础得分分量。来自 r.base_attraction（离线路由坍缩中间量）。"
        ),
    )
    rank_penalty: Optional[float] = Field(
        default=None,
        description=("帕累托等级惩罚分量。来自 r.rank_penalty（离线路由坍缩中间量）。"),
    )
    cross_penalty: Optional[float] = Field(
        default=None,
        description=("跨界惩罚分量。来自 r.cross_penalty（离线路由坍缩中间量）。"),
    )

    # Lineage
    build_run_id: Optional[str] = Field(
        default=None,
        description=(
            "该边来自哪个离线构图 Run。来自 r.build_run_id（离线固化）；"
            "其值应对应节点 (BuildRun.id)。"
        ),
    )
    lineage_json: Optional[str] = Field(
        default=None,
        description=(
            "离线决策快照原文（JSON 字符串）。来自 r.lineage_json；"
            "包含阈值/目标/社区/路由分解等可回溯信息，用于解释该边为何被保留。"
        ),
    )


class JobSnapshot(BaseModel):
    """岗位快照（节点级证据与上下文）。

    来历：来自图中节点 (Job) 的属性快照。
    - `attributes`：结构化的 Job 节点属性（GraphNodeJob），用于最大化可回溯与类型稳定。
    """

    job_id: str = Field(
        ...,
        description="岗位 ID。来自节点 (Job.id)。",
    )
    job_name: Optional[str] = Field(
        default=None,
        description="岗位名称。来自节点 (Job.job_name) 或等价字段（取决于图的字段命名）。",
    )

    attributes: GraphNodeJob = Field(
        description=(
            "岗位节点的结构化属性快照。类型为 GraphNodeJob（#sym:GraphNodeJob），"
            "字段来源为节点 (Job) 的同名属性（例如 macro_community_id/micro_community_id、"
            "comm_desc/logic_desc/learn_desc 等）。"
        ),
    )


# ==========================================
# 2. 演化步骤 (逻辑图与语义图的结合) - 供前端画"时间轴(Timeline)"
# ==========================================
class TransitionStep(BaseModel):
    """路径中的一次跳跃 (Job A -> Job B)"""

    step_index: int = Field(
        ...,
        description=(
            "步骤序号（从 1 开始）。来自服务端对路径中边的顺序编号，"
            "用于前端时间轴渲染与稳定定位。"
        ),
    )

    from_job_id: str = Field(
        ...,
        description="起始岗位 ID。来自路径中起点节点 (Job.id)。",
    )
    from_job_name: str = Field(
        ...,
        description="起始岗位名称。来自节点 (Job.job_name) 或等价字段。",
    )
    to_job_id: str = Field(
        ...,
        description="目标岗位 ID。来自路径中终点节点 (Job.id)。",
    )
    to_job_name: str = Field(
        ...,
        description="目标岗位名称。来自节点 (Job.job_name) 或等价字段。",
    )

    # 物理指标 (供前端画 雷达图 或 趋势图)
    jaccard_high: float = Field(
        ...,
        description=(
            "硬技能重合度指标。通常来自对应 EVOLVE_TO 边的 r.jaccard_high（离线计算固化）。"
        ),
    )
    cos_low: float = Field(
        ...,
        description=(
            "软素质/文本相似度指标。通常来自对应 EVOLVE_TO 边的 r.cos_low（离线计算固化）。"
        ),
    )
    salary_gain: float = Field(
        ...,
        description=(
            "薪资增益指标。通常来自对应 EVOLVE_TO 边的 r.salary_gain（离线估计/固化）。"
        ),
    )

    # 岗位快照（from/to 全量属性 + desc 文本属性）
    from_job_snapshot: Optional[JobSnapshot] = Field(
        default=None,
        description=(
            "起始岗位的节点级证据快照。来自节点 (Job {id=from_job_id}) 的属性抽取。"
        ),
    )
    to_job_snapshot: Optional[JobSnapshot] = Field(
        default=None,
        description=(
            "目标岗位的节点级证据快照。来自节点 (Job {id=to_job_id}) 的属性抽取。"
        ),
    )

    # 缺口明细 (挂载在这一次跳跃上)：硬技能缺口 + 软素质字段对比缺口
    skill_gaps: List[UniversalGapInfo] = Field(
        default_factory=list,
        description=(
            "为完成该步跃迁需要补齐的硬技能缺口列表（纯证据）。"
            "计算口径：对目标岗位 to_job 的 REQUIRES 技能集合做差集，"
            "并结合路径上下文维护的 known_skills 累积集合进行去重。"
        ),
    )

    # 新图证据：边级全量快照（供后续AI解读）
    edge_evidence: Optional[EvolveEdgeEvidence] = Field(
        default=None,
        description=(
            "该步对应的 EVOLVE_TO 边证据快照。来自关系"
            " (Job)-[EVOLVE_TO]->(Job) 的属性（含 lineage_json、pareto、路由分解等）。"
        ),
    )


# ==========================================
# 3. 完整路径聚合 (最终返回给前端的 Root Model)
# ==========================================
class CareerPath(BaseModel):
    """一条完整的职业规划路线"""

    path_id: str = Field(
        ...,
        description=(
            "路径唯一 Key，用于前端列表渲染与稳定定位。"
            "来自服务端生成（例如基于 start_job_id + steps 的目标序列哈希）。"
        ),
    )
    path_type: PathType = Field(
        ...,
        description=(
            "路径类型（服务端分类）。vertical/lateral/cross_industry 之一，"
            "与调用的路径接口及其约束相匹配。"
        ),
    )

    # 总体评估指标
    total_steps: int = Field(
        ...,
        description="需要跳跃的次数，等于 steps 的长度。",
    )
    total_routing_cost: float = Field(
        ...,
        description=(
            "总体演化阻力（路径总成本）。计算口径：对路径上每条 EVOLVE_TO 边的"
            " final_routing_cost 做求和（与在线寻路/排序一致）。"
        ),
    )

    # 详情
    steps: List[TransitionStep] = Field(
        ...,
        description=(
            "演化步骤明细（链式结构）。每个 step 对应路径中的一条 EVOLVE_TO 边，"
            "并携带该边的证据快照与该步的技能缺口证据。"
        ),
    )

    # Run级证据（可选）：同一条路径的边通常来自同一BuildRun
    build_run_evidence: Optional[BuildRunEvidence] = Field(
        default=None,
        description=(
            "离线 BuildRun 快照（Run 级证据）。通常由路径中任一边的 build_run_id 追溯到 (BuildRun)；"
            "用于复核该批次构图的阈值/统计口径/参数。若图中未写入 build_run_id，则为空。"
        ),
    )


class CareerPathBundle(BaseModel):
    """接口返回：起点岗位 + 路径列表。

    目的：批量接口不再扁平化 paths，前端可按起点岗位进行分组复用组件。
    """

    start_job_id: str = Field(
        ...,
        description="起点岗位 ID。来自请求参数 job_id，并用于匹配图中节点 (Job.id)。",
    )
    start_job_name: Optional[str] = Field(
        default=None,
        description=(
            "起点岗位名称。来自节点 (Job.job_name) 或等价字段的读取结果；"
            "若查询不到岗位或未回填则为 null。"
        ),
    )
    paths: List[CareerPath] = Field(
        default_factory=list,
        description=(
            "该起点岗位下的候选职业路径列表（纯证据）。"
            "列表为空表示在当前约束（跳数上限/跨社区规则/薪资约束等）下未找到路径。"
        ),
    )
