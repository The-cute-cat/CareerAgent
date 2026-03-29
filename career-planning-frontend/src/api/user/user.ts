//API呢是我们用来存放和我们后端对接接口
import request from '@/utils/request'
// import { API } from '@/api/user/index'
import type { LoginFormDTO } from '../../types/user'
import { mockUserLoginApi } from '@/mock/mockdata/Login_mockdata'
/** 通用响应结果 */
import type {  Result } from "../../types/type"

const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'


// 用户登录接口 -maq
export interface LoginResponse {
  message: string
  code: number
  msg?: string
  data: {
    accessToken: string
    refreshToken: string
    userInfo: any
  }
}

export const userLoginService = (loginInfo: LoginFormDTO) => {
  if (ENABLE_MOCK) {
    return mockUserLoginApi(loginInfo)
  }
  return request.post('/user/login', loginInfo)
}

export const userRegisterService = (loginInfo: LoginFormDTO) => {
  return request.post('/user/register', loginInfo)
}

export const userForgetPasswordService = (loginInfo: LoginFormDTO) => {
  return request.post('/user/forget-password', loginInfo)
}

export const userSendCodeRegisterService = (loginInfo: LoginFormDTO) => {
  return request.post('/user/send-code-register', loginInfo)
}

export const userSendCodeForgetService = (loginInfo: LoginFormDTO) => {
  return request.post('/user/send-code-forget', loginInfo)
}

export const userGetUserInfoService = () => {
  return request.get('/user/get-user-info')
}

export const userGetUserBasicFileInfoService = () => {
  return request.get('/user/get-basic-info')
}
