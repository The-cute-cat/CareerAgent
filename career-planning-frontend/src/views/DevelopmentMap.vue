<template>
  <div class="development-map-page">
    <section class="hero-card">
      <div class="hero-copy">
        <span class="eyebrow">发展图谱</span>
        <h1>围绕当前职业画像，动态生成岗位晋升与换岗路径</h1>
        <p>
          当前目标岗位为 {{ runtimeMeta.targetJobName }}，目标行业为 {{ runtimeMeta.targetIndustry }}。
          图谱会优先结合你已填写的职业画像与人岗匹配结果，展示岗位描述、垂直晋升关系和横向转岗方向。
        </p>
      </div>

      <div class="hero-actions">
        <div class="hero-stat-list">
          <div class="hero-stat">
            <strong>{{ promotionNodes.length }}</strong>
            <span>晋升节点</span>
          </div>
          <div class="hero-stat">
            <strong>{{ transferRoles.length }}</strong>
            <span>换岗方向</span>
          </div>
          <div class="hero-stat">
            <strong>{{ totalTransferPaths }}</strong>
            <span>换岗路径</span>
          </div>
        </div>
      </div>
    </section>

    <section class="content-grid">
      <div class="chart-card">
        <div class="card-head">
          <div class="chart-head-left">
            <el-radio-group v-model="viewMode" size="large">
              <el-radio-button label="vertical">垂直岗位图谱</el-radio-button>
              <el-radio-button label="transfer">换岗路径图谱</el-radio-button>
            </el-radio-group>
            <el-select v-model="selectedJobId" class="job-selector" placeholder="选择岗位" filterable>
              <el-option v-for="job in selectableJobs" :key="job.id" :label="job.name" :value="job.id" />
            </el-select>
          </div>
          <div class="chart-head-right">
            <div>
              <span class="card-kicker">{{ currentViewMeta.kicker }}</span>
              <h2>{{ currentViewMeta.title }}</h2>
            </div>
          </div>
        </div>

        <div class="chart-toolbar">
          <div class="toolbar-note">
            {{ toolbarText }}
          </div>
          <div class="toolbar">
            <el-button-group>
              <el-button @click="zoomChart(1.15)">放大</el-button>
              <el-button @click="zoomChart(1 / 1.15)">缩小</el-button>
              <el-button @click="resetChart">重置</el-button>
            </el-button-group>
          </div>
        </div>

        <div ref="chartRef" class="graph-canvas"></div>

        <div class="legend-row">
          <div class="legend-item"><span class="legend-dot current"></span><span>当前聚焦岗位</span></div>
          <div class="legend-item"><span class="legend-dot next"></span><span>晋升目标岗位</span></div>
          <div class="legend-item"><span class="legend-dot related"></span><span>关联岗位</span></div>
          <div class="legend-item"><span class="legend-line solid"></span><span>晋升路径</span></div>
          <div class="legend-item"><span class="legend-line dashed"></span><span>换岗路径</span></div>
        </div>
      </div>

      <aside class="detail-column">
        <div class="summary-card">
          <span class="card-kicker">岗位摘要</span>
          <h3>{{ selectedJob.name }}</h3>
          <p>{{ selectedJob.summary }}</p>
          <div class="summary-tags">
            <el-tag>{{ selectedJob.level }}</el-tag>
            <el-tag type="success">{{ selectedJob.salary }}</el-tag>
            <el-tag type="warning">{{ selectedJob.experience }}</el-tag>
          </div>
        </div>

        <div class="detail-card">
          <div class="section-title">
            <h3>岗位描述</h3>
            <span>{{ selectedJob.track }}</span>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="核心职责">{{ selectedJob.description }}</el-descriptions-item>
            <el-descriptions-item label="典型产出">{{ selectedJob.deliverables.join('、') }}</el-descriptions-item>
            <el-descriptions-item label="关键能力">{{ selectedJob.skills.join('、') }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div v-if="viewMode === 'vertical'" class="detail-card">
          <div class="section-title">
            <h3>晋升路径关联</h3>
            <span>纵向成长</span>
          </div>
          <el-timeline>
            <el-timeline-item v-for="step in selectedPromotionTrail" :key="step.id"
              :type="step.id === selectedJobId ? 'primary' : 'success'" :timestamp="step.period">
              <div class="path-block">
                <strong>{{ step.name }}</strong>
                <p>{{ step.goal }}</p>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-alert :title="`下一阶段目标：${selectedJob.nextStep}`" :description="selectedJob.nextAdvice"
            type="success" :closable="false" show-icon />
        </div>

        <div v-else class="detail-card">
          <div class="section-title">
            <h3>换岗路径方案</h3>
            <span>每个方向至少 2 条路径</span>
          </div>
          <div class="transfer-role-list">
            <div v-for="role in transferRoles" :key="role.id" class="transfer-role-item"
              :class="{ active: role.id === selectedTransferRole.id }"
              @click="selectTransferRole(role.id)">
              <div>
                <strong>{{ role.name }}</strong>
                <p>{{ role.summary }}</p>
              </div>
              <span>{{ role.paths.length }} 条路径</span>
            </div>
          </div>
        </div>

        <div v-if="viewMode === 'transfer'" class="detail-card">
          <div class="section-title">
            <h3>{{ selectedTransferRole.name }}</h3>
            <span>转岗详情</span>
          </div>
          <div v-for="path in selectedTransferRole.paths" :key="path.id" class="transfer-path-card">
            <div class="transfer-path-top">
              <strong>{{ path.title }}</strong>
              <el-tag :type="path.difficultyType">{{ path.difficulty }}</el-tag>
            </div>
            <p>{{ path.description }}</p>
            <div class="mini-label">转岗步骤</div>
            <ol class="plain-steps">
              <li v-for="step in path.steps" :key="step">{{ step }}</li>
            </ol>
          </div>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch
} from 'vue'
import * as echarts from 'echarts'

