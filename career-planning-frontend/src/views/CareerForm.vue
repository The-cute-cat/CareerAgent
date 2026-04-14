<script setup lang="ts">
import { ref, reactive, computed, nextTick, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { cloneDeep } from 'lodash'



import {
  DocumentAdd,
  Trophy,
  DataAnalysis,
  Position,
  Plus,
  Delete,
  Upload,
  Check,
  ArrowUp,
  ArrowDown,
  RefreshRight,
  InfoFilled,
  CircleCheck,
  Document,
  Loading,
  Warning,
  Rank,
  Folder,
  Briefcase,
  OfficeBuilding,
  User,
  Calendar,
  Edit,
  EditPen,
  Switch,
  Medal,
  Download,
  View
} from '@element-plus/icons-vue'
import CareerFormUpload from '@/components/CareerForm_Upload.vue'
import ResumeMissingFieldsChat from '@/components/ResumeMissingFieldsChat.vue'
import Quenation from '@/components/Quenation.vue'
import { submitCareerFormApi, convertToSubmitDTO } from '@/api/career-form/formdata'
import { evaluateCodeAbilityApi } from '@/api/career-form/codeAbility'
import { submitQuiz, getQuestionsApi, getPersonQuizApi } from '@/api/career-form/questions'
import type { CareerFormData, QuizDetailItem } from '@/types/careerform_report'
import type { Question, BackendPersonData } from '@/types/careerform_question'
import type { CodeAbilityEvaluateData } from '@/types/code-ability'
import type { JobMatchItem } from '@/types/job-match'
import type { JsonResumeGenerationResult, ResumeProfileExtras } from '@/types/json-resume'
import { useJsonResumeStore } from '@/stores/modules/jsonResume'
import { createDefaultResumeProfileExtras, generateJsonResume } from '@/utils/json-resume'
import { exportJsonResumeToWord, exportResumePreviewToPdf } from '@/utils/resume-export'
import { clearCareerFormData, loadCareerFormData, saveCareerFormData } from '@/utils/career-runtime'
import {
  majorOptions
} from '@/mock/mockdata/CareerForm_mockdata'


// --- 状态定义 ---

/** 路由实例 */
const route = useRoute()
const router = useRouter()
const jsonResumeStore = useJsonResumeStore()

/** 表单引用，用于表单验证和重置 */
const formRef = ref<FormInstance>()

/** 当前激活的菜单项索引，控制显示哪个表单步骤 (1-5) */
const activeMenu = ref('1')
type CareerSection = 'resume' | 'template' | 'voice'
const activeProfileTab = ref<'resume' | 'template'>('resume')

/** 表单提交状态，控制提交按钮的加载状态 */
const submitting = ref(false)

/** 新增技能输入框的临时值 */
const newSkill = ref('')

/** 新增工具输入框的临时值 */
const newTool = ref('')

/** 控制简历上传弹窗的显示/隐藏 */
const showUploadDialog = ref(false)

/** 标记用户是否已上传简历 */
const hasUploadedResume = ref(false)
const showMissingFieldsChat = ref(false)

/** 控制学历"其他"输入框的显示/隐藏 */
const showEducationInput = ref(false)

/** 控制证书"其他"输入框的显示/隐藏 */
const showCertificateInput = ref(false)

/** 当前正在进行的素质测评类型 (communication/stress/learning) */
const currentQuizType = ref('')

/** 拖拽排序相关状态 */
const dragIndex = ref(-1)
const dragOverIndex = ref(-1)

/** 控制项目经历弹窗显示/隐藏 */
const showProjectDialog = ref(false)

/** 控制实践经历弹窗显示/隐藏 */
const showInternshipDialog = ref(false)
const codeAbilityUseAi = ref(false)
const codeAbilityEvaluating = ref(false)
const codeAbilityResultVisible = ref(false)
const codeAbilityResult = ref<CodeAbilityEvaluateData | null>(null)
const lastEvaluatedCodeRepoUrls = ref<string[]>([])
type MissingFieldKey = keyof CareerFormData | 'qualityAssessment'
type ResumeChatField = { field: MissingFieldKey; label: string; step: string; optional?: boolean }
const pendingMissingFields = ref<ResumeChatField[]>([])
const resumeProfileDialogVisible = ref(false)
const resumePreviewDialogVisible = ref(false)
const resumeTemplateDialogVisible = ref(false)
const resumeGenerating = ref(false)
const resumeExportingPdf = ref(false)
const resumeExportingWord = ref(false)
const resumePreviewRef = ref<HTMLElement | null>(null)
const jsonResumeResult = ref<JsonResumeGenerationResult | null>(null)
const resumeProfileExtras = ref<ResumeProfileExtras>(
  cloneDeep(jsonResumeStore.profileExtras || createDefaultResumeProfileExtras())
)
const selectedResumeTemplate = ref<'professional' | 'modern' | 'compact'>('professional')

if (!resumeProfileExtras.value.educationHistory?.length) {
  resumeProfileExtras.value.educationHistory = [
    {
      institution: '',
      area: '',
      studyType: '',
      startDate: '',
      endDate: ''
    }
  ]
}

const syncCareerSectionFromRoute = () => {
  if (route.path.includes('/career-form/template')) {
    activeProfileTab.value = 'template'
    return
  }
  activeProfileTab.value = 'resume'
}

watch(() => route.path, syncCareerSectionFromRoute, { immediate: true })



/** 项目经历弹窗表单数据 */
const projectForm = reactive({
  isCompetition: false,
  name: '',
  desc: '',
  isEdit: false,
  editIndex: -1
})

/** 实践经历弹窗表单数据 */
const internshipForm = reactive({
  company: '',
  role: '',
  date: [] as Date[],
  desc: '',
  isEdit: false,
  editIndex: -1
})

/** 人岗匹配结果数据（后端返回的岗位匹配数组） */
const jobMatchResult = reactive<JobMatchItem[]>([])

/** 画像完整度 (0-100) */
const profileCompleteness = computed(() => {
  let total = 0
  let completed = 0

  // 基本信息项
  const basicItems = [
    !!formData.education,
    formData.major.length > 0,
    !!formData.graduationDate
  ]
  total += basicItems.length
  completed += basicItems.filter(Boolean).length

  // 技能与证书项
  const skillItems = [
    formData.languages.some(l => l.type && l.level),
    formData.certificates.length > 0,
    formData.skills.length > 0,
    formData.tools.length > 0
  ]
  total += skillItems.length
  completed += skillItems.filter(Boolean).length

  // 经历与项目项
  const expItems = [
    formData.projects.length > 0,
    formData.internships.length > 0
  ]
  total += expItems.length
  completed += expItems.filter(Boolean).length

  // 素质测评项
  const quizItems = [
    quizCompleted.communication,
    quizCompleted.stress,
    quizCompleted.learning,
    !!formData.innovation
  ]
  total += quizItems.length
  completed += quizItems.filter(Boolean).length

  // 职业意向项
  const careerItems = [
    !!formData.targetJob,
    formData.targetIndustries.length > 0
  ]
  total += careerItems.length
  completed += careerItems.filter(Boolean).length

  return Math.round((completed / total) * 100)
})


// --- 素质测评完成状态（独立于表单数据） ---

const quizCompleted = reactive({
  communication: false,
  stress: false,
  learning: false
})


// --- 表单数据 ---

const formData = reactive<CareerFormData>({
  /** 学历：高中/大专/本科/硕士/博士/其他 */
  education: '',
  /** 当学历选择"其他"时的自定义输入值 */
  educationOther: '',
  /** 专业：级联选择，如 ['计算机类', '软件工程'] */
  major: [],
  /** 预计毕业日期：格式为 YYYY-MM */
  graduationDate: '',
  /** 语言能力列表：每项包含语言类型、等级和其他说明 */
  languages: [{ type: '', level: '', other: '' }],
  /** 已获得的证书列表：如 ['CET-4', 'PMP'] */
  certificates: [],
  /** 当证书选择"其他"时的自定义输入值 */
  certificateOther: '',
  /** 技能列表：每项包含技能名称和熟练度(0-100) */
  skills: [],
  /** 工具列表：每项包含工具名称和熟练程度(了解/熟练/精通) */
  tools: [],
  /** 代码能力：包含代码仓库链接 */
  codeAbility: { links: '' },
  /** 项目经历列表：每项包含项目名称、描述、是否为竞赛项目 */
  projects: [],
  /** 实习经历列表：每项包含公司、职位、日期范围、描述 */
  internships: [],
  /** 素质测评答题记录 */
  quizDetail: [],
  /** 创新案例描述：用户填写的创新经历 */
  innovation: '',
  /** 目标岗位：用户期望的职位名称 */
  targetJob: '',
  /** 目标行业：用户期望进入的行业列表 */
  targetIndustries: [],
  /** 职业优先级排序：技术成长/薪资/稳定，可拖拽调整顺序 */
  priorities: [
    { value: 'tech', label: '技术成长' },
    { value: 'salary', label: '薪资' },
    { value: 'stable', label: '稳定' }
  ]
})


// --- 计算属性 ---

/**
 * 当前步骤的标题
 * 根据 activeMenu 的值返回对应的步骤名称
 */
const currentSectionTitle = computed(() => {
  const titles: Record<string, string> = {
    '1': '基本信息',
    '2': '技能与证书',
    '3': '经历与项目',
    '4': '素质测评',
    '5': '职业意向'
  }
  return titles[activeMenu.value] || '基本信息'
})


/**
 * 表单完成进度百分比 (0-100)
 * 根据5个主要步骤的完成情况计算：基本信息、技能证书、经历项目、素质测评、职业意向
 */
const formProgress = computed(() => {
  let completed = 0
  const total = 5

  if (formData.education) completed++
  if (formData.major.length > 0) completed++
  if (formData.skills.length > 0) completed++
  if (formData.projects.length > 0 || formData.internships.length > 0) completed++
  if (formData.targetJob) completed++

  return Math.round((completed / total) * 100)
})

const completedStepCount = computed(() => {
  return [1, 2, 3, 4, 5].filter((step) => isStepCompleted(step)).length
})

const currentSectionDescription = computed(() => {
  const descriptions: Record<string, string> = {
    '1': '聚焦本步核心信息完善',
    '2': '补充技能、证书与能力标签',
    '3': '记录项目成果与实践履历',
    '4': '完成测评后可提升画像准确度',
    '5': '明确岗位偏好与发展方向'
  }
  return descriptions[activeMenu.value] || '聚焦本步核心信息完善'
})

const readinessText = computed(() => {
  if (profileCompleteness.value >= 80) return '较完善'
  if (profileCompleteness.value >= 40) return '完善中'
  return '待完善'
})

const readinessHint = computed(() => {
  if (profileCompleteness.value >= 80) return '信息较完整，后续建议会更准确'
  if (profileCompleteness.value >= 40) return '继续补充关键信息可提升评估质量'
  return '完善越充分，后续建议越准确'
})

const hasValidLanguage = (languages: Array<{ type: string; level: string }>) => {
  return Array.isArray(languages) && languages.some((language) => {
    const type = typeof language?.type === 'string' ? language.type.trim() : ''
    const level = typeof language?.level === 'string' ? language.level.trim() : ''
    return !!(type && level)
  })
}



/**
 * 判断指定步骤是否已完成
 * @param step - 步骤编号 (1-5)
 * @returns 该步骤是否已完成
 *
 * 步骤1: 基本信息 - 需要填写学历和专业
 * 步骤2: 技能证书 - 需要填写至少一项外语水平和一项专业技能
 * 步骤3: 经历项目 - 需要至少添加一个项目或实习经历
 * 步骤4: 素质测评 - 需要完成所有三项测评并填写创新案例
 * 步骤5: 职业意向 - 需要填写目标岗位和目标行业
 */
const isStepCompleted = (step: number) => {
  switch (step) {
    case 1:
      return !!(formData.education && formData.major.length > 0)
    case 2:
      return hasValidLanguage(formData.languages) && formData.skills.length > 0
    case 3:
      return !!(formData.projects.length > 0 || formData.internships.length > 0)
    case 4:
      return !!(quizCompleted.communication && quizCompleted.stress && quizCompleted.learning && formData.innovation)
    case 5:
      return !!(formData.targetJob && formData.targetIndustries.length > 0)
    default:
      return false
  }
}


// --- 专业级联数据 ---

/**
 * 专业级联选择器的数据源
 * 用于学历信息中的专业选择
 */



// --- 方法 ---

/**
 * 处理侧边栏菜单选择事件
 * @param index - 选中的菜单项索引
 */
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
}

const switchCareerSection = (section: CareerSection) => {
  if (section !== 'voice') {
    activeProfileTab.value = section
  }
  const routeMap: Record<CareerSection, string> = {
    resume: '/career-form/resume',
    template: '/career-form/template',
    voice: '/career-form/voice'
  }
  router.push(routeMap[section])
}

const goToResumeEditor = () => {
  router.push('/resume-editor')
}


/** 添加新的语言能力项 */
const addLanguage = () => formData.languages.push({ type: '', level: '', other: '' })

/**
 * 移除指定索引的语言能力项
 * @param index - 要移除的项的索引
 */
const removeLanguage = (index: number) => {
  ElMessageBox.confirm(
    '确定要删除此外语能力吗？',
    '删除确认',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      formData.languages.splice(index, 1)
      ElMessage({
        type: 'success',
        message: '已删除',
      })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除',
      })
    })
}

/**
 * 确认自定义语言输入
 * 将输入框的值回写到对应字段，并清空输入框
 * @param index - 语言项索引
 * @param field - 要更新的字段：type(语种) 或 level(水平)
 */
const confirmCustomLanguage = (index: number, field: 'type' | 'level') => {
  const lang = formData.languages[index]
  if (!lang) return
  if (lang.other.trim()) {
    if (field === 'type') {
      lang.type = lang.other.trim()
    } else {
      lang.level = lang.other.trim()
    }
    lang.other = ''
  }
}

/**
 * 处理学历选择变化
 * 当选择"其他"时显示自定义输入框，否则清空自定义值
 * @param value - 选中的学历值
 */
const handleEducationChange = (value: string) => {
  showEducationInput.value = value === '其他'
  if (value !== '其他') {
    formData.educationOther = ''
  }
}

/**
 * 处理证书选择变化
 * 当选择"其他"时显示自定义输入框，否则清空自定义值
 * @param value - 选中的证书数组
 */
const handleCertificateChange = (value: string[]) => {
  showCertificateInput.value = value.includes('其他')
  if (!showCertificateInput.value) {
    formData.certificateOther = ''
  }
}


/**
 * 添加新技能
 * 将 newSkill 输入框的值添加到技能列表，默认熟练度为50
 * 检查是否已存在（不区分大小写）
 */
const addSkill = () => {
  if (newSkill.value) {
    const skillName = newSkill.value.trim()
    // 检查是否已存在（不区分大小写）
    const isDuplicate = formData.skills.some(
      skill => skill.name.toLowerCase() === skillName.toLowerCase()
    )
    if (isDuplicate) {
      ElMessage.warning(`技能 "${skillName}" 已经添加过了`)
      return
    }
    formData.skills.push({ name: skillName, score: 50 })
    newSkill.value = ''
  }
}

/**
 * 移除指定索引的技能
 * @param index - 要移除的技能索引
 */
const removeSkill = (index: number) => {
  ElMessageBox.confirm(
    '确定要删除此专业技能吗？',
    '删除确认',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      formData.skills.splice(index, 1)
      ElMessage({
        type: 'success',
        message: '已删除',
      })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除',
      })
    })
}


/**
 * 添加新工具
 * 将 newTool 输入框的值添加到工具列表，默认熟练程度为"熟练"
 * 检查是否已存在（不区分大小写）
 */
const addTool = () => {
  if (newTool.value) {
    const toolName = newTool.value.trim()
    // 检查是否已存在（不区分大小写）
    const isDuplicate = formData.tools.some(
      tool => tool.name.toLowerCase() === toolName.toLowerCase()
    )
    if (isDuplicate) {
      ElMessage.warning(`工具 "${toolName}" 已经添加过了`)
      return
    }
    formData.tools.push({ name: toolName, score: 50 })
    newTool.value = ''
  }
}

/**
 * 移除指定索引的工具
 * @param index - 要移除的工具索引
 */
const removeTool = (index: number) => {
  ElMessageBox.confirm(
    '确定要删除此工具技能吗？',
    '删除确认',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      formData.tools.splice(index, 1)
      ElMessage({
        type: 'success',
        message: '已删除',
      })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除',
      })
    })
}


/** 打开项目经历弹窗（新增模式） */
const openProjectDialog = () => {
  projectForm.isCompetition = false
  projectForm.name = ''
  projectForm.desc = ''
  projectForm.isEdit = false
  projectForm.editIndex = -1
  showProjectDialog.value = true
}

/** 打开项目经历弹窗（编辑模式） */
const openEditProjectDialog = (index: number) => {
  const project = formData.projects[index]
  if (!project) {
    ElMessage.error('项目不存在')
    return
  }
  projectForm.isCompetition = project.isCompetition
  projectForm.name = project.name
  projectForm.desc = project.desc
  projectForm.isEdit = true
  projectForm.editIndex = index
  showProjectDialog.value = true
}

/** 确认添加/编辑项目经历 */
const confirmAddProject = () => {
  if (!projectForm.name.trim()) {
    ElMessage.warning('请输入项目名称')
    return
  }

  const projectData = {
    isCompetition: projectForm.isCompetition,
    name: projectForm.name,
    desc: projectForm.desc
  }

  if (projectForm.isEdit) {
    // 编辑模式：弹出确认弹窗
    ElMessageBox.confirm(
      '确定要保存对该项目/竞赛经历的修改吗？',
      '修改确认',
      {
        confirmButtonText: '确认修改',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
      .then(() => {
        formData.projects[projectForm.editIndex] = projectData
        showProjectDialog.value = false
        ElMessage.success('修改成功')
        // 重置编辑状态
        projectForm.isEdit = false
        projectForm.editIndex = -1
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消修改',
        })
      })
  } else {
    // 新增模式
    formData.projects.push(projectData)
    showProjectDialog.value = false
    ElMessage.success('添加成功')
  }
}

/**
 * 移除指定索引的项目经历
 * @param index - 要移除的项目索引
 */
const removeProject = (index: number) => {
  ElMessageBox.confirm(
    '确定要删除此项目/竞赛经历吗？',
    '删除确认',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      formData.projects.splice(index, 1)
      ElMessage({
        type: 'success',
        message: '已删除',
      })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除',
      })
    })
}

/** 打开实践经历弹窗（新增模式） */
const openInternshipDialog = () => {
  internshipForm.company = ''
  internshipForm.role = ''
  internshipForm.date = []
  internshipForm.desc = ''
  internshipForm.isEdit = false
  internshipForm.editIndex = -1
  showInternshipDialog.value = true
}

/** 打开实践经历弹窗（编辑模式） */
const openEditInternshipDialog = (index: number) => {
  const internship = formData.internships[index]
  if (!internship) {
    ElMessage.error('实践经历不存在')
    return
  }
  internshipForm.company = internship.company
  internshipForm.role = internship.role
  internshipForm.date = Array.isArray(internship.date)
    ? [...internship.date] as Date[]
    : []
  internshipForm.desc = internship.desc
  internshipForm.isEdit = true
  internshipForm.editIndex = index
  showInternshipDialog.value = true
}

/** 确认添加/编辑实践经历 */
const confirmAddInternship = () => {
  if (!internshipForm.company.trim()) {
    ElMessage.warning('请输入公司名称')
    return
  }
  if (!internshipForm.role.trim()) {
    ElMessage.warning('请输入担任岗位')
    return
  }

  const internshipData = {
    company: internshipForm.company,
    role: internshipForm.role,
    date: internshipForm.date,
    desc: internshipForm.desc
  }

  if (internshipForm.isEdit) {
    // 编辑模式：弹出确认弹窗
    ElMessageBox.confirm(
      '确定要保存对该实践经历的修改吗？',
      '修改确认',
      {
        confirmButtonText: '确认修改',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
      .then(() => {
        formData.internships[internshipForm.editIndex] = internshipData
        showInternshipDialog.value = false
        ElMessage.success('修改成功')
        // 重置编辑状态
        internshipForm.isEdit = false
        internshipForm.editIndex = -1
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消修改',
        })
      })
  } else {
    // 新增模式
    formData.internships.push(internshipData)
    showInternshipDialog.value = false
    ElMessage.success('添加成功')
  }
}

/**
 * 移除指定索引的实习经历
 * @param index - 要移除的实习索引
 */
const removeInternship = (index: number) => {
  ElMessageBox.confirm(
    '确定要删除此实习/工作经历吗？',
    '删除确认',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      formData.internships.splice(index, 1)
      ElMessage({
        type: 'success',
        message: '已删除',
      })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除',
      })
    })
}

/**
 * 格式化日期范围显示
 * @param dateRange - 日期范围数组 [开始日期, 结束日期]
 * @returns 格式化后的日期字符串
 */
const formatDateRange = (dateRange: Date[]) => {
  if (!dateRange || dateRange.length !== 2) return ''
  const startDate = dateRange[0]
  const endDate = dateRange[1]
  if (!startDate || !endDate) return ''
  const start = new Date(startDate)
  const end = new Date(endDate)
  const format = (date: Date) => {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    return `${y}.${m}`
  }
  return `${format(start)} - ${format(end)}`
}


/**
 * 调整职业优先级的排序
 * @param index - 当前项的索引
 * @param direction - 移动方向：-1为上移，1为下移
 */
const movePriority = (index: number, direction: number) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= formData.priorities.length) return

  const temp = formData.priorities[index]
  const target = formData.priorities[newIndex]
  if (!temp || !target) return

  formData.priorities[index] = { ...target }
  formData.priorities[newIndex] = { ...temp }
}

/**
 * 拖拽开始
 * @param index - 被拖拽项的索引
 */
const handleDragStart = (index: number) => {
  dragIndex.value = index
}

/**
 * 拖拽经过某一项
 * @param index - 被经过项的索引
 */
const handleDragOver = (e: DragEvent, index: number) => {
  e.preventDefault()
  dragOverIndex.value = index
}

/**
 * 拖拽离开
 */
const handleDragLeave = () => {
  dragOverIndex.value = -1
}

/**
 * 放置拖拽项
 * @param dropIndex - 放置位置的索引
 */
const handleDrop = (dropIndex: number) => {
  if (dragIndex.value === -1 || dragIndex.value === dropIndex) {
    dragIndex.value = -1
    dragOverIndex.value = -1
    return
  }

  // 移动数组元素
  const items = formData.priorities.splice(dragIndex.value, 1)
  if (items.length === 0 || !items[0]) return
  formData.priorities.splice(dropIndex, 0, items[0])

  dragIndex.value = -1
  dragOverIndex.value = -1
}

/**
 * 拖拽结束
 */
const handleDragEnd = () => {
  dragIndex.value = -1
  dragOverIndex.value = -1
}

/**
 * 获取优先级序号的颜色类名
 * @param index - 序号索引（0开始）
 */
const getPriorityClass = (index: number) => {
  if (index === 0) return 'priority-first'
  if (index === 1) return 'priority-second'
  return 'priority-third'
}

/**
 * 获取优先级提示文字
 * @param index - 序号索引（0开始）
 */
