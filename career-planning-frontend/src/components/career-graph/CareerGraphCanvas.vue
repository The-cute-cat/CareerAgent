<template>
  <div ref="wrapperRef" class="career-graph-canvas">
    <div ref="graphRef" class="graph-surface" />

    <transition name="tooltip-fade">
      <div
        v-if="tooltip.visible"
        class="graph-tooltip"
        :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
      >
        {{ tooltip.content }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { Graph } from '@antv/x6'
import type {
  CareerEdge,
  CareerGraphData,
  CareerGraphMode,
  CareerNode,
} from './careerGraph.types'

const props = defineProps<{
  mode: CareerGraphMode
  graphData: CareerGraphData
}>()

const emit = defineEmits<{
  (event: 'node-click', node: CareerNode): void
  (event: 'edge-click', payload: { edge: CareerEdge; sourceNode?: CareerNode; targetNode?: CareerNode }): void
  (event: 'blank-click'): void
  (event: 'scale-change', scale: number): void
}>()

const wrapperRef = ref<HTMLDivElement | null>(null)
const graphRef = ref<HTMLDivElement | null>(null)

const tooltip = reactive({
  visible: false,
  x: 0,
  y: 0,
  content: '',
})

let graphInstance: Graph | null = null
let resizeObserver: ResizeObserver | null = null
let isNodeRegistered = false

let selectedNodeId: string | null = null
let selectedEdgeId: string | null = null
let hoveredNodeId: string | null = null
let hoveredEdgeId: string | null = null

const NODE_SHAPE = 'career-card-node'

function ensureNodeRegistered() {
  if (isNodeRegistered) {
    return
  }

  Graph.registerNode(
    NODE_SHAPE,
    {
      inherit: 'html',
      width: 280,
      height: 136,
      html(cell: unknown) {
        const raw = (cell as { getData: () => { node: CareerNode } }).getData()
        return createNodeCard(raw.node)
      },
    },
    true,
  )

  isNodeRegistered = true
}

function resolveCategoryColor(category: string) {
  const colorMap: Record<string, string> = {
    frontend: '#4f46e5',
    architecture: '#8b5cf6',
    management: '#14b8a6',
    backend: '#0ea5e9',
    fullstack: '#22c55e',
    qa: '#f59e0b',
    mobile: '#06b6d4',
    visualization: '#7c3aed',
    lowcode: '#ec4899',
  }

  return colorMap[category] ?? '#4f46e5'
}

function createTagMarkup(tags: string[]) {
  return tags
    .slice(0, 3)
    .map((tag) => `<span class="career-node-chip">${tag}</span>`)
    .join('')
}

function createNodeCard(node: CareerNode) {
  const root = document.createElement('div')
  const accent = node.highlightColor ?? resolveCategoryColor(node.category)

  root.className = 'career-node-card'
  root.dataset.nodeId = node.id
  root.style.setProperty('--node-accent', accent)
  root.title = `${node.name}｜${node.level}`

  root.innerHTML = `
    <div class="career-node-card__halo"></div>
    <div class="career-node-card__header">
      <div>
        <div class="career-node-card__name">${node.name}</div>
        <div class="career-node-card__meta">${node.level} · ${node.type}</div>
      </div>
      <div class="career-node-card__badge">${node.category}</div>
    </div>
    <div class="career-node-card__content">${node.description}</div>
    <div class="career-node-card__chips">${createTagMarkup(node.tags)}</div>
  `

  return root
}

function edgeStyle(edge: CareerEdge, status: 'default' | 'hover' | 'selected') {
  const isPromotion = edge.relationType === 'promotion'

  if (status === 'selected') {
    return {
      stroke: isPromotion ? '#4f46e5' : '#f59e0b',
      strokeWidth: 3.2,
      dasharray: isPromotion ? '' : '8 6',
      opacity: 1,
    }
  }

  if (status === 'hover') {
    return {
      stroke: isPromotion ? '#2563eb' : '#ea580c',
      strokeWidth: 2.8,
      dasharray: isPromotion ? '' : '8 6',
      opacity: 1,
    }
  }

  return {
    stroke: isPromotion ? '#60a5fa' : '#22c55e',
    strokeWidth: 2.2,
    dasharray: isPromotion ? '' : '8 6',
    opacity: 0.9,
  }
}

function labelStyle(selected: boolean) {
  return {
    fill: selected ? '#ffffff' : '#475569',
    fontSize: 12,
    fontWeight: 600,
  }
}

function syncNodeCardStates() {
  if (!graphInstance || !wrapperRef.value) {
    return
  }

  const cards = wrapperRef.value.querySelectorAll<HTMLElement>('.career-node-card')
  cards.forEach((card) => {
    const nodeId = card.dataset.nodeId ?? ''
    const node = props.graphData.nodes.find((item) => item.id === nodeId)
    card.classList.toggle('is-current', Boolean(node?.isCurrent))
    card.classList.toggle('is-selected', nodeId === selectedNodeId)
    card.classList.toggle('is-hovered', nodeId === hoveredNodeId)
  })
}

function syncEdgeStates() {
  if (!graphInstance) {
    return
  }

  graphInstance.getEdges().forEach((edgeCell) => {
    const edge = edgeCell.getData<CareerEdge>()
    const currentState =
      edge.id === selectedEdgeId ? 'selected' : edge.id === hoveredEdgeId ? 'hover' : 'default'
    const style = edgeStyle(edge, currentState)
    const isSelected = edge.id === selectedEdgeId

    edgeCell.attr({
      line: {
        stroke: style.stroke,
        strokeWidth: style.strokeWidth,
        strokeDasharray: style.dasharray,
        opacity: style.opacity,
        targetMarker: {
          name: 'block',
          width: isSelected ? 10 : 8,
          height: isSelected ? 14 : 12,
        },
      },
    })

    edgeCell.setLabels([
      {
        attrs: {
          body: {
            fill: isSelected ? style.stroke : '#ffffff',
            stroke: isSelected ? style.stroke : 'rgba(148, 163, 184, 0.45)',
            strokeWidth: 1,
            rx: 12,
            ry: 12,
          },
          label: {
            text: edge.relationType === 'promotion' ? '晋升' : '转岗',
            ...labelStyle(isSelected),
          },
        },
        position: 0.5,
      },
    ])
  })
}

function refreshVisualState() {
  nextTick(() => {
    syncNodeCardStates()
    syncEdgeStates()
  })
}

function showTooltip(event: MouseEvent, content: string) {
  if (!wrapperRef.value) {
    return
  }

  const rect = wrapperRef.value.getBoundingClientRect()
  tooltip.visible = true
  tooltip.content = content
  tooltip.x = event.clientX - rect.left + 14
  tooltip.y = event.clientY - rect.top + 14
}

function hideTooltip() {
  tooltip.visible = false
}

function updateScale() {
  if (!graphInstance) {
    return
  }

  emit('scale-change', Number((graphInstance.zoom() * 100).toFixed(0)))
}

function buildNodeCell(node: CareerNode) {
  return {
    id: node.id,
    shape: NODE_SHAPE,
    x: node.x,
    y: node.y,
    width: 280,
    height: 136,
    data: {
      node,
    },
  }
}

function buildEdgeCell(edge: CareerEdge) {
  const style = edgeStyle(edge, 'default')

  return {
    id: edge.id,
    shape: 'edge',
    source: edge.source,
    target: edge.target,
    zIndex: 0,
    data: edge,
    router:
      props.mode === 'promotion'
        ? {
            name: 'manhattan',
            args: {
              startDirections: ['bottom'],
              endDirections: ['top'],
              padding: 24,
            },
          }
        : {
            name: 'manhattan',
            args: {
              padding: 24,
            },
          },
    connector: {
      name: 'rounded',
      args: {
        radius: 14,
      },
    },
    attrs: {
      line: {
        stroke: style.stroke,
        strokeWidth: style.strokeWidth,
        strokeDasharray: style.dasharray,
        opacity: style.opacity,
        targetMarker: {
          name: 'block',
          width: 8,
          height: 12,
        },
      },
    },
    labels: [
      {
        attrs: {
          body: {
            fill: '#ffffff',
            stroke: 'rgba(148, 163, 184, 0.45)',
            strokeWidth: 1,
            rx: 12,
            ry: 12,
          },
          label: {
            text: edge.relationType === 'promotion' ? '晋升' : '转岗',
            ...labelStyle(false),
          },
        },
        position: 0.5,
      },
    ],
  }
}

function resolveNodeById(nodeId: string) {
  return props.graphData.nodes.find((item) => item.id === nodeId)
}

function selectNode(nodeId: string) {
  selectedNodeId = nodeId
  selectedEdgeId = null
  refreshVisualState()

  const targetNode = resolveNodeById(nodeId)
  if (targetNode) {
    emit('node-click', targetNode)
  }
}

function selectEdge(edgeId: string) {
  const edge = props.graphData.edges.find((item) => item.id === edgeId)
  if (!edge) {
    return
  }

  selectedEdgeId = edgeId
  selectedNodeId = null
  refreshVisualState()

  emit('edge-click', {
    edge,
    sourceNode: resolveNodeById(edge.source),
    targetNode: resolveNodeById(edge.target),
  })
}

function clearSelection() {
  selectedNodeId = null
  selectedEdgeId = null
  refreshVisualState()
  emit('blank-click')
}

function renderGraph() {
  if (!graphInstance) {
    return
  }

  selectedNodeId = null
  selectedEdgeId = null
  hoveredNodeId = null
  hoveredEdgeId = null
  hideTooltip()

  const nodeCells = props.graphData.nodes.map(buildNodeCell)
  const edgeCells = props.graphData.edges.map(buildEdgeCell)

  graphInstance.fromJSON({
    nodes: nodeCells,
    edges: edgeCells,
  })

  window.requestAnimationFrame(() => {
    graphInstance?.fitToContent({
      padding: 70,
      allowNewOrigin: 'any',
    })
    graphInstance?.centerContent()
    updateScale()
    refreshVisualState()
  })
}

function bindEvents() {
  if (!graphInstance) {
    return
  }

  graphInstance.on('node:click', ({ node }) => {
    selectNode(node.id)
  })

  graphInstance.on('edge:click', ({ edge }) => {
    selectEdge(edge.id)
  })

  graphInstance.on('blank:click', () => {
    clearSelection()
  })

  graphInstance.on('node:mouseenter', ({ e, node }) => {
    hoveredNodeId = node.id
    refreshVisualState()
    const data = node.getData<{ node: CareerNode }>()
    showTooltip(e as unknown as MouseEvent, `${data.node.name}｜${data.node.level}`)
  })

  graphInstance.on('node:mousemove', ({ e, node }) => {
    const data = node.getData<{ node: CareerNode }>()
    showTooltip(e as unknown as MouseEvent, `${data.node.name}｜${data.node.level}`)
  })

  graphInstance.on('node:mouseleave', () => {
    hoveredNodeId = null
    refreshVisualState()
    hideTooltip()
  })

  graphInstance.on('edge:mouseenter', ({ e, edge }) => {
    hoveredEdgeId = edge.id
    refreshVisualState()
    const data = edge.getData<CareerEdge>()
    showTooltip(e as unknown as MouseEvent, data.description)
  })

  graphInstance.on('edge:mousemove', ({ e, edge }) => {
    const data = edge.getData<CareerEdge>()
    showTooltip(e as unknown as MouseEvent, data.description)
  })

  graphInstance.on('edge:mouseleave', () => {
    hoveredEdgeId = null
    refreshVisualState()
    hideTooltip()
  })

  graphInstance.on('scale', () => {
    updateScale()
  })
}

function initializeGraph() {
  if (!graphRef.value) {
    return
  }

  ensureNodeRegistered()

  graphInstance = new Graph({
    container: graphRef.value,
    autoResize: false,
    background: {
      color: '#f8fbff',
    },
    grid: {
      visible: true,
      type: 'doubleMesh',
      args: [
        {
          color: 'rgba(99, 102, 241, 0.06)',
          thickness: 1,
        },
        {
          color: 'rgba(14, 165, 233, 0.04)',
          thickness: 1,
          factor: 5,
        },
      ],
    },
    panning: {
      enabled: true,
    },
    mousewheel: {
      enabled: true,
      factor: 1.08,
      minScale: 0.55,
      maxScale: 1.8,
    },
    interacting: {
      nodeMovable: false,
      edgeMovable: false,
      magnetConnectable: false,
      vertexMovable: false,
    },
    connecting: {
      allowBlank: false,
      allowLoop: false,
      allowNode: false,
      allowEdge: false,
      allowMulti: false,
    },
  })

  bindEvents()
  renderGraph()

  if (wrapperRef.value) {
    resizeObserver = new ResizeObserver(() => {
      graphInstance?.resize(wrapperRef.value?.clientWidth ?? 0, wrapperRef.value?.clientHeight ?? 0)
      graphInstance?.centerContent()
    })
    resizeObserver.observe(wrapperRef.value)
  }
}

function zoomIn() {
  graphInstance?.zoom(0.12)
  updateScale()
}

function zoomOut() {
  graphInstance?.zoom(-0.12)
  updateScale()
}

function resetView() {
  if (!graphInstance) {
    return
  }

  graphInstance.zoomTo(1)
  graphInstance.fitToContent({
    padding: 70,
    allowNewOrigin: 'any',
  })
  graphInstance.centerContent()
  updateScale()
}

function centerView() {
  graphInstance?.centerContent()
}

defineExpose({
  zoomIn,
  zoomOut,
  resetView,
  centerView,
})

watch(
  () => props.graphData,
  () => {
    renderGraph()
  },
  { deep: true },
)

onMounted(() => {
  initializeGraph()
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  graphInstance?.dispose()
  graphInstance = null
})
</script>

<style scoped lang="scss">
.career-graph-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 620px;
  overflow: hidden;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(79, 70, 229, 0.08), transparent 30%),
    radial-gradient(circle at bottom left, rgba(6, 182, 212, 0.08), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 249, 255, 0.98));
}

