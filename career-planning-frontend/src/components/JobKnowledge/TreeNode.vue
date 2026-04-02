<template>
  <div class="tree-node" :style="{ '--depth': String(depth) }">
    <div class="tree-node__branch">
      <div class="tree-node__self">
        <button
          type="button"
          class="tree-node__label"
          :class="{
            active: activeId === node.id,
            expandable: hasChildren,
            opened: expanded,
          }"
          @click="emit('select', node)"
        >
          <span class="tree-node__text">{{ node.label }}</span>
        </button>

        <button
          v-if="hasChildren"
          type="button"
          class="tree-node__toggle"
          :aria-label="expanded ? '收起下一级内容' : '展开下一级内容'"
          @click.stop="expanded = !expanded"
        >
          <el-icon>
            <ArrowDownBold v-if="expanded" />
            <ArrowRightBold v-else />
          </el-icon>
        </button>
      </div>

      <div v-if="hasChildren && expanded" class="tree-node__children">
        <TreeNode
          v-for="child in node.children"
          :key="child.id"
          :node="child"
          :depth="depth + 1"
          :active-id="activeId"
          @select="emit('select', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowDownBold, ArrowRightBold } from '@element-plus/icons-vue'

export interface KnowledgeTreeNode {
  id: string
  label: string
  summary: string
  description: string
  difficulty: string
  duration: string
  status: 'completed' | 'current' | 'planned'
  tags: string[]
  resources: string[]
  milestones: string[]
  children: KnowledgeTreeNode[]
}

const props = withDefaults(
  defineProps<{
    node: KnowledgeTreeNode
    depth?: number
    activeId?: string
  }>(),
  {
    depth: 0,
    activeId: '',
  },
)

const emit = defineEmits<{
  select: [node: KnowledgeTreeNode]
}>()

const expanded = ref(false)
const hasChildren = computed(() => props.node.children.length > 0)
</script>

<style scoped lang="scss">
.tree-node {
  position: relative;
}

.tree-node__branch {
  display: flex;
  align-items: center;
  gap: 28px;
  min-height: 86px;
}

.tree-node__self {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.tree-node__label {
  min-width: 190px;
  max-width: 240px;
  min-height: 46px;
  padding: 0 18px;
  border-radius: 14px;
  border: 1.5px solid rgba(212, 220, 230, 0.95);
  background: rgba(255, 255, 255, 0.96);
  color: #3b4655;
  font-size: 15px;
  font-weight: 700;
  text-align: left;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
  cursor: pointer;
  transition: all 0.22s ease;
}

.tree-node__label:hover {
  transform: translateY(-1px);
  border-color: rgba(37, 99, 235, 0.38);
  box-shadow: 0 12px 26px rgba(37, 99, 235, 0.12);
}

.tree-node__label.active {
  border-color: #2563eb;
  box-shadow: 0 14px 28px rgba(37, 99, 235, 0.18);
  color: #1849b8;
}

.tree-node__label.opened {
  background: rgba(244, 248, 255, 0.98);
}

.tree-node__text {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.tree-node__toggle {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 10px;
  background: rgba(241, 245, 249, 0.95);
  color: #6b7280;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: inset 0 0 0 1px rgba(203, 213, 225, 0.85);
}

.tree-node__toggle:hover {
  color: #2563eb;
  background: rgba(239, 246, 255, 1);
  box-shadow: inset 0 0 0 1px rgba(96, 165, 250, 0.5), 0 8px 20px rgba(37, 99, 235, 0.12);
}

.tree-node__children {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding-left: 26px;
}

.tree-node__children::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 26px;
  height: 1.5px;
  background: rgba(148, 163, 184, 0.9);
}

.tree-node__children::after {
  content: '';
  position: absolute;
  left: 0;
  top: 16px;
  bottom: 16px;
  width: 1.5px;
  background: rgba(148, 163, 184, 0.75);
}

.tree-node__children > :deep(.tree-node) {
  position: relative;
}

.tree-node__children > :deep(.tree-node)::before {
  content: '';
  position: absolute;
  left: -26px;
  top: 50%;
  width: 26px;
  height: 1.5px;
  background: rgba(148, 163, 184, 0.85);
}

@media (max-width: 1024px) {
  .tree-node__branch {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
    min-height: initial;
  }

  .tree-node__children {
    padding-left: 18px;
  }

  .tree-node__children::before,
  .tree-node__children::after,
  .tree-node__children > :deep(.tree-node)::before {
    display: none;
  }

  .tree-node__label {
    min-width: 168px;
    max-width: min(74vw, 230px);
  }
}
</style>
