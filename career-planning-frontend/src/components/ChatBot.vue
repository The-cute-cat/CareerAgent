<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { ChatDotRound, Close, Promotion, Paperclip, Delete } from '@element-plus/icons-vue'
import VueMarkdown from 'vue-markdown-render'
import { chatBotWelcomeMessage, chatBotReplies } from '@/mock/data'
import { ElMessage } from 'element-plus'

// 获取当前时间
function getCurrentTime(): string {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

// ============ 配置项 ============
interface ChatConfig {
  autoOpen?: boolean           // 页面加载时自动打开
  autoOpenDelay?: number       // 自动打开延迟（毫秒）
  openOnScroll?: boolean       // 滚动到特定位置时打开
  scrollThreshold?: number     // 滚动阈值（像素）
  openOnExit?: boolean         // 退出意图时打开
}

const props = withDefaults(defineProps<ChatConfig>(), {
  autoOpen: false,
  autoOpenDelay: 3000,
  openOnScroll: false,
  scrollThreshold: 500,
  openOnExit: false
})

// ============ 状态 ============
const dialogVisible = ref(false)
const userInput = ref('')
const isTyping = ref(false)
const isMinimized = ref(false)
const isFullscreen = ref(false)

// 窗口尺寸
const defaultSize = { width: 420, height: 600 }
const currentSize = ref({ ...defaultSize })

// 文件上传相关
interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  url?: string
}
const uploadedFiles = ref<UploadedFile[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)

// 聊天记录
interface Message {
  role: 'user' | 'ai'
  content: string
  time: string
  files?: UploadedFile[]
}

const messages = ref<Message[]>([
  {
    role: 'ai',
    content: chatBotWelcomeMessage,
    time: getCurrentTime()
  }
])

// ============ 窗口拖拽 ============
const chatWindowRef = ref<HTMLElement | null>(null)
const windowPosition = ref({ x: 0, y: 0 })
const isDraggingWindow = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const isHeaderDragging = ref(false)

// 初始化窗口位置（右下角）
const initWindowPosition = () => {
  const padding = 20
  if (isFullscreen.value) {
    windowPosition.value = { x: 0, y: 0 }
  } else {
    windowPosition.value = {
      x: window.innerWidth - currentSize.value.width - padding,
      y: window.innerHeight - currentSize.value.height - padding - 80
    }
  }
}

// 获取事件坐标
const getClientPos = (e: MouseEvent | TouchEvent): { x: number; y: number } => {
  const touchEvent = e as TouchEvent
  const mouseEvent = e as MouseEvent
  const touch = touchEvent.touches?.[0]
  if (touch) return { x: touch.clientX, y: touch.clientY }
  const changedTouch = touchEvent.changedTouches?.[0]
  if (changedTouch) return { x: changedTouch.clientX, y: changedTouch.clientY }
  return { x: mouseEvent.clientX, y: mouseEvent.clientY }
}

// 开始拖拽窗口
const startWindowDrag = (e: MouseEvent | TouchEvent) => {
  isHeaderDragging.value = true
  isDraggingWindow.value = true
  const pos = getClientPos(e)
  dragOffset.value = {
    x: pos.x - windowPosition.value.x,
    y: pos.y - windowPosition.value.y
  }
}

// 拖拽中
const onWindowDrag = (e: MouseEvent | TouchEvent) => {
  if (!isDraggingWindow.value || isFullscreen.value) return
  e.preventDefault()
  const pos = getClientPos(e)
  
  let newX = pos.x - dragOffset.value.x
  let newY = pos.y - dragOffset.value.y
  
  // 边界限制
  const windowWidth = isMinimized.value ? currentSize.value.width : currentSize.value.width
  const windowHeight = isMinimized.value ? 60 : currentSize.value.height
  newX = Math.max(0, Math.min(newX, window.innerWidth - windowWidth))
  newY = Math.max(0, Math.min(newY, window.innerHeight - windowHeight))
  
  windowPosition.value = { x: newX, y: newY }
}

