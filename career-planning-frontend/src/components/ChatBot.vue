<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  ChatDotRound,
  Close,
  Promotion,
  Paperclip,
  Delete,
  FullScreen,
  CopyDocument,
  MoreFilled,
  Document,
  Picture,
  Files,
  Loading,
  CircleCheckFilled,
  WarningFilled,
} from '@element-plus/icons-vue'
import VueMarkdown from 'vue-markdown-render'
import { ElMessage } from 'element-plus'
import { streamChatbotMessage } from '@/api/chatbot'
import { usePoints } from '@/composables/usePoints'

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
type FileStatus = 'added' | 'parsing' | 'used' | 'failed'
type StreamResult = 'idle' | 'stopped' | 'error'

interface UploadedFileItem {
  id: string
  name: string
  size: number
  type: string
  file: File | null
  status: FileStatus
  statusText?: string
}

interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  time: string
  files?: UploadedFileItem[]
  streaming?: boolean
  error?: boolean
  stopped?: boolean
}

interface LayoutState {
  btnPosition: { x: number; y: number }
  windowPosition: { x: number; y: number }
  size: { width: number; height: number }
}

interface RequestSnapshot {
  text: string
  fileIds: string[]
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
  defaultWidth: 420,
  defaultHeight: 560,
  minWidth: 340,
  minHeight: 500,
  maxFileSizeMB: 10,
  quickQuestions: () => ['帮我分析一下我的简历', '这个岗位适合我吗？', '给我一些职业规划建议'],
  persistLayout: true,
  layoutStorageKey: 'career-chatbot-layout'
})

const CONVERSATION_ID_KEY = 'career-chatbot-conversation-id'
const EDGE_GAP = 12
const FLOAT_BTN_SIZE = 72
const MAX_UPLOAD_FILES = 5
const COLLAPSE_THRESHOLD = 220
const COLLAPSE_LINES = 4

const emit = defineEmits<{
  (e: 'update:conversationId', value: string): void
  (e: 'error', value: string): void
  (e: 'opened'): void
  (e: 'closed'): void
}>()

const dialogVisible = ref(false)
const isFullscreen = ref(false)
const isStreaming = ref(false)
const isHeaderDragging = ref(false)
const isDraggingWindow = ref(false)
const isDraggingBtn = ref(false)
const isResizing = ref(false)
const isDragOver = ref(false)
const moreMenuVisible = ref(false)
const resizeDirection = ref<ResizeDirection | null>(null)
const userInput = ref('')

// 积分系统
const { consumePoints } = usePoints()
const uploadedFiles = ref<UploadedFileItem[]>([])
const expandedMessageIds = ref<string[]>([])
const sendingState = ref<'idle' | 'sending' | 'error'>('idle')
const showThinking = ref(false)
const streamResult = ref<StreamResult>('idle')
const fileInputRef = ref<HTMLInputElement | null>(null)
const chatWindowRef = ref<HTMLElement | null>(null)
const messagesContainer = ref<HTMLElement | null>(null)
const moreMenuRef = ref<HTMLElement | null>(null)
const abortController = ref<AbortController | null>(null)
const manualStopRequested = ref(false)
const lastRequestSnapshot = ref<RequestSnapshot | null>(null)

