/**
 * CareerFormData -> JSON Resume 生成器。
 * 该模块负责：
 * 1. 将职业画像表单转换为标准化 JSON Resume
 * 2. 进行 JSON Schema 校验
 * 3. 生成内容完整性检查报告
 * 4. 提供可直接复用的示例数据
 */

import Ajv from 'ajv'
import dayjs from 'dayjs'
import { uniq } from 'lodash'

import type { SkillTool } from '@/types/careerform_question'
import type { CareerFormData, Internship, Project } from '@/types/careerform_report'
import type {
  GenerateJsonResumeInput,
  JsonResume,
  JsonResumeBasics,
  JsonResumeCertificate,
  JsonResumeEducation,
  JsonResumeGenerationResult,
  JsonResumeInterest,
  JsonResumeLanguage,
  JsonResumeProject,
  JsonResumeSkill,
  JsonResumeValidationError,
  JsonResumeWork,
  ResumeCertificateExtra,
  ResumeCompletenessItem,
  ResumeCompletenessReport,
  ResumeEducationExtra,
  ResumeFieldSource,
  ResumeInterestExtra,
  ResumeLanguageExtra,
  ResumeProfileExtras,
  ResumeProjectExtra,
  ResumeSkillExtra,
  ResumeWorkExtra
} from '@/types/json-resume'

/**
 * JSON Resume 简化版 JSON Schema。
 * 当前 Schema 覆盖了本项目后续模板渲染、预览、编辑、导出所需的核心字段。
 */
export const jsonResumeSchema: Record<string, unknown> = {
  type: 'object',
  additionalProperties: false,
  required: ['basics'],
  properties: {
    meta: {
      type: 'object',
      additionalProperties: false,
      properties: {
        version: { type: 'string' },
        lastModified: { type: 'string' },
        language: { type: 'string' }
      }
    },
    basics: {
      type: 'object',
      additionalProperties: false,
      required: ['name'],
      properties: {
        name: { type: 'string', minLength: 1 },
        label: { type: 'string' },
        image: { type: 'string' },
        email: { type: 'string' },
        phone: { type: 'string' },
        url: { type: 'string' },
        summary: { type: 'string' },
        location: {
          type: 'object',
          additionalProperties: false,
          properties: {
            address: { type: 'string' },
            postalCode: { type: 'string' },
            city: { type: 'string' },
            region: { type: 'string' },
            countryCode: { type: 'string' }
          }
        },
        profiles: {
          type: 'array',
          items: {
            type: 'object',
            additionalProperties: false,
            required: ['network'],
            properties: {
              network: { type: 'string', minLength: 1 },
              username: { type: 'string' },
              url: { type: 'string' }
            }
          }
        }
      }
    },
    work: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['name'],
        properties: {
          name: { type: 'string', minLength: 1 },
          position: { type: 'string' },
          url: { type: 'string' },
          startDate: { type: 'string' },
          endDate: { type: 'string' },
          summary: { type: 'string' },
          highlights: {
            type: 'array',
            items: { type: 'string' }
          },
          location: { type: 'string' }
        }
      }
    },
    education: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['institution'],
        properties: {
          institution: { type: 'string', minLength: 1 },
          url: { type: 'string' },
          area: { type: 'string' },
          studyType: { type: 'string' },
          startDate: { type: 'string' },
          endDate: { type: 'string' },
          score: { type: 'string' },
          courses: {
            type: 'array',
            items: { type: 'string' }
          }
        }
      }
    },
    skills: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['name', 'keywords'],
        properties: {
          name: { type: 'string', minLength: 1 },
          level: { type: 'string' },
          keywords: {
            type: 'array',
            items: { type: 'string' }
          }
        }
      }
    },
    projects: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['name'],
        properties: {
          name: { type: 'string', minLength: 1 },
          description: { type: 'string' },
          startDate: { type: 'string' },
          endDate: { type: 'string' },
          url: { type: 'string' },
          highlights: {
            type: 'array',
            items: { type: 'string' }
          },
          roles: {
            type: 'array',
            items: { type: 'string' }
          },
          keywords: {
            type: 'array',
            items: { type: 'string' }
          },
          entity: { type: 'string' }
        }
      }
    },
    languages: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['language'],
        properties: {
          language: { type: 'string', minLength: 1 },
          fluency: { type: 'string' }
        }
      }
    },
    certificates: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['name'],
        properties: {
          name: { type: 'string', minLength: 1 },
          issuer: { type: 'string' },
          date: { type: 'string' },
          url: { type: 'string' }
        }
      }
    },
    interests: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['name'],
        properties: {
          name: { type: 'string', minLength: 1 },
          keywords: {
            type: 'array',
            items: { type: 'string' }
          }
        }
      }
    }
  }
}

