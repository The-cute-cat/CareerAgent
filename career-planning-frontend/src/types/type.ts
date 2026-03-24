

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





