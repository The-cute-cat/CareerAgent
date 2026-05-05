<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, House, Memo, Timer, Finished, Reading } from '@element-plus/icons-vue'

import InterviewOverview from '../components/CInterviews_Component/InterviewOverview.vue'
import InterviewList from '../components/CInterviews_Component/InterviewList.vue'
import InterviewReview from '../components/CInterviews_Component/InterviewReview.vue'
import InterviewCalendarView from '../components/CInterviews_Component/InterviewCalendarView.vue'

const route = useRoute()
const isMobileLayout = ref(false)

// 默认选中今天 (YYYY-MM-DD 格式)
const formatDate = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const selectedDate = ref(formatDate(new Date())) 

// 面试示例数据，用于日历打点和列表展示
const interviewsData = ref([
  { id: 1, company: '字节跳动', role: '前端开发工程师', time: '2026-04-01 10:00', location: '视频面试 (飞书)', type: '初面(技术面试)', status: 'pending', logo: 'https://p1-tt.byteimg.com/origin/pgc-image/80387588147d4e3cb98e3b5695a0468e' },
  { id: 2, company: '腾讯', role: '全栈开发工程师', time: '2026-04-03 15:30', location: '腾讯会议', type: '二面', status: 'ongoing', logo: 'https://www.tencent.com/img/index/menu-logo-hover.png' },
  { id: 3, company: '阿里巴巴', role: 'Java 专家', time: '2026-03-28 14:00', location: '钉钉会议', type: '终面', status: 'passed', logo: 'https://img.alicdn.com/tfs/TB1_uT8n6ihY1JjSZFwXXcj3FXa-115-115.png' },
  { id: 4, company: '美团', role: '后端开发', time: '2026-04-01 11:00', location: '北京朝阳区望京', type: '技术初面', status: 'pending', logo: 'https://p0.meituan.net/travelcube/45c79afaa6f328136e4f3a9e9de0914c10243.png' },
  { id: 5, company: '百度', role: '算法工程师', time: '2026-04-10 14:00', location: '百度大厦', type: '终面', status: 'pending', logo: 'https://www.baidu.com/img/flexible/logo/pc/result.png' }
])

const todayInterviews = computed(() => {
  const today = formatDate(new Date())
  return interviewsData.value.filter(item => item.time.startsWith(today))
})

const filteredInterviews = computed(() => {
  if (!selectedDate.value) return interviewsData.value
  return interviewsData.value.filter(item => item.time.startsWith(selectedDate.value))
})

const handleResize = () => {
  if (typeof window !== 'undefined') {
    isMobileLayout.value = window.innerWidth <= 768
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    handleResize()
    window.addEventListener('resize', handleResize)
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleResize)
  }
})

// 根据路由路径判断当前选中的子模块
const currentType = computed(() => {
  const path = route.path
  if (path.includes('calendar')) return 'calendar'
  if (path.includes('ongoing')) return 'ongoing'
  if (path.includes('finished')) return 'finished'
  if (path.includes('review')) return 'review'
  return 'all'
})

const pageTitle = computed(() => {
  const titles = {
    all: '我的面试',
    calendar: '面试日历（整体安排）',
    ongoing: '进行中面试（待面试/面试中）',
    finished: '已完成面试（通过/未通过）',
    review: '面试复盘（笔记/资料）'
  }
  return titles[currentType.value] || '我的面试'
})

const pageDescription = computed(() => {
  const descriptions = {
    all: '查看面试概览看板、分类列表及复盘笔记，全方位管理你的求职进程。',
    calendar: '通过日历视图查看未来一周的面试安排。',
    ongoing: '关注眼前的挑战，确保每一场面试都准时参加。',
    finished: '回顾面试结果，总结得失。',
    review: '深度记录面试细节，积累实战经验。'
  }
  return descriptions[currentType.value] || '全方位管理你的求职进程。'
})

const handleHeaderAction = (action) => {
  console.log('Action triggered:', action)
}
</script>

