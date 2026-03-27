<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { ChatDotRound, Close, Promotion } from '@element-plus/icons-vue'
import VueMarkdown from 'vue-markdown-render'
import { chatBotWelcomeMessage, chatBotReplies } from '@/mock/data'

// 对话框显示状态
const dialogVisible = ref(false)

// 用户输入
const userInput = ref('')

// 聊天记录
interface Message {
  role: 'user' | 'ai'
  content: string
  time: string
}

const messages = ref<Message[]>([
  {
    role: 'ai',
    content: chatBotWelcomeMessage,
    time: getCurrentTime()
  }
])

// 是否正在输入中
const isTyping = ref(false)

// 获取当前时间
function getCurrentTime(): string {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

// 打开/关闭对话框
const toggleDialog = () => {
  dialogVisible.value = !dialogVisible.value
  if (dialogVisible.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

// 关闭对话框
const closeDialog = () => {
  dialogVisible.value = false
}

// 发送消息
const sendMessage = () => {
  if (!userInput.value.trim() || isTyping.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userInput.value,
    time: getCurrentTime()
  })

  const userQuestion = userInput.value
  userInput.value = ''

  nextTick(() => {
    scrollToBottom()
  })

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
    nextTick(() => {
      scrollToBottom()
    })
  }, 1000)
}

// 简单的 AI 回复逻辑（模拟）
const generateAIReply = (question: string): string => {
  const lowerQ = question.toLowerCase()

  if (lowerQ.includes('简历') && (lowerQ.includes('不好') || lowerQ.includes('缺点') || lowerQ.includes('问题'))) {
    return chatBotReplies.resume
  }

  if (lowerQ.includes('岗位') && (lowerQ.includes('适合') || lowerQ.includes('匹配'))) {
    return chatBotReplies.jobMatch
  }

  if (lowerQ.includes('发展') || lowerQ.includes('晋升') || lowerQ.includes('职业规划')) {
    return chatBotReplies.careerPlan
  }

  if (lowerQ.includes('你好') || lowerQ.includes('在吗')) {
    return chatBotReplies.greeting
  }

  return chatBotReplies.default
}

// 滚动到底部
const messagesContainer = ref<HTMLElement | null>(null)
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 按 Enter 发送
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// ============ 拖拽功能 ============
const floatBtnRef = ref<HTMLElement | null>(null)
const btnPosition = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

// 初始化位置（右下角）
const initPosition = () => {
  const padding = 30
  btnPosition.value = {
    x: window.innerWidth - 90 - padding,
    y: window.innerHeight - 90 - padding
  }
}

// 获取事件坐标
const getClientPos = (e: MouseEvent | TouchEvent): { x: number; y: number } => {
  const touchEvent = e as TouchEvent
  const mouseEvent = e as MouseEvent

  const touch = touchEvent.touches?.[0]
  if (touch) {
    return { x: touch.clientX, y: touch.clientY }
  }
  const changedTouch = touchEvent.changedTouches?.[0]
  if (changedTouch) {
    return { x: changedTouch.clientX, y: changedTouch.clientY }
  }
  return { x: mouseEvent.clientX, y: mouseEvent.clientY }
}

// 开始拖拽
const startDrag = (e: MouseEvent | TouchEvent) => {
  if (dialogVisible.value) return // 对话框打开时不可拖拽

  isDragging.value = true
  const pos = getClientPos(e)

  dragOffset.value = {
    x: pos.x - btnPosition.value.x,
    y: pos.y - btnPosition.value.y
  }
}

// 拖拽中
const onDrag = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return

  e.preventDefault()
  const pos = getClientPos(e)

  let newX = pos.x - dragOffset.value.x
  let newY = pos.y - dragOffset.value.y

  // 边界限制（按钮实际尺寸 64px）
  const btnSize = 64
  const maxX = window.innerWidth - btnSize
  const maxY = window.innerHeight - btnSize

  newX = Math.max(0, Math.min(newX, maxX))
  newY = Math.max(0, Math.min(newY, maxY))

  btnPosition.value = { x: newX, y: newY }
}

// 结束拖拽
const endDrag = () => {
  isDragging.value = false
}

// 点击按钮（区分拖拽和点击）
let dragStartTime = 0
let dragStartPos = { x: 0, y: 0 }
const onMouseDown = (e: MouseEvent | TouchEvent) => {
  dragStartTime = Date.now()
  const pos = getClientPos(e)
  dragStartPos = { x: pos.x, y: pos.y }
  startDrag(e)
}

const onMouseUp = (e: MouseEvent | TouchEvent) => {
  const dragDuration = Date.now() - dragStartTime
  const pos = getClientPos(e)

  // 计算位移距离
  const moveDistance = Math.sqrt(
    Math.pow(pos.x - dragStartPos.x, 2) + Math.pow(pos.y - dragStartPos.y, 2)
  )

  endDrag()

  // 如果拖拽时间很短 (< 200ms) 且位移很小 (< 5px)，认为是点击
  if (dragDuration < 200 && moveDistance < 5) {
    toggleDialog()
  }
}

onMounted(() => {
  initPosition()

  // 全局拖拽事件
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', endDrag)
  document.addEventListener('touchmove', onDrag, { passive: false })
  document.addEventListener('touchend', endDrag)

  // 窗口大小改变时重新计算位置
  window.addEventListener('resize', initPosition)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', endDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', endDrag)
  window.removeEventListener('resize', initPosition)
})
</script>