// 结束拖拽
const endWindowDrag = () => {
  isDraggingWindow.value = false
  setTimeout(() => { isHeaderDragging.value = false }, 100)
}

// ============ 按钮拖拽（浮窗按钮） ============
const floatBtnRef = ref<HTMLElement | null>(null)
const btnPosition = ref({ x: 0, y: 0 })
const isDraggingBtn = ref(false)
const btnDragOffset = ref({ x: 0, y: 0 })

const initBtnPosition = () => {
  const padding = 20
  btnPosition.value = {
    x: window.innerWidth - 64 - padding,
    y: window.innerHeight - 64 - padding
  }
}

const startBtnDrag = (e: MouseEvent | TouchEvent) => {
  if (dialogVisible.value) return
  isDraggingBtn.value = true
  const pos = getClientPos(e)
  btnDragOffset.value = {
    x: pos.x - btnPosition.value.x,
    y: pos.y - btnPosition.value.y
  }
}

const onBtnDrag = (e: MouseEvent | TouchEvent) => {
  if (!isDraggingBtn.value) return
  e.preventDefault()
  const pos = getClientPos(e)
  
  let newX = pos.x - btnDragOffset.value.x
  let newY = pos.y - btnDragOffset.value.y
  
  const btnSize = 64
  newX = Math.max(0, Math.min(newX, window.innerWidth - btnSize))
  newY = Math.max(0, Math.min(newY, window.innerHeight - btnSize))
  
  btnPosition.value = { x: newX, y: newY }
}

const endBtnDrag = () => {
  isDraggingBtn.value = false
}

// 点击按钮（区分拖拽和点击）
let btnDragStartTime = 0
let btnDragStartPos = { x: 0, y: 0 }
const onBtnMouseDown = (e: MouseEvent | TouchEvent) => {
  btnDragStartTime = Date.now()
  const pos = getClientPos(e)
  btnDragStartPos = { x: pos.x, y: pos.y }
  startBtnDrag(e)
}

const onBtnMouseUp = (e: MouseEvent | TouchEvent) => {
  const dragDuration = Date.now() - btnDragStartTime
  const pos = getClientPos(e)
  const moveDistance = Math.sqrt(
    Math.pow(pos.x - btnDragStartPos.x, 2) + Math.pow(pos.y - btnDragStartPos.y, 2)
  )
  
  endBtnDrag()
  
  if (dragDuration < 200 && moveDistance < 5) {
    openChat()
  }
}

// ============ 聊天窗口操作 ============
const openChat = () => {
  dialogVisible.value = true
  isMinimized.value = false
  nextTick(() => scrollToBottom())
}

const closeChat = () => {
  dialogVisible.value = false
  uploadedFiles.value = []
}

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
}

const toggleFullscreen = () => {
  if (isMinimized.value) {
    isMinimized.value = false
  }
  isFullscreen.value = !isFullscreen.value
  
  if (isFullscreen.value) {
    // 进入全屏
    const newFullscreenSize = {
      width: window.innerWidth,
      height: window.innerHeight
    }
    currentSize.value = { ...newFullscreenSize }
    windowPosition.value = { x: 0, y: 0 }
  } else {
    // 退出全屏，恢复默认大小
    currentSize.value = { ...defaultSize }
    const padding = 20
    windowPosition.value = {
      x: window.innerWidth - currentSize.value.width - padding,
      y: window.innerHeight - currentSize.value.height - padding - 80
    }
  }
}

// ============ 消息发送 ============
const sendMessage = () => {
  if ((!userInput.value.trim() && uploadedFiles.value.length === 0) || isTyping.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userInput.value,
    time: getCurrentTime(),
    files: uploadedFiles.value.length > 0 ? [...uploadedFiles.value] : undefined
  })

  const userQuestion = userInput.value
  userInput.value = ''
  uploadedFiles.value = []

  nextTick(() => scrollToBottom())

  // 模拟 AI 回复
  isTyping.value = true
  setTimeout(() => {
    const reply = generateAIReply(userQuestion)
    messages.value.push({
      role: 'ai',
      content: reply,
      time: getCurrentTime()
    })
    isTyping.value = false
    nextTick(() => scrollToBottom())
  }, 1000)
}

