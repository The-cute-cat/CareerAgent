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
  Close
} from '@element-plus/icons-vue'
import {
  careerStages,
  verticalPathNodes,
  verticalPathEdges,
  transferPathNodes,
  transferPathEdges,
  progressColors
} from '@/mock/data'

// 容器引用
const graphContainer = ref<HTMLDivElement | null>(null)
let graph: Graph | null = null

// 当前选中节点详情
const selectedNode = ref<any>(null)

// 用户数据（来自 Report.vue）
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

// 初始化图谱
const initGraph = () => {
  if (!graphContainer.value) return

  // 确保容器有尺寸
  const container = graphContainer.value
  const width = container.clientWidth || container.offsetWidth || 800
  const height = 580

  graph = new Graph({
    container: container,
    width: width,
    height: height,
    background: { color: '#f8f9fa' },
    grid: {
      visible: true,
      type: 'dot',
      args: { color: '#e0e0e0', thickness: 1 }
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

  // 节点点击事件
  graph.on('node:click', ({ node }) => {
    const data = node.getData()
    const label = node.attr('label/text') || ''
    selectedNode.value = { label, ...data }
    ElMessage.success(`已选中：${label}`)
  })

  // 边点击事件
  graph.on('edge:click', ({ edge }) => {
    const label = edge.getLabelAt(0)?.attrs?.label?.text || '晋升路径'
    ElMessage.info(`路径：${label}`)
  })

  // 加载垂直路径
  loadVerticalPath()
}

// 加载垂直晋升路径（基于李明的 Java 后端职业路线）
const loadVerticalPath = () => {
  if (!graph) return

  graph.clearCells()
  selectedNode.value = null

  // 使用模拟数据中的节点
  verticalPathNodes.forEach(node => {
    graph?.addNode({
      id: node.id,
      x: node.x,
      y: node.y,
      width: 160,
      height: 70,
      label: node.label,
      data: node.data,
      attrs: {
        body: {
          fill: node.color,
          stroke: node.stroke,
          strokeWidth: 2,
          rx: 10,
          ry: 10
        },
        label: {
          fill: node.textColor || '#000',
          fontSize: 14,
          fontWeight: 'bold'
        }
      }
    })
  })

  // 使用模拟数据中的连线
  verticalPathEdges.forEach(edge => {
    graph?.addEdge({
      source: edge.source,
      target: edge.target,
      label: edge.label,
      attrs: {
        line: {
          stroke: edge.color,
          strokeWidth: 3,
          targetMarker: { name: 'block', width: 14, height: 10 }
        },
        label: {
          fill: edge.color,
          fontSize: 12,
          fontWeight: 'bold'
        }
      }
    })
  })

  // 居中显示
  graph.centerContent()
  ElMessage.success('已加载李明的 Java 后端晋升路径')
}

// 加载横向换岗路径（基于技能相关性）
const loadTransferPath = () => {
  if (!graph) return

  graph.clearCells()
  selectedNode.value = null

  // 使用模拟数据中的横向换岗路径节点
  transferPathNodes.forEach(node => {
    graph?.addNode({
      id: node.id,
      x: node.x,
      y: node.y,
      width: 150,
      height: 65,
      label: node.label,
      data: node.data,
      attrs: {
        body: {
          fill: node.color,
          stroke: node.stroke,
          strokeWidth: 2,
          rx: 8,
          ry: 8
        },
        label: {
          fill: node.textColor || '#fff',
          fontSize: 13,
          fontWeight: 'bold'
        }
      }
    })
  })

  // 使用模拟数据中的横向换岗路径连线
  transferPathEdges.forEach(edge => {
    graph?.addEdge({
      source: edge.source,
      target: edge.target,
      label: edge.label,
      attrs: {
        line: {
          stroke: '#999',
          strokeWidth: 2,
          strokeDasharray: '5 5',
          targetMarker: { name: 'classic', width: 10, height: 10 }
        },
        label: {
          fill: '#666',
          fontSize: 11
        }
      }
    })
  })

  graph.centerContent()
  ElMessage.success('已加载横向换岗路径图')
}

// 重置图谱
const resetGraph = () => {
  if (!graph) return
  graph.clearCells()
  selectedNode.value = null
  ElMessage.info('图谱已重置')
}

// 导出图片
const exportImage = () => {
  if (!graph) return
  graph.toPNG((dataUri: string) => {
    const link = document.createElement('a')
    link.href = dataUri
    link.download = '职业发展路径图.png'
    link.click()
  })
}

// 生命周期
onMounted(() => {
  // 使用 nextTick 确保 DOM 完全渲染后再初始化图谱
  nextTick(() => {
    // 延迟执行确保容器已布局完成
    requestAnimationFrame(() => {
      initGraph()
    })
  })
})

onBeforeUnmount(() => {
  if (graph) {
    graph.dispose()
    graph = null
  }
})
</script>

<template>
  <div class="development-map-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon :size="28" color="#1890FF"><TrendCharts /></el-icon>
        <div class="title-section">
          <h2>职业发展路径图谱</h2>
          <span class="subtitle">基于个人能力画像的智能职业规划</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="loadVerticalPath">
          <el-icon><TrendCharts /></el-icon>
          垂直晋升路径
        </el-button>
        <el-button type="success" @click="loadTransferPath">
          <el-icon><ArrowRight /></el-icon>
          横向换岗路径
        </el-button>
        <el-button @click="exportImage">
          <el-icon><Check /></el-icon>
          导出图片
        </el-button>
        <el-button type="warning" plain @click="resetGraph">重置</el-button>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧：用户信息面板 -->
      <div class="user-panel">
        <el-card class="user-card" shadow="hover">
          <div class="user-header">
            <el-avatar :size="60" :icon="User" class="user-avatar" />
            <div class="user-info">
              <h3>{{ userData.name }}</h3>
              <p class="school">{{ userData.school }}</p>
            </div>
          </div>

          <div class="position-info">
            <el-tag type="primary" effect="dark" size="large">
              <el-icon><OfficeBuilding /></el-icon>
              {{ userData.position }}
            </el-tag>
            <div class="match-rate">
              <span class="label">岗位匹配度</span>
              <el-progress
                :percentage="userData.matchRate"
                :color="progressColors"
                :stroke-width="10"
              />
            </div>
          </div>
        </el-card>

        <!-- 能力维度 -->
        <el-card class="skills-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Star /></el-icon>
              <span>能力维度评估</span>
            </div>
          </template>
          <div class="skill-list">
            <div v-for="skill in userData.skills" :key="skill.name" class="skill-item">
              <span class="skill-name">{{ skill.name }}</span>
              <div class="skill-bar-wrapper">
                <div class="skill-bar" :style="{ width: skill.value + '%' }"></div>
              </div>
              <span class="skill-value" :class="{ high: skill.value >= 85 }">{{ skill.value }}</span>
            </div>
          </div>
        </el-card>

        <!-- 优劣势分析 -->
        <el-card class="analysis-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Check /></el-icon>
              <span>核心优势</span>
            </div>
          </template>
          <p class="advantage-text">{{ userData.advantages }}</p>
        </el-card>

        <el-card class="analysis-card warning" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Warning /></el-icon>
              <span>待提升项</span>
            </div>
          </template>
          <p class="improve-text">{{ userData.improvements }}</p>
        </el-card>

        <!-- 职业发展阶段 -->
        <el-card class="stages-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>职业发展阶段</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(stage, index) in careerStages"
              :key="index"
              :type="index <= 1 ? 'primary' : index === 2 ? 'warning' : 'success'"
              :timestamp="stage.stage"
            >
              <div class="stage-content">
                <strong>{{ stage.level }}</strong>
                <p class="stage-ability">{{ stage.ability }}</p>
                <el-progress :percentage="stage.score" :show-text="true" :stroke-width="6" />
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </div>

      <!-- 中间：图谱区域 -->
      <div class="graph-section">
        <div ref="graphContainer" class="graph-container"></div>

        <!-- 节点详情浮层 -->
        <transition name="fade">
          <div v-if="selectedNode" class="node-detail-panel">
            <div class="detail-header">
              <h4>{{ selectedNode.label }}</h4>
              <el-icon class="close-btn" @click="selectedNode = null"><Close /></el-icon>
            </div>
            <div class="detail-content">
              <p class="desc">{{ selectedNode.desc }}</p>
              <div v-if="selectedNode.requirements" class="detail-section">
                <h5>岗位要求</h5>
                <ul>
                  <li v-for="(req, idx) in selectedNode.requirements" :key="idx">{{ req }}</li>
                </ul>
              </div>
              <div v-if="selectedNode.salary" class="detail-section">
                <h5>参考薪资</h5>
                <p class="salary">{{ selectedNode.salary }}</p>
              </div>
              <div v-if="selectedNode.needSkills" class="detail-section">
                <h5>技能补充</h5>
                <p class="need">{{ selectedNode.needSkills }}</p>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.development-map-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 84px);
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: #fff;
  padding: 20px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-section h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 主内容区 */
.main-content {
  display: flex;
  gap: 20px;
}

/* 左侧面板 */
.user-panel {
  width: 340px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.user-card {
  border-radius: 12px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.user-avatar {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
}

.user-info h3 {
  margin: 0 0 6px 0;
  font-size: 18px;
  color: #303133;
}

.school {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.position-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.match-rate {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.match-rate .label {
  font-size: 13px;
  color: #606266;
}

/* 能力维度卡片 */
.skills-card :deep(.el-card__header) {
  padding: 14px 20px;
  background: #f5f7fa;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.skill-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skill-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.skill-name {
  width: 80px;
  font-size: 13px;
  color: #606266;
  flex-shrink: 0;
}

.skill-bar-wrapper {
  flex: 1;
  height: 8px;
  background: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.skill-bar {
  height: 100%;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.skill-value {
  width: 30px;
  text-align: right;
  font-size: 13px;
  color: #606266;
  font-weight: 600;
}

.skill-value.high {
  color: #67c23a;
}

/* 分析卡片 */
.analysis-card :deep(.el-card__header) {
  padding: 14px 20px;
  background: #f0f9ff;
}

.analysis-card.warning :deep(.el-card__header) {
  background: #fff7e6;
}

.advantage-text {
  margin: 0;
  color: #52c41a;
  font-size: 13px;
  line-height: 1.8;
}

.improve-text {
  margin: 0;
  color: #fa8c16;
  font-size: 13px;
  line-height: 1.8;
}

/* 阶段卡片 */
.stages-card :deep(.el-card__header) {
  padding: 14px 20px;
  background: #f5f7fa;
}

.stage-content {
  margin-bottom: 8px;
}

.stage-content strong {
  color: #303133;
  font-size: 14px;
}

.stage-ability {
  margin: 4px 0 8px;
  color: #909399;
  font-size: 12px;
}

/* 图谱区域 */
.graph-section {
  flex: 1;
  position: relative;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  height: 700px;
}

.graph-container {
  width: 100%;
  height: 100%;
}

/* 节点详情面板 */
.node-detail-panel {
  position: absolute;
  right: 20px;
  top: 20px;
  width: 280px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 100;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  color: #fff;
  border-radius: 12px 12px 0 0;
}

.detail-header h4 {
  margin: 0;
  font-size: 16px;
}

.close-btn {
  cursor: pointer;
  font-size: 16px;
}

.detail-content {
  padding: 20px;
}

.detail-content .desc {
  margin: 0 0 16px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
  color: #606266;
  font-size: 13px;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section h5 {
  margin: 0 0 8px;
  font-size: 13px;
  color: #303133;
}

.detail-section ul {
  margin: 0;
  padding-left: 18px;
  color: #606266;
  font-size: 12px;
  line-height: 1.8;
}

.detail-section .salary {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.detail-section .need {
  color: #e6a23c;
  font-size: 12px;
  margin: 0;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 响应式 */
@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }

  .user-panel {
    width: 100%;
  }

  .graph-section {
    min-height: 500px;
  }
}
</style>
