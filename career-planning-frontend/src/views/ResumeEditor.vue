<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, CircleCheck, Download, Files, RefreshRight, UploadFilled, Warning } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useJsonResumeStore } from '@/stores'
import { loadCareerFormData } from '@/utils/career-runtime'
import { exportManualResumeToWord, exportResumePreviewToPdf } from '@/utils/resume-export'

type ResumeWorkItem = { company: string; position: string; date: string; desc: string }
type ResumeProjectItem = { name: string; tech: string; date: string; desc: string }
type ResumeEditorState = {
  name: string
  title: string
  phone: string
  email: string
  location: string
  education: string
  school: string
  summary: string
  skills: string
  awards: string
  languages: string
  portfolio: string
  work: ResumeWorkItem[]
  projects: ResumeProjectItem[]
}
type ValidationError = { field: string; label: string; message: string }

const router = useRouter()
const jsonResumeStore = useJsonResumeStore()
const previewRef = ref<HTMLElement | null>(null)
const exportingPdf = ref(false)
const exportingWord = ref(false)
const templateDialogVisible = ref(false)
const validationDialogVisible = ref(false)
const pendingExportAction = ref<'pdf' | 'word' | null>(null)
const activeTab = ref<'basic' | 'work' | 'project' | 'other'>('basic')
const selectedTemplate = ref<'professional' | 'modern' | 'compact'>('professional')
const validationErrors = ref<ValidationError[]>([])
const completenessScore = ref(0)
const workExpanded = ref([true, true])
const projectExpanded = ref([true, true])

// 标签页完成状态检查
const isTabCompleted = (tab: string) => {
  switch (tab) {
    case 'basic':
      return hasText(form.name) && hasText(form.phone) && hasText(form.email) &&
             hasText(form.school) && hasText(form.education)
    case 'work':
      return works.value.length > 0
    case 'project':
      return projects.value.length > 0
    case 'other':
      return hasText(form.awards) || hasText(form.languages) || hasText(form.portfolio)
    default:
      return false
  }
}

// 切换工作经历展开状态
const toggleWorkExpand = (index: number) => {
  workExpanded.value[index] = !workExpanded.value[index]
}

// 切换项目经验展开状态
const toggleProjectExpand = (index: number) => {
  projectExpanded.value[index] = !projectExpanded.value[index]
}

const form = reactive<ResumeEditorState>({
  name: '', title: '', phone: '', email: '', location: '', education: '', school: '', summary: '',
  skills: '', awards: '', languages: '', portfolio: '',
  work: [{ company: '', position: '', date: '', desc: '' }, { company: '', position: '', date: '', desc: '' }],
  projects: [{ name: '', tech: '', date: '', desc: '' }, { name: '', tech: '', date: '', desc: '' }]
})

const demo: ResumeEditorState = {
  name: '张三', title: 'Java 后端开发工程师', phone: '13800000000', email: 'zhangsan@example.com', location: '广州',
  education: '本科 / 计算机科学与技术', school: '华南理工大学',
  summary: '3 年 Java 后端开发经验，熟悉 Spring 生态体系，具备高并发系统设计与优化能力。主导过多个核心系统的架构设计与开发，对微服务、分布式系统有较深入理解。',
  skills: 'Java, Spring Boot, Spring Cloud, MySQL, Redis, Kafka, Docker, Vue.js',
  awards: '优秀员工（2023）\n技术创新奖（2022）\nACM 程序设计竞赛省二等奖',
  languages: '英语 CET-6\n普通话二级甲等', portfolio: 'github.com/zhangsan',
  work: [
    { company: '某科技有限公司', position: '高级 Java 开发工程师', date: '2022.06 - 至今', desc: '- 负责核心交易系统的架构升级与性能优化\n- 主导微服务拆分项目，完成关键服务治理\n- 设计并实现分布式缓存方案，提高系统稳定性' },
    { company: '某互联网公司', position: 'Java 开发工程师', date: '2020.07 - 2022.05', desc: '- 参与电商后台管理系统开发，负责订单、库存模块\n- 使用 Redis 实现秒杀功能\n- 优化慢 SQL 与接口响应性能' }
  ],
  projects: [
    { name: '分布式电商交易系统', tech: 'Spring Cloud, MySQL, Redis, RocketMQ', date: '2023.01 - 2023.06', desc: '- 项目背景：支撑业务快速增长，重构交易链路\n- 核心职责：负责下单、支付、库存扣减流程设计与实现\n- 项目成果：高峰期保持稳定，系统可用性显著提升' },
    { name: '智能客服系统', tech: 'Spring Boot, WebSocket, NLP', date: '2022.07 - 2022.12', desc: '- 项目背景：降低人工客服成本，提升响应效率\n- 核心职责：设计会话管理模块，对接第三方 NLP 服务\n- 项目成果：自动回复准确率提升，人工压力明显下降' }
  ]
}

const trim = (v: unknown) => typeof v === 'string' ? v.trim() : ''
const hasText = (v: unknown) => trim(v).length > 0
const splitLines = (v: string) => trim(v).split('\n').map(i => i.trim()).filter(Boolean)
const splitTags = (v: string) => trim(v).split(/[，,]/).map(i => i.trim()).filter(Boolean)
const contacts = computed(() => [form.phone, form.email, form.location].filter(hasText))
const skills = computed(() => splitTags(form.skills))
const awards = computed(() => splitLines(form.awards))
const languages = computed(() => splitLines(form.languages))
const works = computed(() => form.work.filter(i => [i.company, i.position, i.date, i.desc].some(hasText)))
const projects = computed(() => form.projects.filter(i => [i.name, i.tech, i.date, i.desc].some(hasText)))
const templateLabel = computed(() => ({ professional: '专业模板', modern: '现代模板', compact: '紧凑模板' }[selectedTemplate.value]))

const fill = (data: ResumeEditorState) => {
  Object.assign(form, {
    ...data,
    work: data.work.map(i => ({ ...i })),
    projects: data.projects.map(i => ({ ...i }))
  })
}

// 计算完整度评分
const calculateCompleteness = () => {
  let score = 0
  const totalFields = 12 // 总字段数
  let filledFields = 0

  // 基本信息字段
  if (hasText(form.name)) filledFields++
  if (hasText(form.phone)) filledFields++
  if (hasText(form.email)) filledFields++
  if (hasText(form.title)) filledFields++
  if (hasText(form.school)) filledFields++
  if (hasText(form.education)) filledFields++

  // 内容字段
  if (hasText(form.summary)) filledFields++
  if (hasText(form.skills)) filledFields++
  if (works.value.length > 0) filledFields++
  if (projects.value.length > 0) filledFields++
  if (awards.value.length > 0 || hasText(form.awards)) filledFields++
  if (languages.value.length > 0 || hasText(form.languages)) filledFields++

  score = Math.round((filledFields / totalFields) * 100)
  completenessScore.value = score
  return { score }
}

