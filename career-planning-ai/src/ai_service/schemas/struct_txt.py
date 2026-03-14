from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


# --- 子维度模型定义 ---

class BasicRequirements(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    degree: str = Field(alias="学历", description="当前最高学历：专科/本科/硕士/博士")
    major: str = Field(alias="专业背景", description="所学专业全称及类别")
    certificates: List[str] = Field(alias="证书", description="已获得的证书列表,如,CET-6、计算机二级、软考中级")
    internship_months: int = Field(alias="实习时长", description="累计实习总月数，无则填 0")
    status: str = Field(alias="求职状态", description="应届生/在校生/有工作经验")


class ProfessionalSkills(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # 评分项改为 int，方便 Layer 1 向量计算
    skill_tags: List[str] = Field(alias="核心专业技能", description="提取学生掌握的技术栈关键词列表")
    tool_tags: List[str] = Field(alias="工具与平台能力", description="掌握的软件、工具、平台列表")
    domain_knowledge: int = Field(alias="行业领域知识评分", ge=1, le=5, description="对目标行业的了解程度评分 1-5")
    language_skills: List[str] = Field(alias="语言能力", description="外语等级及口语水平描述")
    project_score: int = Field(alias="项目经验丰富度", ge=1, le=5, description="项目经验的复杂度与完整度评分 1-5")


class ProfessionalLiteracy(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    communication: int = Field(alias="沟通能力", ge=1, le=5, description="沟通表达与协调能力评分 1-5")
    teamwork: int = Field(alias="团队协作", ge=1, le=5, description="团队配合与协作精神评分 1-5")
    stress_management: int = Field(alias="抗压能力", ge=1, le=5, description="面对压力时的情绪调节与执行力评分 1-5")
    logic_thinking: int = Field(alias="逻辑思维", ge=1, le=5, description="分析问题与解决问题的逻辑性评分 1-5")
    ethics: int = Field(alias="责任心与职业道德", ge=1, le=5, description="工作态度与职业操守评分 1-5")


class DevelopmentPotential(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    learning_ability: int = Field(alias="学习能力", ge=1, le=5, description="自学能力与知识迁移能力评分 1-5")
    innovation: int = Field(alias="创新能力", ge=1, le=5, description="打破常规与提出新方案的能力评分 1-5")
    leadership: int = Field(alias="领导力潜质", ge=1, le=5, description="组织能力与影响力潜质评分 1-5")
    career_orientation: str = Field(alias="职业倾向性", description="管理型/技术型/创意型/研究型")
    adaptability: int = Field(alias="环境适应性", ge=1, le=5, description="对新环境、新岗位的适应速度评分 1-5")


class SpecialConstraints(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # 这里是核心：身体与环境禁忌
    physical_limit: Optional[str] = Field(alias="生理限制", description="学生自述的特殊生理限制，如心脏病、过敏、色弱等，无则填'无'")
    value_conflict: Optional[str] = Field(alias="价值观限制", description="不能接受的行业或公司文化，如：拒绝烟草行业")
    env_limit: Optional[str] = Field(alias="环境限制", description="无法接受的环境，如：恐高、无法出差、无法加班")
    schedule_limit: Optional[str] = Field(alias="时间习惯限制", description="无法接受的时间安排，如：拒绝夜班、拒绝轮班")
    personal_demands: Optional[str] = Field(alias="其他特殊要求", description="如：必须在某个城市、需要办公空间有特定设施")


class PracticalExperience(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    # 存储详细文本，用于 Layer 2 深度对比和规划报告生成
    project_details: str = Field(alias="项目经历详情", description="详细描述参与过的项目、角色及成果")
    intern_details: str = Field(alias="实习经历详情", description="详细描述实习岗位职责、核心产出")
    campus_activities: str = Field(alias="校园/实践活动", description="社团、志愿活动、社会实践等描述")
    competition_exp: str = Field(alias="竞赛获奖详情", description="参加过的比赛、获得的奖项及个人贡献")


# --- 总模型定义 ---

class StudentProfile(BaseModel):
    """
    学生画像总模型：结合了用于召回的量化维度和用于规划的文本维度
    """
    model_config = ConfigDict(populate_by_name=True)

    basic_info: BasicRequirements = Field(alias="基础信息", description="学生的基础背景")
    skills: ProfessionalSkills = Field(alias="专业技能", description="学生的技术能力画像")
    literacy: ProfessionalLiteracy = Field(alias="职业素养", description="学生的软素质评价")
    potential: DevelopmentPotential = Field(alias="发展潜力", description="学生的长期发展潜质")
    constraints: SpecialConstraints = Field(alias="个人限制", description="学生的红线与避坑指南")
    experience: PracticalExperience = Field(alias="实践详情", description="支撑上述评分的原始经历证据")