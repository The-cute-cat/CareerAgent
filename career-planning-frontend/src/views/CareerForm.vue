<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
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
  Medal
} from '@element-plus/icons-vue'
<<<<<<< HEAD
import CareerFormUpload from '@/components/CareerForm_Upload.vue'
import Quenation from '@/components/Quenation.vue'
import { submitCareerFormApi, convertToSubmitDTO } from '@/api/career-form/formdata'
import { submitQuiz, getQuestionsApi } from '@/api/career-form/questions'
import type { CareerFormData } from '@/types/careerform_report'
import type { Question } from '@/types/careerform_question'
import type { JobMatchItem } from '@/types/job-match'
=======
import CareerFormUpload from '@/components/CareerFormUpload.vue'
import CareerFormRadar from '@/components/CareerFormRadar.vue'
import type { RadarScores, MissingItem } from '@/components/CareerFormRadar.vue'
import { submitCareerFormApi, convertToSubmitDTO, getCareerReportStatusApi, getCareerReportApi } from '@/api/career-form/formdata'
import { getResumeReportApi, getResumeParseStatusApi } from '@/api/career-form/resume'
import type { CareerFormData, CareerFormSubmitResult } from '@/types/type'
>>>>>>> 5c07dc6 (修改代码)
import {
  majorOptions
} from '@/mock/mockdata/CareerForm_mockdata'


// --- 状态定义 ---

/** 路由实例 */
const router = useRouter()

/** 表单引用，用于表单验证和重置 */
const formRef = ref<FormInstance>()

/** 当前激活的菜单项索引，控制显示哪个表单步骤 (1-5) */
const activeMenu = ref('1')

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
    !!formData.value.education,
    formData.value.major.length > 0,
    !!formData.value.graduationDate
  ]
  total += basicItems.length
  completed += basicItems.filter(Boolean).length

  // 技能与证书项
  const skillItems = [
    formData.value.languages.some(l => l.type && l.level),
    formData.value.certificates.length > 0,
    formData.value.skills.length > 0,
    formData.value.tools.length > 0
  ]
  total += skillItems.length
  completed += skillItems.filter(Boolean).length

  // 经历与项目项
  const expItems = [
    formData.value.projects.length > 0,
    formData.value.internships.length > 0
  ]
  total += expItems.length
  completed += expItems.filter(Boolean).length

  // 素质测评项
  const quizItems = [
<<<<<<< HEAD
    quizCompleted.communication,
    quizCompleted.stress,
    quizCompleted.learning,
    !!formData.innovation
=======
    formData.value.scores.communication,
    formData.value.scores.stress,
    formData.value.scores.learning,
    !!formData.value.innovation
>>>>>>> 5c07dc6 (修改代码)
  ]
  total += quizItems.length
  completed += quizItems.filter(Boolean).length

  // 职业意向项
  const careerItems = [
    !!formData.value.targetJob,
    formData.value.targetIndustries.length > 0
  ]
  total += careerItems.length
  completed += careerItems.filter(Boolean).length

  return Math.round((completed / total) * 100)
})


<<<<<<< HEAD
// --- 素质测评完成状态（独立于表单数据） ---

const quizCompleted = reactive({
  communication: false,
  stress: false,
  learning: false
=======
  // 检查证书
  if (formData.value.certificates.length === 0) {
    items.push({
      field: 'certificates',
      label: '缺少专业证书',
      icon: 'certificate',
      priority: 'medium'
    })
  }

  // 检查实习经历
  if (formData.value.internships.length === 0) {
    items.push({
      field: 'internships',
      label: '缺少实习经历',
      icon: 'internship',
      priority: 'high'
    })
  }

  // 检查项目经历
  if (formData.value.projects.length === 0) {
    items.push({
      field: 'projects',
      label: '缺少项目经历',
      icon: 'project',
      priority: 'high'
    })
  }

  // 检查语言能力
  if (!formData.value.languages.some(l => l.type && l.level)) {
    items.push({
      field: 'languages',
      label: '缺少语言能力',
      icon: 'language',
      priority: 'medium'
    })
  }

  // 检查技能
  if (formData.value.skills.length === 0) {
    items.push({
      field: 'skills',
      label: '缺少专业技能',
      icon: 'skill',
      priority: 'high'
    })
  }

  // 检查工具
  if (formData.value.tools.length === 0) {
    items.push({
      field: 'tools',
      label: '缺少工具掌握',
      icon: 'tool',
      priority: 'low'
    })
  }

  // 检查素质测评
  if (!formData.value.scores.communication) {
    items.push({
      field: 'quiz-communication',
      label: '未完成沟通能力测评',
      icon: 'quiz',
      priority: 'medium'
    })
  }
  if (!formData.value.scores.stress) {
    items.push({
      field: 'quiz-stress',
      label: '未完成抗压能力测评',
      icon: 'quiz',
      priority: 'medium'
    })
  }
  if (!formData.value.scores.learning) {
    items.push({
      field: 'quiz-learning',
      label: '未完成学习能力测评',
      icon: 'quiz',
      priority: 'medium'
    })
  }

  // 检查创新案例
  if (!formData.value.innovation) {
    items.push({
      field: 'innovation',
      label: '缺少创新案例',
      icon: 'innovation',
      priority: 'low'
    })
  }

  return items
>>>>>>> 5c07dc6 (修改代码)
})


// --- 表单数据 ---

const formData = ref<CareerFormData>({
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
  /** 素质测评分数（沟通/抗压/学习，各0-100） */
  quizScores: { communication: 0, stress: 0, learning: 0 },
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

  if (formData.value.education) completed++
  if (formData.value.major.length > 0) completed++
  if (formData.value.skills.length > 0) completed++
  if (formData.value.projects.length > 0 || formData.value.internships.length > 0) completed++
  if (formData.value.targetJob) completed++

  return Math.round((completed / total) * 100)
})


<<<<<<< HEAD
=======
/**
 * 判断用户是否选择了计算机相关专业
 * 用于显示/隐藏代码能力相关表单项
 */
const isComputerMajor = computed(() => {
  const majorStr = JSON.stringify(formData.value.major)
  return majorStr.includes('计算机') || majorStr.includes('软件')
})
>>>>>>> 5c07dc6 (修改代码)

/**
 * 判断指定步骤是否已完成
 * @param step - 步骤编号 (1-5)
 * @returns 该步骤是否已完成
 *
 * 步骤1: 基本信息 - 需要填写学历和专业
 * 步骤2: 技能证书 - 需要至少添加一项技能或证书
 * 步骤3: 经历项目 - 需要至少添加一个项目或实习经历
 * 步骤4: 素质测评 - 需要完成所有三项测评并填写创新案例
 * 步骤5: 职业意向 - 需要填写目标岗位和目标行业
 */
