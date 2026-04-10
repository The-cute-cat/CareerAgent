<script setup lang="ts">
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/modules/user'
import { useAppStore } from '@/stores/modules/app'
import { getAccountPointsService, getUserInfoService } from '@/api/points'
import { ArrowDown, User, SwitchButton, Menu as MenuIcon, Sunny, Moon } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const isMobileLayout = inject('isMobileLayout', ref(false))
const toggleMobileDrawer = inject('toggleMobileDrawer', () => { })

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

const currentTitle = computed(() => route.meta.title || '欢迎使用职业规划智能体')
const isLoggedIn = computed(() => userStore.isLoggedIn)
const userName = computed(
  () => (userStore.userInfo as any)?.name || userStore.userInfo?.nickname || userStore.userInfo?.username || '用户'
)
const userAvatar = computed(() => (userStore.userInfo as any)?.avatar || '')

const userPoints = computed(() => {
  const rawPoints = Number(
    (userStore.userInfo as any)?.pointsBalance ??
    (userStore.userInfo as any)?.points ??
    (userStore.userInfo as any)?.score ??
    500
  )
  return Number.isNaN(rawPoints) ? 500 : rawPoints
})

const memberType = computed(() => ((userStore.userInfo as any)?.memberType || 'normal').toLowerCase())

const memberLabel = computed(() => {
  const memberMap: Record<string, string> = {
    normal: '普通用户',
    monthly: '月度会员',
    quarter: '季度会员',
    quarterly: '季度会员',
    yearly: '年度会员',
    annual: '年度会员'
  }
  return memberMap[memberType.value] || '普通用户'
})

const memberBadgeClass = computed(() => {
  const classMap: Record<string, string> = {
    monthly: 'is-monthly',
    quarter: 'is-quarter',
    quarterly: 'is-quarter',
    yearly: 'is-yearly',
    annual: 'is-yearly'
  }
  return classMap[memberType.value] || 'is-normal'
})

const handleLogout = () => {
  userStore.clearUserInfo()
  router.push('/login')
}

const syncAccountPoints = async () => {
  console.log("syncAccountPoints", userStore.userInfo?.id)

  const userId = Number(userStore.userInfo?.id)
  if (!userStore.isLoggedIn || !userId) return

  try {
    const result = await getAccountPointsService(userId)
    const payload = result.data

    if (payload?.code !== 200 || !payload.data || !userStore.userInfo) {
      return
    }
    console.log('同步账号积分', payload.data);

    userStore.userInfo = {
      ...userStore.userInfo,
      pointsBalance: payload.data.pointsBalance
    } as any
  } catch (error) {
    console.warn('同步账号积分失败', error)
  }
}

const syncUserInfo = async () => {
  console.log("syncUserInfo", userStore.userInfo?.id)
  const userId = Number(userStore.userInfo?.id)
  if (!userStore.isLoggedIn || !userId) return

  try {
    const result = await getUserInfoService(userId)
    const payload = result.data

    if (payload?.code !== 200 || !payload.data || !userStore.userInfo) {
      return
    }
    console.log('同步用户信息', payload.data);

    userStore.userInfo = {
      ...userStore.userInfo
    } as any
  } catch (error) {
    console.warn('同步用户信息失败', error)
  }
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    confirmLogout()
  } else if (command === 'profile' || command === 'membership') {
    router.push({ path: '/profile', query: { tab: 'profile' } })
  }
}

const confirmLogout = () => {
  ElMessageBox.confirm('确认退出？', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      userStore.clearUserALLInfo()
      ElMessage({
        type: 'success',
        message: '退出成功'
      })
      handleLogout()
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '取消退出'
      })
    })
}

onMounted(() => {
  syncAccountPoints()
  syncUserInfo()
})

watch(
  () => (userStore.userInfo as any)?.user_id || userStore.userInfo?.id,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      syncAccountPoints()
    }
  }
)
</script>

