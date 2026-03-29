<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
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
  Orange
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { JobMatchItem } from '@/types/job-match'

// ==================== Props ====================
const props = defineProps<{
  jobData?: JobMatchItem
}>()

// ==================== 状态定义 ====================
const route = useRoute()
const router = useRouter()
const jobItem = ref<JobMatchItem | null>(props.jobData || null)
const loading = ref(!props.jobData)

// 图表实例
let literacyChart: echarts.ECharts | null = null
let potentialChart: echarts.ECharts | null = null

// ==================== 计算属性 ====================

/** 从localStorage或路由参数获取数据 */
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

/** 将逗号分隔的字符串转为数组 */
const splitSkills = (str: string) => {
  return str ? str.split(/[,，、]/).map(s => s.trim()).filter(Boolean) : []
}

/** 文字等级转数值 */
const literacyToNum = (val: string): number => {
  if (val === '高') return 90
  if (val === '中') return 60
  if (val === '低') return 30
  return 50
}

/** 获取匹配度颜色 */
const getMatchScoreColor = (score: number) => {
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

/** 获取匹配度等级 */
const getMatchScoreLevel = (score: number) => {
  if (score >= 85) return '非常匹配'
  if (score >= 70) return '较为匹配'
  if (score >= 55) return '基本匹配'
  return '有待提升'
}

/** 素养雷达图配置 */
const getLiteracyOption = (literacy: any) => {
  const data = [
    literacyToNum(literacy.communication),
    literacyToNum(literacy.teamwork),
    literacyToNum(literacy.stress_management),
    literacyToNum(literacy.logic_thinking),
    literacyToNum(literacy.ethics)
  ]
  
  return {
    radar: {
      indicator: [
        { name: '沟通能力', max: 100 },
        { name: '团队协作', max: 100 },
        { name: '抗压能力', max: 100 },
        { name: '逻辑思维', max: 100 },
        { name: '职业道德', max: 100 }
      ],
      shape: 'polygon',
      center: ['50%', '50%'],
      radius: '65%',
      name: {
        textStyle: { color: '#606266', fontSize: 12, fontWeight: 500 }
      },
      splitArea: {
        areaStyle: { 
          color: ['rgba(64,158,255,0.05)', 'rgba(64,158,255,0.1)', 'rgba(64,158,255,0.15)', 'rgba(64,158,255,0.2)']
        }
      },
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      splitLine: { lineStyle: { color: '#e4e7ed' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: data,
        name: '职业素养',
        areaStyle: { color: 'rgba(64,158,255,0.3)' },
        lineStyle: { color: '#409EFF', width: 2 },
        itemStyle: { color: '#409EFF' },
        symbol: 'circle',
        symbolSize: 6
      }]
    }]
  }
}

/** 潜力雷达图配置 */
const getPotentialOption = (potential: any) => {
  const data = [
    literacyToNum(potential.learning_ability),
    literacyToNum(potential.innovation),
    literacyToNum(potential.leadership),
    literacyToNum(potential.career_orientation),
    literacyToNum(potential.adaptability)
  ]
  
  return {
    radar: {
      indicator: [
        { name: '学习能力', max: 100 },
        { name: '创新能力', max: 100 },
        { name: '领导力', max: 100 },
        { name: '职业取向', max: 100 },
        { name: '适应能力', max: 100 }
      ],
      shape: 'polygon',
      center: ['50%', '50%'],
      radius: '65%',
      name: {
        textStyle: { color: '#606266', fontSize: 12, fontWeight: 500 }
      },
      splitArea: {
        areaStyle: { 
          color: ['rgba(103,194,58,0.05)', 'rgba(103,194,58,0.1)', 'rgba(103,194,58,0.15)', 'rgba(103,194,58,0.2)']
        }
      },
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      splitLine: { lineStyle: { color: '#e4e7ed' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: data,
        name: '发展潜力',
        areaStyle: { color: 'rgba(103,194,58,0.3)' },
        lineStyle: { color: '#67C23A', width: 2 },
        itemStyle: { color: '#67C23A' },
        symbol: 'circle',
        symbolSize: 6
      }]
    }]
  }
}

/** 初始化雷达图 */
const initCharts = () => {
  if (!jobItem.value) return
  
  nextTick(() => {
    const item = jobItem.value
    if (!item) return
    
    const literacyEl = document.getElementById('literacy-radar')
    const potentialEl = document.getElementById('potential-radar')
    
    if (literacyEl) {
      literacyChart = echarts.init(literacyEl)
      literacyChart.setOption(getLiteracyOption(item.raw_data.profiles.professional_literacy))
    }
    
    if (potentialEl) {
      potentialChart = echarts.init(potentialEl)
      potentialChart.setOption(getPotentialOption(item.raw_data.profiles.development_potential))
    }
  })
}

