<template>
  <div class="toolbar">
    <div class="toolbar-top">
      <el-radio-group :model-value="layout" @change="$emit('change', $event)" size="small">
        <el-radio-button label="force">横向换岗图谱</el-radio-button>
        <el-radio-button label="dagre">垂直晋升图谱</el-radio-button>
      </el-radio-group>
      <el-button size="small" @click="$emit('reset')">重置视图</el-button>
    </div>
    <div class="toolbar-desc">
      <span class="legend-item"><i class="dot lateral"></i> 横向换岗</span>
      <span class="legend-item"><i class="dot vertical"></i> 垂直晋升</span>
      <span class="legend-item"><i class="dot start"></i> 当前起点</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  layout: 'force' | 'dagre'
}>()

defineEmits<{
  change: [layout: 'force' | 'dagre']
  reset: []
}>()
</script>

<style scoped>
.toolbar {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.toolbar-top {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.toolbar-desc {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #606266;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.dot.lateral {
  background: #67c23a;
}

.dot.vertical {
  background: #e6a23c;
}

.dot.start {
  background: #409eff;
}
</style>