import type {
  ECharts,
  EChartsCoreOption
} from 'echarts'

import {
  buildDynamicDevelopmentData,
  loadCareerFormData,
  loadJobMatchResult
} from '@/utils/career-runtime'

import type {
  JobMatchItem
} from '@/types/job-match'

type ViewMode = 'vertical' | 'transfer'

interface PromotionNode {
  id: string
  name: string
  level: string
  track: string
  salary: string
  experience: string
  period: string
  goal: string
  summary: string
  description: string
  deliverables: string[]
  skills: string[]
  nextStep: string
  nextAdvice: string
}

interface TransferPath {
  id: string
  title: string
  description: string
  difficulty: string
  difficultyType: 'success' | 'warning' | 'danger' | 'info'
  steps: string[]
}

interface TransferRole {
  id: string
  name: string
  summary: string
  description: string
  level: string
  salary: string
  experience: string
  track: string
  deliverables: string[]
  skills: string[]
  nextStep: string
  nextAdvice: string
  paths: TransferPath[]
}

const emptyTransferRole: TransferRole = {
  id: 'transfer-empty',
  name: '暂无换岗方向',
  summary: '当前暂无可展示的换岗路径，请先完成人岗匹配分析。',
  description: '暂无数据',
  level: '待补充',
  salary: '待补充',
  experience: '待补充',
  track: '待补充',
  deliverables: ['待补充'],
  skills: ['待补充'],
  nextStep: '待补充',
  nextAdvice: '请先完成人岗匹配分析或完善职业画像表单。',
  paths: []
}

const emptyPromotionNode: PromotionNode = {
  id: 'promotion-empty',
  name: '暂无目标岗位',
  level: '待补充',
  track: '待补充',
  salary: '待补充',
  experience: '待补充',
  period: '待补充',
  goal: '请先完善职业画像表单中的目标岗位信息。',
  summary: '当前暂无可展示的岗位成长路径。',
  description: '请先填写目标岗位并生成人岗匹配结果。',
  deliverables: ['待补充'],
  skills: ['待补充'],
  nextStep: '待补充',
  nextAdvice: '先完善职业画像表单，再查看动态发展图谱。'
}

