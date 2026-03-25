<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Money,
  Briefcase,
  TrendCharts,
  Star,
  InfoFilled,
  DataAnalysis,
  MagicStick,
  Document,
  ArrowRight,
  Trophy,
  CircleCheck,
  Refresh,
  ArrowLeft,
  CircleClose
} from '@element-plus/icons-vue'
import type { JobMatchItem } from '@/types/job-match'
import { mockJobMatchItems } from '@/mock/mockdata/JobMatch_mockdata'

// ==================== 状态定义 ====================

const router = useRouter()
/** 匹配结果数据（后端返回的岗位匹配数组） */
const matchItems = ref<JobMatchItem[]>([])
/** 加载状态 */
const loading = ref(false)

// ==================== 计算属性 ====================

/** 推荐岗位列表（按匹配度降序排列） */
const sortedJobs = computed<JobMatchItem[]>(() => {
  return [...matchItems.value].sort((a, b) => b.deep_analysis.score - a.deep_analysis.score)
})

/** 最高匹配分数 */
const topScore = computed(() => {
  if (sortedJobs.value.length === 0) return 0
  return sortedJobs.value[0]?.deep_analysis.score ?? 0
})

/** 建议投递的岗位数量 */
const canApplyCount = computed(() => {
  return matchItems.value.filter(item => item.deep_analysis.can_apply).length
})

/** 是否有数据 */
const hasData = computed(() => matchItems.value.length > 0)

// ==================== 方法 ====================

/** 加载匹配结果数据 */
const loadMatchResult = () => {
  loading.value = true
  try {
    const stored = localStorage.getItem('jobMatchResult')
    console.log('stored', stored)
    matchItems.value = stored ? JSON.parse(stored) as JobMatchItem[] : []

    //模拟数据
    // if (stored) {
    //   matchItems.value = JSON.parse(stored) as JobMatchItem[]

    //   if (matchItems.value.length === 0) {
    //     ElMessage.warning('推荐岗位数据不完整，已使用补充数据')
    //     matchItems.value = mockJobMatchItems
    //   }

    // } else {
    //   ElMessage.info('暂无评估数据，已加载示例数据')
    //   matchItems.value = mockJobMatchItems
    // }

  } catch (e) {
    console.error('加载匹配结果失败:', e)
    ElMessage.error('数据加载失败，已使用示例数据')
    matchItems.value = mockJobMatchItems
  } finally {
    loading.value = false
  }
}

