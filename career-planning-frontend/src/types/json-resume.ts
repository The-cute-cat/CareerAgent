/**
 * JSON Resume 标准对象类型定义。
 * 这里保留了 JSON Resume 常见核心字段，并补充了当前项目生成简历所需的扩展入参类型。
 */

import type { CareerFormData } from '@/types/careerform_report'

/** JSON Resume 元信息。 */
export interface JsonResumeMeta {
  /** JSON Resume 版本号。 */
  version?: string
  /** 最后修改时间，使用 ISO 8601 格式。 */
  lastModified?: string
  /** 简历语言。 */
  language?: string
}

/** 地理位置。 */
export interface JsonResumeLocation {
  /** 详细地址。 */
  address?: string
  /** 邮编。 */
  postalCode?: string
  /** 城市。 */
  city?: string
  /** 省/州。 */
  region?: string
  /** 国家/地区代码或名称。 */
  countryCode?: string
}

/** 社交链接。 */
export interface JsonResumeProfile {
  /** 平台名称，如 GitHub / LinkedIn。 */
  network: string
  /** 主页地址。 */
  url?: string
  /** 用户名。 */
  username?: string
}

/** 基础信息。 */
export interface JsonResumeBasics {
  /** 姓名。 */
  name: string
  /** 职位标签。 */
  label?: string
  /** 头像地址。 */
  image?: string
  /** 邮箱。 */
  email?: string
  /** 电话。 */
  phone?: string
  /** 个人网站。 */
  url?: string
  /** 个人简介。 */
  summary?: string
  /** 所在地。 */
  location?: JsonResumeLocation
  /** 社交资料。 */
  profiles?: JsonResumeProfile[]
}

/** 工作经历。 */
export interface JsonResumeWork {
  /** 公司名称。 */
  name: string
  /** 职位名称。 */
  position?: string
  /** 公司网站。 */
  url?: string
  /** 入职日期，格式 YYYY-MM-DD。 */
  startDate?: string
  /** 离职日期，格式 YYYY-MM-DD；留空表示至今。 */
  endDate?: string
  /** 工作内容概述。 */
  summary?: string
  /** 成果亮点。 */
  highlights?: string[]
  /** 所在城市。 */
  location?: string
}

/** 教育经历。 */
export interface JsonResumeEducation {
  /** 学校名称。 */
  institution: string
  /** 学校主页。 */
  url?: string
  /** 专业方向。 */
  area?: string
  /** 学历。 */
  studyType?: string
  /** 入学日期。 */
  startDate?: string
  /** 毕业日期。 */
  endDate?: string
  /** 绩点。 */
  score?: string
  /** 课程列表。 */
  courses?: string[]
}

/** 技能。 */
export interface JsonResumeSkill {
  /** 技能分类名称。 */
  name: string
  /** 熟练度标签。 */
  level?: string
  /** 关键词列表。 */
  keywords: string[]
}

/** 项目经历。 */
export interface JsonResumeProject {
  /** 项目名称。 */
  name: string
  /** 项目描述。 */
  description?: string
  /** 项目开始时间。 */
  startDate?: string
  /** 项目结束时间。 */
  endDate?: string
  /** 项目主页。 */
  url?: string
  /** 项目亮点。 */
  highlights?: string[]
  /** 角色。 */
  roles?: string[]
  /** 使用技术。 */
  keywords?: string[]
  /** 项目类型。 */
  entity?: string
}

/** 语言能力。 */
export interface JsonResumeLanguage {
  /** 语言名称。 */
  language: string
  /** 语言级别。 */
  fluency?: string
}

/** 证书。 */
export interface JsonResumeCertificate {
  /** 证书名称。 */
  name: string
  /** 发证机构。 */
  issuer?: string
  /** 获取日期。 */
  date?: string
  /** 证书链接。 */
  url?: string
}

/** 兴趣爱好。 */
export interface JsonResumeInterest {
  /** 兴趣名称。 */
  name: string
  /** 关键词。 */
  keywords?: string[]
}

/** JSON Resume 根对象。 */
export interface JsonResume {
  /** 元信息。 */
  meta?: JsonResumeMeta
  /** 基础信息。 */
  basics: JsonResumeBasics
  /** 工作经历。 */
  work?: JsonResumeWork[]
  /** 教育经历。 */
  education?: JsonResumeEducation[]
  /** 技能。 */
  skills?: JsonResumeSkill[]
  /** 项目经历。 */
  projects?: JsonResumeProject[]
  /** 语言能力。 */
  languages?: JsonResumeLanguage[]
  /** 证书。 */
  certificates?: JsonResumeCertificate[]
  /** 兴趣爱好。 */
  interests?: JsonResumeInterest[]
}

/** 额外基础资料。 */
export interface ResumeBasicsExtras {
  /** 姓名。 */
  name: string
  /** 职位标签。 */
  label?: string
  /** 邮箱。 */
  email?: string
  /** 电话。 */
  phone?: string
  /** 个人主页。 */
  url?: string
  /** 头像地址。 */
  image?: string
  /** 个人简介。 */
  summary?: string
  /** 城市。 */
  city?: string
  /** 省/州。 */
  region?: string
  /** 详细地址。 */
  address?: string
  /** 邮编。 */
  postalCode?: string
  /** 国家/地区。 */
  countryCode?: string
  /** 社交信息。 */
  profiles?: JsonResumeProfile[]
}