const getPriorityHint = (index: number) => {
  if (index === 0) return '最优先考虑'
  if (index === 1) return '次要因素'
  return '第三因素'
}


// --- 测试弹窗逻辑 ---

/**
 * 测试弹窗的状态数据
 * 用于技能测试、工具测试、代码能力测试和素质测评
 */
const testDialog = reactive({
  /** 弹窗显示状态 */
  visible: false,
  /** 弹窗标题 */
  title: '',
  /** 测试类型：skill(技能) / tool(工具) / code(代码) / communication(沟通) / stress(抗压) / learning(学习) */
  type: 'skill' as 'skill' | 'tool' | 'code' | 'communication' | 'stress' | 'learning',
  /** 当前测试项的索引 */
  currentIndex: -1,
  /** 当前测试项的名称 */
  currentName: '',
  /** 是否正在加载题目 */
  loading: false
})

/** 后端返回的问卷数据 */
const backendQuizData = ref<BackendQuizData | null>(null)


/** Quenation组件引用 */
const quenationRef = ref<InstanceType<typeof Quenation> | null>(null)

/** 导入 BackendQuizData 类型 */
interface BackendQuizData {
  tool: string
  total_questions: number
  questions: {
    id: number
    type: 'choice' | 'fill_in' | 'open_ended'
    content: string
    options: string[] | null
    correct_answer: string | null
    evaluation_criteria?: string
    difficulty: 'easy' | 'medium' | 'hard'
  }[]
}


/** 当前测试的技能/工具名称 */
const currentTestSkill = ref('')

/** 当前测试的技能/工具索引 */
const currentTestIndex = ref(-1)

/**
 * 从后端获取问卷数据
 * @param type - 测试类型
 * @param name - 技能/工具名称
 */
const fetchQuizData = async (type: string, name?: string): Promise<BackendQuizData> => {
  const params = {
    quizType: type as any,
    ...(name ? { title: name } : {})
  }
  const res = await getQuestionsApi(params)
  // 后端返回 Result<QuizResponse> 格式
  const result = res.data as any
  if (result.code !== 200) {
    throw new Error(result.msg || '获取题目失败')
  }
  return result.data
}


/**
 * 从后端获取素质测评/代码能力测评题目
 * @param type - 测评类型：code / communication / stress / learning
 */
const fetchPersonData = async (type: string): Promise<BackendQuizData> => {
  const res = await getPersonQuizApi(type)
  const result = res.data as any
  console.log('result', result)
  if (result.code !== 200) {
    throw new Error(result.msg || '获取题目失败')
  }
  const personQuestions: BackendPersonData[] = result.data || []
  // 将 BackendPersonData[] 转换为 BackendQuizData 格式，供 Quenation 组件使用
  return {
    tool: type,
    total_questions: personQuestions.length,
    questions: personQuestions.map(item => ({
      id: item.id,
      type: item.type as 'choice' | 'open_ended',
      content: item.text,
      options: item.options,
      correct_answer: null,
      evaluation_criteria: undefined,
      difficulty: 'medium' as const
    }))
  }
}


/**
 * 打开技能/工具/代码能力测试弹窗
 * 使用Quenation组件展示完整问卷
 * @param type - 测试类型：skill(技能) / tool(工具) / code(代码)
 * @param index - 可选，测试项的索引
 */
const openTestModal = async (type: 'skill' | 'tool', index?: number) => {
  // 保存当前测试的技能信息
  let name = ''
  if (type === 'skill' && index !== undefined) {
    name = formData.skills[index]?.name || ''
    currentTestSkill.value = name
    currentTestIndex.value = index
    testDialog.title = `${name} 技能测试`

  } else if (type === 'tool' && index !== undefined) {
    name = formData.tools[index]?.name || ''
    currentTestSkill.value = name
    currentTestIndex.value = index
    testDialog.title = `${name} 工具测试`
  }

  testDialog.type = type
  testDialog.currentIndex = index ?? -1
  testDialog.loading = true
  testDialog.visible = true
  backendQuizData.value = null


  console.log("类型", type)
  console.log("名称", name)

  try {
    // 从后端获取题目数据
    const quizData = await fetchQuizData(type, name)
    backendQuizData.value = quizData
  } catch (error) {
    console.error('获取题目失败:', error)
    ElMessage.error('获取题目失败，请稍后重试')
    testDialog.visible = false
  } finally {
    testDialog.loading = false
  }
}


/**
 * 打开素质测评弹窗
 * 使用Quenation组件展示完整问卷
 * @param type - 测评类型：communication(沟通) / stress(抗压) / learning(学习)
 */
const openQuizModal = async (type: 'code' | 'communication' | 'stress' | 'learning') => {
  currentQuizType.value = type
  testDialog.type = type

  console.log('类别', type)

  // 测评标题映射
  const titles: Record<string, string> = {
    'code': '代码能力测评',
    'communication': '沟通能力测评',
    'stress': '抗压能力测评',
    'learning': '学习能力测评'
  }

  testDialog.title = titles[type] || '素质测评'
  testDialog.currentIndex = -1
  testDialog.loading = true
  testDialog.visible = true
  backendQuizData.value = null



  try {
    // 从后端获取题目数据（openQuizModal的类型不需要name参数）
    const quizData = await fetchPersonData(type)
    console.log("quizData", quizData)
    backendQuizData.value = quizData
  } catch (error) {
    console.error('获取题目失败:', error)
    ElMessage.error('获取题目失败，请稍后重试')
    testDialog.visible = false
  } finally {
    testDialog.loading = false
  }
}


/**
 * 问答题评分结果（提交后展示在弹窗中）
 */
const quizResult = ref<{
  totalScore: number
  totalMaxScore: number
  openEndedDetails: {
    score: number
    max_score: number
    score_details: Array<{
      point: string
      max_point_score: number
      earned_score: number
      reason: string
    }>
    comment: string
    suggestions: string
  }
} | null>(null)

/** 后端评分是否失败 */
const scoreFailed = ref(false)
const quizSubmitting = ref(false)

/**
 * 处理问卷提交完成
 * 根据测试类型更新相应的分数或完成状态
 * @param submitData - 问卷提交的数据 { quizType, answers }
 */
const handleQuizSubmit = async (submitData: any) => {
  const { quizType, answers } = submitData

  // ---- 素质测评（communication / stress / learning）：不做评分，直接收集答案 ----
  if (['communication', 'stress', 'learning'].includes(quizType)) {
    const questions = backendQuizData.value?.questions || []
    const detailItems: QuizDetailItem[] = []

    questions.forEach(q => {
      const key = `q_${q.id}`
      const rawAnswer = answers?.[key] || ''

      // 选择题：将选项字母(如"A")还原为完整选项文本
      let displayAnswer = rawAnswer
      if (q.type === 'choice' && q.options && rawAnswer) {
        const matched = q.options.find(opt =>
          opt.startsWith(`${rawAnswer}.`) ||
          opt.startsWith(`${rawAnswer}、`) ||
          opt.startsWith(`${rawAnswer})`)
        )
        if (matched) {
          displayAnswer = matched.replace(/^[A-Za-z][.．、)\s]+/, '').trim()
        }
      }

      detailItems.push({
        type: q.type as 'choice' | 'open_ended',
        question: q.content,
        answer: displayAnswer
      })
    })


    // 追加到 quizDetail
    formData.quizDetail.push(...detailItems)

    // 标记完成
    quizCompleted[quizType as 'communication' | 'stress' | 'learning'] = true
    currentQuizType.value = ''

    ElMessage.success(`${getQuizTypeName(quizType)}测评完成！`)
    closeTestDialog()
    return
  }

  // ---- 技能/工具/代码测试：走原有评分流程 ----
  const userAnswers: Record<number, string> = {}
  Object.entries(answers || {}).forEach(([key, value]) => {
    const match = key.match(/q_(\d+)/)
    if (match && match[1]) userAnswers[parseInt(match[1])] = value as string
  })

  try {
    if (['skill', 'tool'].includes(quizType)) {
      quizSubmitting.value = true
    }

    const result = await submitQuiz({
      quizType,
      name: ['skill', 'tool'].includes(quizType) ? currentTestSkill.value || '' : undefined,
      questions: (backendQuizData.value?.questions || []) as Question[],
      userAnswers
    })

    scoreFailed.value = false

    // 更新分数
    updateQuizScore(quizType, result.totalScore)

    // quizResult 传入 Quenation 组件，watch 会自动切换到结果页面
    quizResult.value = {
      totalScore: result.totalScore,
      totalMaxScore: result.totalMaxScore,
      openEndedDetails: result.openEndedDetails
    }

    ElMessage.success(`${getQuizTypeName(quizType)}完成！得分：${result.totalScore}分，请查看答题结果`)
  } catch (error) {
    console.error('提交问卷失败:', error)
    scoreFailed.value = true
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    quizSubmitting.value = false
  }
}

/**
 * 更新测试分数到表单数据
 */
const updateQuizScore = (quizType: string, score: number) => {
  const index = currentTestIndex.value

  if (quizType === 'skill' && index >= 0 && formData.skills[index]) {
    formData.skills[index].score = score
  } else if (quizType === 'tool' && index >= 0 && formData.tools[index]) {
    formData.tools[index].score = score
  }
}

/**
 * 获取测试类型名称
 */
const getQuizTypeName = (quizType: string): string => {
  const names: Record<string, string> = {
    'skill': currentTestSkill.value || '技能',
    'tool': currentTestSkill.value || '工具',
    'code': '代码能力',
    'communication': '沟通能力',
    'stress': '抗压能力',
    'learning': '学习能力'
  }
  return names[quizType] || quizType
}

/**
 * 根据得分比例返回颜色
 */
const getScoreColor = (score: number, maxScore: number): string => {
  const ratio = score / maxScore
  if (ratio >= 0.8) return '#67c23a'
  if (ratio >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const getCodeAbilityUrls = (rawLinks: string) => {
  return rawLinks
    .split(/[\n,，]/)
    .map(item => item.trim())
    .filter(Boolean)
}

const isValidCodeRepoUrl = (url: string) => {
  return /^https?:\/\/(www\.)?(github\.com|gitee\.com)\/[^/]+\/[^/]+\/?$/i.test(url)
}

const getCodeRepoMeta = (url: string) => {
  const normalized = url.trim().replace(/\/+$/, '')
  const match = normalized.match(/^https?:\/\/(?:www\.)?(github\.com|gitee\.com)\/([^/]+)\/([^/]+)$/i)

  if (!match) {
    return {
      hostLabel: '未知平台',
      owner: '',
      repo: '',
      fullName: '',
      normalized
    }
  }

  const matchResult = match as RegExpMatchArray
  const [, host, owner, repo] = matchResult

  return {
    hostLabel: host?.toLowerCase() === 'gitee.com' ? 'Gitee' : 'GitHub',
    owner: owner || '',
    repo: repo || '',
    fullName: `${owner || ''}/${repo || ''}`,
    normalized
  }
}

const getRepoDisplayNames = (urls: string[]) => {
  return urls.map((url) => {
    const meta = getCodeRepoMeta(url)
    return meta.fullName || meta.normalized || url
  })
}

const getCodeAbilityResultModeText = () => {
  return codeAbilityResult.value?.ai_analysis ? '深度分析结果' : '基础评估'
}

const getCodeAbilityResultModeTagType = () => {
  return codeAbilityResult.value?.ai_analysis ? 'warning' : 'info'
}

const getCodeAbilityTagType = (score?: number) => {
  if ((score ?? 0) >= 85) return 'success'
  if ((score ?? 0) >= 70) return 'warning'
  return 'danger'
}

const showCodeAbilityResultDialog = () => {
  if (!codeAbilityResult.value) {
    ElMessage.warning('请先完成代码能力评估')
    return
  }
  codeAbilityResultVisible.value = true
}

const handleCodeAbilityEvaluate = async (options?: {
  rawLinks?: string
  useAi?: boolean
  openResultDialog?: boolean
}) => {
  const rawLinks = (options?.rawLinks ?? formData.codeAbility.links).trim()
  const useAi = options?.useAi ?? codeAbilityUseAi.value
  const openResultDialog = options?.openResultDialog ?? true
  const repoUrls = getCodeAbilityUrls(rawLinks)

  if (!repoUrls.length) {
    ElMessage.warning('请输入至少一个 GitHub 或 Gitee 仓库链接')
    return
  }

  const invalidUrl = repoUrls.find(url => !isValidCodeRepoUrl(url))
  if (invalidUrl) {
    ElMessage.warning(`存在无效仓库链接：${invalidUrl}`)
    return
  }

  codeAbilityEvaluating.value = true
  lastEvaluatedCodeRepoUrls.value = repoUrls

  try {
    const res = await evaluateCodeAbilityApi({
      urls: repoUrls,
      use_ai: useAi
    })
    const result = res.data as any

    if (result?.code !== 200 || !result?.data) {
      throw new Error(result?.msg || '代码能力评估失败')
    }

    codeAbilityResult.value = result.data
    codeAbilityUseAi.value = useAi
    if (openResultDialog) {
      codeAbilityResultVisible.value = true
    }

    ElMessage.success(result.data?.ai_analysis ? '代码能力深度分析完成' : '代码能力评估完成')
  } catch (error: any) {
    console.error('代码能力评估失败:', error)
    ElMessage.error(error?.message || '代码能力评估失败，请稍后重试')
  } finally {
    codeAbilityEvaluating.value = false
  }
}

/**
 * 关闭测试弹窗
 */
const closeTestDialog = () => {
  testDialog.visible = false
  currentTestSkill.value = ''
  currentTestIndex.value = -1
  currentQuizType.value = ''
  quizResult.value = null
  scoreFailed.value = false
  quizSubmitting.value = false
  backendQuizData.value = null
  // 重置Quenation组件
  quenationRef.value?.reset()
}


// --- 必填字段配置 ---

/**
 * 必填字段配置
 * 定义哪些字段是必填项以及如何验证
 */
const requiredFields: Array<{ field: MissingFieldKey; label: string; step: string; validate: (value: any) => boolean }> = [
  { field: 'education', label: '学历', step: '1', validate: (v: any) => !!v },
  { field: 'major', label: '专业', step: '1', validate: (v: any) => Array.isArray(v) && v.length > 0 },
  { field: 'graduationDate', label: '预计毕业日期', step: '1', validate: (v: any) => !!v },
  { field: 'languages', label: '外语能力', step: '2', validate: (v: any) => hasValidLanguage(v) },
  { field: 'skills', label: '专业技能', step: '2', validate: (v: any) => Array.isArray(v) && v.length > 0 },
  { field: 'qualityAssessment', label: '素质测评', step: '4', validate: () => quizCompleted.communication && quizCompleted.stress && quizCompleted.learning },
  { field: 'targetJob', label: '目标岗位', step: '5', validate: (v: any) => !!v },
  { field: 'targetIndustries', label: '期望行业', step: '5', validate: (v: any) => Array.isArray(v) && v.length > 0 }
]

/**
 * 检查必填字段，返回缺失的字段列表
 * @returns 缺失的字段配置数组
 */
const checkRequiredFields = () => {
  return requiredFields.filter((item) => {
    if (item.field === 'qualityAssessment') {
      return !item.validate(undefined)
    }
    return !item.validate(formData[item.field as keyof CareerFormData])
  })
}

const mapPendingMissingFields = (missingFields: typeof requiredFields): ResumeChatField[] => {
  return missingFields.map((field) => ({
    field: field.field,
    label: field.label,
    step: field.step
  }))
}

const getOptionalResumeChatFields = (): ResumeChatField[] => {
  if (formData.codeAbility.links.trim()) {
    return []
  }

  return [{
    field: 'codeAbility',
    label: '代码能力',
    step: '2',
    optional: true
  }]
}

const syncPendingMissingFields = () => {
  pendingMissingFields.value = [
    ...mapPendingMissingFields(checkRequiredFields()),
    ...getOptionalResumeChatFields()
  ]
}

const missingFieldCount = computed(() => checkRequiredFields().length)
const showResumeContinueButton = computed(() => hasUploadedResume.value && missingFieldCount.value > 0)

/**
 * 显示缺失字段提醒，引导用户补充
 * @param missingFields 缺失的字段列表
 */
const showMissingFieldsReminder = (missingFields: typeof requiredFields) => {
  const chatFields = [
    ...mapPendingMissingFields(missingFields),
    ...getOptionalResumeChatFields()
  ]

  if (chatFields.length === 0) {
    pendingMissingFields.value = []
    ElMessage.success('简历信息已完整填充，可以直接提交！')
    return
  }
  pendingMissingFields.value = chatFields
  switchCareerSection('resume')
  activeMenu.value = pendingMissingFields.value[0]?.step || '1'
  showMissingFieldsChat.value = true
}

const reopenMissingFieldsChat = () => {
  syncPendingMissingFields()

  if (pendingMissingFields.value.length === 0) {
    ElMessage.success('待补充信息已完成，无需继续补全')
    return
  }

  switchCareerSection('resume')
  activeMenu.value = pendingMissingFields.value[0]?.step || activeMenu.value
  showMissingFieldsChat.value = true
}

const handleMissingFieldSave = (payload: { field: string; value: unknown }) => {
  switch (payload.field) {
    case 'education':
      formData.education = String(payload.value || '')
      showEducationInput.value = formData.education === '其他'
      if (formData.education !== '其他') {
        formData.educationOther = ''
      }
      break
    case 'major':
      formData.major = Array.isArray(payload.value)
        ? payload.value.map((item) => String(item))
        : []
      break
    case 'graduationDate':
      formData.graduationDate = String(payload.value || '')
      break
    case 'languages':
      formData.languages = Array.isArray(payload.value)
        ? payload.value as CareerFormData['languages']
        : [{ type: '', level: '', other: '' }]
      break
    case 'skills':
      formData.skills = Array.isArray(payload.value)
        ? payload.value as CareerFormData['skills']
        : []
      break
    case 'targetJob':
      formData.targetJob = String(payload.value || '')
      break
    case 'targetIndustries':
      formData.targetIndustries = Array.isArray(payload.value)
        ? payload.value.map((item) => String(item))
        : []
      break
    case 'codeAbility': {
      const value = payload.value as { links?: string; useAi?: boolean } | null
      formData.codeAbility.links = String(value?.links || '')
      codeAbilityUseAi.value = !!value?.useAi
      break
    }
  }
}

const handleMissingFieldCodeAbilityEvaluate = async (payload: { links: string; useAi: boolean }) => {
  formData.codeAbility.links = payload.links
  codeAbilityUseAi.value = payload.useAi
  await handleCodeAbilityEvaluate({
    rawLinks: payload.links,
    useAi: payload.useAi,
    openResultDialog: true
  })
}

const handleMissingFieldComplete = () => {
  syncPendingMissingFields()

  if (pendingMissingFields.value.length === 0) {
    ElMessage.success('必填信息已补充完成，可以继续完善其他内容或直接提交')
    return
  }

  ElMessage.info(`还剩 ${pendingMissingFields.value.length} 项待补充，可继续在表单中完善`)
}

const findMajorPath = (options: typeof majorOptions, target: string): string[] | null => {
  for (const option of options) {
    if (option.value === target || option.label === target) {
      return [option.value]
    }

    if (option.children?.length) {
      for (const child of option.children) {
        if (child.value === target || child.label === target) {
          return [option.value, child.value]
        }
      }
    }
  }

  return null
}

const normalizeMajorValue = (major: unknown): string[] => {
  if (Array.isArray(major)) {
    if (major.length >= 2) {
      return major.map((item) => String(item))
    }

    if (major.length === 1) {
      const matchPath = findMajorPath(majorOptions, String(major[0]))
      return matchPath || [String(major[0])]
    }
  }

  if (typeof major === 'string' && major.trim()) {
    const normalized = major.trim()

    if (normalized.includes('/')) {
      return normalized.split('/').map((item) => item.trim()).filter(Boolean)
    }

    if (normalized.includes('／')) {
      return normalized.split('／').map((item) => item.trim()).filter(Boolean)
    }

    const matchPath = findMajorPath(majorOptions, normalized)
    return matchPath || [normalized]
  }

  return []
}

/**
 * 将后端返回的表单数据填充到前端表单
 * @param parsedFormData 后端返回的解析后的表单数据
 */
const fillFormWithParsedData = (parsedFormData: any) => {
  if (!parsedFormData) return

  // 填充学历
  if (parsedFormData.education) {
    formData.education = parsedFormData.education
    if (parsedFormData.education === '其他' && parsedFormData.educationOther) {
      formData.educationOther = parsedFormData.educationOther
      showEducationInput.value = true
    }
  }

  // 填充专业
  if (parsedFormData.major) {
    formData.major = normalizeMajorValue(parsedFormData.major)
  }

  // 填充毕业日期
  if (parsedFormData.graduationDate) {
    formData.graduationDate = parsedFormData.graduationDate
  }

  // 填充语言能力
  if (parsedFormData.languages && Array.isArray(parsedFormData.languages) && parsedFormData.languages.length > 0) {
    formData.languages = parsedFormData.languages.map((l: any) => ({
      type: l.type || '',
      level: l.level || '',
      other: l.other || ''
    }))
  }

  // 填充证书
  if (parsedFormData.certificates && Array.isArray(parsedFormData.certificates)) {
    formData.certificates = parsedFormData.certificates
    if (parsedFormData.certificates.includes('其他') && parsedFormData.certificateOther) {
      formData.certificateOther = parsedFormData.certificateOther
      showCertificateInput.value = true
    }
  }

  // 填充技能
  if (parsedFormData.skills && Array.isArray(parsedFormData.skills)) {
    formData.skills = parsedFormData.skills.map((s: any) => ({
      name: s.name || s,
      score: s.score ?? s.credibility ?? 70
    }))
  }

  // 填充工具
  if (parsedFormData.tools && Array.isArray(parsedFormData.tools)) {
    const proficiencyMap: Record<string, number> = { '了解': 25, '熟练': 50, '精通': 75 }
    formData.tools = parsedFormData.tools.map((t: any) => ({
      name: t.name || t,
      score: t.score ?? (t.proficiency ? proficiencyMap[t.proficiency] : undefined) ?? 50
    }))
  }

  // 填充代码能力
  if (parsedFormData.codeAbility?.links || parsedFormData.codeLinks) {
    const parsedCodeLinks = parsedFormData.codeAbility?.links || parsedFormData.codeLinks || ''
    formData.codeAbility.links = Array.isArray(parsedCodeLinks)
      ? parsedCodeLinks.join('\n')
      : String(parsedCodeLinks)
  }

  // 填充项目经历
  if (parsedFormData.projects && Array.isArray(parsedFormData.projects)) {
    formData.projects = parsedFormData.projects.map((p: any) => ({
      isCompetition: p.isCompetition || false,
      name: p.name || '',
      desc: p.desc || ''
    }))
  }

  // 填充实习经历
  if (parsedFormData.internships && Array.isArray(parsedFormData.internships)) {
    formData.internships = parsedFormData.internships.map((i: any) => ({
      company: i.company || '',
      role: i.role || '',
      date: i.date || [],
      desc: i.desc || ''
    }))
  }

  // 填充素质测评答题记录，并根据记录判断完成状态
  if (parsedFormData.quizDetail && Array.isArray(parsedFormData.quizDetail)) {
    formData.quizDetail = parsedFormData.quizDetail
    // 有答题记录即标记全部素质测评已完成
    if (parsedFormData.quizDetail.length > 0) {
      quizCompleted.communication = true
      quizCompleted.stress = true
      quizCompleted.learning = true
    }
  }

  // 填充创新案例
  if (parsedFormData.innovation) {
    formData.innovation = parsedFormData.innovation
  }

  // 填充目标岗位
  if (parsedFormData.targetJob) {
    formData.targetJob = parsedFormData.targetJob
  }

  // 填充目标行业
  if (parsedFormData.targetIndustries && Array.isArray(parsedFormData.targetIndustries)) {
    formData.targetIndustries = parsedFormData.targetIndustries
  }

  // 填充职业优先级
  if (parsedFormData.priorities && Array.isArray(parsedFormData.priorities) && parsedFormData.priorities.length > 0) {
    formData.priorities = parsedFormData.priorities.map((p: any) => ({
      value: p.value || 'tech',
      label: p.label || '技术成长'
    }))
  }
}

/**
 * 处理简历解析完成后的数据
 * 直接将返回的表单数据填充到表单中，检测缺失字段并提醒用户
 * @param parsedData - 简历解析后的表单数据对象（直接是 CareerFormData 格式）
 */
const handleResumeParsed = (parsedData: unknown) => {
  hasUploadedResume.value = true
  showUploadDialog.value = false

  const formDataFromResume = parsedData as Record<string, unknown> | null
  if (!formDataFromResume) {
    ElMessage.warning('简历解析结果为空，请手动填写表单')
    return
  }

  fillFormWithParsedData(formDataFromResume)
  ElMessage.success('简历解析成功！已自动填充表单信息')

  // 检查并提示缺失的必填字段
  const missingFields = checkRequiredFields()
  const optionalFields = getOptionalResumeChatFields()
  if (missingFields.length > 0 || optionalFields.length > 0) {
    if (missingFields.length > 0) {
      ElMessage.warning(`识别完成，但还有 ${missingFields.length} 项必填信息待补充`)
    } else {
      ElMessage.info('识别完成，你还可以继续补充可选的代码能力信息')
    }
    setTimeout(() => showMissingFieldsReminder(missingFields), 300)
  }
}

const hydrateCareerFormFromStorage = () => {
  const cachedFormData = loadCareerFormData()
  if (!cachedFormData) return
  fillFormWithParsedData(cachedFormData)
}

onMounted(() => {
  hydrateCareerFormFromStorage()
})

watch(
  formData,
  () => {
    saveCareerFormData(formData)
  },
  { deep: true }
)

// --- 岗位联想搜索 ---

/**
 * 目标岗位输入框的联想搜索回调
 * 根据输入内容返回匹配的岗位建议
 * @param queryString - 用户输入的搜索关键字
 * @param cb - 回调函数，用于返回搜索结果
 */
interface SearchSuggestion {
  value: string
}

const querySearch = (queryString: string, cb: (results: SearchSuggestion[]) => void) => {
  const jobOptions = ['后端工程师', '前端开发', '后端运维工程师', '产品经理']
  const results = queryString
    ? jobOptions.filter(i => i.includes(queryString))
    : []
  cb(results.map(i => ({ value: i })))
}


// --- 表单验证与提交 ---

/**
 * 表单验证规则
 * 定义各字段的必填验证和触发时机
 */
const formRules = reactive<FormRules>({
  /** 学历：必填，变更时触发验证 */
  education: [{ required: true, message: '请选择学历', trigger: 'change' }],
  /** 专业：必填，变更时触发验证 */
  major: [{ required: true, message: '请选择专业', trigger: 'change' }],
  /** 外语水平：必填，自定义验证 */
  languages: [{
    required: true,
    validator: (_rule, value: Array<{ type: string; level: string }>, callback) => {
      if (!hasValidLanguage(value)) {
        callback(new Error('请至少填写一项外语水平'))
      } else {
        callback()
      }
    },
    trigger: 'change'
  }],
  /** 技能：必填，变更时触发验证 */
  skills: [{ required: true, message: '请至少添加一项技能', trigger: 'change' }],
  /** 目标岗位：必填，失焦时触发验证 */
  targetJob: [{ required: true, message: '请输入目标岗位', trigger: 'blur' }],
  /** 创新案例：必填，失焦时触发验证 */
  innovation: [{ required: true, message: '请填写创新案例', trigger: 'blur' }]
})


/**
 * 获取模拟人岗匹配结果
 */
const fetchMockJobMatchResult = async (): Promise<JobMatchItem[]> => {
  const { mockJobMatchItems } = await import('@/mock/mockdata/JobMatch_mockdata')
  return mockJobMatchItems
}

/** 当前生成的 JSON Resume。 */
const currentJsonResume = computed(() => jsonResumeResult.value?.resume ?? null)
const currentResumeTemplateLabel = computed(() => {
  const mapping = {
    professional: '专业模板',
    modern: '现代模板',
    compact: '紧凑模板'
  } satisfies Record<typeof selectedResumeTemplate.value, string>

  return mapping[selectedResumeTemplate.value]
})

/** 当前简历缺失的必填项 - 直接从表单数据计算，实时反映填写情况。 */
const resumeMissingRequiredFields = computed(() => {
  const missing: { field: string; label: string }[] = []

  // 从 resumeProfileExtras.basics 检查基本信息
  const basics = resumeProfileExtras.value.basics
  if (!basics.name?.trim()) missing.push({ field: 'basics.name', label: '姓名' })
  if (!basics.phone?.trim()) missing.push({ field: 'basics.phone', label: '手机' })
  if (!basics.email?.trim()) missing.push({ field: 'basics.email', label: '邮箱' })

  // 从 resumeProfileExtras.educationHistory 检查教育信息
  const education = resumeProfileExtras.value.educationHistory?.[0]
  if (!education?.institution?.trim()) missing.push({ field: 'education.institution', label: '学校' })
  if (!education?.studyType?.trim()) missing.push({ field: 'education.studyType', label: '学历' })

  // 从 formData 检查技能和求职意向
  if (formData.skills.length === 0) missing.push({ field: 'skills', label: '专业技能' })
  if (!formData.targetJob?.trim()) missing.push({ field: 'targetJob', label: '目标岗位' })

  // 检查项目/经历（建议至少有一个）
  if (formData.projects.length === 0 && formData.internships.length === 0) {
    missing.push({ field: 'experience', label: '项目或实习经历' })
  }

  return missing
})

/** 简历内容完整度评分 - 直接从表单数据计算（0-100）。 */
const resumeCompletenessScore = computed(() => {
  let score = 0
  const basics = resumeProfileExtras.value.basics
  const education = resumeProfileExtras.value.educationHistory?.[0]

  // 基本信息（35分）：姓名、手机、邮箱、求职意向
  if (basics.name?.trim()) score += 10
  if (basics.phone?.trim()) score += 8
  if (basics.email?.trim()) score += 7
  if (basics.label?.trim() || formData.targetJob?.trim()) score += 10

  // 教育信息（20分）：学校、学历、专业
  if (education?.institution?.trim()) score += 8
  if (education?.studyType?.trim()) score += 7
  if (education?.area?.trim()) score += 5

  // 技能（15分）
  if (formData.skills.length > 0) {
    score += Math.min(15, formData.skills.length * 5)
  }

  // 经历/项目（20分）
  const expCount = formData.projects.length + formData.internships.length
  if (expCount > 0) {
    score += Math.min(20, expCount * 10)
  }

  // 其他信息（10分）：证书、语言、工具
  if (formData.certificates.length > 0) score += 4
  if (formData.languages.some(l => l.type && l.level)) score += 3
  if (formData.tools.length > 0) score += 3

  return Math.min(100, score)
})

/** 简历结构是否有效 - 检查必填项是否满足基本要求。 */
const resumeStructureValid = computed(() => {
  const basics = resumeProfileExtras.value.basics
  const education = resumeProfileExtras.value.educationHistory?.[0]

  // 基本结构有效：姓名 + 手机/邮箱 + 学校 + 学历
  const hasBasicInfo = !!basics.name?.trim()
  const hasContact = !!basics.phone?.trim() || !!basics.email?.trim()
  const hasEducation = !!education?.institution?.trim() && !!education?.studyType?.trim()

  return hasBasicInfo && hasContact && hasEducation
})

const resumePrimaryEducation = computed(() => currentJsonResume.value?.education?.[0] ?? null)

const resumeProfessionalFacts = computed(() => {
  if (!currentJsonResume.value) {
    return []
  }

  const basics = currentJsonResume.value.basics
  const education = resumePrimaryEducation.value

  return [
    { label: '姓名', value: basics.name },
    { label: '手机', value: basics.phone },
    { label: '邮箱', value: basics.email },
    { label: '学历', value: education?.studyType },
    { label: '求职意向', value: formData.targetJob.trim() || basics.label },
    {
      label: '地址',
      value: [basics.location?.city, basics.location?.region].filter(Boolean).join(' / ')
    }
  ].filter(item => item.value)
})

const formatResumeDisplayDate = (value?: string) => {
  if (!value) return ''

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return value.slice(0, 7).replace('-', '.')
  }

  if (/^\d{4}-\d{2}$/.test(value)) {
    return value.replace('-', '.')
  }

  return value
}

const formatResumeDisplayRange = (startDate?: string, endDate?: string, withPresent = false) => {
  const start = formatResumeDisplayDate(startDate)
  const end = formatResumeDisplayDate(endDate)

  if (start && end) {
    return `${start}-${end}`
  }

  if (start && withPresent) {
    return `${start}-至今`
  }

  return start || end || ''
}

/** 当前编辑中的教育补充记录。 */
const primaryResumeEducation = computed(() => {
  ensureResumeEducationHistory()
  return resumeProfileExtras.value.educationHistory![0]!
})

/** 确保扩展资料中的教育经历至少存在一项。 */
const ensureResumeEducationHistory = () => {
  if (!resumeProfileExtras.value.educationHistory?.length) {
    resumeProfileExtras.value.educationHistory = [
      {
        institution: '',
        area: '',
        studyType: '',
        startDate: '',
        endDate: ''
      }
    ]
  }

  return resumeProfileExtras.value.educationHistory![0]!
}

const syncResumeProfileExtrasFromForm = () => {
  const firstEducation = ensureResumeEducationHistory()

  if (!resumeProfileExtras.value.basics.label?.trim() && formData.targetJob.trim()) {
    resumeProfileExtras.value.basics.label = formData.targetJob.trim()
  }
  if (!firstEducation.area?.toString().trim() && formData.major.length) {
    firstEducation.area = formData.major.join(' / ')
  }
  if (!firstEducation.studyType?.toString().trim() && formData.education) {
    firstEducation.studyType = formData.education === '其他'
      ? formData.educationOther
      : formData.education
  }
  if (!firstEducation.endDate?.toString().trim() && formData.graduationDate) {
    firstEducation.endDate = formData.graduationDate
  }
}

/** 打开简历补充资料弹窗，并按当前表单默认补齐部分字段。 */
const openResumeProfileDialog = () => {
  syncResumeProfileExtrasFromForm()
  resumeProfileDialogVisible.value = true
}

const syncResumeTemplateFromProfile = () => {
  syncResumeProfileExtrasFromForm()
  jsonResumeStore.setProfileExtras(cloneDeep(resumeProfileExtras.value))
  ElMessage.success('已同步“我的简历”信息，现在可以直接选择模板并预览简历')
}

/** 打开模板选择弹窗。 */
const openResumeTemplateDialog = () => {
  resumeTemplateDialogVisible.value = true
}

/** 选择简历模板。 */
const selectResumeTemplate = (template: 'professional' | 'modern' | 'compact') => {
  selectedResumeTemplate.value = template
}

/** 校验生成 JSON Resume 前的关键附加资料。 */
const validateResumeEducationDates = () => {
  const education = ensureResumeEducationHistory()
  const startDate = education.startDate?.toString().trim()
  const endDate = education.endDate?.toString().trim()

  if (startDate && endDate && startDate > endDate) {
    ElMessage.warning('教育经历的入学时间不能晚于毕业时间')
    resumeProfileDialogVisible.value = true
    return false
  }

  return true
}

/** 保存简历补充资料弹窗。 */
const saveResumeProfileDialog = () => {
  if (!validateResumeEducationDates()) {
    return
  }

  resumeProfileDialogVisible.value = false
  ElMessage.success('简历补充资料已保存')
}

/** 校验生成 JSON Resume 前的关键附加资料。 */
const validateResumeProfileExtras = () => {
  const basics = resumeProfileExtras.value.basics
  const education = ensureResumeEducationHistory()

  if (!basics.name.trim()) {
    ElMessage.warning('请先补充简历姓名')
    resumeProfileDialogVisible.value = true
    return false
  }

  if (!education.institution?.toString().trim()) {
    ElMessage.warning('请先补充学校名称')
    resumeProfileDialogVisible.value = true
    return false
  }

  if (!validateResumeEducationDates()) {
    return false
  }

  return true
}

/** 基于当前表单构建 JSON Resume。 */
const buildJsonResumeFromForm = async () => {
  if (!formRef.value) return null

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    ElMessage.error('请先完善职业画像表单中的必填信息')
    return null
  }

  if (!validateResumeProfileExtras()) {
    return null
  }

  resumeGenerating.value = true

  try {
    jsonResumeStore.setProfileExtras(cloneDeep(resumeProfileExtras.value))
    const result = generateJsonResume({
      careerFormData: cloneDeep(formData),
      profileExtras: cloneDeep(resumeProfileExtras.value)
    })

    jsonResumeResult.value = result
    return result
  } finally {
    resumeGenerating.value = false
  }
}

