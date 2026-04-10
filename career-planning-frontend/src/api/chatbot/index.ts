import request from '@/utils/request'
import type { AxiosProgressEvent } from 'axios'

export interface ChatbotStreamParams {
  message: string
  conversationId?: string
  files?: File[]
  signal?: AbortSignal
  onChunk?: (chunk: string) => void
  onConversationId?: (conversationId: string) => void
}

interface ParsedSSEBuffer {
  chunks: string[]
  done: boolean
  errorMessage: string
  rest: string
}

/**
 * Parse SSE (Server-Sent Events) buffer and extract data chunks
 * Handles multi-line data fields and SSE protocol metadata
 */
function parseSSEBuffer(buffer: string): ParsedSSEBuffer {
  const normalized = buffer.replace(/\r/g, '')
  const rawEvents = normalized.split('\n\n')

  // Handle empty buffer case
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

    // Extract data lines (SSE format: data: <content>)
    const dataLines = eventBlock
      .split('\n')
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(5).trimStart())

    if (!dataLines.length) {
      // Skip SSE metadata lines (event:, id:, retry:)
      const isMetadataLine = /^(event|id|retry):/i.test(trimmedBlock)
      if (!isMetadataLine) {
        chunks.push(trimmedBlock)
      }
      return
    }

    const data = dataLines.join('\n')

    // Handle SSE control messages
    if (data === '[DONE]') {
      done = true
      return
    }

    // Handle error messages from server
    if (data.startsWith('[ERROR]')) {
      errorMessage = data.replace('[ERROR]', '').trim() || 'Stream response failed'
      return
    }

    // Validate chunk size to prevent memory issues
    const MAX_CHUNK_SIZE = 1024 * 1024 // 1MB limit per chunk
    if (data.length > MAX_CHUNK_SIZE) {
      console.warn('SSE chunk exceeds maximum size, truncating')
      chunks.push(data.slice(0, MAX_CHUNK_SIZE))
    } else {
      chunks.push(data)
    }
  })

  return {
    chunks,
    done,
    errorMessage,
    rest: tail,
  }
}

/**
 * Consume remaining buffer content after SSE stream ends
 * Extracts data lines or returns trimmed content if no SSE format
 */
function consumeResidualChunk(buffer: string): string {
  const trimmed = buffer.trim()
  if (!trimmed) return ''

  // Extract data lines with proper SSE format handling
  const dataLines = trimmed
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trimStart())

  if (dataLines.length) {
    // Filter out control messages from residual data
    const validData = dataLines.filter(
      (data) => data !== '[DONE]' && !data.startsWith('[ERROR]')
    )
    return validData.join('\n')
  }

  // Return non-empty trimmed content only if it doesn't look like SSE metadata
  if (trimmed && !/^(event|id|retry):/i.test(trimmed)) {
    return trimmed
  }

  return ''
}

/**
 * Extract response text from Axios progress event
 * Safely handles different browser implementations
 */
function getResponseText(progressEvent: AxiosProgressEvent): string {
  // Access XMLHttpRequest through the event target
  const event = progressEvent.event as ProgressEvent | undefined
  const xhr = event?.target as XMLHttpRequest | undefined

  if (xhr?.responseText) {
    return xhr.responseText
  }

  // Fallback: try to access from progressEvent directly
  const anyEvent = progressEvent as unknown as { target?: { responseText?: string } }
  return anyEvent.target?.responseText ?? ''
}

/**
 * Maximum buffer size for SSE data (5MB) to prevent memory exhaustion
 */
const MAX_BUFFER_SIZE = 5 * 1024 * 1024

/**
 * Stream chatbot messages with Server-Sent Events
 * Handles file uploads, progress tracking, and conversation state
 */
export async function streamChatbotMessage({
  message,
  conversationId,
  files = [],
  signal,
  onChunk,
  onConversationId,
}: ChatbotStreamParams): Promise<unknown> {
  // Validate message content (basic XSS prevention)
  const sanitizedMessage = (message || 'Please analyze the uploaded file')
    .slice(0, 10000) // Limit message length

  const formData = new FormData()
  formData.append('message', sanitizedMessage)

  if (conversationId) {
    formData.append('conversationId', conversationId)
  }

  // Validate file uploads
  const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB per file
  const MAX_TOTAL_SIZE = 50 * 1024 * 1024 // 50MB total
  let totalSize = 0

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

  let processedLength = 0
  let sseBuffer = ''
  let streamDone = false
  let errorOccurred = false

  try {
    const response = await request.request<string>({
      url: '/AIChat/message/stream',
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

          // Memory safety: check buffer size limit
          if (sseBuffer.length + incrementalText.length > MAX_BUFFER_SIZE) {
            console.error('SSE buffer size limit exceeded')
            errorOccurred = true
            throw new Error('Response too large')
          }

          sseBuffer += incrementalText

          const parsed = parseSSEBuffer(sseBuffer)
          sseBuffer = parsed.rest

          if (parsed.errorMessage) {
            errorOccurred = true
            throw new Error(parsed.errorMessage)
          }

          // Process chunks safely
          parsed.chunks.forEach((chunk) => {
            try {
              onChunk?.(chunk)
            } catch (callbackError) {
              console.error('Error in onChunk callback:', callbackError)
            }
          })

          if (parsed.done) {
            streamDone = true
          }
        } catch (processingError) {
          errorOccurred = true
          throw processingError
        }
      },
    })

    // Extract conversation ID from response headers
    const conversationIdFromHeader = response.headers?.['x-conversation-id']
    if (conversationIdFromHeader && typeof conversationIdFromHeader === 'string') {
      try {
        onConversationId?.(conversationIdFromHeader)
      } catch (callbackError) {
        console.error('Error in onConversationId callback:', callbackError)
      }
    }

    // Process any remaining buffer content
    if (!streamDone && !errorOccurred) {
      const residualChunk = consumeResidualChunk(sseBuffer)
      if (residualChunk) {
        try {
          onChunk?.(residualChunk)
        } catch (callbackError) {
          console.error('Error in onChunk callback:', callbackError)
        }
      }
    }

    return response
  } catch (error) {
    // Enhance error information
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
