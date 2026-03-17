<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
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
  Rank
} from '@element-plus/icons-vue'
import CareerFormUpload from '@/components/CareerForm_Upload.vue'
import { submitCareerFormApi, convertToSubmitDTO } from '@/api/career-form/formdata'
import type { CareerFormData } from '@/types/type'


// --- 状态定义 ---

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
  /** 素质测评完成状态：沟通/抗压/学习能力 */
  scores: { communication: false, stress: false, learning: false },
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


/**
 * 判断用户是否选择了计算机相关专业
 * 用于显示/隐藏代码能力相关表单项
 */
const isComputerMajor = computed(() => {
  const majorStr = JSON.stringify(formData.major)
  return majorStr.includes('计算机') || majorStr.includes('软件')
})

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
      return !!(formData.education && formData.major.length > 0)
    case 2:
      return !!(formData.skills.length > 0 || formData.certificates.length > 0)
    case 3:
      return !!(formData.projects.length > 0 || formData.internships.length > 0)
    case 4:
      return !!(formData.scores.communication && formData.scores.stress && formData.scores.learning && formData.innovation)
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
const majorOptions = [
 {
    "value": "计算机类",
    "label": "计算机类",
    "children": [
      { "value": "软件工程", "label": "软件工程" },
      { "value": "计算机科学与技术", "label": "计算机科学与技术" },
      { "value": "网络工程", "label": "网络工程" },
      { "value": "信息安全", "label": "信息安全" },
      { "value": "物联网工程", "label": "物联网工程" },
      { "value": "数字媒体技术", "label": "数字媒体技术" },
      { "value": "智能科学与技术", "label": "智能科学与技术" },
      { "value": "空间信息与数字技术", "label": "空间信息与数字技术" },
      { "value": "电子与计算机工程", "label": "电子与计算机工程" },
      { "value": "数据科学与大数据技术", "label": "数据科学与大数据技术" },
      { "value": "网络空间安全", "label": "网络空间安全" },
      { "value": "新媒体技术", "label": "新媒体技术" },
      { "value": "电影制作", "label": "电影制作" },
      { "value": "保密技术", "label": "保密技术" },
      { "value": "服务科学与工程", "label": "服务科学与工程" },
      { "value": "虚拟现实技术", "label": "虚拟现实技术" },
      { "value": "区块链工程", "label": "区块链工程" },
      { "value": "密码科学与技术", "label": "密码科学与技术" }
    ]
  },
  {
    "value": "电子信息类",
    "label": "电子信息类",
    "children": [
      { "value": "电子信息工程", "label": "电子信息工程" },
      { "value": "电子科学与技术", "label": "电子科学与技术" },
      { "value": "通信工程", "label": "通信工程" },
      { "value": "微电子科学与工程", "label": "微电子科学与工程" },
      { "value": "光电信息科学与工程", "label": "光电信息科学与工程" },
      { "value": "信息工程", "label": "信息工程" },
      { "value": "广播电视工程", "label": "广播电视工程" },
      { "value": "水声工程", "label": "水声工程" },
      { "value": "电子封装技术", "label": "电子封装技术" },
      { "value": "集成电路设计与集成系统", "label": "集成电路设计与集成系统" },
      { "value": "医学信息工程", "label": "医学信息工程" },
      { "value": "电磁场与无线技术", "label": "电磁场与无线技术" },
      { "value": "电波传播与天线", "label": "电波传播与天线" },
      { "value": "电子信息科学与技术", "label": "电子信息科学与技术" },
      { "value": "电信工程及管理", "label": "电信工程及管理" },
      { "value": "应用电子技术教育", "label": "应用电子技术教育" },
      { "value": "人工智能", "label": "人工智能" },
      { "value": "海洋信息工程", "label": "海洋信息工程" },
      { "value": "柔性电子学", "label": "柔性电子学" },
      { "value": "智能测控工程", "label": "智能测控工程" }
    ]
  },
  {
    "value": "自动化类",
    "label": "自动化类",
    "children": [
      { "value": "自动化", "label": "自动化" },
      { "value": "轨道交通信号与控制", "label": "轨道交通信号与控制" },
      { "value": "机器人工程", "label": "机器人工程" },
      { "value": "邮政工程", "label": "邮政工程" },
      { "value": "核电技术与控制工程", "label": "核电技术与控制工程" },
      { "value": "智能装备与系统", "label": "智能装备与系统" },
      { "value": "工业智能", "label": "工业智能" },
      { "value": "智能工程与创意设计", "label": "智能工程与创意设计" }
    ]
  },
  {
    "value": "数学类",
    "label": "数学类",
    "children": [
      { "value": "数学与应用数学", "label": "数学与应用数学" },
      { "value": "信息与计算科学", "label": "信息与计算科学" },
      { "value": "数理基础科学", "label": "数理基础科学" },
      { "value": "数据计算及应用", "label": "数据计算及应用" }
    ]
  },
  {
    "value": "统计学类",
    "label": "统计学类",
    "children": [
      { "value": "统计学", "label": "统计学" },
      { "value": "应用统计学", "label": "应用统计学" },
      { "value": "数据科学", "label": "数据科学" },
      { "value": "生物统计学", "label": "生物统计学" }
    ]
  },
  {
    "value": "集成电路科学与工程类",
    "label": "集成电路科学与工程类",
    "children": [
      { "value": "集成电路设计与集成系统", "label": "集成电路设计与集成系统" }
    ]
  },
  {
    "value": "国家安全学类",
    "label": "国家安全学类",
    "children": [
      { "value": "信息安全", "label": "信息安全" }
    ]
  },
  {
    "value": "交叉工程类",
    "label": "交叉工程类",
    "children": [
      { "value": "碳中和科学与工程", "label": "碳中和科学与工程" },
      { "value": "低空技术与工程", "label": "低空技术与工程" },
      { "value": "智能分子工程", "label": "智能分子工程" },
      { "value": "时空信息工程", "label": "时空信息工程" },
      { "value": "智慧应急", "label": "智慧应急" },
      { "value": "工业软件", "label": "工业软件" }
    ]
  },
  {
    "value": "管理科学与工程类",
    "label": "管理科学与工程类",
    "children": [
      { "value": "信息管理与信息系统", "label": "信息管理与信息系统" },
      { "value": "大数据管理与应用", "label": "大数据管理与应用" },
      { "value": "计算金融", "label": "计算金融" }
    ]
  },
  {
    "value": "电子商务类",
    "label": "电子商务类",
    "children": [
      { "value": "电子商务", "label": "电子商务" },
      { "value": "跨境电子商务", "label": "跨境电子商务" }
    ]
  },
  {
    "value": "物流管理与工程类",
    "label": "物流管理与工程类",
    "children": [
      { "value": "物流工程", "label": "物流工程" }
    ]
  }
]


