/**
 * 语音输入完整模拟数据
 *
 * 功能说明：
 * 1. 提供符合 CareerFormData 结构的完整问答式采集流程
 * 2. 必填字段必须回答，非必填字段可由用户自主跳过
 * 3. 素质测评以问答形式呈现
 * 4. 支持跳转到人岗匹配界面和填写到表单的操作
 */

import type { QuizDetailItem } from '@/types/careerform_report'

// ==================== 类型定义 ====================

/** 语音场景类型 */
export type VoiceSceneKey = 'campus' | 'skill' | 'experience' | 'assessment' | 'career'

/** 语音问题配置 */
export interface VoiceQuestionConfig {
  /** 字段标识 */
  field: string
  /** 所属场景 */
  scene: VoiceSceneKey
  /** 问题文本 */
  question: string
  /** 示例回答（用于模拟识别） */
  sampleAnswer: string
  /** 是否为必填项 */
  required: boolean
  /** 字段分组（用于显示进度） */
  group: string
  /** 跳过提示语 */
  skipHint?: string
}

/** 完整语音答案集合 */
export interface CompleteVoiceAnswers {
  // ===== 必填字段 =====
  /** 学历信息 */
  education: string
  /** 专业 */
  major: string
  /** 毕业时间 */
  graduationDate: string
  /** 语言能力 */
  language: string
  /** 技能列表 */
  skills: string
  /** 工具列表 */
  tools: string
  /** 项目/实习经历 */
  experience: string
  /** 目标岗位 */
  targetJob: string
  /** 目标行业 */
  targetIndustry: string

  // ===== 非必填字段 =====
  /** 证书 */
  certificates?: string
  /** 代码能力链接 */
  codeAbility?: string
  /** 创新案例 */
  innovation?: string

  // ===== 素质测评（问答形式）=====
  /** 沟通能力 - 选择题1 */
  communication_q1?: string
  /** 沟通能力 - 问答题 */
  communication_open?: string
  /** 抗压能力 - 选择题1 */
  stress_q1?: string
  /** 抗压能力 - 问答题 */
  stress_open?: string
  /** 学习能力 - 选择题1 */
  learning_q1?: string
  /** 学习能力 - 问答题 */
  learning_open?: string
}

/** 场景信息 */
export interface VoiceSceneInfo {
  key: VoiceSceneKey
  title: string
  description: string
  icon: string
  className: string
}

// ==================== 场景定义 ====================

export const voiceScenes: Record<VoiceSceneKey, VoiceSceneInfo> = {
  campus: {
    key: 'campus',
    title: '基础信息',
    description: '学历、专业、语言能力',
    icon: '🎓',
    className: 'scene-campus',
  },
  skill: {
    key: 'skill',
    title: '技能工具',
    description: '专业技能、开发工具、证书',
    icon: '💻',
    className: 'scene-skill',
  },
  experience: {
    key: 'experience',
    title: '经历项目',
    description: '项目经验、实习经历、创新案例',
    icon: '🚀',
    className: 'scene-experience',
  },
  assessment: {
    key: 'assessment',
    title: '素质测评',
    description: '沟通、抗压、学习能力评估',
    icon: '📊',
    className: 'scene-assessment',
  },
  career: {
    key: 'career',
    title: '职业意向',
    description: '目标岗位、期望行业',
    icon: '🎯',
    className: 'scene-career',
  },
}

// ==================== 完整问答列表 ====================

/**
 * 完整的语音输入问答配置
 *
 * 设计原则：
 * 1. 必填字段（required: true）：用户必须回答才能继续
 * 2. 非必填字段（required: false）：用户可以选择"跳过"
 * 3. 素质测评以选择题+问答题的形式呈现
 * 4. 每个场景包含相关联的问题组
 */
