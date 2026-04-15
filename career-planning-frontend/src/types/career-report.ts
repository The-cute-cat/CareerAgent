import type { GrowthPlanWordExportData } from '@/utils/resume-export'

export type ResourceItem = {
  id: string
  title?: string
  name?: string
  author?: string
  category?: string
  category_name?: string
  categoryName?: string
  publisher?: string
  isbn?: string
  url?: string
  duration?: string
  content?: string
  description?: string
  difficulty?: string
  cover_image?: string
  coverImage?: string
  favorite_count?: string
  favoriteCount?: string
  like_count?: string
  likeCount?: string
  play_count?: string
  playCount?: string
  publish_date?: string
  publishDate?: string
  stars?: number
  language?: string
  tags?: string
  tech_tags?: string
  techTags?: string
  use_cases?: string
  useCases?: string
  reason?: string
}

export type PlanTask = {
  task_name: string
  description: string
  priority: '高' | '中' | '低' | string
  estimated_time: string
  skill_target: string
  success_criteria: string
  resources: ResourceItem[]
}

export interface Milestone {
  milestone_name: string
  target_date: string
  key_results: string[]
  tasks: PlanTask[]
}

export type InternshipItem = {
  id: string
  job_title: string
  company_name: string
  company_industry?: string
  companyIndustry?: string
  company_scale?: string
  companyScale?: string
  salary: string
  city: string
  degree: string
  days_per_week: number
  months: number
  job_type: string
  tech_stack?: string
  url?: string
  content?: string
  reason: string
}

export type GrowthPlanData = GrowthPlanWordExportData & {
  target_position_profile_summary?: string
  mid_term_plan: GrowthPlanWordExportData['mid_term_plan'] & {
    recommended_internships: InternshipItem[]
  }
}

type RawTask = Partial<PlanTask> & {
  taskName?: string
  estimatedTime?: string
  skillTarget?: string
  successCriteria?: string
}

type RawMilestone = Partial<Milestone> & {
  milestoneName?: string
  targetDate?: string
  keyResults?: string[]
  tasks?: RawTask[]
}

type RawShortTermPlan = Partial<GrowthPlanData['short_term_plan']> & {
  focusAreas?: string[]
  quickwins?: string[]
  milestones?: RawMilestone[]
}

type RawMidTermPlan = Partial<GrowthPlanData['mid_term_plan']> & {
  skillRoadmap?: string[]
  careerProgression?: string
  recommendedInternships?: InternshipItem[]
  milestones?: RawMilestone[]
}

type GrowthPlanRawData = Partial<GrowthPlanData> & {
  studentSummary?: string
  targetPosition?: string
  targetPositionProfileSummary?: string
  currentGap?: string
  shortTermPlan?: RawShortTermPlan
  midTermPlan?: RawMidTermPlan
  actionChecklist?: string[]
}

export type EditableSectionKey =
  | 'student_summary'
  | 'current_gap'
  | 'short_goal'
  | 'mid_goal'
  | 'career_progression'

export const editableSectionOptions: Array<{ key: EditableSectionKey; label: string }> = [
  { key: 'student_summary', label: '学生画像摘要' },
  { key: 'current_gap', label: '能力差距分析' },
  { key: 'short_goal', label: '短期目标' },
  { key: 'mid_goal', label: '中期目标' },
  { key: 'career_progression', label: '职业发展预期' },
]

export const createEmptyCareerReport = (): GrowthPlanData => ({
  student_summary: '',
  target_position: '待生成职业方向',
  target_position_profile_summary: '',
  current_gap: '',
  short_term_plan: {
    duration: '1-3个月',
    goal: '',
    focus_areas: [],
    milestones: [],
    quick_wins: [],
  },
  mid_term_plan: {
    duration: '3-12个月',
    goal: '',
    skill_roadmap: [],
    milestones: [],
    career_progression: '',
    recommended_internships: [],
  },
  action_checklist: [],
  tips: [],
})

function normalizeString(value: unknown): string {
  return typeof value === 'string' ? value.trim() : ''
}

function normalizeStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value
    .map(item => (typeof item === 'string' ? item.trim() : ''))
    .filter(Boolean)
}

function normalizeResourceItem(resource: unknown, index: number): ResourceItem {
  const item = (resource || {}) as ResourceItem
  return {
    ...item,
    id: normalizeString(item.id) || `resource-${index}`,
    title: normalizeString(item.title),
    name: normalizeString(item.name),
    author: normalizeString(item.author),
    category: normalizeString(item.category),
    category_name: normalizeString(item.category_name || item.categoryName),
    categoryName: normalizeString(item.categoryName || item.category_name),
    publisher: normalizeString(item.publisher),
    isbn: normalizeString(item.isbn),
    url: normalizeString(item.url),
    duration: normalizeString(item.duration),
    content: normalizeString(item.content),
    description: normalizeString(item.description),
    difficulty: normalizeString(item.difficulty),
    cover_image: normalizeString(item.cover_image || item.coverImage),
    coverImage: normalizeString(item.coverImage || item.cover_image),
    favorite_count: normalizeString(item.favorite_count || item.favoriteCount),
    favoriteCount: normalizeString(item.favoriteCount || item.favorite_count),
    like_count: normalizeString(item.like_count || item.likeCount),
    likeCount: normalizeString(item.likeCount || item.like_count),
    play_count: normalizeString(item.play_count || item.playCount),
    playCount: normalizeString(item.playCount || item.play_count),
    publish_date: normalizeString(item.publish_date || item.publishDate),
    publishDate: normalizeString(item.publishDate || item.publish_date),
    stars: typeof item.stars === 'number' ? item.stars : undefined,
    language: normalizeString(item.language),
    tags: normalizeString(item.tags),
    tech_tags: normalizeString(item.tech_tags || item.techTags),
    techTags: normalizeString(item.techTags || item.tech_tags),
    use_cases: normalizeString(item.use_cases || item.useCases),
    useCases: normalizeString(item.useCases || item.use_cases),
    reason: normalizeString(item.reason),
  }
}

