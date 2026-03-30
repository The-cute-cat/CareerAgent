<template>
  <div class="job-matching-container">
    <div class="job-matching-shell">
      <!-- 顶部 Hero 区域 -->
      <section class="hero-panel">
        <div class="hero-copy">
          <div class="hero-kicker">
            <el-icon><MagicStick /></el-icon>
            AI 匹配引擎
          </div>
          <h1 class="page-title">
            <el-icon><TrendCharts /></el-icon>
            岗位推荐与人岗匹配分析
          </h1>
          <p class="page-subtitle">
            围绕你的职业画像、技能结构与发展方向，系统会筛选更适合投递的岗位，并给出清晰的匹配理由与行动建议。
          </p>
          <div class="hero-tags">
            <span class="hero-tag">职业画像驱动</span>
            <span class="hero-tag">推荐结果可解释</span>
            <span class="hero-tag">行动建议可执行</span>
          </div>
        </div>

        <div v-if="hasData" class="hero-score-panel">
          <div class="hero-score-caption">当前最佳匹配</div>
          <div class="hero-score-value">{{ topScore }}<span>分</span></div>
          <div class="hero-score-level">{{ getMatchScoreLevel(topScore) }}</div>
          <div class="hero-score-meta">
            <div class="hero-meta-item">
              <span class="hero-meta-label">推荐岗位</span>
              <strong>{{ canApplyCount }}</strong>
            </div>
            <div class="hero-meta-item">
              <span class="hero-meta-label">平均匹配</span>
              <strong>{{ averageScore }}</strong>
            </div>
          </div>
        </div>
      </section>

      <!-- Loading 状态 -->
      <div v-if="loading" class="loading-container state-card">
        <el-icon class="loading-icon" :size="52"><DataAnalysis /></el-icon>
        <h3>正在生成岗位匹配视图</h3>
        <p>系统正在整理岗位推荐结果和人岗匹配分析，请稍候片刻。</p>
      </div>

      <!-- 主要内容区域 -->
      <template v-else-if="hasData">
        <!-- 第一行卡片：最佳推荐 + 整体概况 -->
        <div class="top-cards-row">
          <!-- 最佳推荐岗位卡片（大卡片） -->
          <article class="overview-card spotlight-card">
            <div class="spotlight-header">
              <div>
                <div class="section-eyebrow">最佳推荐岗位</div>
                <h2>{{ topJob?.raw_data.job_name || '暂无岗位' }}</h2>
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
            </div>

            <p class="spotlight-analysis">{{ topJob?.deep_analysis.all_analysis || '暂无分析数据。' }}</p>

            <div class="spotlight-actions">
              <el-button v-if="topJob" type="primary" @click="goToJobDetail(topJob.job_id)">
                查看最佳岗位详情
                <el-icon><ArrowRight /></el-icon>
              </el-button>
              <div class="spotlight-advice">
                <el-icon><InfoFilled /></el-icon>
                <span>{{ topJob?.deep_analysis.actionable_advice || '继续完善技能与项目经历，可提升匹配准确性。' }}</span>
              </div>
            </div>
          </article>

          <!-- 右侧组合：整体概况 + 推荐岗位序列 -->
          <div class="right-cards-stack">
            <!-- 整体概况卡片 -->
            <article class="overview-card metrics-card">
              <div class="section-eyebrow">整体概况</div>
              <div class="metrics-list">
                <div class="metric-tile">
                  <span class="metric-label">分析岗位</span>
                  <strong>{{ matchItems.length }}</strong>
                  <small>已纳入本次智能推荐</small>
                </div>
                <div class="metric-tile accent">
                  <span class="metric-label">建议投递</span>
                  <strong>{{ canApplyCount }}</strong>
                  <small>投递建议占比 {{ recommendRatio }}%</small>
                </div>
                <div class="metric-tile">
                  <span class="metric-label">平均匹配度</span>
                  <strong>{{ averageScore }}</strong>
                  <small>反映当前整体竞争力</small>
                </div>
              </div>
            </article>

            <!-- 推荐岗位序列卡片 -->
            <article class="overview-card ranking-card">
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
                  <span class="ranking-index">{{ index + 1 }}</span>
                  <span class="ranking-name">{{ item.raw_data.job_name }}</span>
                  <span class="ranking-score" :style="{ color: getMatchScoreColor(Math.round((item.score || 0) * 100)) }">
                    {{ Math.round((item.score || 0) * 100) }}分
                  </span>
                </button>
              </div>
            </article>
          </div>
        </div>

        <!-- 岗位推荐列表区域 -->
        <section class="recommend-section">
          <div class="section-header">
            <div>
              <div class="section-eyebrow">岗位推荐列表</div>
              <h2 class="section-title">为你精选的匹配岗位</h2>
              <p class="section-desc">
                从匹配度、投递建议、岗位门槛与核心技能几个维度，帮助你快速判断优先级。
              </p>
            </div>
            <el-tag size="large" type="primary" effect="light" class="count-tag">共 {{ sortedJobs.length }} 个岗位</el-tag>
          </div>

          <div class="job-recommend-grid">
            <article
              v-for="(item, index) in sortedJobs"
              :key="item.job_id"
              class="job-recommend-card"
            >
              <div class="job-card-top">
                <div class="job-rank" :class="{ 'top-rank': index < 3 }">{{ index + 1 }}</div>
                <div class="job-main">
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
                        {{ item.deep_analysis.can_apply ? '建议投递' : '建议补强后再投递' }}
                      </el-tag>
                    </div>
                  </div>

                  <div class="job-meta-grid">
                    <span class="meta-chip"><el-icon><Briefcase /></el-icon>{{ item.raw_data.profiles.job_attributes.industry }}</span>
                    <span class="meta-chip"><el-icon><Money /></el-icon>{{ item.raw_data.profiles.job_attributes.salary_competitiveness }}竞争力</span>
                    <span class="meta-chip"><el-icon><Trophy /></el-icon>{{ item.raw_data.profiles.basic_requirements.degree }}</span>
                    <span class="meta-chip"><el-icon><Briefcase /></el-icon>经验 {{ item.raw_data.profiles.basic_requirements.experience_years }}</span>
                  </div>
                </div>
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

              <div class="job-body">
                <p class="job-analysis">{{ item.deep_analysis.all_analysis || '暂无岗位分析摘要。' }}</p>

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

      <!-- 空状态 -->
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

