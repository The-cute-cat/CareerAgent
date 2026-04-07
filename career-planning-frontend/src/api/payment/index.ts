import request from '@/utils/request'
import type { Result } from '@/types/type'

const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'

// ==================== 类型定义 ====================

/** 支付订单请求（创建订单 + 支付） */
export interface PaymentOrderRequest {
  amount: number            // 金额（元）
  pointsGranted: number     // 赠送积分
  payType: number           // 1微信, 2支付宝
  purpose: number           // 1积分充值, 2会员购买
  memberLevel?: number      // 会员等级：1月度, 2季度, 3年度
}

/** 创建订单响应 */
export interface PaymentOrderResponse {
  orderId: string           // 雪花算法订单号
  payUrl?: string           // 支付宝支付URL（如后端返回）
}

/** 订单状态查询返回 */
export interface PaymentStatusVO {
  orderId: string
  status: 'pending' | 'paid' | 'expired' | 'cancelled'
  amount?: number
  paidAt?: string
}

// ==================== API 方法 ====================

/**
 * 1. 创建支付订单
 *
 * POST /member/pay/order
 * Content-Type: application/json
 * 
 * 后端接收 @RequestBody PaymentOrder，创建订单后：
 * - 返回 HTML：直接在新窗口渲染跳转支付宝
 * - 返回 JSON：包含 payUrl，前端 window.open 跳转
 */
export const createPaymentService = async (data: PaymentOrderRequest): Promise<PaymentOrderResponse> => {
  if (ENABLE_MOCK) {
    const mockOrderId = Date.now() * 10000 + Math.floor(Math.random() * 10000)
    localStorage.setItem('currentPayOrderId', String(mockOrderId))
    return { orderId: String(mockOrderId) }
  }

  // 使用配置好的 axios 实例，自动带上 Token 等拦截器配置
  // 后端可能返回 HTML 或 JSON，使用 responseType: 'text' 来统一处理
  const response = await request.post('/member/pay/order', data, {
    responseType: 'text',
    transformResponse: [(data) => data] // 阻止 axios 自动解析 JSON
  })

  const content = response.data as string

  // 情况1：后端返回 HTML（包含支付宝表单，直接渲染跳转）
  if (content.trim().startsWith('<!DOCTYPE') || content.trim().startsWith('<html')) {
    // 提取订单号（从 HTML 中的 out_trade_no）
    const orderIdMatch = content.match(/out_trade_no['"]\s*[:=]\s*['"]([^'"]+)/)
    const orderId = orderIdMatch?.[1] ?? ''

    if (orderId) {
      localStorage.setItem('currentPayOrderId', orderId)
    }

    // 在新窗口渲染 HTML
    const payWindow = window.open('', '_blank', 'width=1200,height=800,menubar=no,toolbar=no')
    if (payWindow) {
      payWindow.document.write(content)
      payWindow.document.close()
    }

    return { orderId }
  }

  // 情况2：后端返回 JSON（包含 orderId 和 payUrl）
  try {
    const result = JSON.parse(content)
    if (result.code !== 0 && result.code !== 200) {
      throw new Error(result.msg || '创建支付订单失败')
    }

    const orderId = result.data?.orderId || result.data?.id || result.data?.outTradeNo
    const payUrl = result.data?.payUrl || result.data?.qrCode

    if (orderId) {
      localStorage.setItem('currentPayOrderId', String(orderId))
    }

    if (payUrl) {
      window.open(payUrl, '_blank', 'width=1200,height=800,menubar=no,toolbar=no')
    }

    return { orderId: String(orderId), payUrl }
  } catch {
    throw new Error('解析支付响应失败')
  }
}

/**
 * 2. 构建支付宝支付跳转 URL
 * GET /member/pay/{orderNumber}
 * 后端根据订单号查询，返回 HTML 跳转支付宝
 */
export const buildAlipayPagePayUrl = (orderNo: string | number): string => {
  if (ENABLE_MOCK) {
    console.log('[Mock] 构建支付URL:', orderNo)
    return `https://mock.alipay.com/pay?orderNo=${orderNo}`
  }

  const serverURL = import.meta.env.VITE_SERVER || 'http://localhost:8080'
  return `${serverURL}/member/pay/${orderNo}`
}

/**
 * 3. 根据订单号重新支付（重试用）
 * 在新窗口打开支付页面
 */
export const payByOrderNo = (orderNo: string | number): void => {
  if (ENABLE_MOCK) {
    console.log('[Mock] 重新支付:', orderNo)
    return
  }

  const serverURL = import.meta.env.VITE_SERVER || 'http://localhost:8080'
  const payUrl = `${serverURL}/member/pay/${orderNo}`

  window.open(payUrl, '_blank', 'width=1200,height=800,menubar=no,toolbar=no')
}

/**
 * 3. 查询订单支付状态（轮询用）
 *
 * GET /member/order/status/{orderNo}
 */
export const queryPaymentStatusService = (orderNo: string) => {
  if (ENABLE_MOCK) {
    return Promise.resolve({
      data: {
        code: 0,
        msg: '查询成功',
        data: {
          orderId: orderNo,
          status: 'pending',
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

/**
 * 获取当前支付订单号
 */
export const getCurrentPayOrderId = (): string | null => {
  return localStorage.getItem('currentPayOrderId')
}

/**
 * 清除当前支付订单号
 */
export const clearCurrentPayOrderId = (): void => {
  localStorage.removeItem('currentPayOrderId')
}

// ==================== 后端接口说明 ====================

/**
 * 后端 PayController 接口：
 * 
 * 1. POST /member/pay/order
 *    - 接收：@RequestBody PaymentOrder (JSON)
 *    - 功能：创建订单 + 调用支付宝生成支付表单
 *    - 返回：HTML 表单（自动跳转）或 JSON { orderId, payUrl }
 * 
 * 2. GET /member/pay/{orderNumber}
 *    - 接收：@PathVariable Long orderNumber
 *    - 功能：根据订单号重新发起支付
 *    - 返回：HTML 表单（自动跳转）
 * 
 * 3. POST /member/notify
 *    - 接收：支付宝异步回调参数
 *    - 功能：验签 + 更新订单状态 + 加积分
 *    - 返回："success" 或 "fail"
 */
