import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/modules/user'
import { 
  consumePointsService, 
  getAccountPointsService,
  rechargePointsService,
  type PointsConsumeRequest 
} from '@/api/points'
import { 
  POINTS_CONSUME_CONFIG, 
  calculateActualPoints, 
  getMemberInfo,
  updateMemberInfo,
  getPointsRecords,
  type PointsRecord,
  mockRechargePointsApi
} from '@/mock/mockdata/Points_mockdata'

// 积分不足弹窗状态
const showInsufficientDialog = ref(false)
const insufficientData = ref({
  required: 0,
  current: 0,
  functionName: ''
})

// 积分消费确认弹窗状态
const showConsumeConfirm = ref(false)
const consumeConfirmData = ref({
  functionKey: '',
  functionName: '',
  basePoints: 0,
  actualPoints: 0,
  discount: 0,
  onConfirm: null as (() => void) | null,
  onCancel: null as (() => void) | null
})

// 注册成功弹窗状态
const showWelcomeGift = ref(false)
const welcomeGiftPoints = ref(500)

export function usePoints() {
  const userStore = useUserStore()
  const loading = ref(false)
  const records = ref<PointsRecord[]>([])
  
  const userId = computed(() => Number(userStore.userInfo?.id))
  
  const currentPoints = computed(() => {
    return Number((userStore.userInfo as any)?.pointsBalance || 
           (userStore.userInfo as any)?.points || 0)
  })
  
  const memberInfo = computed(() => {
    if (!userId.value) return null
    return getMemberInfo(userId.value)
  })
  
  const memberType = computed(() => {
    return memberInfo.value?.memberType || 'normal'
  })
  
  const isMember = computed(() => {
    return memberType.value !== 'normal'
  })
  
  const discountRate = computed(() => {
    return memberInfo.value?.discountRate || 1
  })
  
  const memberExpireAt = computed(() => {
    return memberInfo.value?.memberExpireAt
  })
  
  // 获取功能配置
  const getFunctionConfig = (functionKey: keyof typeof POINTS_CONSUME_CONFIG) => {
    return POINTS_CONSUME_CONFIG[functionKey]
  }
  
  // 计算实际消耗积分
  const calculatePoints = (basePoints: number) => {
    if (!userId.value) return basePoints
    return calculateActualPoints(userId.value, basePoints)
  }
  
  // 检查积分是否充足
  const hasEnoughPoints = (points: number) => {
    return currentPoints.value >= points
  }
  
  // 检查功能是否可用（积分是否充足）
  const checkFunctionAvailable = (functionKey: keyof typeof POINTS_CONSUME_CONFIG) => {
    const config = POINTS_CONSUME_CONFIG[functionKey]
    const actualPoints = calculatePoints(config.points)
    
    if (!hasEnoughPoints(actualPoints)) {
      insufficientData.value = {
        required: actualPoints,
        current: currentPoints.value,
        functionName: config.name
      }
      showInsufficientDialog.value = true
      return false
    }
    return true
  }
  
  // 显示积分消费确认
  const showConsumeConfirmDialog = (
    functionKey: keyof typeof POINTS_CONSUME_CONFIG,
    onConfirm: () => void,
    onCancel?: () => void
  ) => {
    const config = POINTS_CONSUME_CONFIG[functionKey]
    const actualPoints = calculatePoints(config.points)
    const discount = Math.round((1 - discountRate.value) * 100)
    
    consumeConfirmData.value = {
      functionKey,
      functionName: config.name,
      basePoints: config.points,
      actualPoints,
      discount,
      onConfirm,
      onCancel: onCancel || null
    }
    showConsumeConfirm.value = true
  }
  
  // 消费积分
  const consumePoints = async (
    functionKey: keyof typeof POINTS_CONSUME_CONFIG,
    description?: string
  ) => {
    const config = POINTS_CONSUME_CONFIG[functionKey]
    const actualPoints = calculatePoints(config.points)

    // 检查积分
    if (!hasEnoughPoints(actualPoints)) {
      insufficientData.value = {
        required: actualPoints,
        current: currentPoints.value,
        functionName: config.name
      }
      showInsufficientDialog.value = true
      return { success: false, code: 'INSUFFICIENT_POINTS' }
    }

    loading.value = true

    try {
      const request: PointsConsumeRequest = {
        userId: userId.value,
        amount: -actualPoints, // 负数表示消费
        type: 2, // 消费类型
        description: description || config.name,
        status: 1
      }

      const result = await consumePointsService(request)

      if (result.data.code === 200) {
        // 更新本地积分
        if (userStore.userInfo) {
          userStore.userInfo = {
            ...userStore.userInfo,
            pointsBalance: result.data.data.pointsBalance,
            points: result.data.data.pointsBalance
          } as any
        }

        ElMessage.success(`成功使用 ${config.name}，消耗 ${actualPoints} 积分`)

        // 刷新记录
        await fetchPointsRecords()

        return { success: true, data: result.data.data }
      } else if (result.data.code === 4001) {
        insufficientData.value = {
          required: actualPoints,
          current: currentPoints.value,
          functionName: config.name
        }
        showInsufficientDialog.value = true
        return { success: false, code: 'INSUFFICIENT_POINTS' }
      } else {
        ElMessage.error(result.data.msg || '积分消费失败')
        return { success: false, code: 'ERROR', msg: result.data.msg }
      }
    } catch (error) {
      console.error('消费积分失败:', error)
      ElMessage.error('网络错误，请稍后重试')
      return { success: false, code: 'NETWORK_ERROR' }
    } finally {
      loading.value = false
    }
  }
  
  // 充值积分（模拟）
  const rechargePoints = async (amount: number, description: string) => {
    loading.value = true
    
    try {
      const result = await mockRechargePointsApi(userId.value, amount, description)
      
      if (result.data.code === 200) {
        // 更新本地积分
        if (userStore.userInfo) {
          userStore.userInfo = {
            ...userStore.userInfo,
            pointsBalance: result.data.data.pointsBalance,
            points: result.data.data.pointsBalance
          } as any
        }
        
        ElMessage.success(`成功充值 ${amount} 积分`)
        await fetchPointsRecords()
        
        return { success: true, data: result.data.data }
      } else {
        ElMessage.error(result.data.msg || '充值失败')
        return { success: false }
      }
    } catch (error) {
      console.error('充值积分失败:', error)
      ElMessage.error('充值失败，请稍后重试')
      return { success: false }
    } finally {
      loading.value = false
    }
  }
  
  // 开通会员
  const upgradeMember = async (memberType: 'monthly' | 'quarterly' | 'yearly') => {
    const memberInfo = updateMemberInfo(userId.value, memberType)
    
    // 更新本地用户信息
    if (userStore.userInfo) {
      userStore.userInfo = {
        ...userStore.userInfo,
        memberType: memberInfo.memberType,
        memberExpireAt: memberInfo.memberExpireAt
      } as any
    }
    
    ElMessage.success(`恭喜您成功开通${memberInfo.memberType === 'monthly' ? '月度' : memberInfo.memberType === 'quarterly' ? '季度' : '年度'}会员！`)
    
    return { success: true, data: memberInfo }
  }
  
  // 获取积分记录
  const fetchPointsRecords = async () => {
    if (!userId.value) return
    records.value = getPointsRecords(userId.value)
  }
  
  // 同步积分
  const syncPoints = async () => {
    if (!userId.value) return
    
    try {
      const result = await getAccountPointsService(userId.value)
      if (result.data.code === 200 && result.data.data) {
        if (userStore.userInfo) {
          userStore.userInfo = {
            ...userStore.userInfo,
            pointsBalance: result.data.data.pointsBalance,
            points: result.data.data.pointsBalance
          } as any
        }
      }
    } catch (error) {
      console.warn('同步积分失败:', error)
    }
  }
  
  // 显示新用户欢迎弹窗
  const showNewUserWelcome = (points: number = 500) => {
    welcomeGiftPoints.value = points
    showWelcomeGift.value = true
  }
  
  // 跳转到积分中心
  const goToPointsCenter = () => {
    // 可以通过路由跳转到积分中心页面
    window.location.href = '/#/profile?tab=member'
  }
  
  // 跳转到会员中心
  const goToMemberCenter = () => {
    window.location.href = '/#/profile?tab=member'
  }
  
  return {
    // 状态
    loading,
    currentPoints,
    memberType,
    memberInfo,
    isMember,
    discountRate,
    memberExpireAt,
    records,
    
    // 弹窗状态
    showInsufficientDialog,
    insufficientData,
    showConsumeConfirm,
    consumeConfirmData,
    showWelcomeGift,
    welcomeGiftPoints,
    
    // 方法
    getFunctionConfig,
    calculatePoints,
    hasEnoughPoints,
    checkFunctionAvailable,
    showConsumeConfirmDialog,
    consumePoints,
    rechargePoints,
    upgradeMember,
    fetchPointsRecords,
    syncPoints,
    showNewUserWelcome,
    goToPointsCenter,
    goToMemberCenter,
    
    // 配置
    POINTS_CONSUME_CONFIG,
    MEMBER_CONFIG: {
      monthly: { name: '月度会员', giftPoints: 1000, monthlyPoints: 1000, discountRate: 0.9, price: 29.9 },
      quarterly: { name: '季度会员', giftPoints: 3500, monthlyPoints: 1200, discountRate: 0.8, price: 79.9 },
      yearly: { name: '年度会员', giftPoints: 15000, monthlyPoints: 1500, discountRate: 0.7, price: 299.9 }
    }
  }
}

// 导出单例状态，供组件共享
export {
  showInsufficientDialog,
  insufficientData,
  showConsumeConfirm,
  consumeConfirmData,
  showWelcomeGift,
  welcomeGiftPoints
}
