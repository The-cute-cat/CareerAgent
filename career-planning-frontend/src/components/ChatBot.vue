<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  ChatDotRound,
  Close,
  Promotion,
  Paperclip,
  Delete,
  FullScreen,
  Minus,
  CopyDocument,
  Sunny,
} from '@element-plus/icons-vue'
import VueMarkdown from 'vue-markdown-render'
import { ElMessage } from 'element-plus'
import { streamChatbotMessage } from '@/api/chatbot'

interface ChatConfig {
  userId?: string
  conversationId?: string
  title?: string
  subtitle?: string
  welcomeMessage?: string
  autoExtractMemory?: boolean
  autoExtractMemoryWithFiles?: boolean
  autoOpen?: boolean
  autoOpenDelay?: number
  openOnScroll?: boolean
  scrollThreshold?: number
  openOnExit?: boolean
  defaultWidth?: number
  defaultHeight?: number
  minWidth?: number
  minHeight?: number
  maxFileSizeMB?: number
  quickQuestions?: string[]
  persistLayout?: boolean
  layoutStorageKey?: string
}

const props = withDefaults(defineProps<ChatConfig>(), {
  conversationId: '',
  title: 'AI 智能助手',
  subtitle: '支持流式回复 · 文件问答',
  welcomeMessage: '你好，我是你的 AI 智能助手。你可以直接向我提问，也可以上传 PDF / DOCX / 图片让我帮你分析。',
  autoExtractMemory: true,
  autoExtractMemoryWithFiles: false,
  autoOpen: false,
  autoOpenDelay: 1200,
  openOnScroll: false,
  scrollThreshold: 500,
  openOnExit: false,
  defaultWidth: 320,
  defaultHeight: 400,
  minWidth: 320,
  minHeight: 400,
  maxFileSizeMB: 10,
  quickQuestions: () => ['帮我分析一下我的简历', '这个岗位适合我吗？', '给我一些职业规划建议'],
  persistLayout: true,
  layoutStorageKey: 'career-chatbot-layout'
})

// Conversation ID 本地存储 key
const CONVERSATION_ID_KEY = 'career-chatbot-conversation-id'

const emit = defineEmits<{
  (e: 'update:conversationId', value: string): void
  (e: 'error', value: string): void
  (e: 'opened'): void
  (e: 'closed'): void
}>()

type MessageRole = 'user' | 'assistant'
type ResizeDirection =
  | 'top'
  | 'right'
  | 'bottom'
  | 'left'
  | 'top-left'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-right'

interface UploadedFileItem {
  id: string
  name: string
  size: number
  type: string
  file: File
}

interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  time: string
  files?: UploadedFileItem[]
  streaming?: boolean
  error?: boolean
}

interface LayoutState {
  btnPosition: { x: number; y: number }
  windowPosition: { x: number; y: number }
  size: { width: number; height: number }
}

const EDGE_GAP = 12
const HEADER_HEIGHT = 64
const FLOAT_BTN_SIZE = 64
const MAX_UPLOAD_FILES = 5
const COLLAPSE_THRESHOLD = 220
const COLLAPSE_LINES = 4
const emojiList = ['😊', '👍', '🎯', '📄', '💡', '🚀', '👏', '🤔']

const dialogVisible = ref(false)
const isMinimized = ref(false)
const isFullscreen = ref(false)
const isStreaming = ref(false)
const isHeaderDragging = ref(false)
const isDraggingWindow = ref(false)
const isDraggingBtn = ref(false)
const isResizing = ref(false)
const resizeDirection = ref<ResizeDirection | null>(null)
const userInput = ref('')
const uploadedFiles = ref<UploadedFileItem[]>([])
const showEmojiPanel = ref(false)
const expandedMessageIds = ref<string[]>([])
const sendingState = ref<'idle' | 'sending' | 'error'>('idle')
const fileInputRef = ref<HTMLInputElement | null>(null)
const chatWindowRef = ref<HTMLElement | null>(null)
const floatBtnRef = ref<HTMLElement | null>(null)
const messagesContainer = ref<HTMLElement | null>(null)
const abortController = ref<AbortController | null>(null)

// 从 localStorage 恢复 conversationId，如果没有则使用 props 传入的值（可能为空）
function getStoredConversationId(): string {
  try {
    const stored = localStorage.getItem(CONVERSATION_ID_KEY)
    if (stored) {
      return stored
    }
  } catch {
    // 静默处理存储异常
  }
  return props.conversationId || ''
}

const currentConversationId = ref(getStoredConversationId())

const currentSize = ref({
  width: props.defaultWidth,
  height: props.defaultHeight
})
const windowPosition = ref({ x: 0, y: 0 })
const btnPosition = ref({ x: 0, y: 0 })
const dragOffset = ref({ x: 0, y: 0 })
const btnDragOffset = ref({ x: 0, y: 0 })
const resizeStartRect = ref({
  x: 0,
  y: 0,
  width: props.defaultWidth,
  height: props.defaultHeight,
  pointX: 0,
  pointY: 0
})
const restoreRect = ref({
  x: 0,
  y: 0,
  width: props.defaultWidth,
  height: props.defaultHeight
})

const messages = ref<ChatMessage[]>([
  {
    id: createId(),
    role: 'assistant',
    content: props.welcomeMessage,
    time: getCurrentTime()
  }
])

const canSend = computed(() => {
  return (!!userInput.value.trim() || uploadedFiles.value.length > 0) && !isStreaming.value
})

watch(
  () => props.conversationId,
  (value) => {
    const newId = value || ''
    if (newId !== currentConversationId.value) {
      currentConversationId.value = newId
      if (newId) {
        saveConversationId(newId)
      } else {
        clearStoredConversationId()
      }
    }
  }
)