function normalizeTask(task: unknown): PlanTask {
  const item = (task || {}) as RawTask
  return {
    task_name: normalizeString(item.task_name || item.taskName),
    description: normalizeString(item.description),
    priority: normalizeString(item.priority) || '中',
    estimated_time: normalizeString(item.estimated_time || item.estimatedTime),
    skill_target: normalizeString(item.skill_target || item.skillTarget),
    success_criteria: normalizeString(item.success_criteria || item.successCriteria),
    resources: Array.isArray(item.resources) ? item.resources.map(normalizeResourceItem) : [],
  }
}

function normalizeMilestone(milestone: unknown): Milestone {
  const item = (milestone || {}) as RawMilestone
  return {
    milestone_name: normalizeString(item.milestone_name || item.milestoneName),
    target_date: normalizeString(item.target_date || item.targetDate),
    key_results: normalizeStringList(item.key_results || item.keyResults),
    tasks: Array.isArray(item.tasks) ? item.tasks.map(normalizeTask) : [],
  }
}

function normalizeInternship(item: unknown, index: number): InternshipItem {
  const internship = (item || {}) as InternshipItem
  return {
    ...internship,
    id: normalizeString(internship.id) || `internship-${index}`,
    job_title: normalizeString(internship.job_title),
    company_name: normalizeString(internship.company_name),
    company_industry: normalizeString(internship.company_industry || internship.companyIndustry),
    companyIndustry: normalizeString(internship.companyIndustry || internship.company_industry),
    company_scale: normalizeString(internship.company_scale || internship.companyScale),
    companyScale: normalizeString(internship.companyScale || internship.company_scale),
    salary: normalizeString(internship.salary),
    city: normalizeString(internship.city),
    degree: normalizeString(internship.degree),
    days_per_week: Number(internship.days_per_week) > 0 ? Number(internship.days_per_week) : 0,
    months: Number(internship.months) > 0 ? Number(internship.months) : 0,
    job_type: normalizeString(internship.job_type),
    tech_stack: normalizeString(internship.tech_stack),
    url: normalizeString(internship.url),
    content: normalizeString(internship.content),
    reason: normalizeString(internship.reason),
  }
}

export function normalizeGrowthPlanData(data?: GrowthPlanRawData | null): GrowthPlanData {
  const fallback = createEmptyCareerReport()
  const source = (data || {}) as GrowthPlanRawData
  const shortTermPlan = (source.short_term_plan || source.shortTermPlan || {}) as RawShortTermPlan
  const midTermPlan = (source.mid_term_plan || source.midTermPlan || {}) as RawMidTermPlan
  const recommendedInternships = midTermPlan.recommended_internships || midTermPlan.recommendedInternships || []

  return {
    ...fallback,
    ...source,
    student_summary: normalizeString(source.student_summary || source.studentSummary),
    target_position: normalizeString(source.target_position || source.targetPosition) || fallback.target_position,
    target_position_profile_summary: normalizeString(
      source.target_position_profile_summary || source.targetPositionProfileSummary,
    ),
    current_gap: normalizeString(source.current_gap || source.currentGap),
    short_term_plan: {
      ...fallback.short_term_plan,
      ...shortTermPlan,
      duration: normalizeString(shortTermPlan.duration) || fallback.short_term_plan.duration,
      goal: normalizeString(shortTermPlan.goal),
      focus_areas: normalizeStringList(shortTermPlan.focus_areas || shortTermPlan.focusAreas),
      milestones: Array.isArray(shortTermPlan.milestones) ? shortTermPlan.milestones.map(normalizeMilestone) : [],
      quick_wins: normalizeStringList(shortTermPlan.quick_wins || shortTermPlan.quickwins),
    },
    mid_term_plan: {
      ...fallback.mid_term_plan,
      ...midTermPlan,
      duration: normalizeString(midTermPlan.duration) || fallback.mid_term_plan.duration,
      goal: normalizeString(midTermPlan.goal),
      skill_roadmap: normalizeStringList(midTermPlan.skill_roadmap || midTermPlan.skillRoadmap),
      milestones: Array.isArray(midTermPlan.milestones) ? midTermPlan.milestones.map(normalizeMilestone) : [],
      career_progression: normalizeString(midTermPlan.career_progression || midTermPlan.careerProgression),
      recommended_internships: Array.isArray(recommendedInternships)
        ? recommendedInternships.map(normalizeInternship)
        : [],
    },
    action_checklist: normalizeStringList(source.action_checklist || source.actionChecklist),
    tips: normalizeStringList(source.tips),
  }
}
