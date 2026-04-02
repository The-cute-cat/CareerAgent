<template>
  <div class="career-report-page">
    <section class="report-hero">
      <div class="hero-main">
        <span class="eyebrow">生涯报告</span>
        <h1>基于当前职业画像与匹配结果动态生成职业发展报告</h1>
        <p>
          报告内容会优先读取你在职业画像表单中填写的数据，以及已经生成的人岗匹配结果，
          自动形成岗位匹配、职业目标、路径规划、行动计划和成果展示内容。
        </p>
      </div>
      <div class="hero-actions">
        <el-switch v-model="previewMode" inline-prompt active-text="预览" inactive-text="编辑" />
        <el-button type="success" @click="polishAllContent">智能润色</el-button>
        <el-button type="warning" @click="checkCompleteness">完整性检查</el-button>
        <el-dropdown @command="handleExport">
          <el-button type="primary">
            导出报告
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
              <el-dropdown-item command="word">导出 Word</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </section>

    <div class="metric-grid">
      <div class="metric-card highlight">
        <span>综合匹配度</span>
        <strong>{{ matchingSummary.totalScore }}%</strong>
        <p>{{ matchingSummary.conclusion }}</p>
      </div>
      <div class="metric-card">
        <span>目标岗位</span>
        <strong>{{ reportData.userInfo.targetPosition }}</strong>
        <p>{{ reportData.goalSummary.shortTerm }}</p>
      </div>
      <div class="metric-card">
        <span>行业趋势判断</span>
        <strong>{{ reportData.trendSummary.outlook }}</strong>
        <p>{{ reportData.trendSummary.note }}</p>
      </div>
      <div class="metric-card">
        <span>待补齐能力项</span>
        <strong>{{ biggestGap.label }}</strong>
        <p>差距 {{ biggestGap.gap }} 分，优先纳入短期计划。</p>
      </div>
    </div>

    <div class="main-layout">
      <div class="content-panel" id="report-content">
        <section class="base-info-card">
          <div class="section-heading">
            <div>
              <span class="section-kicker">学生画像</span>
              <h2>基本信息与职业意向</h2>
            </div>
            <el-tag type="info">生成时间 {{ reportData.meta.generateTime }}</el-tag>
          </div>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="姓名">{{ reportData.userInfo.name }}</el-descriptions-item>
            <el-descriptions-item label="专业">{{ reportData.userInfo.major }}</el-descriptions-item>
            <el-descriptions-item label="年级">{{ reportData.userInfo.grade }}</el-descriptions-item>
            <el-descriptions-item label="目标岗位">{{ reportData.userInfo.targetPosition }}</el-descriptions-item>
            <el-descriptions-item label="目标行业">{{ reportData.userInfo.targetIndustry }}</el-descriptions-item>
            <el-descriptions-item label="目标城市">{{ reportData.userInfo.targetCity }}</el-descriptions-item>
          </el-descriptions>
        </section>

        <el-tabs v-model="activeTab" class="report-tabs">
          <el-tab-pane label="岗位匹配" name="matching">
            <section class="tab-section">
              <div class="section-heading">
                <div>
                  <span class="section-kicker">职业探索与岗位匹配</span>
                  <h2>人岗匹配度分析</h2>
                </div>
                <el-button text @click="focusEditor('matching')">编辑本节</el-button>
              </div>
              <div class="chart-grid">
                <div class="chart-card"><div ref="radarChartRef" class="chart-box"></div></div>
                <div class="chart-card"><div ref="gapChartRef" class="chart-box"></div></div>
              </div>
              <div class="dimension-list">
                <div v-for="item in reportData.matchingDimensions" :key="item.label" class="dimension-item">
                  <div class="dimension-top">
                    <strong>{{ item.label }}</strong>
                    <span>{{ item.current }}/{{ item.target }}</span>
                  </div>
                  <el-progress :percentage="Math.round((item.current / item.target) * 100)" :stroke-width="10" />
                  <p>{{ item.analysis }}</p>
                </div>
              </div>
              <div class="recommend-card">
                <div class="recommend-head">
                  <h3>岗位推荐与匹配结论</h3>
                  <el-tag type="success">Top 3 推荐</el-tag>
                </div>
                <div class="recommend-list">
                  <div v-for="item in reportData.recommendedJobs" :key="item.name" class="recommend-item">
                    <div>
                      <strong>{{ item.name }}</strong>
                      <p>{{ item.reason }}</p>
                    </div>
                    <span>{{ item.score }}%</span>
                  </div>
                </div>
              </div>
              <WangEditor v-model="reportData.content.matching" :height="editorHeight" :mode="previewMode ? 'simple' : 'default'" @change="handleContentChange('matching')" />
            </section>
          </el-tab-pane>

          <el-tab-pane label="目标规划" name="goals">
            <section class="tab-section">
              <div class="section-heading">
                <div>
                  <span class="section-kicker">职业目标设定</span>
                  <h2>职业目标与社会需求分析</h2>
                </div>
                <el-button text @click="focusEditor('goals')">编辑本节</el-button>
              </div>
              <div class="info-grid">
                <div class="info-card">
                  <h3>目标设定</h3>
                  <ul>
                    <li><strong>短期：</strong>{{ reportData.goalSummary.shortTerm }}</li>
                    <li><strong>中期：</strong>{{ reportData.goalSummary.midTerm }}</li>
                    <li><strong>长期：</strong>{{ reportData.goalSummary.longTerm }}</li>
                  </ul>
                </div>
                <div class="info-card">
                  <h3>社会需求与行业趋势</h3>
                  <ul>
                    <li v-for="item in reportData.trendSummary.highlights" :key="item">{{ item }}</li>
                  </ul>
                </div>
              </div>
              <WangEditor v-model="reportData.content.goals" :height="editorHeight" :mode="previewMode ? 'simple' : 'default'" @change="handleContentChange('goals')" />
            </section>
          </el-tab-pane>

          <el-tab-pane label="路径规划" name="pathway">
            <section class="tab-section">
              <div class="section-heading">
                <div>
                  <span class="section-kicker">职业路径规划</span>
                  <h2>清晰职业发展路径</h2>
                </div>
                <el-button text @click="focusEditor('pathway')">编辑本节</el-button>
              </div>
              <div class="chart-card pathway-chart-card">
                <div ref="pathwayChartRef" class="chart-box pathway-chart"></div>
              </div>
              <div class="roadmap-list">
                <div v-for="item in reportData.pathwayMilestones" :key="item.stage" class="roadmap-item">
                  <span class="stage">{{ item.stage }}</span>
                  <strong>{{ item.role }}</strong>
                  <p>{{ item.focus }}</p>
                </div>
              </div>
              <WangEditor v-model="reportData.content.pathway" :height="editorHeight" :mode="previewMode ? 'simple' : 'default'" @change="handleContentChange('pathway')" />
            </section>
          </el-tab-pane>

          <el-tab-pane label="行动计划" name="action">
            <section class="tab-section">
              <div class="section-heading">
                <div>
                  <span class="section-kicker">行动计划与成果展示</span>
                  <h2>短期 / 中期成长计划</h2>
                </div>
                <el-button text @click="focusEditor('action')">编辑本节</el-button>
              </div>
              <div class="phase-grid">
                <div class="phase-card" v-for="phase in reportData.actionPhases" :key="phase.title">
                  <div class="phase-head">
                    <strong>{{ phase.title }}</strong>
                    <el-tag :type="phase.tagType">{{ phase.period }}</el-tag>
                  </div>
                  <p>{{ phase.summary }}</p>
                  <div class="mini-label">学习路径</div>
                  <ul><li v-for="item in phase.learning" :key="item">{{ item }}</li></ul>
                  <div class="mini-label">实践安排</div>
                  <ul><li v-for="item in phase.practice" :key="item">{{ item }}</li></ul>
                  <div class="mini-label">评估指标</div>
                  <ul><li v-for="item in phase.metrics" :key="item">{{ item }}</li></ul>
                </div>
              </div>
              <WangEditor v-model="reportData.content.action" :height="editorHeight" :mode="previewMode ? 'simple' : 'default'" @change="handleContentChange('action')" />
            </section>
          </el-tab-pane>

          <el-tab-pane label="成果展示" name="assessment">
            <section class="tab-section">
              <div class="section-heading">
                <div>
                  <span class="section-kicker">成果展示与复盘</span>
                  <h2>阶段成果与后续建议</h2>
                </div>
                <el-button text @click="focusEditor('assessment')">编辑本节</el-button>
              </div>
              <div class="info-grid">
                <div class="info-card">
                  <h3>已形成成果</h3>
                  <ul><li v-for="item in reportData.outcomes" :key="item">{{ item }}</li></ul>
                </div>
                <div class="info-card">
                  <h3>动态调整建议</h3>
                  <ul><li v-for="item in reportData.adjustments" :key="item">{{ item }}</li></ul>
                </div>
              </div>
              <WangEditor v-model="reportData.content.assessment" :height="editorHeight" :mode="previewMode ? 'simple' : 'default'" @change="handleContentChange('assessment')" />
            </section>
          </el-tab-pane>
        </el-tabs>
      </div>

      <aside class="sidebar-panel">
        <div class="sidebar-card">
          <div class="section-heading compact">
            <div>
              <span class="section-kicker">内容检查</span>
              <h3>完整性状态</h3>
            </div>
            <el-button text @click="checkCompleteness">重新检查</el-button>
          </div>
          <div class="check-list">
            <div v-for="item in completenessChecklist" :key="item.key" class="check-item" :class="{ done: item.done }">
              <div>
                <strong>{{ item.label }}</strong>
                <p>{{ item.tip }}</p>
              </div>
              <el-tag :type="item.done ? 'success' : 'warning'">{{ item.done ? '已覆盖' : '待完善' }}</el-tag>
            </div>
          </div>
        </div>

        <div class="sidebar-card">
          <div class="section-heading compact">
            <div>
              <span class="section-kicker">智能润色</span>
              <h3>优化建议</h3>
            </div>
            <el-button text @click="regenerateSuggestions">刷新建议</el-button>
          </div>
          <div class="suggestion-list">
            <div v-for="(item, index) in polishSuggestions" :key="item.id" class="suggestion-item">
              <div class="suggestion-top">
                <el-tag :type="item.tagType">{{ item.category }}</el-tag>
                <span>{{ item.confidence }}%</span>
              </div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.suggestion }}</p>
              <div class="suggestion-actions">
                <el-button size="small" type="primary" @click="applyPolish(index)">应用</el-button>
                <el-button size="small" @click="removeSuggestion(index)">忽略</el-button>
              </div>
            </div>
          </div>
        </div>

        <div class="sidebar-card">
          <div class="section-heading compact">
            <div>
              <span class="section-kicker">编辑记录</span>
              <h3>操作历史</h3>
            </div>
          </div>
          <el-timeline>
            <el-timeline-item v-for="item in polishHistory" :key="item.time + item.action" :timestamp="item.time">
              {{ item.action }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </aside>
    </div>

    <div v-if="exporting" class="export-overlay">
      <el-progress type="circle" :percentage="exportProgress" />
      <p>{{ exportStatus }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import WangEditor from '@/components/Person_Report/WangEditor.vue'
import { buildDynamicReportData, loadCareerFormData, loadJobMatchResult } from '@/utils/career-runtime'

type ReportSection = 'matching' | 'goals' | 'pathway' | 'action' | 'assessment'

interface PolishSuggestion {
  id: string
  category: string
  title: string
  suggestion: string
  tagType: 'success' | 'warning' | 'danger'
  confidence: number
  apply: () => void
}

const previewMode = ref(false)
const activeTab = ref<ReportSection>('matching')
const editorHeight = '320px'
const exporting = ref(false)
const exportProgress = ref(0)
const exportStatus = ref('准备导出...')

const radarChartRef = ref<HTMLDivElement>()
const gapChartRef = ref<HTMLDivElement>()
const pathwayChartRef = ref<HTMLDivElement>()

let radarChart: echarts.ECharts | null = null
let gapChart: echarts.ECharts | null = null
let pathwayChart: echarts.ECharts | null = null

const initialReportData = buildDynamicReportData(loadCareerFormData(), loadJobMatchResult())
const reportData = reactive(initialReportData)

const polishHistory = reactive([
  { time: new Date().toLocaleString(), action: '已根据职业画像表单与岗位匹配结果生成动态报告。' }
])

const matchingSummary = computed(() => {
  const total = Math.round(
    reportData.matchingDimensions.reduce((sum, item) => sum + (item.current / item.target) * 100, 0) /
      reportData.matchingDimensions.length
  )
  return {
    totalScore: total,
    conclusion: total >= 80 ? '当前画像与目标岗位整体较为匹配，建议集中补齐少量关键差距。' : '当前仍有一定差距，建议优先落实阶段化补齐计划。'
  }
})

const biggestGap = computed(() => {
  const target = reportData.matchingDimensions.reduce((prev, current) =>
    current.target - current.current > prev.target - prev.current ? current : prev
  )
  return { label: target.label, gap: target.target - target.current }
})

const completenessChecklist = computed(() => [
  { key: 'matching', label: '职业探索与岗位匹配', tip: '来自当前表单与匹配结果。', done: reportData.content.matching.length > 80 },
  { key: 'goals', label: '职业目标设定', tip: '结合目标岗位与行业意向自动生成。', done: reportData.content.goals.length > 80 },
  { key: 'pathway', label: '职业路径规划', tip: '结合晋升路径自动组装。', done: reportData.content.pathway.length > 80 },
  { key: 'action', label: '行动计划', tip: '结合技能、项目、实习动态生成。', done: reportData.content.action.length > 80 },
  { key: 'assessment', label: '成果展示与导出', tip: '支持编辑、润色、检查与导出。', done: reportData.content.assessment.length > 60 }
])

const createSuggestions = (): PolishSuggestion[] => [
  {
    id: 's1',
    category: '表达优化',
    title: '强化匹配结论表达',
    suggestion: '建议补充“优势、差距、行动建议”三段式总结，让人岗匹配结论更利于展示。',
    tagType: 'success',
    confidence: 93,
    apply: () => {
      reportData.content.matching += '<p>建议展示时先说明当前优势，再说明关键差距，最后给出可执行行动建议。</p>'
    }
  },
  {
    id: 's2',
    category: '内容完整性',
    title: '补强评估周期',
    suggestion: '建议在行动计划中进一步强调季度复盘和指标跟踪机制。',
    tagType: 'warning',
    confidence: 90,
    apply: () => {
      reportData.content.action += '<p>建议以季度为单位复盘岗位投递、项目参与和能力提升情况，并根据结果动态调整下一阶段计划。</p>'
    }
  },
  {
    id: 's3',
    category: '逻辑增强',
    title: '补充中长期路径衔接',
    suggestion: '建议补充从当前目标岗位到中长期目标岗位之间的关键转折点。',
    tagType: 'danger',
    confidence: 87,
    apply: () => {
      reportData.content.pathway += '<p>中长期路径建议围绕复杂项目能力、业务理解和跨团队协同三个核心转折点持续推进。</p>'
    }
  }
]

const polishSuggestions = reactive<PolishSuggestion[]>(createSuggestions())

const pushHistory = (action: string) => {
  polishHistory.unshift({ time: new Date().toLocaleString(), action })
}

const initRadarChart = () => {
  if (!radarChartRef.value) return
  radarChart?.dispose()
  radarChart = echarts.init(radarChartRef.value)
  radarChart.setOption({
    title: { text: '能力画像对比', left: 'center', textStyle: { fontSize: 14 } },
    legend: { bottom: 0, data: ['当前能力', '岗位要求'] },
    radar: { radius: '62%', indicator: reportData.matchingDimensions.map((item) => ({ name: item.label, max: 100 })) },
    series: [{
      type: 'radar',
      data: [
        { name: '当前能力', value: reportData.matchingDimensions.map((item) => item.current), areaStyle: { color: 'rgba(37, 99, 235, 0.24)' }, lineStyle: { color: '#2563eb' } },
        { name: '岗位要求', value: reportData.matchingDimensions.map((item) => item.target), areaStyle: { color: 'rgba(22, 163, 74, 0.18)' }, lineStyle: { color: '#16a34a' } }
      ]
    }]
  })
}

const initGapChart = () => {
  if (!gapChartRef.value) return
  gapChart?.dispose()
  gapChart = echarts.init(gapChartRef.value)
  gapChart.setOption({
    title: { text: '能力差距量化', left: 'center', textStyle: { fontSize: 14 } },
    xAxis: { type: 'category', data: reportData.matchingDimensions.map((item) => item.label) },
    yAxis: { type: 'value', max: 100 },
    series: [
      { type: 'bar', data: reportData.matchingDimensions.map((item) => item.current), barWidth: 24, itemStyle: { color: '#38bdf8', borderRadius: [8, 8, 0, 0] } },
      { type: 'line', data: reportData.matchingDimensions.map((item) => item.target), smooth: true, lineStyle: { color: '#f97316', width: 3 } }
    ]
  })
}

const initPathwayChart = () => {
  if (!pathwayChartRef.value) return
  pathwayChart?.dispose()
  pathwayChart = echarts.init(pathwayChartRef.value)
  pathwayChart.setOption({
    series: [{
      type: 'sankey',
      nodeAlign: 'left',
      emphasis: { focus: 'adjacency' },
      data: reportData.pathwayMilestones.map((item) => ({ name: item.role })),
      links: reportData.pathwayMilestones.slice(0, -1).map((item, index) => {
        const nextItem = reportData.pathwayMilestones[index + 1]
        return { source: item.role, target: nextItem?.role ?? '', value: index + 2 }
      }),
      lineStyle: { color: 'gradient', curveness: 0.45 },
      itemStyle: { color: '#2563eb', borderColor: '#fff', borderWidth: 1 }
    }]
  })
}

const renderCharts = () => {
  initRadarChart()
  initGapChart()
  initPathwayChart()
}

const handleResize = () => {
  radarChart?.resize()
  gapChart?.resize()
  pathwayChart?.resize()
}

const handleContentChange = (_section: ReportSection) => {
  pushHistory('更新了报告内容。')
}

const focusEditor = (section: ReportSection) => {
  activeTab.value = section
}

const applyPolish = (index: number) => {
  const suggestion = polishSuggestions[index]
  if (!suggestion) return
  suggestion.apply()
  polishSuggestions.splice(index, 1)
  pushHistory(`应用了“${suggestion.title}”建议。`)
  ElMessage.success('已应用润色建议')
}

const removeSuggestion = (index: number) => {
  polishSuggestions.splice(index, 1)
  ElMessage.info('已忽略该建议')
}

const regenerateSuggestions = () => {
  polishSuggestions.splice(0, polishSuggestions.length, ...createSuggestions())
  pushHistory('重新生成了润色建议。')
  ElMessage.success('已刷新润色建议')
}

const polishAllContent = async () => {
  await ElMessageBox.confirm('将对当前动态报告内容进行统一润色，是否继续？', '智能润色', {
    type: 'info',
    confirmButtonText: '继续',
    cancelButtonText: '取消'
  })
  reportData.content.matching += '<p>建议在展示时优先说明当前优势、关键差距和下一步行动。</p>'
  reportData.content.goals += '<p>建议将职业目标拆分为可入岗、可成长和可转向三个层次。</p>'
  reportData.content.pathway += '<p>建议根据岗位反馈和项目经历，以 1-2 年为一个周期动态校正职业路径。</p>'
  reportData.content.action += '<p>建议同步记录阶段成果，如项目复盘、实习总结和岗位反馈表。</p>'
  reportData.content.assessment += '<p>后续每次更新职业画像或人岗匹配结果后，都可以继续刷新和导出本报告。</p>'
  pushHistory('执行了一键全文润色。')
  ElMessage.success('报告已完成一键润色')
}

const checkCompleteness = () => {
  const missing = completenessChecklist.value.filter((item) => !item.done)
  if (missing.length) {
    ElMessage.warning(`仍有 ${missing.length} 个模块建议继续补充。`)
    return
  }
  ElMessage.success('报告完整性检查通过')
}

const exportPDF = async () => {
  exporting.value = true
  exportProgress.value = 20
  exportStatus.value = '正在准备导出...'
  try {
    const element = document.getElementById('report-content')
    if (!element) throw new Error('未找到报告内容节点')
    const previousMode = previewMode.value
    previewMode.value = true
    await nextTick()
    exportProgress.value = 50
    exportStatus.value = '正在生成预览图...'
    const canvas = await html2canvas(element, { scale: 2, useCORS: true, backgroundColor: '#ffffff', logging: false })
    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgData = canvas.toDataURL('image/png')
    const pdfWidth = 210
    const pdfHeight = 297
    const imgHeight = (canvas.height * pdfWidth) / canvas.width
    let heightLeft = imgHeight
    let position = 0
    pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, imgHeight)
    heightLeft -= pdfHeight
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, imgHeight)
      heightLeft -= pdfHeight
    }
    exportProgress.value = 100
    exportStatus.value = '导出成功'
    pdf.save(`职业生涯发展报告_${reportData.userInfo.name}.pdf`)
    previewMode.value = previousMode
    pushHistory('导出了 PDF 报告。')
    ElMessage.success('PDF 导出成功')
  } catch (error) {
    ElMessage.error(`PDF 导出失败：${(error as Error).message}`)
  } finally {
    setTimeout(() => {
      exporting.value = false
      exportProgress.value = 0
    }, 800)
  }
}

