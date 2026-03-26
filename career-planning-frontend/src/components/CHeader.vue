<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/modules/user'
import { ArrowDown, User, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } fromment-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const currentTitle = computed(() => route.meta.title || '欢迎使用职业规划智能体')
const isLoggedIn = computed(() => userStore.isLoggedIn)
const userName = computed(() => userStore.userInfo?.nickname || userStore.userInfo?.username || '用户')

const handleLogout = () => {
  userStore.clearUserInfo()
  router.push('/login')
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    confirmLogout()
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

const confirmLogout = () => {
  ElMessageBox.confirm(
    '确认退出？',
    '提示',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      userStore.clearUserALLInfo()
      ElMessage({
        type: 'success',
        message: '退出成功',
      })
      handleLogout()
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '取消退出',
      })
    })
}
</script>

<template>
  <header class="header glass-header">
    <div class="header-left">
      <div class="breadcrumb">
        <span class="app-name">AI Career Agent</span>
        <span class="divider">/</span>
        <span class="page-title">{{ currentTitle }}</span>
      </div>
    </div>
    <div class="header-right">
      <!-- 未登录状态：显示登录/注册按钮 -->
      <div v-if="!isLoggedIn" class="auth-buttons">
        <el-button class="custom-btn-primary" type="primary" round @click="router.push('/login')">登录</el-button>
        <el-button class="custom-btn-default" round @click="router.push('/register')">注册</el-button>
      </div>

      <!-- 已登录状态：显示用户信息下拉菜单 -->
      <el-dropdown v-else @command="handleCommand" trigger="click">
        <div class="user-info">
          <div class="user-avatar">
            {{ userName.charAt(0).toUpperCase() }}
          </div>
          <span class="user-name">{{ userName }}</span>
          <el-icon class="dropdown-icon">
            <ArrowDown />
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu class="custom-dropdown">
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item divided command="logout" class="logout-item">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<style scoped>
.glass-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 28px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
}

.app-name {
  font-weight: 700;
  background: linear-gradient(135deg, #409eff 0%, #764BA2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 16px;
  letter-spacing: 0.5px;
}

.divider {
  color: #c0c4cc;
}

.page-title {
  color: #606266;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.custom-btn-primary {
  background: linear-gradient(135deg, #409eff 0%, #1677ff 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.custom-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

.custom-btn-default {
  border: 1px solid rgba(64, 158, 255, 0.5);
  color: #409eff;
  background: transparent;
  transition: all 0.3s ease;
}

.custom-btn-default:hover {
  background: rgba(64, 158, 255, 0.1);
  color: #1677ff;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 14px;
  border-radius: 20px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff 0%, #1677ff 100%);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
}

.user-name {
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.dropdown-icon {
  color: #909399;
  font-size: 12px;
  transition: transform 0.3s ease;
}

.user-info:hover .dropdown-icon {
  transform: rotate(180deg);
  color: #409eff;
}

:deep(.custom-dropdown) {
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9);
}

:deep(.logout-item) {
  color: #f56c6c !important;
}

:deep(.logout-item:hover) {
  background: rgba(245, 108, 108, 0.1) !important;
  color: #f56c6c !important;
}
</style>
