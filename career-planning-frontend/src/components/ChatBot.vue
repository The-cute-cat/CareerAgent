<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { ChatDotRound, Close, Promotion } from '@element-plus/icons-vue'
import VueMarkdown from 'vue-markdown-render'

// 控制对话框显示
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
    content: '你好！我是你的 AI 职业规划助手。我可以帮你：\n• 分析简历优缺点\n• 评估岗位匹配度\n• 提供职业发展建议\n• 解答职业规划相关问题\n\n请问有什么可以帮你的吗？',
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

// Markdown格式文本，需要安装：npm install vue-markdown-render
// 简单的 AI 回复逻辑（模拟）
const generateAIReply = (question: string): string => {
  const lowerQ = question.toLowerCase()

  if (lowerQ.includes('简历') && (lowerQ.includes('不好') || lowerQ.includes('缺点') || lowerQ.includes('问题'))) {
    return `根据常见的简历问题，我建议你检查以下几点：

1. **突出量化成果**：用数字展示成绩，比如"提升效率 30%"
2. **针对性修改**：根据目标岗位调整关键词
3. **简洁明了**：控制在一页纸内，重点突出
4. **格式统一**：保持字体、间距一致

你可以先上传简历，我可以帮你做更详细的分析！`
  }

  if (lowerQ.includes('岗位') && (lowerQ.includes('适合') || lowerQ.includes('匹配'))) {
    return `判断岗位是否适合，可以从这几个维度考虑：

1. **技能匹配度**：你的核心技能是否满足岗位要求
2. **发展空间**：这个岗位能否帮助你成长
3. **兴趣契合**：工作内容是否符合你的职业兴趣
4. **薪资期望**：是否符合你的预期

建议你先去"人岗匹配"页面查看详细的匹配分析报告！`
  }

  if (lowerQ.includes('发展') || lowerQ.includes('晋升') || lowerQ.includes('职业规划')) {
    return `职业发展规划建议：

**短期（1-2 年）**：
- 夯实专业技能，成为团队骨干
- 建立良好的工作口碑

**中期（3-5 年）**：
- 向管理岗或专家岗发展
- 扩大行业人脉网络

**长期（5 年以上）**：
- 成为领域专家或中高层管理者
- 或者考虑创业/转型

你可以查看"发展图谱"了解更详细的晋升路线！`
  }

  if (lowerQ.includes('你好') || lowerQ.includes('在吗')) {
    return '你好！我在的😊 有什么职业规划相关的问题，随时可以问我！'
  }

  return `这是一个很好的问题！

作为你的 AI 职业规划助手，我建议你可以：

1. 先上传简历，获取能力画像
2. 查看人岗匹配结果
3. 阅读生涯报告
4. 探索职业发展图谱

如果你有更具体的问题，比如简历修改建议、岗位评估等，欢迎继续提问！`
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
</script>

<template>
  <div class="chatbot-container">
    <!-- 悬浮按钮 -->
    <div
      class="chatbot-float-btn"
      :class="{ 'active': dialogVisible }"
      @click="toggleDialog"
    >
      <el-icon :size="28">
        <ChatDotRound v-if="!dialogVisible" />
        <Close v-else />
      </el-icon>
      <span class="btn-text">AI 助手</span>
    </div>

    <!-- 对话框 -->
    <transition name="slide-up">
      <div v-show="dialogVisible" class="chatbot-dialog">
        <!-- 对话框头部 -->
        <div class="dialog-header">
          <div class="header-left">
            <div class="ai-avatar">
              <el-icon :size="20"><ChatDotRound /></el-icon>
            </div>
            <div class="header-info">
              <h4>AI 职业规划助手</h4>
              <span class="status">
                <span class="status-dot"></span>
                在线
              </span>
            </div>
          </div>
          <el-icon class="close-icon" @click="toggleDialog"><Close /></el-icon>
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
            placeholder="请输入你的问题，比如：我的简历哪里写得不好？"
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
    </transition>
  </div>
</template>

<style scoped>
.chatbot-container {
  position: fixed;
  right: 30px;
  bottom: 30px;
  z-index: 9999;
}

/* 悬浮按钮 */
.chatbot-float-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #20cab6 100%);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  position: relative;
}

.chatbot-float-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 30px rgba(102, 126, 234, 0.5);
}

.chatbot-float-btn.active {
  background: linear-gradient(135deg, #f56c6c 0%, #e6a23c 100%);
}

.btn-text {
  font-size: 10px;
  margin-top: 2px;
}

/* 对话框 */
.chatbot-dialog {
  position: absolute;
  right: 0;
  bottom: 80px;
  width: 450px;
  height: 580px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 对话框头部 */
.dialog-header {
  padding: 16px 20px;
  background: linear-gradient(135deg, #706969 0%, #454242 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-info h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.status {
  font-size: 12px;
  opacity: 0.9;
  display: flex;
  align-items: center;
  gap: 6px;
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
  font-size: 20px;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.close-icon:hover {
  opacity: 1;
}

/* 消息区域 */
.messages-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f5f7fa;
}

.message-item {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 12px;
}

.message-item.ai .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #06a3f1 100%);
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
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
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
  font-size: 11px;
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
  padding: 12px 20px;
  background: white;
  border-top: 1px solid #ebeef5;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-tag {
  padding: 8px 14px;
  background: #f0f2f5;
  border-radius: 18px;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  flex: 0 0 auto;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.quick-tag:hover {
  background: #e6f2ff;
  color: #409eff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.quick-tag:active {
  transform: translateY(0);
  box-shadow: none;
}

/* 输入区域 */
.input-area {
  padding: 12px 20px 20px;
  background: white;
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-area :deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: none;
}

.input-area .el-button {
  height: 54px;
  width: 54px;
  border-radius: 8px;
}

/* 动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
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
@media (max-width: 480px) {
  .chatbot-container {
    right: 16px;
    bottom: 16px;
  }

  .chatbot-dialog {
    width: calc(100vw - 32px);
    right: 0;
    height: 460px;
  }
}
</style>