export const completeVoiceQuestions: VoiceQuestionConfig[] = [
  // ==================== 场景1：基础信息（必填）====================
  {
    field: 'education',
    scene: 'campus',
    required: true,
    group: '基本信息',
    question:
      '你好呀！我是职业规划小精灵 Pixie 🧚‍♀️ 请先介绍一下你的基本情况吧，比如你现在的学历、什么专业、大几了？',
    sampleAnswer:
      '我是本科学历，学的是软件工程专业，目前大四在读，预计明年6月份毕业',
    skipHint: '学历信息为必填项',
  },

  {
    field: 'language',
    scene: 'campus',
    required: true,
    group: '基本信息',
    question:
      '好的，那你的外语能力怎么样呢？比如过了四六级吗？或者有托福雅思成绩？',
    sampleAnswer: '我通过了英语六级，雅思考了6.5分，日常看英文文档没什么问题',
    skipHint: '语言能力为必填项',
  },

  // ==================== 场景2：技能工具 =====================

  {
    field: 'skills',
    scene: 'skill',
    required: true,
    group: '技能工具',
    question:
      '很好！接下来聊聊你最擅长的技术栈吧，你比较熟悉哪些前端或后端技术？',
    sampleAnswer: '我主要熟悉Vue3和TypeScript，熟练度大概85分左右，也会用React，大概70分，后端了解一点Node.js和Python',
    skipHint: '技能信息为必填项',
  },

  {
    field: 'tools',
    scene: 'skill',
    required: true,
    group: '技能工具',
    question:
      '那你平时常用哪些开发工具呢？比如代码编辑器、版本管理、接口测试这些？',
    sampleAnswer: '我平时用VSCode写代码，Git做版本管理，Apifox测试接口，偶尔用Figma看看设计稿，也会用Docker配一下环境',
    skipHint: '工具信息为必填项',
  },

  {
    field: 'certificates',
    scene: 'skill',
    required: false,
    group: '技能工具',
    question:
      '有获得什么专业证书吗？比如软考、云计算认证、或者其他技术证书？没有的话可以说"跳过"。',
    sampleAnswer: '我有软件设计师中级证书，还有阿里云的ACA云计算认证',
    skipHint: '已跳过证书填写',
  },

  // ==================== 场景3：经历项目 =====================

  {
    field: 'experience',
    scene: 'experience',
    required: true,
    group: '经历项目',
    question:
      '说一段你觉得最能代表自己能力的项目经历吧！可以是课程设计、竞赛项目或者实习时参与的，你负责了什么？做出了什么成果？',
    sampleAnswer: '我做过一个企业级后台管理系统，用的是Vue3加Element Plus，我主要负责首页搭建、权限路由设计和公共组件封装，还优化了列表页的加载速度，首屏加载时间从3秒优化到了1.2秒',
    skipHint: '项目经历为必填项',
  },

  {
    field: 'codeAbility',
    scene: 'experience',
    required: false,
    group: '经历项目',
    question:
      '有 GitHub 或 Gitee 代码仓库链接吗？可分享用于分析代码能力（没有可跳过）。',
    sampleAnswer: '我的GitHub是github.com/zhangsan-vue，上面有几个Vue的项目',
    skipHint: '已跳过代码仓库填写',
  },

  {
    field: 'innovation',
    scene: 'experience',
    required: false,
    group: '经历项目',
    question:
      '有创新性经历或案例吗？如解决技术难题、提出优化方案、参加创新创业大赛（没有可跳过）。',
    sampleAnswer: '我曾经提出过一个组件库的按需加载方案，通过Tree Shaking把打包体积减少了30%，后来被团队采纳了',
    skipHint: '已跳过创新案例填写',
  },

  // ==================== 场景4：素质测评（问答形式）====================
  // 注意：素质测评以简化的问答形式呈现，每类测评包含1道选择题 + 1道问答题

  {
    field: 'communication_q1',
    scene: 'assessment',
    required: false,
    group: '沟通能力',
    question:
      '【沟通能力测评·选择题】当你与团队成员意见不一致时，你通常会怎么做？\n\nA. 坚持己见，试图说服对方\nB. 避免冲突，选择沉默\nC. 倾听对方观点，寻找共同点\nD. 请第三方仲裁',
    sampleAnswer: 'C',
    skipHint: '已跳过沟通能力选择题',
  },

  {
    field: 'communication_open',
    scene: 'assessment',
    required: false,
    group: '沟通能力',
    question:
      '【沟通能力测评·问答题】描述一次你解决团队冲突或沟通问题的经历：情况、措施、结果。',
    sampleAnswer:
      '做小组项目的时候，两位同学对技术选型有分歧，我组织了一次讨论会，让他们分别展示方案的优缺点，最后综合选择了Vue3加Vite的方案，项目顺利完成。',
    skipHint: '已跳过沟通能力问答题',
  },

  {
    field: 'stress_q1',
    scene: 'assessment',
    required: false,
    group: '抗压能力',
    question:
      '【抗压能力测评·选择题】当你面临多个紧急截止日期时，你通常会怎么做？\n\nA. 感到不知所措，无法开始\nB. 随机选择任务开始做\nC. 评估优先级，制定计划，逐一完成\nD. 加班到深夜试图同时处理所有任务',
    sampleAnswer: 'C',
    skipHint: '已跳过抗压能力选择题',
  },

  {
    field: 'stress_open',
    scene: 'assessment',
    required: false,
    group: '抗压能力',
    question:
      '【抗压能力测评·问答题】描述一次在压力下完成重要任务的经历：情况、应对方式、收获。',
    sampleAnswer:
      '期末周的时候要同时完成课程设计和准备考试，我把任务按照优先级排好序，每天固定时间学习，周末集中做项目，虽然很累但是两样都完成了不错。',
    skipHint: '已跳过抗压能力问答题',
  },

  {
    field: 'learning_q1',
    scene: 'assessment',
    required: false,
    group: '学习能力',
    question:
      '【学习能力测评·选择题】当你需要学习一项全新的技术时，你通常会怎么做？\n\nA. 等待培训或别人教\nB. 找同事请教基础知识\nC. 制定学习计划，结合文档、课程和实践系统学习\nD. 直接开始尝试边做边学',
    sampleAnswer: 'C',
    skipHint: '已跳过学习能力选择题',
  },

  {
    field: 'learning_open',
    scene: 'assessment',
    required: false,
    group: '学习能力',
    question:
      '【学习能力测评·问答题】描述一次快速掌握新技能的经历：学习方法、时间周期、心得体会。',
    sampleAnswer:
      '大三的时候需要学React来做项目，我用了一周时间看官方文档，跟着做了个Todo App，然后对比Vue总结了一下异同，两周后就能独立开发了。我发现动手实践真的是最快的学习方式。',
    skipHint: '已跳过学习能力问答题',
  },

  // ==================== 场景5：职业意向（必填）====================

  {
    field: 'targetJob',
    scene: 'career',
    required: true,
    group: '职业意向',
    question:
      '太棒了！最后一个部分——你希望投递什么目标岗位呢？比如前端工程师、后端开发、产品经理等等。',
    sampleAnswer: '我想投递前端开发工程师，最好是Vue技术栈相关的方向',
    skipHint: '目标岗位为必填项',
  },

  {
    field: 'targetIndustry',
    scene: 'career',
    required: true,
    group: '职业意向',
    question:
      '好的！那你对行业方向有什么偏好吗？比如互联网、金融科技、企业服务、教育、电商这些？',
    sampleAnswer:
      '我比较偏向互联网和企业服务领域，尤其是做SaaS产品的公司，对金融科技也感兴趣',
    skipHint: '行业偏好为必填项',
  },
]

