from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    computed_field,
)
from typing import List, Optional, Literal
import re

# --- 嵌套子模型 ---


class ProjectExperience(BaseModel):
    name: str = Field(
        description="项目名称。优先提取正式项目名；若无明确名称，可用‘某电商推荐系统项目’这类可识别短语。"
    )
    role: str = Field(
        description="在项目中的角色或职责身份，如‘后端开发/算法实习生/项目负责人’。"
    )
    content: str = Field(
        description="核心工作内容与技术应用，需包含做了什么、用到哪些技术/方法，避免只写技术名。"
    )
    output: str = Field(
        description="项目成果或量化表现，优先提取可量化结果（如‘准确率提升5%’、‘服务日活1万+’）；无量化时写明确业务结果。"
    )


class InternshipExperience(BaseModel):
    company: str = Field(
        description="实习单位全称，若文本仅有简称则保留简称，不臆造公司信息。"
    )
    position: str = Field(
        description="实习岗位名称，如‘数据分析实习生’、‘产品经理实习生’。"
    )
    duration: str = Field(
        description="实习起止时间或时长，尽量保留原文时间表达（如‘2024.07-2024.10’或‘3个月’）。"
    )
    content: str = Field(
        description="实习职责与产出，优先提取动作+结果信息，如‘搭建报表并将统计耗时从2小时降至20分钟’。"
    )


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
    major: Optional[str] = Field(
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
    languages: List[str] = Field(
        default_factory=list,
        alias="languages",
        description="掌握的语言列表（自然语言或编程语言均可），去重后输出，如‘英语’‘Python’。无信息时返回空列表。",
    )
    certificates: List[str] = Field(
        default_factory=list,
        alias="certificates",
        description="证书列表，提取正式证书名称（如‘CET-6’‘软考中级’），去重后输出。",
    )
    skills: List[str] = Field(
        default_factory=list,
        alias="skills",
        description="专业技能列表，提取可迁移能力与专业能力（如‘机器学习建模’‘需求分析’），避免与 tools 重复。",
    )
    tools: List[str] = Field(
        default_factory=list,
        alias="tools",
        description="工具/平台/框架列表（如‘Excel’‘Power BI’‘PyTorch’‘Figma’），去重后输出。",
    )

    # 3. 实践与产出 (这里是 AI 提取的“工作区”)
    # 修改：别名不与计算属性冲突，使用内部标识符
    code_links: Optional[str] = Field(
        None,
        alias="codeLinks",
        description="代码仓库链接。仅提取明确 URL（如 GitHub/Gitee）；无链接时返回 null。",
    )

    # AI 会根据 description 填充这两个列表
    internal_project_list: List[ProjectExperience] = Field(
        default_factory=list,
        alias="internal_project_list",  # 避开 projects 别名
        description=(
            "从文本提取的项目经历明细。每个元素需尽量包含 "
            "name/role/content/output；无项目信息时返回空列表。"
        ),
        exclude=True,
    )
    internal_internship_list: List[InternshipExperience] = Field(
        default_factory=list,
        alias="internal_internship_list",  # 避开 internships 别名
        description=(
            "从文本提取的实习经历明细。每个元素需尽量包含 "
            "company/position/duration/content；无实习信息时返回空列表。"
        ),
        exclude=True,
    )

    # 4. 素质与规划
    quiz_scores: Optional[str] = Field(
        None,
        alias="quizScores",
        description="问卷得分或测评结果原文（如‘职业兴趣：RIA’或‘综合得分82’）。无信息时返回 null。",
    )
    innovation: Optional[str] = Field(
        None,
        alias="innovation",
        description="创新能力相关表述，提取原文中的能力评价或案例摘要；无信息时返回 null。",
    )
    target_job: Optional[str] = Field(
        None,
        alias="targetJob",
        description="目标岗位名称，优先提取最明确的单一岗位（如‘数据分析师’）；无信息时返回 null。",
    )
    target_industries: List[str] = Field(
        default_factory=list,
        alias="targetIndustries",
        description="目标行业列表（如‘互联网’‘智能制造’‘金融科技’），去重后输出。",
    )
    priorities: List[str] = Field(
        default_factory=list,
        alias="priorities",
        description="发展方向优先级关键词列表（如‘城市优先’‘薪资优先’‘成长优先’），按文本表达顺序输出。",
    )
    # --- 自动化坍缩：将结构化列表转为前端需要的字符串 ---

    @computed_field(alias="projects")  # 这里才是真正输出给前端的键名
    @property
    def projects_display(self) -> str:
        if not self.internal_project_list:
            return "无"
        return "\n".join(
            [
                f"在【{p.name}】项目担任{p.role}，工作内容：{p.content}。成果：{p.output}"
                for p in self.internal_project_list
            ]
        )

    @computed_field(alias="internships")  # 这里才是真正输出给前端的键名
    @property
    def internships_display(self) -> str:
        if not self.internal_internship_list:
            return "无"
        return "\n".join(
            [
                f"{i.duration} 在【{i.company}】担任{i.position}，职责：{i.content}"
                for i in self.internal_internship_list
            ]
        )

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
