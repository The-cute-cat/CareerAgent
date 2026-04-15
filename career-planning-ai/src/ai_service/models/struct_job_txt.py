# ==========================================
# 1. 定义 Pydantic 数据模型 (对应 JSON Schema)
# 字段名已英文标准化，并与学生画像模型关键维度对齐
# ==========================================
import json
import re
from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from typing import List, Tuple, Union, Any, Dict

from ai_service.models.job_portrait import JobPortrait
from ai_service.utils.logger_handler import log


class DegreeEnum(StrEnum):
    UNLIMITED = "不限"
    JUNIOR_COLLEGE = "专科"
    BACHELOR = "本科"
    MASTER = "硕士"
    DOCTOR = "博士"


class LevelEnum(StrEnum):
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"


class IndustryTrendEnum(StrEnum):
    SHRINKING = "萎缩"
    STABLE = "平稳"
    GROWING = "朝阳"


class CareerOrientationEnum(StrEnum):
    MANAGEMENT = "管理型"
    TECHNOLOGY = "技术型"
    BUSINESS = "业务型"
    RESEARCH = "研究型"
    COMPREHENSIVE = "综合型"
    UNLIMITED = "不限"


def robust_list_parser(v):
    """通用的防呆列表解析器：兼容大模型的字符串/列表混吐现象"""
    if isinstance(v, str):
        # 兼容中文逗号、分号、顿号、换行
        items = re.split(r"[,，;；、\n]", v.strip())
        return list({item.strip() for item in items if item.strip()})
    if isinstance(v, list):
        return list({str(item).strip() for item in v if item and str(item).strip()})
    return []


class BasicRequirements(BaseModel):
    """
    基础要求：字段名与学生画像 BasicRequirements 保持一致，便于直接匹配
    """

    model_config = ConfigDict(populate_by_name=True)
    degree: DegreeEnum = Field(
        validation_alias="学历要求",
        default=DegreeEnum.UNLIMITED,
        description="岗位要求的最低学历层次，必须从枚举值中选择：不限/专科/本科/硕士/博士",
    )
    major: str = Field(
        validation_alias="专业背景",
        default="不限",
        description="岗位要求的专业背景，优先填写具体专业名称（如'计算机科学与技术'），若不限专业则填'不限'",
    )
    certificates: List[str] = Field(
        validation_alias="证书要求",
        default_factory=list,
        description="岗位明确要求的证书列表，如['英语六级', 'PMP证书', '注册会计师']，若无明确要求则返回空列表",
    )
    internship_requirement: str = Field(
        validation_alias="实习经历要求",
        default="",
        description="岗位对实习经历的具体要求，包括是否必需、最短时长、领域要求等，如'需有互联网公司3个月以上实习经历'，若无要求则填空字符串",
    )
    experience_years: str = Field(
        validation_alias="工作年限",
        default="不限",
        description="岗位要求的最低工作年限，优先填写具体年限范围（如'1-3年'、'5年以上'），应届生岗填'应届生'，不限则填'不限'",
    )
    special_requirements: str = Field(
        validation_alias="特殊要求",
        default="",
        description="岗位的其他特殊要求，如'能接受出差'、'需持有驾照'等，若无特殊要求则填空字符串",
    )

    @field_validator("degree", mode="before")
    @classmethod
    def fallback_degree(cls, v):
        if v not in [e.value for e in DegreeEnum]:
            log.warning(f"学历值 '{v}' 不在枚举范围内，降级为'不限'")
            return DegreeEnum.UNLIMITED
        return v

    @field_validator("certificates", mode="before")
    @classmethod
    def clean_certs(cls, v):
        return robust_list_parser(v)


class ProfessionalSkills(BaseModel):
    """
    职业技能：核心字段名与学生画像 ProfessionalSkills 保持语义对齐
    """

    model_config = ConfigDict(populate_by_name=True)
    core_skills: List[str] = Field(
        validation_alias="核心专业技能",
        default_factory=list,
        description="岗位明确要求的核心专业技能，需提取具体技能名称，如['Python编程', '数据分析', '项目管理']，避免泛泛描述，若未明确则返回空列表",
    )
    tool_capabilities: List[str] = Field(
        validation_alias="工具与平台能力",
        default_factory=list,
        description="岗位要求的具体工具或平台，如['MySQL', 'Docker', 'Git', 'Excel']，需填写具体名称而非类别，若未明确则返回空列表",
    )
    language_requirements: List[str] = Field(
        validation_alias="语言能力",
        default_factory=list,
        description="岗位要求的语言能力及熟练度，如['英语-流利', '日语-读写']，若未明确要求则返回空列表",
    )
    domain_knowledge: str = Field(
        validation_alias="行业_Domain_知识",
        default="",
        description="岗位所需的行业领域知识深度要求，如'熟悉金融风控流程'、'了解电商运营模式'，若未明确则填空字符串",
    )
    project_requirements: str = Field(
        validation_alias="项目经验",
        default="",
        description="岗位对项目经验的具体要求，包括项目类型、规模、角色等，如'有完整的电商系统开发经验'，若未明确则填空字符串",
    )

    @field_validator(
        "core_skills", "tool_capabilities", "language_requirements", mode="before"
    )
    @classmethod
    def clean_skills(cls, v):
        return robust_list_parser(v)