/** 返回列表页 */
const goBack = () => {
  router.push('/job-matching')
}

/** 格式化素养key */
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

// ==================== 生命周期 ====================
onMounted(() => {
  loadJobData()
  if (jobItem.value) {
    initCharts()
  }
})

onBeforeUnmount(() => {
  literacyChart?.dispose()
  potentialChart?.dispose()
})
</script>

<template>
  <div class="position-detail-container">
    <!-- 顶部导航 -->
    <div class="detail-header">
      <el-button type="primary" text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回岗位列表
      </el-button>
      <h1 class="detail-title">
        <el-icon><TrendCharts /></el-icon>
        岗位详情分析
      </h1>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon" :size="48"><DataAnalysis /></el-icon>
      <p>正在加载岗位详情...</p>
    </div>

    <template v-else-if="jobItem">
      <!-- 顶部概览区 -->
      <div class="overview-section">
        <!-- 左侧：岗位基本信息卡片 -->
        <div class="info-card main-info">
          <div class="job-header">
            <div class="job-icon">
              <el-icon :size="32"><OfficeBuilding /></el-icon>
            </div>
            <div class="job-title-section">
              <h2 class="job-name">{{ jobItem.raw_data.job_name }}</h2>
              <div class="job-tags">
                <el-tag
                  size="small"
                  :color="getMatchScoreColor(Math.round((jobItem.score || 0) * 100))"
                  effect="dark"
                >
                  {{ Math.round((jobItem.score || 0) * 100) }}分匹配
                </el-tag>
                <el-tag
                  size="small"
                  :type="jobItem.deep_analysis.can_apply ? 'success' : 'danger'"
                  effect="light"
                >
                  <el-icon class="tag-icon">
                    <CircleCheck v-if="jobItem.deep_analysis.can_apply" />
                    <CircleClose v-else />
                  </el-icon>
                  {{ jobItem.deep_analysis.can_apply ? '推荐' : '不推荐' }}
                </el-tag>
              </div>
            </div>
          </div>
          
          <div class="basic-info-grid">
            <div class="info-item">
              <el-icon><School /></el-icon>
              <span class="info-label">学历要求</span>
              <span class="info-value">{{ jobItem.raw_data.profiles.basic_requirements.degree }}</span>
            </div>
            <div class="info-item">
              <el-icon><Document /></el-icon>
              <span class="info-label">专业要求</span>
              <span class="info-value">{{ jobItem.raw_data.profiles.basic_requirements.major }}</span>
            </div>
            <div class="info-item">
              <el-icon><Timer /></el-icon>
              <span class="info-label">经验要求</span>
              <span class="info-value">{{ jobItem.raw_data.profiles.basic_requirements.experience_years }}</span>
            </div>
            <div class="info-item">
              <el-icon><Medal /></el-icon>
              <span class="info-label">证书要求</span>
              <span class="info-value">{{ jobItem.raw_data.profiles.basic_requirements.certificates }}</span>
            </div>
            <div class="info-item">
              <el-icon><Briefcase /></el-icon>
              <span class="info-label">所属行业</span>
              <span class="info-value">{{ jobItem.raw_data.profiles.job_attributes.industry }}</span>
            </div>
            <div class="info-item">
            <el-icon><Collection /></el-icon>
            <span class="info-label">行业趋势</span>
              <span class="info-value">{{ jobItem.raw_data.profiles.job_attributes.industry_trend }}</span>
            </div>
          </div>
        </div>

        <!-- 中间：匹配分数大圆环 -->
        <div class="info-card score-ring-card">
          <div class="score-ring-container">
            <div 
              class="score-ring" 
              :style="{ 
                background: `conic-gradient(${getMatchScoreColor(Math.round((jobItem.score || 0) * 100))} ${Math.round((jobItem.score || 0) * 100) * 3.6}deg, #e4e7ed 0deg)`
              }"
            >
              <div class="score-inner">
                <span class="score-num">{{ Math.round((jobItem.score || 0) * 100) }}</span>
                <span class="score-unit">分</span>
              </div>
            </div>
          </div>
          <div class="score-labels">
            <div class="score-level" :style="{ color: getMatchScoreColor(Math.round((jobItem.score || 0) * 100)) }">
              {{ getMatchScoreLevel(Math.round((jobItem.score || 0) * 100)) }}
            </div>
            <div class="score-desc">综合匹配度</div>
          </div>
        </div>

        <!-- 右侧：岗位属性 -->
        <div class="info-card attributes-card">
          <h3 class="card-title">
            <el-icon><Aim /></el-icon>
            岗位属性
          </h3>
          <div class="attributes-list">
            <div class="attr-item">
              <span class="attr-label">薪资竞争力</span>
              <el-tag size="small" :type="jobItem.raw_data.profiles.job_attributes.salary_competitiveness === '高' ? 'danger' : 'info'">
                {{ jobItem.raw_data.profiles.job_attributes.salary_competitiveness }}
              </el-tag>
            </div>
            <div class="attr-item">
              <span class="attr-label">社会需求度</span>
              <el-tag size="small" :type="jobItem.raw_data.profiles.job_attributes.social_demand === '高' ? 'success' : 'info'">
                {{ jobItem.raw_data.profiles.job_attributes.social_demand }}
              </el-tag>
            </div>
            <div class="attr-item">
              <span class="attr-label">纵向晋升</span>
              <span class="attr-value">{{ jobItem.raw_data.profiles.job_attributes.vertical_promotion_path }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">横向发展</span>
              <span class="attr-value">{{ jobItem.raw_data.profiles.job_attributes.lateral_transfer_directions }}</span>
            </div>
            <div class="attr-item">
              <span class="attr-label">前置角色</span>
              <span class="attr-value">{{ jobItem.raw_data.profiles.job_attributes.prerequisite_roles }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间内容区：左右布局 -->
      <div class="content-section">
        <!-- 左侧：雷达图区域 -->
        <div class="left-panel">
          <!-- 职业素养雷达图 -->
          <div class="chart-card">
            <h3 class="chart-title">
              <el-icon><User /></el-icon>
              职业素养评估
            </h3>
            <div id="literacy-radar" class="radar-chart"></div>
            <div class="radar-legend">
              <div 
                v-for="(val, key) in jobItem.raw_data.profiles.professional_literacy" 
                :key="key"
                class="legend-item"
              >
                <span class="legend-dot" :style="{ background: val === '高' ? '#67C23A' : val === '中' ? '#E6A23C' : '#909399' }"></span>
                <span class="legend-name">{{ formatLiteracyKey(key as string) }}</span>
                <span class="legend-value" :class="val === '高' ? 'high' : val === '中' ? 'medium' : 'low'">{{ val }}</span>
              </div>
            </div>
          </div>

          <!-- 发展潜力雷达图 -->
          <div class="chart-card">
            <h3 class="chart-title">
            <el-icon><Orange /></el-icon>
            发展潜力评估
            </h3>
            <div id="potential-radar" class="radar-chart"></div>
            <div class="radar-legend">
              <div 
                v-for="(val, key) in jobItem.raw_data.profiles.development_potential" 
                :key="key"
                class="legend-item"
              >
                <span class="legend-dot" :style="{ background: val === '高' ? '#67C23A' : val === '中' ? '#E6A23C' : '#909399' }"></span>
                <span class="legend-name">{{ formatLiteracyKey(key as string) }}</span>
                <span class="legend-value" :class="val === '高' ? 'high' : val === '中' ? 'medium' : 'low'">{{ val }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：详细信息区域 -->
        <div class="right-panel">
          <!-- 专业技能 -->
          <div class="detail-card">
            <h3 class="card-title">
              <el-icon><MagicStick /></el-icon>
              专业技能要求
            </h3>
            <div class="skills-section">
              <div class="skill-block">
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
                <span class="skill-text">{{ jobItem.raw_data.profiles.professional_skills.domain_knowledge }}</span>
              </div>
              <div class="skill-block">
                <div class="skill-label">语言要求</div>
                <span class="skill-text">{{ jobItem.raw_data.profiles.professional_skills.language_requirements }}</span>
              </div>
              <div class="skill-block">
                <div class="skill-label">项目要求</div>
                <p class="skill-desc">{{ jobItem.raw_data.profiles.professional_skills.project_requirements }}</p>
              </div>
            </div>
          </div>

          <!-- 深度分析 -->
          <div class="detail-card">
            <h3 class="card-title">
              <el-icon><DataAnalysis /></el-icon>
              深度匹配分析
            </h3>
            
            <!-- 综合评语 -->
            <div class="analysis-section">
              <div class="section-label">
                <el-icon color="#409EFF"><InfoFilled /></el-icon>
                综合评语
              </div>
              <p class="analysis-text">{{ jobItem.deep_analysis.all_analysis }}</p>
            </div>

            <!-- 缺失技能 -->
            <div v-if="jobItem.deep_analysis.missing_key_skills.length > 0" class="analysis-section warning">
              <div class="section-label">
                <el-icon color="#E6A23C"><Warning /></el-icon>
                缺失的关键技能
              </div>
              <div class="missing-skills">
                <div
                  v-for="(skill, i) in jobItem.deep_analysis.missing_key_skills"
                  :key="i"
                  class="missing-item"
                >
                  <el-icon color="#E6A23C"><Warning /></el-icon>
                  <span>{{ skill }}</span>
                </div>
              </div>
            </div>

            <!-- 差距矩阵表格 -->
            <div class="analysis-section">
              <div class="section-label">
                <el-icon color="#409EFF"><DataAnalysis /></el-icon>
                差距矩阵
              </div>
              <div class="gap-table">
                <div class="gap-header">
                  <span class="gap-col dim">维度</span>
                  <span class="gap-col">岗位要求</span>
                  <span class="gap-col">当前水平</span>
                  <span class="gap-col analysis">差距分析</span>
                </div>
                <div
                  v-for="(gap, i) in jobItem.deep_analysis.gap_matrix"
                  :key="i"
                  class="gap-row"
                >
                  <span class="gap-col dim">
                    <el-tag size="small" type="primary" effect="plain">{{ gap.dimension }}</el-tag>
                  </span>
                  <span class="gap-col required">{{ gap.required }}</span>
                  <span class="gap-col current">{{ gap.current }}</span>
                  <span class="gap-col analysis">{{ gap.gap_analysis }}</span>
                </div>
              </div>
            </div>

            <!-- 可执行建议 -->
            <div class="analysis-section success">
              <div class="section-label">
                <el-icon color="#67C23A"><SuccessFilled /></el-icon>
                可执行建议
              </div>
              <p class="advice-text">{{ jobItem.deep_analysis.actionable_advice }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 无数据状态 -->
    <div v-else class="empty-container">
      <el-icon class="empty-icon" :size="64"><Document /></el-icon>
      <h3>未找到岗位信息</h3>
      <p>请从岗位列表中选择要查看的岗位</p>
      <el-button type="primary" @click="goBack">返回岗位列表</el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.position-detail-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

// 顶部导航
.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;

  .detail-title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      color: #409EFF;
    }
  }
}

// 加载状态
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #909399;
  background: #fff;
  border-radius: 12px;

  .loading-icon {
    color: #409EFF;
    animation: rotate 1.5s linear infinite;
    margin-bottom: 16px;
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 顶部概览区
.overview-section {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr 1fr;
    .main-info { grid-column: 1 / -1; }
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    .main-info { grid-column: 1; }
  }
}

.info-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  padding: 20px;
}

