<script setup lang="ts">
import { ref, computed, onUnmounted, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { useVirtualHuman } from '@/composables/use-virtual-human'
import { VirtualHumanConfig } from '@/config/virtual-human-config'
import { 
  VideoPlay, 
  VideoPause, 
  Microphone, 
  Mute,
  ChatDotSquare,
  Timer,
  SwitchButton,
  Setting,
  TrendCharts,
  RefreshRight,
  Document,
  MagicStick,
  Briefcase,
  Check,
  ArrowRight,
  ArrowLeft,
  Monitor,
  Search,
  Close,
  View,
  // 岗位图标
  Monitor as IconFrontEnd,
  Cpu,
  Iphone,
  Brush,
  DataLine,
  Cpu as IconAlgorithm,
  Promotion,
  UserFilled,
  // 面试类型图标
  Monitor as IconTech,
  ChatDotRound,
  Aim,
  // 结果页面图标
  Trophy,
  Warning,
  Lightning,
  Share,
  Download,
  CircleCheck
} from '@element-plus/icons-vue'

const router = useRouter()

// 面试步骤
enum InterviewStep {
  SELECTING = 'selecting',
  PREPARING = 'preparing',
  INTERVIEWING = 'interviewing',
  PAUSED = 'paused',
  FINISHED = 'finished',
  RESULT = 'result'  // 新增结果展示步骤
}

// 面试结果数据接口
interface InterviewResult {
  overallScore: number
  dimensionScores: {
    technical: number
    communication: number
    logic: number
    expression: number
    attitude: number
  }
  skillAssessment: {
    name: string
    score: number
    fullMark: number
  }[]
  weaknessAnalysis: {
    area: string
    severity: 'high' | 'medium' | 'low'
    suggestion: string
  }[]
  improvementSuggestions: {
    category: string
    items: string[]
  }[]
  interviewRecord: {
    totalQuestions: number
    answeredQuestions: number
    avgResponseTime: number
    fluencyScore: number
  }
  aiFeedback: string
}

// 消息类型
interface ChatMessage {
  id: string
  role: 'ai' | 'user'
  content: string
  timestamp: Date
  emotion?: 'neutral' | 'happy' | 'thinking' | 'encouraging'
}

// 岗位类型
interface Position {
  id: string
  name: string
  category: string
  icon: any
  description: string
  difficulty: 'easy' | 'medium' | 'hard'
  duration: number
  tags: string[]
}

// 预设岗位列表
const positions = ref<Position[]>([
  {
    id: '1',
    name: '前端开发工程师',
    category: '技术开发',
    icon: IconFrontEnd,
    description: 'HTML/CSS/JS、Vue/React、性能优化',
    difficulty: 'medium',
    duration: 30,
    tags: ['Vue', 'React', 'TypeScript']
  },
  {
    id: '2',
    name: 'Java后端工程师',
    category: '技术开发',
    icon: Cpu,
    description: 'Java/Go、数据库、微服务架构',
    difficulty: 'hard',
    duration: 35,
    tags: ['Java', 'MySQL', 'Redis']
  },
  {
    id: '3',
    name: '产品经理',
    category: '产品设计',
    icon: Iphone,
    description: '需求分析、产品设计、项目管理',
    difficulty: 'medium',
    duration: 25,
    tags: ['Axure', '需求分析', '数据分析']
  },
  {
    id: '4',
    name: 'UI/UX设计师',
    category: '产品设计',
    icon: Brush,
    description: '视觉设计、交互设计、用户体验',
    difficulty: 'medium',
    duration: 25,
    tags: ['Figma', 'Sketch', '设计系统']
  },
  {
    id: '5',
    name: '数据分析师',
    category: '数据科学',
    icon: DataLine,
    description: 'SQL、Python、数据可视化',
    difficulty: 'hard',
    duration: 30,
    tags: ['Python', 'SQL', 'Tableau']
  },
  {
    id: '6',
    name: '算法工程师',
    category: '数据科学',
    icon: IconAlgorithm,
    description: '机器学习、深度学习、算法优化',
    difficulty: 'hard',
    duration: 40,
    tags: ['Python', 'TensorFlow', '算法']
  },
  {
    id: '7',
    name: '运营专员',
    category: '运营市场',
    icon: Promotion,
    description: '内容运营、用户增长、活动策划',
    difficulty: 'easy',
    duration: 20,
    tags: ['内容运营', '数据分析', '文案']
  },
  {
    id: '8',
    name: '人力资源',
    category: '职能支持',
    icon: UserFilled,
    description: '招聘、培训、绩效管理',
    difficulty: 'easy',
    duration: 20,
    tags: ['招聘', 'HRBP', '员工关系']
  }
])

// 面试类型选项
const interviewTypes = [
  { value: 'technical', label: '技术面试', icon: IconTech, description: '侧重技术能力、项目经验、编码能力' },
  { value: 'behavior', label: '行为面试', icon: ChatDotRound, description: '侧重沟通能力、团队协作、解决问题' },
  { value: 'comprehensive', label: '综合面试', icon: Aim, description: '技术+行为全方位考察' }
]

// 难度级别选项
const difficultyLevels = [
  { value: 'easy', label: '初级', color: '#10b981', bgColor: 'rgba(16, 185, 129, 0.1)', description: '适合应届生或1-2年经验' },
  { value: 'medium', label: '中级', color: '#f59e0b', bgColor: 'rgba(245, 158, 11, 0.1)', description: '适合3-5年经验' },
  { value: 'hard', label: '高级', color: '#ef4444', bgColor: 'rgba(239, 68, 68, 0.1)', description: '适合5年以上经验或专家' }
]

// 当前步骤
const currentStep = ref<InterviewStep>(InterviewStep.SELECTING)
const selectedPosition = ref<Position | null>(null)
const selectedType = ref('technical')
const selectedDifficulty = ref('medium')

// 搜索功能
const searchQuery = ref('')
const showAllPositions = ref(false)
const INITIAL_DISPLAY_COUNT = 6

const filteredPositions = computed(() => {
  let result = positions.value
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = positions.value.filter(pos => 
      pos.name.toLowerCase().includes(query) ||
      pos.category.toLowerCase().includes(query) ||
      pos.tags.some(tag => tag.toLowerCase().includes(query)) ||
      pos.description.toLowerCase().includes(query)
    )
  }
  // 如果不是搜索状态且未展开，只显示前6个
  if (!searchQuery.value.trim() && !showAllPositions.value) {
    return result.slice(0, INITIAL_DISPLAY_COUNT)
  }
  return result
})

const hasMorePositions = computed(() => {
  return positions.value.length > INITIAL_DISPLAY_COUNT && !searchQuery.value.trim()
})

const clearSearch = () => {
  searchQuery.value = ''
}

const toggleShowAll = () => {
  showAllPositions.value = !showAllPositions.value
}

// 面试配置
const interviewConfig = computed(() => ({
  type: selectedType.value,
  duration: selectedPosition.value?.duration || 30,
  difficulty: selectedDifficulty.value,
  position: selectedPosition.value?.name || '前端开发工程师',
  positionId: selectedPosition.value?.id || '1',
  company: '模拟科技公司'
}))