// ==================== 必填字段列表 ====================

/** 必填字段名集合 */
export const REQUIRED_VOICE_FIELDS = new Set(
  completeVoiceQuestions.filter(q => q.required).map(q => q.field),
)

// ==================== 默认完整答案 ====================

/**
 * 默认的完整语音答案
 * 用于快速填充
 */
export const defaultCompleteVoiceAnswers: CompleteVoiceAnswers = {
  // 必填字段
  education: '本科，软件工程专业，大四在读，预计2026年6月毕业',
  major: '软件工程',
  graduationDate: '2026-06',
  language: '英语六级，雅思6.5分',
  skills: 'Vue3、TypeScript、React、JavaScript、Node.js、HTML/CSS',
  tools: 'VSCode、Git、Apifox、Figma、Docker、Chrome DevTools',
  experience:
    '企业级后台管理系统：使用Vue3 + Element Plus开发，负责首页搭建、权限路由设计和公共组件封装。优化列表页加载速度，从3秒优化到1.2秒。',
  targetJob: '前端开发工程师',
  targetIndustry: '互联网、企业服务、金融科技',

  // 非必填字段
  certificates: '软件设计师（中级）、阿里云ACA云计算认证',
  codeAbility: 'github.com/zhangsan-vue',
  innovation:
    '提出组件库按需加载方案，通过Tree Shaking将打包体积减少30%，被团队采纳。',

  // 素质测评
  communication_q1: 'C',
  communication_open:
    '小组项目中对技术选型有分歧时，组织讨论会展示方案优缺点，最终综合选择Vue3+Vite方案，项目顺利完成。',
  stress_q1: 'C',
  stress_open:
    '期末周同时面对课程设计和考试，按优先级排序任务、固定时间学习、周末集中做项目，学会了时间管理的重要性。',
  learning_q1: 'C',
  learning_open:
    '学习React：查看官方文档→完成Todo App→对比Vue总结异同→独立开发实际项目。发现动手实践是最快的学习方式。',
}

// ==================== 辅助函数 ====================

/**
 * 根据答案生成素质测评答题记录
 * @param answers 语音答案
 * @returns 素质测评答题记录数组
 */