<template>
  <div class="interviews-page">
    <div class="page-glow page-glow-top"></div>
    <div class="page-glow page-glow-bottom"></div>

    <div class="content-wrapper split-layout">
      <!-- 左侧：调度侧边栏 (日历 + 今日摘要) -->
      <div class="sidebar-column">
        <!-- 迷你日历 -->
        <InterviewCalendarView 
          :interviews="interviewsData"
          @select-date="date => selectedDate = date"
          class="mini-calendar-wrapper"
        />

        <!-- 今日面试安排 -->
        <div class="today-summary-card">
          <div class="summary-header">
            <h3>今天的面试安排 <span class="count">({{ todayInterviews.length }})</span></h3>
            <span class="add-link">新增面试</span>
          </div>
          <div class="summary-list">
            <div v-for="item in todayInterviews" :key="item.id" class="summary-item">
              <div class="item-left">
                <div class="item-title">{{ item.type }}</div>
                <div class="item-subtitle">{{ item.role }} - {{ item.company }}</div>
                <div class="item-time"><el-icon><Timer /></el-icon> {{ item.time.split(' ')[1] }}</div>
              </div>
              <div class="item-status-tag">面试准备</div>
            </div>
            <el-empty v-if="todayInterviews.length === 0" description="今天暂无安排" :image-size="60" />
          </div>
        </div>
      </div>

      <!-- 右侧：面试详情区 -->
      <div class="main-column">
        <InterviewList 
          v-if="currentType !== 'review'" 
          :interviews="filteredInterviews"
          :selectedDate="selectedDate"
          :active-tab="currentType === 'all' ? 'all' : currentType" 
        />
        <InterviewReview v-if="currentType === 'all' || currentType === 'review'" />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.interviews-page {
  position: relative;
  min-height: calc(100vh - 80px);
  padding: 40px;
  box-sizing: border-box;
  background: 
    radial-gradient(ellipse at top left, rgba(64, 158, 255, 0.05), transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(118, 75, 162, 0.05), transparent 50%),
    var(--color-background-soft);
  overflow: hidden;
  font-family: 'Inter', -apple-system, sans-serif;
}

.page-glow {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  z-index: 0;
  opacity: 0.4;
}

.page-glow-top { top: -200px; left: -100px; background: rgba(64, 158, 255, 0.2); }
.page-glow-bottom { bottom: -200px; right: -100px; background: rgba(118, 75, 162, 0.1); }

.content-wrapper.split-layout {
  display: flex;
  gap: 24px;
  max-width: 1400px;
  align-items: flex-start;
}

.sidebar-column {
  flex: 0 0 380px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.main-column {
  flex: 1;
  min-width: 0;
}

/* 今日摘要卡片 */
.today-summary-card {
  background: var(--color-background);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03);
  border: 1px solid var(--color-border);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h3 {
    font-size: 16px;
    font-weight: 800;
    color: var(--color-heading);
    margin: 0;
    .count { color: var(--color-text); font-weight: 500; font-size: 14px; margin-left: 4px; }
  }
  
  .add-link {
    font-size: 13px;
    font-weight: 600;
    color: #1e62c5;
    cursor: pointer;
  }
}

.summary-item {
  padding: 16px;
  background: var(--color-background-soft);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  
  .item-left {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .item-title { font-size: 14px; font-weight: 800; color: var(--color-heading); margin-bottom: 4px; }
  .item-subtitle { font-size: 12px; color: var(--color-text); margin-bottom: 8px; }
  .item-time { font-size: 12px; color: var(--el-color-primary); font-weight: 600; display: flex; align-items: center; gap: 4px; }
  
  .item-status-tag {
    font-size: 11px;
    padding: 4px 8px;
    background: var(--color-background-soft);
    color: var(--el-color-primary);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    font-weight: 700;
  }
}

@media (max-width: 768px) {
  .interviews-page { padding: 24px 16px; }
  .content-intro h1 { font-size: 24px; }
}
</style>
