<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Briefcase,
  TrendCharts,
  Warning,
  InfoFilled,
  DataAnalysis,
  MagicStick,
  Document,
  ArrowLeft,
  CircleCheck,
  CircleClose,
  SuccessFilled,
  OfficeBuilding,
  School,
  Timer,
  Medal,
  User,
  Collection,
  Aim,
  Orange,
  Histogram,
  Opportunity,
  Connection,
  Promotion,
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { JobMatchItem } from '@/types/job-match'

const props = defineProps<{
  jobData?: JobMatchItem
}>()

const route = useRoute()
const router = useRouter()
const jobItem = ref<JobMatchItem | null>(props.jobData || null)
const loading = ref(!props.jobData)

let literacyChart: echarts.ECharts | null = null
let potentialChart: echarts.ECharts | null = null

const literacyOrder = ['communication', 'teamwork', 'stress_management', 'logic_thinking', 'ethics']
const potentialOrder = ['learning_ability', 'innovation', 'leadership', 'career_orientation', 'adaptability']

const score = computed(() => Math.round((jobItem.value?.score || 0) * 100))
const missingSkillCount = computed(() => jobItem.value?.deep_analysis.missing_key_skills.length || 0)
const literacyAverage = computed(() => {
  if (!jobItem.value) return 0
  const values = literacyOrder.map((key) =>
    literacyToNum(jobItem.value!.raw_data.profiles.professional_literacy[key as keyof typeof jobItem.value.raw_data.profiles.professional_literacy]),
  )
  return Math.round(values.reduce((sum, item) => sum + item, 0) / values.length)
})

const potentialAverage = computed(() => {
  if (!jobItem.value) return 0
  const values = potentialOrder.map((key) =>
    literacyToNum(jobItem.value!.raw_data.profiles.development_potential[key as keyof typeof jobItem.value.raw_data.profiles.development_potential]),
  )
  return Math.round(values.reduce((sum, item) => sum + item, 0) / values.length)
})

const dimensionCards = computed(() => {
  if (!jobItem.value) return []

  const baseRequirements = jobItem.value.raw_data.profiles.basic_requirements
  const baseScore =
    score.value >= 80
      ? Math.min(92, score.value)
      : baseRequirements.certificates && baseRequirements.certificates !== '无'
        ? Math.max(55, score.value - 4)
        : Math.max(50, score.value - 8)

  const skillPenalty = Math.min(26, missingSkillCount.value * 8)
  const skillScore = Math.max(38, Math.min(95, score.value - skillPenalty + 6))
  const literacyScore = Math.max(45, Math.min(96, literacyAverage.value))
  const potentialScore = Math.max(45, Math.min(96, potentialAverage.value))

  return [
    { key: 'basic', title: '基础匹配', desc: '学历、专业、经验与证书要求匹配度', value: baseScore, icon: School },
    { key: 'skills', title: '技能匹配', desc: '核心技能、工具能力与项目经验匹配度', value: skillScore, icon: MagicStick },
    { key: 'literacy', title: '素养匹配', desc: '职业素养结构与岗位协同要求匹配度', value: literacyScore, icon: User },
    { key: 'potential', title: '潜力匹配', desc: '学习、创新、适应与成长潜力匹配度', value: potentialScore, icon: TrendCharts },
  ]
})

const topActionItems = computed(() => {
  if (!jobItem.value) return []
  const adviceSource = jobItem.value.deep_analysis.actionable_advice || ''
  const adviceParts = adviceSource.split(/[；;。]\s*/).map((item) => item.trim()).filter(Boolean)
  const missingParts = jobItem.value.deep_analysis.missing_key_skills.map(
    (skill, index) => `优先补强第 ${index + 1} 项关键能力：${skill}`,
  )
  return [...missingParts, ...adviceParts].slice(0, 4)
})

const loadJobData = () => {
  if (props.jobData) {
    jobItem.value = props.jobData
    return
  }

  const jobId = route.query.jobId as string
  if (jobId) {
    const stored = localStorage.getItem('jobMatchResult')
    if (stored) {
      const items: JobMatchItem[] = JSON.parse(stored)
      const found = items.find(item => item.job_id === jobId)
      if (found) {
        jobItem.value = found
      } else {
        ElMessage.error('未找到岗位信息')
      }
    }
  }
  loading.value = false
}

