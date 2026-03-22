<!-- src/components/CareerFormRadar.vue -->
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import { Loading, DocumentChecked, Warning, DataAnalysis, CircleCheck, Close, ArrowUp, ArrowDown, Collection, OfficeBuilding, Trophy, Edit } from '@element-plus/icons-vue'

// 定义接收的分数类型
export interface RadarScores {
  专业: number
  创新: number
  学习: number
  抗压: number
  沟通: number
  实习: number
}

// 缺失项类型
export interface MissingItem {
  field: string
  label: string
  icon: string
  priority: 'high' | 'medium' | 'low'
}

// 组件状态类型
type RadarStatus = 'empty' | 'loading' | 'ready' | 'error'

const props = withDefaults(defineProps<{
  // 六维能力分数
  scores?: RadarScores
  // 是否正在加载中（等待后端数据）
  loading?: boolean
  // 加载提示文本
  loadingText?: string
  // 错误提示文本
  errorText?: string
  // 数据来源标识：'manual' | 'resume' | 'api'
  sourceType?: string
  // 画像完整度 (0-100)
  completeness?: number
  // 缺失项列表
  missingItems?: MissingItem[]
  // 是否显示弹窗
  visible?: boolean
}>(), {
  scores: () => ({
    专业: 0,
    创新: 0,
    学习: 0,
    抗压: 0,
    沟通: 0,
    实习: 0
  }),
  loading: false,
  loadingText: '正在分析能力数据...',
  errorText: '数据加载失败，请重试',
  sourceType: 'manual',
  completeness: 0,
  missingItems: () => [],
  visible: false
})

const emit = defineEmits<{
  retry: []
  'update:visible': [value: boolean]
  'jump-to-field': [field: string]
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

// 弹窗收起/展开状态
const isCollapsed = ref(false)

// 判断是否有有效数据（任一维度大于0）
const hasValidData = computed(() => {
  const values = Object.values(props.scores)
  return values.some(val => (val || 0) > 0)
})

// 计算当前组件状态
const status = computed<RadarStatus>(() => {
  if (props.loading) return 'loading'
  if (hasValidData.value) return 'ready'
  return 'empty'
})

// 计算是否显示雷达图
const showRadar = computed(() => {
  return status.value === 'ready'
})

// 计算是否显示加载状态
const isLoading = computed(() => {
  return status.value === 'loading'
})

// 计算是否显示空状态
const isEmpty = computed(() => {
  return status.value === 'empty'
})

// 计算平均分
const averageScore = computed(() => {
  const values = Object.values(props.scores)
  if (values.length === 0) return 0
  const sum = values.reduce((acc, val) => acc + (val || 0), 0)
  return Math.round(sum / values.length)
})

// 获取能力等级评价
const getAbilityLevel = (score: number) => {
  if (score >= 90) return { label: '卓越', color: '#67c23a' }
  if (score >= 80) return { label: '优秀', color: '#409eff' }
  if (score >= 70) return { label: '良好', color: '#e6a23c' }
  if (score >= 60) return { label: '合格', color: '#909399' }
  return { label: '待提升', color: '#f56c6c' }
}

// 获取完整度等级
const completenessLevel = computed(() => {
  const value = props.completeness
  if (value >= 90) return { label: '完善', color: '#67c23a', status: 'success' as const }
  if (value >= 70) return { label: '良好', color: '#409eff', status: '' as const }
  if (value >= 50) return { label: '一般', color: '#e6a23c', status: 'warning' as const }
  return { label: '待完善', color: '#f56c6c', status: 'exception' as const }
})

// 获取优先级标签
const getPriorityLabel = (priority: string) => {
  switch (priority) {
    case 'high': return '重要'
    case 'medium': return '建议'
    case 'low': return '可选'
    default: return ''
  }
}

// 切换收起/展开状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  if (!isCollapsed.value) {
    nextTick(() => {
      initChart()
    })
  }
}

// 关闭弹窗
const closeDialog = () => {
  emit('update:visible', false)
}

// 跳转到指定字段
const jumpToField = (field: string) => {
  emit('jump-to-field', field)
  closeDialog()
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value || !showRadar.value) return
  chart = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表配置