// 进度条状态
const getProgressStatus = (score: number) => {
  if (score >= 80) return 'success'
  if (score >= 50) return ''
  return 'exception'
}

// 分数样式类
const getScoreClass = (score: number) => {
  if (score >= 80) return 'score-excellent'
  if (score >= 50) return 'score-good'
  return 'score-poor'
}

// 必填字段检查
const resumeMissingRequiredFields = computed(() => {
  const missing: { field: string; label: string }[] = []
  if (!hasText(form.name)) missing.push({ field: 'name', label: '姓名' })
  if (!hasText(form.phone)) missing.push({ field: 'phone', label: '手机号' })
  if (!hasText(form.email)) missing.push({ field: 'email', label: '邮箱' })
  if (!hasText(form.school)) missing.push({ field: 'school', label: '学校' })
  if (!hasText(form.education)) missing.push({ field: 'education', label: '学历' })
  return missing
})

const hydrate = () => {
  const cached = loadCareerFormData()
  const resume = jsonResumeStore.resume
  const extras = jsonResumeStore.profileExtras
  fill({
    name: trim(resume?.basics.name) || trim(extras.basics.name),
    title: trim(resume?.basics.label) || trim(extras.basics.label) || trim(cached?.targetJob),
    phone: trim(resume?.basics.phone) || trim(extras.basics.phone),
    email: trim(resume?.basics.email) || trim(extras.basics.email),
    location: [trim(resume?.basics.location?.city) || trim(extras.basics.city), trim(resume?.basics.location?.region) || trim(extras.basics.region)].filter(Boolean).join(' / '),
    education: [trim(resume?.education?.[0]?.studyType) || trim(cached?.education), trim(resume?.education?.[0]?.area) || cached?.major?.join(' / ') || ''].filter(Boolean).join(' / '),
    school: trim(resume?.education?.[0]?.institution) || trim(extras.educationHistory?.[0]?.institution),
    summary: trim(resume?.basics.summary) || trim(extras.basics.summary),
    skills: [...(resume?.skills?.flatMap(i => i.keywords || []) || []), ...(cached?.skills?.map(i => i.name) || [])].filter(Boolean).join(', '),
    awards: [...(resume?.certificates?.map(i => i.name) || []), ...(cached?.certificates || [])].filter(Boolean).join('\n'),
    languages: [...(resume?.languages?.map(i => [i.language, i.fluency].filter(Boolean).join(' ')) || []), ...(cached?.languages?.map(i => [i.type, i.level].filter(Boolean).join(' ')) || [])].filter(Boolean).join('\n'),
    portfolio: trim(resume?.basics.profiles?.[0]?.url) || trim(extras.basics.url) || trim(cached?.codeAbility?.links),
    work: [
      ...(resume?.work?.map(i => ({ company: trim(i.name), position: trim(i.position), date: [trim(i.startDate), trim(i.endDate) || '至今'].filter(Boolean).join(' - '), desc: [trim(i.summary), ...(i.highlights || [])].filter(Boolean).join('\n') })) || []),
      ...(cached?.internships?.map(i => ({ company: trim(i.company), position: trim(i.role), date: Array.isArray(i.date) && i.date.length === 2 ? i.date.map(d => new Date(d).toISOString().slice(0, 10)).join(' - ') : '', desc: trim(i.desc) })) || [])
    ].slice(0, 2).concat(Array.from({ length: 2 }, () => ({ company: '', position: '', date: '', desc: '' }))).slice(0, 2),
    projects: [
      ...(resume?.projects?.map(i => ({ name: trim(i.name), tech: i.keywords?.join(', ') || '', date: [trim(i.startDate), trim(i.endDate)].filter(Boolean).join(' - '), desc: [trim(i.description), ...(i.highlights || [])].filter(Boolean).join('\n') })) || []),
      ...(cached?.projects?.map(i => ({ name: trim(i.name), tech: '', date: i.isCompetition ? '竞赛项目' : '', desc: trim(i.desc) })) || [])
    ].slice(0, 2).concat(Array.from({ length: 2 }, () => ({ name: '', tech: '', date: '', desc: '' }))).slice(0, 2)
  })
  ElMessage.success('已从能力画像载入当前简历信息')
}

const completeness = () => {
  const checks = [hasText(form.name), hasText(form.phone), hasText(form.email), hasText(form.school), hasText(form.education), hasText(form.summary), skills.value.length > 0, works.value.length > 0, projects.value.length > 0]
  return Math.round(checks.filter(Boolean).length / checks.length * 100)
}

const validate = () => {
  const errors: ValidationError[] = []
  if (!hasText(form.name)) errors.push({ field: 'name', label: '姓名', message: '姓名不能为空' })
  if (!hasText(form.phone)) errors.push({ field: 'phone', label: '手机号', message: '手机号不能为空' })
  if (!hasText(form.email)) errors.push({ field: 'email', label: '邮箱', message: '邮箱不能为空' })
  if (!hasText(form.school)) errors.push({ field: 'school', label: '毕业院校', message: '毕业院校不能为空' })
  if (!hasText(form.education)) errors.push({ field: 'education', label: '学历/专业', message: '学历/专业不能为空' })
  if (skills.value.length === 0) errors.push({ field: 'skills', label: '专业技能', message: '请至少填写一项专业技能' })
  if (works.value.length === 0) errors.push({ field: 'work', label: '工作经历', message: '建议至少填写一段工作经历' })
  if (projects.value.length === 0) errors.push({ field: 'project', label: '项目经验', message: '建议至少填写一个项目经验' })
  validationErrors.value = errors
  completenessScore.value = completeness()
  if (errors.length) {
    const firstError = errors[0]
    const field = firstError?.field
    activeTab.value = ['work', 'project', 'other'].includes(field as string)
      ? field as 'work' | 'project' | 'other'
      : 'basic'
  }
}

const requestExport = (type: 'pdf' | 'word') => {
  pendingExportAction.value = type
  validate()
  validationDialogVisible.value = true
}

const confirmExport = async () => {
  validationDialogVisible.value = false
  if (pendingExportAction.value === 'pdf' && previewRef.value) {
    exportingPdf.value = true
    try {
      await exportResumePreviewToPdf(previewRef.value, { fileName: `${form.name || 'resume-editor'}.pdf`, margin: 0 })
      ElMessage.success('PDF 导出成功')
    } catch (error) {
      console.error(error)
      ElMessage.error('导出 PDF 失败，请稍后再试')
    } finally {
      exportingPdf.value = false
    }
  }
  if (pendingExportAction.value === 'word') {
    exportingWord.value = true
    try {
      await exportManualResumeToWord(form, { fileName: `${form.name || 'resume-editor'}.docx` })
      ElMessage.success('Word 导出成功')
    } catch (error) {
      console.error(error)
      ElMessage.error('导出 Word 失败，请稍后再试')
    } finally {
      exportingWord.value = false
    }
  }
}