const splitSkills = (str: string | any[] | null | undefined): string[] => {
  if (!str) return []
  if (Array.isArray(str)) return str.map((s) => String(s).trim()).filter(Boolean)
  if (typeof str === 'string') return str.split(/[,，、]/).map((s) => s.trim()).filter(Boolean)
  return []
}

const literacyToNum = (val: string): number => {
  if (val === '高') return 90
  if (val === '中') return 60
  if (val === '低') return 30
  return 50
}

const getMatchScoreColor = (scoreValue: number) => {
  if (scoreValue >= 80) return '#67C23A'
  if (scoreValue >= 60) return '#E6A23C'
  return '#F56C6C'
}

const getMatchScoreLevel = (scoreValue: number) => {
  if (scoreValue >= 85) return '非常匹配'
  if (scoreValue >= 70) return '较为匹配'
  if (scoreValue >= 55) return '基本匹配'
  return '有待提升'
}

const getGapLevel = (gapAnalysis: string) => {
  if (/明显|较大|不足|短板|欠缺|薄弱/.test(gapAnalysis)) {
    return { label: '高差距', type: 'danger' as const, color: '#F56C6C' }
  }
  if (/一定|需要|建议|提升|补足/.test(gapAnalysis)) {
    return { label: '中差距', type: 'warning' as const, color: '#E6A23C' }
  }
  return { label: '低差距', type: 'success' as const, color: '#67C23A' }
}

const getLiteracyOption = (literacy: any) => {
  const data = [
    literacyToNum(literacy.communication),
    literacyToNum(literacy.teamwork),
    literacyToNum(literacy.stress_management),
    literacyToNum(literacy.logic_thinking),
    literacyToNum(literacy.ethics)
  ]

  return {
    tooltip: { trigger: 'item' },
    radar: {
      indicator: [
        { name: '沟通能力', max: 100 },
        { name: '团队协作', max: 100 },
        { name: '抗压能力', max: 100 },
        { name: '逻辑思维', max: 100 },
        { name: '职业道德', max: 100 }
      ],
      shape: 'polygon',
      center: ['50%', '54%'],
      radius: '67%',
      name: { textStyle: { color: '#5e6b80', fontSize: 12, fontWeight: 500 } },
      splitArea: { areaStyle: { color: ['rgba(64,158,255,0.04)', 'rgba(64,158,255,0.08)', 'rgba(64,158,255,0.12)', 'rgba(64,158,255,0.16)'] } },
      axisLine: { lineStyle: { color: '#d8e2ef' } },
      splitLine: { lineStyle: { color: '#e6edf7' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: data,
        name: '职业素养',
        areaStyle: { color: 'rgba(64,158,255,0.28)' },
        lineStyle: { color: '#409EFF', width: 2.5 },
        itemStyle: { color: '#409EFF' },
        symbol: 'circle',
        symbolSize: 7
      }]
    }]
  }
}

const getPotentialOption = (potential: any) => {
  const data = [
    literacyToNum(potential.learning_ability),
    literacyToNum(potential.innovation),
    literacyToNum(potential.leadership),
    literacyToNum(potential.career_orientation),
    literacyToNum(potential.adaptability)
  ]

  return {
    tooltip: { trigger: 'item' },
    radar: {
      indicator: [
        { name: '学习能力', max: 100 },
        { name: '创新能力', max: 100 },
        { name: '领导力', max: 100 },
        { name: '职业取向', max: 100 },
        { name: '适应能力', max: 100 }
      ],
      shape: 'polygon',
      center: ['50%', '54%'],
      radius: '67%',
      name: { textStyle: { color: '#5e6b80', fontSize: 12, fontWeight: 500 } },
      splitArea: { areaStyle: { color: ['rgba(103,194,58,0.04)', 'rgba(103,194,58,0.08)', 'rgba(103,194,58,0.12)', 'rgba(103,194,58,0.16)'] } },
      axisLine: { lineStyle: { color: '#d8e2ef' } },
      splitLine: { lineStyle: { color: '#e6edf7' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: data,
        name: '发展潜力',
        areaStyle: { color: 'rgba(103,194,58,0.26)' },
        lineStyle: { color: '#67C23A', width: 2.5 },
        itemStyle: { color: '#67C23A' },
        symbol: 'circle',
        symbolSize: 7
      }]
    }]
  }
}

