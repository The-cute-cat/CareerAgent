<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search,
  Filter,
  Location,
  Money,
  Briefcase,
  OfficeBuilding,
  TrendCharts,
  Warning,
  Check,
  Star,
  InfoFilled,
  DataAnalysis,
  MagicStick,
  Document,
  ArrowRight,
  Tools,
  User
} from '@element-plus/icons-vue'
import CareerFormRadar from '@/components/CareerForm_Radar.vue'
import {
  mockJobs,
  mockMatchAnalysis,
  filterOptions,
  searchJobs,
  getMatchAnalysisByJobId,
  type JobPosition,
  type MatchAnalysis
} from '@/mock/mockdata/JobMatch_mockdata'

// ==================== 状态定义 ====================

/** 搜索关键词 */
const searchKeyword = ref('')
/** 筛选条件 */
const filters = reactive({
  industry: '',
  location: '',
  salaryRange: '',
  experience: ''
})
/** 岗位列表 */
const jobList = ref<JobPosition[]>(mockJobs)
/** 当前选中的岗位 */
const selectedJob = ref<JobPosition | null>(null)
/** 是否显示匹配分析 */
const showAnalysis = ref(false)
/** 匹配分析数据 */
const matchAnalysis = ref<MatchAnalysis>(mockMatchAnalysis)
/** 加载状态 */
const loading = ref(false)

// ==================== 计算属性 ====================

/** 行业选项 */
const industryOptions = filterOptions.industryOptions
/** 地点选项 */
const locationOptions = filterOptions.locationOptions
/** 薪资范围选项 */
const salaryOptions = filterOptions.salaryOptions
/** 经验选项 */
const experienceOptions = filterOptions.experienceOptions

/** 匹配总分样式 */
const scoreClass = computed(() => {
  const score = matchAnalysis.value.totalScore
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'fair'
  return 'poor'
})

/** 雷达图数据 */
const radarData = computed(() => ({
  indicator: matchAnalysis.value.dimensions.map(d => ({
    name: d.name,
    max: d.maxScore
  })),
  series: [{
    value: matchAnalysis.value.dimensions.map(d => d.score),
    name: '匹配度'
  }]
}))

// ==================== 方法 ====================

/** 搜索岗位 */
const handleSearch = () => {
  loading.value = true
  // 模拟API调用
  setTimeout(() => {
    jobList.value = searchJobs(searchKeyword.value, {
      industry: filters.industry,
      location: filters.location,
      salaryRange: filters.salaryRange,
      experience: filters.experience
    })
    loading.value = false
  }, 500)
}

/** 选择岗位 */
const handleSelectJob = (job: JobPosition) => {
  selectedJob.value = job
  showAnalysis.value = false
  // 模拟获取匹配分析
  loading.value = true
  setTimeout(() => {
    matchAnalysis.value = getMatchAnalysisByJobId(job.id)
    showAnalysis.value = true
    loading.value = false
  }, 800)
}

/** 获取差距等级样式 */
const getGapClass = (gap: string) => {
  const map: Record<string, string> = {
    high: 'gap-high',
    medium: 'gap-medium',
    low: 'gap-low'
  }
  return map[gap] || ''
}

/** 获取差距标签 */
const getGapLabel = (gap: string) => {
  const map: Record<string, string> = {
    high: '差距较大',
    medium: '需提升',
    low: '小幅提升'
  }
  return map[gap] || ''
}

/** 获取可信度颜色 */
const getConfidenceColor = (confidence: number) => {
  if (confidence >= 90) return '#67C23A'
  if (confidence >= 75) return '#E6A23C'
  return '#F56C6C'
}
</script>

