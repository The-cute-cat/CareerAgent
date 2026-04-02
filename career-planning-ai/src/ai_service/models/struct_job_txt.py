# ==========================================
# 1. 定义 Pydantic 数据模型 (对应 JSON Schema)
# 字段名已英文标准化，并与学生画像模型关键维度对齐
# ==========================================
import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from typing import List, Union
from ai_service.utils.logger_handler import log


class BasicRequirements(BaseModel):
    """
    基础要求：字段名与学生画像 BasicRequirements 保持一致，便于直接匹配
    """
    model_config = ConfigDict(populate_by_name=True)
    degree: str = Field(validation_alias="学历要求", description="岗位要求的最低学历：专科/本科/硕士/博士/不限")
    major: str = Field(validation_alias="专业背景", description="岗位要求的专业类别：计算机类/数学类/不限等")
    certificates: str = Field(validation_alias="证书要求", description="岗位必需的证书描述：必需/优先/无 + 具体证书名")
    internship_requirement: str = Field(validation_alias="实习经历要求", description="实习要求描述：必需/优先/无 + 月数等")
    experience_years: str = Field(validation_alias="工作年限", description="岗位要求的工作年限：应届/1-3 年/3-5 年/5 年 + 等")
    special_requirements: str = Field(validation_alias="特殊要求", description="其他特殊硬性要求")


class ProfessionalSkills(BaseModel):
    """
    职业技能：核心字段名与学生画像 ProfessionalSkills 保持语义对齐
    """
    model_config = ConfigDict(populate_by_name=True)
    core_skills: str = Field(validation_alias="核心专业技能", description="岗位必需的核心技术栈关键词描述")
    tool_capabilities: str = Field(validation_alias="工具与平台能力", description="岗位必需的软件、工具、平台描述")
    domain_knowledge: str = Field(validation_alias="行业_Domain_知识", description="岗位所需的行业知识深度描述")
    language_requirements: str = Field(validation_alias="语言能力", description="岗位外语要求：CET4/CET6/托福/雅思等")
    project_requirements: str = Field(validation_alias="项目经验", description="岗位对项目经验的具体要求描述")


class ProfessionalLiteracy(BaseModel):
    """
    职业素养：字段名与学生画像 ProfessionalLiteracy 完全一致，便于软硬素质对比
    注意：JD 中通常为文本描述，学生画像中为评分，匹配时需做转换
    """
    model_config = ConfigDict(populate_by_name=True)
    communication: str = Field(validation_alias="沟通能力", description="岗位对沟通能力的要求描述")
    teamwork: str = Field(validation_alias="团队协作", description="岗位对团队协作的要求描述")
    stress_management: str = Field(validation_alias="抗压能力", description="岗位对抗压能力的要求描述")
    logic_thinking: str = Field(validation_alias="逻辑思维", description="岗位对逻辑思维的要求描述")
    ethics: str = Field(validation_alias="责任心与职业道德", description="岗位对职业道德的要求描述")


class DevelopmentPotential(BaseModel):
    """
    发展潜力：字段名与学生画像 DevelopmentPotential 完全一致
    """
    model_config = ConfigDict(populate_by_name=True)
    learning_ability: str = Field(validation_alias="学习能力", description="岗位对学习能力的要求描述")
    innovation: str = Field(validation_alias="创新能力", description="岗位对创新能力的要求描述")
    leadership: str = Field(validation_alias="领导力潜质", description="岗位对领导力潜质的要求描述")
    career_orientation: str = Field(validation_alias="职业倾向性", description="岗位适合的职业倾向：管理/技术/创业/研究等")
    adaptability: str = Field(validation_alias="适应性", description="岗位对适应性的要求描述")


class JobAttributes(BaseModel):
    """
    岗位属性：英文命名
    """
    model_config = ConfigDict(populate_by_name=True)
    salary_competitiveness: str = Field(validation_alias="薪资竞争力", description="低/中/高")
    industry: str = Field(validation_alias="所属行业", description="互联网/金融/制造等")
    vertical_promotion_path: str = Field(validation_alias="垂直晋升路径", description="晋升路径列表 (如：初级->资深->组长)")
    prerequisite_roles: str = Field(validation_alias="前置岗位要求", description="通常需要先做过哪些岗位")
    lateral_transfer_directions: str = Field(validation_alias="横向转岗方向", description="可转岗方向列表（至少 5 个）")
    social_demand: str = Field(validation_alias="社会需求度", description="高/中/低")
    industry_trend: str = Field(validation_alias="行业发展趋势", description="朝阳/平稳/萎缩等")


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



