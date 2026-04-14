/** 代码能力评估请求参数 */
export interface CodeAbilityEvaluateParams {
  /** GitHub/Gitee 代码仓库链接列表，格式如 https://github.com/user/repo */
  urls: string[]
  /** 是否启用 AI 深度分析，开启后会额外返回文字性的分析内容 */
  use_ai?: boolean
}

/** 代码能力五维评分 */
export interface CodeAbilityDimensionScores {
  /** 项目规模 — 衡量用户参与项目的规模大小（仓库体积、代码行数、文件数量等） */
  project_scale: number
  /** 技术广度 — 衡量用户使用技术的多样性（编程语言、框架、工具种类等） */
  tech_breadth: number
  /** 活跃度 — 衡量用户的提交频率、贡献频率及最近活跃时间 */
  activity: number
  /** 工程化 — 衡量工程实践水平（CI/CD、测试覆盖、文档完善度、项目结构规范性等） */
  engineering: number
  /** 社区影响力 — 衡量用户的开源影响力（star、fork、被引用次数、开源项目参与度等） */
  influence: number
}

/** 代码能力综合特征数据（量化评分） */
export interface CodeAbilityCompositeFeatures {
  /** 综合评分数值 */
  total_score: number
  /** 评级等级，如 "A" / "B" / "C" 等 */
  rank: string
  /** 百分位排名，如 85 表示超过 85% 的用户 */
  percentile: number
  /** 五维细分评分 */
  dimensions: CodeAbilityDimensionScores
}

/** 代码能力量化特征（包装层） */
export interface CodeAbilityFeatures {
  /** 综合特征数据 */
  composite?: CodeAbilityCompositeFeatures
}

/** AI 分析 — 整体评价 */
export interface CodeAbilityOverallAssessment {
  /** AI 对用户代码能力的整体文字总结 */
  summary: string
  /** 用户的优势列表，以标签形式展示 */
  strengths: string[]
  /** 用户的不足列表，以标签形式展示 */
  weaknesses: string[]
}

/** AI 分析 — 技术栈分析 */
export interface CodeAbilityTechStackAnalysis {
  /** 主技术栈：用户最常用、最擅长的技术 */
  primary_stack: string[]
  /** 辅助技术栈：用户了解或使用过的次要技术 */
  secondary_stack: string[]
  /** 技术栈成熟度的文字描述 */
  stack_maturity: string
  /** 对用户技术栈的改进建议 */
  stack_recommendations: string[]
}

/** AI 分析 — 项目质量分析 */
export interface CodeAbilityProjectQualityAnalysis {
  /** 代码质量的文字评价 */
  code_quality: string
  /** 架构设计水平的文字评价 */
  architecture: string
  /** 用户做得好的最佳实践列表 */
  best_practices: string[]
  /** 需要改进的待改进项列表 */
  improvement_areas: string[]
}

/** AI 分析 — 分阶段行动建议 */
export interface CodeAbilityActionableAdvice {
  /** 短期建议：近期可以立即执行的行动 */
  short_term: string[]
  /** 中期建议：需要一定时间积累的提升方向 */
  mid_term: string[]
  /** 长期建议：职业发展层面的长远规划 */
  long_term: string[]
}

/** AI 深度分析结果汇总（仅在 use_ai 为 true 时返回） */
export interface CodeAbilityAiAnalysis {
  /** 整体评价 */
  overall_assessment?: CodeAbilityOverallAssessment | null
  /** 技术栈分析 */
  tech_stack_analysis?: CodeAbilityTechStackAnalysis | null
  /** 项目质量分析 */
  project_quality_analysis?: CodeAbilityProjectQualityAnalysis | null
  /** 分阶段行动建议 */
  actionable_advice?: CodeAbilityActionableAdvice | null
}

/** 代码能力评估接口的完整返回数据 */
export interface CodeAbilityEvaluateData {
  /** 代码托管平台名称，如 "GitHub" / "Gitee" */
  platform: string
  /** 仓库所属用户或组织名 */
  username: string
  /** 综合评分（所有维度的加权总分） */
  composite_score: number
  /** 评级等级标签，如 "A" / "B" / "C" */
  level: string
  /** 量化特征数据（五维评分），始终返回 */
  features?: CodeAbilityFeatures | null
  /** AI 深度分析内容，仅在开启深度分析时返回 */
  ai_analysis?: CodeAbilityAiAnalysis | null
}
