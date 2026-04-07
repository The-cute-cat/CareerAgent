<template>
  <div class="custom-job-node" :class="nodeClassList">
    <div class="node-icon">
      <el-icon :size="20">
        <OfficeBuilding v-if="isStart" />
        <TopRight v-else-if="nodeData.pathType === 'vertical'" />
        <Right v-else />
      </el-icon>
    </div>
    <div class="node-content">
      <div class="node-title" :title="nodeData.label">{{ nodeData.label }}</div>
      <div class="node-id">{{ nodeData.id }}</div>
    </div>
    <div class="node-badge">
      <el-tag v-if="isStart" size="small" type="primary" effect="light">起点</el-tag>
      <el-tag
        v-else
        size="small"
        effect="light"
        :type="nodeData.pathType === 'vertical' ? 'warning' : 'success'"
      >
        {{ nodeData.pathType === 'vertical' ? '晋升' : '转岗' }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue'
import { OfficeBuilding, TopRight, Right } from '@element-plus/icons-vue'

interface NodeData {
  id?: string
  label?: string
  isStart?: boolean
  pathType?: 'vertical' | 'lateral'
}

interface X6NodeInstance {
  getData: () => NodeData
}

const getNode = inject<() => X6NodeInstance | undefined>('getNode')
const nodeData = ref<NodeData>({})
const isStart = ref(false)

const nodeClassList = computed(() => ({
  'is-start': isStart.value,
  'is-vertical': !isStart.value && nodeData.value.pathType === 'vertical',
  'is-lateral': !isStart.value && nodeData.value.pathType === 'lateral',
}))

onMounted(() => {
  const node = getNode?.()
  if (!node) return

  nodeData.value = node.getData() || {}
  isStart.value = nodeData.value.isStart === true
})
</script>

<style scoped>
.custom-job-node {
  width: 100%;
  height: 100%;
  background: #ffffff;
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
  padding: 10px 12px;
  overflow: hidden;
}

.custom-job-node.is-start {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #f5f7fa 100%);
  box-shadow: 0 4px 14px rgba(64, 158, 255, 0.18);
}

.custom-job-node.is-vertical {
  border-color: #e6a23c;
  background: linear-gradient(135deg, #fff8eb 0%, #fdfcfa 100%);
}

.custom-job-node.is-lateral {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9eb 0%, #fafcfa 100%);
}

.custom-job-node:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transform: translateY(-1px) scale(1.01);
}

.node-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #606266;
}

.is-start .node-icon {
  background: #409eff;
  color: #ffffff;
}

.is-vertical .node-icon {
  background: #fdf6ec;
  color: #e6a23c;
}

.is-lateral .node-icon {
  background: #f0f9eb;
  color: #67c23a;
}

.node-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.node-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-id {
  font-size: 10px;
  color: #909399;
  font-family: 'SF Mono', Monaco, monospace;
}

.node-badge {
  flex-shrink: 0;
}

.node-badge :deep(.el-tag) {
  border-radius: 4px;
  font-size: 11px;
  padding: 0 6px;
  height: 20px;
  line-height: 18px;
}
</style>