/** 生成并打开简历预览。 */
const generateResumePreview = async () => {
  const result = await buildJsonResumeFromForm()
  if (!result) {
    return
  }

  resumePreviewDialogVisible.value = true

  if (!result.valid) {
    ElMessage.warning('JSON Resume 已生成，但存在结构校验提醒，请检查后再导出')
    return
  }

  if (result.completeness.missingRequiredFields.length) {
    ElMessage.warning('JSON Resume 已生成，但仍有必填信息缺失')
    return
  }

  ElMessage.success('JSON Resume 已生成，可直接预览和导出')
}

/** 导出 PDF。 */
const exportResumePdf = async () => {
  if (!currentJsonResume.value || !resumePreviewRef.value) {
    ElMessage.warning('请先生成并打开简历预览')
    return
  }

  resumeExportingPdf.value = true

  try {
    await nextTick()
    await exportResumePreviewToPdf(resumePreviewRef.value, {
      fileName: 'resume.pdf'
    })
    ElMessage.success('PDF 已导出')
  } catch (error) {
    console.error('导出 PDF 失败:', error)
    ElMessage.error('导出 PDF 失败，请稍后重试')
  } finally {
    resumeExportingPdf.value = false
  }
}

/** 导出 Word。 */
const exportResumeWord = async () => {
  if (!currentJsonResume.value) {
    ElMessage.warning('请先生成简历')
    return
  }

  resumeExportingWord.value = true

  try {
    await exportJsonResumeToWord(currentJsonResume.value, {
      fileName: 'resume.docx'
    })
    ElMessage.success('Word 已导出')
  } catch (error) {
    console.error('导出 Word 失败:', error)
    ElMessage.error('导出 Word 失败，请稍后重试')
  } finally {
    resumeExportingWord.value = false
  }
}

/**
 * 提交表单
 * 验证表单数据，提交到后端并等待返回能力评估报告
 */
const submitForm = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    ElMessage.error('请完善必填信息')
    return
  }

  submitting.value = true
  try {
    const submitData = convertToSubmitDTO(formData, {
      codeAbilityResult: codeAbilityResult.value,
      codeAbilityUseAi: codeAbilityUseAi.value
    })
    console.log('submitData', submitData)
    const res = await submitCareerFormApi(submitData)

    console.log("表单提交返回结果:", res)
    console.log("res.data:", res.data)
    console.log("res.data.data:", res.data.data)

    // 处理两种响应格式：1) res.data 是数组 2) res.data 是 {code, data} 对象
    let matchResult: JobMatchItem[]
    if (Array.isArray(res.data)) {
      matchResult = res.data as JobMatchItem[]
    } else if (res.data?.code === 200) {
      matchResult = res.data.data as JobMatchItem[]
    } else {
      ElMessage.error(res.data?.msg || '提交失败，请稍后重试')
      return
    }
    localStorage.setItem('jobMatchResult', JSON.stringify(matchResult))
    ElMessage.success('人岗匹配分析完成！')
    router.push('/job-matching')
  } catch (error: any) {
    console.error('提交失败:', error)
    ElMessage.error(error.message || '网络错误，请稍后重试')
  } finally {
    submitting.value = false
  }
}

/**
 * 使用模拟数据生成人岗匹配结果（调试/预览模式）
 * 当后端服务不可用时，可调用此方法使用前端模拟数据
 */
