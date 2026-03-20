/**
 * 简历上传接口模拟数据
 * 用于测试简历上传、解析、补写缺失数据、提交表单的完整流程
 */

import type {
  UploadResponse,
  CareerReport,
  CareerFormSubmitResult,
  CareerReportStatus,
  JobMatchResult,
  Result
} from '@/types/type'
import { mockJobMatchResult } from './JobMatch_mockdata'
import type { AxiosResponse } from 'axios'

/**
 * 将 Result 包装为 AxiosResponse 格式，与真实 API 保持一致
 */
function wrapAsAxiosResponse<T>(result: Result<T>): AxiosResponse<Result<T>> {
  return {
    data: result,
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as any
  }
}

// ==================== 1. 简历上传接口模拟数据 ====================

/**
 * 模拟场景1：简历解析成功，返回完整表单数据
 * 用于测试正常流程 - 直接返回表单数据格式
 */
export const mockResumeUploadSuccess: Result<UploadResponse> = {
  code: 200,
  msg: '简历解析成功',
  data: {
    education: '本科',
    educationOther: '',
    major: ['计算机类', '软件工程'],
    graduationDate: '2025-06',
    languages: [
      { type: '英语', level: 'CET-6', other: '' }
    ],
    certificates: ['CET-6', '软件设计师'],
    certificateOther: '',
    skills: [
      { name: 'Java', credibility: 85 },
      { name: 'Spring Boot', credibility: 80 },
      { name: 'MySQL', credibility: 75 },
      { name: 'Redis', credibility: 70 },
      { name: 'Vue.js', credibility: 65 },
      { name: 'Docker', credibility: 60 }
    ],
    tools: [
      { name: 'Git', proficiency: '熟练' },
      { name: 'IntelliJ IDEA', proficiency: '精通' },
      { name: 'VS Code', proficiency: '熟练' }
    ],
    codeAbility: { links: 'https://github.com/zhangsan' },
    projects: [
      {
        isCompetition: false,
        name: '电商平台后端系统',
        desc: '负责订单模块的设计与开发，使用Spring Boot + MySQL + Redis技术栈，支持高并发场景'
      },
      {
        isCompetition: true,
        name: '校园二手交易平台',
        desc: '获得校级创新创业大赛二等奖，负责整体架构设计和核心功能开发'
      }
    ],
    internships: [
      {
        company: 'ABC科技有限公司',
        role: 'Java开发工程师',
        date: [],
        desc: '参与公司核心业务系统开发，负责订单管理模块的设计与实现'
      }
    ],
    scores: {
      communication: true,
      stress: false,
      learning: true
    },
    innovation: '通过引入Redis缓存和数据库索引优化，将系统查询性能提升30%',
    targetJob: '', // 故意留空，测试必填检测
    targetIndustries: [], // 故意留空，测试必填检测
    priorities: [
      { value: 'tech', label: '技术成长' },
      { value: 'salary', label: '薪资' },
      { value: 'stable', label: '稳定' }
    ]
  }
}

/**
 * 模拟场景2：简历解析成功，但部分字段缺失
 * 用于测试缺失字段提醒功能 - 直接返回表单数据格式
 */
export const mockResumeUploadPartial: Result<UploadResponse> = {
  code: 200,
  msg: '简历上传成功，部分字段解析失败',
  data: {
    education: '本科',
    major: [], // 缺失
    graduationDate: '', // 缺失
    languages: [], // 缺失
    certificates: [],
    certificateOther: '',
    skills: [
      { name: 'Python', credibility: 75 },
      { name: '数据分析', credibility: 70 }
    ],
    tools: [],
    codeAbility: { links: '' },
    projects: [],
    internships: [],
    scores: {
      communication: false,
      stress: false,
      learning: false
    },
    innovation: '', // 缺失
    targetJob: '', // 缺失
    targetIndustries: [], // 缺失
    priorities: [
      { value: 'tech', label: '技术成长' },
      { value: 'salary', label: '薪资' },
      { value: 'stable', label: '稳定' }
    ]
  }
}

/**
 * 模拟场景3：异步解析模式（解析耗时较长）
 * 用于测试轮询获取结果 - 返回空对象，表示正在处理
 */
export const mockResumeUploadProcessing: Result<UploadResponse> = {
  code: 200,
  msg: '简历上传成功，正在解析中',
  data: {}  // 空对象表示正在处理中
}

/**
 * 模拟场景4：简历解析失败
 * 用于测试错误处理 - 返回空对象
 */
export const mockResumeUploadFailed: Result<UploadResponse> = {
  code: 200,
  msg: '简历上传成功，但解析失败',
  data: {}  // 空对象表示解析失败
}