const isStepCompleted = (step: number) => {
  switch (step) {
    case 1:
      return !!(formData.value.education && formData.value.major.length > 0)
    case 2:
      return !!(formData.value.skills.length > 0 || formData.value.certificates.length > 0)
    case 3:
      return !!(formData.value.projects.length > 0 || formData.value.internships.length > 0)
    case 4:
<<<<<<< HEAD
      return !!(quizCompleted.communication && quizCompleted.stress && quizCompleted.learning && formData.innovation)
=======
      return !!(formData.value.scores.communication && formData.value.scores.stress && formData.value.scores.learning && formData.value.innovation)
>>>>>>> 5c07dc6 (修改代码)
    case 5:
      return !!(formData.value.targetJob && formData.value.targetIndustries.length > 0)
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


/** 添加新的语言能力项 */
const addLanguage = () => formData.value.languages.push({ type: '', level: '', other: '' })

/**
 * 移除指定索引的语言能力项
 * @param index - 要移除的项的索引
 */
<<<<<<< HEAD
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
=======
const removeLanguage = (index: number) => formData.value.languages.splice(index, 1)
>>>>>>> 5c07dc6 (修改代码)

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
    formData.value.educationOther = ''
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
    formData.value.certificateOther = ''
  }
}


/**
 * 添加新技能
 * 将 newSkill 输入框的值添加到技能列表，默认熟练度为50
 * 检查是否已存在（不区分大小写）
 */
const addSkill = () => {
  if (newSkill.value) {
<<<<<<< HEAD
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
=======
    formData.value.skills.push({ name: newSkill.value, credibility: 50 })
>>>>>>> 5c07dc6 (修改代码)
    newSkill.value = ''
  }
}

/**
 * 移除指定索引的技能
 * @param index - 要移除的技能索引
 */
<<<<<<< HEAD
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
=======
const removeSkill = (index: number) => formData.value.skills.splice(index, 1)
>>>>>>> 5c07dc6 (修改代码)


/**
 * 添加新工具
 * 将 newTool 输入框的值添加到工具列表，默认熟练程度为"熟练"
 * 检查是否已存在（不区分大小写）
 */
const addTool = () => {
  if (newTool.value) {
<<<<<<< HEAD
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
=======
    formData.value.tools.push({ name: newTool.value, proficiency: '熟练' })
>>>>>>> 5c07dc6 (修改代码)
    newTool.value = ''
  }
}

/**
 * 移除指定索引的工具
 * @param index - 要移除的工具索引
 */
