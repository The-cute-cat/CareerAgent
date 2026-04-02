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
  gap: 24px;
  font-family: 'Inter', system-ui, sans-serif;
}

.invite-hero {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  padding: 40px 36px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  color: #0f172a;
  border: 1px solid #e2e8f0;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.03), inset 0 1px 2px rgba(255, 255, 255, 1);
}

.hero-decoration {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 50%;
  background-image: linear-gradient(rgba(148, 163, 184, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.1) 1px, transparent 1px);
  background-size: 30px 30px;
  -webkit-mask-image: linear-gradient(to left, rgba(0,0,0,1), rgba(0,0,0,0));
  mask-image: linear-gradient(to left, rgba(0,0,0,1), rgba(0,0,0,0));
}

.hero-decoration::after {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  height: 28px;
  align-items: center;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: #4f46e5;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.hero-title {
  margin: 16px 0 10px;
  font-size: 32px;
  font-weight: 900;
  line-height: 1.25;
  letter-spacing: -0.02em;
}

.hero-desc {
  margin: 0;
  max-width: 500px;
  font-size: 15px;
  line-height: 1.7;
  color: #64748b;
}

.hero-btn {
  margin-top: 24px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border: none;
  font-weight: 800;
  padding: 12px 28px;
  border-radius: 999px;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(99, 102, 241, 0.4);
  }
}

.flow-title-bar {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 20px;
}

.flow-title {
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
}

.flow-subtitle {
  font-size: 14px;
  color: #64748b;
}

.flow-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 24px 28px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04), inset 0 1px 2px rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08), inset 0 1px 2px rgba(255, 255, 255, 1);
  }
}

.step-number {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  right: 30px;
  font-size: 42px;
  font-weight: 900;
  color: rgba(15, 23, 42, 0.03);
  line-height: 1;
  pointer-events: none;
}

.step-icon {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.8);
}

.step-content {
  flex: 1;
  min-width: 0;
  z-index: 1;
}

.step-name {
  font-size: 16px;
  font-weight: 800;
  color: #1e293b;
}

.step-desc {
  margin-top: 6px;
  font-size: 14px;
  line-height: 1.6;
  color: #64748b;
}

.code-section {
  margin-top: 8px;
}

.code-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 32px;
  border-radius: 28px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.03);
}

.code-label {
  font-size: 14px;
  font-weight: 800;
  color: #475569;
}

.code-value {
  margin-top: 8px;
  font-size: 34px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: 0.1em;
  font-family: 'SF Mono', 'Fira Code', monospace;
  text-shadow: 0 2px 4px rgba(15, 23, 42, 0.03);
}

.code-hint {
  margin-top: 8px;
  font-size: 14px;
  color: #64748b;
}

@media (max-width: 768px) {
  .invite-hero {
    padding: 32px 24px;
  }

  .hero-title {
    font-size: 26px;
  }

  .code-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
