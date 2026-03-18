<script setup lang="ts">
import Sidebar from '@/components/Sidebar.vue'
import CHeader from '@/components/CHeader.vue'
import ChatBot from '@/components/ChatBot.vue'
</script>

<template>
  <el-container class="layout-container">
    <!-- 左侧侧边栏 -->
    <el-aside width="220px" class="sidebar-wrapper">
      <Sidebar />
    </el-aside>

    <!-- 右侧主内容区 -->
    <el-container class="main-wrapper">
      <!-- 顶部 CHeader -->
      <CHeader />

      <!-- 页面内容 -->
      <el-main class="main-content">
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>

    <!-- AI 助手悬浮窗 -->
    <ChatBot />
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  overflow: hidden;
}

.sidebar-wrapper {
  background: linear-gradient(180deg, #1a1f36 0%, #243042 100%);
  flex-shrink: 0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #f0f2f5;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
}

.content-wrapper {
  background: #ffffff;
  border-radius: 8px;
  min-height: calc(100vh - 140px);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滚动条样式 */
.main-content::-webkit-scrollbar {
  width: 6px;
}

.main-content::-webkit-scrollbar-track {
  background: transparent;
}

.main-content::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>
