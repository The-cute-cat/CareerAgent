import type { CareerFormData, EducationType, Priority } from '@/types/careerform_report'
import type { SkillTool } from '@/types/careerform_question'
import type { JobMatchItem } from '@/types/job-match'

const defaultPriorities: Priority[] = [
  { value: 'tech', label: '技术成长' },
  { value: 'salary', label: '薪资' },
  { value: 'stable', label: '稳定' },
]

export type VoiceCollectedAnswers = Record<string, string>

// ==================== 口语化 → 专业格式 转换工具 ====================

/** 去除常见口语化前缀词 */
const removeConversationalPrefixes = (text: string): string =>
  text
    .replace(/^(我(主要|比较|平时|通常|一般)|我)(熟悉|常用|用|会|了解)/g, '')
    .replace(/^(我|我的|我有|我是)/g, '')
    .replace(/^(做过?|在|有|能|可以|想)/g, '')
    .replace(/^(这个|那个|这些|这种|该|其)/g, '')
    .replace(/^(比如|例如|像是|好像|大概|左右|可能|也许)/g, '')
    .replace(/^(其实|当然|确实|真的|非常|特别|超级|挺|蛮|很|较)/g, '')
    .replace(/^(然后|后来|之后|最后|之前|首先|其次|再次)/g, '')
    .trim()

