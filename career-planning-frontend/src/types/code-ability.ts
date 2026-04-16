/** 代码能力评估请求参数 */
export interface CodeAbilityEvaluateParams {
  /** GitHub/Gitee 用户主页链接，格式如 https://github.com/username */
  url: string
  /** 是否启用 AI 深度分析，开启后会额外返回文字性的分析内容 */
  use_ai?: boolean
  /** 是否启用缓存，默认 true */
  cache_enabled?: boolean
}

/** 代码能力五维评分 */
export interface CodeAbilityDimensionScores {
  /** 项目规模 */
  project_scale: number
  /** 技术广度 */
  tech_breadth: number
  /** 活跃度 */
  activity: number
  /** 工程化 */
  engineering: number
  /** 社区影响力 */
  community: number
}

/** 权重配置 */
export interface CodeAbilityWeights {
  project_scale: number
  tech_breadth: number
  activity: number
  engineering: number
  community: number
}

/** 代码能力综合特征数据（量化评分） */
export interface CodeAbilityCompositeFeatures {
  /** 综合评分数值 */
  total_score: number
  /** 评级等级，如 "S（卓越）" / "A（优秀）" 等 */
  level: string
  /** 五维细分评分 */
  dimension_scores: CodeAbilityDimensionScores
  /** 权重配置 */
  weights: CodeAbilityWeights
  /** 评分上限 */
  max_score: number
}

/** 基础特征 */
export interface CodeAbilityBasicFeatures {
  platform: string
  username: string
  account_years: number
  total_public_repos: number
  followers: number
  following: number
  has_bio: boolean
  has_company: boolean
  has_location: boolean
}

/** 仓库详情 */
export interface CodeAbilityRepoInfo {
  repo_name: string
  full_name: string
  description: string | null
  language: string | null
  languages_url: string
  stargazers_count: number
  forks_count: number
  open_issues_count: number
  watchers_count: number
  size: number
  created_at: string
  updated_at: string
  pushed_at: string
  fork: boolean
  has_readme: boolean | null
  has_wiki: boolean
  has_pages: boolean
  topics: string[]
  license: string | null
}

/** 仓库特征 */
export interface CodeAbilityRepoFeatures {
  original_repo_count: number
  forked_repo_count: number
  total_stars: number
  total_forks: number
  avg_stars_per_repo: number
  max_star_repo: number
  repos_starred: number
  repos_popular: number
  small_repos: number
  medium_repos: number
  large_repos: number
  description_ratio: number
  license_ratio: number
  top_repos: CodeAbilityRepoInfo[]
}

/** 语言分布 */
export interface CodeAbilityLanguageDistribution {
  language: string
  count: number
  ratio: number
}

/** 语言特征 */
export interface CodeAbilityLanguageFeatures {
  total_language_count: number
  primary_language: string
  language_distribution: CodeAbilityLanguageDistribution[]
  language_categories: Record<string, number>
  language_diversity: string
  full_stack_potential: boolean
}

/** 活跃度特征 */
export interface CodeAbilityActivityFeatures {
  active_repos_3m: number
  active_repos_6m: number
  active_repos_1y: number
  active_ratio_3m: number
  activity_level: string
  recently_active: boolean
}

/** 质量特征 */
export interface CodeAbilityQualityFeatures {
  engineering_score: number
  engineering_level: string
  engineering_details: string[]
}

/** 代码能力量化特征（包装层） */
export interface CodeAbilityFeatures {
  /** 综合特征数据 */
  composite?: CodeAbilityCompositeFeatures
  /** 基础特征 */
  basic?: CodeAbilityBasicFeatures
  /** 仓库特征 */
  repo?: CodeAbilityRepoFeatures
  /** 语言特征 */
  language?: CodeAbilityLanguageFeatures
  /** 活跃度特征 */
  activity?: CodeAbilityActivityFeatures
  /** 质量特征 */
  quality?: CodeAbilityQualityFeatures
}

/** AI 分析 — 行动建议项 */
export interface CodeAbilityActionableAdviceItem {
  action: string
  expected_outcome: string
  priority: string
  reason: string
}

/** AI 分析 — 活跃度分析 */
export interface CodeAbilityActivityAnalysis {
  consistency: string
  recent_focus: string
  suggestion: string
}

/** AI 分析 — 职业匹配 */
export interface CodeAbilityCareerAlignment {
  growth_direction: string
  skill_gaps: string[]
  suitable_roles: string[]
}

/** AI 分析 — 整体评价 */
export interface CodeAbilityOverallAssessment {
  concerns: string[]
  highlights: string[]
  level: string
  score: number
  summary: string
}

/** AI 分析 — 技术栈分析 */
export interface CodeAbilityTechStackAnalysis {
  breadth_assessment: string
  depth_assessment: string
  primary_languages: string[]
  suggestion: string
  tech_domains: string[]
}

/** AI 分析 — 项目质量分析 */
export interface CodeAbilityProjectQualityAnalysis {
  engineering_habits: string
  project_scale: string
  quality_rating: string
  suggestion: string
}

/** AI 深度分析结果汇总 */
export interface CodeAbilityAiAnalysis {
  actionable_advice?: CodeAbilityActionableAdviceItem[]
  activity_analysis?: CodeAbilityActivityAnalysis
  career_alignment?: CodeAbilityCareerAlignment
  error?: string
  overall_assessment?: CodeAbilityOverallAssessment
  project_quality_analysis?: CodeAbilityProjectQualityAnalysis
  tech_stack_analysis?: CodeAbilityTechStackAnalysis
}

/** 代码能力评估接口的完整返回数据 */
export interface CodeAbilityEvaluateData {
  /** AI 深度分析内容，仅在开启深度分析时返回 */
  ai_analysis?: CodeAbilityAiAnalysis
  /** 综合评分（所有维度的加权总分） */
  composite_score: number
  /** 量化特征数据，始终返回 */
  features: CodeAbilityFeatures
  /** 评级等级标签，如 "S（卓越）" / "A（优秀）" */
  level: string
  /** 代码托管平台名称，如 "GitHub" / "Gitee" */
  platform: string
  /** 仓库所属用户名 */
  username: string
}
