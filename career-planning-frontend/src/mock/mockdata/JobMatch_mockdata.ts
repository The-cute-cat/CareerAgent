/**
 * 人岗匹配模块模拟数据
 * 包含岗位列表、匹配分析数据、筛选选项等
 */

import type { JobMatchResult, Result } from '@/types/type'
import type { AxiosResponse } from 'axios'

// ==================== 工具函数 ====================

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

function wrapAsAxiosResponse<T>(result: Result<T>): AxiosResponse<Result<T>> {
  return {
    data: result,
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as any
  }
}

// ==================== 类型定义 ====================

/** 岗位数据 */
export interface JobPosition {
  id: string
  title: string
  company: string
  industry: string
  location: string
  salaryMin: number
  salaryMax: number
  experience: string
  education: string
  tags: string[]
  description: string
  /** AI提取的核心技能 */
  coreSkills: string[]
  /** 证书要求 */
  requiredCertificates: string[]
  /** 素养要求 */
  requiredQualities: string[]
  /** 匹配分数 */
  matchScore?: number
  /** AI置信度 */
  confidence: number
}

/** 匹配维度分数 */
export interface MatchDimension {
  name: string
  score: number
  maxScore: number
  weight: number
  description: string
}

/** 差距分析项 */
export interface GapItem {
  type: 'skill' | 'certificate' | 'quality' | 'experience'
  name: string
  required: string
  current: string
  gap: 'high' | 'medium' | 'low'
  suggestion: string
}

/** 匹配分析结果 */
export interface MatchAnalysis {
  totalScore: number
  dimensions: MatchDimension[]
  gaps: GapItem[]
  aiExplanation: string
  confidence: number
}

/** 筛选选项 */
export interface FilterOptions {
  industryOptions: string[]
  locationOptions: string[]
  salaryOptions: { label: string; value: string }[]
  experienceOptions: string[]
}

// ==================== 模拟数据 ====================