// 主信息卡片
.main-info {
  .job-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #ebeef5;

    .job-icon {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      background: linear-gradient(135deg, #409EFF, #66b1ff);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }

    .job-title-section {
      flex: 1;

      .job-name {
        font-size: 22px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 10px 0;
      }

      .job-tags {
        display: flex;
        gap: 8px;

        .tag-icon {
          margin-right: 2px;
        }
      }
    }
  }

  .basic-info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;

    @media (max-width: 600px) {
      grid-template-columns: repeat(2, 1fr);
    }

    .info-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 10px;
      background: #f5f7fa;
      border-radius: 8px;

      .el-icon {
        color: #409EFF;
        font-size: 16px;
      }

      .info-label {
        font-size: 12px;
        color: #909399;
      }

      .info-value {
        font-size: 14px;
        color: #303133;
        font-weight: 500;
      }
    }
  }
}

// 分数圆环卡片
.score-ring-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  .score-ring-container {
    position: relative;
    width: 140px;
    height: 140px;
    margin-bottom: 16px;

    .score-ring {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;

      .score-inner {
        width: 110px;
        height: 110px;
        background: #fff;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        .score-num {
          font-size: 36px;
          font-weight: 700;
          color: #303133;
          line-height: 1;
        }

        .score-unit {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .score-labels {
    text-align: center;

    .score-level {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 4px;
    }

    .score-desc {
      font-size: 13px;
      color: #909399;
    }
  }
}

// 属性卡片
.attributes-card {
  .card-title {
    font-size: 15px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      color: #409EFF;
    }
  }

  .attributes-list {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .attr-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px dashed #ebeef5;

      &:last-child {
        border-bottom: none;
      }

      .attr-label {
        font-size: 13px;
        color: #606266;
      }

      .attr-value {
        font-size: 13px;
        color: #303133;
        font-weight: 500;
        text-align: right;
        max-width: 60%;
      }
    }
  }
}