// ==================== 2. 解析状态查询接口模拟数据 ====================

/**
 * 模拟解析状态 - 处理中
 */
export const mockParseStatusProcessing: Result<CareerReportStatus> = {
  code: 200,
  msg: 'success',
  data: {
    taskId: 'task_resume_processing_001',
    status: 'processing',
    progress: 65,
    estimatedTimeRemaining: 15
  }
}

/**
 * 模拟解析状态 - 已完成
 */
export const mockParseStatusCompleted: Result<CareerReportStatus> = {
  code: 200,
  msg: 'success',
  data: {
    taskId: 'task_resume_abc123',
    status: 'completed',
    progress: 100,
    estimatedTimeRemaining: 0
  }
}

/**
 * 模拟解析状态 - 失败
 */
export const mockParseStatusFailed: Result<CareerReportStatus> = {
  code: 200,
  msg: 'success',
  data: {
    taskId: 'task_resume_failed_001',
    status: 'failed',
    progress: 0,
    estimatedTimeRemaining: 0,
    errorMessage: '简历内容无法识别，请上传清晰的PDF或Word文件'
  }
}

// ==================== 3. 简历解析报告接口模拟数据 ====================

/**
 * 模拟完整的职业规划报告
 */
export const mockResumeReport: Result<CareerReport> = {
  code: 200,
  msg: 'success',
  data: {
    taskId: 'task_resume_abc123',
    abilityScores: {
      专业: 85,
      创新: 78,
      学习: 82,
      抗压: 75,
      沟通: 80,
      实习: 70
    },
    overallAssessment: {
      level: '良好',
      summary: '综合评估显示，您的专业能力为85分，整体具备较强的竞争力。技术基础扎实，项目经验丰富，建议继续保持学习热情。',
      strengths: ['专业', '学习', '沟通'],
      weaknesses: ['抗压']
    },
    dimensionAnalysis: {
      专业: {
        score: 85,
        analysis: '您的专业技能扎实，掌握Java、Spring Boot等主流技术栈，具备独立开发项目的能力。',
        suggestions: ['深入学习微服务架构', '关注云原生技术趋势', '考取高级技术认证']
      },
      创新: {
        score: 78,
        analysis: '您展现出良好的创新思维，能够从项目中提炼创新点，但创新性解决方案的深度还有提升空间。',
        suggestions: ['多参与技术创新项目', '培养全链路思维', '关注行业前沿技术']
      },
      学习: {
        score: 82,
        analysis: '您具备优秀的学习能力，能够快速掌握新技术并应用到实际项目中。',
        suggestions: ['建立系统化学习体系', '参与技术社区交流', '阅读经典技术书籍']
      },
      抗压: {
        score: 75,
        analysis: '您具备基本的抗压能力，但在高强度工作环境下的持续表现还可以加强。',
        suggestions: ['学习时间管理法', '培养运动习惯', '建立压力释放机制']
      },
      沟通: {
        score: 80,
        analysis: '您具备良好的沟通协调能力，能够有效与团队成员协作完成项目。',
        suggestions: ['提升跨部门沟通技巧', '加强书面表达能力', '培养领导力']
      },
      实习: {
        score: 70,
        analysis: '您的实习经历为企业级项目开发经验，对职场环境有较好的适应能力。',
        suggestions: ['争取更多实习机会', '拓展不同行业经验', '积累项目管理经验']
      }
    },
    generatedAt: '2025-03-19T10:30:00Z'
  }
}

// ==================== 4. 表单提交接口模拟数据 ====================

/**
 * 模拟表单提交成功
 */
export const mockFormSubmitSuccess: Result<CareerFormSubmitResult> = {
  code: 200,
  msg: '表单提交成功',
  data: {
    taskId: 'task_career_def456',
    status: 'processing',
    estimatedTime: 15
  }
}

/**
 * 模拟表单提交验证失败
 */
export const mockFormSubmitValidationError: Result<null> = {
  code: 400,
  msg: '表单数据验证失败：目标岗位不能为空',
  data: null
}

// ==================== 5. 职业规划报告状态查询模拟数据 ====================

/**
 * 模拟报告生成状态 - 处理中
 */
export const mockReportStatusProcessing: Result<CareerReportStatus> = {
  code: 200,
  msg: 'success',
  data: {
    taskId: 'task_career_def456',
    status: 'processing',
    progress: 45,
    estimatedTimeRemaining: 10
  }
}

/**
 * 模拟报告生成状态 - 已完成
 */
export const mockReportStatusCompleted: Result<CareerReportStatus> = {
  code: 200,
  msg: 'success',
  data: {
    taskId: 'task_career_def456',
    status: 'completed',
    progress: 100,
    estimatedTimeRemaining: 0
  }
}

