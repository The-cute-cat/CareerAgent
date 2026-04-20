import request from '@/utils/request'
import type { AxiosProgressEvent } from 'axios'
import { getKnowledgeMockData } from '@/mock/mockdata/JobKnowledge_mockdata'

const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'

/**
 * 知识图谱流式请求参数
 */
export interface KnowledgeStreamParams {
  /** 当前知识点ID（节点ID） */
  currentNode: string
  /** 目标岗位 ID */
  jobId: string | number
  /** 图谱关系（可选） */
  graphContext?: string
  /** 行业数据（可选） */
  industryData?: string
  /** AbortSignal，用于取消请求 */
  signal?: AbortSignal
  /** 接收到内容块时的回调 */
  onChunk?: (chunk: string) => void
  /** 流结束时的回调 */
  onDone?: () => void
  /** 发生错误时的回调 */
  onError?: (error: string) => void
}

/**
 * 解析单个 JSON 对象载荷
 */
function parsePayloadObject(
  payload: Record<string, unknown>,
  chunks: string[]
): { done: boolean; errorMessage: string } {
  // 处理完成状态
  if (payload.status === 'completed') {
    return { done: true, errorMessage: '' }
  }

  // 处理错误状态
  if (payload.type === 'error') {
    const errorMessage =
      typeof payload.content === 'string' ? payload.content : 'Stream response failed'
    return { done: false, errorMessage }
  }

  // 处理内容类型数据
  if (payload.type === 'content') {
    const content = typeof payload.content === 'string' ? payload.content : ''
    if (content) chunks.push(content)
    return { done: false, errorMessage: '' }
  }

  // 默认处理：如果有 content 字段则提取内容
  if (typeof payload.content === 'string' && payload.content) {
    chunks.push(payload.content)
  }

  return { done: false, errorMessage: '' }
}

/**
 * 解析 JSON 对象流缓冲区（状态机方式）
 */
function parseJsonObjectBuffer(buffer: string): {
  chunks: string[]
  done: boolean
  errorMessage: string
  rest: string
} {
  const chunks: string[] = []
  let done = false
  let errorMessage = ''

  let depth = 0
  let inString = false
  let escaped = false
  let start = -1
  let lastConsumedIndex = 0

  for (let i = 0; i < buffer.length; i++) {
    const ch = buffer[i]

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

    if (ch === '"') {
      inString = true
      continue
    }

    if (ch === '{') {
      if (depth === 0) start = i
      depth++
      continue
    }

    if (ch === '}') {
      if (depth > 0) depth--

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
          // 解析失败，保留 rest 等待后续更多数据
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
 * 解析 SSE 格式数据
 */
function parseSSEBuffer(buffer: string): {
  chunks: string[]
  done: boolean
  errorMessage: string
  rest: string
} {
  const normalized = buffer.replace(/\r/g, '')
  const rawEvents = normalized.split('\n\n')

  if (rawEvents.length === 0 || (rawEvents.length === 1 && !rawEvents[0])) {
    return { chunks: [], done: false, errorMessage: '', rest: buffer }
  }

  const completeEvents = rawEvents.slice(0, -1)
  const tail = rawEvents[rawEvents.length - 1] || ''

  const chunks: string[] = []
  let done = false
  let errorMessage = ''

  completeEvents.forEach((eventBlock) => {
    const trimmedBlock = eventBlock.trim()
    if (!trimmedBlock) return

    // 提取所有 data: 开头的行
    const dataLines = eventBlock
      .split('\n')
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(5).trimStart())

    if (!dataLines.length) return

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

    // 检测完成事件
    if (data.includes('"status":"completed"') || data.includes('"status": "completed"')) {
      done = true
      return
    }

    // JSON 对象数据
    if (data.startsWith('{')) {
      const parsed = parseJsonObjectBuffer(data)
      chunks.push(...parsed.chunks)
      if (parsed.done) done = true
      if (parsed.errorMessage) errorMessage = parsed.errorMessage
      return
    }

    // 普通文本数据
    chunks.push(data)
  })

  return { chunks, done, errorMessage, rest: tail }
}

/**
 * 自动检测并解析流数据
 */
function parseStreamBuffer(buffer: string): {
  chunks: string[]
  done: boolean
  errorMessage: string
  rest: string
} {
  const normalized = buffer.replace(/\r/g, '')
  const looksLikeSSE = /(^|\n)(data:|event:|id:|retry:)/.test(normalized)

  if (looksLikeSSE) {
    return parseSSEBuffer(normalized)
  }

  return parseJsonObjectBuffer(normalized)
}

/**
 * 从 Axios 进度事件中获取响应文本
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

/**
 * 通用知识图谱流式请求
 * @param endpoint - API 端点路径
 * @param params - 请求参数
 */
async function streamKnowledgeRequest(endpoint: string, params: KnowledgeStreamParams): Promise<unknown> {
  const { currentNode, jobId, graphContext, industryData, signal, onChunk, onDone, onError } = params

  // 构建 FormData（后端 @RequestParam 接收）
  const formData = new FormData()
  formData.append('currentNode', currentNode)
  formData.append('jobId', String(jobId))
  if (graphContext) formData.append('graphContext', graphContext)
  if (industryData) formData.append('industryData', industryData)

  let processedLength = 0
  let streamBuffer = ''
  let streamDone = false
  let errorOccurred = false

  try {
    const response = await request.request<string>({
      url: endpoint,
      method: 'POST',
      data: formData,
      signal,
      responseType: 'text',
      onDownloadProgress: (progressEvent) => {
        if (streamDone || errorOccurred) return

        try {
          const responseText = getResponseText(progressEvent)
          if (!responseText || responseText.length <= processedLength) return

          const incrementalText = responseText.slice(processedLength)
          processedLength = responseText.length

          streamBuffer += incrementalText
          const parsed = parseStreamBuffer(streamBuffer)
          streamBuffer = parsed.rest

          if (parsed.errorMessage) {
            errorOccurred = true
            onError?.(parsed.errorMessage)
            return
          }

          parsed.chunks.forEach((chunk) => {
            onChunk?.(chunk)
          })

          if (parsed.done) {
            streamDone = true
            onDone?.()
          }
        } catch (processingError) {
          errorOccurred = true
          onError?.(processingError instanceof Error ? processingError.message : 'Unknown error')
        }
      },
    })

    // 处理剩余未解析的缓冲区内容
    if (!errorOccurred && streamBuffer.trim()) {
      const parsed = parseStreamBuffer(streamBuffer)
      if (parsed.errorMessage) {
        onError?.(parsed.errorMessage)
      } else {
        parsed.chunks.forEach((chunk) => {
          onChunk?.(chunk)
        })
        if (parsed.done && !streamDone) {
          onDone?.()
        }
      }
    }

    return response
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        return null
      }
      onError?.(error.message)
    }
    throw error
  }
}