function createId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`
}

// 保存 conversationId 到 localStorage
function saveConversationId(conversationId: string) {
  if (!conversationId) return
  try {
    localStorage.setItem(CONVERSATION_ID_KEY, conversationId)
  } catch {
    // 静默处理存储异常
  }
}

// 清除 localStorage 中的 conversationId
function clearStoredConversationId() {
  try {
    localStorage.removeItem(CONVERSATION_ID_KEY)
  } catch {
    // 静默处理存储异常
  }
}

function ensureConversationId() {
  // 优先使用已有的 conversationId（从 localStorage 或 props 恢复）
  if (currentConversationId.value) {
    return currentConversationId.value
  }

  // 初始状态：返回空字符串，由服务端生成
  // 第一次对话后，服务端会返回 conversationId
  return ''
}

function getCurrentTime() {
  const now = new Date()
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
}

function getEventPoint(e: MouseEvent | TouchEvent) {
  const touch = 'touches' in e && e.touches?.length ? e.touches[0] : undefined
  if (touch) {
    return { x: touch.clientX, y: touch.clientY }
  }
  const changedTouch = 'changedTouches' in e && e.changedTouches?.length ? e.changedTouches[0] : undefined
  if (changedTouch) {
    return { x: changedTouch.clientX, y: changedTouch.clientY }
  }
  const mouseEvent = e as MouseEvent
  return { x: mouseEvent.clientX, y: mouseEvent.clientY }
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}

function initBtnPosition() {
  btnPosition.value = {
    x: window.innerWidth - FLOAT_BTN_SIZE - EDGE_GAP,
    y: window.innerHeight - FLOAT_BTN_SIZE - EDGE_GAP
  }
}

function initWindowPosition() {
  currentSize.value = {
    width: clamp(props.defaultWidth, props.minWidth, window.innerWidth - EDGE_GAP * 2),
    height: clamp(props.defaultHeight, props.minHeight, window.innerHeight - EDGE_GAP * 2)
  }
  windowPosition.value = {
    x: window.innerWidth - currentSize.value.width - EDGE_GAP,
    y: window.innerHeight - currentSize.value.height - EDGE_GAP - 12
  }
  restoreRect.value = {
    x: windowPosition.value.x,
    y: windowPosition.value.y,
    width: currentSize.value.width,
    height: currentSize.value.height
  }
}

function saveLayout() {
  if (!props.persistLayout) return
  try {
    const payload: LayoutState = {
      btnPosition: btnPosition.value,
      windowPosition: windowPosition.value,
      size: currentSize.value
    }
    localStorage.setItem(props.layoutStorageKey, JSON.stringify(payload))
  } catch {
    // 静默处理存储异常（如存储空间已满）
  }
}

function restoreLayout() {
  if (!props.persistLayout) {
    initBtnPosition()
    initWindowPosition()
    return
  }

  const raw = localStorage.getItem(props.layoutStorageKey)
  if (!raw) {
    initBtnPosition()
    initWindowPosition()
    return
  }

  try {
    const parsed = JSON.parse(raw) as LayoutState
    btnPosition.value = parsed.btnPosition
    currentSize.value = {
      width: clamp(parsed.size.width, props.minWidth, window.innerWidth - EDGE_GAP * 2),
      height: clamp(parsed.size.height, props.minHeight, window.innerHeight - EDGE_GAP * 2)
    }
    windowPosition.value = parsed.windowPosition
    syncToViewport()
  } catch {
    initBtnPosition()
    initWindowPosition()
  }
}

function syncToViewport() {
  if (isFullscreen.value) {
    windowPosition.value = { x: 0, y: 0 }
    currentSize.value = {
      width: window.innerWidth,
      height: window.innerHeight
    }
    return
  }

  currentSize.value.width = clamp(currentSize.value.width, props.minWidth, window.innerWidth - EDGE_GAP * 2)
  currentSize.value.height = clamp(currentSize.value.height, props.minHeight, window.innerHeight - EDGE_GAP * 2)

  const minimizedHeight = isMinimized.value ? HEADER_HEIGHT : currentSize.value.height
  windowPosition.value.x = clamp(windowPosition.value.x, EDGE_GAP, window.innerWidth - currentSize.value.width - EDGE_GAP)
  windowPosition.value.y = clamp(windowPosition.value.y, EDGE_GAP, window.innerHeight - minimizedHeight - EDGE_GAP)

  btnPosition.value.x = clamp(btnPosition.value.x, EDGE_GAP, window.innerWidth - FLOAT_BTN_SIZE - EDGE_GAP)
  btnPosition.value.y = clamp(btnPosition.value.y, EDGE_GAP, window.innerHeight - FLOAT_BTN_SIZE - EDGE_GAP)

  saveLayout()
}

function openChat() {
  dialogVisible.value = true
  isMinimized.value = false
  syncToViewport()
  nextTick(() => scrollToBottom())
  emit('opened')
}

function closeChat() {
  stopStream(false)
  dialogVisible.value = false
  isMinimized.value = false
  uploadedFiles.value = []
  emit('closed')
}

function toggleMinimize() {
  if (isFullscreen.value && isMinimized.value) {
    isFullscreen.value = false
  }
  isMinimized.value = !isMinimized.value
  syncToViewport()
  saveLayout()
}

function toggleFullscreen() {
  if (!isFullscreen.value) {
    restoreRect.value = {
      x: windowPosition.value.x,
      y: windowPosition.value.y,
      width: currentSize.value.width,
      height: currentSize.value.height
    }
    isFullscreen.value = true
    isMinimized.value = false
    windowPosition.value = { x: 0, y: 0 }
    currentSize.value = {
      width: window.innerWidth,
      height: window.innerHeight
    }
  } else {
    isFullscreen.value = false
    currentSize.value = {
      width: clamp(restoreRect.value.width, props.minWidth, window.innerWidth - EDGE_GAP * 2),
      height: clamp(restoreRect.value.height, props.minHeight, window.innerHeight - EDGE_GAP * 2)
    }
    windowPosition.value = {
      x: clamp(restoreRect.value.x, EDGE_GAP, window.innerWidth - currentSize.value.width - EDGE_GAP),
      y: clamp(restoreRect.value.y, EDGE_GAP, window.innerHeight - currentSize.value.height - EDGE_GAP)
    }
  }
  saveLayout()
}

function startWindowDrag(e: MouseEvent | TouchEvent) {
  if (isFullscreen.value) return
  isHeaderDragging.value = true
  isDraggingWindow.value = true
  const point = getEventPoint(e)
  dragOffset.value = {
    x: point.x - windowPosition.value.x,
    y: point.y - windowPosition.value.y
  }
}

function startBtnDrag(e: MouseEvent | TouchEvent) {
  if (dialogVisible.value) return
  isDraggingBtn.value = true
  const point = getEventPoint(e)
  dragOffset.value = { x: point.x, y: point.y }
  btnDragOffset.value = {
    x: point.x - btnPosition.value.x,
    y: point.y - btnPosition.value.y
  }
}

function snapFloatButton() {
  const midpoint = window.innerWidth / 2
  btnPosition.value.x = btnPosition.value.x + FLOAT_BTN_SIZE / 2 < midpoint ? EDGE_GAP : window.innerWidth - FLOAT_BTN_SIZE - EDGE_GAP
  btnPosition.value.y = clamp(btnPosition.value.y, EDGE_GAP, window.innerHeight - FLOAT_BTN_SIZE - EDGE_GAP)
  saveLayout()
}

let btnDragStartTime = 0
let btnDragStartPoint = { x: 0, y: 0 }

function onFloatBtnDown(e: MouseEvent | TouchEvent) {
  btnDragStartTime = Date.now()
  btnDragStartPoint = getEventPoint(e)
  startBtnDrag(e)
}

function onFloatBtnUp(e: MouseEvent | TouchEvent) {
  const point = getEventPoint(e)
  const duration = Date.now() - btnDragStartTime
  const distance = Math.hypot(point.x - btnDragStartPoint.x, point.y - btnDragStartPoint.y)

  if (isDraggingBtn.value) {
    isDraggingBtn.value = false
    snapFloatButton()
  }

  if (duration < 180 && distance < 6) {
    openChat()
  }
}

function startResize(direction: ResizeDirection, e: MouseEvent | TouchEvent) {
  if (isFullscreen.value || isMinimized.value) return
  isResizing.value = true
  resizeDirection.value = direction
  const point = getEventPoint(e)
  resizeStartRect.value = {
    x: windowPosition.value.x,
    y: windowPosition.value.y,
    width: currentSize.value.width,
    height: currentSize.value.height,
    pointX: point.x,
    pointY: point.y
  }
}

function onGlobalMove(e: MouseEvent | TouchEvent) {
  if (dragThrottleTimer) return
  dragThrottleTimer = setTimeout(() => { dragThrottleTimer = null }, 16)

  if (isDraggingWindow.value && !isFullscreen.value) {
    e.preventDefault()
    const point = getEventPoint(e)
    const height = isMinimized.value ? HEADER_HEIGHT : currentSize.value.height
    windowPosition.value = {
      x: clamp(point.x - dragOffset.value.x, EDGE_GAP, window.innerWidth - currentSize.value.width - EDGE_GAP),
      y: clamp(point.y - dragOffset.value.y, EDGE_GAP, window.innerHeight - height - EDGE_GAP)
    }
    return
  }

  if (isDraggingBtn.value) {
    e.preventDefault()
    const point = getEventPoint(e)
    btnPosition.value = {
      x: clamp(point.x - btnDragOffset.value.x, EDGE_GAP, window.innerWidth - FLOAT_BTN_SIZE - EDGE_GAP),
      y: clamp(point.y - btnDragOffset.value.y, EDGE_GAP, window.innerHeight - FLOAT_BTN_SIZE - EDGE_GAP)
    }
    return
  }

  if (isResizing.value && resizeDirection.value) {
    e.preventDefault()
    const point = getEventPoint(e)
    const dx = point.x - resizeStartRect.value.pointX
    const dy = point.y - resizeStartRect.value.pointY

    let nextX = resizeStartRect.value.x
    let nextY = resizeStartRect.value.y
    let nextWidth = resizeStartRect.value.width
    let nextHeight = resizeStartRect.value.height

    if (resizeDirection.value.includes('right')) {
      nextWidth = resizeStartRect.value.width + dx
    }
    if (resizeDirection.value.includes('bottom')) {
      nextHeight = resizeStartRect.value.height + dy
    }
    if (resizeDirection.value.includes('left')) {
      nextWidth = resizeStartRect.value.width - dx
      nextX = resizeStartRect.value.x + dx
    }
    if (resizeDirection.value.includes('top')) {
      nextHeight = resizeStartRect.value.height - dy
      nextY = resizeStartRect.value.y + dy
    }

    nextWidth = Math.max(nextWidth, props.minWidth)
    nextHeight = Math.max(nextHeight, props.minHeight)

    if (resizeDirection.value.includes('left')) {
      nextX = resizeStartRect.value.x + (resizeStartRect.value.width - nextWidth)
    }
    if (resizeDirection.value.includes('top')) {
      nextY = resizeStartRect.value.y + (resizeStartRect.value.height - nextHeight)
    }

    if (nextX < EDGE_GAP) {
      nextWidth -= EDGE_GAP - nextX
      nextX = EDGE_GAP
    }
    if (nextY < EDGE_GAP) {
      nextHeight -= EDGE_GAP - nextY
      nextY = EDGE_GAP
    }
    if (nextX + nextWidth > window.innerWidth - EDGE_GAP) {
      nextWidth = window.innerWidth - EDGE_GAP - nextX
    }
    if (nextY + nextHeight > window.innerHeight - EDGE_GAP) {
      nextHeight = window.innerHeight - EDGE_GAP - nextY
    }

    currentSize.value = {
      width: Math.max(nextWidth, props.minWidth),
      height: Math.max(nextHeight, props.minHeight)
    }
    windowPosition.value = { x: nextX, y: nextY }
  }
}

function onGlobalUp() {
  if (isDraggingWindow.value || isDraggingBtn.value || isResizing.value) {
    saveLayout()
  }
  isDraggingWindow.value = false
  isDraggingBtn.value = false
  isResizing.value = false
  resizeDirection.value = null
  setTimeout(() => {
    isHeaderDragging.value = false
  }, 50)
}

function triggerFileUpload() {
  fileInputRef.value?.click()
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function removeFile(id: string) {
  uploadedFiles.value = uploadedFiles.value.filter((item) => item.id !== id)
}

function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const files = Array.from(input.files || [])
  if (!files.length) return

  if (uploadedFiles.value.length + files.length > MAX_UPLOAD_FILES) {
    ElMessage.warning(`最多只能上传 ${MAX_UPLOAD_FILES} 个文件`)
    input.value = ''
    return
  }

  const maxFileSize = props.maxFileSizeMB * 1024 * 1024
  const allowedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/png',
    'image/jpeg',
    'image/jpg'
  ]

  files.forEach((file) => {
    if (file.size > maxFileSize) {
      ElMessage.warning(`${file.name} 超过 ${props.maxFileSizeMB}MB 限制`)
      return
    }
    if (!allowedTypes.includes(file.type)) {
      ElMessage.warning(`${file.name} 类型不支持，仅支持 PDF / DOCX / PNG / JPG / JPEG`)
      return
    }
    uploadedFiles.value.push({
      id: createId(),
      name: file.name,
      size: file.size,
      type: file.type,
      file
    })
  })

  input.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function scrollToBottom() {
  if (!messagesContainer.value) return
  if (scrollRafId) cancelAnimationFrame(scrollRafId)
  scrollRafId = requestAnimationFrame(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
    scrollRafId = null
  })
}

function pushAssistantPlaceholder() {
  const message: ChatMessage = {
    id: createId(),
    role: 'assistant',
    content: '',
    time: getCurrentTime(),
    streaming: true
  }
  messages.value.push(message)
  return message
}

function appendChunkToMessage(messageId: string, chunk: string) {
  const target = messages.value.find((item) => item.id === messageId)
  if (!target) return
  target.content += chunk
  nextTick(() => scrollToBottom())
}

function finishAssistantMessage(messageId: string) {
  const target = messages.value.find((item) => item.id === messageId)
  if (!target) return
  target.streaming = false
  if (!target.content.trim()) {
    target.content = '已收到请求，但本次没有返回可展示内容。'
  }
}

function markAssistantError(messageId: string, errorMessage: string) {
  const target = messages.value.find((item) => item.id === messageId)
  if (!target) return
  target.streaming = false
  target.error = true
  target.content = errorMessage
}

function clearLocalMessages() {
  stopStream(false)
  // 清除 conversationId，开始新会话
  currentConversationId.value = ''
  clearStoredConversationId()
  emit('update:conversationId', '')
  messages.value = [
    {
      id: createId(),
      role: 'assistant',
      content: props.welcomeMessage,
      time: getCurrentTime()
    }
  ]
  expandedMessageIds.value = []
}

function shouldCollapseMessage(message: ChatMessage) {
  if (message.streaming) return false
  if (message.files?.length) return false
  const lineCount = message.content.split('\n').length
  return message.content.length > COLLAPSE_THRESHOLD || lineCount > COLLAPSE_LINES
}

function isExpanded(messageId: string) {
  return expandedMessageIds.value.includes(messageId)
}

function getDisplayContent(message: ChatMessage) {
  if (!shouldCollapseMessage(message) || isExpanded(message.id)) {
    return message.content
  }
  return `${message.content.slice(0, COLLAPSE_THRESHOLD).trim()}...`
}

function toggleMessageExpand(messageId: string) {
  if (isExpanded(messageId)) {
    expandedMessageIds.value = expandedMessageIds.value.filter((item) => item !== messageId)
  } else {
    expandedMessageIds.value = [...expandedMessageIds.value, messageId]
  }
}

async function copyMessage(content: string) {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('消息已复制')
  } catch {
    ElMessage.warning('复制失败，请手动复制')
  }
}

function deleteMessage(messageId: string) {
  const target = messages.value.find((item) => item.id === messageId)
  if (!target || target.streaming) return
  messages.value = messages.value.filter((item) => item.id !== messageId)
  expandedMessageIds.value = expandedMessageIds.value.filter((item) => item !== messageId)
}

function insertEmoji(emoji: string) {
  userInput.value += emoji
  showEmojiPanel.value = false
}

async function sendMessage() {
  const text = userInput.value.trim()
  const files = [...uploadedFiles.value]

  if ((!text && files.length === 0) || isStreaming.value) return
  const conversationId = ensureConversationId()

  messages.value.push({
    id: createId(),
    role: 'user',
    content: text || 'Please analyze the uploaded file',
    time: getCurrentTime(),
    files: files.length ? files : undefined
  })

  userInput.value = ''
  uploadedFiles.value = []
  showEmojiPanel.value = false
  sendingState.value = 'sending'
  nextTick(() => scrollToBottom())

  const assistantMessage = pushAssistantPlaceholder()
  const messageId = assistantMessage.id
  const controller = new AbortController()
  abortController.value = controller
  isStreaming.value = true

  try {
    await streamChatbotMessage({
      message: text || 'Please analyze the uploaded file',
      conversationId,
      files: files.map((item) => item.file),
      signal: controller.signal,
      onConversationId: (newConversationId) => {
        // 接收到服务端返回的 conversationId，更新状态并持久化
        if (newConversationId && newConversationId !== currentConversationId.value) {
          currentConversationId.value = newConversationId
          saveConversationId(newConversationId)
          emit('update:conversationId', newConversationId)
        }
      },
      onChunk: (chunk) => {
        appendChunkToMessage(messageId, chunk)
      }
    })

    finishAssistantMessage(messageId)
    sendingState.value = 'idle'
  } catch (error) {
    const message = error instanceof Error
      ? error.name === 'AbortError'
        ? 'Generation stopped'
        : error.message
      : 'Send failed, please try again later'

    if (message === 'Generation stopped') {
      finishAssistantMessage(messageId)
      sendingState.value = 'idle'
    } else {
      markAssistantError(messageId, message)
      sendingState.value = 'error'
      ElMessage.error(message)
      emit('error', message)
    }
  } finally {
    isStreaming.value = false
    abortController.value = null
    nextTick(() => scrollToBottom())
    saveLayout()
  }
}

function stopStream(showToast = true) {
  if (!abortController.value) return
  abortController.value.abort()
  abortController.value = null
  isStreaming.value = false
    const lastIdx = messages.value.length - 1
  for (let i = lastIdx; i >= 0; i--) {
    const item = messages.value[i]
    if (item && item.role === 'assistant' && item.streaming) {
      item.streaming = false
      if (!item.content.trim()) {
        item.content = '生成已停止。'
      }
      break
    }
  }
  if (showToast) {
    ElMessage.info('已停止生成')
  }
}

function sendQuickQuestion(question: string) {
  userInput.value = question
  sendMessage()
}

function handleResize() {
  syncToViewport()
}

let autoOpenTimer: ReturnType<typeof setTimeout> | null = null
let scrollHandler: (() => void) | null = null
let mouseLeaveHandler: ((e: MouseEvent) => void) | null = null
let dragThrottleTimer: ReturnType<typeof setTimeout> | null = null
let scrollRafId: number | null = null

watch(
  () => messages.value.length,
  () => {
    nextTick(() => scrollToBottom())
  }
)

function setupAutoTriggers() {
  if (props.autoOpen) {
    autoOpenTimer = setTimeout(() => {
      if (!dialogVisible.value) openChat()
    }, props.autoOpenDelay)
  }

  if (props.openOnScroll) {
    scrollHandler = () => {
      if (!dialogVisible.value && window.scrollY >= props.scrollThreshold) {
        openChat()
        if (scrollHandler) {
          window.removeEventListener('scroll', scrollHandler)
          scrollHandler = null
        }
      }
    }
    window.addEventListener('scroll', scrollHandler, { passive: true })
  }

  if (props.openOnExit) {
    mouseLeaveHandler = (e: MouseEvent) => {
      if (!dialogVisible.value && e.clientY <= 0) {
        openChat()
      }
    }
    document.addEventListener('mouseout', mouseLeaveHandler)
  }
}

onMounted(() => {
  restoreLayout()
  syncToViewport()
  setupAutoTriggers()

  window.addEventListener('resize', handleResize)
  window.addEventListener('mousemove', onGlobalMove, { passive: false })
  window.addEventListener('mouseup', onGlobalUp)
  window.addEventListener('touchmove', onGlobalMove, { passive: false })
  window.addEventListener('touchend', onGlobalUp)
})

onUnmounted(() => {
  stopStream(false)
  if (autoOpenTimer) clearTimeout(autoOpenTimer)
  if (dragThrottleTimer) clearTimeout(dragThrottleTimer)
  if (scrollRafId) cancelAnimationFrame(scrollRafId)
  if (scrollHandler) window.removeEventListener('scroll', scrollHandler)
  if (mouseLeaveHandler) document.removeEventListener('mouseout', mouseLeaveHandler)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', onGlobalMove)
  window.removeEventListener('mouseup', onGlobalUp)
  window.removeEventListener('touchmove', onGlobalMove)
  window.removeEventListener('touchend', onGlobalUp)
})
</script>

<template>
  <div class="chatbot-wrapper">
    <transition name="assistant-window">
      <div
        v-show="dialogVisible"
        ref="chatWindowRef"
        class="chat-window"
        :class="{
          minimized: isMinimized,
          fullscreen: isFullscreen,
          dragging: isHeaderDragging,
          resizing: isResizing
        }"
        :style="{
          left: `${windowPosition.x}px`,
          top: `${windowPosition.y}px`,
          width: `${currentSize.width}px`,
          height: `${isMinimized ? HEADER_HEIGHT : currentSize.height}px`
        }"
      >
        <div
          class="chat-header"
          @mousedown="startWindowDrag"
          @touchstart="startWindowDrag"
        >
          <div class="header-left">
            <div class="assistant-avatar">
              <el-icon :size="20"><ChatDotRound /></el-icon>
            </div>
            <div class="header-meta">
              <div class="header-title-row">
                <h4>{{ title }}</h4>
                <span class="assistant-badge">AI</span>
                <span class="drag-tip">可拖拽</span>
              </div>
              <div class="header-status">
                <span class="status-dot" :class="{ streaming: isStreaming }"></span>
                <span>{{ isStreaming ? 'AI 正在输入…' : subtitle }}</span>
              </div>
            </div>
          </div>

          <div class="header-actions" @mousedown.stop @touchstart.stop>
            <button class="action-btn" type="button" title="清空本地消息" @click="clearLocalMessages">
              清空
            </button>
            <button
              v-if="isStreaming"
              class="action-btn danger"
              type="button"
              title="停止生成"
              @click="stopStream()"
            >
              停止
            </button>
            <button class="icon-btn" type="button" :title="isMinimized ? '展开' : '最小化'" @click="toggleMinimize">
              <el-icon><Minus /></el-icon>
            </button>
            <button class="icon-btn" type="button" :title="isFullscreen ? '退出全屏' : '全屏'" @click="toggleFullscreen">
              <el-icon><FullScreen /></el-icon>
            </button>
            <button class="icon-btn close" type="button" title="关闭" @click="closeChat">
              <el-icon><Close /></el-icon>
            </button>
          </div>
        </div>

        <div v-show="!isMinimized" class="chat-body">
          <div ref="messagesContainer" class="messages-container">
            <TransitionGroup name="message-fade" tag="div" class="message-list">
              <div
                v-for="message in messages"
                :key="message.id"
                class="message-row"
                :class="message.role"
              >
                <div class="message-avatar">
                  <el-icon v-if="message.role === 'assistant'"><ChatDotRound /></el-icon>
                  <span v-else>我</span>
                </div>

                <div class="message-main">
                  <div
                    class="message-bubble"
                    :class="{ error: message.error, collapsed: shouldCollapseMessage(message) && !isExpanded(message.id) }"
                  >
                    <div class="message-tools">
                      <button class="bubble-tool-btn" type="button" title="复制消息" @click="copyMessage(message.content)">
                        <el-icon><CopyDocument /></el-icon>
                      </button>
                      <button
                        class="bubble-tool-btn"
                        type="button"
                        title="删除消息"
                        :disabled="message.streaming"
                        @click="deleteMessage(message.id)"
                      >
                        <el-icon><Delete /></el-icon>
                      </button>
                    </div>

                    <template v-if="message.content">
                      <VueMarkdown
                        :source="getDisplayContent(message)"
                        :options="{ html: false, linkify: true, typographer: true }"
                      />
                    </template>
                    <template v-else>
                      <div class="typing-placeholder">
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span>AI 正在输入…</span>
                      </div>
                    </template>

                    <button
                      v-if="shouldCollapseMessage(message)"
                      class="expand-btn"
                      type="button"
                      @click="toggleMessageExpand(message.id)"
                    >
                      {{ isExpanded(message.id) ? '收起' : '展开更多' }}
                    </button>

                    <div v-if="message.files?.length" class="message-files">
                      <div v-for="file in message.files" :key="file.id" class="message-file-item">
                        <el-icon><Paperclip /></el-icon>
                        <span class="file-name">{{ file.name }}</span>
                        <span class="file-size">{{ formatFileSize(file.size) }}</span>
                      </div>
                    </div>

                    <div class="message-time-inline">
                      <span>{{ message.time }}</span>
                      <span v-if="message.streaming" class="stream-tag">生成中</span>
                    </div>
                  </div>
                </div>
              </div>
            </TransitionGroup>
          </div>

          <div v-if="quickQuestions.length" class="quick-questions">
            <button
              v-for="question in quickQuestions"
              :key="question"
              type="button"
              class="quick-chip"
              @click="sendQuickQuestion(question)"
            >
              {{ question }}
            </button>
          </div>

          <div v-if="uploadedFiles.length" class="upload-preview">
            <div v-for="file in uploadedFiles" :key="file.id" class="upload-chip">
              <div class="upload-chip-left">
                <el-icon><Paperclip /></el-icon>
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
              </div>
              <button class="delete-btn" type="button" @click="removeFile(file.id)">
                <el-icon><Delete /></el-icon>
              </button>
            </div>
          </div>

          <div class="input-panel">
            <div v-if="showEmojiPanel" class="emoji-panel">
              <button
                v-for="emoji in emojiList"
                :key="emoji"
                class="emoji-btn"
                type="button"
                @click="insertEmoji(emoji)"
              >
                {{ emoji }}
              </button>
            </div>

            <div class="input-shell">
              <div class="input-row">
                <el-input
                  v-model="userInput"
                  type="textarea"
                  resize="none"
                  :autosize="{ minRows: 2, maxRows: 6 }"
                  placeholder="输入你的问题，Enter 发送，Shift + Enter 换行"
                  @keydown="handleKeydown"
                />

                <button
                  v-if="isStreaming"
                  class="send-btn stop"
                  type="button"
                  @click="stopStream()"
                >
                  停止
                </button>
                <button
                  v-else
                  class="send-btn"
                  type="button"
                  :disabled="!canSend"
                  @click="sendMessage"
                >
                  <el-icon><Promotion /></el-icon>
                  <span>发送</span>
                </button>
              </div>

              <div class="input-toolbar">
                <div class="input-toolbar-left">
                  <button class="tool-btn" type="button" title="上传文件" @click="triggerFileUpload">
                    <el-icon><Paperclip /></el-icon>
                    <span>上传</span>
                  </button>
                  <button class="tool-btn ghost" type="button" title="表情" @click="showEmojiPanel = !showEmojiPanel">
                    <el-icon><Sunny /></el-icon>
                    <span>表情</span>
                  </button>
                </div>

                <div class="input-toolbar-right">
                  <span class="hint-text">支持 PDF / DOCX / PNG / JPG / JPEG</span>
                  <span v-if="sendingState === 'error'" class="network-hint is-error">网络异常，请重试</span>
                  <span v-else-if="isStreaming" class="network-hint">AI 正在输入…</span>
                  <span v-else-if="sendingState === 'sending'" class="network-hint">消息发送中…</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <template v-if="!isFullscreen && !isMinimized">
          <span class="resize-handle top" @mousedown.prevent="startResize('top', $event)"></span>
          <span class="resize-handle right" @mousedown.prevent="startResize('right', $event)"></span>
          <span class="resize-handle bottom" @mousedown.prevent="startResize('bottom', $event)"></span>
          <span class="resize-handle left" @mousedown.prevent="startResize('left', $event)"></span>
          <span class="resize-handle top-left" @mousedown.prevent="startResize('top-left', $event)"></span>
          <span class="resize-handle top-right" @mousedown.prevent="startResize('top-right', $event)"></span>
          <span class="resize-handle bottom-left" @mousedown.prevent="startResize('bottom-left', $event)"></span>
          <span class="resize-handle bottom-right" @mousedown.prevent="startResize('bottom-right', $event)"></span>
        </template>
      </div>
    </transition>

    <div
      v-show="!dialogVisible"
      ref="floatBtnRef"
      class="chatbot-float-btn"
      :class="{ dragging: isDraggingBtn }"
      :style="{ left: `${btnPosition.x}px`, top: `${btnPosition.y}px` }"
      @mousedown="onFloatBtnDown"
      @mouseup="onFloatBtnUp"
      @touchstart="onFloatBtnDown"
      @touchend="onFloatBtnUp"
    >
      <div class="float-btn-icon">
        <el-icon :size="24"><ChatDotRound /></el-icon>
      </div>
      <div class="float-btn-text">
        <span>AI 助手</span>
        <small>点击咨询</small>
      </div>
    </div>

    <input
      ref="fileInputRef"
      type="file"
      multiple
      accept=".pdf,.docx,.png,.jpg,.jpeg"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<style scoped>
.chatbot-wrapper {
  position: fixed;
  inset: 0;
  width: 0;
  height: 0;
  z-index: 9999;
  pointer-events: none;
}

.chat-window {
  position: fixed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(16px);
  box-shadow:
    0 24px 64px rgba(15, 23, 42, 0.16),
    0 10px 24px rgba(15, 23, 42, 0.08);
  pointer-events: auto;
  user-select: none;
}

.chat-window.fullscreen {
  border-radius: 0;
  border: none;
}

.chat-window.dragging,
.chat-window.resizing {
  transition: none;
}

.chat-header {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 52%, #0f172a 100%);
  color: #fff;
  cursor: grab;
  flex-shrink: 0;
}

.chat-header:active {
  cursor: grabbing;
}

.header-left {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.assistant-avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.18);
  flex-shrink: 0;
}

.header-meta {
  min-width: 0;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title-row h4 {
  margin: 0;
  font-size: 15px;
  line-height: 1;
  font-weight: 700;
}

.assistant-badge {
  height: 20px;
  padding: 0 8px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.16);
}

.drag-tip {
  height: 20px;
  padding: 0 8px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  background: rgba(15, 23, 42, 0.18);
  color: rgba(255, 255, 255, 0.86);
}

.header-status {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  opacity: 0.95;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #86efac;
  box-shadow: 0 0 0 4px rgba(134, 239, 172, 0.18);
  flex-shrink: 0;
}

.status-dot.streaming {
  animation: pulse 1.1s infinite ease-in-out;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
}

.action-btn,
.icon-btn,
.tool-btn,
.send-btn,
.quick-chip,
.delete-btn {
  border: none;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn {
  height: 30px;
  padding: 0 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.action-btn:hover,
.icon-btn:hover {
  background: rgba(255, 255, 255, 0.24);
}

.action-btn.danger {
  background: rgba(239, 68, 68, 0.18);
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.icon-btn.close:hover {
  background: rgba(239, 68, 68, 0.22);
}

.chat-body {
  min-height: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at top, rgba(59, 130, 246, 0.08), transparent 28%),
    linear-gradient(180deg, #f8fbff 0%, #f6f7fb 100%);
}

.messages-container {
  flex: 1;
  min-height: 0;
  padding: 18px 16px 12px;
  overflow-y: auto;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 30px;
  height: 30px;
  border-radius: 12px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.message-row.assistant .message-avatar {
  background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%);
  color: #fff;
}

.message-row.user .message-avatar {
  background: #0f172a;
  color: #fff;
}

.message-main {
  max-width: min(82%, 680px);
  display: flex;
  flex-direction: column;
}

.message-row.user .message-main {
  align-items: flex-end;
}

.message-bubble {
  position: relative;
  padding: 12px 14px 30px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.7;
  word-break: break-word;
  overflow-wrap: anywhere;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.message-row.assistant .message-bubble {
  color: #1f2937;
  background: rgba(255, 255, 255, 0.95);
  border-bottom-left-radius: 6px;
}

.message-row.user .message-bubble {
  color: #fff;
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  border-bottom-right-radius: 6px;
}

.message-bubble.error {
  background: #fff1f2 !important;
  color: #b91c1c !important;
  border: 1px solid #fecdd3;
}

.message-bubble.collapsed {
  overflow: hidden;
}

.message-tools {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 6px;
  opacity: 0;
  transform: translateY(-4px);
  transition: all 0.18s ease;
}

.message-row:hover .message-tools {
  opacity: 1;
  transform: translateY(0);
}

.bubble-tool-btn {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.68);
  color: #334155;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.message-row.user .bubble-tool-btn {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.bubble-tool-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.message-time-inline {
  position: absolute;
  right: 12px;
  bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: inherit;
  opacity: 0.72;
}

.stream-tag {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.message-row.user .stream-tag {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}

.typing-placeholder {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #64748b;
  animation: typing 1.2s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.3s;
}

.expand-btn {
  margin-top: 8px;
  padding: 0;
  background: transparent;
  color: inherit;
  font-size: 12px;
  font-weight: 700;
  opacity: 0.85;
}

.emoji-panel {
  margin-bottom: 10px;
  padding: 8px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.16);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.emoji-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #f8fafc;
  font-size: 18px;
}

.emoji-btn:hover {
  background: #e2e8f0;
}

.message-files {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed rgba(148, 163, 184, 0.35);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-file-item,
.upload-chip-left {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.file-name {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: inherit;
  opacity: 0.7;
  flex-shrink: 0;
}

.quick-questions {
  padding: 0 14px 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-chip {
  height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.85);
  color: #334155;
  font-size: 12px;
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.quick-chip:hover {
  transform: translateY(-1px);
  color: #1d4ed8;
  border-color: rgba(59, 130, 246, 0.24);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.12);
}

.upload-preview {
  padding: 0 14px 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-chip {
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(148, 163, 184, 0.16);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.delete-btn {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: #f8fafc;
  color: #64748b;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.delete-btn:hover {
  color: #dc2626;
  background: #fee2e2;
}

.input-panel {
  padding: 0 14px 14px;
  flex-shrink: 0;
}

.input-shell {
  padding: 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: 0 16px 30px rgba(148, 163, 184, 0.12);
}

.input-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  align-items: end;
}

.input-shell :deep(.el-textarea__inner) {
  min-height: 56px !important;
  max-height: 140px;
  padding: 12px 14px;
  border-radius: 14px;
  border-color: rgba(148, 163, 184, 0.22);
  box-shadow: none;
  background: #f8fafc;
  font-size: 13px;
  line-height: 1.7;
}

.input-shell :deep(.el-textarea__inner:focus) {
  border-color: #60a5fa;
  background: #fff;
}

.input-toolbar {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.input-toolbar-left,
.input-toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tool-btn {
  height: 34px;
  padding: 0 12px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 600;
}

.tool-btn.ghost {
  background: #f8fafc;
  color: #475569;
}

.tool-btn:hover {
  background: #dbeafe;
}

.tool-btn.ghost:hover {
  background: #e2e8f0;
}

.hint-text,
.network-hint {
  font-size: 11px;
  color: #94a3b8;
}

.network-hint.is-error {
  color: #dc2626;
}

.send-btn {
  height: 38px;
  padding: 0 16px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.22);
}

.send-btn:hover {
  transform: translateY(-1px);
}

.send-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
  transform: none;
  box-shadow: none;
}

.send-btn.stop {
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
  box-shadow: 0 10px 20px rgba(249, 115, 22, 0.22);
}

.message-fade-enter-active,
.message-fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.message-fade-enter-from,
.message-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.chatbot-float-btn {
  position: fixed;
  width: 64px;
  height: 64px;
  border-radius: 22px;
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 68%, #111827 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 18px 36px rgba(37, 99, 235, 0.26);
  cursor: grab;
  pointer-events: auto;
  user-select: none;
  overflow: hidden;
  transition: width 0.22s ease, border-radius 0.22s ease, transform 0.18s ease, box-shadow 0.18s ease;
}

.chatbot-float-btn:hover {
  width: 156px;
  border-radius: 18px;
}

.chatbot-float-btn.dragging,
.chatbot-float-btn:active {
  cursor: grabbing;
  transform: scale(1.04);
  box-shadow: 0 20px 40px rgba(37, 99, 235, 0.32);
}

.float-btn-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.float-btn-text {
  width: 88px;
  padding-right: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  font-size: 12px;
  font-weight: 700;
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.22s ease;
}

.float-btn-text small {
  font-size: 10px;
  opacity: 0.82;
}

.chatbot-float-btn:hover .float-btn-text {
  opacity: 1;
  transform: translateX(0);
}

.resize-handle {
  position: absolute;
  z-index: 3;
}

.resize-handle.top,
.resize-handle.bottom {
  left: 14px;
  right: 14px;
  height: 8px;
}

.resize-handle.left,
.resize-handle.right {
  top: 14px;
  bottom: 14px;
  width: 8px;
}

.resize-handle.top {
  top: -4px;
  cursor: ns-resize;
}

.resize-handle.right {
  right: -4px;
  cursor: ew-resize;
}

.resize-handle.bottom {
  bottom: -4px;
  cursor: ns-resize;
}

.resize-handle.left {
  left: -4px;
  cursor: ew-resize;
}

.resize-handle.top-left,
.resize-handle.top-right,
.resize-handle.bottom-left,
.resize-handle.bottom-right {
  width: 16px;
  height: 16px;
}

.resize-handle.top-left {
  left: -4px;
  top: -4px;
  cursor: nwse-resize;
}

.resize-handle.top-right {
  right: -4px;
  top: -4px;
  cursor: nesw-resize;
}

.resize-handle.bottom-left {
  left: -4px;
  bottom: -4px;
  cursor: nesw-resize;
}

.resize-handle.bottom-right {
  right: -4px;
  bottom: -4px;
  cursor: nwse-resize;
}

.assistant-window-enter-active,
.assistant-window-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.assistant-window-enter-from,
.assistant-window-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.98);
}

.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.5);
  border: 2px solid transparent;
  background-clip: padding-box;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

:deep(p) {
  margin: 0 0 8px;
}

:deep(p:last-child) {
  margin-bottom: 0;
}

:deep(pre) {
  overflow-x: auto;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.06);
}

:deep(code) {
  font-family: Consolas, Monaco, monospace;
  font-size: 12px;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.12);
    opacity: 0.72;
  }
}

@keyframes typing {
  0%,
  80%,
  100% {
    transform: scale(0.7);
    opacity: 0.45;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .chat-window {
    border-radius: 18px;
  }

  .header-actions .action-btn,
  .drag-tip {
    display: none;
  }

  .chatbot-float-btn:hover {
    width: 64px;
    border-radius: 22px;
  }

  .float-btn-text {
    display: none;
  }

  .message-main {
    max-width: 88%;
  }

  .hint-text {
    display: none;
  }

  .input-row {
    grid-template-columns: 1fr;
  }

  .send-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .chat-window:not(.fullscreen) {
    width: calc(100vw - 16px) !important;
    height: calc(100vh - 100px) !important;
    left: 8px !important;
    top: auto !important;
    bottom: 80px !important;
  }

  .quick-questions {
    padding-inline: 10px;
  }

  .upload-preview,
  .input-panel {
    padding-inline: 10px;
  }
}
</style>