const router = useRouter()
const matchItems = ref<JobMatchItem[]>([])
const loading = ref(false)

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
    matchItems.value = stored ? JSON.parse(stored) as JobMatchItem[] : []
  } catch (e) {
    console.error('加载匹配结果失败:', e)
    ElMessage.error('数据加载失败，已使用示例数据')
    matchItems.value = mockJobMatchItems
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
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

const getMatchScoreLevel = (score: number) => {
  if (score >= 85) return '非常匹配'
  if (score >= 70) return '较为匹配'
  if (score >= 55) return '基本匹配'
  return '有待提升'
}

const splitSkills = (str: string) => {
  return str ? str.split(/[,，、]/).map(s => s.trim()).filter(Boolean) : []
}

const goToAssessment = () => {
  router.push('/career-form')
}

const refreshData = () => {
  loadMatchResult()
}

onMounted(() => {
  loadMatchResult()
})
</script>

<style scoped lang="scss">
.job-matching-container {
  min-height: calc(100vh - 60px);
  padding: 28px 20px 48px;
  background:
    radial-gradient(circle at top left, rgba(90, 149, 255, 0.18), transparent 22%),
    radial-gradient(circle at top right, rgba(255, 193, 92, 0.18), transparent 18%),
    linear-gradient(180deg, #f4f8ff 0%, #edf5ff 52%, #f7fbff 100%);
}

.job-matching-shell {
  max-width: 1260px;
  margin: 0 auto;
  position: relative;
}

.job-matching-shell::before {
  content: '';
  position: absolute;
  inset: 88px 0 auto;
  height: 520px;
  border-radius: 40px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.56), rgba(255, 255, 255, 0.16)),
    radial-gradient(circle at left center, rgba(59, 130, 246, 0.16), transparent 35%);
  pointer-events: none;
}

.hero-panel,
.overview-card,
.recommend-section,
.state-card,
.bottom-actions {
  position: relative;
  z-index: 1;
}

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.8fr);
  gap: 24px;
  padding: 34px 36px;
  margin-bottom: 28px;
  border-radius: 32px;
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.24), transparent 26%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(245, 250, 255, 0.92));
  border: 1px solid rgba(211, 226, 246, 0.9);
  box-shadow:
    0 24px 60px rgba(31, 78, 145, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.86);
}

.hero-kicker,
.section-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.page-title {
  margin: 18px 0 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: clamp(30px, 4vw, 42px);
  line-height: 1.1;
  font-weight: 800;
  color: #173a5d;
}

.page-title .el-icon {
  color: #2f7df6;
}

.page-subtitle {
  max-width: 760px;
  margin: 0;
  color: #5f738b;
  font-size: 15px;
  line-height: 1.9;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
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
  padding: 24px;
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(18, 72, 142, 0.96), rgba(29, 97, 181, 0.92));
  color: #fff;
  box-shadow: 0 22px 48px rgba(29, 97, 181, 0.24);
}

