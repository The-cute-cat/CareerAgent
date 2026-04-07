import request from '@/utils/request'
import type { Result } from '@/types/type'

/**
 * 获取邀请码
 * 如果用户已经是大使，则返回邀请码；如果不是，通常返回空或特定错误码。
 */
export const getInviteCodeService = () => {
  return request.get<Result<string>>('/points/invite')
}

/**
 * 注册成为邀请大使并生成邀请码
 */
export const registerAmbassadorService = () => {
  return request.post<Result<string>>('/points/invite')
}
