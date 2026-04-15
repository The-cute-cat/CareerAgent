import re
from pydantic import BaseModel, Field
from typing import List, Optional
from config import settings
from ai_service.models.struct_job_txt import (
    JDAnalysisResult,
    Profiles,
    BasicRequirements,
    ProfessionalSkills,
    ProfessionalLiteracy,
    DevelopmentPotential,
    JobAttributes,
)


class GraphNodeJob(BaseModel):
    # --- 1. 唯一标识 ---
    id: str = Field(description="岗位ID，唯一标识")
    job_name: str = Field(description="岗位名称")
    macro_community_id: int = Field(
        default=0, description="第一次聚类算法分的宏观行业社区标签"
    )
    micro_community_id: int = Field(
        default=0, description="第二次聚类算法分的细分职业社区标签"
    )

    # --- 2. 物理过滤属性 (全部数字化/序数化，用于 Cypher WHERE) ---
    # 转为数字，方便图库里做 >= 的大小比较
    min_degree: int = Field(default=0, description="最低学历要求")
    demand_rank: int = Field(default=2, description="该岗位在当前就业市场中的需求程度")
    trend_rank: int = Field(default=0, description="该岗位所属行业的发展趋势")
    salary_rank: int = Field(default=2, description="薪资竞争力等级")
    min_experience: int = Field(default=0, description="最低工作经验年限")
    major: str = Field(default="", description="专业要求")

    # --- 3. 业务维度属性 (用于离线算权重 & Agent 阅读) ---
    industry: str = Field(default="", description="所属行业")
    career_orientation: str = Field(default="", description="职业发展方向")

    # 软素质描述：存原文，Agent 规划时的黄金语料
    comm_desc: str = Field(default="", description="沟通能力描述")
    team_desc: str = Field(default="", description="团队合作能力描述")
    stress_desc: str = Field(default="", description="抗压能力描述")
    logic_desc: str = Field(default="", description="逻辑思维能力描述")

    # --- 4. 发展潜力描述 ---
    learn_desc: str = Field(default="", description="学习能力描述")
    innov_desc: str = Field(default="", description="创新能力描述")
    lead_desc: str = Field(default="", description="领导能力描述")
    adapt_desc: str = Field(default="", description="适应能力描述")
    ethics_desc: str = Field(default="", description="职业道德描述")

    # --- 5. 项目需求描述 ---
    project_reqs: str = Field(default="", description="项目需求描述")
    intern_reqs: str = Field(default="", description="实习需求描述")

    # --- 6. 特殊要求描述 ---
    special_reqs: str = Field(default="", description="特殊要求描述")

    # --- 7. 图构建血缘（离线计算 -> 在线推理） ---
    last_build_run_id: Optional[str] = Field(
        default=None, description="最后一次构建图的 Run ID"
    )
    last_build_ts: Optional[str] = Field(
        default=None, description="最后一次构建图的时间戳"
    )

    @staticmethod
    def convert_experience_to_min(experience_str: str) -> int:
        if not experience_str or "应届" in experience_str:
            return 0
        # 提取所有数字，取最小值作为最低要求
        nums = re.findall(r"(\d+)", experience_str)
        return int(min(nums)) if nums else 0

    # 从JDAnalysisResult中提取job节点信息，并对数据进行规范化处理，并转为GraphNodeJob对象
    @staticmethod
    def transform_job_to_graph_node(job: JDAnalysisResult) -> "GraphNodeJob":
        """
        从JDAnalysisResult中提取job节点信息，并对数据进行规范化处理，并转为GraphNodeJob对象
        """
        # 转换字典映射
        degree_map = {"不限": 0, "专科": 1, "本科": 2, "硕士": 3, "博士": 4}
        level_map = {"低": 1, "中": 2, "高": 3}
        trend_map = {"萎缩": -1, "平稳": 0, "朝阳": 1}

        job_profiles: Profiles = job.profiles

        major_raw = (job_profiles.basic_requirements.major or "").strip()
        if major_raw and major_raw not in {"不限", "未提及", "未知", "无", "无要求"}:
            try:
                from ai_service.scripts.py.major_aliger import major_aligner

                major_raw = major_aligner.align(major_raw)
            except Exception:
                # 对齐失败时保留原值，避免影响主流程
                pass
        job_node = {
            # --- 1. 唯一标识 ---
            "id": job.job_id,
            "job_name": job.job_name,
            "macro_community_id": 0,  # 第一次聚类算法分的宏观行业社区标签
            "micro_community_id": 0,  # 第二次聚类算法分的细分职业社区标签
            # --- 2. 物理过滤属性 (全部数字化/序数化，用于 Cypher WHERE) ---
            # 转为数字，方便图库里做 >= 的大小比较
            "min_degree": degree_map.get(
                job_profiles.basic_requirements.degree.value, 0
            ),
            "salary_rank": level_map.get(
                job_profiles.job_attributes.salary_competitiveness.value, 2
            ),
            "demand_rank": level_map.get(
                job_profiles.job_attributes.social_demand.value, 2
            ),
            "trend_rank": trend_map.get(
                job_profiles.job_attributes.industry_trend.value, 0
            ),
            "min_experience": GraphNodeJob.convert_experience_to_min(
                job_profiles.basic_requirements.experience_years
            ),
            "major": major_raw,
            # --- 3. 业务维度属性 (用于离线算权重 & Agent 阅读) ---
            "industry": job_profiles.job_attributes.industry,
            "career_orientation": job_profiles.development_potential.career_orientation.value,
            # 软素质描述：存原文，Agent 规划时的黄金语料
            "comm_desc": job_profiles.professional_literacy.communication,
            "team_desc": job_profiles.professional_literacy.teamwork,
            "stress_desc": job_profiles.professional_literacy.stress_management,
            "logic_desc": job_profiles.professional_literacy.logic_thinking,
            "ethics_desc": job_profiles.professional_literacy.ethics,
            # 发展潜力描述
            "learn_desc": job_profiles.development_potential.learning_ability,
            "innov_desc": job_profiles.development_potential.innovation,
            "lead_desc": job_profiles.development_potential.leadership,
            "adapt_desc": job_profiles.development_potential.adaptability,
            "project_reqs": job_profiles.professional_skills.project_requirements,
            "intern_reqs": job_profiles.basic_requirements.internship_requirement,
            "special_reqs": job_profiles.basic_requirements.special_requirements,
        }

        job_node = GraphNodeJob(**job_node)
        return job_node


