/**
 * 通用响应结果
 * @template T 响应数据的类型
 */
export interface Result<T> {
  /**
   * 成功为 --200  失败为 401
   */
  code: number
  /**
   * 返回数据
   */
  data?: T | null
  /**
   * 提示消息
   */
  msg?: string | null
}

// ==================== 能力评估报告类型定义 ====================

/** 能力评估分数（雷达图数据） */
export interface AbilityScores {
  /** 专业能力分数 (0-100) */
  专业: number
  /** 创新能力分数 (0-100) */
  创新: number
  /** 学习能力分数 (0-100) */
  学习: number
  /** 抗压能力分数 (0-100) */
  抗压: number
  /** 沟通能力分数 (0-100) */
  沟通: number
  /** 实习能力分数 (0-100) */
  实习: number
}

/** 总体评价 */
export interface OverallAssessment {
  /** 综合等级：优秀/良好/待提升 */
  level: string
  /** 总体评价摘要 */
  summary: string
  /** 优势维度列表 */
  strengths: string[]
  /** 待提升维度列表 */
  weaknesses: string[]
}

/** 单维度分析 */
export interface DimensionAnalysis {
  /** 该维度分数 */
  score: number
  /** 分析评价 */
  analysis: string
  /** 改进建议列表 */
  suggestions: string[]
}

/** 职业规划报告 */
export interface CareerReport {
  /** 任务ID */
  taskId: string
  /** 能力评估分数（雷达图数据） */
  abilityScores: AbilityScores
  /** 总体评价 */
  overallAssessment: OverallAssessment
  /** 各维度详细分析 */
  dimensionAnalysis: {
    专业: DimensionAnalysis
    创新: DimensionAnalysis
    学习: DimensionAnalysis
    抗压: DimensionAnalysis
    沟通: DimensionAnalysis
    实习: DimensionAnalysis
  }
  /** 报告生成时间 */
  generatedAt: string
}

/** 报告状态查询响应 */
export interface CareerReportStatus {
  /** 任务ID */
  taskId: string
  /** 报告生成状态 */
  status: 'pending' | 'processing' | 'completed' | 'failed'
  /** 进度百分比 (0-100) */
  progress?: number
  /** 预计剩余时间（秒） */
  estimatedTimeRemaining?: number
  /** 失败原因（当 status 为 failed 时） */
  errorMessage?: string
}

/**
 * LoginVO
 */
export interface LoginVO {
  /**
   * Token 信息
   */
  accessToken?: string | null
  /**
   * 刷新令牌
   */
  refreshToken?: string | null
}

export interface UserInfo {
  id: number
  nickname: string
  username: string
  avatar: string
  email: string
  info: string
  phone: string
  createTime: string
  updateTime: string
  accessToken: string
  refreshToken: string
}

//登录接口需要携带的参数类型定义
export interface loginForm {
  username: string
  password: string
  rememberMe: boolean
}

interface dataType {
  token: string
}

//服务器返回的用户信息类型定义
interface user {
  checkUser: UserInfo
}

export interface userInfoResponseData {
  code: number
  data: user
}

//简历上传接口返回的数据类型定义
export interface UploadResponse {
  code: number
  message: string
  data: {
    file_id: string // 文件存储 ID
    parse_status: 'pending' | 'processing' | 'completed' | 'failed'
    task_id?: string // 异步解析任务 ID (若耗时较长)

    //  赛题核心：AI 解析出的画像数据
    profile?: {
      name: string
      skills: string[] // 技能标签
      experience: string[] // 经历摘要
      education: string // 学历
      confidence_score: number // 解析置信度 (0-1)
    }

    // 能力评估分数（与表单提交返回的 abilityScores 格式一致）
    abilityScores?: AbilityScores

    // 完整报告（与表单提交流程返回的 CareerReport 格式一致）
    report?: CareerReport
  }
}

// ==================== CareerForm 表单类型定义 ====================

/** 学历类型 */
export type EducationType = '高中' | '专科' | '本科' | '硕士' | '博士' | '其他'

/** 语言能力项 */
export interface Language {
  /** 语种：英语/日语/其他 */
  type: string
  /** 水平：四级/六级/托福/雅思/其他 */
  level: string
  /** 其他说明（当选择"其他"时填写） */
  other: string
}

/** 技能项 */
export interface Skill {
  /** 技能名称，如 Java、Python */
  name: string
  /** 熟练度，范围 0-100 */
  credibility: number
}

/** 工具熟练度级别 */
export type ToolProficiency = '了解' | '熟练' | '精通'

/** 工具项 */
export interface Tool {
  /** 工具名称，如 Git、Docker */
  name: string
  /** 熟练程度 */
  proficiency: ToolProficiency
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
export interface QuizScores {
  /** 沟通能力测评 */
  communication: boolean
  /** 抗压能力测评 */
  stress: boolean
  /** 学习能力测评 */
  learning: boolean
}

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
  skills: Skill[]
  /** 工具掌握列表 */
  tools: Tool[]
  /** 代码能力 */
  codeAbility: CodeAbility
  /** 项目经历列表 */
  projects: Project[]
  /** 实习经历列表 */
  internships: Internship[]
  /** 素质测评完成状态 */
  scores: QuizScores
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
  skills: Skill[]
  /** 工具列表 */
  tools: Tool[]
  /** 代码仓库链接 */
  codeLinks?: string
  /** 项目经历 */
  projects: Project[]
  /** 实习经历 */
  internships: Internship[]
  /** 素质测评结果 */
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

/** 提交职业表单的响应结果 */
export interface CareerFormSubmitResult {
  /** 任务ID */
  taskId: string
  /** 规划报告生成状态 */
  status: 'pending' | 'processing' | 'completed' | 'failed'
  /** 预估完成时间（秒） */
  estimatedTime?: number
}

/** 报告状态查询响应 */
export interface CareerReportStatus {
  /** 任务ID */
  taskId: string
  /** 报告生成状态 */
  status: 'pending' | 'processing' | 'completed' | 'failed'
  /** 进度百分比 (0-100) */
  progress?: number
  /** 预计剩余时间（秒） */
  estimatedTimeRemaining?: number
  /** 失败原因（当 status 为 failed 时） */
  errorMessage?: string
}
