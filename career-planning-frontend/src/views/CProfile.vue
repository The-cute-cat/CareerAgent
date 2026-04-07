<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/modules/user'
import { logout as userLogoutService } from '@/api/user'
import { getAccountPointsService } from '@/api/points'
import type { AccountPointsData } from '@/api/points'
import { getUserInfo } from '@/api/user'

import ProfileInfoPanel from '../components/CProfile_Component/ProfileInfoPanel.vue'
import ProfileSidebar from '../components/CProfile_Component/ProfileSidebar.vue'
import ProfileDashboard from '../components/CProfile_Component/ProfileDashboard.vue'
import MemberPlanPanel from '../components/CProfile_Component/MemberPlanPanel.vue'
import InviteFriendsPanel from '../components/CProfile_Component/InviteFriendsPanel.vue'
import FeedbackPanel from '../components/CProfile_Component/FeedbackPanel.vue'
import MoreSettingsPanel from '../components/CProfile_Component/MoreSettingsPanel.vue'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const sidebarCollapsed = ref(false)

const activeMenu = ref('dashboard')
const isMobileLayout = ref(false)
const isMobileMenuOpen = ref(true)
const accountPoints = ref<AccountPointsData | null>(null)
const pointsLoading = ref(false)

const isSettingsCenter = computed(() => route.path.includes('/settings'))

const handleResize = () => {
  if (typeof window !== 'undefined') {
    isMobileLayout.value = window.innerWidth <= 768
    if (!isMobileLayout.value) {
      isMobileMenuOpen.value = true
    }
  }
}

watch(activeMenu, () => {
  if (isMobileLayout.value) {
    isMobileMenuOpen.value = false
  }
})

const storedUser = userStore.userInfo || {}
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const userInfo = ref({
  name: (storedUser as any)?.name || (storedUser as any)?.nickname || (storedUser as any)?.username || `用户${userStore.userInfo?.id || 5442}`,
  avatar: (storedUser as any)?.avatar || defaultAvatar,
  signature: (storedUser as any)?.signature || (storedUser as any)?.info || '利用职路AI,为更好的自己',
  gender: (storedUser as any)?.gender || '男',
  education: (storedUser as any)?.education || '本科',
  experience: (storedUser as any)?.experience || '在校生',
  industries: (storedUser as any)?.industries || '互联网、电子商务、计算机',
  jobs: (storedUser as any)?.jobs || 'Java、前端开发工程师'
})

const displayPoints = computed(() => {
  if (typeof accountPoints.value?.pointsBalance === 'number') {
    return accountPoints.value.pointsBalance
  }

  const storePoints = Number((userStore.userInfo as any)?.points)
  return Number.isNaN(storePoints) ? 300 : storePoints
})

const allMenus = [
  { key: 'dashboard', label: '我的主页', onlyProfile: true },
  { key: 'profile', label: '个人资料', onlyProfile: true },
  { key: 'member', label: '会员计划', onlyProfile: true },
  { key: 'invite', label: '邀请好友', onlyProfile: true },
  { key: 'feedback', label: '反馈建议', onlyProfile: true },
  { key: 'setting', label: '更多设置', onlyProfile: true }
]

const visibleMenus = computed(() => {
  if (isSettingsCenter.value) {
    return allMenus.filter((m: any) => m.onlySettings || m.key === 'feedback')
  }
  return allMenus.filter((m: any) => m.onlyProfile || m.key === 'feedback')
})

const pointRecords = computed(() => {
  if (!accountPoints.value) {
    return []
  }

  return [
    {
      id: 1,
      type: '当前可用积分',
      remain: accountPoints.value.pointsBalance,
      total: accountPoints.value.pointsBalance,
      expireText: '账户当前可用余额 ' + accountPoints.value.pointsBalance
    },
    {
      id: 2,
      type: '累计消耗积分',
      remain: accountPoints.value.totalConsumed,
      total: accountPoints.value.totalConsumed,
      expireText: '历史累计消耗 ' + accountPoints.value.totalConsumed
    },
    {
      id: 3,
      type: '邀请奖励积分',
      remain: accountPoints.value.referralRewardTotal,
      total: accountPoints.value.referralRewardTotal,
      expireText: `已邀请 ${accountPoints.value.referralCount == null ? 0 : accountPoints.value.referralCount} 人`
    }
  ]
})

