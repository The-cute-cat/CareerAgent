<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, nextTick } from 'vue'
import { Graph } from '@antv/x6'
import { ElMessage } from 'element-plus'
import {
  User,
  OfficeBuilding,
  TrendCharts,
  Star,
  Warning,
  Check,
  ArrowRight,
  Close,
  Download
} from '@element-plus/icons-vue'

// 容器引用
const graphContainer = ref<HTMLDivElement | null>(null)
let graph: Graph | null = null

// 当前选中节点详情
const selectedNode = ref<any>(null)

// 用户数据
const userData = {
  name: '李明',
  school: 'XX 大学 (985/211)',
  position: 'Java 后端开发工程师',
  matchRate: 88,
  skills: [
    { name: 'Java 基础', value: 85 },
    { name: '框架应用', value: 80 },
    { name: '数据库', value: 85 },
    { name: '算法逻辑', value: 90 },
    { name: '沟通协作', value: 75 }
  ],
  advantages: '985 院校背景，GPA 前 5%，GitHub 活跃 (1000+ commits)，算法基础扎实',
  improvements: '缺乏高并发生产环境经验，大型分布式系统实战较少'
}

// 职业发展阶段数据
const careerStages = [
  { stage: '入职 0-1 年', level: '初级工程师', score: 60, ability: '基础夯实期' },
  { stage: '入职 1-3 年', level: '中级工程师', score: 75, ability: '快速成长期' },
  { stage: '入职 3-5 年', level: '高级工程师', score: 90, ability: '核心骨干期' },
  { stage: '入职 5 年+', level: '技术专家/总监', score: 95, ability: '专家深耕期' }
]

// 进度条颜色配置
const progressColors = [
  { color: '#409eff', percentage: 0 },
  { color: '#67c23a', percentage: 100 }
]

// 初始化图谱
const initGraph = () => {
  if (!graphContainer.value) return

  const container = graphContainer.value
  const width = container.clientWidth || 800
  const height = container.clientHeight || 580

  graph = new Graph({
    container: container,
    width: width,
    height: height,
    background: { color: 'transparent' },
    grid: {
      visible: true,
      type: 'dot',
      args: { color: 'rgba(0,0,0,0.05)', thickness: 1 }
    },
    panning: true,
    mousewheel: { enabled: true, minScale: 0.5, maxScale: 1.5 },
    connecting: {
      snap: true,
      allowBlank: false,
      allowLoop: false
    },
    interacting: {
      nodeMovable: true
    }
  })

  graph.on('node:click', ({ node }) => {
    const data = node.getData()
    const label = node.attr('label/text') || ''
    selectedNode.value = { label, ...data }
  })

  loadVerticalPath()
}

// 加载垂直路径
const loadVerticalPath = () => {
  if (!graph) return
  graph.clearCells()
  selectedNode.value = null

  const nodes = [
    { id: '1', label: '初级工程师', x: 400, y: 40, data: { status: '已达成', desc: '基础夯实期', salary: '8-15K', requirements: ['Java 基础', 'Spring Boot'] }, color: '#ecf5ff', stroke: '#409eff' },
    { id: '2', label: '中级工程师', x: 400, y: 160, data: { status: '进行中', desc: '快速成长期', salary: '15-25K', requirements: ['微服务', '性能优化'] }, color: '#f0f9eb', stroke: '#67c23a' },
    { id: '3', label: '高级工程师', x: 400, y: 280, data: { status: '目标', desc: '核心骨干期', salary: '25-40K', requirements: ['系统架构', '技术选型'] }, color: '#fdf6ec', stroke: '#e6a23c' },
    { id: '4', label: '技术专家', x: 250, y: 420, data: { status: '长远目标', desc: '领域深耕', salary: '40-60K', requirements: ['源码钻研', '影响力'] }, color: '#fef0f0', stroke: '#f56c6c' },
    { id: '5', label: '技术总监', x: 550, y: 420, data: { status: '管理路线', desc: '团队领导', salary: '60-100K', requirements: ['团队管理', '战略规划'] }, color: '#f5f7fa', stroke: '#909399' }
  ]

  nodes.forEach(node => {
    graph?.addNode({
      id: node.id,
      x: node.x - 80,
      y: node.y,
      width: 160,
      height: 64,
      label: node.label,
      data: node.data,
      attrs: {
        body: { fill: node.color, stroke: node.stroke, strokeWidth: 2, rx: 12, ry: 12 },
        label: { fill: '#303133', fontSize: 14, fontWeight: 'bold' }
      }
    })
  })

  const edges = [
    { source: '1', target: '2', label: '提升' },
    { source: '2', target: '3', label: '突破' },
    { source: '3', target: '4', label: '技术型' },
    { source: '3', target: '5', label: '管理型' }
  ]

  edges.forEach(edge => {
    graph?.addEdge({
      source: edge.source,
      target: edge.target,
      label: edge.label,
      attrs: {
        line: { stroke: '#bdc3c7', strokeWidth: 2, targetMarker: 'classic' },
        label: { fill: '#909399', fontSize: 11 }
      }
    })
  })

  graph.centerContent()
  ElMessage.success('已恢复职业发展路径图')
}

