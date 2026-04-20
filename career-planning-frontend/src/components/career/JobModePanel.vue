<script setup lang="ts">
import { computed } from 'vue'
import { jobFocusCards, jobMilestones } from '@/mock/mockdata/CareerMode_mockdata'
import { loadCareerFormData } from '@/utils/career-runtime'

// 检查用户是否已提供信息
const hasUserInfo = computed(() => {
  const formData = loadCareerFormData()
  return !!(formData?.education || formData?.major?.length || formData?.targetJob)
})

// 空状态时的引导卡片
const emptyFocusCards = [
  {
    status: '待开始',
    title: '完善求职档案',
    summary: '填写基本信息和求职意向，让系统为你匹配适合的岗位'
  },
  {
    status: '待开始',
    title: '人岗匹配分析',
    summary: '根据你的背景和能力，分析你与目标岗位的匹配度'
  },
  {
    status: '待开始',
    title: '简历优化导出',
    summary: '生成专业的求职简历，支持 PDF/Word 格式导出'
  }
]

// 空状态时的里程碑引导
const emptyMilestones = [
  {
    title: '开始你的求职之旅',
    detail: '点击首页快捷入口「职业规划表」或「简历助手」，开启求职准备流程'
  },
  {
    title: '查看匹配岗位',
    detail: '系统会根据你的信息推荐适合的岗位和发展路径'
  },
  {
    title: '准备面试',
    detail: '获取针对性的面试建议和常见问题准备'
  }
]
</script>

<template>
  <section class="mode-panel mode-panel--job">
    <div class="mode-panel-head">
      <div>
        <p class="mode-panel-kicker">Job Workbench</p>
        <h3>求职冲刺工作台</h3>
      </div>
      <span class="mode-panel-note">基于求职主链路整理的工作台，帮助你高效准备求职</span>
    </div>

    <!-- 有用户信息时显示实际内容 -->
    <template v-if="hasUserInfo">
      <div class="focus-grid">
        <article v-for="item in jobFocusCards" :key="item.title" class="focus-card">
          <span>{{ item.status }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.summary }}</p>
        </article>
      </div>

      <div class="milestone-block">
        <article v-for="item in jobMilestones" :key="item.title" class="milestone-item">
          <strong>{{ item.title }}</strong>
          <p>{{ item.detail }}</p>
        </article>
      </div>
    </template>

    <!-- 无用户信息时显示引导 -->
    <template v-else>
      <div class="focus-grid">
        <article v-for="item in emptyFocusCards" :key="item.title" class="focus-card focus-card--empty">
          <span class="status-tag">{{ item.status }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.summary }}</p>
        </article>
      </div>

      <div class="milestone-block">
        <article v-for="item in emptyMilestones" :key="item.title" class="milestone-item milestone-item--empty">
          <strong>{{ item.title }}</strong>
          <p>{{ item.detail }}</p>
        </article>
      </div>

      <div class="empty-hint">
        <p>💡 请先填写职业规划表单或上传简历，系统将为你匹配合适的岗位和求职建议</p>
      </div>
    </template>
  </section>
</template>

<style scoped>
.mode-panel {
  padding: 22px;
  border-radius: 20px;
  border: 1px solid rgba(191, 219, 254, 0.8);
}

.mode-panel--job {
  background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
}

.mode-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.mode-panel-kicker {
  margin: 0 0 6px;
  color: #2563eb;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.mode-panel-head h3 {
  margin: 0;
  color: #1e3a8a;
  font-size: 20px;
}

.mode-panel-note {
  color: #6b7280;
  font-size: 12px;
  line-height: 1.6;
}

.focus-grid,
.milestone-block {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.focus-card,
.milestone-item {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(191, 219, 254, 0.95);
  background: rgba(255, 255, 255, 0.94);
}

.focus-card span {
  display: inline-flex;
  margin-bottom: 8px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
}

.focus-card strong,
.milestone-item strong {
  display: block;
  margin-bottom: 8px;
  color: #1e3a8a;
  font-size: 16px;
}

.focus-card p,
.milestone-item p {
  margin: 0;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.75;
}

.milestone-block {
  margin-top: 14px;
}

/* 空状态样式 */
.focus-card--empty,
.milestone-item--empty {
  border-style: dashed;
  background: rgba(255, 255, 255, 0.6);
}

.focus-card--empty strong,
.milestone-item--empty strong {
  color: #6b7280;
}

.status-tag {
  display: inline-flex;
  margin-bottom: 8px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(107, 114, 128, 0.1) !important;
  color: #6b7280 !important;
  font-size: 12px;
  font-weight: 700;
}

.empty-hint {
  margin-top: 20px;
  padding: 16px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(37, 99, 235, 0.02) 100%);
  border: 1px dashed rgba(37, 99, 235, 0.3);
  text-align: center;
}

.empty-hint p {
  margin: 0;
  color: #2563eb;
  font-size: 14px;
}

@media (max-width: 960px) {
  .focus-grid,
  .milestone-block {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .mode-panel-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
