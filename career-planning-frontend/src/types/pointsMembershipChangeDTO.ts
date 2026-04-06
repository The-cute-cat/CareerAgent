
export interface PointsMembershipChangeDTO {

  // 套餐id
  id: number

  name: string

  // 1:充值,2:消费
  type: 1 | 2

  // 充值金额
  amount: number
  
  // 描述
  description: string

  // 充值积分
  points: number

  // 状态
  status: number
}