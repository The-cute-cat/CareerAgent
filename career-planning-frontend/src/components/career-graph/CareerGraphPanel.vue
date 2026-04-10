<template>
  <section class="career-graph-panel">
    <div class="panel-layout">
      <div class="graph-column">
        <div class="toolbar-card">
          <div class="toolbar-main">
            <div>
              <p class="toolbar-kicker">Visualization Module</p>
              <h2>职业发展路径图谱</h2>
              <p class="toolbar-desc">
                从垂直晋升到横向转岗，直观呈现岗位成长路线、能力要求与阶段说明。
              </p>
            </div>

            <div class="toolbar-metrics">
              <div class="metric-pill">
                <span>节点</span>
                <strong>{{ currentGraphData.nodes.length }}</strong>
              </div>
              <div class="metric-pill">
                <span>路径</span>
                <strong>{{ currentGraphData.edges.length }}</strong>
              </div>
              <div class="metric-pill metric-pill--accent">
                <span>缩放</span>
                <strong>{{ scalePercent }}%</strong>
              </div>
            </div>
          </div>

          <div class="toolbar-actions">
            <el-radio-group v-model="activeMode" size="large" class="mode-switch">
              <el-radio-button label="promotion">垂直晋升图谱</el-radio-button>
              <el-radio-button label="transfer">横向换岗图谱</el-radio-button>
            </el-radio-group>

            <div class="action-buttons">
              <el-button circle :icon="ZoomOut" @click="canvasRef?.zoomOut()" />
              <el-button circle :icon="ZoomIn" @click="canvasRef?.zoomIn()" />
              <el-button :icon="RefreshRight" @click="canvasRef?.resetView()">重置</el-button>
              <el-button :icon="Aim" @click="canvasRef?.centerView()">居中</el-button>
            </div>
          </div>
        </div>

        <div class="graph-stage-card">
          <div class="stage-header">
            <div>
              <h3>{{ currentGraphData.title }}</h3>
              <p>{{ currentGraphData.subtitle }}</p>
            </div>
            <el-tag round effect="dark" type="primary">
              当前岗位：{{ currentNode?.name ?? '-' }}
            </el-tag>
          </div>

          <CareerGraphCanvas
            ref="canvasRef"
            :mode="activeMode"
            :graph-data="currentGraphData"
            @node-click="handleNodeClick"
            @edge-click="handleEdgeClick"
            @blank-click="resetDetail"
            @scale-change="handleScaleChange"
          />
        </div>
      </div>

      <aside class="detail-column">
        <CareerGraphDetail :detail-state="detailState" />
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { Aim, RefreshRight, ZoomIn, ZoomOut } from '@element-plus/icons-vue'
import CareerGraphCanvas from './CareerGraphCanvas.vue'
import CareerGraphDetail from './CareerGraphDetail.vue'
import { careerGraphDataMap, defaultGraphMode } from './careerGraph.mock'
import type {
  CareerEdge,
  CareerGraphMode,
  CareerNode,
  DetailState,
} from './careerGraph.types'

const activeMode = ref<CareerGraphMode>(defaultGraphMode)
const detailState = ref<DetailState>({ type: 'empty' })
const scalePercent = ref(100)
const canvasRef = ref<InstanceType<typeof CareerGraphCanvas> | null>(null)

const currentGraphData = computed(() => careerGraphDataMap[activeMode.value])

const currentNode = computed(() =>
  currentGraphData.value.nodes.find((item) => item.id === currentGraphData.value.currentNodeId),
)

function handleNodeClick(node: CareerNode) {
  detailState.value = {
    type: 'node',
    data: node,
  }
}

function handleEdgeClick(payload: { edge: CareerEdge; sourceNode?: CareerNode; targetNode?: CareerNode }) {
  detailState.value = {
    type: 'edge',
    data: payload.edge,
    sourceNode: payload.sourceNode,
    targetNode: payload.targetNode,
  }
}

function resetDetail() {
  detailState.value = { type: 'empty' }
}

function handleScaleChange(scale: number) {
  scalePercent.value = scale
}

watch(activeMode, async () => {
  resetDetail()
  scalePercent.value = 100
  await nextTick()
  canvasRef.value?.resetView()
})
</script>

<style scoped lang="scss">
.career-graph-panel {
  width: 100%;
  padding: 6px 0;
}

.panel-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(320px, 0.95fr);
  gap: 22px;
  align-items: stretch;
}

.graph-column,
.detail-column {
  min-width: 0;
}

.toolbar-card,
.graph-stage-card,
.detail-column {
  position: relative;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background:
    radial-gradient(circle at top right, rgba(79, 70, 229, 0.08), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(248, 250, 255, 0.95));
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
  overflow: hidden;
}

.toolbar-card {
  padding: 24px 24px 20px;
}

.toolbar-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
}

.toolbar-kicker {
  margin: 0 0 10px;
  color: #4f46e5;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.toolbar-main h2,
.stage-header h3 {
  margin: 0;
  color: #0f172a;
}

.toolbar-desc,
.stage-header p {
  margin: 10px 0 0;
  color: #64748b;
  font-size: 14px;
  line-height: 1.7;
}

.toolbar-metrics {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.metric-pill {
  min-width: 92px;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(241, 245, 249, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.metric-pill span {
  display: block;
  color: #64748b;
  font-size: 12px;
  margin-bottom: 6px;
}

.metric-pill strong {
  color: #0f172a;
  font-size: 18px;
}

.metric-pill--accent {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.12), rgba(6, 182, 212, 0.14));
}

.toolbar-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid rgba(148, 163, 184, 0.12);
}

.mode-switch {
  :deep(.el-radio-button__inner) {
    min-width: 148px;
    border-radius: 14px;
    font-weight: 600;
  }

  :deep(.el-radio-button:first-child .el-radio-button__inner) {
    border-radius: 14px 0 0 14px;
  }

  :deep(.el-radio-button:last-child .el-radio-button__inner) {
    border-radius: 0 14px 14px 0;
  }
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.graph-stage-card {
  margin-top: 18px;
  padding: 18px;
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 14px;
  padding: 4px 4px 0;
}

.detail-column {
  padding: 18px;
  min-height: 760px;
}

@media (max-width: 1280px) {
  .panel-layout {
    grid-template-columns: minmax(0, 1.55fr) minmax(300px, 0.9fr);
  }

  .toolbar-main,
  .toolbar-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-metrics {
    justify-content: flex-start;
  }
}

@media (max-width: 960px) {
  .panel-layout {
    grid-template-columns: 1fr;
  }

  .detail-column {
    min-height: auto;
  }
}

@media (max-width: 640px) {
  .toolbar-card,
  .graph-stage-card,
  .detail-column {
    border-radius: 20px;
  }

  .toolbar-card {
    padding: 20px 18px 18px;
  }

  .mode-switch {
    width: 100%;

    :deep(.el-radio-group) {
      width: 100%;
    }
  }

  .action-buttons {
    width: 100%;
  }

  .action-buttons :deep(.el-button) {
    flex: 1;
  }
}
</style>
