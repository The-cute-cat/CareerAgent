import datetime
import re
import unicodedata
from typing import List, Optional, Literal
from dateutil import parser

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
)
from ai_service.services import log

__all__=[
    "QuizDetailItem",
    "ProjectExperience",
    "InternshipExperience",
    "SkillDetail",
    "ToolDetail",
    "LanguageDetail",
    "StudentFormProfile"
]


# --- 嵌套子模型 ---


class QuizDetailItem(BaseModel):
    type: Literal["choice", "open_ended"] = Field(description="题目类型：选择题/开放题")
    question: str = Field(description="测评题目")
    answer: str = Field(description="用户答案")


class ProjectExperience(BaseModel):
    isCompetition: bool = Field(alias="competition", description="boolean(是否竞赛）")
    name: str = Field(description="项目/竞赛名称")
    desc: str = Field(description="项目描述")


class InternshipExperience(BaseModel):
    company: str = Field(
        description="实习单位全称，若文本仅有简称则保留简称，不臆造公司信息。"
    )
    role: str = Field(
        description="实习岗位名称，如'数据分析实习生'、'产品经理实习生'。"
    )
    date: List[datetime.date] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="""实习日期范围，必须包含两个元素：[开始日期, 结束日期]。格式统一为 YYYY-MM-DD, 如果是类似"至今"这样描述当前时间日期，直接输出"至今"。"""
    )
    desc: str = Field(
        description="实习职责与产出，优先提取动作+结果信息，如'搭建报表并将统计耗时从2小时降至20分钟'。"
    )

    @field_validator("date", mode="before")
    @classmethod
    def parse_date_list(cls, v):
        if not isinstance(v, list):
            return v

        PRESENT_RE = re.compile(r"(今|目|现|present|current|now|active|today|至今)", re.IGNORECASE)

        cleaned_dates = []
        for item in v:
            # 如果已经是 datetime.date 对象，直接保留
            if isinstance(item, datetime.date):
                cleaned_dates.append(item)
                continue

            s = str(item).strip()

            # Unicode 归一化 (NFKC 格式可以把各种变体字符转为标准形式)
            s = unicodedata.normalize('NFKC', s)
            # 强制过滤掉所有非打印字符
            s = "".join(ch for ch in s if ch.isprintable())

            s = s.lower()  # 统一小写，方便后续语义匹配

            # 1. 优先处理语义词 (dateutil 搞不定的)
            if PRESENT_RE.search(s):
                cleaned_dates.append(datetime.date.today())
                log.info(f"解析到语义日期 '{item}'，已转换为当前日期 {datetime.date.today()}")
                continue

            # 将中文字符替换为 dateutil 认识的横杠
            s = s.replace("年", "-").replace("月", "-").replace("日", "")
            # 强力去除所有空格（解决 '2024 . 05' 这种问题）
            s = re.sub(r'\s+', '', s)
            # 将连续的非数字字符替换为单个横杠（解决 '--' 或 '...' 这种问题）
            s = re.sub(r'[^0-9]+', '-', s)
            # 修剪两端的横杠
            s = s.strip('-')

            try:
                # 2. 利用 dateutil 的黑科技进行解析
                # fuzzy=True: 自动忽略字符串里的杂质
                # yearfirst=True: 优先按年-月-日的顺序解析，符合中文习惯
                # default: 当字符串缺失某部分时用默认值补齐，避免解析失败（如缺月日时补齐为1月1日）
                default_date = datetime.datetime(2000, 1, 1)
                parsed_dt = parser.parse(s, fuzzy=True, yearfirst=True, default=default_date)
                cleaned_dates.append(parsed_dt.date())
            except (ValueError, OverflowError):
                # 3. 如果 dateutil 也跪了，尝试简单的正则补齐逻辑 (如 2024-5 -> 2024-05-01)
                # 或者直接放行，让 Pydantic 抛错触发 Instructor 的 AI 重试
                log.warning(f"无法解析的日期: {item}")
        return cleaned_dates


class SkillDetail(BaseModel):
    name: str = Field(description="技能名称")
    score: float = Field(description="技能分数")


class ToolDetail(BaseModel):
    name: str = Field(description="工具名称")
    score: float = Field(description="工具分数")


class LanguageDetail(BaseModel):
    type: Literal["英语", "日语", "其他"] = Field(description="语种：英语/日语/其他")
    level: Literal["四级", "六级", "托福", "雅思", "其他"] = Field(description="水平：四级/六级/托福/雅思/其他")
    other: str = Field(description="其他相关信息")


# --- 主画像模型 ---

