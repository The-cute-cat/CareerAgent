<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { Close, Microphone } from '@element-plus/icons-vue'
import Live2DCat from '@/components/Live2DCat.vue'
import {
  completeVoiceQuestions,
  voiceScenes,
  type CompleteVoiceAnswers,
  type VoiceSceneKey,
  type VoiceQuestionConfig,
  REQUIRED_VOICE_FIELDS,
  calculateSceneProgress,
  calculateOverallProgress,
  areAllRequiredFieldsFilled,
} from '@/mock/mockdata/VoiceInput_mockdata'

declare global {
  interface Window {
    webkitSpeechRecognition?: SpeechRecognitionConstructor
    SpeechRecognition?: SpeechRecognitionConstructor
  }
}

interface SpeechRecognitionResultLike {
  readonly isFinal: boolean
  readonly 0: {
    readonly transcript: string
  }
}

interface SpeechRecognitionEventLike extends Event {
  readonly results: ArrayLike<SpeechRecognitionResultLike>
}

interface SpeechRecognitionLike {
  lang: string
  interimResults: boolean
  maxAlternatives: number
  onresult: ((event: SpeechRecognitionEventLike) => void) | null
  onerror: (() => void) | null
  onend: (() => void) | null
  start(): void
  stop(): void
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognitionLike
}

type VoiceRole = 'pixie' | 'user'

type VoiceHistoryItem = {
  role: VoiceRole
  text: string
  step: number
  required: boolean
  skipped: boolean
}

type VoiceFormSnapshot = {
  education: string
  major: string[]
  targetJob: string
  targetIndustries: string[]
  skillNames: string[]
  toolNames: string[]
  projectCount: number
  internshipCount: number
}

const props = defineProps<{
  formProgress: number
  profileCompleteness: number
  completedStepCount: number
  resumeUploaded: boolean
  formSnapshot: VoiceFormSnapshot
}>()

const emit = defineEmits<{
  back: []
  'save-to-form': [answers: Record<string, string>]
  'generate-matching': [answers: Record<string, string>]
}>()

const sceneDecoSvg =
  '<svg width="100%" height="100%" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" style="opacity:.2"><circle cx="1300" cy="0" r="130" fill="#a8ebd7"/><rect x="198" y="585" width="122" height="360" rx="12" fill="rgba(148,163,184,.32)"/><circle cx="258" cy="508" r="122" fill="rgba(152,240,217,.52)"/><rect x="620" y="626" width="132" height="320" rx="12" fill="rgba(148,163,184,.28)"/><circle cx="686" cy="548" r="142" fill="rgba(128,230,214,.46)"/><rect x="1134" y="592" width="138" height="352" rx="12" fill="rgba(148,163,184,.26)"/><circle cx="1203" cy="509" r="132" fill="rgba(69,197,216,.30)"/></svg>'

// 场景配置（使用新的5场景配置）
const sceneInfoMap = voiceScenes

// 场景映射（兼容原有组件结构）
const sceneMap = {
  campus: { title: sceneInfoMap.campus.title, className: `scene-${sceneInfoMap.campus.key}`, deco: sceneDecoSvg },
  skill: { title: sceneInfoMap.skill.title, className: `scene-${sceneInfoMap.skill.key}`, deco: sceneDecoSvg },
  experience: { title: sceneInfoMap.experience.title, className: `scene-${sceneInfoMap.experience.key}`, deco: sceneDecoSvg },
  assessment: { title: sceneInfoMap.assessment.title, className: `scene-${sceneInfoMap.assessment.key}`, deco: sceneDecoSvg },
  career: { title: sceneInfoMap.career.title, className: `scene-${sceneInfoMap.career.key}`, deco: sceneDecoSvg },
}

// 使用完整的问答列表（包含必填/非必填标记）
const questions: VoiceQuestionConfig[] = completeVoiceQuestions

// 当前步骤索引
const currentStep = ref(0)
// 对话历史
const history = ref<VoiceHistoryItem[]>([])
// 已收集的答案
const collectedAnswers = ref<Record<string, string>>({})
// 跳过的非必填字段
const skippedFields = ref<Set<string>>(new Set())
// 当前气泡文本
const currentBubbleText = ref('')
// 用户字幕文本
const userSubtitleText = ref('')

// UI 状态控制
const showHistoryModal = ref(false)
const showProfileModal = ref(false)
const showActionPanel = ref(false)
const sceneTitleVisible = ref(false)
const bubbleVisible = ref(false)
const listeningVisible = ref(false)
const subtitleVisible = ref(false)
const subtitleFlash = ref(false)
const thinking = ref(false)
const recording = ref(false)
const speaking = ref(false)
const mascotBouncing = ref(false)
const litCharIndex = ref(-1)

let highlightTimer: number | null = null
let sceneTimer: number | null = null
let bubbleHideTimer: number | null = null
let subtitleTimer: number | null = null
let subtitleFlashTimer: number | null = null
let bounceTimer: number | null = null
let activeRecognition: SpeechRecognitionLike | null = null
let recognitionStoppedByUser = false
let recognitionSessionId = 0

const synth = typeof window !== 'undefined' ? window.speechSynthesis : null