const generateAIReply = (question: string): string => {
  const lowerQ = question.toLowerCase()
  if (lowerQ.includes('简历') && (lowerQ.includes('不好') || lowerQ.includes('缺点'))) return chatBotReplies.resume
  if (lowerQ.includes('岗位') && (lowerQ.includes('适合') || lowerQ.includes('匹配'))) return chatBotReplies.jobMatch
  if (lowerQ.includes('发展') || lowerQ.includes('晋升') || lowerQ.includes('职业规划')) return chatBotReplies.careerPlan
  if (lowerQ.includes('你好') || lowerQ.includes('在吗')) return chatBotReplies.greeting
  return chatBotReplies.default
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const messagesContainer = ref<HTMLElement | null>(null)

// ============ 文件上传 ============
const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (!files) return

  Array.from(files).forEach(file => {
    // 文件大小限制 10MB
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.warning(`文件 ${file.name} 超过10MB限制`)
      return
    }
    
    // 支持的文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      ElMessage.warning(`文件 ${file.name} 类型不支持`)
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      uploadedFiles.value.push({
        id: Date.now().toString() + Math.random().toString(36).substring(2, 11),
        name: file.name,
        size: file.size,
        type: file.type,
        url: reader.result as string
      })
    }
    reader.readAsDataURL(file)
  })

  // 清空 input 以便重复选择同一文件
  target.value = ''
}

const removeFile = (id: string) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== id)
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// ============ 快捷问题 ============
const quickQuestions = [
  '我的简历哪里写得不好？',
  '这个岗位适合我吗？',
  '职业发展建议'
]

const sendQuickQuestion = (question: string) => {
  userInput.value = question
  sendMessage()
}

// ============ 自动触发逻辑 ============
let scrollHandler: (() => void) | null = null
let exitIntentHandler: ((e: MouseEvent) => void) | null = null

onMounted(() => {
  initWindowPosition()
  initBtnPosition()

  // 全局拖拽事件
  document.addEventListener('mousemove', onWindowDrag)
  document.addEventListener('mouseup', endWindowDrag)
  document.addEventListener('mousemove', onBtnDrag)
  document.addEventListener('mouseup', endBtnDrag)
  document.addEventListener('touchmove', onWindowDrag, { passive: false })
  document.addEventListener('touchend', endWindowDrag)
  document.addEventListener('touchmove', onBtnDrag, { passive: false })
  document.addEventListener('touchend', endBtnDrag)
  window.addEventListener('resize', () => {
    initWindowPosition()
    initBtnPosition()
  })

  // 自动打开
  if (props.autoOpen) {
    setTimeout(() => openChat(), props.autoOpenDelay)
  }

  // 滚动触发
  if (props.openOnScroll) {
    let hasTriggered = false
    scrollHandler = () => {
      if (hasTriggered || dialogVisible.value) return
      if (window.scrollY > props.scrollThreshold) {
        hasTriggered = true
        openChat()
      }
    }
    window.addEventListener('scroll', scrollHandler)
  }

  // 退出意图触发
  if (props.openOnExit) {
    let hasTriggered = false
    exitIntentHandler = (e: MouseEvent) => {
      if (hasTriggered || dialogVisible.value) return
      if (e.clientY < 10) { // 鼠标移到顶部
        hasTriggered = true
        openChat()
      }
    }
    document.addEventListener('mouseleave', exitIntentHandler)
  }
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onWindowDrag)
  document.removeEventListener('mouseup', endWindowDrag)
  document.removeEventListener('mousemove', onBtnDrag)
  document.removeEventListener('mouseup', endBtnDrag)
  document.removeEventListener('touchmove', onWindowDrag)
  document.removeEventListener('touchend', endWindowDrag)
  document.removeEventListener('touchmove', onBtnDrag)
  document.removeEventListener('touchend', endBtnDrag)
  
  if (scrollHandler) window.removeEventListener('scroll', scrollHandler)
  if (exitIntentHandler) document.removeEventListener('mouseleave', exitIntentHandler)
})
</script>