// ==================== 6. 职业规划报告获取接口模拟数据 ====================

/**
 * 模拟完整的职业规划报告（表单提交后生成）
 */
export const mockCareerReport: Result<CareerReport> = {
  code: 200,
  msg: 'success',
  data: {
    taskId: 'task_career_def456',
    abilityScores: {
      专业: 88,
      创新: 82,
      学习: 85,
      抗压: 78,
      沟通: 83,
      实习: 75
    },
    overallAssessment: {
      level: '优秀',
      summary: '恭喜！您的综合评估达到优秀水平。六维能力均衡且表现突出，在同龄人中具有较强的竞争优势，建议积极投递心仪岗位。',
      strengths: ['专业', '学习', '沟通', '创新'],
      weaknesses: []
    },
    dimensionAnalysis: {
      专业: {
        score: 88,
        analysis: '您的专业技能非常扎实，技术栈全面且熟练度高，具备解决复杂技术问题的能力。',
        suggestions: ['挑战更高难度的技术问题', '参与开源社区贡献', '考虑技术专家路线发展']
      },
      创新: {
        score: 82,
        analysis: '您具备优秀的创新思维能力，能够从多角度思考问题并提出创新解决方案。',
        suggestions: ['申请创新项目', '培养产品思维', '关注用户体验设计']
      },
      学习: {
        score: 85,
        analysis: '您的学习能力突出，知识吸收和应用转化效率高，具备持续成长的潜力。',
        suggestions: ['拓展技术广度', '深入研究某一领域', '学习技术管理知识']
      },
      抗压: {
        score: 78,
        analysis: '您具备良好的抗压能力，能够在压力下保持稳定的工作状态。',
        suggestions: ['挑战更高强度项目', '培养团队管理经验', '建立个人工作节奏']
      },
      沟通: {
        score: 83,
        analysis: '您的沟通表达能力优秀，能够有效传递信息并协调团队合作。',
        suggestions: ['提升演讲能力', '参与技术分享', '培养跨文化沟通能力']
      },
      实习: {
        score: 75,
        analysis: '您的实习经历丰富，具备较好的职场适应能力和实际项目经验。',
        suggestions: ['积累不同规模公司经验', '拓展行业视野', '建立职业人脉网络']
      }
    },
    generatedAt: '2025-03-19T10:45:00Z'
  }
}

// ==================== 7. 草稿保存/获取接口模拟数据 ====================

/**
 * 模拟保存草稿成功
 */
export const mockSaveDraftSuccess: Result<null> = {
  code: 200,
  msg: '草稿保存成功',
  data: null
}

/**
 * 模拟获取草稿数据
 */
export const mockGetDraftData: Result<Record<string, unknown>> = {
  code: 200,
  msg: 'success',
  data: {
    education: '本科',
    major: '计算机类 / 软件工程',
    graduationDate: '2025-06',
    languages: [
      { type: '英语', level: 'CET-6', other: '' }
    ],
    certificates: ['CET-6'],
    skills: [
      { name: 'Java', credibility: 80 },
      { name: 'Spring Boot', credibility: 75 }
    ],
    tools: [
      { name: 'Git', proficiency: '熟练' }
    ],
    codeLinks: 'https://github.com/example',
    projects: [
      {
        isCompetition: false,
        name: '在线商城系统',
        desc: '基于Spring Boot的电商平台'
      }
    ],
    internships: [],
    quizScores: {
      communication: true,
      stress: false,
      learning: true
    },
    innovation: '',
    targetJob: '后端工程师',
    targetIndustries: ['互联网'],
    priorities: ['tech', 'salary', 'stable']
  }
}

// ==================== 8. 错误响应模拟数据 ====================

/**
 * 模拟401未登录错误
 */
export const mockErrorUnauthorized: Result<null> = {
  code: 401,
  msg: '登录已过期，请重新登录',
  data: null
}

/**
 * 模拟413文件过大错误
 */
export const mockErrorFileTooLarge: Result<null> = {
  code: 413,
  msg: '文件过大，请上传小于5MB的文件',
  data: null
}

/**
 * 模拟500服务器错误
 */
export const mockErrorServerError: Result<null> = {
  code: 500,
  msg: '服务器繁忙，请稍后重试',
  data: null
}

// ==================== 9. 模拟API函数 ====================

