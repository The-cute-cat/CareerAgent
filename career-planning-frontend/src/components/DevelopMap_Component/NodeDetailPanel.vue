<template>
  <div class="node-panel fade-in-up">
    <div class="node-main-title">{{ nodeData.label }}</div>
    <div class="node-tags">
      <el-tag v-if="nodeData.isStart" type="primary">当前起点</el-tag>
      <el-tag v-else :type="nodeData.pathType === 'vertical' ? 'warning' : 'success'">
        {{ nodeData.pathType === 'vertical' ? '垂直晋升节点' : '横向换岗节点' }}
      </el-tag>
      <el-tag type="info">ID: {{ nodeData.id }}</el-tag>
    </div>
  </div>

  <div class="action-section fade-in-up" style="animation-delay: 0.1s;">
    <h4 class="section-title">与该岗位相关的路径</h4>
    <el-empty v-if="!relatedPaths.length" description="暂无关联路径" />
    <el-card v-for="path in relatedPaths" :key="path.path_id" class="related-path-card" shadow="hover">
      <div class="gap-header">
        <span class="skill-name">{{ path.path_title }}</span>
        <el-tag size="small" :type="path.path_type === 'vertical' ? 'warning' : 'success'">
          {{ path.path_type === 'vertical' ? '垂直晋升' : '横向换岗' }}
        </el-tag>
      </div>
      <p class="summary-text">{{ path.overall_summary }}</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import type { NodeDetailData, CareerPath } from '../types'

defineProps<{
  nodeData: NodeDetailData
  relatedPaths: CareerPath[]
}>()
</script>

<style scoped>
.node-panel {
  margin-bottom: 20px;
}

.node-main-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
}

.node-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

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

.related-path-card {
  margin-bottom: 12px;
  border-radius: 8px;
}

.gap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.skill-name {
  font-weight: bold;
  font-size: 14px;
  color: #303133;
}

.summary-text {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  margin: 0;
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
