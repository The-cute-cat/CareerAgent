<template>
  <div class="tree-node" :class="{ 'tree-node--root': depth === 0 }">
    <div class="tree-node__branch">
      <div class="tree-node__self">
        <button
          type="button"
          class="tree-node__label"
          :class="{
            active: activeId === node.id,
            opened: expanded,
            'is-root': depth === 0,
          }"
          @click="emit('select', node)"
        >
          <span class="tree-node__text">{{ node.label }}</span>
          <span class="tree-node__action">
            <el-icon
              v-if="hasChildren"
              class="tree-node__icon"
              :class="{ 'tree-node__icon--opened': expanded }"
            >
              <ArrowDownBold />
            </el-icon>
            <el-icon v-else class="tree-node__icon tree-node__icon--leaf">
              <ArrowRightBold />
            </el-icon>
          </span>
        </button>

        <button
          v-if="hasChildren"
          type="button"
          class="tree-node__toggle"
          :aria-label="expanded ? '收起下一级内容' : '展开下一级内容'"
          @click.stop="expanded = !expanded"
        />
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

const expanded = ref(true)
const hasChildren = computed(() => props.node.children.length > 0)
</script>

<style scoped lang="scss">
.tree-node {
  position: relative;
}

.tree-node__branch {
  display: flex;
  align-items: center;
  gap: 86px;
  min-height: 96px;
}

.tree-node__self {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
}

.tree-node__label {
  min-width: 200px;
  max-width: 274px;
  padding: 13px 18px;
  border-radius: 17px;
  border: 1px solid #e5e7eb;
  background: #ececec;
  color: #3f3f46;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.35;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  box-shadow: none;
}

.tree-node__label:hover {
  background: #e7e7e7;
  border-color: #d4d4d8;
}

.tree-node__label.active {
  background: #e7e7e7;
  border-color: #d4d4d8;
  color: #27272a;
}

.tree-node__label.opened {
  background: #e8e8e8;
}

.tree-node__label.is-root {
  min-width: 258px;
  max-width: 330px;
  padding: 15px 18px;
  border: 4px solid #0f4ab8;
  background: #ececec;
  color: #1f2937;
  font-size: 18px;
  font-weight: 700;
  border-radius: 17px;
}

.tree-node__text {
  display: inline-block;
}

.tree-node__action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #71717a;
}

.tree-node__icon {
  font-size: 12px;
  transition: transform 0.2s ease;
}

.tree-node__icon--opened {
  transform: rotate(0deg);
}

.tree-node__icon--leaf {
  font-size: 11px;
}

.tree-node__toggle {
  position: absolute;
  inset: 0;
  opacity: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
}

.tree-node__children {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 30px;
  padding-left: 94px;
}

.tree-node__children > :deep(.tree-node) {
  position: relative;
}

.tree-node__children > :deep(.tree-node)::before {
  content: '';
  position: absolute;
  left: -94px;
  top: 50%;
  width: 94px;
  height: 2px;
  border-top: 2px solid #a1a1aa;
  border-top-left-radius: 999px;
  border-bottom-left-radius: 999px;
  transform: translateY(-50%);
  opacity: 0.92;
}

.tree-node__children > :deep(.tree-node)::after {
  content: '';
  position: absolute;
  left: -94px;
  top: 0;
  bottom: 50%;
  width: 94px;
  border-left: 2px solid #a1a1aa;
  border-bottom: 2px solid #a1a1aa;
  border-bottom-left-radius: 52px;
  opacity: 0.92;
}

.tree-node__children > :deep(.tree-node:first-child)::after {
  top: 50%;
  bottom: auto;
  height: 0;
  border-left: 2px solid #a1a1aa;
  border-top: 2px solid #a1a1aa;
  border-bottom: none;
  border-top-left-radius: 52px;
}

.tree-node__children > :deep(.tree-node:only-child)::after {
  display: none;
}

.tree-node__children > :deep(.tree-node:last-child)::after {
  bottom: 50%;
}

@media (max-width: 1024px) {
  .tree-node__branch {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
    min-height: auto;
  }

  .tree-node__children {
    padding-left: 18px;
    gap: 14px;
  }

  .tree-node__children > :deep(.tree-node)::before,
  .tree-node__children > :deep(.tree-node)::after {
    display: none;
  }

  .tree-node__label {
    min-width: 180px;
    max-width: 240px;
  }

  .tree-node__label.is-root {
    min-width: 220px;
    max-width: 280px;
    font-size: 16px;
  }
}
</style>
