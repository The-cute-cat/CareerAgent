<script setup lang="ts">
import { ref, provide, onMounted, onUnmounted } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import CHeader from '@/components/CHeader.vue'
import MobileTabBar from '@/components/MobileTabBar.vue'
import ChatBot from '@/components/ChatBot.vue'

const sidebarRef = ref<InstanceType<typeof Sidebar>>()

const isMobile = ref(false)
const mobileDrawerVisible = ref(false)

const handleResize = () => {
  if (typeof window !== 'undefined') {
    isMobile.value = window.innerWidth <= 768
    if (!isMobile.value) {
      mobileDrawerVisible.value = false
    }
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

const toggleMobileDrawer = () => {
  mobileDrawerVisible.value = !mobileDrawerVisible.value
}

provide('toggleMobileDrawer', toggleMobileDrawer)
provide('isMobileLayout', isMobile)
</script>

<template>
  <div class="app-background">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>
  </div>
  <el-container class="layout-container">
    <!-- 移动端侧边栏抽屉 -->
    <el-drawer
      v-if="isMobile"
      v-model="mobileDrawerVisible"
      direction="ltr"
      size="260px"
      :with-header="false"
      class="mobile-sidebar-drawer"
    >
      <Sidebar ref="sidebarRef" @close-drawer="mobileDrawerVisible = false" />
    </el-drawer>

    <!-- 桌面端侧边栏 -->
    <el-aside v-else :width="sidebarRef?.collapsed ? '80px' : '260px'" class="sidebar-wrapper">
      <Sidebar ref="sidebarRef" />
    </el-aside>

    <!-- 右侧主内容区 -->
    <el-container class="main-wrapper">
      <!-- 顶部 CHeader -->
      <CHeader />

      <!-- 页面内容 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- AI 助手悬浮窗 -->
    <!-- <ChatBot /> -->

    <!-- 移动端底部导航 -->
    <MobileTabBar v-if="isMobile" />
  </el-container>
</template>

<style scoped>
/* 动态背景特效 */
.app-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  background-color: #f3f6f9;
  overflow: hidden;
}

.blob {
  position: absolute;
  filter: blur(80px);
  z-index: -1;
  opacity: 0.6;
  border-radius: 50%;
  animation: float 20s infinite ease-in-out alternate;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: #f1f5f9;
  top: -100px;
  left: -100px;
}

.blob-2 {
  width: 500px;
  height: 500px;
  background: #e2e8f0;
  bottom: -150px;
  right: -100px;
  animation-delay: -5s;
}

.blob-3 {
  width: 300px;
  height: 300px;
  background: #cbd5e1;
  top: 40%;
  left: 30%;
  animation-delay: -10s;
}

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(50px, 30px) scale(1.1); }
  100% { transform: translate(-30px, 60px) scale(0.9); }
}

.layout-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  overflow: hidden;
  background: transparent;
}

.sidebar-wrapper {
  flex-shrink: 0;
  z-index: 10;
  border-right: 1px solid rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: transparent;
}

.main-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  overflow-x: hidden;
  scroll-behavior: smooth;
  transition: all 0.3s ease;
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px 16px 80px; /* 底部预留 TabBar 空间 */
  }
}

/* 页面切换动画 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 滚动条样式 */
.main-content::-webkit-scrollbar {
  width: 8px;
}

.main-content::-webkit-scrollbar-track {
  background: transparent;
}

.main-content::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.3);
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.5);
}

:deep(.el-drawer.mobile-sidebar-drawer) {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
:deep(.el-drawer.mobile-sidebar-drawer .el-drawer__body) {
  padding: 0;
}
</style>