const inviteCode = ref('ZHILU2026')

const panelTitleMap: Record<string, string> = {
  dashboard: '我的主页',
  profile: '个人资料',
  member: '会员计划',
  invite: '邀请好友',
  feedback: '反馈建议',
  setting: '更多设置'
}

const panelDescriptionMap: Record<string, string> = {
  dashboard: '欢迎回来，在这里查看你的职业成长进度与最新动态。',
  profile: '在这里完善你的资料、兴趣方向和职业偏好，让个人中心更像你的专属名片。',
  member: '查看积分权益与会员状态，了解当前账户可使用的成长资源。',
  invite: '把职业规划工具分享给朋友，一起解锁更多使用权益。',
  feedback: '告诉我们你的使用感受和改进建议，帮助产品持续变得更好。',
  setting: '统一管理隐私、协议、推荐偏好与账号相关设置。'
}

const fetchAccountPoints = async () => {
  const userId = Number(userStore.userInfo?.id)
  if (!userId) return

  pointsLoading.value = true
  try {
    const result = await getAccountPointsService(userId)
    const payload = result.data

    if (payload?.code !== 200 || !payload.data) {
      throw new Error(payload?.msg || '获取积分信息失败')
    }

    accountPoints.value = payload.data

    if (userStore.userInfo) {
      userStore.userInfo = {
        ...userStore.userInfo,
        points: payload.data.pointsBalance,
        pointsBalance: payload.data.pointsBalance
      } as any
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : '获取积分信息失败'
    ElMessage.error(message)
  } finally {
    pointsLoading.value = false
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    handleResize()
    window.addEventListener('resize', handleResize)
  }

  fetchAccountPoints()

  if (isSettingsCenter.value) {
    activeMenu.value = 'setting'
  } else {
    activeMenu.value = 'dashboard'
  }
})

watch(
  () => route.path,
  () => {
    if (isSettingsCenter.value) {
      activeMenu.value = 'setting'
    } else {
      activeMenu.value = 'dashboard'
    }
  }
)

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleResize)
  }
})

const updateUserInfo = (payload: Record<string, any>) => {
  userInfo.value = {
    ...userInfo.value,
    ...payload
  }

  if (userStore.userInfo) {
    userStore.userInfo = {
      ...userStore.userInfo,
      ...payload,
      name: payload.name ?? (userStore.userInfo as any).name,
      nickname: payload.nickname ?? userStore.userInfo.nickname,
      username: payload.username ?? userStore.userInfo.username,
      avatar: payload.avatar ?? userStore.userInfo.avatar,
      signature: payload.signature ?? (userStore.userInfo as any).signature,
      info: payload.info ?? userStore.userInfo.info
    } as any
  }

  ElMessage({
    message: '个人信息已更新',
    type: 'success',
    duration: 1800
  })
}

const confirmLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确认退出当前账号吗？退出后需要重新登录才能继续使用个人中心相关功能。',
      '退出登录',
      {
        confirmButtonText: '确认退出',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    ElMessage({
      message: '已取消退出登录',
      type: 'info',
      duration: 1800
    })
    return
  }

  try {
    await userLogoutService()
  } catch (error) {
    console.warn('退出登录接口调用失败，已执行本地退出逻辑', error)
  } finally {
    userStore.clearUserALLInfo()
    ElMessage({
      message: '已退出登录',
      type: 'success',
      duration: 1800
    })
    router.push('/login')
  }
}

const handleSettingAction = (key: string) => {
  if (key === 'logout') {
    confirmLogout()
    return
  }

  const actionMap: Record<string, string> = {
    recommend: '后续可跳转到个性化推荐设置页',
    agreement: '后续可跳转到用户协议页',
    privacy: '后续可跳转到隐私政策页',
    cancel: '后续可接入注销账号逻辑',
    contact: '后续可跳转到联系我们页面'
  }

  ElMessage({
    message: actionMap[key] || '功能开发中',
    type: 'info',
    duration: 1800
  })
}