<template>
  <header class="header glass-header">
    <div class="header-left">
      <el-icon v-if="isMobileLayout" class="mobile-menu-btn" @click="toggleMobileDrawer">
        <MenuIcon />
      </el-icon>
      <div class="breadcrumb">
        <span class="app-name">职引未来</span>
        <!--<span class="app-name">职悟 Agent</span>-->
        <span class="divider">/</span>
        <span class="page-title">{{ currentTitle }}</span>
      </div>
    </div>
    <div class="header-right">
      <!-- 环境背景色与主题切换 -->
      <div class="theme-switch-wrapper">
        <el-tooltip content="自定义背景色" placement="bottom">
          <el-color-picker v-model="appStore.customBgColor" size="small" show-alpha class="bg-color-picker" />
        </el-tooltip>
        <el-switch v-model="appStore.isDarkMode" inline-prompt :active-icon="Moon" :inactive-icon="Sunny"
          class="theme-toggle-switch" />
      </div>

      <div v-if="!isLoggedIn" class="auth-buttons">
        <el-button class="custom-btn-primary" type="primary" round @click="router.push('/login')">登录</el-button>
        <el-button class="custom-btn-default" round @click="router.push('/register')">注册</el-button>
      </div>

      <el-dropdown v-else @command="handleCommand" :show-timeout="0">
        <div class="user-info">
          <div class="user-avatar">
            <img v-if="userAvatar" :src="userAvatar" alt="avatar" class="user-avatar-image" />
            <span v-else>{{ userName.charAt(0).toUpperCase() }}</span>
          </div>

          <div class="user-main">
            <div class="user-main-top">
              <span class="user-name">{{ userName }}</span>
              <span class="member-badge" :class="memberBadgeClass">{{ memberLabel }}</span>
            </div>
            <div class="user-main-bottom">
              <span class="points-badge">积分 {{ userPoints }}</span>
            </div>
          </div>

          <el-icon class="dropdown-icon">
            <ArrowDown />
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu class="custom-dropdown">
            <el-dropdown-item command="profile">
              <el-icon>
                <User />
              </el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item divided command="logout" class="logout-item">
              <el-icon>
                <SwitchButton />
              </el-icon>
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
  height: 72px;
  padding: 0 28px;
  background: var(--color-background-soft);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
  z-index: 50;
  transition: background-color 0.5s ease, border-color 0.5s ease;
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
  background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 16px;
  letter-spacing: 0.5px;
}

.divider {
  color: #c0c4cc;
}

.page-title {
  color: var(--color-text);
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-switch-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-right: 16px;
  border-right: 1px solid var(--color-border);
}

.bg-color-picker :deep(.el-color-picker__trigger) {
  border: 1px solid var(--color-border);
  background: var(--color-background-soft);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.bg-color-picker :deep(.el-color-picker__trigger):hover {
  border-color: #409eff;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.2);
}

.theme-toggle-switch {
  --el-switch-on-color: #334155;
  --el-switch-off-color: #f1f5f9;
  --el-switch-border-color: var(--color-border);
}

.theme-toggle-switch :deep(.el-switch__core) {
  border: 1px solid var(--color-border);
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
  padding: 8px 14px;
  border-radius: 22px;
  cursor: pointer;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  /* 移除触发后的焦点轮廓，防止出现黑框 */
}

.user-info:focus,
.user-info:focus-visible {
  outline: none;
  /* 彻底消除不同浏览器（如 Chrome）下的默认焦点框 */
}

.user-info:hover {
  background: var(--color-background-soft);
  border-color: rgba(64, 158, 255, 0.3);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff 0%, #1677ff 100%);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
  flex-shrink: 0;
  overflow: hidden;
}

.user-avatar-image {
  display: block;
  width: 100%;
  height: 100%;
  max-width: 36px;
  max-height: 36px;
  object-fit: cover;
}

.user-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.user-main-top,
.user-main-bottom {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-size: 14px;
  color: var(--color-heading);
  font-weight: 600;
  max-width: 96px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.points-badge,
.member-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 22px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.points-badge {
  color: #b26a00;
  background: linear-gradient(135deg, rgba(255, 218, 102, 0.95), rgba(255, 237, 180, 0.95));
  box-shadow: inset 0 0 0 1px rgba(255, 185, 0, 0.18);
}

.member-badge {
  color: #606266;
  background: rgba(144, 147, 153, 0.1);
}

.member-badge.is-normal {
  color: #606266;
  background: rgba(144, 147, 153, 0.14);
}

.member-badge.is-monthly {
  color: #1d4ed8;
  background: linear-gradient(135deg, rgba(219, 234, 254, 0.95), rgba(191, 219, 254, 0.95));
}

.member-badge.is-quarter {
  color: #6d28d9;
  background: linear-gradient(135deg, rgba(237, 233, 254, 0.95), rgba(221, 214, 254, 0.95));
}

.member-badge.is-yearly {
  color: #9a6700;
  background: linear-gradient(135deg, rgba(255, 244, 204, 0.98), rgba(255, 224, 130, 0.98));
}

.dropdown-icon {
  color: #909399;
  font-size: 12px;
  transition: transform 0.3s ease;
  margin-left: 2px;
}

.user-info:hover .dropdown-icon {
  transform: rotate(180deg);
  color: #409eff;
}

:deep(.custom-dropdown) {
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  background: var(--color-background-soft);
}

:deep(.logout-item) {
  color: #f56c6c !important;
}

@media (max-width: 768px) {
  .glass-header {
    height: auto;
    min-height: 72px;
    padding: 12px 16px;
    gap: 12px;
  }

  .header-left {
    gap: 12px;
  }

  .mobile-menu-btn {
    font-size: 20px;
    color: #409eff;
    cursor: pointer;
    padding: 4px;
    border-radius: 6px;
    background: rgba(64, 158, 255, 0.1);
  }

  .breadcrumb {
    gap: 8px;
    font-size: 14px;
  }

  .page-title {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .user-info {
    padding: 8px 12px;
  }

  .user-name {
    max-width: 72px;
  }
}
</style>