.hero-score-caption {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.72);
}

.hero-score-value {
  margin-top: 10px;
  font-size: 64px;
  font-weight: 800;
  line-height: 1;
}

.hero-score-value span {
  margin-left: 4px;
  font-size: 24px;
  font-weight: 600;
}

.hero-score-level {
  margin-top: 12px;
  font-size: 18px;
  font-weight: 700;
}

.hero-score-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 22px;
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
  font-size: 24px;
  font-weight: 800;
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
  color: #409EFF;
  margin-bottom: 12px;
}

.loading-icon {
  animation: rotate 1.5s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 重构第一行布局：左侧大卡片，右侧两个卡片垂直排列 */
.top-cards-row {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.75fr);
  gap: 22px;
  margin-bottom: 30px;
}

.right-cards-stack {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.overview-card {
  padding: 24px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(220, 231, 244, 0.96);
  box-shadow: 0 20px 48px rgba(27, 74, 130, 0.08);
}

.spotlight-card {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.15), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 250, 255, 0.96));
}

.spotlight-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.spotlight-header h2 {
  margin: 14px 0 0;
  color: #173a5d;
  font-size: 30px;
  font-weight: 800;
  line-height: 1.2;
}

.spotlight-score {
  flex-shrink: 0;
  width: 124px;
  height: 124px;
  border-radius: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--score-color) 16%, white);
  border: 1px solid color-mix(in srgb, var(--score-color) 35%, white);
  color: var(--score-color);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.86);
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
  gap: 10px;
  margin: 18px 0 20px;
}

.spotlight-meta span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(237, 245, 255, 0.96);
  color: #55718f;
  font-size: 13px;
  font-weight: 600;
}

.spotlight-analysis {
  margin: 0;
  color: #49647f;
  font-size: 15px;
  line-height: 1.9;
}

.spotlight-actions {
  margin-top: auto;
  padding-top: 22px;
}

.spotlight-actions .el-button {
  border-radius: 14px;
}

.spotlight-advice {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(240, 247, 255, 0.95);
  color: #5f738b;
  font-size: 14px;
  line-height: 1.7;
}

.metrics-card,
.ranking-card {
  display: flex;
  flex-direction: column;
}

.metrics-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  height: 100%;
}

.metric-tile {
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
  font-size: 36px;
  font-weight: 800;
}

.metric-tile small {
  color: #6d8298;
  font-size: 13px;
  line-height: 1.6;
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

.card-heading .el-icon {
  color: #2563eb;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 18px;
}

.ranking-item {
  width: 100%;
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
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
  background: linear-gradient(135deg, #2f7df6, #69b5ff);
  color: #fff;
  font-size: 14px;
  font-weight: 800;
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

.recommend-section {
  margin-bottom: 28px;
  padding: 28px;
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.92);
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
  padding: 22px;
  border-radius: 26px;
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

.job-card-top {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.job-rank {
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

.job-rank.top-rank {
  background: linear-gradient(135deg, #f0aa2a, #f7c870);
  color: #fff;
  box-shadow: 0 12px 28px rgba(240, 170, 42, 0.26);
}

.job-main {
  flex: 1;
  min-width: 0;
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
  font-size: 22px;
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
  margin: 18px 0 16px;
  border-radius: 999px;
  background: #e8f0fa;
  overflow: hidden;
}

.job-score-fill {
  height: 100%;
  border-radius: inherit;
}

.job-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.job-analysis {
  margin: 0;
  color: #516b85;
  font-size: 14px;
  line-height: 1.85;
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

.job-footer {
  margin-top: auto;
  padding-top: 4px;
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

.advice-label {
  color: #173a5d;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.job-footer .el-button {
  border-radius: 14px;
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

@media (max-width: 1180px) {
  .hero-panel,
  .top-cards-row {
    grid-template-columns: 1fr;
  }

  .metrics-list,
  .job-recommend-grid {
    grid-template-columns: 1fr;
  }
  
  .right-cards-stack {
    gap: 22px;
  }
}

@media (max-width: 768px) {
  .job-matching-container {
    padding: 20px 14px 36px;
  }

  .hero-panel,
  .recommend-section,
  .overview-card,
  .state-card {
    padding: 22px 18px;
    border-radius: 24px;
  }

  .page-title {
    font-size: 28px;
  }

  .hero-score-panel {
    padding: 20px;
  }

  .hero-score-value {
    font-size: 54px;
  }

  .spotlight-header,
  .section-header,
  .job-title-row,
  .job-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .spotlight-score {
    width: 100%;
    height: auto;
    padding: 18px 16px;
    align-items: flex-start;
  }

  .hero-score-meta {
    grid-template-columns: 1fr;
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