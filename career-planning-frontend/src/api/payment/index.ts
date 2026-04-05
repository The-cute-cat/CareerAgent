import request from '@/utils/request'
import type { Result } from '@/types/type'

const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'
// 使用 /api 前缀走 vite 代理到后端
const API_BASE_URL = ''

// ==================== 类型定义 ====================

/** 创建支付订单请求（发给后端，不含订单号） */
export interface PaymentCreateRequest {
  amount: number
  pointsGranted: number
  payType: number           // 1微信, 2支付宝
  purpose: number           // 1积分充值, 2会员购买
  memberLevel?: number      // 会员购买时传：1月度, 2季度, 3年度
}

/** 后端返回的订单数据（对应 PaymentOrder 实体） */
export interface PaymentOrderVO {
  id: number                // 雪花算法生成的ID，这就是订单号
  orderNo: string | null
  userId: number
  amount: number
  pointsGranted: number
  payType: number
  status: number            // 0待支付, 1已支付, 2已取消, 3已退款
  transactionId: string | null
  payTime: string | null
  createTime: string
}

/** 订单状态查询返回 */
export interface PaymentStatusVO {
  orderId: string
  status: 'pending' | 'paid' | 'expired' | 'cancelled' | string
  amount?: number
  pointsGranted?: number
  paidAt?: string
}

// ==================== API 方法 ====================

/**
 * 1. 创建支付订单
 *
 * 前端传业务参数（金额、积分数、支付方式），不含订单号。
 * 后端创建 PaymentOrder 存入数据库，雪花算法自动生成 id，返回给前端。
 * 前端拿到 data.id 就是订单号，后续用它去支付和轮询。
 *
 * POST /member/order/create
 * 请求体：{ amount, pointsGranted, payType, purpose, memberLevel }
 * 响应体：{ code: 0, msg: "创建订单成功", data: { id: 1892738564231725057, ... } }
 */
export const createPaymentService = (data: PaymentCreateRequest) => {
  if (ENABLE_MOCK) {
    // Mock 模式下模拟后端返回雪花ID
    const snowflakeId = Date.now() * 10000 + Math.floor(Math.random() * 10000)
    return Promise.resolve({
      data: {
        code: 0,
        msg: '创建订单成功',
        data: {
          id: snowflakeId,
          orderNo: null,
          userId: 1,
          amount: data.amount,
          pointsGranted: data.pointsGranted,
          payType: data.payType,
          status: 0,
          transactionId: null,
          payTime: null,
          createTime: new Date().toISOString()
        }
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    })
  }

  return request.post<Result<PaymentOrderVO>>('/api/member/order/create', data)
}

/**
 * 2. 构建支付宝支付跳转 URL
 *
 * 注意：这不是 AJAX 请求，只是拼接 URL 字符串。
 * 最终用 window.open(url) 打开，后端返回 HTML 表单自动跳转到支付宝收银台。
 * 后端会根据 orderNo 去 payment_order 表查金额等信息，所以只需要传订单号。
 *
 * 对应后端：GET /member/pay/{orderNo}
 * 返回：text/html（不是 JSON，浏览器直接渲染）
 */
export const buildAlipayPagePayUrl = (orderNo: string | number): string => {
  // 使用完整后端地址直接跳转（不走前端代理，因为是 window.open）
  const serverURL = import.meta.env.VITE_SERVER || 'http://localhost:8080'
  return `${serverURL}/member/pay/${orderNo}`
}

/**
 * 3. 查询订单支付状态（轮询用）
 *
 * 前端每 3 秒调一次，直到返回 paid / expired / cancelled 停止。
 *
 * 对应后端：GET /member/order/status/{orderNo}
 * 请求：无 body
 * 响应：{ code: 0, data: { orderId, status, paidAt } }
 */
export const queryPaymentStatusService = (orderNo: string) => {
  if (ENABLE_MOCK) {
    const store: Record<string, string> = {}
    store[orderNo] = 'pending'

    return Promise.resolve({
      data: {
        code: 0,
        msg: '查询成功',
        data: {
          orderId: orderNo,
          status: store[orderNo] || 'pending',
          paidAt: null
        }
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    })
  }

  return request.get<Result<PaymentStatusVO>>(`/api/member/order/status/${orderNo}`)
}

// ==================== 不需要前端调用的接口 ====================

/**
 * POST /member/notify — 支付宝异步回调
 *
 * 这个接口不需要前端调用，是支付宝服务器在用户支付成功后主动回调后端的。
 * 前端通过 queryPaymentStatusService 轮询间接感知支付结果。
 * 列在这里仅作说明。
 */
