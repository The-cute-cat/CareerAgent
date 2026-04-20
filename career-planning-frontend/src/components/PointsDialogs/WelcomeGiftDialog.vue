<script setup lang="ts">
import { computed } from 'vue'
import { Present, Coin, Star, Check } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: boolean
  points: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const benefits = [
  { icon: Check, text: 'AI职业测评 × 16次' },
  { icon: Check, text: 'AI智能问答 × 50次' },
  { icon: Check, text: '岗位推荐分析 × 25次' },
  { icon: Check, text: '简历优化 × 10次' }
]

const handleStart = () => {
  visible.value = false
}
</script>

<template>
  <el-dialog
    v-model="visible"
    width="420px"
    :show-close="false"
    class="welcome-gift-dialog"
    :close-on-click-modal="false"
    append-to-body
  >
    <div class="welcome-content">
      <!-- 礼物图标动画 -->
      <div class="gift-animation">
        <div class="gift-icon">
          <el-icon><Present /></el-icon>
        </div>
        <div class="sparkles">
          <span class="sparkle s1">✨</span>
          <span class="sparkle s2">✨</span>
          <span class="sparkle s3">✨</span>
          <span class="sparkle s4">✨</span>
        </div>
      </div>
      
      <!-- 标题 -->
      <h2 class="title">欢迎加入职引未来！</h2>
      <p class="subtitle">新用户专属大礼包</p>
      
      <!-- 积分展示 -->
      <div class="points-display">
        <div class="points-icon">
          <el-icon><Coin /></el-icon>
        </div>
        <div class="points-number">{{ points }}</div>
        <div class="points-label">新人积分</div>
      </div>
      
      <!-- 可用功能 -->
      <div class="benefits-section">
        <p class="benefits-title">可用功能</p>
        <div class="benefits-list">
          <div v-for="(benefit, index) in benefits" :key="index" class="benefit-item">
            <el-icon class="benefit-icon"><component :is="benefit.icon" /></el-icon>
            <span class="benefit-text">{{ benefit.text }}</span>
          </div>
        </div>
      </div>
      
      <!-- 开始按钮 -->
      <button class="start-btn" @click="handleStart">
        <el-icon><Star /></el-icon>
        开启职业之旅
      </button>
      
      <!-- 提示 -->
      <p class="hint">积分可用于平台所有功能</p>
    </div>
  </el-dialog>
</template>

<style scoped lang="scss">
.welcome-content {
  padding: 36px 28px;
  text-align: center;
  background: linear-gradient(180deg, #fff 0%, #f8fafc 100%);
}

.gift-animation {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
}

.gift-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3);
  animation: giftBounce 2s ease-in-out infinite;
  
  .el-icon {
    font-size: 40px;
    color: #fff;
  }
}

@keyframes giftBounce {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -55%) scale(1.05);
  }
}

.sparkles {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.sparkle {
  position: absolute;
  font-size: 16px;
  animation: sparkle 1.5s ease-in-out infinite;
  
  &.s1 {
    top: 0;
    left: 20%;
    animation-delay: 0s;
  }
  
  &.s2 {
    top: 10%;
    right: 15%;
    animation-delay: 0.3s;
  }
  
  &.s3 {
    bottom: 20%;
    left: 10%;
    animation-delay: 0.6s;
  }
  
  &.s4 {
    bottom: 10%;
    right: 20%;
    animation-delay: 0.9s;
  }
}

@keyframes sparkle {
  0%, 100% {
    opacity: 0;
    transform: scale(0.5);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.title {
  font-size: 24px;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 8px;
}

.subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 24px;
}

.points-display {
  background: linear-gradient(135deg, #fef9c3, #fef3c7);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  border: 2px solid #fde68a;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
    animation: shimmer 3s ease-in-out infinite;
  }
}

@keyframes shimmer {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.points-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  
  .el-icon {
    font-size: 24px;
    color: #fff;
  }
}

.points-number {
  font-size: 56px;
  font-weight: 900;
  color: #d97706;
  line-height: 1;
  margin-bottom: 6px;
  text-shadow: 2px 2px 4px rgba(217, 119, 6, 0.1);
}

.points-label {
  font-size: 14px;
  color: #b45309;
  font-weight: 600;
}

.benefits-section {
  margin-bottom: 24px;
}

.benefits-title {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.benefits-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f1f5f9;
  border-radius: 10px;
  
  .benefit-icon {
    font-size: 14px;
    color: #10b981;
  }
  
  .benefit-text {
    font-size: 12px;
    color: #475569;
    font-weight: 500;
  }
}

.start-btn {
  width: 100%;
  padding: 16px 24px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
  margin-bottom: 12px;
  
  .el-icon {
    font-size: 20px;
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45);
  }
}

.hint {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
}

:deep(.welcome-gift-dialog) {
  border-radius: 28px;
  overflow: hidden;
  
  .el-dialog__header {
    display: none;
  }
  
  .el-dialog__body {
    padding: 0;
  }
}
</style>