// 计算属性
const currentQuestion = computed(() => questions[currentStep.value] ?? questions[questions.length - 1]!)
const currentScene = computed(() => (sceneMap as Record<string, any>)[currentQuestion.value.scene] || sceneMap.campus)
const bubbleChars = computed(() => [...currentBubbleText.value])
const visibleHistory = computed(() => history.value.slice(-8))
const latestPixieMessage = computed(() => [...history.value].reverse().find(item => item.role === 'pixie') ?? null)

// 完成状态：必填字段全部完成即可
const completed = computed(() => areAllRequiredFieldsFilled(collectedAnswers.value))
const actionDisabled = computed(() => !completed.value || thinking.value || recording.value)

// 总体进度（基于必填字段）
const overallProgress = computed(() => calculateOverallProgress(collectedAnswers.value))

// 当前场景进度
const currentSceneProgress = computed(() =>
  calculateSceneProgress(collectedAnswers.value, currentQuestion.value.scene as VoiceSceneKey)
)

// 麦克风提示文字
const micHintText = computed(() => {
  if (speaking.value) return '点击可打断'
  if (recording.value) return '点击结束'
  if (thinking.value) return '正在整理...'
  if (completed.value) return '已完成采集，请选择下一步操作'
  if (currentQuestion.value.required) return `这个很重要，来聊聊吧~`
  return `想分享就说说看，也可以跳过~`
})

// 是否可以跳过当前问题（仅非必填）
const canSkipCurrent = computed(() => !currentQuestion.value.required)

// 学生画像摘要
const profileSummaryList = computed(() => {
  const items: string[] = []
  if (props.formSnapshot.education) items.push(`学历：${props.formSnapshot.education}`)
  if (props.formSnapshot.major.length) items.push(`专业：${props.formSnapshot.major.join(' / ')}`)
  if (props.formSnapshot.targetJob) items.push(`岗位：${props.formSnapshot.targetJob}`)
  if (props.formSnapshot.skillNames.length) items.push(`技能：${props.formSnapshot.skillNames.slice(0, 3).join('、')}`)
  return items
})

// 各场景的完成情况统计
const sceneStats = computed(() => {
  const stats: Record<string, { total: number; answered: number; label: string }> = {}
  for (const [key, scene] of Object.entries(sceneInfoMap)) {
    const sceneQuestions = questions.filter(q => q.scene === key)
    const answered = sceneQuestions.filter(q => collectedAnswers.value[q.field]).length
    stats[key] = {
      total: sceneQuestions.length,
      answered,
      label: `${answered}/${sceneQuestions.length}`,
    }
  }
  return stats
})

// 画像面板各部分内容
const profileSections = computed(() => [
  {
    title: '📊 采集进度',
    items: [
      `总体完成 ${overallProgress.value}%`,
      `已回答 ${Object.keys(collectedAnswers.value).length}/${questions.length} 题`,
      `必填项 ${Array.from(REQUIRED_VOICE_FIELDS).filter(f => collectedAnswers.value[f]).length}/${REQUIRED_VOICE_FIELDS.size}`,
    ]
  },
  ...Object.entries(sceneInfoMap).map(([key, scene]) => ({
    title: `${scene.icon} ${scene.title}`,
    items: [
      scene.description,
      `进度：${sceneStats[key]?.label || '0/0'}`,
    ]
  })),
  {
    title: '📝 本轮对话摘要',
    items: Object.entries(collectedAnswers.value).map(([key, value]) => {
      const q = questions.find(qu => qu.field === key)
      return `[${q?.required ? '必填' : '选填'}] ${q?.group || key}：${value?.substring(0, 50)}${value && value.length > 50 ? '...' : ''}`
    })
  },
])

// ==================== 工具函数 ====================

function clearTimers(): void {
  if (highlightTimer) window.clearInterval(highlightTimer)
  if (sceneTimer) window.clearTimeout(sceneTimer)
  if (bubbleHideTimer) window.clearTimeout(bubbleHideTimer)
  if (subtitleTimer) window.clearTimeout(subtitleTimer)
  if (subtitleFlashTimer) window.clearTimeout(subtitleFlashTimer)
  if (bounceTimer) window.clearTimeout(bounceTimer)
  highlightTimer = null
  sceneTimer = null
  bubbleHideTimer = null
  subtitleTimer = null
  subtitleFlashTimer = null
  bounceTimer = null
}

function addHistory(role: VoiceRole, text: string, step: number, required: boolean, skipped = false): void {
  history.value.push({ role, text, step, required, skipped })
}

function setSceneTitle(): void {
  sceneTitleVisible.value = true
  if (sceneTimer) window.clearTimeout(sceneTimer)
  sceneTimer = window.setTimeout(() => {
    sceneTitleVisible.value = false
    sceneTimer = null
  }, 1800)
}

function bounceMascot(): void {
  mascotBouncing.value = true
  if (bounceTimer) window.clearTimeout(bounceTimer)
  bounceTimer = window.setTimeout(() => {
    mascotBouncing.value = false
    bounceTimer = null
  }, 620)
}

function showBubble(text: string): void {
  currentBubbleText.value = text
  bubbleVisible.value = true
  litCharIndex.value = -1
}

function hideBubble(): void {
  bubbleVisible.value = false
}

