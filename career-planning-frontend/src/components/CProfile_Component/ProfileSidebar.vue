<script setup>
import {
  User,
  Star,
  UserFilled,
  ChatDotRound,
  Setting,
  ArrowRight,
  Fold,
  Expand
} from '@element-plus/icons-vue'

const props = defineProps({
  activeMenu: String,
  collapsed: Boolean,
  menus: Array,
  userInfo: Object,
  points: Number
})

const emit = defineEmits(['update:activeMenu', 'update:collapsed'])

const iconMap = {
  profile: User,
  member: Star,
  invite: UserFilled,
  feedback: ChatDotRound,
  setting: Setting
}

const quickStats = [
  { label: '我的参与', value: '12' },
  { label: '成长任务', value: '08' },
  { label: '内容收藏', value: '21' }
]

const toggleCollapse = () => {
  emit('update:collapsed', !props.collapsed)
}
</script>

<template>
  <aside class="left-panel" :class="{ collapsed: collapsed }">
    <div class="sidebar-top">
      <div v-if="!collapsed" class="sidebar-title-group">
        <div class="sidebar-title">个人中心</div>
        <div class="sidebar-subtitle">Profile Hub</div>
      </div>

      <el-button circle class="collapse-btn" @click="toggleCollapse">
        <el-icon>
          <component :is="collapsed ? Expand : Fold" />
        </el-icon>
      </el-button>
    </div>

    <div class="user-card" :class="{ collapsed: collapsed }">
      <div class="user-card-bg"></div>
      <img class="avatar" :src="userInfo.avatar" alt="avatar" />

      <div v-if="!collapsed" class="user-meta">
        <div class="user-name">{{ userInfo.name }}</div>
        <div class="user-signature">{{ userInfo.signature || '继续向着更清晰的方向前进' }}</div>
        <div class="user-points">积分 {{ points }}</div>
      </div>
    </div>

    <div v-if="!collapsed" class="data-cards">
      <div v-for="item in quickStats" :key="item.label" class="data-item">
        <div class="num">{{ item.value }}</div>
        <div class="label">{{ item.label }}</div>
      </div>
    </div>

    <div class="menu-card" :class="{ collapsed: collapsed }">
      <div class="menu-caption" v-if="!collapsed">功能导航</div>

      <div
        v-for="item in menus"
        :key="item.key"
        class="menu-item"
        :class="{ active: activeMenu === item.key, collapsed: collapsed }"
        @click="emit('update:activeMenu', item.key)"
      >
        <div class="left">
          <el-icon><component :is="iconMap[item.key]" /></el-icon>
          <span v-if="!collapsed">{{ item.label }}</span>
        </div>

        <el-icon v-if="!collapsed" class="arrow-icon"><ArrowRight /></el-icon>
      </div>
    </div>
  </aside>
</template>

<style scoped lang="scss">
.left-panel {
  position: relative;
  z-index: 1;
  width: 320px;
  min-width: 320px;
  transition: all 0.25s ease;
}

.left-panel.collapsed {
  width: 88px;
  min-width: 88px;
}

.sidebar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  padding: 0 4px;
}

.sidebar-title {
  font-size: 22px;
  font-weight: 800;
  color: #173a5d;
}

.sidebar-subtitle {
  margin-top: 4px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #86a0bd;
  text-transform: uppercase;
}

.collapse-btn {
  flex-shrink: 0;
  border: 1px solid #dce6f2;
  box-shadow: 0 8px 20px rgba(16, 42, 67, 0.05);
}

.user-card {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 122px;
  margin-bottom: 14px;
  padding: 18px;
  border-radius: 24px;
  border: 1px solid rgba(204, 223, 246, 0.8);
  background: linear-gradient(135deg, #eef5ff 0%, #f7fbff 65%, #f0fbf6 100%);
  box-shadow: 0 16px 36px rgba(18, 52, 92, 0.08);
}

.user-card-bg {
  position: absolute;
  top: -26px;
  right: -32px;
  width: 128px;
  height: 128px;
  border-radius: 50%;
  background: rgba(22, 119, 255, 0.08);
}

.avatar {
  position: relative;
  z-index: 1;
  width: 60px;
  height: 60px;
  border-radius: 18px;
  object-fit: cover;
  box-shadow: 0 10px 24px rgba(21, 83, 199, 0.14);
}

.user-meta {
  position: relative;
  z-index: 1;
  min-width: 0;
}

.user-name {
  font-size: 20px;
  font-weight: 800;
  color: #1553c7;
}

.user-signature {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.6;
  color: #627389;
}

.user-points {
  display: inline-flex;
  align-items: center;
  margin-top: 10px;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(21, 83, 199, 0.08);
  color: #1553c7;
  font-size: 12px;
  font-weight: 700;
}

.user-card.collapsed {
  justify-content: center;
  min-height: auto;
  padding: 14px 8px;
}

.user-card.collapsed .avatar {
  width: 48px;
  height: 48px;
  border-radius: 16px;
}

.data-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.data-item {
  padding: 14px 8px;
  text-align: center;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(228, 236, 245, 0.95);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.num {
  font-size: 22px;
  font-weight: 800;
  color: #165bcf;
}

.label {
  margin-top: 6px;
  color: #6f8197;
  font-size: 12px;
  line-height: 1.4;
}

.menu-card {
  padding: 12px;
  border-radius: 22px;
  border: 1px solid rgba(228, 236, 245, 0.95);
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(14px);
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.05);
}

.menu-card.collapsed {
  padding: 8px;
}

.menu-caption {
  margin: 2px 8px 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #8da1b8;
}

.menu-item {
  position: relative;
  height: 50px;
  margin-bottom: 6px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 16px;
  color: #2b3f57;
  cursor: pointer;
  transition: all 0.25s ease;
}

.menu-item:last-child {
  margin-bottom: 0;
}

.left {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 700;
}

.menu-item .el-icon {
  font-size: 18px;
}

.arrow-icon {
  color: #9db0c5;
}

.menu-item:hover {
  background: #f4f8ff;
  transform: translateX(2px);
}

.menu-item.active {
  background: linear-gradient(90deg, rgba(22, 119, 255, 0.12), rgba(69, 182, 255, 0.08));
  color: #1553c7;
}

.menu-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 4px;
  border-radius: 999px;
  background: linear-gradient(180deg, #1677ff, #67b8ff);
}

.menu-item.collapsed {
  justify-content: center;
  padding: 0;
}

.menu-item.collapsed .left {
  gap: 0;
  justify-content: center;
  width: 100%;
}

.menu-item.collapsed.active::before {
  left: 5px;
}

@media (max-width: 1400px) {
  .left-panel,
  .left-panel.collapsed {
    width: 100%;
    min-width: auto;
  }
}
</style>
