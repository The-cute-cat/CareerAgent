// 面试结果模拟数据
export const mockInterviewResult = {
  // 综合评分
  overallScore: 82,
  
  // 能力维度评分
  dimensionScores: {
    technical: 85,
    communication: 78,
    logic: 88,
    expression: 80,
    attitude: 92
  },
  
  // 技能掌握程度评估
  skillAssessment: [
    { name: 'HTML/CSS基础', score: 90, fullMark: 100 },
    { name: 'JavaScript/ES6+', score: 85, fullMark: 100 },
    { name: 'Vue/React框架', score: 88, fullMark: 100 },
    { name: '性能优化', score: 75, fullMark: 100 },
    { name: '工程化实践', score: 70, fullMark: 100 },
    { name: '代码规范', score: 82, fullMark: 100 },
    { name: '沟通能力', score: 80, fullMark: 100 },
    { name: '问题解决', score: 86, fullMark: 100 }
  ],
  
  // 能力短板分析
  weaknessAnalysis: [
    {
      area: '性能优化深入理解',
      severity: 'high',
      suggestion: '建议深入学习浏览器渲染原理、懒加载、代码分割等优化技术，可以通过阅读《高性能JavaScript》和实践Webpack优化配置来提升'
    },
    {
      area: '工程化实践经验',
      severity: 'medium',
      suggestion: '建议多实践Webpack/Vite配置，了解CI/CD流程，尝试搭建自己的前端工程化脚手架'
    },
    {
      area: '复杂场景问题解决',
      severity: 'medium',
      suggestion: '建议多做算法题和实际项目中的复杂需求拆解，提升架构设计能力'
    },
    {
      area: 'TypeScript高级应用',
      severity: 'low',
      suggestion: '建议深入学习TypeScript泛型、类型体操等高级特性，提升代码类型安全'
    }
  ],
  
  // 个性化提升建议
  improvementSuggestions: [
    {
      category: '技术能力提升',
      items: [
        '深入学习Vue3源码，理解响应式原理和虚拟DOM实现',
        '掌握前端性能优化最佳实践，包括代码分割、懒加载、缓存策略',
        '学习TypeScript高级用法和类型体操，提升代码健壮性',
        '了解微前端架构设计，掌握qiankun/module-federation等方案'
      ]
    },
    {
      category: '项目经验积累',
      items: [
        '参与开源项目贡献，如Vue、React生态相关项目',
        '完成一个完整的技术博客项目，包含前后端和部署',
        '实践微前端架构设计，搭建多团队协作的解决方案',
        '尝试开发一个Chrome插件或VS Code插件'
      ]
    },
    {
      category: '软实力提升',
      items: [
        '提升技术表达和文档能力，尝试写技术博客或做内部分享',
        '练习结构化思考和表达，学会STAR法则描述项目经历',
        '加强团队协作沟通技巧，提升跨部门协作效率',
        '培养产品思维，从用户角度思考技术方案'
      ]
    }
  ],
  
  // 面试过程记录
  interviewRecord: {
    totalQuestions: 12,
    answeredQuestions: 11,
    avgResponseTime: 45,
    fluencyScore: 85
  },
  
  // AI面试官评语
  aiFeedback: '整体表现良好，技术基础扎实，对主流框架有较好的理解。在Vue响应式原理和组件通信方面有较深入的认识。建议在性能优化和工程化方面加强学习，同时提升复杂问题的分析和解决能力。表达清晰，态度积极，具备较好的团队协作潜力。建议多关注前端新技术动态，保持持续学习的热情。'
}

