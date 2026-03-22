// ==================== 人岗匹配类型定义（后端接口格式） ====================

/** 通用响应结果 */
import type { Result } from "./type"

// ==================== 岗位画像子类型 ====================

/** 基础要求 */
export interface JobProfileBasicRequirements {
  degree: string
  major: string
  certificates: string
  internship_requirement: string
  experience_years: string
  special_requirements: string
}

/** 专业技能 */
export interface JobProfileProfessionalSkills {
  core_skills: string
  tool_capabilities: string
  domain_knowledge: string
  language_requirements: string
  project_requirements: string
}

/** 职业素养 */
export interface JobProfileProfessionalLiteracy {
  communication: string
  teamwork: string
  stress_management: string
  logic_thinking: string
  ethics: string
}

/** 发展潜力 */
export interface JobProfileDevelopmentPotential {
  learning_ability: string
  innovation: string
  leadership: string
  career_orientation: string
  adaptability: string
}

/** 岗位属性 */
export interface JobProfileJobAttributes {
  salary_competitiveness: string
  industry: string
  vertical_promotion_path: string
  prerequisite_roles: string
  lateral_transfer_directions: string
  social_demand: string
  industry_trend: string
}

/** 岗位画像（profiles） */
export interface JobProfiles {
  basic_requirements: JobProfileBasicRequirements
  professional_skills: JobProfileProfessionalSkills
  professional_literacy: JobProfileProfessionalLiteracy
  development_potential: JobProfileDevelopmentPotential
  job_attributes: JobProfileJobAttributes
}

/** 原始岗位数据（raw_data） */
export interface JobRawData {
  job_id: string
  job_name: string
  profiles: JobProfiles
}

// ==================== 深度分析子类型 ====================

/** 差距矩阵项 */
export interface GapMatrixItem {
  dimension: string
  required: string
  current: string
  gap_analysis: string
}

/** 深度分析结果（deep_analysis） */
export interface JobDeepAnalysis {
  can_apply: boolean
  score: number
  missing_key_skills: string[]
  gap_matrix: GapMatrixItem[]
  actionable_advice: string
  all_analysis: string
}

// ==================== 顶层类型 ====================

/** 单个岗位匹配结果（后端返回的数组元素） */
export interface JobMatchItem {
  job_id: string
  score: number
  raw_data: JobRawData
  deep_analysis: JobDeepAnalysis
}