const chartRef = ref<HTMLDivElement>()
let chartInstance: ECharts | null = null
const currentZoom = ref(1)
const viewMode = ref<ViewMode>('vertical')
const formData = ref(loadCareerFormData())
const matchItems = ref<JobMatchItem[]>(loadJobMatchResult())

const runtimeMeta = computed(() => buildDynamicDevelopmentData(formData.value, matchItems.value))

const splitText = (value: string | undefined) =>
  (value || '')
    .split(/[、, ，/；; |\n]/)
    .map((item) => item.trim())
    .filter(Boolean)

const topMatch = computed(() => matchItems.value[0] || null)

const coreSkills = computed(() =>
  splitText(topMatch.value?.raw_data.profiles.professional_skills.core_skills)
)

const promotionPath = computed(() => {
  const path = splitText(topMatch.value?.raw_data.profiles.job_attributes.vertical_promotion_path)
  return path.length
    ? path
    : [
        `资深${runtimeMeta.value.targetJobName}`,
        `${runtimeMeta.value.targetJobName}负责人`,
        `高级${runtimeMeta.value.targetJobName}管理岗`
      ]
})

const lateralDirections = computed(() => {
  const dirs = splitText(topMatch.value?.raw_data.profiles.job_attributes.lateral_transfer_directions)
  return dirs.length ? dirs : ['产品经理', '运营经理', '数据分析师', '项目经理', '用户研究员']
})

const promotionNodes = computed<PromotionNode[]>(() => {
  const targetJob = runtimeMeta.value.targetJobName
  const industry = runtimeMeta.value.targetIndustry
  const salary = topMatch.value?.raw_data.profiles.job_attributes.salary_competitiveness || '待补充'

  const baseSkills = coreSkills.value.length
    ? coreSkills.value
    : ['岗位核心技能', '项目协作', '业务理解']
  const stages = [targetJob, ...promotionPath.value.slice(0, 4)]
  return stages.map((name, index) => ({
    id: `promotion-${index}`,
    name,
    level: index === 0 ? '当前目标岗位' : `晋升阶段 ${index}`,
    track: industry,
    salary: index === 0 ? salary : `${salary} / 晋升后提升`,
    experience: index === 0 ? '0-2 年' : `${index * 2}-${index * 2 + 2}年`,
    period: index === 0 ? '入岗阶段' : `阶段 ${index}`,
    goal:
      index === 0
        ? `进入 ${name} 岗位并完成岗位基础能力补齐。`
        : `向 ${name} 发展，提升更复杂场景下的项目和业务能力。`,
    summary:
      index === 0
        ? `结合职业画像与匹配结果，当前优先关注 ${name}。`
        : `${name} 是 ${targetJob} 的后续发展方向之一。`,
    description:
      topMatch.value?.deep_analysis.all_analysis ||
      `围绕 ${name} 的岗位要求，持续提升专业能力、业务理解与项目产出。`,
    deliverables: ['项目成果', '方案沉淀', '阶段复盘'],
    skills: baseSkills.slice(0, Math.min(baseSkills.length, 4)),
    nextStep: stages[index + 1] || '持续成长',
    nextAdvice:
      index === 0
        ? topMatch.value?.deep_analysis.actionable_advice || '优先补齐关键技能差距，进入目标岗位。'
        : `继续向 ${stages[index + 1] || '更高层级岗位'} 提升。`
  }))
})