// 状态变量
const isMuted = ref(false)
const isVideoOn = ref(true)
const currentTime = ref(0)
const aiSpeaking = ref(false)
const userInput = ref('')
const chatContainerRef = ref<HTMLElement | null>(null)
const messages = ref<ChatMessage[]>([])
const virtualHumanAvatarId = ref(VirtualHumanConfig.DEFAULT_AVATAR_ID)
const virtualHumanVoice = ref(VirtualHumanConfig.DEFAULT_VCN)
const {
  containerRef: virtualHumanContainerRef,
  status: virtualHumanStatus,
  connect: connectVirtualHuman,
  speak: speakVirtualHuman,
  disconnect: disconnectVirtualHuman,
  updateConfig: updateVirtualHumanConfig
} = useVirtualHuman()

const digitalHumanSpeaking = computed(() => aiSpeaking.value || virtualHumanStatus.value.isSpeaking)
const virtualHumanStatusText = computed(() => {
  if (virtualHumanStatus.value.isLoading) return '数字人连接中'
  if (virtualHumanStatus.value.error) return '数字人离线'
  if (virtualHumanStatus.value.isConnected) return digitalHumanSpeaking.value ? 'AI面试官正在提问' : 'AI面试官在线'
  return '点击开始后连接数字人'
})

// 面试统计数据
const interviewStats = ref({
  questionsAsked: 0,
  answersGiven: 0,
  fluency: 0,
  technicalScore: 0,
  communicationScore: 0
})

// 面试结果数据
const interviewResult = ref<InterviewResult>({
  overallScore: 82,
  dimensionScores: {
    technical: 85,
    communication: 78,
    logic: 88,
    expression: 80,
    attitude: 92
  },
  skillAssessment: [
    { name: 'HTML/CSS基础', score: 90, fullMark: 100 },
    { name: 'JavaScript/ES6+', score: 85, fullMark: 100 },
    { name: 'Vue/React框架', score: 88, fullMark: 100 },
    { name: '性能优化', score: 75, fullMark: 100 },
    { name: '工程化实践', score: 70, fullMark: 100 },
    { name: '沟通能力', score: 80, fullMark: 100 }
  ],
  weaknessAnalysis: [
    {
      area: '性能优化深入理解',
      severity: 'high',
      suggestion: '建议深入学习浏览器渲染原理、懒加载、代码分割等优化技术'
    },
    {
      area: '工程化实践经验',
      severity: 'medium',
      suggestion: '建议多实践Webpack/Vite配置，了解CI/CD流程'
    },
    {
      area: '复杂场景问题解决',
      severity: 'medium',
      suggestion: '建议多做算法题和实际项目中的复杂需求拆解'
    }
  ],
  improvementSuggestions: [
    {
      category: '技术能力提升',
      items: [
        '深入学习Vue3源码，理解响应式原理',
        '掌握前端性能优化最佳实践',
        '学习TypeScript高级用法和类型体操'
      ]
    },
    {
      category: '项目经验积累',
      items: [
        '参与开源项目贡献',
        '完成一个完整的技术博客项目',
        '实践微前端架构设计'
      ]
    },
    {
      category: '软实力提升',
      items: [
        '提升技术表达和文档能力',
        '练习结构化思考和表达',
        '加强团队协作沟通技巧'
      ]
    }
  ],
  interviewRecord: {
    totalQuestions: 12,
    answeredQuestions: 11,
    avgResponseTime: 45,
    fluencyScore: 85
  },
  aiFeedback: '整体表现良好，技术基础扎实，对主流框架有较好的理解。建议在性能优化和工程化方面加强学习，同时提升复杂问题的分析和解决能力。表达清晰，态度积极，具备较好的团队协作潜力。'
})

// 图表DOM引用
const radarChartRef = ref<HTMLElement | null>(null)
const barChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
let radarChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChartRef.value) return
  // 先销毁已存在的实例,避免内存泄漏
  if (radarChart) {
    radarChart.dispose()
  }
  radarChart = echarts.init(radarChartRef.value)
  const option = {
    color: ['#409EFF'],
    radar: {
      indicator: [
        { name: '技术能力', max: 100 },
        { name: '沟通能力', max: 100 },
        { name: '逻辑思维', max: 100 },
        { name: '表达能力', max: 100 },
        { name: '态度素养', max: 100 }
      ],
      radius: '65%',
      center: ['50%', '55%'],
      axisName: {
        color: '#606266',
        fontSize: 12
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(64, 158, 255, 0.02)', 'rgba(64, 158, 255, 0.06)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(64, 158, 255, 0.2)'
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(64, 158, 255, 0.2)'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          interviewResult.value.dimensionScores.technical,
          interviewResult.value.dimensionScores.communication,
          interviewResult.value.dimensionScores.logic,
          interviewResult.value.dimensionScores.expression,
          interviewResult.value.dimensionScores.attitude
        ],
        name: '能力评估',
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        },
        lineStyle: {
          color: '#409EFF',
          width: 2
        },
        itemStyle: {
          color: '#409EFF'
        }
      }]
    }]
  }
  radarChart.setOption(option)
}

// 初始化柱状图
const initBarChart = () => {
  if (!barChartRef.value) return
  // 先销毁已存在的实例,避免内存泄漏
  if (barChart) {
    barChart.dispose()
  }
  barChart = echarts.init(barChartRef.value)
  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: interviewResult.value.skillAssessment.map(item => item.name),
      axisLabel: {
        color: '#606266',
        fontSize: 11,
        interval: 0,
        rotate: 15
      },
      axisLine: {
        lineStyle: { color: '#e4e7ed' }
      }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        color: '#606266'
      },
      splitLine: {
        lineStyle: { color: '#f0f2f5' }
      }
    },
    series: [{
      type: 'bar',
      data: interviewResult.value.skillAssessment.map(item => ({
        value: item.score,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#64b5f6' }
          ])
        }
      })),
      barWidth: '50%',
      label: {
        show: true,
        position: 'top',
        color: '#409EFF',
        fontSize: 12,
        formatter: '{c}分'
      }
    }]
  }
  barChart.setOption(option)
}

// 查看面试结果
const viewResults = () => {
  // 避免重复进入结果页
  if (currentStep.value === InterviewStep.RESULT) return
  
  currentStep.value = InterviewStep.RESULT
  nextTick(() => {
    initRadarChart()
    initBarChart()
    // 启动眨眼动画(会先停止已存在的)
    startBlinking()
  })
}

// 图表resize处理
const handleResize = () => {
  if (radarChart && !radarChart.isDisposed()) {
    radarChart.resize()
  }
  if (barChart && !barChart.isDisposed()) {
    barChart.resize()
  }
}

// 销毁图表
const disposeCharts = () => {
  if (radarChart) {
    radarChart.dispose()
    radarChart = null
  }
  if (barChart) {
    barChart.dispose()
    barChart = null
  }
}

// 返回面试列表
const backToInterview = () => {
  restartInterview()
}