/** 岗位列表数据 */
export const mockJobs: JobPosition[] = [
  {
    id: '1',
    title: 'Java后端开发工程师',
    company: '腾讯科技',
    industry: '互联网',
    location: '深圳',
    salaryMin: 15000,
    salaryMax: 25000,
    experience: '3-5年',
    education: '本科及以上',
    tags: ['Java', 'Spring Boot', '微服务', 'MySQL'],
    description: '负责后端系统设计与开发，参与架构设计',
    coreSkills: ['Java', 'Spring Boot', 'MySQL', 'Redis', 'Kafka'],
    requiredCertificates: ['软件设计师', '阿里云认证'],
    requiredQualities: ['团队协作', '抗压能力', '学习能力强'],
    matchScore: 85,
    confidence: 92
  },
  {
    id: '2',
    title: '前端开发工程师',
    company: '阿里巴巴',
    industry: '互联网',
    location: '杭州',
    salaryMin: 18000,
    salaryMax: 30000,
    experience: '2-4年',
    education: '本科及以上',
    tags: ['Vue', 'React', 'TypeScript', 'Webpack'],
    description: '负责前端界面开发，优化用户体验',
    coreSkills: ['Vue.js', 'React', 'TypeScript', '前端工程化'],
    requiredCertificates: ['前端开发工程师认证'],
    requiredQualities: ['创新能力', '审美能力', '沟通能力'],
    matchScore: 72,
    confidence: 88
  },
  {
    id: '3',
    title: '数据分析师',
    company: '字节跳动',
    industry: '互联网',
    location: '北京',
    salaryMin: 20000,
    salaryMax: 35000,
    experience: '1-3年',
    education: '本科及以上',
    tags: ['SQL', 'Python', '数据挖掘', '机器学习'],
    description: '负责业务数据分析，挖掘数据价值',
    coreSkills: ['SQL', 'Python', '数据可视化', '统计学'],
    requiredCertificates: ['数据分析师认证', 'Python编程认证'],
    requiredQualities: ['逻辑思维', '细心', '业务敏感度'],
    matchScore: 65,
    confidence: 85
  },
  {
    id: '4',
    title: '产品经理',
    company: '美团',
    industry: '互联网',
    location: '北京',
    salaryMin: 20000,
    salaryMax: 40000,
    experience: '3-5年',
    education: '本科及以上',
    tags: ['产品设计', '需求分析', '数据分析', '项目管理'],
    description: '负责产品规划与设计，推动产品落地',
    coreSkills: ['需求分析', '原型设计', '数据分析', '项目管理'],
    requiredCertificates: ['PMP', 'NPDP'],
    requiredQualities: ['沟通能力', '逻辑思维', '用户思维'],
    matchScore: 58,
    confidence: 82
  },
  {
    id: '5',
    title: 'DevOps工程师',
    company: '华为',
    industry: '通信',
    location: '深圳',
    salaryMin: 18000,
    salaryMax: 32000,
    experience: '2-4年',
    education: '本科及以上',
    tags: ['Docker', 'K8s', 'CI/CD', 'Linux'],
    description: '负责DevOps平台建设与运维自动化',
    coreSkills: ['Docker', 'Kubernetes', 'Jenkins', 'Linux'],
    requiredCertificates: ['CKA', 'AWS认证'],
    requiredQualities: ['自动化思维', '问题解决', '持续学习'],
    matchScore: 78,
    confidence: 90
  },
  {
    id: '6',
    title: '算法工程师',
    company: '百度',
    industry: '互联网',
    location: '北京',
    salaryMin: 25000,
    salaryMax: 45000,
    experience: '3-5年',
    education: '硕士及以上',
    tags: ['机器学习', '深度学习', 'Python', 'TensorFlow'],
    description: '负责搜索推荐算法研发与优化',
    coreSkills: ['机器学习', '深度学习', 'Python', '算法设计'],
    requiredCertificates: ['机器学习工程师认证'],
    requiredQualities: ['数学基础扎实', '论文阅读能力', '工程实现'],
    matchScore: 45,
    confidence: 87
  },
  {
    id: '7',
    title: '测试开发工程师',
    company: '京东',
    industry: '电商',
    location: '北京',
    salaryMin: 15000,
    salaryMax: 28000,
    experience: '2-4年',
    education: '本科及以上',
    tags: ['自动化测试', 'Selenium', 'Python', '性能测试'],
    description: '负责测试平台开发和自动化测试框架建设',
    coreSkills: ['自动化测试', 'Python', 'Selenium', '性能测试'],
    requiredCertificates: ['软件测试工程师'],
    requiredQualities: ['细心', '质量意识', '沟通能力'],
    matchScore: 68,
    confidence: 84
  },
  {
    id: '8',
    title: 'Go后端开发工程师',
    company: '小米',
    industry: '互联网',
    location: '北京',
    salaryMin: 20000,
    salaryMax: 35000,
    experience: '3-5年',
    education: '本科及以上',
    tags: ['Go', '微服务', 'Redis', 'gRPC'],
    description: '负责高并发后端服务开发',
    coreSkills: ['Go语言', '微服务架构', 'Redis', 'gRPC'],
    requiredCertificates: ['Go语言认证'],
    requiredQualities: ['高并发思维', '性能优化', '团队协作'],
    matchScore: 62,
    confidence: 86
  }
]

/** 默认匹配分析数据 */
export const mockMatchAnalysis: MatchAnalysis = {
  totalScore: 85,
  confidence: 92,
  aiExplanation: '基于您的技能画像与该岗位需求分析，您在技术基础方面表现优秀，Java相关技能匹配度较高。建议加强分布式系统设计经验。',
  dimensions: [
    { name: '基础匹配', score: 90, maxScore: 100, weight: 25, description: '学历、专业、工作经验' },
    { name: '技能匹配', score: 88, maxScore: 100, weight: 30, description: '技术栈、工具掌握程度' },
    { name: '素养匹配', score: 82, maxScore: 100, weight: 25, description: '软实力、沟通能力、团队协作' },
    { name: '潜力评估', score: 80, maxScore: 100, weight: 20, description: '学习能力、成长空间' }
  ],
  gaps: [
    {
      type: 'skill',
      name: '分布式系统设计',
      required: '熟练掌握微服务架构',
      current: '了解基础概念，缺乏实战经验',
      gap: 'medium',
      suggestion: '建议学习Spring Cloud，参与开源项目或完成相关实战课程'
    },
    {
      type: 'certificate',
      name: '软件设计师证书',
      required: '持有软件设计师中级证书',
      current: '未获得相关证书',
      gap: 'low',
      suggestion: '可报考下半年软考，备考周期约3个月'
    },
    {
      type: 'experience',
      name: '大型项目经验',
      required: '参与过百万级用户项目',
      current: '中小项目开发经验',
      gap: 'high',
      suggestion: '当前项目经验与目标存在差距，建议在工作中主动承担核心模块'
    }
  ]
}