class ProfessionalLiteracy(BaseModel):
    """
    职业素养：字段名与学生画像 ProfessionalLiteracy 完全一致，便于软硬素质对比
    注意：JD 中通常为文本描述，学生画像中为评分，匹配时需做转换
    """

    model_config = ConfigDict(populate_by_name=True)
    communication: str = Field(
        validation_alias="沟通能力",
        default="",
        description="岗位对沟通能力的具体要求，包括沟通场景和程度，如'跨部门协调沟通能力'、'能撰写专业文档'，若未明确则填空字符串",
    )
    teamwork: str = Field(
        validation_alias="团队协作",
        default="",
        description="岗位对团队协作的具体要求，包括团队规模、协作方式等，如'能带领5人以上团队'、'具备跨团队协作经验'，若未明确则填空字符串",
    )
    stress_management: str = Field(
        validation_alias="抗压能力",
        default="",
        description="岗位对抗压能力的具体要求，包括压力来源和应对方式，如'能适应项目上线前的高强度工作'，若未明确则填空字符串",
    )
    logic_thinking: str = Field(
        validation_alias="逻辑思维",
        default="",
        description="岗位对逻辑思维能力的具体要求，如'具备系统性分析问题的能力'、'能独立完成业务逻辑设计'，若未明确则填空字符串",
    )
    ethics: str = Field(
        validation_alias="责任心与职业道德",
        default="",
        description="岗位对责任心和职业道德的具体要求，如'严格遵守数据保密规定'、'对代码质量负责'，若未明确则填空字符串",
    )


class DevelopmentPotential(BaseModel):
    """
    发展潜力：字段名与学生画像 DevelopmentPotential 完全一致
    """

    model_config = ConfigDict(populate_by_name=True)
    learning_ability: str = Field(
        validation_alias="学习能力",
        default="",
        description="岗位对学习能力的具体要求，如'能快速掌握新技术'、'具备自主学习能力'，若未明确则填空字符串",
    )
    innovation: str = Field(
        validation_alias="创新能力",
        default="",
        description="岗位对创新能力的具体要求，如'有技术创新成果优先'、'能提出改进方案'，若未明确则填空字符串",
    )
    leadership: str = Field(
        validation_alias="领导力潜质",
        default="",
        description="岗位对领导力潜质的具体要求，如'有团队管理潜力'、'能培养新人'，若未明确则填空字符串",
    )
    adaptability: str = Field(
        validation_alias="适应性",
        default="",
        description="岗位对适应性的具体要求，如'能快速适应业务变化'、'接受岗位轮换'，若未明确则填空字符串",
    )
    career_orientation: CareerOrientationEnum = Field(
        validation_alias="职业倾向性",
        default=CareerOrientationEnum.UNLIMITED,
        description="岗位的职业发展倾向，必须从枚举值中选择：管理型/技术型/业务型/研究型/综合型/不限",
    )


