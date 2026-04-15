import request from '@/utils/request'
import type { GrowthPlanData } from '@/types/career-report'
import type { Result } from '@/types/type'

export interface GetReportPlanParams {
  jobId: number
  cacheEnabled?: boolean
}

export interface ReportIntegrityCheckRequest {
  report_content: string
  job_title?: string
}

export interface ReportIntegrityCheckItem {
  dimension: string
  is_present: boolean
  description: string
  suggestion?: string | null
}

export interface ReportIntegrityCheckResponse {
  is_complete: boolean
  check_results: ReportIntegrityCheckItem[]
  missing_items: string[]
  overall_score: number
  summary: string
}

export type ReportPolishType = 'match_analysis' | 'action_plan' | 'other'

export interface ReportPolishRequest {
  original_content: string
  report_type: ReportPolishType
  context?: Record<string, unknown>
}

export interface ReportPolishResponse {
  original_content: string
  polished_content: string
  report_type: ReportPolishType
  length_before: number
  length_after: number
}

export function getReportPlanApi(params: GetReportPlanParams) {
  return request.post<Result<GrowthPlanData>>('/report/plan', null, {
    params: {
      job_id: params.jobId,
      cache_enabled: params.cacheEnabled ?? true,
    },
  })
}

export function checkReportIntegrityApi(data: ReportIntegrityCheckRequest) {
  return request.post<Result<ReportIntegrityCheckResponse>>('/report/check', data)
}

export function polishReportParagraphApi(data: ReportPolishRequest) {
  return request.post<Result<ReportPolishResponse>>('/report/polish', data)
}
