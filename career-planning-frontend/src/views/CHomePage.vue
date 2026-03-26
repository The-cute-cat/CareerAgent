<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { Warning, Lock, DataLine } from '@element-plus/icons-vue'
import { quickActions, homeRadarData } from '@/mock/data'
import { useUserStore } from '@/stores/modules/user'

const router = useRouter()
const userStore = useUserStore()
const radarChartRef = ref<HTMLElement | null>(null)

// 计算登录状态
const isLoggedIn = computed(() => userStore.isLoggedIn)
const userName = computed(() => userStore.userInfo?.nickname || userStore.userInfo?.username || '用户')

// 跳转到对应页面
const navigateTo = (route: string) => {
  router.push(route)
}

// 初始化雷达图
onMounted(() => {
  if (radarChartRef.value && isLoggedIn.value) {
    initRadarChart()
  }
})

// 初始化雷达图方法
const initRadarChart = () => {
  if (!radarChartRef.value) return
  const chart = echarts.init(radarChartRef.value)
  const option = {
    backgroundColor: 'transparent',
    radar: {
      indicator: homeRadarData.indicator,
      radius: '65%',
      center: ['50%', '55%'],
      axisName: {
        color: '#606266',
        fontSize: 13,
        fontWeight: 500
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(64, 158, 255, 0.02)', 'rgba(64, 158, 255, 0.08)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(64, 158, 255, 0.2)'
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(64, 158, 255, 0.2)'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: homeRadarData.value,
        name: homeRadarData.name,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
            offset: 0,
            color: 'rgba(64, 158, 255, 0.6)'
          }, {
            offset: 1,
            color: 'rgba(64, 158, 255, 0.1)'
          }])
        },
        lineStyle: {
          color: '#409eff',
          width: 2
        },
        itemStyle: {
          color: '#409eff',
          borderColor: '#fff',
          borderWidth: 2
        }
      }]
    }]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="dashboard-container">
    <div class="welcome-header">
      <h1 class="greeting">
        欢迎回来, <span class="gradient-text">{{ userName }}</span> 👋
      </h1>
      <p class="subtitle">今天你想如何规划你的职业生涯？</p>
    </div>

    <!-- 第一行：快捷功能卡 -->
    <div class="quick-actions-grid">
      <div
        v-for="action in quickActions"
        :key="action.title"
        class="glass-action-card"
        @click="navigateTo(action.route)"
      >
        <div class="card-glow" :style="{ background: action.color }"></div>
        <div class="action-icon-wrapper" :style="{ background: `linear-gradient(135deg, ${action.color}22, ${action.color}11)` }">
          <el-icon :size="28" :color="action.color">
            <component :is="action.icon" />
          </el-icon>
        </div>
        <div class="action-info">
          <h3>{{ action.title }}</h3>
          <p>{{ action.desc }}</p>
        </div>
        <div class="action-arrow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 第二行：能力概览 + 系统公告 -->
    <el-row :gutter="24" class="card-row">
      <!-- 能力概览卡 -->
      <el-col :xs="24" :sm="24" :md="14">
        <div class="glass-panel radar-panel">
          <div class="panel-header">
            <div class="header-icon-box blue-box">
              <el-icon><DataLine /></el-icon>
            </div>
            <h2>能力概览</h2>
          </div>
          
          <!-- 未登录状态：显示登录提醒 -->
          <div v-if="!isLoggedIn" class="login-prompt">
            <div class="lock-circle">
              <el-icon :size="48"><Lock /></el-icon>
            </div>
            <h3>请先登录</h3>
            <p>登录后即可查看基于简历的个人能力智能分析</p>
            <el-button class="gradient-btn" size="large" round @click="goToLogin">
              立即登录
            </el-button>
          </div>
          
          <!-- 已登录状态：显示雷达图 -->
          <template v-else>
            <div ref="radarChartRef" class="radar-chart"></div>
            <div class="radar-legend">
              <div class="legend-item">
                <span class="legend-dot"></span>
                <span>智能能力评估画像（基于简历及行为分析）</span>
              </div>
            </div>
          </template>
        </div>
      </el-col>

      <!-- 系统公告卡 -->
      <el-col :xs="24" :sm="24" :md="10">
        <div class="glass-panel notice-panel">
          <div class="panel-header">
            <div class="header-icon-box orange-box">
              <el-icon><Warning /></el-icon>
            </div>
            <h2>系统公告</h2>
          </div>
          
          <div class="notice-content">
            <div class="welcome-alert">
              <div class="alert-icon">✨</div>
              <div class="alert-text">
                <h4>欢迎使用 AI 职业规划</h4>
                <p>请先上传简历以生成智能画像并获取专属建议。</p>
              </div>
            </div>
            
            <div class="guide-steps">
              <h4 class="guide-title">快速指南</h4>
              <div class="step-item">
                <div class="step-num">1</div>
                <div class="step-desc">
                  <strong>上传简历</strong>
                  <span>支持 PDF/Word 格式的个人简历解析</span>
                </div>
              </div>
              <div class="step-item">
                <div class="step-num">2</div>
                <div class="step-desc">
                  <strong>智能分析</strong>
                  <span>系统通过大模型分析您的能力与强项</span>
                </div>
              </div>
              <div class="step-item">
                <div class="step-num">3</div>
                <div class="step-desc">
                  <strong>匹配岗位</strong>
                  <span>自动匹配最符合您的市场高薪岗位</span>
                </div>
              </div>
              <div class="step-item">
                <div class="step-num">4</div>
                <div class="step-desc">
                  <strong>规划路线</strong>
                  <span>查阅职业地图，获得详细的成长与晋升路线</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 10px;
  min-height: 100%;
}

