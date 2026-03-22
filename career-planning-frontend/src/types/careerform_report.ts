

// ==================== CareerForm 表单类型定义 ====================

import type {  QuizScores,SkillTool } from "./careerform_question"

/** 通用响应结果 */
import type {  Result } from "./type"


/** 学历类型（标准选项） */
export type EducationType = '高中' | '专科' | '本科' | '硕士' | '博士' | '其他' | string

/** 语言能力项 */
export interface Language {
  /** 语种：英语/日语/其他 */
  type: string
  /** 水平：四级/六级/托福/雅思/其他 */
  level: string
  /** 其他说明（当选择"其他"时填写） */
  other: string
}


/** 项目经历项 */
export interface Project {
  /** 是否为竞赛项目 */
  isCompetition: boolean
  /** 项目名称/竞赛名称 */
  name: string
  /** 项目描述 */
  desc: string
}

/** 实习经历项 */
export interface Internship {
  /** 公司名称 */
  company: string
  /** 担任岗位 */
  role: string
  /** 实习日期范围 [开始日期, 结束日期] */
  date: Date[]
  /** 工作内容描述 */
  desc: string
}

/** 素质测评完成状态 */

/** 职业优先级项 */
export interface Priority {
  /** 优先级值：tech-技术成长, salary-薪资, stable-稳定 */
  value: 'tech' | 'salary' | 'stable'
  /** 显示标签 */
  label: string
}

/** 代码能力 */
export interface CodeAbility {
  /** GitHub/Gitee 仓库链接，多个用逗号分隔 */
  links: string
}

/** 职业表单数据（完整的表单数据结构） */
export interface CareerFormData {
  /** 学历 */
  education: EducationType | ''
  /** 学历其他说明（当选择"其他"时） */
  educationOther: string
  /** 专业类别 */
  major: string[]
  /** 预计毕业日期，格式 YYYY-MM */
  graduationDate: string
  /** 外语能力列表 */
  languages: Language[]
  /** 专业证书列表 */
  certificates: string[]
  /** 证书其他说明（当选择"其他"时） */
  certificateOther: string
  /** 专业技能列表 */
  skills: SkillTool[]
  /** 工具掌握列表 */
  tools:  SkillTool[]
  /** 代码能力 */
  codeAbility: CodeAbility
  /** 项目经历列表 */
  projects: Project[]
  /** 实习经历列表 */
  internships: Internship[]
  /** 素质测评分数（沟通/抗压/学习，各0-100） */
  quizScores?: QuizScores
  /** 创新案例描述 */
  innovation: string
  /** 目标岗位 */
  targetJob: string
  /** 期望行业列表 */
  targetIndustries: string[]
  /** 职业优先级排序 */
  priorities: Priority[]
}


/** 提交职业表单的请求参数 */
export interface CareerFormSubmitDTO {
  /** 学历 */
  education: string
  /** 专业 */
  major: string
  /** 毕业时间 */
  graduationDate?: string
  /** 外语能力 */
  languages: Language[]
  /** 证书列表 */
  certificates: string[]
  /** 技能列表 */
  skills:  SkillTool[]
  /** 工具列表 */
  tools:  SkillTool[]
  /** 代码仓库链接 */
  codeLinks?: string
  /** 项目经历 */
  projects: Project[]
  /** 实习经历 */
  internships: Internship[]
  /** 素质测评分数（沟通/抗压/学习，各0-100） */
  quizScores: QuizScores
  /** 创新案例 */
  innovation: string
  /** 目标岗位 */
  targetJob: string
  /** 期望行业 */
  targetIndustries: string[]
  /** 职业优先级 */
  priorities: string[]
}




//简历上传接口返回的数据类型定义
// 简化版：直接返回表单数据，用于自动填充
export interface UploadResponse extends Partial<CareerFormData> {
  // 直接继承 CareerFormData 的所有字段
  // 前端直接使用返回的数据填充表单
}

/** 简历解析后的表单字段数据 - 用于自动填充 */
export interface ParsedResumeFormData {
  /** 学历 */
  education?: string
  /** 学历其他说明 */
  educationOther?: string
  /** 专业 */
  major?: string[]
  /** 预计毕业日期 */
  /** 外语能力 */
  graduationDate?: string
  languages?: Language[]
  /** 证书列表 */
  certificates?: string[]
  /** 证书其他说明 */
  certificateOther?: string
  /** 技能列表 */
  skills?:  SkillTool[]
  /** 工具列表 */
  tools?:  SkillTool[]
  /** 代码能力 */
  codeAbility?: CodeAbility
  /** 代码仓库链接（兼容字段） */
  codeLinks?: string
  /** 项目经历 */
  projects?: Project[]
  /** 实习经历 */
  internships?: Internship[]
  /** 素质测评完成状态 */
  quizscores?: QuizScores
  /** 创新案例 */
  innovation?: string
  /** 目标岗位 */
  targetJob?: string
  /** 期望行业 */
  targetIndustries?: string[]
  /** 职业优先级排序 */
  priorities?: Priority[]
}

/** 必填字段配置 */
export interface RequiredFieldConfig {
  field: keyof CareerFormData
  label: string
  validate: (value: any) => boolean
}


