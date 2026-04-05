import request from '@/utils/request'
import type { Result } from '@/types/type'
import { mockConsumePointsApi, mockGetAccountPointsApi } from '@/mock/mockdata/Points_mockdata'

const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'

export interface AccountPointsData {
  userId: number
  pointsBalance: number
  totalConsumed: number
  updateTime: string
  referralCount: number
  referralRewardTotal: number
}

export interface PointsConsumeRequest {
  amount: number
  description?: string
  status?: number
  type: number
  userId: number
  vip?: number
  [property: string]: any
}

export interface PointsConsumeData {
  id: number
  userId: number
  pointsBalance: number
  PointsRemainAmount: number
  status: number
  totalConsumed: number
  endTime: string
  ActivityEndTime: string
  createTime: string
  updateTime: string
}

export const getAccountPointsService = (id: number) => {
  if (ENABLE_MOCK) {
    return mockGetAccountPointsApi(id)
  }

  return request.get<Result<AccountPointsData>>(`/points/account/${id}`)
}

export const consumePointsService = (data: PointsConsumeRequest) => {
  if (ENABLE_MOCK) {
    return mockConsumePointsApi(data)
  }

  return request.post<Result<PointsConsumeData>>('/points/consume', data)
}