/**
 * 模拟延迟
 * @param ms 延迟毫秒数
 */
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 模拟简历上传接口
 * @param fileName 文件名
 * @param scenario 模拟场景：'success' | 'partial' | 'processing' | 'failed'
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockUploadResumeApi(
  fileName: string,
  scenario: 'success' | 'partial' | 'processing' | 'failed' = 'success',
  delayMs: number = 1500
): Promise<AxiosResponse<Result<UploadResponse>>> {
  await delay(delayMs)

  switch (scenario) {
    case 'partial':
      return wrapAsAxiosResponse(mockResumeUploadPartial)
    case 'processing':
      return wrapAsAxiosResponse(mockResumeUploadProcessing)
    case 'failed':
      return wrapAsAxiosResponse(mockResumeUploadFailed)
    case 'success':
    default:
      return wrapAsAxiosResponse(mockResumeUploadSuccess)
  }
}

/**
 * 模拟获取解析状态接口
 * @param taskId 任务ID
 * @param scenario 模拟场景
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockGetParseStatusApi(
  taskId: string,
  scenario: 'processing' | 'completed' | 'failed' = 'completed',
  delayMs: number = 500
): Promise<AxiosResponse<Result<CareerReportStatus>>> {
  await delay(delayMs)

  switch (scenario) {
    case 'processing':
      return wrapAsAxiosResponse(mockParseStatusProcessing)
    case 'failed':
      return wrapAsAxiosResponse(mockParseStatusFailed)
    case 'completed':
    default:
      return wrapAsAxiosResponse(mockParseStatusCompleted)
  }
}

/**
 * 模拟获取简历报告接口
 * @param taskId 任务ID
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockGetResumeReportApi(
  taskId: string,
  delayMs: number = 800
): Promise<AxiosResponse<Result<CareerReport>>> {
  await delay(delayMs)
  return wrapAsAxiosResponse(mockResumeReport)
}

/**
 * 模拟提交表单接口
 * 直接返回人岗匹配结果，无需轮询
 * @param scenario 模拟场景
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockSubmitFormApi(
  scenario: 'success' | 'validation_error' = 'success',
  delayMs: number = 1000
): Promise<AxiosResponse<Result<JobMatchResult>>> {
  await delay(delayMs)

  if (scenario === 'validation_error') {
    return wrapAsAxiosResponse({
      code: 400,
      msg: '表单验证失败，请检查必填字段',
      data: null as unknown as JobMatchResult
    })
  }

  // 返回人岗匹配结果
  return wrapAsAxiosResponse({
    code: 200,
    msg: '提交成功',
    data: mockJobMatchResult
  })
}

/**
 * 模拟获取报告状态接口
 * @param scenario 模拟场景
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockGetReportStatusApi(
  scenario: 'processing' | 'completed' = 'completed',
  delayMs: number = 500
): Promise<AxiosResponse<Result<CareerReportStatus>>> {
  await delay(delayMs)

  if (scenario === 'processing') {
    return wrapAsAxiosResponse(mockReportStatusProcessing)
  }
  return wrapAsAxiosResponse(mockReportStatusCompleted)
}

/**
 * 模拟获取职业规划报告接口
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockGetCareerReportApi(
  delayMs: number = 800
): Promise<AxiosResponse<Result<CareerReport>>> {
  await delay(delayMs)
  return wrapAsAxiosResponse(mockCareerReport)
}

/**
 * 模拟轮询获取完整报告
 * 模拟实际场景中的多次轮询
 * @param onProgress 进度回调
 */
export async function mockPollForReport(
  onProgress?: (progress: number) => void
): Promise<Result<CareerReport>> {
  const stages = [
    { progress: 0, delay: 500 },
    { progress: 25, delay: 1000 },
    { progress: 50, delay: 1000 },
    { progress: 75, delay: 1000 },
    { progress: 100, delay: 500 }
  ]

  for (const stage of stages) {
    await delay(stage.delay)
    onProgress?.(stage.progress)
  }

  return mockCareerReport
}

// ==================== 10. 导出所有模拟数据 ====================

export default {
  // 静态数据
  mockResumeUploadSuccess,
  mockResumeUploadPartial,
  mockResumeUploadProcessing,
  mockResumeUploadFailed,
  mockParseStatusProcessing,
  mockParseStatusCompleted,
  mockParseStatusFailed,
  mockResumeReport,
  mockFormSubmitSuccess,
  mockFormSubmitValidationError,
  mockReportStatusProcessing,
  mockReportStatusCompleted,
  mockCareerReport,
  mockSaveDraftSuccess,
  mockGetDraftData,
  mockErrorUnauthorized,
  mockErrorFileTooLarge,
  mockErrorServerError,

  // 模拟API函数
  mockUploadResumeApi,
  mockGetParseStatusApi,
  mockGetResumeReportApi,
  mockSubmitFormApi,
  mockGetReportStatusApi,
  mockGetCareerReportApi,
  mockPollForReport
}
