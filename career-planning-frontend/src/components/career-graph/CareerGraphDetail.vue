<template>
  <div class="career-graph-detail">
    <div class="detail-hero">
      <div>
        <p class="detail-kicker">Insight Panel</p>
        <h3>岗位 / 路径详情</h3>
        <p class="detail-subtitle">点击左侧节点或路径后，这里会同步展示关键说明与成长建议。</p>
      </div>
      <div class="detail-badge">
        <span>{{ detailBadge }}</span>
      </div>
    </div>

    <el-empty
      v-if="detailState.type === 'empty'"
      class="detail-empty"
      description="请点击左侧节点或路径查看详情"
    >
      <template #image>
        <div class="empty-illustration">
          <span class="empty-ring empty-ring--outer" />
          <span class="empty-ring empty-ring--inner" />
          <span class="empty-core">Graph</span>
        </div>
      </template>
    </el-empty>

    <template v-else-if="detailState.type === 'node'">
      <el-card shadow="never" class="detail-card detail-card--node">
        <template #header>
          <div class="card-header">
            <div>
              <p class="card-kicker">Career Node</p>
              <h4>{{ detailState.data.name }}</h4>
            </div>
            <el-tag
              round
              effect="dark"
              :type="detailState.data.isCurrent ? 'primary' : 'success'"
            >
              {{ detailState.data.level }}
            </el-tag>
          </div>
        </template>

        <div class="overview-strip">
          <div class="overview-item">
            <span>岗位类型</span>
            <strong>{{ detailState.data.type }}</strong>
          </div>
          <div class="overview-item">
            <span>薪资范围</span>
            <strong>{{ detailState.data.salaryRange }}</strong>
          </div>
          <div class="overview-item">
            <span>经验要求</span>
            <strong>{{ detailState.data.experience }}</strong>
          </div>
        </div>

        <el-descriptions :column="1" border class="detail-descriptions">
          <el-descriptions-item label="岗位层级">
            {{ detailState.data.level }}
          </el-descriptions-item>
          <el-descriptions-item label="学历要求">
            {{ detailState.data.education }}
          </el-descriptions-item>
          <el-descriptions-item label="岗位说明">
            {{ detailState.data.description }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card shadow="never" class="detail-card">
        <template #header>
          <div class="section-header">
            <span>核心技能</span>
            <el-tag type="info" round>{{ detailState.data.skills.length }} 项</el-tag>
          </div>
        </template>
        <div class="tag-list">
          <el-tag
            v-for="skill in detailState.data.skills"
            :key="skill"
            round
            effect="plain"
            type="primary"
          >
            {{ skill }}
          </el-tag>
        </div>
      </el-card>

      <el-card shadow="never" class="detail-card">
        <template #header>
          <div class="section-header">
            <span>岗位标签</span>
            <el-tag type="success" round>{{ detailState.data.tags.length }} 个</el-tag>
          </div>
        </template>
        <div class="tag-list">
          <el-tag
            v-for="tag in detailState.data.tags"
            :key="tag"
            round
            effect="light"
            type="success"
          >
            {{ tag }}
          </el-tag>
        </div>
      </el-card>

      <el-card shadow="never" class="detail-card">
        <template #header>
          <div class="section-header">
            <span>推荐学习方向</span>
            <el-tag type="warning" round>{{ detailState.data.recommendedLearning.length }} 条</el-tag>
          </div>
        </template>
        <ul class="learning-list">
          <li v-for="item in detailState.data.recommendedLearning" :key="item">
            {{ item }}
          </li>
        </ul>
      </el-card>
    </template>

    <template v-else>
      <el-card shadow="never" class="detail-card detail-card--edge">
        <template #header>
          <div class="card-header">
            <div>
              <p class="card-kicker">Career Path</p>
              <h4>{{ detailState.sourceNode?.name || detailState.data.source }} → {{ detailState.targetNode?.name || detailState.data.target }}</h4>
            </div>
            <el-tag
              round
              effect="dark"
              :type="detailState.data.relationType === 'promotion' ? 'primary' : 'warning'"
            >
              {{ detailState.data.relationType === 'promotion' ? '晋升路径' : '转岗路径' }}
            </el-tag>
          </div>
        </template>

        <div class="path-meta-grid">
          <div class="meta-card">
            <span>转换难度</span>
            <strong>{{ detailState.data.difficulty }}</strong>
          </div>
          <div class="meta-card">
            <span>预计周期</span>
            <strong>{{ detailState.data.duration }}</strong>
          </div>
          <div class="meta-card">
            <span>起点岗位</span>
            <strong>{{ detailState.sourceNode?.name || detailState.data.source }}</strong>
          </div>
          <div class="meta-card">
            <span>终点岗位</span>
            <strong>{{ detailState.targetNode?.name || detailState.data.target }}</strong>
          </div>
        </div>

        <div class="explain-block">
          <span class="block-title">转换说明</span>
          <p>{{ detailState.data.description }}</p>
        </div>
      </el-card>

      <el-card shadow="never" class="detail-card">
        <template #header>
          <div class="section-header">
            <span>需要补充的技能</span>
            <el-tag type="danger" round>{{ detailState.data.requiredSkills.length }} 项</el-tag>
          </div>
        </template>
        <div class="tag-list">
          <el-tag
            v-for="skill in detailState.data.requiredSkills"
            :key="skill"
            round
            effect="plain"
            type="danger"
          >
            {{ skill }}
          </el-tag>
        </div>
      </el-card>

      <el-card shadow="never" class="detail-card">
        <template #header>
          <div class="section-header">
            <span>建议学习内容</span>
            <el-tag type="primary" round>{{ detailState.data.suggestedLearning.length }} 条</el-tag>
          </div>
        </template>
        <ul class="learning-list">
          <li v-for="item in detailState.data.suggestedLearning" :key="item">
            {{ item }}
          </li>
        </ul>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DetailState } from './careerGraph.types'

