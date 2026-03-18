import request from '@/utils/request'
import type {
  CareerFormSubmitDTO,
  CareerFormData,
  CareerFormSubmitResult,
  CareerReport,
  CareerReportStatus,
  Result
} from '@/types/type'


/**
 * 提交职业规划表单数据
 * @param data 表单数据
 * @returns 提交结果，包含任务ID和状态
 */
export function submitCareerFormApi(data: CareerFormSubmitDTO) {
  return request.post<Result<CareerFormSubmitResult>>('/career/form/submit', data)
}

/**
 * 获取职业规划报告状态
 * @param taskId 任务ID
 * @returns 报告生成状态
 */
export function getCareerReportStatusApi(taskId: string) {
  return request.get<Result<CareerReportStatus>>(`/career/form/status/${taskId}`)
}

/**
 * 获取职业规划报告
 * @param taskId 任务ID
 * @returns 规划报告内容（包含能力评估分数）
 */
export function getCareerReportApi(taskId: string) {
  return request.get<Result<CareerReport>>(`/career/form/report/${taskId}`)
}

/**
 * 保存表单草稿
 * @param data 表单数据（部分字段可选）
 * @returns 保存结果
 */
export function saveCareerFormDraftApi(data: Partial<CareerFormSubmitDTO>) {
  return request.post<Result>('/career/form/draft', data)
}

/**
 * 获取表单草稿
 * @returns 已保存的草稿数据
 */
export function getCareerFormDraftApi() {
  return request.get<Result>('/career/form/draft')
}

/**
 * 转换 CareerFormData 为提交 DTO
 * 用于将前端表单数据转换为后端接口所需格式
 * @param formData 前端表单数据
 * @returns 后端所需的提交数据格式
 */
export function convertToSubmitDTO(formData: CareerFormData): CareerFormSubmitDTO {
  // 处理专业数据：将级联选择器的数组转换为字符串
  const majorStr = formData.major?.length > 0
    ? formData.major.join(' / ')
    : ''

  // 处理学历：如果选择"其他"，则使用自定义值
  const educationStr = formData.education === '其他' && formData.educationOther
    ? formData.educationOther
    : (formData.education || '')

  // 处理证书：如果选择"其他"，添加自定义证书
  const certificates = [...(formData.certificates || [])]
  if (certificates.includes('其他') && formData.certificateOther) {
    // 移除"其他"，添加实际的自定义证书
    const otherIndex = certificates.indexOf('其他')
    certificates.splice(otherIndex, 1)
    certificates.push(formData.certificateOther)
  }

  // 处理优先级：转换为字符串数组
  const priorities = (formData.priorities || []).map(p => p.value)

  // 处理技能，确保 credibility 有值
  const skills = (formData.skills || []).map(s => ({
    name: s.name || '',
    credibility: s.credibility || 0
  })).filter(s => s.name)

  // 处理工具
  const tools = (formData.tools || []).map(t => ({
    name: t.name || '',
    proficiency: t.proficiency || '了解'
  })).filter(t => t.name)

  // 处理项目经历
  const projects = (formData.projects || []).map(p => ({
    isCompetition: p.isCompetition || false,
    name: p.name || '',
    desc: p.desc || ''
  })).filter(p => p.name || p.desc)

  // 处理实习经历
  const internships = (formData.internships || []).map(i => ({
    company: i.company || '',
    role: i.role || '',
    date: i.date || [],
    desc: i.desc || ''
  })).filter(i => i.company || i.role || i.desc)

  // 处理语言能力
  const languages = (formData.languages || [])
    .filter(lang => lang.type || lang.level || lang.other)
    .map(lang => ({
      type: lang.type || '',
      level: lang.level || '',
      other: lang.other || ''
    }))

  return {
    education: educationStr,
    major: majorStr,
    graduationDate: formData.graduationDate || undefined,
    languages,
    certificates,
    skills,
    tools,
    codeLinks: formData.codeAbility?.links || undefined,
    projects,
    internships,
    quizScores: {
      communication: formData.scores?.communication || false,
      stress: formData.scores?.stress || false,
      learning: formData.scores?.learning || false
    },
    innovation: formData.innovation || '',
    targetJob: formData.targetJob || '',
    targetIndustries: formData.targetIndustries || [],
    priorities
  }
}