const ajv = new Ajv({
  allErrors: true,
  allowUnionTypes: true
})

const validateJsonResumeSchema = ajv.compile(jsonResumeSchema)

/** 将任意文本标准化，去除多余空白。 */
function normalizeText(value?: string | null): string {
  if (!value) {
    return ''
  }

  return value
    .replace(/\r\n/g, '\n')
    .replace(/\s+/g, ' ')
    .trim()
}

/** 将多行描述拆分为亮点列表。 */
function splitToHighlights(value?: string | null): string[] {
  if (!value) {
    return []
  }

  const normalized = value.replace(/\r\n/g, '\n')
  const fragments = normalized
    .split(/\n+|[；;]+/)
    .map(item => item.replace(/^[\s\-•·]+/, '').trim())
    .filter(Boolean)

  return uniq(fragments)
}

/** 判断字符串是否非空。 */
function hasText(value?: string | null): boolean {
  return normalizeText(value).length > 0
}

/** 获取第一项非空字符串。 */
function firstNonEmpty(...values: Array<string | undefined | null>): string | undefined {
  for (const value of values) {
    const normalized = normalizeText(value)
    if (normalized) {
      return normalized
    }
  }

  return undefined
}

/** 将日期统一转换为 YYYY-MM-DD。 */
export function toJsonResumeDate(
  value?: string | Date | null,
  options?: { endOfPeriod?: boolean }
): string | undefined {
  if (!value) {
    return undefined
  }

  if (value instanceof Date) {
    const dateValue = dayjs(value)
    return dateValue.isValid() ? dateValue.format('YYYY-MM-DD') : undefined
  }

  const raw = value.trim()
  if (!raw) {
    return undefined
  }

  const normalized = raw.replace(/\./g, '-').replace(/\//g, '-')

  if (/^\d{4}$/.test(normalized)) {
    return options?.endOfPeriod
      ? dayjs(`${normalized}-12-31`).format('YYYY-MM-DD')
      : dayjs(`${normalized}-01-01`).format('YYYY-MM-DD')
  }

  if (/^\d{4}-\d{2}$/.test(normalized)) {
    const base = dayjs(`${normalized}-01`)
    if (!base.isValid()) {
      return undefined
    }

    return options?.endOfPeriod
      ? base.endOf('month').format('YYYY-MM-DD')
      : base.startOf('month').format('YYYY-MM-DD')
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(normalized)) {
    const dateValue = dayjs(normalized)
    return dateValue.isValid() ? dateValue.format('YYYY-MM-DD') : undefined
  }

  const fallback = dayjs(normalized)
  return fallback.isValid() ? fallback.format('YYYY-MM-DD') : undefined
}

/** 将学校专业数组拼接为可读专业名。 */
function formatMajor(major: string[]): string | undefined {
  const result = major.map(item => normalizeText(item)).filter(Boolean).join(' / ')
  return result || undefined
}

/** 将学历字段转为标准输出。 */
function formatEducationLabel(formData: CareerFormData): string | undefined {
  const education = normalizeText(formData.education)
  const other = normalizeText(formData.educationOther)
  if (education === '其他' && other) {
    return other
  }

  return education || undefined
}

/** 将技能分数转为可读等级。 */
function mapScoreToLevel(score?: number): string | undefined {
  if (typeof score !== 'number' || Number.isNaN(score)) {
    return undefined
  }

  if (score >= 90) return 'expert'
  if (score >= 75) return 'advanced'
  if (score >= 60) return 'intermediate'
  if (score > 0) return 'beginner'
  return undefined
}

/** 构建 basics.summary。 */
function buildSummary(formData: CareerFormData, extras: ResumeProfileExtras): string | undefined {
  const directSummary = normalizeText(extras.basics.summary)
  if (directSummary) {
    return directSummary
  }

  const major = formatMajor(formData.major)
  const targetJob = normalizeText(formData.targetJob)
  const industries = formData.targetIndustries.map(item => normalizeText(item)).filter(Boolean)
  const innovation = normalizeText(formData.innovation)

  const segments = [
    targetJob ? `目标岗位为${targetJob}` : '',
    major ? `专业背景为${major}` : '',
    industries.length ? `关注行业包括${industries.join('、')}` : '',
    innovation ? `具备创新实践：${innovation}` : ''
  ].filter(Boolean)

  return segments.length ? `${segments.join('，')}。` : undefined
}

/** 构建基础信息。 */
function buildBasics(formData: CareerFormData, extras: ResumeProfileExtras): JsonResumeBasics {
  const basics: JsonResumeBasics = {
    name: normalizeText(extras.basics.name),
    label: firstNonEmpty(extras.basics.label, formData.targetJob),
    image: firstNonEmpty(extras.basics.image),
    email: firstNonEmpty(extras.basics.email),
    phone: firstNonEmpty(extras.basics.phone),
    url: firstNonEmpty(extras.basics.url),
    summary: buildSummary(formData, extras)
  }

  const location = {
    address: firstNonEmpty(extras.basics.address),
    postalCode: firstNonEmpty(extras.basics.postalCode),
    city: firstNonEmpty(extras.basics.city),
    region: firstNonEmpty(extras.basics.region),
    countryCode: firstNonEmpty(extras.basics.countryCode)
  }

  if (Object.values(location).some(Boolean)) {
    basics.location = location
  }

  if (extras.basics.profiles?.length) {
    basics.profiles = extras.basics.profiles
      .map(profile => ({
        network: normalizeText(profile.network),
        username: firstNonEmpty(profile.username),
        url: firstNonEmpty(profile.url)
      }))
      .filter(profile => hasText(profile.network))
  }

  return removeEmptyFields(basics)
}

/** 将 CareerForm 实习经历映射为工作经历。 */
function mapInternshipToWork(internship: Internship): JsonResumeWork | null {
  const company = normalizeText(internship.company)
  const role = normalizeText(internship.role)
  const summary = normalizeText(internship.desc)

  if (!company && !role && !summary) {
    return null
  }

  const dates = Array.isArray(internship.date) ? internship.date : []
  const highlights = splitToHighlights(internship.desc)

  return removeEmptyFields({
    name: company || '未命名公司',
    position: role || undefined,
    startDate: dates[0] ? toJsonResumeDate(dates[0]) : undefined,
    endDate: dates[1] ? toJsonResumeDate(dates[1], { endOfPeriod: true }) : undefined,
    summary: summary || undefined,
    highlights: highlights.length ? highlights : undefined
  })
}

/** 将扩展工作经历转为 JSON Resume 工作经历。 */
function mapExtraWorkToWork(work: ResumeWorkExtra): JsonResumeWork | null {
  const name = normalizeText(work.name)
  if (!name) {
    return null
  }

  return removeEmptyFields({
    name,
    position: firstNonEmpty(work.position),
    url: firstNonEmpty(work.url),
    startDate: toJsonResumeDate(work.startDate),
    endDate: toJsonResumeDate(work.endDate ?? undefined, { endOfPeriod: true }),
    summary: firstNonEmpty(work.summary),
    highlights: work.highlights?.map(item => normalizeText(item)).filter(Boolean),
    location: firstNonEmpty(work.location)
  })
}

/** 构建工作经历。 */
function buildWork(formData: CareerFormData, extras: ResumeProfileExtras): JsonResumeWork[] {
  const items: JsonResumeWork[] = []

  if (extras.includeCareerFormSections !== false) {
    for (const internship of formData.internships) {
      const mapped = mapInternshipToWork(internship)
      if (mapped) {
        items.push(mapped)
      }
    }
  }

  for (const work of extras.workHistory ?? []) {
    const mapped = mapExtraWorkToWork(work)
    if (mapped) {
      items.push(mapped)
    }
  }

  return items
}

/** 将 CareerForm 教育信息映射为教育经历。 */
function mapFormEducation(formData: CareerFormData): JsonResumeEducation | null {
  const studyType = formatEducationLabel(formData)
  const area = formatMajor(formData.major)
  const endDate = toJsonResumeDate(formData.graduationDate, { endOfPeriod: true })

  if (!studyType && !area && !endDate) {
    return null
  }

  return removeEmptyFields({
    institution: '待补充学校名称',
    area,
    studyType,
    endDate
  })
}

/** 将扩展教育经历映射为标准教育经历。 */
function mapExtraEducation(education: ResumeEducationExtra): JsonResumeEducation | null {
  const institution = normalizeText(education.institution)
  if (!institution) {
    return null
  }

  const startDate = toJsonResumeDate(education.startDate)
  const endDate = toJsonResumeDate(education.endDate, { endOfPeriod: true })
  const normalizedDates =
    startDate && endDate && dayjs(startDate).isAfter(dayjs(endDate))
      ? {
          startDate: toJsonResumeDate(education.endDate),
          endDate: toJsonResumeDate(education.startDate, { endOfPeriod: true })
        }
      : { startDate, endDate }

  return removeEmptyFields({
    institution,
    url: firstNonEmpty(education.url),
    area: firstNonEmpty(education.area),
    studyType: firstNonEmpty(education.studyType),
    startDate: normalizedDates.startDate,
    endDate: normalizedDates.endDate,
    score: firstNonEmpty(education.score),
    courses: education.courses?.map(item => normalizeText(item)).filter(Boolean)
  })
}

/** 构建教育经历。 */
function buildEducation(formData: CareerFormData, extras: ResumeProfileExtras): JsonResumeEducation[] {
  const items: JsonResumeEducation[] = []
  const hasExtraInstitution = (extras.educationHistory ?? []).some(education =>
    hasText(education.institution)
  )

  if (extras.includeCareerFormSections !== false && !hasExtraInstitution) {
    const mappedFormEducation = mapFormEducation(formData)
    if (mappedFormEducation) {
      items.push(mappedFormEducation)
    }
  }

  for (const education of extras.educationHistory ?? []) {
    const mapped = mapExtraEducation(education)
    if (mapped) {
      items.push(mapped)
    }
  }

  return items
}

/** 将技能列表映射为关键词。 */
function mapSkillToolKeywords(items: SkillTool[]): string[] {
  return uniq(
    items
      .map(item => normalizeText(item.name))
      .filter(Boolean)
  )
}

/** 构建技能分组。 */
function buildSkills(formData: CareerFormData, extras: ResumeProfileExtras): JsonResumeSkill[] {
  const skills: JsonResumeSkill[] = []

  const coreSkills = mapSkillToolKeywords(formData.skills)
  if (coreSkills.length) {
    const avgScore = formData.skills.length
      ? Math.round(formData.skills.reduce((sum, item) => sum + (item.score || 0), 0) / formData.skills.length)
      : undefined

    skills.push(removeEmptyFields({
      name: '专业技能',
      level: mapScoreToLevel(avgScore),
      keywords: coreSkills
    }))
  }

  const toolSkills = mapSkillToolKeywords(formData.tools)
  if (toolSkills.length) {
    const avgScore = formData.tools.length
      ? Math.round(formData.tools.reduce((sum, item) => sum + (item.score || 0), 0) / formData.tools.length)
      : undefined

    skills.push(removeEmptyFields({
      name: '工具能力',
      level: mapScoreToLevel(avgScore),
      keywords: toolSkills
    }))
  }

  const certificateKeywords = uniq(
    formData.certificates
      .map(item => normalizeText(item))
      .filter(item => item && item !== '其他')
      .concat(hasText(formData.certificateOther) ? [normalizeText(formData.certificateOther)] : [])
  )
  if (certificateKeywords.length) {
    skills.push({
      name: '证书资质',
      keywords: certificateKeywords
    })
  }

  if (formData.targetIndustries.length) {
    skills.push({
      name: '目标行业',
      keywords: uniq(formData.targetIndustries.map(item => normalizeText(item)).filter(Boolean))
    })
  }

  for (const customGroup of extras.customSkillGroups ?? []) {
    const mapped = mapExtraSkillGroup(customGroup)
    if (mapped) {
      skills.push(mapped)
    }
  }

  return skills
}

/** 扩展技能组映射。 */
function mapExtraSkillGroup(group: ResumeSkillExtra): JsonResumeSkill | null {
  const name = normalizeText(group.name)
  const keywords = uniq(group.keywords.map(item => normalizeText(item)).filter(Boolean))

  if (!name || !keywords.length) {
    return null
  }

  return removeEmptyFields({
    name,
    level: firstNonEmpty(group.level),
    keywords
  })
}

/** 将 CareerForm 项目映射为项目经历。 */
function mapProjectToResumeProject(project: Project): JsonResumeProject | null {
  const name = normalizeText(project.name)
  const description = normalizeText(project.desc)

  if (!name && !description) {
    return null
  }

  return removeEmptyFields({
    name: name || '未命名项目',
    description: description || undefined,
    highlights: splitToHighlights(project.desc),
    entity: project.isCompetition ? 'competition' : 'project'
  })
}

/** 扩展项目映射。 */
function mapExtraProject(project: ResumeProjectExtra): JsonResumeProject | null {
  const name = normalizeText(project.name)
  if (!name) {
    return null
  }

  return removeEmptyFields({
    name,
    description: firstNonEmpty(project.description),
    startDate: toJsonResumeDate(project.startDate),
    endDate: toJsonResumeDate(project.endDate ?? undefined, { endOfPeriod: true }),
    url: firstNonEmpty(project.url),
    highlights: project.highlights?.map(item => normalizeText(item)).filter(Boolean),
    roles: project.roles?.map(item => normalizeText(item)).filter(Boolean),
    keywords: project.keywords?.map(item => normalizeText(item)).filter(Boolean),
    entity: firstNonEmpty(project.entity)
  })
}

/** 构建项目经历。 */
function buildProjects(formData: CareerFormData, extras: ResumeProfileExtras): JsonResumeProject[] {
  const items: JsonResumeProject[] = []

  if (extras.includeCareerFormSections !== false) {
    for (const project of formData.projects) {
      const mapped = mapProjectToResumeProject(project)
      if (mapped) {
        items.push(mapped)
      }
    }
  }

  for (const project of extras.projectHistory ?? []) {
    const mapped = mapExtraProject(project)
    if (mapped) {
      items.push(mapped)
    }
  }

  return items
}

/** 构建语言能力。 */
function buildLanguages(formData: CareerFormData, extras: ResumeProfileExtras): JsonResumeLanguage[] {
  const items: JsonResumeLanguage[] = []

  for (const item of formData.languages) {
    const language = normalizeText(item.type)
    const fluency = firstNonEmpty(item.level, item.other)
    if (language) {
      items.push(removeEmptyFields({ language, fluency }))
    }
  }

  for (const item of extras.languages ?? []) {
    const mapped = mapExtraLanguage(item)
    if (mapped) {
      items.push(mapped)
    }
  }

  return items
}

/** 扩展语言映射。 */
function mapExtraLanguage(item: ResumeLanguageExtra): JsonResumeLanguage | null {
  const language = normalizeText(item.language)
  if (!language) {
    return null
  }

  return removeEmptyFields({
    language,
    fluency: firstNonEmpty(item.fluency)
  })
}

/** 构建证书。 */
function buildCertificates(formData: CareerFormData, extras: ResumeProfileExtras): JsonResumeCertificate[] {
  const items: JsonResumeCertificate[] = []

  for (const name of formData.certificates) {
    const normalized = normalizeText(name)
    if (!normalized || normalized === '其他') {
      continue
    }

    items.push({ name: normalized })
  }

  if (hasText(formData.certificateOther)) {
    items.push({ name: normalizeText(formData.certificateOther) })
  }

  for (const certificate of extras.certificates ?? []) {
    const mapped = mapExtraCertificate(certificate)
    if (mapped) {
      items.push(mapped)
    }
  }

  return items
}

/** 扩展证书映射。 */
function mapExtraCertificate(item: ResumeCertificateExtra): JsonResumeCertificate | null {
  const name = normalizeText(item.name)
  if (!name) {
    return null
  }

  return removeEmptyFields({
    name,
    issuer: firstNonEmpty(item.issuer),
    date: toJsonResumeDate(item.date),
    url: firstNonEmpty(item.url)
  })
}

/** 构建兴趣。 */
function buildInterests(extras: ResumeProfileExtras): JsonResumeInterest[] {
  return (extras.interests ?? [])
    .map(item => mapExtraInterest(item))
    .filter((item): item is JsonResumeInterest => item !== null)
}

/** 扩展兴趣映射。 */
function mapExtraInterest(item: ResumeInterestExtra): JsonResumeInterest | null {
  const name = normalizeText(item.name)
  if (!name) {
    return null
  }

  return removeEmptyFields({
    name,
    keywords: item.keywords?.map(keyword => normalizeText(keyword)).filter(Boolean)
  })
}

/** 删除对象中的空值字段。 */
function removeEmptyFields<T extends object>(value: T): T {
  const entries = Object.entries(value as Record<string, unknown>).filter(([, item]) => {
    if (item === undefined || item === null) {
      return false
    }

    if (typeof item === 'string') {
      return item.trim().length > 0
    }

    if (Array.isArray(item)) {
      return item.length > 0
    }

    if (typeof item === 'object') {
      return Object.keys(item).length > 0
    }

    return true
  })

  return Object.fromEntries(entries) as T
}

/** 按是否保留空数组字段处理最终对象。 */
function finalizeResume(resume: JsonResume, keepEmptyArrays?: boolean): JsonResume {
  const nextResume: JsonResume = {
    meta: resume.meta,
    basics: resume.basics
  }

  const listFields: Array<keyof JsonResume> = [
    'work',
    'education',
    'skills',
    'projects',
    'languages',
    'certificates',
    'interests'
  ]

  for (const field of listFields) {
    const fieldValue = resume[field]
    if (Array.isArray(fieldValue)) {
      if (fieldValue.length > 0 || keepEmptyArrays) {
        ;((nextResume as unknown) as Record<string, unknown>)[field] = fieldValue
      }
    }
  }

  return nextResume
}

/** 执行 JSON Schema 校验。 */
export function validateJsonResume(resume: JsonResume): {
  valid: boolean
  errors: JsonResumeValidationError[]
} {
  const valid = validateJsonResumeSchema(resume)

  const errors: JsonResumeValidationError[] = (validateJsonResumeSchema.errors ?? []).map(error => ({
    instancePath: error.instancePath || '/',
    message: error.message || '未知校验错误',
    keyword: error.keyword
  }))

  return {
    valid: Boolean(valid),
    errors
  }
}

/** 添加完整性检查项。 */
function createCompletenessItem(
  field: string,
  label: string,
  required: boolean,
  completed: boolean,
  source: ResumeFieldSource,
  message?: string
): ResumeCompletenessItem {
  return {
    field,
    label,
    required,
    completed,
    source,
    message
  }
}

/** 生成完整性检查报告。 */
export function inspectJsonResumeCompleteness(resume: JsonResume): ResumeCompletenessReport {
  const items: ResumeCompletenessItem[] = []

  items.push(
    createCompletenessItem('basics.name', '姓名', true, hasText(resume.basics.name), 'profileExtras', '姓名是简历模板渲染的核心字段'),
    createCompletenessItem('basics.label', '职位标签', true, hasText(resume.basics.label), 'derived', '建议填写目标岗位或当前岗位'),
    createCompletenessItem('basics.email', '邮箱', false, hasText(resume.basics.email), 'profileExtras'),
    createCompletenessItem('basics.phone', '电话', false, hasText(resume.basics.phone), 'profileExtras'),
    createCompletenessItem('basics.summary', '个人简介', true, hasText(resume.basics.summary), 'derived', '个人简介会直接影响预览质量和后续 AI 优化效果'),
    createCompletenessItem(
      'education[0].institution',
      '学校名称',
      true,
      Boolean(resume.education?.some(item => hasText(item.institution) && item.institution !== '待补充学校名称')),
      'profileExtras',
      'CareerFormData 本身没有学校名称，建议通过额外资料补齐'
    ),
    createCompletenessItem(
      'education[0].area',
      '专业',
      true,
      Boolean(resume.education?.some(item => hasText(item.area))),
      'careerForm'
    ),
    createCompletenessItem(
      'skills',
      '技能信息',
      true,
      Boolean(resume.skills?.some(item => item.keywords.length > 0)),
      'careerForm',
      '技能为空会影响岗位匹配和简历完整度检查'
    ),
    createCompletenessItem(
      'projects/work',
      '项目或工作经历',
      true,
      Boolean((resume.projects?.length || 0) > 0 || (resume.work?.length || 0) > 0),
      'careerForm',
      '至少建议保留一个项目或工作经历'
    )
  )

  const requiredItems = items.filter(item => item.required)
  const completedRequiredItems = requiredItems.filter(item => item.completed)
  const score = requiredItems.length
    ? Math.round((completedRequiredItems.length / requiredItems.length) * 100)
    : 100

  return {
    score,
    items,
    missingRequiredFields: requiredItems.filter(item => !item.completed)
  }
}

/** 生成标准 JSON Resume。 */
export function generateJsonResume(input: GenerateJsonResumeInput): JsonResumeGenerationResult {
  const { careerFormData, profileExtras } = input

  const draftResume: JsonResume = {
    meta: {
      version: '1.0.0',
      language: 'zh-CN',
      lastModified: new Date().toISOString()
    },
    basics: buildBasics(careerFormData, profileExtras),
    work: buildWork(careerFormData, profileExtras),
    education: buildEducation(careerFormData, profileExtras),
    skills: buildSkills(careerFormData, profileExtras),
    projects: buildProjects(careerFormData, profileExtras),
    languages: buildLanguages(careerFormData, profileExtras),
    certificates: buildCertificates(careerFormData, profileExtras),
    interests: buildInterests(profileExtras)
  }

  const resume = finalizeResume(draftResume, profileExtras.keepEmptyArrays)
  const validation = validateJsonResume(resume)
  const completeness = inspectJsonResumeCompleteness(resume)

  return {
    resume,
    valid: validation.valid,
    errors: validation.errors,
    completeness
  }
}

/** 为当前项目提供的默认 extras 模板。 */
export function createDefaultResumeProfileExtras(name: string = ''): ResumeProfileExtras {
  return {
    basics: {
      name: normalizeText(name),
      label: '',
      email: '',
      phone: '',
      summary: '',
      city: '',
      region: '',
      profiles: []
    },
    workHistory: [],
    educationHistory: [],
    projectHistory: [],
    customSkillGroups: [],
    languages: [],
    certificates: [],
    interests: [],
    includeCareerFormSections: true,
    keepEmptyArrays: false
  }
}

/**
 * 使用示例：
 * 1. 直接将 CareerFormData + 扩展资料转为 JSON Resume
 * 2. 获得校验结果和完整性报告
 */
export const jsonResumeGenerationExample: GenerateJsonResumeInput = {
  careerFormData: {
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
      { name: 'TypeScript', score: 88 },
      { name: 'Vue 3', score: 85 },
      { name: 'Node.js', score: 78 }
    ],
    tools: [
      { name: 'Git', score: 90 },
      { name: 'Docker', score: 72 }
    ],
    codeAbility: {
      links: 'https://github.com/johndoe'
    },
    projects: [
      {
        isCompetition: false,
        name: '职业画像系统前端重构',
        desc: '负责 Vue 3 + TypeScript 前端重构；完成组件拆分与表单体验优化；页面加载性能提升 35%'
      }
    ],
    internships: [
      {
        company: '示例科技有限公司',
        role: '前端开发实习生',
        date: [new Date('2024-07-01'), new Date('2024-10-31')],
        desc: '参与招聘后台系统开发；封装通用表单组件；联调简历解析与岗位匹配接口'
      }
    ],
    quizDetail: [],
    innovation: '将复杂表单拆分为分步流程，并补充完整性引导，大幅降低用户放弃率',
    targetJob: '前端工程师',
    targetIndustries: ['互联网', '企业服务'],
    priorities: [
      { value: 'tech', label: '技术成长' },
      { value: 'salary', label: '薪资' },
      { value: 'stable', label: '稳定' }
    ]
  },
  profileExtras: {
    basics: {
      name: '张三',
      label: '前端工程师',
      email: 'zhangsan@example.com',
      phone: '13800000000',
      summary: '具备 Vue 3、TypeScript 和企业级中后台项目经验，关注可维护性、表单体验与简历产品化能力。',
      city: '上海',
      region: '上海',
      profiles: [
        {
          network: 'GitHub',
          username: 'johndoe',
          url: 'https://github.com/johndoe'
        }
      ]
    },
    workHistory: [],
    educationHistory: [
      {
        institution: '华东某大学',
        area: '软件工程',
        studyType: '本科',
        startDate: '2021-09',
        endDate: '2025-06'
      }
    ],
    projectHistory: [
      {
        name: 'JSON Resume 简历生成模块',
        description: '为职业画像系统新增标准化 JSON Resume 产物，支持预览、编辑、完整性校验和导出。',
        startDate: '2026-03-01',
        endDate: '2026-03-31',
        highlights: [
          '统一简历结构，减少多处重复映射逻辑',
          '增加 AJV 校验和内容完整性评分，方便后续编辑与导出'
        ],
        keywords: ['TypeScript', 'AJV', 'JSON Resume']
      }
    ],
    customSkillGroups: [
      {
        name: '工程化',
        level: 'advanced',
        keywords: ['Vite', 'ESLint', 'Vitest']
      }
    ],
    languages: [
      {
        language: '中文',
        fluency: '母语'
      }
    ],
    certificates: [
      {
        name: '软件设计师',
        issuer: '工业和信息化部教育与考试中心'
      }
    ],
    interests: [
      {
        name: '技术写作',
        keywords: ['前端架构', '工程实践']
      }
    ],
    includeCareerFormSections: true,
    keepEmptyArrays: false
  }
}

/** 示例运行结果，便于调用方直接参考。 */
export const jsonResumeGenerationExampleResult = generateJsonResume(jsonResumeGenerationExample)
