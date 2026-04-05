

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
 * 通用响应结果
 * @template T 响应数据的类型
 */
export interface Result<T = unknown> {
  /**
   * 成功为 --200  失败为 401
   */
  code: number
  /**
   * 返回数据
   */
  data?: T | null
  /**
   * 提示消息
   */
  msg?: string | null
}





