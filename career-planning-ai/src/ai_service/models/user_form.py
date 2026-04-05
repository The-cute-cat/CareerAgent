from pydantic import BaseModel, Field

from ai_service.models.user_form_profile import LanguageDetail, SkillDetail, ToolDetail, ProjectExperience, \
    InternshipExperience, QuizDetailItem


class UserForm(BaseModel):
    education: str | None = Field(None, description="学历：高中/专科/本科/硕士/博士/其他")
    educationOther: str | None = None
    major: str | None = Field(None, description="专业类别")
    graduationDate: str | None = Field(None, description="毕业日期,YYYY-MM格式")
    languages: list[LanguageDetail] | None = Field(None, description="语言能力")
    certificates: list[str] | None = Field(None, description="证书列表")
    certificatesOther: str | None = None
    summary: str | None = Field(None, description="ai对用户整体情况的总结描述，黄金语料")
    strengths: list[str] | None = Field(None, description="优势列表")
    weaknesses: list[str] | None = Field(None, description="劣势列表")
    skills: list[SkillDetail] | None = Field(None, description="技能列表")
    tools: list[ToolDetail] | None = Field(None, description="工具列表")
    codeLinks: str | None = Field(None, description="代码仓库链接,如GitHub/Gitee,多个逗号分隔")
    projects: list[ProjectExperience] | None = Field(None, description="项目经历列表")
    internships: list[InternshipExperience] | None = Field(None, description="实习经历列表")
    quizDetail: list[QuizDetailItem] | None = Field(None,
                                                    description="测评详细，包含沟通能力、抗压能力、学习能力等题目以及用户答案")
    innovation: str | None = Field(None, description="创新表现描述")
    targetJob: str | None = Field(None, description="目标岗位")
    targetIndustries: list[str] | None = Field(None, description="期望行业列表")
    priorities: list[str] | None = Field(None, description="核心价值观优先级列表，包含技术成长、薪资、稳定等")

    def to_llm_context(self) -> str:
        # 1. 预处理：将列表转为逗号分隔的字符串（如果没有数据则显示“无”）
        def fmt_list(l):
            return ", ".join(map(str, l)) if l else "无"

        # 2. 使用 f-string 配合多行字符串 (triple quotes)
        # 注意：每一行都清晰定义，方便 AI 像阅读简历一样阅读
        return f"""
            <candidate_raw_data>
            [基本背景]
            - 学历: {self.education}
            - 专业: {self.major}
            - 毕业时间: {self.graduationDate or "未提供"}
            - 其他学历信息: {self.educationOther or "无"}

            [专业技能]
            - 技能列表: {fmt_list(self.skills)}
            - 工具平台: {fmt_list(self.tools)}
            - 外语能力: {fmt_list(self.languages)}
            - 证书: {fmt_list(self.certificates)}
            - 其他证书信息: {self.certificatesOther or "无"}
            - 代码仓库: {self.codeLinks or "无"}

            [实践经历]
            - 项目经历: {fmt_list([p.name for p in self.projects]) if self.projects else "无"}
            - 实习经历: {fmt_list([i.company for i in self.internships]) if self.internships else "无"}

            [个人素质与意向]
            - 测评详细: {self.quizDetail or "未提供"}
            - 创新表现: {self.innovation or "未提供"}
            - 目标岗位: {self.targetJob or "待定"}
            - 目标职位: {self.targetJob or "待定"}
            - 期望行业: {fmt_list(self.targetIndustries)}
            - 核心价值观优先级: {" > ".join([p for p in self.priorities]) if self.priorities else "未排序"}
            - AI总结: {self.summary or "无"}
            - 优势: {fmt_list(self.strengths)}
            - 劣势: {fmt_list(self.weaknesses)}
            </candidate_raw_data>
                    """.strip()