const updateChart = () => {
  if (!chart || !showRadar.value) return

  const option = {
    radar: {
      indicator: [
        { name: '专业', max: 100 },
        { name: '创新', max: 100 },
        { name: '学习', max: 100 },
        { name: '抗压', max: 100 },
        { name: '沟通', max: 100 },
        { name: '实习', max: 100 }
      ],
      shape: 'circle',
      center: ['50%', '50%'],
      radius: '65%',
      name: {
        textStyle: {
          color: '#2c3e50',
          fontSize: 12,
          fontWeight: 500
        }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(64,158,255,0.02)', 'rgba(64,158,255,0.05)']
        }
      },
      axisLine: {
        lineStyle: {
          color: '#dcdfe6'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#e4e7ed'
        }
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const data = params.value as number[]
        const indicators = ['专业', '创新', '学习', '抗压', '沟通', '实习']
        let html = '<div style="padding: 8px;">'
        html += '<div style="font-weight: 600; margin-bottom: 8px;">能力评分详情</div>'
        indicators.forEach((name, index) => {
          const score = data[index] ?? 0
          const level = getAbilityLevel(score)
          html += `<div style="display: flex; justify-content: space-between; align-items: center; margin: 4px 0;">
            <span>${name}:</span>
            <span style="font-weight: 600; color: ${level.color}; margin-left: 12px;">${score}分</span>
          </div>`
        })
        html += '</div>'
        return html
      }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              props.scores.专业,
              props.scores.创新,
              props.scores.学习,
              props.scores.抗压,
              props.scores.沟通,
              props.scores.实习
            ],
            name: '能力评估',
            areaStyle: {
              color: new (echarts as any).graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(64,158,255,0.4)' },
                { offset: 1, color: 'rgba(64,158,255,0.1)' }
              ])
            },
            lineStyle: {
              color: '#409eff',
              width: 2
            },
            itemStyle: {
              color: '#409eff',
              borderWidth: 2,
              borderColor: '#fff'
            },
            emphasis: {
              areaStyle: {
                color: 'rgba(64,158,255,0.5)'
              }
            }
          }
        ]
      }
    ]
  }
  chart.setOption(option)
}

// 处理窗口大小变化
const handleResize = () => {
  chart?.resize()
}

// 监听弹窗显示状态
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    isCollapsed.value = false
    nextTick(() => {
      initChart()
    })
  }
})

onMounted(() => {
  if (props.visible) {
    initChart()
  }
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})

// 监听分数变化，更新图表
watch(
  () => props.scores,
  () => {
    nextTick(() => {
      updateChart()
    })
  },
  { deep: true }
)
</script>