function showUserSubtitle(text: string): void {
  userSubtitleText.value = text
  subtitleVisible.value = true
  subtitleFlash.value = true
  if (subtitleFlashTimer) window.clearTimeout(subtitleFlashTimer)
  if (subtitleTimer) window.clearTimeout(subtitleTimer)
  subtitleFlashTimer = window.setTimeout(() => {
    subtitleFlash.value = false
    subtitleFlashTimer = null
  }, 1400)
  subtitleTimer = window.setTimeout(() => {
    subtitleVisible.value = false
    subtitleTimer = null
  }, 3200)
}

function scheduleHighlight(text: string): void {
  if (highlightTimer) window.clearInterval(highlightTimer)
  let index = 0
  highlightTimer = window.setInterval(() => {
    litCharIndex.value = index
    index += 1
    if (index >= Math.max(text.length, 1)) {
      if (highlightTimer) window.clearInterval(highlightTimer)
      highlightTimer = null
    }
  }, 55)
}

function revealAll(): void {
  litCharIndex.value = bubbleChars.value.length - 1
}

function stopSpeech(): void {
  if (highlightTimer) {
    window.clearInterval(highlightTimer)
    highlightTimer = null
  }
  synth?.cancel()
  speaking.value = false
  revealAll()
  if (bubbleHideTimer) window.clearTimeout(bubbleHideTimer)
  bubbleHideTimer = window.setTimeout(() => {
    if (!speaking.value) hideBubble()
    bubbleHideTimer = null
  }, 800)
}

function speak(text: string): void {
  if (!synth) {
    showBubble(text)
    revealAll()
    return
  }
  synth.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'zh-CN'
  utterance.rate = 0.96
  utterance.pitch = 1.08
  utterance.onstart = () => {
    speaking.value = true
    showBubble(text)
    scheduleHighlight(text)
  }
  utterance.onend = () => {
    speaking.value = false
    revealAll()
    if (bubbleHideTimer) window.clearTimeout(bubbleHideTimer)
    bubbleHideTimer = window.setTimeout(() => {
      if (!speaking.value && !thinking.value) hideBubble()
      bubbleHideTimer = null
    }, 2200)
  }
  synth.speak(utterance)
}

// ==================== 核心对话逻辑 ====================

async function startConversation(): Promise<void> {
  const firstQuestion = questions[0]!
  setSceneTitle()
  addHistory('pixie', firstQuestion.question, 0, firstQuestion.required)
  showBubble(firstQuestion.question)
  await nextTick()
  window.setTimeout(() => speak(firstQuestion.question), 120)
}

/** 构建回复文本 */
function buildReply(): string {
  // 检查是否所有问题都已回答或跳过
  const remainingRequired = questions.filter(q => q.required && !collectedAnswers.value[q.field])
  
  // 找下一个未回答的问题
  const nextUnansweredIndex = questions.findIndex((q, idx) => 
    idx > currentStep.value && !collectedAnswers.value[q.field]
  )

  if (nextUnansweredIndex === -1 && remainingRequired.length === 0) {
    // 所有必填问题都已完成
    const answeredCount = Object.keys(collectedAnswers.value).length
    return `太棒了！我已经收集了 ${answeredCount} 个问题的信息，其中所有必填项都已填写完毕。接下来你可以选择「保存到表单」或「生成人岗匹配结果」！`
  }

  if (nextUnansweredIndex === -1) {
    // 还有必填项没填完，找第一个未答的必填项
    const nextRequired = questions.find(q => q.required && !collectedAnswers.value[q.field])
    if (nextRequired) {
      return `好的。我们还有个重要的信息需要补充——${nextRequired.question}`
    }
  }

  const nextQuestion = questions[nextUnansweredIndex]!
  const intros = ['收到，记下来了！', '很好，这部分已经清晰了。', '我已经抓到重点啦。', '这段经历很有参考价值。', '了解，继续下一个~']
  const prefix = intros[currentStep.value % intros.length]
  const hint = nextQuestion.required ? '（这个需要你回答哦）' : '（不想说可以跳过）'
  return `${prefix}\n${hint}${nextQuestion.question}`
}

/** 推进对话 */
function advanceConversation(text: string): void {
  addHistory('user', text, currentStep.value, currentQuestion.value.required)
  collectedAnswers.value = { ...collectedAnswers.value, [currentQuestion.value.field]: text }
  thinking.value = true
  bounceMascot()
  window.setTimeout(() => {
    thinking.value = false
    const reply = buildReply()
    addHistory('pixie', reply, currentStep.value, false)
    
    // 查找下一个未答问题
    const nextUnansweredIndex = questions.findIndex((q, idx) => 
      idx > currentStep.value && !collectedAnswers.value[q.field]
    )
    
    if (nextUnansweredIndex !== -1) {
      currentStep.value = nextUnansweredIndex
      setSceneTitle()
    } else {
      // 检查是否还有必填项未答
      const remainingRequired = questions.find(q => q.required && !collectedAnswers.value[q.field])
      if (remainingRequired) {
        const reqIdx = questions.indexOf(remainingRequired)
        currentStep.value = reqIdx
        setSceneTitle()
      } else {
        showActionPanel.value = true
      }
    }
    
    showBubble(reply)
    speak(reply)
  }, 780)
}