<template>
  <div class="chatbot-wrapper">
    <!-- 浮动聊天窗口 -->
    <transition name="chat-window">
      <div
        v-show="dialogVisible"
        ref="chatWindowRef"
        class="chat-window"
        :class="{ 'minimized': isMinimized, 'fullscreen': isFullscreen }"
        :style="{ 
          left: windowPosition.x + 'px', 
          top: windowPosition.y + 'px',
          width: currentSize.width + 'px',
          height: isMinimized ? '60px' : currentSize.height + 'px'
        }"
      >
        <!-- 可拖拽头部 -->
        <div 
          class="chat-header"
          @mousedown="startWindowDrag"
          @touchstart="startWindowDrag"
        >
          <div class="header-left">
            <div class="ai-avatar">
              <el-icon :size="18"><ChatDotRound /></el-icon>
            </div>
            <div class="header-info">
              <h4>AI 助手</h4>
              <span class="status">
                <span class="status-dot"></span>
                在线
              </span>
            </div>
          </div>
          <div class="header-actions">
            <el-icon class="action-icon" @click.stop="toggleFullscreen" :title="isFullscreen ? '退出全屏' : '全屏'">
              <svg v-if="isFullscreen" viewBox="0 0 1024 1024" width="16" height="16">
                <path fill="currentColor" d="M391 240.9c-.8-6.6-8.9-9.4-13.6-4.7l-43.7 43.7L200 146.3c-3.1-3.1-8.2-3.1-11.3 0l-42.4 42.3c-3.1 3.1-3.1 8.2 0 11.3L280 333.6l-43.7 43.7c-4.7 4.7-2 12.8 4.7 13.6l138.1 19.5 19.5 138.1c.9 6.6 9 9.4 13.6 4.7l43.7-43.7L644.7 754l43.7-43.7c4.7-4.7 2-12.8-4.7-13.6L545.6 677.2l-19.5-138.1c-.9-6.6-9-9.4-13.6-4.7L468.8 578.1 330.7 440l138.1-138.1L391 240.9z"/>
              </svg>
              <svg v-else viewBox="0 0 1024 1024" width="16" height="16">
                <path fill="currentColor" d="M240.9 391l138.1 138.1 138.1-138.1-43.7-43.7c-4.7-4.7-2-12.8 4.7-13.6l138.1-19.5 19.5-138.1c.8-6.6 8.9-9.4 13.6-4.7l43.7 43.7L754 200c3.1-3.1 8.2-3.1 11.3 0l42.4 42.3c3.1 3.1 3.1 8.2 0 11.3L677.2 280l43.7 43.7c4.7 4.7 2 12.8-4.7 13.6l-138.1 19.5-19.5 138.1c-.9 6.6-9 9.4-13.6 4.7l-43.7-43.7L440 643.9l-43.7 43.7c-4.7 4.7-2 12.8 4.7 13.6l138.1 19.5 19.5 138.1c.9 6.6 9 9.4 13.6 4.7l43.7-43.7L754 823.7l43.7 43.7c4.7 4.7 12.8 2 13.6-4.7l19.5-138.1 138.1-19.5c6.6-.9 9.4-9 4.7-13.6l-43.7-43.7L823.7 514l43.7-43.7c3.1-3.1 3.1-8.2 0-11.3l-42.4-42.3c-3.1-3.1-8.2-3.1-11.3 0L754 460.4l-138.1-138.1 138.1-138.1c3.1-3.1 3.1-8.2 0-11.3l-42.4-42.3c-3.1-3.1-8.2-3.1-11.3 0L514 268.6 391 391z"/>
              </svg>
            </el-icon>
            <el-icon class="action-icon" @click.stop="toggleMinimize" :title="isMinimized ? '展开' : '最小化'">
              <span v-if="isMinimized" class="restore-icon">□</span>
              <span v-else class="minimize-icon">−</span>
            </el-icon>
            <el-icon class="action-icon close" @click.stop="closeChat" title="关闭">
              <Close />
            </el-icon>
          </div>
        </div>

        <!-- 聊天内容区 -->
        <div v-show="!isMinimized" class="chat-body">
          <!-- 消息区域 -->
          <div ref="messagesContainer" class="messages-container">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message-item"
              :class="msg.role"
            >
              <div class="message-avatar">
                <el-icon v-if="msg.role === 'ai'" :size="14"><ChatDotRound /></el-icon>
                <span v-else>我</span>
              </div>
              <div class="message-content">
                <div class="message-bubble">
                  <VueMarkdown :source="msg.content" />
                  <!-- 文件附件 -->
                  <div v-if="msg.files && msg.files.length > 0" class="file-attachments">
                    <div v-for="file in msg.files" :key="file.id" class="file-item">
                      <el-icon><Paperclip /></el-icon>
                      <span class="file-name">{{ file.name }}</span>
                      <span class="file-size">({{ formatFileSize(file.size) }})</span>
                    </div>
                  </div>
                </div>
                <span class="message-time">{{ msg.time }}</span>
              </div>
            </div>

            <!-- 输入中提示 -->
            <div v-if="isTyping" class="message-item ai typing">
              <div class="message-avatar">
                <el-icon :size="14"><ChatDotRound /></el-icon>
              </div>
              <div class="message-content">
                <div class="message-bubble">
                  <span class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 快捷问题 -->
          <div class="quick-questions">
            <span
              v-for="question in quickQuestions"
              :key="question"
              class="quick-tag"
              @click="sendQuickQuestion(question)"
            >
              {{ question }}
            </span>
          </div>

          <!-- 已上传文件预览 -->
          <div v-if="uploadedFiles.length > 0" class="uploaded-files">
            <div v-for="file in uploadedFiles" :key="file.id" class="uploaded-file-item">
              <el-icon><Paperclip /></el-icon>
              <span class="file-name">{{ file.name }}</span>
              <el-icon class="delete-icon" @click="removeFile(file.id)"><Delete /></el-icon>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <div class="input-wrapper">
              <el-input
                v-model="userInput"
                type="textarea"
                :rows="2"
                placeholder="请输入你的问题..."
                resize="none"
                @keydown="handleKeydown"
              />
              <div class="input-actions">
                <el-icon class="attach-icon" @click="triggerFileUpload">
                  <Paperclip />
                </el-icon>
                <el-button
                  type="primary"
                  size="small"
                  :disabled="(!userInput.trim() && uploadedFiles.length === 0) || isTyping"
                  @click="sendMessage"
                >
                  <el-icon><Promotion /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 可拖拽悬浮按钮 -->
    <div
      v-show="!dialogVisible"
      ref="floatBtnRef"
      class="chatbot-float-btn"
      :class="{ 'dragging': isDraggingBtn }"
      :style="{ left: btnPosition.x + 'px', top: btnPosition.y + 'px' }"
      @mousedown="onBtnMouseDown"
      @mouseup="onBtnMouseUp"
      @touchstart="onBtnMouseDown"
      @touchend="onBtnMouseUp"
    >
      <el-icon :size="24"><ChatDotRound /></el-icon>
      <span class="btn-text">AI 助手</span>
    </div>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInputRef"
      type="file"
      multiple
      accept=".jpg,.jpeg,.png,.gif,.pdf,.txt,.doc,.docx"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<style scoped>