// 中间内容区
.content-section {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;

  @media (max-width: 1100px) {
    grid-template-columns: 1fr;
  }
}

// 左侧面板
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  padding: 20px;

  .chart-title {
    font-size: 15px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      color: #409EFF;
    }
  }

  .radar-chart {
    width: 100%;
    height: 260px;
  }

  .radar-legend {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #ebeef5;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;

      .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
      }

      .legend-name {
        color: #606266;
      }

      .legend-value {
        font-weight: 500;
        margin-left: auto;

        &.high { color: #67C23A; }
        &.medium { color: #E6A23C; }
        &.low { color: #909399; }
      }
    }
  }
}

// 右侧面板
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  padding: 20px;

  .card-title {
    font-size: 15px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;

    .el-icon {
      color: #409EFF;
    }
  }
}

// 技能区域
.skills-section {
  display: flex;
  flex-direction: column;
  gap: 16px;

  .skill-block {
    .skill-label {
      font-size: 13px;
      color: #909399;
      margin-bottom: 8px;
    }

    .skill-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .skill-tag-primary {
      background: linear-gradient(135deg, #409EFF, #66b1ff) !important;
      border: none !important;
    }

    .skill-text {
      font-size: 14px;
      color: #606266;
    }

    .skill-desc {
      margin: 0;
      font-size: 14px;
      color: #606266;
      line-height: 1.6;
      padding: 12px;
      background: #f5f7fa;
      border-radius: 8px;
    }
  }
}

// 分析区域
.analysis-section {
  margin-bottom: 20px;

  &:last-child {
    margin-bottom: 0;
  }

  &.warning {
    .analysis-text, .missing-skills {
      background: #fdf6ec;
      border-left: 3px solid #E6A23C;
    }
  }

  &.success {
    .advice-text {
      background: #f0f9eb;
      border-left: 3px solid #67C23A;
    }
  }

  .section-label {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
  }

  .analysis-text {
    margin: 0;
    font-size: 14px;
    color: #606266;
    line-height: 1.8;
    padding: 14px;
    background: #f5f7fa;
    border-radius: 0 8px 8px 0;
    border-left: 3px solid #409EFF;
  }

  .missing-skills {
    padding: 14px;
    background: #f5f7fa;
    border-radius: 0 8px 8px 0;

    .missing-item {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      font-size: 13px;
      color: #606266;
      line-height: 1.6;
      padding: 6px 0;

      .el-icon {
        flex-shrink: 0;
        margin-top: 2px;
      }
    }
  }

  .advice-text {
    margin: 0;
    font-size: 14px;
    color: #606266;
    line-height: 1.8;
    padding: 14px;
    background: #f5f7fa;
    border-radius: 0 8px 8px 0;
  }
}

// 差距矩阵表格
.gap-table {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;

  .gap-header {
    display: grid;
    grid-template-columns: 80px 1fr 1fr 1.5fr;
    gap: 12px;
    padding: 12px;
    background: #f5f7fa;
    font-size: 13px;
    font-weight: 600;
    color: #303133;
  }

  .gap-row {
    display: grid;
    grid-template-columns: 80px 1fr 1fr 1.5fr;
    gap: 12px;
    padding: 12px;
    border-top: 1px solid #ebeef5;
    font-size: 13px;
    line-height: 1.5;

    &:nth-child(even) {
      background: #fafbfc;
    }

    .gap-col {
      &.dim {
        display: flex;
        align-items: center;
      }

      &.required {
        color: #F56C6C;
      }

      &.current {
        color: #67C23A;
      }

      &.analysis {
        color: #606266;
      }
    }
  }

  @media (max-width: 900px) {
    .gap-header, .gap-row {
      grid-template-columns: 70px 1fr 1fr;
      .analysis { display: none; }
    }
  }
}

// 无数据状态
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);

  .empty-icon {
    color: #dcdfe6;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 18px;
    color: #606266;
    margin: 0 0 8px 0;
  }

  p {
    color: #909399;
    margin: 0 0 24px 0;
  }
}

// 滚动条样式
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
