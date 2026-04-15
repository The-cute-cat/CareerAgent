<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { Close, Microphone } from '@element-plus/icons-vue'
import Live2DCat from '@/components/Live2DCat.vue'

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

type VoiceSceneKey = 'campus' | 'office' | 'code' | 'future'
type VoiceRole = 'pixie' | 'user'

type VoiceHistoryItem = {
  role: VoiceRole
  text: string
  step: number
}

type VoiceQuestion = {
  field: string
  scene: VoiceSceneKey
  question: string
  sampleAnswer: string
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

const emit = defineEmits<{ back: [] }>()

const sceneDecoSvg =
  '<svg width="100%" height="100%" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" style="opacity:.2"><circle cx="1300" cy="0" r="130" fill="#a8ebd7"/><rect x="198" y="585" width="122" height="360" rx="12" fill="rgba(148,163,184,.32)"/><circle cx="258" cy="508" r="122" fill="rgba(152,240,217,.52)"/><rect x="620" y="626" width="132" height="320" rx="12" fill="rgba(148,163,184,.28)"/><circle cx="686" cy="548" r="142" fill="rgba(128,230,214,.46)"/><rect x="1134" y="592" width="138" height="352" rx="12" fill="rgba(148,163,184,.26)"/><circle cx="1203" cy="509" r="132" fill="rgba(69,197,216,.30)"/></svg>'

const sceneMap: Record<VoiceSceneKey, { title: string; className: string; deco: string }> = {
  campus: { title: '校园', className: 'scene-campus', deco: sceneDecoSvg },
  office: { title: '实践', className: 'scene-office', deco: sceneDecoSvg },
  code: { title: '技能', className: 'scene-code', deco: sceneDecoSvg },
  future: { title: '方向', className: 'scene-future', deco: sceneDecoSvg }
}

const questions: VoiceQuestion[] = [
  {
    field: 'education',
    scene: 'campus',
    question: '你好呀！我是职业规划小精灵 Pixie。我们先轻松聊聊，你现在的学历、专业和所处阶段是什么？',
    sampleAnswer: '我是本科，软件工程专业，目前大四在读。'
  },
  {
    field: 'skills',
    scene: 'code',
    question: '那我们接着聊技能。你目前最拿手的技术栈、框架，或者擅长的工作内容是什么？',
    sampleAnswer: '我比较熟悉 Vue3、TypeScript、Element Plus，也做过组件封装和接口联调。'
  },
  {
    field: 'tools',
    scene: 'office',
    question: '平时你常用哪些工具和平台？比如 Git、Apifox、Docker、Figma、云服务这些都可以说。',
    sampleAnswer: '我常用 Git、Apifox、Figma，也会用 Docker 做本地环境配置。'
  },
  {
    field: 'experience',
    scene: 'office',
    question: '说一段你最能代表自己的项目经历吧。你负责了什么，做出了什么结果？',
    sampleAnswer: '我做过一个后台管理系统，负责页面搭建、权限路由和公共组件封装，也优化了列表页加载体验。'
  },
  {
    field: 'target',
    scene: 'future',
    question: '你现在更想投递什么岗位？如果有偏好的行业方向，也可以顺便告诉我。',
    sampleAnswer: '我主要想投前端开发工程师，也比较偏向互联网产品和企业服务方向。'
  },
  {
    field: 'expectation',
    scene: 'future',
    question: '最后告诉我，你希望这份职业画像重点帮你看什么，是优势、短板，还是下一步该怎么补齐？',
    sampleAnswer: '我希望重点突出项目成果，也想知道自己在工程化和项目包装方面还需要补哪些内容。'
  }
]

const currentStep = ref(0)
const history = ref<VoiceHistoryItem[]>([])
const collectedAnswers = ref<Record<string, string>>({})
const currentBubbleText = ref('')
const userSubtitleText = ref('')
const showHistoryModal = ref(false)
const showProfileModal = ref(false)
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

const synth = typeof window !== 'undefined' ? window.speechSynthesis : null

const currentQuestion = computed(() => questions[currentStep.value] ?? questions[questions.length - 1]!)
const currentScene = computed(() => sceneMap[currentQuestion.value.scene])
const bubbleChars = computed(() => [...currentBubbleText.value])
const visibleHistory = computed(() => history.value.slice(-8))
const latestPixieMessage = computed(() => [...history.value].reverse().find(item => item.role === 'pixie') ?? null)
const completed = computed(() => Object.keys(collectedAnswers.value).length >= questions.length)
const micHintText = computed(() => {
  if (speaking.value) return '点击可打断'
  if (recording.value) return '点击结束'
  if (thinking.value) return '正在整理'
  return '点击说话'
})

const profileSummaryList = computed(() => {
  const items: string[] = []
  if (props.formSnapshot.education) items.push(`学历：${props.formSnapshot.education}`)
  if (props.formSnapshot.major.length) items.push(`专业：${props.formSnapshot.major.join(' / ')}`)
  if (props.formSnapshot.targetJob) items.push(`岗位：${props.formSnapshot.targetJob}`)
  if (props.formSnapshot.skillNames.length) items.push(`技能：${props.formSnapshot.skillNames.slice(0, 3).join('、')}`)
  return items
})

const profileSections = computed(() => [
  {
    title: '表单快照',
    items: [`表单完成度 ${props.formProgress}%`, `画像完整度 ${props.profileCompleteness}%`, `${props.completedStepCount}/5 个模块已完成`]
  },
  {
    title: '基础信息',
    items: [
      props.formSnapshot.education ? `学历：${props.formSnapshot.education}` : '学历：待补充',
      props.formSnapshot.major.length ? `专业：${props.formSnapshot.major.join(' / ')}` : '专业：待补充',
      props.formSnapshot.targetJob ? `目标岗位：${props.formSnapshot.targetJob}` : '目标岗位：待补充',
      props.formSnapshot.targetIndustries.length ? `目标行业：${props.formSnapshot.targetIndustries.join(' / ')}` : '目标行业：待补充'
    ]
  },
  {
    title: '经验概况',
    items: [
      props.formSnapshot.skillNames.length ? `技能：${props.formSnapshot.skillNames.join('、')}` : '技能：待补充',
      props.formSnapshot.toolNames.length ? `工具：${props.formSnapshot.toolNames.join('、')}` : '工具：待补充',
      `项目经历：${props.formSnapshot.projectCount} 项`,
      `实习经历：${props.formSnapshot.internshipCount} 项`
    ]
  },
  {
    title: '本轮对话摘要',
    items: Object.entries(collectedAnswers.value).map(([key, value]) => `${key}：${value}`)
  }
])

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

function addHistory(role: VoiceRole, text: string, step: number): void {
  history.value.push({ role, text, step })
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

async function startConversation(): Promise<void> {
  const firstQuestion = questions[0]!
  setSceneTitle()
  addHistory('pixie', firstQuestion.question, 0)
  showBubble(firstQuestion.question)
  await nextTick()
  window.setTimeout(() => speak(firstQuestion.question), 120)
}

function buildReply(): string {
  if (currentStep.value >= questions.length - 1) {
    return '太好了，这一轮信息我已经帮你整理好了。你可以返回表单继续完善，也可以重新开始再补充一轮。'
  }
  const nextQuestion = questions[currentStep.value + 1]!
  const intros = ['收到，我先帮你记下来。', '很好，这部分已经清晰了。', '我已经抓到重点啦。', '这段经历很有参考价值。']
  return `${intros[currentStep.value % intros.length]} ${nextQuestion.question}`
}

function advanceConversation(text: string): void {
  addHistory('user', text, currentStep.value)
  collectedAnswers.value = { ...collectedAnswers.value, [currentQuestion.value.field]: text }
  thinking.value = true
  bounceMascot()
  window.setTimeout(() => {
    thinking.value = false
    const reply = buildReply()
    addHistory('pixie', reply, currentStep.value)
    if (currentStep.value < questions.length - 1) {
      currentStep.value += 1
      setSceneTitle()
    }
    showBubble(reply)
    speak(reply)
  }, 780)
}

function mockRecognize(): Promise<string> {
  return new Promise(resolve => {
    window.setTimeout(() => resolve(currentQuestion.value.sampleAnswer), 1100)
  })
}

function recognizeByBrowser(): Promise<string | null> {
  const RecognitionCtor = window.SpeechRecognition ?? window.webkitSpeechRecognition
  if (!RecognitionCtor) return Promise.resolve(null)

  return new Promise(resolve => {
    const recognition = new RecognitionCtor()
    activeRecognition = recognition
    let resolved = false

    recognition.lang = 'zh-CN'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onresult = event => {
      const transcript = event.results[0]?.[0]?.transcript?.trim() ?? ''
      if (!resolved) {
        resolved = true
        resolve(transcript || null)
      }
    }

    recognition.onerror = () => {
      if (!resolved) {
        resolved = true
        resolve(null)
      }
    }

    recognition.onend = () => {
      activeRecognition = null
      if (!resolved) {
        resolved = true
        resolve(null)
      }
    }

    recognition.start()
  })
}

async function onMic(): Promise<void> {
  if (speaking.value) {
    stopSpeech()
    return
  }
  if (recording.value || thinking.value || completed.value) return
  recording.value = true
  listeningVisible.value = true
  hideBubble()
  const browserText = await recognizeByBrowser()
  const text = browserText || (await mockRecognize())
  listeningVisible.value = false
  recording.value = false
  showUserSubtitle(text)
  advanceConversation(text)
}

function restartConversation(): void {
  clearTimers()
  synth?.cancel()
  currentStep.value = 0
  history.value = []
  collectedAnswers.value = {}
  currentBubbleText.value = ''
  userSubtitleText.value = ''
  thinking.value = false
  recording.value = false
  speaking.value = false
  listeningVisible.value = false
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
  activeRecognition?.stop()
  synth?.cancel()
})
</script>

<template>
  <section class="pixie-scene-page" :class="currentScene.className">
    <div class="scene-bg"></div>
    <div class="scene-deco" v-html="currentScene.deco"></div>

    <div class="scene-title" :class="{ show: sceneTitleVisible }">
      <span class="scene-title-text">{{ currentScene.title }}</span>
    </div>

    <div class="side-panel side-panel-left">
      <div class="side-panel-inner side-panel-card history-card" @click="showHistoryModal = true">
        <p class="panel-caption">对话历史</p>
        <div class="panel-scroll">
          <span v-if="!history.length" class="panel-empty">等待对话开始...</span>
          <div v-for="(item, index) in visibleHistory" :key="`${item.role}-${index}-${item.text}`" class="history-item">
            <div class="hi-step">{{ item.role === 'pixie' ? `✨ 第${item.step + 1}轮` : `🎙 第${item.step + 1}轮` }}</div>
            <div :class="item.role === 'pixie' ? 'hi-q' : 'hi-a'">{{ item.text }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="side-panel side-panel-right" @click="showProfileModal = true">
      <div class="side-panel-inner side-panel-card profile-card">
        <p class="panel-caption">学生画像</p>
        <div class="panel-scroll">
          <span v-if="!profileSummaryList.length" class="panel-empty">等待对话开始...</span>
          <div v-for="item in profileSummaryList.slice(0, 3)" :key="item" class="profile-chip">{{ item }}</div>
        </div>
      </div>
    </div>

    <button type="button" class="floating-btn floating-back" @click="emit('back')">返回表单</button>
    <button type="button" class="floating-btn floating-reset" @click="restartConversation">重新开始</button>

    <div class="elf-bubble" :class="bubbleVisible ? 'show' : 'hide'">
      <div class="elf-bubble-inner">
        <p class="elf-bubble-text">
          <span v-for="(char, index) in bubbleChars" :key="`${index}-${char}`" class="ec" :class="{ lit: index <= litCharIndex }">
            {{ char }}
          </span>
        </p>
      </div>
    </div>

    <div class="thinking-dots" :class="{ show: thinking }">
      <div class="thinking-dot"></div>
      <div class="thinking-dot"></div>
      <div class="thinking-dot"></div>
    </div>

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

    <div class="user-subtitle" :class="[{ show: subtitleVisible }, { 'subtitle-flash': subtitleFlash }]">
      <div class="user-subtitle-inner">{{ userSubtitleText }}</div>
    </div>

    <div class="listening-indicator" :class="{ show: listeningVisible }">
      <div class="listening-dot"></div>
      <div class="listening-dot"></div>
      <div class="listening-dot"></div>
      <span class="listening-text">聆听中...</span>
    </div>

    <div class="mic-hint">{{ micHintText }}</div>
    <button type="button" class="mic-btn" :class="{ active: recording }" @click="onMic">
      <el-icon v-if="!recording && !speaking"><Microphone /></el-icon>
      <span v-else class="mic-stop"></span>
    </button>

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
            <div v-for="(item, index) in history" :key="`modal-${index}`" class="hm-item">
              <div class="hm-step">{{ item.role === 'pixie' ? 'Pixie' : '你' }} · 第{{ item.step + 1 }}轮</div>
              <div :class="item.role === 'pixie' ? 'hm-q' : 'hm-a'">{{ item.text }}</div>
            </div>
          </div>
        </div>
      </div>
    </transition>

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
            <div class="profile-overview">
              <div class="profile-overview-card">
                <strong>{{ props.formProgress }}%</strong>
                <span>表单完成度</span>
              </div>
              <div class="profile-overview-card">
                <strong>{{ props.profileCompleteness }}%</strong>
                <span>画像完整度</span>
              </div>
              <div class="profile-overview-card">
                <strong>{{ Object.keys(collectedAnswers).length }}</strong>
                <span>本轮已回答</span>
              </div>
            </div>

            <div v-for="section in profileSections" :key="section.title" class="profile-section">
              <div class="profile-section-title">{{ section.title }}</div>
              <div class="profile-fields-grid">
                <span v-for="item in section.items" :key="item" class="profile-tag-wide">{{ item }}</span>
                <span v-if="!section.items.length" class="panel-empty">暂无内容</span>
              </div>
            </div>

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
* {
  box-sizing: border-box;
}

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

.scene-campus,
.scene-office,
.scene-code,
.scene-future {
  background: linear-gradient(180deg, #cfe4f5 0%, #78c9f5 58%, #46b5ee 100%);
}

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

.scene-title.show {
  opacity: 1;
}

.scene-title-text {
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.side-panel-left {
  left: 18px;
}

.side-panel-right {
  right: 18px;
  cursor: pointer;
}

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

.history-item {
  margin-bottom: 6px;
}

.hi-step {
  margin-bottom: 2px;
  color: #aebac8;
  font-size: 10px;
}

.hi-q,
.hi-a {
  color: #55697d;
  font-size: 11px;
  line-height: 1.45;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hi-a {
  color: #5b6f8a;
}

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

.floating-back {
  left: 352px;
}

.floating-reset {
  right: 146px;
}

.elf-bubble {
  position: absolute;
  bottom: calc(36% + 230px);
  left: 50%;
  z-index: 6;
  width: min(500px, calc(100vw - 72px));
  opacity: 0;
  transform: translateX(-50%);
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.elf-bubble.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.elf-bubble.hide {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

.elf-bubble-inner {
  position: relative;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.92);
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
  border-top: 10px solid rgba(255, 255, 255, 0.92);
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

.ec.lit {
  color: #2563eb;
  font-weight: 700;
}

.thinking-dots {
  position: absolute;
  bottom: calc(36% + 204px);
  left: 50%;
  z-index: 6;
  display: none;
  gap: 8px;
  transform: translateX(-50%);
}

.thinking-dots.show {
  display: flex;
}

.thinking-dot,
.listening-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4f8cff;
  animation: ldot 0.8s ease-in-out infinite;
}

.thinking-dot:nth-child(2),
.listening-dot:nth-child(2) {
  animation-delay: 0.12s;
}

.thinking-dot:nth-child(3),
.listening-dot:nth-child(3) {
  animation-delay: 0.24s;
}

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

.mascot-live2d.bounce {
  animation: mascotBounce 0.55s ease;
}

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

.wave-bar.speaking:nth-child(1) {
  animation: w1 0.5s ease-in-out infinite;
}

.wave-bar.speaking:nth-child(2) {
  animation: w2 0.5s ease-in-out infinite 0.12s;
}

.wave-bar.speaking:nth-child(3) {
  animation: w3 0.5s ease-in-out infinite 0.24s;
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

.user-subtitle.show {
  opacity: 1;
}

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

.subtitle-flash .user-subtitle-inner {
  animation: greenFlash 1.4s ease-out forwards;
}

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

.listening-indicator.show {
  display: flex;
}

.listening-text {
  color: rgba(255, 255, 255, 0.72);
  font-size: 12px;
}

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

.mic-btn:hover {
  transform: translateX(-50%) scale(1.05);
  box-shadow: 0 18px 40px rgba(79, 93, 255, 0.34);
}

.mic-btn.active {
  animation: micPulse 1s ease-in-out infinite;
}

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

.history-modal--wide {
  width: min(760px, 100%);
}

.history-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px;
  border-bottom: 1px solid rgba(228, 236, 245, 0.95);
}

.modal-title {
  color: #244564;
  font-size: 18px;
  font-weight: 800;
}

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

.hm-item {
  margin-bottom: 14px;
}

.hm-step {
  margin-bottom: 4px;
  color: #94a3b8;
  font-size: 11px;
}

.hm-q,
.hm-a {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.7;
}

.hm-q {
  color: #486483;
  background: rgba(246, 249, 253, 0.98);
}

.hm-a {
  color: #355b89;
  background: rgba(236, 245, 255, 0.96);
}

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

.profile-overview-card strong {
  color: #214b75;
  font-size: 28px;
  line-height: 1;
}

.profile-overview-card span {
  color: #69819b;
  font-size: 13px;
  font-weight: 700;
}

.profile-section {
  margin-bottom: 18px;
}

.profile-section-title {
  margin-bottom: 10px;
  color: #4b6787;
  font-size: 14px;
  font-weight: 800;
}

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
.dialog-fade-leave-active {
  transition: opacity 0.24s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

@keyframes mascotBounce {
  0%,
  100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-12px);
  }
  60% {
    transform: translateY(-4px);
  }
}

@keyframes w1 {
  0%,
  100% {
    height: 6px;
  }
  50% {
    height: 20px;
  }
}

@keyframes w2 {
  0%,
  100% {
    height: 10px;
  }
  50% {
    height: 28px;
  }
}

@keyframes w3 {
  0%,
  100% {
    height: 6px;
  }
  50% {
    height: 16px;
  }
}

@keyframes ldot {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  40% {
    transform: translateY(-6px);
    opacity: 1;
  }
}

@keyframes greenFlash {
  0% {
    background-color: rgba(34, 197, 94, 0.4);
  }
  100% {
    background-color: rgba(0, 0, 0, 0.6);
  }
}

@keyframes micPulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(79, 93, 255, 0.34);
  }
  50% {
    box-shadow: 0 0 0 14px rgba(79, 93, 255, 0);
  }
}

@media (max-width: 960px) {
  .side-panel,
  .floating-btn {
    display: none;
  }

  .elf-bubble {
    width: calc(100vw - 32px);
  }
}

@media (max-width: 768px) {
  .scene-title {
    top: 72px;
  }

  .elf-bubble {
    bottom: calc(36% + 196px);
  }

  .elf-bubble-inner {
    padding: 18px;
  }

  .elf-bubble-text {
    font-size: 15px;
  }

  .mascot-live2d {
    width: 190px;
    height: 250px;
  }

  .profile-overview {
    grid-template-columns: 1fr;
  }
}
</style>
