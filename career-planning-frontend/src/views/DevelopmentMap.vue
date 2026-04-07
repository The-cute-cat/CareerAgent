<template>
  <div class="career-map-wrapper">
    <MapToolbar
      :layout="currentLayout"
      @change="changeLayout"
      @reset="resetViewport"
    />

    <div ref="graphContainer" class="graph-canvas"></div>

    <PathDetailDrawer
      v-model="drawerVisible"
      :mode="drawerMode"
      :path-data="currentPathData"
      :step="currentStep"
      :node-data="currentNodeData"
      :related-paths="relatedPaths"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import { Graph } from '@antv/x6'
import { register } from '@antv/x6-vue-shape'
import { AntVDagreLayout, ForceLayout } from '@antv/layout'
import { Graph as LayoutGraph } from '@antv/graphlib'

import MapToolbar from '@/components/DevelopMap_Component/MapToolbar.vue'
import PathDetailDrawer from '@/components/DevelopMap_Component/PathDetailDrawer.vue'
import JobNode from '@/components/DevelopMap_Component/JobNode.vue'

import type {
  LayoutType,
  PathType,
  CareerPath,
  PathStep,
  CareerMapData,
  ApiResponse,
  NodeDetailData,
  X6Node,
  X6Edge,
} from '@/components/DevelopMap_Component/types'

const props = defineProps<{
  lateralResponse?: ApiResponse | null
  verticalResponse?: ApiResponse | null
}>()

// 常量定义
const NODE_WIDTH = 180
const NODE_HEIGHT = 88

// 注册自定义节点
register({
  shape: 'custom-vue-node',
  width: NODE_WIDTH,
  height: NODE_HEIGHT,
  component: JobNode,
})

// 响应式状态
const graphContainer = ref<HTMLElement | null>(null)
const graph = shallowRef<Graph | null>(null)
const drawerVisible = ref(false)
const currentPathData = ref<CareerPath | null>(null)
const currentStep = ref<PathStep | null>(null)
const currentNodeData = ref<NodeDetailData | null>(null)
const drawerMode = ref<'edge' | 'node'>('edge')
const currentLayout = ref<LayoutType>('force')

// 默认模拟数据
const defaultLateralResponse: ApiResponse = {
  code: 200,
  state: true,
  msg: 'Success',
  data: {
    start_job_id: 'job_002',
    start_job_name: '前端开发工程师',
    paths: [
      {
        path_id: 'path_001',
        path_type: 'lateral',
        path_title: '前端→Node后端：全栈能力跃迁路线',
        total_steps: 1,
        total_routing_cost: 0.35,
        steps: [
          {
            step_index: 1,
            from_job_id: 'job_002',
            from_job_name: '前端开发工程师',
            to_job_id: 'job_105',
            to_job_name: 'Node后端工程师',
            jaccard_high: 0.6,
            cos_low: 0.8,
            salary_gain: 0,
            transition_reason: '该路径具有较低演化阻力，前端工程师在 JS 生态、工程化和协作方式上与 Node 后端存在显著迁移基础。',
            skill_gaps: [
              {
                competency_name: 'Redis',
                category: '核心专业技能',
                target_score: 3,
                original_context: '熟练使用Redis进行高并发缓存设计',
                actionable_advice: '搭建 Node + Redis 微服务项目，补齐缓存设计与穿透防护经验。',
              },
            ],
          },
        ],
        overall_summary: '低风险横向演进路线，适合希望向全栈方向拓展的前端工程师。',
      },
      {
        path_id: 'path_002',
        path_type: 'lateral',
        path_title: '前端→技术产品经理：需求翻译者成长路线',
        total_steps: 1,
        total_routing_cost: 0.75,
        steps: [
          {
            step_index: 1,
            from_job_id: 'job_002',
            from_job_name: '前端开发工程师',
            to_job_id: 'job_201',
            to_job_name: '技术产品经理',
            jaccard_high: 0.2,
            cos_low: 0.85,
            salary_gain: 0,
            transition_reason: '前端工程师对用户交互和需求落地理解较深，适合转向技术产品经理。',
            skill_gaps: [
              {
                competency_name: 'Axure/PRD编写',
                category: '工具与平台能力',
                target_score: 4,
                original_context: '熟练输出高质量PRD文档及高保真原型',
                actionable_advice: '围绕熟悉的前端项目补全 PRD、流程图和原型。',
              },
            ],
          },
        ],
        overall_summary: '中风险跨职能转岗路线，关键在于产品交付工具链与需求抽象能力。',
      },
    ],
  },
}

