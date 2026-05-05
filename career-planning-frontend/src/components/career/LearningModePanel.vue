<script setup lang="ts">
import { computed } from 'vue'
import { learningFocusCards, learningRoadmap } from '@/mock/mockdata/CareerMode_mockdata'
import { loadCareerFormData } from '@/utils/career-runtime'

// 检查用户是否已提供信息
const hasUserInfo = computed(() => {
  const formData = loadCareerFormData()
  return !!(formData?.education || formData?.major?.length || formData?.targetJob)
})

// 空状态时的引导卡片
const emptyFocusCards = [
  {
    label: '第一步',
    value: '完善个人档案',
    hint: '先填写基本信息，让系统了解你的背景和兴趣方向'
  },
  {
    label: '第二步', 
    value: '探索职业方向',
    hint: '根据你的专业和兴趣，获取个性化的发展建议'
  },
  {
    label: '第三步',
    value: '制定学习计划',
    hint: '系统会为你生成专属的成长路径和学习路线'
  }
]

// 空状态时的学习路径引导
const emptyRoadmap = [
  {
    stage: '1',
    title: '开始职业规划之旅',
    summary: '点击首页快捷入口「职业规划表」或「简历助手」，填写你的基本信息、技能和求职意向',
    tags: ['上传简历', '填写表单', '语音输入']
  }
]
</script>

<template>
  <section class="mode-panel mode-panel--learning">
    <div class="mode-panel-head">
      <div>
        <p class="mode-panel-kicker">Learning Workbench</p>
        <h3>学习成长工作台</h3>
      </div>
      <span class="mode-panel-note">本地示例数据，快速预览功能效果</span>
    </div>

    <!-- 有用户信息时显示推荐 -->
    <template v-if="hasUserInfo">
      <div class="focus-grid">
        <article v-for="item in learningFocusCards" :key="item.label" class="focus-card">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.hint }}</p>
        </article>
      </div>

      <div class="roadmap-block">
        <article v-for="item in learningRoadmap" :key="item.stage" class="roadmap-item">
          <div class="roadmap-stage">{{ item.stage }}</div>
          <div class="roadmap-main">
            <strong>{{ item.title }}</strong>
            <p>{{ item.summary }}</p>
            <div class="roadmap-tags">
              <span v-for="tag in item.tags" :key="tag">{{ tag }}</span>
            </div>
          </div>
        </article>
      </div>
    </template>

    <!-- 无用户信息时显示引导 -->
    <template v-else>
      <div class="focus-grid">
        <article v-for="item in emptyFocusCards" :key="item.label" class="focus-card focus-card--empty">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.hint }}</p>
        </article>
      </div>

      <div class="roadmap-block">
        <article v-for="item in emptyRoadmap" :key="item.stage" class="roadmap-item roadmap-item--empty">
          <div class="roadmap-stage roadmap-stage--empty">{{ item.stage }}</div>
          <div class="roadmap-main">
            <strong>{{ item.title }}</strong>
            <p>{{ item.summary }}</p>
            <div class="roadmap-tags">
              <span v-for="tag in item.tags" :key="tag">{{ tag }}</span>
            </div>
          </div>
        </article>
      </div>

      <div class="empty-hint">
        <p>💡 请先填写职业规划表单或上传简历，系统将为你生成专属的学习发展建议</p>
      </div>
    </template>
  </section>
</template>

<style scoped>
.mode-panel {
  padding: 22px;
  border-radius: 20px;
  border: 1px solid rgba(186, 230, 253, 0.7);
}

.mode-panel--learning {
  background: linear-gradient(180deg, #f0fdfa 0%, #ffffff 100%);
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
  color: #0f766e;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.mode-panel-head h3 {
  margin: 0;
  color: #134e4a;
  font-size: 20px;
}

.mode-panel-note {
  color: #6b7280;
  font-size: 12px;
  line-height: 1.6;
}

.focus-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.focus-card,
.roadmap-item {
  border-radius: 16px;
  border: 1px solid rgba(153, 246, 228, 0.8);
  background: rgba(255, 255, 255, 0.92);
}

.focus-card {
  padding: 16px;
}

.focus-card span {
  display: block;
  margin-bottom: 8px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
}

.focus-card strong {
  display: block;
  margin-bottom: 8px;
  color: #134e4a;
  font-size: 16px;
}

.focus-card p,
.roadmap-main p {
  margin: 0;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.75;
}

.roadmap-block {
  display: grid;
  gap: 12px;
}

.roadmap-item {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 16px;
  padding: 16px;
}

.roadmap-stage {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 64px;
  border-radius: 14px;
  background: linear-gradient(135deg, #14b8a6 0%, #0f766e 100%);
  color: #fff;
  font-size: 20px;
  font-weight: 800;
}

.roadmap-main strong {
  display: block;
  margin-bottom: 8px;
  color: #134e4a;
  font-size: 16px;
}

.roadmap-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.roadmap-tags span {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(20, 184, 166, 0.1);
  color: #0f766e;
  font-size: 12px;
  font-weight: 600;
}

/* 空状态样式 */
.focus-card--empty {
  border-style: dashed;
  background: rgba(255, 255, 255, 0.6);
}

.focus-card--empty strong {
  color: #6b7280;
}

.roadmap-item--empty {
  border-style: dashed;
  background: rgba(255, 255, 255, 0.6);
}

.roadmap-stage--empty {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
}

.empty-hint {
  margin-top: 20px;
  padding: 16px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.08) 0%, rgba(64, 158, 255, 0.02) 100%);
  border: 1px dashed rgba(64, 158, 255, 0.3);
  text-align: center;
}

.empty-hint p {
  margin: 0;
  color: #409eff;
  font-size: 14px;
}

@media (max-width: 960px) {
  .focus-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .mode-panel-head,
  .roadmap-item {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