/** 跳转到岗位详情页 */
const goToJobDetail = (jobId: string) => {
  router.push({
    path: '/job-position',
    query: { jobId }
  })
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

/** 将逗号分隔的字符串转为数组 */
const splitSkills = (str: string) => {
  return str ? str.split(/[,，、]/).map(s => s.trim()).filter(Boolean) : []
}

/** 返回重新评估 */
const goToAssessment = () => {
  router.push('/career-form')
}

/** 刷新数据 */
const refreshData = () => {
  loadMatchResult()
}

onMounted(() => {
  loadMatchResult()
})
</script>

<template>
  <div class="job-matching-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><TrendCharts /></el-icon>
        岗位推荐与人岗匹配分析
      </h1>
      <p class="page-subtitle">基于您的职业画像，AI智能推荐适合的岗位并分析匹配情况</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon" :size="48"><DataAnalysis /></el-icon>
      <p>正在加载匹配分析结果...</p>
    </div>

    <template v-else-if="hasData">
      <!-- 顶部：整体匹配概况 -->
      <div class="match-overview-section">
        <div class="overview-card score-card">
          <div class="score-circle" :class="topScore >= 80 ? 'excellent' : topScore >= 60 ? 'good' : 'fair'">
            <div class="score-value">{{ topScore }}</div>
            <div class="score-label">最高匹配分</div>
            <div class="score-level" :class="topScore >= 80 ? 'excellent' : topScore >= 60 ? 'good' : 'fair'">
              {{ getMatchScoreLevel(topScore) }}
            </div>
          </div>
          <div class="score-stats">
            <div class="stat-item">
              <span class="stat-num">{{ matchItems.length }}</span>
              <span class="stat-label">分析岗位</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num highlight">{{ canApplyCount }}</span>
              <span class="stat-label">建议投递</span>
            </div>
          </div>
        </div>

        <div class="overview-card summary-card">
          <h3 class="card-title">
            <el-icon><MagicStick /></el-icon>
            匹配概况
          </h3>
          <div class="summary-list">
            <div
              v-for="(item, index) in sortedJobs.slice(0, 5)"
              :key="item.job_id"
              class="summary-item"
            >
              <div class="summary-rank">{{ index + 1 }}</div>
              <div class="summary-info">
                <span class="summary-name">{{ item.raw_data.job_name }}</span>
                <span class="summary-score" :style="{ color: getMatchScoreColor(item.deep_analysis.score) }">
                  {{ item.deep_analysis.score }}分
                </span>
              </div>
              <el-tag
                size="small"
                :type="item.deep_analysis.can_apply ? 'success' : 'danger'"
                effect="plain"
              >
                {{ item.deep_analysis.can_apply ? '建议投递' : '不建议投递' }}
              </el-tag>
            </div>
          </div>
        </div>

        <div class="overview-card ai-card">
          <h3 class="card-title">
            <el-icon><InfoFilled /></el-icon>
            最佳匹配分析
          </h3>
          <p class="ai-text">{{ sortedJobs[0]?.deep_analysis.all_analysis || '暂无分析数据' }}</p>
          <div class="ai-meta">
            <span class="meta-advice">
              <el-icon color="#67C23A"><Check /></el-icon>
              核心建议：{{ sortedJobs[0]?.deep_analysis.actionable_advice?.slice(0, 60) }}...
            </span>
          </div>
        </div>
      </div>

      <!-- 岗位推荐列表 -->
      <div class="recommend-section">
        <div class="section-header">
          <h2 class="section-title">
            <el-icon><Star /></el-icon>
            为您推荐的岗位
            <el-tag size="small" type="primary" effect="plain" class="count-tag">
              共 {{ sortedJobs.length }} 个岗位
            </el-tag>
          </h2>
          <p class="section-desc">基于您的技能、经验和职业目标，AI为您精选了以下岗位</p>
        </div>

        <div class="job-recommend-list">
          <div
            v-for="(item, index) in sortedJobs"
            :key="item.job_id"
            class="job-recommend-card"
            
          >
            <!-- 岗位概要信息 -->
            <div class="job-summary" @click="goToJobDetail(item.job_id)">
              <div class="job-rank" :class="index < 3 ? 'top-rank' : ''">
                <span v-if="index < 3" class="rank-icon">{{ index + 1 }}</span>
                <span v-else class="rank-num">{{ index + 1 }}</span>
              </div>

              <div class="job-info">
                <div class="job-title-row">
                  <h3 class="job-title">{{ item.raw_data.job_name }}</h3>
                  <div class="job-title-tags">
                    <el-tag
                      size="small"
                      :color="getMatchScoreColor(item.deep_analysis.score)"
                      effect="dark"
                      class="match-tag"
                    >
                      {{ item.deep_analysis.score }}分 · {{ getMatchScoreLevel(item.deep_analysis.score) }}
                    </el-tag>
                    <el-tag
                      size="small"
                      :type="item.deep_analysis.can_apply ? 'success' : 'danger'"
                      effect="light"
                    >
                      <el-icon class="apply-icon">
                        <CircleCheck v-if="item.deep_analysis.can_apply" />
                        <CircleClose v-else />
                      </el-icon>
                      {{ item.deep_analysis.can_apply ? '建议投递' : '不建议' }}
                    </el-tag>
                  </div>
                </div>
                <div class="job-company-row">
                  <span class="industry-tag">
                    <el-icon><Briefcase /></el-icon>
                    {{ item.raw_data.profiles.job_attributes.industry }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Money /></el-icon>
                    {{ item.raw_data.profiles.job_attributes.salary_competitiveness }}竞争力
                  </span>
                  <span class="meta-item">
                    <el-icon><Trophy /></el-icon>
                    {{ item.raw_data.profiles.basic_requirements.degree }} · {{ item.raw_data.profiles.basic_requirements.experience_years }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Briefcase /></el-icon>
                    社会需求: {{ item.raw_data.profiles.job_attributes.social_demand }}
                  </span>
                </div>
                <div class="job-tags">
                  <el-tag
                    v-for="skill in splitSkills(item.raw_data.profiles.professional_skills.core_skills).slice(0, 6)"
                    :key="skill"
                    size="small"
                    effect="plain"
                    class="skill-tag"
                  >
                    {{ skill }}
                  </el-tag>
                </div>
              </div>

              <div class="job-action">
                <el-button type="primary" size="small" text>
                  查看详情
                  <el-icon class="detail-icon"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="bottom-actions">
        <el-button type="primary" size="large" @click="goToAssessment">
          <el-icon><ArrowLeft /></el-icon>
          重新评估
        </el-button>
        <el-button size="large" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </template>

    <!-- 无数据状态 -->
    <div v-else class="empty-container">
      <el-icon class="empty-icon"><Document /></el-icon>
      <h3>暂无匹配分析数据</h3>
      <p>请先完成职业评估，系统将为您生成个性化的岗位推荐</p>
      <el-button type="primary" size="large" @click="goToAssessment">
        前往职业评估
      </el-button>
    </div>
  </div>
</template>

<script lang="ts">
export default {}
</script>

<style scoped lang="scss">
.job-matching-container {
  padding: 20px;
  max-width: 1200px;
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

// 加载状态
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #909399;

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
    font-size: 64px;
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

// ========== 整体匹配概况 ==========
.match-overview-section {
  display: grid;
  grid-template-columns: 260px 1fr 1fr;
  gap: 20px;
  margin-bottom: 32px;

  @media (max-width: 1100px) {
    grid-template-columns: 1fr 1fr;
    .score-card {
      grid-column: 1 / -1;
    }
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.overview-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  padding: 24px;
}

.card-title {
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
}

// 总分卡片
.score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;

  .score-circle {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;

    &.excellent {
      background: linear-gradient(135deg, #67C23A15, #67C23A30);
      border: 4px solid #67C23A;
      .score-value { color: #67C23A; }
    }

    &.good {
      background: linear-gradient(135deg, #E6A23C15, #E6A23C30);
      border: 4px solid #E6A23C;
      .score-value { color: #E6A23C; }
    }

    &.fair {
      background: linear-gradient(135deg, #409EFF15, #409EFF30);
      border: 4px solid #409EFF;
      .score-value { color: #409EFF; }
    }

    &.poor {
      background: linear-gradient(135deg, #F56C6C15, #F56C6C30);
      border: 4px solid #F56C6C;
      .score-value { color: #F56C6C; }
    }

    .score-value {
      font-size: 44px;
      font-weight: 700;
      line-height: 1;
    }

    .score-label {
      font-size: 13px;
      color: #909399;
      margin-top: 4px;
    }

    .score-level {
      font-size: 12px;
      margin-top: 4px;
      padding: 2px 10px;
      border-radius: 10px;

      &.excellent { background: #67C23A20; color: #67C23A; }
      &.good { background: #E6A23C20; color: #E6A23C; }
      &.fair { background: #409EFF20; color: #409EFF; }
      &.poor { background: #F56C6C20; color: #F56C6C; }
    }
  }

  .score-stats {
    display: flex;
    align-items: center;
    gap: 16px;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;

      .stat-num {
        font-size: 22px;
        font-weight: 700;
        color: #303133;

        &.highlight {
          color: #67C23A;
        }
      }

      .stat-label {
        font-size: 12px;
        color: #909399;
      }
    }

    .stat-divider {
      width: 1px;
      height: 32px;
      background: #ebeef5;
    }
  }
}

// 匹配概况卡片
.summary-list {
  display: flex;
  flex-direction: column;
  gap: 10px;

  .summary-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    border-radius: 8px;
    background: #f5f7fa;
    transition: background-color 0.2s;

    &:hover {
      background-color: #ecf5ff;
    }

    .summary-rank {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #409EFF;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      flex-shrink: 0;
    }

    .summary-info {
      flex: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      min-width: 0;

      .summary-name {
        font-size: 14px;
        color: #303133;
        font-weight: 500;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .summary-score {
        font-size: 14px;
        font-weight: 600;
        flex-shrink: 0;
        margin-left: 8px;
      }
    }
  }
}

// AI建议卡片
.ai-card {
  .ai-text {
    margin: 0 0 16px;
    font-size: 14px;
    color: #606266;
    line-height: 1.8;
    padding: 16px;
    background: linear-gradient(135deg, #ecf5ff, #f5f7fa);
    border-left: 4px solid #409EFF;
    border-radius: 0 8px 8px 0;
  }

  .ai-meta {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .meta-advice {
      font-size: 13px;
      color: #909399;
      display: flex;
      align-items: flex-start;
      gap: 6px;
      line-height: 1.5;
    }
  }
}

// ========== 岗位推荐列表 ==========
.recommend-section {
  margin-bottom: 32px;
}

.section-header {
  margin-bottom: 20px;

  .section-title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    gap: 10px;

    .el-icon {
      color: #E6A23C;
      font-size: 24px;
    }

    .count-tag {
      margin-left: 4px;
    }
  }

  .section-desc {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.job-recommend-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.job-recommend-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  overflow: hidden;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  }

  &.expanded {
    box-shadow: 0 4px 24px rgba(64,158,255,0.12);
  }
}

.job-summary {
  display: flex;
  align-items: flex-start;
  padding: 20px 24px;
  cursor: pointer;
  gap: 16px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #fafbfc;
  }
}

.job-rank {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;

  .rank-icon {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #E6A23C, #f0c78a);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 700;
  }

  .rank-num {
    font-size: 18px;
    font-weight: 600;
    color: #c0c4cc;
  }
}

.job-info {
  flex: 1;
  min-width: 0;

  .job-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    gap: 12px;

    .job-title {
      font-size: 17px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }

    .job-title-tags {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;

      .match-tag {
        border: none;
        font-size: 12px;
      }

      .apply-icon {
        margin-right: 2px;
      }
    }
  }

  .job-company-row {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 8px;
    flex-wrap: wrap;

    .industry-tag {
      font-size: 13px;
      color: #606266;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .meta-item {
      font-size: 13px;
      color: #909399;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .job-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;

    .skill-tag {
      font-size: 12px;
    }
  }
}

.job-action {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding-top: 8px;

  .detail-icon {
    margin-left: 4px;
    transition: transform 0.2s;
  }

  &:hover .detail-icon {
    transform: translateX(2px);
  }
}

// 岗位详细面板
.detail-divider {
  height: 1px;
  background: #ebeef5;
  margin: 0 24px;
}

.job-detail-panel {
  padding: 0 24px 24px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.detail-section {
  margin-top: 20px;

  .detail-section-title {
    font-size: 15px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      color: #409EFF;
    }
  }
}

// 岗位画像
.profile-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.profile-item {
  background: #f5f7fa;
  padding: 14px;
  border-radius: 8px;

  .profile-label {
    font-size: 13px;
    color: #909399;
    margin-bottom: 8px;
    font-weight: 500;
  }

  .profile-content {
    .profile-row {
      display: flex;
      gap: 4px;
      font-size: 13px;
      line-height: 1.8;

      .profile-key {
        color: #909399;
        flex-shrink: 0;
      }

      .profile-val {
        color: #606266;
      }
    }

    .profile-tags-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
  }
}

.core-skill-tag {
  background: linear-gradient(135deg, #409EFF, #66b1ff) !important;
  border: none !important;
}

// 素养展示
.literacy-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  padding: 3px 0;

  .literacy-key {
    color: #606266;
  }

  .literacy-val {
    font-weight: 500;
  }
}

// 深度分析
.analysis-box {
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 14px;

  .analysis-label {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
  }

  p {
    margin: 0;
    font-size: 14px;
    color: #606266;
    line-height: 1.8;
  }
}

.all-analysis-box {
  background: linear-gradient(135deg, #ecf5ff, #f5f7fa);
  border-left: 4px solid #409EFF;
}

.missing-box {
  background: #fdf6ec;
  border-left: 4px solid #E6A23C;

  .missing-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .missing-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 13px;
    color: #606266;
    line-height: 1.5;
  }
}

.advice-box {
  background: #f0f9eb;
  border-left: 4px solid #67C23A;
}

// 差距矩阵
.gap-matrix-section {
  margin-bottom: 14px;

  .analysis-label {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    display: flex;
    align-items: center;
    gap: 6px;
  }
}

.gap-matrix-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.gap-matrix-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 14px;
  border: 1px solid #ebeef5;

  .gap-dimension {
    margin-bottom: 10px;

    .dim-badge {
      display: inline-block;
      font-size: 13px;
      font-weight: 600;
      color: #409EFF;
      padding: 2px 10px;
      background: #ecf5ff;
      border-radius: 4px;
    }
  }

  .gap-content {
    .gap-row {
      display: flex;
      gap: 8px;
      margin-bottom: 6px;
      font-size: 13px;
      line-height: 1.6;

      .gap-label {
        flex-shrink: 0;
        width: 72px;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        text-align: center;

        &.required-label {
          background: #fef0f0;
          color: #F56C6C;
        }

        &.current-label {
          background: #f0f9eb;
          color: #67C23A;
        }
      }

      .gap-text {
        color: #606266;

        &.required-text {
          color: #F56C6C;
        }

        &.current-text {
          color: #67C23A;
        }
      }
    }

    .gap-analysis {
      display: flex;
      align-items: flex-start;
      gap: 6px;
      margin-top: 8px;
      padding: 8px 12px;
      background: #f0f9eb;
      border-radius: 6px;
      font-size: 13px;
      color: #606266;
      line-height: 1.5;

      .el-icon {
        flex-shrink: 0;
        margin-top: 3px;
      }
    }
  }
}

// ========== 底部操作 ==========
.bottom-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 24px 0;
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