// 加载横向换岗路径
const loadTransferPath = () => {
  if (!graph) return
  graph.clearCells()
  selectedNode.value = null

  const nodes = [
    { id: 'java', label: 'Java 后端', x: 400, y: 100, color: '#ecf5ff', stroke: '#409eff' },
    { id: 'fullstack', label: '全栈工程师', x: 200, y: 220, color: '#f0f9eb', stroke: '#67c23a' },
    { id: 'bigdata', label: '大数据开发', x: 600, y: 220, color: '#fdf6ec', stroke: '#e6a23c' },
    { id: 'architect', label: '系统架构师', x: 400, y: 340, color: '#f5f7fa', stroke: '#909399' }
  ]

  nodes.forEach(node => {
    graph?.addNode({
      id: node.id,
      x: node.x - 75,
      y: node.y,
      width: 150,
      height: 60,
      label: node.label,
      attrs: {
        body: { fill: node.color, stroke: node.stroke, strokeWidth: 2, rx: 10, ry: 10 },
        label: { fill: '#303133', fontSize: 13, fontWeight: 'bold' }
      }
    })
  })

  const edges = [
    { source: 'java', target: 'fullstack', label: '广度' },
    { source: 'java', target: 'bigdata', label: '转型' },
    { source: 'java', target: 'architect', label: '深度' }
  ]

  edges.forEach(edge => {
    graph?.addEdge({
      source: edge.source,
      target: edge.target,
      label: edge.label,
      attrs: {
        line: { stroke: '#909399', strokeWidth: 2, strokeDasharray: '5 5' }
      }
    })
  })

  graph.centerContent()
}

const resetGraph = () => loadVerticalPath()
const exportImage = () => {
  graph?.toPNG((dataUri: string) => {
    const link = document.createElement('a')
    link.href = dataUri
    link.download = '职业路径图.png'
    link.click()
  })
}

onMounted(() => {
  nextTick(() => {
    requestAnimationFrame(() => {
      initGraph()
    })
  })
})

onBeforeUnmount(() => {
  graph?.dispose()
})
</script>