const props = defineProps<{
  detailState: DetailState
}>()

const detailBadge = computed(() => {
  if (props.detailState.type === 'node') {
    return '岗位详情'
  }

  if (props.detailState.type === 'edge') {
    return '路径详情'
  }

  return '等待选择'
})
</script>

<style scoped lang="scss">
.career-graph-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  min-height: 0;
}

.detail-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px;
  border-radius: 22px;
  background:
    radial-gradient(circle at top right, rgba(99, 102, 241, 0.16), transparent 35%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(245, 248, 255, 0.94));
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.detail-kicker,
.card-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6366f1;
  font-weight: 700;
}

.detail-hero h3,
.card-header h4 {
  margin: 0;
  color: #0f172a;
}

.detail-subtitle {
  margin: 10px 0 0;
  color: #64748b;
  line-height: 1.7;
  font-size: 14px;
}

.detail-badge {
  flex-shrink: 0;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(79, 70, 229, 0.1);
  color: #4338ca;
  font-size: 13px;
  font-weight: 700;
}

.detail-empty {
  padding: 30px 10px 10px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px dashed rgba(99, 102, 241, 0.22);
}

.empty-illustration {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(99, 102, 241, 0.25);
  animation: pulse-ring 4s ease-in-out infinite;
}

.empty-ring--outer {
  width: 150px;
  height: 150px;
}

.empty-ring--inner {
  width: 94px;
  height: 94px;
  animation-delay: -1.5s;
}

.empty-core {
  width: 68px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  background: linear-gradient(135deg, #4f46e5, #06b6d4);
  color: #fff;
  font-weight: 700;
  box-shadow: 0 16px 30px rgba(79, 70, 229, 0.24);
}

.detail-card {
  border: none;
  border-radius: 22px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.07);

  :deep(.el-card__header) {
    border-bottom: 1px solid rgba(148, 163, 184, 0.14);
    padding: 18px 22px;
  }

  :deep(.el-card__body) {
    padding: 22px;
  }
}

.detail-card--node {
  background:
    radial-gradient(circle at top right, rgba(56, 189, 248, 0.12), transparent 40%),
    rgba(255, 255, 255, 0.96);
}

.detail-card--edge {
  background:
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.12), transparent 40%),
    rgba(255, 255, 255, 0.96);
}

.card-header,
.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.overview-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.overview-item,
.meta-card {
  padding: 14px 16px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.overview-item span,
.meta-card span,
.block-title {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
}

.overview-item strong,
.meta-card strong {
  color: #0f172a;
  font-size: 15px;
}

.detail-descriptions {
  :deep(.el-descriptions__label) {
    width: 110px;
  }
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.learning-list {
  display: grid;
  gap: 12px;
  margin: 0;
  padding-left: 18px;
  color: #334155;
  line-height: 1.7;
}

.path-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.explain-block {
  margin-top: 18px;
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, #fffaf0 0%, #ffffff 100%);
  border: 1px solid rgba(245, 158, 11, 0.16);
}

.explain-block p {
  margin: 0;
  color: #475569;
  line-height: 1.8;
}

@keyframes pulse-ring {
  0%,
  100% {
    transform: scale(0.96);
    opacity: 0.6;
  }

  50% {
    transform: scale(1.04);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .detail-hero {
    padding: 20px;
  }

  .overview-strip,
  .path-meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
