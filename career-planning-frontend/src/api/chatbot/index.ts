import request from '@/utils/request'
import type { AxiosProgressEvent } from 'axios'

/**
 * 聊天机器人流式请求参数接口
 * @property message - 用户输入的消息内容
 * @property conversationId - 对话ID，用于保持上下文连续性
 * @property files - 上传的文件列表（PDF/DOCX/图片等）
 * @property signal - AbortSignal，用于取消请求
 * @property autoExtractMemory - 是否自动提取记忆信息
 * @property showThinking - 是否显示AI思考过程
 * @property onChunk - 接收到数据块时的回调函数
 * @property onConversationId - 获取到对话ID时的回调函数
 */
export interface ChatbotStreamParams {
  message: string
  conversationId?: string
  files?: File[]
  signal?: AbortSignal
  autoExtractMemory?: boolean
  showThinking?: boolean
  onChunk?: (chunk: string) => void
  onConversationId?: (conversationId: string) => void
}

/**
 * 流数据解析结果接口
 * @property chunks - 解析出的内容块数组
 * @property done - 流是否已结束
 * @property errorMessage - 错误信息（如果有）
 * @property rest - 未处理的缓冲区剩余内容
 */
interface ParsedStreamBuffer {
  chunks: string[]
  done: boolean
  errorMessage: string
  rest: string
}

/**
 * 生成唯一的对话ID
 * 优先使用 crypto.randomUUID()，如果不支持则使用时间戳+随机数
 * @returns 生成的对话ID字符串
 */
