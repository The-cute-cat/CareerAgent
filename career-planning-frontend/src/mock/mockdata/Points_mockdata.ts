import type { AxiosResponse } from 'axios'
import type { Result } from '@/types/type'
import type { AccountPointsData, PointsConsumeData, PointsConsumeRequest } from '@/api/points'

export type MockAccountPointsResponse = Result<AccountPointsData>

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// localStorage 键名
const STORAGE_KEYS = {
  accounts: 'career_points_accounts',
  records: 'career_points_records',
  members: 'career_points_members'
} as const

// 从 localStorage 加载数据
const loadFromStorage = <T>(key: string): Map<number, T> => {
  const map = new Map<number, T>()
  try {
    const data = localStorage.getItem(key)
    if (data) {
      const parsed = JSON.parse(data) as Array<[number, T]>
      parsed.forEach(([id, value]) => map.set(id, value))
    }
  } catch (e) {
    console.warn(`加载 ${key} 失败:`, e)
  }
  return map
}

// 保存数据到 localStorage
const saveToStorage = <T>(key: string, map: Map<number, T>) => {
  try {
    const data = Array.from(map.entries())
    localStorage.setItem(key, JSON.stringify(data))
  } catch (e) {
    console.warn(`保存 ${key} 失败:`, e)
  }
}

// 积分账户存储（从 localStorage 初始化）
const pointsAccountStore = loadFromStorage<AccountPointsData>(STORAGE_KEYS.accounts)
// 积分流水记录存储（从 localStorage 初始化）
const pointsRecordsStore = loadFromStorage<PointsRecord[]>(STORAGE_KEYS.records)
// 用户会员信息存储（从 localStorage 初始化）
const memberInfoStore = loadFromStorage<MemberInfo>(STORAGE_KEYS.members)

// 积分流水记录类型
export interface PointsRecord {
  id: number
  userId: number
  type: 'earn' | 'consume' | 'recharge' | 'gift' | 'refund'
  amount: number
  balance: number
  description: string
  createTime: string
  relatedFunction?: string
}

// 会员信息类型
export interface MemberInfo {
  userId: number
  memberType: 'normal' | 'monthly' | 'quarterly' | 'yearly'
  memberExpireAt: string | null
  monthlyPoints: number
  discountRate: number
  createTime: string
}

// 功能积分消耗配置
export const POINTS_CONSUME_CONFIG = {
  careerAssessment: { name: 'AI职业测评', points: 30, key: 'career_assessment' },
  jobMatching: { name: '岗位推荐分析', points: 20, key: 'job_matching' },
  resumeOptimize: { name: '简历优化', points: 50, key: 'resume_optimize' },
  resumeGenerate: { name: '简历一键生成', points: 60, key: 'resume_generate' },
  mockInterview: { name: '模拟面试', points: 80, key: 'mock_interview' },
  careerReport: { name: '生涯规划报告', points: 100, key: 'career_report' },
  developmentMap: { name: '职业发展图谱', points: 80, key: 'development_map' },
  aiChat: { name: 'AI问答', points: 10, key: 'ai_chat' }
} as const

// 会员套餐配置
export const MEMBER_CONFIG = {
  monthly: {
    name: '月度会员',
    giftPoints: 1000,
    monthlyPoints: 1000,
    discountRate: 0.9,
    price: 29.9,
    durationDays: 30
  },
  quarterly: {
    name: '季度会员',
    giftPoints: 3500,
    monthlyPoints: 1200,
    discountRate: 0.8,
    price: 79.9,
    durationDays: 90
  },
  yearly: {
    name: '年度会员',
    giftPoints: 15000,
    monthlyPoints: 1500,
    discountRate: 0.7,
    price: 299.9,
    durationDays: 365
  }
} as const

function wrapAsAxiosResponse<T>(data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: 'OK',
    headers: {},
    config: {} as any
  }
}

// 创建默认会员信息
const createDefaultMemberInfo = (id: number): MemberInfo => ({
  userId: id,
  memberType: 'normal',
  memberExpireAt: null,
  monthlyPoints: 0,
  discountRate: 1,
  createTime: new Date().toISOString()
})

