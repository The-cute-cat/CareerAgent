import { onBeforeUnmount, ref } from 'vue'
import { VirtualHumanConfig, type VirtualHumanVoice } from '@/config/virtual-human-config'

interface SDKModule {
  default?: new (props?: Record<string, unknown>) => any
  SDKEvents?: Record<string, string>
}

export interface VirtualHumanStatus {
  isLoading: boolean
  isConnected: boolean
  isSpeaking: boolean
  error: string | null
}

export interface VirtualHumanConnectOptions {
  avatarId?: string
  vcn?: VirtualHumanVoice | string
}

const loadAvatarSDK = async () => {
  const baseUrl = import.meta.env.BASE_URL.endsWith('/')
    ? import.meta.env.BASE_URL
    : `${import.meta.env.BASE_URL}/`
  const sdkPath = `${baseUrl}avatar-sdk-web_3.1.2.1002/index.js`
  const sdkUrl = new URL(sdkPath, window.location.origin).href
  const sdkModule = await import(/* @vite-ignore */ sdkUrl) as SDKModule
  return {
    AvatarPlatformSDK: sdkModule.default,
    SDKEvents: sdkModule.SDKEvents
  }
}

const getApiSecret = () => {
  if (VirtualHumanConfig.API_SECRET_ENCODING !== 'base64') {
    return VirtualHumanConfig.API_SECRET
  }

  try {
    return window.atob(VirtualHumanConfig.API_SECRET)
  } catch {
    return VirtualHumanConfig.API_SECRET
  }
}

// 生成签名 URL（使用预签名方式连接）
const generateSignedUrl = async (): Promise<string> => {
  const apiKey = VirtualHumanConfig.API_KEY
  const apiSecret = getApiSecret()
  const host = 'avatar.cn-huadong-1.xf-yun.com'
  const date = new Date().toUTCString()
  const requestLine = 'GET /v1/interact HTTP/1.1'

  const signatureOrigin = `host: ${host}\ndate: ${date}\n${requestLine}`
  const encoder = new TextEncoder()
  const key = encoder.encode(apiSecret)
  const message = encoder.encode(signatureOrigin)

  const cryptoKey = await crypto.subtle.importKey('raw', key, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])
  const signature = await crypto.subtle.sign('HMAC', cryptoKey, message)
  const signatureBase64 = btoa(String.fromCharCode(...new Uint8Array(signature)))
  const authorization = btoa(`api_key="${apiKey}", algorithm="hmac-sha256", headers="host date request-line", signature="${signatureBase64}"`)

  return `${VirtualHumanConfig.SERVER_URL}?authorization=${encodeURIComponent(authorization)}&date=${encodeURIComponent(date)}&host=${host}`
}

const getConnectErrorMessage = (error: any) => {
  const message = error?.message || String(error || '')
  if (message && message !== '[object Event]') return message

  return '虚拟人连接失败：请检查 APISecret 是否为原始值、AppID/APIKey/SceneID 是否匹配，浏览器时间是否与北京时间一致，并确认当前网络允许访问讯飞 wss 服务。'
}

// 备用签名算法（讯飞不同服务可能有不同的签名格式）
const generateSignedUrlV2 = async (): Promise<string> => {
  const apiKey = VirtualHumanConfig.API_KEY
  const apiSecret = getApiSecret()
  const host = 'avatar.cn-huadong-1.xf-yun.com'
  const date = new Date().toUTCString()
  
  // 尝试另一种格式：不包含 request-line
  const signatureOrigin = `host: ${host}\ndate: ${date}`
  const encoder = new TextEncoder()
  const key = encoder.encode(apiSecret)
  const message = encoder.encode(signatureOrigin)

  const cryptoKey = await crypto.subtle.importKey('raw', key, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])
  const signature = await crypto.subtle.sign('HMAC', cryptoKey, message)
  const signatureBase64 = btoa(String.fromCharCode(...new Uint8Array(signature)))
  const authorization = btoa(`api_key="${apiKey}", algorithm="hmac-sha256", headers="host date", signature="${signatureBase64}"`)

  return `${VirtualHumanConfig.SERVER_URL}?authorization=${encodeURIComponent(authorization)}&date=${encodeURIComponent(date)}&host=${host}`
}

