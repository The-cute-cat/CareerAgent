<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Upload,
  DocumentChecked,
  DataLine,
  MapLocation,
  Warning
} from '@element-plus/icons-vue'

const router = useRouter()
const radarChartRef = ref<HTMLElement | null>(null)

// 快捷功能卡片数据
const quickActions = [
  {
    title: '上传简历',
    icon: Upload,
    desc: '点击上传简历',
    color: '#409eff',
    route: '/upload'
  },
  {
    title: '查看匹配',
    icon: DocumentChecked,
    desc: '岗位匹配',
    color: '#67c23a',
    route: '/report'
  },
  {
    title: '生成报告',
    icon: DataLine,
    desc: '生成我的生涯报告',
    color: '#e6a23c',
    route: '/report'
  },
  {
    title: '职业地图',
    icon: MapLocation,
    desc: '查看岗位晋升路线',
    color: '#f56c6c',
    route: '/development-map'
  }
]


// 跳转到对应页面
const navigateTo = (route: string) => {
  router.push(route)
}

// 初始化雷达图
onMounted(() => {
  if (radarChartRef.value) {
    const chart = echarts.init(radarChartRef.value)
    const option = {
      radar: {
        indicator: [
          { name: '沟通能力', max: 100 },
          { name: '专业技能', max: 100 },
          { name: '团队协作', max: 100 },
          { name: '学习能力', max: 100 },
          { name: '领导力', max: 100 },
          { name: '创新思维', max: 100 }
        ],
        radius: '65%',
        center: ['50%', '55%'],
        axisName: {
          color: '#606266',
          fontSize: 12
        },
        splitArea: {
          areaStyle: {
            color: ['#f5f7fa', '#fff']
          }
        }
      },
      series: [{
        type: 'radar',
        data: [{
          value: [75, 85, 70, 80, 60, 72],
          name: '当前能力',
          areaStyle: {
            color: 'rgba(64, 158, 255, 0.3)'
          },
          lineStyle: {
            color: '#409eff',
            width: 2
          },
          itemStyle: {
            color: '#409eff'
          }
        }]
      }]
    }
    chart.setOption(option)
    window.addEventListener('resize', () => chart.resize())
  }
})
</script>

<template>
  <div class="dashboard-container">

    <!-- 第一行：快捷功能卡 -->
    <el-row :gutter="20" class="card-row">
      <el-col :span="24">
        <el-card class="quick-actions-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataLine /></el-icon>
              <span>快捷功能</span>
            </div>
          </template>
          <div class="quick-actions-grid">
            <div
              v-for="action in quickActions"
              :key="action.title"
              class="action-block"
              :style="{ borderColor: action.color }"
              @click="navigateTo(action.route)"
            >
              <div class="action-icon" :style="{ backgroundColor: action.color + '20', color: action.color }">
                <el-icon :size="32">
                  <component :is="action.icon" />
                </el-icon>
              </div>
              <div class="action-info">
                <h3 :style="{ color: action.color }">{{ action.title }}</h3>
                <p>{{ action.desc }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：能力概览 + 系统公告 -->
    <el-row :gutter="20" class="card-row">
      <!-- 能力概览卡 -->
      <el-col :xs="24" :sm="24" :md="14">
        <el-card class="radar-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataLine /></el-icon>
              <span>能力概览</span>
            </div>
          </template>
          <div ref="radarChartRef" class="radar-chart"></div>
          <div class="radar-legend">
            <div class="legend-item">
              <span class="legend-dot" style="background-color: #409eff;"></span>
              <span>当前能力评估（基于简历分析）</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 系统公告卡 -->
      <el-col :xs="24" :sm="24" :md="10">
        <el-card class="notice-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Warning /></el-icon>
              <span>系统公告</span>
            </div>
          </template>
          <div class="notice-content">
            <el-alert
              title="欢迎使用 AI 职业规划"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <p>请先上传简历以生成画像</p>
              </template>
            </el-alert>
            <div class="notice-tips">
              <h4>使用指南：</h4>
              <ol>
                <li>点击"上传简历"，上传您的个人简历</li>
                <li>系统将自动分析您的能力特点</li>
                <li>查看匹配岗位和生涯报告</li>
                <li>探索职业地图，规划晋升路线</li>
              </ol>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.dashboard-header {
  margin-bottom: 24px;
}

.dashboard-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.card-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

/* 快捷功能卡样式 */
.quick-actions-card {
  border-radius: 12px;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.action-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
  border-radius: 12px;
  border: 2px solid;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fff;
}

.action-block:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.action-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.action-info {
  text-align: center;
}

.action-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
}

.action-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

/* 雷达图卡片样式 */
.radar-card {
  border-radius: 12px;
  height: 100%;
}

.radar-chart {
  width: 100%;
  height: 320px;
}

.radar-legend {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}


.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

/* 系统公告卡样式 */
.notice-card {
  border-radius: 12px;
  height: 100%;
}

.notice-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.notice-tips {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
}

.notice-tips h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
}

.notice-tips ol {
  margin: 0;
  padding-left: 18px;
  color: #606266;
  font-size: 13px;
  line-height: 2;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .quick-actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .action-block {
    flex-direction: row;
    padding: 20px;
    gap: 16px;
  }
  
  .action-icon {
    margin-bottom: 0;
  }
  
  .action-info {
    text-align: left;
  }
}
</style>
