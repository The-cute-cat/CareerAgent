import request from '@/utils/request'
import type { JobMatchItem } from '@/types/job-match'
import { mockSubmitFormApi } from '@/mock/mockdata/Resume_mockdata'
import type { CareerFormData, CareerFormSubmitDTO } from '@/types/careerform_report'
import type { Result } from '@/types/type'

// ==================== Mock 开关配置 ====================
const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'

/**
 * 提交职业规划表单数据
 * 后端直接返回人岗匹配结果，无需轮询
 * @param data 表单数据
 * @returns 人岗匹配分析结果（包含推荐岗位列表）
 */
export function submitCareerFormApi(data: CareerFormSubmitDTO) {
  if (ENABLE_MOCK) {
    console.log('[Mock] 提交表单数据:', data)
    return mockSubmitFormApi('success', 1000)
  }
  return request.post<Result<JobMatchItem[]>>('/career/form/submit', data)
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

  // 处理技能，确保 score 有值
  const skills = (formData.skills || []).map(s => ({
    name: s.name || '',
    score: s.score || 0
  })).filter(s => s.name)

  // 处理工具
  const tools = (formData.tools || []).map(t => ({
    name: t.name || '',
    score: t.score || 0
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
    quizDetail: formData.quizDetail?.length ? formData.quizDetail : undefined,
    innovation: formData.innovation || '',
    targetJob: formData.targetJob || '',
    targetIndustries: formData.targetIndustries || [],
    priorities
  }
}
