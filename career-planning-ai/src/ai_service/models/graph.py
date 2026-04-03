import re
from pydantic import BaseModel, Field
from typing import List, Optional
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
    id: str
    job_name: str
    coarse_community_id: int = 0  # 第一次聚类算法分的宏观行业社区标签
    fine_community_id: int = 0  # 第二次聚类算法分的细分职业社区标签


    # --- 2. 物理过滤属性 (全部数字化/序数化，用于 Cypher WHERE) ---
    # 转为数字，方便图库里做 >= 的大小比较
    min_degree: int = 0
    demand_rank: int = 2
    trend_rank: int = 0
    salary_rank: int = 2
    min_experience: int = 0
    major: str = ""

    # --- 3. 业务维度属性 (用于离线算权重 & Agent 阅读) ---
    industry: str = ""
    career_orientation: str = ""

    # 软素质描述：存原文，Agent 规划时的黄金语料
    comm_desc: str = ""
    team_desc: str = ""
    stress_desc: str = ""
    logic_desc: str = ""

    # --- 4. 发展潜力描述 ---
    learn_desc: str = ""
    innov_desc: str = ""
    lead_desc: str = ""
    adapt_desc: str = ""
    ethics_desc: str = ""

    # --- 5. 项目需求描述 ---
    project_reqs: str = ""
    intern_reqs: str = ""

    # --- 6. 特殊要求描述 ---
    special_reqs: str = ""

    @staticmethod
    def convert_experience_to_min(experience_str: str) -> int:
        if not experience_str or "应届" in experience_str:
            return 0
        num_match = re.search(r'(\d+)', experience_str)
        return int(num_match.group(1)) if num_match else 0

    # 从JDAnalysisResult中提取job节点信息，并对数据进行规范化处理，并转为GraphNodeJob对象
    @staticmethod
    def transform_job_to_graph_node(job: JDAnalysisResult) -> "GraphNodeJob":
        """
        从JDAnalysisResult中提取job节点信息，并对数据进行规范化处理，并转为GraphNodeJob对象
        """
        job_profiles: Profiles = job.profiles
        job_node = {
            # --- 1. 唯一标识 ---
            "id": job.job_id,
            "job_name": job.job_name,
            "coarse_community_id": 0,  # 第一次聚类算法分的宏观行业社区标签
            "fine_community_id": 0,  # 第二次聚类算法分的细分职业社区标签
            # --- 2. 物理过滤属性 (全部数字化/序数化，用于 Cypher WHERE) ---
            # 转为数字，方便图库里做 >= 的大小比较
            "min_degree": {"不限": 0, "专科": 1, "本科": 2, "硕士": 3, "博士": 4}.get(
                job_profiles.basic_requirements.degree, 0
            ),
            "demand_rank": {"低": 1, "中": 2, "高": 3}.get(
                job_profiles.job_attributes.social_demand, 2
            ),
            "trend_rank": {"萎缩": -1, "平稳": 0, "朝阳": 1}.get(
                job_profiles.job_attributes.industry_trend, 0
            ),
            "salary_rank": {"低": 1, "中": 2, "高": 3}.get(
                job_profiles.job_attributes.salary_competitiveness, 2
            ),
            "min_experience": GraphNodeJob.convert_experience_to_min(
                job_profiles.basic_requirements.experience_years),
            # --- 3. 业务维度属性 (用于离线算权重 & Agent 阅读) ---
            "industry": job_profiles.job_attributes.industry,
            "career_orientation": job_profiles.development_potential.career_orientation,
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
    name: str
    category: str

    # 将用逗号分隔的字符串转为标准competency节点
    @staticmethod
    def parse_competencies(
        competencies_str: str, category: str
    ) -> list["GraphNodeCompetency"]:
        competencies = []

        if not competencies_str or competencies_str.strip() in {"无", "无要求", "未提及", "不限"}:
            return competencies

        for item in competencies_str.split(","):
            item = item.strip()
            if item:
                competencies.append(
                    GraphNodeCompetency(
                        name=item,
                        category=category,
                    )
                )
        return competencies

    # 从JDAnalysisResult中提取能力枢纽信息，并转为GraphNodeCompetency对象列表
    @staticmethod
    def transform_competencies_to_graph_nodes(
        job: JDAnalysisResult,
    ) -> list["GraphNodeCompetency"]:
        job_profiles: Profiles = job.profiles
        competencies_strlist = [
            job_profiles.professional_skills.core_skills,
            job_profiles.professional_skills.tool_capabilities,
            job_profiles.professional_skills.domain_knowledge,
            job_profiles.basic_requirements.certificates,
        ]

        competencies = []
        for idx, comp_str in enumerate(competencies_strlist):
            category = [
                "核心专业技能",
                "工具与平台能力",
                "行业_Domain_知识",
                "证书要求",
            ][idx]
            competencies.extend(GraphNodeCompetency.parse_competencies(comp_str, category))

        return competencies


class GraphEdgeEvolve(BaseModel):
    jaccard_high: float  # 高区分度特征杰卡德相似度（目标 1：最大化）
    cos_low: float  # 低区分度属性加权余弦相似度（目标 2：最大化）
    salary_gain: float  # 薪资增长潜力（目标 3：最大化）
    transfer_cost: float  # 换岗成本 / 难度（目标 4：可选最小化）
    final_routing_cost: float  # 综合路由成本


class GraphEdgeRequires(BaseModel):
    weight: float = Field(..., ge=0, le=1.0)
    min_score: int = Field(..., ge=1, le=5)
    context: str  # JD里的原话


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
            job_node = GraphNodeJob.transform_job_to_graph_node(job)

            # 2. 提取需要成为节点的能力枢纽 (Competencies)
            competency_nodes = GraphNodeCompetency.transform_competencies_to_graph_nodes(
                job
            )

            # 3. 构建岗位-能力关系，关系属性存原文上下文, 此时reqiure关系无权重。目前context置空，之后存JD里的原话，供Agent规划时参考
            for comp_node in competency_nodes:
                edge = GraphEdgeRequires(
                    weight=0.0,  # 初始权重，后续根据JD文本分析结果调整
                    min_score=1,  # 初始最低分数要求，后续根据JD文本分析结果调整
                    context="",  # JD里的原话，后续存储在关系属性里
                )

                batch_payload.append(
                    JobCompetency(
                        from_job=job_node, to_competency=comp_node, edge=edge
                    )
                )

        return batch_payload


class JobEvolution(BaseModel):
    from_job: GraphNodeJob
    to_job: GraphNodeJob
    edge: GraphEdgeEvolve