export function buildQuizDetailFromVoiceAnswers(
  answers: Partial<CompleteVoiceAnswers>,
): QuizDetailItem[] {
  const quizDetail: QuizDetailItem[] = []

  // 沟通能力
  if (answers.communication_q1 || answers.communication_open) {
    if (answers.communication_q1) {
      quizDetail.push({
        type: 'choice',
        question:
          '当你与团队成员意见不一致时，你通常会怎么做？（A.坚持己见 B.避免冲突 C.倾听寻找共同点 D.第三方仲裁）',
        answer: answers.communication_q1,
      })
    }
    if (answers.communication_open) {
      quizDetail.push({
        type: 'open_ended',
        question: '描述一次你成功解决团队冲突或沟通问题的经历',
        answer: answers.communication_open,
      })
    }
  }

  // 抗压能力
  if (answers.stress_q1 || answers.stress_open) {
    if (answers.stress_q1) {
      quizDetail.push({
        type: 'choice',
        question:
          '当你面临多个紧急截止日期时，你会怎么做？（A.不知所措 B.随机选择 C.评估优先级 D.全部加班处理）',
        answer: answers.stress_q1,
      })
    }
    if (answers.stress_open) {
      quizDetail.push({
        type: 'open_ended',
        question: '描述一次你在压力下完成重要任务的经历',
        answer: answers.stress_open,
      })
    }
  }

  // 学习能力
  if (answers.learning_q1 || answers.learning_open) {
    if (answers.learning_q1) {
      quizDetail.push({
        type: 'choice',
        question:
          '当你需要学习全新技术时，你会怎么做？（A.等人教 B.找同事问 C.制定计划系统学习 D.边做边学）',
        answer: answers.learning_q1,
      })
    }
    if (answers.learning_open) {
      quizDetail.push({
        type: 'open_ended',
        question: '分享一次你快速学会新技能或技术的经历',
        answer: answers.learning_open,
      })
    }
  }

  return quizDetail
}

/**
 * 获取场景对应的问题索引范围
 * @param scene 场景key
 * @returns 该场景的问题索引数组
 */
export function getSceneQuestionIndices(scene: VoiceSceneKey): number[] {
  return completeVoiceQuestions
    .map((q, index) => ({ q, index }))
    .filter(({ q }) => q.scene === scene)
    .map(({ index }) => index)
}

/**
 * 获取某个场景的必填未答字段
 * @param answers 当前已收集的答案
 * @param currentScene 当前场景
 * @returns 未回答的必填字段名数组
 */
export function getRequiredUnansweredFields(
  answers: Partial<CompleteVoiceAnswers>,
  currentScene: VoiceSceneKey,
): string[] {
  return completeVoiceQuestions
    .filter(q => q.scene === currentScene && q.required && !answers[q.field as keyof CompleteVoiceAnswers])
    .map(q => q.field)
}

/**
 * 计算当前场景的完成百分比
 * @param answers 当前已收集的答案
 * @param currentScene 当前场景
 * @returns 完成百分比 0-100
 */
export function calculateSceneProgress(
  answers: Partial<CompleteVoiceAnswers>,
  currentScene: VoiceSceneKey,
): number {
  const sceneQuestions = completeVoiceQuestions.filter(q => q.scene === currentScene)
  if (sceneQuestions.length === 0) return 100

  const answeredCount = sceneQuestions.filter(
    q => !!answers[q.field as keyof CompleteVoiceAnswers],
  ).length

  return Math.round((answeredCount / sceneQuestions.length) * 100)
}

/**
 * 计算总体完成百分比
 * @param answers 当前已收集的答案
 * @returns 完成百分比 0-100
 */
export function calculateOverallProgress(
  answers: Partial<CompleteVoiceAnswers>,
): number {
  const requiredQuestions = completeVoiceQuestions.filter(q => q.required)
  if (requiredQuestions.length === 0) return 100

  const answeredRequired = requiredQuestions.filter(
    q => !!answers[q.field as keyof CompleteVoiceAnswers],
  ).length

  return Math.round((answeredRequired / requiredQuestions.length) * 100)
}

/**
 * 检查所有必填字段是否都已填写
 * @param answers 当前已收集的答案
 * @returns 是否所有必填字段都已填写
 */
export function areAllRequiredFieldsFilled(
  answers: Partial<CompleteVoiceAnswers>,
): boolean {
  for (const q of completeVoiceQuestions) {
    if (q.required && !answers[q.field as keyof CompleteVoiceAnswers]) {
      return false
    }
  }
  return true
}