// ==================== 支付成功后刷新用户信息 ====================

// 刷新用户信息（积分和会员状态）
const refreshUserInfoAfterPurchase = async () => {
  const userId = Number(userStore.userInfo?.id)
  if (!userId) {
    ElMessage.warning('无法获取用户信息，请重新登录')
    return
  }

  ElMessage.info('正在刷新账户信息...')

  try {
    // 并行获取积分账户信息和用户信息
    const [pointsResult, userResult] = await Promise.all([
      getAccountPointsService(userId).catch(err => {
        console.error('获取积分信息失败:', err)
        return null
      }),
      getUserInfo().catch(err => {
        console.error('获取用户信息失败:', err)
        return null
      })
    ])

    // 更新积分信息
    if (pointsResult?.data?.code === 200 && pointsResult.data.data) {
      accountPoints.value = pointsResult.data.data

      if (userStore.userInfo) {
        userStore.userInfo = {
          ...userStore.userInfo,
          points: pointsResult.data.data.pointsBalance,
          pointsBalance: pointsResult.data.data.pointsBalance
        } as any
      }
    }

    // 更新用户信息（会员状态等）
    if (userResult?.data?.code === 200 && userResult.data.data) {
      const newUserInfo = userResult.data.data

      // 更新本地 userInfo
      userInfo.value = {
        ...userInfo.value,
        name: (newUserInfo as any).name || (newUserInfo as any).nickname || userInfo.value.name,
        avatar: (newUserInfo as any).avatar || userInfo.value.avatar,
        signature: (newUserInfo as any).signature || (newUserInfo as any).info || userInfo.value.signature,
        gender: (newUserInfo as any).gender || userInfo.value.gender,
        education: (newUserInfo as any).education || userInfo.value.education,
        experience: (newUserInfo as any).experience || userInfo.value.experience,
        industries: (newUserInfo as any).industries || userInfo.value.industries,
        jobs: (newUserInfo as any).jobs || userInfo.value.jobs
      }

      // 更新全局 store
      userStore.userInfo = {
        ...userStore.userInfo,
        ...newUserInfo,
        memberType: (newUserInfo as any).memberType,
        memberExpireAt: (newUserInfo as any).memberExpireAt
      } as any

      // 显示成功提示
      const memberType = String((newUserInfo as any).memberType || 'normal').toLowerCase()
      const memberText = memberType === 'normal' ? '基础会员' :
                        memberType === 'monthly' ? '月度会员' :
                        memberType === 'quarterly' || memberType === 'quarter' ? '季度会员' :
                        memberType === 'yearly' || memberType === 'annual' ? '年度会员' : '基础会员'

      ElMessage.success({
        message: `账户信息已更新！当前会员：${memberText}，积分余额：${accountPoints.value?.pointsBalance || 0}`,
        duration: 3000
      })
    } else {
      ElMessage.success('账户信息已更新')
    }
  } catch (error) {
    console.error('刷新用户信息失败:', error)
    ElMessage.warning('支付成功，但刷新账户信息失败，请手动刷新页面')
  }
}
</script>