<template>
  <div class="job-matching-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><TrendCharts /></el-icon>
        岗位探索与人岗匹配
      </h1>
      <p class="page-subtitle">基于AI智能分析，为您推荐最适合的岗位机会</p>
    </div>

    <div class="main-content">
      <!-- 左侧：岗位搜索列表 -->
      <div class="job-list-section">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索职位、公司..."
            class="search-input"
            size="large"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="handleSearch">搜索</el-button>
            </template>
          </el-input>

          <!-- 筛选条件 -->
          <div class="filter-row">
            <el-select v-model="filters.industry" placeholder="行业" clearable size="small">
              <el-option
                v-for="item in industryOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
            <el-select v-model="filters.location" placeholder="地点" clearable size="small">
              <el-option
                v-for="item in locationOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
            <el-select v-model="filters.salaryRange" placeholder="薪资范围" clearable size="small">
              <el-option
                v-for="item in salaryOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <el-select v-model="filters.experience" placeholder="经验要求" clearable size="small">
              <el-option
                v-for="item in experienceOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </div>
        </div>

        <!-- 岗位列表 -->
        <div class="job-list" v-loading="loading">
          <div
            v-for="job in jobList"
            :key="job.id"
            class="job-card"
            :class="{ active: selectedJob?.id === job.id }"
            @click="handleSelectJob(job)"
          >
            <div class="job-header">
              <h3 class="job-title">{{ job.title }}</h3>
              <div v-if="job.matchScore" class="match-badge">
                <el-icon><Star /></el-icon>
                {{ job.matchScore }}%匹配
              </div>
            </div>
            <div class="job-company">
              <el-icon><OfficeBuilding /></el-icon>
              {{ job.company }}
            </div>
            <div class="job-meta">
              <span class="meta-item">
                <el-icon><Location /></el-icon>
                {{ job.location }}
              </span>
              <span class="meta-item">
                <el-icon><Money /></el-icon>
                {{ job.salaryMin }}K-{{ job.salaryMax }}K
              </span>
              <span class="meta-item">
                <el-icon><Briefcase /></el-icon>
                {{ job.experience }}
              </span>
            </div>
            <div class="job-tags">
              <el-tag v-for="tag in job.tags.slice(0, 4)" :key="tag" size="small" effect="plain">
                {{ tag }}
              </el-tag>
            </div>
            <!-- 可信度标识 -->
            <div class="confidence-badge" v-if="job.confidence">
              <el-icon><InfoFilled /></el-icon>
              AI置信度: {{ job.confidence }}%
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：岗位详情与匹配分析 -->
      <div class="analysis-section">
        <div v-if="!selectedJob" class="empty-state">
          <el-icon class="empty-icon"><Document /></el-icon>
          <p>请选择左侧岗位查看详细匹配分析</p>
        </div>

        <template v-else>
          <!-- 岗位详情 -->
          <div class="job-detail-card">
            <div class="detail-header">
              <div>
                <h2 class="detail-title">{{ selectedJob.title }}</h2>
                <p class="detail-company">{{ selectedJob.company }} · {{ selectedJob.industry }}</p>
              </div>
              <el-button type="primary" size="large">
                申请岗位 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
              </el-button>
            </div>

            <div class="detail-meta">
              <span class="meta-item">
                <el-icon><Location /></el-icon>
                {{ selectedJob.location }}
              </span>
              <span class="meta-item">
                <el-icon><Money /></el-icon>
                {{ selectedJob.salaryMin }}K-{{ selectedJob.salaryMax }}K·13薪
              </span>
              <span class="meta-item">
                <el-icon><Briefcase /></el-icon>
                {{ selectedJob.experience }}
              </span>
              <span class="meta-item">
                <el-icon><el-icon-medal /></el-icon>
                {{ selectedJob.education }}
              </span>
            </div>

            <!-- AI岗位画像 -->
            <div class="ai-profile-section">
              <h3 class="section-title">
                <el-icon><MagicStick /></el-icon>
                AI岗位画像
                <el-tag size="small" type="success" effect="plain" class="confidence-tag">
                  置信度 {{ selectedJob.confidence }}%
                </el-tag>
              </h3>
              
              <div class="profile-grid">
                <div class="profile-item">
                  <div class="profile-label">核心技能要求</div>
                  <div class="profile-content">
                    <el-tag
                      v-for="skill in selectedJob.coreSkills"
                      :key="skill"
                      size="small"
                      effect="dark"
                      class="skill-tag"
                    >
                      {{ skill }}
                    </el-tag>
                  </div>
                </div>
                
                <div class="profile-item">
                  <div class="profile-label">必备证书</div>
                  <div class="profile-content">
                    <el-tag
                      v-for="cert in selectedJob.requiredCertificates"
                      :key="cert"
                      size="small"
                      type="warning"
                      effect="plain"
                    >
                      {{ cert }}
                    </el-tag>
                  </div>
                </div>
                
                <div class="profile-item">
                  <div class="profile-label">素养要求</div>
                  <div class="profile-content">
                    <el-tag
                      v-for="quality in selectedJob.requiredQualities"
                      :key="quality"
                      size="small"
                      type="info"
                      effect="plain"
                    >
                      {{ quality }}
                    </el-tag>
                  </div>
                </div>
              </div>

              <div class="job-description">
                <div class="profile-label">职位描述</div>
                <p>{{ selectedJob.description }}</p>
              </div>
            </div>
          </div>

          <!-- 人岗匹配分析 -->
          <div v-if="showAnalysis" class="match-analysis-card" v-loading="loading">
            <h3 class="section-title">
              <el-icon><DataAnalysis /></el-icon>
              人岗匹配分析
            </h3>

            <!-- 匹配总分 -->
            <div class="score-overview">
              <div class="score-circle" :class="scoreClass">
                <div class="score-value">{{ matchAnalysis.totalScore }}</div>
                <div class="score-label">匹配总分</div>
              </div>
              <div class="score-dimensions">
                <div
                  v-for="dim in matchAnalysis.dimensions"
                  :key="dim.name"
                  class="dimension-item"
                >
                  <div class="dimension-header">
                    <span class="dim-name">{{ dim.name }}</span>
                    <span class="dim-score">{{ dim.score }}分</span>
                  </div>
                  <el-progress
                    :percentage="dim.score"
                    :color="dim.score >= 80 ? '#67C23A' : dim.score >= 60 ? '#E6A23C' : '#F56C6C'"
                    :stroke-width="8"
                    :show-text="false"
                  />
                  <div class="dim-desc">{{ dim.description }} (权重{{ dim.weight }}%)</div>
                </div>
              </div>
            </div>

            <!-- AI解释 -->
            <div class="ai-explanation">
              <div class="explanation-header">
                <el-icon><InfoFilled /></el-icon>
                <span>AI分析结论</span>
                <el-tag size="small" :style="{ backgroundColor: getConfidenceColor(matchAnalysis.confidence) + '20', color: getConfidenceColor(matchAnalysis.confidence), borderColor: getConfidenceColor(matchAnalysis.confidence) }">
                  置信度 {{ matchAnalysis.confidence }}%
                </el-tag>
              </div>
              <p class="explanation-text">{{ matchAnalysis.aiExplanation }}</p>
            </div>

            <!-- 差距分析报告 -->
            <div class="gap-analysis">
              <h4 class="gap-title">
                <el-icon><Warning /></el-icon>
                能力差距分析与改进建议
              </h4>
              
              <div class="gap-list">
                <div
                  v-for="(gap, index) in matchAnalysis.gaps"
                  :key="index"
                  class="gap-item"
                  :class="getGapClass(gap.gap)"
                >
                  <div class="gap-header">
                    <div class="gap-type-icon">
                      <el-icon v-if="gap.type === 'skill'"><Tools /></el-icon>
                      <el-icon v-else-if="gap.type === 'certificate'"><Document /></el-icon>
                      <el-icon v-else-if="gap.type === 'quality'"><User /></el-icon>
                      <el-icon v-else><Briefcase /></el-icon>
                    </div>
                    <span class="gap-name">{{ gap.name }}</span>
                    <el-tag size="small" :type="gap.gap === 'high' ? 'danger' : gap.gap === 'medium' ? 'warning' : 'info'">
                      {{ getGapLabel(gap.gap) }}
                    </el-tag>
                  </div>
                  
                  <div class="gap-comparison">
                    <div class="comparison-item">
                      <span class="label">岗位要求：</span>
                      <span class="value required">{{ gap.required }}</span>
                    </div>
                    <div class="comparison-item">
                      <span class="label">当前水平：</span>
                      <span class="value current">{{ gap.current }}</span>
                    </div>
                  </div>
                  
                  <div class="suggestion-box">
                    <el-icon><Check /></el-icon>
                    <span class="suggestion-text">{{ gap.suggestion }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.job-matching-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 24px;
  
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    gap: 10px;
    
    .el-icon {
      color: #409EFF;
      font-size: 28px;
    }
  }
  
  .page-subtitle {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.main-content {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 20px;
}

// 左侧岗位列表
.job-list-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  overflow: hidden;
}

