//统一管理用户相关的接口
import request from '@/utils/request3'
import type { loginForm, userInfoResponseData } from '../../types/type'

// 定义接口枚举，方便管理和维护
enum API {
  REGISTER = '/user/register',
  LOGIN_URL = '/user/login',
  GET_USER_INFO = '/user/info',
  LOGOUT = '/user/logout',
  FORGOT_PASSWORD = '/user/forgot-password',
}

// 用户注册接口
export const register = (data: loginForm) => {
  //上传到后端的数据
  return request.post(API.REGISTER, data) //后端返回数据
}

// 获取用户信息接口
export const getUserInfo = () => {
  return request.get<any, userInfoResponseData>(API.GET_USER_INFO)
}
// 用户登出接口
export const logout = () => {
  return request.post(API.LOGOUT)
}

//忘记密码接口
export const forgotPassword = (data: any) => {
  return request.post(API.FORGOT_PASSWORD, data)
}

export default API
