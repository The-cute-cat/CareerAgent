<script setup lang="ts">
import { computed } from 'vue'
import { Briefcase, Reading } from '@element-plus/icons-vue'

import { useCareerModeStore, type CareerMode } from '@/stores/careerMode'

const careerModeStore = useCareerModeStore()

const options: Array<{
  value: CareerMode
  title: string
  desc: string
  icon: typeof Reading
}> = [
  {
    value: 'learning',
    title: '学习为主',
    desc: '优先展示成长路线、能力提升和学习规划',
    icon: Reading,
  },
  {
    value: 'job',
    title: '找工作为主',
    desc: '优先展示简历、匹配分析和求职准备',
    icon: Briefcase,
  },
]

const currentMode = computed(() => careerModeStore.mode)

const handleSelect = (mode: CareerMode) => {
  if (currentMode.value === mode) return
  careerModeStore.setMode(mode)
}
</script>

<template>
  <section class="mode-switch-card">
    <div class="mode-switch-header">
      <div>
        <p class="mode-switch-kicker">Mode</p>
        <h3>顶部模式切换</h3>
      </div>
    </div>

    <div class="mode-switch-grid">
      <button
        v-for="item in options"
        :key="item.value"
        type="button"
        class="mode-option"
        :class="{ 'is-active': currentMode === item.value }"
        @click="handleSelect(item.value)"
      >
        <div class="mode-option-icon">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div class="mode-option-content">
          <strong>{{ item.title }}</strong>
          <p>{{ item.desc }}</p>
        </div>
      </button>
    </div>
  </section>
</template>

<style scoped>
.mode-switch-card {
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid rgba(191, 203, 217, 0.65);
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.mode-switch-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.mode-switch-kicker {
  margin: 0 0 6px;
  color: #3b82f6;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.mode-switch-header h3 {
  margin: 0;
  font-size: 16px;
  color: #1f2d3d;
}

.mode-switch-tip {
  color: #6b7280;
  font-size: 12px;
  line-height: 1.6;
}

.mode-switch-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.mode-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border: 1px solid #dbe5f0;
  border-radius: 14px;
  background: #fff;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.mode-option:hover {
  border-color: #93c5fd;
  box-shadow: 0 8px 18px rgba(59, 130, 246, 0.08);
}

.mode-option.is-active {
  border-color: #409eff;
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
  box-shadow: 0 10px 22px rgba(64, 158, 255, 0.14);
}

.mode-option-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: #f3f7fb;
  color: #409eff;
  flex-shrink: 0;
}

.mode-option-icon .el-icon {
  font-size: 18px;
}

.mode-option-content strong {
  display: block;
  margin-bottom: 4px;
  color: #1f2d3d;
  font-size: 14px;
}

.mode-option-content p {
  margin: 0;
  color: #5f6b7a;
  font-size: 12px;
  line-height: 1.65;
}

@media (max-width: 768px) {
  .mode-switch-header,
  .mode-switch-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