/**
 * Mock 流式响应生成器
 * 模拟 SSE 流式返回数据
 */
function mockStreamResponse(
  content: string,
  onChunk?: (chunk: string) => void,
  onDone?: () => void
): Promise<void> {
  return new Promise((resolve) => {
    const chunks = content.split('')
    let index = 0
    
    const interval = setInterval(() => {
      if (index < chunks.length) {
        // 每次发送 3-8 个字符，模拟打字效果
        const batchSize = Math.floor(Math.random() * 6) + 3
        const batch = chunks.slice(index, index + batchSize).join('')
        onChunk?.(batch)
        index += batchSize
      } else {
        clearInterval(interval)
        onDone?.()
        resolve()
      }
    }, 30) // 30ms 间隔，模拟真实流式体验
  })
}

/**
 * 流式分析知识点对岗位的影响（SSE）
 * 用于"岗位影响"标签页
 */
export function streamAnalyzeKnowledge(params: KnowledgeStreamParams): Promise<unknown> {
  const { currentNode, jobId, onChunk, onDone } = params
  
  // Mock 模式：返回预定义数据
  if (ENABLE_MOCK) {
    // 从 currentNode 中提取 nodeId（格式：roleId_nodeId）
    const roleId = String(jobId)
    const mockData = getKnowledgeMockData(roleId, currentNode)
    
    if (mockData?.analyze) {
      return mockStreamResponse(mockData.analyze, onChunk, onDone)
        .then(() => null)
    }
    
    // 如果没有找到 Mock 数据，返回默认内容
    const defaultContent = `## ${currentNode} 对岗位的影响\n\n### 🔥 岗位匹配度：重要\n\n该知识点是目标岗位的核心技能之一，掌握程度直接影响：\n\n1. **面试表现** - 相关知识点是技术面试的常考内容\n2. **工作效率** - 熟练掌握可显著提升开发效率\n3. **职业发展** - 是晋升高级工程师的必备技能\n\n### 💡 学习建议\n\n建议结合实际项目进行学习，通过实践加深理解。可参考官方文档和行业最佳实践。`
    
    return mockStreamResponse(defaultContent, onChunk, onDone).then(() => null)
  }
  
  return streamKnowledgeRequest('/knowledge-graph/analyze/stream', params)
}

/**
 * 流式解释知识点内容（SSE）
 * 用于"知识精讲"标签页
 */
export function streamExplainKnowledge(params: KnowledgeStreamParams): Promise<unknown> {
  const { currentNode, jobId, onChunk, onDone } = params
  
  // Mock 模式：返回预定义数据
  if (ENABLE_MOCK) {
    const roleId = String(jobId)
    const mockData = getKnowledgeMockData(roleId, currentNode)
    
    if (mockData?.explain) {
      return mockStreamResponse(mockData.explain, onChunk, onDone)
        .then(() => null)
    }
    
    // 如果没有找到 Mock 数据，返回默认内容
    const defaultContent = `## ${currentNode} 知识精讲\n\n### 一、核心概念\n\n该知识点是领域内的重要组成部分，需要理解其基本原理和应用场景。\n\n### 二、深入理解\n\n建议从以下几个方面深入学习：\n1. 理论基础 - 掌握核心概念和原理\n2. 实践应用 - 通过项目实战加深理解\n3. 最佳实践 - 学习行业标准和规范\n\n### 三、学习资源\n\n- 官方文档\n- 在线教程\n- 实战项目\n\n持续学习和实践是掌握该知识点的关键。`
    
    return mockStreamResponse(defaultContent, onChunk, onDone).then(() => null)
  }
  
  return streamKnowledgeRequest('/knowledge-graph/explain/stream', params)
}