class GraphNodeCompetency(BaseModel):
    name: str = Field(description="能力节点唯一名称")
    category: str = Field(
        description="能力分类（如：核心专业技能/工具与平台能力/语言能力/证书要求）"
    )

    # --- 图构建血缘（离线计算 -> 在线推理） ---
    last_build_run_id: Optional[str] = Field(
        default=None, description="最后一次写入/更新该能力节点的 BuildRun ID"
    )
    last_build_ts: Optional[str] = Field(
        default=None, description="最后一次写入/更新该能力节点的时间戳"
    )

    # --- IDF 证据（离线固化 -> 在线解释） ---
    idf_weight: Optional[float] = Field(
        default=None, description="该能力的全局 IDF 稀缺度权重（与 r.idf_weight 同源）"
    )
    df: Optional[int] = Field(default=None, description="文档频次：包含该能力的岗位数")
    total_jobs: Optional[int] = Field(
        default=None, description="参与本次 IDF 统计的岗位总数"
    )
    prevalence: Optional[float] = Field(
        default=None, description="覆盖率：df / total_jobs"
    )
    idf_run_id: Optional[str] = Field(
        default=None, description="写入 IDF 证据的 BuildRun ID（与 r.idf_run_id 一致）"
    )
    idf_ts: Optional[str] = Field(default=None, description="写入 IDF 证据的时间戳")

    # 从JDAnalysisResult中提取能力枢纽信息，并转为GraphNodeCompetency对象列表
    @staticmethod
    def transform_competencies_to_graph_nodes(
        job: JDAnalysisResult,
    ) -> list["GraphNodeCompetency"]:

        jp: Profiles = job.profiles

        # 定义哪些字段需要被提取为“能力节点”
        source_map = {
            "核心专业技能": jp.professional_skills.core_skills,
            "工具与平台能力": jp.professional_skills.tool_capabilities,
            "语言能力": jp.professional_skills.language_requirements,
            "证书要求": jp.basic_requirements.certificates,
        }

        competencies = []
        for category, items in source_map.items():
            # 此时 items 已经是 List[str]
            for item in items:
                clean_name = item.strip()
                if clean_name and clean_name.lower() not in {
                    "无",
                    "无要求",
                    "未提及",
                    "不限",
                }:
                    competencies.append(
                        GraphNodeCompetency(name=clean_name, category=category)
                    )
        return competencies


