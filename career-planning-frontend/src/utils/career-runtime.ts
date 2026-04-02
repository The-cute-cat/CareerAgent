import type { CareerFormData } from '@/types/careerform_report'
import type { JobMatchItem } from '@/types/job-match'

export const CAREER_FORM_STORAGE_KEY = 'careerFormData'
export const JOB_MATCH_STORAGE_KEY = 'jobMatchResult'

const safeJsonParse = <T>(raw: string | null): T | null => {
  if (!raw) return null
  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

const canUseStorage = () => typeof window !== 'undefined' && typeof window.localStorage !== 'undefined'

export const loadCareerFormData = (): CareerFormData | null =>
  canUseStorage() ? safeJsonParse<CareerFormData>(localStorage.getItem(CAREER_FORM_STORAGE_KEY)) : null

export const saveCareerFormData = (formData: CareerFormData) => {
  if (!canUseStorage()) return
  localStorage.setItem(CAREER_FORM_STORAGE_KEY, JSON.stringify(formData))
}

export const clearCareerFormData = () => {
  if (!canUseStorage()) return
  localStorage.removeItem(CAREER_FORM_STORAGE_KEY)
}

export const loadJobMatchResult = (): JobMatchItem[] =>
  (canUseStorage() ? safeJsonParse<JobMatchItem[]>(localStorage.getItem(JOB_MATCH_STORAGE_KEY)) : null) || []

const splitText = (value: string | undefined) =>
  (value || '')
    .split(/[、,，/；;|\n]/)
    .map((item) => item.trim())
    .filter(Boolean)

const scoreFromCount = (count: number, base: number, step: number, max = 95) =>
  Math.min(base + count * step, max)

const getTargetJobName = (formData: CareerFormData | null, matches: JobMatchItem[]) =>
  formData?.targetJob?.trim() || matches[0]?.raw_data.job_name || '目标岗位'

const getTargetIndustry = (formData: CareerFormData | null, matches: JobMatchItem[]) =>
  formData?.targetIndustries?.join(' / ') || matches[0]?.raw_data.profiles.job_attributes.industry || '待补充'

export interface DynamicReportData {
  meta: { generateTime: string }
  userInfo: {
    name: string
    major: string
    grade: string
    targetPosition: string
    targetIndustry: string
    targetCity: string
  }
  matchingDimensions: Array<{
    label: string
    current: number
    target: number
    analysis: string
  }>
  recommendedJobs: Array<{
    name: string
    score: number
    reason: string
  }>
  goalSummary: {
    shortTerm: string
    midTerm: string
    longTerm: string
  }
  trendSummary: {
    outlook: string
    note: string
    highlights: string[]
  }
  pathwayMilestones: Array<{
    stage: string
    role: string
    focus: string
  }>
  actionPhases: Array<{
    title: string
    period: string
    tagType: 'success' | 'warning' | 'primary'
    summary: string
    learning: string[]
    practice: string[]
    metrics: string[]
  }>
  outcomes: string[]
  adjustments: string[]
  content: Record<'matching' | 'goals' | 'pathway' | 'action' | 'assessment', string>
}

export const buildDynamicReportData = (
  formData: CareerFormData | null,
  matches: JobMatchItem[]
): DynamicReportData => {
  const topMatches = [...matches]
    .sort((a, b) => (b.score || 0) - (a.score || 0))
    .slice(0, 3)

  const targetJob = getTargetJobName(formData, matches)
  const topJob = topMatches[0]
  const skillsCount = formData?.skills?.length || 0
  const toolsCount = formData?.tools?.length || 0
  const projectCount = formData?.projects?.length || 0
  const internshipCount = formData?.internships?.length || 0
  const certificateCount = formData?.certificates?.length || 0
  const hasInnovation = !!formData?.innovation?.trim()

  const matchingDimensions = [
    {
      label: '专业技能',
      current: scoreFromCount(skillsCount + toolsCount, 45, 7),
      target: 90,
      analysis: `当前已沉淀 ${skillsCount} 项技能、${toolsCount} 项工具能力，建议继续围绕 ${targetJob} 补齐岗位核心技能。`
    },
    {
      label: '通用素质',
      current: scoreFromCount(certificateCount + internshipCount, 58, 6),
      target: 88,
      analysis: internshipCount > 0 ? '已有一定职业素养与协作经历，可继续通过项目复盘强化表达能力。' : '建议增加实习、社团或项目协作案例，提升职业素养证明材料。'
    },
    {
      label: '项目实战',
      current: scoreFromCount(projectCount + internshipCount, 50, 8),
      target: 85,
      analysis: projectCount > 0 ? `目前已有 ${projectCount} 段项目经历，建议补充更贴近目标岗位的真实业务案例。` : '项目实战偏弱，建议尽快增加课程项目、竞赛或实习案例。'
    },
    {
      label: '发展潜力',
      current: Math.min(95, 60 + (hasInnovation ? 15 : 0) + certificateCount * 4),
      target: 90,
      analysis: hasInnovation ? '创新案例能够体现成长潜力，后续建议继续补充持续学习与复盘成果。' : '建议增加创新案例、学习成果或个人作品沉淀，增强发展潜力说明。'
    }
  ]

  const trendHighlights = splitText(topJob?.raw_data.profiles.job_attributes.industry_trend)
  const socialDemand = topJob?.raw_data.profiles.job_attributes.social_demand || '行业对复合能力与岗位适配度要求持续提升。'
  const verticalPath = splitText(topJob?.raw_data.profiles.job_attributes.vertical_promotion_path)
  const transferDirections = splitText(topJob?.raw_data.profiles.job_attributes.lateral_transfer_directions)

  const recommendedJobs = topMatches.map((item) => ({
    name: item.raw_data.job_name,
    score: Math.round((item.score || 0) * 100),
    reason: item.deep_analysis.actionable_advice || item.deep_analysis.all_analysis || '与当前画像具备一定契合度。'
  }))

  const milestones = [
    targetJob,
    verticalPath[0] || `资深${targetJob}`,
    verticalPath[1] || `${targetJob}负责人`,
    verticalPath[2] || `高级${targetJob}管理岗位`
  ].map((role, index) => ({
    stage: `阶段${index + 1}`,
    role,
    focus:
      index === 0
        ? '完成入岗能力补齐，建立岗位基础胜任力。'
        : index === 1
          ? '强化复杂项目、业务理解和跨团队协作能力。'
          : index === 2
            ? '逐步承担团队协同、方案统筹或方向负责职责。'
            : '向更高层级的专家或管理岗位持续发展。'
  }))

  return {
    meta: {
      generateTime: new Date().toISOString().slice(0, 10)
    },
    userInfo: {
      name: '同学',
      major: formData?.major?.join(' / ') || '待补充专业信息',
      grade: formData?.graduationDate ? `${formData.graduationDate} 届` : '待补充',
      targetPosition: targetJob,
      targetIndustry: getTargetIndustry(formData, matches),
      targetCity: '待补充'
    },
    matchingDimensions,
    recommendedJobs: recommendedJobs.length
      ? recommendedJobs
      : [{ name: targetJob, score: 60, reason: '当前暂无匹配结果，建议先完成人岗匹配分析。' }],
    goalSummary: {
      shortTerm: `优先进入 ${targetJob} 相关岗位，完成岗位基础能力补齐与首轮投递。`,
      midTerm: `在 2-3 年内成长为更高一级的 ${verticalPath[0] || targetJob}，形成稳定项目产出。`,
      longTerm: `结合岗位发展路径，向 ${verticalPath[1] || '更高阶专家或管理岗位'} 持续发展。`
    },
    trendSummary: {
      outlook: topJob ? '结合匹配岗位动态生成' : '待补充',
      note: socialDemand,
      highlights: trendHighlights.length ? trendHighlights : ['建议结合岗位画像补充行业趋势描述。']
    },
    pathwayMilestones: milestones,
    actionPhases: [
      {
        title: '短期成长计划',
        period: '0-6 个月',
        tagType: 'success',
        summary: `围绕 ${targetJob} 完成岗位基础能力补齐与求职准备。`,
        learning: [
          `补齐 ${splitText(topJob?.raw_data.profiles.professional_skills.core_skills).slice(0, 3).join('、') || '目标岗位核心技能'}`,
          '完善简历与作品材料',
          '针对目标岗位进行高频题与案例训练'
        ],
        practice: [
          projectCount > 0 ? '复盘并优化现有项目经历表述' : '新增至少 1 个可展示项目',
          internshipCount > 0 ? '沉淀实习成果与业务复盘' : '争取与目标方向相关的实习或项目机会',
          '进行阶段性岗位投递与反馈记录'
        ],
        metrics: ['每月复盘 1 次', '形成 1 份岗位能力差距清单', '完成 1 轮集中投递']
      },
      {
        title: '中期成长计划',
        period: '6-24 个月',
        tagType: 'warning',
        summary: '从入岗适应转向业务产出、复杂项目能力和可持续成长。',
        learning: ['建立系统化学习路径', '结合行业趋势补强新能力', '沉淀可复用的方法论与案例库'],
        practice: ['参与复杂项目', '持续做季度复盘', '根据岗位反馈动态修正发展方向'],
        metrics: ['季度评估 1 次', '至少沉淀 2 份项目复盘', '补齐 2 项关键差距能力']
      }
    ],
    outcomes: [
      `已结合现有表单数据生成 ${targetJob} 方向的职业分析结论`,
      `已读取 ${matches.length} 条岗位匹配结果并形成推荐排序`,
      '已生成动态职业路径与阶段行动计划'
    ],
    adjustments: [
      '建议每次更新职业画像后重新生成人岗匹配与报告',
      transferDirections.length ? `若后续转向，可重点关注：${transferDirections.slice(0, 3).join('、')}` : '可根据岗位匹配结果动态补充备选方向',
      '建议以季度为周期，根据项目、实习和投递反馈做动态调整'
    ],
    content: {
      matching: `<h3>人岗匹配分析</h3><p>当前报告基于已有职业画像表单与岗位匹配结果动态生成，目标岗位为 <strong>${targetJob}</strong>。系统结合专业技能、通用素质、项目实战与发展潜力四个维度进行了量化分析。</p>`,
      goals: `<h3>职业目标设定</h3><p>结合个人目标岗位、行业意向与匹配结果，建议将 <strong>${targetJob}</strong> 作为当前首要发展方向，并围绕市场需求持续补齐岗位要求。</p>`,
      pathway: `<h3>职业路径规划</h3><p>建议优先沿着 <strong>${milestones.map((item) => item.role).join(' → ')}</strong> 的路径发展，并根据岗位反馈动态修正成长方向。</p>`,
      action: '<h3>行动计划</h3><p>行动计划已根据当前表单中的技能、项目、实习和目标岗位动态生成，包含短期与中期两个阶段。</p>',
      assessment: '<h3>成果展示与复盘</h3><p>该报告内容已与当前职业画像和岗位匹配结果联动，后续每次更新数据后都可继续编辑、润色和导出。</p>'
    }
  }
}

export interface DynamicDevelopmentData {
  targetJobName: string
  targetIndustry: string
  topMatch: JobMatchItem | null
}

export const buildDynamicDevelopmentData = (
  formData: CareerFormData | null,
  matches: JobMatchItem[]
): DynamicDevelopmentData => ({
  targetJobName: getTargetJobName(formData, matches),
  targetIndustry: getTargetIndustry(formData, matches),
  topMatch: matches[0] || null
})
