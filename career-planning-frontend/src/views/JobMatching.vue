<template>
  <div class="job-matching-container">
    <div class="job-matching-shell">
      <section class="hero-panel">
        <div class="hero-copy">
          <div class="hero-kicker">
            <el-icon><MagicStick /></el-icon>
            AI 匹配引擎
          </div>
          <h1 class="page-title">
            <el-icon><TrendCharts /></el-icon>
            岗位探索与人岗匹配分析
          </h1>
          <p class="page-subtitle">
            围绕你的职业画像、技能结构与发展方向，系统会筛选更适合投递的岗位，并给出清晰的匹配理由、差距预警与行动建议。
          </p>
          <div class="hero-tags">
            <span class="hero-tag">F-09 岗位画像</span>
            <span class="hero-tag">F-10 人岗匹配</span>
            <span class="hero-tag">F-11 差距分析</span>
            <span class="hero-tag">F-12 匹配可信度</span>
          </div>
        </div>

        <div v-if="hasData" class="hero-score-panel">
          <div class="hero-score-caption">当前最佳匹配</div>
          <div class="hero-score-value">{{ topScore }}<span>分</span></div>
          <div class="hero-score-level">{{ getMatchScoreLevel(topScore) }}</div>
          <div class="hero-score-meta">
            <div class="hero-meta-item">
              <span class="hero-meta-label">最佳岗位</span>
              <strong>{{ topJob?.raw_data.job_name || '-' }}</strong>
            </div>
            <div class="hero-meta-item">
              <span class="hero-meta-label">推荐投递数</span>
              <strong>{{ canApplyCount }}</strong>
            </div>
          </div>
        </div>
      </section>

      <div v-if="loading" class="loading-container state-card">
        <el-icon class="loading-icon" :size="52"><DataAnalysis /></el-icon>
        <h3>正在生成岗位匹配视图</h3>
        <p>系统正在整理岗位推荐结果和人岗匹配分析，请稍候片刻。</p>
      </div>

      <template v-else-if="hasData">
        <section class="overview-section">
          <article class="summary-card summary-card--spotlight summary-card--best-match">
            <div class="summary-header">
              <div>
                <div class="section-eyebrow">当前最佳匹配岗位</div>
                <h2>{{ topJob?.raw_data.job_name || '暂无岗位' }}</h2>
                <p class="summary-copy">
                  {{ topJob?.deep_analysis.all_analysis || '暂无岗位分析摘要。' }}
                </p>
              </div>

              <div class="spotlight-score" :style="{ '--score-color': getMatchScoreColor(topScore) }">
                <span>{{ topScore }}</span>
                <small>匹配分</small>
              </div>
            </div>

            <div class="spotlight-meta">
              <span><el-icon><Briefcase /></el-icon>{{ topJob?.raw_data.profiles.job_attributes.industry || '待分析' }}</span>
              <span><el-icon><Money /></el-icon>{{ topJob?.raw_data.profiles.job_attributes.salary_competitiveness || '待分析' }}竞争力</span>
              <span><el-icon><Trophy /></el-icon>{{ topJob?.raw_data.profiles.basic_requirements.degree || '待分析' }}</span>
              <span><el-icon><Briefcase /></el-icon>{{ topJob?.raw_data.profiles.basic_requirements.experience_years || '待分析' }}</span>
            </div>

            <div class="spotlight-footer">
              <div class="insight-note">
                <el-icon><InfoFilled /></el-icon>
                <span>{{ topJob?.deep_analysis.actionable_advice || '继续完善技能与项目经历，可提升匹配准确性。' }}</span>
              </div>
              <el-button v-if="topJob" type="primary" @click="goToJobDetail(topJob.job_id)">
                查看最佳岗位详情
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </article>

          <article class="summary-card summary-card--overview">
            <div class="section-eyebrow">匹配结果概览</div>
            <div class="metrics-grid">
              <div class="metric-tile">
                <span class="metric-label">平均匹配度</span>
                <strong>{{ averageScore }}</strong>
                <small>{{ getMatchScoreLevel(averageScore) }}</small>
              </div>
              <div class="metric-tile accent">
                <span class="metric-label">建议投递比例</span>
                <strong>{{ recommendRatio }}%</strong>
                <small>{{ canApplyCount }}/{{ matchItems.length }} 个岗位推荐投递</small>
              </div>
              <div class="metric-tile">
                <span class="metric-label">分析岗位数</span>
                <strong>{{ matchItems.length }}</strong>
                <small>已纳入本次智能推荐</small>
              </div>
            </div>

            <div class="level-bar">
              <div
                class="level-bar__fill"
                :style="{
                  width: `${averageScore}%`,
                  background: getMatchScoreColor(averageScore)
                }"
              ></div>
            </div>

            <div class="trust-note">
              <el-icon><InfoFilled /></el-icon>
              <span>匹配结果基于职业画像、技能结构、岗位要求及本地知识库岗位画像综合分析。</span>
            </div>
          </article>

          <article class="summary-card summary-card--ranking">
            <div class="card-heading">
              <div class="section-eyebrow">优先关注</div>
              <h3>
                <el-icon><Star /></el-icon>
                推荐岗位序列
              </h3>
            </div>

            <div class="ranking-list">
              <button
                v-for="(item, index) in sortedJobs.slice(0, 5)"
                :key="item.job_id"
                class="ranking-item"
                type="button"
                @click="goToJobDetail(item.job_id)"
              >
                <span class="ranking-index" :class="{ 'is-top': index < 3 }">{{ index + 1 }}</span>
                <span class="ranking-name">{{ item.raw_data.job_name }}</span>
                <span class="ranking-score" :style="{ color: getMatchScoreColor(Math.round((item.score || 0) * 100)) }">
                  {{ Math.round((item.score || 0) * 100) }}分
                </span>
              </button>
            </div>
          </article>

          <article class="summary-card summary-card--digest">
            <div class="card-heading">
              <div class="section-eyebrow">投递摘要</div>
              <h3>
                <el-icon><DataAnalysis /></el-icon>
                匹配依据与差距提醒
              </h3>
            </div>

            <div class="digest-grid">
              <div class="digest-item">
                <span class="digest-label">当前建议</span>
                <strong>{{ topJob?.deep_analysis.can_apply ? '可优先投递' : '建议先补强再投递' }}</strong>
                <p>{{ topJob?.deep_analysis.actionable_advice || '继续完善技能与项目经历，可提升匹配准确性。' }}</p>
              </div>

              <div class="digest-item digest-item--warning">
                <span class="digest-label">关键差距</span>
                <strong>
                  <template v-if="topJob?.deep_analysis.missing_key_skills.length">
                    缺少 {{ topJob?.deep_analysis.missing_key_skills.length }} 项关键技能
                  </template>
                  <template v-else>
                    核心能力较完整
                  </template>
                </strong>
                <p>
                  {{
                    topJob?.deep_analysis.missing_key_skills.slice(0, 2).join('、') ||
                    '当前岗位要求与你的能力结构匹配度较高，可优先进入投递清单。'
                  }}
                </p>
              </div>
            </div>

            <div class="digest-highlight">
              <el-icon><InfoFilled /></el-icon>
              <span>建议优先查看前 3 个岗位详情，再结合缺失技能和行动建议决定投递顺序。</span>
            </div>
          </article>
        </section>

        <section class="recommend-section">
          <div class="section-header">
            <div>
              <div class="section-eyebrow">推荐岗位列表</div>
              <h2 class="section-title">为你精选的匹配岗位</h2>
              <p class="section-desc">
                聚焦岗位画像、匹配评分、差距预警和行动建议，帮助你更快判断投递优先级。
              </p>
            </div>
            <el-tag size="large" type="primary" effect="light" class="count-tag">共 {{ sortedJobs.length }} 个岗位</el-tag>
          </div>

          <div class="job-recommend-grid">
            <article
              v-for="(item, index) in sortedJobs"
              :key="item.job_id"
              class="job-recommend-card"
              :class="{ 'is-top-card': index < 3 }"
            >
              <div class="job-card-head">
                <div class="job-card-head__main">
                  <div class="job-card-rank" :class="{ 'top-rank': index < 3 }">{{ index + 1 }}</div>
                  <div>
                    <div class="job-title-row">
                      <h3 class="job-title">{{ item.raw_data.job_name }}</h3>
                      <div class="job-title-tags">
                        <el-tag
                          size="small"
                          :color="getMatchScoreColor(Math.round((item.score || 0) * 100))"
                          effect="dark"
                          class="match-tag"
                        >
                          {{ Math.round((item.score || 0) * 100) }}分
                        </el-tag>
                        <el-tag
                          size="small"
                          :type="item.deep_analysis.can_apply ? 'success' : 'warning'"
                          effect="light"
                        >
                          <el-icon class="apply-icon">
                            <CircleCheck v-if="item.deep_analysis.can_apply" />
                            <CircleClose v-else />
                          </el-icon>
                          {{ item.deep_analysis.can_apply ? '建议投递' : '建议补强' }}
                        </el-tag>
                      </div>
                    </div>

                    <div class="job-meta-grid">
                      <span class="meta-chip"><el-icon><Briefcase /></el-icon>{{ item.raw_data.profiles.job_attributes.industry }}</span>
                      <span class="meta-chip"><el-icon><Trophy /></el-icon>{{ item.raw_data.profiles.basic_requirements.degree }}</span>
                      <span class="meta-chip"><el-icon><Briefcase /></el-icon>{{ item.raw_data.profiles.basic_requirements.experience_years }}</span>
                      <span class="meta-chip"><el-icon><Money /></el-icon>{{ item.raw_data.profiles.job_attributes.salary_competitiveness }}竞争力</span>
                    </div>
                  </div>
                </div>

                <el-tooltip
                  placement="top"
                  effect="dark"
                  content="AI分析依据：基于职业画像、技能结构、岗位要求及本地知识库岗位画像综合分析"
                >
                  <div class="trust-badge">
                    <el-icon><InfoFilled /></el-icon>
                    <span>匹配可信度</span>
                  </div>
                </el-tooltip>
              </div>

              <div class="job-score-track">
                <div
                  class="job-score-fill"
                  :style="{
                    width: `${Math.round((item.score || 0) * 100)}%`,
                    background: getMatchScoreColor(Math.round((item.score || 0) * 100))
                  }"
                ></div>
              </div>

              <div class="job-analysis-block">
                <span class="block-label">岗位摘要分析</span>
                <p class="job-analysis">{{ item.deep_analysis.all_analysis || '暂无岗位分析摘要。' }}</p>
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

              <div class="warning-strip" :class="{ warning: !item.deep_analysis.can_apply }">
                <el-icon><InfoFilled /></el-icon>
                <span>
                  <template v-if="item.deep_analysis.missing_key_skills.length">
                    缺少 {{ item.deep_analysis.missing_key_skills.length }} 项关键技能，{{ item.deep_analysis.can_apply ? '建议边投递边补强' : '建议先补强后投递' }}
                  </template>
                  <template v-else>
                    核心能力结构较完整，可优先进入投递观察清单
                  </template>
                </span>
              </div>

              <div class="job-footer">
                <div class="job-advice">
                  <span class="advice-label">行动建议</span>
                  <span>{{ item.deep_analysis.actionable_advice || '先补齐核心能力，再进一步查看岗位详情。' }}</span>
                </div>
                <el-button type="primary" plain @click="goToJobDetail(item.job_id)">
                  查看详情
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </article>
          </div>
        </section>

        <div class="bottom-actions">
          <el-button type="primary" size="large" @click="goToAssessment">
            <el-icon><ArrowLeft /></el-icon>
            返回重新评估
          </el-button>
          <el-button size="large" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新匹配结果
          </el-button>
        </div>
      </template>

      <div v-else class="empty-container state-card">
        <el-icon class="empty-icon" :size="64"><Document /></el-icon>
        <h3>暂无匹配分析数据</h3>
        <p>先完成职业画像评估，系统才会基于你的背景、技能与发展方向生成个性化岗位推荐。</p>
        <el-button type="primary" size="large" @click="goToAssessment">
          前往职业评估
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
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
  CircleClose,
} from '@element-plus/icons-vue'
import type { JobMatchItem } from '@/types/job-match'
import { mockJobMatchItems } from '@/mock/mockdata/JobMatch_mockdata'
import { mockLearningJobMatchItems } from '@/mock/mockdata/LearningMode_mockdata'
import { usePoints } from '@/composables/usePoints'
import { useCareerModeStore } from '@/stores/careerMode'

