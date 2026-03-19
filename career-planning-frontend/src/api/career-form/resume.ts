// src/api/resume.ts
import request from '@/utils/request'
import type { UploadResponse, Result, CareerReport } from '@/types/type'

export interface UploadParams {
  file: File
  userId?: string
  // parseMode?: 'quick' | 'ai_deep' // 数据解析模式
  overwrite?: boolean
  onProgress?: (percent: number) => void
}

/**
 * 上传简历并触发 AI 解析
 * 返回结果包含 abilityScores（能力评估分数，与表单提交流程格式一致）
 */
export function uploadResumeApi(params: UploadParams) {
  const formData = new FormData()

  //核心：文件流 (Key 必须与后端约定一致，通常为 file)
  formData.append('file', params.file)

  //用户上下文 (用于后端存储和权限验证)
  if (params.userId) {
    formData.append('user_id', params.userId)
  }

  //业务参数 (告诉后端如何处理)
  // formData.append('parse_mode', params.parseMode || 'ai_deep')
  formData.append('overwrite', params.overwrite ? 'true' : 'false')

  //可选：前端预提取的元数据 (减轻后端压力)
  // formData.append('file_type', params.file.type)

  return request.post<Result<UploadResponse>>('/resume-upload-chat/message', formData, {
    // 上传进度监控 (提升用户体验)
    onUploadProgress: (progressEvent: any) => {
      if (progressEvent.total && params.onProgress) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        console.log(`上传进度：${percent}%`)
        params.onProgress(percent)
      }
    },
  })
}

/**
 * 获取简历解析后的能力评估报告
 * 与表单提交流程的 /career/form/report/{taskId} 返回格式一致
 * @param taskId 简历解析任务ID
 * @returns 职业规划报告（包含 abilityScores 雷达图数据）
 */
export function getResumeReportApi(taskId: string) {
  return request.get<Result<CareerReport>>(`/resume/report/${taskId}`)
}

/**
 * 获取简历解析状态
 * @param taskId 简历解析任务ID
 * @returns 解析状态和进度
 */
export function getResumeParseStatusApi(taskId: string) {
  return request.get<
    Result<{
      taskId: string
      status: 'pending' | 'processing' | 'completed' | 'failed'
      progress?: number
      estimatedTimeRemaining?: number
    }>
  >(`/resume/status/${taskId}`)
}
