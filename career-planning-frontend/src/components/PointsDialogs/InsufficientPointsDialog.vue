<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Coin, ShoppingCart, Medal, WarningFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: boolean
  required: number
  current: number
  functionName: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const router = useRouter()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const shortage = computed(() => Math.max(0, props.required - props.current))

const handleBuyPoints = () => {
  visible.value = false
  router.push('/profile?tab=member')
}

const handleUpgradeMember = () => {
  visible.value = false
  router.push('/profile?tab=member')
}
</script>

<template>
  <el-dialog
    v-model="visible"
    width="420px"
    :show-close="false"
    class="insufficient-dialog"
    :close-on-click-modal="false"
    append-to-body
  >
    <div class="insufficient-content">
      <!-- 警告图标 -->
      <div class="warning-icon">
        <el-icon><WarningFilled /></el-icon>
      </div>
      
      <!-- 标题 -->
      <h3 class="title">积分不足</h3>
      
      <!-- 提示信息 -->
      <p class="description">
        使用「<span class="highlight">{{ functionName }}</span>」需要
        <span class="points-required">{{ required }}</span> 积分
      </p>
      
      <!-- 积分状态卡片 -->
      <div class="points-status">
        <div class="status-item">
          <span class="label">当前积分</span>
          <span class="value current">{{ current }}</span>
        </div>
        <div class="status-divider">
          <el-icon><span class="minus-icon">−</span></el-icon>
        </div>
        <div class="status-item">
          <span class="label">需要积分</span>
          <span class="value required">{{ required }}</span>
        </div>
        <div class="status-divider">
          <el-icon><span class="equal-icon">=</span></el-icon>
        </div>
        <div class="status-item">
          <span class="label">还需</span>
          <span class="value shortage">{{ shortage }}</span>
        </div>
      </div>
      
      <!-- 操作建议 -->
      <div class="suggestions">
        <p class="suggestion-text">您可以选择以下方式解决：</p>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions">
        <button class="action-btn buy-points" @click="handleBuyPoints">
          <el-icon><Coin /></el-icon>
          <div class="btn-content">
            <span class="btn-title">购买积分</span>
            <span class="btn-desc">按需购买，灵活使用</span>
          </div>
        </button>
        
        <button class="action-btn upgrade-member" @click="handleUpgradeMember">
          <el-icon><Medal /></el-icon>
          <div class="btn-content">
            <span class="btn-title">开通会员</span>
            <span class="btn-desc">享9折优惠，每月送积分</span>
          </div>
        </button>
      </div>
      
      <!-- 关闭按钮 -->
      <button class="close-btn" @click="visible = false">
        稍后再说
      </button>
    </div>
  </el-dialog>
</template>

<style scoped lang="scss">
.insufficient-content {
  padding: 32px 24px;
  text-align: center;
}

.warning-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  
  .el-icon {
    font-size: 36px;
    color: #f59e0b;
  }
}

.title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px;
}

.description {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 24px;
  line-height: 1.6;
  
  .highlight {
    color: #3b82f6;
    font-weight: 600;
  }
  
  .points-required {
    color: #ef4444;
    font-weight: 700;
  }
}

.points-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 16px;
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  
  .label {
    font-size: 12px;
    color: #94a3b8;
  }
  
  .value {
    font-size: 20px;
    font-weight: 800;
    
    &.current {
      color: #3b82f6;
    }
    
    &.required {
      color: #ef4444;
    }
    
    &.shortage {
      color: #f59e0b;
    }
  }
}

.status-divider {
  color: #cbd5e1;
  font-weight: 700;
  font-size: 14px;
}

.suggestions {
  margin-bottom: 16px;
  
  .suggestion-text {
    font-size: 13px;
    color: #64748b;
    margin: 0;
  }
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 12px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  background: #fff;
  
  .el-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
  }
  
  .btn-content {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .btn-title {
    font-size: 16px;
    font-weight: 700;
  }
  
  .btn-desc {
    font-size: 12px;
    color: #64748b;
  }
  
  &.buy-points {
    border-color: #dbeafe;
    background: linear-gradient(135deg, #eff6ff, #fff);
    
    .el-icon {
      background: linear-gradient(135deg, #60a5fa, #3b82f6);
      color: #fff;
    }
    
    .btn-title {
      color: #3b82f6;
    }
    
    &:hover {
      border-color: #3b82f6;
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(59, 130, 246, 0.2);
    }
  }
  
  &.upgrade-member {
    border-color: #fde68a;
    background: linear-gradient(135deg, #fef9c3, #fff);
    
    .el-icon {
      background: linear-gradient(135deg, #fbbf24, #f59e0b);
      color: #fff;
    }
    
    .btn-title {
      color: #d97706;
    }
    
    &:hover {
      border-color: #f59e0b;
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(245, 158, 11, 0.2);
    }
  }
}

.close-btn {
  width: 100%;
  padding: 12px;
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 14px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  
  &:hover {
    background: #f1f5f9;
    color: #64748b;
  }
}

:deep(.insufficient-dialog) {
  border-radius: 24px;
  overflow: hidden;
  
  .el-dialog__header {
    display: none;
  }
  
  .el-dialog__body {
    padding: 0;
  }
}
</style>
