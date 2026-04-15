export type CareerGraphMode = 'promotion' | 'transfer'

export type CareerRelationType = 'promotion' | 'transfer'

export interface CareerNode {
  id: string
  name: string
  level: string
  type: string
  category: string
  salaryRange: string
  experience: string
  education: string
  description: string
  skills: string[]
  tags: string[]
  recommendedLearning: string[]
  x: number
  y: number
  isCurrent?: boolean
  highlightColor?: string
}

export interface CareerEdge {
  id: string
  source: string
  target: string
  relationType: CareerRelationType
  difficulty: '低' | '中' | '中高' | '高'
  requiredSkills: string[]
  duration: string
  description: string
  suggestedLearning: string[]
}

export interface CareerGraphData {
  mode: CareerGraphMode
  title: string
  subtitle: string
  currentNodeId: string
  nodes: CareerNode[]
  edges: CareerEdge[]
}

export type DetailState =
  | { type: 'empty' }
  | { type: 'node'; data: CareerNode }
  | { type: 'edge'; data: CareerEdge; sourceNode?: CareerNode; targetNode?: CareerNode }