const submitFormWithMockData = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请完善必填信息')
      return
    }

    submitting.value = true

    try {
      // 使用模拟数据生成人岗匹配结果
      const mockResult = await fetchMockJobMatchResult()

      // 保存人岗匹配结果到本地存储
      localStorage.setItem('jobMatchResult', JSON.stringify(mockResult))

      console.log('【模拟模式】人岗匹配结果:', mockResult)
      ElMessage.success('人岗匹配分析完成，正在跳转...')

      // 直接跳转到人岗匹配页面
      router.push('/job-matching')
    } catch (error) {
      console.error('生成模拟人岗匹配失败:', error)
      ElMessage.error('生成报告失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 重置表单
 * 清空所有表单数据并恢复初始状态
 */
const resetForm = () => {
  if (!formRef.value) return

  // 重置 Element Plus 表单组件的字段
  formRef.value.resetFields()

  // 手动重置动态列表数据（resetFields 无法处理动态添加的数组项）
  formData.languages = [{ type: '', level: '', other: '' }]
  formData.certificates = []
  formData.certificateOther = ''
  formData.skills = []
  formData.tools = []
  formData.projects = []
  formData.internships = []
  formData.quizDetail = []
  quizCompleted.communication = false
  quizCompleted.stress = false
  quizCompleted.learning = false
  formData.priorities = [
    { value: 'tech', label: '技术成长' },
    { value: 'salary', label: '薪资' },
    { value: 'stable', label: '稳定' }
  ]

  // 重置临时输入值
  newSkill.value = ''
  newTool.value = ''

  // 重置显示状态
  showEducationInput.value = false
  showCertificateInput.value = false
  hasUploadedResume.value = false

  // 重置测试相关状态
  currentTestSkill.value = ''
  currentTestIndex.value = -1
  currentQuizType.value = ''

  // 重置当前步骤到第一步
  activeMenu.value = '1'
  clearCareerFormData()

  ElMessage.success('表单已重置')
}
</script>



<template>
  <div class="career-form-layout">
    <el-container>
      <!-- 高端自定义侧边栏 -->
      <el-aside width="260px" class="premium-sidebar">
        <div class="sidebar-brand">
          <div class="brand-icon-wrapper">
            <el-icon :size="24">
              <DocumentAdd />
            </el-icon>
            <div class="brand-glow"></div>
          </div>
          <div class="brand-info">
            <div class="brand-text">能力画像</div>
            <div class="brand-subtitle">AI 智能规划</div>
          </div>
        </div>

        <!-- 进度概览 -->
        <div v-if="activeProfileTab === 'resume'" class="progress-overview">
          <div class="progress-text">
            <span>完成度</span>
            <span class="progress-percent">{{ formProgress }}%</span>
          </div>
          <el-progress :percentage="formProgress" :show-text="false" :stroke-width="6" class="sidebar-progress" />
        </div>

        <div class="career-section-switcher">
          <button
            type="button"
            class="career-section-tab"
            :class="{ 'is-active': activeProfileTab === 'resume' }"
            @click="switchCareerSection('resume')"
          >
            <el-icon><Document /></el-icon>
            <span>我的简历</span>
          </button>
          <button
            type="button"
            class="career-section-tab"
            :class="{ 'is-active': activeProfileTab === 'template' }"
            @click="switchCareerSection('template')"
          >
            <el-icon><Folder /></el-icon>
            <span>导出简历</span>
          </button>
          <button
            type="button"
            class="career-section-tab"
            :class="{ 'is-active': route.path.includes('/career-form/voice') }"
            @click="switchCareerSection('voice')"
          >
            <el-icon><DataAnalysis /></el-icon>
            <span>语音输入</span>
          </button>
        </div>

        <template v-if="activeProfileTab === 'resume'">
          <el-menu :default-active="activeMenu" class="sidebar-menu" @select="handleMenuSelect">
            <el-menu-item index="1" :class="{ 'is-completed': isStepCompleted(1) }">
              <div class="menu-step">
                <el-icon v-if="isStepCompleted(1)">
                  <Check />
                </el-icon>
                <span v-else>1</span>
              </div>
              <span class="menu-text">基本信息</span>
              <el-icon class="menu-check" v-if="isStepCompleted(1)"><Circle-Check /></el-icon>
            </el-menu-item>

            <el-menu-item index="2" :class="{ 'is-completed': isStepCompleted(2) }">
              <div class="menu-step">
                <el-icon v-if="isStepCompleted(2)">
                  <Check />
                </el-icon>
                <span v-else>2</span>
              </div>
              <span class="menu-text">技能证书</span>
              <el-icon class="menu-check" v-if="isStepCompleted(2)"><Circle-Check /></el-icon>
            </el-menu-item>

            <el-menu-item index="3" :class="{ 'is-completed': isStepCompleted(3) }">
              <div class="menu-step">
                <el-icon v-if="isStepCompleted(3)">
                  <Check />
                </el-icon>
                <span v-else>3</span>
              </div>
              <span class="menu-text">经历项目</span>
              <el-icon class="menu-check" v-if="isStepCompleted(3)"><Circle-Check /></el-icon>
            </el-menu-item>

            <el-menu-item index="4" :class="{ 'is-completed': isStepCompleted(4) }">
              <div class="menu-step">
                <el-icon v-if="isStepCompleted(4)">
                  <Check />
                </el-icon>
                <span v-else>4</span>
              </div>
              <span class="menu-text">素质测评</span>
              <el-icon class="menu-check" v-if="isStepCompleted(4)"><Circle-Check /></el-icon>
            </el-menu-item>

            <el-menu-item index="5" :class="{ 'is-completed': isStepCompleted(5) }">
              <div class="menu-step">
                <el-icon v-if="isStepCompleted(5)">
                  <Check />
                </el-icon>
                <span v-else>5</span>
              </div>
              <span class="menu-text">职业意向</span>
              <el-icon class="menu-check" v-if="isStepCompleted(5)"><Circle-Check /></el-icon>
            </el-menu-item>
          </el-menu>

          <div class="resume-upload-section">
            <el-button class="upload-btn" :type="hasUploadedResume ? 'info' : 'primary'" @click="showUploadDialog = true"
              :icon="Upload" size="large">
              {{ hasUploadedResume ? '重新上传简历' : '智能解析简历' }}
            </el-button>
            <el-button
              v-if="showResumeContinueButton"
              class="resume-continue-btn"
              plain
              :icon="Warning"
              @click="reopenMissingFieldsChat"
            >
              继续补全信息
            </el-button>
            <div v-if="showResumeContinueButton" class="resume-continue-tip">
              识别后还有 {{ missingFieldCount }} 项必填信息待补充，稍后也可以从这里继续。
            </div>
          </div>
        </template>

      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <el-card v-if="activeProfileTab === 'resume'" class="form-card">
          <template #header>
            <div class="dashboard-header-modern">
              <div class="dashboard-hero-main">
                <div class="header-left">
                  <h2>{{ currentSectionTitle }}</h2>
                  <div class="step-indicator">第 {{ activeMenu }} 步，共 5 步</div>
                </div>

                <div class="dashboard-progress-panel">
                  <span class="dashboard-progress-label">完成度 {{ formProgress }}%</span>
                  <el-progress
                    :percentage="formProgress"
                    :show-text="false"
                    :stroke-width="10"
                    class="dashboard-progress-bar"
                  />
                </div>
              </div>

              <div class="dashboard-pill-row">
                <span class="dashboard-pill dashboard-pill--primary">画像完整度 {{ profileCompleteness }}%</span>
                <span class="dashboard-pill">逐步完善后可生成更准确评估</span>
              </div>

              <div class="dashboard-stat-row">
                <div class="dash-stat-item">
                  <div class="stat-info">
                    <span class="stat-label">当前阶段</span>
                    <div class="stat-value-row">
                      <span class="stat-value">{{ currentSectionTitle }}</span>
                    </div>
                    <span class="stat-desc">{{ currentSectionDescription }}</span>
                  </div>
                </div>

                <div class="dash-stat-item">
                  <div class="stat-info">
                    <span class="stat-label">已完成步骤</span>
                    <div class="stat-value-row">
                      <span class="stat-value">{{ completedStepCount }}/5</span>
                    </div>
                    <span class="stat-desc">每完成一步都会提升画像可用性</span>
                  </div>
                </div>

                <div class="dash-stat-item">
                  <div class="stat-info">
                    <span class="stat-label">评估准备度</span>
                    <div class="stat-value-row">
                      <span class="stat-value">{{ readinessText }}</span>
                    </div>
                    <span class="stat-desc">{{ readinessHint }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px" size="default">
            <!-- 1. 基本信息 -->
            <div v-show="activeMenu === '1'" class="section-content">
              <div class="form-section-title">教育背景</div>
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="最高学历" prop="education">
                    <el-select v-model="formData.education" placeholder="请选择最高学历" style="width: 100%"
                      @change="handleEducationChange" clearable>
                      <el-option label="专科" value="专科" />
                      <el-option label="本科" value="本科" />
                      <el-option label="硕士" value="硕士" />
                      <el-option label="博士" value="博士" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12" v-if="showEducationInput">
                  <el-form-item label="学历说明" prop="educationOther">
                    <el-input v-model="formData.educationOther" placeholder="如：MBA、双学位等" clearable />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="专业类别" prop="major">
                    <el-cascader v-model="formData.major" :options="majorOptions" placeholder="请选择专业类别"
                      style="width: 100%" :props="{ expandTrigger: 'hover' }" clearable />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="毕业时间" prop="graduationDate">
                    <el-date-picker v-model="formData.graduationDate" type="month" placeholder="选择毕业年月" format="YYYY-MM"
                      style="width: 100%" clearable />
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="form-tips">
                <el-icon><Info-Filled /></el-icon>
                <span>完善的教育背景信息有助于系统更准确地评估你的职业发展路径</span>
              </div>
            </div>

            <!-- 2. 技能与证书 -->
           <div v-show="activeMenu === '2'" class="section-content">
              <div class="form-section-title">外语能力</div>
              <el-form-item label="外语水平" prop="languages">
                <div class="list-container">
                  <div v-for="(lang, index) in formData.languages" :key="index" class="list-row">
                    <el-select v-model="lang.type" placeholder="语种" style="width: 130px">
                      <el-option label="英语" value="英语" />
                      <el-option label="日语" value="日语" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                    <el-select v-model="lang.level" placeholder="水平" style="width: 130px" :disabled="lang.type === ''">
                      <el-option label="四级" value="四级" />
                      <el-option label="六级" value="六级" />
                      <el-option label="托福/雅思" value="托福/雅思" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                    <!-- 语种选择"其他"时的自定义输入 -->
                    <template v-if="lang.type === '其他'">
                      <el-input v-model="lang.other" placeholder="请输入语种" style="width: 150px" />
                      <el-button type="primary" @click="confirmCustomLanguage(index, 'type')">
                        确认
                      </el-button>
                    </template>
                    <!-- 水平选择"其他"时的自定义输入 -->
                    <template v-else-if="lang.level === '其他'">
                      <el-input v-model="lang.other" placeholder="请输入证书" style="width: 150px" />
                      <el-button type="primary" @click="confirmCustomLanguage(index, 'level')">
                        确认
                      </el-button>
                    </template>
                    <el-button text type="danger" :icon="Delete" @click="removeLanguage(index)" />
                  </div>
                  <el-button class="add-item-btn" type="primary" plain :icon="Plus" @click="addLanguage">
                    添加外语
                  </el-button>
                </div>
              </el-form-item>

              <div class="form-section-title">专业证书</div>
              <el-form-item label="核心证书" prop="certificates">
                <el-select v-model="formData.certificates" multiple placeholder="请选择证书" style="width: 100%"
                  @change="handleCertificateChange">
                  <el-option label="软考中级" value="软考中级" />
                  <el-option label="软考高级" value="软考高级" />
                  <el-option label="英语六级" value="英语六级" />
                  <el-option label="PMP" value="PMP" />
                  <el-option label="其他" value="其他" />
                </el-select>
                <el-input v-if="showCertificateInput" v-model="formData.certificateOther"
                  placeholder="请输入证书名称，如：CPA、CFA 等" style="margin-top: 12px" />
              </el-form-item>

              <div class="form-section-title">专业技能</div>
              <el-form-item label="专业技能" prop="skills">
                <div class="input-list-group">
                  <div class="add-input-row">
                    <el-input v-model="newSkill" placeholder="输入技能（如 Java、Python）" @keyup.enter="addSkill"
                      style="flex: 1" />
                    <el-button type="primary" :icon="Plus" @click="addSkill">
                      添加
                    </el-button>
                  </div>
                  <div v-for="(skill, index) in formData.skills" :key="index" class="skill-item">
                    <span class="skill-name">{{ skill.name }}</span>
                    <el-progress :percentage="skill.score || 0" status="success" style="width: 120px"
                      :stroke-width="8" />
                    <div class="skill-actions">
                      <el-button text type="primary" @click="openTestModal('skill', index)">测试</el-button>
                      <el-button text type="danger" :icon="Delete" @click="removeSkill(index)" />
                    </div>
                  </div>
                </div>
              </el-form-item>

              <div class="form-section-title">工具掌握</div>
              <el-form-item label="工具掌握" prop="tools">
                <div class="input-list-group">
                  <div class="add-input-row">
                    <el-input v-model="newTool" placeholder="输入工具（如 Git、Docker）" @keyup.enter="addTool"
                      style="flex: 1" />
                    <el-button type="primary" :icon="Plus" @click="addTool">
                      添加
                    </el-button>
                  </div>
                  <div v-for="(tool, index) in formData.tools" :key="index" class="skill-item">
                    <span class="skill-name">{{ tool.name }}</span>
                    <div class="skill-actions">
                      <el-button text type="primary" @click="openTestModal('tool', index)">测试</el-button>
                      <el-button text type="danger" :icon="Delete" @click="removeTool(index)" />
                    </div>
                  </div>
                </div>
              </el-form-item>

              <!-- 代码能力 -->
              <el-form-item 
                label="代码能力" 
                prop="codeAbility"
              >
                <div class="code-ability-panel">
                  <div class="code-ability-row">
                    <el-input
                      v-model="formData.codeAbility.links"
                      placeholder="请输入 GitHub / Gitee 仓库链接，如 https://github.com/user/repo"
                      style="flex: 1"
                    />
                    <el-button
                      type="warning"
                      :icon="DataAnalysis"
                      :loading="codeAbilityEvaluating"
                      @click="handleCodeAbilityEvaluate"
                    >
                      {{ codeAbilityEvaluating ? '评估中...' : '开始评估' }}
                    </el-button>
                    <el-button
                      v-if="codeAbilityResult"
                      plain
                      :icon="Rank"
                      @click="showCodeAbilityResultDialog"
                    >
                      查看结果
                    </el-button>
                  </div>

                  <div class="code-ability-toolbar">
                    <div class="code-ability-ai-toggle">
                      <span class="toggle-label">深度分析</span>
                      <el-switch
                        v-model="codeAbilityUseAi"
                        inline-prompt
                        active-text="开"
                        inactive-text="关"
                      />
                      <span class="toggle-hint">开启后会返回 AI 深度分析的内容</span>
                    </div>
                    <div class="code-ability-input-hint">
                      支持多个代码仓库联合评估，可用换行、英文逗号或中文逗号分隔多个仓库地址。
                    </div>
                  </div>

                  <div v-if="codeAbilityResult" class="code-ability-summary">
                    <div class="summary-main">
                      <div class="summary-score">{{ codeAbilityResult.composite_score }}</div>
                      <div class="summary-meta">
                        <div class="summary-title">
                          {{ lastEvaluatedCodeRepoUrls.length > 1 ? `已评估 ${lastEvaluatedCodeRepoUrls.length} 个仓库` : (getCodeRepoMeta(lastEvaluatedCodeRepoUrls[0] || '').repo || '未命名仓库') }}
                          <el-tag size="small" :type="getCodeAbilityTagType(codeAbilityResult.composite_score)">
                            {{ codeAbilityResult.level || '未评级' }}
                          </el-tag>
                        </div>
                        <div class="summary-subtitle">
                          {{ getRepoDisplayNames(lastEvaluatedCodeRepoUrls).slice(0, 3).join(' · ') }}
                          <span v-if="lastEvaluatedCodeRepoUrls.length > 3"> 等 {{ lastEvaluatedCodeRepoUrls.length }} 个仓库</span>
                        </div>
                      </div>
                    </div>
                    <div class="summary-actions">
                      <el-button text type="primary" @click="showCodeAbilityResultDialog">展开完整评估</el-button>
                    </div>
                  </div>
                </div>
              </el-form-item>
            </div>

            <!-- 3. 经历与项目 -->
            <div v-show="activeMenu === '3'" class="section-content experience-section">
              <!-- 项目经历 -->
              <div class="experience-block">
                <div class="experience-block-title">
                  <span class="dot-indicator"></span>
                  <span>项目经历</span>
                </div>
                <div class="experience-list-modern">
                  <div v-for="(proj, index) in formData.projects" :key="index" class="premium-exp-card"
                    :class="{ 'is-competition': proj.isCompetition }">
                    <div class="card-indicator"></div>
                    <div class="card-content">
                      <div class="card-top">
                        <div class="exp-badge">
                          <el-icon v-if="proj.isCompetition">
                            <Trophy />
                          </el-icon>
                          <el-icon v-else>
                            <Folder />
                          </el-icon>
                          <span>{{ proj.isCompetition ? '竞赛精华' : '核心项目' }}</span>
                        </div>
                        <div class="card-actions-minimal">
                          <el-button link type="primary" :icon="Edit" @click="openEditProjectDialog(index)" />
                          <el-button link type="danger" :icon="Delete" @click="removeProject(index)" />
                        </div>
                      </div>
                      <h4 class="exp-title">{{ proj.name }}</h4>
                      <div class="exp-desc-box" v-if="proj.desc">
                        {{ proj.desc }}
                      </div>
                    </div>
                  </div>
                </div>
                <el-form-item label="项目或竞赛" class="experience-form-item">
                  <div class="experience-add-box" @click="openProjectDialog">
                    <span class="add-link">添加项目/竞赛</span>
                    <span class="add-hint">记录你的精彩作品</span>
                  </div>
                </el-form-item>
              </div>

              <!-- 实践经历 -->
              <div class="experience-block">
                <div class="experience-block-title">
                  <span class="dot-indicator"></span>
                  <span>实践经历</span>
                </div>
                <div class="experience-list-modern">
                  <div v-for="(intern, index) in formData.internships" :key="index"
                    class="premium-exp-card internship-themed">
                    <div class="card-indicator"></div>
                    <div class="card-content">
                      <div class="card-top">
                        <div class="exp-badge">
                          <el-icon>
                            <Briefcase />
                          </el-icon>
                          <span>职业实战</span>
                        </div>
                        <div class="card-actions-minimal">
                          <el-button link type="primary" :icon="Edit" @click="openEditInternshipDialog(index)" />
                          <el-button link type="danger" :icon="Delete" @click="removeInternship(index)" />
                        </div>
                      </div>
                      <div class="exp-header-info">
                        <h4 class="company-name">{{ intern.company }}</h4>
                        <span class="role-tag">{{ intern.role }}</span>
                      </div>
                      <div class="exp-meta-info" v-if="intern.date && intern.date.length === 2">
                        <el-icon>
                          <Calendar />
                        </el-icon>
                        <span>{{ formatDateRange(intern.date) }}</span>
                      </div>
                      <div class="exp-desc-box" v-if="intern.desc">
                        {{ intern.desc }}
                      </div>
                    </div>
                  </div>
                </div>
                <el-form-item label="实习/工作" prop="internships" class="experience-form-item">
                  <div class="experience-add-box internship-box" @click="openInternshipDialog">
                    <span class="add-link">添加实践经历</span>
                    <span class="add-hint">丰富你的职场履历</span>
                  </div>
                </el-form-item>
              </div>
            </div>

            <!-- 4. 素质测评 -->
            <div v-show="activeMenu === '4'" class="section-content">
              <div class="form-section-title">能力测评</div>
              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="沟通能力">
                    <el-button :type="quizCompleted.communication ? 'success' : 'default'"
                      :class="quizCompleted.communication ? 'quiz-complete' : 'quiz-pending'"
                      @click="!quizCompleted.communication && openQuizModal('communication')">
                      <el-icon v-if="quizCompleted.communication">
                        <Check />
                      </el-icon>
                      {{ quizCompleted.communication ? '已完成' : '开始测试' }}
                    </el-button>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="抗压能力">
                    <el-button :type="quizCompleted.stress ? 'success' : 'default'"
                      :class="quizCompleted.stress ? 'quiz-complete' : 'quiz-pending'"
                      @click="!quizCompleted.stress && openQuizModal('stress')">
                      <el-icon v-if="quizCompleted.stress">
                        <Check />
                      </el-icon>
                      {{ quizCompleted.stress ? '已完成' : '开始测试' }}
                    </el-button>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="学习能力">
                    <el-button :type="quizCompleted.learning ? 'success' : 'default'"
                      :class="quizCompleted.learning ? 'quiz-complete' : 'quiz-pending'"
                      @click="!quizCompleted.learning && openQuizModal('learning')">
                      <el-icon v-if="quizCompleted.learning">
                        <Check />
                      </el-icon>
                      {{ quizCompleted.learning ? '已完成' : '开始测试' }}
                    </el-button>
                  </el-form-item>
                </el-col>
              </el-row>
              <div class="form-section-title">创新案例</div>
              <el-form-item label="创新思维" prop="innovation">
                <el-input v-model="formData.innovation" type="textarea" :rows="4"
                  placeholder="请填写一个改进案例，如：优化了某算法，效率提升 20%" />
              </el-form-item>
            </div>

            <!-- 5. 职业意向 -->
            <div v-show="activeMenu === '5'" class="section-content">
              <div class="form-section-title">求职意向</div>
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="目标岗位" prop="targetJob">
                    <el-autocomplete v-model="formData.targetJob" :fetch-suggestions="querySearch"
                      placeholder="输入意向岗位，如后端工程师" style="width: 100%" clearable />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="期望行业" prop="targetIndustries">
                    <el-select v-model="formData.targetIndustries" multiple placeholder="请选择期望行业" style="width: 100%"
                      clearable>
                      <el-option label="互联网/IT" value="互联网" />
                      <el-option label="金融科技" value="金融" />
                      <el-option label="智能制造" value="制造" />
                      <el-option label="教育培训" value="教育" />
                      <el-option label="医疗健康" value="医疗" />
                      <el-option label="新能源" value="新能源" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="form-section-title">
                <el-icon>
                  <Medal />
                </el-icon>
                发展优先级
              </div>
              <el-form-item label="优先级排序" prop="priorities">
                <div class="priority-container">
                  <div class="priority-header">
                    <div class="priority-desc">
                      <el-icon>
                        <InfoFilled />
                      </el-icon>
                      拖拽调整优先级顺序，第1位为你的首要考虑因素
                    </div>
                    <div class="priority-legend">
                      <span class="legend-item first">
                        <span class="legend-dot"></span>
                        首要
                      </span>
                      <span class="legend-item second">
                        <span class="legend-dot"></span>
                        次要
                      </span>
                      <span class="legend-item third">
                        <span class="legend-dot"></span>
                        第三
                      </span>
                    </div>
                  </div>
                  <div class="priority-cards">
                    <div v-for="(item, index) in formData.priorities" :key="item.value" class="priority-card" :class="{
                      'is-first': index === 0,
                      'is-second': index === 1,
                      'is-third': index === 2,
                      'is-dragging': dragIndex === index,
                      'is-drag-over': dragOverIndex === index
                    }" draggable="true" @dragstart="handleDragStart(index)" @dragover="handleDragOver($event, index)"
                      @dragleave="handleDragLeave" @drop="handleDrop(index)" @dragend="handleDragEnd">
                      <div class="card-rank">
                        <div class="rank-badge" :class="getPriorityClass(index)">
                          <el-icon v-if="index === 0">
                            <Trophy />
                          </el-icon>
                          <span v-else>{{ index + 1 }}</span>
                        </div>
                      </div>
                      <div class="card-content">
                        <div class="card-label">{{ item.label }}</div>
                        <div class="card-hint">{{ getPriorityHint(index) }}</div>
                      </div>
                      <div class="card-actions">
                        <el-button text circle size="small" :disabled="index === 0" @click="movePriority(index, -1)"
                          :icon="ArrowUp" title="上移" class="action-btn" />
                        <el-button text circle size="small" :disabled="index === formData.priorities.length - 1"
                          @click="movePriority(index, 1)" :icon="ArrowDown" title="下移" class="action-btn" />
                      </div>
                      <div class="drag-indicator">
                        <el-icon>
                          <Rank />
                        </el-icon>
                      </div>
                    </div>
                  </div>
                </div>
              </el-form-item>
            </div>

            <!-- 底部操作按钮 -->
            <div class="form-actions">
              <el-button class="form-action-btn" @click="resetForm" :icon="RefreshRight">
                重置表单
              </el-button>
              <el-button class="form-action-btn" @click="switchCareerSection('voice')" :icon="DataAnalysis">
                语音输入
              </el-button>
              <el-button class="form-action-btn form-action-btn--template" @click="switchCareerSection('template')" :icon="Document">
                前往简历模板
              </el-button>
              <el-button type="primary" class="form-action-btn form-action-btn--primary" @click="submitForm"
                :loading="submitting" :icon="Check">
                提交画像
              </el-button>
            </div>
          </el-form>

        </el-card>

        <el-card v-else class="form-card template-workspace-card">
          <template #header>
            <div class="card-header template-card-header">
              <div class="title-section">
                <h2>简历模板生成</h2>
                <p class="subtitle">基于你的“我的简历”信息，快速生成更适合投递的简历版本</p>
                <div class="header-badges">
                  <span class="header-badge">当前模板 {{ currentResumeTemplateLabel }}</span>
                  <span class="header-badge header-badge--soft">可直接同步能力画像并生成预览</span>
                </div>
              </div>
              <el-button type="primary" class="template-sync-btn" @click="syncResumeTemplateFromProfile">
                一键同步能力画像
              </el-button>
            </div>
            <div class="header-stats">
              <div class="header-stat-card" :class="{ 'is-valid': resumeStructureValid }">
                <span class="stat-label">结构校验</span>
                <strong :class="{ 'valid-text': resumeStructureValid }">
                  {{ resumeStructureValid ? '通过' : '待完善' }}
                </strong>
                <small>{{ resumeStructureValid ? '基本信息已满足' : '请完善姓名、联系方式和教育背景' }}</small>
              </div>
              <div class="header-stat-card">
                <span class="stat-label">内容完整度</span>
                <strong :class="{
                  'score-high': resumeCompletenessScore >= 80,
                  'score-medium': resumeCompletenessScore >= 50 && resumeCompletenessScore < 80,
                  'score-low': resumeCompletenessScore < 50
                }">{{ resumeCompletenessScore }}%</strong>
                <small>资料越完整，模板内容越饱满</small>
              </div>
              <div class="header-stat-card" :class="{ 'has-missing': resumeMissingRequiredFields.length > 0 }">
                <span class="stat-label">必填缺失</span>
                <strong :class="{ 'missing-text': resumeMissingRequiredFields.length > 0 }">
                  {{ resumeMissingRequiredFields.length }}
                </strong>
                <small>{{ resumeMissingRequiredFields.length > 0 ? '请补充以下信息：' + resumeMissingRequiredFields.slice(0, 2).map(f => f.label).join('、') : '必填项已完成' }}</small>
              </div>
            </div>
          </template>

          <div class="template-workspace">
            <div class="template-toolbar">
              <el-button class="form-action-btn" @click="goToResumeEditor" :icon="Edit">
                编辑简历
              </el-button>
              <el-button class="form-action-btn" @click="switchCareerSection('resume')" :icon="RefreshRight">
                返回我的简历
              </el-button>
            </div>

            <div class="resume-template-grid template-page-grid">
              <button
                type="button"
                class="resume-template-card template-page-card"
                :class="{ 'is-active': selectedResumeTemplate === 'professional' }"
                @click="selectResumeTemplate('professional')"
              >
                <span class="template-tag">热门</span>
                <div class="template-preview template-preview--professional">
                  <div class="template-preview-header"></div>
                  <div class="template-preview-line large"></div>
                  <div class="template-preview-line"></div>
                  <div class="template-preview-columns">
                    <span></span>
                    <span></span>
                  </div>
                </div>
                <strong>专业商务版</strong>
                <p>适合校招、社招与正式投递场景，结构清晰、信息完整。</p>
                <span class="template-use-btn">使用该模板</span>
              </button>

              <button
                type="button"
                class="resume-template-card template-page-card"
                :class="{ 'is-active': selectedResumeTemplate === 'modern' }"
                @click="selectResumeTemplate('modern')"
              >
                <span class="template-tag template-tag--green">经典</span>
                <div class="template-preview template-preview--modern">
                  <div class="template-preview-header accent"></div>
                  <div class="template-preview-line large"></div>
                  <div class="template-preview-columns">
                    <span class="accent"></span>
                    <span></span>
                  </div>
                  <div class="template-preview-line"></div>
                </div>
                <strong>现代视觉版</strong>
                <p>更适合产品、运营、前端、设计等强调表达与亮点的岗位。</p>
                <span class="template-use-btn">使用该模板</span>
              </button>

              <button
                type="button"
                class="resume-template-card template-page-card"
                :class="{ 'is-active': selectedResumeTemplate === 'compact' }"
                @click="selectResumeTemplate('compact')"
              >
                <span class="template-tag template-tag--orange">新趋势</span>
                <div class="template-preview template-preview--compact">
                  <div class="template-preview-line large"></div>
                  <div class="template-preview-line small"></div>
                  <div class="template-preview-line"></div>
                  <div class="template-preview-line"></div>
                </div>
                <strong>紧凑高效版</strong>
                <p>适合一页式简历，重点突出核心项目、技能标签与求职方向。</p>
                <span class="template-use-btn">使用该模板</span>
              </button>
            </div>

            <div class="template-note-card">
              <el-icon><InfoFilled /></el-icon>
              <span>AI 提示：简历内容会优先同步“能力画像-我的简历”中填写的最新信息，建议先完善表单与上传信息，再生成模板。</span>
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>

    <transition name="submit-overlay-fade">
      <div v-if="submitting" class="submit-overlay">
        <div class="submit-overlay-card">
          <div class="submit-overlay-badge">AI 正在分析中</div>
          <el-icon class="loading-icon submit-overlay-icon" :size="54">
            <Loading />
          </el-icon>
          <h3>正在生成你的能力画像</h3>
          <p>我们正在整理表单信息、分析岗位匹配结果，并为你准备下一步的职业建议。</p>
          <div class="submit-overlay-progress">
            <span class="progress-dot"></span>
            <span class="progress-dot"></span>
            <span class="progress-dot"></span>
          </div>
          <div class="submit-overlay-tip">页面会在分析完成后自动跳转，请稍候片刻。</div>
        </div>
      </div>
    </transition>

    <!-- 素质测评弹窗 - 使用Quenation组件 -->
    <el-dialog v-model="testDialog.visible" :title="testDialog.title" width="800px" class="quiz-dialog" destroy-on-close
      @close="closeTestDialog">
      <!-- 加载状态 -->
      <div v-if="testDialog.loading" class="quiz-loading">
        <el-icon class="loading-icon" :size="48">
          <Loading />
        </el-icon>
        <p>正在加载题目...</p>
        <el-progress :percentage="50" :stroke-width="8" :indeterminate="true" />
      </div>

      <!-- 问卷内容 - 确保数据加载完成后再渲染 -->
      <Quenation v-if="backendQuizData" ref="quenationRef" :title="testDialog.title" :quiz-type="testDialog.type"
        :backend-data="backendQuizData" :quiz-result="quizResult" :score-failed="scoreFailed" @submit="handleQuizSubmit"
        @cancel="closeTestDialog" />

      <transition name="submit-overlay-fade">
        <div v-if="quizSubmitting" class="quiz-submit-overlay">
          <div class="quiz-submit-overlay-card">
            <div class="submit-overlay-badge">问卷提交中</div>
            <el-icon class="loading-icon submit-overlay-icon" :size="44">
              <Loading />
            </el-icon>
            <h3>正在批改{{ testDialog.type === 'skill' ? '专业技能' : '工具掌握' }}测试</h3>
            <p>系统正在分析你的作答表现并生成评分结果，请稍候。</p>
          </div>
        </div>
      </transition>
    </el-dialog>

    <!-- 简历上传弹窗 -->
    <el-dialog v-model="showUploadDialog" title="简历智能上传" width="650px" destroy-on-close>
      <CareerFormUpload :show-close="true" @close="showUploadDialog = false" @parsed="handleResumeParsed" />
    </el-dialog>

    <el-dialog v-model="resumeProfileDialogVisible" title="补充简历资料" width="760px" destroy-on-close
      class="resume-profile-dialog">
      <div class="resume-profile-grid">
        <div class="resume-profile-block">
          <h4>基础信息</h4>
          <div class="resume-profile-form two-col">
            <el-input v-model="resumeProfileExtras.basics.name" placeholder="姓名，必填">
              <template #prepend>姓名</template>
            </el-input>
            <el-input v-model="resumeProfileExtras.basics.label" placeholder="职位标签，如前端工程师">
              <template #prepend>标签</template>
            </el-input>
            <el-input v-model="resumeProfileExtras.basics.email" placeholder="邮箱">
              <template #prepend>邮箱</template>
            </el-input>
            <el-input v-model="resumeProfileExtras.basics.phone" placeholder="电话">
              <template #prepend>电话</template>
            </el-input>
            <el-input v-model="resumeProfileExtras.basics.city" placeholder="城市">
              <template #prepend>城市</template>
            </el-input>
            <el-input v-model="resumeProfileExtras.basics.region" placeholder="省 / 州">
              <template #prepend>地区</template>
            </el-input>
          </div>
          <el-input v-model="resumeProfileExtras.basics.summary" type="textarea" :rows="5"
            placeholder="个人简介，建议补充核心技能、项目亮点和求职方向" />
        </div>

        <div class="resume-profile-block">
          <h4>教育补充</h4>
          <div class="resume-profile-form two-col">
            <el-input v-model="primaryResumeEducation.institution" placeholder="学校名称，必填">
              <template #prepend>学校</template>
            </el-input>
            <el-input v-model="primaryResumeEducation.studyType" placeholder="本科 / 硕士 / 博士">
              <template #prepend>学历</template>
            </el-input>
            <el-input v-model="primaryResumeEducation.area" placeholder="专业">
              <template #prepend>专业</template>
            </el-input>
            <el-date-picker v-model="primaryResumeEducation.startDate" type="month" format="YYYY-MM"
              value-format="YYYY-MM" placeholder="入学时间" style="width: 100%" />
            <el-date-picker v-model="primaryResumeEducation.endDate" type="month" format="YYYY-MM"
              value-format="YYYY-MM" placeholder="毕业时间" style="width: 100%" />
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="resumeProfileDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveResumeProfileDialog">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resumeTemplateDialogVisible" title="选择简历模板" width="820px" destroy-on-close
      class="resume-template-dialog">
      <div class="resume-template-grid">
        <button type="button" class="resume-template-card"
          :class="{ 'is-active': selectedResumeTemplate === 'professional' }"
          @click="selectResumeTemplate('professional')">
          <div class="template-preview template-preview--professional">
            <div class="template-preview-header"></div>
            <div class="template-preview-line large"></div>
            <div class="template-preview-line"></div>
            <div class="template-preview-columns">
              <span></span>
              <span></span>
            </div>
          </div>
          <strong>专业模板</strong>
          <p>适合校招、社招和正式投递场景，信息结构更完整。</p>
        </button>

        <button type="button" class="resume-template-card" :class="{ 'is-active': selectedResumeTemplate === 'modern' }"
          @click="selectResumeTemplate('modern')">
          <div class="template-preview template-preview--modern">
            <div class="template-preview-header accent"></div>
            <div class="template-preview-line large"></div>
            <div class="template-preview-columns">
              <span class="accent"></span>
              <span></span>
            </div>
            <div class="template-preview-line"></div>
          </div>
          <strong>现代模板</strong>
          <p>视觉更突出，适合产品、设计、前端等需要展示感的岗位。</p>
        </button>

        <button type="button" class="resume-template-card"
          :class="{ 'is-active': selectedResumeTemplate === 'compact' }" @click="selectResumeTemplate('compact')">
          <div class="template-preview template-preview--compact">
            <div class="template-preview-line large"></div>
            <div class="template-preview-line small"></div>
            <div class="template-preview-line"></div>
            <div class="template-preview-line"></div>
          </div>
          <strong>紧凑模板</strong>
          <p>适合一页式简历，重点突出核心经历与技能摘要。</p>
        </button>
      </div>

      <template #footer>
        <el-button @click="resumeTemplateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="resumeTemplateDialogVisible = false">使用当前模板</el-button>
      </template>
    </el-dialog>

    <ResumeMissingFieldsChat v-model="showMissingFieldsChat" :fields="pendingMissingFields" :form-data="formData"
      :major-options="majorOptions" :quiz-status="quizCompleted" @save="handleMissingFieldSave"
      @complete="handleMissingFieldComplete" @step-change="activeMenu = $event" @open-quiz="openQuizModal"
      @evaluate-code-ability="handleMissingFieldCodeAbilityEvaluate" />

    <el-dialog v-model="resumePreviewDialogVisible" title="JSON Resume 简历预览" width="1000px" destroy-on-close
      class="resume-preview-dialog">
      <template v-if="jsonResumeResult && currentJsonResume">
        <div class="resume-preview-toolbar">
          <div class="resume-preview-meta">
            <el-tag type="info" effect="light">当前模板: {{ currentResumeTemplateLabel }}</el-tag>
            <el-tag type="primary" effect="light">结构校验: {{ jsonResumeResult.valid ? '通过' : '未通过' }}</el-tag>
            <el-tag :type="jsonResumeResult.completeness.score >= 80 ? 'success' : 'warning'" effect="light">
              完整度: {{ jsonResumeResult.completeness.score }}%
            </el-tag>
            <el-tag v-if="resumeMissingRequiredFields.length" type="danger" effect="light">
              缺失必填: {{ resumeMissingRequiredFields.length }}
            </el-tag>
          </div>
          <div class="resume-preview-actions">
            <el-button plain :icon="Download" @click="exportResumePdf" :loading="resumeExportingPdf">PDF</el-button>
            <el-button type="primary" :icon="Download" @click="exportResumeWord"
              :loading="resumeExportingWord">Word</el-button>
          </div>
        </div>

        <div v-if="resumeMissingRequiredFields.length" class="resume-preview-warning">
          <div class="warning-title">仍有必填信息待补充</div>
          <div class="warning-list">
            <span v-for="item in resumeMissingRequiredFields" :key="item.field">{{ item.label }}</span>
          </div>
        </div>

        <div ref="resumePreviewRef" class="resume-preview-sheet" :class="`template-${selectedResumeTemplate}`">
          <template v-if="selectedResumeTemplate === 'professional'">
            <header class="resume-sheet-header professional-header">
              <div class="professional-header-banner">
                <div class="professional-header-copy">
                  <div class="professional-title-line">
                    <h1>{{ currentJsonResume.basics.name || '求职简历' }}</h1>
                    <span>PERSONAL RESUME</span>
                  </div>
                  <p>{{ currentJsonResume.basics.label || '我一直在努力' }}</p>
                </div>
                <div class="professional-header-mark">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </header>

            <section class="resume-section professional-section">
              <div class="professional-section-head">基本信息</div>
              <div class="professional-basic-grid">
                <div class="professional-basic-list">
                  <div v-for="item in resumeProfessionalFacts" :key="item.label" class="professional-basic-item">
                    <span class="professional-basic-label">{{ item.label }}</span>
                    <span class="professional-basic-value">{{ item.value }}</span>
                  </div>
                </div>
                <div class="professional-avatar-card">
                  <img v-if="currentJsonResume.basics.image" :src="currentJsonResume.basics.image" alt="简历头像"
                    class="professional-avatar-image">
                  <div v-else class="professional-avatar-placeholder">
                    {{ currentJsonResume.basics.name?.slice(0, 1) || '简' }}
                  </div>
                </div>
              </div>
            </section>

            <section v-if="currentJsonResume.basics.summary" class="resume-section professional-section">
              <div class="professional-section-head">自我评价</div>
              <p class="professional-summary">{{ currentJsonResume.basics.summary }}</p>
            </section>

            <section v-if="currentJsonResume.education?.length" class="resume-section professional-section">
              <div class="professional-section-head">教育背景</div>
              <article v-for="item in currentJsonResume.education" :key="`${item.institution}-${item.endDate || ''}`"
                class="professional-entry">
                <div class="professional-entry-head">
                  <strong>{{ item.area || item.studyType || item.institution }}</strong>
                  <span>{{ item.institution }}<template v-if="item.studyType">（{{ item.studyType }}）</template></span>
                  <em>{{ formatResumeDisplayRange(item.startDate, item.endDate) }}</em>
                </div>
                <p v-if="item.courses?.length" class="professional-entry-text">
                  主修课程：{{ item.courses.join('、') }}
                </p>
              </article>
            </section>

            <section v-if="currentJsonResume.work?.length" class="resume-section professional-section">
              <div class="professional-section-head">工作经验</div>
              <article v-for="item in currentJsonResume.work" :key="`${item.name}-${item.startDate || ''}`"
                class="professional-entry">
                <div class="professional-entry-head">
                  <strong>{{ item.position || item.name }}</strong>
                  <span>{{ item.name }}</span>
                  <em>{{ formatResumeDisplayRange(item.startDate, item.endDate, true) }}</em>
                </div>
                <ul v-if="item.highlights?.length" class="professional-bullet-list">
                  <li v-for="highlight in item.highlights" :key="highlight">{{ highlight }}</li>
                </ul>
                <p v-else-if="item.summary" class="professional-entry-text">{{ item.summary }}</p>
              </article>
            </section>

            <section v-if="currentJsonResume.projects?.length" class="resume-section professional-section">
              <div class="professional-section-head">项目经历</div>
              <article v-for="item in currentJsonResume.projects" :key="`${item.name}-${item.startDate || ''}`"
                class="professional-entry">
                <div class="professional-entry-head">
                  <strong>{{ item.name }}</strong>
                  <span>{{ item.entity || '项目实践' }}</span>
                  <em>{{ formatResumeDisplayRange(item.startDate, item.endDate) }}</em>
                </div>
                <p v-if="item.description" class="professional-entry-text">{{ item.description }}</p>
                <ul v-if="item.highlights?.length" class="professional-bullet-list">
                  <li v-for="highlight in item.highlights" :key="highlight">{{ highlight }}</li>
                </ul>
              </article>
            </section>

            <section
              v-if="currentJsonResume.skills?.length || currentJsonResume.languages?.length || currentJsonResume.certificates?.length"
              class="resume-section professional-section">
              <div class="professional-section-head">职业技能</div>
              <div class="professional-skill-block">
                <div v-for="item in currentJsonResume.skills" :key="item.name" class="professional-skill-item">
                  <strong>{{ item.name }}：</strong>{{ item.keywords.join('、') }}
                </div>
                <div v-for="item in currentJsonResume.languages" :key="item.language" class="professional-skill-item">
                  <strong>语言能力：</strong>{{ item.language }}<template v-if="item.fluency">（{{ item.fluency }}）</template>
                </div>
                <div v-for="item in currentJsonResume.certificates" :key="item.name" class="professional-skill-item">
                  <strong>证书：</strong>{{ item.name }}
                </div>
              </div>
            </section>
          </template>

          <template v-else-if="selectedResumeTemplate === 'modern'">
            <div class="modern-layout">
              <aside class="modern-sidebar">
                <div class="modern-identity">
                  <div class="modern-avatar">
                    <img v-if="currentJsonResume.basics.image" :src="currentJsonResume.basics.image" alt="简历头像">
                    <span v-else>{{ currentJsonResume.basics.name?.slice(0, 1) || '简' }}</span>
                  </div>
                  <h1>{{ currentJsonResume.basics.name }}</h1>
                  <p>{{ currentJsonResume.basics.label }}</p>
                </div>

                <section class="modern-side-section">
                  <h3>联系方式</h3>
                  <div class="modern-side-list">
                    <span v-if="currentJsonResume.basics.phone">{{ currentJsonResume.basics.phone }}</span>
                    <span v-if="currentJsonResume.basics.email">{{ currentJsonResume.basics.email }}</span>
                    <span v-if="currentJsonResume.basics.location?.city || currentJsonResume.basics.location?.region">
                      {{ [currentJsonResume.basics.location?.city,
                      currentJsonResume.basics.location?.region].filter(Boolean).join(' / ') }}
                    </span>
                  </div>
                </section>

                <section v-if="currentJsonResume.skills?.length" class="modern-side-section">
                  <h3>技能矩阵</h3>
                  <div class="modern-chip-list">
                    <span v-for="item in currentJsonResume.skills" :key="item.name">{{ item.name }}</span>
                  </div>
                </section>

                <section v-if="currentJsonResume.languages?.length || currentJsonResume.certificates?.length"
                  class="modern-side-section">
                  <h3>补充信息</h3>
                  <div class="modern-side-list">
                    <span v-for="item in currentJsonResume.languages" :key="item.language">
                      {{ item.language }}<template v-if="item.fluency"> / {{ item.fluency }}</template>
                    </span>
                    <span v-for="item in currentJsonResume.certificates" :key="item.name">{{ item.name }}</span>
                  </div>
                </section>
              </aside>

              <main class="modern-main">
                <section v-if="currentJsonResume.basics.summary" class="modern-card modern-card--hero">
                  <h3>职业概述</h3>
                  <p>{{ currentJsonResume.basics.summary }}</p>
                </section>

                <section v-if="currentJsonResume.work?.length" class="modern-card">
                  <h3>工作经历</h3>
                  <article v-for="item in currentJsonResume.work" :key="`${item.name}-${item.startDate || ''}`"
                    class="modern-entry">
                    <div class="modern-entry-head">
                      <div>
                        <strong>{{ item.position || item.name }}</strong>
                        <span>{{ item.name }}</span>
                      </div>
                      <em>{{ formatResumeDisplayRange(item.startDate, item.endDate, true) }}</em>
                    </div>
                    <p v-if="item.summary">{{ item.summary }}</p>
                    <ul v-if="item.highlights?.length">
                      <li v-for="highlight in item.highlights" :key="highlight">{{ highlight }}</li>
                    </ul>
                  </article>
                </section>

                <section v-if="currentJsonResume.projects?.length" class="modern-card">
                  <h3>项目经历</h3>
                  <article v-for="item in currentJsonResume.projects" :key="`${item.name}-${item.startDate || ''}`"
                    class="modern-entry">
                    <div class="modern-entry-head">
                      <div>
                        <strong>{{ item.name }}</strong>
                        <span>{{ item.entity || '项目实践' }}</span>
                      </div>
                      <em>{{ formatResumeDisplayRange(item.startDate, item.endDate) }}</em>
                    </div>
                    <p v-if="item.description">{{ item.description }}</p>
                    <ul v-if="item.highlights?.length">
                      <li v-for="highlight in item.highlights" :key="highlight">{{ highlight }}</li>
                    </ul>
                  </article>
                </section>

                <section v-if="currentJsonResume.education?.length" class="modern-card">
                  <h3>教育经历</h3>
                  <article v-for="item in currentJsonResume.education"
                    :key="`${item.institution}-${item.endDate || ''}`" class="modern-entry modern-entry--education">
                    <div class="modern-entry-head">
                      <div>
                        <strong>{{ item.institution }}</strong>
                        <span>{{ [item.area, item.studyType].filter(Boolean).join(' / ') }}</span>
                      </div>
                      <em>{{ formatResumeDisplayRange(item.startDate, item.endDate) }}</em>
                    </div>
                  </article>
                </section>
              </main>
            </div>
          </template>

          <template v-else>
            <header class="resume-sheet-header compact-header">
              <div>
                <h1>{{ currentJsonResume.basics.name }}</h1>
                <p>{{ currentJsonResume.basics.label }}</p>
              </div>
              <div class="compact-contact">
                <span v-if="currentJsonResume.basics.phone">{{ currentJsonResume.basics.phone }}</span>
                <span v-if="currentJsonResume.basics.email">{{ currentJsonResume.basics.email }}</span>
                <span v-if="currentJsonResume.basics.location?.city || currentJsonResume.basics.location?.region">
                  {{ [currentJsonResume.basics.location?.city,
                  currentJsonResume.basics.location?.region].filter(Boolean).join(' / ') }}
                </span>
              </div>
            </header>

            <div class="compact-layout">
              <aside class="compact-side">
                <section v-if="currentJsonResume.basics.summary" class="compact-block">
                  <h3>简介</h3>
                  <p>{{ currentJsonResume.basics.summary }}</p>
                </section>

                <section v-if="currentJsonResume.skills?.length" class="compact-block">
                  <h3>核心技能</h3>
                  <div class="compact-skill-list">
                    <div v-for="item in currentJsonResume.skills" :key="item.name" class="compact-skill-item">
                      <strong>{{ item.name }}</strong>
                      <p>{{ item.keywords.join(' / ') }}</p>
                    </div>
                  </div>
                </section>

                <section v-if="currentJsonResume.languages?.length || currentJsonResume.certificates?.length"
                  class="compact-block">
                  <h3>语言与证书</h3>
                  <ul class="compact-inline-list">
                    <li v-for="item in currentJsonResume.languages" :key="item.language">
                      {{ item.language }}<template v-if="item.fluency">（{{ item.fluency }}）</template>
                    </li>
                    <li v-for="item in currentJsonResume.certificates" :key="item.name">{{ item.name }}</li>
                  </ul>
                </section>
              </aside>

              <main class="compact-main">
                <section v-if="currentJsonResume.work?.length" class="compact-block">
                  <h3>工作经历</h3>
                  <article v-for="item in currentJsonResume.work" :key="`${item.name}-${item.startDate || ''}`"
                    class="compact-entry">
                    <div class="compact-entry-head">
                      <strong>{{ item.position || item.name }}</strong>
                      <em>{{ formatResumeDisplayRange(item.startDate, item.endDate, true) }}</em>
                    </div>
                    <div class="compact-entry-sub">{{ item.name }}</div>
                    <p v-if="item.summary">{{ item.summary }}</p>
                    <ul v-if="item.highlights?.length">
                      <li v-for="highlight in item.highlights" :key="highlight">{{ highlight }}</li>
                    </ul>
                  </article>
                </section>

                <section v-if="currentJsonResume.projects?.length" class="compact-block">
                  <h3>项目经历</h3>
                  <article v-for="item in currentJsonResume.projects" :key="`${item.name}-${item.startDate || ''}`"
                    class="compact-entry">
                    <div class="compact-entry-head">
                      <strong>{{ item.name }}</strong>
                      <em>{{ formatResumeDisplayRange(item.startDate, item.endDate) }}</em>
                    </div>
                    <div class="compact-entry-sub">{{ item.entity || '项目实践' }}</div>
                    <p v-if="item.description">{{ item.description }}</p>
                  </article>
                </section>

                <section v-if="currentJsonResume.education?.length" class="compact-block">
                  <h3>教育经历</h3>
                  <article v-for="item in currentJsonResume.education"
                    :key="`${item.institution}-${item.endDate || ''}`" class="compact-entry">
                    <div class="compact-entry-head">
                      <strong>{{ item.institution }}</strong>
                      <em>{{ formatResumeDisplayRange(item.startDate, item.endDate) }}</em>
                    </div>
                    <div class="compact-entry-sub">{{ [item.area, item.studyType].filter(Boolean).join(' / ') }}</div>
                  </article>
                </section>
              </main>
            </div>
          </template>
        </div>
      </template>
    </el-dialog>

    <!-- 项目经历弹窗 -->
    <el-dialog v-model="showProjectDialog" :title="projectForm.isEdit ? '编辑项目/竞赛经历' : '添加项目/竞赛经历'" width="600px"
      destroy-on-close class="experience-dialog">
      <div class="experience-form">
        <div class="form-item">
          <label class="form-label">
            <el-icon>
              <Switch />
            </el-icon>
            类型
          </label>
          <el-switch v-model="projectForm.isCompetition" active-text="竞赛" inactive-text="项目" inline-prompt
            style="--el-switch-on-color: #e6a23c; --el-switch-off-color: #409eff" />
        </div>
        <div class="form-item">
          <label class="form-label">
            <el-icon>
              <Document />
            </el-icon>
            {{ projectForm.isCompetition ? '竞赛名称' : '项目名称' }}
          </label>
          <el-input v-model="projectForm.name" :placeholder="projectForm.isCompetition ? '请输入竞赛名称' : '请输入项目名称'"
            size="large" />
        </div>
        <div class="form-item">
          <label class="form-label">
            <el-icon>
              <Edit />
            </el-icon>
            详细描述
          </label>
          <el-input v-model="projectForm.desc" type="textarea" :rows="5" :placeholder="projectForm.isCompetition
            ? '描述竞赛背景、你的角色分工、具体工作和最终成绩'
            : '描述项目背景、你的职责、技术栈和取得的成果'
            " />
        </div>
      </div>
      <template #footer>
        <el-button @click="showProjectDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAddProject" :disabled="!projectForm.name.trim()">
          {{ projectForm.isEdit ? '确认修改' : '确认添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 实践经历弹窗 -->
    <el-dialog v-model="showInternshipDialog" :title="internshipForm.isEdit ? '编辑实践经历' : '添加实践经历'" width="600px"
      destroy-on-close class="experience-dialog">
      <div class="experience-form">
        <div class="form-row two-col">
          <div class="form-item">
            <label class="form-label">
              <el-icon>
                <OfficeBuilding />
              </el-icon>
              公司/组织
            </label>
            <el-input v-model="internshipForm.company" placeholder="请输入公司或组织全称" size="large" />
          </div>
          <div class="form-item">
            <label class="form-label">
              <el-icon>
                <User />
              </el-icon>
              担任岗位
            </label>
            <el-input v-model="internshipForm.role" placeholder="请输入你的职位" size="large" />
          </div>
        </div>
        <div class="form-item">
          <label class="form-label">
            <el-icon>
              <Calendar />
            </el-icon>
            起止时间
          </label>
          <el-date-picker v-model="internshipForm.date" type="daterange" range-separator="至" start-placeholder="开始时间"
            end-placeholder="结束时间" style="width: 100%" size="large" />
        </div>
        <div class="form-item">
          <label class="form-label">
            <el-icon>
              <EditPen />
            </el-icon>
            工作描述
          </label>
          <el-input v-model="internshipForm.desc" type="textarea" :rows="5" placeholder="详细描述工作内容、承担的责任和取得的成果" />
        </div>
      </div>
      <template #footer>
        <el-button @click="showInternshipDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAddInternship"
          :disabled="!internshipForm.company.trim() || !internshipForm.role.trim()">
          {{ internshipForm.isEdit ? '确认修改' : '确认添加' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="codeAbilityResultVisible" title="代码能力评估结果" width="920px" destroy-on-close
      class="code-ability-result-dialog">
      <template v-if="codeAbilityResult">
        <div class="code-result-hero">
          <div class="hero-topline">
            <span class="hero-eyebrow">代码仓库评估报告</span>
            <el-tag :type="getCodeAbilityResultModeTagType()" effect="dark">
              {{ getCodeAbilityResultModeText() }}
            </el-tag>
          </div>
          <div class="hero-main">
            <div class="code-result-score">
              <div class="score-value">{{ codeAbilityResult.composite_score }}</div>
              <div class="score-label">综合评分</div>
            </div>
            <div class="hero-content">
              <h3>{{ lastEvaluatedCodeRepoUrls.length > 1 ? `${lastEvaluatedCodeRepoUrls.length} 个仓库联合评估` :
                (getCodeRepoMeta(lastEvaluatedCodeRepoUrls[0] || '').repo || '未命名仓库') }}</h3>
              <p>{{ lastEvaluatedCodeRepoUrls.length > 1 ? '综合多个代码仓库的结构、活跃度与工程化表现进行评估' :
                (getCodeRepoMeta(lastEvaluatedCodeRepoUrls[0] || '').fullName || codeAbilityResult.username || '-') }}
              </p>
              <div v-if="lastEvaluatedCodeRepoUrls.length" class="hero-link-list">
                <a v-for="url in lastEvaluatedCodeRepoUrls" :key="url" :href="url" target="_blank"
                  rel="noopener noreferrer" class="hero-link">
                  {{ getCodeRepoMeta(url).fullName || url }}
                </a>
              </div>
            </div>
          </div>
        </div>

        <div class="code-result-overview">
          <div class="code-result-meta">
            <div class="meta-line featured">
              <span class="meta-label">评估等级</span>
              <el-tag :type="getCodeAbilityTagType(codeAbilityResult.composite_score)" size="large">
                {{ codeAbilityResult.level || '-' }}
              </el-tag>
            </div>
            <div class="meta-line">
              <span class="meta-label">仓库平台</span>
              <span class="meta-value">{{ codeAbilityResult.platform || getCodeRepoMeta(lastEvaluatedCodeRepoUrls[0] ||
                '').hostLabel || '-' }}</span>
            </div>
            <div class="meta-line">
              <span class="meta-label">评估仓库数</span>
              <span class="meta-value">{{ lastEvaluatedCodeRepoUrls.length || 0 }}</span>
            </div>
            <div class="meta-line" v-if="codeAbilityResult.features?.composite?.percentile !== undefined">
              <span class="meta-label">超过用户</span>
              <span class="meta-value">{{ codeAbilityResult.features?.composite?.percentile }}%</span>
            </div>
          </div>

          <div v-if="codeAbilityResult.features?.composite?.dimensions" class="dimension-grid dimension-grid-hero">
            <div class="dimension-card">
              <span>项目规模</span>
              <strong>{{ codeAbilityResult.features.composite.dimensions.project_scale }}</strong>
            </div>
            <div class="dimension-card">
              <span>技术广度</span>
              <strong>{{ codeAbilityResult.features.composite.dimensions.tech_breadth }}</strong>
            </div>
            <div class="dimension-card">
              <span>活跃度</span>
              <strong>{{ codeAbilityResult.features.composite.dimensions.activity }}</strong>
            </div>
            <div class="dimension-card">
              <span>工程化</span>
              <strong>{{ codeAbilityResult.features.composite.dimensions.engineering }}</strong>
            </div>
            <div class="dimension-card">
              <span>社区影响力</span>
              <strong>{{ codeAbilityResult.features.composite.dimensions.influence }}</strong>
            </div>
          </div>
        </div>

        <div v-if="codeAbilityResult.ai_analysis" class="code-result-section">
          <h4>AI 深度分析</h4>

          <div v-if="codeAbilityResult.ai_analysis.overall_assessment" class="analysis-block">
            <h5>整体评价</h5>
            <p>{{ codeAbilityResult.ai_analysis.overall_assessment.summary }}</p>
            <div class="analysis-tags" v-if="codeAbilityResult.ai_analysis.overall_assessment.strengths?.length">
              <el-tag v-for="item in codeAbilityResult.ai_analysis.overall_assessment.strengths"
                :key="`strength-${item}`" type="success" effect="light">
                {{ item }}
              </el-tag>
            </div>
            <div class="analysis-tags" v-if="codeAbilityResult.ai_analysis.overall_assessment.weaknesses?.length">
              <el-tag v-for="item in codeAbilityResult.ai_analysis.overall_assessment.weaknesses"
                :key="`weakness-${item}`" type="danger" effect="light">
                {{ item }}
              </el-tag>
            </div>
          </div>

          <div v-if="codeAbilityResult.ai_analysis.tech_stack_analysis" class="analysis-block">
            <h5>技术栈分析</h5>
            <p>{{ codeAbilityResult.ai_analysis.tech_stack_analysis.stack_maturity }}</p>
            <div class="analysis-list-grid">
              <div>
                <div class="list-title">主技术栈</div>
                <ul>
                  <li v-for="item in codeAbilityResult.ai_analysis.tech_stack_analysis.primary_stack"
                    :key="`primary-${item}`">{{ item }}</li>
                </ul>
              </div>
              <div>
                <div class="list-title">辅助技术栈</div>
                <ul>
                  <li v-for="item in codeAbilityResult.ai_analysis.tech_stack_analysis.secondary_stack"
                    :key="`secondary-${item}`">{{ item }}</li>
                </ul>
              </div>
            </div>
            <div v-if="codeAbilityResult.ai_analysis.tech_stack_analysis.stack_recommendations?.length"
              class="analysis-list">
              <div class="list-title">技术栈建议</div>
              <ul>
                <li v-for="item in codeAbilityResult.ai_analysis.tech_stack_analysis.stack_recommendations"
                  :key="`stack-rec-${item}`">{{ item }}</li>
              </ul>
            </div>
          </div>

          <div v-if="codeAbilityResult.ai_analysis.project_quality_analysis" class="analysis-block">
            <h5>项目质量分析</h5>
            <p>{{ codeAbilityResult.ai_analysis.project_quality_analysis.code_quality }}</p>
            <p>{{ codeAbilityResult.ai_analysis.project_quality_analysis.architecture }}</p>
            <div class="analysis-list-grid">
              <div v-if="codeAbilityResult.ai_analysis.project_quality_analysis.best_practices?.length">
                <div class="list-title">最佳实践</div>
                <ul>
                  <li v-for="item in codeAbilityResult.ai_analysis.project_quality_analysis.best_practices"
                    :key="`best-${item}`">{{ item }}</li>
                </ul>
              </div>
              <div v-if="codeAbilityResult.ai_analysis.project_quality_analysis.improvement_areas?.length">
                <div class="list-title">待改进项</div>
                <ul>
                  <li v-for="item in codeAbilityResult.ai_analysis.project_quality_analysis.improvement_areas"
                    :key="`improve-${item}`">{{ item }}</li>
                </ul>
              </div>
            </div>
          </div>

          <div v-if="codeAbilityResult.ai_analysis.actionable_advice" class="analysis-block">
            <h5>行动建议</h5>
            <div class="analysis-list-grid">
              <div v-if="codeAbilityResult.ai_analysis.actionable_advice.short_term?.length">
                <div class="list-title">短期</div>
                <ul>
                  <li v-for="item in codeAbilityResult.ai_analysis.actionable_advice.short_term" :key="`short-${item}`">
                    {{ item }}</li>
                </ul>
              </div>
              <div v-if="codeAbilityResult.ai_analysis.actionable_advice.mid_term?.length">
                <div class="list-title">中期</div>
                <ul>
                  <li v-for="item in codeAbilityResult.ai_analysis.actionable_advice.mid_term" :key="`mid-${item}`">{{
                    item }}</li>
                </ul>
              </div>
              <div v-if="codeAbilityResult.ai_analysis.actionable_advice.long_term?.length">
                <div class="list-title">长期</div>
                <ul>
                  <li v-for="item in codeAbilityResult.ai_analysis.actionable_advice.long_term" :key="`long-${item}`">{{
                    item }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <el-empty v-else description="本次未开启 AI 深度分析，当前结果仅展示基础评分数据。" />
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.career-form-layout {
  min-height: calc(100vh - 60px);
  background:
    radial-gradient(circle at top left, rgba(64, 158, 255, 0.12), transparent 22%),
    linear-gradient(180deg, #f4f8ff 0%, #edf4fb 56%, #f8fbff 100%);
  display: flex;
  flex-direction: column;
}

.el-container {
  min-height: calc(100vh - 60px);
  width: 100%;
}

.el-main {
  height: auto;
  min-height: auto;
  padding: 20px;
  margin-left: 0;
  flex: 1;
}

.premium-sidebar {
  background: #fff;
  border-right: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  z-index: 10;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 20px 24px;
  border-bottom: 1px solid rgba(222, 232, 244, 0.9);
  margin-bottom: 16px;
}

.brand-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-text {
  color: #173a5d;
  font-size: 17px;
  font-weight: 700;
}

.brand-subtitle {
  color: #88a0ba;
  font-size: 12px;
  font-weight: 400;
}

/* 进度概览 */
.progress-overview {
  padding: 0 20px 18px;
  margin: 0 12px 10px;
  border-radius: 18px;
  background: rgba(240, 246, 255, 0.9);
  border: 1px solid rgba(220, 231, 244, 0.92);
}

.progress-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
}

.progress-percent {
  color: #409eff;
  font-size: 16px;
  font-weight: 600;
}

.sidebar-progress :deep(.el-progress-bar__outer) {
  background-color: #e4e7ed;
  border-radius: 2px;
}

.sidebar-progress :deep(.el-progress-bar__inner) {
  background: #409eff;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.career-section-switcher {
  display: grid;
  gap: 10px;
  padding: 0 12px 10px;
}

.career-section-tab {
  width: 100%;
  border: 1px solid rgba(219, 230, 243, 0.96);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.92);
  color: #60758d;
  padding: 13px 14px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.24s ease;
}

.career-section-tab:hover,
.career-section-tab.is-active {
  border-color: rgba(47, 125, 246, 0.38);
  color: #2f7df6;
  background: linear-gradient(135deg, rgba(47, 125, 246, 0.1), rgba(99, 183, 255, 0.04));
  box-shadow: 0 10px 20px rgba(47, 125, 246, 0.1);
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  flex: 1;
  padding: 8px 0;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  padding: 0 16px;
  margin: 4px 12px;
  border-radius: 14px;
  color: #5f738b;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(237, 245, 255, 0.96);
  color: #2f7df6;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(229, 241, 255, 0.98), rgba(242, 248, 255, 0.98));
  color: #2f7df6;
  box-shadow: 0 10px 20px rgba(47, 125, 246, 0.12);
}

.sidebar-menu :deep(.el-menu-item.is-completed) {
  color: #10b981;
}

.sidebar-menu :deep(.el-menu-item.is-completed:not(.is-active)) {
  background: rgba(240, 253, 244, 0.9);
}

.sidebar-menu :deep(.el-menu-item.is-completed:not(.is-active)):hover {
  background: rgba(220, 252, 231, 0.96);
}

.menu-step {
  width: 26px;
  height: 26px;
  border-radius: 9px;
  background: #eef4fb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #6b7f96;
  flex-shrink: 0;
  transition: all 0.24s ease;
}

.sidebar-menu :deep(.el-menu-item.is-active .menu-step) {
  background: linear-gradient(135deg, #409eff 0%, #1677ff 100%);
  color: #fff;
  box-shadow: 0 8px 16px rgba(64, 158, 255, 0.28);
}

.sidebar-menu :deep(.el-menu-item.is-completed .menu-step) {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: #fff;
}

.menu-text {
  flex: 1;
}

.menu-check {
  font-size: 16px;
  color: #16a34a;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.24s ease;
}

.sidebar-menu :deep(.el-menu-item.is-completed .menu-check) {
  opacity: 1;
  transform: scale(1);
}

.resume-upload-section {
  padding: 16px;
  margin: 12px;
  background: linear-gradient(180deg, rgba(244, 248, 255, 0.95), rgba(238, 245, 255, 0.92));
  border-radius: 18px;
  border: 1px solid rgba(220, 231, 244, 0.96);
  flex-shrink: 0;
  box-shadow: 0 12px 30px rgba(22, 59, 102, 0.08);
}

.upload-btn {
  width: 100%;
  border-radius: 14px;
  font-weight: 500;
  font-size: 13px;
  padding: 10px 0;
}

.upload-btn.el-button--info {
  background: #909399;
  border: none;
  color: #ffffff !important;
}

.upload-btn.el-button--info:hover {
  background: #a6a9ad;
}

.resume-continue-btn {
  width: 100%;
  margin-top: 10px;
  margin-left: auto;
  padding: 10px 18px;
  border-radius: 14px;
  box-sizing: border-box;
  border-color: rgba(230, 162, 60, 0.45);
  color: #b76a00;
  background: rgba(255, 247, 237, 0.92);
  font-weight: 600;
  line-height: 1.2;
}

.resume-continue-btn:hover {
  border-color: rgba(230, 162, 60, 0.68);
  color: #9a5a00;
  background: rgba(255, 243, 224, 0.96);
}

.resume-continue-btn :deep(> span) {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.resume-continue-tip {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.6;
  color: #8a6a2f;
}

.main-content {
  padding: 28px;
  display: flex;
  flex-direction: column;
}

.form-card {
  width: 100%;
  max-width: 1040px;
  margin: 0 auto;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(220, 231, 244, 0.96);
  height: auto;
  min-height: fit-content;
  box-shadow:
    0 18px 42px rgba(22, 59, 102, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.84);
  overflow: hidden;
}

.form-card :deep(.el-card__header) {
  padding: 24px 28px;
  border-bottom: 1px solid rgba(225, 234, 244, 0.94);
  background: linear-gradient(180deg, rgba(248, 251, 255, 0.94), rgba(244, 248, 255, 0.92));
}

.form-card :deep(.el-card__body) {
  padding: 28px;
  height: auto;
  min-height: auto;
}

.form-card :deep(.el-form) {
  display: flex;
  flex-direction: column;
  height: auto;
  min-height: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.dashboard-header-modern {
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.dashboard-hero-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.header-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
}

.title-section h2,
.header-left h2 {
  margin: 0;
  font-size: 32px;
  font-weight: 800;
  line-height: 1.2;
  color: #173a5d;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: #8aa0b7;
  font-weight: 500;
}

.step-indicator {
  color: #8aa3c0;
  font-size: 16px;
  font-weight: 700;
}

.dashboard-progress-panel {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  min-width: 280px;
  padding-top: 8px;
}

.dashboard-progress-label {
  color: #6f89a8;
  font-size: 14px;
  font-weight: 700;
}

.dashboard-progress-bar {
  width: 280px;
}

.dashboard-progress-bar :deep(.el-progress-bar__outer) {
  background: rgba(15, 23, 42, 0.05);
  border-radius: 999px;
}

.dashboard-progress-bar :deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
  border-radius: 999px;
}

.dashboard-pill-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.dashboard-pill {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0 18px;
  border-radius: 999px;
  background: #edf3fc;
  color: #6d85a4;
  font-size: 14px;
  font-weight: 700;
}

.dashboard-pill--primary {
  background: #e9f1ff;
  color: #2f7df6;
}

.header-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(47, 125, 246, 0.1);
  color: #2f7df6;
  font-size: 12px;
  font-weight: 700;
}

.header-badge--soft {
  background: rgba(136, 160, 186, 0.12);
  color: #6f839a;
}

.dashboard-stat-row,
.header-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.dashboard-stat-row {
  min-width: min(100%, 560px);
}

.header-stats {
  margin-top: 20px;
}

.dash-stat-item,
.header-stat-card {
  position: relative;
  padding: 28px 28px 26px;
  border-radius: 26px;
  border: 1px solid rgba(210, 225, 244, 0.98);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 250, 255, 0.94));
  box-shadow: 0 14px 36px rgba(67, 103, 149, 0.06);
  overflow: hidden;
}

.dash-stat-item {
  display: block;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
}

.stat-label {
  display: inline-block;
  margin-bottom: 0;
  color: #7f9abd;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0;
}

.header-stat-card strong,
.stat-value {
  display: block;
  margin-bottom: 0;
  color: #173a5d;
  font-size: 30px;
  font-weight: 800;
  line-height: 1.2;
}

.header-stat-card small {
  display: block;
  color: #8aa0b7;
  font-size: 12px;
  line-height: 1.6;
}

.stat-desc {
  color: #8aa3c0;
  font-size: 14px;
  line-height: 1.8;
}

.progress-label {
  font-size: 12px;
  color: #6c8199;
  font-weight: 600;
}

.progress-bar {
  width: 180px;
}

.progress-bar :deep(.el-progress-bar__outer) {
  background-color: #f0f0f0;
  border-radius: 4px;
}

.progress-bar :deep(.el-progress-bar__inner) {
  background: #409eff;
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* 高端侧边栏重塑 */
.premium-sidebar {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.5);
  display: flex;
  flex-direction: column;
  padding: 0;
  height: calc(100vh - 80px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.sidebar-brand {
  padding: 32px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon-wrapper {
  position: relative;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #409eff 0%, #1677ff 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 8px 16px rgba(64, 158, 255, 0.3);
}

.brand-glow {
  position: absolute;
  inset: -4px;
  background: inherit;
  filter: blur(8px);
  opacity: 0.4;
  border-radius: inherit;
  z-index: -1;
}

.brand-text {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: 0.5px;
}

.brand-subtitle {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 主进度盘 */
.main-progress-container {
  padding: 0 24px 32px;
  display: flex;
  justify-content: center;
}

.progress-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.progress-inner .pct {
  font-size: 24px;
  font-weight: 800;
  color: #1e293b;
}

.progress-inner .lbl {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
}

/* 时间轴导航 */
.timeline-nav {
  flex: 1;
  padding: 0 24px;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.track-line {
  position: absolute;
  left: 42px;
  top: 10px;
  bottom: 10px;
  width: 2px;
  background: rgba(226, 232, 240, 0.8);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  z-index: 2;
  transition: all 0.3s ease;
}

.dot-box {
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-dot {
  width: 26px;
  height: 26px;
  background: #fff;
  border: 2px solid #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #94a3b8;
  transition: all 0.3s ease;
}

.active-glow {
  position: absolute;
  width: 36px;
  height: 36px;
  background: rgba(64, 158, 255, 0.15);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }

  50% {
    transform: scale(1.2);
    opacity: 0.2;
  }

  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
}

.nav-item.is-active .step-dot {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.4);
}

.nav-item.is-completed .step-dot {
  background: #10b981;
  border-color: #10b981;
  color: #fff;
}

.nav-text {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  transition: color 0.3s ease;
}

.nav-item.is-active .nav-text {
  color: #1e293b;
  font-weight: 800;
}

/* 侧边栏页脚 */
.sidebar-footer {
  padding: 24px;
  border-top: 1px solid rgba(226, 232, 240, 0.5);
}

/* 统计卡片状态样式 */
.header-stat-card.is-valid {
  border-color: rgba(103, 194, 58, 0.5);
  background: linear-gradient(180deg, rgba(240, 249, 235, 0.94), rgba(230, 245, 220, 0.92));
}

.header-stat-card.has-missing {
  border-color: rgba(245, 108, 108, 0.5);
  background: linear-gradient(180deg, rgba(254, 240, 240, 0.94), rgba(253, 230, 230, 0.92));
}

.valid-text {
  color: #67c23a !important;
}

.missing-text {
  color: #f56c6c !important;
}

.score-high {
  color: #67c23a !important;
}

.score-medium {
  color: #e6a23c !important;
}

.score-low {
  color: #f56c6c !important;
}

.progress-section {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
}

.stat-value {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
}

.stat-value-row {
  display: flex;
  align-items: center;
  height: 32px; /* 固定高度确保对齐 */
}

.stat-glass-glow {
  position: absolute;
  right: -10px;
  top: -10px;
  width: 40px;
  height: 40px;
  background: inherit;
  filter: blur(15px);
  opacity: 0.3;
}

/* 表单内容样式 */
.section-content {
 padding: 18px 20px;
  border: 1px solid rgba(227, 236, 245, 0.92);
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(248, 251, 255, 0.96));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.86);
  position: relative;
  overflow: hidden;
}

.section-content::after {
  content: '';
  position: absolute;
  top: -48px;
  right: -42px;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(47, 125, 246, 0.08), transparent 68%);
  pointer-events: none;
}

/* 分组标题 */
.form-section-title {
  font-size: 16px;
  font-weight: 700;
  color: #173a5d;
  margin: 28px 0 18px;
  padding-left: 0;
  border-left: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-section-title::before {
  content: '';
  width: 16px;
  height: 16px;
  background: linear-gradient(180deg, #60a5fa 0%, #3b82f6 100%);
  border-radius: 50%;
  box-shadow: 0 0 0 8px rgba(59, 130, 246, 0.12);
}

.form-section-title:first-child {
  margin-top: 0;
}

/* 表单提示 */
.form-tips {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 20px;
  padding: 14px 16px;
  background: rgba(241, 247, 255, 0.92);
  border-radius: 16px;
  border-left: 3px solid #409eff;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
  box-shadow: 0 10px 20px rgba(47, 125, 246, 0.05);
}

.form-tips .el-icon {
  color: #409eff;
  font-size: 16px;
  margin-top: 1px;
  flex-shrink: 0;
}

:deep(.el-form-item__label) {
  font-size: 16px;
  color: #183b68;
  font-weight: 700;
  padding-right: 24px;
  height: 48px;
  line-height: 48px;
}

/* 输入框样式优化 */
:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  box-shadow: 0 0 0 1px rgba(208, 222, 239, 0.98) inset;
  transition: all 0.2s ease;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.98);
}

:deep(.el-input__wrapper) {
  min-height: 50px;
  padding: 0 16px;
}

:deep(.el-input__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px rgba(47, 125, 246, 0.72) inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 2px rgba(59, 130, 246, 0.86) inset,
    0 0 0 4px rgba(47, 125, 246, 0.08);
}

/* 选择器样式 */
:deep(.el-select .el-input__wrapper) {
  border-radius: 16px;
}

:deep(.el-select .el-input__inner::placeholder) {
  color: #c0c4cc;
}

/* 日期选择器 */
:deep(.el-date-editor.el-input__wrapper) {
  border-radius: 20px;
}

:deep(.el-date-editor .el-input__prefix) {
  color: #909399;
}

/* 级联选择器 */
:deep(.el-cascader .el-input__wrapper) {
  border-radius: 16px;
}

:deep(.el-cascader .el-input__suffix) {
  color: #909399;
}

:deep(.el-form-item.is-required:not(.is-no-asterisk).asterisk-left > .el-form-item__label::before),
:deep(.el-form-item.is-required:not(.is-no-asterisk) > .el-form-item__label::before) {
  color: #ff6b6b;
  margin-right: 6px;
}

/* 行间距优化 */
.section-content .el-row {
  margin-bottom: 8px;
}

.section-content .el-row:last-child {
  margin-bottom: 0;
}

/* 经历卡片现代版样式 */
.experience-list-modern {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.premium-exp-card {
  position: relative;
  background: #ffffff;
  border: 1px solid rgba(226, 232, 240, 0.6);
  border-radius: 20px;
  padding: 0;
  display: flex;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}

.premium-exp-card:hover {
  transform: translateY(-4px) scale(1.005);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
  border-color: rgba(64, 158, 255, 0.3);
}

.card-indicator {
  width: 6px;
  background: linear-gradient(180deg, #409eff 0%, #1677ff 100%);
  flex-shrink: 0;
}

.is-competition .card-indicator {
  background: linear-gradient(180deg, #8b5cf6 0%, #6d28d9 100%);
}

.internship-themed .card-indicator {
  background: linear-gradient(180deg, #10b981 0%, #059669 100%);
}

.premium-exp-card .card-content {
  flex: 1;
  padding: 20px 24px;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.exp-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.is-competition .exp-badge {
  background: #f5f3ff;
  color: #8b5cf6;
}

.internship-themed .exp-badge {
  background: #ecfdf5;
  color: #10b981;
}

.card-actions-minimal {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.premium-exp-card:hover .card-actions-minimal {
  opacity: 1;
}

.exp-title {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.exp-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.company-name {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
}

.role-tag {
  font-size: 12px;
  font-weight: 600;
  background: #eff6ff;
  color: #3b82f6;
  padding: 2px 8px;
  border-radius: 6px;
}

.exp-meta-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-bottom: 12px;
}

.exp-desc-box {
  font-size: 14px;
  line-height: 1.6;
  color: #475569;
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
}

/* 按钮全局优化 */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #409eff 0%, #1677ff 100%) !important;
  border: none !important;
  border-radius: 14px !important;
  font-weight: 700;
  padding: 12px 24px;
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.25);
  transition: all 0.3s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(64, 158, 255, 0.35);
}

/* 按钮样式 */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #2f7df6 0%, #63b7ff 100%);
  border: none;
  border-radius: 14px;
  font-weight: 600;
  font-size: 14px;
  color: #ffffff !important;
  transition: all 0.2s ease;
  box-shadow: 0 12px 22px rgba(47, 125, 246, 0.18);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #4d8ff6 0%, #73c4ff 100%);
  color: #ffffff !important;
  transform: translateY(-1px);
}

:deep(.el-button--primary:active) {
  background: #3a8ee6;
}

:deep(.el-button--success) {
  background: #67c23a;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  color: #ffffff !important;
}

/* 统一文字按钮 */
:deep(.el-button.is-text) {
  border-radius: 10px;
  transition: all 0.2s ease;
  color: #409eff;
  font-weight: 700;
}

:deep(.el-button.is-text:hover) {
  background: rgba(64, 158, 255, 0.08);
  color: #1677ff;
}

/* 复写兼容性 lint 问题 */
.gradient-text {
  background: linear-gradient(135deg, #409EFF 0%, #764BA2 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.upload-inline {
  display: inline-block;
}

/* ========== 发展优先级样式 - 卡片式设计 ========== */

.priority-container {
  background: linear-gradient(180deg, #f9fbff 0%, #f3f8ff 100%);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(220, 231, 244, 0.96);
}

.priority-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.priority-desc {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.priority-desc .el-icon {
  color: #409eff;
  font-size: 16px;
}

/* 优先级图例 */
.priority-legend {
  display: flex;
  gap: 16px;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-item.first .legend-dot {
  background: linear-gradient(135deg, #f0c78a 0%, #e6a23c 100%);
  box-shadow: 0 2px 6px rgba(230, 162, 60, 0.3);
}

.legend-item.second .legend-dot {
  background: linear-gradient(135deg, #b3d8ff 0%, #409eff 100%);
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
}

.legend-item.third .legend-dot {
  background: linear-gradient(135deg, #d9d9d9 0%, #909399 100%);
}

/* 优先级卡片容器 */
.priority-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 优先级卡片 */
.priority-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 16px;
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: grab;
  user-select: none;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(8px);
}

.priority-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #dcdfe6;
  transition: all 0.3s ease;
}

.priority-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.priority-card:active {
  cursor: grabbing;
}

/* 第一名 - 金色 */
.priority-card.is-first {
  border-color: #e6a23c;
  background: linear-gradient(135deg, #fffaf0 0%, #ffffff 100%);
}

.priority-card.is-first::before {
  background: linear-gradient(180deg, #f0c78a 0%, #e6a23c 100%);
  width: 6px;
}

/* 第二名 - 蓝色 */
.priority-card.is-second {
  border-color: #409eff;
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
}

.priority-card.is-second::before {
  background: linear-gradient(180deg, #b3d8ff 0%, #409eff 100%);
  width: 6px;
}

/* 第三名 - 灰色 */
.priority-card.is-third {
  border-color: #c0c4cc;
}

.priority-card.is-third::before {
  background: linear-gradient(180deg, #d9d9d9 0%, #909399 100%);
}

/* 拖拽状态 */
.priority-card.is-dragging {
  opacity: 0.6;
  transform: scale(0.98) rotate(1deg);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.priority-card.is-drag-over {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
  border-style: dashed;
}

/* 排名徽章 */
.card-rank {
  flex-shrink: 0;
}

.rank-badge {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  transition: all 0.3s ease;
}

.rank-badge.priority-first {
  background: linear-gradient(135deg, #f0c78a 0%, #e6a23c 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.35);
  font-size: 22px;
}

.rank-badge.priority-second {
  background: linear-gradient(135deg, #b3d8ff 0%, #409eff 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.35);
}

.rank-badge.priority-third {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  color: #606266;
  border: 2px solid #dcdfe6;
}

/* 卡片内容 */
.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-hint {
  font-size: 13px;
  color: #909399;
}

.priority-card.is-first .card-hint {
  color: #e6a23c;
  font-weight: 500;
}

.priority-card.is-second .card-hint {
  color: #409eff;
  font-weight: 500;
}

/* 卡片操作按钮 */
.card-actions {
  display: flex;
  gap: 8px;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.priority-card:hover .card-actions {
  opacity: 1;
}

.card-actions .action-btn {
  transition: all 0.2s ease;
}

.card-actions .action-btn:hover:not(:disabled) {
  background: #f5f7fa;
  transform: scale(1.1);
}

/* 拖拽指示器 */
.drag-indicator {
  color: #c0c4cc;
  font-size: 18px;
  cursor: grab;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.drag-indicator:hover {
  color: #909399;
  background: #f5f7fa;
}

.priority-card:active .drag-indicator {
  cursor: grabbing;
}

/* 入场动画 */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.priority-card {
  animation: slideInUp 0.4s ease forwards;
}

.priority-card:nth-child(1) {
  animation-delay: 0.05s;
}

.priority-card:nth-child(2) {
  animation-delay: 0.1s;
}

.priority-card:nth-child(3) {
  animation-delay: 0.15s;
}

/* 底部操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 28px;
  padding-top: 22px;
  border-top: 1px solid rgba(225, 234, 244, 0.94);
}

.form-actions .el-button {
  padding: 12px 28px;
  font-size: 14px;
  border-radius: 14px;
  min-width: 144px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.form-action-btn {
  border: 1px solid #d8e2ee !important;
  background: #ffffff !important;
  color: #46627f !important;
  box-shadow: none !important;
}

.form-action-btn:hover {
  border-color: #9dc3f9 !important;
  color: #2f7df6 !important;
  background: #f7fbff !important;
  transform: translateY(-1px);
}

.form-action-btn--template {
  background: linear-gradient(135deg, #fff9ef 0%, #ffffff 100%) !important;
}

.form-action-btn--preview {
  background: linear-gradient(135deg, #eef7ff 0%, #ffffff 100%) !important;
}

.form-action-btn--primary {
  background: linear-gradient(135deg, #2f7df6 0%, #63b7ff 100%) !important;
  color: #ffffff !important;
  border: none !important;
  box-shadow: 0 12px 24px rgba(47, 125, 246, 0.24) !important;
}

.form-action-btn--primary:hover {
  background: linear-gradient(135deg, #4d8ff6 0%, #73c4ff 100%) !important;
  color: #ffffff !important;
}

.form-action-btn--primary:active {
  background: linear-gradient(135deg, #256ee0 0%, #55a8ff 100%) !important;
  color: #ffffff !important;
}

.template-workspace-card {
  min-height: 760px;
}

.template-card-header {
  align-items: flex-start;
}

.template-sync-btn {
  min-width: 168px;
  height: 44px;
  border-radius: 999px;
  padding: 0 22px;
  border: none;
  box-shadow: 0 12px 26px rgba(47, 125, 246, 0.2);
}

.template-workspace {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.template-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.template-page-grid {
  align-items: stretch;
}

.template-page-card {
  position: relative;
  display: flex;
  flex-direction: column;
}

.template-tag {
  position: absolute;
  top: 18px;
  right: 18px;
  z-index: 1;
  padding: 4px 10px;
  border-radius: 999px;
  background: linear-gradient(135deg, #2f7df6 0%, #63b7ff 100%);
  color: #ffffff;
  font-size: 12px;
  font-weight: 700;
}

.template-tag--green {
  background: linear-gradient(135deg, #37b26c 0%, #72d383 100%);
}

.template-tag--orange {
  background: linear-gradient(135deg, #ffb347 0%, #ff9b42 100%);
}

.template-use-btn {
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  min-width: 116px;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid rgba(106, 169, 255, 0.4);
  background: rgba(238, 247, 255, 0.92);
  color: #409eff;
  font-size: 13px;
  font-weight: 600;
}

.template-note-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 20px;
  border-radius: 18px;
  border: 1px solid rgba(190, 219, 255, 0.9);
  background: linear-gradient(90deg, rgba(240, 248, 255, 0.98), rgba(255, 255, 255, 0.94));
  color: #56718f;
  line-height: 1.8;
}

.template-note-card .el-icon {
  color: #409eff;
  font-size: 18px;
  flex-shrink: 0;
}

/* 重置按钮 - 浅色背景深色文字 */
.form-actions .el-button--default {
  border: 1px solid #dcdfe6;
  color: #606266;
  background: #ffffff;
}

.form-actions .el-button--default:hover {
  border-color: #409eff;
  color: #409eff;
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-1px);
}

/* 提交按钮 - 深色背景白色文字 */
.form-actions .el-button--primary {
  background: #409eff;
  border: none;
  color: #ffffff !important;
}

.form-actions .el-button--primary:hover {
  background: #66b1ff;
  color: #ffffff !important;
}

.form-actions .el-button--primary:active {
  background: #3a8ee6;
}

/* 表单间距 */
:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

:deep(.el-card__body) {
  height: auto;
  min-height: auto;
  padding: 24px;
}

/* 优化输入框 */
:deep(.el-input__inner) {
  height: 36px;
  line-height: 36px;
  font-size: 14px;
}

:deep(.el-input__wrapper) {
  padding: 0 12px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #409eff inset;
}

/* 文本域样式 */
:deep(.el-textarea__inner) {
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.6;
  min-height: 100px !important;
  border-radius: 4px;
  resize: vertical;
}

/* 标签样式 */
:deep(.el-tag) {
  border-radius: 4px;
  padding: 2px 10px;
  font-size: 13px;
}

/* 滑动条样式 */
:deep(.el-slider__runway) {
  height: 4px;
  border-radius: 2px;
}

:deep(.el-slider__bar) {
  border-radius: 2px;
}

:deep(.el-slider__button) {
  border-width: 2px;
}


/* 素质测评按钮样式 */
.quiz-complete,
.quiz-pending {
  min-width: 100px;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.quiz-pending {
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  color: #606266;
}

.quiz-pending:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.quiz-complete {
  background: #67c23a;
  border: none;
  color: #fff;
}

.quiz-complete:hover {
  background: #85ce61;
}

/* 列表样式 */
.list-container,
.input-list-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 添加按钮样式 */
.add-item-btn {
  margin-top: 10px;
  padding: 8px 20px;
  border-radius: 4px;
  font-weight: 500;
}

/* 输入添加行 */
.add-input-row {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.add-input-row .el-button {
  padding: 0 20px;
  border-radius: 4px;
  white-space: nowrap;
}

.list-row,
.skill-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding: 12px 14px;
  background: linear-gradient(180deg, #f7fbff 0%, #f2f7fd 100%);
  border-radius: 16px;
  border: 1px solid rgba(220, 231, 244, 0.96);
  transition: all 0.2s ease;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

/* 技能名称 */
.skill-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
  min-width: 60px;
}

/* 技能操作按钮组 - 靠右对齐 */
.skill-actions {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

/* 代码能力行 */
.code-ability-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 100%;
}

.code-ability-row {
  display: flex;
  gap: 10px;
  align-items: center;
  width: 100%;
}

.code-ability-row .el-button {
  border-radius: 4px;
  padding: 8px 16px;
}

.code-ability-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.code-ability-ai-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 12px 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, #fff8e8 0%, #fffdf6 100%);
  border: 1px solid #f5deb3;
}

.toggle-label {
  font-weight: 600;
  color: #7c4a03;
}

.toggle-hint {
  color: #8a6a35;
  font-size: 13px;
}

.code-ability-input-hint {
  padding: 10px 14px;
  border-radius: 12px;
  background: #f5f8ff;
  border: 1px dashed #bfd3ff;
  color: #5d6f92;
  font-size: 13px;
}

.code-ability-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f0f7ff 0%, #f8fbff 100%);
  border: 1px solid #cfe1ff;
}

.summary-main {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-score {
  min-width: 72px;
  height: 72px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409eff 0%, #1d4ed8 100%);
  color: #fff;
  font-size: 28px;
  font-weight: 800;
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #22324d;
  font-size: 17px;
  font-weight: 700;
}

.summary-subtitle {
  margin-top: 6px;
  color: #6c7b94;
  font-size: 13px;
}

.summary-actions {
  flex-shrink: 0;
}

.code-ability-result-dialog :deep(.el-dialog__body) {
  padding-top: 12px;
}

.code-result-hero {
  padding: 22px 24px;
  margin-bottom: 18px;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(147, 197, 253, 0.28), transparent 28%),
    linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #60a5fa 100%);
  color: #fff;
  box-shadow: 0 24px 56px rgba(29, 78, 216, 0.24);
}

.hero-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.hero-main {
  display: grid;
  grid-template-columns: 170px 1fr;
  gap: 22px;
  align-items: center;
}

.code-result-overview {
  display: grid;
  grid-template-columns: minmax(260px, 320px) 1fr;
  gap: 18px;
  margin-bottom: 20px;
}

.code-result-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, #1d4ed8 0%, #409eff 100%);
  color: #fff;
}

.code-result-score .score-value {
  font-size: 44px;
  font-weight: 800;
  line-height: 1;
}

.code-result-score .score-label {
  margin-top: 10px;
  font-size: 14px;
  opacity: 0.92;
}

.hero-content h3 {
  margin: 0 0 8px;
  font-size: 32px;
  font-weight: 800;
  line-height: 1.1;
}

.hero-content p {
  margin: 0 0 10px;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.82);
}

.hero-link-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-link {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 8px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.14);
  color: #f8fbff;
  text-decoration: none;
  font-size: 13px;
  overflow-wrap: anywhere;
}

.hero-link:hover {
  background: rgba(255, 255, 255, 0.22);
}

.code-result-meta {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.meta-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 14px;
  background: #f7f9fc;
  border: 1px solid #e6edf7;
}

.meta-line.featured {
  background: linear-gradient(135deg, #eef4ff 0%, #f8fbff 100%);
  border-color: #bfd3ff;
}

.meta-label {
  color: #6b7280;
  font-size: 13px;
}

.meta-value {
  color: #1f2937;
  font-weight: 600;
}

.code-result-section {
  margin-top: 22px;
  padding: 18px 20px;
  border-radius: 18px;
  background: #fbfcff;
  border: 1px solid #e8eef8;
}

.code-result-section h4,
.analysis-block h5 {
  margin: 0 0 14px;
  color: #22324d;
}

.dimension-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.dimension-grid-hero {
  align-content: start;
}

.dimension-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  border-radius: 14px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border: 1px solid #dfe8f5;
  box-shadow: 0 10px 22px rgba(148, 163, 184, 0.08);
}

.dimension-card span {
  color: #6b7280;
  font-size: 13px;
}

.dimension-card strong {
  color: #1d4ed8;
  font-size: 24px;
}

.analysis-block+.analysis-block {
  margin-top: 18px;
}

.analysis-block p {
  margin: 0 0 12px;
  color: #4b5563;
  line-height: 1.8;
}

.analysis-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.analysis-list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.analysis-list,
.analysis-list-grid>div {
  padding: 14px 16px;
  border-radius: 14px;
  background: #fff;
  border: 1px solid #e5ebf5;
}

.list-title {
  margin-bottom: 10px;
  color: #22324d;
  font-weight: 700;
}

.analysis-list ul,
.analysis-list-grid ul {
  margin: 0;
  padding-left: 18px;
  color: #4b5563;
  line-height: 1.8;
}

/* 步骤切换动画 */
.section-content {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

/* 素质测评弹窗样式 */
.quiz-dialog :deep(.el-dialog__header) {
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  margin-right: 0;
}

.quiz-dialog :deep(.el-dialog__title) {
  font-weight: 600;
  font-size: 18px;
  color: #303133;
}

.quiz-dialog :deep(.el-dialog__body) {
  padding: 0;
  background: #f5f7fa;
  max-height: 70vh;
  overflow-y: auto;
  position: relative;
}

.quiz-dialog :deep(.el-dialog__footer) {
  display: none;
}

/* Quenation组件在弹窗中的样式适配 */
.quiz-dialog :deep(.questionnaire-container) {
  padding: 0;
}

.quiz-dialog :deep(.questionnaire-card) {
  box-shadow: none;
  border-radius: 0;
}

.quiz-dialog :deep(.questionnaire-card .el-card__header) {
  display: none;
}

.quiz-dialog :deep(.questionnaire-card .el-card__body) {
  padding: 24px;
}

/* 测试提交等待界面 */
.quiz-submit-overlay {
  position: absolute;
  inset: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(241, 247, 255, 0.84);
  backdrop-filter: blur(8px);
}

.quiz-submit-overlay-card {
  width: min(100%, 420px);
  padding: 28px 26px 24px;
  border-radius: 24px;
  text-align: center;
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.18), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 250, 255, 0.98));
  border: 1px solid rgba(191, 219, 254, 0.85);
  box-shadow: 0 22px 50px rgba(37, 99, 235, 0.14);
}

.quiz-submit-overlay-card h3 {
  margin: 0 0 10px;
  color: #173a5d;
  font-size: 24px;
  font-weight: 800;
}

.quiz-submit-overlay-card p {
  margin: 0;
  color: #5f738b;
  font-size: 14px;
  line-height: 1.8;
}

/* 提交等待界面 */
.submit-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(241, 247, 255, 0.82);
  backdrop-filter: blur(10px);
}

.submit-overlay-card {
  width: min(100%, 520px);
  padding: 32px 32px 28px;
  border-radius: 28px;
  text-align: center;
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.2), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 250, 255, 0.98));
  border: 1px solid rgba(191, 219, 254, 0.85);
  box-shadow: 0 24px 60px rgba(37, 99, 235, 0.14);
}

.submit-overlay-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 0 14px;
  margin-bottom: 16px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.12);
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
}

.submit-overlay-icon {
  margin-bottom: 18px;
}

.submit-overlay-card h3 {
  margin: 0 0 12px;
  color: #173a5d;
  font-size: 30px;
  font-weight: 800;
}

.submit-overlay-card p {
  margin: 0 auto;
  max-width: 420px;
  color: #5f738b;
  font-size: 15px;
  line-height: 1.8;
}

.submit-overlay-progress {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin: 22px 0 16px;
}

.progress-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%);
  animation: submitPulse 1.2s ease-in-out infinite;
}

.progress-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.progress-dot:nth-child(3) {
  animation-delay: 0.3s;
}

.submit-overlay-tip {
  color: #7b91a7;
  font-size: 13px;
  line-height: 1.7;
}

@keyframes submitPulse {

  0%,
  80%,
  100% {
    transform: scale(0.85);
    opacity: 0.45;
  }

  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 提交等待界面过渡 */
.submit-overlay-fade-enter-active,
.submit-overlay-fade-leave-active {
  transition: opacity 0.2s ease;
}

.submit-overlay-fade-enter-from,
.submit-overlay-fade-leave-to {
  opacity: 0;
}

/* 加载状态样式 */
.quiz-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  gap: 20px;
  min-height: 300px;
}

.quiz-loading p {
  color: #606266;
  font-size: 16px;
}

.loading-icon {
  color: #409eff;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

/* 测评结果展示样式 */
.quiz-result-container {
  padding: 32px 24px;
  background: #f5f7fa;
}

.quiz-result-header {
  text-align: center;
  margin-bottom: 24px;

  .quiz-result-title {
    margin: 12px 0 0;
    font-size: 22px;
    font-weight: 600;
    color: #303133;
  }
}

.quiz-score-overview {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 28px;
  padding: 20px;
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9eb 100%);
  border-radius: 12px;

  .score-circle {
    display: flex;
    align-items: baseline;
    gap: 2px;
  }

  .score-number {
    font-size: 48px;
    font-weight: 700;
    color: #409eff;
  }

  .score-divider {
    font-size: 28px;
    color: #909399;
    margin: 0 2px;
  }

  .score-max {
    font-size: 28px;
    font-weight: 600;
    color: #909399;
  }

  .score-label {
    margin-top: 4px;
    font-size: 14px;
    color: #909399;
  }
}

.open-ended-result {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;

  .section-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 16px;
  }
}

.oe-score-bar {
  margin-bottom: 20px;

  .oe-score-text {
    display: block;
    margin-bottom: 8px;
    font-size: 15px;
    color: #606266;

    strong {
      font-size: 20px;
      color: #409eff;
    }
  }
}

.score-details {
  margin-bottom: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 16px;

  .score-detail-item {
    padding: 12px 16px;
    margin-bottom: 8px;
    background: #fafafa;
    border-radius: 8px;
    border-left: 3px solid #409eff;

    &:last-child {
      margin-bottom: 0;
    }

    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;

      .detail-point {
        font-weight: 600;
        font-size: 14px;
        color: #303133;
      }
    }

    .detail-reason {
      font-size: 13px;
      color: #606266;
      line-height: 1.6;
    }
  }
}

.result-comment,
.result-suggestions {
  margin-top: 16px;
  padding: 16px;
  border-radius: 8px;

  .comment-label,
  .suggestions-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 8px;
  }

  .comment-text,
  .suggestions-text {
    margin: 0;
    font-size: 14px;
    line-height: 1.8;
    color: #606266;
    white-space: pre-wrap;
  }
}

.result-comment {
  background: #f0f9eb;
  border-left: 3px solid #67c23a;

  .comment-label {
    color: #67c23a;
  }
}

.result-suggestions {
  background: #fdf6ec;
  border-left: 3px solid #e6a23c;

  .suggestions-label {
    color: #e6a23c;
  }
}

.quiz-result-footer {
  margin-top: 28px;
  text-align: center;
}

.quiz-content {
  min-height: 200px;
}

.quiz-question {
  margin-bottom: 28px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 12px;
  border-left: 4px solid #409eff;
}

.question-tag {
  margin-bottom: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 20px;
}

.question-text {
  font-size: 16px;
  color: #303133;
  line-height: 1.7;
  font-weight: 500;
  margin: 0;
}

.question-text {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  line-height: 1.6;
  margin: 0;
}

.quiz-options {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  width: 100%;
}

.quiz-option {
  padding: 0;
  margin: 0 !important;
  height: auto;
  display: flex;
  align-items: stretch;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  background: #fff;
}

.quiz-option:hover {
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.quiz-option.is-checked {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #f5f7fa 100%);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

/* 隐藏原生 radio 圆圈 */
.quiz-option :deep(.el-radio__input) {
  display: none;
}

.quiz-option :deep(.el-radio__label) {
  padding: 0;
  width: 100%;
  display: flex !important;
  align-items: stretch;
}

/* 选项标签容器 */
.option-label {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  color: #606266;
  font-weight: 700;
  font-size: 18px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.quiz-option:hover .option-label {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
}

.quiz-option.is-checked .option-label {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
}

/* 选项文本 */
.option-text {
  flex: 1;
  padding: 16px 20px;
  color: #303133;
  font-size: 15px;
  line-height: 1.6;
  display: flex;
  align-items: center;
}

.quiz-option:hover .option-text {
  color: #409eff;
}

.quiz-option.is-checked .option-text {
  color: #409eff;
  font-weight: 500;
}

/* 选中标记 */
.quiz-option::after {
  content: '';
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%) scale(0);
  width: 24px;
  height: 24px;
  background: #409eff;
  border-radius: 50%;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.quiz-option.is-checked::after {
  content: '✓';
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  transform: translateY(-50%) scale(1);
  opacity: 1;
}

.quiz-option {
  position: relative;
}

.quiz-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 16px;
}

.loading-icon {
  color: #409eff;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

/* 不支持的技能提示样式 */
.quiz-unsupported {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 20px;
  text-align: center;
}

.unsupported-text {
  font-size: 15px;
  color: #606266;
  line-height: 1.8;
  white-space: pre-line;
  margin: 0;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .form-card {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 160px !important;
    min-width: 160px !important;
    max-width: 160px !important;
  }

  .code-ability-row,
  .code-ability-summary {
    flex-direction: column;
  }

  .hero-main,
  .code-result-overview,
  .code-result-meta {
    grid-template-columns: 1fr;
  }

  .hero-content h3 {
    font-size: 24px;
  }

  .summary-main {
    width: 100%;
  }

  .summary-actions {
    width: 100%;
  }

  .summary-actions .el-button {
    width: 100%;
  }

  .el-main {
    padding: 12px;
  }

  .form-card :deep(.el-card__body) {
    padding: 20px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .progress-section {
    align-items: flex-start;
  }

  .header-stats {
    grid-template-columns: 1fr;
  }

  .dashboard-header-modern {
    flex-direction: column;
  }

  .dashboard-stat-row {
    grid-template-columns: 1fr;
    min-width: 0;
  }

  .section-content {
    padding: 16px;
    border-radius: 20px;
  }
}

/* ========== 经历列表样式 ========== */

/* 经历列表容器 */
.experience-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

/* 经历卡片 - 展示模式 */
.experience-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.experience-card:hover {
  border-color: #c0c4cc;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* 竞赛类型卡片特殊样式 */
.experience-card.is-competition {
  border-left: 4px solid #e6a23c;
}

.experience-card.is-competition:hover {
  border-color: #e6a23c;
  box-shadow: 0 4px 16px rgba(230, 162, 60, 0.15);
}

/* 实习卡片特殊样式 */
.experience-card.internship-card {
  border-left: 4px solid #67c23a;
}

.experience-card.internship-card:hover {
  border-color: #67c23a;
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.15);
}

/* 卡片头部 */
.experience-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
  border-bottom: 1px solid #ebeef5;
}

/* 经历类型徽章 */
.experience-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.experience-type-badge .el-icon {
  font-size: 13px;
}

/* 竞赛徽章 */
.experience-card.is-competition .experience-type-badge {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
}

/* 工作徽章 */
.experience-type-badge.work-badge {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

/* 卡片内容区 - 预览模式 */
.experience-card-body {
  padding: 20px;
}

.experience-card-body.preview-mode {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  line-height: 1.4;
}

.preview-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.7;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 信息行 */
.info-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.info-company {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.info-role {
  font-size: 14px;
  color: #409eff;
  background: #ecf5ff;
  padding: 2px 10px;
  border-radius: 4px;
}

.info-date {
  font-size: 13px;
  color: #909399;
}

/* 经历区块样式 */
.experience-section {
  padding: 0;
}

.experience-block {
  margin-bottom: 32px;
}

.experience-block:last-child {
  margin-bottom: 0;
}

.experience-block-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 20px;
}

.dot-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #409eff;
  flex-shrink: 0;
}

/* 经历表单项样式 */
.experience-form-item {
  margin-bottom: 0;
  margin-top: 12px;
}

.experience-form-item :deep(.el-form-item__label) {
  font-size: 14px;
  color: #606266;
  font-weight: 400;
  padding-right: 12px;
}

.experience-form-item :deep(.el-form-item__content) {
  display: flex;
  align-items: center;
}

.experience-add-box {
  width: 100%;
  min-height: 56px;
  padding: 12px 20px;
  border: 1.5px dashed #409eff;
  border-radius: 8px;
  background-color: #f5f9ff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.experience-add-box:hover {
  background-color: #ecf5ff;
  border-color: #66b1ff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

.experience-add-box.internship-box {
  border-color: #c0c4cc;
  background-color: #fafafa;
}

.experience-add-box.internship-box:hover {
  border-color: #409eff;
  background-color: #f5f9ff;
}

.experience-add-box .add-link {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}

.experience-add-box .add-hint {
  font-size: 13px;
  color: #909399;
}

/* 添加经历按钮 */
.add-experience-btn {
  width: 100%;
  height: auto;
  min-height: 80px;
  padding: 20px 28px;
  border: 2px dashed #d0d3d9;
  border-radius: 14px;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.add-experience-btn:hover {
  border-color: #409eff;
  border-style: solid;
  background: linear-gradient(135deg, #ecf5ff 0%, #f5f7fa 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.18);
}

.add-experience-btn .el-icon {
  font-size: 28px;
  margin-bottom: 4px;
  color: #409eff;
  transition: transform 0.3s ease;
}

.add-experience-btn:hover .el-icon {
  transform: scale(1.1) rotate(90deg);
}

.add-experience-btn .btn-text {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  line-height: 1.4;
}

.add-experience-btn .btn-hint {
  font-size: 13px;
  color: #606266;
  font-weight: 400;
  line-height: 1.4;
}

/* ========== 经历弹窗样式 ========== */

.experience-dialog :deep(.el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #e4e7ed;
  margin-right: 0;
}

.experience-dialog :deep(.el-dialog__title) {
  font-weight: 600;
  font-size: 18px;
  color: #303133;
}

.experience-dialog :deep(.el-dialog__body) {
  padding: 28px 24px;
}

.experience-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
}

/* 弹窗表单样式 */
.experience-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.experience-form .form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.experience-form .form-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.experience-form .form-label .el-icon {
  font-size: 16px;
  color: #409eff;
}

.experience-form .form-row.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.experience-form :deep(.el-input__wrapper) {
  background: #f5f7fa;
  border-radius: 8px;
}

.experience-form :deep(.el-input__wrapper:hover) {
  background: #ffffff;
}

.experience-form :deep(.el-textarea__inner) {
  background: #f5f7fa;
  border-radius: 8px;
  min-height: 120px !important;
}

.experience-form :deep(.el-textarea__inner:hover) {
  background: #ffffff;
}

/* ========== 缺失字段提醒对话框样式 ========== */

/* 全局样式覆盖 - 需要在全局CSS中生效 */
:global(.missing-fields-dialog) {
  max-width: 480px !important;
}

:global(.missing-fields-dialog .el-message-box__content) {
  padding: 20px 24px;
}

:global(.missing-fields-dialog .el-message-box__message) {
  padding: 0;
}

:global(.missing-fields-dialog .el-message-box__btns) {
  padding: 12px 24px 20px;
}

/* 缺失字段提示样式 - 组件内部使用 */
.missing-fields-hint {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 2000;
  max-width: 360px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.missing-fields-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #fff7e6 0%, #ffffff 100%);
  border-bottom: 1px solid #f0f0f0;
}

.missing-fields-header .el-icon {
  color: #e6a23c;
  font-size: 20px;
}

.missing-fields-title {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
}

.missing-fields-body {
  padding: 16px 20px;
  max-height: 300px;
  overflow-y: auto;
}

.missing-fields-group {
  margin-bottom: 14px;
}

.missing-fields-group:last-child {
  margin-bottom: 0;
}

.missing-fields-group-title {
  font-size: 13px;
  color: #409eff;
  font-weight: 500;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.missing-fields-group-title::before {
  content: '';
  width: 3px;
  height: 14px;
  background: #409eff;
  border-radius: 2px;
}

.missing-fields-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.missing-fields-list li {
  padding: 6px 0 6px 16px;
  color: #606266;
  font-size: 13px;
  position: relative;
}

.missing-fields-list li::before {
  content: '•';
  position: absolute;
  left: 4px;
  color: #c0c4cc;
}

.missing-fields-footer {
  padding: 12px 20px 16px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

/* 简历解析后的提示样式 */
.resume-parsed-notification {
  background: linear-gradient(135deg, #f0f9eb 0%, #ffffff 100%);
  border: 1px solid #b3e19d;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 20px;
}

.resume-parsed-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.resume-parsed-header .el-icon {
  color: #67c23a;
  font-size: 20px;
}

.resume-parsed-title {
  font-weight: 600;
  color: #67c23a;
  font-size: 15px;
}

.resume-parsed-desc {
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
  padding-left: 30px;
}

.resume-parsed-desc .highlight {
  color: #409eff;
  font-weight: 500;
}

.resume-profile-grid {
  display: grid;
  gap: 20px;
}

.resume-template-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.resume-template-card {
  width: 100%;
  padding: 18px;
  text-align: left;
  border-radius: 20px;
  border: 1px solid #dbe6f3;
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
  cursor: pointer;
  transition: all 0.25s ease;
}

.resume-template-card:hover,
.resume-template-card.is-active {
  border-color: #6aa9ff;
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(47, 125, 246, 0.12);
}

.resume-template-card strong {
  display: block;
  margin-bottom: 6px;
  color: #173a5d;
  font-size: 16px;
}

.resume-template-card p {
  margin: 0;
  color: #60758d;
  line-height: 1.7;
  font-size: 13px;
}

.template-preview {
  display: grid;
  gap: 8px;
  height: 150px;
  padding: 14px;
  margin-bottom: 16px;
  border-radius: 16px;
  border: 1px solid #e8eef7;
  background: #ffffff;
}

.template-preview--professional {
  background:
    linear-gradient(135deg, #6c86a7 0%, #7e94b0 54%, transparent 54%),
    linear-gradient(180deg, #ffffff 54%, #f5f7fb 100%);
}

.template-preview--modern {
  background:
    linear-gradient(90deg, #0f766e 0%, #0f766e 32%, #f7fbfd 32%, #ffffff 100%);
}

.template-preview--compact {
  background:
    linear-gradient(180deg, #ffffff 0%, #fbfcfe 34%, #f6f7f9 34%, #f6f7f9 100%);
}

.template-preview-header,
.template-preview-line,
.template-preview-columns span {
  display: block;
  border-radius: 999px;
  background: #d6e2f0;
}

.template-preview-header {
  width: 46%;
  height: 12px;
}

.template-preview-header.accent,
.template-preview-columns .accent {
  background: linear-gradient(135deg, #2f7df6 0%, #63b7ff 100%);
}

.template-preview-line.large {
  width: 68%;
  height: 10px;
}

.template-preview-line.small {
  width: 40%;
  height: 8px;
}

.template-preview-line {
  width: 100%;
  height: 8px;
}

.template-preview-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.template-preview-columns span {
  height: 56px;
}

.resume-profile-block {
  padding: 20px;
  border-radius: 18px;
  border: 1px solid #e5edf7;
  background: linear-gradient(180deg, #f9fbff 0%, #f3f7fd 100%);
}

.resume-profile-block h4 {
  margin: 0 0 16px;
  color: #173a5d;
  font-size: 18px;
  font-weight: 700;
}

.resume-profile-form {
  display: grid;
  gap: 14px;
  margin-bottom: 14px;
}

.resume-profile-form.two-col {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.resume-preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.resume-preview-meta,
.resume-preview-actions,
.warning-list,
.resume-sheet-contact {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.resume-preview-warning {
  margin-bottom: 16px;
  padding: 16px 18px;
  border-radius: 16px;
  border: 1px solid #f3d19e;
  background: #fff8eb;
}

.warning-title {
  margin-bottom: 8px;
  color: #8a5a00;
  font-weight: 700;
}

.warning-list span {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(230, 162, 60, 0.14);
  color: #a06200;
  font-size: 12px;
}

.resume-preview-sheet {
  padding: 32px;
  border-radius: 24px;
  background: #ffffff;
  border: 1px solid #dbe5f1;
  box-shadow: 0 18px 48px rgba(17, 40, 74, 0.1);
}

.resume-preview-sheet.template-professional {
  background: linear-gradient(180deg, #f7f9fd 0%, #ffffff 100%);
  border-top: 8px solid #6e87a7;
}

.resume-preview-sheet.template-modern {
  padding: 0;
  overflow: hidden;
  background: #eef4fb;
  border-top: 8px solid #0f766e;
}

.resume-preview-sheet.template-compact {
  padding: 28px;
  background: #fffefb;
  border-top: 8px solid #334155;
}

.professional-header {
  margin-bottom: 28px;
}

.professional-header-banner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 28px 34px;
  border-radius: 0 44px 44px 0;
  background: linear-gradient(135deg, #617c9f 0%, #7189ab 100%);
  color: #ffffff;
}

.professional-header-copy h1 {
  margin: 0;
  font-size: 50px;
  line-height: 1;
  letter-spacing: 2px;
  font-weight: 300;
}

.professional-title-line {
  display: flex;
  align-items: flex-start;
  gap: 18px;
}

.professional-title-line span {
  padding-top: 6px;
  font-size: 14px;
  letter-spacing: 1px;
  font-weight: 700;
}

.professional-header-copy p {
  margin: 10px 0 0;
  font-size: 14px;
  opacity: 0.92;
}

.professional-header-mark {
  width: 26px;
  display: grid;
  gap: 6px;
}

.professional-header-mark span {
  display: block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
}

.professional-section {
  position: relative;
  margin-left: 38px;
  padding: 26px 0 18px 20px;
  border-left: 2px solid #d5dce7;
}

.professional-section:last-child {
  padding-bottom: 0;
}

.professional-section-head {
  position: relative;
  display: inline-flex;
  align-items: center;
  min-width: 136px;
  margin: 0 0 18px -40px;
  padding: 7px 24px;
  border-radius: 999px;
  background: #6c86a7;
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
}

.professional-basic-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) 170px;
  gap: 28px;
  align-items: start;
}

.professional-basic-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 28px;
}

.professional-basic-item {
  display: flex;
  gap: 14px;
  line-height: 1.9;
  color: #384b63;
}

.professional-basic-label {
  min-width: 56px;
  color: #60758f;
  font-weight: 700;
}

.professional-basic-value {
  color: #24384d;
}

.professional-avatar-card {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 188px;
  border: 1px solid #d5dfeb;
  background: #ffffff;
}

.professional-avatar-image {
  width: 100%;
  height: 100%;
  max-width: 150px;
  object-fit: cover;
}

.professional-avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 118px;
  height: 148px;
  background: linear-gradient(180deg, #d9e4f1 0%, #edf3fa 100%);
  color: #5c7390;
  font-size: 42px;
  font-weight: 700;
}

.professional-summary,
.professional-entry-text,
.professional-bullet-list {
  margin: 0;
  color: #435671;
  line-height: 1.95;
  font-size: 14px;
}

.professional-entry {
  margin-bottom: 18px;
}

.professional-entry:last-child {
  margin-bottom: 0;
}

.professional-entry-head {
  display: grid;
  grid-template-columns: minmax(120px, 1fr) minmax(180px, 1.2fr) auto;
  gap: 14px;
  align-items: baseline;
  margin-bottom: 8px;
  color: #415b7b;
}

.professional-entry-head strong {
  font-size: 16px;
  color: #476586;
}

.professional-entry-head span {
  color: #5f728d;
}

.professional-entry-head em {
  font-style: normal;
  color: #5f82b1;
}

.professional-bullet-list {
  padding-left: 18px;
}

.professional-bullet-list li+li {
  margin-top: 6px;
}

.professional-skill-block {
  display: grid;
  gap: 10px;
}

.professional-skill-item {
  color: #435671;
  line-height: 1.9;
}

.modern-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  min-height: 960px;
}

.modern-sidebar {
  padding: 34px 26px;
  background: linear-gradient(180deg, #0f766e 0%, #0b3f5c 100%);
  color: #e9fffb;
}

.modern-identity {
  text-align: center;
  margin-bottom: 30px;
}

.modern-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  margin: 0 auto 16px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.14);
  overflow: hidden;
  font-size: 34px;
  font-weight: 700;
}

.modern-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modern-identity h1 {
  margin: 0 0 8px;
  font-size: 30px;
  color: #ffffff;
}

.modern-identity p {
  margin: 0;
  color: rgba(233, 255, 251, 0.84);
}

.modern-side-section {
  margin-bottom: 26px;
}

.modern-side-section h3 {
  margin: 0 0 12px;
  font-size: 14px;
  letter-spacing: 1px;
  color: #9ef3df;
}

.modern-side-list {
  display: grid;
  gap: 10px;
  font-size: 13px;
  line-height: 1.7;
}

.modern-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.modern-chip-list span {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  font-size: 12px;
}

.modern-main {
  padding: 34px;
  display: grid;
  gap: 18px;
  align-content: start;
}

.modern-card {
  padding: 22px 24px;
  border-radius: 22px;
  background: #ffffff;
  border: 1px solid #dbe7f2;
  box-shadow: 0 12px 28px rgba(15, 63, 92, 0.08);
}

.modern-card--hero {
  background: linear-gradient(135deg, #ffffff 0%, #f2fbfa 100%);
}

.modern-card h3 {
  margin: 0 0 16px;
  color: #0b3f5c;
  font-size: 18px;
}

.modern-card p,
.modern-card ul {
  margin: 0;
  color: #4f6377;
  line-height: 1.8;
}

.modern-card ul {
  padding-left: 18px;
  margin-top: 8px;
}

.modern-entry {
  padding: 14px 0;
  border-top: 1px solid #edf2f7;
}

.modern-entry:first-of-type {
  padding-top: 0;
  border-top: none;
}

.modern-entry-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 8px;
}

.modern-entry-head strong {
  display: block;
  margin-bottom: 4px;
  color: #173a5d;
}

.modern-entry-head span,
.modern-entry-head em {
  color: #688096;
  font-style: normal;
}

.compact-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding-bottom: 18px;
  margin-bottom: 22px;
  border-bottom: 2px solid #dfe7ef;
}

.compact-header h1 {
  margin: 0 0 6px;
  color: #24384d;
  font-size: 30px;
}

.compact-header p {
  margin: 0;
  color: #617487;
  font-weight: 600;
}

.compact-contact {
  display: grid;
  gap: 6px;
  justify-items: end;
  color: #5f7284;
  font-size: 13px;
}

.compact-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 24px;
}

.compact-block {
  margin-bottom: 18px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid #e6eaef;
  background: #ffffff;
}

.compact-block h3 {
  margin: 0 0 12px;
  color: #24384d;
  font-size: 16px;
}

.compact-block p,
.compact-block ul {
  margin: 0;
  color: #556676;
  line-height: 1.8;
}

.compact-block ul {
  padding-left: 18px;
  margin-top: 8px;
}

.compact-skill-list {
  display: grid;
  gap: 12px;
}

.compact-skill-item strong {
  display: block;
  margin-bottom: 4px;
  color: #334155;
}

.compact-inline-list {
  display: grid;
  gap: 8px;
  padding-left: 18px;
}

.compact-entry+.compact-entry {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #d8e0e8;
}

.compact-entry-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 4px;
}

.compact-entry-head strong {
  color: #24384d;
}

.compact-entry-head em,
.compact-entry-sub {
  color: #718397;
  font-style: normal;
}

.compact-entry-sub {
  margin-bottom: 6px;
  font-size: 13px;
}

@media (max-width: 768px) {

  .resume-profile-form.two-col,
  .resume-template-grid {
    grid-template-columns: 1fr;
  }

  .resume-preview-sheet {
    padding: 24px 18px;
  }

  .resume-preview-toolbar,
  .template-card-header,
  .template-toolbar,
  .form-actions,
  .professional-title-line,
  .compact-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .modern-layout,
  .compact-layout,
  .professional-basic-grid,
  .professional-basic-list {
    grid-template-columns: 1fr;
  }

  .modern-entry-head,
  .compact-entry-head,
  .professional-entry-head {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .professional-section {
    margin-left: 14px;
    padding-left: 14px;
  }

  .professional-section-head {
    margin-left: -24px;
  }

  .professional-header-banner,
  .modern-main,
  .modern-sidebar,
  .compact-block {
    padding-left: 18px;
    padding-right: 18px;
  }

  .compact-contact {
    justify-items: start;
  }

  .form-actions .el-button {
    width: 100%;
  }

  .template-sync-btn,
  .template-use-btn {
    width: 100%;
  }
}
</style>