const initCharts = () => {
  if (!jobItem.value) return
  nextTick(() => {
    const item = jobItem.value
    if (!item) return

    const literacyEl = document.getElementById('literacy-radar')
    const potentialEl = document.getElementById('potential-radar')

    if (literacyEl) {
      literacyChart?.dispose()
      literacyChart = echarts.init(literacyEl)
      literacyChart.setOption(getLiteracyOption(item.raw_data.profiles.professional_literacy))
    }

    if (potentialEl) {
      potentialChart?.dispose()
      potentialChart = echarts.init(potentialEl)
      potentialChart.setOption(getPotentialOption(item.raw_data.profiles.development_potential))
    }
  })
}

const resizeCharts = () => {
  literacyChart?.resize()
  potentialChart?.resize()
}

const goBack = () => {
  router.push('/job-matching')
}

const formatLiteracyKey = (key: string): string => {
  const map: Record<string, string> = {
    communication: '沟通能力',
    teamwork: '团队协作',
    stress_management: '抗压能力',
    logic_thinking: '逻辑思维',
    ethics: '职业道德',
    learning_ability: '学习能力',
    innovation: '创新能力',
    leadership: '领导力',
    career_orientation: '职业取向',
    adaptability: '适应能力'
  }
  return map[key] || key
}

onMounted(() => {
  loadJobData()
  if (jobItem.value) {
    initCharts()
  }
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  literacyChart?.dispose()
  potentialChart?.dispose()
  window.removeEventListener('resize', resizeCharts)
})
</script>