// 面试聊天记录模拟
export const mockChatHistory = [
  {
    id: '1',
    role: 'ai',
    content: '你好！我是你的AI面试官。准备好了吗？我们可以随时开始面试。',
    timestamp: new Date('2024-01-15 14:00:00'),
    emotion: 'happy'
  },
  {
    id: '2',
    role: 'user',
    content: '你好，我准备好了，请开始吧。',
    timestamp: new Date('2024-01-15 14:00:05')
  },
  {
    id: '3',
    role: 'ai',
    content: '好的，让我们开始吧！请先简单介绍一下你自己。',
    timestamp: new Date('2024-01-15 14:00:08'),
    emotion: 'encouraging'
  },
  {
    id: '4',
    role: 'user',
    content: '我是一名有3年前端开发经验的工程师，主要技术栈是Vue和React。之前在互联网公司负责过多个中大型项目的前端开发工作，熟悉前端工程化和性能优化。',
    timestamp: new Date('2024-01-15 14:00:25')
  },
  {
    id: '5',
    role: 'ai',
    content: '很好的自我介绍！能详细说说你在Vue项目中遇到的比较有挑战性的问题，以及你是如何解决的吗？',
    timestamp: new Date('2024-01-15 14:00:35'),
    emotion: 'thinking'
  },
  {
    id: '6',
    role: 'user',
    content: '在一个大型后台管理系统的项目中，我们遇到了首屏加载过慢的问题。我通过代码分割、路由懒加载、组件异步加载等方式进行了优化。同时使用Webpack Bundle Analyzer分析打包体积，将第三方库进行CDN引入，最终将首屏加载时间从5s降低到了1.5s。',
    timestamp: new Date('2024-01-15 14:01:05')
  },
  {
    id: '7',
    role: 'ai',
    content: '不错的优化思路！能说说Vue的响应式原理吗？Vue2和Vue3有什么区别？',
    timestamp: new Date('2024-01-15 14:01:20'),
    emotion: 'neutral'
  },
  {
    id: '8',
    role: 'user',
    content: 'Vue2使用Object.defineProperty进行数据劫持，而Vue3使用Proxy。Proxy可以监听整个对象，不需要像Vue2那样递归遍历对象属性。Vue3的响应式系统性能更好，也解决了Vue2中数组和对象新增属性无法监听的问题。',
    timestamp: new Date('2024-01-15 14:01:45')
  },
  {
    id: '9',
    role: 'ai',
    content: '很好！继续下一个问题。你在团队协作中遇到过什么困难吗？是如何解决的？',
    timestamp: new Date('2024-01-15 14:02:00'),
    emotion: 'happy'
  },
  {
    id: '10',
    role: 'user',
    content: '在项目紧张的时候，团队成员对技术方案有不同意见。我组织了一次技术评审会议，让每个人阐述自己的观点，然后我们一起评估各种方案的优缺点，最终达成共识。这个过程让我学会了倾听和沟通的重要性。',
    timestamp: new Date('2024-01-15 14:02:30')
  }
]

// 面试统计数据
export const mockInterviewStats = {
  questionsAsked: 12,
  answersGiven: 11,
  fluency: 85,
  technicalScore: 85,
  communicationScore: 80
}

// 面试过程时间轴数据
export const mockTimelineData = [
  { time: '00:00', event: '面试开始', type: 'start' },
  { time: '00:30', event: '自我介绍环节', type: 'normal' },
  { time: '02:15', event: '技术问题环节', type: 'normal' },
  { time: '05:45', event: '项目经验提问', type: 'normal' },
  { time: '08:20', event: '场景题讨论', type: 'highlight' },
  { time: '12:30', event: '软技能评估', type: 'normal' },
  { time: '15:00', event: '面试结束', type: 'end' }
]

// 能力变化趋势数据（多次面试对比）
export const mockProgressTrend = [
  { name: '第1次面试', technical: 65, communication: 60, logic: 70 },
  { name: '第2次面试', technical: 72, communication: 68, logic: 75 },
  { name: '第3次面试', technical: 78, communication: 72, logic: 80 },
  { name: '本次面试', technical: 85, communication: 78, logic: 88 }
]

// 技能雷达图对比数据（当前 vs 目标）
export const mockRadarComparison = {
  current: [85, 78, 88, 80, 92],
  target: [90, 85, 90, 85, 90],
  labels: ['技术能力', '沟通能力', '逻辑思维', '表达能力', '态度素养']
}

// 答题情况统计
export const mockAnswerStats = {
  categories: ['基础知识', '框架原理', '性能优化', '工程化', '软技能'],
  correct: [5, 4, 2, 2, 4],
  total: [5, 5, 3, 3, 4],
  avgTime: [30, 45, 60, 50, 40]
}

// 常用词汇分析
export const mockWordAnalysis = [
  { word: 'Vue', count: 12 },
  { word: '组件', count: 8 },
  { word: '优化', count: 6 },
  { word: '性能', count: 5 },
  { word: '响应式', count: 4 },
  { word: '团队协作', count: 3 },
  { word: 'Webpack', count: 3 },
  { word: '异步', count: 2 }
]

// 情感分析数据
export const mockEmotionAnalysis = {
  confidence: 75,      // 自信度
  nervousness: 20,     // 紧张度
  enthusiasm: 85,      // 热情度
  pressure: 30,        // 压力感
  overall: 'positive'  // 整体倾向
}

export default {
  mockInterviewResult,
  mockChatHistory,
  mockInterviewStats,
  mockTimelineData,
  mockProgressTrend,
  mockRadarComparison,
  mockAnswerStats,
  mockWordAnalysis,
  mockEmotionAnalysis
}
