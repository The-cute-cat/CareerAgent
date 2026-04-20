<script setup lang="ts">
import { computed } from 'vue'

import { learningModeFeatures } from '@/mock/mockdata/CareerMode_mockdata'

const props = withDefaults(
  defineProps<{
    activeStep?: string
  }>(),
  {
    activeStep: '1',
  },
)

const currentFeature = computed(() => {
  return learningModeFeatures.find((item) => item.step === props.activeStep) || learningModeFeatures[0]
})
</script>

<template>
  <section class="learning-feature-panel">
    <div class="learning-feature-head">
      <div>
        <p class="learning-feature-kicker">Learning Mode Detail</p>
        <h3>{{ currentFeature.title }}</h3>
        <p class="learning-feature-summary">{{ currentFeature.summary }}</p>
      </div>
      <span class="learning-feature-step">步骤 {{ currentFeature.step }}/5</span>
    </div>

    <div class="learning-feature-grid">
      <article class="learning-feature-card">
        <span>核心输入</span>
        <ul>
          <li v-for="item in currentFeature.inputs" :key="item">{{ item }}</li>
        </ul>
      </article>

      <article class="learning-feature-card">
        <span>系统输出</span>
        <ul>
          <li v-for="item in currentFeature.outputs" :key="item">{{ item }}</li>
        </ul>
      </article>

      <article class="learning-feature-card">
        <span>视频演示点</span>
        <ul>
          <li v-for="item in currentFeature.demoPoints" :key="item">{{ item }}</li>
        </ul>
      </article>

      <article class="learning-feature-card learning-feature-card--accent">
        <span>与就业模式区分</span>
        <ul>
          <li v-for="item in currentFeature.differentiators" :key="item">{{ item }}</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<style scoped>
.learning-feature-panel {
  padding: 18px 20px;
  border-radius: 20px;
  border: 1px solid rgba(125, 211, 252, 0.45);
  background: linear-gradient(180deg, rgba(236, 254, 255, 0.96) 0%, #ffffff 100%);
  box-shadow: 0 12px 26px rgba(15, 118, 110, 0.07);
}

.learning-feature-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.learning-feature-kicker {
  margin: 0 0 6px;
  color: #0891b2;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.learning-feature-head h3 {
  margin: 0;
  color: #164e63;
  font-size: 18px;
}

.learning-feature-summary {
  margin: 8px 0 0;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.75;
}

.learning-feature-step {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(8, 145, 178, 0.1);
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.learning-feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.learning-feature-card {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(186, 230, 253, 0.85);
  background: rgba(255, 255, 255, 0.92);
}

.learning-feature-card--accent {
  background: linear-gradient(180deg, #f0fdfa 0%, #ffffff 100%);
  border-color: rgba(94, 234, 212, 0.9);
}

.learning-feature-card span {
  display: block;
  margin-bottom: 10px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
}

.learning-feature-card ul {
  margin: 0;
  padding-left: 18px;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.8;
}

@media (max-width: 1280px) {
  .learning-feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .learning-feature-head,
  .learning-feature-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
