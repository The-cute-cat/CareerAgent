<script setup lang="ts">
import { ref } from 'vue'
import { Monitor, ChatLineRound, Document } from '@element-plus/icons-vue'
import FeedbackManager from './FeedbackManager.vue'
import UsageRecordManager from './UsageRecordManager.vue'

const activeTab = ref('feedback')

const handleTabChange = (tabName: string) => {
  activeTab.value = tabName
}
</script>

<template>
  <div class="admin-panel-container">
    <div class="admin-header">
      <div class="header-left">
        <el-icon class="logo-icon"><Monitor /></el-icon>
        <span class="logo-text">职悟 Agent · 管理端</span>
      </div>
    </div>

    <div class="admin-layout">
      <!-- 侧边菜单 -->
      <div class="admin-sidebar">
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'feedback' }"
          @click="handleTabChange('feedback')"
        >
          <el-icon><ChatLineRound /></el-icon>
          <span>反馈管理</span>
        </div>
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'usage' }"
          @click="handleTabChange('usage')"
        >
          <el-icon><Document /></el-icon>
          <span>使用记录</span>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="admin-main">
        <transition name="fade-slide" mode="out-in">
          <div :key="activeTab" class="content-wrapper">
             <div class="page-header">
                <h2>{{ activeTab === 'feedback' ? '用户反馈处理' : '平台使用记录' }}</h2>
                <p>{{ activeTab === 'feedback' ? '查看并回复来自用户的使用建议与问题反馈' : '监控全站用户的 AI 交互与资源消耗情况' }}</p>
             </div>
             
             <div class="component-card">
                <FeedbackManager v-if="activeTab === 'feedback'" />
                <UsageRecordManager v-else-if="activeTab === 'usage'" />
             </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.admin-panel-container {
  min-height: 100vh;
  background: #f1f5f9;
  display: flex;
  flex-direction: column;
}

.admin-header {
  height: 64px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  display: flex;
  align-items: center;
  padding: 0 24px;
  z-index: 10;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .logo-icon {
      font-size: 24px;
      color: #3b82f6;
    }
    
    .logo-text {
      font-size: 18px;
      font-weight: 800;
      color: #1e293b;
      letter-spacing: -0.01em;
    }
  }
}

.admin-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.admin-sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #e2e8f0;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  .menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #64748b;
    font-weight: 500;
    
    &:hover {
      background: #f8fafc;
      color: #3b82f6;
    }
    
    &.active {
      background: #eff6ff;
      color: #3b82f6;
      font-weight: 700;
    }
    
    .el-icon {
      font-size: 20px;
    }
  }
}

.admin-main {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  background: #f8fafc;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  
  h2 {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 8px 0;
  }
  
  p {
    font-size: 14px;
    color: #64748b;
    margin: 0;
  }
}

.component-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid white;
  border-radius: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03);
  overflow: hidden;
}

/* 动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