const router = useRouter()
const matchItems = ref<JobMatchItem[]>([])
const loading = ref(false)

// 积分系统
const { consumePoints, showConsumeConfirmDialog } = usePoints()

// 职业模式
const careerModeStore = useCareerModeStore()
const isLearningMode = computed(() => careerModeStore.isLearningMode)

// 加载匹配结果（带积分检查）
const loadMatchResultWithPoints = async () => {
  // 先检查/扣除积分
  const result = await consumePoints('jobMatching', '岗位推荐分析')
  if (!result.success) {
    // 积分不足，已弹出提示
    return
  }
  // 积分扣除成功，加载数据
  loadMatchResult()
}

const sortedJobs = computed<JobMatchItem[]>(() => {
  return [...matchItems.value].sort((a, b) => (b.score || 0) * 100 - (a.score || 0) * 100)
})

const topScore = computed(() => {
  if (sortedJobs.value.length === 0) return 0
  return Math.round((sortedJobs.value[0]?.score || 0) * 100)
})

const canApplyCount = computed(() => {
  return matchItems.value.filter(item => item.deep_analysis.can_apply).length
})

const hasData = computed(() => matchItems.value.length > 0)
const topJob = computed(() => sortedJobs.value[0] ?? null)
const averageScore = computed(() => {
  if (!matchItems.value.length) return 0
  const total = matchItems.value.reduce((sum, item) => sum + Math.round((item.score || 0) * 100), 0)
  return Math.round(total / matchItems.value.length)
})
const recommendRatio = computed(() => {
  if (!matchItems.value.length) return 0
  return Math.round((canApplyCount.value / matchItems.value.length) * 100)
})

