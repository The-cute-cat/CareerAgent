export type PathType = 'lateral' | 'vertical'

export type LayoutType = 'force' | 'dagre'

export interface SkillGap {
  competency_name: string
  category: string
  target_score?: number
  original_context: string
  actionable_advice: string
}

export interface PathStep {
  step_index: number
  from_job_id: string
  from_job_name: string
  to_job_id: string
  to_job_name: string
  jaccard_high: number
  cos_low: number
  salary_gain: number
  transition_reason: string
  skill_gaps: SkillGap[]
}

export interface CareerPath {
  path_id: string
  path_type: PathType
  path_title: string
  total_steps: number
  total_routing_cost: number
  overall_summary: string
  steps: PathStep[]
}

export interface CareerMapData {
  start_job_id: string
  start_job_name: string
  paths: CareerPath[]
}

export interface ApiResponse {
  code: number
  state: boolean
  msg: string
  data: CareerMapData
}

export interface NodeDetailData {
  id: string
  label: string
  isStart: boolean
  pathType?: PathType
}

export interface X6NodeData extends NodeDetailData {}

export interface X6Node {
  id: string
  shape: string
  width: number
  height: number
  x?: number
  y?: number
  data: X6NodeData
}

export interface X6Edge {
  source: string
  target: string
  shape: string
  labels: Array<{
    attrs: { text: { text: string; fill: string; fontSize: number } }
  }>
  attrs: {
    line: {
      stroke: string
      strokeWidth: number
      strokeDasharray?: string
      targetMarker: { name: string; size: number }
    }
  }
  data: {
    path: CareerPath
    step: PathStep
  }
}