// --- 方法 ---

/**
 * 处理侧边栏菜单选择事件
 * @param index - 选中的菜单项索引
 */
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
}


/** 添加新的语言能力项 */
const addLanguage = () => formData.languages.push({ type: '', level: '', other: '' })

/** 
 * 移除指定索引的语言能力项
 * @param index - 要移除的项的索引
 */
const removeLanguage = (index: number) => formData.languages.splice(index, 1)


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
 */
const addSkill = () => {
  if (newSkill.value) {
    formData.skills.push({ name: newSkill.value, credibility: 50 })
    newSkill.value = ''
  }
}

/**
 * 移除指定索引的技能
 * @param index - 要移除的技能索引
 */
const removeSkill = (index: number) => formData.skills.splice(index, 1)


/**
 * 添加新工具
 * 将 newTool 输入框的值添加到工具列表，默认熟练程度为"熟练"
 */
const addTool = () => {
  if (newTool.value) {
    formData.tools.push({ name: newTool.value, proficiency: '熟练' })
    newTool.value = ''
  }
}

/**
 * 移除指定索引的工具
 * @param index - 要移除的工具索引
 */
const removeTool = (index: number) => formData.tools.splice(index, 1)


/** 添加新项目经历，默认为非竞赛项目 */
const addProject = () => formData.projects.push({ isCompetition: false, name: '', desc: '' })

/**
 * 移除指定索引的项目经历
 * @param index - 要移除的项目索引
 */
const removeProject = (index: number) => formData.projects.splice(index, 1)


/** 添加新实习经历 */
const addInternship = () => formData.internships.push({ company: '', role: '', date: [], desc: '' })

/**
 * 移除指定索引的实习经历
 * @param index - 要移除的实习索引
 */
const removeInternship = (index: number) => formData.internships.splice(index, 1)


/**
 * 调整职业优先级的排序
 * @param index - 当前项的索引
 * @param direction - 移动方向：-1为上移，1为下移
 */
const movePriority = (index: number, direction: number) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= formData.priorities.length) return
  
  const temp = formData.priorities[index]!
  const target = formData.priorities[newIndex]!
  
  formData.priorities[index] = target
  formData.priorities[newIndex] = temp
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
  const item = formData.priorities.splice(dragIndex.value, 1)[0]!
  formData.priorities.splice(dropIndex, 0, item)
  
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
  /** 测试类型：quiz(测评) / ai(AI生成) */
  type: 'quiz',
  /** 当前题目对象 */
  currentQuestion: null as QuizQuestion | null,
  /** 用户的答案 */
  answer: '',
  /** AI生成进度 (0-100) */
  progress: 0
})

/** 测评题目类型定义 */
interface QuizQuestion {
  id: number
  question: string
  options: { label: string; value: string; text: string }[]
  correctAnswer?: string
}

/** 沟通能力测评题库 */
const communicationQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: '当团队成员之间产生分歧时，你会如何处理？',
    options: [
      { label: 'A', value: 'A', text: '主动协调，倾听各方意见，寻求共识' },
      { label: 'B', value: 'B', text: '保持中立，让团队自行解决' },
      { label: 'C', value: 'C', text: '支持最有说服力的观点' },
      { label: 'D', value: 'D', text: '向上级汇报，请求决策' }
    ]
  },
  {
    id: 2,
    question: '在跨部门协作中，遇到对方不配合的情况，你会？',
    options: [
      { label: 'A', value: 'A', text: '了解对方需求，寻找双赢方案' },
      { label: 'B', value: 'B', text: '坚持原则，按流程推进' },
      { label: 'C', value: 'C', text: '寻求上级介入协调' },
      { label: 'D', value: 'D', text: '暂时搁置，等待时机' }
    ]
  },
  {
    id: 3,
    question: '向领导汇报工作时，你更倾向于？',
    options: [
      { label: 'A', value: 'A', text: '先说结果，再补充关键细节' },
      { label: 'B', value: 'B', text: '按时间顺序详细描述过程' },
      { label: 'C', value: 'C', text: '准备书面材料，让领导自己看' },
      { label: 'D', value: 'D', text: '等领导询问再回答' }
    ]
  },
  {
    id: 4,
    question: '客户提出不合理需求时，你会如何回应？',
    options: [
      { label: 'A', value: 'A', text: '耐心解释，提供替代方案' },
      { label: 'B', value: 'B', text: '直接拒绝，说明原因' },
      { label: 'C', value: 'C', text: '先答应下来，再内部协商' },
      { label: 'D', value: 'D', text: '请示上级如何处理' }
    ]
  },
  {
    id: 5,
    question: '在会议中，你发现有人误解了你的观点，你会？',
    options: [
      { label: 'A', value: 'A', text: '立即澄清，确保理解一致' },
      { label: 'B', value: 'B', text: '会后单独沟通解释' },
      { label: 'C', value: 'C', text: '通过他人转达正确信息' },
      { label: 'D', value: 'D', text: '不解释，用行动证明' }
    ]
  }
]