"""
JD 数据转换工具
读取文件中的 JSON 数据，转换为 Pydantic 模型列表
"""


# ==========================================
# 2. 核心转换函数
# ==========================================

def convert_file_to_pydantic_list(
        file_path: Union[str, Path],
        encoding: str = 'utf-8',
        skip_invalid: bool = True,
        verbose: bool = True
) -> List[JDAnalysisResult]:
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
        'file_path': str(path.absolute()),
        'success': False,
        'total_items': 0,
        'valid_items': 0,
        'invalid_items': 0,
        'errors': []
    }


    # 检查文件
    if not path.exists():
        msg = f"文件不存在：{path.absolute()}"
        report['errors'].append(msg)
        if verbose:
            log.error(f"❌ {msg}")
        return [], report

    if not path.is_file():
        msg = f"路径不是文件：{path.absolute()}"
        report['errors'].append(msg)
        if verbose:
            log.error(f"❌ {msg}")
        return [], report

    # 读取文件内容
    try:
        with open(path, 'r', encoding=encoding) as f:
            content = f.read().strip()
        if verbose:
            log.info(f"✓ 读取文件成功 ({len(content)} 字符)")
    except Exception as e:
        msg = f"读取文件失败：{e}"
        report['errors'].append(msg)
        if verbose:
            log.error(f"❌ {msg}")
        return [], report

    # 解析 JSON
    data = None

    try:
        data = json.loads(content)
        if verbose:
            log.info("✓ JSON 格式正确")
    except json.JSONDecodeError as e:
        msg = f"JSON 格式错误：{e.msg} (第 {e.lineno} 行，第 {e.colno} 列)"
        report['errors'].append(msg)

        return [], report

    # 确保数据是列表
    if not isinstance(data, list):
        data = [data]

    report['total_items'] = len(data)
    if verbose:
        log.info(f"📊 共解析 {len(data)} 条数据")

    # 转换为 Pydantic 模型
    results = []
    invalid_details = []

    for i, item in enumerate(data):
        try:
            result = JDAnalysisResult.model_validate(item)
            results.append(result)
            report['valid_items'] += 1
        except ValidationError as e:
            report['invalid_items'] += 1
            job_id = item.get('job_id', f'索引 {i}')

            if skip_invalid:
                if verbose and len(invalid_details) < 5:
                    log.warning(f"⚠ 第 {i + 1} 条数据验证失败 ({job_id})")
                invalid_details.append({
                    'index': i,
                    'job_id': job_id,
                    'error': str(e)[:200]
                })
            else:
                msg = f"第 {i + 1} 条数据验证失败：{e}"
                report['errors'].append(msg)
                if verbose:
                    log.error(f"❌ {msg}")
                return [], report

    report['success'] = True

    if verbose:
        log.info(f"✅ 转换完成！")
        log.info(f"📊 总数据数：{report['total_items']}")
        log.info(f"📊 有效数据：{report['valid_items']}")
        log.info(f"📊 无效数据：{report['invalid_items']}")

    return results




def load_jd_to_pydantic(
        file_path: Union[str, Path],
        encoding: str = 'utf-8',
        verbose: bool = True
) -> List[JDAnalysisResult]:
    """
    便捷函数：加载文件并返回 Pydantic 模型列表

    参数:
        file_path: 文件路径
        encoding: 文件编码
        verbose: 是否输出日志

    返回:
        List[JDAnalysisResult]

    异常:
        ValueError: 转换失败时抛出
    """
    results= convert_file_to_pydantic_list(
        file_path,
        encoding=encoding,
        verbose=verbose
    )

    return results



# ==========================================
# 4. 使用示例
# ==========================================

if __name__ == "__main__":
    # 示例 1: 转换单个文件
    print("\n" + "=" * 70)
    print("示例 1: 转换单个文件")
    print("=" * 70)

    file_path = r"E:\软件工程相关资料\项目比赛\服创 2026\岗位.json"

    try:
        results = convert_file_to_pydantic_list(
            file_path,
            verbose=True
        )

        if results:
            print(f"\n✅ 成功转换 {len(results)} 条数据\n")

            # 显示前 3 条
            for i, job in enumerate(results[:3]):
                print(f"[{i + 1}] {job.job_id}: {job.job_name}")
                print(f"    学历：{job.profiles.basic_requirements.degree}")
                print(f"    核心技能：{job.profiles.professional_skills.core_skills[:50]}...")
                print(f"    薪资：{job.profiles.job_attributes.salary_competitiveness}")
                print()

    except Exception as e:
        print(f"❌ 转换失败：{e}")