const loadMatchResult = () => {
  loading.value = true
  try {
    const stored = localStorage.getItem('jobMatchResult')
    if (stored) {
      matchItems.value = JSON.parse(stored) as JobMatchItem[]
    } else {
      // 没有存储数据时，根据模式使用对应的模拟数据
      matchItems.value = isLearningMode.value ? mockLearningJobMatchItems : mockJobMatchItems
    }
  } catch (e) {
    console.error('加载匹配结果失败:', e)
    ElMessage.error('数据加载失败，已使用示例数据')
    matchItems.value = isLearningMode.value ? mockLearningJobMatchItems : mockJobMatchItems
  } finally {
    loading.value = false
  }
}

const goToJobDetail = (jobId: string) => {
  router.push({
    path: '/job-position',
    query: { jobId }
  })
}

const getMatchScoreColor = (score: number) => {
  if (score >= 80) return '#16a34a'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

const getMatchScoreLevel = (score: number) => {
  if (score >= 85) return '非常匹配'
  if (score >= 70) return '较为匹配'
  if (score >= 55) return '基本匹配'
  return '有待提升'
}

const splitSkills = (str: string | any[] | null | undefined): string[] => {
  if (!str) return []
  if (Array.isArray(str)) return str.map((s) => String(s).trim()).filter(Boolean)
  if (typeof str === 'string') return str.split(/[,，、]/).map((s) => s.trim()).filter(Boolean)
  return []
}

const goToAssessment = () => {
  router.push('/career-form')
}

const refreshData = () => {
  loadMatchResult()
}

onMounted(() => {
  // 初始化职业模式
  careerModeStore.initMode()
  // 页面加载时只加载已有数据，不消耗积分
  loadMatchResult()
})
</script>

<style scoped lang="scss">
.job-matching-container {
  min-height: calc(100vh - 60px);
  padding: 24px 20px 42px;
  background:
    radial-gradient(circle at top left, rgba(90, 149, 255, 0.16), transparent 22%),
    radial-gradient(circle at top right, rgba(255, 193, 92, 0.16), transparent 18%),
    linear-gradient(180deg, #f4f8ff 0%, #edf5ff 52%, #f7fbff 100%);
}

.job-matching-shell {
  max-width: 1280px;
  margin: 0 auto;
  position: relative;
}

.hero-panel,
.summary-card,
.recommend-section,
.state-card,
.bottom-actions {
  position: relative;
  z-index: 1;
}

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.72fr);
  gap: 22px;
  padding: 28px 30px;
  margin-bottom: 22px;
  border-radius: 28px;
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.24), transparent 26%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(245, 250, 255, 0.93));
  border: 1px solid rgba(211, 226, 246, 0.92);
  box-shadow:
    0 22px 56px rgba(31, 78, 145, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.86);
}

