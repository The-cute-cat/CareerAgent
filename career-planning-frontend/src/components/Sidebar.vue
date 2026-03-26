<script setup>
// 侧边栏组件，包含应用 Logo 和导航菜单
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  House,
  Document,
  DataAnalysis,
  User,
  TrendCharts,
  Setting,
  Star,
  Collection,
  Position
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

// 菜单配置项
const menuItems = [
  { title: '核心功能', isGroup: true },
  { index: '/', icon: House, text: '首页' },
  { index: '/career-form', icon: Document, text: '能力画像' },
  { index: '/job-matching', icon: TrendCharts, text: '人岗匹配' },
  { index: '/report', icon: DataAnalysis, text: '生涯报告' },
  { index: '/development-map', icon: Position, text: '发展图谱' },
  { title: '知识与探索', isGroup: true },
  { index: '/knowledge-base', icon: Collection, text: '岗位知识库' },
  { index: '/favorites', icon: Star, text: '我的收藏' },
  { title: '系统与管理', isGroup: true },
  { index: '/profile', icon: User, text: '个人中心' },
  { index: '/admin', icon: Setting, text: '系统管理' }
]
</script>

<template>
  <div class="sidebar-container">
    <div class="logo-wrapper">
      <div class="logo-icon-box" style="background: transparent; box-shadow: none;">
        <img src="../assets/1234.png" alt="logo" style="width: 100%; height: 100%; object-fit: contain;" />
      </div>
      <span class="logo-text">职引未来</span>
    </div>
    
    <div class="menu-wrapper">
      <el-menu
        :default-active="activeIndex"
        class="side-menu"
        :unique-opened="true"
        @select="handleSelect"
      >
        <template v-for="(item, i) in menuItems" :key="i">
          <!-- 分组小标题 -->
          <div v-if="item.isGroup" class="menu-group-title">
            {{ item.title }}
          </div>
          <!-- 菜单项目 -->
          <el-menu-item v-else :index="item.index" class="custom-menu-item">
            <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
            <template #title>
              <span class="menu-text">{{ item.text }}</span>
            </template>
          </el-menu-item>
        </template>
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
  margin-bottom: 12px;
}

.logo-icon-box {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  margin-left: 16px;
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(135deg, #1e293b 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.menu-wrapper {
  flex: 1;
  padding: 0 16px 20px 16px;
  overflow-y: auto;
}

.side-menu {
  border-right: none;
  background: transparent;
}

.menu-group-title {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  margin: 16px 0 8px 12px;
  letter-spacing: 0.5px;
}

.custom-menu-item {
  height: 48px;
  line-height: 48px;
  border-radius: 12px;
  margin-bottom: 4px;
  color: #475569;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.custom-menu-item:hover {
  background: rgba(59, 130, 246, 0.06);
  color: #3b82f6;
  transform: translateX(4px);
}

.menu-icon {
  font-size: 18px;
  margin-right: 10px;
  transition: all 0.3s ease;
}

.custom-menu-item:hover .menu-icon {
  transform: scale(1.1);
  color: #3b82f6;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.02) 100%) !important;
  color: #3b82f6 !important;
  font-weight: 600;
}

:deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 4px;
  border-radius: 4px;
  background: #3b82f6;
  box-shadow: 0 0 6px rgba(59, 130, 246, 0.4);
}

.side-menu::-webkit-scrollbar {
  width: 0;
}

.menu-text {
  font-size: 14px;
  letter-spacing: 0.3px;
}
</style>
