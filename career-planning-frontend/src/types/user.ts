/**
 * 用户相关类型定义
 */

/** 通用响应结果 */
import type {  Result } from "./type"


/** 用户信息 */
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
  pointBalance: number
  endTime: string
}

/** 用户信息响应 */
export interface UserInfoResponseData {
  code: number
  data: {
    checkUser: UserInfo
  }
}


/**
 * LoginFormDTO
 */
export interface LoginFormDTO {
  /**
   * 验证码
   */
  code?: string | null
  /**
   * 邀请码
   */
  inviteCode?: string | null
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




/** 登录表单参数 */
export interface LoginFormDTO {
  /** 验证码 */
  code?: string | null
  /** 邀请码 */
  inviteCode?: string | null
  /** 邮箱 */
  email?: string | null
  /** 密码 */
  password?: string | null
  /** 确认密码 */
  passwordConfirm?: string | null
  /** 用户名 */
  username?: string
  /** 记住我 */
  rememberMe?: boolean
}

/** 登录响应 */
export interface LoginVO {
  /** Token 信息 */
  accessToken?: string | null
  /** 刷新令牌 */
  refreshToken?: string | null
}

/** 登录接口参数 */
export interface LoginForm {
  username: string
  password: string
  rememberMe: boolean
}

/** 必填字段配置 */
export interface RequiredFieldConfig<T> {
  field: keyof T
  label: string
  validate: (value: unknown) => boolean
}
