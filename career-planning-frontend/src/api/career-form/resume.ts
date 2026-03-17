// src/api/resume.ts
import request from '@/utils/request'
import type { UploadResponse } from '@/types/type'

export interface UploadParams {
  file: File
  userId?: string
  // parseMode?: 'quick' | 'ai_deep' // 数据解析模式
  overwrite?: boolean
  onProgress?: (percent: number) => void
}

/**
 * 上传简历并触发 AI 解析
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
  
  return request.post<UploadResponse>('/resume/upload', formData, {
    // 上传进度监控 (提升用户体验)
    onUploadProgress: (progressEvent: any) => {
      if (progressEvent.total && params.onProgress) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        console.log(`上传进度：${percent}%`)
        params.onProgress(percent)
      }
    }
  })
}