const exportWord = () => {
  const html = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset='utf-8'><title>职业生涯发展报告</title></head>
    <body>
      <h1>职业生涯发展报告</h1>
      <h2>职业探索与岗位匹配</h2>${reportData.content.matching}
      <h2>职业目标设定</h2>${reportData.content.goals}
      <h2>职业路径规划</h2>${reportData.content.pathway}
      <h2>行动计划</h2>${reportData.content.action}
      <h2>成果展示</h2>${reportData.content.assessment}
    </body></html>`
  const blob = new Blob(['\ufeff', html], { type: 'application/msword' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `职业生涯发展报告_${reportData.userInfo.name}.doc`
  link.click()
  URL.revokeObjectURL(url)
  pushHistory('导出了 Word 报告。')
  ElMessage.success('Word 导出成功')
}

const handleExport = async (command: string) => {
  if (command === 'pdf') {
    await exportPDF()
    return
  }
  exportWord()
}

onMounted(async () => {
  await nextTick()
  renderCharts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  radarChart?.dispose()
  gapChart?.dispose()
  pathwayChart?.dispose()
})
</script>

<style scoped lang="scss">
.career-report-page { min-height: 100vh; padding: 28px; background: radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 30%), radial-gradient(circle at top right, rgba(249, 115, 22, 0.14), transparent 30%), linear-gradient(180deg, #f8fbff 0%, #eef3ff 100%); }
.report-hero,.metric-card,.content-panel,.sidebar-card,.chart-card,.base-info-card,.info-card,.phase-card,.recommend-card { background: rgba(255, 255, 255, 0.92); border: 1px solid rgba(148, 163, 184, 0.18); box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08); backdrop-filter: blur(10px); }
.report-hero { display: flex; justify-content: space-between; gap: 24px; padding: 28px; border-radius: 28px; }
.eyebrow,.section-kicker { display: inline-flex; font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #2563eb; }
.hero-main h1 { margin: 12px 0; font-size: 34px; line-height: 1.24; color: #0f172a; }
.hero-main p,.metric-card p,.dimension-item p,.recommend-item p,.check-item p,.suggestion-item p,.roadmap-item p,.phase-card p { color: #475569; line-height: 1.7; }
.hero-actions { display: flex; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-top: 20px; }
.metric-card { padding: 20px; border-radius: 22px; }
.metric-card.highlight { background: linear-gradient(135deg, #dbeafe 0%, #ecfccb 100%); }
.metric-card span { color: #64748b; font-size: 13px; }
.metric-card strong { display: block; margin: 12px 0 8px; font-size: 30px; color: #0f172a; }
.main-layout { display: grid; grid-template-columns: minmax(0, 1.55fr) 360px; gap: 20px; margin-top: 20px; }
.content-panel { padding: 24px; border-radius: 28px; }
.base-info-card,.sidebar-card { padding: 20px; border-radius: 22px; }
.report-tabs { margin-top: 18px; }
.tab-section { display: flex; flex-direction: column; gap: 18px; padding: 8px 0 18px; }
.section-heading,.dimension-top,.recommend-head,.phase-head,.suggestion-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.section-heading h2,.section-heading.compact h3 { margin: 6px 0 0; color: #0f172a; }
.chart-grid,.info-grid,.phase-grid,.dimension-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.chart-card,.info-card,.phase-card,.recommend-card { padding: 18px; border-radius: 20px; }
.chart-box { width: 100%; height: 320px; }
.pathway-chart { height: 340px; }
.dimension-item,.recommend-item,.check-item,.suggestion-item,.roadmap-item { padding: 14px 16px; border-radius: 18px; background: #f8fafc; }
.recommend-list,.check-list,.suggestion-list { display: flex; flex-direction: column; gap: 12px; }
.recommend-item { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.recommend-item span { font-size: 20px; font-weight: 700; color: #1d4ed8; }
.roadmap-list { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.roadmap-item .stage,.mini-label { display: inline-flex; margin-bottom: 8px; font-size: 12px; font-weight: 700; color: #7c3aed; }
.sidebar-panel { display: flex; flex-direction: column; gap: 16px; }
.check-item.done { background: #effcf3; border: 1px solid rgba(34, 197, 94, 0.24); }
.suggestion-item { background: linear-gradient(135deg, #fff7ed 0%, #fdf2f8 100%); }
.suggestion-item strong { display: block; margin-top: 8px; color: #0f172a; }
.suggestion-actions { display: flex; gap: 8px; margin-top: 10px; }
.export-overlay { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 16px; background: rgba(15, 23, 42, 0.62); color: #fff; z-index: 1000; }
@media (max-width: 1280px) { .metric-grid,.roadmap-list { grid-template-columns: repeat(2, minmax(0, 1fr)); } .main-layout { grid-template-columns: 1fr; } }
@media (max-width: 768px) { .career-report-page { padding: 14px; } .report-hero,.section-heading,.hero-actions { flex-direction: column; align-items: flex-start; } .hero-main h1 { font-size: 26px; } .metric-grid,.chart-grid,.info-grid,.phase-grid,.dimension-list,.roadmap-list { grid-template-columns: 1fr; } .content-panel,.base-info-card,.sidebar-card { border-radius: 20px; } }
</style>
