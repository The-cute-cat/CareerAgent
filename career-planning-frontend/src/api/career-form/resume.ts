// src/api/resume.ts
import request from '@/utils/request'
import type { UploadResponse } from '@/types/careerform_report'
import type { AxiosResponse } from 'axios'
import { mockUploadResumeApi } from '@/mock/mockdata/Resume_mockdata'
/** 通用响应结果 */
import type {  Result } from "../../types/type"


// ==================== Mock 开关配置 ====================
// 设置 VITE_ENABLE_MOCK=true 在 .env 文件中启用 Mock
const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'

// Mock 场景配置：'success' | 'partial' | 'processing' | 'failed'
const MOCK_SCENARIO = import.meta.env.VITE_MOCK_SCENARIO || 'success'

export interface UploadParams {
  file: File
  userId?: string
  overwrite?: boolean
  onProgress?: (progressEvent: any) => void
}

/**
 * 上传简历并触发 AI 解析
 * 返回结果包含 abilityScores（能力评估分数，与表单提交流程格式一致）
 */
export function uploadResumeApi(params: UploadParams, signal?: AbortSignal) {
  // Mock 模式：模拟上传延迟和进度
  if (ENABLE_MOCK) {
    return mockUploadWithProgress(params, MOCK_SCENARIO as any)
  }

  const formData = new FormData()

  //核心：文件流 (Key 必须与后端约定一致，通常为 file)
  formData.append('file', params.file)

  //用户上下文 (用于后端存储和权限验证)
  if (params.userId) {
    formData.append('user_id', params.userId)
  }

  //业务参数
  formData.append('overwrite', params.overwrite ? 'true' : 'false')

  return request.post<Result<UploadResponse>>('/resume/upload', formData, {
    signal, // 用于取消上传
    // 上传进度监控 (提升用户体验)
    onUploadProgress: (progressEvent: any) => {
      if (progressEvent.total && params.onProgress) {
        params.onProgress(progressEvent)
      }
    }
  })
}

/**
 * Mock 模式下的上传，带进度模拟
 */
function mockUploadWithProgress(
  params: UploadParams,
  scenario: 'success' | 'partial' | 'processing' | 'failed'
): Promise<AxiosResponse<Result<UploadResponse>>> {
  return new Promise((resolve, reject) => {
    let progress = 0
    const stepDelay = 100 // 每步100ms，总共约2秒

    // 模拟进度回调
    const interval = setInterval(() => {
      progress += 5

      // 模拟进度事件
      if (params.onProgress && progress < 100) {
        params.onProgress({
          loaded: progress,
          total: 100,
          progress: progress / 100
        })
      }

      // 完成
      if (progress >= 100) {
        clearInterval(interval)
        // 延迟后返回结果，模拟后端处理时间
        setTimeout(() => {
          mockUploadResumeApi(params.file.name, scenario, 500)
            .then(resolve)
            .catch(reject)
        }, 500)
      }
    }, stepDelay)

    // 支持取消
    if (params.onProgress) {
      (params as any)._cancelInterval = () => clearInterval(interval)
    }
  })
}
