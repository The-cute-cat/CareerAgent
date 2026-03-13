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
  { index: '/upload', icon: Document, text: '能力画像' },
  { index: '/match', icon: TrendCharts, text: '人岗匹配' },
  { index: '/report', icon: DataAnalysis, text: '生涯报告' },
  { index: '/development-map', icon: User, text: '发展图谱' },
  { index: '/profile', icon: Setting, text: '个人中心' }
]
</script>

<template>
  <div class="sidebar-container">
    <div class="logo-wrapper">
      <el-icon :size="24" color="#409EFF"><IconMenu /></el-icon>
      <span class="logo-text">职业规划智能体</span>
    </div>
    
    <el-menu
      :default-active="activeIndex"
      class="side-menu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      :unique-opened="true"
      @select="handleSelect"
    >
      <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index">
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.text }}</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<style scoped>
.sidebar-container {
  height: 100%;
  background-color: #304156;
  display: flex;
  flex-direction: column;
}

.logo-wrapper {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4b;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #3d4a5a;
}

.logo-text {
  margin-left: 10px;
}

.side-menu {
  border-right: none;
  flex: 1;
  overflow-y: auto;
}

/* 隐藏滚动条但保留功能 */
.side-menu::-webkit-scrollbar {
  width: 0;
}
</style>