<<<<<<< HEAD
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
=======
const removeTool = (index: number) => formData.value.tools.splice(index, 1)
>>>>>>> 5c07dc6 (修改代码)


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
<<<<<<< HEAD

  const projectData = {
=======
  formData.value.projects.push({
>>>>>>> 5c07dc6 (修改代码)
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
<<<<<<< HEAD
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
=======
const removeProject = (index: number) => formData.value.projects.splice(index, 1)
>>>>>>> 5c07dc6 (修改代码)

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
<<<<<<< HEAD

  const internshipData = {
=======
  formData.value.internships.push({
>>>>>>> 5c07dc6 (修改代码)
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
<<<<<<< HEAD
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
=======
const removeInternship = (index: number) => formData.value.internships.splice(index, 1)
>>>>>>> 5c07dc6 (修改代码)

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
<<<<<<< HEAD
  if (newIndex < 0 || newIndex >= formData.priorities.length) return

  const temp = formData.priorities[index]
  const target = formData.priorities[newIndex]
  if (!temp || !target) return

  formData.priorities[index] = { ...target }
  formData.priorities[newIndex] = { ...temp }
=======
  if (newIndex < 0 || newIndex >= formData.value.priorities.length) return

  const temp = formData.value.priorities[index]!
  const target = formData.value.priorities[newIndex]!

  formData.value.priorities[index] = target
  formData.value.priorities[newIndex] = temp
>>>>>>> 5c07dc6 (修改代码)
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
<<<<<<< HEAD
  const items = formData.priorities.splice(dragIndex.value, 1)
  if (items.length === 0 || !items[0]) return
  formData.priorities.splice(dropIndex, 0, items[0])

=======
  const item = formData.value.priorities.splice(dragIndex.value, 1)[0]!
  formData.value.priorities.splice(dropIndex, 0, item)

>>>>>>> 5c07dc6 (修改代码)
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
 * 打开技能/工具/代码能力测试弹窗
 * 使用Quenation组件展示完整问卷
 * @param type - 测试类型：skill(技能) / tool(工具) / code(代码)
 * @param index - 可选，测试项的索引
 */
const openTestModal = async (type: 'skill' | 'tool', index?: number) => {
  // 保存当前测试的技能信息
  let name = ''
  if (type === 'skill' && index !== undefined) {
<<<<<<< HEAD
    name = formData.skills[index]?.name || ''
    currentTestSkill.value = name
=======
    currentTestSkill.value = formData.value.skills[index]?.name || ''
>>>>>>> 5c07dc6 (修改代码)
    currentTestIndex.value = index
    testDialog.title = `${name} 技能测试`

  } else if (type === 'tool' && index !== undefined) {
<<<<<<< HEAD
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


  console.log("类型",type)
  console.log("名称",name)

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
=======
    currentTestSkill.value = formData.value.tools[index]?.name || ''
    currentTestIndex.value = index
  } else {
    currentTestSkill.value = ''
    currentTestIndex.value = -1
  }

  testDialog.visible = true
  testDialog.type = type === 'code' ? 'ai' : 'quiz'
  testDialog.answer = ''
  testDialog.progress = 0

  // 技能测试：根据技能名称匹配题库
  if (type === 'skill') {
    const skillName = currentTestSkill.value.toLowerCase().trim()

    // 根据技能名称选择对应题库（忽略大小写）
    let questionBank: QuizQuestion[] = []
    let skillType = ''

    if (skillName === 'python') {
      questionBank = pythonQuestions
      skillType = 'Python'
    } else if (skillName === 'java') {
      questionBank = javaQuestions
      skillType = 'Java'
    } else if (skillName === 'c++' || skillName === 'cpp' || skillName === 'c') {
      questionBank = cppQuestions
      skillType = 'C++'
    }

    // 如果匹配到支持的技能题库
    if (questionBank.length > 0) {
      testDialog.title = `${skillType} 技能测试`
      testDialog.currentQuestion = getRandomQuestion(questionBank)
      return
    } else {
      // 不支持的技能，显示提示
      testDialog.title = '技能测试'
      testDialog.currentQuestion = {
        id: -1,
        question: `系统题库暂不支持 "${currentTestSkill.value}" 的测试。\n\n当前支持的技能：Python、Java、C++`,
        options: [
          { label: 'A', value: 'A', text: '了解，继续使用该技能' }
        ]
      }
      return
    }
  }

  // 工具测试：根据工具名称匹配题库
  if (type === 'tool') {
    const toolName = currentTestSkill.value.toLowerCase().trim()

    // 根据工具名称选择对应题库（忽略大小写）
    let questionBank: QuizQuestion[] = []
    let toolType = ''

    if (toolName === 'git') {
      questionBank = gitQuestions
      toolType = 'Git'
    } else if (toolName === 'docker') {
      questionBank = dockerQuestions
      toolType = 'Docker'
    }

    // 如果匹配到支持的工具题库
    if (questionBank.length > 0) {
      testDialog.title = `${toolType} 工具测试`
      testDialog.currentQuestion = getRandomQuestion(questionBank)
      return
    } else {
      // 不支持的工具，显示提示
      testDialog.title = '工具测试'
      testDialog.currentQuestion = {
        id: -1,
        question: `系统题库暂不支持 "${currentTestSkill.value}" 的测试。\n\n当前支持的工具：Git、Docker`,
        options: [
          { label: 'A', value: 'A', text: '了解，继续使用该工具' }
        ]
      }
      return
    }
  }

  // 代码能力测试（AI类型）
  testDialog.title = '代码能力测试'
  testDialog.currentQuestion = {
    id: 0,
    question: 'AI 正在为你生成代码能力测试题...',
    options: []
  }

  // AI类型测试显示进度条动画
  const timer = setInterval(() => {
    testDialog.progress += 10
    if (testDialog.progress >= 100) {
      clearInterval(timer)
      testDialog.currentQuestion = {
        id: 0,
        question: '请完成以下代码能力测试题：',
        options: [
          { label: 'A', value: 'A', text: '能够编写高质量的代码，熟悉设计模式' },
          { label: 'B', value: 'B', text: '能够独立完成开发任务，代码规范良好' },
          { label: 'C', value: 'C', text: '能够完成基础编码，需要代码审查' },
          { label: 'D', value: 'D', text: '正在学习编程基础知识' }
        ]
      }
    }
  }, 200)
>>>>>>> 5c07dc6 (修改代码)
}


/**
 * 打开素质测评弹窗
 * 使用Quenation组件展示完整问卷
 * @param type - 测评类型：communication(沟通) / stress(抗压) / learning(学习)
 */
const openQuizModal = async (type: 'code' | 'communication' | 'stress' | 'learning') => {
  currentQuizType.value = type
<<<<<<< HEAD
  testDialog.type = type

  console.log('类别', type)

=======
  testDialog.visible = true
  testDialog.type = 'quiz'
  testDialog.answer = ''
>>>>>>> 5c07dc6 (修改代码)

  // 测评标题映射
  const titles: Record<string, string> = {
    'code': '代码能力测评',
    'communication': '沟通能力测评',
    'stress': '抗压能力测评',
    'learning': '学习能力测评'
  }

<<<<<<< HEAD
=======
  // 根据类型从对应题库随机抽取题目
  let questionBank: QuizQuestion[] = []
  switch (type) {
    case 'communication':
      questionBank = communicationQuestions
      break
    case 'stress':
      questionBank = stressQuestions
      break
    case 'learning':
      questionBank = learningQuestions
      break
  }

>>>>>>> 5c07dc6 (修改代码)
  testDialog.title = titles[type] || '素质测评'
  testDialog.currentIndex = -1
  testDialog.loading = true
  testDialog.visible = true
  backendQuizData.value = null





  try {
    // 从后端获取题目数据（openQuizModal的类型不需要name参数）
    const quizData = await fetchQuizData(type)
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
<<<<<<< HEAD
} | null>(null)

/**
 * 处理问卷提交完成
 * 根据测试类型更新相应的分数或完成状态
 * @param submitData - 问卷提交的数据 { quizType, answers }
 */
const handleQuizSubmit = async (submitData: any) => {
  const { quizType, answers } = submitData

  // 准备用户答案映射 { questionId: answer }
  const userAnswers: Record<number, string> = {}
  Object.entries(answers || {}).forEach(([key, value]) => {
    const match = key.match(/q_(\d+)/)
    if (match && match[1]) userAnswers[parseInt(match[1])] = value as string
  })

  try {
    const result = await submitQuiz({
      quizType,
      name: ['skill', 'tool'].includes(quizType) ? currentTestSkill.value || '' : undefined,
      questions: (backendQuizData.value?.questions || []) as Question[],
      userAnswers
    })

    // 更新分数
    updateQuizScore(quizType, result.totalScore)

    // 不再自动显示结果页面，保留在Quenation组件中查看答题结果
    // quizResult 用于存储结果但不自动切换视图
    quizResult.value = {
      totalScore: result.totalScore,
      totalMaxScore: result.totalMaxScore,
      openEndedDetails: result.openEndedDetails
    }

    ElMessage.success(`${getQuizTypeName(quizType)}完成！得分：${result.totalScore}分，请查看答题结果`)
  } catch (error) {
    console.error('提交问卷失败:', error)
    ElMessage.error('提交失败，请稍后重试')
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
  } else if (['communication', 'stress', 'learning'].includes(quizType)) {
    if (!formData.quizScores) formData.quizScores = { communication: 0, stress: 0, learning: 0 }
    formData.quizScores[quizType as keyof typeof formData.quizScores] = score
    quizCompleted[quizType as keyof typeof quizCompleted] = true
=======

  // 处理不支持的技能/工具提示
  if (testDialog.currentQuestion.id === -1) {
    testDialog.visible = false
    currentTestSkill.value = ''
    currentTestIndex.value = -1
    return
  }

  // 检查是技能测试还是工具测试
  const isSkillTest = formData.value.skills.some((s, idx) =>
    idx === currentTestIndex.value && s.name.toLowerCase() === currentTestSkill.value.toLowerCase()
  )
  const isToolTest = formData.value.tools.some((t, idx) =>
    idx === currentTestIndex.value && t.name.toLowerCase() === currentTestSkill.value.toLowerCase()
  )

  // 技能测试：验证答案并显示结果
  if (isSkillTest && currentTestIndex.value >= 0) {
    const correctAnswer = testDialog.currentQuestion.correctAnswer

    if (correctAnswer) {
      // 有标准答案的专业技能测试
      const isCorrect = testDialog.answer === correctAnswer

      if (isCorrect) {
        ElMessage.success(`回答正确！${currentTestSkill.value} 技能熟练度提升`)
        // 答对后提升熟练度
        if (formData.value.skills[currentTestIndex.value]) {
          formData.value.skills[currentTestIndex.value]!.credibility = Math.min(100,
            (formData.value.skills[currentTestIndex.value]!.credibility || 50) + 10
          )
        }
      } else {
        ElMessage.error(`回答错误。正确答案是 ${correctAnswer}`)
      }
    } else {
      // 通用测试
      ElMessage.success('测试已完成，结果已记录')
    }

    testDialog.visible = false
    currentTestSkill.value = ''
    currentTestIndex.value = -1
    return
  }

  // 工具测试：验证答案并显示结果
  if (isToolTest && currentTestIndex.value >= 0) {
    const correctAnswer = testDialog.currentQuestion.correctAnswer

    if (correctAnswer) {
      // 有标准答案的工具测试
      const isCorrect = testDialog.answer === correctAnswer

      if (isCorrect) {
        ElMessage.success(`回答正确！${currentTestSkill.value} 工具熟练度提升`)
        // 答对后提升熟练度（将熟练度转换为数值）
        const tool = formData.value.tools[currentTestIndex.value]
        if (tool) {
          const proficiencyMap: Record<string, number> = {
            '了解': 25,
            '熟练': 50,
            '精通': 75
          }
          const currentValue = proficiencyMap[tool.proficiency] || 50
          const newValue = Math.min(100, currentValue + 10)
          // 转换回文字描述
          if (newValue >= 75) tool.proficiency = '精通'
          else if (newValue >= 50) tool.proficiency = '熟练'
          else tool.proficiency = '了解'
        }
      } else {
        ElMessage.error(`回答错误。正确答案是 ${correctAnswer}`)
      }
    } else {
      // 通用测试
      ElMessage.success('测试已完成，结果已记录')
    }

    testDialog.visible = false
    currentTestSkill.value = ''
    currentTestIndex.value = -1
    return
  }

  // 素质测评：标记为已完成
  if (currentQuizType.value) {
    testDialog.visible = false
    formData.value.scores[currentQuizType.value as keyof typeof formData.scores] = true
    ElMessage.success('测试已完成，结果已记录')
>>>>>>> 5c07dc6 (修改代码)
    currentQuizType.value = ''
  }
<<<<<<< HEAD
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

/**
 * 关闭测试弹窗
 */
const closeTestDialog = () => {
=======

  // 其他测试类型
>>>>>>> 5c07dc6 (修改代码)
  testDialog.visible = false
  currentTestSkill.value = ''
  currentTestIndex.value = -1
  currentQuizType.value = ''
  quizResult.value = null
  backendQuizData.value = null
  // 重置Quenation组件
  quenationRef.value?.reset()
}


// --- 必填字段配置 ---

/**
 * 必填字段配置
 * 定义哪些字段是必填项以及如何验证
 */
const requiredFields = [
  { field: 'education', label: '学历', step: '1', validate: (v: any) => !!v },
  { field: 'major', label: '专业', step: '1', validate: (v: any) => Array.isArray(v) && v.length > 0 },
  { field: 'graduationDate', label: '预计毕业日期', step: '1', validate: (v: any) => !!v },
  { field: 'languages', label: '外语能力', step: '2', validate: (v: any) => Array.isArray(v) && v.some((l: any) => l.type && l.level) },
  { field: 'skills', label: '专业技能', step: '2', validate: (v: any) => Array.isArray(v) && v.length > 0 },
  { field: 'targetJob', label: '目标岗位', step: '5', validate: (v: any) => !!v },
  { field: 'targetIndustries', label: '期望行业', step: '5', validate: (v: any) => Array.isArray(v) && v.length > 0 }
]

/**
 * 检查必填字段，返回缺失的字段列表
 * @returns 缺失的字段配置数组
 */
const checkRequiredFields = () => {
  return requiredFields.filter(item => !item.validate(formData[item.field as keyof CareerFormData]))
}

/**
 * 显示缺失字段提醒，引导用户补充
 * @param missingFields 缺失的字段列表
 */
const showMissingFieldsReminder = (missingFields: typeof requiredFields) => {
  if (missingFields.length === 0) {
    ElMessage.success('简历信息已完整填充，可以直接提交！')
    return
  }

  // 按步骤分组
  const stepGroups = missingFields.reduce<Record<string, typeof requiredFields>>((acc, field) => {
    const stepKey = field.step
    if (!acc[stepKey]) {
      acc[stepKey] = []
    }
    // 使用非空断言，因为前面已经确保数组存在
    acc[stepKey]!.push(field)
    return acc
  }, {})

  const stepNames: Record<string, string> = {
    '1': '基本信息',
    '2': '技能与证书',
    '3': '经历与项目',
    '4': '素质测评',
    '5': '职业意向'
  }

  // 构建提示消息
  let message = `<div style="text-align: left; max-height: 300px; overflow-y: auto;">
    <p style="margin-bottom: 12px; color: #e6a23c;"><strong>简历已自动填充，但以下信息需要补充：</strong></p>`

  Object.entries(stepGroups).forEach(([step, fields]) => {
    const fieldList = fields
    if (!fieldList) return
    message += `<div style="margin-bottom: 10px;">
      <p style="color: #409eff; margin: 8px 0 4px 0; font-weight: 500;">【${stepNames[step]}】</p>
      <ul style="margin: 0; padding-left: 20px; color: #606266;">`
    fieldList.forEach(f => {
      message += `<li>${f.label}</li>`
    })
    message += `</ul></div>`
  })

  message += `<p style="margin-top: 12px; color: #909399; font-size: 12px;">点击确定跳转到第一个需要补充的步骤</p></div>`

  ElMessageBox.confirm(message, '信息待完善', {
    confirmButtonText: '去补充',
    cancelButtonText: '暂不补充',
    dangerouslyUseHTMLString: true,
    type: 'warning',
    customClass: 'missing-fields-dialog'
  }).then(() => {
    // 跳转到第一个缺失字段的步骤
    const firstField = missingFields[0]
    if (firstField) {
      const firstMissingStep = firstField.step
      activeMenu.value = firstMissingStep
      const stepName = stepNames[firstMissingStep] || '对应步骤'
      ElMessage.info(`请补充${stepName}中的必填项`)
    }
  }).catch(() => {
    ElMessage.info('您可以稍后通过左侧菜单补充信息')
  })
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
  if (parsedFormData.major && Array.isArray(parsedFormData.major)) {
    formData.major = parsedFormData.major
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
    formData.codeAbility.links = parsedFormData.codeAbility?.links || parsedFormData.codeLinks || ''
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

  // 填充素质测评分数
  if (parsedFormData.quizScores && typeof parsedFormData.quizScores === 'object') {
    formData.quizScores = {
      communication: parsedFormData.quizScores.communication || 0,
      stress: parsedFormData.quizScores.stress || 0,
      learning: parsedFormData.quizScores.learning || 0
    }
    // 如果分数大于0，标记对应测评为已完成
    quizCompleted.communication = !!parsedFormData.quizScores.communication
    quizCompleted.stress = !!parsedFormData.quizScores.stress
    quizCompleted.learning = !!parsedFormData.quizScores.learning
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
<<<<<<< HEAD
const handleResumeParsed = (parsedData: unknown) => {
=======
const handleResumeParsed = async (parsedData: any) => {
  console.log('简历解析结果:', parsedData);
  formData.value = parsedData.value
>>>>>>> 5c07dc6 (修改代码)
  hasUploadedResume.value = true
  showUploadDialog.value = false

<<<<<<< HEAD
  const formDataFromResume = parsedData as Record<string, unknown> | null
  if (!formDataFromResume) {
    ElMessage.warning('简历解析结果为空，请手动填写表单')
=======
  // 将解析出的技能添加到技能列表，默认熟练度70
  if (parsedData?.profile?.skills && parsedData.profile.skills.length > 0) {
    parsedData.profile.skills.forEach((skill: string) => {
      if (!formData.value.skills.find(s => s.name === skill)) {
        formData.value.skills.push({ name: skill, credibility: 70 })
      }
    })
  }

  // 情况1: 如果后端直接返回了 abilityScores，直接展示
  if (parsedData?.abilityScores) {
    Object.assign(radarScores, parsedData.abilityScores)
    showRadarDialog.value = true
    ElMessage.success('简历能力评估报告已生成！')
>>>>>>> 5c07dc6 (修改代码)
    return
  }

  fillFormWithParsedData(formDataFromResume)
  ElMessage.success('简历解析成功！已自动填充表单信息')

  // 检查并提示缺失的必填字段
  const missingFields = checkRequiredFields()
  if (missingFields.length > 0) {
    setTimeout(() => showMissingFieldsReminder(missingFields), 500)
  }
}

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
      const hasValidLanguage = value.some(l => l.type && l.level)
      if (!hasValidLanguage) {
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
    const submitData = convertToSubmitDTO(formData)
    const res = await submitCareerFormApi(submitData)

    if (res.data?.code !== 200) {
      ElMessage.error(res.data?.msg || '提交失败，请稍后重试')
      return
    }

    const matchResult = res.data.data as JobMatchItem[]
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
<<<<<<< HEAD
  formData.languages = [{ type: '', level: '', other: '' }]
  formData.certificates = []
  formData.certificateOther = ''
  formData.skills = []
  formData.tools = []
  formData.projects = []
  formData.internships = []
  formData.quizScores = { communication: 0, stress: 0, learning: 0 }
  quizCompleted.communication = false
  quizCompleted.stress = false
  quizCompleted.learning = false
  formData.priorities = [
=======
  formData.value.languages = [{ type: '', level: '', other: '' }]
  formData.value.certificates = []
  formData.value.certificateOther = ''
  formData.value.skills = []
  formData.value.tools = []
  formData.value.projects = []
  formData.value.internships = []
  formData.value.scores = { communication: false, stress: false, learning: false }
  formData.value.priorities = [
>>>>>>> 5c07dc6 (修改代码)
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

  ElMessage.success('表单已重置')
}
</script>



<template>
  <div class="career-form-layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="220px" class="sidebar">
        <div class="sidebar-brand">
          <div class="brand-icon">
            <el-icon :size="26">
              <DocumentAdd />
            </el-icon>
          </div>
          <div class="brand-info">
            <div class="brand-text">能力画像</div>
            <div class="brand-subtitle">就业规划系统</div>
          </div>
        </div>

        <!-- 进度概览 -->
        <div class="progress-overview">
          <div class="progress-text">
            <span>完成度</span>
            <span class="progress-percent">{{ formProgress }}%</span>
          </div>
          <el-progress :percentage="formProgress" :show-text="false" :stroke-width="6" class="sidebar-progress" />
        </div>

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

        <!-- 简历上传入口 -->
        <div class="resume-upload-section">
          <div class="upload-label">
          </div>
          <el-button class="upload-btn" :type="hasUploadedResume ? 'info' : 'primary'" @click="showUploadDialog = true"
            :icon="hasUploadedResume ? CircleCheck : Upload">
            {{ hasUploadedResume ? '已上传简历' : '上传简历' }}
          </el-button>
        </div>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <el-card class="form-card">
          <template #header>
            <div class="card-header">
              <div class="title-section">
                <h2>{{ currentSectionTitle }}</h2>
                <p class="subtitle">第 {{ activeMenu }} 步，共 5 步</p>
              </div>
              <div class="progress-section">
                <span class="progress-label">完成度 {{ formProgress }}%</span>
                <el-progress :percentage="formProgress" :stroke-width="8" :show-text="false" class="progress-bar" />
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
<<<<<<< HEAD
                    <el-select
                      v-model="formData.education"
                      placeholder="请选择最高学历"
                      style="width: 100%"
                      @change="handleEducationChange"
                      clearable
                    >
=======
                    <el-select v-model="formData.education" placeholder="请选择最高学历" style="width: 100%"
                      @change="handleEducationChange" clearable>
>>>>>>> 5c07dc6 (修改代码)
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
<<<<<<< HEAD
                    <el-input
                      v-model="formData.educationOther"
                      placeholder="如：MBA、双学位等"
                      clearable
                    />
=======
                    <el-input v-model="formData.educationOther" placeholder="如：MBA、双学位等" clearable />
>>>>>>> 5c07dc6 (修改代码)
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
<<<<<<< HEAD
                  <div
                    v-for="(lang, index) in formData.languages"
                    :key="index"
                    class="list-row"
                  >
                    <el-select
                      v-model="lang.type"
                      placeholder="语种"
                      style="width: 130px"
                    >
=======
                  <div v-for="(lang, index) in formData.languages" :key="index" class="list-row">
                    <el-select v-model="lang.type" placeholder="语种" style="width: 130px">
>>>>>>> 5c07dc6 (修改代码)
                      <el-option label="英语" value="英语" />
                      <el-option label="日语" value="日语" />
                      <el-option label="其他" value="其他" />
                    </el-select>
<<<<<<< HEAD
                    <el-select
                      v-model="lang.level"
                      placeholder="水平"
                      style="width: 130px"
                      :disabled="lang.type === ''"
                    >
=======
                    <el-select v-model="lang.level" placeholder="水平" style="width: 130px"
                      :disabled="lang.type === '其他' || lang.type === ''">
>>>>>>> 5c07dc6 (修改代码)
                      <el-option label="四级" value="四级" />
                      <el-option label="六级" value="六级" />
                      <el-option label="托福/雅思" value="托福/雅思" />
                      <el-option label="其他" value="其他" />
                    </el-select>
<<<<<<< HEAD
                    <!-- 语种选择"其他"时的自定义输入 -->
                    <template v-if="lang.type === '其他'">
                      <el-input
                        v-model="lang.other"
                        placeholder="请输入语种"
                        style="width: 150px"
                      />
                      <el-button
                        type="primary"
                        size="small"
                        @click="confirmCustomLanguage(index, 'type')"
                      >
                        确认
                      </el-button>
                    </template>
                    <!-- 水平选择"其他"时的自定义输入 -->
                    <template v-else-if="lang.level === '其他'">
                      <el-input
                        v-model="lang.other"
                        placeholder="请输入证书"
                        style="width: 150px"
                      />
                      <el-button
                        type="primary"
                        size="small"
                        @click="confirmCustomLanguage(index, 'level')"
                      >
                        确认
                      </el-button>
                    </template>
=======
                    <el-input v-if="lang.type === '其他'" v-model="lang.other" placeholder="请输入语种"
                      style="width: 200px; flex: 1" />
                    <el-input v-else-if="lang.level === '其他'" v-model="lang.other" placeholder="请输入证书"
                      style="width: 200px; flex: 1" />
>>>>>>> 5c07dc6 (修改代码)
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
<<<<<<< HEAD
                    <el-progress
                      :percentage="skill.score || 0"
                      status="success"
                      style="width: 120px"
                      :stroke-width="8"
                    />
=======
                    <el-progress :percentage="skill.credibility" status="success" style="width: 120px"
                      :stroke-width="8" />
>>>>>>> 5c07dc6 (修改代码)
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

<<<<<<< HEAD
              <!-- 代码能力 -->
              <el-form-item
                label="代码能力"
                prop="codeAbility"
              >
                <div class="code-ability-row">
                  <el-input
                    v-model="formData.codeAbility.links"
                    placeholder="GitHub/Gitee 链接，多个用逗号分隔"
                    style="flex: 1"
                  />
                  <el-button
                    type="warning"
                    @click="openQuizModal('code')"
                    :icon="DataAnalysis"
                  >
=======
              <!-- 代码能力 (动态显示) -->
              <el-form-item label="代码能力" prop="codeAbility" v-if="isComputerMajor">
                <div class="code-ability-row">
                  <el-input v-model="formData.codeAbility.links" placeholder="GitHub/Gitee 链接，多个用逗号分隔"
                    style="flex: 1" />
                  <el-button type="warning" @click="openTestModal('code')" :icon="DataAnalysis">
>>>>>>> 5c07dc6 (修改代码)
                    AI 测试
                  </el-button>
                </div>
              </el-form-item>
            </div>

            <!-- 3. 经历与项目 -->
            <div v-show="activeMenu === '3'" class="section-content">
              <div class="form-section-title">项目经历</div>
              <el-form-item label="项目或竞赛">
                <div class="experience-list">
                  <div v-for="(proj, index) in formData.projects" :key="index" class="experience-card"
                    :class="{ 'is-competition': proj.isCompetition }">
                    <div class="experience-card-header">
                      <div class="experience-type-badge">
                        <el-icon v-if="proj.isCompetition">
                          <Trophy />
                        </el-icon>
                        <el-icon v-else>
                          <Folder />
                        </el-icon>
                        <span>{{ proj.isCompetition ? '竞赛' : '项目' }}</span>
                      </div>
                      <div class="card-actions">
                        <el-button text type="primary" :icon="Edit" @click="openEditProjectDialog(index)">
                          编辑
                        </el-button>
                        <el-button text type="danger" :icon="Delete" @click="removeProject(index)">
                          删除
                        </el-button>
                      </div>
                    </div>
                    <div class="experience-card-body preview-mode">
                      <h4 class="preview-title">{{ proj.name }}</h4>
                      <p class="preview-desc" v-if="proj.desc">{{ proj.desc }}</p>
                    </div>
                  </div>
                </div>
                <el-button class="add-experience-btn" type="primary" plain :icon="Plus" @click="openProjectDialog">
                  <span class="btn-text">添加项目/竞赛</span>
                  <span class="btn-hint">记录你的精彩作品</span>
                </el-button>
              </el-form-item>

              <div class="form-section-title">实践经历</div>
              <el-form-item label="实习/工作" prop="internships">
                <div class="experience-list">
                  <div v-for="(intern, index) in formData.internships" :key="index"
                    class="experience-card internship-card">
                    <div class="experience-card-header">
                      <div class="experience-type-badge work-badge">
                        <el-icon>
                          <Briefcase />
                        </el-icon>
                        <span>工作/实习</span>
                      </div>
                      <div class="card-actions">
                        <el-button text type="primary" :icon="Edit" @click="openEditInternshipDialog(index)">
                          编辑
                        </el-button>
                        <el-button text type="danger" :icon="Delete" @click="removeInternship(index)">
                          删除
                        </el-button>
                      </div>
                    </div>
                    <div class="experience-card-body preview-mode">
                      <div class="info-row">
                        <span class="info-company">{{ intern.company }}</span>
                        <span class="info-role">{{ intern.role }}</span>
                      </div>
                      <div class="info-date" v-if="intern.date && intern.date.length === 2">
                        {{ formatDateRange(intern.date) }}
                      </div>
                      <p class="preview-desc" v-if="intern.desc">{{ intern.desc }}</p>
                    </div>
                  </div>
                </div>
                <el-button class="add-experience-btn" type="primary" plain :icon="Plus" @click="openInternshipDialog">
                  <span class="btn-text">添加实践经历</span>
                  <span class="btn-hint">丰富你的职场履历</span>
                </el-button>
              </el-form-item>
            </div>

            <!-- 4. 素质测评 -->
            <div v-show="activeMenu === '4'" class="section-content">
              <div class="form-section-title">能力测评</div>
              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="沟通能力">
<<<<<<< HEAD
                    <el-button
                      :type="quizCompleted.communication ? 'success' : 'default'"
                      :class="quizCompleted.communication ? 'quiz-complete' : 'quiz-pending'"
                      @click="!quizCompleted.communication && openQuizModal('communication')"
                    >
                      <el-icon v-if="quizCompleted.communication"><Check /></el-icon>
                      {{ quizCompleted.communication ? '已完成' : '开始测试' }}
=======
                    <el-button :type="formData.scores.communication ? 'success' : 'default'"
                      :class="formData.scores.communication ? 'quiz-complete' : 'quiz-pending'"
                      @click="openQuizModal('communication')">
                      <el-icon v-if="formData.scores.communication">
                        <Check />
                      </el-icon>
                      {{ formData.scores.communication ? '已完成' : '开始测试' }}
>>>>>>> 5c07dc6 (修改代码)
                    </el-button>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="抗压能力">
<<<<<<< HEAD
                    <el-button
                      :type="quizCompleted.stress ? 'success' : 'default'"
                      :class="quizCompleted.stress ? 'quiz-complete' : 'quiz-pending'"
                      @click="!quizCompleted.stress && openQuizModal('stress')"
                    >
                      <el-icon v-if="quizCompleted.stress"><Check /></el-icon>
                      {{ quizCompleted.stress ? '已完成' : '开始测试' }}
=======
                    <el-button :type="formData.scores.stress ? 'success' : 'default'"
                      :class="formData.scores.stress ? 'quiz-complete' : 'quiz-pending'"
                      @click="openQuizModal('stress')">
                      <el-icon v-if="formData.scores.stress">
                        <Check />
                      </el-icon>
                      {{ formData.scores.stress ? '已完成' : '开始测试' }}
>>>>>>> 5c07dc6 (修改代码)
                    </el-button>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="学习能力">
<<<<<<< HEAD
                    <el-button
                      :type="quizCompleted.learning ? 'success' : 'default'"
                      :class="quizCompleted.learning ? 'quiz-complete' : 'quiz-pending'"
                      @click="!quizCompleted.learning && openQuizModal('learning')"
                    >
                      <el-icon v-if="quizCompleted.learning"><Check /></el-icon>
                      {{ quizCompleted.learning ? '已完成' : '开始测试' }}
=======
                    <el-button :type="formData.scores.learning ? 'success' : 'default'"
                      :class="formData.scores.learning ? 'quiz-complete' : 'quiz-pending'"
                      @click="openQuizModal('learning')">
                      <el-icon v-if="formData.scores.learning">
                        <Check />
                      </el-icon>
                      {{ formData.scores.learning ? '已完成' : '开始测试' }}
>>>>>>> 5c07dc6 (修改代码)
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
              <el-button @click="resetForm" :icon="RefreshRight">
                重置表单
              </el-button>
              <el-button type="primary" @click="submitForm" :loading="submitting" :icon="Check">
                提交画像
              </el-button>
            </div>
          </el-form>

<<<<<<< HEAD
=======
          <!-- 雷达图弹窗组件 -->
          <CareerFormRadar v-model:visible="showRadarDialog" :scores="radarScores" :loading="radarLoading"
            :loading-text="'正在生成能力评估报告...'" :source-type="hasUploadedResume ? 'resume' : 'manual'"
            :completeness="profileCompleteness" :missing-items="missingItems" @jump-to-field="handleJumpToField" />
>>>>>>> 5c07dc6 (修改代码)
        </el-card>
      </el-main>
    </el-container>

<<<<<<< HEAD
    <!-- 素质测评弹窗 - 使用Quenation组件 -->
    <el-dialog
      v-model="testDialog.visible"
      :title="testDialog.title"
      width="800px"
      class="quiz-dialog"
      destroy-on-close
      @close="closeTestDialog"
    >
      <!-- 加载状态 -->
      <div v-if="testDialog.loading" class="quiz-loading">
        <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
        <p>正在加载题目...</p>
        <el-progress :percentage="50" :stroke-width="8" :indeterminate="true" />
      </div>

      <!-- 问卷内容 - 确保数据加载完成后再渲染 -->
      <Quenation
        v-if="backendQuizData"
        ref="quenationRef"
        :title="testDialog.title"
        :quiz-type="testDialog.type"
        :backend-data="backendQuizData"
        :quiz-result="quizResult"
        @submit="handleQuizSubmit"
        @cancel="closeTestDialog"
      />
=======
    <!-- 素质测评弹窗 -->
    <el-dialog v-model="testDialog.visible" :title="testDialog.title" width="600px" class="quiz-dialog"
      destroy-on-close>
      <div v-if="testDialog.type === 'quiz' && testDialog.currentQuestion" class="quiz-content">
        <!-- 不支持的技能提示（只有单个选项时显示为提示信息） -->
        <div v-if="testDialog.currentQuestion.id === -1" class="quiz-unsupported">
          <el-icon :size="48" color="#e6a23c">
            <Warning />
          </el-icon>
          <p class="unsupported-text">{{ testDialog.currentQuestion.question }}</p>
        </div>
        <!-- 正常测试题 -->
        <template v-else>
          <div class="quiz-question">
            <el-tag type="primary" size="small" class="question-tag">单选题</el-tag>
            <p class="question-text">{{ testDialog.currentQuestion.question }}</p>
          </div>
          <el-radio-group v-model="testDialog.answer" class="quiz-options">
            <el-radio v-for="option in testDialog.currentQuestion.options" :key="option.value" :label="option.value"
              class="quiz-option">
              <span class="option-label">{{ option.label }}.</span>
              <span class="option-text">{{ option.text }}</span>
            </el-radio>
          </el-radio-group>
        </template>
      </div>
      <div v-else class="quiz-loading">
        <el-icon class="loading-icon" :size="48">
          <Loading />
        </el-icon>
        <p>AI 正在生成测试题...</p>
        <el-progress :percentage="testDialog.progress" :stroke-width="8" />
      </div>
      <template #footer>
        <el-button @click="testDialog.visible = false">
          {{ testDialog.currentQuestion?.id === -1 ? '关闭' : '取消' }}
        </el-button>
        <el-button v-if="testDialog.currentQuestion?.id !== -1" type="primary" @click="confirmTest"
          :disabled="!testDialog.answer">
          提交测试
        </el-button>
      </template>
>>>>>>> 5c07dc6 (修改代码)
    </el-dialog>

    <!-- 简历上传弹窗 -->
    <el-dialog v-model="showUploadDialog" title="简历智能上传" width="650px" destroy-on-close>
      <CareerFormUpload :show-close="true" @close="showUploadDialog = false" @parsed="handleResumeParsed" />
    </el-dialog>

    <!-- 项目经历弹窗 -->
<<<<<<< HEAD
    <el-dialog
      v-model="showProjectDialog"
      :title="projectForm.isEdit ? '编辑项目/竞赛经历' : '添加项目/竞赛经历'"
      width="600px"
      destroy-on-close
      class="experience-dialog"
    >
=======
    <el-dialog v-model="showProjectDialog" title="添加项目/竞赛经历" width="600px" destroy-on-close class="experience-dialog">
>>>>>>> 5c07dc6 (修改代码)
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
<<<<<<< HEAD
    <el-dialog
      v-model="showInternshipDialog"
      :title="internshipForm.isEdit ? '编辑实践经历' : '添加实践经历'"
      width="600px"
      destroy-on-close
      class="experience-dialog"
    >
=======
    <el-dialog v-model="showInternshipDialog" title="添加实践经历" width="600px" destroy-on-close class="experience-dialog">
>>>>>>> 5c07dc6 (修改代码)
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
<<<<<<< HEAD
        <el-button
          type="primary"
          @click="confirmAddInternship"
          :disabled="!internshipForm.company.trim() || !internshipForm.role.trim()"
        >
          {{ internshipForm.isEdit ? '确认修改' : '确认添加' }}
=======
        <el-button type="primary" @click="confirmAddInternship"
          :disabled="!internshipForm.company.trim() || !internshipForm.role.trim()">
          确认添加
>>>>>>> 5c07dc6 (修改代码)
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.career-form-layout {
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
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

.sidebar {
  background: #fff;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  width: 200px !important;
  min-width: 200px !important;
  max-width: 200px !important;
  height: 100%;
  position: relative;
  flex-shrink: 0;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 16px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  background: #409eff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.brand-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-text {
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.brand-subtitle {
  color: #909399;
  font-size: 12px;
  font-weight: 400;
}

/* 进度概览 */
.progress-overview {
  padding: 0 20px 20px;
  margin-bottom: 8px;
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

.sidebar-menu {
  border-right: none;
  background: transparent;
  flex: 1;
  padding: 8px 0;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  padding: 0 16px;
  margin: 2px 12px;
  border-radius: 4px;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: #f5f7fa;
  color: #409eff;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #ecf5ff;
  color: #409eff;
}

.sidebar-menu :deep(.el-menu-item.is-completed) {
  color: #67c23a;
}

.sidebar-menu :deep(.el-menu-item.is-completed:not(.is-active)) {
  background: #f0f9ff;
}

.sidebar-menu :deep(.el-menu-item.is-completed:not(.is-active)):hover {
  background: #ecf5ff;
}

.menu-step {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.sidebar-menu :deep(.el-menu-item.is-active .menu-step) {
  background: #409eff;
  color: #fff;
}

.sidebar-menu :deep(.el-menu-item.is-completed .menu-step) {
  background: #67c23a;
  color: #fff;
}

.menu-text {
  flex: 1;
}

.menu-check {
  font-size: 16px;
  color: #3fb950;
  opacity: 0;
  transform: scale(0);
  transition: all 0.3s ease;
}

.sidebar-menu :deep(.el-menu-item.is-completed .menu-check) {
  opacity: 1;
  transform: scale(1);
}

.resume-upload-section {
  padding: 16px;
  margin: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.upload-label {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 10px;
}

.upload-label .el-icon {
  font-size: 14px;
}

.upload-btn {
  width: 100%;
  border-radius: 4px;
  font-weight: 500;
  font-size: 13px;
  padding: 10px 0;
  background: #67c23a;
  border: none;
  color: #ffffff !important;
  transition: all 0.2s ease;
}

.upload-btn:hover {
  background: #85ce61;
}

/* 已上传简历状态 */
.upload-btn.el-button--info {
  background: #909399;
  border: none;
  color: #ffffff !important;
}

.upload-btn.el-button--info:hover {
  background: #a6a9ad;
}

.upload-tip {
  margin-top: 8px;
  font-size: 11px;
  color: #c0c4cc;
  text-align: center;
  line-height: 1.5;
}

/* 主内容区样式 */
.main-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.form-card {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  border-radius: 4px;
  background: #fff;
  border: 1px solid #e4e7ed;
  height: auto;
  min-height: fit-content;
}

.form-card :deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafbfc;
}

.form-card :deep(.el-card__body) {
  padding: 24px;
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
}

.title-section h2 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
  font-weight: 400;
}

.progress-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.progress-label {
  font-size: 12px;
  color: #595959;
  font-weight: 500;
}

.progress-bar {
  width: 160px;
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

/* 表单内容样式 */
.section-content {
  padding: 8px 0;
}

/* 分组标题 */
.form-section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 24px 0 16px;
  padding-left: 12px;
  border-left: 3px solid #409eff;
  display: flex;
  align-items: center;
  gap: 6px;
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
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
}

.form-tips .el-icon {
  color: #409eff;
  font-size: 16px;
  margin-top: 1px;
  flex-shrink: 0;
}

:deep(.el-form-item__label) {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  padding-right: 16px;
  height: 40px;
  line-height: 40px;
}

/* 输入框样式优化 */
:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.2s ease;
  border-radius: 4px;
}

:deep(.el-input__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #409eff inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

/* 选择器样式 */
:deep(.el-select .el-input__wrapper) {
  border-radius: 4px;
}

:deep(.el-select .el-input__inner::placeholder) {
  color: #c0c4cc;
}

/* 日期选择器 */
:deep(.el-date-editor.el-input__wrapper) {
  border-radius: 4px;
}

:deep(.el-date-editor .el-input__prefix) {
  color: #909399;
}

/* 级联选择器 */
:deep(.el-cascader .el-input__wrapper) {
  border-radius: 4px;
}

:deep(.el-cascader .el-input__suffix) {
  color: #909399;
}

/* 行间距优化 */
.section-content .el-row {
  margin-bottom: 8px;
}

.section-content .el-row:last-child {
  margin-bottom: 0;
}

/* 列表样式 */
.list-container,
.input-list-group {
  width: 100%;
}

.list-row,
.skill-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 10px 14px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  transition: all 0.2s ease;
}

.list-row:last-child,
.skill-item:last-child {
  margin-bottom: 0;
}

.list-row:hover,
.skill-item:hover {
  border-color: #c0c4cc;
  background: #f5f7fa;
}

/* 技能项特殊样式 */
.skill-item {
  justify-content: space-between;
}

.skill-item span {
  font-weight: 500;
  color: #303133;
  flex: 1;
}

/* 项目卡片样式 */
.project-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  /* 统一控制内部间距 */
  padding: 20px;
  background: #fafbfc;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 16px;
}

.project-card:hover {
  border-color: #c0c4cc;
}

.project-card .el-input,
.project-card .el-textarea {
  width: 100%;
}

.project-card :deep(.el-input__wrapper),
.project-card :deep(.el-textarea__inner) {
  background: #fff;
  border-radius: 10px;
}

/* 项目卡片头部 */
.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed #dcdfe6;
  padding-bottom: 16px;
  /* 这个 padding 不影响外部间距，因为 gap 已经处理了 */
}

/* 项目操作区 */
.project-actions {
  display: flex;
  justify-content: flex-end;
  width: 500px;
  /* 不需要额外样式 */
}

/* 实习经历行 */
.internship-row {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

/* 项目卡片内的 Switch */
.project-card .el-switch {
  --el-switch-core-border-radius: 10px;
}

.project-card .el-switch__label {
  font-weight: 500;
}

/* 日期选择器在项目卡片内 */
.project-card .el-date-editor {
  width: 100% !important;
}

.project-card .el-date-editor .el-input__wrapper {
  border-radius: 4px;
}

/* 按钮样式 */
:deep(.el-button--primary) {
  background: #409eff;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  font-size: 14px;
  color: #ffffff !important;
  transition: all 0.2s ease;
}

:deep(.el-button--primary:hover) {
  background: #66b1ff;
  color: #ffffff !important;
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

:deep(.el-button.is-text) {
  border-radius: 4px;
  transition: all 0.2s ease;
  color: #409eff;
  font-weight: 500;
}

:deep(.el-button.is-text:hover) {
  background: #ecf5ff;
  color: #409eff;
}

/* 危险操作文字按钮 */
:deep(.el-button.is-text.el-button--danger) {
  color: #f56c6c;
}

:deep(.el-button.is-text.el-button--danger:hover) {
  background: rgba(245, 108, 108, 0.1);
  color: #ff4d4f;
}

.upload-inline {
  display: inline-block;
}

/* ========== 发展优先级样式 - 卡片式设计 ========== */

.priority-container {
  background: #fafbfc;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e4e7ed;
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
  border-radius: 12px;
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: grab;
  user-select: none;
  position: relative;
  overflow: hidden;
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
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.form-actions .el-button {
  padding: 10px 28px;
  font-size: 14px;
  border-radius: 4px;
  min-width: 100px;
  font-weight: 500;
  transition: all 0.2s ease;
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
}

/* 技能名称 */
.skill-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
  min-width: 80px;
}

/* 技能操作按钮组 */
.skill-actions {
  display: flex;
  gap: 4px;
}

/* 代码能力行 */
.code-ability-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.code-ability-row .el-button {
  border-radius: 4px;
  padding: 8px 16px;
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
<<<<<<< HEAD

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

</style>
=======
</style>
>>>>>>> 5c07dc6 (修改代码)