/** 跳过当前问题（仅限非必填）*/
function skipCurrentQuestion(): void {
  if (canSkipCurrent.value && !recording.value && !thinking.value) {
    const question = currentQuestion.value
    const skipHint = question.skipHint || `已跳过「${question.group || question.field}」`
    skippedFields.value = new Set([...skippedFields.value, question.field])
    
    addHistory('用户', `[跳过] ${skipHint}`, currentStep.value, question.required, true)
    thinking.value = true
    bounceMascot()
    
    window.setTimeout(() => {
      thinking.value = false
      const reply = buildReply()
      addHistory('pixie', reply, currentStep.value, false)
      
      // 移动到下一题
      const nextUnansweredIndex = questions.findIndex((q, idx) => 
        idx > currentStep.value && !collectedAnswers.value[q.field]
      )
      
      if (nextUnansweredIndex !== -1) {
        currentStep.value = nextUnansweredIndex
        setSceneTitle()
      } else {
        const remainingRequired = questions.find(q => q.required && !collectedAnswers.value[q.field])
        if (remainingRequired) {
          currentStep.value = questions.indexOf(remainingRequired)
          setSceneTitle()
        } else {
          showActionPanel.value = true
        }
      }
      
      showBubble(reply)
      speak(reply)
    }, 500)
  }
}

/** 保存到表单 */
function handleSaveToForm(): void {
  // 只有未完成时才阻止，语音播放中允许点击
  if (!completed.value || thinking.value || recording.value) return
  showActionPanel.value = false
  const reply = '好的，我先帮你把刚刚收集到的信息保存到表单里，然后带你跳转回去查看。'
  addHistory('pixie', reply, currentStep.value, false)
  showBubble(reply)
  speak(reply)
  // 延迟跳转，让用户听到回复并看到气泡提示
  window.setTimeout(() => {
    emit('save-to-form', { ...collectedAnswers.value })
  }, 1500)
}

/** 生成人岗匹配结果并跳转 */
function handleGenerateMatching(): void {
  // 只有未完成时才阻止，语音播放中允许点击
  if (!completed.value || thinking.value || recording.value) return
  showActionPanel.value = false
  const reply = '好的，我现在就根据这些信息生成人岗匹配结果，马上带你过去看看。'
  addHistory('pixie', reply, currentStep.value, false)
  showBubble(reply)
  speak(reply)
  // 延迟跳转，让用户听到回复并看到气泡提示
  window.setTimeout(() => {
    emit('generate-matching', { ...collectedAnswers.value })
  }, 1800)
}

/** 模拟语音识别（返回示例答案）*/
function mockRecognize(): Promise<string> {
  return new Promise(resolve => {
    window.setTimeout(() => resolve(currentQuestion.value.sampleAnswer), 1100)
  })
}

/** 使用浏览器原生语音识别 */
function recognizeByBrowser(): Promise<string | null> {
  const RecognitionCtor = window.SpeechRecognition ?? window.webkitSpeechRecognition
  if (!RecognitionCtor) return Promise.resolve(null)

  return new Promise(resolve => {
    const sessionId = ++recognitionSessionId
    const recognition = new RecognitionCtor()
    activeRecognition = recognition
    recognitionStoppedByUser = false
    let resolved = false

    const finish = (value: string | null) => {
      if (resolved) return
      resolved = true
      if (activeRecognition === recognition) {
        activeRecognition = null
      }
      resolve(value)
    }

    recognition.lang = 'zh-CN'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onresult = event => {
      const transcript = event.results[0]?.[0]?.transcript?.trim() ?? ''
      finish(transcript || null)
    }

    recognition.onerror = () => {
      finish(null)
    }

    recognition.onend = () => {
      if (recognitionStoppedByUser && sessionId === recognitionSessionId) {
        recognitionStoppedByUser = false
        finish('')
        return
      }
      finish(null)
    }

    recognition.start()
  })
}

/** 停止录音 */
function stopRecording(): void {
  recognitionStoppedByUser = true
  recording.value = false
  listeningVisible.value = false

  try {
    activeRecognition?.stop()
  } catch {
    activeRecognition = null
  }
}

/** 麦克风按钮点击事件 */
async function onMic(): Promise<void> {
  if (speaking.value) {
    stopSpeech()
    return
  }
  if (recording.value) {
    stopRecording()
    return
  }
  if (thinking.value || completed.value) return
  recording.value = true
  listeningVisible.value = true
  hideBubble()
  const browserText = await recognizeByBrowser()

  if (browserText === '') {
    return
  }

  const text = browserText || (await mockRecognize())
  listeningVisible.value = false
  recording.value = false
  showUserSubtitle(text)
  advanceConversation(text)
}

/** 重置对话 */
function restartConversation(): void {
  clearTimers()
  synth?.cancel()
  currentStep.value = 0
  history.value = []
  collectedAnswers.value = {}
  skippedFields.value = new Set()
  showActionPanel.value = false
  currentBubbleText.value = ''
  userSubtitleText.value = ''
  thinking.value = false
  recording.value = false
  speaking.value = false
  listeningVisible.value = false
  recognitionStoppedByUser = false
  activeRecognition?.stop()
  activeRecognition = null
  subtitleVisible.value = false
  bubbleVisible.value = false
  startConversation()
}

onMounted(() => {
  window.setTimeout(() => {
    startConversation()
  }, 260)
})