// 测试不同签名格式的 WebSocket 连接
export const testSignatureFormat = async (): Promise<WebSocketTestResult[]> => {
  const results: WebSocketTestResult[] = []
  
  // 格式 1：带 request-line（当前实现）
  console.log('【签名测试1】带 request-line 格式...')
  try {
    const url1 = await generateSignedUrl()
    const result1 = await testWebSocketWithUrl(url1, '带 request-line')
    results.push(result1)
  } catch (e: any) {
    results.push({ test: '签名格式1 (带 request-line)', status: 'error', message: e.message })
  }
  
  // 格式 2：不带 request-line
  console.log('【签名测试2】不带 request-line 格式...')
  try {
    const url2 = await generateSignedUrlV2()
    const result2 = await testWebSocketWithUrl(url2, '不带 request-line')
    results.push(result2)
  } catch (e: any) {
    results.push({ test: '签名格式2 (不带 request-line)', status: 'error', message: e.message })
  }
  
  return results
}

const testWebSocketWithUrl = (url: string, formatName: string): Promise<WebSocketTestResult> => {
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      resolve({
        test: `签名格式测试 (${formatName})`,
        status: 'error',
        message: '连接超时'
      })
    }, 5000)
    
    try {
      const ws = new WebSocket(url)
      
      ws.onopen = () => {
        clearTimeout(timeout)
        ws.close()
        resolve({
          test: `签名格式测试 (${formatName})`,
          status: 'success',
          message: `✅ ${formatName} 格式连接成功！`,
          details: '请使用此格式的签名算法'
        })
      }
      
      ws.onerror = () => {
        clearTimeout(timeout)
        resolve({
          test: `签名格式测试 (${formatName})`,
          status: 'error',
          message: `❌ ${formatName} 格式失败`
        })
      }
      
      ws.onclose = (e) => {
        clearTimeout(timeout)
        resolve({
          test: `签名格式测试 (${formatName})`,
          status: 'error',
          message: `❌ ${formatName} 格式关闭 (code: ${e.code})`
        })
      }
    } catch (e: any) {
      clearTimeout(timeout)
      resolve({
        test: `签名格式测试 (${formatName})`,
        status: 'error',
        message: `❌ ${formatName} 异常: ${e.message}`
      })
    }
  })
}

// ==================== WebSocket 诊断测试工具 ====================

export interface WebSocketTestResult {
  test: string
  status: 'success' | 'error' | 'pending'
  message: string
  details?: any
}

// 测试 1: 基础 WebSocket 连接（不带鉴权，仅测试网络）
export const testBasicWebSocket = (): Promise<WebSocketTestResult> => {
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      resolve({
        test: '基础 WebSocket 连接测试',
        status: 'error',
        message: '连接超时（5秒），网络可能阻止 WebSocket'
      })
    }, 5000)

    try {
      const ws = new WebSocket('wss://avatar.cn-huadong-1.xf-yun.com/v1/interact')
      
      ws.onopen = () => {
        clearTimeout(timeout)
        ws.close()
        resolve({
          test: '基础 WebSocket 连接测试',
          status: 'success',
          message: '✅ 网络层 WebSocket 连接正常（鉴权前的 TCP/TLS 层已连通）',
          details: '可以建立 WebSocket 连接，问题可能在鉴权参数'
        })
      }
      
      ws.onerror = (error) => {
        clearTimeout(timeout)
        resolve({
          test: '基础 WebSocket 连接测试',
          status: 'error',
          message: '❌ WebSocket 连接失败，网络层被阻断',
          details: '可能是防火墙、公司网络策略或 DNS 问题阻止了 wss 连接'
        })
      }
      
      ws.onclose = (event) => {
        clearTimeout(timeout)
        if (event.code === 1006) {
          resolve({
            test: '基础 WebSocket 连接测试',
            status: 'error',
            message: `❌ 连接异常关闭 (code: ${event.code})`,
            details: '1006 表示连接未能正常建立就被关闭，通常是网络阻止或服务器拒绝'
          })
        }
      }
    } catch (error: any) {
      clearTimeout(timeout)
      resolve({
        test: '基础 WebSocket 连接测试',
        status: 'error',
        message: `❌ WebSocket 创建失败: ${error.message}`,
        details: error
      })
    }
  })
}

