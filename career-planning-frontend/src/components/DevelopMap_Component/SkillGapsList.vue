<template>
  <div class="action-section fade-in-up" style="animation-delay: 0.3s;">
    <h4 class="section-title">需补齐技能与核心行动方案</h4>
    <el-empty v-if="!skillGaps.length" description="当前步骤暂无技能缺口" />
    <el-card v-for="(gap, index) in skillGaps" :key="index" class="gap-card" shadow="hover">
      <div class="gap-header">
        <span class="skill-name">{{ gap.competency_name }}</span>
        <el-tag size="small" effect="light">{{ gap.category }}</el-tag>
      </div>
      <div class="gap-comparison">
        <div class="gap-label">目标岗位真实要求：</div>
        <div class="gap-desc">{{ gap.original_context }}</div>
      </div>
      <div class="action-advice">
        <div class="advice-label">AI 行动建议：</div>
        <div class="advice-content">{{ gap.actionable_advice }}</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import type { SkillGap } from '../types'

defineProps<{
  skillGaps: SkillGap[]
}>()
</script>

<style scoped>
.action-section {
  margin-top: 24px;
}

.section-title {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
  border-left: 3px solid #303133;
  padding-left: 8px;
}

.gap-card {
  margin-bottom: 16px;
  border-radius: 8px;
}

.gap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.skill-name {
  font-weight: bold;
  font-size: 14px;
  color: #303133;
}

.gap-comparison {
  background: #f4f4f5;
  padding: 10px;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  margin-bottom: 12px;
}

.gap-label {
  font-weight: bold;
  margin-bottom: 4px;
  color: #909399;
}

.action-advice {
  background: #fdf6ec;
  padding: 12px;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.6;
  border: 1px solid #faecd8;
}

.advice-label {
  font-weight: bold;
  color: #e6a23c;
  margin-bottom: 6px;
}

.advice-content {
  color: #606266;
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
