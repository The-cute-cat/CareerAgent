<script setup lang="ts">
import { computed } from 'vue'
import { Coin, InfoFilled, Check } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: boolean
  functionName: string
  basePoints: number
  actualPoints: number
  discount: number
  currentPoints: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const hasDiscount = computed(() => props.discount > 0)

const remainingPoints = computed(() => props.currentPoints - props.actualPoints)

const handleConfirm = () => {
  visible.value = false
  emit('confirm')
}

const handleCancel = () => {
  visible.value = false
  emit('cancel')
}
</script>

<template>
  <el-dialog
    v-model="visible"
    width="400px"
    :show-close="false"
    class="consume-confirm-dialog"
    :close-on-click-modal="false"
    append-to-body
  >
    <div class="consume-content">
      <!-- 标题 -->
      <div class="header">
        <div class="icon-wrapper">
          <el-icon><Coin /></el-icon>
        </div>
        <h3 class="title">确认使用</h3>
      </div>
      
      <!-- 功能信息 -->
      <div class="function-info">
        <p class="function-name">{{ functionName }}</p>
        <p class="function-desc">本次操作将消耗积分</p>
      </div>
      
      <!-- 积分信息 -->
      <div class="points-info">
        <div class="points-display">
          <span v-if="hasDiscount" class="original-points">{{ basePoints }}</span>
          <span class="actual-points">{{ actualPoints }}</span>
          <span class="points-unit">积分</span>
        </div>
        
        <!-- 折扣标签 -->
        <div v-if="hasDiscount" class="discount-badge">
          <el-icon><Check /></el-icon>
          会员 {{ discount }}% 折扣已生效
        </div>
      </div>
      
      <!-- 积分余额 -->
      <div class="balance-info">
        <div class="balance-row">
          <span class="label">当前积分</span>
          <span class="value">{{ currentPoints }}</span>
        </div>
        <div class="balance-row">
          <span class="label">消耗积分</span>
          <span class="value minus">- {{ actualPoints }}</span>
        </div>
        <div class="balance-divider"></div>
        <div class="balance-row">
          <span class="label">剩余积分</span>
          <span class="value remaining">{{ remainingPoints }}</span>
        </div>
      </div>
      
      <!-- 提示信息 -->
      <div class="tips">
        <el-icon><InfoFilled /></el-icon>
        <span>积分一经消耗不可退还，请确认后再操作</span>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions">
        <button class="btn cancel" @click="handleCancel">
          取消
        </button>
        <button class="btn confirm" @click="handleConfirm">
          确认使用
        </button>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped lang="scss">
.consume-content {
  padding: 28px 24px;
}

.header {
  text-align: center;
  margin-bottom: 20px;
}

.icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  
  .el-icon {
    font-size: 32px;
    color: #3b82f6;
  }
}

.title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.function-info {
  text-align: center;
  margin-bottom: 24px;
  
  .function-name {
    font-size: 18px;
    font-weight: 700;
    color: #3b82f6;
    margin: 0 0 6px;
  }
  
  .function-desc {
    font-size: 13px;
    color: #94a3b8;
    margin: 0;
  }
}

.points-info {
  text-align: center;
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #fef9c3, #fef3c7);
  border-radius: 16px;
  border: 1px solid #fde68a;
}

.points-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 6px;
  margin-bottom: 10px;
  
  .original-points {
    font-size: 20px;
    color: #94a3b8;
    text-decoration: line-through;
    font-weight: 500;
  }
  
  .actual-points {
    font-size: 42px;
    font-weight: 900;
    color: #d97706;
    line-height: 1;
  }
  
  .points-unit {
    font-size: 14px;
    color: #d97706;
    font-weight: 600;
  }
}

.discount-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  
  .el-icon {
    font-size: 14px;
  }
}

.balance-info {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
}

.balance-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  
  .label {
    font-size: 14px;
    color: #64748b;
  }
  
  .value {
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
    
    &.minus {
      color: #ef4444;
    }
    
    &.remaining {
      color: #3b82f6;
      font-size: 18px;
    }
  }
}

.balance-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 8px 0;
}

.tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #fff7ed;
  border-radius: 8px;
  margin-bottom: 20px;
  
  .el-icon {
    color: #f97316;
    font-size: 16px;
  }
  
  span {
    font-size: 12px;
    color: #c2410c;
  }
}

.actions {
  display: flex;
  gap: 12px;
}

.btn {
  flex: 1;
  padding: 14px 20px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  
  &.cancel {
    background: #f1f5f9;
    color: #64748b;
    
    &:hover {
      background: #e2e8f0;
    }
  }
  
  &.confirm {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: #fff;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
    }
  }
}

:deep(.consume-confirm-dialog) {
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