.search-bar {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  
  .search-input {
    margin-bottom: 12px;
  }
  
  .filter-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .el-select {
      width: calc(50% - 4px);
    }
  }
}

.job-list {
  max-height: calc(100vh - 280px);
  overflow-y: auto;
  padding: 12px;
}

.job-card {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    border-color: #409EFF;
    box-shadow: 0 2px 12px rgba(64,158,255,0.15);
  }
  
  &.active {
    border-color: #409EFF;
    background-color: #f0f9ff;
  }
  
  .job-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
    
    .job-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
    
    .match-badge {
      display: flex;
      align-items: center;
      gap: 4px;
      background: linear-gradient(135deg, #67C23A, #85ce61);
      color: #fff;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      white-space: nowrap;
    }
  }
  
  .job-company {
    font-size: 13px;
    color: #606266;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  
  .job-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 10px;
    
    .meta-item {
      font-size: 12px;
      color: #909399;
      display: flex;
      align-items: center;
      gap: 2px;
    }
  }
  
  .job-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 8px;
  }
  
  .confidence-badge {
    font-size: 11px;
    color: #909399;
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

// 右侧分析区域
.analysis-section {
  .empty-state {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    padding: 60px 20px;
    text-align: center;
    color: #909399;
    
    .empty-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }
  }
}