<template>
  <!-- 悬浮按钮 - 当弹窗关闭时显示 -->
  <div v-if="!visible" class="radar-float-btn" :class="{ 'has-data': hasValidData }"
    @click="$emit('update:visible', true)">
    <el-icon :size="24">
      <DataAnalysis />
    </el-icon>
    <span class="float-text">能力评估</span>
    <div v-if="hasValidData" class="score-badge">{{ averageScore }}</div>
  </div>

  <!-- 雷达图弹窗 -->
  <div v-if="visible" class="radar-dialog-overlay" @click.self="closeDialog">
    <div class="radar-dialog" :class="{ 'is-collapsed': isCollapsed }">
      <!-- 弹窗头部 -->
      <div class="radar-dialog-header">
        <div class="header-left">
          <el-icon class="header-icon" :size="20">
            <DataAnalysis />
          </el-icon>
          <span class="header-title">能力画像评估</span>
          <div class="radar-badge" :class="sourceType">
            <el-icon v-if="sourceType === 'manual'">
              <DocumentChecked />
            </el-icon>
            <el-icon v-else-if="sourceType === 'resume'">
              <DataAnalysis />
            </el-icon>
            <span>{{ sourceType === 'manual' ? '手动填写' : sourceType === 'resume' ? '简历解析' : '系统评估' }}</span>
          </div>
        </div>
        <div class="header-actions">
          <el-button text class="collapse-btn" @click="toggleCollapse" :title="isCollapsed ? '展开' : '收起'">
            <el-icon :size="16">
              <ArrowUp v-if="!isCollapsed" />
              <ArrowDown v-else />
            </el-icon>
          </el-button>
          <el-button text class="close-btn" @click="closeDialog" title="关闭">
            <el-icon :size="16">
              <Close />
            </el-icon>
          </el-button>
        </div>
      </div>

      <!-- 弹窗内容 -->
      <div v-show="!isCollapsed" class="radar-dialog-body">
        <!-- 画像完整度区域 -->
        <div class="completeness-section">
          <div class="completeness-header">
            <div class="completeness-title">
              <el-icon :size="18" :color="completenessLevel.color">
                <CircleCheck />
              </el-icon>
              <span>画像完整度</span>
            </div>
            <div class="completeness-value" :style="{ color: completenessLevel.color }">
              <span class="percentage">{{ completeness }}%</span>
              <el-tag :type="completenessLevel.status" size="small" effect="light">
                {{ completenessLevel.label }}
              </el-tag>
            </div>
          </div>
          <el-progress :percentage="completeness" :status="completenessLevel.status" :stroke-width="10"
            :show-text="false" class="completeness-progress" />
          <p class="completeness-hint">
            {{ completeness >= 90 ? '您的画像信息已非常完善，可以进行能力评估' :
              completeness >= 70 ? '您的画像信息较为完善，建议补充以下内容' :
                '您的画像信息有待完善，建议先补充以下重要信息' }}
          </p>
        </div>

        <!-- 缺失项提示区域 -->
        <div v-if="missingItems.length > 0" class="missing-section">
          <div class="missing-title">
            <el-icon :size="16">
              <Warning />
            </el-icon>
            <span>待完善项 ({{ missingItems.length }})</span>
          </div>
          <div class="missing-list">
            <div v-for="(item, index) in missingItems" :key="index" class="missing-item"
              :class="`priority-${item.priority}`" @click="jumpToField(item.field)">
              <div class="missing-icon">
                <el-icon :size="16">
                  <Collection v-if="item.icon === 'certificate'" />
                  <OfficeBuilding v-else-if="item.icon === 'internship'" />
                  <Trophy v-else-if="item.icon === 'project'" />
                  <Edit v-else />
                </el-icon>
              </div>
              <div class="missing-info">
                <span class="missing-label">{{ item.label }}</span>
                <el-tag size="small"
                  :type="item.priority === 'high' ? 'danger' : item.priority === 'medium' ? 'warning' : 'info'"
                  effect="light" class="priority-tag">
                  {{ getPriorityLabel(item.priority) }}
                </el-tag>
              </div>
              <el-button text type="primary" size="small" class="fill-btn">
                去填写
              </el-button>
            </div>
          </div>
        </div>

        <!-- 雷达图展示区域 -->
        <div v-if="showRadar" class="radar-chart-section">
          <div class="section-title">
            <el-icon :size="16">
              <DataAnalysis />
            </el-icon>
            <span>六维能力评估</span>
          </div>
          <div ref="chartRef" class="chart-content"></div>

          <!-- 分数详情 -->
          <div class="scores-detail">
            <div class="average-score">
              <span class="label">综合评分</span>
              <span class="score" :style="{ color: getAbilityLevel(averageScore).color }">
                {{ averageScore }}
              </span>
              <span class="level"
                :style="{ backgroundColor: getAbilityLevel(averageScore).color + '20', color: getAbilityLevel(averageScore).color }">
                {{ getAbilityLevel(averageScore).label }}
              </span>
            </div>
            <div class="scores-grid">
              <div v-for="(score, key) in scores" :key="key" class="score-item">
                <span class="score-name">{{ key }}</span>
                <div class="score-bar">
                  <div class="score-progress" :style="{
                    width: score + '%',
                    backgroundColor: getAbilityLevel(score).color
                  }"></div>
                </div>
                <span class="score-value" :style="{ color: getAbilityLevel(score).color }">
                  {{ score }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-else-if="isLoading" class="status-container loading">
          <el-icon class="loading-icon" :size="48">
            <Loading />
          </el-icon>
          <p class="status-text">{{ loadingText }}</p>
          <el-progress :percentage="100" :indeterminate="true" :stroke-width="4" class="loading-progress" />
          <p class="status-hint">AI 正在分析您的画像数据，请稍候...</p>
        </div>

        <!-- 空状态 -->
        <div v-else-if="isEmpty" class="status-container empty">
          <el-icon class="empty-icon" :size="48">
            <DataAnalysis />
          </el-icon>
          <p class="status-text">暂无能力评估数据</p>
          <p class="status-hint">请先完善画像信息，提交后生成能力雷达图</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 悬浮按钮 */
.radar-float-btn {
  position: fixed;
  right: 24px;
  bottom: 100px;
  width: 65px;
  height: 65px;
  background: #918c8c;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(255, 255, 255, 0.12);
  transition: all 0.3s ease;
  z-index: 1000;
  border: 2px solid #ffffff;
}

.radar-float-btn:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.25);
  border-color: #409eff;
}