.chatbot-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 0;
  height: 0;
  z-index: 9999;
}

/* ========== 浮动聊天窗口 (420x600px) ========== */
.chat-window {
  position: fixed;
  width: 420px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  pointer-events: auto;
  z-index: 10000;
}

.chat-window.minimized {
  height: 60px !important;
}

.chat-window.fullscreen {
  border-radius: 0;
}

.chat-window.fullscreen .chat-header {
  border-radius: 0;
}

/* 可拖拽头部 */
.chat-header {
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: grab;
  flex-shrink: 0;
  user-select: none;
}

.chat-header:active {
  cursor: grabbing;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-info h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.status {
  font-size: 11px;
  opacity: 0.9;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #67c23a;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-icon {
  cursor: pointer;
  font-size: 18px;
  opacity: 0.85;
  transition: opacity 0.2s;
  padding: 4px;
}

.action-icon:hover {
  opacity: 1;
}

.action-icon.close:hover {
  color: #f56c6c;
}

.minimize-icon {
  font-size: 20px;
  font-weight: bold;
  line-height: 1;
}

.restore-icon {
  font-size: 14px;
  font-weight: bold;
  line-height: 1;
}

/* 聊天内容区 */
.chat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 消息区域 */
.messages-container {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #f8fafc;
}

.message-item {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 10px;
}

.message-item.ai .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-item.user .message-avatar {
  background: #409eff;
  color: white;
}

.message-content {
  max-width: 75%;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
}

.message-item.ai .message-bubble {
  background: white;
  color: #303133;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-item.user .message-bubble {
  background: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-time {
  font-size: 10px;
  color: #909399;
  margin-top: 4px;
  display: block;
}

.message-item.user .message-time {
  text-align: right;
}

/* 输入中动画 */
.typing-dots {
  display: flex;
  gap: 4px;
  padding: 4px 8px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #909399;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

/* 文件附件 */
.file-attachments {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.9);
}

.message-item.ai .file-item {
  color: #606266;
}

.file-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  opacity: 0.7;
}

/* 快捷问题 */
.quick-questions {
  padding: 10px 12px;
  background: white;
  border-top: 1px solid #ebeef5;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex-shrink: 0;
}

.quick-tag {
  padding: 6px 12px;
  background: #f0f7ff;
  border-radius: 16px;
  font-size: 12px;
  color: #409eff;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  border: 1px solid transparent;
}

.quick-tag:hover {
  background: #e6f2ff;
  border-color: #409eff;
}

/* 已上传文件 */
.uploaded-files {
  padding: 8px 12px;
  background: #f5f7fa;
  border-top: 1px solid #ebeef5;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex-shrink: 0;
}

.uploaded-file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: white;
  border-radius: 12px;
  font-size: 11px;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.uploaded-file-item .file-name {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete-icon {
  cursor: pointer;
  color: #909399;
  font-size: 12px;
}

.delete-icon:hover {
  color: #f56c6c;
}

/* 输入区域 */
.input-area {
  padding: 10px 12px 12px;
  background: white;
  border-top: 1px solid #ebeef5;
  flex-shrink: 0;
}

.input-wrapper {
  position: relative;
}

.input-wrapper :deep(.el-textarea__inner) {
  border-radius: 10px;
  resize: none;
  padding: 10px 80px 10px 12px;
  min-height: 60px !important;
}

.input-actions {
  position: absolute;
  right: 8px;
  bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.attach-icon {
  cursor: pointer;
  font-size: 18px;
  color: #909399;
  padding: 4px;
  transition: color 0.2s;
}

.attach-icon:hover {
  color: #409eff;
}

.input-actions .el-button {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 8px;
}

/* ========== 可拖拽悬浮按钮 ========== */
.chatbot-float-btn {
  position: fixed;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: grab;
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
  pointer-events: auto;
  user-select: none;
  z-index: 10000;
}

.chatbot-float-btn:active,
.chatbot-float-btn.dragging {
  cursor: grabbing;
  transform: scale(1.05);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.5);
}

.btn-text {
  font-size: 10px;
  margin-top: 2px;
  font-weight: 500;
}

/* ========== 动画 ========== */
.chat-window-enter-active,
.chat-window-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chat-window-enter-from,
.chat-window-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 4px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 2px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 响应式 */
@media (max-width: 480px) {
  .chat-window {
    width: calc(100vw - 40px) !important;
    height: 500px !important;
    left: 20px !important;
    right: 20px;
    top: auto !important;
    bottom: 100px !important;
  }
  
  .chat-window.fullscreen {
    width: 100vw !important;
    height: 100vh !important;
    left: 0 !important;
    right: 0 !important;
    top: 0 !important;
    bottom: 0 !important;
    border-radius: 0;
  }
}
</style>