const buildTransferPath = (roleName: string, index: number): TransferRole => ({
  id: `transfer-${index}`,
  name: roleName,
  summary: `从 ${runtimeMeta.value.targetJobName} 转向 ${roleName} 的可行路径。`,
  description: `结合当前岗位画像与目标岗位要求，${roleName} 是一条可延展的横向发展方向。`,
  level: '关联岗位',
  salary: topMatch.value?.raw_data.profiles.job_attributes.salary_competitiveness || '待补充',
  experience: '1-3 年起步',
  track: runtimeMeta.value.targetIndustry,
  deliverables: ['转岗能力证明', '项目案例', '岗位认知沉淀'],
  skills: splitText(topMatch.value?.raw_data.profiles.professional_skills.tool_capabilities)
    .slice(0, 4)
    .concat(roleName)
    .slice(0, 4),
  nextStep: `${roleName} 进阶岗位`,
  nextAdvice: `建议围绕 ${roleName} 补齐差异能力，并用项目/实习验证转岗可行性。`,
  paths: [
    {
      id: `path-a-${index}`,
      title: `${runtimeMeta.value.targetJobName} -> ${roleName}`,
      description: '基于现有画像直接补齐岗位关键能力后转入目标方向。',
      difficulty: '中等',
      difficultyType: 'warning',
      steps: ['识别岗位差距', '补齐核心技能', '形成可展示案例']
    },
    {
      id: `path-b-${index}`,
      title: `${runtimeMeta.value.targetJobName} -> 过渡岗位 -> ${roleName}`,
      description: '先通过关联岗位积累经验，再平滑转入目标方向。',
      difficulty: '较稳妥',
      difficultyType: 'success',
      steps: ['选择过渡岗位', '积累业务经验', '完成方向切换']
    }
  ]
})

const transferRoles = computed<TransferRole[]>(() =>
  lateralDirections.value.slice(0, 5).map(buildTransferPath)
)

const promotionTrail = computed(() =>
  promotionNodes.value.map(({ id, name, period, goal }) => ({ id, name, period, goal }))
)

const totalTransferPaths = computed(() =>
  transferRoles.value.reduce((sum, role) => sum + role.paths.length, 0)
)

const selectedJobId = ref('promotion-0')
const selectedTransferRoleId = ref('transfer-0')

const selectableJobs = computed(() =>
  viewMode.value === 'vertical'
    ? promotionNodes.value.map(({ id, name }) => ({ id, name }))
    : transferRoles.value.map(({ id, name }) => ({ id, name }))
)

const selectedJob = computed(() => {
  if (viewMode.value === 'vertical') {
    return (
      promotionNodes.value.find((item) => item.id === selectedJobId.value) ??
      promotionNodes.value[0] ??
      emptyPromotionNode
    )
  }
  return (
    transferRoles.value.find((item) => item.id === selectedJobId.value) ??
    transferRoles.value[0] ??
    emptyTransferRole
  )
})

const selectedPromotionTrail = computed(() => {
  const currentIndex = promotionNodes.value.findIndex((item) => item.id === selectedJobId.value)
  return currentIndex < 0
    ? promotionTrail.value
    : promotionTrail.value.slice(0, Math.min(currentIndex + 2, promotionTrail.value.length))
})

const selectedTransferRole = computed(
  () =>
    transferRoles.value.find((item) => item.id === selectedTransferRoleId.value) ??
    transferRoles.value[0] ??
    emptyTransferRole
)

const currentViewMeta = computed(() =>
  viewMode.value === 'vertical'
    ? {
        kicker: '岗位晋升关系',
        title: `垂直岗位图谱：${runtimeMeta.value.targetJobName} 的成长路径`
      }
    : {
        kicker: '岗位血缘关系',
        title: `换岗路径图谱：${runtimeMeta.value.targetJobName} 的横向转岗方向`
      }
)

const toolbarText = computed(() =>
  viewMode.value === 'vertical'
    ? `当前图谱结合目标岗位"${runtimeMeta.value.targetJobName}"与匹配结果中的垂直晋升路径动态生成。`
    : `当前图谱结合匹配结果中的横向转岗方向动态生成，至少展示 5 个岗位方向。`
)

const syncSelectionByMode = () => {
  selectedJobId.value =
    viewMode.value === 'vertical' ? promotionNodes.value[0]?.id || '' : transferRoles.value[0]?.id || ''
  selectedTransferRoleId.value = transferRoles.value[0]?.id || ''
}

