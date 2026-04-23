<template>
  <div class="interview-report-page">
    <!-- 页面头部 -->
    <div class="report-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" text @click="goBack">返回</el-button>
        <div class="title-section">
          <h1>{{ positionName }} - 面试报告</h1>
          <p class="subtitle">面试日期：{{ interviewDate }}</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button :icon="Download" type="primary" plain @click="downloadReport">下载报告</el-button>
        <el-button :icon="Share" type="success" plain @click="shareReport">分享报告</el-button>
      </div>
    </div>

    <!-- 报告内容 -->
    <div class="report-content">
      <!-- 综合评分卡片 -->
      <div class="score-overview">
        <div class="main-score-card">
          <div class="score-circle">
            <el-progress
              type="dashboard"
              :percentage="interviewResult.overallScore"
              :color="scoreColor"
              :stroke-width="12"
              :width="160"
            />
            <div class="score-label">综合评分</div>
          </div>
          <div class="score-detail">
            <h3>面试表现</h3>
            <p class="score-desc">{{ getScoreDescription(interviewResult.overallScore) }}</p>
            <div class="score-tags">
              <el-tag v-for="tag in scoreTags" :key="tag" :type="tag.type" effect="light">
                {{ tag.label }}
              </el-tag>
            </div>
          </div>
        </div>
        <div class="dimension-scores">
          <div class="dimension-item" v-for="(score, key) in interviewResult.dimensionScores" :key="key">
            <div class="dimension-label">{{ dimensionLabels[key] }}</div>
            <el-progress :percentage="score" :color="getProgressColor(score)" :stroke-width="8" />
            <div class="dimension-value">{{ score }}分</div>
          </div>
        </div>
      </div>

      <!-- 技能评估 -->
      <div class="skill-assessment section-card">
        <div class="section-header">
          <el-icon><TrendCharts /></el-icon>
          <h3>技能掌握程度</h3>
        </div>
        <div class="skill-list">
          <div 
            class="skill-item" 
            v-for="skill in interviewResult.skillAssessment" 
            :key="skill.name"
          >
            <div class="skill-info">
              <span class="skill-name">{{ skill.name }}</span>
              <span class="skill-score" :class="getScoreClass(skill.score)">
                {{ skill.score }}/{{ skill.fullMark }}
              </span>
            </div>
            <el-progress 
              :percentage="skill.score" 
              :color="getProgressColor(skill.score)"
              :stroke-width="6"
              :show-text="false"
            />
          </div>
        </div>
      </div>

      <!-- 能力短板分析 -->
      <div class="weakness-analysis section-card">
        <div class="section-header">
          <el-icon><Warning /></el-icon>
          <h3>能力短板分析</h3>
        </div>
        <div class="weakness-list">
          <div 
            class="weakness-item" 
            :class="item.severity"
            v-for="item in interviewResult.weaknessAnalysis" 
            :key="item.area"
          >
            <div class="weakness-header">
              <el-tag :type="item.severity === 'high' ? 'danger' : item.severity === 'medium' ? 'warning' : 'info'" size="small">
                {{ severityLabels[item.severity] }}
              </el-tag>
              <span class="weakness-area">{{ item.area }}</span>
            </div>
            <p class="weakness-suggestion">{{ item.suggestion }}</p>
          </div>
        </div>
      </div>

      <!-- 提升建议 -->
      <div class="improvement-suggestions section-card">
        <div class="section-header">
          <el-icon><Lightning /></el-icon>
          <h3>个性化提升建议</h3>
        </div>
        <div class="suggestion-categories">
          <div 
            class="suggestion-category" 
            v-for="category in interviewResult.improvementSuggestions" 
            :key="category.category"
          >
            <h4>{{ category.category }}</h4>
            <ul>
              <li v-for="(item, index) in category.items" :key="index">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- AI评语 -->
      <div class="ai-feedback section-card">
        <div class="section-header">
          <el-icon><ChatDotSquare /></el-icon>
          <h3>AI面试官评语</h3>
        </div>
        <div class="feedback-content">
          <div class="ai-avatar">🤖</div>
          <div class="feedback-text">
            <p>{{ interviewResult.aiFeedback }}</p>
          </div>
        </div>
      </div>

      <!-- 面试记录统计 -->
      <div class="interview-stats section-card">
        <div class="section-header">
          <el-icon><Document /></el-icon>
          <h3>面试过程记录</h3>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ interviewResult.interviewRecord.totalQuestions }}</div>
            <div class="stat-label">总问题数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ interviewResult.interviewRecord.answeredQuestions }}</div>
            <div class="stat-label">已回答</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ interviewResult.interviewRecord.avgResponseTime }}s</div>
            <div class="stat-label">平均回答时长</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ interviewResult.interviewRecord.fluencyScore }}%</div>
            <div class="stat-label">流畅度评分</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, 
  Download, 
  Share, 
  TrendCharts, 
  Warning, 
  Lightning,
  ChatDotSquare,
  Document
} from '@element-plus/icons-vue'
import { mockBackendInterviewResult } from '@/mock/mockBackendInterviewData'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

// 获取岗位名称
const positionName = computed(() => {
  const name = route.query.position as string
  return name ? decodeURIComponent(name) : 'Java后端工程师'
})

// 面试日期
const interviewDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// 面试结果数据（使用后端开发模拟数据）
const interviewResult = ref(mockBackendInterviewResult)

// 维度标签映射
const dimensionLabels: Record<string, string> = {
  technical: '技术能力',
  communication: '沟通能力',
  logic: '逻辑思维',
  expression: '表达能力',
  attitude: '态度素养'
}