/** 提取技能/工具名称（去除描述性文字） */
const extractTechnicalTerms = (text: string): string[] => {
  // 先去除口语化前缀
  let cleaned = removeConversationalPrefixes(text)
  
  // 常见技术栈关键词映射（用于识别）
  const techKeywords = [
    'Vue', 'React', 'Angular', 'TypeScript', 'JavaScript', 'JS',
    'Node.js', 'Python', 'Java', 'C\\+\\+', 'Go', 'Rust', 'Swift', 'Kotlin',
    'Dart', 'PHP', 'Ruby', '.NET', 'C#',
    'HTML', 'CSS', 'SASS', 'SCSS', 'Less', 'Tailwind', 'Bootstrap',
    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
    'VSCode', 'WebStorm', 'IDEA', 'Vim', 'Sublime', 'Atom',
    'Git', 'SVN', 'Mercurial', 'Gitee', 'GitHub', 'GitLab',
    'Docker', 'Kubernetes', 'Jenkins', 'Nginx', 'Linux',
    'Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator',
    'Apifox', 'Postman', 'Swagger', 'JMeter', 'Chrome DevTools',
    'Webpack', 'Vite', 'Rollup', 'Parcel', 'Babel',
    'Element Plus', 'Ant Design', 'Material UI', 'Vant', 'Naive UI',
    'Pinia', 'Vuex', 'Redux', 'MobX',
    'Express', 'Koa', 'Fastify', 'NestJS', 'NextJS', 'NuxtJS',
    'GraphQL', 'RESTful', 'gRPC', 'WebSocket',
    'AWS', 'Azure', '阿里云', '腾讯云', '华为云',
    'Webpack', 'ESLint', 'Prettier', 'Husky', 'Lint-staged',
  ]
  
  // 按分隔符分割
  const parts = cleaned.split(/[，。；、/,\n\t]|以及|还有|和|与|或者|或者|等/)
    .map(s => s.trim())
    .filter(Boolean)
  
  // 提取包含技术关键词的部分
  const results: string[] = []
  for (const part of parts) {
    // 检查是否匹配已知技术关键词
    for (const keyword of techKeywords) {
      if (part.toLowerCase().includes(keyword.toLowerCase())) {
        results.push(part.replace(/[^a-zA-Z0-9+\-#.@_\/]/g, '').trim())
      }
    }
    
    // 如果是短词（2-25字符）且不包含太多描述性词汇，直接保留
    if (
      part.length >= 2 && 
      part.length <= 30 &&
      !/(熟悉|熟练|擅长|掌握|使用|用|会|了解|知道|学习|做过|负责|参与|实现|开发|编写|搭建|设计|测试|优化|配置|部署|管理|维护|修复|解决|处理|完成)/.test(part)
    ) {
      results.push(part)
    }
  }
  
  return uniqueList(results).slice(0, 8)
}

/** 将技能文本转换为标准 SkillTool 格式 */
const normalizeSkillsToTools = (text: string): SkillTool[] => {
  const terms = extractTechnicalTerms(text)
  return terms.slice(0, 6).map(name => ({ name, score: 85 }))
}

/** 将工具文本转换为标准 SkillTool 格式 */
const normalizeToolsToTools = (text: string): SkillTool[] => {
  const terms = extractTechnicalTerms(text)
  return terms.slice(0, 6).map(name => ({ name, score: 80 }))
}

/** 规范化语言能力 */
const normalizeLanguage = (text: string): { type: string; level: string } => {
  const t = text.toLowerCase()
  let type = ''
  let level = ''
  
  if (t.includes('英语') || t.includes('英文')) type = '英语'
  else if (t.includes('日语')) type = '日语'
  else if (t.includes('韩语')) type = '韩语'
  else if (t.includes('法语')) type = '法语'
  else if (t.includes('德语')) type = '德语'
  else type = text.substring(0, 10)
  
  if (t.includes('六级') || t.includes('cet-6') || t.includes('cet6')) level = 'CET-6'
  else if (t.includes('四级') || t.includes('cet-4') || t.includes('cet4')) level = 'CET-4'
  else if (t.includes('托福') || t.includes('toefl')) level = '托福'
  else if (t.includes('雅思') || t.includes('ielts')) level = '雅思'
  else if (t.includes('专四') || t.includes('专八')) level = text.match(/专[四八]/)?.[0] || ''
  else if (t.includes('BEC')) level = 'BEC'
  else {
    // 尝试从文本中提取等级信息
    const scoreMatch = text.match(/(\d+(?:\.\d+)?)分/)
    if (scoreMatch) level = `${scoreMatch[1]}分`
    else level = text.length > 15 ? text.substring(0, 15) : text
  }
  
  return { type, level }
}

/** 规范化证书列表 */
const normalizeCertificates = (text: string): string[] => {
  const items = text.split(/[,，、;和与或\/]/).map(s => s.trim()).filter(Boolean)
  return uniqueList(items).slice(0, 5).map(item => {
    // 去除 "我"、"有" 等前缀
    return item.replace(/^(我有|已获得|持有|考取了?)/, '').replace(/证书$/,'')
  })
}

/** 规范化项目经历 */
const normalizeExperience = (text: string): string => {
  let normalized = text
  
  // 替换常见口语化表达为专业术语
  const replacements: [regex, string][] = [
    [/做了/g, '完成'],
    [/负责/g, '主导'],
    [/参与了?/g, '参与'],
    [/搭建了?/g, '搭建'],
    [/封装了?/g, '封装'],
    [/优化了?/g, '优化'],
    [/提升了?/g, '提升'],
    [/改善了?/g, '改善'],
    [/实现了?/g, '实现'],
    [/开发了?/g, '开发'],
    [/设计了?/g, '设计'],
    [/写了个?/g, '开发'],
    [/做了一个?/g, '开发'],
    [/用了?/g, '采用'],
    [/主要是/g, '核心工作包括'],
    [/还/g, '，并'],
    [/大概/g, '约'],
    [/左右/g, ''],
    [/挺好的/g, '效果显著'],
    [/不错/g, '良好'],
    [/很好/g, '优秀'],
    [/没什么问题/g, '无障碍'],
    [/还可以/g, '合格'],
  ]
  
  for (const [pattern, replacement] of replacements) {
    normalized = normalized.replace(pattern, replacement)
  }
  
  return normalized
}

/** 规范化目标岗位 */
const normalizeTargetJob = (text: string): string => {
  let job = text.trim()
  
  // 去除前缀
  job = job.replace(/^(我想|我要|希望|打算|准备|计划|想要)/g, '')
           .replace(/^(投递|应聘|申请|找|做|当|成为)/g, '')
           .replace(/^(一个|一名|一位|作为)/g, '')
  
  // 标准化岗位名称
  const jobMapping: Record<string, string> = {
    '前端': '前端工程师',
    '前端开发': '前端开发工程师',
    '后端': '后端工程师',
    '后端开发': 'Java后端工程师',
    '全栈': '全栈工程师',
    '产品': '产品经理',
    '产品经理': '产品经理',
    '运营': '运营专员',
    'UI': 'UI设计师',
    'UI设计师': 'UI设计师',
    'UE': '交互设计师',
    '测试': '测试工程师',
    'QA': '测试工程师',
    '数据': '数据分析师',
    '算法': '算法工程师',
    '运维': '运维工程师',
    'DBA': '数据库管理员',
  }
  
  // 检查是否有匹配的标准名称
  for (const [key, value] of Object.entries(jobMapping)) {
    if (job.toLowerCase().includes(key.toLowerCase())) {
      job = value
      break
    }
  }
  
  // 清理括号内容
  job = job.replace(/\([^)]*?\)/g, '').trim()
  
  return job || text
}

/** 规范化行业方向 */
const normalizeIndustries = (text: string): string[] => {
  const knownIndustries = [
    '互联网', '企业服务', 'SaaS', '金融科技', '教育', '医疗健康',
    '游戏', '电商', '新零售', '智能制造', '汽车', '房地产',
    '政务', '咨询', '广告营销', '媒体娱乐', '社交网络',
    '人工智能', '大数据', '云计算', '区块链', '物联网',
    '安全', '芯片半导体', '新能源', '生物科技',
  ]
  
  const matched: string[] = []
  
  for (const industry of knownIndustries) {
    if (text.includes(industry) && !matched.includes(industry)) {
      matched.push(industry)
    }
  }
  
  // 如果没匹配到任何已知行业，尝试按标点分割
  if (matched.length === 0) {
    return uniqueList(text.split(/[，。；、/,\n]/)).slice(0, 3)
  }
  
  return matched.slice(0, 4)
}

// ==================== 原有工具函数 ====================

const uniqueList = (items: string[]) => [...new Set(items.map(item => item.trim()).filter(Boolean))]

const splitByPunctuation = (text: string) =>
  text
    .split(/[，。；、/,\n]|以及|还有|和|与/)
    .map(item => item.trim())
    .filter(Boolean)

const normalizeEducation = (text: string): EducationType | '' => {
  if (text.includes('博士')) return '博士'
  if (text.includes('硕士') || text.includes('研究生')) return '硕士'
  if (text.includes('本科')) return '本科'
  if (text.includes('专科') || text.includes('大专')) return '专科'
  if (text.includes('高中')) return '高中'
  return ''
}

const extractMajor = (text: string): string[] => {
  const match = text.match(/([\u4e00-\u9fa5A-Za-z]{2,20}(?:工程|专业|科学|技术|设计|管理|金融|医学|法学|文学))/)
  if (!match?.[1]) return []
  return [match[1].replace(/专业$/, '')]
}

const extractGraduationDate = (text: string): string => {
  const explicit = text.match(/(20\d{2})[年\-/. ]?(0?[1-9]|1[0-2])?/)
  if (explicit?.[1]) {
    const month = explicit[2] ? explicit[2].padStart(2, '0') : '06'
    return `${explicit[1]}-${month}`
  }

  const year = new Date().getFullYear()
  if (text.includes('大一')) return `${year + 3}-06`
  if (text.includes('大二')) return `${year + 2}-06`
  if (text.includes('大三')) return `${year + 1}-06`
  if (text.includes('大四') || text.includes('应届')) return `${year}-06`
  if (text.includes('研一')) return `${year + 2}-06`
  if (text.includes('研二')) return `${year + 1}-06`
  if (text.includes('研三')) return `${year}-06`
  return ''
}

const toSkillTools = (text: string, fallbackScore: number): SkillTool[] =>
  uniqueList(splitByPunctuation(text))
    .slice(0, 6)
    .map(name => ({ name, score: fallbackScore }))

const extractTargetIndustries = (text: string): string[] => {
  const knownIndustries = [
    '互联网',
    '企业服务',
    '教育',
    '金融',
    '医疗',
    '游戏',
    '电商',
    '人工智能',
    '制造业',
    '政务',
    'SaaS',
  ]

  const matched = knownIndustries.filter(item => text.includes(item))
  if (matched.length) return matched

  return uniqueList(splitByPunctuation(text)).slice(0, 3)
}

const buildInnovationSummary = (answers: VoiceCollectedAnswers): string => {
  const experience = answers.experience?.trim()
  const expectation = answers.expectation?.trim()
  if (experience && expectation) {
    return `语音补充经历：${experience}\n期望重点：${expectation}`
  }
  return experience || expectation || ''
}

export const createEmptyCareerFormData = (): CareerFormData => ({
  education: '',
  educationOther: '',
  major: [],
  graduationDate: '',
  languages: [{ type: '', level: '', other: '' }],
  certificates: [],
  certificateOther: '',
  skills: [],
  tools: [],
  codeAbility: { links: '' },
  projects: [],
  internships: [],
  quizDetail: [],
  innovation: '',
  targetJob: '',
  targetIndustries: [],
  priorities: defaultPriorities.map(item => ({ ...item })),
})

export const mergeVoiceAnswersToForm = (
  answers: VoiceCollectedAnswers,
  baseFormData?: CareerFormData | null,
): CareerFormData => {
  const nextFormData: CareerFormData = {
    ...(baseFormData ? structuredClone(baseFormData) : createEmptyCareerFormData()),
    priorities: baseFormData?.priorities?.length
      ? baseFormData.priorities.map(item => ({ ...item }))
      : defaultPriorities.map(item => ({ ...item })),
    languages: baseFormData?.languages?.length
      ? baseFormData.languages.map(item => ({ ...item }))
      : [{ type: '', level: '', other: '' }],
    skills: baseFormData?.skills?.map(item => ({ ...item })) || [],
    tools: baseFormData?.tools?.map(item => ({ ...item })) || [],
    projects: baseFormData?.projects?.map(item => ({ ...item })) || [],
    internships: baseFormData?.internships?.map(item => ({
      ...item,
      date: Array.isArray(item.date) ? [...item.date] : [],
    })) || [],
    quizDetail: baseFormData?.quizDetail?.map(item => ({ ...item })) || [],
  }

  // ===== 基础信息 =====
  // 支持新格式 (education 字段) 和旧格式兼容
  const educationAnswer = (answers.education || '').trim()
  
  const normalizedEducation = normalizeEducation(educationAnswer)
  if (normalizedEducation) {
    nextFormData.education = normalizedEducation
  } else if (educationAnswer) {
    nextFormData.education = '其他'
    nextFormData.educationOther = educationAnswer
  }

  const major = extractMajor(educationAnswer)
  if (major.length) nextFormData.major = major

  const graduationDate = extractGraduationDate(educationAnswer)
  if (graduationDate) nextFormData.graduationDate = graduationDate

  // 语言能力（使用新的规范化函数）
  const languageAnswer = (answers.language || '').trim()
  if (languageAnswer) {
    const normalizedLang = normalizeLanguage(languageAnswer)
    nextFormData.languages = [{ 
      type: normalizedLang.type, 
      level: normalizedLang.level, 
      other: languageAnswer 
    }]
  }

  // ===== 技能工具（使用新的规范化函数）=====
  const skillsAnswer = (answers.skills || '').trim()
  const skillList = normalizeSkillsToTools(skillsAnswer)
  if (skillList.length) nextFormData.skills = skillList

  const toolsAnswer = (answers.tools || '').trim()
  const toolList = normalizeToolsToTools(toolsAnswer)
  if (toolList.length) nextFormData.tools = toolList

  // 证书（使用新的规范化函数）
  const certificatesAnswer = (answers.certificates || '').trim()
  if (certificatesAnswer && !certificatesAnswer.includes('跳过')) {
    nextFormData.certificates = normalizeCertificates(certificatesAnswer)
  }

  // ===== 经历项目（使用规范化函数处理描述）=====
  const experienceAnswer = (answers.experience || '').trim()
  if (experienceAnswer) {
    const normalizedDesc = normalizeExperience(experienceAnswer)
    nextFormData.projects = [
      {
        isCompetition: false,
        name: nextFormData.targetJob || '语音补充项目',
        desc: normalizedDesc,
      },
      ...(nextFormData.projects.length > 1 ? nextFormData.projects.slice(1) : []),
    ]
  }

  // 代码能力（新增可选字段）
  const codeAbilityAnswer = (answers.codeAbility || '').trim()
  if (codeAbilityAnswer && !codeAbilityAnswer.includes('跳过')) {
    nextFormData.codeAbility = { links: codeAbilityAnswer }
  }

  // 创新案例（新增可选字段）
  const innovationAnswer = (answers.innovation || '').trim()
  if (innovationAnswer && !innovationAnswer.includes('跳过')) {
    nextFormData.innovation = `语音采集创新案例：${innovationAnswer}`
  } else {
    // 兼容旧的 expectation 字段
    const legacyExpectation = (answers.expectation || '').trim()
    if (legacyExpectation) {
      nextFormData.innovation = `语音期望重点：${legacyExpectation}`
    }
  }

  // ===== 职业意向（使用新的规范化函数）=====
  // 支持新格式 (targetJob/targetIndustry) 和旧格式 (target) 兼容
  const targetJobAnswer = (answers.targetJob || answers.target || '').trim()
  
  const normalizedTargetJob = normalizeTargetJob(targetJobAnswer)
  if (normalizedTargetJob) nextFormData.targetJob = normalizedTargetJob

  // 支持新格式的目标行业字段（使用新的规范化函数）
  const targetIndustryAnswer = (answers.targetIndustry || targetJobAnswer || '').trim()
  const targetIndustries = normalizeIndustries(targetIndustryAnswer)
  if (targetIndustries.length) nextFormData.targetIndustries = targetIndustries

  // ===== 素质测评数据（问答形式）=====
  // 收集所有素质测评答案到 quizDetail
  const quizItems: typeof nextFormData.quizDetail = []
  
  // 沟通能力
  if (answers.communication_q1) {
    quizItems.push({
      type: 'choice' as const,
      question: '当你与团队成员意见不一致时，你通常会怎么做？',
      answer: answers.communication_q1,
    })
  }
  if (answers.communication_open) {
    quizItems.push({
      type: 'open_ended' as const,
      question: '描述一次你成功解决团队冲突或沟通问题的经历',
      answer: answers.communication_open,
    })
  }

  // 抗压能力
  if (answers.stress_q1) {
    quizItems.push({
      type: 'choice' as const,
      question: '当你面临多个紧急截止日期时，你会怎么做？',
      answer: answers.stress_q1,
    })
  }
  if (answers.stress_open) {
    quizItems.push({
      type: 'open_ended' as const,
      question: '描述一次你在压力下完成重要任务的经历',
      answer: answers.stress_open,
    })
  }

  // 学习能力
  if (answers.learning_q1) {
    quizItems.push({
      type: 'choice' as const,
      question: '当你需要学习全新技术时，你会怎么做？',
      answer: answers.learning_q1,
    })
  }
  if (answers.learning_open) {
    quizItems.push({
      type: 'open_ended' as const,
      question: '分享一次你快速学会新技能或技术的经历',
      answer: answers.learning_open,
    })
  }

  // 合并素质测评数据（保留原有的非语音测评数据）
  if (quizItems.length > 0) {
    nextFormData.quizDetail = [
      ...nextFormData.quizDetail.filter(item => !item.question.startsWith('沟通') && 
                                                   !item.question.startsWith('抗压') && 
                                                   !item.question.startsWith('学习')),
      ...quizItems,
    ]
  }

  return nextFormData
}

export const buildDemoJobMatchResult = async (formData: CareerFormData, isLearningMode = false): Promise<JobMatchItem[]> => {
  const { mockJobMatchItems } = await import('@/mock/mockdata/JobMatch_mockdata')
  const { mockLearningJobMatchItems } = await import('@/mock/mockdata/LearningMode_mockdata')
  const targetJob = formData.targetJob?.trim()
  const sourceItems = isLearningMode ? mockLearningJobMatchItems : mockJobMatchItems
  const clonedItems = sourceItems.map(item => structuredClone(item))

  if (!targetJob) return clonedItems

  clonedItems.sort((a, b) => {
    const scoreA = Number(a.raw_data.job_name.includes(targetJob) || targetJob.includes(a.raw_data.job_name))
    const scoreB = Number(b.raw_data.job_name.includes(targetJob) || targetJob.includes(b.raw_data.job_name))
    return scoreB - scoreA
  })

  const firstItem = clonedItems[0]
  if (firstItem) {
    firstItem.raw_data.job_name = targetJob
    firstItem.score = Math.max(firstItem.score || 0, 0.91)
    firstItem.deep_analysis.can_apply = true
    firstItem.deep_analysis.actionable_advice = `已根据语音采集结果为你生成 ${targetJob} 的人岗匹配建议。`
    firstItem.deep_analysis.all_analysis = `系统已结合语音补充的教育背景、技能、工具、项目经历和求职意向，生成 ${targetJob} 的匹配分析结果。`
  }

  return clonedItems
}