<template>
  <div class="chatbot-wrapper">
    <!-- 右侧对话框（占屏幕 1/3） -->
    <transition name="slide-right">
      <div v-show="dialogVisible" class="chatbot-sidebar">
        <!-- 遮罩层（点击关闭） -->
        <div class="sidebar-overlay" @click="closeDialog"></div>

        <!-- 对话框内容 -->
        <div class="sidebar-content">
          <!-- 头部 -->
          <div class="sidebar-header">
            <div class="header-left">
              <div class="ai-avatar">
                <el-icon :size="22"><ChatDotRound /></el-icon>
              </div>
              <div class="header-info">
                <h4>AI 职业规划助手</h4>
                <span class="status">
                  <span class="status-dot"></span>
                  在线
                </span>
              </div>
            </div>
            <el-icon class="close-icon" @click="closeDialog"><Close /></el-icon>
          </div>

          <!-- 消息区域 -->
          <div ref="messagesContainer" class="messages-container">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message-item"
              :class="msg.role"
            >
              <div class="message-avatar">
                <el-icon v-if="msg.role === 'ai'" :size="16"><ChatDotRound /></el-icon>
                <span v-else>我</span>
              </div>
              <div class="message-content">
                <div class="message-bubble">
                  <VueMarkdown :source="msg.content" />
                </div>
                <span class="message-time">{{ msg.time }}</span>
              </div>
            </div>

            <!-- 输入中提示 -->
            <div v-if="isTyping" class="message-item ai typing">
              <div class="message-avatar">
                <el-icon :size="16"><ChatDotRound /></el-icon>
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
              v-for="question in ['我的简历哪里写得不好？', '这个岗位适合我吗？', '职业发展建议']"
              :key="question"
              class="quick-tag"
              @click="userInput = question; sendMessage()"
            >
              {{ question }}
            </span>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="2"
              placeholder="请输入你的问题..."
              resize="none"
              @keydown="handleKeydown"
            />
            <el-button
              type="primary"
              :disabled="!userInput.trim() || isTyping"
              @click="sendMessage"
            >
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 可拖拽悬浮按钮 -->
    <div
      ref="floatBtnRef"
      class="chatbot-float-btn"
      :class="{ 'active': dialogVisible, 'dragging': isDragging }"
      :style="{ left: btnPosition.x + 'px', top: btnPosition.y + 'px' }"
      @mousedown="onMouseDown"
      @mouseup="onMouseUp"
      @touchstart="onMouseDown"
      @touchend="onMouseUp"
    >
      <el-icon :size="26">
        <ChatDotRound v-if="!dialogVisible" />
        <Close v-else />
      </el-icon>
      <span class="btn-text">AI 助手</span>
    </div>
  </div>
</template>

<style scoped>
.chatbot-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 9999;
}

/* ========== 右侧侧边栏对话框 ========== */
.chatbot-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: flex-end;
  pointer-events: auto;
}

.sidebar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
}

.sidebar-content {
  position: relative;
  width: 33.333%;
  min-width: 380px;
  max-width: 520px;
  height: 100%;
  background: white;
  box-shadow: -4px 0 30px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

/* 头部 */
.sidebar-header {
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.ai-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-info h4 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
}

.status {
  font-size: 12px;
  opacity: 0.9;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #67c23a;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.close-icon {
  cursor: pointer;
  font-size: 22px;
  opacity: 0.85;
  transition: opacity 0.2s;
  padding: 4px;
}

.close-icon:hover {
  opacity: 1;
}

/* 消息区域 */
.messages-container {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f8fafc;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 12px;
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
  max-width: 78%;
}

.message-bubble {
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
}

.message-item.ai .message-bubble {
  background: white;
  color: #303133;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.message-item.user .message-bubble {
  background: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #909399;
  margin-top: 6px;
  display: block;
}

.message-item.user .message-time {
  text-align: right;
}

/* 输入中动画 */
.typing-dots {
  display: flex;
  gap: 5px;
  padding: 6px 10px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}

/* 快捷问题 */
.quick-questions {
  padding: 16px 24px;
  background: white;
  border-top: 1px solid #ebeef5;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  flex-shrink: 0;
}

.quick-tag {
  padding: 10px 16px;
  background: #f0f7ff;
  border-radius: 20px;
  font-size: 13px;
  color: #409eff;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  border: 1px solid transparent;
}

.quick-tag:hover {
  background: #e6f2ff;
  border-color: #409eff;
  transform: translateY(-1px);
}

/* 输入区域 */
.input-area {
  padding: 16px 24px 24px;
  background: white;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-shrink: 0;
  border-top: 1px solid #ebeef5;
}

.input-area :deep(.el-textarea__inner) {
  border-radius: 12px;
  resize: none;
  padding: 12px 16px;
}

.input-area .el-button {
  height: 56px;
  width: 56px;
  border-radius: 12px;
  font-size: 18px;
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

.chatbot-float-btn.active {
  background: linear-gradient(135deg, #f56c6c 0%, #e6a23c 100%);
}

.btn-text {
  font-size: 10px;
  margin-top: 2px;
  font-weight: 500;
}

/* ========== 动画 ========== */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-right-enter-from,
.slide-right-leave-to {
  opacity: 0;
}

.slide-right-enter-from .sidebar-content,
.slide-right-leave-to .sidebar-content {
  transform: translateX(100%);
}

.slide-right-enter-active .sidebar-content,
.slide-right-leave-active .sidebar-content {
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar-content {
    width: 100%;
    min-width: auto;
    max-width: none;
  }

  .chatbot-float-btn {
    width: 56px;
    height: 56px;
  }

  .btn-text {
    font-size: 9px;
  }
}
</style>