class StudentFormProfile(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    # 1. 基础背景
    education: Optional[Literal["专科", "本科", "硕士", "博士", "其他"]] = Field(
        None,
        alias="education",
        description="最高学历。仅允许‘专科/本科/硕士/博士/其他’，无法判断时返回 null。",
    )
    educationOther: Optional[str] = Field(
        None,
        alias="educationOther",
        description="其他学历信息，当 education 为‘其他’时填写, 无法判断时返回 null。比如:曾在美国留学等。",
    )
    major: Optional[List[str]] = Field(
        None,
        alias="major",
        description="就读专业全称，尽量标准化为正式专业名称（如‘计算机科学与技术’），无法确认时返回 null。",
    )
    graduation_date: Optional[str] = Field(
        None,
        alias="graduationDate",
        description="毕业时间。统一输出为 YYYY-MM；若原文缺失或无法解析为年月则返回 null。",
    )

    # 2. 能力矩阵
    languages: Optional[List[LanguageDetail]] = Field(
        None,
        alias="languages",
        description="掌握的语言列表（自然语言），去重后输出，如'英语'。无信息时返回空列表。",
    )
    certificates: Optional[List[str]] = Field(
        None,
        alias="certificates",
        description="证书列表，提取正式证书名称（如‘CET-6’‘软考中级’），去重后输出。"
    )
    certificates_other: Optional[str] = Field(
        None,
        alias="certificatesOther",
        description="外语水平选择'其他'后显示，与水平信息在同一行，供 AI 填写具体信息；无信息时返回 null。比如:学习过世界语。",
    )
    skills: Optional[List[SkillDetail]] = Field(
        None,
        alias="skills",
        description="专业技能列表，提取可迁移能力与专业能力（如‘机器学习建模’‘需求分析’），避免与 tools 重复。",
    )
    tools: Optional[List[ToolDetail]] = Field(
        None,
        alias="tools",
        description="工具/平台/框架列表（如‘Excel’‘Power BI’‘PyTorch’‘Figma’），去重后输出。",
    )

    # 3. 实践与产出 (这里是 AI 提取的“工作区”)
    # 修改：别名不与计算属性冲突，使用内部标识符
    code_ability: Optional[str] = Field(
        None,
        alias="codeAbility",
        description="代码仓库链接。仅提取明确 URL(如 GitHub/Gitee), 不同链接用逗号分隔；无链接时返回 null。",
    )

    # AI 会根据 description 填充这两个列表
    projects: Optional[List[ProjectExperience]] = Field(
        None,
        alias="projects",  # 避开 projects 别名
        description=(
            "从文本提取的项目经历明细。每个元素需尽量包含 "
            "name/role/content/output；无项目信息时返回空列表。"
        ),
    )
    internships: Optional[List[InternshipExperience]] = Field(
        None,
        alias="internships",  # 避开 internships 别名
        description=(
            "从文本提取的实习经历明细。每个元素需尽量包含 "
            "company/role/date/desc；无实习信息时返回空列表。"
        ),
    )

    # 4. 素质与规划
    quiz: None = Field(
        None,
        alias="quiz",
        description="保持为空对象，AI 不需要填充此字段，后续会根据其他字段内容自动生成测验分数结果。",
    )
    innovation: Optional[str] = Field(
        None,
        alias="innovation",
        description="创新能力相关表述，提取原文中的能力评价或案例摘要；无信息时返回 null。比如:“优化了某算法，效率提升 20%”",
    )
    target_job: Optional[str] = Field(
        None,
        alias="targetJob",
        description="目标岗位名称，优先提取最明确的单一岗位（如‘数据分析师’）；无信息时返回 null。",
    )
    target_industries: Optional[List[str]] = Field(
        None,
        alias="targetIndustries",
        description="目标行业列表（如‘互联网’‘智能制造’‘金融科技’），去重后输出。",
    )
    priorities: None = Field(
        None,
        alias="priorities",
        description="保持为空列表，AI 不需要填充此字段，后续会根据其他字段内容自动生成优先级排序结果。",
    )

    # --- 自动化坍缩：将结构化列表转为前端需要的字符串 ---

    # --- 校验器优化 ---

    @field_validator("graduation_date", mode="before")
    @classmethod
    def validate_graduation_date(cls, v):
        if not v or v in [
            "未知",
            "无",
            "暂无",
            "不详",
            "N/A",
            "null",
            "none",
            "未提供",
        ]:
            return None

        if isinstance(v, str):
            v = v.replace(".", "-").strip()
            # 强化正则：匹配 YYYY-MM，且月份在 01-12 之间
            if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
                # 抛出异常会触发 Instructor 的 self-correction (重试)
                raise ValueError(
                    "日期格式错误。必须为 YYYY-MM (月分需为01-12)，例如 2025-06"
                )
            return v
        return v