const selectTemplate = (template: 'professional' | 'modern' | 'compact') => {
  selectedTemplate.value = template
  templateDialogVisible.value = false
  ElMessage.success(`已切换为${templateLabel.value}`)
}

onMounted(hydrate)
</script>
<template>
  <div class="resume-editor-page">
    <!-- 顶部导航栏 -->
    <header class="editor-header">
      <div class="editor-header__brand">
        <div class="brand-mark">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
        </div>
        <div class="brand-text">
          <h1>简历编辑器</h1>
          <p>实时预览 · 智能排版 · 一键导出</p>
        </div>
      </div>

      <div class="editor-header__actions">
        <el-tooltip content="返回模板选择" placement="bottom">
          <el-button circle :icon="ArrowLeft" @click="router.push('/career-form/template')" />
        </el-tooltip>

        <el-divider direction="vertical" class="header-divider" />

        <el-button-group>
          <el-button :icon="UploadFilled" @click="hydrate">导入画像</el-button>
          <el-button :icon="RefreshRight" @click="fill(demo)">示例数据</el-button>
          <el-button :icon="Files" @click="templateDialogVisible = true">切换模板</el-button>
        </el-button-group>

        <el-divider direction="vertical" class="header-divider" />

        <el-dropdown split-button type="primary" :loading="exportingPdf || exportingWord" @click="requestExport('pdf')">
          <el-icon class="export-icon"><Download /></el-icon>
          <span class="export-text">导出 PDF</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item :icon="Download" @click="requestExport('word')" :disabled="exportingWord">
                {{ exportingWord ? '导出中...' : '导出 Word' }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 实时状态栏 -->
    <div class="status-bar">
      <div class="status-section">
        <span class="status-label">完整度</span>
        <div class="status-progress">
          <el-progress
            :percentage="completenessScore"
            :status="getProgressStatus(completenessScore)"
            :stroke-width="8"
            :show-text="false"
            class="compact-progress"
          />
          <span class="status-value" :class="getScoreClass(completenessScore)">{{ completenessScore }}%</span>
        </div>
      </div>
      <div class="status-divider" />
      <div class="status-section">
        <span class="status-label">当前模板</span>
        <span class="status-badge template-badge">{{ templateLabel }}</span>
      </div>
      <div class="status-divider" />
      <div class="status-section">
        <span class="status-label">字段状态</span>
        <span :class="['status-badge', validationErrors.length === 0 ? 'status-success' : 'status-warning']">
          <el-icon v-if="validationErrors.length === 0"><CircleCheck /></el-icon>
          <el-icon v-else><Warning /></el-icon>
          {{ validationErrors.length === 0 ? '已完善' : `待补充 ${validationErrors.length} 项` }}
        </span>
      </div>
    </div>

    <main class="editor-body">
      <!-- 编辑面板 -->
      <section class="editor-panel">
        <!-- 标签导航 -->
        <nav class="panel-nav">
          <button
            v-for="tab in [
              { key: 'basic', label: '基本信息', icon: '👤' },
              { key: 'work', label: '工作经历', icon: '💼' },
              { key: 'project', label: '项目经验', icon: '🚀' },
              { key: 'other', label: '其他信息', icon: '🏆' }
            ]"
            :key="tab.key"
            type="button"
            class="nav-tab"
            :class="{ active: activeTab === tab.key, completed: isTabCompleted(tab.key) }"
            @click="activeTab = tab.key as 'basic' | 'work' | 'project' | 'other'"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
            <span v-if="isTabCompleted(tab.key)" class="tab-check">✓</span>
          </button>
        </nav>

        <!-- 基本信息面板 -->
        <div v-show="activeTab === 'basic'" class="tab-content">
          <!-- 个人信息卡片 -->
          <div class="form-card">
            <div class="card-header">
              <span class="card-icon">📝</span>
              <span class="card-title">个人信息</span>
              <span class="card-subtitle">基本信息将展示在简历头部</span>
            </div>
            <div class="form-grid form-grid--2col">
              <div class="input-group" :class="{ 'has-value': hasText(form.name) }">
                <label class="input-label">
                  <span class="label-text">姓名</span>
                  <span class="label-required">*</span>
                </label>
                <input v-model="form.name" class="form-input" placeholder="请输入真实姓名" maxlength="20">
              </div>
              <div class="input-group" :class="{ 'has-value': hasText(form.title) }">
                <label class="input-label">
                  <span class="label-text">职位 / 目标岗位</span>
                </label>
                <input v-model="form.title" class="form-input" placeholder="如：Java 后端开发工程师" maxlength="30">
              </div>
              <div class="input-group" :class="{ 'has-value': hasText(form.phone) }">
                <label class="input-label">
                  <span class="label-text">手机号</span>
                  <span class="label-required">*</span>
                </label>
                <input v-model="form.phone" class="form-input" placeholder="11位手机号码" maxlength="11">
              </div>
              <div class="input-group" :class="{ 'has-value': hasText(form.email) }">
                <label class="input-label">
                  <span class="label-text">邮箱地址</span>
                  <span class="label-required">*</span>
                </label>
                <input v-model="form.email" class="form-input" placeholder="example@email.com" maxlength="50">
              </div>
              <div class="input-group" :class="{ 'has-value': hasText(form.location) }">
                <label class="input-label">
                  <span class="label-text">所在城市</span>
                </label>
                <input v-model="form.location" class="form-input" placeholder="如：北京市" maxlength="20">
              </div>
              <div class="input-group" :class="{ 'has-value': hasText(form.education) }">
                <label class="input-label">
                  <span class="label-text">学历 / 专业</span>
                  <span class="label-required">*</span>
                </label>
                <input v-model="form.education" class="form-input" placeholder="如：本科 / 计算机科学" maxlength="30">
              </div>
              <div class="input-group input-group--full" :class="{ 'has-value': hasText(form.school) }">
                <label class="input-label">
                  <span class="label-text">毕业院校</span>
                  <span class="label-required">*</span>
                </label>
                <input v-model="form.school" class="form-input" placeholder="请输入学校全称" maxlength="50">
              </div>
            </div>
          </div>

          <!-- 个人简介卡片 -->
          <div class="form-card">
            <div class="card-header">
              <span class="card-icon">💡</span>
              <span class="card-title">个人简介</span>
              <span class="card-subtitle">用 2-3 句话概括你的核心优势</span>
            </div>
            <div class="textarea-wrapper">
              <textarea
                v-model="form.summary"
                class="form-textarea"
                rows="4"
                placeholder="介绍你的核心优势、项目方向与求职定位..."
                maxlength="500"
              />
              <span class="char-count" :class="{ 'near-limit': form.summary.length > 400 }">
                {{ form.summary.length }}/500
              </span>
            </div>
          </div>

          <!-- 专业技能卡片 -->
          <div class="form-card">
            <div class="card-header">
              <span class="card-icon">⚡</span>
              <span class="card-title">专业技能</span>
              <span class="card-subtitle">用逗号分隔多个技能</span>
            </div>
            <div class="textarea-wrapper">
              <textarea
                v-model="form.skills"
                class="form-textarea"
                rows="3"
                placeholder="如：Java, Spring Boot, MySQL, Redis, Vue.js, Docker..."
                maxlength="200"
              />
            </div>
            <div v-if="skills.length > 0" class="skill-preview">
              <span v-for="skill in skills.slice(0, 8)" :key="skill" class="skill-tag">{{ skill }}</span>
              <span v-if="skills.length > 8" class="skill-more">+{{ skills.length - 8 }}</span>
            </div>
          </div>
        </div>

        <!-- 工作经历面板 -->
        <div v-show="activeTab === 'work'" class="tab-content">
          <div v-for="(item, index) in form.work" :key="`work-${index}`" class="form-card form-card--collapsible">
            <div class="card-header card-header--collapsible" @click="toggleWorkExpand(index)">
              <div class="header-left">
                <span class="card-icon">💼</span>
                <span class="card-title">工作经历 {{ index + 1 }}</span>
                <span v-if="hasText(item.company)" class="card-preview">{{ item.company }}</span>
              </div>
              <span class="expand-icon" :class="{ expanded: workExpanded[index] }">▼</span>
            </div>
            <div v-show="workExpanded[index]" class="card-body">
              <div class="form-grid form-grid--2col">
                <div class="input-group" :class="{ 'has-value': hasText(item.company) }">
                  <label class="input-label">
                    <span class="label-text">公司名称</span>
                  </label>
                  <input v-model="item.company" class="form-input" placeholder="请输入公司名称" maxlength="50">
                </div>
                <div class="input-group" :class="{ 'has-value': hasText(item.position) }">
                  <label class="input-label">
                    <span class="label-text">职位名称</span>
                  </label>
                  <input v-model="item.position" class="form-input" placeholder="如：高级前端工程师" maxlength="30">
                </div>
                <div class="input-group input-group--full" :class="{ 'has-value': hasText(item.date) }">
                  <label class="input-label">
                    <span class="label-text">时间范围</span>
                  </label>
                  <input v-model="item.date" class="form-input" placeholder="如：2022.06 - 至今" maxlength="30">
                </div>
              </div>
              <div class="textarea-wrapper textarea-wrapper--tall">
                <label class="input-label textarea-label">
                  <span class="label-text">工作内容与成果</span>
                  <span class="label-hint">支持换行，建议用「-」列出要点</span>
                </label>
                <textarea
                  v-model="item.desc"
                  class="form-textarea"
                  rows="6"
                  placeholder="描述你的工作职责和主要成就...&#10;- 负责 XX 系统的架构设计&#10;- 优化性能，使响应速度提升 50%"
                  maxlength="1000"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 项目经验面板 -->
        <div v-show="activeTab === 'project'" class="tab-content">
          <div v-for="(item, index) in form.projects" :key="`project-${index}`" class="form-card form-card--collapsible">
            <div class="card-header card-header--collapsible" @click="toggleProjectExpand(index)">
              <div class="header-left">
                <span class="card-icon">🚀</span>
                <span class="card-title">项目经验 {{ index + 1 }}</span>
                <span v-if="hasText(item.name)" class="card-preview">{{ item.name }}</span>
              </div>
              <span class="expand-icon" :class="{ expanded: projectExpanded[index] }">▼</span>
            </div>
            <div v-show="projectExpanded[index]" class="card-body">
              <div class="form-grid form-grid--2col">
                <div class="input-group" :class="{ 'has-value': hasText(item.name) }">
                  <label class="input-label">
                    <span class="label-text">项目名称</span>
                  </label>
                  <input v-model="item.name" class="form-input" placeholder="如：电商平台重构" maxlength="50">
                </div>
                <div class="input-group" :class="{ 'has-value': hasText(item.tech) }">
                  <label class="input-label">
                    <span class="label-text">技术栈</span>
                  </label>
                  <input v-model="item.tech" class="form-input" placeholder="如：Vue3 + TypeScript + Node.js" maxlength="50">
                </div>
                <div class="input-group input-group--full" :class="{ 'has-value': hasText(item.date) }">
                  <label class="input-label">
                    <span class="label-text">项目时间</span>
                  </label>
                  <input v-model="item.date" class="form-input" placeholder="如：2023.01 - 2023.06" maxlength="30">
                </div>
              </div>
              <div class="textarea-wrapper textarea-wrapper--tall">
                <label class="input-label textarea-label">
                  <span class="label-text">项目描述</span>
                  <span class="label-hint">描述项目背景、你的职责和项目成果</span>
                </label>
                <textarea
                  v-model="item.desc"
                  class="form-textarea"
                  rows="6"
                  placeholder="介绍项目背景和你的核心贡献...&#10;- 项目背景：解决 XX 问题&#10;- 我的职责：负责 XX 模块开发&#10;- 项目成果：性能提升 30%"
                  maxlength="1000"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 其他信息面板 -->
        <div v-show="activeTab === 'other'" class="tab-content">
          <div class="form-card">
            <div class="card-header">
              <span class="card-icon">🏆</span>
              <span class="card-title">荣誉证书</span>
              <span class="card-subtitle">每行填写一项证书或荣誉</span>
            </div>
            <div class="textarea-wrapper">
              <textarea
                v-model="form.awards"
                class="form-textarea"
                rows="4"
                placeholder="如：&#10;优秀员工（2023）&#10;PMP 项目管理认证&#10;全国大学生数学建模竞赛一等奖"
                maxlength="500"
              />
            </div>
          </div>

          <div class="form-card">
            <div class="card-header">
              <span class="card-icon">🌍</span>
              <span class="card-title">语言能力</span>
              <span class="card-subtitle">每行填写一项语言能力</span>
            </div>
            <div class="textarea-wrapper">
              <textarea
                v-model="form.languages"
                class="form-textarea"
                rows="3"
                placeholder="如：&#10;英语 CET-6（580分）&#10;日语 N2"
                maxlength="200"
              />
            </div>
          </div>

          <div class="form-card">
            <div class="card-header">
              <span class="card-icon">🔗</span>
              <span class="card-title">作品链接</span>
              <span class="card-subtitle">GitHub、个人博客或作品集链接</span>
            </div>
            <div class="input-group input-group--full" :class="{ 'has-value': hasText(form.portfolio) }">
              <input v-model="form.portfolio" class="form-input" placeholder="https://github.com/username" maxlength="100">
            </div>
          </div>
        </div>
      </section>

      <section class="preview-panel">
        <div ref="previewRef" class="resume-paper" :class="`template-${selectedTemplate}`"><div class="resume-template-badge">{{ templateLabel }}</div>
          <template v-if="selectedTemplate === 'professional'"><header class="resume-header professional-header"><div><div class="resume-name">{{ form.name || '你的姓名' }}</div><div v-if="form.title" class="resume-title">{{ form.title }}</div></div><div v-if="contacts.length" class="resume-contact resume-contact--stacked"><span v-for="item in contacts" :key="item">{{ item }}</span></div></header><section v-if="form.summary" class="resume-section"><div class="resume-section-title">个人简介</div><div class="resume-item-content">{{ form.summary }}</div></section><section v-if="form.education || form.school" class="resume-section"><div class="resume-section-title">教育背景</div><div class="resume-item"><div class="resume-item-title">{{ form.school }}</div><div class="resume-item-subtitle">{{ form.education }}</div></div></section><section v-if="works.length" class="resume-section"><div class="resume-section-title">工作经历</div><div v-for="(item, index) in works" :key="`pw-${index}`" class="resume-item"><div class="resume-item-header"><span class="resume-item-title">{{ item.company }}<template v-if="item.position"> / {{ item.position }}</template></span><span class="resume-item-date">{{ item.date }}</span></div><div class="resume-item-content">{{ item.desc }}</div></div></section><section v-if="projects.length" class="resume-section"><div class="resume-section-title">项目经验</div><div v-for="(item, index) in projects" :key="`pp-${index}`" class="resume-item"><div class="resume-item-header"><span class="resume-item-title">{{ item.name }}<template v-if="item.tech"> ({{ item.tech }})</template></span><span class="resume-item-date">{{ item.date }}</span></div><div class="resume-item-content">{{ item.desc }}</div></div></section><section v-if="skills.length" class="resume-section"><div class="resume-section-title">专业技能</div><div class="tag-wrap"><span v-for="item in skills" :key="item" class="resume-skill-tag">{{ item }}</span></div></section></template>
          <template v-else-if="selectedTemplate === 'modern'"><div class="modern-layout"><aside class="modern-sidebar"><div class="modern-profile"><div class="resume-name modern-name">{{ form.name || '你的姓名' }}</div><div v-if="form.title" class="resume-title modern-title">{{ form.title }}</div></div><section v-if="contacts.length" class="modern-section"><div class="resume-section-title modern-section-title">联系方式</div><div class="modern-list"><span v-for="item in contacts" :key="item">{{ item }}</span></div></section><section v-if="skills.length" class="modern-section"><div class="resume-section-title modern-section-title">专业技能</div><div class="tag-wrap"><span v-for="item in skills" :key="item" class="resume-skill-tag modern-tag">{{ item }}</span></div></section><section v-if="awards.length" class="modern-section"><div class="resume-section-title modern-section-title">荣誉证书</div><div class="resume-item-content modern-copy">{{ awards.join('\n') }}</div></section><section v-if="languages.length || form.portfolio" class="modern-section"><div class="resume-section-title modern-section-title">其他信息</div><div v-if="languages.length" class="resume-item-content modern-copy">{{ languages.join('\n') }}</div><div v-if="form.portfolio" class="resume-item-content modern-link">{{ form.portfolio }}</div></section></aside><main class="modern-main"><section v-if="form.summary" class="resume-section"><div class="resume-section-title">个人简介</div><div class="resume-item-content">{{ form.summary }}</div></section><section v-if="works.length" class="resume-section"><div class="resume-section-title">工作经历</div><div v-for="(item, index) in works" :key="`mw-${index}`" class="resume-item"><div class="resume-item-header"><span class="resume-item-title">{{ item.company }}<template v-if="item.position"> / {{ item.position }}</template></span><span class="resume-item-date">{{ item.date }}</span></div><div class="resume-item-content">{{ item.desc }}</div></div></section><section v-if="projects.length" class="resume-section"><div class="resume-section-title">项目经验</div><div v-for="(item, index) in projects" :key="`mp-${index}`" class="resume-item"><div class="resume-item-header"><span class="resume-item-title">{{ item.name }}<template v-if="item.tech"> ({{ item.tech }})</template></span><span class="resume-item-date">{{ item.date }}</span></div><div class="resume-item-content">{{ item.desc }}</div></div></section><section v-if="form.education || form.school" class="resume-section"><div class="resume-section-title">教育背景</div><div class="resume-item"><div class="resume-item-title">{{ form.school }}</div><div class="resume-item-subtitle">{{ form.education }}</div></div></section></main></div></template>
          <template v-else><header class="resume-header compact-header"><div><div class="resume-name compact-name">{{ form.name || '你的姓名' }}</div><div v-if="form.title" class="resume-title compact-title">{{ form.title }}</div></div><div v-if="contacts.length" class="resume-contact compact-contact"><span v-for="item in contacts" :key="item">{{ item }}</span></div></header><div class="compact-layout"><aside class="compact-side"><section v-if="form.summary" class="resume-section compact-block"><div class="resume-section-title compact-section-title">个人简介</div><div class="resume-item-content">{{ form.summary }}</div></section><section v-if="skills.length" class="resume-section compact-block"><div class="resume-section-title compact-section-title">专业技能</div><div class="tag-wrap"><span v-for="item in skills" :key="item" class="resume-skill-tag compact-tag">{{ item }}</span></div></section><section v-if="languages.length" class="resume-section compact-block"><div class="resume-section-title compact-section-title">语言能力</div><div class="resume-item-content">{{ languages.join('\n') }}</div></section><section v-if="awards.length" class="resume-section compact-block"><div class="resume-section-title compact-section-title">荣誉证书</div><div class="resume-item-content">{{ awards.join('\n') }}</div></section></aside><main class="compact-main"><section v-if="works.length" class="resume-section compact-block"><div class="resume-section-title compact-section-title">工作经历</div><div v-for="(item, index) in works" :key="`cw-${index}`" class="resume-item"><div class="resume-item-header"><span class="resume-item-title">{{ item.company }}<template v-if="item.position"> / {{ item.position }}</template></span><span class="resume-item-date">{{ item.date }}</span></div><div class="resume-item-content">{{ item.desc }}</div></div></section><section v-if="projects.length" class="resume-section compact-block"><div class="resume-section-title compact-section-title">项目经验</div><div v-for="(item, index) in projects" :key="`cp-${index}`" class="resume-item"><div class="resume-item-header"><span class="resume-item-title">{{ item.name }}<template v-if="item.tech"> ({{ item.tech }})</template></span><span class="resume-item-date">{{ item.date }}</span></div><div class="resume-item-content">{{ item.desc }}</div></div></section><section v-if="form.education || form.school || form.portfolio" class="resume-section compact-block"><div class="resume-section-title compact-section-title">教育与链接</div><div v-if="form.school || form.education" class="resume-item"><div class="resume-item-title">{{ form.school }}</div><div class="resume-item-subtitle">{{ form.education }}</div></div><div v-if="form.portfolio" class="resume-item-content resume-item-link">{{ form.portfolio }}</div></section></main></div></template>
        </div>
      </section>
    </main>

    <el-dialog v-model="validationDialogVisible" title="简历质量检查" width="520px" :close-on-click-modal="false"><div class="validation-content"><div class="validation-score"><div class="validation-score__header"><span>内容完整度</span><strong>{{ completenessScore }}%</strong></div><el-progress :percentage="completenessScore" :status="completenessScore >= 80 ? 'success' : completenessScore >= 60 ? '' : 'exception'" :stroke-width="12" /></div><div v-if="validationErrors.length" class="validation-errors"><div class="validation-errors__title"><el-icon><Warning /></el-icon><span>以下内容建议先补充后再导出</span></div><div class="error-list"><div v-for="item in validationErrors" :key="`${item.field}-${item.message}`" class="error-item"><strong>{{ item.label }}</strong><span>{{ item.message }}</span></div></div></div><div v-else class="validation-success"><el-icon><CircleCheck /></el-icon><span>简历信息完整，可以直接导出</span></div></div><template #footer><div class="dialog-footer"><el-button @click="validationDialogVisible = false">返回编辑</el-button><el-button type="primary" @click="confirmExport">{{ pendingExportAction === 'word' ? '继续导出 Word' : '继续导出 PDF' }}</el-button></div></template></el-dialog>

    <el-dialog v-model="templateDialogVisible" title="选择简历模板" width="860px"><div class="resume-template-grid"><button type="button" class="resume-template-card" :class="{ 'is-active': selectedTemplate === 'professional' }" @click="selectTemplate('professional')"><div class="template-preview template-preview--professional"><div class="template-preview-header"></div><div class="template-preview-line large"></div><div class="template-preview-line"></div><div class="template-preview-columns"><span></span><span></span></div></div><strong>专业模板</strong><p>正式投递风格，版式稳重，适合校招和社招。</p></button><button type="button" class="resume-template-card" :class="{ 'is-active': selectedTemplate === 'modern' }" @click="selectTemplate('modern')"><div class="template-preview template-preview--modern"><div class="template-preview-header accent"></div><div class="template-preview-line large"></div><div class="template-preview-columns"><span class="accent"></span><span></span></div><div class="template-preview-line"></div></div><strong>现代模板</strong><p>左侧边栏布局，更强调个人标签、技能与信息层级。</p></button><button type="button" class="resume-template-card" :class="{ 'is-active': selectedTemplate === 'compact' }" @click="selectTemplate('compact')"><div class="template-preview template-preview--compact"><div class="template-preview-line large"></div><div class="template-preview-line small"></div><div class="template-preview-line"></div><div class="template-preview-line"></div></div><strong>紧凑模板</strong><p>双栏一页式，适合内容密度较高、强调效率表达的简历。</p></button></div></el-dialog>
  </div>