/** 根据岗位ID获取匹配分析数据 */
export const getMatchAnalysisByJobId = (jobId: string): MatchAnalysis => {
  const job = mockJobs.find(j => j.id === jobId)
  const score = job?.matchScore || 75
  
  // 根据匹配分数动态调整维度分数
  const baseDimensions = [
    { name: '基础匹配', maxScore: 100, weight: 25, description: '学历、专业、工作经验' },
    { name: '技能匹配', maxScore: 100, weight: 30, description: '技术栈、工具掌握程度' },
    { name: '素养匹配', maxScore: 100, weight: 25, description: '软实力、沟通能力、团队协作' },
    { name: '潜力评估', maxScore: 100, weight: 20, description: '学习能力、成长空间' }
  ]
  
  const dimensions: MatchDimension[] = baseDimensions.map(dim => ({
    ...dim,
    score: Math.min(100, Math.max(40, score + Math.floor(Math.random() * 20 - 10)))
  }))
  
  // 根据岗位类型生成不同的差距分析
  const gapsMap: Record<string, GapItem[]> = {
    '1': [ // Java后端
      {
        type: 'skill',
        name: '分布式系统设计',
        required: '熟练掌握微服务架构',
        current: '了解基础概念，缺乏实战经验',
        gap: 'medium',
        suggestion: '建议学习Spring Cloud，参与开源项目或完成相关实战课程'
      },
      {
        type: 'certificate',
        name: '软件设计师证书',
        required: '持有软件设计师中级证书',
        current: '未获得相关证书',
        gap: 'low',
        suggestion: '可报考下半年软考，备考周期约3个月'
      }
    ],
    '2': [ // 前端
      {
        type: 'skill',
        name: '前端性能优化',
        required: '深入理解浏览器渲染原理',
        current: '了解基础优化手段',
        gap: 'medium',
        suggestion: '学习Web性能优化最佳实践，掌握Chrome DevTools性能分析'
      },
      {
        type: 'skill',
        name: 'TypeScript',
        required: '熟练使用TypeScript',
        current: '基本使用，类型定义不够规范',
        gap: 'low',
        suggestion: '系统学习TypeScript高级类型，参与类型安全的项目开发'
      }
    ],
    '3': [ // 数据分析
      {
        type: 'skill',
        name: '机器学习算法',
        required: '掌握常用机器学习算法',
        current: '了解基础概念',
        gap: 'high',
        suggestion: '建议学习吴恩达机器学习课程，完成Kaggle入门项目'
      },
      {
        type: 'certificate',
        name: '数据分析师认证',
        required: '持有数据分析师认证',
        current: '未获得认证',
        gap: 'medium',
        suggestion: '报考CDA或相关数据分析认证考试'
      }
    ],
    '6': [ // 算法
      {
        type: 'skill',
        name: '深度学习框架',
        required: '熟练使用PyTorch/TensorFlow',
        current: '仅了解基础',
        gap: 'high',
        suggestion: '建议完成深度学习专项课程，复现经典论文'
      },
      {
        type: 'experience',
        name: '顶会论文',
        required: '有顶会论文发表经历',
        current: '无相关经历',
        gap: 'high',
        suggestion: '尝试参与实验室项目，从论文复现开始积累经验'
      }
    ]
  }
  
  const gaps = gapsMap[jobId] || mockMatchAnalysis.gaps
  
  // 生成AI解释
  const explanations: Record<string, string> = {
    '1': '基于您的技能画像与该岗位需求分析，您在Java技术栈方面表现优秀，Spring Boot使用经验丰富。建议加强分布式系统设计经验。',
    '2': '您的前端基础扎实，Vue.js使用熟练。建议深入学习前端工程化和性能优化相关内容。',
    '3': '您的数据分析基础较好，SQL能力突出。建议加强统计学和机器学习方面的学习。',
    '6': '该岗位要求较高的算法能力，目前您的技能画像与岗位需求存在较大差距，建议制定长期学习计划。'
  }
  
  return {
    totalScore: score,
    confidence: job?.confidence || 85,
    aiExplanation: explanations[jobId] || mockMatchAnalysis.aiExplanation,
    dimensions,
    gaps
  }
}