<template>
  <div class="position-detail-container">
    <div class="detail-header">
      <el-button type="primary" text @click="goBack">
        <el-icon>
          <ArrowLeft />
        </el-icon>
        返回岗位列表
      </el-button>
      <h1 class="detail-title">
        <el-icon>
          <TrendCharts />
        </el-icon>
        岗位匹配分析报告
      </h1>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon" :size="48">
        <DataAnalysis />
      </el-icon>
      <p>正在加载岗位详情...</p>
    </div>

    <template v-else-if="jobItem">
      <section class="overview-section">
        <div class="overview-main info-card">
          <div class="overview-main__head">
            <div class="job-identity">
              <div class="job-icon">
                <el-icon :size="30">
                  <OfficeBuilding />
                </el-icon>
              </div>
              <div class="job-identity__content">
                <div class="eyebrow">F-09 岗位 AI 画像</div>
                <h2 class="job-name">{{ jobItem.raw_data.job_name }}</h2>
                <div class="job-tags">
                  <el-tag size="small" :color="getMatchScoreColor(score)" effect="dark">
                    {{ score }}分匹配
                  </el-tag>
                  <el-tag size="small" :type="jobItem.deep_analysis.can_apply ? 'success' : 'danger'" effect="light">
                    <el-icon class="tag-icon">
                      <CircleCheck v-if="jobItem.deep_analysis.can_apply" />
                      <CircleClose v-else />
                    </el-icon>
                    {{ jobItem.deep_analysis.can_apply ? '推荐投递' : '暂不建议直接投递' }}
                  </el-tag>
                  <el-tooltip
                    placement="top"
                    content="本次匹配结果综合了职业画像、岗位要求、技能标签、素养潜力等多维信息，由本地知识库岗位画像与 AI 提取结果支撑。"
                  >
                    <el-tag size="small" type="info" effect="plain">匹配可信度说明</el-tag>
                  </el-tooltip>
                </div>
              </div>
            </div>

            <div class="score-panel" :style="{ '--score-color': getMatchScoreColor(score) }">
              <div
                class="score-ring"
                :style="{ background: `conic-gradient(${getMatchScoreColor(score)} ${score * 3.6}deg, #e7eef7 0deg)` }"
              >
                <div class="score-ring__inner">
                  <strong>{{ score }}</strong>
                  <span>综合匹配分</span>
                </div>
              </div>
              <div class="score-level" :style="{ color: getMatchScoreColor(score) }">
                {{ getMatchScoreLevel(score) }}
              </div>
            </div>
          </div>

          <div class="overview-grid">
            <div class="overview-item">
              <el-icon><School /></el-icon>
              <span class="item-label">学历要求</span>
              <strong>{{ jobItem.raw_data.profiles.basic_requirements.degree }}</strong>
            </div>
            <div class="overview-item">
              <el-icon><Document /></el-icon>
              <span class="item-label">专业要求</span>
              <strong>{{ jobItem.raw_data.profiles.basic_requirements.major }}</strong>
            </div>
            <div class="overview-item">
              <el-icon><Timer /></el-icon>
              <span class="item-label">经验要求</span>
              <strong>{{ jobItem.raw_data.profiles.basic_requirements.experience_years }}</strong>
            </div>
            <div class="overview-item">
              <el-icon><Medal /></el-icon>
              <span class="item-label">证书要求</span>
              <strong>{{ jobItem.raw_data.profiles.basic_requirements.certificates }}</strong>
            </div>
            <div class="overview-item">
              <el-icon><Briefcase /></el-icon>
              <span class="item-label">所属行业</span>
              <strong>{{ jobItem.raw_data.profiles.job_attributes.industry }}</strong>
            </div>
            <div class="overview-item">
              <el-icon><Collection /></el-icon>
              <span class="item-label">行业趋势</span>
              <strong>{{ jobItem.raw_data.profiles.job_attributes.industry_trend }}</strong>
            </div>
          </div>
        </div>

        <div class="overview-side info-card">
          <h3 class="section-title">
            <el-icon><Aim /></el-icon>
            岗位属性
          </h3>
          <div class="attribute-list">
            <div class="attribute-item">
              <span>薪资竞争力</span>
              <el-tag size="small" :type="jobItem.raw_data.profiles.job_attributes.salary_competitiveness === '高' ? 'danger' : 'info'">
                {{ jobItem.raw_data.profiles.job_attributes.salary_competitiveness }}
              </el-tag>
            </div>
            <div class="attribute-item">
              <span>社会需求度</span>
              <el-tag size="small" :type="jobItem.raw_data.profiles.job_attributes.social_demand === '高' ? 'success' : 'info'">
                {{ jobItem.raw_data.profiles.job_attributes.social_demand }}
              </el-tag>
            </div>
            <div class="attribute-item attribute-item--text">
              <span><el-icon><Promotion /></el-icon>纵向晋升</span>
              <strong>{{ jobItem.raw_data.profiles.job_attributes.vertical_promotion_path }}</strong>
            </div>
            <div class="attribute-item attribute-item--text">
              <span><el-icon><Connection /></el-icon>横向发展</span>
              <strong>{{ jobItem.raw_data.profiles.job_attributes.lateral_transfer_directions }}</strong>
            </div>
            <div class="attribute-item attribute-item--text">
              <span><el-icon><Opportunity /></el-icon>前置角色</span>
              <strong>{{ jobItem.raw_data.profiles.job_attributes.prerequisite_roles }}</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="dimension-section info-card">
        <div class="module-head">
          <div>
            <div class="eyebrow">F-10 人岗匹配分析</div>
            <h3 class="module-title">四大维度匹配总览</h3>
            <p class="module-desc">将基础条件、技能结构、职业素养与成长潜力整理为更易阅读的分析视图。</p>
          </div>
        </div>

        <div class="dimension-grid">
          <div v-for="card in dimensionCards" :key="card.key" class="dimension-card">
            <div class="dimension-card__head">
              <div class="dimension-icon">
                <el-icon>
                  <component :is="card.icon" />
                </el-icon>
              </div>
              <div>
                <h4>{{ card.title }}</h4>
                <p>{{ card.desc }}</p>
              </div>
              <strong :style="{ color: getMatchScoreColor(card.value) }">{{ card.value }}</strong>
            </div>
            <div class="dimension-progress">
              <div class="dimension-progress__fill" :style="{ width: `${card.value}%`, background: getMatchScoreColor(card.value) }"></div>
            </div>
          </div>
        </div>
      </section>

      <section class="analysis-layout">
        <div class="charts-column">
          <div class="chart-card">
            <div class="chart-head">
              <div>
                <div class="eyebrow">图表分析区</div>
                <h3 class="section-title">
                  <el-icon><User /></el-icon>
                  职业素养评估
                </h3>
              </div>
            </div>
            <div id="literacy-radar" class="radar-chart"></div>
            <div class="radar-legend">
              <div v-for="(val, key) in jobItem.raw_data.profiles.professional_literacy" :key="key" class="legend-item">
                <span class="legend-dot" :style="{ background: val === '高' ? '#67C23A' : val === '中' ? '#E6A23C' : '#909399' }"></span>
                <span class="legend-name">{{ formatLiteracyKey(key as string) }}</span>
                <span class="legend-value" :class="val === '高' ? 'high' : val === '中' ? 'medium' : 'low'">{{ val }}</span>
              </div>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-head">
              <div>
                <div class="eyebrow">图表分析区</div>
                <h3 class="section-title">
                  <el-icon><Orange /></el-icon>
                  发展潜力评估
                </h3>
              </div>
            </div>
            <div id="potential-radar" class="radar-chart"></div>
            <div class="radar-legend">
              <div v-for="(val, key) in jobItem.raw_data.profiles.development_potential" :key="key" class="legend-item">
                <span class="legend-dot" :style="{ background: val === '高' ? '#67C23A' : val === '中' ? '#E6A23C' : '#909399' }"></span>
                <span class="legend-name">{{ formatLiteracyKey(key as string) }}</span>
                <span class="legend-value" :class="val === '高' ? 'high' : val === '中' ? 'medium' : 'low'">{{ val }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-column">
          <div class="detail-card">
            <div class="module-head">
              <div>
                <div class="eyebrow">F-09 岗位 AI 画像</div>
                <h3 class="module-title">
                  <el-icon><MagicStick /></el-icon>
                  专业技能要求
                </h3>
              </div>
            </div>

            <div class="skills-section">
              <div class="skill-block skill-block--primary">
                <div class="skill-label">核心技能</div>
                <div class="skill-tags">
                  <el-tag
                    v-for="skill in splitSkills(jobItem.raw_data.profiles.professional_skills.core_skills)"
                    :key="skill"
                    size="small"
                    effect="dark"
                    class="skill-tag-primary"
                  >
                    {{ skill }}
                  </el-tag>
                </div>
              </div>

              <div class="skill-grid">
                <div class="skill-block">
                  <div class="skill-label">工具能力</div>
                  <div class="skill-tags">
                    <el-tag
                      v-for="tool in splitSkills(jobItem.raw_data.profiles.professional_skills.tool_capabilities)"
                      :key="tool"
                      size="small"
                      type="warning"
                      effect="plain"
                    >
                      {{ tool }}
                    </el-tag>
                  </div>
                </div>

                <div class="skill-block">
                  <div class="skill-label">领域知识</div>
                  <div class="text-panel">{{ jobItem.raw_data.profiles.professional_skills.domain_knowledge }}</div>
                </div>

                <div class="skill-block">
                  <div class="skill-label">语言要求</div>
                  <div class="text-panel">{{ jobItem.raw_data.profiles.professional_skills.language_requirements }}</div>
                </div>

                <div class="skill-block">
                  <div class="skill-label">项目要求</div>
                  <div class="text-panel text-panel--desc">{{ jobItem.raw_data.profiles.professional_skills.project_requirements }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-card">
            <div class="module-head">
              <div>
                <div class="eyebrow">F-10 深度匹配分析</div>
                <h3 class="module-title">
                  <el-icon><DataAnalysis /></el-icon>
                  综合分析与关键短板
                </h3>
              </div>
            </div>

            <div class="highlight-analysis">
              <div class="highlight-analysis__label">
                <el-icon><InfoFilled /></el-icon>
                综合评语
              </div>
              <p>{{ jobItem.deep_analysis.all_analysis }}</p>
            </div>

            <div v-if="jobItem.deep_analysis.missing_key_skills.length > 0" class="warning-panel">
              <div class="warning-panel__head">
                <span>
                  <el-icon><Warning /></el-icon>
                  当前最需要补强的关键技能
                </span>
                <el-tag type="warning" effect="dark">{{ jobItem.deep_analysis.missing_key_skills.length }} 项</el-tag>
              </div>
              <div class="warning-tags">
                <el-tag v-for="(skill, i) in jobItem.deep_analysis.missing_key_skills" :key="i" type="warning" effect="plain" round>
                  {{ skill }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="detail-card">
        <div class="module-head">
          <div>
            <div class="eyebrow">F-11 差距分析报告</div>
            <h3 class="module-title">
              <el-icon><Histogram /></el-icon>
              差距矩阵与优先改进方向
            </h3>
            <p class="module-desc">保留原有差距矩阵数据结构，通过卡片式对比让岗位要求、当前水平和差距说明更易理解。</p>
          </div>
        </div>

        <div class="gap-cards-container">
          <div v-for="(gap, i) in jobItem.deep_analysis.gap_matrix" :key="i" class="gap-card">
            <div class="gap-card-header">
              <el-tag :type="['primary', 'success', 'warning', 'danger'][i % 4]" effect="light" round>
                {{ gap.dimension }}
              </el-tag>
              <el-tag size="small" :type="getGapLevel(gap.gap_analysis).type" effect="dark" round>
                {{ getGapLevel(gap.gap_analysis).label }}
              </el-tag>
            </div>

            <div class="compare-row">
              <div class="compare-item required">
                <div class="compare-title">岗位要求</div>
                <div class="compare-value">{{ gap.required }}</div>
              </div>
              <div class="compare-item current">
                <div class="compare-title">当前水平</div>
                <div class="compare-value">{{ gap.current }}</div>
              </div>
            </div>

            <div class="analysis-box" :style="{ '--gap-color': getGapLevel(gap.gap_analysis).color }">
              <div class="analysis-box__label">差距说明</div>
              <div class="analysis-box__value">{{ gap.gap_analysis }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="action-layout">
        <div class="action-card action-card--primary">
          <div class="module-head">
            <div>
              <div class="eyebrow">行动建议区</div>
              <h3 class="module-title">
                <el-icon><SuccessFilled /></el-icon>
                下一步该做什么
              </h3>
            </div>
          </div>

          <div class="action-steps">
            <div v-for="(item, index) in topActionItems" :key="`${item}-${index}`" class="action-step">
              <div class="step-index">{{ index + 1 }}</div>
              <div class="step-content">{{ item }}</div>
            </div>
          </div>

          <div class="action-summary">
            {{ jobItem.deep_analysis.actionable_advice }}
          </div>
        </div>

        <div class="action-card action-card--trust">
          <div class="module-head">
            <div>
              <div class="eyebrow">F-12 匹配可信度</div>
              <h3 class="module-title">
                <el-icon><InfoFilled /></el-icon>
                数据来源说明
              </h3>
            </div>
          </div>

          <div class="trust-list">
            <div class="trust-item">
              <span>分析依据</span>
              <p>岗位画像、岗位要求、技能标签、职业素养、发展潜力等多维信息综合判断。</p>
            </div>
            <div class="trust-item">
              <span>知识支撑</span>
              <p>岗位画像与分析结论由本地知识库及 AI 提取结果支撑，适合用于展示与决策参考。</p>
            </div>
            <div class="trust-item">
              <span>使用建议</span>
              <p>建议结合个人真实项目经验、证书情况和近期求职目标，进一步核验投递优先级。</p>
            </div>
          </div>
        </div>
      </section>
    </template>

    <div v-else class="empty-container">
      <el-icon class="empty-icon" :size="64">
        <Document />
      </el-icon>
      <h3>未找到岗位信息</h3>
      <p>请从岗位列表中选择要查看的岗位</p>
      <el-button type="primary" @click="goBack">返回岗位列表</el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.position-detail-container {
  padding: 22px 20px 36px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 60px);
  background:
    radial-gradient(circle at top left, rgba(64, 158, 255, 0.08), transparent 20%),
    linear-gradient(180deg, #f5f9ff 0%, #f2f7fd 52%, #f7fbff 100%);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;

  .detail-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
    color: #173a5d;
    font-size: 22px;
    font-weight: 700;
  }
}

.loading-container,
.empty-container,
.info-card,
.detail-card,
.chart-card,
.action-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(220, 231, 244, 0.96);
  border-radius: 24px;
  box-shadow: 0 20px 48px rgba(28, 74, 127, 0.08);
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 84px 24px;
  text-align: center;
  color: #7b8ca1;
}

.loading-container p,
.empty-container p {
  margin: 12px 0 0;
}

.loading-icon {
  color: #409eff;
  animation: rotate 1.5s linear infinite;
}

.empty-icon {
  color: #c8d4e3;
  margin-bottom: 16px;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(64, 158, 255, 0.1);
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.section-title,
.module-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0 0;
  color: #173a5d;
  font-size: 20px;
  font-weight: 700;
}

.module-desc {
  margin: 8px 0 0;
  color: #6c8198;
  line-height: 1.7;
  font-size: 14px;
}

.overview-section {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.82fr);
  gap: 20px;
  margin-bottom: 20px;
}

.info-card,
.detail-card,
.chart-card,
.action-card {
  padding: 24px;
}

.overview-main__head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding-bottom: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e9eff6;
}

