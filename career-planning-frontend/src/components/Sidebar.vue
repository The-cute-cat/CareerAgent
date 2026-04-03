<script setup>
// 侧边栏组件，包含应用 Logo 和导航菜单
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  House, Document, DataAnalysis,
  User, TrendCharts, Setting,
  Star, Collection, Position,
  Fold, Expand, Guide, Connection, Calendar,
  Memo, Timer, Finished, Reading,
  Promotion, MagicStick, Files
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const collapsed = ref(false)

const handleResize = () => {
  if (typeof window !== 'undefined') {
    collapsed.value = window.innerWidth <= 992
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

// 当前激活的菜单项，根据路由路径自动计算
const activeIndex = computed(() => {
  const path = route.path
  // 处理面试路由的子路径匹配，确保父级在有子项激活时也能正确映射逻辑（如果需要）
  if (path.startsWith('/interviews/')) return path
  return path
})

const handleSelect = (index) => {
  if (index && index !== 'spacer' && index.startsWith('/')) {
    router.push(index)
  }
}

const toggleCollapse = () => {
  collapsed.value = !collapsed.value
}

const menuItems = [
  { title: '核心功能', isGroup: true },
  { index: '/', icon: House, text: '首页' },
  {
    index: '/career-form-group',
    icon: Document,
    text: '能力画像',
    children: [
      { index: '/career-form/resume', icon: Document, text: '我的简历' },
      { index: '/career-form/template', icon: Files, text: '导出简历' }
    ]
  },
  { index: '/job-matching', icon: TrendCharts, text: '人岗匹配' },
  { index: '/development-map', icon: Position, text: '发展图谱' },
  { index: '/report', icon: DataAnalysis, text: '生涯报告' },
  { title: '知识与探索', isGroup: true },
  { index: '/knowledge-base', icon: Collection, text: '岗位知识库' },
  { index: '/favorites', icon: Star, text: '我的收藏' },
  { title: '系统与管理', isGroup: true },
  { index: '/profile', icon: User, text: '个人中心' },
  { index: '/admin', icon: Setting, text: '系统管理' }
]

defineExpose({ collapsed })
</script>

<template>
  <div class="sidebar-container" :class="{ collapsed }">
    <div class="logo-section">
      <div class="logo-icon-box">
        <img src="../assets/1234.png" alt="logo" />
      </div>
      <transition name="text-fade">
        <span v-if="!collapsed" class="logo-text">职路 Agent</span>
      </transition>
      <el-button class="collapse-toggle" circle size="small" @click="toggleCollapse">
        <el-icon :size="14">
          <component :is="collapsed ? Expand : Fold" />
        </el-icon>
      </el-button>
    </div>

    <!-- 菜单区域 -->
    <div class="menu-wrapper">
      <el-menu :default-active="activeIndex" class="side-menu" :unique-opened="true" :collapse="collapsed"
        @select="handleSelect">
        <template v-for="(item, i) in menuItems" :key="i">
          <!-- 分隔符 -->
          <div v-if="item.isSpacer" class="menu-spacer"></div>

          <!-- 分组标题 -->
          <div v-else-if="item.isGroup" class="menu-group-title">
            <span>{{ item.title }}</span>
          </div>

          <!-- 带有子菜单的项 -->
          <el-sub-menu v-else-if="item.children" :index="item.index" class="custom-sub-menu">
            <template #title>
              <el-icon class="menu-icon">
                <component :is="item.icon" />
              </el-icon>
              <span class="menu-text">{{ item.text }}</span>
            </template>
            <el-menu-item v-for="child in item.children" :key="child.index" :index="child.index"
              class="custom-menu-item sub-item">
              <el-icon class="menu-icon">
                <component :is="child.icon" />
              </el-icon>
              <template #title>
                <span class="menu-text">{{ child.text }}</span>
              </template>
            </el-menu-item>
          </el-sub-menu>

          <!-- 普通菜单项目 -->
          <template v-else>
            <el-tooltip v-if="collapsed" :content="item.text" placement="right" :offset="8" :show-after="400">
              <el-menu-item :index="item.index" class="custom-menu-item">
                <el-icon class="menu-icon">
                  <component :is="item.icon" />
                </el-icon>
                <template #title>
                  <span class="menu-text">{{ item.text }}</span>
                </template>
              </el-menu-item>
            </el-tooltip>
            <el-menu-item v-else :index="item.index" class="custom-menu-item">
              <el-icon class="menu-icon">
                <component :is="item.icon" />
              </el-icon>
              <template #title>
                <span class="menu-text">{{ item.text }}</span>
              </template>
            </el-menu-item>
          </template>
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

.logo-section {
  display: flex;
  align-items: center;
  padding: 24px 16px 36px 20px;
  /* 增加底部 padding 以拉开与菜单的距离 */
  gap: 12px;
  flex-shrink: 0;
}

.sidebar-container.collapsed .logo-section {
  flex-direction: column;
  justify-content: center;
  padding: 16px 8px 12px;
  gap: 8px;
}

.logo-icon-box {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon-box img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.logo-text {
  font-size: 19px;
  font-weight: 800;
  background: linear-gradient(135deg, #2c3e50 20%, #409eff 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
  white-space: nowrap;
  line-height: 1.2;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.text-fade-enter-active,
.text-fade-leave-active {
  transition: opacity 0.15s ease;
}

.text-fade-enter-from,
.text-fade-leave-to {
  opacity: 0;
}

.collapse-toggle {
  margin-left: auto;
  border: 1px solid #e2e8f0;
  background: rgba(255, 255, 255, 0.8);
  color: #64748b;
  width: 32px;
  height: 32px;
  transition: all 0.25s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

.sidebar-container.collapsed .collapse-toggle {
  margin-left: 0;
}

.collapse-toggle:hover {
  background: #f1f5f9;
  color: #3b82f6;
  border-color: #cbd5e1;
  transform: scale(1.05);
}

.menu-wrapper {
  flex: 1;
  padding: 0 16px 20px 16px;
  overflow-y: auto;
  transition: padding 0.3s ease;
}

.sidebar-container.collapsed .menu-wrapper {
  padding: 0 10px 20px;
}

.side-menu {
  border-right: none;
  background: transparent;
}

.menu-spacer {
  height: 1px;
  background: rgba(0, 0, 0, 0.05);
  margin: 16px 12px;
}

.menu-group-title {
  padding: 20px 16px 8px;
  font-size: 15px;
  font-weight: 500;
  color: #94a3b8;
  line-height: 1.5;
}

.menu-group-title:first-child {
  padding-top: 8px;
}

.sidebar-container.collapsed .menu-group-title {
  display: none;
}

.custom-menu-item,
:deep(.custom-submenu > .el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  border-radius: 12px;
  margin-bottom: 10px;
  /* 增加间距以提升档次感 */
  color: #475569;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.custom-menu-item:hover,
:deep(.el-sub-menu__title:hover) {
  background: rgba(59, 130, 246, 0.06) !important;
  color: #3b82f6 !important;
  transform: translateX(4px);
}

.custom-menu-item.sub-item {
  padding-left: 48px !important;
  height: 40px;
  line-height: 40px;
  margin-top: 6px;
  /* 增加二级菜单的上方间距 */
}

.custom-menu-item.sub-item:hover::before {
  content: '';
  position: absolute;
  left: 32px;
  top: 12px;
  bottom: 12px;
  width: 2px;
  background: #3b82f6;
  border-radius: 2px;
}

.sidebar-container.collapsed .custom-menu-item:hover,
.sidebar-container.collapsed :deep(.el-sub-menu__title:hover) {
  transform: none;
}

.menu-icon,
.submenu-icon {
  font-size: 18px;
  margin-right: 10px;
  transition: all 0.3s ease;
}

.custom-menu-item:hover .menu-icon,
:deep(.custom-submenu > .el-sub-menu__title:hover .menu-icon) {
  transform: scale(1.1);
  color: #3b82f6;
}

/* ========== 激活状态 ========== */
:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.12) 0%, rgba(59, 130, 246, 0.02) 100%) !important;
  color: #3b82f6 !important;
  font-weight: 700;
}

/* 父级菜单在子级激活时的样式 */
:deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: #3b82f6 !important;
  font-weight: 700;
}

:deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 10px;
  bottom: 10px;
  width: 4px;
  border-radius: 4px;
  background: #3b82f6;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.6);
  z-index: 2;
}

.sidebar-container.collapsed :deep(.el-menu-item.is-active)::before {
  left: 6px;
}

.custom-submenu-item {
  height: 42px;
  line-height: 42px;
  margin: 4px 0 4px 10px;
  border-radius: 12px;
  color: #64748b;
}

.custom-submenu-item .submenu-icon {
  font-size: 16px;
}

:deep(.custom-submenu .el-menu) {
  background: transparent;
}

:deep(.custom-submenu .el-sub-menu__icon-arrow) {
  color: #94a3b8;
}

.side-menu::-webkit-scrollbar {
  width: 0;
}

.menu-text {
  font-size: 14px;
  letter-spacing: 0.3px;
}

.sidebar-container.collapsed :deep(.el-menu--collapse) {
  border-right: none;
}

.sidebar-container.collapsed :deep(.el-menu--collapse .el-menu-item),
.sidebar-container.collapsed :deep(.el-menu--collapse .el-sub-menu__title) {
  padding: 0 !important;
  justify-content: center;
}

.sidebar-container.collapsed :deep(.el-menu--collapse .el-menu-item .menu-icon),
.sidebar-container.collapsed :deep(.el-menu--collapse .el-sub-menu__title .menu-icon) {
  margin-right: 0;
  font-size: 20px;
}
</style>
