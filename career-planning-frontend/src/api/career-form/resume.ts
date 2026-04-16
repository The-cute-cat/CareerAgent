import type { AxiosResponse } from 'axios'

import { mockUploadResumeApi } from '@/mock/mockdata/Resume_mockdata'
import type { UploadResponse } from '@/types/careerform_report'
import type { Result } from '@/types/type'
import request from '@/utils/request'

const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'
const MOCK_SCENARIO = import.meta.env.VITE_MOCK_SCENARIO || 'success'

export interface UploadParams {
  files: File[]
  userId?: string
  overwrite?: boolean
  onProgress?: (progressEvent: any) => void
}

export function uploadProfileFilesApi(params: UploadParams, signal?: AbortSignal) {
  if (ENABLE_MOCK) {
    return mockUploadWithProgress(params, MOCK_SCENARIO as any)
  }

  const formData = new FormData()

  params.files.forEach((file) => {
    formData.append('files', file)
  })

  if (params.userId) {
    formData.append('user_id', params.userId)
  }

  formData.append('overwrite', params.overwrite ? 'true' : 'false')

  return request.post<Result<UploadResponse | UploadResponse[]>>('/parse/file', formData, {
    signal,
    onUploadProgress: (progressEvent: any) => {
      if (progressEvent.total && params.onProgress) {
        params.onProgress(progressEvent)
      }
    }
  })
}

function mockUploadWithProgress(
  params: UploadParams,
  scenario: 'success' | 'partial' | 'processing' | 'failed'
): Promise<AxiosResponse<Result<UploadResponse | UploadResponse[]>>> {
  return new Promise((resolve, reject) => {
    let progress = 0
    const stepDelay = 100

    const interval = setInterval(() => {
      progress += 5

      if (params.onProgress && progress < 100) {
        params.onProgress({
          loaded: progress,
          total: 100,
          progress: progress / 100
        })
      }

      if (progress >= 100) {
        clearInterval(interval)
        setTimeout(() => {
          mockUploadResumeApi(params.files.map(file => file.name), scenario, 500)
            .then(resolve)
            .catch(reject)
        }, 500)
      }
    }, stepDelay)

    if (params.onProgress) {
      ;(params as UploadParams & { _cancelInterval?: () => void })._cancelInterval = () => clearInterval(interval)
    }
  })
}

export const uploadResumeApi = uploadProfileFilesApi