</template>
<style scoped>
/* ========== 基础样式 ========== */
.resume-editor-page {
  min-height: 100vh;
  padding: 24px 32px 32px;
  background:
    radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 100% 0%, rgba(236, 72, 153, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 100% 100%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
    linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

/* ========== 头部导航 ========== */
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 16px;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.05),
    0 2px 4px -2px rgba(0, 0, 0, 0.05),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  backdrop-filter: blur(12px);
}

.editor-header__brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.brand-mark:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
}

.brand-mark svg {
  width: 22px;
  height: 22px;
}

.brand-text h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.02em;
}

.brand-text p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.editor-header__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-divider {
  height: 24px !important;
  margin: 0 4px !important;
  border-color: #e2e8f0 !important;
}

.export-icon {
  margin-right: 6px;
}

.export-text {
  font-weight: 500;
}

/* ========== 状态栏 ========== */
.status-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 16px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.status-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 140px;
}

.compact-progress {
  flex: 1;
}

.status-value {
  font-size: 14px;
  font-weight: 700;
  min-width: 40px;
  text-align: right;
}

.score-excellent { color: #10b981; }
.score-good { color: #f59e0b; }
.score-poor { color: #ef4444; }

.status-divider {
  width: 1px;
  height: 24px;
  background: #e2e8f0;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 20px;
  background: #f1f5f9;
  color: #64748b;
}

.status-badge.status-success {
  background: #d1fae5;
  color: #059669;
}

.status-badge.status-warning {
  background: #fef3c7;
  color: #d97706;
}

.template-badge {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

/* ========== 主体布局 ========== */
.editor-body {
  display: grid;
  grid-template-columns: minmax(380px, 440px) minmax(0, 1fr);
  gap: 24px;
  margin-top: 16px;
  align-items: start;
}

.editor-panel,
.preview-panel {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 20px;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.05),
    0 2px 4px -2px rgba(0, 0, 0, 0.05);
}

/* ========== 编辑面板 ========== */
.editor-panel {
  padding: 20px;
}

/* 导航标签 */
.panel-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding: 4px;
  background: #f8fafc;
  border-radius: 12px;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.nav-tab:hover {
  color: #475569;
  background: rgba(255, 255, 255, 0.6);
}

.nav-tab.active {
  color: #6366f1;
  background: white;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15);
}

.nav-tab.completed:not(.active) {
  color: #10b981;
}

.nav-tab.completed:not(.active)::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: #10b981;
  border-radius: 50%;
}

.tab-icon {
  font-size: 14px;
}

.tab-label {
  white-space: nowrap;
}

.tab-check {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: #10b981;
  color: white;
  font-size: 10px;
  border-radius: 50%;
}

/* 内容区域 */
.tab-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ========== 表单卡片 ========== */
.form-card {
  padding: 16px;
  background: #fafafa;
  border: 1px solid #f1f5f9;
  border-radius: 14px;
  transition: all 0.2s ease;
}

.form-card:hover {
  border-color: #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.form-card--collapsible {
  padding: 0;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.form-card--collapsible .card-header {
  margin-bottom: 0;
  padding: 14px 16px;
}

.card-header--collapsible {
  cursor: pointer;
  transition: background 0.2s ease;
}

.card-header--collapsible:hover {
  background: #f8fafc;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.card-icon {
  font-size: 18px;
}

.card-title {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
}

.card-subtitle {
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
}

.card-preview {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.expand-icon {
  font-size: 12px;
  color: #94a3b8;
  transition: transform 0.2s ease;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.card-body {
  padding: 0 16px 16px;
}

/* ========== 表单输入 ========== */
.form-grid {
  display: grid;
  gap: 12px;
}

.form-grid--2col {
  grid-template-columns: repeat(2, 1fr);
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-group--full {
  grid-column: 1 / -1;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.label-required {
  color: #ef4444;
}

.label-hint {
  font-size: 11px;
  font-weight: 500;
  color: #94a3b8;
  margin-left: auto;
}

.textarea-label {
  margin-bottom: 6px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  color: #1e293b;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  transition: all 0.2s ease;
  outline: none;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #94a3b8;
}

.form-input:hover,
.form-textarea:hover {
  border-color: #cbd5e1;
}

.form-input:focus,
.form-textarea:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-group.has-value .form-input,
.input-group.has-value .form-textarea {
  border-color: #6366f1;
  background: #fafaff;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.6;
}

.textarea-wrapper {
  position: relative;
}

.textarea-wrapper--tall .form-textarea {
  min-height: 140px;
}

.char-count {
  position: absolute;
  bottom: 10px;
  right: 12px;
  font-size: 11px;
  font-weight: 500;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 4px;
}

.char-count.near-limit {
  color: #f59e0b;
}

/* 技能预览标签 */
.skill-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #e2e8f0;
}

.skill-tag {
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  color: #6366f1;
  background: #eef2ff;
  border-radius: 6px;
}

.skill-more {
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  background: #f1f5f9;
  border-radius: 6px;
}

/* ========== 预览面板 ========== */
.preview-panel {
  padding: 20px;
  display: flex;
  justify-content: center;
  min-height: calc(100vh - 240px);
}

.resume-paper {
  width: 210mm;
  min-height: 297mm;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  position: relative;

  gap: 20px;
  padding: 24px 28px;
  border-radius: 28px;
}

.editor-header__brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.editor-header__brand h1 {
  margin: 0 0 6px;
  font-size: 30px;
  color: #17314f;
}

.editor-header__brand p {
  margin: 0;
  color: #7084a3;
}

.brand-mark {
  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;
  border-radius: 18px;
  background: linear-gradient(135deg, #5ca5ff, #6f7dff);
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  box-shadow: 0 14px 28px rgba(92, 165, 255, 0.28);
}

.editor-header__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.editor-body {
  display: grid;
  grid-template-columns: minmax(340px, 420px) minmax(0, 1fr);
  gap: 24px;
  margin-top: 24px;
  align-items: start;
}

.editor-panel,
.preview-panel {
  border-radius: 30px;
}

.editor-panel {
  padding: 24px;
}

.panel-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.tab-btn {
  border: none;
  border-radius: 999px;
  background: #edf4ff;
  color: #6180a6;
  padding: 10px 18px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: linear-gradient(135deg, #5ca5ff, #6b7cff);
  color: #fff;
  box-shadow: 0 10px 24px rgba(92, 165, 255, 0.24);
}

.tab-pane {
  display: grid;
  gap: 18px;
}

.edit-group {
  padding: 18px;
  border: 1px solid #e3edf9;
  border-radius: 22px;
  background: linear-gradient(180deg, #fcfdff 0%, #f5f9ff 100%);
}

.edit-group-title {
  margin-bottom: 14px;
  font-size: 15px;
  font-weight: 700;
  color: #17314f;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.form-input {
  width: 100%;
  border: 1px solid #d7e3f6;
  border-radius: 16px;
  background: #fff;
  padding: 12px 14px;
  font: inherit;
  color: #21354d;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus {
  border-color: #7bb0ff;
  box-shadow: 0 0 0 4px rgba(123, 176, 255, 0.14);
}

.form-input--full {
  grid-column: 1 / -1;
}

textarea.form-input {
  resize: vertical;
  min-height: 96px;
}

.preview-panel {
  padding: 26px;
}

.resume-paper {
  position: relative;
  min-height: 1040px;
  padding: 38px;
  border-radius: 28px;
  background: #fff;
  color: #223248;
  box-shadow: inset 0 0 0 1px rgba(218, 227, 242, 0.84);
}

.resume-paper.template-professional {
  border-top: 8px solid #6f88a9;
}

.resume-paper.template-modern {
  border-top: 8px solid #0f766e;
}

.resume-paper.template-compact {
  border-top: 8px solid #334155;
}

.resume-template-badge {
  position: absolute;
  top: 24px;
  right: 24px;
  border-radius: 999px;
  background: #eef5ff;
  color: #6680a4;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 700;
}

.resume-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 18px;
  margin-bottom: 22px;
  border-bottom: 1px solid #dfe7f2;
}

.resume-name {
  font-size: 32px;
  font-weight: 800;
  color: #18304c;
  letter-spacing: 1px;
}

.resume-title {
  margin-top: 8px;
  font-size: 16px;
  color: #6e84a2;
}

.resume-contact {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  justify-content: flex-end;
  color: #68809f;
  font-size: 14px;
}

.resume-contact--stacked {
  flex-direction: column;
  align-items: flex-end;
}

.resume-section {
  margin-top: 24px;
}

.resume-section:first-of-type {
  margin-top: 0;
}

.resume-section-title {
  margin-bottom: 14px;
  font-size: 15px;
  font-weight: 800;
  color: #17314f;
  letter-spacing: 0.08em;
}

.resume-item {
  margin-bottom: 16px;
}

.resume-item:last-child {
  margin-bottom: 0;
}

.resume-item-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 8px;
}

.resume-item-title {
  font-size: 15px;
  font-weight: 700;
  color: #203650;
}

.resume-item-subtitle,
.resume-item-date,
.resume-item-link {
  color: #6b809d;
  font-size: 14px;
}

.resume-item-content {
  white-space: pre-line;
  line-height: 1.72;
  color: #435774;
}

.tag-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.resume-skill-tag {
  border-radius: 999px;
  background: #eef4ff;
  color: #44658f;
  padding: 8px 12px;
  font-size: 13px;
}

.modern-layout,
.compact-layout {
  display: grid;
  gap: 22px;
}

.modern-layout {
  grid-template-columns: 240px minmax(0, 1fr);
}

.modern-sidebar {
  border-radius: 24px;
  background: linear-gradient(180deg, #e4f6f3 0%, #eefbf9 100%);
  padding: 26px 20px;
}

.modern-name {
  font-size: 28px;
}

.modern-title {
  color: #1c7b71;
}

.modern-section {
  margin-top: 22px;
}

.modern-section-title {
  color: #0e5f58;
}

.modern-list {
  display: grid;
  gap: 8px;
  color: #2f5f59;
  font-size: 14px;
}

.modern-copy,
.modern-link {
  color: #2f5f59;
}

.modern-tag {
  background: rgba(15, 118, 110, 0.12);
  color: #0d6159;
}

.modern-main {
  padding-top: 6px;
}

.compact-header {
  align-items: flex-end;
}

.compact-name {
  font-size: 30px;
}

.compact-contact {
  max-width: 280px;
}

.compact-layout {
  grid-template-columns: 260px minmax(0, 1fr);
}

.compact-side,
.compact-main {
  display: grid;
  gap: 18px;
  align-content: start;
}

.compact-block {
  margin-top: 0;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  padding: 18px;
}

.compact-section-title {
  color: #334155;
}

.compact-tag {
  background: #e8eef6;
  color: #334155;
}

.validation-content {
  display: grid;
  gap: 18px;
}

.validation-score {
  padding: 18px;
  border-radius: 18px;
  background: #f6faff;
}

.validation-score__header,
.validation-errors__title,
.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.validation-errors {
  padding: 18px;
  border-radius: 18px;
  background: #fff8f4;
}

.validation-errors__title {
  justify-content: flex-start;
  gap: 8px;
  margin-bottom: 12px;
  color: #b85b28;
}

.error-list {
  display: grid;
  gap: 10px;
}

.error-item {
  display: grid;
  gap: 4px;
  color: #5b6270;
}

.validation-success {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px;
  border-radius: 18px;
  background: #f2fbf5;
  color: #2b8a57;
}

.resume-template-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.resume-template-card {
  border: 1px solid #dfe8f5;
  border-radius: 24px;
  background: #fff;
  padding: 18px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.resume-template-card:hover,
.resume-template-card.is-active {
  border-color: #7fb0ff;
  box-shadow: 0 18px 34px rgba(108, 146, 204, 0.16);
  transform: translateY(-2px);
}

.resume-template-card strong {
  display: block;
  margin: 14px 0 8px;
  font-size: 17px;
  color: #17314f;
}

.resume-template-card p {
  margin: 0;
  color: #6e819e;
  line-height: 1.7;
}

.template-preview {
  display: grid;
  gap: 10px;
  height: 190px;
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fbff 0%, #eef4fd 100%);
}

.template-preview-header,
.template-preview-line,
.template-preview-columns span {
  border-radius: 999px;
  background: #cbd8ea;
}

.template-preview-header {
  height: 12px;
  width: 46%;
}

.template-preview-line {
  height: 10px;
  width: 100%;
}

.template-preview-line.large {
  width: 72%;
}

.template-preview-line.small {
  width: 52%;
}

.template-preview-columns {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 10px;
  flex: 1;
}

.template-preview-columns span {
  min-height: 86px;
}

.template-preview .accent {
  background: #8dd7c4;
}

/* ========== 简历内容样式（保留原有） ========== */
.resume-template-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
  background: #eef2ff;
  border-radius: 20px;
}

.resume-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding-bottom: 20px;
  margin-bottom: 24px;
  border-bottom: 2px solid #f1f5f9;
}

.resume-name {
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: -0.02em;
}

.resume-title {
  margin-top: 6px;
  font-size: 16px;
  font-weight: 600;
  color: #6366f1;
}

.resume-contact {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
}

.resume-section {
  margin-bottom: 24px;
}

.resume-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.resume-section-title::before {
  content: '';
  width: 4px;
  height: 16px;
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 2px;
}

.resume-item {
  margin-bottom: 16px;
}

.resume-item:last-child {
  margin-bottom: 0;
}

.resume-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 6px;
}

.resume-item-title {
  font-size: 15px;
  font-weight: 700;
  color: #334155;
}

.resume-item-date {
  font-size: 13px;
  font-weight: 500;
  color: #94a3b8;
  white-space: nowrap;
}

.resume-item-subtitle {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

.resume-item-content {
  font-size: 14px;
  line-height: 1.7;
  color: #475569;
  white-space: pre-line;
}

.resume-item-link {
  color: #6366f1;
  font-weight: 500;
}

.tag-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.resume-skill-tag {
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #6366f1;
  background: #eef2ff;
  border-radius: 6px;
}

/* 模板特定样式 */
.template-modern .resume-paper {
  background: linear-gradient(90deg, #f0fdf4 0%, #f0fdf4 30%, #ffffff 30%);
}

.template-compact .resume-paper {
  font-size: 13px;
}

/* ========== 校验弹窗 ========== */
.validation-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.validation-score {
  padding: 16px;
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
  border-radius: 12px;
}

.validation-score__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.validation-score__header span {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
}

.validation-score__header strong {
  font-size: 24px;
  font-weight: 800;
  color: #6366f1;
}

.validation-errors {
  padding: 16px;
  background: #fef3c7;
  border-radius: 12px;
}

.validation-errors__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 700;
  color: #92400e;
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.error-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  font-size: 13px;
}

.error-item strong {
  color: #78350f;
  font-weight: 600;
}

.error-item span {
  color: #92400e;
}

.validation-success {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  background: #d1fae5;
  border-radius: 12px;
  color: #065f46;
  font-size: 15px;
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* ========== 模板选择弹窗 ========== */
.resume-template-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.resume-template-card {
  padding: 16px;
  background: white;
  border: 2px solid #f1f5f9;
  border-radius: 16px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.resume-template-card:hover {
  border-color: #c7d2fe;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(99, 102, 241, 0.1);
}

.resume-template-card.is-active {
  border-color: #6366f1;
  background: #fafaff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.resume-template-card strong {
  display: block;
  margin-top: 12px;
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
}

.resume-template-card p {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.5;
  color: #64748b;
}

.template-preview {
  height: 160px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

/* ========== 响应式设计 ========== */
@media (max-width: 1280px) {
  .editor-body {
    grid-template-columns: 1fr;
  }

  .preview-panel {
    order: -1;
    min-height: auto;
    padding: 16px;
  }

  .resume-paper {
    width: 100%;
    max-width: 600px;
    min-height: auto;
    padding: 32px;
  }
}

@media (max-width: 768px) {
  .resume-editor-page {
    padding: 16px;
  }

  .editor-header {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }

  .editor-header__actions {
    flex-wrap: wrap;
    justify-content: center;
    width: 100%;
  }

  .header-divider {
    display: none;
  }

  .status-bar {
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px 16px;
  }

  .status-divider {
    display: none;
  }

  .panel-nav {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .nav-tab {
    white-space: nowrap;
  }

  .form-grid--2col {
    grid-template-columns: 1fr;
  }

  .resume-template-grid {
    grid-template-columns: 1fr;
  }

  .resume-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .resume-contact {
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .brand-text p {
    display: none;
  }

  .export-text {
    display: none;
  }

  .tab-label {
    display: none;
  }

  .nav-tab {
    padding: 10px;
  }

  .resume-paper {
    padding: 24px;
  }

  .resume-name {
    font-size: 24px;
  }
}
</style>
