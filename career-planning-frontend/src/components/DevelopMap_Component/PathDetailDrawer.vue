<template>
  <el-drawer v-model="visible" :title="title" size="460px" destroy-on-close>
    <div class="drawer-container">
      <!-- 边详情：路径信息 -->
      <template v-if="mode === 'edge' && step && pathData">
        <PathMetricsPanel :path-data="pathData" :step="step" />
        <PathAIInsight :path-data="pathData" :step="step" />
        <SkillGapsList :skill-gaps="step.skill_gaps || []" />
      </template>

      <!-- 节点详情 -->
      <template v-else-if="mode === 'node' && nodeData">
        <NodeDetailPanel :node-data="nodeData" :related-paths="relatedPaths" />
      </template>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import PathMetricsPanel from './PathMetricsPanel.vue'
import PathAIInsight from './PathAIInsight.vue'
import SkillGapsList from './SkillGapsList.vue'
import NodeDetailPanel from './NodeDetailPanel.vue'
import type { CareerPath, PathStep, NodeDetailData } from '../types'

const props = defineProps<{
  modelValue: boolean
  mode: 'edge' | 'node'
  pathData?: CareerPath | null
  step?: PathStep | null
  nodeData?: NodeDetailData | null
  relatedPaths?: CareerPath[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const title = computed(() => {
  if (props.mode === 'edge' && props.pathData) {
    return props.pathData.path_title
  }
  if (props.mode === 'node' && props.nodeData) {
    return props.nodeData.label
  }
  return '详情'
})
</script>

<style scoped>
.drawer-container {
  padding: 0 10px 20px;
}
</style>