.hero-kicker,
.section-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 30px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.page-title {
  margin: 16px 0 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: clamp(28px, 4vw, 38px);
  line-height: 1.12;
  font-weight: 800;
  color: #173a5d;
}

.page-subtitle {
  max-width: 760px;
  margin: 0;
  color: #5f738b;
  font-size: 15px;
  line-height: 1.85;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(214, 228, 246, 0.96);
  color: #6a8199;
  font-size: 13px;
  font-weight: 600;
}

.hero-score-panel {
  align-self: stretch;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 22px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(18, 72, 142, 0.96), rgba(29, 97, 181, 0.92));
  color: #fff;
  box-shadow: 0 22px 48px rgba(29, 97, 181, 0.24);
}

.hero-score-caption {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.72);
}

.hero-score-value {
  margin-top: 10px;
  font-size: 58px;
  font-weight: 800;
  line-height: 1;
}

.hero-score-value span {
  margin-left: 4px;
  font-size: 22px;
  font-weight: 600;
}

.hero-score-level {
  margin-top: 10px;
  font-size: 18px;
  font-weight: 700;
}

.hero-score-meta {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.hero-meta-item {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.12);
}

.hero-meta-label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.68);
}

.hero-meta-item strong {
  font-size: 20px;
  line-height: 1.5;
}

