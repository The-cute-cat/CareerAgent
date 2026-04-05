from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class PathType(str, Enum):
    """路径类型枚举"""

    VERTICAL = "vertical"  # 垂直晋升 (如: 前端 -> 资深前端)
    LATERAL = "lateral"  # 横向转岗 (如: 前端 -> Node后端)
    CROSS_INDUSTRY = "cross_industry"  # 跨界跃迁 (可选：用于高难度高回报推荐)


# ==========================================
# 1. 缺口分析 (语义图的投影) - 供前端展示"学习清单"
# ==========================================
class SkillGapInfo(BaseModel):
    """具体的技能缺口项"""

    competency_name: str = Field(..., description="缺失的技能/能力名称，如'Redis'")
    category: str = Field(..., description="能力分类，如'核心专业技能'")
    target_score: int = Field(..., description="目标岗位要求的最低评分")
    original_context: str = Field(..., description="JD原话（来自REQUIRES边的context）")
    actionable_advice: str = Field(
        ..., description="AI针对该缺口给出的具体行动建议（如：建议做个xx项目）"
    )


# ==========================================
# 2. 演化步骤 (逻辑图与语义图的结合) - 供前端画"时间轴(Timeline)"
# ==========================================
class TransitionStep(BaseModel):
    """路径中的一次跳跃 (Job A -> Job B)"""

    step_index: int = Field(..., description="步骤序号，如 1, 2")

    from_job_id: str = Field(..., description="起始岗位ID")
    from_job_name: str = Field(..., description="起始岗位名称")
    to_job_id: str = Field(..., description="目标岗位ID")
    to_job_name: str = Field(..., description="目标岗位名称")

    # 物理指标 (供前端画 雷达图 或 趋势图)
    jaccard_high: float = Field(..., description="硬技能重合度")
    cos_low: float = Field(..., description="软素质契合度")
    salary_gain: float = Field(..., description="薪资增益指数")

    # 语义解释 (Agent 的舞台)
    transition_reason: str = Field(
        ..., description="AI解释：为什么推荐走这一步？(基于EVOLVE边指标)"
    )

    # 缺口明细 (挂载在这一次跳跃上)
    skill_gaps: List[SkillGapInfo] = Field(
        default_factory=list, description="为了完成这一跳，需要补齐的缺口"
    )


# ==========================================
# 3. 完整路径聚合 (最终返回给前端的 Root Model)
# ==========================================
class CareerPath(BaseModel):
    """一条完整的职业规划路线"""

    path_id: str = Field(..., description="前端渲染列表用的唯一Key")
    path_type: PathType = Field(..., description="垂直晋升/横向转岗")
    path_title: str = Field(
        ..., description="AI生成的路线响亮标题，如'全栈大牛速成路线'"
    )

    # 总体评估指标
    total_steps: int = Field(..., description="需要跳跃的次数")
    total_routing_cost: float = Field(
        ..., description="总体演化阻力 (供前端做路径对比)"
    )

    # 详情
    steps: List[TransitionStep] = Field(..., description="演化步骤明细（链式结构）")
    overall_summary: str = Field(..., description="Agent对整条路线的全局点评与风险提示")


class CareerPathBundle(BaseModel):
    """接口返回：起点岗位 + 路径列表。

    目的：批量接口不再扁平化 paths，前端可按起点岗位进行分组复用组件。
    """

    start_job_id: str = Field(..., description="起点岗位ID")
    start_job_name: Optional[str] = Field(
        default=None,
        description="起点岗位名称（若 raw_data 提供则回填）",
    )
    paths: List[CareerPath] = Field(
        default_factory=list,
        description="该起点岗位下的候选职业路径列表",
    )


# 最终 API 接口返回的格式：
# List[CareerPath]
