<template>
  <div class="metrics-panel fade-in-up" style="animation-delay: 0.1s;">
    <el-row :gutter="10">
      <el-col :span="8">
        <div class="metric-card">
          <div class="label">路径阻力</div>
          <div class="value highlight-low">{{ pathData.total_routing_cost }}</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="metric-card">
          <div class="label">硬技能重合</div>
          <div class="value">{{ formatPercent(step.jaccard_high) }}</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="metric-card">
          <div class="label">软素质契合</div>
          <div class="value highlight-high">{{ formatPercent(step.cos_low) }}</div>
        </div>
      </el-col>
    </el-row>
  </div>

  <div class="metrics-panel fade-in-up" style="animation-delay: 0.15s; margin-top: 10px;">
    <el-row :gutter="10">
      <el-col :span="12">
        <div class="metric-card">
          <div class="label">预期薪资增益</div>
          <div class="value">
            {{ step.salary_gain > 0 ? `+${formatPercent(step.salary_gain)}` : '暂无增益' }}
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="metric-card">
          <div class="label">路径类型</div>
          <div class="value">{{ pathTypeText }}</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CareerPath, PathStep } from '../types'

const props = defineProps<{
  pathData: CareerPath
  step: PathStep
}>()

const pathTypeText = computed(() => 
  props.pathData.path_type === 'vertical' ? '垂直晋升' : '横向换岗'
)

function formatPercent(val: number): string {
  return `${(val * 100).toFixed(0)}%`
}
</script>

<style scoped>
.metrics-panel {
  margin-bottom: 16px;
}

.metric-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  border: 1px solid #ebeef5;
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.metric-card .label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.metric-card .value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.highlight-low { color: #67c23a !important; }
.highlight-high { color: #e6a23c !important; }

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