// 格式化时间
const formattedTime = computed(() => {
  const mins = Math.floor(currentTime.value / 60)
  const secs = currentTime.value % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

// 进度百分比
const progressPercent = computed(() => {
  return Math.min((currentTime.value / (interviewConfig.value.duration * 60)) * 100, 100)
})

// 眼睛眨动控制
const isBlinking = ref(false)
let blinkInterval: number | null = null

// 启动眨眼动画
const startBlinking = () => {
  // 先停止已存在的动画,避免重复启动
  stopBlinking()
  blinkInterval = window.setInterval(() => {
    isBlinking.value = true
    setTimeout(() => {
      isBlinking.value = false
    }, 200)
  }, 3000 + Math.random() * 2000) // 3-5秒随机眨眼
}

// 停止眨眼动画
const stopBlinking = () => {
  if (blinkInterval !== null) {
    clearInterval(blinkInterval)
    blinkInterval = null
  }
}

// AI表情状态
const aiEmotion = computed(() => {
  if (digitalHumanSpeaking.value) return 'speaking'
  const lastMessage = messages.value[messages.value.length - 1]
  return lastMessage?.emotion || 'neutral'
})

// 选择岗位
const selectPosition = (position: Position) => {
  selectedPosition.value = position
}

// 确认选择并开始准备
const confirmPosition = () => {
  if (!selectedPosition.value) return
  currentStep.value = InterviewStep.PREPARING
  messages.value = [{
    id: '1',
    role: 'ai',
    content: `你好！我是你的AI面试官。我将为你模拟一场${selectedPosition.value.name}岗位的面试。准备好了吗？点击"开始面试"按钮，我们就可以开始了。`,
    timestamp: new Date(),
    emotion: 'happy'
  }]
}

// 返回选择
const backToSelection = () => {
  currentStep.value = InterviewStep.SELECTING
  selectedPosition.value = null
}

const ensureVirtualHumanConnected = async () => {
  await nextTick()
  if (virtualHumanStatus.value.isConnected || virtualHumanStatus.value.isLoading) return

  await connectVirtualHuman({
    avatarId: virtualHumanAvatarId.value,
    vcn: virtualHumanVoice.value
  })
}

const handleVirtualHumanConfigChange = async () => {
  updateVirtualHumanConfig({
    avatarId: virtualHumanAvatarId.value,
    vcn: virtualHumanVoice.value
  })

  if (virtualHumanStatus.value.isConnected) {
    disconnectVirtualHuman()
    await ensureVirtualHumanConnected()
  }
}

// 开始面试
const startInterview = async () => {
  currentStep.value = InterviewStep.INTERVIEWING
  await ensureVirtualHumanConnected()
  startTimer()
  addAIMessage('好的，让我们开始吧！请先简单介绍一下你自己。', 'encouraging')
}

// 暂停/继续面试
const togglePause = () => {
  if (currentStep.value === InterviewStep.INTERVIEWING) {
    currentStep.value = InterviewStep.PAUSED
    stopTimer()
  } else if (currentStep.value === InterviewStep.PAUSED) {
    currentStep.value = InterviewStep.INTERVIEWING
    startTimer()
  }
}

// 结束面试
const endInterview = () => {
  stopTimer()
  currentStep.value = InterviewStep.FINISHED
  // 使用nextTick确保状态更新后再添加消息
  nextTick(() => {
    addAIMessage('面试到此结束。感谢你的参与！我们会尽快为你生成面试报告。', 'happy')
  })
}

// 查看面试结果
const viewInterviewResult = () => {
  // 根据当前岗位跳转到对应的面试结果页面
  const positionId = interviewConfig.value.positionId || '1'
  const positionName = interviewConfig.value.position || '前端开发工程师'
  
  // 跳转到面试报告页面，传递岗位信息
  router.push({
    name: 'interview-report',
    params: { id: positionId },
    query: { position: encodeURIComponent(positionName) }
  })
}

// 计时器
let timerInterval: number | null = null
const startTimer = () => {
  timerInterval = window.setInterval(() => {
    currentTime.value++
    if (currentTime.value >= interviewConfig.value.duration * 60) {
      endInterview()
    }
  }, 1000)
}
const stopTimer = () => {
  if (timerInterval !== null) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

// 添加AI消息
const addAIMessage = (content: string, emotion: ChatMessage['emotion'] = 'neutral') => {
  aiSpeaking.value = true
  setTimeout(() => {
    messages.value.push({
      id: Date.now().toString(),
      role: 'ai',
      content,
      timestamp: new Date(),
      emotion
    })
    aiSpeaking.value = false
    void speakVirtualHuman(content)
    scrollToBottom()
  }, 1000)
}

// 发送用户消息
const sendMessage = () => {
  if (!userInput.value.trim() || currentStep.value !== InterviewStep.INTERVIEWING) return
  
  messages.value.push({
    id: Date.now().toString(),
    role: 'user',
    content: userInput.value,
    timestamp: new Date()
  })
  
  interviewStats.value.answersGiven++
  const userQuestion = userInput.value
  userInput.value = ''
  scrollToBottom()
  
  simulateAIResponse(userQuestion)
}

// 模拟AI回复
const simulateAIResponse = (userQuestion: string) => {
  const responses = [
    { content: '很好的回答！能再详细说说你在那个项目中的具体贡献吗？', emotion: 'encouraging' as const },
    { content: '明白了。那你觉得在这个场景下，如何优化性能呢？', emotion: 'thinking' as const },
    { content: '不错的思路。还有其他的解决方案吗？', emotion: 'happy' as const },
    { content: '了解了。让我们继续下一个问题。', emotion: 'neutral' as const }
  ]
  
  interviewStats.value.questionsAsked++
  const randomResponse = responses[Math.floor(Math.random() * responses.length)] ?? responses[0]!
  addAIMessage(randomResponse.content, randomResponse.emotion)
}

// 滚动到底部
const scrollToBottom = () => {
  setTimeout(() => {
    if (chatContainerRef.value) {
      chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight
    }
  }, 100)
}

// 重新开始
const restartInterview = () => {
  currentStep.value = InterviewStep.SELECTING
  selectedPosition.value = null
  selectedType.value = 'technical'
  selectedDifficulty.value = 'medium'
  currentTime.value = 0
  messages.value = []
  interviewStats.value = {
    questionsAsked: 0,
    answersGiven: 0,
    fluency: 0,
    technicalScore: 0,
    communicationScore: 0
  }
  // 清理资源
  stopBlinking()
  disposeCharts()
  disconnectVirtualHuman()
}

// 获取难度标签
const getDifficultyLabel = (difficulty: string) => {
  const map: Record<string, string> = {
    easy: '初级',
    medium: '中级',
    hard: '高级'
  }
  return map[difficulty] || '中级'
}

// 获取难度颜色
const getDifficultyColor = (difficulty: string) => {
  const map: Record<string, string> = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return map[difficulty] || 'warning'
}

onMounted(() => {
  // 添加resize监听
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  stopTimer()
  stopBlinking()
  disposeCharts()
  disconnectVirtualHuman()
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="ai-interview-page">
    <!-- 页面标题 -->
    <div class="page-header" v-if="currentStep === InterviewStep.SELECTING || currentStep === InterviewStep.PREPARING">
      <h1 class="page-title">
        <span class="gradient-text">AI 智能面试</span>
      </h1>
      <p class="page-subtitle">选择岗位，开始你的模拟面试之旅</p>
    </div>

    <!-- 面试中头部 -->
    <div class="interview-header-card" v-else>
      <div class="header-left">
        <div class="ai-avatar-small">
          <div class="avatar-pulse" :class="{ speaking: digitalHumanSpeaking }"></div>
          <span class="ai-icon">🤖</span>
        </div>
        <div class="interview-info">
          <h3>{{ interviewConfig.position }}</h3>
          <p>{{ getDifficultyLabel(interviewConfig.difficulty) }} · {{ interviewConfig.duration }}分钟</p>
        </div>
      </div>
      
      <div class="header-center">
        <div class="timer-display" :class="{ warning: currentTime > interviewConfig.duration * 60 * 0.8 }">
          <el-icon><Timer /></el-icon>
          <span>{{ formattedTime }}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
        </div>
      </div>

      <div class="header-right">
        <el-button 
          :icon="View" 
          circle 
          class="control-btn"
          title="查看面试结果"
          @click="viewInterviewResult"
        />
        <el-button :icon="Setting" circle class="control-btn" />
        <el-button 
          :icon="currentStep === InterviewStep.INTERVIEWING ? VideoPause : VideoPlay" 
          circle 
          class="control-btn"
          :type="currentStep === InterviewStep.INTERVIEWING ? 'warning' : 'primary'"
          @click="togglePause"
        />
        <el-button 
          :icon="SwitchButton" 
          circle 
          class="control-btn danger"
          @click="endInterview"
        />
      </div>
    </div>

    <!-- 步骤 1: 选择岗位 -->
    <div v-if="currentStep === InterviewStep.SELECTING" class="selection-panel glass-panel">
      <!-- 搜索栏 -->
      <div class="search-section">
        <div class="search-box">
          <el-icon class="search-icon"><Search /></el-icon>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索岗位名称、类别或技能标签..."
            class="search-input"
          />
          <el-icon v-if="searchQuery" class="clear-icon" @click="clearSearch"><Close /></el-icon>
        </div>
        <div v-if="searchQuery" class="search-result-count">
          找到 <span>{{ filteredPositions.length }}</span> 个相关岗位
        </div>
      </div>

      <!-- 岗位网格 -->
      <div class="positions-grid" v-if="filteredPositions.length > 0">
        <div
          v-for="position in filteredPositions"
          :key="position.id"
          class="position-card glass-card"
          :class="{ selected: selectedPosition?.id === position.id }"
          @click="selectPosition(position)"
        >
          <div class="position-icon">
            <el-icon :size="32" color="#409EFF">
              <component :is="position.icon" />
            </el-icon>
          </div>
          <div class="position-info">
            <h4>{{ position.name }}</h4>
            <span class="position-category">{{ position.category }}</span>
            <p class="position-desc">{{ position.description }}</p>
            <div class="position-tags">
              <span v-for="tag in position.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
          <div class="position-meta">
            <span class="difficulty-badge" :class="position.difficulty">
              {{ getDifficultyLabel(position.difficulty) }}
            </span>
            <span class="duration">
              <el-icon><Timer /></el-icon>
              {{ position.duration }}分钟
            </span>
          </div>
          <div class="selection-check" v-if="selectedPosition?.id === position.id">
            <el-icon><Check /></el-icon>
          </div>
        </div>
      </div>

      <!-- 展开/收起按钮 -->
      <div v-if="hasMorePositions" class="expand-actions">
        <el-button 
          type="primary" 
          text
          size="large"
          @click="toggleShowAll"
        >
          {{ showAllPositions ? '收起' : '展开更多' }}
          <el-icon class="el-icon--right" :class="{ 'is-rotate': showAllPositions }">
            <ArrowRight />
          </el-icon>
        </el-button>
      </div>

      <!-- 搜索无结果 -->
      <div v-else class="no-results">
        <div class="no-results-icon">🔍</div>
        <h3>未找到相关岗位</h3>
        <p>换个关键词试试，或浏览全部岗位列表</p>
        <el-button type="primary" plain @click="clearSearch">
          清除搜索
        </el-button>
      </div>

      <!-- 底部操作 -->
      <div class="selection-actions">
        <el-button 
          type="primary" 
          size="large"
          :disabled="!selectedPosition"
          @click="confirmPosition"
        >
          确认选择
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 步骤 2: 准备开始 -->
    <div v-else-if="currentStep === InterviewStep.PREPARING" class="preparing-panel">
      <div class="preparing-content glass-panel">
        <div class="preparing-header">
          <div class="preparing-icon-wrapper">
            <el-icon :size="32" color="#409EFF"><MagicStick /></el-icon>
          </div>
          <h2>准备开始面试</h2>
        </div>

        <!-- 已选岗位卡片 -->
        <div class="selected-position-card">
          <div class="sp-icon">
            <el-icon :size="40" color="#409EFF">
              <component :is="selectedPosition?.icon" />
            </el-icon>
          </div>
          <div class="sp-info">
            <h3>{{ selectedPosition?.name }}</h3>
            <p>{{ selectedPosition?.description }}</p>
          </div>
        </div>
        
        <!-- 面试类型选择 -->
        <div class="config-section">
          <div class="config-section-title">
            <el-icon><Briefcase /></el-icon>
            选择面试类型
          </div>
          <div class="type-options">
            <div
              v-for="type in interviewTypes"
              :key="type.value"
              class="type-option"
              :class="{ selected: selectedType === type.value }"
              @click="selectedType = type.value"
            >
              <div class="type-icon-wrapper">
                <el-icon :size="24" color="#409EFF">
                  <component :is="type.icon" />
                </el-icon>
              </div>
              <div class="type-info">
                <span class="type-label">{{ type.label }}</span>
                <span class="type-desc">{{ type.description }}</span>
              </div>
              <div class="type-check" v-if="selectedType === type.value">
                <el-icon><Check /></el-icon>
              </div>
            </div>
          </div>
        </div>

        <!-- 难度级别选择 -->
        <div class="config-section">
          <div class="config-section-title">
            <el-icon><TrendCharts /></el-icon>
            选择难度级别
          </div>
          <div class="difficulty-options">
            <div
              v-for="level in difficultyLevels"
              :key="level.value"
              class="difficulty-option"
              :class="{ selected: selectedDifficulty === level.value }"
              :style="selectedDifficulty === level.value ? { 
                background: level.bgColor, 
                borderColor: level.color,
                color: level.color 
              } : {}"
              @click="selectedDifficulty = level.value"
            >
              <span class="difficulty-label" :style="selectedDifficulty === level.value ? { color: level.color } : {}">
                {{ level.label }}
              </span>
              <span class="difficulty-desc">{{ level.description }}</span>
              <div class="difficulty-check" v-if="selectedDifficulty === level.value" :style="{ background: level.color }">
                <el-icon><Check /></el-icon>
              </div>
            </div>
          </div>
        </div>

        <!-- 预计时长 -->
        <div class="duration-display">
          <span class="duration-label">
            <el-icon><Timer /></el-icon>
            预计面试时长
          </span>
          <span class="duration-value">{{ interviewConfig.duration }} 分钟</span>
        </div>

        <!-- 面试小贴士 -->
        <div class="preparing-tips">
          <h4>💡 面试小贴士</h4>
          <ul>
            <li>保持网络畅通，选择安静的环境</li>
            <li>准备好纸笔，方便记录和整理思路</li>
            <li>回答问题时尽量详细，展示你的思考过程</li>
            <li>不必紧张，把AI面试官当成你的朋友</li>
          </ul>
        </div>

        <!-- 操作按钮 -->
        <div class="preparing-actions">
          <el-button size="large" @click="backToSelection">
            <el-icon><ArrowLeft /></el-icon>
            重新选择
          </el-button>
          <el-button type="primary" size="large" :icon="MagicStick" @click="startInterview">
            开始面试
          </el-button>
        </div>
      </div>
    </div>

    <!-- 步骤 3: 面试中 -->
    <template v-else-if="[InterviewStep.INTERVIEWING, InterviewStep.PAUSED, InterviewStep.FINISHED].includes(currentStep)">
      <div class="interview-main glass-panel">
        <!-- 左侧：数字人展示区 -->
        <div class="avatar-section">
          <div class="avatar-container" :class="aiEmotion">
            <div
              ref="virtualHumanContainerRef"
              class="virtual-human-renderer"
              :class="{ connected: virtualHumanStatus.isConnected, hidden: !isVideoOn }"
            >
              <div v-if="!virtualHumanStatus.isConnected && !virtualHumanStatus.isLoading" class="virtual-human-placeholder">
                <div class="placeholder-mark">AI</div>
                <strong>{{ virtualHumanStatus.error ? '虚拟人暂未连接' : '讯飞虚拟人面试官' }}</strong>
                <span>{{ virtualHumanStatus.error || '开始面试后自动连接并播报问题' }}</span>
              </div>
              <div v-if="virtualHumanStatus.isLoading" class="virtual-human-loading">
                <span class="loading-ring"></span>
                <span>正在连接讯飞虚拟人...</span>
              </div>
              <div v-if="!isVideoOn" class="virtual-human-offline">
                <el-icon><VideoPause /></el-icon>
                <span>数字人画面已关闭</span>
              </div>
            </div>

            <div class="virtual-human-toolbar">
              <div class="virtual-human-status">
                <span class="status-dot" :class="{ online: virtualHumanStatus.isConnected, speaking: digitalHumanSpeaking, error: virtualHumanStatus.error }"></span>
                {{ virtualHumanStatusText }}
              </div>
              <div class="virtual-human-actions">
                <el-select
                  v-model="virtualHumanVoice"
                  size="small"
                  class="voice-select"
                  :disabled="virtualHumanStatus.isLoading"
                  @change="handleVirtualHumanConfigChange"
                >
                  <el-option
                    v-for="voice in VirtualHumanConfig.VOICES"
                    :key="voice.value"
                    :label="`${voice.label} · ${voice.gender}`"
                    :value="voice.value"
                  />
                </el-select>
                <el-button
                  size="small"
                  :loading="virtualHumanStatus.isLoading"
                  :disabled="virtualHumanStatus.isLoading"
                  @click="ensureVirtualHumanConnected"
                >
                  {{ virtualHumanStatus.isConnected ? '已连接' : '连接' }}
                </el-button>
              </div>
            </div>

            <div v-if="digitalHumanSpeaking" class="virtual-human-speaking">
              <span v-for="i in 5" :key="i" :style="{ animationDelay: `${i * 0.08}s` }"></span>
            </div>
          </div>

          <!-- 快速统计 -->
          <div class="quick-stats">
            <div class="stat-item glass-card">
              <span class="stat-label">已提问</span>
              <span class="stat-value">{{ interviewStats.questionsAsked }}</span>
            </div>
            <div class="stat-item glass-card">
              <span class="stat-label">已回答</span>
              <span class="stat-value">{{ interviewStats.answersGiven }}</span>
            </div>
            <div class="stat-item glass-card">
              <span class="stat-label">流畅度</span>
              <span class="stat-value">{{ interviewStats.fluency }}%</span>
            </div>
          </div>
        </div>

        <!-- 右侧：对话区 -->
        <div class="chat-section glass-card">
          <div class="chat-messages" ref="chatContainerRef">
            <div 
              v-for="msg in messages" 
              :key="msg.id"
              class="message"
              :class="msg.role"
            >
              <div class="message-avatar">
                <span v-if="msg.role === 'ai'">🤖</span>
                <span v-else>👤</span>
              </div>
              <div class="message-content">
                <div class="message-bubble">{{ msg.content }}</div>
                <div class="message-time">
                  {{ msg.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }}
                </div>
              </div>
            </div>
            
            <div class="message ai typing" v-if="aiSpeaking">
              <div class="message-avatar"><span>🤖</span></div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <div class="input-toolbar">
              <el-button 
                :icon="isMuted ? Mute : Microphone" 
                circle
                :type="isMuted ? 'info' : 'primary'"
                @click="isMuted = !isMuted"
              />
              <el-button 
                :icon="isVideoOn ? Monitor : VideoPause" 
                circle
                :type="isVideoOn ? 'primary' : 'info'"
                @click="isVideoOn = !isVideoOn"
              />
              <div class="toolbar-divider"></div>
              <el-button 
                type="success" 
                :icon="TrendCharts"
                @click="viewInterviewResult"
                class="view-result-btn"
              >
                查看面试结果
              </el-button>
            </div>
            <div class="input-box">
              <el-input
                v-model="userInput"
                type="textarea"
                :rows="2"
                placeholder="输入你的回答..."
                @keyup.enter.prevent="sendMessage"
                :disabled="currentStep !== InterviewStep.INTERVIEWING"
              />
              <el-button 
                type="primary" 
                :icon="ChatDotSquare"
                @click="sendMessage"
                :disabled="!userInput.trim() || currentStep !== InterviewStep.INTERVIEWING"
              >
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部功能区 -->
      <div class="interview-footer" v-if="currentStep === InterviewStep.FINISHED">
        <div class="footer-actions">
          <el-button :icon="TrendCharts" type="primary" @click="viewResults">
            查看面试结果
          </el-button>
          <el-button :icon="RefreshRight" @click="restartInterview">
            重新开始
          </el-button>
        </div>
      </div>
    </template>

    <!-- 步骤 4: 面试结果报告 -->
    <div v-else-if="currentStep === InterviewStep.RESULT" class="result-panel">
      <!-- 结果头部 -->
      <div class="result-header">
        <div class="result-title-section">
          <div class="result-icon-wrapper">
            <el-icon :size="32" color="#fff"><Trophy /></el-icon>
          </div>
          <div class="result-title-info">
            <h2>面试完成！</h2>
            <p>{{ selectedPosition?.name }} · {{ getDifficultyLabel(interviewConfig.difficulty) }}难度</p>
          </div>
        </div>
        <div class="overall-score">
          <div class="score-circle">
            <span class="score-value">{{ interviewResult.overallScore }}</span>
            <span class="score-label">综合评分</span>
          </div>
        </div>
      </div>

      <!-- 核心指标卡片 -->
      <div class="metrics-cards">
        <div class="metric-card">
          <div class="metric-icon blue">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="metric-info">
            <span class="metric-value">{{ interviewResult.interviewRecord.answeredQuestions }}/{{ interviewResult.interviewRecord.totalQuestions }}</span>
            <span class="metric-label">答题完成率</span>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon green">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="metric-info">
            <span class="metric-value">{{ interviewResult.interviewRecord.avgResponseTime }}s</span>
            <span class="metric-label">平均回答时长</span>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon purple">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="metric-info">
            <span class="metric-value">{{ interviewResult.interviewRecord.fluencyScore }}%</span>
            <span class="metric-label">表达流畅度</span>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <el-row :gutter="24">
          <el-col :xs="24" :md="12">
            <div class="chart-card glass-card">
              <div class="chart-header">
                <h3>能力维度雷达图</h3>
                <p>全方位评估各维度表现</p>
              </div>
              <div ref="radarChartRef" class="chart-container"></div>
            </div>
          </el-col>
          <el-col :xs="24" :md="12">
            <div class="chart-card glass-card">
              <div class="chart-header">
                <h3>技能掌握程度</h3>
                <p>各项技能得分详情</p>
              </div>
              <div ref="barChartRef" class="chart-container"></div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 能力短板分析 -->
      <div class="weakness-section">
        <div class="section-header">
          <div class="section-icon orange">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="section-title">
            <h3>能力短板定位</h3>
            <p>AI智能识别需要重点提升的领域</p>
          </div>
        </div>
        <div class="weakness-list">
          <div 
            v-for="(weakness, index) in interviewResult.weaknessAnalysis" 
            :key="index"
            class="weakness-item"
            :class="weakness.severity"
          >
            <div class="weakness-severity-badge" :class="weakness.severity">
              {{ weakness.severity === 'high' ? '高' : weakness.severity === 'medium' ? '中' : '低' }}
            </div>
            <div class="weakness-content">
              <h4>{{ weakness.area }}</h4>
              <p>{{ weakness.suggestion }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 个性化提升建议 -->
      <div class="suggestions-section">
        <div class="section-header">
          <div class="section-icon green">
            <el-icon><Lightning /></el-icon>
          </div>
          <div class="section-title">
            <h3>个性化提升建议</h3>
            <p>根据你的面试表现定制的学习计划</p>
          </div>
        </div>
        <div class="suggestions-grid">
          <div 
            v-for="(suggestion, index) in interviewResult.improvementSuggestions" 
            :key="index"
            class="suggestion-card glass-card"
          >
            <div class="suggestion-header">
              <span class="suggestion-index">{{ index + 1 }}</span>
              <h4>{{ suggestion.category }}</h4>
            </div>
            <ul class="suggestion-list">
              <li v-for="(item, idx) in suggestion.items" :key="idx">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- AI评语 -->
      <div class="ai-feedback-section">
        <div class="feedback-card glass-card">
          <div class="feedback-header">
            <div class="ai-avatar-mini">
              <span>🤖</span>
            </div>
            <h3>AI 面试官评语</h3>
          </div>
          <p class="feedback-content">{{ interviewResult.aiFeedback }}</p>
        </div>
      </div>

      <!-- 结果页面操作按钮 -->
      <div class="result-actions">
        <el-button :icon="Download" type="primary" size="large">
          下载报告
        </el-button>
        <el-button :icon="Share" type="success" size="large">
          分享成绩
        </el-button>
        <el-button :icon="RefreshRight" size="large" @click="restartInterview">
          再来一次
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
// ========== 项目统一风格变量 ==========
$primary-color: #409EFF;
$success-color: #10b981;
$warning-color: #f59e0b;
$danger-color: #ef4444;
$text-primary: #2c3e50;
$text-secondary: #606266;
$text-muted: #909399;
$bg-primary: #ffffff;
$bg-secondary: #f5f7fa;

// ========== 页面容器 ==========
.ai-interview-page {
  padding: 24px;
  min-height: calc(100vh - 80px);
  background: 
    radial-gradient(ellipse at top left, rgba(64, 158, 255, 0.05), transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(118, 75, 162, 0.05), transparent 50%),
    $bg-secondary;
}

// ========== 页面标题 ==========
.page-header {
  text-align: center;
  margin-bottom: 32px;
  
  .page-title {
    font-size: 32px;
    font-weight: 800;
    color: $text-primary;
    margin: 0 0 8px;
    
    .gradient-text {
      background: linear-gradient(135deg, #409EFF 0%, #764BA2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }
  
  .page-subtitle {
    font-size: 16px;
    color: $text-secondary;
    margin: 0;
  }
}

// ========== 玻璃拟态面板 ==========
.glass-panel {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.glass-card {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  
  &:hover {
    background: rgba(255, 255, 255, 0.7);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  }
}

// ========== 面试头部卡片 ==========
.interview-header-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar-small {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409EFF 0%, #764BA2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  
  .avatar-pulse {
    position: absolute;
    inset: -4px;
    border-radius: 16px;
    border: 2px solid #409EFF;
    opacity: 0;
    animation: pulse 2s infinite;
    
    &.speaking {
      animation: pulse 1s infinite;
    }
  }
  
  .ai-icon {
    font-size: 24px;
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0; }
  50% { transform: scale(1.1); opacity: 0.5; }
}

.interview-info {
  h3 {
    font-size: 16px;
    font-weight: 700;
    color: $text-primary;
    margin: 0;
  }
  
  p {
    font-size: 13px;
    color: $text-muted;
    margin: 4px 0 0;
  }
}

.header-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 200px;
}

.timer-display {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 700;
  color: $text-primary;
  font-variant-numeric: tabular-nums;
  
  &.warning {
    color: $warning-color;
    animation: blink 1s infinite;
  }
  
  .el-icon {
    font-size: 20px;
    color: $primary-color;
  }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #764BA2);
  border-radius: 2px;
  transition: width 1s linear;
}

.header-right {
  display: flex;
  gap: 8px;
}

.control-btn {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: $text-secondary;
  
  &:hover {
    background: rgba(255, 255, 255, 1);
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.danger:hover {
    background: $danger-color;
    border-color: $danger-color;
    color: #fff;
  }
}

// ========== 选择面板 ==========
.selection-panel {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

// 搜索栏
.search-section {
  margin-bottom: 24px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  padding: 0 16px;
  transition: all 0.3s ease;
  
  &:focus-within {
    background: #fff;
    border-color: $primary-color;
    box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.15);
  }
  
  .search-icon {
    font-size: 18px;
    color: $text-muted;
    margin-right: 12px;
  }
  
  .search-input {
    flex: 1;
    height: 48px;
    background: transparent;
    border: none;
    outline: none;
    color: $text-primary;
    font-size: 15px;
    
    &::placeholder {
      color: $text-muted;
    }
  }
  
  .clear-icon {
    font-size: 16px;
    color: $text-muted;
    cursor: pointer;
    padding: 4px;
    border-radius: 50%;
    transition: all 0.2s;
    
    &:hover {
      background: rgba(0, 0, 0, 0.05);
      color: $text-primary;
    }
  }
}

.search-result-count {
  margin-top: 8px;
  font-size: 13px;
  color: $text-muted;
  
  span {
    color: $primary-color;
    font-weight: 700;
  }
}

// 岗位网格
.positions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.position-card {
  padding: 24px;
  cursor: pointer;
  position: relative;
  
  &.selected {
    background: rgba(64, 158, 255, 0.08);
    border-color: $primary-color;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2), 0 8px 24px rgba(64, 158, 255, 0.1);
  }
  
  .position-icon {
    width: 56px;
    height: 56px;
    background: rgba(64, 158, 255, 0.1);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;
  }
  
  .position-info {
    h4 {
      font-size: 17px;
      font-weight: 700;
      color: $text-primary;
      margin: 0 0 4px;
    }
    
    .position-category {
      font-size: 12px;
      color: $text-muted;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .position-desc {
      font-size: 13px;
      color: $text-secondary;
      margin: 10px 0;
      line-height: 1.5;
    }
    
    .position-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      
      .tag {
        font-size: 11px;
        padding: 4px 8px;
        background: rgba(64, 158, 255, 0.1);
        color: $primary-color;
        border-radius: 4px;
        font-weight: 500;
      }
    }
  }
  
  .position-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    
    .difficulty-badge {
      font-size: 12px;
      padding: 4px 10px;
      border-radius: 12px;
      font-weight: 600;
      
      &.easy {
        background: rgba(16, 185, 129, 0.1);
        color: $success-color;
      }
      
      &.medium {
        background: rgba(245, 158, 11, 0.1);
        color: $warning-color;
      }
      
      &.hard {
        background: rgba(239, 68, 68, 0.1);
        color: $danger-color;
      }
    }
    
    .duration {
      font-size: 12px;
      color: $text-muted;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }
  
  .selection-check {
    position: absolute;
    top: 16px;
    right: 16px;
    width: 24px;
    height: 24px;
    background: $primary-color;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    animation: scaleIn 0.2s ease;
  }
}

@keyframes scaleIn {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

// 无结果
.no-results {
  text-align: center;
  padding: 60px;
  
  .no-results-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.6;
  }
  
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 8px;
  }
  
  p {
    font-size: 14px;
    color: $text-muted;
    margin: 0 0 20px;
  }
}

// 展开/收起按钮
.expand-actions {
  display: flex;
  justify-content: center;
  margin: 8px 0 24px;
  
  .el-icon {
    transition: transform 0.3s ease;
    
    &.is-rotate {
      transform: rotate(-90deg);
    }
  }
}

// 底部操作
.selection-actions {
  display: flex;
  justify-content: center;
  padding-top: 16px;
}

// ========== 准备面板 ==========
.preparing-panel {
  display: flex;
  justify-content: center;
  padding: 0 24px;
}

.preparing-content {
  max-width: 560px;
  width: 100%;
  padding: 40px;
}

.preparing-header {
  text-align: center;
  margin-bottom: 32px;
  
  .preparing-icon-wrapper {
    width: 64px;
    height: 64px;
    background: rgba(64, 158, 255, 0.1);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 16px;
  }
  
  h2 {
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;
    margin: 0;
  }
}

// 已选岗位卡片
.selected-position-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(64, 158, 255, 0.08);
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 28px;
  
  .sp-icon {
    width: 64px;
    height: 64px;
    background: rgba(64, 158, 255, 0.1);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .sp-info {
    h3 {
      font-size: 18px;
      font-weight: 700;
      color: $text-primary;
      margin: 0 0 4px;
    }
    
    p {
      font-size: 13px;
      color: $text-secondary;
      margin: 0;
    }
  }
}

// 配置区域
.config-section {
  margin-bottom: 24px;
}

.config-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: $text-secondary;
  margin-bottom: 12px;
  
  .el-icon {
    color: $text-muted;
  }
}

// 类型选项
.type-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.type-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.8);
    border-color: rgba(64, 158, 255, 0.3);
  }
  
  &.selected {
    background: rgba(64, 158, 255, 0.08);
    border-color: $primary-color;
  }
  
  .type-icon-wrapper {
    width: 48px;
    height: 48px;
    background: rgba(64, 158, 255, 0.1);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  
  .type-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  
  .type-label {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
  }
  
  .type-desc {
    font-size: 12px;
    color: $text-muted;
  }
  
  .type-check {
    width: 22px;
    height: 22px;
    background: $primary-color;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 12px;
  }
}

// 难度选项
.difficulty-options {
  display: flex;
  gap: 12px;
}

.difficulty-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 12px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  
  &:hover {
    background: rgba(255, 255, 255, 0.8);
    transform: translateY(-2px);
  }
  
  &.selected {
    background: rgba(255, 255, 255, 0.9);
  }
  
  .difficulty-label {
    font-size: 16px;
    font-weight: 700;
  }
  
  .difficulty-desc {
    font-size: 11px;
    color: $text-muted;
    text-align: center;
    line-height: 1.3;
  }
  
  .difficulty-check {
    position: absolute;
    top: -8px;
    right: -8px;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
}

// 时长显示
.duration-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 12px;
  margin-bottom: 24px;
  
  .duration-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: $success-color;
    font-weight: 500;
    
    .el-icon {
      font-size: 18px;
    }
  }
  
  .duration-value {
    font-size: 16px;
    font-weight: 700;
    color: $success-color;
  }
}

// 面试小贴士
.preparing-tips {
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 28px;
  
  h4 {
    font-size: 14px;
    font-weight: 700;
    color: $warning-color;
    margin: 0 0 12px;
  }
  
  ul {
    margin: 0;
    padding-left: 18px;
  }
  
  li {
    font-size: 13px;
    color: $text-secondary;
    margin-bottom: 8px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
}

// 准备操作按钮
.preparing-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

// ========== 面试主界面 ==========
.interview-main {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 24px;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.avatar-container {
  flex: 1;
  background: linear-gradient(160deg, #07111f 0%, #12233a 52%, #172417 100%);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  min-height: 400px;
  box-shadow: inset 0 0 60px rgba(64, 158, 255, 0.08);
}

.virtual-human-renderer {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 50% 100%, rgba(16, 185, 129, 0.16), transparent 38%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0));
  transition: opacity 0.25s ease;

  &.hidden {
    opacity: 0.18;
    filter: grayscale(1);
  }

  :deep(video),
  :deep(canvas) {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain;
  }
}

.virtual-human-placeholder,
.virtual-human-loading,
.virtual-human-offline {
  position: absolute;
  z-index: 4;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-align: center;
  color: rgba(255, 255, 255, 0.82);
  padding: 24px;
}

.placeholder-mark {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.22);
  color: #fff;
  font-size: 22px;
  font-weight: 800;
}

.virtual-human-placeholder {
  strong {
    font-size: 18px;
    color: #fff;
  }

  span {
    max-width: 260px;
    font-size: 13px;
    line-height: 1.6;
    color: rgba(255, 255, 255, 0.62);
  }
}

.virtual-human-loading {
  inset: 0;
  background: rgba(7, 17, 31, 0.62);
  backdrop-filter: blur(3px);
  font-size: 14px;
}

.loading-ring {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.24);
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.virtual-human-offline {
  inset: 0;
  background: rgba(7, 17, 31, 0.72);
  font-size: 14px;

  .el-icon {
    font-size: 28px;
  }
}

.virtual-human-toolbar {
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: 16px;
  z-index: 6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(9, 18, 31, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(12px);
}

.virtual-human-status {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  color: rgba(255, 255, 255, 0.86);
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
  flex-shrink: 0;

  &.online {
    background: #10b981;
    box-shadow: 0 0 0 5px rgba(16, 185, 129, 0.12);
  }

  &.speaking {
    background: #409EFF;
    animation: pulse-dot 0.9s ease-in-out infinite;
  }

  &.error {
    background: #ef4444;
    box-shadow: 0 0 0 5px rgba(239, 68, 68, 0.12);
  }
}

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); opacity: 0.72; }
  50% { transform: scale(1.35); opacity: 1; }
}

