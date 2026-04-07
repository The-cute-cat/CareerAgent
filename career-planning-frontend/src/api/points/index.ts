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

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/master
=======
>>>>>>> origin/master
=======
>>>>>>> 46c4c4915a8e69a1e650eca09eaaa76221b03829
export const getUserInfoService = (id: number) => {

  return request.get<Result<AccountPointsData>>(`/user/info`)
}

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> origin/master
=======
>>>>>>> origin/master
=======
>>>>>>> origin/master
=======
>>>>>>> 46c4c4915a8e69a1e650eca09eaaa76221b03829
export const consumePointsService = (data: PointsConsumeRequest) => {
  if (ENABLE_MOCK) {
    return mockConsumePointsApi(data)
  }

  return request.post<Result<PointsConsumeData>>('/points/consume', data)
}
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> origin/master

export interface PointsMembershipChangeDTO {
  userId: number
  amount: number
  type: number
  vip?: number
  status?: number
  description?: string
}
=======

import type { PointsMembershipChangeDTO } from '@/types/pointsMembershipChangeDTO'
export type { PointsMembershipChangeDTO }
>>>>>>> origin/master
=======

import type { PointsMembershipChangeDTO } from '@/types/pointsMembershipChangeDTO'
export type { PointsMembershipChangeDTO }
>>>>>>> 46c4c4915a8e69a1e650eca09eaaa76221b03829

export const rechargePointsService = (data: PointsMembershipChangeDTO) => {
  return request.post<Result<any>>('/points/recharge', data)
}

export interface PackageData {
  id: number
  name: string
  price: number
  points?: number
  type: number
  description?: string
  status?: number
  [key: string]: any
}

export const getPackagesByTypeService = (type: number) => {
  return request.get<Result<PackageData[]>>(`/package/list/type/${type}`)
}
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> origin/master
=======
>>>>>>> origin/master
=======
=======
>>>>>>> 46c4c4915a8e69a1e650eca09eaaa76221b03829

export const getAlipayService = (orderNo: number) => {
  return request.get(`/alipay/pay/${orderNo}`)
}
<<<<<<< HEAD
>>>>>>> origin/master
=======
>>>>>>> 46c4c4915a8e69a1e650eca09eaaa76221b03829