// 创建默认积分账户
const createMockPointsData = (id: number): AccountPointsData => ({
  userId: id,
  pointsBalance: 50000, // 新用户默认50000积分
  totalConsumed: 0,
  updateTime: new Date().toISOString(),
  referralCount: 0,
  referralRewardTotal: 0
})

// 保存所有积分数据到 localStorage
const saveAllPointsData = () => {
  saveToStorage(STORAGE_KEYS.accounts, pointsAccountStore)
  saveToStorage(STORAGE_KEYS.records, pointsRecordsStore)
  saveToStorage(STORAGE_KEYS.members, memberInfoStore)
}

// 获取或创建用户账户
const getOrCreateAccount = (id: number) => {
  const existing = pointsAccountStore.get(id)
  if (existing) return existing

  const created = createMockPointsData(id)
  pointsAccountStore.set(id, created)

  // 同时初始化会员信息
  if (!memberInfoStore.has(id)) {
    memberInfoStore.set(id, createDefaultMemberInfo(id))
  }

  // 初始化积分记录
  if (!pointsRecordsStore.has(id)) {
    pointsRecordsStore.set(id, [{
      id: Date.now(),
      userId: id,
      type: 'gift',
      amount: 500,
      balance: 500,
      description: '新用户注册奖励',
      createTime: new Date().toISOString()
    }])
  }

  // 持久化到 localStorage
  saveAllPointsData()

  return created
}

// 获取会员信息
export const getMemberInfo = (userId: number): MemberInfo => {
  return memberInfoStore.get(userId) || createDefaultMemberInfo(userId)
}

// 更新会员信息
export const updateMemberInfo = (userId: number, memberType: 'monthly' | 'quarterly' | 'yearly') => {
  const config = MEMBER_CONFIG[memberType]
  const now = new Date()
  const expireAt = new Date(now.getTime() + config.durationDays * 24 * 60 * 60 * 1000)

  const memberInfo: MemberInfo = {
    userId,
    memberType,
    memberExpireAt: expireAt.toISOString(),
    monthlyPoints: config.monthlyPoints,
    discountRate: config.discountRate,
    createTime: now.toISOString()
  }

  memberInfoStore.set(userId, memberInfo)

  // 同时赠送积分
  const account = getOrCreateAccount(userId)
  const newBalance = account.pointsBalance + config.giftPoints
  account.pointsBalance = newBalance
  account.updateTime = new Date().toISOString()
  pointsAccountStore.set(userId, account)

  // 添加积分记录
  addPointsRecord(userId, {
    id: Date.now(),
    userId,
    type: 'gift',
    amount: config.giftPoints,
    balance: newBalance,
    description: `开通${config.name}赠送积分`,
    createTime: new Date().toISOString()
  })

  // 持久化到 localStorage
  saveAllPointsData()

  return memberInfo
}

// 添加积分记录
const addPointsRecord = (userId: number, record: PointsRecord) => {
  const records = pointsRecordsStore.get(userId) || []
  records.unshift(record)
  pointsRecordsStore.set(userId, records)
  // 持久化到 localStorage
  saveToStorage(STORAGE_KEYS.records, pointsRecordsStore)
}

// 获取积分记录
export const getPointsRecords = (userId: number): PointsRecord[] => {
  return pointsRecordsStore.get(userId) || []
}

// 计算实际消耗积分（考虑会员折扣）
export const calculateActualPoints = (userId: number, basePoints: number): number => {
  const memberInfo = getMemberInfo(userId)
  return Math.ceil(basePoints * memberInfo.discountRate)
}

// 检查会员是否过期
export const isMemberExpired = (userId: number): boolean => {
  const memberInfo = memberInfoStore.get(userId)
  if (!memberInfo || !memberInfo.memberExpireAt) return true
  if (memberInfo.memberType === 'normal') return true

  const expireAt = new Date(memberInfo.memberExpireAt)
  return expireAt < new Date()
}

// 获取账号积分（API）
export async function mockGetAccountPointsApi(
  id: number,
  delayMs = 400
): Promise<AxiosResponse<MockAccountPointsResponse>> {
  await delay(delayMs)
  const account = getOrCreateAccount(id)

  // 检查会员是否过期
  if (isMemberExpired(id) && account.pointsBalance >= 0) {
    const memberInfo = memberInfoStore.get(id)
    if (memberInfo && memberInfo.memberType !== 'normal') {
      memberInfo.memberType = 'normal'
      memberInfo.memberExpireAt = null
      memberInfo.discountRate = 1
      memberInfoStore.set(id, memberInfo)
    }
  }

  return wrapAsAxiosResponse({
    code: 200,
    msg: '获取账号积分成功',
    data: account
  })
}