function createConversationId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`
}

/**
 * 解析单个JSON对象载荷
 * 根据不同类型的payload返回对应的处理结果
 * @param payload - 解析后的JSON对象
 * @param chunks - 内容块数组，用于存储解析出的内容
 * @returns 包含done状态(是否完成)和errorMessage(错误信息)的对象
 */
function parsePayloadObject(
  payload: Record<string, unknown>,
  chunks: string[]
): { done: boolean; errorMessage: string } {
  let done = false
  let errorMessage = ''

  // 处理完成状态
  if (payload.status === 'completed') {
    done = true
    return { done, errorMessage }
  }

  // 处理错误状态
  if (payload.status === 'error') {
    errorMessage =
      typeof payload.message === 'string' ? payload.message : 'Stream response failed'
    return { done, errorMessage }
  }

  // 处理内容类型数据
  if (payload.type === 'content') {
    const content = typeof payload.content === 'string' ? payload.content : ''
    if (content) chunks.push(content)
    return { done, errorMessage }
  }

  // 处理错误类型数据
  if (payload.type === 'error') {
    errorMessage =
      typeof payload.message === 'string' ? payload.message : 'Stream response failed'
    return { done, errorMessage }
  }

  // 默认处理：如果有content字段则提取内容
  if (typeof payload.content === 'string' && payload.content) {
    chunks.push(payload.content)
  }

  return { done, errorMessage }
}

/**
 * 解析JSON对象流缓冲区
 * 从连续的JSON字符串中提取完整的JSON对象
 * 使用状态机方式处理嵌套的大括号
 * @param buffer - 待解析的字符串缓冲区
 * @returns 解析结果，包含chunks、done状态、错误信息和剩余未处理内容
 */
function parseJsonObjectBuffer(buffer: string): ParsedStreamBuffer {
  const chunks: string[] = []
  let done = false
  let errorMessage = ''

  // 状态机变量
  let depth = 0          // 大括号嵌套深度
  let inString = false   // 是否在字符串内
  let escaped = false    // 是否处于转义状态
  let start = -1         // 当前JSON对象的起始位置
  let lastConsumedIndex = 0  // 最后处理的位置

  for (let i = 0; i < buffer.length; i++) {
    const ch = buffer[i]

    // 字符串状态处理
    if (inString) {
      if (escaped) {
        escaped = false
        continue
      }
      if (ch === '\\') {
        escaped = true
        continue
      }
      if (ch === '"') {
        inString = false
      }
      continue
    }

    // 检测字符串开始
    if (ch === '"') {
      inString = true
      continue
    }

    // 检测对象开始
    if (ch === '{') {
      if (depth === 0) start = i
      depth++
      continue
    }

    // 检测对象结束
    if (ch === '}') {
      if (depth > 0) depth--

      // 找到一个完整的JSON对象
      if (depth === 0 && start !== -1) {
        const raw = buffer.slice(start, i + 1)
        lastConsumedIndex = i + 1
        start = -1

        try {
          const payload = JSON.parse(raw) as Record<string, unknown>
          const parsed = parsePayloadObject(payload, chunks)
          if (parsed.done) done = true
          if (parsed.errorMessage) errorMessage = parsed.errorMessage
        } catch {
          // 解析失败，保留rest等待后续更多数据
        }
      }
    }
  }

  return {
    chunks,
    done,
    errorMessage,
    rest: buffer.slice(lastConsumedIndex),
  }
}

/**
 * 解析SSE（Server-Sent Events）格式数据
 * SSE格式：每个事件以"data:"开头，事件之间用两个换行符分隔
 * @param buffer - 待解析的SSE数据字符串
 * @returns 解析结果
 */
function parseSSEBuffer(buffer: string): ParsedStreamBuffer {
  const normalized = buffer.replace(/\r/g, '')
  const rawEvents = normalized.split('\n\n')

  // 如果没有完整事件，全部作为剩余内容返回
  if (rawEvents.length === 0 || (rawEvents.length === 1 && !rawEvents[0])) {
    return { chunks: [], done: false, errorMessage: '', rest: buffer }
  }

  // 最后一个可能是不完整的，保留到rest
  const completeEvents = rawEvents.slice(0, -1)
  const tail = rawEvents[rawEvents.length - 1] || ''

  const chunks: string[] = []
  let done = false
  let errorMessage = ''

  completeEvents.forEach((eventBlock) => {
    const trimmedBlock = eventBlock.trim()
    if (!trimmedBlock) return

    // 提取所有data:开头的行
    const dataLines = eventBlock
      .split('\n')
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(5).trimStart())

    if (!dataLines.length) {
      return
    }

    const data = dataLines.join('\n').trim()
    if (!data) return

    // 检测流结束标记
    if (data === '[DONE]') {
      done = true
      return
    }

    // 检测错误标记
    if (data.startsWith('[ERROR]')) {
      errorMessage = data.replace('[ERROR]', '').trim() || 'Stream response failed'
      return
    }

    // JSON对象数据，使用parseJsonObjectBuffer解析
    if (data.startsWith('{')) {
      const parsed = parseJsonObjectBuffer(data)
      chunks.push(...parsed.chunks)
      if (parsed.done) done = true
      if (parsed.errorMessage) errorMessage = parsed.errorMessage
      return
    }

    // 普通文本数据直接添加
    chunks.push(data)
  })

  return {
    chunks,
    done,
    errorMessage,
    rest: tail,
  }
}

/**
 * 自动检测并解析流数据缓冲区
 * 根据内容特征判断是SSE格式还是普通JSON对象流
 * @param buffer - 待解析的数据缓冲区
 * @returns 解析结果
 */
function parseStreamBuffer(buffer: string): ParsedStreamBuffer {
  const normalized = buffer.replace(/\r/g, '')
  // 检测SSE特征：包含data:/event:/id:/retry:等关键字
  const looksLikeSSE = /(^|\n)(data:|event:|id:|retry:)/.test(normalized)

  if (looksLikeSSE) {
    return parseSSEBuffer(normalized)
  }

  return parseJsonObjectBuffer(normalized)
}

/**
 * 从Axios进度事件中获取响应文本
 * 支持从XMLHttpRequest对象或event.target中获取
 * @param progressEvent - Axios进度事件
 * @returns 响应文本内容
 */
function getResponseText(progressEvent: AxiosProgressEvent): string {
  const event = progressEvent.event as ProgressEvent | undefined
  const xhr = event?.target as XMLHttpRequest | undefined

  if (xhr?.responseText) {
    return xhr.responseText
  }

  const anyEvent = progressEvent as unknown as { target?: { responseText?: string } }
  return anyEvent.target?.responseText ?? ''
}

// 最大缓冲区大小限制：5MB
const MAX_BUFFER_SIZE = 5 * 1024 * 1024

/**
 * 发送流式聊天消息
 * 支持文本消息和文件上传，使用流式响应实时获取AI回复
 * @param params - 请求参数，包含消息、文件、回调等
 * @returns Promise，resolve时返回完整的响应对象
 * @throws 网络错误或服务器错误时会抛出异常
 */
export async function streamChatbotMessage({
  message,
  conversationId,
  files = [],
  signal,
  autoExtractMemory,
  showThinking,
  onChunk,
  onConversationId,
}: ChatbotStreamParams): Promise<unknown> {
  // 处理并限制消息长度（最大10000字符）
  const sanitizedMessage = (message || 'Please analyze the uploaded file').slice(0, 10000)
  // 生成或复用对话ID
  const finalConversationId = conversationId || createConversationId()

  // 构建FormData请求体
  const formData = new FormData()
  formData.append('message', sanitizedMessage)
  formData.append('conversationId', finalConversationId)

  // 添加可选参数
  if (typeof autoExtractMemory === 'boolean') {
    formData.append('auto_extract_memory', String(autoExtractMemory))
  }

  if (typeof showThinking === 'boolean') {
    formData.append('show_thinking', String(showThinking))
  }

  // 文件大小限制：单个文件最大10MB，总共最大50MB
  const MAX_FILE_SIZE = 10 * 1024 * 1024
  const MAX_TOTAL_SIZE = 50 * 1024 * 1024
  let totalSize = 0

  // 处理文件上传
  files.forEach((file) => {
    if (file.size > MAX_FILE_SIZE) {
      console.warn(`File ${file.name} exceeds maximum size limit`)
      return
    }
    totalSize += file.size
    if (totalSize <= MAX_TOTAL_SIZE) {
      formData.append('files', file)
    } else {
      console.warn(`Total upload size exceeds limit, skipping ${file.name}`)
    }
  })

  // 回调通知对话ID
  try {
    onConversationId?.(finalConversationId)
  } catch (callbackError) {
    console.error('Error in onConversationId callback:', callbackError)
  }

  // 流处理状态变量
  let processedLength = 0    // 已处理的数据长度
  let streamBuffer = ''      // 数据缓冲区
  let streamDone = false     // 流是否已结束
  let errorOccurred = false  // 是否发生错误

  try {
    // 发送请求，根据是否有文件选择不同的API端点
    const response = await request.request<string>({
      url: files.length > 0 ? '/chat/stream/message-and-files' : '/chat/stream/message',
      method: 'POST',
      data: formData,
      signal,
      responseType: 'text',
      // 下载进度回调，用于处理流式响应
      onDownloadProgress: (progressEvent) => {
        if (streamDone || errorOccurred) return

        try {
          const responseText = getResponseText(progressEvent)
          if (!responseText || responseText.length <= processedLength) return

          // 提取新增的数据
          const incrementalText = responseText.slice(processedLength)
          processedLength = responseText.length

          // 打印收到的原始数据
          console.log('[Chatbot] 收到原始数据:', incrementalText)

          // 检查缓冲区大小限制
          if (streamBuffer.length + incrementalText.length > MAX_BUFFER_SIZE) {
            errorOccurred = true
            throw new Error('Response too large')
          }

          // 累积到缓冲区并解析
          streamBuffer += incrementalText
          const parsed = parseStreamBuffer(streamBuffer)
          streamBuffer = parsed.rest

          // 处理错误
          if (parsed.errorMessage) {
            console.error('[Chatbot] 解析错误:', parsed.errorMessage)
            errorOccurred = true
            throw new Error(parsed.errorMessage)
          }

          // 回调通知每个内容块
          parsed.chunks.forEach((chunk) => {
            console.log('[Chatbot] 解析出的内容块:', chunk)
            try {
              onChunk?.(chunk)
            } catch (callbackError) {
              console.error('Error in onChunk callback:', callbackError)
            }
          })

          // 检测流结束
          if (parsed.done) {
            console.log('[Chatbot] 流已结束')
            streamDone = true
          }

          // 打印错误信息
          if (parsed.errorMessage) {
            console.error('[Chatbot] 解析错误:', parsed.errorMessage)
          }
        } catch (processingError) {
          errorOccurred = true
          throw processingError
        }
      },
    })

    // 处理剩余未解析的缓冲区内容
    if (!errorOccurred && streamBuffer.trim()) {
      console.log('[Chatbot] 处理剩余缓冲区:', streamBuffer)
      const parsed = parseStreamBuffer(streamBuffer)

      if (parsed.errorMessage) {
        console.error('[Chatbot] 最终解析错误:', parsed.errorMessage)
        throw new Error(parsed.errorMessage)
      }

      parsed.chunks.forEach((chunk) => {
        console.log('[Chatbot] 最终内容块:', chunk)
        try {
          onChunk?.(chunk)
        } catch (callbackError) {
          console.error('Error in onChunk callback:', callbackError)
        }
      })
    }

    console.log('[Chatbot] 请求完成')

    return response
  } catch (error) {
    // 错误处理：区分取消请求、网络错误和其他错误
    console.error('[Chatbot] 请求错误:', error)
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Request was cancelled')
      }
      if (error.message.includes('Network Error')) {
        throw new Error('Network connection failed. Please check your internet connection.')
      }
    }
    throw error
  }
}