const defaultVerticalResponse: ApiResponse = {
  code: 200,
  state: true,
  msg: 'Success',
  data: {
    start_job_id: 'job_002',
    start_job_name: '前端开发工程师',
    paths: [
      {
        path_id: 'path_101',
        path_type: 'vertical',
        path_title: '前端架构跃迁路线：从开发工程师到资深架构师',
        total_steps: 1,
        total_routing_cost: 0.15,
        steps: [
          {
            step_index: 1,
            from_job_id: 'job_002',
            from_job_name: '前端开发工程师',
            to_job_id: 'job_003',
            to_job_name: '资深前端架构师',
            jaccard_high: 0.85,
            cos_low: 0.9,
            salary_gain: 0.5,
            transition_reason: '高技能重合度与高软素质契合度，且薪资增益显著，是极优的垂直晋升通道。',
            skill_gaps: [
              {
                competency_name: '前端微服务架构',
                category: '核心专业技能',
                target_score: 3,
                original_context: '主导过前端微服务(Qiankun)拆分与落地',
                actionable_advice: '独立主导一个微前端拆分落地项目，并输出完整技术方案。',
              },
            ],
          },
        ],
        overall_summary: '纯垂直晋升链，强调工程决策能力与系统抽象能力。',
      },
    ],
  },
}

// 计算属性
const mergedData = computed<CareerMapData>(() => {
  const lateral = props.lateralResponse?.data ?? defaultLateralResponse.data
  const vertical = props.verticalResponse?.data ?? defaultVerticalResponse.data
  return {
    start_job_id: lateral.start_job_id || vertical.start_job_id,
    start_job_name: lateral.start_job_name || vertical.start_job_name,
    paths: [...(lateral.paths || []), ...(vertical.paths || [])],
  }
})

const relatedPaths = computed(() => {
  if (!currentNodeData.value) return []
  const nodeId = currentNodeData.value.id
  return mergedData.value.paths.filter((path) =>
    path.steps.some((step) => step.from_job_id === nodeId || step.to_job_id === nodeId),
  )
})

// 数据转换
function transformDataForX6(data: CareerMapData, layout: LayoutType) {
  const nodesMap = new Map<string, X6Node>()
  const edges: X6Edge[] = []
  const targetType: PathType = layout === 'dagre' ? 'vertical' : 'lateral'
  const filteredPaths = data.paths.filter((path) => path.path_type === targetType)

  nodesMap.set(data.start_job_id, {
    id: data.start_job_id,
    shape: 'custom-vue-node',
    width: NODE_WIDTH,
    height: NODE_HEIGHT,
    data: { id: data.start_job_id, label: data.start_job_name, isStart: true },
  })

  filteredPaths.forEach((path) => {
    path.steps.forEach((step) => {
      if (!nodesMap.has(step.from_job_id)) {
        nodesMap.set(step.from_job_id, {
          id: step.from_job_id,
          shape: 'custom-vue-node',
          width: NODE_WIDTH,
          height: NODE_HEIGHT,
          data: {
            id: step.from_job_id,
            label: step.from_job_name,
            isStart: step.from_job_id === data.start_job_id,
            pathType: path.path_type,
          },
        })
      }

      if (!nodesMap.has(step.to_job_id)) {
        nodesMap.set(step.to_job_id, {
          id: step.to_job_id,
          shape: 'custom-vue-node',
          width: NODE_WIDTH,
          height: NODE_HEIGHT,
          data: {
            id: step.to_job_id,
            label: step.to_job_name,
            isStart: false,
            pathType: path.path_type,
          },
        })
      }

      edges.push({
        source: step.from_job_id,
        target: step.to_job_id,
        shape: 'edge',
        labels: [
          {
            attrs: {
              text: {
                text: `${path.path_type === 'vertical' ? '晋升' : '转岗'}阻力: ${path.total_routing_cost}`,
                fill: '#909399',
                fontSize: 12,
              },
            },
          },
        ],
        attrs: {
          line: {
            stroke: path.path_type === 'vertical' ? '#e6a23c' : '#67c23a',
            strokeWidth: 2,
            strokeDasharray: path.path_type === 'vertical' ? undefined : '5 5',
            targetMarker: { name: 'classic', size: 8 },
          },
        },
        data: { path, step },
      })
    })
  })

  return { nodes: Array.from(nodesMap.values()), edges }
}