/** 抗压能力测评题库 */
const stressQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: '面对紧急且困难的任务 deadline，你的应对方式是？',
    options: [
      { label: 'A', value: 'A', text: '立即制定计划，分解任务，加班加点完成' },
      { label: 'B', value: 'B', text: '评估可行性，必要时申请延期或求助' },
      { label: 'C', value: 'C', text: '保持冷静，按部就班推进' },
      { label: 'D', value: 'D', text: '焦虑但强迫自己硬撑完成' }
    ]
  },
  {
    id: 2,
    question: '当工作出现重大失误时，你的第一反应是？',
    options: [
      { label: 'A', value: 'A', text: '立即承认错误，积极寻找补救方案' },
      { label: 'B', value: 'B', text: '分析原因，避免类似问题再次发生' },
      { label: 'C', value: 'C', text: '担心被批评，想办法掩盖' },
      { label: 'D', value: 'D', text: '情绪低落，需要时间恢复' }
    ]
  },
  {
    id: 3,
    question: '连续加班一周后，你会如何调整自己？',
    options: [
      { label: 'A', value: 'A', text: '适当休息，运动放松，保持工作生活平衡' },
      { label: 'B', value: 'B', text: '坚持完成工作，结束后再好好休息' },
      { label: 'C', value: 'C', text: '向领导反映情况，申请调休' },
      { label: 'D', value: 'D', text: '抱怨但继续硬撑' }
    ]
  },
  {
    id: 4,
    question: '面对多方同时施压的情况，你会？',
    options: [
      { label: 'A', value: 'A', text: '按优先级排序，逐一沟通处理' },
      { label: 'B', value: 'B', text: '先处理最紧急的事项' },
      { label: 'C', value: 'C', text: '同时推进所有事项' },
      { label: 'D', value: 'D', text: '感到 overwhelmed，不知从何开始' }
    ]
  },
  {
    id: 5,
    question: '项目失败后，你的态度是？',
    options: [
      { label: 'A', value: 'A', text: '总结经验教训，为下一次做准备' },
      { label: 'B', value: 'B', text: '分析责任归属，明确改进方向' },
      { label: 'C', value: 'C', text: '沮丧一段时间，然后重新振作' },
      { label: 'D', value: 'D', text: '怀疑自己的能力' }
    ]
  }
]

/** 学习能力测评题库 */
const learningQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: '遇到不熟悉的技术领域需要快速上手，你会怎么做？',
    options: [
      { label: 'A', value: 'A', text: '系统学习基础，边学边实践' },
      { label: 'B', value: 'B', text: '直接找相关项目练手，遇到问题再查资料' },
      { label: 'C', value: 'C', text: '请教有经验的同事，快速入门' },
      { label: 'D', value: 'D', text: '阅读官方文档和优质教程' }
    ]
  },
  {
    id: 2,
    question: '学习新技术时，你更喜欢的方式是？',
    options: [
      { label: 'A', value: 'A', text: '看视频教程，跟着做项目' },
      { label: 'B', value: 'B', text: '阅读书籍和文档，深入理解原理' },
      { label: 'C', value: 'C', text: '参加培训课程，系统学习' },
      { label: 'D', value: 'D', text: '加入技术社区，与他人交流学习' }
    ]
  },
  {
    id: 3,
    question: '当学习遇到瓶颈时，你通常会？',
    options: [
      { label: 'A', value: 'A', text: '换个角度思考，尝试不同方法' },
      { label: 'B', value: 'B', text: '暂时放下，过一段时间再回来' },
      { label: 'C', value: 'C', text: '寻求他人帮助，讨论解决方案' },
      { label: 'D', value: 'D', text: '反复练习，直到突破' }
    ]
  },
  {
    id: 4,
    question: '对于技术更新迭代，你的态度是？',
    options: [
      { label: 'A', value: 'A', text: '保持好奇心，主动学习新技术' },
      { label: 'B', value: 'B', text: '等技术成熟稳定后再学习' },
      { label: 'C', value: 'C', text: '根据工作需求选择性学习' },
      { label: 'D', value: 'D', text: '专注于精通现有技术栈' }
    ]
  },
  {
    id: 5,
    question: '如何检验自己是否真正掌握了一项新技术？',
    options: [
      { label: 'A', value: 'A', text: '能独立完成一个实际项目' },
      { label: 'B', value: 'B', text: '能向他人讲解清楚技术原理' },
      { label: 'C', value: 'C', text: '通过相关认证考试' },
      { label: 'D', value: 'D', text: '能解决实际工作中遇到的问题' }
    ]
  }
]

/**
 * 从题库中随机获取一道题目
 * @param questions - 题目数组
 * @returns 随机选中的题目
 */
const getRandomQuestion = (questions: QuizQuestion[]): QuizQuestion => {
  const randomIndex = Math.floor(Math.random() * questions.length)
  return questions[randomIndex]!
}