.virtual-human-actions {
  display: flex;
  align-items: center;
  gap: 8px;

  .voice-select {
    width: 120px;
  }
}

.virtual-human-speaking {
  position: absolute;
  left: 50%;
  bottom: 78px;
  z-index: 6;
  transform: translateX(-50%);
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 26px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(64, 158, 255, 0.16);
  border: 1px solid rgba(64, 158, 255, 0.2);

  span {
    width: 4px;
    height: 18px;
    border-radius: 999px;
    background: #8cc8ff;
    animation: wave 0.55s ease-in-out infinite;
  }
}

@keyframes wave {
  0%, 100% { transform: scaleY(0.35); }
  50% { transform: scaleY(1); }
}

// 快速统计
.quick-stats {
  display: flex;
  gap: 12px;
}

.stat-item {
  flex: 1;
  padding: 16px;
  text-align: center;
  
  .stat-label {
    display: block;
    font-size: 12px;
    color: $text-muted;
    margin-bottom: 6px;
  }
  
  .stat-value {
    font-size: 22px;
    font-weight: 700;
    color: $text-primary;
  }
}

// 对话区
.chat-section {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 400px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  
  &.user {
    flex-direction: row-reverse;
    
    .message-content {
      align-items: flex-end;
    }
    
    .message-bubble {
      background: linear-gradient(135deg, #409EFF 0%, #764BA2 100%);
      color: #fff;
      border-radius: 16px 16px 4px 16px;
    }
  }
  
  &.ai .message-bubble {
    background: rgba(255, 255, 255, 0.8);
    color: $text-primary;
    border-radius: 16px 16px 16px 4px;
    border: 1px solid rgba(0, 0, 0, 0.06);
  }
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 75%;
}

.message-bubble {
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.message-time {
  font-size: 11px;
  color: $text-muted;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px 16px 16px 4px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  
  span {
    width: 8px;
    height: 8px;
    background: $text-muted;
    border-radius: 50%;
    animation: typing 1s infinite;
    
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes typing {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

// 输入区
.chat-input-area {
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.5);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.input-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  align-items: center;

  .toolbar-divider {
    width: 1px;
    height: 24px;
    background: rgba(0, 0, 0, 0.1);
    margin: 0 4px;
  }

  .view-result-btn {
    margin-left: auto;
    padding: 8px 16px;
    font-weight: 500;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
    }
  }
}

.input-box {
  display: flex;
  gap: 12px;
  
  :deep(.el-textarea__inner) {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.08);
    color: $text-primary;
    border-radius: 12px;
    resize: none;
    
    &::placeholder {
      color: $text-muted;
    }
    
    &:focus {
      border-color: $primary-color;
    }
  }
}

// 底部功能区
.interview-footer {
  padding: 24px;
  display: flex;
  justify-content: center;
}

.footer-actions {
  display: flex;
  gap: 16px;
}

// ========== 面试结果页面 ==========
.result-panel {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 40px;
}

// 结果头部
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #409EFF 0%, #764BA2 100%);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  color: #fff;
}

.result-title-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.result-icon-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-title-info {
  h2 {
    font-size: 28px;
    font-weight: 700;
    margin: 0 0 8px;
  }
  
  p {
    font-size: 15px;
    opacity: 0.9;
    margin: 0;
  }
}

.overall-score {
  .score-circle {
    width: 120px;
    height: 120px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 4px solid rgba(255, 255, 255, 0.3);
  }
  
  .score-value {
    font-size: 42px;
    font-weight: 800;
    line-height: 1;
  }
  
  .score-label {
    font-size: 13px;
    opacity: 0.9;
    margin-top: 4px;
  }
}

// 核心指标卡片
.metrics-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  }
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  
  &.blue {
    background: rgba(64, 158, 255, 0.1);
    color: #409EFF;
  }
  
  &.green {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
  }
  
  &.purple {
    background: rgba(118, 75, 162, 0.1);
    color: #764BA2;
  }
}