onBeforeUnmount(() => {
  clearTimers()
  recognitionStoppedByUser = true
  activeRecognition?.stop()
  synth?.cancel()
})
</script>

<template>
  <section class="pixie-scene-page" :class="currentScene.className">
    <div class="scene-bg"></div>
    <div class="scene-deco" v-html="currentScene.deco"></div>

    <!-- 场景标题 -->
    <div class="scene-title" :class="{ show: sceneTitleVisible }">
      <span class="scene-title-text">{{ currentScene.title }}</span>
    </div>

    <!-- 左侧对话历史面板 -->
    <div class="side-panel side-panel-left">
      <div class="side-panel-inner side-panel-card history-card" @click="showHistoryModal = true">
        <p class="panel-caption">对话历史</p>
        <div class="panel-scroll">
          <span v-if="!history.length" class="panel-empty">等待对话开始...</span>
          <div v-for="(item, index) in visibleHistory" :key="`${item.role}-${index}-${item.text}`" 
               :class="['history-item', { 'skipped-item': item.skipped }]">
            <div class="hi-step">{{ item.role === 'pixie' ? `✨ 第${item.step + 1}轮` : `🎙 第${item.step + 1}轮` }}</div>
            <div :class="item.role === 'pixie' ? 'hi-q' : 'hi-a'">{{ item.text }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧学生画像面板 -->
    <div class="side-panel side-panel-right" @click="showProfileModal = true">
      <div class="side-panel-inner side-panel-card profile-card">
        <p class="panel-caption">学生画像</p>
        <div class="panel-scroll">
          <span v-if="!profileSummaryList.length" class="panel-empty">等待对话开始...</span>
          <div v-for="item in profileSummaryList.slice(0, 3)" :key="item" class="profile-chip">{{ item }}</div>
        </div>
      </div>
    </div>

    <!-- 浮动按钮 -->
    <button type="button" class="floating-btn floating-back" @click="emit('back')">返回表单</button>
    <button type="button" class="floating-btn floating-reset" @click="restartConversation">重新开始</button>

    <!-- 进度指示器 -->
    <div class="progress-indicator">
      <div class="progress-bar-container">
        <div class="progress-bar-fill" :style="{ width: `${overallProgress}%` }"></div>
      </div>
      <span class="progress-text">{{ overallProgress }}% 完成</span>
    </div>

    <!-- 当前问题类型标签 -->
    <div class="question-badge" :class="{ required: currentQuestion.required }">
      {{ currentQuestion.required ? '⚡ 必填' : '💡 选填' }} · {{ currentQuestion.group || '其他' }}
    </div>

    <!-- Pixie 气泡对话框 -->
    <div class="elf-bubble" :class="bubbleVisible ? 'show' : 'hide'">
      <div class="elf-bubble-inner">
        <p class="elf-bubble-text">
          <span v-for="(char, index) in bubbleChars" :key="`${index}-${char}`" class="ec" :class="{ lit: index <= litCharIndex }">
            {{ char }}
          </span>
        </p>
      </div>
    </div>

    <!-- 思考中动画 -->
    <div class="thinking-dots" :class="{ show: thinking }">
      <div class="thinking-dot"></div>
      <div class="thinking-dot"></div>
      <div class="thinking-dot"></div>
    </div>

    <!-- Live2D 角色 -->
    <div class="mascot-wrap">
      <div class="mascot-live2d" :class="{ bounce: mascotBouncing }">
        <Live2DCat :speaking-text="currentBubbleText" :active="speaking || thinking" />
      </div>
      <div class="wave-wrap">
        <div class="wave-bar" :class="{ speaking: speaking || thinking }"></div>
        <div class="wave-bar" :class="{ speaking: speaking || thinking }"></div>
        <div class="wave-bar" :class="{ speaking: speaking || thinking }"></div>
      </div>
    </div>

    <!-- 操作面板（完成后显示）-->
    <transition name="dialog-fade">
      <div v-if="showActionPanel" class="action-panel">
        <div class="action-panel__title">✅ 信息采集完成</div>
        <div class="action-panel__desc">
          已收集 {{ Object.keys(collectedAnswers).length }} 项信息，{{ REQUIRED_VOICE_FIELDS.size }} 项必填信息已全部填写。
          你可以选择保存到表单，或直接生成人岗匹配结果。
        </div>
        <div class="action-panel__buttons">
          <el-button 
            type="primary" 
            size="large" 
            :disabled="!completed || thinking || recording" 
            @click="handleSaveToForm"
          >
            💾 保存到表单
          </el-button>
          <el-button 
            type="success" 
            size="large" 
            plain 
            :disabled="!completed || thinking || recording" 
            @click="handleGenerateMatching"
          >
            🎯 生成人岗匹配
          </el-button>
        </div>
      </div>
    </transition>

    <!-- 跳过按钮（仅非必填时显示）-->
    <transition name="fade-slide">
      <button v-if="canSkipCurrent && !completed && !recording && !thinking && !speaking" 
              type="button" class="skip-btn" @click="skipCurrentQuestion">
        ⏭️ 跳过此题
      </button>
    </transition>

    <!-- 用户字幕 -->
    <div class="user-subtitle" :class="[{ show: subtitleVisible }, { 'subtitle-flash': subtitleFlash }]">
      <div class="user-subtitle-inner">{{ userSubtitleText }}</div>
    </div>

    <!-- 聆听中指示器 -->
    <div class="listening-indicator" :class="{ show: listeningVisible }">
      <div class="listening-dot"></div>
      <div class="listening-dot"></div>
      <div class="listening-dot"></div>
      <span class="listening-text">聆听中...</span>
    </div>

    <!-- 麦克风提示 -->
    <div class="mic-hint">{{ micHintText }}</div>
    <button type="button" class="mic-btn" :class="{ active: recording }" @click="onMic">
      <el-icon v-if="!recording && !speaking"><Microphone /></el-icon>
      <span v-else class="mic-stop"></span>
    </button>

    <!-- 对话历史弹窗 -->
    <transition name="dialog-fade">
      <div v-if="showHistoryModal" class="history-modal-overlay" @click.self="showHistoryModal = false">
        <div class="history-modal">
          <div class="history-modal-header">
            <span class="modal-title">完整对话记录</span>
            <button type="button" class="modal-close-btn" @click="showHistoryModal = false">
              <el-icon><Close /></el-icon>
            </button>
          </div>
          <div class="history-modal-body">
            <div v-for="(item, index) in history" :key="`modal-${index}`" 
                 :class="['hm-item', { 'skipped-item': item.skipped }]">
              <div class="hm-step">{{ item.role === 'pixie' ? 'Pixie' : '你' }} · 第{{ item.step + 1 }}轮{{ item.skipped ? ' (跳过)' : '' }}</div>
              <div :class="item.role === 'pixie' ? 'hm-q' : 'hm-a'">{{ item.text }}</div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 学生画像弹窗 -->
    <transition name="dialog-fade">
      <div v-if="showProfileModal" class="history-modal-overlay" @click.self="showProfileModal = false">
        <div class="history-modal history-modal--wide">
          <div class="history-modal-header">
            <span class="modal-title">完整学生画像</span>
            <button type="button" class="modal-close-btn" @click="showProfileModal = false">
              <el-icon><Close /></el-icon>
            </button>
          </div>
          <div class="history-modal-body">
            <!-- 概览卡片 -->
            <div class="profile-overview">
              <div class="profile-overview-card">
                <strong>{{ overallProgress }}%</strong>
                <span>总体完成度</span>
              </div>
              <div class="profile-overview-card">
                <strong>{{ Object.keys(collectedAnswers).length }}</strong>
                <span>已回答问题</span>
              </div>
              <div class="profile-overview-card">
                <strong>{{ REQUIRED_VOICE_FIELDS.size }}</strong>
                <span>必填项总数</span>
              </div>
            </div>

            <!-- 各部分详情 -->
            <div v-for="section in profileSections" :key="section.title" class="profile-section">
              <div class="profile-section-title">{{ section.title }}</div>
              <div class="profile-fields-grid">
                <span v-for="item in section.items" :key="item" class="profile-tag-wide">{{ item }}</span>
                <span v-if="!section.items.length" class="panel-empty">暂无内容</span>
              </div>
            </div>

            <!-- 最近一轮引导 -->
            <div v-if="latestPixieMessage" class="profile-section">
              <div class="profile-section-title">最近一轮引导</div>
              <div class="profile-field-value">{{ latestPixieMessage.text }}</div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </section>
</template>

<style scoped>
* { box-sizing: border-box; }

.pixie-scene-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  overflow: hidden;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.scene-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.55), rgba(255, 255, 255, 0.08));
}

