import type { AxiosResponse } from 'axios'
import type { Result } from '@/types/type'
import type { AccountPointsData, PointsConsumeData, PointsConsumeRequest } from '@/api/points'

export type MockAccountPointsResponse = Result<AccountPointsData>

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
const pointsAccountStore = new Map<number, AccountPointsData>()

function wrapAsAxiosResponse<T>(data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: 'OK',
    headers: {},
    config: {} as any
  }
}

const createMockPointsData = (id: number): AccountPointsData => ({
  userId: id,
  pointsBalance: 1680,
  totalConsumed: 420,
  updateTime: '2026-04-05 10:30:00',
  referralCount: 6,
  referralRewardTotal: 1200
})

const getOrCreateAccount = (id: number) => {
  const existing = pointsAccountStore.get(id)
  if (existing) {
    return existing
  }

  const created = createMockPointsData(id)
  pointsAccountStore.set(id, created)
  return created
}

export async function mockGetAccountPointsApi(
  id: number,
  delayMs = 400
): Promise<AxiosResponse<MockAccountPointsResponse>> {
  await delay(delayMs)

  return wrapAsAxiosResponse({
    code: 0,
    msg: 'mock 获取账号积分成功',
    data: getOrCreateAccount(id)
  })
}

export async function mockConsumePointsApi(
  request: PointsConsumeRequest,
  delayMs = 500
): Promise<AxiosResponse<Result<PointsConsumeData>>> {
  await delay(delayMs)

  const base = getOrCreateAccount(request.userId)
  const nextBalance = Math.max(0, base.pointsBalance + request.amount)
  const consumedAmount = request.amount < 0 ? Math.abs(request.amount) : 0
  const nextAccount: AccountPointsData = {
    ...base,
    pointsBalance: nextBalance,
    totalConsumed: base.totalConsumed + consumedAmount,
    updateTime: '2026-04-05 10:35:00'
  }

  pointsAccountStore.set(request.userId, nextAccount)

  return wrapAsAxiosResponse({
    code: 200,
    msg: 'mock 积分变更成功',
    data: {
      id: 9001,
      userId: request.userId,
      pointsBalance: nextBalance,
      PointsRemainAmount: nextBalance,
      status: request.status ?? 1,
      totalConsumed: nextAccount.totalConsumed,
      endTime: '2026-12-31 23:59:59',
      ActivityEndTime: '2026-04-30 23:59:59',
      createTime: '2026-04-05 10:35:00',
      updateTime: '2026-04-05 10:35:00'
    }
  })
}