class JobAttributes(BaseModel):
    """
    岗位属性：英文命名
    """

    model_config = ConfigDict(populate_by_name=True)
    salary_competitiveness: LevelEnum = Field(
        validation_alias="薪资竞争力",
        default=LevelEnum.MEDIUM,
        description="该岗位在行业内的薪资竞争力水平，必须从枚举值中选择：低/中/高，需结合市场数据和岗位级别判断",
    )
    social_demand: LevelEnum = Field(
        validation_alias="社会需求度",
        default=LevelEnum.MEDIUM,
        description="该岗位在当前就业市场中的需求程度，必须从枚举值中选择：低/中/高，需参考招聘网站数据和行业报告",
    )
    industry_trend: IndustryTrendEnum = Field(
        validation_alias="行业发展趋势",
        default=IndustryTrendEnum.STABLE,
        description="该岗位所属行业的发展趋势，必须从枚举值中选择：萎缩/平稳/朝阳",
    )
    industry: str = Field(
        validation_alias="所属行业",
        default="不限",
        description="岗位所属的具体行业领域，优先填写细分类别（如'互联网金融'、'新零售'、'SaaS软件'），若无法判断则填'不限'",
    )
    vertical_promotion_path: str = Field(
        validation_alias="垂直晋升路径",
        default="",
        description="岗位的垂直晋升路径，需填写具体职位序列，如'初级工程师→中级工程师→高级工程师→技术专家'，若无法判断则填空字符串",
    )
    prerequisite_roles: str = Field(
        validation_alias="前置岗位要求",
        default="",
        description="担任该岗位通常需要的前置职位，如'需有产品助理或运营专员经验'，若未明确则填空字符串",
    )
    lateral_transfer_directions: List[str] = Field(
        validation_alias="横向转岗方向",
        default=[],
        description="从该岗位可以横向转岗的方向，如'产品经理可转向项目管理或运营管理'，若无法判断则填空字符串",
    )

    @field_validator("salary_competitiveness", "social_demand", mode="before")
    @classmethod
    def fallback_level(cls, v):
        if v not in [e.value for e in LevelEnum]:
            log.warning(f"等级值 '{v}' 不在枚举范围内，降级为'中'")
            return LevelEnum.MEDIUM
        return v

    @field_validator("industry_trend", mode="before")
    @classmethod
    def fallback_trend(cls, v):
        if v not in [e.value for e in IndustryTrendEnum]:
            log.warning(f"行业趋势值 '{v}' 不在枚举范围内，降级为'平稳'")
            return IndustryTrendEnum.STABLE
        return v


class Profiles(BaseModel):
    """
    岗位详细画像聚合
    """

    model_config = ConfigDict(populate_by_name=True)
    basic_requirements: BasicRequirements = Field(validation_alias="基础要求")
    professional_skills: ProfessionalSkills = Field(validation_alias="职业技能")
    professional_literacy: ProfessionalLiteracy = Field(validation_alias="职业素养")
    development_potential: DevelopmentPotential = Field(validation_alias="发展潜力")
    job_attributes: JobAttributes = Field(validation_alias="岗位属性")


class JDAnalysisResult(BaseModel):
    """
    JD 分析最终结果
    """

    model_config = ConfigDict(populate_by_name=True)
    job_id: str = Field(description="职位 ID")
    job_name: str = Field(description="职位名称")
    profiles: Profiles = Field(validation_alias="profiles", description="岗位详细画像")

    @field_validator("job_id", mode="before")
    @classmethod
    def convert_to_str(cls, v):
        """自动将整数类型的 job_id 转换为字符串"""
        if isinstance(v, int):
            return str(v)
        return v



"""
JD 数据转换工具
读取文件中的 JSON 数据，转换为 Pydantic 模型列表
"""


# ==========================================
# 2. 核心转换函数
# ==========================================
def ensure_dict(value: Any) -> Dict[str, Any]:
    """将 JSON 字段安全转换为 dict"""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return {}
        return json.loads(value)
    raise TypeError(f"不支持的 JSON 类型: {type(value)}")

def build_jd_result_from_portrait(portrait: JobPortrait) -> JDAnalysisResult:
    """
    将 job_profile 表中的一条数据转换为 JDAnalysisResult。

    约定：
    1. skills_req 与 JDAnalysisResult.profiles 的内容结构对应；
    2. 若 skills_req 本身已是完整 JDAnalysisResult 结构（含 profiles），则直接补齐 job_id / job_name；
    3. Milvus 主键 job_id 使用 job_profile.id 的字符串形式，保证唯一稳定。
    """
    skills_req = ensure_dict(portrait.skills_req)
    if not skills_req:
        raise ValueError("skills_req 为空，无法转换为 JDAnalysisResult")

    job_id = str(portrait.id)
    job_name = portrait.job_title or f"岗位_{portrait.id}"

    payload = dict(skills_req)

    # 情况1：skills_req 已经是完整结构
    if "profiles" in payload:
        payload.setdefault("job_id", job_id)
        payload.setdefault("job_name", job_name)
        return JDAnalysisResult.model_validate(payload)

    # 情况2：skills_req 仅为 profiles 内容
    jd_payload = {
        "job_id": job_id,
        "job_name": job_name,
        "profiles": payload
    }
    return JDAnalysisResult.model_validate(jd_payload)