// 测试 2: 检查 API Secret 解码
export const testApiSecret = (): WebSocketTestResult => {
  const encoded = VirtualHumanConfig.API_SECRET
  const encoding = VirtualHumanConfig.API_SECRET_ENCODING
  
  if (encoding === 'plain') {
    return {
      test: 'API Secret 配置检查',
      status: 'success',
      message: '配置为 plain 模式，使用原始值',
      details: { length: encoded.length, preview: encoded.substring(0, 8) + '...' }
    }
  }
  
  try {
    const decoded = window.atob(encoded)
    return {
      test: 'API Secret 配置检查',
      status: 'success',
      message: '✅ Base64 解码成功',
      details: { 
        encodedLength: encoded.length, 
        decodedLength: decoded.length,
        decodedPreview: decoded.substring(0, 16) + '...',
        suggestion: '如果连接仍失败，尝试将 API_SECRET_ENCODING 改为 "plain"，API_SECRET 改为原始值'
      }
    }
  } catch (error) {
    return {
      test: 'API Secret 配置检查',
      status: 'error',
      message: '❌ Base64 解码失败，API_SECRET 可能不是有效的 Base64',
      details: { encoding, error }
    }
  }
}

// 测试 3: 生成签名 URL 并验证格式
export const testSignedUrlGeneration = async (): Promise<WebSocketTestResult> => {
  try {
    const url = await generateSignedUrl()
    const urlObj = new URL(url)
    const auth = urlObj.searchParams.get('authorization')
    
    // 解析 authorization
    let authObj: any = null
    try {
      authObj = JSON.parse(atob(auth || ''))
    } catch {
      // 可能是逗号分隔格式
      const authStr = atob(auth || '')
      authObj = { raw: authStr.substring(0, 100) + '...' }
    }
    
    // 检查日期是否接近当前时间
    const dateStr = urlObj.searchParams.get('date')
    const dateDiff = dateStr ? Math.abs(new Date().getTime() - new Date(dateStr).getTime()) : Infinity
    
    return {
      test: '签名 URL 生成测试',
      status: 'success',
      message: '✅ 签名 URL 生成成功',
      details: {
        urlLength: url.length,
        hasAuthorization: !!auth,
        hasDate: !!dateStr,
        hasHost: !!urlObj.searchParams.get('host'),
        dateDiffMinutes: Math.round(dateDiff / 60000),
        authorizationPreview: authObj,
        suggestion: dateDiff > 300000 ? '警告：系统时间与服务器时间可能相差超过5分钟，会导致鉴权失败' : '时间戳正常'
      }
    }
  } catch (error: any) {
    return {
      test: '签名 URL 生成测试',
      status: 'error',
      message: `❌ 签名生成失败: ${error.message}`,
      details: error
    }
  }
}