.state-card {
  padding: 64px 28px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(219, 231, 245, 0.96);
  box-shadow: 0 22px 52px rgba(32, 78, 137, 0.08);
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.loading-container h3,
.empty-container h3 {
  margin: 18px 0 8px;
  color: #173a5d;
  font-size: 26px;
  font-weight: 800;
}

.loading-container p,
.empty-container p {
  max-width: 520px;
  margin: 0 0 24px;
  color: #6c8198;
  font-size: 15px;
  line-height: 1.8;
}

.loading-icon,
.empty-icon {
  color: #409eff;
  margin-bottom: 12px;
}

.loading-icon {
  animation: rotate 1.5s linear infinite;
}

.overview-section {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 22px;
  margin-bottom: 24px;
  align-items: start;
}

.summary-card {
  padding: 24px;
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(220, 231, 244, 0.96);
  box-shadow: 0 20px 48px rgba(27, 74, 130, 0.08);
}

.summary-card--spotlight {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.14), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(246, 250, 255, 0.96));
}

.summary-card--best-match {
  grid-column: span 7;
}

.summary-card--overview {
  grid-column: span 5;
}

.summary-card--ranking {
  grid-column: span 7;
}

.summary-card--digest {
  grid-column: span 5;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
}

.summary-header h2 {
  margin: 14px 0 10px;
  color: #173a5d;
  font-size: 30px;
  font-weight: 800;
  line-height: 1.2;
}

.summary-header p {
  margin: 0;
  color: #49647f;
  line-height: 1.85;
}

.summary-copy {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.spotlight-score {
  --score-color: #16a34a;
  flex-shrink: 0;
  width: 124px;
  height: 124px;
  border-radius: 26px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--score-color) 14%, white);
  border: 1px solid color-mix(in srgb, var(--score-color) 30%, white);
  color: var(--score-color);
}

