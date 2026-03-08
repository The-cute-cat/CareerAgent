//API呢是我们用来存放和我们后端对接接口
import request from '@/utils/request'
// import { API } from '@/api/user/index'
import type { LoginFormDTO } from '../../types/type'
// 用户登录接口 -maq
export const userLoginService = (loginInfo: LoginFormDTO) => {
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
