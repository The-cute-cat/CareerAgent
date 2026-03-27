<script setup>
// 侧边栏组件，包含应用 Logo 和导航菜单
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  House,
  Document,
  DataAnalysis,
  User,
  Menu as IconMenu,
  TrendCharts,
  Setting
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 当前激活的菜单项，根据路由路径自动计算
const activeIndex = computed(() => {
  return route.path
})

// 菜单点击跳转
const handleSelect = (index) => {
  router.push(index)
}

// 菜单配置项 (方便后续扩展)
const menuItems = [
  { index: '/', icon: House, text: '首页' },
  { index: '/career-form', icon: Document, text: '能力画像' },
  { index: '/job-matching', icon: TrendCharts, text: '人岗匹配' },
  { index: '/report', icon: DataAnalysis, text: '生涯报告' },
  { index: '/development-map', icon: User, text: '发展图谱' }
]
</script>

<template>
  <div class="sidebar-container">
    <div class="logo-wrapper">
      <div class="logo-icon-box">
        <el-icon :size="20" color="#fff"><IconMenu /></el-icon>
      </div>
      <span class="logo-text">AI Career</span>
    </div>
    
    <div class="menu-wrapper">
      <el-menu
        :default-active="activeIndex"
        class="side-menu"
        :unique-opened="true"
        @select="handleSelect"
      >
        <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index" class="custom-menu-item">
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>
            <span class="menu-text">{{ item.text }}</span>
          </template>
        </el-menu-item>
      </el-menu>
    </div>
  </div>
</template>

<style scoped>
.sidebar-container {
  height: 100%;
  background: transparent;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 100;
}

.logo-wrapper {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: transparent;
  margin-bottom: 10px;
}

.logo-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409EFF 0%, #764BA2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(64, 158, 255, 0.25);
}

.logo-text {
  margin-left: 14px;
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #2b3240 0%, #409EFF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.menu-wrapper {
  flex: 1;
  padding: 10px 16px;
  overflow-y: auto;
}

.side-menu {
  border-right: none;
  background: transparent;
}

.custom-menu-item {
  height: 52px;
  line-height: 52px;
  border-radius: 12px;
  margin-bottom: 8px;
  color: #606266;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.custom-menu-item:hover {
  background: rgba(64, 158, 255, 0.08);
  color: #409EFF;
  transform: translateX(4px);
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.1) 0%, rgba(64, 158, 255, 0.02) 100%) !important;
  color: #409EFF !important;
  font-weight: 600;
}

:deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 4px;
  border-radius: 4px;
  background: #409EFF;
}

.side-menu::-webkit-scrollbar {
  width: 0;
}

.menu-text {
  font-size: 15px;
  margin-left: 4px;
}
</style>
