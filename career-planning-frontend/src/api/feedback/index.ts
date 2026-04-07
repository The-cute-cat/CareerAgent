import request from '@/utils/request'
import type { AxiosResponse } from 'axios'
import type { Result } from '@/types/type'

// ==================== Mock 开关配置 ====================
const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'

/**
 * 反馈信息实体
 */
export interface Feedback {
  id?: number
  userId?: number
  content: string
  type: string
  contact?: string
  images?: string // 图片URL，多张可以用逗号分隔
  createTime?: string
  updateTime?: string
  status?: number // 0:待处理, 1:已回复, 2:已关闭
  response?: string // 管理员回复
}

/**
 * 提交反馈
 * @param data 反馈数据
 */
export const submitFeedbackService = (data: Feedback) => {
  return request.post<Result<boolean>>('/feedback/submit', data)
}

/**
 * 查询用户反馈历史
 * @param userId 用户ID
 * @param pageNum 页码
 * @param pageSize 每页数量
 */
export const getUserFeedbackHistoryService = (userId: number, pageNum: number = 1, pageSize: number = 10) => {
  return request.get<Result<any>>(`/feedback/user/${userId}/history`, {
    params: { pageNum, pageSize }
  })
}

/**
 * 查询反馈详情
 * @param id 反馈ID
 */
export const getFeedbackByIdService = (id: number) => {
  return request.get<Result<Feedback>>(`/feedback/${id}`)
}

/**
 * 更新反馈
 * @param data 反馈数据
 */
export const updateFeedbackService = (data: Feedback) => {
  return request.put<Result<boolean>>('/feedback/update', data)
}
// 上传图片接口
export const uploadImageService = (formData: FormData) => {
  return request.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * Mock 模式下的图片上传
 */
function mockUploadImage(file: File): Promise<AxiosResponse<Result<{ url: string }>>> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data: {
          code: 200,
          msg: '上传成功（Mock）',
          // 生成一个临时的预览 URL 模拟服务端返回
          data: { url: URL.createObjectURL(file) }
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any
      })
    }, 800)
  })
}


/**
 * 查询所有反馈列表 (管理员)
 * @param pageNum 页码
 * @param pageSize 每页数量
 * @param status 状态过滤 (可选)
 */
export const getFeedbackListService = (pageNum: number = 1, pageSize: number = 10, status?: number) => {
  return request.get<Result<any>>('/feedback/list', {
    params: { pageNum, pageSize, status }
  })
}