class GraphEdgeEvolve(BaseModel):
    jaccard_high: float = Field(
        description="高区分度特征杰卡德相似度（目标：最大化）；来自 Competency 子图的加权 Jaccard"
    )
    cos_low: float = Field(
        description="低区分度背景相似度（目标：最大化）；语义文本与结构化属性的加权余弦融合"
    )
    salary_gain: float = Field(
        description="薪资增长潜力（目标：最大化）；有向指标，表示 from->to 的薪资提升趋势"
    )
    transfer_cost: float = Field(
        description="换岗成本/难度（目标：最小化或作为惩罚项）；由经验/学历/行业等迁移难度综合而来"
    )
    final_routing_cost: float = Field(
        description="最终路由成本；用于在线寻路（如 Dijkstra）的边权重，越小越优"
    )
    pareto_rank: int = Field(
        default=0, description="局部帕累托前沿层级（0 表示最优前沿）"
    )
    is_cross_macro: bool = Field(default=False, description="是否跨宏观社区（跨行业）")
    is_cross_micro: bool = Field(default=False, description="是否跨细分社区（跨赛道）")

    # --- Lineage / Decision Snapshot ---
    build_run_id: Optional[str] = Field(
        default=None,
        description="生成/更新该 EVOLVE_TO 的 BuildRun ID（用于版本清理与回溯）",
    )
    lineage_json: Optional[str] = Field(
        default=None,
        description="决策血缘快照（JSON 字符串）；记录候选来源、帕累托选择理由、guardrail 命中等",
    )

    # --- 关键中间量（便于在线快速解释/检索） ---
    base_attraction: Optional[float] = Field(
        default=None, description="基础吸引力分（未叠加惩罚项前的综合相似/收益分）"
    )
    rank_penalty: Optional[float] = Field(
        default=None,
        description="社区内排序/稀疏化带来的惩罚项（用于解释 final_routing_cost）",
    )
    cross_penalty: Optional[float] = Field(
        default=None, description="跨社区惩罚项（用于解释跨行业/跨赛道迁移成本）"
    )
    pareto_group_size: Optional[int] = Field(
        default=None, description="帕累托分组大小（同起点边数），用于解释稀疏化强度"
    )
    pareto_front_size: Optional[int] = Field(
        default=None, description="帕累托前沿保留边数（同起点），用于解释最终出边稀疏度"
    )


class GraphNodeBuildRun(BaseModel):
    id: str = Field(description="离线建图 Run ID，唯一标识")
    created_at: Optional[str] = Field(
        default=None, description="首次创建该 Run 的时间戳"
    )
    updated_at: Optional[str] = Field(
        default=None, description="该 Run 最近一次更新的时间戳"
    )
    status: str = Field(description="构建状态（如 running/completed/failed）")
    meta_json: str = Field(
        description="构建元信息快照（JSON 字符串），包含参数/统计/告警等"
    )
    jaccard_threshold: Optional[float] = Field(
        default=None, description="本次构建使用的 Jaccard 阈值（候选边硬筛选）"
    )
    coarse_resolution: Optional[float] = Field(
        default=None, description="粗聚类 Leiden resolution 参数（宏观社区划界）"
    )
    fine_resolution: Optional[float] = Field(
        default=None, description="细聚类 Leiden resolution 参数（细分社区划界）"
    )


class GraphEdgeRequires(BaseModel):
    # 注意：当前离线建图会将 r.weight 复用为“可计算用权重”（例如写入 IDF 后 r.weight = r.idf_weight），
    # 因此不应对 weight 设置 1.0 的上界约束。
    weight: float = Field(
        ..., ge=0, description="用于计算/排序的边权重（当前实现默认写入 IDF 权重）"
    )
    min_score: int = Field(
        ..., ge=1, le=5, description="岗位对该能力的最低要求强度（1-5）"
    )
    context: str = Field(
        description="JD/画像中对应维度的原始上下文文本（用于语义复水与解释）"
    )

    # --- 图构建血缘 ---
    build_run_id: Optional[str] = Field(
        default=None, description="写入该 REQUIRES 关系的 BuildRun ID"
    )
    build_ts: Optional[str] = Field(
        default=None, description="写入该 REQUIRES 关系的时间戳"
    )

    # --- IDF 证据（离线固化 -> 在线解释） ---
    local_weight: Optional[float] = Field(
        default=None,
        ge=0,
        description="局部权重快照（保留写入 IDF 前的原始 weight，便于回溯）",
    )
    idf_weight: Optional[float] = Field(
        default=None, ge=0, description="全局 IDF 稀缺度权重"
    )
    df: Optional[int] = Field(
        default=None, ge=0, description="文档频次：包含该能力的岗位数"
    )
    total_jobs: Optional[int] = Field(
        default=None, ge=0, description="参与本次 IDF 统计的岗位总数"
    )
    prevalence: Optional[float] = Field(
        default=None, ge=0, description="覆盖率：df / total_jobs"
    )
    idf_run_id: Optional[str] = Field(
        default=None, description="写入 IDF 证据的 BuildRun ID"
    )
    idf_ts: Optional[str] = Field(default=None, description="写入 IDF 证据的时间戳")


