# ==========================================
# 1. 定义 Pydantic 数据模型 (对应 JSON Schema)
# 字段名已英文标准化，并与学生画像模型关键维度对齐
# ==========================================
from pydantic import BaseModel, ConfigDict, Field


class BasicRequirements(BaseModel):
    """
    基础要求：字段名与学生画像 BasicRequirements 保持一致，便于直接匹配
    """
    model_config = ConfigDict(populate_by_name=True)
    degree: str = Field(alias="学历要求", description="岗位要求的最低学历：专科/本科/硕士/博士/不限")
    major: str = Field(alias="专业背景", description="岗位要求的专业类别：计算机类/数学类/不限等")
    certificates: str = Field(alias="证书要求", description="岗位必需的证书描述：必需/优先/无 + 具体证书名")
    internship_requirement: str = Field(alias="实习经历要求", description="实习要求描述：必需/优先/无 + 月数等")
    experience_years: str = Field(alias="工作年限", description="岗位要求的工作年限：应届/1-3 年/3-5 年/5 年 + 等")
    special_requirements: str = Field(alias="特殊要求", description="其他特殊硬性要求")


class ProfessionalSkills(BaseModel):
    """
    职业技能：核心字段名与学生画像 ProfessionalSkills 保持语义对齐
    """
    model_config = ConfigDict(populate_by_name=True)
    core_skills: str = Field(alias="核心专业技能", description="岗位必需的核心技术栈关键词描述")
    tool_capabilities: str = Field(alias="工具与平台能力", description="岗位必需的软件、工具、平台描述")
    domain_knowledge: str = Field(alias="行业_Domain_知识", description="岗位所需的行业知识深度描述")
    language_requirements: str = Field(alias="语言能力", description="岗位外语要求：CET4/CET6/托福/雅思等")
    project_requirements: str = Field(alias="项目经验", description="岗位对项目经验的具体要求描述")


class ProfessionalLiteracy(BaseModel):
    """
    职业素养：字段名与学生画像 ProfessionalLiteracy 完全一致，便于软硬素质对比
    注意：JD 中通常为文本描述，学生画像中为评分，匹配时需做转换
    """
    model_config = ConfigDict(populate_by_name=True)
    communication: str = Field(alias="沟通能力", description="岗位对沟通能力的要求描述")
    teamwork: str = Field(alias="团队协作", description="岗位对团队协作的要求描述")
    stress_management: str = Field(alias="抗压能力", description="岗位对抗压能力的要求描述")
    logic_thinking: str = Field(alias="逻辑思维", description="岗位对逻辑思维的要求描述")
    ethics: str = Field(alias="责任心与职业道德", description="岗位对职业道德的要求描述")


class DevelopmentPotential(BaseModel):
    """
    发展潜力：字段名与学生画像 DevelopmentPotential 完全一致
    """
    model_config = ConfigDict(populate_by_name=True)
    learning_ability: str = Field(alias="学习能力", description="岗位对学习能力的要求描述")
    innovation: str = Field(alias="创新能力", description="岗位对创新能力的要求描述")
    leadership: str = Field(alias="领导力潜质", description="岗位对领导力潜质的要求描述")
    career_orientation: str = Field(alias="职业倾向性", description="岗位适合的职业倾向：管理/技术/创业/研究等")
    adaptability: str = Field(alias="适应性", description="岗位对适应性的要求描述")


class JobAttributes(BaseModel):
    """
    岗位属性：英文命名
    """
    model_config = ConfigDict(populate_by_name=True)
    salary_competitiveness: str = Field(alias="薪资竞争力", description="低/中/高")
    industry: str = Field(alias="所属行业", description="互联网/金融/制造等")
    vertical_promotion_path: str = Field(alias="垂直晋升路径", description="晋升路径列表 (如：初级->资深->组长)")
    prerequisite_roles: str = Field(alias="前置岗位要求", description="通常需要先做过哪些岗位")
    lateral_transfer_directions: str = Field(alias="横向转岗方向", description="可转岗方向列表（至少 5 个）")
    social_demand: str = Field(alias="社会需求度", description="高/中/低")
    industry_trend: str = Field(alias="行业发展趋势", description="朝阳/平稳/萎缩等")


class Profiles(BaseModel):
    """
    岗位详细画像聚合
    """
    model_config = ConfigDict(populate_by_name=True)
    basic_requirements: BasicRequirements = Field(alias="基础要求")
    professional_skills: ProfessionalSkills = Field(alias="职业技能")
    professional_literacy: ProfessionalLiteracy = Field(alias="职业素养")
    development_potential: DevelopmentPotential = Field(alias="发展潜力")
    job_attributes: JobAttributes = Field(alias="岗位属性")


class JDAnalysisResult(BaseModel):
    """
    JD 分析最终结果
    """
    model_config = ConfigDict(populate_by_name=True)
    job_id: str = Field(description="职位 ID")
    job_name: str = Field(description="职位名称")
    profiles: Profiles = Field(alias="profiles", description="岗位详细画像")