export interface PointsMembershipChangeDTO {
  packageId: number       // 套餐id
  amount: number          // 支付金额 (BigDecimal)
  points: number          // 积分数 (Integer)
  payType: number         // 支付方式: 1微信, 2支付宝
  
  description?: number    // 后端要求 Integer 类型
  membershipLevel?: number // 会员等级 (月卡=1, 季卡=2, 年卡=3)
  name?: string           // 套餐名称
}