const buildVerticalOption = (): EChartsCoreOption => ({
  title: {
    text: '职业发展垂直图谱',
    subtext: `当前目标岗位：${runtimeMeta.value.targetJobName}`,
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  series: [
    {
      type: 'graph',
      layout: 'force',
      roam: true,
      zoom: currentZoom.value,
      symbolSize: 78,
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: 8,
      label: {
        show: true,
        formatter: '{b}',
        fontSize: 12
      },
      lineStyle: {
        width: 3,
        color: '#1f8fff',
        curveness: 0.18
      },
      force: {
        repulsion: 320,
        edgeLength: 130,
        gravity: 0.08
      },
      data: promotionNodes.value.map((node) => ({
        id: node.id,
        name: node.name,
        itemStyle: {
          color: node.id === selectedJobId.value ? '#1d4ed8' : '#8bd3dd',
          borderColor: node.id === selectedJobId.value ? '#0f172a' : '#0f766e',
          borderWidth: 2
        }
      })),
      links: promotionNodes.value.slice(0, -1).map((node, index) => {
        const nextNode = promotionNodes.value[index + 1]
        return {
          source: node.id,
          target: nextNode?.id ?? '',
          label: {
            show: true,
            formatter: nextNode?.period ?? ''
          }
        }
      })
    }
  ]
})

const buildTransferOption = (): EChartsCoreOption => ({
  title: {
    text: '岗位换岗路径图谱',
    subtext: `当前目标岗位：${runtimeMeta.value.targetJobName}`,
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  series: [
    {
      type: 'graph',
      layout: 'force',
      roam: true,
      zoom: currentZoom.value,
      force: {
        repulsion: 320,
        edgeLength: [120, 160]
      },
      label: {
        show: true,
        formatter: '{b}',
        fontSize: 12
      },
      lineStyle: {
        color: '#fb7185',
        width: 2,
        type: 'dashed',
        curveness: 0.15
      },
      data: [
        {
          id: 'origin',
          name: runtimeMeta.value.targetJobName,
          symbolSize: 94,
          itemStyle: {
            color: '#f97316',
            borderColor: '#7c2d12',
            borderWidth: 2
          }
        },
        ...transferRoles.value.map((role) => ({
          id: role.id,
          name: role.name,
          value: role.paths.length,
          symbolSize: role.id === selectedTransferRoleId.value ? 84 : 72,
          itemStyle: {
            color: role.id === selectedTransferRoleId.value ? '#ec4899' : '#a5b4fc',
            borderColor: role.id === selectedTransferRoleId.value ? '#831843' : '#3730a3',
            borderWidth: 2
          }
        }))
      ],
      links: transferRoles.value.flatMap((role) =>
        role.paths.map((path) => ({
          source: 'origin',
          target: role.id,
          value: path.title,
          label: {
            show: false
          }
        }))
      )
    }
  ]
})

const renderChart = () => {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
    chartInstance.on('click', (params: unknown) => {
      const p = params as {
        data?: {
          id?: string
        }
      }

      const nodeId = p.data?.id
      if (!nodeId || nodeId === 'origin') return
      if (viewMode.value === 'vertical') {
        selectedJobId.value = nodeId
      } else {
        selectTransferRole(nodeId)
      }
    })
  }

  chartInstance.setOption(
    viewMode.value === 'vertical' ? buildVerticalOption() : buildTransferOption(),
    true
  )
}

const zoomChart = (ratio: number) => {
  currentZoom.value = Math.min(2.4, Math.max(0.6, currentZoom.value * ratio))
  renderChart()
}

const resetChart = () => {
  currentZoom.value = 1
  renderChart()
}

const selectTransferRole = (roleId: string) => {
  selectedTransferRoleId.value = roleId
  selectedJobId.value = roleId
}

const handleResize = () => chartInstance?.resize()

watch(viewMode, async () => {
  syncSelectionByMode()
  await nextTick()
  renderChart()
})

watch(selectedJobId, () => {
  if (viewMode.value === 'transfer') selectedTransferRoleId.value = selectedJobId.value
  renderChart()
})

onMounted(async () => {
  syncSelectionByMode()
  await nextTick()
  renderChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped lang="scss">
.development-map-page {
  min-height: 100vh;
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(34, 197, 94, 0.14), transparent 34%),
    radial-gradient(circle at top right, rgba(249, 115, 22, 0.12), transparent 28%),
    linear-gradient(180deg, #f7fbff 0%, #eef4ff 100%);
}

.hero-card,
.chart-card,
.summary-card,
.detail-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(10px);
}

.hero-card {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 28px;
  padding: 28px;
  border-radius: 28px;
}

.eyebrow,
.card-kicker {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #2563eb;
}

.hero-copy h1 {
  margin: 12px 0 14px;
  font-size: 34px;
  line-height: 1.25;
  color: #0f172a;
}

.hero-copy p {
  margin: 0;
  font-size: 15px;
  line-height: 1.8;
  color: #475569;
}

.hero-actions {
  display: flex;
  align-items: center;
}

.job-selector {
  width: 220px;
}

.hero-stat-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.hero-stat {
  padding: 16px;
  border-radius: 20px;
  background: linear-gradient(135deg, #dbeafe 0%, #fef3c7 100%);
}

.hero-stat strong {
  display: block;
  margin-bottom: 6px;
  font-size: 28px;
  color: #0f172a;
}

.hero-stat span {
  font-size: 13px;
  color: #475569;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) 430px;
  gap: 22px;
  margin-top: 22px;
}

.chart-card {
  padding: 24px;
  border-radius: 26px;
}

.card-head,
.section-title,
.transfer-path-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-head {
  align-items: flex-start;
}

.chart-head-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.chart-head-right {
  text-align: right;
}

.chart-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(219, 234, 254, 0.78), rgba(255, 247, 237, 0.78));
}

.toolbar-note {
  font-size: 13px;
  color: #475569;
}

.card-head h2,
.section-title h3,
.summary-card h3 {
  margin: 6px 0 0;
  color: #0f172a;
}

.graph-canvas {
  height: 620px;
  margin-top: 16px;
}

.legend-row {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  padding-top: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
}

.legend-dot.current {
  background: #1d4ed8;
}

.legend-dot.next {
  background: #f97316;
}

.legend-dot.related {
  background: #a855f7;
}

.legend-line {
  width: 26px;
  height: 2px;
  background: #475569;
}

.legend-line.dashed {
  background: repeating-linear-gradient(to right, #475569 0, #475569 6px, transparent 6px, transparent 12px);
}

.detail-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-card,
.detail-card {
  padding: 22px;
  border-radius: 24px;
}

.summary-card p,
.detail-card p,
.transfer-role-item p {
  color: #475569;
  line-height: 1.7;
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.path-block p {
  margin: 6px 0 0;
}

.transfer-role-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.transfer-role-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.transfer-role-item.active,
.transfer-role-item:hover {
  border-color: rgba(236, 72, 153, 0.4);
  background: #fff1f7;
  transform: translateY(-1px);
}

.transfer-role-item span {
  color: #be185d;
  font-size: 12px;
  white-space: nowrap;
}

.transfer-path-card {
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #fff7ed 0%, #fdf2f8 100%);
}

.transfer-path-card + .transfer-path-card {
  margin-top: 12px;
}

.mini-label {
  margin-top: 10px;
  font-size: 12px;
  font-weight: 700;
  color: #7c3aed;
}

.plain-steps {
  margin: 8px 0 0;
  padding-left: 18px;
  color: #475569;
  line-height: 1.8;
}

@media (max-width: 1200px) {
  .hero-card,
  .content-grid {
    grid-template-columns: 1fr;
  }

  .detail-column {
    order: 2;
  }
}

@media (max-width: 768px) {
  .development-map-page {
    padding: 14px;
  }

  .hero-card,
  .chart-card,
  .summary-card,
  .detail-card {
    border-radius: 20px;
  }

  .hero-copy h1 {
    font-size: 26px;
  }

  .hero-stat-list,
  .content-grid {
    grid-template-columns: 1fr;
  }

  .graph-canvas {
    height: 480px;
  }

  .card-head,
  .section-title,
  .transfer-path-top,
  .chart-toolbar,
  .chart-head-left {
    align-items: flex-start;
    flex-direction: column;
  }

  .chart-head-right {
    text-align: left;
  }
}
</style>