.graph-surface {
  width: 100%;
  height: 100%;
}

.graph-tooltip {
  position: absolute;
  z-index: 20;
  max-width: 260px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.92);
  color: #fff;
  font-size: 12px;
  line-height: 1.6;
  pointer-events: none;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.28);
}

.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

:deep(.career-node-card) {
  position: relative;
  height: 100%;
  padding: 16px 18px;
  border-radius: 22px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(246, 249, 255, 0.95) 100%);
  box-shadow: 0 18px 34px rgba(15, 23, 42, 0.08);
  overflow: hidden;
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
  cursor: pointer;
}

:deep(.career-node-card__halo) {
  position: absolute;
  top: -26px;
  right: -18px;
  width: 92px;
  height: 92px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--node-accent) 24%, white) 0%, transparent 70%);
  opacity: 0.85;
  pointer-events: none;
}

:deep(.career-node-card__header) {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

:deep(.career-node-card__name) {
  color: #0f172a;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.35;
}

:deep(.career-node-card__meta) {
  margin-top: 6px;
  color: #64748b;
  font-size: 12px;
  letter-spacing: 0.02em;
}

:deep(.career-node-card__badge) {
  padding: 6px 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--node-accent) 12%, white);
  color: var(--node-accent);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

:deep(.career-node-card__content) {
  position: relative;
  margin-top: 14px;
  height: 40px;
  overflow: hidden;
  color: #475569;
  font-size: 12px;
  line-height: 1.7;
}

