<template>
  <div class="ai-insight-box fade-in-up" style="animation-delay: 0.2s;">
    <div class="box-header">
      <el-icon><MagicStick /></el-icon>
      <span>AI 路径诊断</span>
    </div>
    <div class="box-content">
      <p class="summary-text">{{ step.transition_reason }}</p>
      <el-divider border-style="dashed" style="margin: 12px 0;" />
      <p class="summary-text"><strong>全局总结：</strong>{{ pathData.overall_summary }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MagicStick } from '@element-plus/icons-vue'
import type { CareerPath, PathStep } from '../types'

defineProps<{
  pathData: CareerPath
  step: PathStep
}>()
</script>

<style scoped>
.ai-insight-box {
  margin: 20px 0;
  background: linear-gradient(145deg, #f0f7ff 0%, #e6f3ff 100%);
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #409eff;
}

.box-header {
  display: flex;
  align-items: center;
  color: #409eff;
  font-weight: bold;
  font-size: 15px;
  margin-bottom: 10px;
}

.box-header .el-icon {
  margin-right: 6px;
  font-size: 18px;
}

.summary-text {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  margin: 0;
  text-align: justify;
}

.fade-in-up {
  animation: fadeInUp 0.5s ease-out forwards;
  opacity: 0;
  transform: translateY(15px);
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
