<template>
  <div class="knowledge-tree-node" :style="{ '--level': props.level }">
    <div class="node-row">
      <button
        v-if="hasChildren"
        type="button"
        class="toggle-btn"
        :aria-label="expanded ? '收起子节点' : '展开子节点'"
        @click="expanded = !expanded"
      >
        <el-icon>
          <ArrowDown v-if="expanded" />
          <ArrowRight v-else />
        </el-icon>
      </button>
      <span v-else class="toggle-placeholder"></span>

      <button
        type="button"
        class="node-card"
        :class="{
          active: props.activeId === props.node.id,
          completed: props.node.status === 'completed',
          current: props.node.status === 'current',
        }"
        @click="emit('select', props.node)"
      >
        <div class="node-card__header">
          <div class="node-title-group">
            <span class="node-title">{{ props.node.label }}</span>
            <span class="node-summary">{{ props.node.summary }}</span>
          </div>
          <span class="status-badge" :class="props.node.status">
            {{ statusLabelMap[props.node.status] }}
          </span>
        </div>

        <div class="node-meta">
          <span>{{ props.node.difficulty }}</span>
          <span>{{ props.node.duration }}</span>
          <span>{{ props.node.resources.length }} 个资源</span>
        </div>

        <div v-if="props.node.tags.length" class="node-tags">
          <span v-for="tag in props.node.tags.slice(0, 4)" :key="tag" class="tag-chip">
            {{ tag }}
          </span>
        </div>
      </button>
    </div>

    <div v-if="hasChildren && expanded" class="children">
      <TreeNode
        v-for="child in props.node.children"
        :key="child.id"
        :node="child"
        :level="props.level + 1"
        :active-id="props.activeId"
        @select="emit('select', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowDown, ArrowRight } from '@element-plus/icons-vue'

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
    level?: number
    activeId?: string
  }>(),
  {
    level: 0,
    activeId: '',
  },
)

const emit = defineEmits<{
  select: [node: KnowledgeTreeNode]
}>()

const expanded = ref(props.level < 1)
const hasChildren = computed(() => props.node.children.length > 0)

const statusLabelMap: Record<KnowledgeTreeNode['status'], string> = {
  completed: '已掌握',
  current: '进行中',
  planned: '待学习',
}
</script>

<style scoped lang="scss">
.knowledge-tree-node {
  --line-color: rgba(148, 163, 184, 0.28);
  position: relative;
  padding-left: calc(var(--level) * 18px);
}

.knowledge-tree-node::before {
  content: '';
  position: absolute;
  left: calc(var(--level) * 18px + 10px);
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--line-color);
}

.node-row {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 14px;
}

.node-row::before {
  content: '';
  position: absolute;
  left: 10px;
  top: 18px;
  width: 14px;
  height: 1px;
  background: var(--line-color);
}

.toggle-btn,
.toggle-placeholder {
  position: relative;
  z-index: 1;
  flex: 0 0 22px;
  width: 22px;
  height: 22px;
  margin-top: 8px;
}

.toggle-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(191, 219, 254, 0.9);
  border-radius: 999px;
  background: #fff;
  color: #2563eb;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.toggle-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.14);
}

.node-card {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 16px 18px;
  text-align: left;
  border: 1px solid rgba(219, 231, 245, 0.94);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(245, 249, 255, 0.96));
  box-shadow: 0 16px 36px rgba(28, 74, 126, 0.06);
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.node-card:hover {
  transform: translateY(-2px);
  border-color: rgba(96, 165, 250, 0.5);
  box-shadow: 0 20px 44px rgba(37, 99, 235, 0.1);
}

.node-card.active {
  border-color: rgba(37, 99, 235, 0.55);
  box-shadow: 0 22px 50px rgba(37, 99, 235, 0.16);
  background: linear-gradient(180deg, rgba(239, 246, 255, 0.98), rgba(255, 255, 255, 0.98));
}

.node-card.completed {
  border-left: 4px solid #22c55e;
}

.node-card.current {
  border-left: 4px solid #f59e0b;
}

.node-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.node-title-group {
  min-width: 0;
}

.node-title {
  display: block;
  color: #16324f;
  font-size: 16px;
  font-weight: 800;
}

.node-summary {
  display: block;
  margin-top: 4px;
  color: #6b7f94;
  font-size: 13px;
  line-height: 1.6;
}

.status-badge {
  flex-shrink: 0;
  min-width: 68px;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  text-align: center;
}

.status-badge.completed {
  background: rgba(34, 197, 94, 0.12);
  color: #15803d;
}

.status-badge.current {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.status-badge.planned {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.node-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  margin-top: 12px;
  color: #72879c;
  font-size: 12px;
  font-weight: 600;
}

.node-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.tag-chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(226, 232, 240, 0.7);
  color: #47627f;
  font-size: 12px;
  font-weight: 600;
}

.children {
  margin-left: 12px;
}

@media (max-width: 768px) {
  .knowledge-tree-node {
    padding-left: calc(var(--level) * 10px);
  }

  .knowledge-tree-node::before {
    left: calc(var(--level) * 10px + 10px);
  }

  .node-card__header {
    flex-direction: column;
  }
}
</style>