<template>
  <div class="profile-page">
    <div class="page-glow page-glow-left"></div>
    <div class="page-glow page-glow-right"></div>

    <ProfileSidebar v-show="!isMobileLayout || isMobileMenuOpen" v-model:activeMenu="activeMenu"
      v-model:collapsed="sidebarCollapsed" :menus="visibleMenus" :user-info="userInfo" :points="displayPoints"
      class="responsive-sidebar" />

    <div class="right-panel" v-show="!isMobileLayout || !isMobileMenuOpen">
      <div class="panel-shell">
        <div class="mobile-nav-header" v-if="isMobileLayout">
          <el-icon class="back-btn" @click="isMobileMenuOpen = true">
            <ArrowLeft />
          </el-icon>
          <span class="mobile-nav-title">{{ panelTitleMap[activeMenu] }}</span>
        </div>

        <div class="content-intro" v-else>
          <!-- <div class="intro-badge">个人中心</div> -->
          <h1>{{ panelTitleMap[activeMenu] }}</h1>
          <p>{{ panelDescriptionMap[activeMenu] }}</p>
        </div>

        <transition name="fade-slide" mode="out-in">
          <div :key="activeMenu" class="panel-content">
            <ProfileDashboard v-if="activeMenu === 'dashboard'" :user-info="userInfo" />

            <ProfileInfoPanel v-else-if="activeMenu === 'profile'" :user-info="userInfo"
              @update-user="updateUserInfo" />

            <MemberPlanPanel v-else-if="activeMenu === 'member'" :points="displayPoints" :records="pointRecords"
              :account-points="accountPoints" :loading="pointsLoading" @purchase-success="refreshUserInfoAfterPurchase" />

            <InviteFriendsPanel v-else-if="activeMenu === 'invite'" :invite-code="inviteCode" />

            <FeedbackPanel v-else-if="activeMenu === 'feedback'" />

            <MoreSettingsPanel v-else-if="activeMenu === 'setting'" @action="handleSettingAction" />
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.profile-page {
  position: relative;
  display: flex;
  gap: 24px;
  padding: 24px;
  min-height: calc(100vh - 80px);
  box-sizing: border-box;
  background:
    radial-gradient(ellipse at top left, rgba(255, 255, 255, 0.8), transparent 45%),
    radial-gradient(ellipse at bottom right, rgba(226, 232, 240, 0.4), transparent 50%),
    linear-gradient(180deg, #f4f6f8 0%, #e8eef3 100%);
  overflow: hidden;
  font-family: 'Inter', -apple-system, sans-serif;
}

.page-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(50px);
  pointer-events: none;
  z-index: 0;
}

.page-glow-left {
  top: -50px;
  left: -100px;
  width: 400px;
  height: 400px;
  background: rgba(255, 255, 255, 0.4);
  animation: floatLeft 15s ease-in-out infinite alternate;
}

.page-glow-right {
  right: -50px;
  bottom: -50px;
  width: 500px;
  height: 500px;
  background: rgba(226, 232, 240, 0.3);
  animation: floatRight 18s ease-in-out infinite alternate;
}

@keyframes floatLeft {
  0% {
    transform: translate(0, 0) scale(1);
  }

  100% {
    transform: translate(40px, 30px) scale(1.1);
  }
}

@keyframes floatRight {
  0% {
    transform: translate(0, 0) scale(1);
  }

  100% {
    transform: translate(-50px, -40px) scale(1.05);
  }
}

.right-panel {
  position: relative;
  z-index: 1;
  flex: 1;
  min-width: 0;
}

.panel-shell {
  min-height: 100%;
  border: 1px solid rgba(255, 255, 255, 0.95);
  border-radius: 32px;
  padding: 36px 40px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.75) 100%);
  backdrop-filter: blur(24px) saturate(120%);
  box-shadow:
    0 10px 40px rgba(15, 23, 42, 0.03),
    inset 0 2px 4px rgba(255, 255, 255, 1);
  transition: all 0.3s ease;
}

.content-intro {
  margin-bottom: 32px;
  padding-bottom: 28px;
  border-bottom: 1px solid rgba(226, 236, 248, 0.7);
  position: relative;
}

.content-intro::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #94a3b8, transparent);
  border-radius: 2px;
}

.content-intro h1 {
  margin: 14px 0 8px;
  font-size: 30px;
  font-weight: 800;
  line-height: 1.25;
  color: #0f243d;
  letter-spacing: -0.02em;
}

.content-intro p {
  margin: 0;
  max-width: 640px;
  font-size: 14px;
  line-height: 1.8;
  color: #6a7d94;
}

.intro-badge {
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 14px;
  border-radius: 999px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.mobile-nav-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.back-btn {
  font-size: 20px;
  color: #334155;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #f1f5f9;
}

.mobile-nav-title {
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.panel-content {
  min-height: 400px;
  animation: contentIn 0.35s ease;
}

@keyframes contentIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 992px) {
  .profile-page {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .profile-page {
    padding: 12px;
    gap: 12px;
  }

  .panel-shell {
    padding: 24px 20px;
    border-radius: 24px;
  }

  .content-intro h1 {
    font-size: 24px;
  }
}
</style>