.job-identity {
  display: flex;
  gap: 16px;
  min-width: 0;
}

.job-icon {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 16px 30px rgba(64, 158, 255, 0.24);
}

.job-name {
  margin: 12px 0;
  color: #173a5d;
  font-size: 30px;
  line-height: 1.2;
  font-weight: 800;
}

.job-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-icon {
  margin-right: 2px;
}

.score-panel {
  --score-color: #67C23A;
  flex-shrink: 0;
  width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-ring {
  width: 164px;
  height: 164px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-ring__inner {
  width: 124px;
  height: 124px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.score-ring__inner strong {
  font-size: 42px;
  line-height: 1;
  color: #173a5d;
}

.score-ring__inner span {
  margin-top: 6px;
  font-size: 13px;
  color: #6b8199;
}

.score-level {
  margin-top: 14px;
  font-size: 18px;
  font-weight: 700;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.overview-item {
  padding: 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f9fbff 0%, #f2f7fd 100%);
  border: 1px solid rgba(226, 234, 245, 0.92);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.overview-item .el-icon {
  font-size: 16px;
  color: #409eff;
}

.item-label {
  color: #7a8ea5;
  font-size: 12px;
}

.overview-item strong {
  color: #2d435b;
  font-size: 14px;
  line-height: 1.7;
}

.attribute-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 18px;
}

.attribute-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px dashed #e6edf7;
  color: #526b86;
}

.attribute-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.attribute-item--text {
  align-items: flex-start;
}

.attribute-item--text span,
.attribute-item--text strong {
  display: flex;
  align-items: center;
  gap: 6px;
}

.attribute-item strong {
  color: #173a5d;
  font-size: 14px;
  text-align: right;
}

.dimension-section {
  margin-bottom: 20px;
}

.module-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
}

.dimension-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.dimension-card {
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #f9fbff 0%, #f3f8ff 100%);
  border: 1px solid rgba(220, 231, 244, 0.96);
}

.dimension-card__head {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: flex-start;
}

.dimension-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(64, 158, 255, 0.12);
  color: #409eff;
}

.dimension-card__head h4 {
  margin: 0 0 6px;
  color: #173a5d;
  font-size: 16px;
}

.dimension-card__head p {
  margin: 0;
  color: #6f849a;
  font-size: 13px;
  line-height: 1.6;
}

.dimension-card__head strong {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
}

.dimension-progress {
  height: 10px;
  margin-top: 16px;
  border-radius: 999px;
  background: #e8f0fa;
  overflow: hidden;
}

.dimension-progress__fill {
  height: 100%;
  border-radius: inherit;
}

.analysis-layout {
  display: grid;
  grid-template-columns: 380px minmax(0, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.charts-column,
.detail-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-head {
  margin-bottom: 10px;
}

.radar-chart {
  width: 100%;
  height: 280px;
}

.radar-legend {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 12px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid #e9eff6;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  font-size: 12px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  color: #5f748c;
}

.legend-value {
  margin-left: auto;
  font-weight: 700;
}

.legend-value.high {
  color: #67C23A;
}

.legend-value.medium {
  color: #E6A23C;
}

.legend-value.low {
  color: #909399;
}

.skills-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.skill-block {
  padding: 16px;
  border-radius: 18px;
  background: #f8fbff;
  border: 1px solid rgba(223, 232, 243, 0.92);
}

.skill-block--primary {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.08), rgba(113, 182, 255, 0.12));
}

.skill-label {
  margin-bottom: 10px;
  color: #6e8399;
  font-size: 13px;
  font-weight: 700;
}

.skill-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag-primary {
  border: none !important;
  background: linear-gradient(135deg, #409eff, #66b1ff) !important;
}

.text-panel {
  padding: 12px 14px;
  border-radius: 14px;
  background: #fff;
  color: #506980;
  line-height: 1.7;
  font-size: 14px;
}

.text-panel--desc {
  min-height: 88px;
}

.highlight-analysis {
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #f7fbff 0%, #edf5ff 100%);
  border: 1px solid rgba(64, 158, 255, 0.14);
}

.highlight-analysis__label,
.warning-panel__head span {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2563eb;
  font-size: 14px;
  font-weight: 700;
}

.highlight-analysis p {
  margin: 12px 0 0;
  color: #4e6780;
  line-height: 1.9;
}

.warning-panel {
  margin-top: 18px;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #fff8ef 0%, #fffaf5 100%);
  border: 1px solid rgba(230, 162, 60, 0.18);
}

.warning-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.warning-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.gap-cards-container {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.gap-card {
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  border: 1px solid rgba(224, 233, 244, 0.96);
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.gap-card:hover {
  transform: translateY(-3px);
  border-color: rgba(64, 158, 255, 0.24);
  box-shadow: 0 20px 42px rgba(32, 91, 165, 0.08);
}

.gap-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.compare-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.compare-item {
  padding: 16px;
  border-radius: 16px;
  min-height: 120px;
}

.compare-item.required {
  background: #fff6ea;
  border: 1px solid rgba(230, 162, 60, 0.16);
}

.compare-item.current {
  background: #f0f9eb;
  border: 1px solid rgba(103, 194, 58, 0.16);
}

.compare-title {
  color: #7a8ca1;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 10px;
}

.compare-value {
  color: #304860;
  line-height: 1.8;
  font-size: 14px;
}

.analysis-box {
  --gap-color: #409eff;
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--gap-color) 8%, white);
  border-left: 4px solid var(--gap-color);
}

.analysis-box__label {
  color: var(--gap-color);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 8px;
}

.analysis-box__value {
  color: #47627d;
  line-height: 1.8;
  font-size: 14px;
}

.action-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
  gap: 20px;
}

.action-card--primary {
  background:
    radial-gradient(circle at top right, rgba(103, 194, 58, 0.08), transparent 26%),
    rgba(255, 255, 255, 0.96);
}

.action-card--trust {
  background:
    radial-gradient(circle at top right, rgba(64, 158, 255, 0.08), transparent 26%),
    rgba(255, 255, 255, 0.96);
}

.action-steps {
  display: grid;
  gap: 12px;
}

.action-step {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
  padding: 14px 16px;
  border-radius: 18px;
  background: #f7fbff;
  border: 1px solid rgba(222, 232, 243, 0.92);
}

.step-index {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, #67C23A, #95d475);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.step-content {
  color: #49647f;
  line-height: 1.8;
  font-size: 14px;
}

.action-summary {
  margin-top: 16px;
  padding: 16px 18px;
  border-radius: 18px;
  background: #f0f9eb;
  border-left: 4px solid #67C23A;
  color: #36546a;
  line-height: 1.85;
}

.trust-list {
  display: grid;
  gap: 14px;
}

.trust-item {
  padding: 16px;
  border-radius: 18px;
  background: #f7fbff;
  border: 1px solid rgba(223, 232, 243, 0.92);
}

.trust-item span {
  display: block;
  margin-bottom: 8px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
}

.trust-item p {
  margin: 0;
  color: #506980;
  line-height: 1.8;
  font-size: 14px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1400px) {
  .dimension-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1200px) {
  .overview-section,
  .analysis-layout,
  .action-layout {
    grid-template-columns: 1fr;
  }

  .score-panel {
    width: 180px;
  }
}

@media (max-width: 992px) {
  .overview-main__head,
  .module-head {
    flex-direction: column;
  }

  .overview-grid,
  .skill-grid,
  .gap-cards-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .position-detail-container {
    padding: 18px 14px 28px;
  }

  .info-card,
  .detail-card,
  .chart-card,
  .action-card {
    padding: 20px 18px;
    border-radius: 20px;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .job-name {
    font-size: 24px;
  }

  .score-panel {
    width: 100%;
    align-items: flex-start;
  }

  .score-ring {
    width: 140px;
    height: 140px;
  }

  .score-ring__inner {
    width: 106px;
    height: 106px;
  }

  .score-ring__inner strong {
    font-size: 34px;
  }

  .radar-legend,
  .compare-row,
  .dimension-grid {
    grid-template-columns: 1fr;
  }
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