.spotlight-score span {
  font-size: 42px;
  font-weight: 800;
  line-height: 1;
}

.spotlight-score small {
  margin-top: 6px;
  font-size: 13px;
  font-weight: 700;
}

.spotlight-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 16px 0 14px;
}

.spotlight-meta span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 32px;
  padding: 0 11px;
  border-radius: 999px;
  background: rgba(237, 245, 255, 0.96);
  color: #55718f;
  font-size: 12px;
  font-weight: 600;
}

.spotlight-footer {
  margin-top: 12px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.insight-note,
.trust-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(240, 247, 255, 0.95);
  color: #5f738b;
  font-size: 13px;
  line-height: 1.65;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 16px;
}

.metric-tile {
  min-height: 128px;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #f8fbff 0%, #eff6ff 100%);
  border: 1px solid rgba(219, 231, 245, 0.96);
}

.metric-tile.accent {
  background: linear-gradient(135deg, rgba(48, 123, 255, 0.12), rgba(88, 176, 255, 0.18));
}

.metric-label {
  display: block;
  color: #7b91a7;
  font-size: 13px;
  font-weight: 600;
}

.metric-tile strong {
  display: block;
  margin: 12px 0 6px;
  color: #173a5d;
  font-size: 34px;
  font-weight: 800;
}

.metric-tile small {
  color: #6d8298;
  font-size: 13px;
  line-height: 1.6;
}

.level-bar {
  height: 12px;
  margin: 16px 0 14px;
  border-radius: 999px;
  background: #e8f0fa;
  overflow: hidden;
}

.level-bar__fill {
  height: 100%;
  border-radius: inherit;
}

.card-heading h3 {
  margin: 14px 0 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #173a5d;
  font-size: 22px;
  font-weight: 800;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 16px;
}

.ranking-item {
  width: 100%;
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid rgba(224, 234, 246, 0.94);
  border-radius: 18px;
  background: #f9fbff;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.ranking-item:hover {
  transform: translateY(-1px);
  border-color: rgba(93, 157, 255, 0.42);
  box-shadow: 0 12px 30px rgba(32, 92, 170, 0.08);
}

.ranking-index {
  width: 38px;
  height: 38px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #edf4fd;
  color: #54708d;
  font-size: 14px;
  font-weight: 800;
}

.ranking-index.is-top {
  background: linear-gradient(135deg, #f0aa2a, #f7c870);
  color: #fff;
}

.ranking-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #224566;
  font-size: 14px;
  font-weight: 700;
}

.ranking-score {
  font-size: 14px;
  font-weight: 800;
}

.digest-grid {
  display: grid;
  gap: 14px;
  margin-top: 16px;
}

.digest-item {
  padding: 16px;
  border-radius: 20px;
  background: linear-gradient(180deg, #f8fbff 0%, #f2f7ff 100%);
  border: 1px solid rgba(220, 231, 244, 0.96);
}

.digest-item--warning {
  background: linear-gradient(180deg, rgba(255, 247, 237, 0.92), rgba(255, 251, 245, 0.96));
  border-color: rgba(245, 158, 11, 0.18);
}

.digest-label {
  display: block;
  margin-bottom: 8px;
  color: #74879d;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.digest-item strong {
  display: block;
  color: #173a5d;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.4;
}

.digest-item p {
  margin: 8px 0 0;
  color: #5d748d;
  font-size: 13px;
  line-height: 1.7;
}

.digest-highlight {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(239, 246, 255, 0.96);
  color: #4f6d8d;
  font-size: 13px;
  line-height: 1.7;
}

.recommend-section {
  margin-bottom: 24px;
  padding: 26px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.93);
  border: 1px solid rgba(220, 232, 244, 0.96);
  box-shadow: 0 24px 60px rgba(28, 74, 127, 0.08);
}

.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 22px;
}

.section-title {
  margin: 12px 0 8px;
  color: #173a5d;
  font-size: 28px;
  font-weight: 800;
}

.section-desc {
  margin: 0;
  color: #6c8198;
  font-size: 15px;
  line-height: 1.8;
}

