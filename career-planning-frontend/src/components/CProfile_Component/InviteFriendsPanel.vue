<script setup>
import { ElMessage } from 'element-plus'

const props = defineProps({
  inviteCode: {
    type: String,
    default: 'ZHILU2026'
  }
})

const copyInviteCode = async () => {
  try {
    await navigator.clipboard.writeText(props.inviteCode)
    ElMessage.success('邀请码已复制')
  } catch {
    ElMessage.warning('复制失败，请手动复制')
  }
}

const steps = [
  {
    icon: '👤',
    title: '成为推广大使',
    desc: '注册成为推广大使，获得专属邀请码'
  },
  {
    icon: '🔗',
    title: '分享邀请码',
    desc: '好友通过邀请码注册，获得积分与会员奖励'
  },
  {
    icon: '💰',
    title: '坐享奖励',
    desc: '好友下单，您立得10%及以上现金分佣'
  }
]
</script>

<template>
  <div class="invite-panel">
    <div class="invite-hero">
      <div class="hero-decoration"></div>
      <div class="hero-content">
        <div class="hero-badge">推广计划</div>
        <h2 class="hero-title">邀请好友，共同成长</h2>
        <p class="hero-desc">分享你的专属邀请码，每成功邀请一位好友即可获得积分和会员奖励</p>
        <el-button type="primary" round class="hero-btn">立即注册成为大使</el-button>
      </div>
    </div>

    <div class="flow-section">
      <div class="flow-title-bar">
        <span class="flow-title">邀请流程</span>
        <span class="flow-subtitle">简单三步，轻松获得奖励</span>
      </div>

      <div class="flow-steps">
        <div v-for="(step, index) in steps" :key="step.title" class="step-card">
          <div class="step-number">{{ String(index + 1).padStart(2, '0') }}</div>
          <div class="step-icon">{{ step.icon }}</div>
          <div class="step-content">
            <div class="step-name">{{ step.title }}</div>
            <div class="step-desc">{{ step.desc }}</div>
          </div>
          <div v-if="index < steps.length - 1" class="step-connector"></div>
        </div>
      </div>
    </div>

    <div class="code-section">
      <div class="code-card">
        <div class="code-info">
          <div class="code-label">我的邀请码</div>
          <div class="code-value">{{ inviteCode }}</div>
          <div class="code-hint">分享给好友，双方均可获得奖励</div>
        </div>
        <el-button type="primary" round @click="copyInviteCode">
          复制邀请码
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.invite-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.invite-hero {
  position: relative;
  overflow: hidden;
  border-radius: 22px;
  padding: 36px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 16px 40px rgba(102, 126, 234, 0.25);
}

.hero-decoration {
  position: absolute;
  top: -40px;
  right: -30px;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.hero-decoration::after {
  content: '';
  position: absolute;
  bottom: -60px;
  left: -40px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.07);
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  height: 26px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.hero-title {
  margin: 14px 0 8px;
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
}

.hero-desc {
  margin: 0;
  max-width: 500px;
  font-size: 14px;
  line-height: 1.7;
  opacity: 0.88;
}

.hero-btn {
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border: none;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);

  &:hover {
    background: #fff;
  }
}

.flow-title-bar {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 16px;
}

.flow-title {
  font-size: 17px;
  font-weight: 800;
  color: #163253;
}

.flow-subtitle {
  font-size: 13px;
  color: #8da1b8;
}

.flow-steps {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.step-card {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #e8eef6;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03);
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    border-color: #d4e2f5;
  }

  & + .step-card {
    margin-top: 12px;
  }
}

.step-number {
  position: absolute;
  top: 18px;
  right: 20px;
  font-size: 28px;
  font-weight: 900;
  color: #e8eef6;
  line-height: 1;
}

.step-icon {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-name {
  font-size: 15px;
  font-weight: 700;
  color: #1f3550;
}

.step-desc {
  margin-top: 4px;
  font-size: 13px;
  line-height: 1.6;
  color: #7a8da3;
}

.code-section {
  margin-top: 4px;
}

.code-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 24px;
  border-radius: 20px;
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.code-label {
  font-size: 12px;
  font-weight: 700;
  color: #6b8a7a;
}

.code-value {
  margin-top: 6px;
  font-size: 28px;
  font-weight: 900;
  color: #166534;
  letter-spacing: 0.08em;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.code-hint {
  margin-top: 4px;
  font-size: 12px;
  color: #86b89a;
}

@media (max-width: 768px) {
  .invite-hero {
    padding: 28px 20px;
  }

  .hero-title {
    font-size: 22px;
  }

  .code-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
