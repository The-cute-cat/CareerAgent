import type { AxiosResponse } from 'axios'

export interface MockLoginUserInfo {
  id: number
  username: string
  nickname: string
  name: string
  avatar: string
  email: string
  info: string
  signature: string
  phone: string
  points: number
  memberType: 'normal' | 'monthly' | 'quarterly' | 'yearly'
  memberExpireAt: string
  createTime: string
  updateTime: string
}

export interface MockLoginResponseData {
  accessToken: string
  refreshToken: string
  userInfo: MockLoginUserInfo
}

export interface MockLoginResponse {
  code: number
  message: string
  msg?: string
  data: MockLoginResponseData
}

export const mockLoginSuccess: MockLoginResponse = {
  code: 200,
  message: '登录成功',
  msg: '登录成功',
  data: {
    accessToken: 'mock-access-token-1001',
    refreshToken: 'mock-refresh-token-1001',
    userInfo: {
      id: 1001,
      username: 'user1001',
      nickname: '用户1001',
      name: '用户1001',
      avatar: 'https://picsum.photos/200/200?random=12',
      email: 'user1001@example.com',
      info: '成为更好的自己',
      signature: '成为更好的自己',
      phone: '13800138000',
      points: 500,
      memberType: 'quarterly',
      memberExpireAt: '2026-06-30 23:59:59',
      createTime: '2026-03-01 10:00:00',
      updateTime: '2026-03-29 12:00:00'
    }
  }
}

export const mockLoginFailed = {
  code: 401,
  message: '用户名或密码错误',
  msg: '用户名或密码错误',
  data: null
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

function wrapAsAxiosResponse<T>(data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: 'OK',
    headers: {},
    config: {} as any
  }
}

export async function mockUserLoginApi(
  loginInfo: { username?: string | null; password?: string | null },
  delayMs = 600
): Promise<AxiosResponse<MockLoginResponse | typeof mockLoginFailed>> {
  await delay(delayMs)

  const username = String(loginInfo.username || '').trim()
  const password = String(loginInfo.password || '').trim()

  if (!username || !password) {
    return wrapAsAxiosResponse(
      {
        code: 400,
        message: '用户名和密码不能为空',
        msg: '用户名和密码不能为空',
        data: null
      },
      200
    )
  }

  if (username === 'user1001' && password === '123456') {
    return wrapAsAxiosResponse(mockLoginSuccess, 200)
  }

  return wrapAsAxiosResponse(mockLoginFailed, 200)
}