// 测试 4: 带鉴权的完整 WebSocket 测试
export const testAuthenticatedWebSocket = async (): Promise<WebSocketTestResult> => {
  const signedUrl = await generateSignedUrl()
  
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      resolve({
        test: '带鉴权 WebSocket 连接测试',
        status: 'error',
        message: '连接超时（10秒），鉴权可能失败或网络延迟过高',
        details: '如果基础测试通过但此测试失败，说明是鉴权参数问题（APISecret、时间戳、签名格式）'
      })
    }, 10000)

    try {
      const ws = new WebSocket(signedUrl)
      
      ws.onopen = () => {
        clearTimeout(timeout)
        ws.close()
        resolve({
          test: '带鉴权 WebSocket 连接测试',
          status: 'success',
          message: '✅ 带鉴权连接成功！配置完全正确',
          details: '所有参数都正确，如果 SDK 仍失败，可能是 SDK 版本或初始化参数问题'
        })
      }
      
      ws.onerror = (error) => {
        clearTimeout(timeout)
        resolve({
          test: '带鉴权 WebSocket 连接测试',
          status: 'error',
          message: '❌ 鉴权失败',
          details: '请检查：1) API Secret 是否为原始值 2) 系统时间是否准确 3) SceneID 是否正确'
        })
      }
      
      ws.onclose = (event) => {
        clearTimeout(timeout)
        let reason = ''
        switch (event.code) {
          case 1000: reason = '正常关闭'; break
          case 1002: reason = '协议错误'; break
          case 1006: reason = '连接异常关闭（鉴权失败或网络问题）'; break
          case 1008: reason = '策略违规（鉴权失败）'; break
          case 1011: reason = '服务器错误'; break
          default: reason = `未知错误码: ${event.code}`
        }
        
        resolve({
          test: '带鉴权 WebSocket 连接测试',
          status: 'error',
          message: `❌ 连接关闭 (code: ${event.code}) - ${reason}`,
          details: { code: event.code, reason: event.reason }
        })
      }
    } catch (error: any) {
      clearTimeout(timeout)
      resolve({
        test: '带鉴权 WebSocket 连接测试',
        status: 'error',
        message: `❌ WebSocket 创建失败: ${error.message}`,
        details: error
      })
    }
  })
}

// 运行所有测试
export const runAllDiagnostics = async (onProgress?: (result: WebSocketTestResult) => void): Promise<WebSocketTestResult[]> => {
  const results: WebSocketTestResult[] = []
  
  // 测试 1: API Secret
  const secretResult = testApiSecret()
  results.push(secretResult)
  onProgress?.(secretResult)
  
  // 测试 2: 基础 WebSocket
  const basicResult = await testBasicWebSocket()
  results.push(basicResult)
  onProgress?.(basicResult)
  
  // 如果基础连接失败，跳过后续测试
  if (basicResult.status === 'error') {
    const skipResult: WebSocketTestResult = {
      test: '签名 URL 生成测试',
      status: 'error',
      message: '⏭️ 跳过：基础 WebSocket 连接失败'
    }
    results.push(skipResult)
    onProgress?.(skipResult)
    
    const skipResult2: WebSocketTestResult = {
      test: '带鉴权 WebSocket 连接测试',
      status: 'error',
      message: '⏭️ 跳过：基础 WebSocket 连接失败'
    }
    results.push(skipResult2)
    onProgress?.(skipResult2)
    
    return results
  }
  
  // 测试 3: 签名 URL
  const urlResult = await testSignedUrlGeneration()
  results.push(urlResult)
  onProgress?.(urlResult)
  
  // 测试 4: 带鉴权连接
  const authResult = await testAuthenticatedWebSocket()
  results.push(authResult)
  onProgress?.(authResult)
  
  return results
}

const browserTTS = (text: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (!('speechSynthesis' in window)) {
      reject(new Error('当前浏览器不支持语音合成'))
      return
    }

    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'zh-CN'
    utterance.rate = 1
    utterance.pitch = 1
    utterance.volume = 1
    utterance.onend = () => resolve()
    utterance.onerror = (event) => reject(event)

    window.speechSynthesis.speak(utterance)
  })
}

