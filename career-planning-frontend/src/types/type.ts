/**
 * LoginFormDTO
 */
export interface LoginFormDTO {
  /**
   * 验证码
   */
  code?: string | null
  /**
   * 邮箱
   */
  email?: string | null
  /**
   * 密码
   */
  password?: string | null
  /**
   * 确认密码(二次密码)
   */
  passwordConfirm?: string | null
  /**
   * 用户名
   */
  username?: string
  /**
   * 记住我
   */
  rememberMe?: boolean
}

/**
 * Result
 */
export interface Result {
  /**
   * 成功为 --200  失败为 401
   */
  code: number
  /**
   * 返回数据
   */
  data?: { [key: string]: unknown } | null
  /**
   * 提示消息
   */
  msg?: string | null
}

/**
 * LoginVO
 */
export interface LoginVO {
  /**
   * Token 信息
   */
  accessToken?: string | null
  /**
   * 刷新令牌
   */
  refreshToken?: string | null
}

export interface UserInfo {
  id: number
  nickname: string
  username: string
  avatar: string
  email: string
  info: string
  phone: string
  createTime: string
  updateTime: string
  accessToken: string
  refreshToken: string
}

//登录接口需要携带的参数类型定义
export interface loginForm {
  username: string
  password: string
  rememberMe: boolean
}

interface dataType {
  token: string
}

//服务器返回的用户信息类型定义
interface user {
  checkUser: UserInfo
}

export interface userInfoResponseData {
  code: number
  data: user
}
