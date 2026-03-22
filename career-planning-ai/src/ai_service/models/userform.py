from pydantic import BaseModel, Field
from typing import List, Optional


class UserForm(BaseModel):
    education: str = Field(..., description="学历")
    major: str = Field(..., description="专业")
    graduationDate: Optional[str] = Field(None, description="毕业时间 YYYY-MM")
    languages: List[str] = Field(..., description="外语能力列表")
    certificates: Optional[List[str]] = Field(default=[], description="证书列表")
    skills: List[str] = Field(..., description="技能列表")
    tools: List[str] = Field(..., description="工具列表")
    codeLinks: Optional[str] = Field(None, description="代码仓库链接")
    projects: List[str] = Field(default=[], description="项目经历")
    internships: List[str] = Field(default=[], description="实习经历")
    quizScores: Optional[str] = Field(None, description="素质测评结果")
    innovation: Optional[str] = Field(None, description="创新案例描述")
    targetJob: Optional[str] = Field(None, description="目标岗位")
    targetIndustries: List[str] = Field(default=[], description="期望行业列表")
    priorities: List[str] = Field(default=[], description="职业优先级")

    def to_llm_context(self) -> str:
        # 1. 预处理：将列表转为逗号分隔的字符串（如果没有数据则显示“无”）
        def fmt_list(l): return ", ".join(l) if l else "无"

        # 2. 使用 f-string 配合多行字符串 (triple quotes)
        # 注意：每一行都清晰定义，方便 AI 像阅读简历一样阅读
        return f"""
            <candidate_raw_data>
            [基本背景]
            - 学历: {self.education}
            - 专业: {self.major}
            - 毕业时间: {self.graduationDate or "未提供"}

            [专业技能]
            - 技能列表: {fmt_list(self.skills)}
            - 工具平台: {fmt_list(self.tools)}
            - 外语能力: {fmt_list(self.languages)}
            - 代码仓库: {self.codeLinks or "无"}

            [实践经历]
            - 项目经历: {" | ".join(self.projects) if self.projects else "暂无项目经历"}
            - 实习经历: {" | ".join(self.internships) if self.internships else "暂无实习经历"}

            [个人素质与意向]
            - 测评自述: {self.quizScores or "未提供"}
            - 创新表现: {self.innovation or "未提供"}
            - 目标岗位: {self.targetJob or "待定"}
            - 期望行业: {fmt_list(self.targetIndustries)}
            - 核心价值观优先级: {" > ".join(self.priorities) if self.priorities else "未排序"}
            </candidate_raw_data>
                    """.strip()