.radar-float-btn.has-data {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-color: #409eff;
  color: #fff;
}

.radar-float-btn .float-text {
  font-size: 11px;
  margin-top: 2px;
  font-weight: 500;
}

.score-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 24px;
  height: 24px;
  background: #f56c6c;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  border: 2px solid #fff;
}

/* 弹窗遮罩 */
.radar-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

/* 弹窗主体 */
.radar-dialog {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 520px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
  transition: all 0.3s ease;
}

.radar-dialog.is-collapsed {
  max-width: 400px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 弹窗头部 */
.radar-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafbfc;
  border-radius: 12px 12px 0 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  color: #409eff;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.radar-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.radar-badge.manual {
  background: #ecf5ff;
  color: #409eff;
}

.radar-badge.resume {
  background: #f0f9eb;
  color: #67c23a;
}

.radar-badge.api {
  background: #fdf6ec;
  color: #e6a23c;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.collapse-btn,
.close-btn {
  padding: 6px;
  border-radius: 4px;
  color: #909399;
}

.collapse-btn:hover,
.close-btn:hover {
  background: #f0f2f5;
  color: #606266;
}

/* 弹窗内容 */
.radar-dialog-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(85vh - 60px);
}

/* 画像完整度区域 */
.completeness-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
}

.completeness-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.completeness-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.completeness-value {
  display: flex;
  align-items: center;
  gap: 8px;
}

.completeness-value .percentage {
  font-size: 20px;
  font-weight: 700;
}

.completeness-progress {
  margin-bottom: 10px;
}

.completeness-progress :deep(.el-progress-bar__outer) {
  background-color: #e4e7ed;
  border-radius: 5px;
}

.completeness-progress :deep(.el-progress-bar__inner) {
  border-radius: 5px;
  transition: width 0.6s ease;
}

.completeness-hint {
  margin: 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

/* 缺失项区域 */
.missing-section {
  margin-bottom: 16px;
}

.missing-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
}

.missing-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.missing-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.missing-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
  transform: translateX(4px);
}

.missing-item.priority-high {
  border-left: 3px solid #f56c6c;
}

.missing-item.priority-medium {
  border-left: 3px solid #e6a23c;
}

.missing-item.priority-low {
  border-left: 3px solid #909399;
}

.missing-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #606266;
  flex-shrink: 0;
}

.missing-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.missing-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.priority-tag {
  width: fit-content;
}

.fill-btn {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.missing-item:hover .fill-btn {
  opacity: 1;
}

/* 雷达图区域 */
.radar-chart-section {
  background: #fafbfc;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid #e4e7ed;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.chart-content {
  width: 100%;
  height: 260px;
}

/* 分数详情 */
.scores-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.average-score {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
}

.average-score .label {
  font-size: 14px;
  color: #606266;
}

.average-score .score {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.average-score .level {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: #fff;
  border-radius: 6px;
}

.score-name {
  width: 36px;
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.score-bar {
  flex: 1;
  height: 5px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.score-progress {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.score-value {
  width: 24px;
  text-align: right;
  font-size: 12px;
  font-weight: 600;
}

/* 状态容器 */
.status-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e4e7ed;
  min-height: 240px;
}

.status-container.loading {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
}

.status-container.empty {
  background: #f5f7fa;
}

.loading-icon {
  color: #409eff;
  animation: rotate 1.5s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.empty-icon {
  color: #c0c4cc;
}

.status-text {
  margin: 12px 0 8px;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.status-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: #909399;
}

.loading-progress {
  width: 180px;
  margin: 12px 0;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .radar-float-btn {
    right: 16px;
    bottom: 80px;
    width: 52px;
    height: 52px;
  }

  .radar-float-btn .float-text {
    font-size: 10px;
  }

  .radar-dialog {
    max-width: 100%;
    max-height: 90vh;
    margin: 0 16px;
  }

  .scores-grid {
    grid-template-columns: 1fr;
  }

  .chart-content {
    height: 220px;
  }

  .missing-item .fill-btn {
    opacity: 1;
  }
}
</style>
