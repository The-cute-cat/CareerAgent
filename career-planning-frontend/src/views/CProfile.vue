<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/modules/user'

import ProfileInfoPanel from '../components/CProfile_Component/ProfileInfoPanel.vue'
import ProfileSidebar from '../components/CProfile_Component/ProfileSidebar.vue'
import MemberPlanPanel from '../components/CProfile_Component/MemberPlanPanel.vue'
import InviteFriendsPanel from '../components/CProfile_Component/InviteFriendsPanel.vue'
import FeedbackPanel from '../components/CProfile_Component/FeedbackPanel.vue'
import MoreSettingsPanel from '../components/CProfile_Component/MoreSettingsPanel.vue'

const userStore = useUserStore()
const sidebarCollapsed = ref(false)

const activeMenu = ref('profile')
const defaultAvatar = 'https://picsum.photos/200/200'

const userInfo = ref({
  name: `用户${userStore.userInfo?.id || 5442}`,
  avatar: userStore.userInfo?.avatar || defaultAvatar,
  signature: '成为更好的自己',
  gender: '男',
  education: '博士',
  experience: '在校生',
  industries: '互联网、电子商务、计算机',
  jobs: 'Java、前端开发工程师'
})

const displayPoints = computed(() => userStore.userInfo?.points || 300)

const menus = [
  { key: 'profile', label: '个人资料' },
  { key: 'member', label: '会员计划' },
  { key: 'invite', label: '邀请好友' },
  { key: 'feedback', label: '反馈建议' },
  { key: 'setting', label: '更多设置' }
]

const pointRecords = ref([
  {
    id: 1,
    type: '每日积分',
    remain: 100,
    total: 100,
    expireText: ''
  },
  {
    id: 2,
    type: '邀请奖励',
    remain: 200,
    total: 200,
    expireText: '距离到期还有 29 天'
  }
])

const inviteCode = ref('ZHILU2026')

const panelTitleMap = {
  profile: '个人资料',
  member: '会员计划',
  invite: '邀请好友',
  feedback: '反馈建议',
  setting: '更多设置'
}

const panelDescriptionMap = {
  profile: '在这里完善你的资料、兴趣方向和职业偏好，让个人中心更像你的专属名片。',
  member: '查看积分权益与会员状态，了解当前账户可使用的成长资源。',
  invite: '把职业规划工具分享给朋友，一起解锁更多使用权益。',
  feedback: '告诉我们你的使用感受和改进建议，帮助产品持续变得更好。',
  setting: '统一管理隐私、协议、推荐偏好与账号相关设置。'
}

const updateUserInfo = (payload) => {
  userInfo.value = {
    ...userInfo.value,
    ...payload
  }

  ElMessage({
    message: '个人信息已更新',
    type: 'success',
    duration: 1800
  })
}

const handleSettingAction = (key) => {
  const actionMap = {
    recommend: '后续可跳转到个性化推荐设置页',
    agreement: '后续可跳转到用户协议页',
    privacy: '后续可跳转到隐私政策页',
    logout: '后续可接入退出登录逻辑',
    cancel: '后续可接入注销账户逻辑',
    contact: '后续可跳转到联系我们页面'
  }

  ElMessage({
    message: actionMap[key] || '功能开发中',
    type: 'info',
    duration: 1800
  })
}
</script>

<template>
  <div class="profile-page">
    <div class="page-glow page-glow-left"></div>
    <div class="page-glow page-glow-right"></div>

    <ProfileSidebar
      v-model:activeMenu="activeMenu"
      v-model:collapsed="sidebarCollapsed"
      :menus="menus"
      :user-info="userInfo"
      :points="displayPoints"
    />

    <div class="right-panel">
      <div class="panel-shell">
        <div class="content-intro">
          <div class="intro-badge">个人中心</div>
          <h1>{{ panelTitleMap[activeMenu] }}</h1>
          <p>{{ panelDescriptionMap[activeMenu] }}</p>
        </div>

        <transition name="fade-slide" mode="out-in">
          <div :key="activeMenu" class="panel-content">
            <ProfileInfoPanel
              v-if="activeMenu === 'profile'"
              :user-info="userInfo"
              @update-user="updateUserInfo"
            />

            <MemberPlanPanel v-else-if="activeMenu === 'member'" :points="displayPoints" :records="pointRecords" />

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
  gap: 20px;
  padding: 20px;
  min-height: calc(100vh - 80px);
  box-sizing: border-box;
  background:
    radial-gradient(circle at top left, rgba(97, 154, 255, 0.2), transparent 28%),
    radial-gradient(circle at right 20%, rgba(40, 199, 111, 0.14), transparent 24%),
    linear-gradient(180deg, #f4f8ff 0%, #eef4fb 52%, #f8fbff 100%);
  overflow: hidden;
}

.page-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(12px);
  pointer-events: none;
}

.page-glow-left {
  top: 72px;
  left: -40px;
  width: 180px;
  height: 180px;
  background: rgba(22, 119, 255, 0.12);
}

.page-glow-right {
  right: 40px;
  bottom: 32px;
  width: 220px;
  height: 220px;
  background: rgba(14, 203, 102, 0.08);
}

.right-panel {
  position: relative;
  z-index: 1;
  flex: 1;
  min-width: 0;
}

.panel-shell {
  min-height: 100%;
  border: 1px solid rgba(219, 230, 244, 0.75);
  border-radius: 24px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(20px);
  box-shadow:
    0 1px 3px rgba(27, 63, 104, 0.04),
    0 20px 50px rgba(27, 63, 104, 0.07);
}

.content-intro {
  margin-bottom: 28px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(219, 230, 244, 0.6);
}

.content-intro h1 {
  margin: 10px 0 6px;
  font-size: 28px;
  font-weight: 800;
  line-height: 1.2;
  color: #163253;
  letter-spacing: -0.02em;
}

.content-intro p {
  margin: 0;
  max-width: 600px;
  font-size: 13px;
  line-height: 1.75;
  color: #7a8da3;
}

.intro-badge {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(22, 119, 255, 0.1), rgba(103, 184, 255, 0.08));
  color: #1668dc;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
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

@media (max-width: 1400px) {
  .profile-page {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .profile-page {
    padding: 14px;
    gap: 14px;
  }

  .panel-shell {
    padding: 20px 16px;
    border-radius: 22px;
  }

  .content-intro h1 {
    font-size: 26px;
  }
}
</style>
