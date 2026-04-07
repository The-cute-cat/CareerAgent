import request from '@/utils/request'
import type { Result } from '@/types/type'

// ==================== Mock 开关配置 ====================
const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'

/**
 * 使用记录实体
 */
export interface UsageRecord {
  id: number
  userId: number
  username?: string
  actionType: string // 如：'CAREER_FORM_SUBMIT', 'REPORT_GENERATE', 'INTERVIEW_PRACTICE'
  actionName: string // 操作名称，如：'提交职业表单', '生成职业报告', '模拟面试'
  pointsConsumed: number
  createTime: string
  details?: string
}

/**
 * 获取全局使用记录 (管理员)
 * @param pageNum 页码
 * @param pageSize 每页数量
 * @param userId 用户ID过滤 (可选)
 */
export const getUsageRecordsService = (pageNum: number = 1, pageSize: number = 20, userId?: number) => {
  if (ENABLE_MOCK) {
    return mockGetUsageRecords(pageNum, pageSize, userId)
  }
  return request.get<Result<any>>('/admin/usage/records', {
    params: { pageNum, pageSize, userId }
  })
}

/**
 * Mock 数据
 */
function mockGetUsageRecords(pageNum: number, pageSize: number, userId?: number) {
  return new Promise<any>((resolve) => {
    const list: UsageRecord[] = []
    const types: { type: string, name: string, points: number }[] = [
      { type: 'CAREER_FORM_SUBMIT', name: '提交职业表单', points: 50 },
      { type: 'REPORT_GENERATE', name: '生成精简报告', points: 100 },
      { type: 'REPORT_GENERATE_FULL', name: '生成深度报告', points: 200 },
      { type: 'INTERVIEW_PRACTICE', name: '模拟面试练习', points: 30 },
      { type: 'RESUME_OPTIMIZE', name: '简历优化', points: 40 }
    ]
    
    for (let i = 0; i < pageSize; i++) {
        const typeIndex = Math.floor(Math.random() * types.length)
        const selectedType = types[typeIndex]
        if (!selectedType) continue
        
        const currentUserId = userId || Math.floor(Math.random() * 1000) + 100
        list.push({
            id: (pageNum - 1) * pageSize + i + 1,
            userId: currentUserId,
            username: `用户_${currentUserId}`,
            actionType: selectedType.type,
            actionName: selectedType.name,
            pointsConsumed: selectedType.points,
            createTime: new Date(Date.now() - Math.random() * 1000000000).toLocaleString(),
            details: '执行了相关 AI 分析操作'
        })
    }

    setTimeout(() => {
      resolve({
        data: {
          code: 200,
          msg: 'Success (Mock)',
          data: {
            list,
            total: 100
          }
        }
      })
    }, 500)
  })
}
