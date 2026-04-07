<script setup>
import {
  User,
  Star,
  UserFilled,
  ChatDotRound,
  Setting,
  ArrowRight,
  Fold,
  Expand,
  House
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
  dashboard: House,
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
    <div class="sidebar-footer">
      <el-button circle class="collapse-btn" @click="toggleCollapse">
        <el-icon>
          <component :is="collapsed ? Expand : Fold" />
        </el-icon>
      </el-button>
    </div>
  </aside>
</template>

<style scoped lang="scss">
.left-panel {
  position: relative;
  z-index: 1;
  flex: 0 0 32%;
  min-width: 300px;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-x: hidden !important; /* 物理锁定横向溢出 */
}

/* 隐藏所有可能的滚动条（滑轮） */
.left-panel::-webkit-scrollbar,
.menu-card::-webkit-scrollbar {
  display: none !important;
}

.left-panel,
.menu-card {
  scrollbar-width: none !important;
  -ms-overflow-style: none !important;
}

.left-panel.collapsed {
  flex: 0 0 88px;
  min-width: 88px;
  max-width: 88px;
}

/* ========== 底部区域 ========== */
.sidebar-footer {
  margin-top: auto;
  padding: 16px 4px 4px;
  display: flex;
  align-items: center;
}

.left-panel.collapsed .sidebar-footer {
  justify-content: center;
  padding: 16px 0 0;
}

.collapse-btn {
  flex-shrink: 0;
  border: 1px solid #dce6f2;
  box-shadow: 0 8px 20px rgba(16, 42, 67, 0.05);
  background: white;
  color: #3b5068;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  background: #f8fafc;
  color: #165bcf;
  border-color: #165bcf;
  transform: scale(1.05);
}

.user-card {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 130px;
  margin-bottom: 16px;
  padding: 20px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 1);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.8) 100%);
  backdrop-filter: blur(20px);
  box-shadow:
    0 12px 32px rgba(15, 23, 42, 0.04),
    inset 0 1px 2px rgba(255, 255, 255, 1);
  transition: all 0.3s ease;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow:
    0 16px 40px rgba(22, 119, 255, 0.12),
    inset 0 1px 2px rgba(255, 255, 255, 0.9);
}

.user-card-bg {
  position: absolute;
  top: -26px;
  right: -32px;
  width: 128px;
  height: 128px;
  border-radius: 50%;
  background: rgba(241, 245, 249, 0.6);
}

.avatar {
  position: relative;
  z-index: 1;
  width: 68px;
  height: 68px;
  border-radius: 20px;
  object-fit: cover;
  border: 2px solid #ffffff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  transition: transform 0.3s ease;
}
.user-card:hover .avatar {
  transform: scale(1.05);
}

.user-meta {
  position: relative;
  z-index: 1;
  min-width: 0;
}

.user-name {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.01em;
}

.user-signature {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.5;
  color: #5c708a;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.user-points {
  display: inline-flex;
  align-items: center;
  margin-top: 12px;
  min-height: 28px;
  padding: 0 14px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #e2e8f0;
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
  gap: 12px;
  margin-bottom: 16px;
}

.data-item {
  padding: 16px 10px;
  text-align: center;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 1);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.03);
  transition: all 0.3s ease;
}

.data-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 12px 28px rgba(22, 119, 255, 0.08);
}

.num {
  font-size: 24px;
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
  padding: 16px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 1);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  box-shadow:
    0 16px 40px rgba(15, 23, 42, 0.03),
    inset 0 1px 2px rgba(255, 255, 255, 1);
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
  height: 54px;
  margin-bottom: 8px;
  padding: 0 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 18px;
  color: #3b5068;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.menu-item:last-child {
  margin-bottom: 0;
}

.left {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.menu-item .el-icon {
  font-size: 20px;
  transition: transform 0.3s ease;
}

.arrow-icon {
  color: #a4b6cf;
  transition: transform 0.3s ease, color 0.3s;
}

.menu-item:hover {
  background: #f8fafc;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02);
  transform: translateX(4px);
}

.menu-item:hover .arrow-icon {
  transform: translateX(2px);
  color: #1e293b;
}

.menu-item:hover .left .el-icon {
  transform: scale(1.1);
  color: #1e293b;
}

.menu-item.active {
  background: #f1f5f9;
  color: #0f172a;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
}

.menu-item.active .left .el-icon {
  color: #0f172a;
}

.menu-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 4px;
  border-radius: 0 4px 4px 0;
  background: #334155;
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

@media (max-width: 992px) {
  .left-panel,
  .left-panel.collapsed {
    width: 100%;
    min-width: 100%;
    max-width: none;
    flex: none;
  }

  .sidebar-top .collapse-btn {
    display: none;
  }

  .data-cards {
    grid-template-columns: repeat(3, 1fr);
  }

  .menu-card {
    display: flex;
    flex-direction: column; /* 改回列表模式 */
    gap: 0px;
    padding: 8px;
  }

  .menu-item {
    width: 100%;
    min-width: 0;
    height: 56px;
    margin-bottom: 4px;
    justify-content: space-between;
    padding: 0 16px;
    border-radius: 12px;
  }

  .menu-item .left {
    justify-content: flex-start;
  }

  .menu-item .arrow-icon {
    display: block; /* 在列表中显示箭头 */
    opacity: 0.5;
  }
}

@media (max-width: 576px) {
  .user-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .user-card-bg {
    right: 50%;
    transform: translateX(50%);
  }

  .menu-item {
    min-width: calc(50% - 10px);
  }
}
</style>
