import type { AxiosResponse } from 'axios'
import type { Result } from '@/types/type'
import type {
  PaymentCreateRequest,
  PaymentCreateData,
  PaymentStatusData,
  PaymentQRCodeData
} from '@/api/payment'

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const paymentStore = new Map<string, PaymentStatusData>()

function wrapAsAxiosResponse<T>(data: T, status = 200): AxiosResponse<T> {
  return {
    data,
    status,
    statusText: 'OK',
    headers: {},
    config: {} as any
  }
}

function generateOrderId(): string {
  const timestamp = Date.now().toString(36).toUpperCase()
  const random = Math.random().toString(36).substring(2, 6).toUpperCase()
  return `ORD${timestamp}${random}`
}

function generateQRCodeBase64(): string {
  const canvas = typeof document !== 'undefined' ? document.createElement('canvas') : null
  if (!canvas) {
    return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
  }
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
  }

  canvas.width = 200
  canvas.height = 200

  ctx.fillStyle = '#FFFFFF'
  ctx.fillRect(0, 0, 200, 200)

  ctx.fillStyle = '#000000'
  const cellSize = 8
  const margin = 20
  const gridSize = 20

  for (let i = 0; i < gridSize; i++) {
    for (let j = 0; j < gridSize; j++) {
      if (Math.random() > 0.5) {
        ctx.fillRect(margin + i * cellSize, margin + j * cellSize, cellSize - 1, cellSize - 1)
      }
    }
  }

  ctx.strokeStyle = '#1677FF'
  ctx.lineWidth = 4
  ctx.strokeRect(10, 10, 180, 180)

  return canvas.toDataURL('image/png')
}

function getExpireTime(minutes = 5): string {
  const date = new Date(Date.now() + minutes * 60 * 1000)
  return date.toISOString()
}

export async function mockCreatePaymentApi(
  request: PaymentCreateRequest,
  delayMs = 600
): Promise<AxiosResponse<Result<PaymentCreateData>>> {
  await delay(delayMs)

  const orderId = generateOrderId()
  const expireTime = getExpireTime(5)

  const planMap: Record<string, { duration: number; unit: string }> = {
    monthly: { duration: 1, unit: '月' },
    quarterly: { duration: 3, unit: '季度' },
    yearly: { duration: 12, unit: '年' }
  }

  const plan = planMap[request.planType]
  const expireDate = new Date()
  if (request.planType === 'monthly') {
    expireDate.setMonth(expireDate.getMonth() + 1)
  } else if (request.planType === 'quarterly') {
    expireDate.setMonth(expireDate.getMonth() + 3)
  } else {
    expireDate.setFullYear(expireDate.getFullYear() + 1)
  }

  paymentStore.set(orderId, {
    orderId,
    status: 'pending',
    planType: request.planType,
    amount: request.amount,
    memberExpireAt: expireDate.toISOString()
  })

  const qrData = generateQRCodeBase64()

  return wrapAsAxiosResponse({
    code: 0,
    msg: '创建支付订单成功',
    data: {
      orderId,
      payUrl: `https://mock.alipay.com/pay/${orderId}`,
      qrCodeUrl: qrData,
      expireTime
    }
  })
}

export async function mockQueryPaymentStatusApi(
  orderId: string,
  delayMs = 300
): Promise<AxiosResponse<Result<PaymentStatusData>>> {
  await delay(delayMs)

  const payment = paymentStore.get(orderId)

  if (!payment) {
    return wrapAsAxiosResponse({
      code: 404,
      msg: '订单不存在',
      data: null as any
    })
  }

  if (payment.status === 'pending') {
    const shouldPay = Math.random() > 0.7
    if (shouldPay) {
      payment.status = 'paid'
      payment.paidAt = new Date().toISOString()
    }
  }

  return wrapAsAxiosResponse({
    code: 0,
    msg: '查询支付状态成功',
    data: payment
  })
}

export async function mockGetPaymentQRCodeApi(
  orderId: string,
  delayMs = 400
): Promise<AxiosResponse<Result<PaymentQRCodeData>>> {
  await delay(delayMs)

  const payment = paymentStore.get(orderId)

  if (!payment) {
    return wrapAsAxiosResponse({
      code: 404,
      msg: '订单不存在',
      data: null as any
    })
  }

  const qrData = generateQRCodeBase64()

  return wrapAsAxiosResponse({
    code: 0,
    msg: '获取支付二维码成功',
    data: {
      orderId,
      qrCodeBase64: qrData,
      expireTime: getExpireTime(5)
    }
  })
}

export function simulatePaymentSuccess(orderId: string): boolean {
  const payment = paymentStore.get(orderId)
  if (payment && payment.status === 'pending') {
    payment.status = 'paid'
    payment.paidAt = new Date().toISOString()
    return true
  }
  return false
}
