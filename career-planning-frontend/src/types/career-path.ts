
// ==================== 后端返回的换岗路径类型定义 ====================

export interface Response {
  code: number
  data: Data
  msg: string
  state: boolean
  [property: string]: any
}

export interface Data {
  /**
   * 该起点岗位下的候选职业路径列表
   */
  paths: Path[]
  /**
   * 起点岗位ID
   */
  startJobid: string
  /**
   * 起点岗位名称
   */
  startJobName: string
  [property: string]: any
}

/**
 * 多条路径列表
 */
export interface Path {
  /**
   * Agent对整条路线的全局点评与风险提示
   */
  overallSummary: string
  /**
   * 前端渲染列表用的唯一Key
   */
  pathid: string
  /**
   * AI生成的路线响亮标题
   */
  pathTitle: string
  /**
   * 垂直晋升/横向转岗/跨界跃迁
   */
  pathType: string
  /**
   * 演化步骤明细（链式结构）
   */
  steps: Step[]
  /**
   * 总体演化阻力
   */
  totalRoutingCost: number
  /**
   * 需要跳跃的次数
   */
  totalSteps: number
  [property: string]: any
}

/**
 * 单条路径的演化步骤列表
 */
export interface Step {
  /**
   * 软素质契合度
   */
  cosLow: number
  /**
   * 起始岗位ID
   */
  fromJobid: string
  /**
   * 起始岗位名称
   */
  fromJobName: string
  /**
   * 硬技能重合度
   */
  jaccardHigh: number
  /**
   * 薪资增益指数
   */
  salaryGain: number
  /**
   * 为了完成这一跳，需要补齐的缺口
   */
  skillGaps: SkillGap[]
  /**
   * 步骤序号
   */
  stepIndex: number
  /**
   * 目标岗位ID
   */
  toJobid: string
  /**
   * 目标岗位名称
   */
  toJobName: string
  /**
   * AI解释：为什么推荐走这一步
   */
  transitionReason: string
  [property: string]: any
}



export interface SkillGap {
  actionableAdvice: string
  category: string
  competencyName: string
  originalContext: string
  targetScore: number
  [property: string]: any
}