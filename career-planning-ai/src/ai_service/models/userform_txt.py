from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from typing import List, Optional, Literal
import re


# --- 嵌套子模型 ---


class ProjectExperience(BaseModel):
    name: str = Field(
        description="项目名称，如'校园二手交易平台'、'毕业设计-智能问答系统'等具体项目标题"
    )
    role: str = Field(
        description="在项目中担任的角色，如'前端负责人'、'核心开发'、'组长'、'独立开发者'等"
    )
    content: str = Field(
        description="核心工作内容及技术应用，详细描述做了什么、用了什么技术栈、解决了什么问题，如'使用Vue3+Element Plus搭建前端页面，实现用户认证、商品发布、订单管理等功能，采用Pinia进行状态管理'"
    )
    output: str = Field(
        description="项目成果或量化表现，如'系统上线后日均访问量500+'、'获得校级创新创业大赛二等奖'、'代码量约8000行'等可量化的成果"
    )


class InternshipExperience(BaseModel):
    company: str = Field(
        description="实习单位名称，填写公司全称或常用简称，如'腾讯科技有限公司'、'字节跳动'、'阿里巴巴'"
    )
    position: str = Field(
        description="实习岗位名称，如'后端开发实习生'、'算法实习生'、'产品运营实习生'"
    )
    duration: str = Field(
        description="实习起止时间或时长，格式尽量统一为'YYYY-MM至YYYY-MM'或'X个月'，如'2024-06至2024-09'、'3个月'"
    )
    content: str = Field(
        description="实习期间的主要职责、工作内容及产出成果，如'负责用户模块的接口开发，独立完成登录注册功能，优化数据库查询性能提升30%'"
    )


# --- 主画像模型 ---


class StudentFormProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    # 1. 基础背景
    education: Optional[Literal["专科", "本科", "硕士", "博士", "其他"]] = Field(
        None,
        alias="education",
        description="最高学历，必须从['专科', '本科', '硕士', '博士', '其他']中选择一个，如'本科'",
    )
    major: Optional[str] = Field(
        None,
        alias="major",
        description="就读专业全称，填写教育部标准专业名称，如'计算机科学与技术'、'软件工程'、'人工智能'、'数据科学与大数据技术'",
    )
    graduation_date: Optional[str] = Field(
        None,
        alias="graduationDate",
        description="毕业时间，严格格式为YYYY-MM，月份必须为01-12，如'2025-06'、'2024-12'",
    )

    # 2. 能力矩阵
    languages: List[str] = Field(
        default_factory=list,
        alias="languages",
        description="掌握的语言列表，仅包括自然语言。自然语言如['英语', '日语']",
    )
    certificates: List[str] = Field(
        default_factory=list,
        alias="certificates",
        description="持有的证书列表，填写证书全称，如['软件设计师(中级)', 'AWS云计算工程师', '全国计算机等级考试二级Python', '教师资格证']",
    )
    skills: List[str] = Field(
        default_factory=list,
        alias="skills",
        description="拥有的专业技能列表，填写具体技能而非笼统描述，如['Spring Boot后端开发', 'Vue前端开发', 'MySQL数据库设计', '机器学习模型训练', 'Docker容器化部署']",
    )
    tools: List[str] = Field(
        default_factory=list,
        alias="tools",
        description="会使用的工具列表，填写具体的开发工具和平台，如['VS Code', 'Git', 'Linux', 'MySQL Workbench', 'Postman', 'Jira']",
    )

    # 3. 实践与产出 (这里是 AI 提取的"工作区")
    # 修改：别名不与计算属性冲突，使用内部标识符
    code_links: Optional[str] = Field(
        None,
        alias="codeLinks",
        description="代码仓库链接，填写GitHub、GitLab、Gitee等平台的仓库地址，如'https://github.com/username/project-name'",
    )

    # AI 会根据 description 填充这两个列表
    internal_project_list: List[ProjectExperience] = Field(
        default_factory=list,
        alias="internal_project_list",  # 避开 projects 别名
        description="从文本中提取的详细项目经历列表，每个项目包含项目名称、担任角色、核心工作内容、项目成果四个字段。注意：课程作业、实验项目也算作项目经历",
        exclude=True,
    )
    internal_internship_list: List[InternshipExperience] = Field(
        default_factory=list,
        alias="internal_internship_list",  # 避开 internships 别名
        description="从文本中提取的详细实习经历列表，每段实习包含公司名称、岗位名称、实习时长、工作职责四个字段。注意：暑期实习、日常实习、兼职都算作实习经历",
        exclude=True,
    )

    # 4. 素质与规划
    quiz_scores: Optional[str] = Field(
        None,
        alias="quizScores",
        description="问卷得分或测评结果，如'职业倾向测试：创新型85分'、'MBTI：ENFP'、'性格测试：外向型'",
    )
    innovation: Optional[str] = Field(
        None,
        alias="innovation",
        description="创新能力描述，包括创新意识、创新实践、创新成果等方面，如'曾获得创新创业大赛省级二等奖，具备较强的产品创新思维'",
    )
    target_job: Optional[str] = Field(
        None,
        alias="targetJob",
        description="目标岗位，填写具体岗位名称，如'后端开发工程师'、'前端开发工程师'、'算法工程师'、'产品经理'、'数据分析师'",
    )
    target_industries: List[str] = Field(
        default_factory=list,
        alias="targetIndustries",
        description="目标行业列表，填写期望从事的行业，如['互联网/IT', '金融科技', '人工智能', '电子商务', '教育科技']",
    )
    priorities: List[str] = Field(
        default_factory=list,
        alias="priorities",
        description="发展方向的优先级列表，按重要性排序，如['技术成长', '薪资待遇', '工作稳定性', '创新空间', '团队氛围']",
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