.count-tag {
  border-radius: 999px;
  padding-inline: 16px;
}

.job-recommend-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.job-recommend-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 22px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 251, 255, 0.98));
  border: 1px solid rgba(219, 232, 246, 0.96);
  box-shadow: 0 18px 40px rgba(27, 75, 132, 0.06);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.job-recommend-card:hover {
  transform: translateY(-3px);
  border-color: rgba(80, 147, 255, 0.42);
  box-shadow: 0 24px 52px rgba(27, 78, 138, 0.12);
}

.job-recommend-card.is-top-card {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.1), transparent 26%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 250, 255, 0.98));
}

.job-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.job-card-head__main {
  display: flex;
  gap: 14px;
  min-width: 0;
  flex: 1;
}

.job-card-rank {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: #edf4fd;
  color: #54708d;
  font-size: 16px;
  font-weight: 800;
}

.job-card-rank.top-rank {
  background: linear-gradient(135deg, #f0aa2a, #f7c870);
  color: #fff;
  box-shadow: 0 12px 28px rgba(240, 170, 42, 0.26);
}

.job-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.job-title {
  margin: 0;
  color: #173a5d;
  font-size: 21px;
  font-weight: 800;
  line-height: 1.25;
}

.job-title-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.match-tag {
  border: none;
  font-weight: 700;
}

.apply-icon {
  margin-right: 2px;
}

.trust-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(239, 246, 255, 0.96);
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid rgba(96, 165, 250, 0.24);
}

.job-meta-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: #f2f7fd;
  color: #627b95;
  font-size: 13px;
  font-weight: 600;
}

.job-score-track {
  height: 10px;
  border-radius: 999px;
  background: #e8f0fa;
  overflow: hidden;
}

.job-score-fill {
  height: 100%;
  border-radius: inherit;
}

.job-analysis-block {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.block-label,
.advice-label {
  display: block;
  margin-bottom: 8px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.job-analysis {
  margin: 0;
  color: #516b85;
  font-size: 14px;
  line-height: 1.8;
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  border-radius: 999px;
  color: #2f6fb0;
  border-color: rgba(127, 177, 231, 0.48);
  background: rgba(240, 247, 255, 0.82);
}

.warning-strip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 13px 14px;
  border-radius: 16px;
  background: rgba(240, 249, 235, 0.9);
  color: #166534;
  border: 1px solid rgba(34, 197, 94, 0.18);
  font-size: 13px;
  line-height: 1.7;
}

.warning-strip.warning {
  background: rgba(255, 247, 237, 0.96);
  color: #9a3412;
  border-color: rgba(245, 158, 11, 0.22);
}

.job-footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
}

.job-advice {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #5f738b;
  font-size: 13px;
  line-height: 1.7;
}

.bottom-actions {
  display: flex;
  justify-content: center;
  gap: 14px;
  padding-top: 4px;
}

.bottom-actions .el-button {
  min-width: 164px;
  border-radius: 16px;
  box-shadow: 0 14px 32px rgba(32, 80, 138, 0.08);
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1180px) {
  .hero-panel,
  .job-recommend-grid {
    grid-template-columns: 1fr;
  }

  .overview-section {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-card--best-match,
  .summary-card--overview,
  .summary-card--ranking,
  .summary-card--digest {
    grid-column: span 1;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .job-matching-container {
    padding: 18px 14px 32px;
  }

  .hero-panel,
  .summary-card,
  .recommend-section,
  .state-card {
    padding: 22px 18px;
    border-radius: 24px;
  }

  .page-title {
    font-size: 28px;
  }

  .overview-section {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .summary-header,
  .spotlight-footer,
  .section-header,
  .job-card-head,
  .job-title-row,
  .job-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .spotlight-score {
    width: 100%;
    height: auto;
    padding: 16px 14px;
    align-items: flex-start;
  }

  .job-card-head__main {
    width: 100%;
  }

  .job-title-tags {
    justify-content: flex-start;
  }

  .bottom-actions {
    flex-direction: column;
  }

  .bottom-actions .el-button {
    width: 100%;
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