.metric-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.metric-label {
  font-size: 13px;
  color: #606266;
}

// 图表区域
.charts-section {
  margin-bottom: 24px;
  
  .chart-card {
    padding: 24px;
    height: 100%;
  }
  
  .chart-header {
    margin-bottom: 16px;
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #2c3e50;
      margin: 0 0 4px;
    }
    
    p {
      font-size: 13px;
      color: #909399;
      margin: 0;
    }
  }
  
  .chart-container {
    height: 300px;
  }
}

// 短板分析
.weakness-section,
.suggestions-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.section-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  
  &.orange {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
  }
  
  &.green {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
  }
}

.section-title {
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0 0 4px;
  }
  
  p {
    font-size: 13px;
    color: #909399;
    margin: 0;
  }
}

.weakness-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.weakness-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border-left: 4px solid;
  
  &.high {
    border-left-color: #ef4444;
  }
  
  &.medium {
    border-left-color: #f59e0b;
  }
  
  &.low {
    border-left-color: #10b981;
  }
}

.weakness-severity-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
  
  &.high {
    background: #ef4444;
  }
  
  &.medium {
    background: #f59e0b;
  }
  
  &.low {
    background: #10b981;
  }
}

.weakness-content {
  flex: 1;
  
  h4 {
    font-size: 15px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0 0 6px;
  }
  
  p {
    font-size: 13px;
    color: #606266;
    margin: 0;
    line-height: 1.6;
  }
}