:deep(.career-node-card__chips) {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

:deep(.career-node-chip) {
  display: inline-flex;
  align-items: center;
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(241, 245, 249, 0.95);
  color: #334155;
  font-size: 11px;
  font-weight: 600;
}

:deep(.career-node-card.is-current) {
  border-color: color-mix(in srgb, var(--node-accent) 36%, white);
  box-shadow:
    0 22px 42px rgba(79, 70, 229, 0.16),
    0 0 0 1px color-mix(in srgb, var(--node-accent) 12%, white);
}

:deep(.career-node-card.is-current::after) {
  content: '当前岗位';
  position: absolute;
  top: 12px;
  right: 14px;
  padding: 4px 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--node-accent), #22d3ee);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

:deep(.career-node-card.is-hovered) {
  transform: translateY(-4px);
  border-color: color-mix(in srgb, var(--node-accent) 45%, white);
  box-shadow: 0 22px 42px rgba(15, 23, 42, 0.14);
}

:deep(.career-node-card.is-selected) {
  transform: translateY(-4px);
  border-color: var(--node-accent);
  box-shadow:
    0 22px 46px rgba(79, 70, 229, 0.18),
    0 0 0 2px color-mix(in srgb, var(--node-accent) 36%, white);
}

@media (max-width: 768px) {
  .career-graph-canvas {
    min-height: 520px;
  }
}
</style>
