<script setup>
import { EditPen, InfoFilled, Warning, Coin, ArrowRight, SwitchButton, Promotion } from '@element-plus/icons-vue'

const emit = defineEmits(['action'])

const clickAction = (key) => {
  emit('action', key)
}

const personalSettings = [
  { key: 'recommend', icon: EditPen, label: '个性化推荐', desc: '根据你的偏好定制内容' },
  { key: 'ads', icon: Promotion, label: '广告推荐', desc: '管理个性化广告展示' }
]

const accountSettings = [
  { key: 'agreement', icon: InfoFilled, label: '用户协议', desc: '查看平台服务条款' },
  { key: 'privacy', icon: Warning, label: '隐私政策', desc: '了解数据保护措施' },
  { key: 'cancel', icon: Coin, label: '注销账户', desc: '永久删除账户数据' }
]

const aboutSettings = [
  { key: 'contact', icon: null, label: '联系我们', desc: '获取帮助与支持' }
]
</script>

<template>
  <div class="settings-panel">
    <div class="settings-section">
      <div class="section-header">
        <span class="section-icon">🎨</span>
        <span class="section-title">个性化设置</span>
      </div>
      <div class="settings-group">
        <div
          v-for="item in personalSettings"
          :key="item.key"
          class="setting-item"
          @click="clickAction(item.key)"
        >
          <div class="setting-icon-wrap">
            <el-icon><component :is="item.icon" /></el-icon>
          </div>
          <div class="setting-info">
            <div class="setting-label">{{ item.label }}</div>
            <div class="setting-desc">{{ item.desc }}</div>
          </div>
          <el-icon class="setting-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-header">
        <span class="section-icon">🔒</span>
        <span class="section-title">账户与隐私</span>
      </div>
      <div class="settings-group">
        <div
          v-for="item in accountSettings"
          :key="item.key"
          class="setting-item"
          @click="clickAction(item.key)"
        >
          <div class="setting-icon-wrap" :class="{ danger: item.key === 'cancel' }">
            <el-icon><component :is="item.icon" /></el-icon>
          </div>
          <div class="setting-info">
            <div class="setting-label">{{ item.label }}</div>
            <div class="setting-desc">{{ item.desc }}</div>
          </div>
          <el-icon class="setting-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-header">
        <span class="section-icon">ℹ️</span>
        <span class="section-title">关于职引未来</span>
      </div>
      <div class="settings-group">
        <div
          v-for="item in aboutSettings"
          :key="item.key"
          class="setting-item"
          @click="clickAction(item.key)"
        >
          <div class="setting-info" style="padding-left: 4px">
            <div class="setting-label">{{ item.label }}</div>
            <div class="setting-desc">{{ item.desc }}</div>
          </div>
          <el-icon class="setting-arrow"><ArrowRight /></el-icon>
        </div>

        <div class="setting-item static">
          <div class="setting-info" style="padding-left: 4px">
            <div class="setting-label">备案信息</div>
            <div class="setting-desc">浙ICP备2025131364号-2A</div>
          </div>
        </div>
      </div>
    </div>

    <div class="logout-area">
      <el-button class="logout-btn" plain @click="clickAction('logout')">
        <el-icon><SwitchButton /></el-icon>
        退出登录
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.settings-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  font-size: 16px;
}

.section-title {
  font-size: 15px;
  font-weight: 800;
  color: #1f3550;
}

.settings-group {
  display: flex;
  flex-direction: column;
  border-radius: 20px;
  background: #ffffff; /* 变回实心纯白，对齐标准设置界面 */
  border: 1px solid #edf2f7;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  overflow: hidden;
  transition: all 0.3s ease;
}

.settings-group:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  cursor: pointer;
  transition: all 0.25s ease;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);

  &:last-child {
    border-bottom: none;
  }

  &:not(.static):hover {
    background: #f8fafc;

    .setting-label {
      color: #1e62c5;
    }
    
    .setting-icon-wrap {
      transform: scale(1.05);
    }
  }

  &.static {
    cursor: default;
  }
}

.setting-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f1f5f9, #f8fafc);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 18px;
  flex-shrink: 0;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 1);

  &.danger {
    background: linear-gradient(135deg, #fef2f2, #fff1f2);
    color: #ef4444;
  }
}

.setting-info {
  flex: 1;
  min-width: 0;
}

.setting-label {
  font-size: 14px;
  font-weight: 700;
  color: #22364d;
  transition: color 0.2s;
}

.setting-desc {
  margin-top: 2px;
  font-size: 12px;
  color: #8da1b8;
}

.setting-arrow {
  color: #c5cdd8;
  font-size: 14px;
  flex-shrink: 0;
}

.logout-area {
  margin-top: 8px;
}

.logout-btn {
  width: 100%;
  height: 48px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 800;
  border: 1.5px solid #fecaca;
  color: #ef4444;
  background: rgba(255, 245, 245, 0.8);
  backdrop-filter: blur(8px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    background: #fef2f2;
    border-color: #f87171;
    color: #dc2626;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.1);
  }
}
</style>