/** 专业技能题库 - Python */
const pythonQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'Python 中，以下哪个函数用于获取列表的长度？',
    options: [
      { label: 'A', value: 'A', text: 'size()' },
      { label: 'B', value: 'B', text: 'len()' },
      { label: 'C', value: 'C', text: 'length()' },
      { label: 'D', value: 'D', text: 'count()' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 2,
    question: 'Python 中，以下哪个不是可变数据类型？',
    options: [
      { label: 'A', value: 'A', text: 'list' },
      { label: 'B', value: 'B', text: 'dict' },
      { label: 'C', value: 'C', text: 'tuple' },
      { label: 'D', value: 'D', text: 'set' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 3,
    question: 'Python 中，以下哪个关键字用于定义函数？',
    options: [
      { label: 'A', value: 'A', text: 'func' },
      { label: 'B', value: 'B', text: 'def' },
      { label: 'C', value: 'C', text: 'function' },
      { label: 'D', value: 'D', text: 'define' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 4,
    question: 'Python 中，以下哪个方法用于向列表末尾添加元素？',
    options: [
      { label: 'A', value: 'A', text: 'add()' },
      { label: 'B', value: 'B', text: 'append()' },
      { label: 'C', value: 'C', text: 'push()' },
      { label: 'D', value: 'D', text: 'insert()' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 5,
    question: 'Python 中，以下哪个符号用于表示注释？',
    options: [
      { label: 'A', value: 'A', text: '//' },
      { label: 'B', value: 'B', text: '/* */' },
      { label: 'C', value: 'C', text: '#' },
      { label: 'D', value: 'D', text: '--' }
    ],
    correctAnswer: 'C'
  }
]

/** 专业技能题库 - Java */
const javaQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'Java 中，以下哪个关键字用于创建类的实例？',
    options: [
      { label: 'A', value: 'A', text: 'new' },
      { label: 'B', value: 'B', text: 'create' },
      { label: 'C', value: 'C', text: 'instance' },
      { label: 'D', value: 'D', text: 'make' }
    ],
    correctAnswer: 'A'
  },
  {
    id: 2,
    question: 'Java 中，以下哪个不是访问修饰符？',
    options: [
      { label: 'A', value: 'A', text: 'public' },
      { label: 'B', value: 'B', text: 'private' },
      { label: 'C', value: 'C', text: 'protected' },
      { label: 'D', value: 'D', text: 'static' }
    ],
    correctAnswer: 'D'
  },
  {
    id: 3,
    question: 'Java 中，String 类存储在哪个区域？',
    options: [
      { label: 'A', value: 'A', text: '栈内存' },
      { label: 'B', value: 'B', text: '堆内存' },
      { label: 'C', value: 'C', text: '字符串常量池' },
      { label: 'D', value: 'D', text: '方法区' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 4,
    question: 'Java 中，以下哪个接口用于实现列表数据结构？',
    options: [
      { label: 'A', value: 'A', text: 'Set' },
      { label: 'B', value: 'B', text: 'Map' },
      { label: 'C', value: 'C', text: 'List' },
      { label: 'D', value: 'D', text: 'Queue' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 5,
    question: 'Java 中，以下哪个关键字用于处理异常？',
    options: [
      { label: 'A', value: 'A', text: 'throw' },
      { label: 'B', value: 'B', text: 'try-catch' },
      { label: 'C', value: 'C', text: 'throws' },
      { label: 'D', value: 'D', text: '以上都是' }
    ],
    correctAnswer: 'D'
  }
]

/** 专业技能题库 - C++ */
const cppQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'C++ 中，以下哪个符号用于表示指针？',
    options: [
      { label: 'A', value: 'A', text: '&' },
      { label: 'B', value: 'B', text: '*' },
      { label: 'C', value: 'C', text: '@' },
      { label: 'D', value: 'D', text: '%' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 2,
    question: 'C++ 中，以下哪个不是构造函数的特性？',
    options: [
      { label: 'A', value: 'A', text: '与类名相同' },
      { label: 'B', value: 'B', text: '没有返回值' },
      { label: 'C', value: 'C', text: '可以被继承' },
      { label: 'D', value: 'D', text: '可以重载' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 3,
    question: 'C++ 中，以下哪个关键字用于动态内存分配？',
    options: [
      { label: 'A', value: 'A', text: 'malloc' },
      { label: 'B', value: 'B', text: 'new' },
      { label: 'C', value: 'C', text: 'alloc' },
      { label: 'D', value: 'D', text: 'create' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 4,
    question: 'C++ 中，以下哪个概念用于实现运行时多态？',
    options: [
      { label: 'A', value: 'A', text: '函数重载' },
      { label: 'B', value: 'B', text: '运算符重载' },
      { label: 'C', value: 'C', text: '虚函数' },
      { label: 'D', value: 'D', text: '模板' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 5,
    question: 'C++ 中，以下哪个容器属于 STL 标准库？',
    options: [
      { label: 'A', value: 'A', text: 'ArrayList' },
      { label: 'B', value: 'B', text: 'vector' },
      { label: 'C', value: 'C', text: 'LinkedList' },
      { label: 'D', value: 'D', text: 'HashMap' }
    ],
    correctAnswer: 'B'
  }
]

/** 工具题库 - Git */
const gitQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'Git 中，以下哪个命令用于将文件添加到暂存区？',
    options: [
      { label: 'A', value: 'A', text: 'git commit' },
      { label: 'B', value: 'B', text: 'git add' },
      { label: 'C', value: 'C', text: 'git push' },
      { label: 'D', value: 'D', text: 'git pull' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 2,
    question: 'Git 中，以下哪个命令用于创建新的分支？',
    options: [
      { label: 'A', value: 'A', text: 'git branch <branch-name>' },
      { label: 'B', value: 'B', text: 'git checkout <branch-name>' },
      { label: 'C', value: 'C', text: 'git merge <branch-name>' },
      { label: 'D', value: 'D', text: 'git switch <branch-name>' }
    ],
    correctAnswer: 'A'
  },
  {
    id: 3,
    question: 'Git 中，以下哪个命令用于查看当前仓库的状态？',
    options: [
      { label: 'A', value: 'A', text: 'git log' },
      { label: 'B', value: 'B', text: 'git status' },
      { label: 'C', value: 'C', text: 'git diff' },
      { label: 'D', value: 'D', text: 'git show' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 4,
    question: 'Git 中，以下哪个命令用于将本地提交推送到远程仓库？',
    options: [
      { label: 'A', value: 'A', text: 'git commit' },
      { label: 'B', value: 'B', text: 'git merge' },
      { label: 'C', value: 'C', text: 'git push' },
      { label: 'D', value: 'D', text: 'git fetch' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 5,
    question: 'Git 中，以下哪个命令用于切换分支？',
    options: [
      { label: 'A', value: 'A', text: 'git branch' },
      { label: 'B', value: 'B', text: 'git checkout' },
      { label: 'C', value: 'C', text: 'git merge' },
      { label: 'D', value: 'D', text: 'git stash' }
    ],
    correctAnswer: 'B'
  }
]

/** 工具题库 - Docker */
const dockerQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'Docker 中，以下哪个命令用于运行一个容器？',
    options: [
      { label: 'A', value: 'A', text: 'docker build' },
      { label: 'B', value: 'B', text: 'docker run' },
      { label: 'C', value: 'C', text: 'docker create' },
      { label: 'D', value: 'D', text: 'docker start' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 2,
    question: 'Docker 中，以下哪个命令用于查看正在运行的容器？',
    options: [
      { label: 'A', value: 'A', text: 'docker ps' },
      { label: 'B', value: 'B', text: 'docker images' },
      { label: 'C', value: 'C', text: 'docker list' },
      { label: 'D', value: 'D', text: 'docker show' }
    ],
    correctAnswer: 'A'
  },
  {
    id: 3,
    question: 'Docker 中，用于构建镜像的文件通常叫什么名字？',
    options: [
      { label: 'A', value: 'A', text: 'docker.yml' },
      { label: 'B', value: 'B', text: 'Dockerfile' },
      { label: 'C', value: 'C', text: 'docker.conf' },
      { label: 'D', value: 'D', text: 'docker.json' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 4,
    question: 'Docker 中，以下哪个命令用于停止一个正在运行的容器？',
    options: [
      { label: 'A', value: 'A', text: 'docker kill' },
      { label: 'B', value: 'B', text: 'docker stop' },
      { label: 'C', value: 'C', text: 'docker pause' },
      { label: 'D', value: 'D', text: 'docker exit' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 5,
    question: 'Docker 中，以下哪个命令用于从镜像仓库拉取镜像？',
    options: [
      { label: 'A', value: 'A', text: 'docker fetch' },
      { label: 'B', value: 'B', text: 'docker download' },
      { label: 'C', value: 'C', text: 'docker pull' },
      { label: 'D', value: 'D', text: 'docker get' }
    ],
    correctAnswer: 'C'
  }
]

/** 当前测试的技能/工具名称 */
const currentTestSkill = ref('')

/** 当前测试的技能/工具索引 */
const currentTestIndex = ref(-1)

/**
 * 打开技能/工具/代码能力测试弹窗
 * 根据技能名称从对应题库中随机抽取题目，支持 Python/Java/C++
 * @param type - 测试类型：skill(技能) / tool(工具) / code(代码)
 * @param index - 可选，测试项的索引
 */
const openTestModal = (type: string, index?: number) => {
  // 保存当前测试的技能信息
  if (type === 'skill' && index !== undefined) {
    currentTestSkill.value = formData.skills[index]?.name || ''
    currentTestIndex.value = index
  } else if (type === 'tool' && index !== undefined) {
    currentTestSkill.value = formData.tools[index]?.name || ''
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
}


/**
 * 打开素质测评弹窗
 * 根据测评类型从对应题库中随机抽取一道题目
 * @param type - 测评类型：communication(沟通) / stress(抗压) / learning(学习)
 */
const openQuizModal = (type: string) => {
  currentQuizType.value = type
  testDialog.visible = true
  testDialog.type = 'quiz'
  testDialog.answer = ''
  
  // 测评标题映射
  const titles: Record<string, string> = {
    'communication': '沟通能力测评',
    'stress': '抗压能力测评',
    'learning': '学习能力测评'
  }
  
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
  
  testDialog.title = titles[type] || '素质测评'
  testDialog.currentQuestion = getRandomQuestion(questionBank)
}


/**
 * 确认完成测试
 * 验证答案并显示结果，更新技能/工具熟练度
 */
const confirmTest = () => {
  // 检查是否有当前题目
  if (!testDialog.currentQuestion) {
    testDialog.visible = false
    return
  }
  
  // 处理不支持的技能/工具提示
  if (testDialog.currentQuestion.id === -1) {
    testDialog.visible = false
    currentTestSkill.value = ''
    currentTestIndex.value = -1
    return
  }
  
  // 检查是技能测试还是工具测试
  const isSkillTest = formData.skills.some((s, idx) => 
    idx === currentTestIndex.value && s.name.toLowerCase() === currentTestSkill.value.toLowerCase()
  )
  const isToolTest = formData.tools.some((t, idx) => 
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
        if (formData.skills[currentTestIndex.value]) {
          formData.skills[currentTestIndex.value]!.credibility = Math.min(100, 
            (formData.skills[currentTestIndex.value]!.credibility || 50) + 10
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
        const tool = formData.tools[currentTestIndex.value]
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
    formData.scores[currentQuizType.value as keyof typeof formData.scores] = true
    ElMessage.success('测试已完成，结果已记录')
    currentQuizType.value = ''
    return
  }
  
  // 其他测试类型
  testDialog.visible = false
  ElMessage.success('测试已完成')
}


// --- 简历上传处理 ---

/**
 * 处理简历解析完成后的数据
 * 自动将解析出的技能填充到表单中
 * @param parsedData - 简历解析后的数据对象
 */
const handleResumeParsed = (parsedData: any) => {
  hasUploadedResume.value = true
  showUploadDialog.value = false
  ElMessage.success('简历解析成功！已自动填充部分信息')
  
  // 将解析出的技能添加到技能列表，默认熟练度70
  if (parsedData?.skills && parsedData.skills.length > 0) {
    parsedData.skills.forEach((skill: string) => {
      if (!formData.skills.find(s => s.name === skill)) {
        formData.skills.push({ name: skill, credibility: 70 })
      }
    })
  }
}


// --- 岗位联想搜索 ---

/**
 * 目标岗位输入框的联想搜索回调
 * 根据输入内容返回匹配的岗位建议
 * @param queryString - 用户输入的搜索关键字
 * @param cb - 回调函数，用于返回搜索结果
 */
const querySearch = (queryString: string, cb: any) => {
  const results = queryString
    ? ['后端工程师', '前端开发', '后端运维工程师', '产品经理'].filter(i => i.includes(queryString))
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
  /** 技能：必填，变更时触发验证 */
  skills: [{ required: true, message: '请至少添加一项技能', trigger: 'change' }],
  /** 目标岗位：必填，失焦时触发验证 */
  targetJob: [{ required: true, message: '请输入目标岗位', trigger: 'blur' }],
  /** 创新案例：必填，失焦时触发验证 */
  innovation: [{ required: true, message: '请填写创新案例', trigger: 'blur' }]
})


/**
 * 提交表单
 * 验证表单数据，验证通过后调用API提交
 */
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请完善必填信息')
      return
    }
    
    submitting.value = true
    
    try {
      // 转换表单数据为提交格式
      const submitData = convertToSubmitDTO(formData)
      
      // 调用API提交
      const res = await submitCareerFormApi(submitData)
      
      if (res.data.code === 200) {
        ElMessage.success('画像提交成功，正在生成规划报告...')
        
        // 可以在这里处理提交成功的后续逻辑
        // 比如跳转到报告页面或显示任务状态
        const result = res.data.data as { taskId: string; status: string; estimatedTime?: number }
        console.log('任务ID:', result?.taskId)
        
        // 可选：保存任务ID到本地存储，用于后续查询
        if (result?.taskId) {
          localStorage.setItem('careerFormTaskId', result.taskId)
        }
      } else {
        ElMessage.error(res.data.msg || '提交失败，请稍后重试')
      }
    } catch (error: any) {
      console.error('提交表单失败:', error)
      ElMessage.error(error.response?.data?.msg || '网络错误，请稍后重试')
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
  formData.scores = { communication: false, stress: false, learning: false }
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
            <el-icon :size="26"><DocumentAdd /></el-icon>
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
          <el-progress 
            :percentage="formProgress" 
            :show-text="false"
            :stroke-width="6"
            class="sidebar-progress"
          />
        </div>
        
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="1" :class="{ 'is-completed': isStepCompleted(1) }">
            <div class="menu-step">
              <el-icon v-if="isStepCompleted(1)"><Check /></el-icon>
              <span v-else>1</span>
            </div>
            <span class="menu-text">基本信息</span>
            <el-icon class="menu-check" v-if="isStepCompleted(1)"><Circle-Check /></el-icon>
          </el-menu-item>
          
          <el-menu-item index="2" :class="{ 'is-completed': isStepCompleted(2) }">
            <div class="menu-step">
              <el-icon v-if="isStepCompleted(2)"><Check /></el-icon>
              <span v-else>2</span>
            </div>
            <span class="menu-text">技能证书</span>
            <el-icon class="menu-check" v-if="isStepCompleted(2)"><Circle-Check /></el-icon>
          </el-menu-item>
          
          <el-menu-item index="3" :class="{ 'is-completed': isStepCompleted(3) }">
            <div class="menu-step">
              <el-icon v-if="isStepCompleted(3)"><Check /></el-icon>
              <span v-else>3</span>
            </div>
            <span class="menu-text">经历项目</span>
            <el-icon class="menu-check" v-if="isStepCompleted(3)"><Circle-Check /></el-icon>
          </el-menu-item>
          
          <el-menu-item index="4" :class="{ 'is-completed': isStepCompleted(4) }">
            <div class="menu-step">
              <el-icon v-if="isStepCompleted(4)"><Check /></el-icon>
              <span v-else>4</span>
            </div>
            <span class="menu-text">素质测评</span>
            <el-icon class="menu-check" v-if="isStepCompleted(4)"><Circle-Check /></el-icon>
          </el-menu-item>
          
          <el-menu-item index="5" :class="{ 'is-completed': isStepCompleted(5) }">
            <div class="menu-step">
              <el-icon v-if="isStepCompleted(5)"><Check /></el-icon>
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
          <el-button 
            class="upload-btn"
            :type="hasUploadedResume ? 'info' : 'primary'"
            @click="showUploadDialog = true"
            :icon="hasUploadedResume ? CircleCheck : Upload"
          >
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
                <el-progress 
                  :percentage="formProgress" 
                  :stroke-width="8"
                  :show-text="false"
                  class="progress-bar"
                />
              </div>
            </div>
          </template>
          
          <el-form 
            ref="formRef" 
            :model="formData" 
            :rules="formRules" 
            label-width="120px" 
            size="default"
          >
            <!-- 1. 基本信息 -->
            <div v-show="activeMenu === '1'" class="section-content">
              <div class="form-section-title">教育背景</div>
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="最高学历" prop="education">
                    <el-select 
                      v-model="formData.education" 
                      placeholder="请选择最高学历" 
                      style="width: 100%" 
                      @change="handleEducationChange"
                      clearable
                    >
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
                    <el-input 
                      v-model="formData.educationOther" 
                      placeholder="如：MBA、双学位等" 
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="专业类别" prop="major">
                    <el-cascader 
                      v-model="formData.major" 
                      :options="majorOptions" 
                      placeholder="请选择专业类别"
                      style="width: 100%"
                      :props="{ expandTrigger: 'hover' }"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="毕业时间" prop="graduationDate">
                    <el-date-picker 
                      v-model="formData.graduationDate" 
                      type="month" 
                      placeholder="选择毕业年月" 
                      format="YYYY-MM"
                      style="width: 100%"
                      clearable
                    />
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
                      <el-option label="英语" value="英语" />
                      <el-option label="日语" value="日语" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                    <el-select 
                      v-model="lang.level" 
                      placeholder="水平" 
                      style="width: 130px"
                      :disabled="lang.type === '其他' || lang.type === ''"
                    >
                      <el-option label="四级" value="四级" />
                      <el-option label="六级" value="六级" />
                      <el-option label="托福/雅思" value="托福/雅思" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                    <el-input 
                      v-if="lang.type === '其他'" 
                      v-model="lang.other" 
                      placeholder="请输入语种" 
                      style="width: 200px; flex: 1"
                    />
                    <el-input 
                      v-else-if="lang.level === '其他'" 
                      v-model="lang.other" 
                      placeholder="请输入证书" 
                      style="width: 200px; flex: 1"
                    />
                    <el-button text type="danger" :icon="Delete" @click="removeLanguage(index)" />
                  </div>
                  <el-button class="add-item-btn" type="primary" plain :icon="Plus" @click="addLanguage">
                    添加外语
                  </el-button>
                </div>
              </el-form-item>

              <div class="form-section-title">专业证书</div>
              <el-form-item label="核心证书" prop="certificates">
                <el-select 
                  v-model="formData.certificates" 
                  multiple 
                  placeholder="请选择证书" 
                  style="width: 100%" 
                  @change="handleCertificateChange"
                >
                  <el-option label="软考中级" value="软考中级" />
                  <el-option label="软考高级" value="软考高级" />
                  <el-option label="英语六级" value="英语六级" />
                  <el-option label="PMP" value="PMP" />
                  <el-option label="其他" value="其他" />
                </el-select>
                <el-input 
                  v-if="showCertificateInput" 
                  v-model="formData.certificateOther" 
                  placeholder="请输入证书名称，如：CPA、CFA 等" 
                  style="margin-top: 12px"
                />
              </el-form-item>

              <div class="form-section-title">专业技能</div>
              <el-form-item label="专业技能" prop="skills">
                <div class="input-list-group">
                  <div class="add-input-row">
                    <el-input 
                      v-model="newSkill" 
                      placeholder="输入技能（如 Java、Python）" 
                      @keyup.enter="addSkill"
                      style="flex: 1"
                    />
                    <el-button type="primary" :icon="Plus" @click="addSkill">
                      添加
                    </el-button>
                  </div>
                  <div 
                    v-for="(skill, index) in formData.skills" 
                    :key="index" 
                    class="skill-item"
                  >
                    <span class="skill-name">{{ skill.name }}</span>
                    <el-progress 
                      :percentage="skill.credibility" 
                      status="success" 
                      style="width: 120px"
                      :stroke-width="8"
                    />
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
                    <el-input 
                      v-model="newTool" 
                      placeholder="输入工具（如 Git、Docker）" 
                      @keyup.enter="addTool"
                      style="flex: 1"
                    />
                    <el-button type="primary" :icon="Plus" @click="addTool">
                      添加
                    </el-button>
                  </div>
                  <div 
                    v-for="(tool, index) in formData.tools" 
                    :key="index" 
                    class="skill-item"
                  >
                    <span class="skill-name">{{ tool.name }}</span>
                    <div class="skill-actions">
                      <el-button text type="primary" @click="openTestModal('tool', index)">测试</el-button>
                      <el-button text type="danger" :icon="Delete" @click="removeTool(index)" />
                    </div>
                  </div>
                </div>
              </el-form-item>

              <!-- 代码能力 (动态显示) -->
              <el-form-item 
                label="代码能力" 
                prop="codeAbility" 
                v-if="isComputerMajor"
              >
                <div class="code-ability-row">
                  <el-input 
                    v-model="formData.codeAbility.links" 
                    placeholder="GitHub/Gitee 链接，多个用逗号分隔"
                    style="flex: 1"
                  />
                  <el-button 
                    type="warning" 
                    @click="openTestModal('code')"
                    :icon="DataAnalysis"
                  >
                    AI 测试
                  </el-button>
                </div>
              </el-form-item>
            </div>

            <!-- 3. 经历与项目 -->
            <div v-show="activeMenu === '3'" class="section-content">
              <div class="form-section-title">项目经历</div>
              <el-form-item label="项目或竞赛">
                <div 
                  v-for="(proj, index) in formData.projects" 
                  :key="index" 
                  class="project-card"
                >
                  <div class="project-header">
                    <el-switch 
                      v-model="proj.isCompetition" 
                      active-text="竞赛" 
                      inactive-text="项目"
                      inline-prompt
                      style="--el-switch-on-color: #e6a23c; --el-switch-off-color: #409eff"
                    />
                    <el-button text type="danger" :icon="Delete" @click="removeProject(index)">
                      删除
                    </el-button>
                  </div>
                  <el-input 
                    v-model="proj.name" 
                    placeholder="项目名称 / 竞赛名称" 
                    style="flex: 1; min-width: 250px"
                  />
                  <el-input 
                    v-model="proj.desc" 
                    type="textarea" 
                    :rows="3"
                    placeholder="详细描述项目内容、你的职责和取得的成果"
                  />
                  <div class="project-actions">
                    <el-upload action="#" :auto-upload="false" :limit="1" class="upload-inline">
                      <el-button type="info" plain size="small" :icon="Upload">上传附件</el-button>
                    </el-upload>
                  </div>
                </div>
                <el-button class="add-item-btn" type="primary" plain :icon="Plus" @click="addProject">
                  添加项目
                </el-button>
              </el-form-item>

              <div class="form-section-title">实践经历</div>
              <el-form-item label="实习/工作" prop="internships">
                <div 
                  v-for="(intern, index) in formData.internships" 
                  :key="index" 
                  class="project-card"
                >
                  <div class="internship-row">
                    <el-input 
                      v-model="intern.company" 
                      placeholder="公司全称" 
                      style="flex: 2; min-width: 200px"
                    />
                    <el-input 
                      v-model="intern.role" 
                      placeholder="担任岗位" 
                      style="flex: 1; min-width: 150px"
                    />
                    <el-button text type="danger" :icon="Delete" @click="removeInternship(index)">
                      删除
                    </el-button>
                  </div>
                  <el-date-picker 
                    v-model="intern.date" 
                    type="daterange" 
                    range-separator="至" 
                    start-placeholder="开始时间" 
                    end-placeholder="结束时间"
                    style="width: 100%"
                  />
                  <el-input 
                    v-model="intern.desc" 
                    type="textarea" 
                    :rows="4"
                    placeholder="详细描述工作内容、承担的责任和取得的成果"
                  />
                </div>
                <el-button class="add-item-btn" type="primary" plain :icon="Plus" @click="addInternship">
                  添加经历
                </el-button>
              </el-form-item>
            </div>

            <!-- 4. 素质测评 -->
            <div v-show="activeMenu === '4'" class="section-content">
              <div class="form-section-title">能力测评</div>
              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="沟通能力">
                    <el-button 
                      :type="formData.scores.communication ? 'success' : 'default'" 
                      :class="formData.scores.communication ? 'quiz-complete' : 'quiz-pending'"
                      @click="openQuizModal('communication')"
                    >
                      <el-icon v-if="formData.scores.communication"><Check /></el-icon>
                      {{ formData.scores.communication ? '已完成' : '开始测试' }}
                    </el-button>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="抗压能力">
                    <el-button 
                      :type="formData.scores.stress ? 'success' : 'default'" 
                      :class="formData.scores.stress ? 'quiz-complete' : 'quiz-pending'"
                      @click="openQuizModal('stress')"
                    >
                      <el-icon v-if="formData.scores.stress"><Check /></el-icon>
                      {{ formData.scores.stress ? '已完成' : '开始测试' }}
                    </el-button>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="学习能力">
                    <el-button 
                      :type="formData.scores.learning ? 'success' : 'default'" 
                      :class="formData.scores.learning ? 'quiz-complete' : 'quiz-pending'"
                      @click="openQuizModal('learning')"
                    >
                      <el-icon v-if="formData.scores.learning"><Check /></el-icon>
                      {{ formData.scores.learning ? '已完成' : '开始测试' }}
                    </el-button>
                  </el-form-item>
                </el-col>
              </el-row>
              <div class="form-section-title">创新案例</div>
              <el-form-item label="创新思维" prop="innovation">
                <el-input 
                  v-model="formData.innovation" 
                  type="textarea" 
                  :rows="4"
                  placeholder="请填写一个改进案例，如：优化了某算法，效率提升 20%"
                />
              </el-form-item>
            </div>

            <!-- 5. 职业意向 -->
            <div v-show="activeMenu === '5'" class="section-content">
              <div class="form-section-title">求职意向</div>
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="目标岗位" prop="targetJob">
                    <el-autocomplete 
                      v-model="formData.targetJob" 
                      :fetch-suggestions="querySearch" 
                      placeholder="输入意向岗位，如后端工程师"
                      style="width: 100%"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="期望行业" prop="targetIndustries">
                    <el-select 
                      v-model="formData.targetIndustries" 
                      multiple 
                      placeholder="请选择期望行业"
                      style="width: 100%"
                      clearable
                    >
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

              <div class="form-section-title">发展优先级</div>
              <el-form-item label="优先级排序" prop="priorities">
                <div class="priority-desc">请根据你的职业期望，拖拽调整以下因素的优先顺序（第1位为最重要）：</div>
                <div class="sort-list">
                  <div 
                    v-for="(item, index) in formData.priorities" 
                    :key="item.value" 
                    class="sort-item"
                    :class="{ 
                      'is-dragging': dragIndex === index,
                      'is-drag-over': dragOverIndex === index 
                    }"
                    draggable="true"
                    @dragstart="handleDragStart(index)"
                    @dragover="handleDragOver($event, index)"
                    @dragleave="handleDragLeave"
                    @drop="handleDrop(index)"
                    @dragend="handleDragEnd"
                  >
                    <div class="sort-item-left">
                      <el-icon class="drag-handle"><Rank /></el-icon>
                      <span class="sort-number" :class="getPriorityClass(index)">{{ index + 1 }}</span>
                      <span class="sort-label">{{ item.label }}</span>
                    </div>
                    <div class="sort-actions">
                      <el-button 
                        text 
                        :disabled="index === 0" 
                        @click="movePriority(index, -1)"
                        :icon="ArrowUp"
                        title="上移"
                      />
                      <el-button 
                        text 
                        :disabled="index === formData.priorities.length - 1" 
                        @click="movePriority(index, 1)"
                        :icon="ArrowDown"
                        title="下移"
                      />
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
        </el-card>
      </el-main>
    </el-container>

    <!-- 素质测评弹窗 -->
    <el-dialog 
      v-model="testDialog.visible" 
      :title="testDialog.title" 
      width="600px"
      class="quiz-dialog"
      destroy-on-close
    >
      <div v-if="testDialog.type === 'quiz' && testDialog.currentQuestion" class="quiz-content">
        <!-- 不支持的技能提示（只有单个选项时显示为提示信息） -->
        <div v-if="testDialog.currentQuestion.id === -1" class="quiz-unsupported">
          <el-icon :size="48" color="#e6a23c"><Warning /></el-icon>
          <p class="unsupported-text">{{ testDialog.currentQuestion.question }}</p>
        </div>
        <!-- 正常测试题 -->
        <template v-else>
          <div class="quiz-question">
            <el-tag type="primary" size="small" class="question-tag">单选题</el-tag>
            <p class="question-text">{{ testDialog.currentQuestion.question }}</p>
          </div>
          <el-radio-group v-model="testDialog.answer" class="quiz-options">
            <el-radio 
              v-for="option in testDialog.currentQuestion.options" 
              :key="option.value"
              :label="option.value"
              class="quiz-option"
            >
              <span class="option-label">{{ option.label }}.</span>
              <span class="option-text">{{ option.text }}</span>
            </el-radio>
          </el-radio-group>
        </template>
      </div>
      <div v-else class="quiz-loading">
        <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
        <p>AI 正在生成测试题...</p>
        <el-progress :percentage="testDialog.progress" :stroke-width="8" />
      </div>
      <template #footer>
        <el-button @click="testDialog.visible = false">
          {{ testDialog.currentQuestion?.id === -1 ? '关闭' : '取消' }}
        </el-button>
        <el-button 
          v-if="testDialog.currentQuestion?.id !== -1"
          type="primary" 
          @click="confirmTest"
          :disabled="!testDialog.answer"
        >
          提交测试
        </el-button>
      </template>
    </el-dialog>

    <!-- 简历上传弹窗 -->
    <el-dialog 
      v-model="showUploadDialog" 
      title="简历智能上传" 
      width="650px"
      destroy-on-close
    >
      <CareerFormUpload 
        :show-close="true" 
        @close="showUploadDialog = false"
        @parsed="handleResumeParsed"
      />
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
.list-container, .input-list-group {
  width: 100%;
}

.list-row, .skill-item {
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

.list-row:last-child, .skill-item:last-child {
  margin-bottom: 0;
}

.list-row:hover, .skill-item:hover {
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
  gap: 16px;  /* 统一控制内部间距 */
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
  padding-bottom: 16px;  /* 这个 padding 不影响外部间距，因为 gap 已经处理了 */
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

/* 优先级描述 */
.priority-desc {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
  padding-left: 4px;
}

/* 排序列表样式 */
.sort-list {
  border: 1px solid #e4e7ed;
  padding: 12px 16px;
  border-radius: 4px;
  background: #fafbfc;
  max-width: 480px;
}

.sort-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  margin: 4px 0;
  border-radius: 4px;
  font-size: 14px;
  color: #303133;
  transition: all 0.2s ease;
  cursor: grab;
  user-select: none;
}

.sort-item:hover {
  background: #f0f2f5;
}

.sort-item:active {
  cursor: grabbing;
}

.sort-item.is-dragging {
  opacity: 0.5;
  background: #ecf5ff;
  border: 1px dashed #409eff;
}

.sort-item.is-drag-over {
  background: #e6f2ff;
  border: 1px dashed #409eff;
  transform: scale(1.02);
}

.sort-item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drag-handle {
  font-size: 16px;
  color: #c0c4cc;
  cursor: grab;
}

.sort-item:hover .drag-handle {
  color: #909399;
}

.sort-number {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

/* 第1优先级 - 金色高亮 */
.sort-number.priority-first {
  background: #f0f9eb;
  color: #67c23a;
  border: 1px solid #b3e19d;
}

/* 第2优先级 - 蓝色 */
.sort-number.priority-second {
  background: #ecf5ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

/* 第3优先级 - 灰色淡化 */
.sort-number.priority-third {
  background: #f5f7fa;
  color: #909399;
  border: 1px solid #dcdfe6;
}

.sort-label {
  font-weight: 500;
  color: #303133;
}

.sort-actions {
  display: flex;
  gap: 2px;
}

.sort-actions .el-button {
  padding: 6px;
  font-size: 14px;
  border-radius: 4px;
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
.quiz-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.quiz-content {
  min-height: 200px;
}

.quiz-question {
  margin-bottom: 20px;
}

.question-tag {
  margin-bottom: 12px;
}

.question-text {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  line-height: 1.6;
  margin: 0;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: auto;
}

.quiz-option {
  padding: 14px 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin: 0 0 12px 0 !important;
  height: auto;
  display: flex;
  align-items: flex-start;
  gap: 8px; /* 控制圆圈和内容的间距 */
}

/* 重置 Element UI 的内部 flex 布局 */
.quiz-option .el-radio__label {
  display: flex !important;
  align-items: flex-start;
  width: calc(100% - 20px); /* 减去圆圈的宽度 */
  white-space: normal;
  line-height: 1.5;
  padding-left: 4px;
}


.quiz-option:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.quiz-option.is-checked {
  border-color: #409eff;
  background: #ecf5ff;
}

.quiz-option :deep(.el-radio__input) {
  flex-shrink: 0;
  margin-top: 2px;
}

.quiz-option :deep(.el-radio__label) {
  padding-left: 10px;
  white-space: normal;
  line-height: 1.6;
  display: flex;
  align-items: flex-start;
}

.option-label {
  font-weight: 600;
  color: #409eff;
  margin-right: 8px;
  flex-shrink: 0;
  line-height: 1.6;
}

.option-text {
  color: #606266;
  line-height: 1.6;
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
</style>