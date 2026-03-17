//API呢是我们用来存放和我们后端对接接口
import request from '@/utils/request'
// import { API } from '@/api/user/index'
import type { LoginFormDTO, Result } from '../../types/type'

// 用户登录接口 -maq
export interface LoginResponse {
  code: number
  msg?: string
  data: {
    accessToken: string
    refreshToken: string
    userInfo: any
  }
}

export const userLoginService = (loginInfo: LoginFormDTO) => {
  return request.post<LoginResponse>('/user/login', loginInfo)
}

export const userRegisterService = (loginInfo: LoginFormDTO) => {
  return request.post<Result>('/user/register', loginInfo)
}

export const userForgetPasswordService = (loginInfo: LoginFormDTO) => {
  return request.post<Result>('/user/forget-password', loginInfo)
}

export const userSendCodeRegisterService = (loginInfo: LoginFormDTO) => {
  return request.post<Result>('/user/send-code-register', loginInfo)
}

export const userSendCodeForgetService = (loginInfo: LoginFormDTO) => {
  return request.post<Result>('/user/send-code-forget', loginInfo)
}