from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from typing import List, Optional, Literal
import re

# --- 嵌套子模型 ---

class ProjectExperience(BaseModel):
    name: str = Field(description="项目名称")
    role: str = Field(description="担任角色")
    content: str = Field(description="核心工作内容及技术应用")
    output: str = Field(description="项目成果或量化表现")

class InternshipExperience(BaseModel):
    company: str = Field(description="实习单位名称")
    position: str = Field(description="实习岗位")
    duration: str = Field(description="实习起止时间或时长")
    content: str = Field(description="实习职责及产出")

# --- 主画像模型 ---

class StudentFormProfile(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    # 1. 基础背景
    education: Optional[Literal["专科", "本科", "硕士", "博士", "其他"]] = Field(
        None, alias="education", description="最高学历"
    )
    major: Optional[str] = Field(
        None, alias="major", description="就读专业全称"
    )
    graduation_date: Optional[str] = Field(
        None, alias="graduationDate", description="毕业时间，严格格式为 YYYY-MM"
    )

    # 2. 能力矩阵
    languages: List[str] = Field(default_factory=list, alias="languages")
    certificates: List[str] = Field(default_factory=list, alias="certificates")
    skills: List[str] = Field(default_factory=list, alias="skills")
    tools: List[str] = Field(default_factory=list, alias="tools")

    # 3. 实践与产出 (这里是 AI 提取的“工作区”)
    # 修改：别名不与计算属性冲突，使用内部标识符
    code_links: Optional[str] = Field(None, alias="codeLinks")
    
    # AI 会根据 description 填充这两个列表
    internal_project_list: List[ProjectExperience] = Field(
        default_factory=list,
        alias="internal_project_list", # 避开 projects 别名
        description="从文本中提取的详细项目经历列表",
        exclude=True 
    )
    internal_internship_list: List[InternshipExperience] = Field(
        default_factory=list,
        alias="internal_internship_list", # 避开 internships 别名
        description="从文本中提取的详细实习经历列表",
        exclude=True
    )

    # 4. 素质与规划
    quiz_scores: Optional[str] = Field(None, alias="quizScores")
    innovation: Optional[str] = Field(None, alias="innovation")
    target_job: Optional[str] = Field(None, alias="targetJob")
    target_industries: List[str] = Field(default_factory=list, alias="targetIndustries")
    priorities: List[str] = Field(default_factory=list, alias="priorities")

    # --- 自动化坍缩：将结构化列表转为前端需要的字符串 ---

    @computed_field(alias="projects") # 这里才是真正输出给前端的键名
    @property
    def projects_display(self) -> str:
        if not self.internal_project_list:
            return "无"
        return "\n".join([
            f"在【{p.name}】项目担任{p.role}，工作内容：{p.content}。成果：{p.output}" 
            for p in self.internal_project_list
        ])
    
    @computed_field(alias="internships") # 这里才是真正输出给前端的键名
    @property
    def internships_display(self) -> str:
        if not self.internal_internship_list:
            return "无"
        return "\n".join([
            f"{i.duration} 在【{i.company}】担任{i.position}，职责：{i.content}" 
            for i in self.internal_internship_list
        ])

    # --- 校验器优化 ---

    @field_validator("graduation_date", mode="before")
    @classmethod
    def validate_graduation_date(cls, v):
        if not v or v in ["未知", "无", "暂无", "不详", "N/A", "null", "none", "未提供"]:
            return None
        
        if isinstance(v, str):
            v = v.replace(".", "-").strip()
            # 强化正则：匹配 YYYY-MM，且月份在 01-12 之间
            if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
                # 抛出异常会触发 Instructor 的 self-correction (重试)
                raise ValueError("日期格式错误。必须为 YYYY-MM (月分需为01-12)，例如 2025-06")
            return v
        return v