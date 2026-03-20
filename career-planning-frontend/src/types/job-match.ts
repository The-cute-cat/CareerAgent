// ==================== 人岗匹配类型定义 ====================

/** 通用响应结果 */
import type {  Result } from "./type"

/** 岗位数据 */
export interface JobPosition {
  id: string
  title: string
  company: string
  industry: string
  location: string
  salaryMin: number
  salaryMax: number
  experience: string
  education: string
  tags: string[]
  description: string
  /** AI提取的核心技能 */
  coreSkills: string[]
  /** 证书要求 */
  requiredCertificates: string[]
  /** 素养要求 */
  requiredQualities: string[]
  /** 匹配分数 */
  matchScore?: number
  /** AI置信度 */
  confidence: number
}

/** 匹配维度分数 */
export interface MatchDimension {
  name: string
  score: number
  maxScore: number
  weight: number
  description: string
}

/** 差距分析项 */
export interface GapItem {
  type: 'skill' | 'certificate' | 'quality' | 'experience'
  name: string
  required: string
  current: string
  gap: 'high' | 'medium' | 'low'
  suggestion: string
}

/** 人岗匹配分析结果 */
export interface JobMatchResult {
  /** 任务ID */
  taskId: string
  /** 匹配总分 (0-100) */
  totalScore: number
  /** 匹配维度分数 */
  dimensions: MatchDimension[]
  /** 差距分析 */
  gaps: GapItem[]
  /** AI解释说明 */
  aiExplanation: string
  /** AI置信度 */
  confidence: number
  /** 推荐岗位列表 */
  recommendedJobs: JobPosition[]
  /** 生成时间 */
  generatedAt: string
}