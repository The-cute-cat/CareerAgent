import type { GrowthPlanWordExportData } from '@/utils/resume-export'

export type ResourceItem = {
  id: string
  title?: string
  name?: string
  author?: string
  publisher?: string
  isbn?: string
  url?: string
  duration?: string
  content?: string
  description?: string
  stars?: number
  language?: string
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
  salary?: string
  city?: string
  degree?: string
  days_per_week: number
  months: number
  job_type?: string
  tech_stack?: string
  url?: string
  content?: string
  reason?: string
}

export type GrowthPlanData = GrowthPlanWordExportData & {
  mid_term_plan: GrowthPlanWordExportData['mid_term_plan'] & {
    recommended_internships: InternshipItem[]
  }
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