// 建议网格
.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.suggestion-card {
  padding: 24px;
  
  .suggestion-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  }
  
  .suggestion-index {
    width: 28px;
    height: 28px;
    background: linear-gradient(135deg, #409EFF, #764BA2);
    color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 600;
  }
  
  h4 {
    font-size: 15px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0;
  }
}

.suggestion-list {
  margin: 0;
  padding-left: 18px;
  
  li {
    font-size: 13px;
    color: #606266;
    margin-bottom: 10px;
    line-height: 1.5;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
}

// AI评语
.ai-feedback-section {
  margin-bottom: 32px;
}

.feedback-card {
  padding: 28px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 1px solid rgba(64, 158, 255, 0.15);
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.ai-avatar-mini {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #409EFF, #764BA2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.feedback-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.feedback-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin: 0;
  padding-left: 52px;
}

// 结果页面操作按钮
.result-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 16px;
}

// ========== 响应式适配 ==========
@media (max-width: 992px) {
  .interview-main {
    grid-template-columns: 1fr;
  }
  
  .avatar-section {
    min-height: auto;
  }
  
  .avatar-container {
    min-height: 300px;
  }
  
  // 结果页面响应式
  .result-header {
    flex-direction: column;
    gap: 24px;
    text-align: center;
  }
  
  .result-title-section {
    flex-direction: column;
  }
  
  .metrics-cards {
    grid-template-columns: 1fr;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .ai-interview-page {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .interview-header-card {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
  
  .header-center {
    width: 100%;
  }
  
  .selection-panel {
    padding: 20px;
  }
  
  .positions-grid {
    grid-template-columns: 1fr;
  }
  
  .preparing-content {
    padding: 24px;
  }
  
  .difficulty-options {
    flex-direction: column;
  }
  
  .difficulty-option {
    flex-direction: row;
    justify-content: space-between;
    padding: 12px 16px;
    
    .difficulty-desc {
      text-align: right;
    }
  }
  
  .preparing-actions {
    flex-direction: column;
  }
  
  .interview-main {
    padding: 16px;
  }
  
  // 结果页面移动端适配
  .result-panel {
    padding: 0 16px 32px;
  }
  
  .result-header {
    padding: 24px;
    
    h2 {
      font-size: 22px;
    }
  }
  
  .overall-score .score-circle {
    width: 100px;
    height: 100px;
    
    .score-value {
      font-size: 36px;
    }
  }
  
  .weakness-item {
    flex-direction: column;
    gap: 12px;
  }
  
  .feedback-content {
    padding-left: 0;
    padding-top: 16px;
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style>
