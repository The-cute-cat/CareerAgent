<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  House,
  Guide,
  Connection,
  User
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const tabs = [
  { label: '首页', icon: House, path: '/' },
  { label: '职位', icon: Guide, path: '/job-matching' },
  { label: '路径', icon: Connection, path: '/development-map' },
  { label: '我的', icon: User, path: '/profile' }
]

const activeTab = computed(() => route.path)

const handleTabClick = (path: string) => {
  router.push(path)
}
</script>

<template>
  <nav class="mobile-tab-bar">
    <div
      v-for="tab in tabs"
      :key="tab.path"
      class="tab-item"
      :class="{ active: activeTab === tab.path }"
      @click="handleTabClick(tab.path)"
    >
      <el-icon class="tab-icon">
        <component :is="tab.icon" />
      </el-icon>
      <span class="tab-label">{{ tab.label }}</span>
    </div>
  </nav>
</template>

<style scoped lang="scss">
.mobile-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: space-around;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.02);
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom);
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #94a3b8;
  transition: all 0.3s ease;
  cursor: pointer;
  flex: 1;

  &.active {
    color: #1e62c5;
    
    .tab-icon {
      transform: translateY(-2px);
    }
  }
}

.tab-icon {
  font-size: 24px;
}

.tab-label {
  font-size: 12px;
  font-weight: 600;
}
</style>