export function useVirtualHuman() {
  const containerRef = ref<HTMLDivElement | null>(null)
  const status = ref<VirtualHumanStatus>({
    isLoading: false,
    isConnected: false,
    isSpeaking: false,
    error: null
  })

  let platformInstance: any = null
  let playerInstance: any = null

  const connect = async (options?: VirtualHumanConnectOptions) => {
    if (status.value.isLoading || status.value.isConnected) return

    try {
      status.value.isLoading = true
      status.value.error = null

      const { AvatarPlatformSDK, SDKEvents } = await loadAvatarSDK()
      if (!AvatarPlatformSDK || !SDKEvents) {
        throw new Error('讯飞虚拟人 SDK 加载失败')
      }

      const avatarId = options?.avatarId || VirtualHumanConfig.DEFAULT_AVATAR_ID
      const vcn = options?.vcn || VirtualHumanConfig.DEFAULT_VCN

      platformInstance = new AvatarPlatformSDK({ useInlinePlayer: true, logLevel: 1 })

      // 使用预签名 URL 方式
      const signedUrl = await generateSignedUrl()
      platformInstance.setApiInfo({
        appId: VirtualHumanConfig.APP_ID,
        apiKey: VirtualHumanConfig.API_KEY,
        sceneId: VirtualHumanConfig.SCENE_ID,
        signedUrl: signedUrl  // 使用预签名 URL 替代 serverUrl + apiSecret
      })

      platformInstance.setGlobalParams({
        stream: {
          protocol: 'xrtc',
          alpha: 1
        },
        avatar: {
          avatar_id: avatarId,
          width: VirtualHumanConfig.RENDER_WIDTH,
          height: VirtualHumanConfig.RENDER_HEIGHT,
          scale: 1
        },
        tts: {
          vcn
        },
        avatar_dispatch: {
          enable_action_status: 1,
          content_analysis: 1
        },
        air: {
          air: 1,
          add_nonsemantic: 1
        }
      })

      platformInstance
        .on(SDKEvents.connected, () => {
          status.value.isConnected = true
          status.value.isLoading = false
        })
        .on(SDKEvents.disconnected, () => {
          status.value.isConnected = false
          status.value.isLoading = false
          status.value.isSpeaking = false
        })
        .on(SDKEvents.error, (error: any) => {
          status.value.error = error?.message || String(error)
          status.value.isLoading = false
          status.value.isSpeaking = false
        })
        .on(SDKEvents.frame_start, () => {
          status.value.isSpeaking = true
        })
        .on(SDKEvents.frame_stop, () => {
          status.value.isSpeaking = false
        })

      playerInstance = platformInstance.player || platformInstance.createPlayer?.()
      if (playerInstance && containerRef.value) {
        playerInstance.container = containerRef.value
        playerInstance.renderAlign = 'bottom'
      }

      await platformInstance.start({
        wrapper: containerRef.value || undefined
      })
    } catch (error: any) {
      status.value.error = getConnectErrorMessage(error)
      status.value.isLoading = false
      status.value.isConnected = false
      console.warn('[VirtualHuman] connect failed:', error)
    }
  }

  const speak = async (text: string) => {
    if (!text.trim()) return

    status.value.isSpeaking = true
    try {
      if (platformInstance?.writeText && status.value.isConnected) {
        await platformInstance.writeText(text, {})
        return
      }

      await browserTTS(text)
    } catch (error) {
      console.warn('[VirtualHuman] speak failed, fallback to browser TTS:', error)
      await browserTTS(text)
    } finally {
      status.value.isSpeaking = false
    }
  }

  const disconnect = () => {
    try {
      platformInstance?.stop?.()
      platformInstance?.destroy?.()
      playerInstance?.destroy?.()
    } catch (error) {
      console.warn('[VirtualHuman] disconnect failed:', error)
    } finally {
      platformInstance = null
      playerInstance = null
      status.value.isConnected = false
      status.value.isLoading = false
      status.value.isSpeaking = false
    }
  }

  const updateConfig = (config: VirtualHumanConnectOptions) => {
    const params: Record<string, unknown> = {}

    if (config.avatarId) {
      params.avatar = {
        avatar_id: config.avatarId,
        width: VirtualHumanConfig.RENDER_WIDTH,
        height: VirtualHumanConfig.RENDER_HEIGHT,
        scale: 1
      }
    }

    if (config.vcn) {
      params.tts = { vcn: config.vcn }
    }

    if (Object.keys(params).length > 0) {
      platformInstance?.setGlobalParams?.(params)
    }
  }

  onBeforeUnmount(disconnect)

  return {
    containerRef,
    status,
    connect,
    speak,
    disconnect,
    updateConfig
  }
}