<template>
  <div class="development-map-container">
    <!-- 顶部标题区 -->
    <div class="page-header premium-glass">
      <div class="header-left">
        <div class="icon-box">
          <el-icon :size="24"><TrendCharts /></el-icon>
        </div>
        <div class="title-text">
          <h2>发现成长路径</h2>
          <p>基于 AI 的职业演进模拟与能力图谱</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button-group>
          <el-button type="primary" @click="loadVerticalPath">垂直晋升路线</el-button>
          <el-button type="success" @click="loadTransferPath">横向转岗路线</el-button>
        </el-button-group>
        <el-button :icon="Download" @click="exportImage">导出影像</el-button>
        <el-button type="warning" plain @click="resetGraph">重置图谱</el-button>
      </div>
    </div>

    <div class="layout-body">
      <!-- 左侧：战力面板 -->
      <div class="sidebar-panel">
        <el-card class="user-profile-card premium-glass" shadow="never">
          <div class="user-header">
            <el-avatar :size="56" :icon="User" class="main-avatar" />
            <div class="name-info">
              <h3>{{ userData.name }}</h3>
              <p>{{ userData.school }}</p>
            </div>
          </div>
          <div class="match-info">
            <div class="match-label">
              <span>当前岗位匹配度</span>
              <strong>{{ userData.matchRate }}%</strong>
            </div>
            <el-progress :percentage="userData.matchRate" :stroke-width="12" stroke-linecap="round" />
          </div>
        </el-card>

        <el-card class="skills-radar-card premium-glass" shadow="never">
          <template #header>
            <div class="card-title"><el-icon><Star /></el-icon>能力指纹</div>
          </template>
          <div class="skill-bars">
            <div v-for="skill in userData.skills" :key="skill.name" class="skill-item">
              <div class="skill-info">
                <span>{{ skill.name }}</span>
                <strong>{{ skill.value }}</strong>
              </div>
              <div class="bar-bg">
                <div class="bar-fill" :style="{ width: skill.value + '%' }"></div>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="timeline-stages-card premium-glass" shadow="never">
          <template #header>
            <div class="card-title"><el-icon><TrendCharts /></el-icon>进阶里程碑</div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(stage, index) in careerStages"
              :key="index"
              :type="index <= 1 ? 'primary' : 'info'"
              :hollow="index > 1"
              :timestamp="stage.stage"
            >
              <h4 :style="{ color: index <= 1 ? '#409eff' : '#909399' }">{{ stage.level }}</h4>
              <p class="stage-tag">{{ stage.ability }}</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </div>

      <!-- 右侧：图谱区 -->
      <div class="graph-main">
        <div class="graph-canvas-wrapper premium-glass">
          <div ref="graphContainer" class="graph-container"></div>
          
          <!-- 悬浮说明 -->
          <div class="canvas-tips">
            <el-icon><Warning /></el-icon> 滚轮缩放，按住画布可自由平移
          </div>
        </div>

        <!-- 节点详情弹窗 -->
        <transition name="el-zoom-in-top">
          <div v-if="selectedNode" class="node-overlay premium-glass">
            <div class="overlay-header">
              <h3>{{ selectedNode.label }}</h3>
              <el-icon class="close-btn" @click="selectedNode = null"><Close /></el-icon>
            </div>
            <div class="overlay-body">
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="发展阶段">{{ selectedNode.desc }}</el-descriptions-item>
                <el-descriptions-item label="薪资范畴">
                  <span class="salary-text">{{ selectedNode.salary }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="核心要求">
                  <div class="req-tags">
                    <el-tag v-for="req in selectedNode.requirements" :key="req" size="small" effect="plain">{{ req }}</el-tag>
                  </div>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.development-map-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  min-height: calc(100vh - 100px);
  background: transparent;
}

/* 玻璃拟态基础 */
.premium-glass {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5) !important;
  border-radius: 20px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.04) !important;
}

/* 页眉 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon-box {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #409eff 0%, #1677ff 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 8px 16px rgba(64, 158, 255, 0.3);
}

.title-text h2 { margin: 0; font-size: 22px; font-weight: 800; color: #1e293b; }
.title-text p { margin: 4px 0 0; color: #64748b; font-size: 14px; }

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

/* 布局体 */
.layout-body {
  display: flex;
  gap: 24px;
  flex: 1;
}

/* 侧边栏面板 */
.sidebar-panel {
  width: 340px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-profile-card .user-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.main-avatar {
  background: linear-gradient(135deg, #409eff 0%, #a5d8ff 100%);
}

.name-info h3 { margin: 0; font-size: 18px; color: #1e293b; }
.name-info p { margin: 4px 0 0; font-size: 13px; color: #94a3b8; }

.match-info .match-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  color: #1e293b;
}

.skill-bars {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.skill-item .skill-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}

.bar-bg {
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff 0%, #3b82f6 100%);
  border-radius: 4px;
}

.stage-tag { font-size: 12px; color: #94a3b8; margin: 4px 0 0; }

/* 图谱主区 */
.graph-main {
  flex: 1;
  position: relative;
}

.graph-canvas-wrapper {
  height: 100%;
  min-height: 600px;
  position: relative;
  overflow: hidden;
}

.graph-container {
  width: 100%;
  height: 100%;
}

.canvas-tips {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 10;
}

/* 详情弹窗 */
.node-overlay {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 280px;
  z-index: 100;
  padding: 0;
  overflow: hidden;
}

.overlay-header {
  padding: 16px 20px;
  background: linear-gradient(135deg, #409eff 0%, #1677ff 100%);
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overlay-header h3 { margin: 0; font-size: 16px; }
.close-btn { cursor: pointer; transition: transform 0.2s; }
.close-btn:hover { transform: scale(1.2); }

.overlay-body { padding: 20px; }
.salary-text { color: #f56c6c; font-weight: 800; font-size: 18px; }
.req-tags { display: flex; flex-wrap: wrap; gap: 6px; }

/* 响应式 */
@media (max-width: 1200px) {
  .layout-body { flex-direction: column; }
  .sidebar-panel { width: 100%; }
}
</style>
