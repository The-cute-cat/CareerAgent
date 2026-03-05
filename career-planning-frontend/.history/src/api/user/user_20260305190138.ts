//API呢是我们用来存放和我们后端对接接口
import request from '@/utils/request'
// import { API } from '@/api/user/index'
import type { LoginFormDTO } from '../../types/type'
// 用户登录接口
export const login = (loginInfo: LoginFormDTO) => {
  return request.post('/user/login', loginInfo)
}
export const register = (loginInfo: LoginFormDTO) => {
  return request.post('/user/register', loginInfo)
}
export const forgetPassword = (loginInfo: LoginFormDTO) => {
  return request.post('/user/forge', loginInfo)
}