// 严重度标签
const severityLabels: Record<string, string> = {
  high: '高优先级',
  medium: '中优先级',
  low: '低优先级'
}

// 评分标签
const scoreTags = computed(() => {
  const score = interviewResult.value.overallScore
  const tags = []
  if (score >= 80) {
    tags.push({ label: '优秀', type: 'success' })
  } else if (score >= 70) {
    tags.push({ label: '良好', type: 'primary' })
  } else {
    tags.push({ label: '待提升', type: 'warning' })
  }
  return tags
})

// 分数颜色
const scoreColor = computed(() => {
  const score = interviewResult.value.overallScore
  if (score >= 85) return '#67C23A'
  if (score >= 75) return '#409EFF'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
})

// 获取进度条颜色
const getProgressColor = (score: number) => {
  if (score >= 85) return '#67C23A'
  if (score >= 70) return '#409EFF'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

// 获取分数描述
const getScoreDescription = (score: number) => {
  if (score >= 85) return '表现非常出色，技术扎实，潜力巨大'
  if (score >= 75) return '表现良好，具备扎实的技术基础'
  if (score >= 60) return '整体表现尚可，有提升空间'
  return '需要加强技术学习和实践'
}

// 获取分数样式类
const getScoreClass = (score: number) => {
  if (score >= 85) return 'excellent'
  if (score >= 70) return 'good'
  if (score >= 60) return 'average'
  return 'poor'
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 下载报告
const downloadReport = () => {
  ElMessage.success('报告下载功能开发中...')
}

// 分享报告
const shareReport = () => {
  ElMessage.success('报告分享功能开发中...')
}

onMounted(() => {
  // 可以根据岗位ID加载对应的面试结果数据
  const positionId = route.params.id as string
  console.log('查看岗位面试报告:', positionId, positionName.value)
})
</script>

<style scoped lang="scss">
.interview-report-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  padding: 24px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: #fff;
  padding: 20px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .title-section {
      h1 {
        margin: 0;
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }
      .subtitle {
        margin: 4px 0 0;
        font-size: 14px;
        color: #909399;
      }
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.report-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.score-overview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;

  .main-score-card {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 32px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

    .score-circle {
      text-align: center;

      .score-label {
        margin-top: 8px;
        font-size: 14px;
        color: #606266;
      }
    }

    .score-detail {
      flex: 1;

      h3 {
        margin: 0 0 8px;
        font-size: 18px;
        color: #303133;
      }

      .score-desc {
        margin: 0 0 16px;
        color: #606266;
        font-size: 14px;
      }

      .score-tags {
        display: flex;
        gap: 8px;
      }
    }
  }

  .dimension-scores {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

    .dimension-item {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }

      .dimension-label {
        width: 80px;
        font-size: 14px;
        color: #606266;
      }

      :deep(.el-progress) {
        flex: 1;
      }

      .dimension-value {
        width: 50px;
        text-align: right;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
}

.section-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;

    .el-icon {
      font-size: 20px;
      color: #409EFF;
    }

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.skill-assessment {
  .skill-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;

    .skill-item {
      .skill-info {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;

        .skill-name {
          font-size: 14px;
          color: #606266;
        }

        .skill-score {
          font-size: 14px;
          font-weight: 600;

          &.excellent { color: #67C23A; }
          &.good { color: #409EFF; }
          &.average { color: #E6A23C; }
          &.poor { color: #F56C6C; }
        }
      }
    }
  }
}

.weakness-analysis {
  .weakness-list {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .weakness-item {
      padding: 16px;
      border-radius: 8px;
      background: #f5f7fa;

      &.high { border-left: 4px solid #F56C6C; }
      &.medium { border-left: 4px solid #E6A23C; }
      &.low { border-left: 4px solid #909399; }

      .weakness-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .weakness-area {
          font-weight: 600;
          color: #303133;
        }
      }

      .weakness-suggestion {
        margin: 0;
        font-size: 14px;
        color: #606266;
        line-height: 1.6;
      }
    }
  }
}

.improvement-suggestions {
  .suggestion-categories {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;

    .suggestion-category {
      padding: 16px;
      border-radius: 8px;
      background: #f5f7fa;

      h4 {
        margin: 0 0 12px;
        font-size: 15px;
        color: #303133;
      }

      ul {
        margin: 0;
        padding-left: 20px;

        li {
          font-size: 13px;
          color: #606266;
          margin-bottom: 8px;
          line-height: 1.5;

          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }
  }
}

.ai-feedback {
  .feedback-content {
    display: flex;
    gap: 16px;
    padding: 20px;
    background: linear-gradient(135deg, #f0f7ff 0%, #e6f2ff 100%);
    border-radius: 8px;

    .ai-avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: #409EFF;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      flex-shrink: 0;
    }

    .feedback-text {
      p {
        margin: 0;
        font-size: 14px;
        color: #303133;
        line-height: 1.8;
      }
    }
  }
}

.interview-stats {
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;

    .stat-item {
      text-align: center;
      padding: 20px;
      background: #f5f7fa;
      border-radius: 8px;

      .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: #409EFF;
        margin-bottom: 8px;
      }

      .stat-label {
        font-size: 14px;
        color: #606266;
      }
    }
  }
}

@media (max-width: 768px) {
  .score-overview {
    grid-template-columns: 1fr;
  }

  .skill-assessment .skill-list {
    grid-template-columns: 1fr;
  }

  .improvement-suggestions .suggestion-categories {
    grid-template-columns: 1fr;
  }

  .interview-stats .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