.job-detail-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  padding: 24px;
  margin-bottom: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  
  .detail-title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }
  
  .detail-company {
    font-size: 14px;
    color: #606266;
    margin: 0;
  }
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 16px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
  
  .meta-item {
    font-size: 14px;
    color: #606266;
    display: flex;
    align-items: center;
    gap: 6px;
  }
}

.ai-profile-section {
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;
    
    .el-icon {
      color: #409EFF;
    }
    
    .confidence-tag {
      margin-left: auto;
    }
  }
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.profile-item {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  
  .profile-label {
    font-size: 13px;
    color: #909399;
    margin-bottom: 10px;
  }
  
  .profile-content {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
}

.skill-tag {
  background: linear-gradient(135deg, #409EFF, #66b1ff) !important;
  border: none !important;
}

.job-description {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  
  .profile-label {
    font-size: 13px;
    color: #909399;
    margin-bottom: 8px;
  }
  
  p {
    margin: 0;
    font-size: 14px;
    color: #606266;
    line-height: 1.6;
  }
}

// 匹配分析卡片
.match-analysis-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  padding: 24px;
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 8px;
    
    .el-icon {
      color: #409EFF;
    }
  }
}

.score-overview {
  display: flex;
  gap: 40px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #ebeef5;
  
  @media (max-width: 1200px) {
    flex-direction: column;
    align-items: center;
  }
}

.score-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  &.excellent {
    background: linear-gradient(135deg, #67C23A20, #67C23A40);
    border: 4px solid #67C23A;
    
    .score-value {
      color: #67C23A;
    }
  }
  
  &.good {
    background: linear-gradient(135deg, #E6A23C20, #E6A23C40);
    border: 4px solid #E6A23C;
    
    .score-value {
      color: #E6A23C;
    }
  }
  
  &.fair {
    background: linear-gradient(135deg, #409EFF20, #409EFF40);
    border: 4px solid #409EFF;
    
    .score-value {
      color: #409EFF;
    }
  }
  
  &.poor {
    background: linear-gradient(135deg, #F56C6C20, #F56C6C40);
    border: 4px solid #F56C6C;
    
    .score-value {
      color: #F56C6C;
    }
  }
  
  .score-value {
    font-size: 36px;
    font-weight: 700;
  }
  
  .score-label {
    font-size: 13px;
    color: #909399;
    margin-top: 4px;
  }
}

.score-dimensions {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dimension-item {
  .dimension-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    
    .dim-name {
      font-size: 14px;
      color: #606266;
    }
    
    .dim-score {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  .dim-desc {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}

.ai-explanation {
  background: linear-gradient(135deg, #ecf5ff, #f5f7fa);
  border-left: 4px solid #409EFF;
  padding: 16px 20px;
  border-radius: 0 8px 8px 0;
  margin-bottom: 24px;
  
  .explanation-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #303133;
    
    .el-icon {
      color: #409EFF;
    }
  }
  
  .explanation-text {
    margin: 0;
    font-size: 14px;
    color: #606266;
    line-height: 1.6;
  }
}

// 差距分析
.gap-analysis {
  .gap-title {
    font-size: 15px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;
    
    .el-icon {
      color: #E6A23C;
    }
  }
}

.gap-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.gap-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
  
  &.gap-high {
    border-color: #F56C6C;
    background-color: #fef0f0;
  }
  
  &.gap-medium {
    border-color: #E6A23C;
    background-color: #fdf6ec;
  }
  
  &.gap-low {
    border-color: #909399;
    background-color: #f4f4f5;
  }
  
  .gap-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    
    .gap-type-icon {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: #409EFF20;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #409EFF;
    }
    
    .gap-name {
      flex: 1;
      font-size: 15px;
      font-weight: 500;
      color: #303133;
    }
  }
  
  .gap-comparison {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
    
    .comparison-item {
      .label {
        font-size: 12px;
        color: #909399;
      }
      
      .value {
        display: block;
        margin-top: 4px;
        font-size: 13px;
        
        &.required {
          color: #F56C6C;
          font-weight: 500;
        }
        
        &.current {
          color: #67C23A;
        }
      }
    }
  }
  
  .suggestion-box {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    background: #fff;
    padding: 12px;
    border-radius: 6px;
    
    .el-icon {
      color: #67C23A;
      margin-top: 2px;
    }
    
    .suggestion-text {
      font-size: 13px;
      color: #606266;
      line-height: 1.5;
    }
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