/**
 * 模拟人岗匹配结果（用于表单提交后返回）
 */
export const mockJobMatchResult: JobMatchResult = {
  taskId: 'task_match_001',
  totalScore: 82,
  dimensions: [
    { name: '技能匹配', score: 85, maxScore: 100, weight: 0.3, description: '专业技能与岗位要求的匹配程度' },
    { name: '经验匹配', score: 78, maxScore: 100, weight: 0.25, description: '工作经验与岗位要求的匹配程度' },
    { name: '学历匹配', score: 90, maxScore: 100, weight: 0.2, description: '学历背景与岗位要求的匹配程度' },
    { name: '证书匹配', score: 75, maxScore: 100, weight: 0.15, description: '专业证书与岗位要求的匹配程度' },
    { name: '素养匹配', score: 80, maxScore: 100, weight: 0.1, description: '职业素养与岗位要求的匹配程度' }
  ],
  gaps: [
    {
      type: 'skill',
      name: '分布式系统',
      required: '熟悉微服务架构、分布式缓存、消息队列',
      current: '了解基础概念，缺乏实际项目经验',
      gap: 'medium',
      suggestion: '建议学习Spring Cloud、Redis集群、Kafka等技术，并尝试在个人项目中实践'
    },
    {
      type: 'certificate',
      name: '软件设计师',
      required: '中级软件设计师证书',
      current: '无相关证书',
      gap: 'low',
      suggestion: '可以考取软件设计师证书提升竞争力，但不是必需项'
    }
  ],
  aiExplanation: '基于您的技能画像分析，您在Java后端开发领域具备扎实的基础，与目标岗位匹配度良好。建议在分布式系统和云原生技术方向加强学习，这将显著提升您的职业竞争力。',
  confidence: 88,
  recommendedJobs: mockJobs.slice(0, 5).map((job, index) => ({
    ...job,
    matchScore: 90 - index * 5
  })),
  generatedAt: new Date().toISOString()
}

/**
 * 模拟获取人岗匹配结果API
 * @param taskId 任务ID
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockGetJobMatchResultApi(
  taskId: string,
  delayMs: number = 800
): Promise<AxiosResponse<Result<JobMatchResult>>> {
  await delay(delayMs)
  return wrapAsAxiosResponse({
    code: 200,
    msg: 'success',
    data: {
      ...mockJobMatchResult,
      taskId
    }
  })
}

/** 筛选选项数据 */
export const filterOptions: FilterOptions = {
  industryOptions: ['互联网', '金融', '通信', '制造业', '教育', '医疗', '电商'],
  locationOptions: ['北京', '上海', '深圳', '杭州', '广州', '成都', '武汉', '西安'],
  salaryOptions: [
    { label: '10K以下', value: '0-10' },
    { label: '10K-20K', value: '10-20' },
    { label: '20K-30K', value: '20-30' },
    { label: '30K-50K', value: '30-50' },
    { label: '50K以上', value: '50-999' }
  ],
  experienceOptions: ['应届生', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']
}

/** 搜索岗位（模拟筛选） */
export const searchJobs = (
  keyword: string,
  filters: {
    industry?: string
    location?: string
    salaryRange?: string
    experience?: string
  }
): JobPosition[] => {
  return mockJobs.filter(job => {
    const matchKeyword = !keyword || 
      job.title.toLowerCase().includes(keyword.toLowerCase()) || 
      job.company.toLowerCase().includes(keyword.toLowerCase()) ||
      job.tags.some(tag => tag.toLowerCase().includes(keyword.toLowerCase()))
    
    const matchIndustry = !filters.industry || job.industry === filters.industry
    const matchLocation = !filters.location || job.location === filters.location
    const matchExperience = !filters.experience || job.experience.includes(filters.experience)
    
    let matchSalary = true
    if (filters.salaryRange) {
      const [minStr, maxStr] = filters.salaryRange.split('-')
      const min = Number(minStr)
      const max = Number(maxStr)
      matchSalary = (job.salaryMin / 1000 >= min && job.salaryMin / 1000 < max) ||
                    (job.salaryMax / 1000 >= min && job.salaryMax / 1000 < max)
    }
    
    return matchKeyword && matchIndustry && matchLocation && matchExperience && matchSalary
  })
}
