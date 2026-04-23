<script setup lang="ts">
import { computed } from 'vue'
import { loadCareerFormData } from '@/utils/career-runtime'

interface LearningRecommendItem {
  title: string
  summary: string
  tags: string[]
}

// 检查用户是否已提供信息
const hasUserInfo = computed(() => {
  const formData = loadCareerFormData()
  return !!(formData?.education || formData?.major?.length || formData?.targetJob)
})

// 有用户信息时的推荐内容
const recommendDirections: LearningRecommendItem[] = [
  {
    title: '推荐先梳理发展方向',
    summary: '先结合你的专业、项目和目标岗位，确认更适合走前端、全栈还是业务型技术方向。',
    tags: ['方向探索', '职业定位'],
  },
  {
    title: '优先补齐核心能力',
    summary: '建议先沉淀 2-3 项能直接支撑目标发展的核心技能，并补一段能展示能力的项目经历。',
    tags: ['技能提升', '项目沉淀'],
  },
  {
    title: '建议查看发展路径',
    summary: '完成基础画像后，可以继续查看职业发展报告，提前理解短期与中期成长路径。',
    tags: ['路径规划', '报告查看'],
  },
]

// 空状态时的引导步骤
const emptyGuidance: LearningRecommendItem[] = [
  {
    title: '第一步：填写基本信息',
    summary: '告诉系统你的专业背景、技能特长和感兴趣的方向，这是获得个性化建议的基础。',
    tags: ['开始', '信息录入'],
  },
  {
    title: '第二步：探索职业方向',
    summary: '基于你提供的信息，系统会分析并推荐适合你的技术发展路线。',
    tags: ['智能分析', '方向推荐'],
  },
  {
    title: '第三步：制定行动计划',
    summary: '获取专属的学习计划和成长路径，一步步实现职业目标。',
    tags: ['计划生成', '持续成长'],
  },
]
</script>

<template>
  <section class="learning-panel">
    <div class="learning-panel-head">
      <div>
        <p class="learning-panel-kicker">Learning Recommendations</p>
        <h3>学习模式推荐</h3>
      </div>
      <span class="learning-panel-note">当前为静态展示，后续可以平滑替换为真实接口数据</span>
    </div>

    <div class="learning-panel-grid">
      <article 
        v-for="item in (hasUserInfo ? recommendDirections : emptyGuidance)" 
        :key="item.title" 
        class="learning-panel-card"
        :class="{ 'learning-panel-card--empty': !hasUserInfo }"
      >
        <strong>{{ item.title }}</strong>
        <p>{{ item.summary }}</p>
        <div class="learning-panel-tags">
          <span v-for="tag in item.tags" :key="tag">{{ tag }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.learning-panel {
  padding: 20px 22px;
  border-radius: 18px;
  border: 1px solid rgba(187, 247, 208, 0.7);
  background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%);
}

.learning-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.learning-panel-kicker {
  margin: 0 0 6px;
  color: #16a34a;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.learning-panel-head h3 {
  margin: 0;
  color: #14532d;
  font-size: 18px;
}

.learning-panel-note {
  color: #6b7280;
  font-size: 12px;
  line-height: 1.6;
}

.learning-panel-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.learning-panel-card {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(187, 247, 208, 0.8);
  background: rgba(255, 255, 255, 0.9);
}

.learning-panel-card--empty {
  border-style: dashed;
  background: rgba(255, 255, 255, 0.6);
}

.learning-panel-card--empty strong {
  color: #6b7280;
}

.learning-panel-card--empty .learning-panel-tags span {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.learning-panel-card strong {
  display: block;
  margin-bottom: 8px;
  color: #166534;
  font-size: 15px;
}

.learning-panel-card p {
  margin: 0;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.75;
}

.learning-panel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.learning-panel-tags span {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.1);
  color: #15803d;
  font-size: 12px;
  font-weight: 600;
}

@media (max-width: 960px) {
  .learning-panel-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .learning-panel-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