class JobCompetency(BaseModel):
    from_job: GraphNodeJob
    to_competency: GraphNodeCompetency
    edge: GraphEdgeRequires

    # 将JDAnalysisResult列表转为图数据库批量导入的 payload
    @staticmethod
    def transform_jobs_to_graph_payload(
        jobs: list[JDAnalysisResult],
    ) -> list["JobCompetency"]:
        """
                将 Pydantic 岗位画像列表，转化为图数据库批量导入的 payload
                划分节点属性和关系属性的标准：
                - 岗位的本体属性应为低区分度的属性，原因：
                    1. 这些属性通常是离散的、枚举的，适合用来物理过滤（如学历要求、行业等），可以直接在 Cypher WHERE 中使用，减少不必要的计算。
                    2. 这些属性的变化频率较低，适合存储在节点上，减少关系上的冗余数据。
                    3. 业务维度属性通常是文本化的，初期只存为节点属性。
                    之后可通过拆分语义单元（如核心技能、沟通能力等）来创建能力节点，并通过关系连接到岗位节点，
                    关系上存储原始描述作为上下文，便于后续的语义分析和 Agent 阅读。
                    4. 与岗位节点直连的节点将在后续参与杰卡德相似度计算，低区分度的属性会导致计算结果不准确。
        ·       - 能力枢纽(Competencies)是高区分度的属性，适合用来创建独立的能力节点，并通过关系连接到岗位节点。
        """
        batch_payload = []

        for job in jobs:
            # 1. 提取岗位的本体属性 (降维过滤用的硬属性)
            jp = job.profiles
            job_node = GraphNodeJob.transform_job_to_graph_node(job)

            # 2. 提取需要成为节点的能力枢纽 (Competencies)
            competency_nodes = (
                GraphNodeCompetency.transform_competencies_to_graph_nodes(job)
            )

            # 3. 建立关系，并注入 context (语义复水)
            for comp_node in competency_nodes:
                # --- 确保 context 永远是字符串 ---
                context_text = ""

                if comp_node.category == "核心专业技能":
                    # 核心技能对应项目背景
                    context_text = jp.professional_skills.project_requirements

                elif comp_node.category == "工具与平台能力":
                    # 工具能力对应行业知识描述（通常描述工具的应用场景）
                    context_text = jp.professional_skills.domain_knowledge

                elif comp_node.category == "证书要求":
                    # 证书对应特殊硬性要求
                    context_text = jp.basic_requirements.special_requirements

                elif comp_node.category == "语言能力":
                    # 语言能力如果没有专门描述，可以写一句标准引导
                    context_text = f"该岗位要求具备以下语言资质：{comp_node.name}"

                # 最终兜底：如果对应的描述字段也是空的，给出一句结构化说明
                # 这样 Agent 至少知道这个缺口是从哪个维度提取出来的
                if not context_text or context_text.strip() == "":
                    context_text = f"根据岗位画像，该职位明确要求掌握【{comp_node.category}】维度的能力：{comp_node.name}"

                # Categorical Weighting：用“所属维度”作为 TF 等效权重（可在 config.yaml 调参）
                tf_weight = float(
                    settings.graph_build.tf.category_weights.get(
                        comp_node.category, settings.graph_build.tf.default_weight
                    )
                )

                edge = GraphEdgeRequires(
                    # 注意：离线建图会在后续 update_idf_weights 阶段回写 idf_weight，
                    # 并将 r.weight 更新为 local_weight * idf_weight。
                    weight=tf_weight,
                    min_score=1,
                    context=context_text,  # 此时 context 100% 是字符串
                    local_weight=tf_weight,
                )

                batch_payload.append(
                    JobCompetency(from_job=job_node, to_competency=comp_node, edge=edge)
                )

        return batch_payload


class JobEvolution(BaseModel):
    from_job: GraphNodeJob
    to_job: GraphNodeJob
    edge: GraphEdgeEvolve


class GraphRequiresIdfEvidence(BaseModel):
    """IDF 证据批量回写 payload（用于 update_idf_weights）。

    说明：该模型是“写库契约”，确保回写字段与 Neo4j 存图字段一致。
    """

    comp_name: str = Field(description="能力名称（用于 MATCH (c:Competency {name})）")
    idf_weight: float = Field(ge=0, description="全局 IDF 稀缺度权重")
    df: int = Field(ge=0, description="文档频次：包含该能力的岗位数")
    total_jobs: int = Field(ge=0, description="参与本次 IDF 统计的岗位总数")
    prevalence: float = Field(ge=0, description="覆盖率：df / total_jobs")