function createId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`
}

function getCurrentTime() {
  const now = new Date()
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
}

function createWelcomeMessage(): ChatMessage {
  return {
    id: createId(),
    role: 'assistant',
    content: props.welcomeMessage,
    time: getCurrentTime()
  }
}

function getStoredConversationId(): string {
  try {
    const stored = localStorage.getItem(CONVERSATION_ID_KEY)
    if (stored) return stored
  } catch {
    // ignore
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

const messages = ref<ChatMessage[]>([createWelcomeMessage()])

const validUploadedFiles = computed(() => uploadedFiles.value.filter((item) => item.status === 'added'))
const canSend = computed(() => {
  return (!!userInput.value.trim() || validUploadedFiles.value.length > 0) && !isStreaming.value
})
const quickQuestionCards = computed(() => {
  const defaults = [
    { title: '简历分析', description: '快速识别亮点、短板与优化方向' },
    { title: '岗位匹配', description: '结合目标职位判断匹配度与差距' },
    { title: '职业规划建议', description: '从阶段目标到行动路径给出建议' },
  ]
  return props.quickQuestions.map((prompt, index) => ({
    prompt,
    title: defaults[index]?.title || `场景 ${index + 1}`,
    description: defaults[index]?.description || '用这个问题快速开始一次对话',
  }))
})

const assistantPresenceTone = computed(() => {
  if (sendingState.value === 'error') return 'danger'
  if (isStreaming.value) return 'info'
  return 'success'
})
const assistantPresenceText = computed(() => {
  if (sendingState.value === 'error') return '连接异常'
  if (isStreaming.value) return '生成中'
  return '在线'
})
const composerStatusText = computed(() => {
  if (sendingState.value === 'error') return '连接异常，请检查网络后重试'
  if (isStreaming.value) return 'Shift + Enter 换行，当前可停止生成'
  if (sendingState.value === 'sending') return '消息发送中，请稍候'
  return 'Enter 发送，Shift + Enter 换行'
})
const latestInteractiveMessageId = computed(() => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    const item = messages.value[i]
    if (item && item.role === 'assistant' && (item.stopped || item.error)) {
      return item.id
    }
  }
  return ''
})
const floatButtonStatusText = computed(() => {
  if (sendingState.value === 'error') return '异常'
  if (isStreaming.value) return '生成中'
  return '在线'
})

const isTooltipRight = computed(() => {
  return btnPosition.value.x < window.innerWidth / 2
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

watch(
  () => messages.value.length,
  () => {
    nextTick(() => scrollToBottom())
  }
)

function saveConversationId(conversationId: string) {
  if (!conversationId) return
  try {
    localStorage.setItem(CONVERSATION_ID_KEY, conversationId)
  } catch {
    // ignore
  }
}

function clearStoredConversationId() {
  try {
    localStorage.removeItem(CONVERSATION_ID_KEY)
  } catch {
    // ignore
  }
}

function ensureConversationId() {
  if (currentConversationId.value) {
    return currentConversationId.value
  }

  const newConversationId = createId()
  currentConversationId.value = newConversationId
  saveConversationId(newConversationId)
  emit('update:conversationId', newConversationId)
  return newConversationId
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
    // ignore
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
  windowPosition.value.x = clamp(windowPosition.value.x, EDGE_GAP, window.innerWidth - currentSize.value.width - EDGE_GAP)
  windowPosition.value.y = clamp(windowPosition.value.y, EDGE_GAP, window.innerHeight - currentSize.value.height - EDGE_GAP)
  btnPosition.value.x = clamp(btnPosition.value.x, EDGE_GAP, window.innerWidth - FLOAT_BTN_SIZE - EDGE_GAP)
  btnPosition.value.y = clamp(btnPosition.value.y, EDGE_GAP, window.innerHeight - FLOAT_BTN_SIZE - EDGE_GAP)
  saveLayout()
}

function openChat() {
  dialogVisible.value = true
  moreMenuVisible.value = false
  syncToViewport()
  nextTick(() => scrollToBottom())
  emit('opened')
}

function closeChat() {
  stopStream(false)
  dialogVisible.value = false
  isDragOver.value = false
  moreMenuVisible.value = false
  emit('closed')
}

function toggleFullscreen() {
  moreMenuVisible.value = false
  if (!isFullscreen.value) {
    restoreRect.value = {
      x: windowPosition.value.x,
      y: windowPosition.value.y,
      width: currentSize.value.width,
      height: currentSize.value.height
    }
    isFullscreen.value = true
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
  btnDragOffset.value = {
    x: point.x - btnPosition.value.x,
    y: point.y - btnPosition.value.y
  }
}

function snapFloatButton() {
  const midpoint = window.innerWidth / 2
  btnPosition.value.x =
    btnPosition.value.x + FLOAT_BTN_SIZE / 2 < midpoint
      ? EDGE_GAP
      : window.innerWidth - FLOAT_BTN_SIZE - EDGE_GAP
  btnPosition.value.y = clamp(btnPosition.value.y, EDGE_GAP, window.innerHeight - FLOAT_BTN_SIZE - EDGE_GAP)
  saveLayout()
}

let btnDragStartTime = 0
let btnDragStartPoint = { x: 0, y: 0 }
let autoOpenTimer: ReturnType<typeof setTimeout> | null = null
let scrollHandler: (() => void) | null = null
let mouseLeaveHandler: ((e: MouseEvent) => void) | null = null
let dragThrottleTimer: ReturnType<typeof setTimeout> | null = null
let scrollRafId: number | null = null

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
  if (isFullscreen.value) return
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
  dragThrottleTimer = setTimeout(() => {
    dragThrottleTimer = null
  }, 16)

  if (isDraggingWindow.value && !isFullscreen.value) {
    e.preventDefault()
    const point = getEventPoint(e)
    windowPosition.value = {
      x: clamp(point.x - dragOffset.value.x, EDGE_GAP, window.innerWidth - currentSize.value.width - EDGE_GAP),
      y: clamp(point.y - dragOffset.value.y, EDGE_GAP, window.innerHeight - currentSize.value.height - EDGE_GAP)
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

    if (resizeDirection.value.includes('right')) nextWidth = resizeStartRect.value.width + dx
    if (resizeDirection.value.includes('bottom')) nextHeight = resizeStartRect.value.height + dy
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

function fileStatusLabel(status: FileStatus) {
  if (status === 'parsing') return '解析中'
  if (status === 'used') return '已用于问答'
  if (status === 'failed') return '失败'
  return '已添加'
}

function getFileIcon(file: UploadedFileItem) {
  if (file.type.startsWith('image/')) return Picture
  if (file.type.includes('pdf')) return Files
  return Document
}

function updateFileStatus(fileIds: string[], status: FileStatus, statusText?: string) {
  const idSet = new Set(fileIds)
  uploadedFiles.value = uploadedFiles.value.map((item) => {
    if (!idSet.has(item.id)) return item
    return {
      ...item,
      status,
      statusText: statusText || fileStatusLabel(status)
    }
  })
}

function removeFile(id: string) {
  uploadedFiles.value = uploadedFiles.value.filter((item) => item.id !== id)
}

function buildUploadItem(file: File, status: FileStatus, statusText?: string): UploadedFileItem {
  return {
    id: createId(),
    name: file.name,
    size: file.size,
    type: file.type,
    file,
    status,
    statusText: statusText || fileStatusLabel(status)
  }
}

function ingestFiles(files: File[]) {
  if (!files.length) return

  const availableSlots = MAX_UPLOAD_FILES - uploadedFiles.value.length
  if (availableSlots <= 0) {
    ElMessage.warning(`最多只能上传 ${MAX_UPLOAD_FILES} 个文件`)
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

  files.slice(0, availableSlots).forEach((file) => {
    if (file.size > maxFileSize) {
      uploadedFiles.value.unshift(buildUploadItem(file, 'failed', `超过 ${props.maxFileSizeMB}MB 限制`))
      ElMessage.warning(`${file.name} 超过 ${props.maxFileSizeMB}MB 限制`)
      return
    }

    if (!allowedTypes.includes(file.type)) {
      uploadedFiles.value.unshift(buildUploadItem(file, 'failed', '类型不支持'))
      ElMessage.warning(`${file.name} 类型不支持，仅支持 PDF / DOCX / PNG / JPG / JPEG`)
      return
    }

    uploadedFiles.value.unshift(buildUploadItem(file, 'added'))
  })

  if (files.length > availableSlots) {
    ElMessage.warning(`最多只能上传 ${MAX_UPLOAD_FILES} 个文件`)
  }
}

function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  ingestFiles(Array.from(input.files || []))
  input.value = ''
}

function onDropAreaDragOver(e: DragEvent) {
  e.preventDefault()
  isDragOver.value = true
}

function onDropAreaDragLeave(e: DragEvent) {
  if (!chatWindowRef.value) {
    isDragOver.value = false
    return
  }

  const relatedTarget = e.relatedTarget as Node | null
  if (relatedTarget && chatWindowRef.value.contains(relatedTarget)) {
    return
  }

  isDragOver.value = false
}

function onDropAreaDrop(e: DragEvent) {
  e.preventDefault()
  isDragOver.value = false
  ingestFiles(Array.from(e.dataTransfer?.files || []))
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

function normalizeIncomingChunk(chunk: string): string {
  const safeChunk = typeof chunk === 'string' ? chunk : ''
  const trimmed = safeChunk.trim()

  if (!trimmed) return safeChunk
  if (!trimmed.startsWith('{')) return safeChunk

  try {
    const payload = JSON.parse(trimmed) as Record<string, unknown>
    if (payload.type === 'content' && typeof payload.content === 'string') {
      return payload.content
    }
    if (typeof payload.content === 'string') {
      return payload.content
    }
    return ''
  } catch {
    return safeChunk
  }
}

function appendChunkToMessage(messageId: string, chunk: string) {
  const target = messages.value.find((item) => item.id === messageId)
  if (!target) return

  const normalizedChunk = normalizeIncomingChunk(chunk)
  if (!normalizedChunk) return

  target.content += normalizedChunk
  nextTick(() => scrollToBottom())
}

function finishAssistantMessage(messageId: string) {
  const target = messages.value.find((item) => item.id === messageId)
  if (!target) return
  target.streaming = false
  target.stopped = false
  if (!target.content.trim()) {
    target.content = '已收到请求，但本次没有返回可展示内容。'
  }
}

function markAssistantStopped(messageId: string) {
  const target = messages.value.find((item) => item.id === messageId)
  if (!target) return
  target.streaming = false
  target.stopped = true
  if (!target.content.trim()) {
    target.content = '已停止生成。你可以继续追问，或重新生成本次回答。'
  }
}

function markAssistantError(messageId: string, errorMessage: string) {
  const target = messages.value.find((item) => item.id === messageId)
  if (!target) return
  target.streaming = false
  target.error = true
  target.stopped = false
  target.content = errorMessage
}

function clearLocalMessages() {
  stopStream(false)
  currentConversationId.value = ''
  clearStoredConversationId()
  emit('update:conversationId', '')
  messages.value = [createWelcomeMessage()]
  uploadedFiles.value = []
  expandedMessageIds.value = []
  streamResult.value = 'idle'
  moreMenuVisible.value = false
}

function shouldCollapseMessage(message: ChatMessage) {
  if (message.streaming || message.files?.length) return false
  const lineCount = message.content.split('\n').length
  return message.content.length > COLLAPSE_THRESHOLD || lineCount > COLLAPSE_LINES
}

function isExpanded(messageId: string) {
  return expandedMessageIds.value.includes(messageId)
}

function toggleMessageExpand(messageId: string) {
  if (isExpanded(messageId)) {
    expandedMessageIds.value = expandedMessageIds.value.filter((item) => item !== messageId)
  } else {
    expandedMessageIds.value = [...expandedMessageIds.value, messageId]
  }
}

function isLatestInteractiveMessage(messageId: string) {
  return latestInteractiveMessageId.value === messageId
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

async function sendMessage(snapshot?: RequestSnapshot) {
  const text = snapshot?.text ?? userInput.value.trim()
  const fileIds = snapshot?.fileIds ?? validUploadedFiles.value.map((item) => item.id)
  const files = fileIds
    .map((id) => uploadedFiles.value.find((item) => item.id === id))
    .filter((item): item is UploadedFileItem => !!item && !!item.file)

  if ((!text && files.length === 0) || isStreaming.value) return

  // 扣除积分（AI问答：10积分/次）
  const pointsResult = await consumePoints('aiChat', 'AI问答')
  if (!pointsResult.success) {
    // 积分不足，已弹出提示
    return
  }

  const conversationId = ensureConversationId()
  const effectiveText = text || 'Please analyze the uploaded file'
  lastRequestSnapshot.value = {
    text: effectiveText,
    fileIds: files.map((item) => item.id)
  }
  streamResult.value = 'idle'
  manualStopRequested.value = false

  messages.value.push({
    id: createId(),
    role: 'user',
    content: effectiveText,
    time: getCurrentTime(),
    files: files.length ? files.map((item) => ({ ...item })) : undefined
  })

  if (!snapshot) {
    userInput.value = ''
  }

  updateFileStatus(files.map((item) => item.id), 'parsing')

  sendingState.value = 'sending'
  nextTick(() => scrollToBottom())

  const assistantMessage = pushAssistantPlaceholder()
  const messageId = assistantMessage.id
  const controller = new AbortController()
  abortController.value = controller
  isStreaming.value = true

  try {
    await streamChatbotMessage({
      message: effectiveText,
      conversationId,
      files: files.map((item) => item.file).filter((item): item is File => !!item),
      signal: controller.signal,
      autoExtractMemory: files.length > 0 ? props.autoExtractMemoryWithFiles : props.autoExtractMemory,
      showThinking: showThinking.value,
      onConversationId: (newConversationId) => {
        if (newConversationId && newConversationId !== currentConversationId.value) {
          currentConversationId.value = newConversationId
          saveConversationId(newConversationId)
          emit('update:conversationId', newConversationId)
        }
      },
      onChunk: (chunk) => {
        appendChunkToMessage(messageId, chunk)
        updateFileStatus(files.map((item) => item.id), 'used')
      }
    })

    finishAssistantMessage(messageId)
    updateFileStatus(files.map((item) => item.id), 'used')
    sendingState.value = 'idle'
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '请求失败，请稍后再试'
    const isAbort = manualStopRequested.value || errorMessage === 'Request was cancelled'

    if (isAbort) {
      markAssistantStopped(messageId)
      updateFileStatus(files.map((item) => item.id), 'used')
      sendingState.value = 'idle'
      streamResult.value = 'stopped'
    } else {
      markAssistantError(messageId, errorMessage || '请求失败，请稍后再试')
      updateFileStatus(files.map((item) => item.id), 'failed', '处理失败')
      sendingState.value = 'error'
      streamResult.value = 'error'
      ElMessage.error(errorMessage || '请求失败，请稍后再试')
      emit('error', errorMessage || '请求失败，请稍后再试')
    }
  } finally {
    isStreaming.value = false
    abortController.value = null
    manualStopRequested.value = false
    nextTick(() => scrollToBottom())
    saveLayout()
  }
}

function stopStream(showToast = true) {
  if (!abortController.value) return
  manualStopRequested.value = true
  abortController.value.abort()
  abortController.value = null
  isStreaming.value = false
  streamResult.value = 'stopped'
  if (showToast) {
    ElMessage.info('已停止生成')
  }
}

function regenerateLastReply() {
  if (!lastRequestSnapshot.value) return
  sendMessage(lastRequestSnapshot.value)
}

function sendQuickQuestion(question: string) {
  userInput.value = question
  sendMessage()
}

function toggleMoreMenu() {
  moreMenuVisible.value = !moreMenuVisible.value
}

function closeMoreMenu() {
  moreMenuVisible.value = false
}

function handleResize() {
  syncToViewport()
}

function handleDocumentPointerDown(e: MouseEvent) {
  const target = e.target as Node | null
  if (moreMenuVisible.value && moreMenuRef.value && target && !moreMenuRef.value.contains(target)) {
    moreMenuVisible.value = false
  }
}

function handleGlobalKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    if (isFullscreen.value) {
      toggleFullscreen()
      return
    }
    closeMoreMenu()
  }
}

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
  document.addEventListener('mousedown', handleDocumentPointerDown)
  window.addEventListener('keydown', handleGlobalKeydown)
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
  document.removeEventListener('mousedown', handleDocumentPointerDown)
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<template>
  <div class="chatbot-wrapper">
    <transition name="assistant-window">
      <div
        v-show="dialogVisible"
        ref="chatWindowRef"
        class="chat-window"
        :class="{ fullscreen: isFullscreen, dragging: isHeaderDragging, resizing: isResizing }"
        :style="{
          left: `${windowPosition.x}px`,
          top: `${windowPosition.y}px`,
          width: `${currentSize.width}px`,
          height: `${currentSize.height}px`
        }"
        @dragover="onDropAreaDragOver"
        @dragleave="onDropAreaDragLeave"
        @drop="onDropAreaDrop"
      >
        <div class="chat-header" @mousedown="startWindowDrag" @touchstart="startWindowDrag">
          <div class="header-left">
            <div class="assistant-avatar">
              <el-icon :size="18"><ChatDotRound /></el-icon>
            </div>
            <div class="header-meta">
              <div class="header-title-row">
                <h4>{{ title }}</h4>
                <span class="assistant-badge" v-if="sendingState === 'error' || isStreaming">{{ assistantPresenceText }}</span>
              </div>
            </div>
          </div>

          <div class="header-actions" @mousedown.stop @touchstart.stop>
            <button
              class="icon-btn"
              type="button"
              :aria-label="isFullscreen ? '退出全屏' : '进入全屏'"
              :title="isFullscreen ? '退出全屏' : '进入全屏'"
              @click="toggleFullscreen"
            >
              <el-icon><FullScreen /></el-icon>
            </button>

            <div ref="moreMenuRef" class="header-menu">
              <button
                class="icon-btn"
                type="button"
                aria-label="更多操作"
                title="更多操作"
                @click="toggleMoreMenu"
              >
                <el-icon><MoreFilled /></el-icon>
              </button>

              <transition name="menu-fade">
                <div v-if="moreMenuVisible" class="header-menu-popover">
                  <button class="menu-item" type="button" @click="clearLocalMessages">清空会话</button>
                  <button v-if="isStreaming" class="menu-item warning" type="button" @click="stopStream()">停止生成</button>
                  <button v-if="lastRequestSnapshot" class="menu-item" type="button" @click="regenerateLastReply">重新生成</button>
                </div>
              </transition>
            </div>

            <button
              class="icon-btn close"
              type="button"
              aria-label="关闭聊天窗口"
              title="关闭"
              @click="closeChat"
            >
              <el-icon><Close /></el-icon>
            </button>
          </div>
        </div>

        <div class="chat-body" :class="{ fullscreen: isFullscreen }">
          <div class="chat-main">
            <div ref="messagesContainer" class="messages-container">
              <TransitionGroup name="message-fade" tag="div" class="message-list">
                <div v-for="message in messages" :key="message.id" class="message-row" :class="message.role">
                  <div class="message-avatar">
                    <el-icon v-if="message.role === 'assistant'"><ChatDotRound /></el-icon>
                    <span v-else>我</span>
                  </div>

                  <div class="message-main">
                    <div class="message-meta-line">
                      <span class="message-author">{{ message.role === 'assistant' ? 'AI 助手' : '用户' }}</span>
                      <span class="message-time">{{ message.time }}</span>
                    </div>

                    <div class="message-bubble" :class="{ error: message.error, collapsed: shouldCollapseMessage(message) && !isExpanded(message.id) }">
                      <div class="message-tools">
                        <button class="bubble-tool-btn" type="button" aria-label="复制消息" title="复制消息" @click="copyMessage(message.content)">
                          <el-icon><CopyDocument /></el-icon>
                        </button>
                        <button
                          class="bubble-tool-btn"
                          type="button"
                          aria-label="删除消息"
                          title="删除消息"
                          :disabled="message.streaming"
                          @click="deleteMessage(message.id)"
                        >
                          <el-icon><Delete /></el-icon>
                        </button>
                      </div>

                      <template v-if="message.content">
                        <div class="message-content" :class="{ 'is-collapsed': shouldCollapseMessage(message) && !isExpanded(message.id) }">
                          <VueMarkdown :source="message.content" :options="{ html: false, linkify: true, typographer: true }" />
                        </div>
                        <div v-if="shouldCollapseMessage(message) && !isExpanded(message.id)" class="collapse-mask"></div>
                      </template>
                      <template v-else>
                        <div class="typing-placeholder">
                          <span>AI 思考中</span>
                          <span class="typing-dot"></span>
                          <span class="typing-dot"></span>
                          <span class="typing-dot"></span>
                        </div>
                      </template>

                     

                      <button v-if="shouldCollapseMessage(message)" class="expand-btn" type="button" @click="toggleMessageExpand(message.id)">
                        {{ isExpanded(message.id) ? '收起' : '展开完整内容' }}
                      </button>

                      <div v-if="message.files?.length" class="message-files">
                        <div v-for="file in message.files" :key="file.id" class="message-file-item">
                          <el-icon><component :is="getFileIcon(file)" /></el-icon>
                          <span class="file-name">{{ file.name }}</span>
                          <span class="file-size">{{ formatFileSize(file.size) }}</span>
                        </div>
                      </div>

                      <div v-if="(message.stopped || message.error) && isLatestInteractiveMessage(message.id)" class="message-state-tip" :class="{ error: message.error }">
                        <el-icon v-if="message.error"><WarningFilled /></el-icon>
                        <el-icon v-else><CircleCheckFilled /></el-icon>
                        <span>{{ message.error ? '请求未成功完成，请检查网络或稍后重试。' : '本次回答已手动停止。' }}</span>
                        <button v-if="lastRequestSnapshot" class="inline-action" type="button" @click="regenerateLastReply">重新生成</button>
                      </div>
                    </div>
                  </div>
                </div>
              </TransitionGroup>
            </div>

            <div class="input-panel" :class="{ 'is-drag-over': isDragOver }">
              <div class="drop-hint">
                <el-icon><Paperclip /></el-icon>
                <span>拖拽文件到这里上传</span>
              </div>

              <div class="input-shell">
                <div class="input-row">
                  <div class="input-left-area">
                    <button
                      class="tool-btn icon-only"
                      type="button"
                      aria-label="上传文件"
                      title="上传文件"
                      @click="triggerFileUpload"
                    >
                      <el-icon><Paperclip /></el-icon>
                    </button>
                    <el-input
                      v-model="userInput"
                      type="textarea"
                      resize="none"
                      :autosize="{ minRows: 1, maxRows: 4 }"
                      placeholder="输入你的问题..."
                      @keydown="handleKeydown"
                    />
                  </div>

                  <button
                    class="send-btn compact"
                    :class="{ stop: isStreaming }"
                    type="button"
                    :disabled="!isStreaming && !canSend"
                    :aria-label="isStreaming ? '停止生成' : '发送消息'"
                    @click="isStreaming ? stopStream() : sendMessage()"
                  >
                    <el-icon><component :is="isStreaming ? Close : Promotion" /></el-icon>
                  </button>
                </div>

                <div v-if="uploadedFiles.length" class="compact-upload-preview">
                  <div v-for="file in uploadedFiles" :key="file.id" class="compact-upload-item" :class="file.status">
                    <el-icon><component :is="getFileIcon(file)" /></el-icon>
                    <span class="file-name">{{ file.name }}</span>
                    <button class="delete-btn tiny" type="button" @click="removeFile(file.id)">
                      <el-icon><Delete /></el-icon>
                    </button>
                  </div>
                </div>

                <div class="input-footer-hint">
                  <span>{{ composerStatusText }}</span>
                  <button v-if="showThinking || isStreaming || sendingState === 'error'" class="thinking-toggle subtle-text" type="button" @click="showThinking = !showThinking">
                    {{ showThinking ? '深度思考已开启' : '深度思考' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <aside v-if="isFullscreen" class="chat-sidebar">
            <section class="sidebar-section">
              <div class="sidebar-title">文件工作台</div>
              <div v-if="uploadedFiles.length" class="sidebar-file-list">
                <div v-for="file in uploadedFiles" :key="file.id" class="upload-card compact" :class="file.status">
                  <div class="upload-card-icon">
                    <el-icon><component :is="getFileIcon(file)" /></el-icon>
                  </div>
                  <div class="upload-card-main">
                    <div class="upload-card-name-row">
                      <span class="file-name">{{ file.name }}</span>
                      <span class="file-size">{{ formatFileSize(file.size) }}</span>
                    </div>
                    <div class="upload-card-status">
                      <span class="upload-status-badge" :class="file.status">
                        <span>{{ file.statusText || fileStatusLabel(file.status) }}</span>
                      </span>
                    </div>
                  </div>
                  <button class="delete-btn" type="button" aria-label="移除文件" title="移除文件" @click="removeFile(file.id)">
                    <el-icon><Delete /></el-icon>
                  </button>
                </div>
              </div>
              <div v-else class="sidebar-empty">
                <span>暂无文件</span>
                <small>上传简历、JD 或作品材料后，侧栏会显示状态与使用记录。</small>
              </div>
            </section>

            <section class="sidebar-section">
              <div class="sidebar-title">推荐问题</div>
              <div class="sidebar-question-list">
                <button v-for="card in quickQuestionCards" :key="card.prompt" type="button" class="sidebar-question" @click="sendQuickQuestion(card.prompt)">
                  <span>{{ card.title }}</span>
                  <small>{{ card.prompt }}</small>
                </button>
              </div>
            </section>
          </aside>
        </div>

        <template v-if="!isFullscreen">
          <span class="resize-handle bottom-right" aria-hidden="true" @mousedown.prevent="startResize('bottom-right', $event)"></span>
        </template>
      </div>
    </transition>

    <div
      v-show="!dialogVisible"
      class="chatbot-float-btn"
      :class="{ dragging: isDraggingBtn, 'tooltip-right': isTooltipRight }"
      :style="{ left: `${btnPosition.x}px`, top: `${btnPosition.y}px` }"
      role="button"
      tabindex="0"
      :aria-label="`打开 AI 助手，当前状态：${floatButtonStatusText}`"
      @mousedown="onFloatBtnDown"
      @mouseup="onFloatBtnUp"
      @touchstart="onFloatBtnDown"
      @touchend="onFloatBtnUp"
      @keydown.enter.prevent="openChat"
      @keydown.space.prevent="openChat"
    >
      <span class="float-btn-status" :class="assistantPresenceTone"></span>
      <div class="float-btn-icon">
        <el-icon :size="20"><ChatDotRound /></el-icon>
      </div>
      <span class="float-btn-label">AI 助手</span>
      <div class="float-btn-tooltip">
        <span>AI 智能助手</span>
        <small>{{ floatButtonStatusText }}</small>
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
  --surface: rgba(255, 255, 255, 0.92);
  --surface-soft: rgba(248, 250, 252, 0.92);
  --line: rgba(148, 163, 184, 0.18);
  --text-main: #0f172a;
  --text-subtle: #64748b;
  --accent: #2563eb;
  --danger: #dc2626;
  position: fixed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.06), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 250, 252, 0.96) 100%);
  backdrop-filter: blur(18px);
  box-shadow:
    0 20px 50px rgba(15, 23, 42, 0.12),
    0 6px 20px rgba(15, 23, 42, 0.06);
  pointer-events: auto;
  user-select: none;
}

.chat-window.fullscreen {
  border-radius: 0;
  border: none;
  box-shadow: none;
}

.chat-window.dragging,
.chat-window.resizing {
  transition: none;
}

.chat-header {
  min-height: 52px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
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
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: linear-gradient(145deg, rgba(37, 99, 235, 0.12), rgba(15, 23, 42, 0.08));
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.08);
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
  font-size: 14px;
  line-height: 1.2;
  font-weight: 700;
  color: var(--text-main);
}

.assistant-badge {
  height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(37, 99, 235, 0.08);
  color: var(--accent);
  font-size: 11px;
  font-weight: 700;
}

.header-subtitle {
  margin: 4px 0 0;
  color: var(--text-subtle);
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-menu {
  position: relative;
}

.icon-btn,
.tool-btn,
.send-btn,
.delete-btn,
.bubble-tool-btn,
.sidebar-question,
.menu-item,
.inline-action,
.expand-btn {
  border: none;
  outline: none;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    background-color 0.18s ease,
    border-color 0.18s ease,
    color 0.18s ease,
    opacity 0.18s ease;
}

.icon-btn,
.delete-btn,
.bubble-tool-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(248, 250, 252, 0.96);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: var(--text-main);
}

.icon-btn:hover,
.tool-btn:hover,
.delete-btn:hover,
.bubble-tool-btn:hover,
.sidebar-question:hover,
.send-btn:hover,
.inline-action:hover,
.expand-btn:hover {
  transform: translateY(-1px);
}

.icon-btn:hover {
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  border-color: rgba(37, 99, 235, 0.18);
}

.icon-btn.close:hover {
  color: var(--danger);
  border-color: rgba(220, 38, 38, 0.18);
}

.icon-btn:focus-visible,
.tool-btn:focus-visible,
.send-btn:focus-visible,
.delete-btn:focus-visible,
.bubble-tool-btn:focus-visible,
.sidebar-question:focus-visible,
.menu-item:focus-visible,
.inline-action:focus-visible,
.expand-btn:focus-visible,
.chatbot-float-btn:focus-visible {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.header-menu-popover {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 148px;
  padding: 8px;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.12);
  z-index: 20;
}

.menu-item {
  width: 100%;
  min-height: 38px;
  padding: 0 12px;
  border-radius: 10px;
  background: transparent;
  color: var(--text-main);
  font-size: 13px;
  font-weight: 600;
  text-align: left;
}

.menu-item:hover {
  background: rgba(248, 250, 252, 0.9);
}

.menu-item.warning {
  color: #b45309;
}

.chat-body {
  min-height: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  background:
    linear-gradient(180deg, rgba(248, 250, 252, 0.72) 0%, rgba(241, 245, 249, 0.9) 100%),
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.06), transparent 28%);
}

.chat-body.fullscreen {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
}

.chat-main {
  min-width: 0;
  min-height: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-sidebar {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 18px 18px 18px 0;
}

.sidebar-section {
  padding: 16px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.76);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
}

.sidebar-title {
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
}

.sidebar-file-list,
.sidebar-question-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-question {
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid var(--line);
  text-align: left;
  color: var(--text-main);
}

.sidebar-question small {
  display: block;
  margin-top: 6px;
  color: var(--text-subtle);
  line-height: 1.5;
}

.sidebar-empty {
  color: var(--text-subtle);
  font-size: 13px;
  line-height: 1.6;
}

.sidebar-empty small {
  display: block;
  margin-top: 6px;
}

.inline-action {
  margin-left: auto;
  padding: 0;
  background: transparent;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
}

.messages-container {
  flex: 1;
  min-height: 0;
  padding: 14px 12px 12px;
  overflow-y: auto;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.message-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 12px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.message-row.assistant .message-avatar {
  background: rgba(37, 99, 235, 0.1);
  color: var(--accent);
}

.message-row.user .message-avatar {
  background: rgba(15, 23, 42, 0.9);
  color: #fff;
}

.message-main {
  max-width: min(82%, 720px);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message-row.user .message-main {
  align-items: flex-end;
}

.message-meta-line {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-subtle);
  font-size: 12px;
}

.message-row.user .message-meta-line {
  justify-content: flex-end;
}

.message-author {
  font-weight: 700;
  color: var(--text-main);
}

.message-bubble {
  position: relative;
  padding: 14px 16px 14px;
  border-radius: 18px;
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(148, 163, 184, 0.12);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
}

.message-row.assistant .message-bubble {
  border-bottom-left-radius: 8px;
}

.message-row.user .message-bubble {
  background: linear-gradient(180deg, #eef4ff 0%, #e3edff 100%);
  border-color: rgba(59, 130, 246, 0.12);
  color: #16325c;
  border-bottom-right-radius: 8px;
}

.message-bubble.error {
  border-color: rgba(220, 38, 38, 0.18);
  background: rgba(254, 242, 242, 0.96);
  color: #991b1b;
}

.message-tools {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 6px;
  opacity: 0;
  transform: translateY(-4px);
}

.message-row:hover .message-tools {
  opacity: 1;
  transform: translateY(0);
}

.bubble-tool-btn {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  background: rgba(248, 250, 252, 0.9);
  color: var(--text-subtle);
}

.bubble-tool-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.message-content {
  padding-right: 28px;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.message-content.is-collapsed {
  max-height: 220px;
  overflow: hidden;
}

.collapse-mask {
  position: absolute;
  inset: auto 0 44px 0;
  height: 72px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.98) 82%);
  pointer-events: none;
}

.message-row.user .collapse-mask {
  background: linear-gradient(180deg, rgba(227, 237, 255, 0) 0%, rgba(227, 237, 255, 0.98) 82%);
}

.expand-btn {
  margin-top: 10px;
  padding: 0;
  background: transparent;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
}

.message-files {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed rgba(148, 163, 184, 0.3);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-file-item,
.upload-card-name-row,
.upload-card-status {
  display: flex;
  align-items: center;
}

.message-file-item {
  gap: 8px;
  color: inherit;
}

.message-state-tip {
  margin-top: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(248, 250, 252, 0.92);
  color: var(--text-subtle);
}

.message-state-tip.error {
  background: rgba(254, 242, 242, 0.92);
  color: #b91c1c;
}

.message-stream-tag {
  margin-top: 12px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
}

.typing-placeholder {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-subtle);
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  animation: typing 1.2s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.3s;
}

.stream-cursor {
  display: inline-block;
  width: 8px;
  height: 18px;
  margin-left: 4px;
  vertical-align: text-bottom;
  background: currentColor;
  border-radius: 999px;
  animation: cursorBlink 1s infinite steps(1, end);
}

.file-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size,
.message-time {
  color: inherit;
  opacity: 0.68;
  flex-shrink: 0;
}

.upload-preview {
  padding: 0 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.upload-card {
  padding: 12px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.upload-card.compact {
  padding: 10px 12px;
}

.upload-card.parsing {
  border-color: rgba(37, 99, 235, 0.22);
  background: rgba(239, 246, 255, 0.96);
}

.upload-card.used {
  border-color: rgba(22, 163, 74, 0.18);
}

.upload-card.failed {
  border-color: rgba(220, 38, 38, 0.22);
  background: rgba(254, 242, 242, 0.96);
}

.upload-card-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(37, 99, 235, 0.08);
  color: var(--accent);
  flex-shrink: 0;
}

.upload-card.failed .upload-card-icon {
  background: rgba(220, 38, 38, 0.08);
  color: var(--danger);
}

.upload-card-main {
  min-width: 0;
  flex: 1;
}

.upload-card-name-row {
  gap: 10px;
  justify-content: space-between;
}

.upload-card-status {
  margin-top: 8px;
}

.upload-status-badge {
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 700;
  background: rgba(248, 250, 252, 0.92);
  color: var(--text-subtle);
}

.upload-status-badge.added {
  color: var(--text-main);
}

.upload-status-badge.parsing {
  color: var(--accent);
  background: rgba(219, 234, 254, 0.96);
}

.upload-status-badge.used {
  color: #166534;
  background: rgba(220, 252, 231, 0.9);
}

.upload-status-badge.failed {
  color: #b91c1c;
  background: rgba(254, 226, 226, 0.94);
}

.delete-btn {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  background: rgba(248, 250, 252, 0.96);
  color: var(--text-subtle);
  flex-shrink: 0;
}

.delete-btn:hover {
  color: var(--danger);
}

.compact-upload-preview {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.compact-upload-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  max-width: 160px;
  height: 28px;
  padding: 0 8px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(248, 250, 252, 0.92);
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  flex-shrink: 0;
}

.compact-upload-item .file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-main);
}

.compact-upload-item.parsing {
  border-color: rgba(37, 99, 235, 0.22);
  background: rgba(239, 246, 255, 0.96);
}

.compact-upload-item.used {
  border-color: rgba(22, 163, 74, 0.18);
}

.compact-upload-item.failed {
  border-color: rgba(220, 38, 38, 0.22);
  background: rgba(254, 242, 242, 0.96);
}

.delete-btn.tiny {
  width: 20px;
  height: 20px;
  border-radius: 7px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--text-subtle);
  flex-shrink: 0;
  font-size: 12px;
}

.delete-btn.tiny:hover {
  color: var(--danger);
  background: rgba(254, 242, 242, 0.9);
}

.input-panel {
  position: relative;
  margin-top: auto;
  flex-shrink: 0;
  padding: 12px 14px 16px;
  background: linear-gradient(180deg, rgba(241, 245, 249, 0) 0%, rgba(241, 245, 249, 0.92) 28%, rgba(241, 245, 249, 0.98) 100%);
}

.drop-hint {
  position: absolute;
  inset: 0 16px 16px;
  border-radius: 22px;
  border: 1.5px dashed rgba(37, 99, 235, 0.22);
  background: rgba(239, 246, 255, 0.88);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  pointer-events: none;
  transform: scale(0.98);
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.input-panel.is-drag-over .drop-hint {
  opacity: 1;
  transform: scale(1);
}

.input-shell {
  position: relative;
  padding: 12px 14px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
}

.tool-btn.icon-only {
  width: 36px;
  height: 36px;
  padding: 0;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 246, 255, 0.96);
  color: var(--accent);
  margin-top: 0;
}

.tool-btn.icon-only:hover {
  transform: translateY(-1px);
}

.input-left-area {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 0;
  flex: 1;
}

.tool-btn {
  height: 32px;
  padding: 0 10px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(239, 246, 255, 0.96);
  color: var(--accent);
  font-size: 11px;
  font-weight: 600;
}

.tool-btn.subtle {
  background: rgba(248, 250, 252, 0.96);
  color: var(--text-main);
}

.tool-btn.active {
  background: rgba(219, 234, 254, 0.98);
  color: var(--accent);
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.1);
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.input-shell :deep(.el-textarea) {
  height: 100%;
}

.input-shell :deep(.el-textarea__inner) {
  min-height: 36px !important;
  max-height: 120px;
  padding: 8px 12px;
  border-radius: 10px;
  border-color: rgba(148, 163, 184, 0.16);
  box-shadow: none;
  background: rgba(248, 250, 252, 0.88);
  color: var(--text-main);
  font-size: 14px;
  line-height: 1.5;
}

.input-shell :deep(.el-textarea__inner:focus) {
  border-color: rgba(59, 130, 246, 0.38);
  background: #fff;
}

.send-btn {
  width: 38px;
  height: 38px;
  min-height: unset;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: #3b82f6;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
  flex-shrink: 0;
}

.send-btn.compact span {
  display: none;
}

.send-btn.stop {
  background: #dc2626;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.input-footer-hint {
  margin-top: 8px;
  padding-left: 46px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.input-footer-hint span,
.thinking-toggle {
  font-size: 11px;
  color: #94a3b8;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: color 0.18s ease;
}

.thinking-toggle:hover {
  color: var(--accent);
}

.chatbot-float-btn {
  position: fixed;
  width: 72px;
  height: 72px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.95) 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 8px 24px rgba(15, 23, 42, 0.22),
    0 2px 8px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
  cursor: grab;
  pointer-events: auto;
  user-select: none;
  transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.22s ease;
  z-index: 2147483647;
}

.chatbot-float-btn:hover {
  transform: translateY(-4px) scale(1.03);
  box-shadow:
    0 20px 50px rgba(15, 23, 42, 0.28),
    0 4px 12px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.chatbot-float-btn.dragging,
.chatbot-float-btn:active {
  cursor: grabbing;
  transform: scale(1.06);
  transition: transform 0.1s ease;
}

.float-btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.float-btn-label {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
  white-space: nowrap;
  line-height: 1;
}

.float-btn-status {
  position: absolute;
  top: 9px;
  right: 9px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.14), 0 0 6px rgba(34, 197, 94, 0.3);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.55; }
}

.float-btn-status.info {
  background: var(--accent);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.16), 0 0 6px rgba(37, 99, 235, 0.3);
}

.float-btn-status.danger {
  background: var(--danger);
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.16), 0 0 6px rgba(220, 38, 38, 0.3);
}

/* tooltip 默认在左侧 */
.float-btn-tooltip {
  position: absolute;
  right: calc(100% + 14px);
  top: 50%;
  transform: translateY(-50%) translateX(8px);
  min-width: 92px;
  padding: 9px 12px;
  border-radius: 13px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.94) 0%, rgba(30, 41, 59, 0.93) 100%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  line-height: 1.35;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.2);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.float-btn-tooltip::after {
  content: '';
  position: absolute;
  right: -6px;
  top: 50%;
  transform: translateY(-50%) rotate(45deg);
  width: 10px;
  height: 10px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.93) 0%, rgba(15, 23, 42, 0.94) 100%);
  border-radius: 2px;
}

.float-btn-tooltip small {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.65);
}

/* 按钮靠左时 tooltip 显示在右侧 */
.chatbot-float-btn.tooltip-right .float-btn-tooltip {
  right: auto;
  left: calc(100% + 14px);
  transform: translateY(-50%) translateX(-8px);
}

.chatbot-float-btn.tooltip-right .float-btn-tooltip::after {
  right: auto;
  left: -6px;
}

.chatbot-float-btn:hover .float-btn-tooltip,
.chatbot-float-btn:focus-visible .float-btn-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.chatbot-float-btn.tooltip-right:hover .float-btn-tooltip,
.chatbot-float-btn.tooltip-right:focus-visible .float-btn-tooltip {
  transform: translateY(-50%) translateX(0);
}

.resize-handle {
  position: absolute;
  z-index: 4;
}

.resize-handle.bottom-right {
  right: 6px;
  bottom: 6px;
  width: 18px;
  height: 18px;
  cursor: nwse-resize;
}

.resize-handle.bottom-right::before {
  content: '';
  position: absolute;
  right: 2px;
  bottom: 2px;
  width: 12px;
  height: 12px;
  border-right: 2px solid rgba(148, 163, 184, 0.65);
  border-bottom: 2px solid rgba(148, 163, 184, 0.65);
  border-bottom-right-radius: 6px;
}

.assistant-window-enter-active,
.assistant-window-leave-active,
.menu-fade-enter-active,
.menu-fade-leave-active,
.message-fade-enter-active,
.message-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.assistant-window-enter-from,
.assistant-window-leave-to {
  opacity: 0;
  transform: translateY(14px) scale(0.985);
}

.menu-fade-enter-from,
.menu-fade-leave-to,
.message-fade-enter-from,
.message-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.48);
  border: 2px solid transparent;
  background-clip: padding-box;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

:deep(h1),
:deep(h2),
:deep(h3),
:deep(h4) {
  margin: 0 0 10px;
  color: inherit;
  line-height: 1.4;
}

:deep(h1) {
  font-size: 20px;
}

:deep(h2) {
  font-size: 17px;
}

:deep(h3) {
  font-size: 15px;
}

:deep(p) {
  margin: 0 0 10px;
}

:deep(p:last-child) {
  margin-bottom: 0;
}

:deep(ul),
:deep(ol) {
  margin: 0 0 10px;
  padding-left: 18px;
}

:deep(li) {
  margin: 4px 0;
}

:deep(blockquote) {
  margin: 0 0 10px;
  padding: 10px 12px;
  border-left: 3px solid rgba(37, 99, 235, 0.25);
  background: rgba(248, 250, 252, 0.9);
  color: #334155;
  border-radius: 0 12px 12px 0;
}

:deep(pre) {
  margin: 0 0 10px;
  overflow-x: auto;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.92);
  color: #e2e8f0;
}

:deep(code) {
  font-family: Consolas, Monaco, monospace;
  font-size: 12px;
}

:deep(:not(pre) > code) {
  padding: 2px 6px;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.07);
  color: #0f172a;
}

:deep(table) {
  width: 100%;
  margin: 0 0 10px;
  border-collapse: collapse;
  overflow: hidden;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.18);
}

:deep(th),
:deep(td) {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
  text-align: left;
  font-size: 12px;
}

:deep(th) {
  background: rgba(248, 250, 252, 0.94);
  font-weight: 700;
}

:deep(a) {
  color: var(--accent);
  text-decoration: none;
}

:deep(hr) {
  margin: 12px 0;
  border: none;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
}

.rotating {
  animation: spin 1s linear infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.08);
    opacity: 0.78;
  }
}

@keyframes typing {
  0%,
  80%,
  100% {
    transform: scale(0.7);
    opacity: 0.4;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes cursorBlink {
  0%,
  45% {
    opacity: 1;
  }
  46%,
  100% {
    opacity: 0;
  }
}

@keyframes spin {
  from {
    transform: rotate(0);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1024px) {
  .chat-body.fullscreen {
    grid-template-columns: minmax(0, 1fr);
  }

  .chat-sidebar {
    padding: 0 16px 16px;
  }
}

@media (max-width: 768px) {
  .chat-window {
    border-radius: 18px;
  }

  .message-main {
    max-width: 90%;
  }
}

@media (max-width: 480px) {
  .chat-window:not(.fullscreen) {
    width: calc(100vw - 16px) !important;
    height: calc(100vh - 80px) !important;
    left: 8px !important;
    top: auto !important;
    bottom: 64px !important;
  }

  .chat-header {
    padding: 10px 12px;
  }

  .assistant-avatar {
    width: 32px;
    height: 32px;
  }

  .messages-container,
  .input-panel {
    padding-left: 12px;
    padding-right: 12px;
  }

  .input-row {
    gap: 8px;
  }

  .send-btn.compact {
    width: 36px;
    height: 36px;
  }

  .input-footer-hint {
    padding-left: 0;
  }
}

  .float-btn-tooltip {
    display: none;
  }

  .chatbot-float-btn {
    width: 64px;
    height: 64px;
    border-radius: 20px;
  }

  .float-btn-label {
    display: none;
  }

</style>