/** 扩展工作经历。 */
export interface ResumeWorkExtra {
  /** 公司名称。 */
  name: string
  /** 职位名称。 */
  position?: string
  /** 公司主页。 */
  url?: string
  /** 开始日期。 */
  startDate?: string | Date
  /** 结束日期。 */
  endDate?: string | Date | null
  /** 工作概述。 */
  summary?: string
  /** 工作亮点。 */
  highlights?: string[]
  /** 工作地点。 */
  location?: string
}

/** 扩展教育经历。 */
export interface ResumeEducationExtra {
  /** 学校名称。 */
  institution: string
  /** 学校主页。 */
  url?: string
  /** 专业。 */
  area?: string
  /** 学历。 */
  studyType?: string
  /** 开始日期。 */
  startDate?: string | Date
  /** 结束日期。 */
  endDate?: string | Date
  /** 绩点。 */
  score?: string
  /** 课程列表。 */
  courses?: string[]
}

/** 扩展项目经历。 */
export interface ResumeProjectExtra {
  /** 项目名称。 */
  name: string
  /** 描述。 */
  description?: string
  /** 开始日期。 */
  startDate?: string | Date
  /** 结束日期。 */
  endDate?: string | Date | null
  /** 项目地址。 */
  url?: string
  /** 亮点。 */
  highlights?: string[]
  /** 角色。 */
  roles?: string[]
  /** 技术栈。 */
  keywords?: string[]
  /** 项目类型。 */
  entity?: string
}

/** 扩展技能配置。 */
export interface ResumeSkillExtra {
  /** 技能组名。 */
  name: string
  /** 熟练度描述。 */
  level?: string
  /** 技能标签。 */
  keywords: string[]
}

/** 扩展语言配置。 */
export interface ResumeLanguageExtra {
  /** 语言名称。 */
  language: string
  /** 熟练度。 */
  fluency?: string
}

/** 扩展证书配置。 */
export interface ResumeCertificateExtra {
  /** 证书名称。 */
  name: string
  /** 发证机构。 */
  issuer?: string
  /** 获取日期。 */
  date?: string | Date
  /** 链接。 */
  url?: string
}

/** 扩展兴趣配置。 */
export interface ResumeInterestExtra {
  /** 兴趣名称。 */
  name: string
  /** 兴趣关键词。 */
  keywords?: string[]
}

/** 生成 JSON Resume 时的额外资料。 */
export interface ResumeProfileExtras {
  /** 基础资料。 */
  basics: ResumeBasicsExtras
  /** 扩展工作经历。 */
  workHistory?: ResumeWorkExtra[]
  /** 扩展教育经历。 */
  educationHistory?: ResumeEducationExtra[]
  /** 扩展项目经历。 */
  projectHistory?: ResumeProjectExtra[]
  /** 额外技能分组。 */
  customSkillGroups?: ResumeSkillExtra[]
  /** 额外语言。 */
  languages?: ResumeLanguageExtra[]
  /** 额外证书。 */
  certificates?: ResumeCertificateExtra[]
  /** 兴趣。 */
  interests?: ResumeInterestExtra[]
  /** 是否将 CareerFormData 中的项目与实习自动映射。 */
  includeCareerFormSections?: boolean
  /** 是否保留空数组字段。 */
  keepEmptyArrays?: boolean
}

/** 字段来源。 */
export type ResumeFieldSource = 'careerForm' | 'profileExtras' | 'derived'

/** 完整性检查项。 */
export interface ResumeCompletenessItem {
  /** 字段路径。 */
  field: string
  /** 中文名称。 */
  label: string
  /** 是否必填。 */
  required: boolean
  /** 是否已填写。 */
  completed: boolean
  /** 数据来源。 */
  source: ResumeFieldSource
  /** 缺失原因。 */
  message?: string
}

/** 完整性检查报告。 */
export interface ResumeCompletenessReport {
  /** 完整度分数，范围 0-100。 */
  score: number
  /** 所有检查项。 */
  items: ResumeCompletenessItem[]
  /** 缺失必填项。 */
  missingRequiredFields: ResumeCompletenessItem[]
}

/** JSON Schema 校验错误。 */
export interface JsonResumeValidationError {
  /** 出错字段路径。 */
  instancePath: string
  /** 错误说明。 */
  message: string
  /** Schema 关键字。 */
  keyword: string
}

/** JSON Resume 生成结果。 */
export interface JsonResumeGenerationResult {
  /** 最终简历对象。 */
  resume: JsonResume
  /** 是否通过 JSON Schema 校验。 */
  valid: boolean
  /** 校验错误。 */
  errors: JsonResumeValidationError[]
  /** 完整度报告。 */
  completeness: ResumeCompletenessReport
}

/** 生成 JSON Resume 的入参。 */
export interface GenerateJsonResumeInput {
  /** 现有职业画像表单数据。 */
  careerFormData: CareerFormData
  /** 额外个人资料字段。 */
  profileExtras: ResumeProfileExtras
}
