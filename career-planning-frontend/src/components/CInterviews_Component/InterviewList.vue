<script setup>
import { ref, computed, watch } from 'vue'
import { Plus, Search, Filter, Monitor } from '@element-plus/icons-vue'
import InterviewCard from './InterviewCard.vue'

const props = defineProps({
  interviews: { type: Array, default: () => [] },
  selectedDate: { type: String, default: '' }
})

const activeTab = ref('all')
const searchQuery = ref('')

const formattedTitle = computed(() => {
  if (!props.selectedDate) return '全部面试'
  const [y, m, d] = props.selectedDate.split('-')
  return `${parseInt(m)}月${parseInt(d)}日的面试`
})

const filteredInterviews = computed(() => {
  let result = props.interviews
  
  if (activeTab.value !== 'all') {
    result = result.filter(item => {
      if (activeTab.value === 'ongoing') return item.status === 'ongoing' || item.status === 'pending'
      if (activeTab.value === 'finished') return item.status === 'passed' || item.status === 'failed'
      return true
    })
  }
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(item => 
      item.company.toLowerCase().includes(q) || 
      item.role.toLowerCase().includes(q)
    )
  }
  
  return result
})
</script>

<template>
  <div class="interview-list-container">
    <div class="main-header-bar">
      {{ formattedTitle }}
    </div>

    <div class="interview-list-section">
      <div class="list-header">
        <el-tabs v-model="activeTab" class="custom-tabs">
          <el-tab-pane label="全部" name="all"></el-tab-pane>
          <el-tab-pane label="进行中" name="ongoing"></el-tab-pane>
          <el-tab-pane label="已结束" name="finished"></el-tab-pane>
          <el-tab-pane label="面试复盘" name="review"></el-tab-pane>
        </el-tabs>

        <div class="header-actions">
          <el-input
            v-model="searchQuery"
            placeholder="搜索公司或职位"
            :prefix-icon="Search"
            class="search-input"
            clearable
          />
          <el-button :icon="Filter" circle plain class="filter-btn"></el-button>
        </div>
      </div>

      <div class="list-content">
        <template v-if="filteredInterviews.length > 0">
          <div
            v-for="item in filteredInterviews"
            :key="item.id"
            class="enhanced-card-wrapper"
          >
            <InterviewCard :interview="item" />
            <!-- 补充视频面试链接（如截图所示） -->
            <div v-if="item.location.includes('视频') || item.location.includes('会议')" class="quick-link">
              <el-icon><Monitor /></el-icon> 视频面试
            </div>
          </div>
        </template>

        <div v-else class="empty-state">
          <div class="empty-icon">📂</div>
          <p>暂无面试记录，点击添加面试安排</p>
          <el-button type="primary" :icon="Plus" round>添加面试安排</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.interview-list-section {
  margin-top: 24px;
}

.interview-list-container {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.main-header-bar {
  height: 64px;
  background: linear-gradient(90deg, #409eff 0%, #1677ff 100%);
  display: flex;
  align-items: center;
  padding: 0 24px;
  color: #fff;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.interview-list-section {
  background: transparent;
  padding: 24px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 0px;
}

.enhanced-card-wrapper {
  position: relative;
  margin-bottom: 24px;
  
  .quick-link {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 700;
    color: #f59e0b;
    margin-top: -8px;
    margin-left: 24px;
    cursor: pointer;
    
    &:hover { color: #d97706; }
  }
}

.custom-tabs {
  :deep(.el-tabs__header) {
    margin: 0;
    border: none;
  }
  
  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }
  
  :deep(.el-tabs__item) {
    font-size: 15px;
    font-weight: 600;
    height: 48px;
    padding: 0 24px;
    color: #64748b;
    
    &.is-active {
      color: #3b82f6;
    }
  }

  :deep(.el-tabs__active-bar) {
    background-color: #3b82f6;
    height: 3px;
    border-radius: 3px;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
  
  :deep(.el-input__wrapper) {
    background-color: #f8fafc;
    box-shadow: none;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    transition: all 0.2s;

    &.is-focus {
      background-color: #fff;
      border-color: #3b82f6;
      box-shadow: 0 0 0 1px #3b82f6;
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  text-align: center;
  background: #ffffff;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
    filter: grayscale(1);
    opacity: 0.5;
  }

  p {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 24px;
    font-weight: 500;
  }
}

@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .header-actions, .search-input {
    width: 100%;
  }
}
</style>