/* 5种场景渐变背景 */
.scene-campus { background: linear-gradient(180deg, #e8f4fd 0%, #a8d8f0 58%, #78c9f5 100%); }
.scene-skill { background: linear-gradient(180deg, #fef3e2 0%, #fdd8a8 58%, #f9c46b 100%); }
.scene-experience { background: linear-gradient(180deg, #e8fbe8 0%, #b8e8b8 58%, #8cd48c 100%); }
.scene-assessment { background: linear-gradient(180deg, #f3e8fd 0%, #d4b8f5 58%, #b89cf0 100%); }
.scene-career { background: linear-gradient(180deg, #fee8e8 0%, #f8b4b4 58%, #f09090 100%); }

.scene-deco {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.scene-title {
  position: absolute;
  top: 18px;
  left: 50%;
  z-index: 8;
  opacity: 0;
  transform: translateX(-50%);
  transition: opacity 0.45s ease;
}
.scene-title.show { opacity: 1; }

.scene-title-text {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 96px;
  height: 34px;
  padding: 0 18px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.74);
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.18em;
}

.side-panel {
  position: absolute;
  top: 18px;
  z-index: 8;
}
.side-panel-left { left: 18px; }
.side-panel-right { right: 18px; cursor: pointer; }

.side-panel-inner {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.06);
}

.side-panel-card {
  width: 314px;
  min-height: 110px;
  padding: 14px 0 14px 16px;
}

.profile-card {
  width: 112px;
  min-height: 84px;
}

.panel-caption {
  margin: 0 14px 8px 0;
  color: #a4afbb;
  font-size: 10px;
  font-weight: 700;
}

.panel-scroll {
  max-height: 160px;
  overflow-y: auto;
  padding-right: 12px;
}

.panel-empty {
  color: #cfd8e3;
  font-size: 10px;
  font-style: italic;
}

.history-item { margin-bottom: 6px; }
.history-item.skipped-item .hi-a { opacity: 0.5; font-style: italic; }

.hi-step {
  margin-bottom: 2px;
  color: #aebac8;
  font-size: 10px;
}

.hi-q, .hi-a {
  color: #55697d;
  font-size: 11px;
  line-height: 1.45;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.hi-a { color: #5b6f8a; }

.profile-chip {
  margin-bottom: 8px;
  color: #95a4b6;
  font-size: 10px;
  line-height: 1.5;
}

.floating-btn {
  position: absolute;
  top: 20px;
  z-index: 8;
  border: none;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.76);
  color: #66798e;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(33, 89, 147, 0.08);
}
.floating-back { left: 352px; }
.floating-reset { right: 146px; }

/* 进度指示器 */
.progress-indicator {
  position: absolute;
  top: 72px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 8;
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar-container {
  width: 200px;
  height: 6px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #6678ff, #4d5ff5);
  border-radius: 3px;
  transition: width 0.35s ease;
}

.progress-text {
  color: #55697d;
  font-size: 11px;
  font-weight: 700;
}

/* 问题标签 */
.question-badge {
  position: absolute;
  top: 92px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 8;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.question-badge.required {
  background: rgba(239, 68, 68, 0.15);
  color: #dc2626;
}

.question-badge:not(.required) {
  background: rgba(59, 130, 246, 0.15);
  color: #2563eb;
}

.elf-bubble {
  position: absolute;
  bottom: calc(36% + 230px);
  left: 50%;
  z-index: 6;
  width: min(520px, calc(100vw - 72px));
  opacity: 0;
  transform: translateX(-50%);
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.elf-bubble.show { opacity: 1; transform: translateX(-50%) translateY(0); }
.elf-bubble.hide { opacity: 0; transform: translateX(-50%) translateY(-10px); }

.elf-bubble-inner {
  position: relative;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}
.elf-bubble-inner::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid rgba(255, 255, 255, 0.94);
}

.elf-bubble-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
  color: #66778d;
}

.ec {
  color: #97a6b7;
  transition: color 0.25s ease, font-weight 0.25s ease;
}
.ec.lit { color: #2563eb; font-weight: 700; }

.thinking-dots {
  position: absolute;
  bottom: calc(36% + 204px);
  left: 50%;
  z-index: 6;
  display: none;
  gap: 8px;
  transform: translateX(-50%);
}
.thinking-dots.show { display: flex; }

.thinking-dot, .listening-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4f8cff;
  animation: ldot 0.8s ease-in-out infinite;
}
.thinking-dot:nth-child(2),
.listening-dot:nth-child(2) { animation-delay: 0.12s; }
.thinking-dot:nth-child(3),
.listening-dot:nth-child(3) { animation-delay: 0.24s; }

.mascot-wrap {
  position: absolute;
  bottom: 36%;
  left: 50%;
  z-index: 5;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform: translateX(-50%);
}

.mascot-live2d {
  width: 220px;
  height: 280px;
}
.mascot-live2d.bounce { animation: mascotBounce 0.55s ease; }

.wave-wrap {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 4px;
  height: 28px;
  margin-top: 8px;
}

.wave-bar {
  width: 4px;
  height: 6px;
  border-radius: 2px;
  background: linear-gradient(180deg, #60a5fa, #2563eb);
}
.wave-bar.speaking:nth-child(1) { animation: w1 0.5s ease-in-out infinite; }
.wave-bar.speaking:nth-child(2) { animation: w2 0.5s ease-in-out infinite 0.12s; }
.wave-bar.speaking:nth-child(3) { animation: w3 0.5s ease-in-out infinite 0.24s; }

.action-panel {
  position: absolute;
  bottom: 232px;
  left: 50%;
  z-index: 7;
  width: min(600px, calc(100vw - 32px));
  padding: 22px 24px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.18);
  transform: translateX(-50%);
  backdrop-filter: blur(14px);
}

.action-panel__title {
  color: #0f172a;
  font-size: 19px;
  font-weight: 800;
}

.action-panel__desc {
  margin-top: 10px;
  color: #475569;
  font-size: 14px;
  line-height: 1.65;
}

.action-panel__buttons {
  display: flex;
  gap: 14px;
  margin-top: 20px;
}

/* 跳过按钮 */
.skip-btn {
  position: absolute;
  bottom: 196px;
  right: 80px;
  z-index: 7;
  padding: 8px 18px;
  border: 1px solid rgba(150, 163, 184, 0.4);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.85);
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.25s ease;
}
.skip-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  color: #66798e;
  border-color: rgba(150, 163, 184, 0.6);
  transform: scale(1.03);
}

.user-subtitle {
  position: absolute;
  bottom: 146px;
  left: 50%;
  z-index: 6;
  opacity: 0;
  transform: translateX(-50%);
  transition: opacity 0.32s ease;
}
.user-subtitle.show { opacity: 1; }

.user-subtitle-inner {
  max-width: 80vw;
  padding: 10px 24px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 15px;
  line-height: 1.6;
  text-align: center;
}
.subtitle-flash .user-subtitle-inner { animation: greenFlash 1.4s ease-out forwards; }

.listening-indicator {
  position: absolute;
  bottom: 146px;
  left: 50%;
  z-index: 6;
  display: none;
  align-items: center;
  gap: 8px;
  transform: translateX(-50%);
}
.listening-indicator.show { display: flex; }

.listening-text { color: rgba(255, 255, 255, 0.72); font-size: 12px; }

.mic-hint {
  position: absolute;
  bottom: 106px;
  left: 50%;
  z-index: 6;
  color: rgba(90, 114, 138, 0.78);
  font-size: 12px;
  font-weight: 600;
  transform: translateX(-50%);
}

.mic-btn {
  position: absolute;
  bottom: 28px;
  left: 50%;
  z-index: 6;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 68px;
  height: 68px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #6678ff, #4d5ff5);
  color: #fff;
  font-size: 28px;
  box-shadow: 0 14px 34px rgba(79, 93, 255, 0.28);
  cursor: pointer;
  transform: translateX(-50%);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.mic-btn:hover { transform: translateX(-50%) scale(1.05); box-shadow: 0 18px 40px rgba(79, 93, 255, 0.34); }
.mic-btn.active { animation: micPulse 1s ease-in-out infinite; }

.mic-stop {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  background: currentColor;
}

.history-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(11, 27, 48, 0.3);
  backdrop-filter: blur(4px);
}

.history-modal {
  width: min(580px, 100%);
  max-height: 82vh;
  overflow: hidden;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 24px 60px rgba(20, 49, 84, 0.18);
}
.history-modal--wide { width: min(780px, 100%); }

.history-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px;
  border-bottom: 1px solid rgba(228, 236, 245, 0.95);
}

.modal-title { color: #244564; font-size: 18px; font-weight: 800; }

.modal-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: rgba(240, 244, 249, 0.95);
  color: #69809a;
  cursor: pointer;
}

.history-modal-body {
  max-height: calc(82vh - 70px);
  overflow: auto;
  padding: 20px 22px 24px;
}

.hm-item { margin-bottom: 14px; }
.hm-item.skipped-item .hm-a { opacity: 0.5; font-style: italic; }

.hm-step { margin-bottom: 4px; color: #94a3b8; font-size: 11px; }

.hm-q, .hm-a {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.7;
}
.hm-q { color: #486483; background: rgba(246, 249, 253, 0.98); }
.hm-a { color: #355b89; background: rgba(236, 245, 255, 0.96); }

.profile-overview {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.profile-overview-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(246, 249, 253, 0.98);
}
.profile-overview-card strong { color: #214b75; font-size: 28px; line-height: 1; }
.profile-overview-card span { color: #69819b; font-size: 13px; font-weight: 700; }

.profile-section { margin-bottom: 18px; }
.profile-section-title { margin-bottom: 10px; color: #4b6787; font-size: 14px; font-weight: 800; }

.profile-fields-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.profile-tag-wide {
  display: inline-flex;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(244, 248, 253, 0.98);
  color: #617a96;
  font-size: 12px;
  line-height: 1.5;
}

.profile-field-value {
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(246, 249, 253, 0.98);
  color: #5c728b;
  line-height: 1.7;
}

.dialog-fade-enter-active,
.dialog-fade-leave-active { transition: opacity 0.24s ease; }
.dialog-fade-enter-from,
.dialog-fade-leave-to { opacity: 0; }

.fade-slide-enter-active,
.fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateX(20px); }
.fade-slide-leave-to { opacity: 0; transform: translateX(20px); }

@keyframes mascotBounce {
  0%, 100% { transform: translateY(0); }
  30% { transform: translateY(-12px); }
  60% { transform: translateY(-4px); }
}

@keyframes w1 { 0%, 100% { height: 6px; } 50% { height: 20px; } }
@keyframes w2 { 0%, 100% { height: 10px; } 50% { height: 28px; } }
@keyframes w3 { 0%, 100% { height: 6px; } 50% { height: 16px; } }

@keyframes ldot {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
  40% { transform: translateY(-6px); opacity: 1; }
}

@keyframes greenFlash {
  0% { background-color: rgba(34, 197, 94, 0.4); }
  100% { background-color: rgba(0, 0, 0, 0.6); }
}

@keyframes micPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(79, 93, 255, 0.34); }
  50% { box-shadow: 0 0 0 14px rgba(79, 93, 255, 0); }
}

@media (max-width: 960px) {
  .side-panel, .floating-btn { display: none; }
  .elf-bubble { width: calc(100vw - 32px); }
  .action-panel { bottom: 214px; }
  .skip-btn { bottom: 180px; right: 20px; }
  .progress-indicator { display: none; }
  .question-badge { display: none; }
}

@media (max-width: 768px) {
  .scene-title { top: 72px; }
  .elf-bubble { bottom: calc(36% + 196px); }
  .elf-bubble-inner { padding: 18px; }
  .elf-bubble-text { font-size: 15px; }
  .mascot-live2d { width: 190px; height: 250px; }
  .action-panel { bottom: 196px; width: calc(100vw - 24px); padding: 16px; }
  .action-panel__buttons { flex-direction: column; }
  .profile-overview { grid-template-columns: 1fr; }
  .skip-btn { display: none; }
}
</style>