.welcome-header {
  margin-bottom: 32px;
}

.greeting {
  font-size: 32px;
  font-weight: 800;
  color: #2c3e50;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.gradient-text {
  background: linear-gradient(135deg, #409EFF 0%, #764BA2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.glass-action-card {
  position: relative;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  padding: 24px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
}

.card-glow {
  position: absolute;
  width: 120px;
  height: 120px;
  right: -30px;
  top: -30px;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.15;
  transition: all 0.4s ease;
}

.glass-action-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.9);
}

.glass-action-card:hover .card-glow {
  opacity: 0.3;
  transform: scale(1.2);
}

.action-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.8);
}

.action-info h3 {
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.action-info p {
  font-size: 13px;
  color: #909399;
  margin: 0;
  line-height: 1.5;
}

.action-arrow {
  position: absolute;
  bottom: 24px;
  right: 24px;
  width: 24px;
  height: 24px;
  color: #c0c4cc;
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateX(-10px);
}

.glass-action-card:hover .action-arrow {
  opacity: 1;
  transform: translateX(0);
  color: #409EFF;
}

.card-row {
  margin-bottom: 24px;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 24px;
  padding: 28px;
  height: 100%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.03);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.header-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.blue-box {
  background: linear-gradient(135deg, #409EFF 0%, #3a8ee6 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.orange-box {
  background: linear-gradient(135deg, #fa8c16 0%, #ffc53d 100%);
  box-shadow: 0 4px 12px rgba(250, 140, 22, 0.3);
}

.panel-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.radar-chart {
  width: 100%;
  height: 340px;
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
  background: rgba(255, 255, 255, 0.8);
  padding: 6px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #409eff;
  box-shadow: 0 0 4px #409eff;
}

.login-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 340px;
  text-align: center;
}

.lock-circle {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: inset 0 2px 4px #fff, 0 8px 24px rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  margin-bottom: 24px;
}

.login-prompt h3 {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.login-prompt p {
  color: #909399;
  font-size: 14px;
  margin: 0 0 24px 0;
}

.gradient-btn {
  background: linear-gradient(135deg, #409EFF 0%, #764BA2 100%);
  border: none;
  font-weight: 600;
  padding: 12px 32px;
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.3);
  color: #fff;
  transition: all 0.3s ease;
}

.gradient-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.4);
  color: #fff;
}

.notice-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.welcome-alert {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1) 0%, rgba(64, 158, 255, 0.02) 100%);
  border: 1px solid rgba(64, 158, 255, 0.2);
  padding: 20px;
  border-radius: 16px;
}

.alert-icon {
  font-size: 24px;
}

.alert-text h4 {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 700;
  color: #409eff;
}

.alert-text p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.guide-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.guide-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #2c3e50;
  padding-left: 4px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.8);
  padding: 16px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.step-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f2f5;
  color: #909399;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.04);
}

.step-item:hover .step-num {
  background: #409eff;
  color: #fff;
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
}

.step-desc {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.step-desc strong {
  font-size: 15px;
  color: #303133;
}

.step-desc span {
  font-size: 13px;
  color: #909399;
}

@media (max-width: 1200px) {
  .quick-actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