// 消费积分（API）
export async function mockConsumePointsApi(
  request: PointsConsumeRequest,
  delayMs = 500
): Promise<AxiosResponse<Result<PointsConsumeData>>> {
  await delay(delayMs)

  const base = getOrCreateAccount(request.userId)
  const amount = request.amount // 负数表示消费

  // 检查积分是否足够（只检查消费场景）
  if (amount < 0 && base.pointsBalance < Math.abs(amount)) {
    return wrapAsAxiosResponse({
      code: 4001,
      msg: '积分余额不足',
      data: null as any
    })
  }

  const nextBalance = Math.max(0, base.pointsBalance + amount)
  const consumedAmount = amount < 0 ? Math.abs(amount) : 0

  const nextAccount: AccountPointsData = {
    ...base,
    pointsBalance: nextBalance,
    totalConsumed: base.totalConsumed + consumedAmount,
    updateTime: new Date().toISOString()
  }

  pointsAccountStore.set(request.userId, nextAccount)

  // 添加积分记录
  addPointsRecord(request.userId, {
    id: Date.now(),
    userId: request.userId,
    type: amount < 0 ? 'consume' : 'earn',
    amount: Math.abs(amount),
    balance: nextBalance,
    description: request.description || (amount < 0 ? '积分消费' : '积分获取'),
    createTime: new Date().toISOString(),
    relatedFunction: request.description
  })

  // 持久化到 localStorage
  saveAllPointsData()

  return wrapAsAxiosResponse({
    code: 200,
    msg: amount < 0 ? '积分消费成功' : '积分充值成功',
    data: {
      id: 9001,
      userId: request.userId,
      pointsBalance: nextBalance,
      PointsRemainAmount: nextBalance,
      status: request.status ?? 1,
      totalConsumed: nextAccount.totalConsumed,
      endTime: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
      ActivityEndTime: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      createTime: new Date().toISOString(),
      updateTime: new Date().toISOString()
    }
  })
}

// 获取用户完整信息（包含会员信息）
export async function mockGetUserFullInfoApi(
  userId: number,
  delayMs = 300
): Promise<AxiosResponse<Result<any>>> {
  await delay(delayMs)

  const account = getOrCreateAccount(userId)
  const memberInfo = getMemberInfo(userId)
  const records = getPointsRecords(userId)

  return wrapAsAxiosResponse({
    code: 200,
    msg: '获取用户信息成功',
    data: {
      ...account,
      ...memberInfo,
      records: records.slice(0, 10) // 最近10条
    }
  })
}

// 充值积分（模拟）
export async function mockRechargePointsApi(
  userId: number,
  amount: number,
  description: string,
  delayMs = 400
): Promise<AxiosResponse<Result<PointsConsumeData>>> {
  await delay(delayMs)

  const base = getOrCreateAccount(userId)
  const nextBalance = base.pointsBalance + amount

  const nextAccount: AccountPointsData = {
    ...base,
    pointsBalance: nextBalance,
    updateTime: new Date().toISOString()
  }

  pointsAccountStore.set(userId, nextAccount)

  // 添加积分记录
  addPointsRecord(userId, {
    id: Date.now(),
    userId,
    type: 'recharge',
    amount,
    balance: nextBalance,
    description,
    createTime: new Date().toISOString()
  })

  // 持久化到 localStorage
  saveAllPointsData()

  return wrapAsAxiosResponse({
    code: 200,
    msg: '积分充值成功',
    data: {
      id: Date.now(),
      userId,
      pointsBalance: nextBalance,
      PointsRemainAmount: nextBalance,
      status: 1,
      totalConsumed: nextAccount.totalConsumed,
      endTime: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
      ActivityEndTime: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      createTime: new Date().toISOString(),
      updateTime: new Date().toISOString()
    }
  })
}

// 导出存储用于调试
export const getPointsStore = () => ({
  accounts: pointsAccountStore,
  records: pointsRecordsStore,
  members: memberInfoStore
})