function createLayoutGraph(_layoutType: LayoutType, graphData: { nodes: X6Node[]; edges: X6Edge[] }) {
  return new LayoutGraph({
    nodes: graphData.nodes.map((node) => ({
      id: node.id,
      data: {
        ...node.data,
        width: NODE_WIDTH,
        height: NODE_HEIGHT,
        size: [NODE_WIDTH, NODE_HEIGHT],
      },
    })),
    edges: graphData.edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      data: {},
    })),
  })
}

async function executeLayout(type: LayoutType) {
  if (!graph.value) return

  // 一次性转换数据，避免重复计算
  const rawGraphData = transformDataForX6(mergedData.value, type)
  const layoutGraph = createLayoutGraph(type, rawGraphData)

  const mapping =
    type === 'dagre'
      ? await new AntVDagreLayout({
          rankdir: 'TB',
          nodesep: 60,
          ranksep: 120,
          nodeSize: [NODE_WIDTH, NODE_HEIGHT],
        }).execute(layoutGraph as never)
      : await new ForceLayout({
          preventOverlap: true,
          nodeSize: Math.max(NODE_WIDTH, NODE_HEIGHT),
          linkDistance: 230,
          nodeSpacing: 50,
          maxIteration: 200,
        }).execute(layoutGraph as never)

  const positionedNodes = rawGraphData.nodes.map((node) => {
    const layoutNode = mapping.nodes.find((item) => item.id === node.id)
    return {
      ...node,
      x: layoutNode?.data.x ?? node.x ?? 0,
      y: layoutNode?.data.y ?? node.y ?? 0,
    }
  })

  graph.value.fromJSON({
    nodes: positionedNodes,
    edges: rawGraphData.edges,
  })
  graph.value.centerContent()
}

// 事件处理
function changeLayout(value: unknown) {
  const layoutType = value as LayoutType
  if (layoutType !== 'force' && layoutType !== 'dagre') {
    console.warn('Invalid layout type:', value)
    return
  }
  currentLayout.value = layoutType
  void executeLayout(layoutType)
}

function resetViewport() {
  graph.value?.centerContent()
  graph.value?.zoomToFit({ maxScale: 1 })
}

// 生命周期
onMounted(() => {
  if (!graphContainer.value) return

  graph.value = new Graph({
    container: graphContainer.value,
    autoResize: true,
    panning: true,
    mousewheel: {
      enabled: true,
      zoomAtMousePosition: true,
      modifiers: ['ctrl', 'meta'],
      minScale: 0.4,
      maxScale: 2,
    },
    interacting: { nodeMovable: true },
    background: { color: '#f5f7fa' },
  })

  void executeLayout(currentLayout.value)

  graph.value.on('edge:click', ({ edge }) => {
    graph.value?.getEdges().forEach((e) => e.attr('line/strokeWidth', 2))
    edge.attr('line/strokeWidth', 4)

    const edgeData = edge.getData<{ path: CareerPath; step: PathStep }>()
    currentPathData.value = edgeData.path
    currentStep.value = edgeData.step
    currentNodeData.value = null
    drawerMode.value = 'edge'
    drawerVisible.value = true
  })

  graph.value.on('node:click', ({ node }) => {
    currentNodeData.value = node.getData<NodeDetailData>()
    currentPathData.value = null
    currentStep.value = null
    drawerMode.value = 'node'
    drawerVisible.value = true
  })
})

onBeforeUnmount(() => {
  graph.value?.dispose()
})
</script>

<style scoped>
.career-map-wrapper {
  width: 100%;
  height: 100vh;
  position: relative;
  background: #f5f7fa;
}

.graph-canvas {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.graph-canvas:active {
  cursor: grabbing;
}
</style>