def convert_file_to_pydantic_list(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    skip_invalid: bool = True,
    verbose: bool = True,
) -> Tuple[List[JDAnalysisResult], dict]:
    """
    将文件中的 JSON 数据转换为 Pydantic 模型列表

    参数:
        file_path: 文件路径（支持 .txt, .json 等格式）
        encoding: 文件编码，默认 'utf-8'
        skip_invalid: 是否跳过无效数据（不抛出异常）
        verbose: 是否输出详细日志

    返回:
        results : List[JDAnalysisResult] Pydantic 模型列表
    """
    path = Path(file_path)

    report = {
        "file_path": str(path.absolute()),
        "success": False,
        "total_items": 0,
        "valid_items": 0,
        "invalid_items": 0,
        "errors": [],
    }

    # 检查文件
    if not path.exists():
        msg = f"文件不存在：{path.absolute()}"
        report["errors"].append(msg)
        if verbose:
            log.error(f"[ERROR] {msg}")
        return [], report

    if not path.is_file():
        msg = f"路径不是文件：{path.absolute()}"
        report["errors"].append(msg)
        if verbose:
            log.error(f"[ERROR] {msg}")
        return [], report

    # 读取文件内容
    try:
        with open(path, "r", encoding=encoding) as f:
            content = f.read().strip()
        if verbose:
            log.info(f"[OK] 读取文件成功 ({len(content)} 字符)")
    except Exception as e:
        msg = f"读取文件失败：{e}"
        report["errors"].append(msg)
        if verbose:
            log.error(f"[ERROR] {msg}")
        return [], report

    # 解析 JSON
    data = None

    try:
        data = json.loads(content)
        if verbose:
            log.info("[OK] JSON 格式正确")
    except json.JSONDecodeError as e:
        msg = f"JSON 格式错误：{e.msg} (第 {e.lineno} 行，第 {e.colno} 列)"
        report["errors"].append(msg)

        return [], report

    # 确保数据是列表
    if not isinstance(data, list):
        data = [data]

    report["total_items"] = len(data)
    if verbose:
        log.info(f"[INFO] 共解析 {len(data)} 条数据")

    # 转换为 Pydantic 模型
    results = []
    invalid_details = []

    for i, item in enumerate(data):
        try:
            result = JDAnalysisResult.model_validate(item)
            results.append(result)
            report["valid_items"] += 1
        except ValidationError as e:
            report["invalid_items"] += 1
            job_id = item.get("job_id", f"索引 {i}")

            if skip_invalid:
                if verbose and len(invalid_details) < 5:
                    log.warning(f"[WARN] 第 {i + 1} 条数据验证失败 ({job_id})")
                invalid_details.append(
                    {"index": i, "job_id": job_id, "error": str(e)[:200]}
                )
            else:
                msg = f"第 {i + 1} 条数据验证失败：{e}"
                report["errors"].append(msg)
                if verbose:
                    log.error(f"[ERROR] {msg}")
                return [], report

    report["success"] = True

    if verbose:
        log.info(f"[SUCCESS] 转换完成")
        log.info(f"[STATS] 总数据数: {report['total_items']}")
        log.info(f"[STATS] 有效数据: {report['valid_items']}")
        log.info(f"[STATS] 无效数据: {report['invalid_items']}")

    return results, report


def load_jd_to_pydantic(
    file_path: Union[str, Path], encoding: str = "utf-8", verbose: bool = True
) -> Tuple[List[JDAnalysisResult], dict]:
    """
    便捷函数：加载文件并返回 Pydantic 模型列表和转换报告

    参数:
        file_path: 文件路径
        encoding: 文件编码
        verbose: 是否输出日志

    返回:
        Tuple[List[JDAnalysisResult], dict]: (模型列表, 转换报告)

    异常:
        ValueError: 转换失败时抛出
    """
    results, report = convert_file_to_pydantic_list(
        file_path, encoding=encoding, verbose=verbose
    )

    return results, report


# ==========================================
# 4. 使用示例
# ==========================================

if __name__ == "__main__":
    import sys

    # 示例 1: 转换单个文件
    print("\n" + "=" * 70)
    print("示例: 转换 JD 文件为 Pydantic 模型")
    print("=" * 70)

    # 从命令行参数获取文件路径，或使用默认测试路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 默认使用项目 data 目录下的示例文件
        file_path = Path(__file__).parent.parent.parent.parent / "data" / "jobs.json"
        print(f"提示: 未指定文件路径，使用默认路径: {file_path}")
        if not file_path.exists():
            print("默认文件不存在，请通过命令行参数指定文件路径:")
            print("  python struct_job_txt.py <文件路径>")
            sys.exit(1)

    try:
        results, report = convert_file_to_pydantic_list(file_path, verbose=True)

        if results:
            print(f"\n成功转换 {len(results)} 条数据\n")

            # 显示前 3 条
            for i, job in enumerate(results[:3]):
                print(f"[{i + 1}] {job.job_id}: {job.job_name}")
                print(f"    学历：{job.profiles.basic_requirements.degree}")
                print(
                    f"    核心技能：{job.profiles.professional_skills.core_skills[:50]}..."
                )
                print(f"    薪资：{job.profiles.job_attributes.salary_competitiveness}")
                print()

    except Exception as e:
        print(f"[ERROR] 转换失败：{e}")
