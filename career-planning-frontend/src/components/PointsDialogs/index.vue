<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/modules/user'
import { 
  usePoints, 
  showInsufficientDialog, 
  insufficientData,
  showConsumeConfirm,
  consumeConfirmData,
  showWelcomeGift,
  welcomeGiftPoints
} from '@/composables/usePoints'
import InsufficientPointsDialog from './InsufficientPointsDialog.vue'
import ConsumeConfirmDialog from './ConsumeConfirmDialog.vue'
import WelcomeGiftDialog from './WelcomeGiftDialog.vue'

const userStore = useUserStore()
const { currentPoints, consumePoints } = usePoints()

// 消费确认相关
const consumeVisible = computed({
  get: () => showConsumeConfirm.value,
  set: (val) => { showConsumeConfirm.value = val }
})

const consumeData = computed(() => consumeConfirmData.value)

const actualPoints = computed(() => {
  if (!consumeData.value.functionKey) return 0
  return consumeData.value.actualPoints
})

const handleConsumeConfirm = async () => {
  if (consumeData.value.onConfirm) {
    // 执行消费
    const result = await consumePoints(
      consumeData.value.functionKey as any,
      consumeData.value.functionName
    )
    
    if (result.success) {
      consumeData.value.onConfirm()
    }
  }
}

const handleConsumeCancel = () => {
  if (consumeData.value.onCancel) {
    consumeData.value.onCancel()
  }
}
</script>

<template>
  <div class="points-dialogs-container">
    <!-- 积分不足弹窗 -->
    <InsufficientPointsDialog
      v-model="showInsufficientDialog"
      :required="insufficientData.required"
      :current="insufficientData.current"
      :function-name="insufficientData.functionName"
    />
    
    <!-- 消费确认弹窗 -->
    <ConsumeConfirmDialog
      v-model="consumeVisible"
      :function-name="consumeData.functionName"
      :base-points="consumeData.basePoints"
      :actual-points="actualPoints"
      :discount="consumeData.discount"
      :current-points="currentPoints"
      @confirm="handleConsumeConfirm"
      @cancel="handleConsumeCancel"
    />
    
    <!-- 新用户欢迎弹窗 -->
    <WelcomeGiftDialog
      v-model="showWelcomeGift"
      :points="welcomeGiftPoints"
    />
  </div>
</template>
