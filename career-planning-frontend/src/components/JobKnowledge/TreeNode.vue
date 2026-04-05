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
            [node.status]: true,
          }"
          @click="emit('select', node)"
        >
          <span class="status-dot" :class="node.status"></span>
          <span class="tree-node__text">{{ node.label }}</span>
          <span v-if="node.difficulty" class="difficulty-tag" :class="getDifficultyClass(node.difficulty)">
            {{ node.difficulty }}
          </span>
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

function getDifficultyClass(difficulty: string): string {
  const map: Record<string, string> = {
    '基础': 'easy',
    '进阶': 'medium',
    '高级': 'hard',
  }
  return map[difficulty] || 'medium'
}
</script>

<style scoped lang="scss">
.tree-node {
  position: relative;
}

.tree-node__branch {
  display: flex;
  align-items: center;
  gap: 20px;
  min-height: 70px;
}

.tree-node__self {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.tree-node__label {
  min-width: 200px;
  max-width: 260px;
  padding: 8px 16px 8px 36px;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #1e293b;
  font-size: 14px;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);

  .status-dot {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 8px;
    height: 8px;
    border-radius: 50%;
    transition: all 0.2s;

    &.completed {
      background: #10b981;
      box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }

    &.current {
      background: #3b82f6;
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
      animation: pulse 1.5s infinite;
    }

    &.planned {
      background: #94a3b8;
    }
  }

  .difficulty-tag {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 30px;
    background: #f1f5f9;
    color: #475569;

    &.easy {
      background: #dcfce7;
      color: #15803d;
    }

    &.medium {
      background: #fef9c3;
      color: #854d0e;
    }

    &.hard {
      background: #fee2e2;
      color: #b91c1c;
    }
  }

  &:hover {
    transform: translateY(-1px);
    border-color: #93c5fd;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.12);
  }

  &.active {
    border-color: #2563eb;
    background: #eff6ff;
    color: #1e40af;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.15);

    .status-dot {
      transform: translateY(-50%) scale(1.2);
    }
  }

  &.opened {
    background: #f8fafc;
  }
}

.tree-node__toggle {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 10px;
  background: #f8fafc;
  color: #64748b;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;

  &:hover {
    color: #2563eb;
    background: #eff6ff;
    border-color: #bfdbfe;
  }
}

.tree-node__children {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-left: 32px;
  margin-top: 8px;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 24px;
    bottom: 24px;
    width: 2px;
    background: linear-gradient(to bottom, #cbd5e1, #e2e8f0);
    border-radius: 2px;
  }
}

.tree-node__children > :deep(.tree-node) {
  position: relative;

  &::before {
    content: '';
    position: absolute;
    left: -32px;
    top: 35px;
    width: 32px;
    height: 2px;
    background: linear-gradient(90deg, #cbd5e1, #e2e8f0);
    border-radius: 2px;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(59, 130, 246, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
  }
}

@media (max-width: 1024px) {
  .tree-node__branch {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
    min-height: auto;
  }

  .tree-node__children {
    padding-left: 20px;

    &::before,
    > :deep(.tree-node)::before {
      display: none;
    }
  }

  .tree-node__label {
    min-width: 180px;
    max-width: 240px;
  }
}
</style>