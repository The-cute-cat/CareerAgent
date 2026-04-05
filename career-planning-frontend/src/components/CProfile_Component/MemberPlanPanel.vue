<script setup lang="ts">
import { computed, ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar, Opportunity, WarningFilled, RefreshRight, CircleCheck, Timer, Loading } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/modules/user'
import type { AccountPointsData } from '@/api/points'
import {
  createPaymentService,
  buildAlipayPagePayUrl,
  queryPaymentStatusService,
  type PaymentOrderVO,
  type PaymentStatusVO
} from '@/api/payment'
import type { PaymentCreateRequest } from '@/api/payment'

const props = defineProps({
  points: {
    type: Number,
    default: 0
  },
  records: {
    type: Array,
    default: () => []
  },
  accountPoints: {
    type: Object as () => AccountPointsData | null,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const userStore = useUserStore()

const activeCenter = ref<'member' | 'points'>('member')
const upgradeVisible = ref(false)
const earnVisible = ref(false)
const insufficientVisible = ref(false)

// 支付相关状态
const payDialogVisible = ref(false)
const payLoading = ref(false)
const payQRCode = ref('')
const currentOrderId = ref('')
const currentPlan = ref<typeof memberPlans[0] | null>(null)
const payStatus = ref<'pending' | 'paid' | 'expired' | 'cancelled'>('pending')
const payCountdown = ref(300)
const pollingTimer = ref<ReturnType<typeof setInterval> | null>(null)
const countdownTimer = ref<ReturnType<typeof setInterval> | null>(null)

const memberType = computed(() => String((userStore.userInfo as any)?.memberType || 'normal').toLowerCase())
const memberExpireAt = computed(() => (userStore.userInfo as any)?.memberExpireAt || '')
const displayPoints = computed(() => Number(props.points || (userStore.userInfo as any)?.points || 0))
const accountSummary = computed(() => props.accountPoints)

const formatDateTime = (value?: string) => {
  if (!value) return '暂无'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  const hh = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${min}`
}

const memberPlans = [
  {
    key: 'monthly',
    title: '月度会员',
    tag: '',
    price: '29',
    giftPoints: 1000,
    monthlyPoints: 1000,
    discount: '9 折',
    badgeClass: 'is-monthly'
  },
  {
    key: 'quarterly',
    title: '季度会员',
    tag: '推荐',
    price: '79',
    giftPoints: 2500,
    monthlyPoints: 1200,
    discount: '8 折',
    badgeClass: 'is-quarterly'
  },
  {
    key: 'yearly',
    title: '年度会员',
    tag: '最划算',
    price: '249',
    giftPoints: 5000,
    monthlyPoints: 1500,
    discount: '7 折',
    badgeClass: 'is-yearly'
  }
]

const earningMethods = [
  { title: '注册成功', points: '+500', desc: '新用户完成注册后立即到账，可选填邀请码。' },
  { title: '每日签到', points: '+100', desc: '连续签到可稳定积累积分，用于功能体验与报告生成。' },
  { title: '邀请好友', points: '+200', desc: '好友成功注册后获得邀请奖励，适合快速补充积分。' },
  { title: '提交反馈', points: '+50', desc: '提交高质量建议或问题反馈，可获得平台感谢积分。' }
]

const consumptionRules = [
  { title: 'AI 职业测评', points: 20 },
  { title: '岗位推荐分析', points: 30 },
  { title: '简历优化', points: 50 },
  { title: '简历一键生成', points: 60 },
  { title: '模拟面试', points: 80 },
  { title: '生涯规划报告', points: 100 },
  { title: 'AI 问答', points: 10 }
]

const memberBenefits = [
  '开通时赠送专属积分礼包',
  '每月自动发放会员积分',
  '积分消费享受专属折扣',
  '高级能力与模板优先解锁',
  '高峰时段享受更高处理优先级'
]

const pointRecords = computed(() => {
  if ((props.records as any[]).length) {
    return props.records as any[]
  }

  return [
    { id: 1, type: '每日积分', remain: 100, total: 100, expireText: '今日已领取' },
    { id: 2, type: '邀请奖励', remain: 200, total: 200, expireText: '距离到期还有 29 天' },
    { id: 3, type: '新用户注册奖励', remain: 500, total: 500, expireText: '注册当日发放' }
  ]
})

const pointSummaryCards = computed(() => {
  if (!accountSummary.value) {
    return []
  }

  return [
    { title: '账户余额', value: accountSummary.value.pointsBalance, desc: '当前可直接使用的积分' },
    { title: '累计消耗', value: accountSummary.value.totalConsumed, desc: '历史使用掉的积分总量' },
    { title: '邀请人数', value: accountSummary.value.referralCount, desc: '通过邀请带来的注册人数' },
    { title: '邀请奖励', value: accountSummary.value.referralRewardTotal, desc: '邀请累计获得的积分奖励' }
  ]
})

const currentMemberText = computed(() => {
  const map: Record<string, string> = {
    normal: '普通用户',
    monthly: '月度会员',
    quarterly: '季度会员',
    quarter: '季度会员',
    yearly: '年度会员',
    annual: '年度会员'
  }
  return map[memberType.value] || '普通用户'
})

const currentMemberPlan = computed(() => memberPlans.find((item) => item.key === memberType.value))
const expiryText = computed(() => memberExpireAt.value || '暂未开通会员')

const handlePlanAction = (planKey: string) => {
  const plan = memberPlans.find((item) => item.key === planKey)
  if (!plan) return

  currentPlan.value = plan
  startPayment(plan)
}

const formatCountdown = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const startPayment = async (plan: typeof memberPlans[0]) => {
  payLoading.value = true
  payDialogVisible.value = true
  payStatus.value = 'pending'
  payCountdown.value = 300

  try {
    // 1. 构建创建订单请求参数
    const memberLevelMap: Record<string, number> = {
      'monthly': 1,
      'quarterly': 2,
      'yearly': 3
    }

    const request: PaymentCreateRequest = {
      amount: parseFloat(plan.price),
      pointsGranted: plan.giftPoints,
      payType: 2,           // 2=支付宝
      purpose: 2,           // 2=会员购买
      memberLevel: memberLevelMap[plan.key]
    }

    // 2. 调用后端创建订单
    const res = await createPaymentService(request)

    if (res.data.code !== 0 || !res.data.data) {
      ElMessage.error(res.data.msg || '创建支付订单失败')
      closePayDialog()
      return
    }

    const orderData: PaymentOrderVO = res.data.data
    const orderId = String(orderData.id)  // 雪花算法生成的订单号
    currentOrderId.value = orderId
    currentPlan.value = plan

    // 3. 构建支付宝电脑网站支付跳转URL
    const payUrl = buildAlipayPagePayUrl(orderId)

    // 4. 新窗口打开支付宝收银台
    const payWindow = window.open(payUrl, '_blank', 'width=1200,height=800,menubar=no,toolbar=no,location=yes')

    if (!payWindow) {
      ElMessage.warning('支付窗口被拦截，请允许浏览器弹窗后重试')
      payLoading.value = false
      return
    }

    // 5. 开始轮询支付状态
    startPolling(orderId)
    // 开始倒计时
    startCountdown()

    ElMessage.info('请在支付宝页面完成支付')
  } catch (error) {
    console.error('支付错误:', error)
    ElMessage.error('发起支付失败，请稍后重试')
    closePayDialog()
  } finally {
    payLoading.value = false
  }
}

const startPolling = (orderId: string) => {
  // 清除之前的轮询
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
  }

  let pollCount = 0
  const maxPollCount = 100 // 最多轮询100次（约5分钟）

  pollingTimer.value = setInterval(async () => {
    pollCount++

    if (pollCount > maxPollCount) {
      stopPolling()
      payStatus.value = 'expired'
      return
    }

    try {
      const res = await queryPaymentStatusService(orderId)

      if (res.data.code === 0 && res.data.data) {
        const statusData = res.data.data as PaymentStatusVO
        payStatus.value = statusData.status as 'pending' | 'paid' | 'expired' | 'cancelled'

        if (statusData.status === 'paid') {
          stopPolling()
          stopCountdown()
          ElMessage.success('支付成功！会员权益已开通')

          // TODO: 更新用户会员信息，需要后端返回 memberExpireAt
          // if (statusData.memberExpireAt && userStore.userInfo) {
          //   (userStore.userInfo as any).memberType = currentPlan.value?.key
          //   ;(userStore.userInfo as any).memberExpireAt = statusData.memberExpireAt
          // }

          // 延迟关闭弹窗
          setTimeout(() => {
            closePayDialog()
            upgradeVisible.value = false
          }, 2000)
        } else if (statusData.status === 'expired' || statusData.status === 'cancelled') {
          stopPolling()
          stopCountdown()
        }
      }
    } catch (error) {
      console.error('查询支付状态失败:', error)
    }
  }, 3000) // 每3秒轮询一次
}

const startCountdown = () => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
  }

  countdownTimer.value = setInterval(() => {
    payCountdown.value--
    if (payCountdown.value <= 0) {
      stopCountdown()
      payStatus.value = 'expired'
      stopPolling()
    }
  }, 1000)
}

const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

const stopCountdown = () => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
    countdownTimer.value = null
  }
}

const closePayDialog = () => {
  payDialogVisible.value = false
  stopPolling()
  stopCountdown()
  payQRCode.value = ''
  currentOrderId.value = ''
  currentPlan.value = null
  payStatus.value = 'pending'
  payCountdown.value = 300
}

const refreshPaymentStatus = () => {
  if (currentOrderId.value && payStatus.value === 'pending') {
    queryPaymentStatusService(currentOrderId.value).then((res) => {
      if (res.data.code === 0 && res.data.data) {
        const statusData = res.data.data as PaymentStatusVO
        payStatus.value = statusData.status as 'pending' | 'paid' | 'expired' | 'cancelled'
        if (statusData.status === 'paid') {
          stopPolling()
          stopCountdown()
          ElMessage.success('支付成功！会员权益已开通')
          // TODO: 更新用户会员信息，需要后端返回 memberExpireAt
          // if (statusData.memberExpireAt && userStore.userInfo) {
          //   ;(userStore.userInfo as any).memberType = currentPlan.value?.key
          //   ;(userStore.userInfo as any).memberExpireAt = statusData.memberExpireAt
          // }
          setTimeout(() => {
            closePayDialog()
            upgradeVisible.value = false
          }, 2000)
        }
      }
    })
  }
}

onUnmounted(() => {
  stopPolling()
  stopCountdown()
})

const handleEarnAction = () => {
  earnVisible.value = true
}

const showInsufficientDialog = () => {
  insufficientVisible.value = true
}

const handleBuyPoints = () => {
  insufficientVisible.value = false
  activeCenter.value = 'points'
  ElMessage.info('这里可以继续接入购买积分流程')
}

const handleOpenMember = () => {
  insufficientVisible.value = false
  activeCenter.value = 'member'
  upgradeVisible.value = true
}
</script>

<template>
  <section class="member-panel">
    <div class="panel-tabs">
      <button class="panel-tab" :class="{ active: activeCenter === 'member' }" @click="activeCenter = 'member'">
        会员中心
      </button>
      <button class="panel-tab" :class="{ active: activeCenter === 'points' }" @click="activeCenter = 'points'">
        积分中心
      </button>
    </div>

    <div class="overview-grid">
      <div class="overview-card overview-card--member">
        <div class="overview-label">当前会员</div>
        <div class="overview-value">{{ currentMemberText }}</div>
        <div class="overview-desc">到期时间：{{ expiryText }}</div>
        <button class="ghost-btn" @click="upgradeVisible = true">升级会员</button>
      </div>

      <div class="overview-card overview-card--points">
        <div class="overview-label">可用积分</div>
        <div class="overview-value">{{ displayPoints }}</div>
        <div class="overview-desc">
          {{ currentMemberPlan ? `当前享受积分消费 ${currentMemberPlan.discount}` : '普通用户按原价消耗积分' }}
        </div>
        <div v-if="accountSummary" class="points-update-time">
          最近更新时间：{{ formatDateTime(accountSummary.updateTime) }}
        </div>
        <div class="overview-actions">
          <button class="ghost-btn ghost-btn--light" @click="handleEarnAction">获取积分</button>
          <button class="ghost-btn ghost-btn--light" @click="showInsufficientDialog">积分不足演示</button>
        </div>
      </div>
    </div>

    <div v-if="activeCenter === 'member'" class="content-stack">
      <div class="section-head">
        <div>
          <h3>会员套餐</h3>
          <p>月度、季度、年度三种方案，适合不同阶段的成长节奏。</p>
        </div>
      </div>

      <div class="plan-grid">
        <article v-for="plan in memberPlans" :key="plan.key" class="plan-card" :class="plan.badgeClass">
          <div class="plan-top">
            <div class="plan-title-row">
              <h4>{{ plan.title }}</h4>
              <span v-if="plan.tag" class="plan-tag">{{ plan.tag }}</span>
            </div>
            <div class="plan-price">¥{{ plan.price }}</div>
          </div>
          <ul class="plan-meta">
            <li>开通赠送 {{ plan.giftPoints }} 积分</li>
            <li>每月发放 {{ plan.monthlyPoints }} 积分</li>
            <li>功能消费享受 {{ plan.discount }}</li>
          </ul>
          <button class="primary-btn" @click="handlePlanAction(plan.key)">立即开通</button>
        </article>
      </div>

      <div class="benefit-panel">
        <div class="section-head">
          <div>
            <h3>会员权益</h3>
            <p>除了积分赠送外，还会同步解锁更完整的成长体验。</p>
          </div>
        </div>
        <div class="benefit-list">
          <div v-for="item in memberBenefits" :key="item" class="benefit-item">
            <el-icon><Opportunity /></el-icon>
            <span>{{ item }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="content-stack">
      <div class="section-head">
        <div>
          <h3>获取积分</h3>
          <p>先看积分余额，再选择最适合当前阶段的获取方式。</p>
        </div>
        <button class="text-btn" @click="earnVisible = true">查看全部方式</button>
      </div>

      <div class="method-grid">
        <article v-for="item in earningMethods" :key="item.title" class="method-card">
          <div class="method-points">{{ item.points }}</div>
          <h4>{{ item.title }}</h4>
          <p>{{ item.desc }}</p>
        </article>
      </div>

      <div v-if="accountSummary || loading" class="records-panel">
        <div class="section-head">
          <div>
            <h3>账户积分概览</h3>
            <p>展示账户积分接口返回的余额、消耗、邀请和更新时间信息。</p>
          </div>
        </div>
        <div v-if="loading" class="account-empty">积分数据加载中...</div>
        <div v-else class="summary-grid">
          <div v-for="item in pointSummaryCards" :key="item.title" class="summary-card">
            <span>{{ item.title }}</span>
            <strong>{{ item.value }}</strong>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>

      <div class="rules-panel">
        <div class="section-head">
          <div>
            <h3>积分消耗规则</h3>
            <p>使用功能前展示预计扣减，积分不足时将弹出购买或开通会员入口。</p>
          </div>
        </div>
        <div class="rule-grid">
          <div v-for="item in consumptionRules" :key="item.title" class="rule-card">
            <span>{{ item.title }}</span>
            <strong>{{ item.points }} 积分 / 次</strong>
          </div>
        </div>
      </div>

      <div class="records-panel">
        <div class="section-head">
          <div>
            <h3>积分明细</h3>
            <p>结合账户接口结果，展示当前余额、累计消耗与邀请奖励来源。</p>
          </div>
        </div>
        <div v-if="loading" class="account-empty">积分明细加载中...</div>
        <div v-else-if="pointRecords.length" class="record-list">
          <div v-for="item in pointRecords" :key="item.id" class="record-item">
            <div class="record-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="record-main">
              <div class="record-title">{{ item.type }}</div>
              <div class="record-desc">剩余 {{ item.remain }} · 总计 {{ item.total }}</div>
            </div>
            <div class="record-side">
              <strong>{{ item.total }}</strong>
              <span>{{ item.expireText }}</span>
            </div>
          </div>
        </div>
        <div v-else class="account-empty">当前暂无积分数据</div>
      </div>
    </div>

    <el-dialog v-model="upgradeVisible" title="基础会员升级" width="680px" class="member-dialog">
      <div class="dialog-stack">
        <div class="dialog-intro">
          <p>当前身份：{{ currentMemberText }}</p>
          <p>开通会员后，积分赠送、每月补给和积分折扣会立即生效。</p>
        </div>
        <div class="plan-grid plan-grid--dialog">
          <article v-for="plan in memberPlans" :key="`${plan.key}-dialog`" class="plan-card" :class="plan.badgeClass">
            <div class="plan-top">
              <div class="plan-title-row">
                <h4>{{ plan.title }}</h4>
                <span v-if="plan.tag" class="plan-tag">{{ plan.tag }}</span>
              </div>
              <div class="plan-price">¥{{ plan.price }}</div>
            </div>
            <ul class="plan-meta">
              <li>赠送 {{ plan.giftPoints }} 积分</li>
              <li>每月补给 {{ plan.monthlyPoints }} 积分</li>
              <li>积分消费 {{ plan.discount }}</li>
            </ul>
          </article>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="earnVisible" title="获取积分" width="720px" class="member-dialog">
      <div class="dialog-method-grid">
        <article v-for="item in earningMethods" :key="`${item.title}-dialog`" class="method-card">
          <div class="method-points">{{ item.points }}</div>
          <h4>{{ item.title }}</h4>
          <p>{{ item.desc }}</p>
        </article>
      </div>
    </el-dialog>

    <el-dialog v-model="insufficientVisible" title="积分不足" width="420px" class="member-dialog">
      <div class="insufficient-box">
        <el-icon class="warning-icon"><WarningFilled /></el-icon>
        <h4>当前积分不足以完成本次操作</h4>
        <p>你可以购买积分继续使用，也可以开通会员获取更多积分和折扣权益。</p>
        <div class="insufficient-actions">
          <button class="ghost-btn" @click="handleBuyPoints">购买积分</button>
          <button class="primary-btn" @click="handleOpenMember">开通会员</button>
        </div>
      </div>
    </el-dialog>

    <!-- 支付宝支付弹窗 -->
    <el-dialog
      v-model="payDialogVisible"
      :title="`开通${currentPlan?.title || '会员'}`"
      width="480px"
      class="member-dialog pay-dialog"
      :close-on-click-modal="false"
      :show-close="payStatus !== 'pending'"
      @close="closePayDialog"
    >
      <div v-loading="payLoading" class="pay-dialog-content">
        <!-- 支付中状态 -->
        <div v-if="payStatus === 'pending'" class="pay-pending">
          <div class="pay-amount">
            <span class="pay-amount-label">支付金额</span>
            <span class="pay-amount-value">¥{{ currentPlan?.price }}</span>
          </div>

          <!-- 等待支付提示（电脑网站支付） -->
          <div class="waiting-pay-box">
            <div class="waiting-icon">
              <el-icon class="loading-icon"><Loading /></el-icon>
            </div>
            <h4 class="waiting-title">正在等待支付完成</h4>
            <p class="waiting-desc">已在浏览器新窗口打开支付宝收银台</p>
            <p class="waiting-sub">请在支付宝页面完成支付，完成后本页面会自动更新</p>
          </div>

          <div class="pay-status-bar">
            <div class="countdown">
              <el-icon><Timer /></el-icon>
              <span>支付剩余时间：{{ formatCountdown(payCountdown) }}</span>
            </div>
            <div class="polling-status">
              <span class="polling-dot"></span>
              <span>等待支付...</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="waiting-actions">
            <button class="ghost-btn" @click="closePayDialog">取消支付</button>
            <button class="primary-btn" @click="refreshPaymentStatus">
              <el-icon><RefreshRight /></el-icon>
              已完成支付
            </button>
          </div>
        </div>

        <!-- 支付成功状态 -->
        <div v-else-if="payStatus === 'paid'" class="pay-result pay-success">
          <div class="result-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <h4>支付成功</h4>
          <p>您的{{ currentPlan?.title }}已开通</p>
          <div class="result-actions">
            <button class="primary-btn" @click="closePayDialog">确定</button>
          </div>
        </div>

        <!-- 支付过期/取消状态 -->
        <div v-else class="pay-result pay-failed">
          <div class="result-icon failed">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <h4>{{ payStatus === 'expired' ? '支付已过期' : '支付已取消' }}</h4>
          <p>请重新发起支付</p>
          <div class="result-actions">
            <button class="ghost-btn" @click="closePayDialog">关闭</button>
            <button v-if="currentPlan" class="primary-btn" @click="startPayment(currentPlan)">重新支付</button>
          </div>
        </div>
      </div>
    </el-dialog>
  </section>
</template>

<style scoped lang="scss">
.member-panel { display: flex; flex-direction: column; gap: 32px; font-family: 'Inter', system-ui, sans-serif; }
.panel-tabs, .overview-grid, .plan-grid, .method-grid, .rule-grid, .overview-actions, .insufficient-actions { display: flex; gap: 20px; }
.panel-tabs { gap: 12px; }
.panel-tab, .ghost-btn, .primary-btn, .text-btn { border: none; cursor: pointer; transition: all .3s cubic-bezier(0.4, 0, 0.2, 1); }
.panel-tab { padding: 12px 24px; border-radius: 999px; background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(12px); color: #5f7896; font-weight: 700; border: 1px solid rgba(255,255,255,0.7); box-shadow: 0 4px 12px rgba(0,0,0,0.02); }
.panel-tab.active, .primary-btn { color: #fff; background: linear-gradient(135deg, #1f6feb, #47a1f5); box-shadow: 0 8px 20px rgba(31, 111, 235, 0.3); border-color: transparent; }
.panel-tab:not(.active):hover { background: rgba(255,255,255,0.9); transform: translateY(-1px); }
.overview-grid, .plan-grid, .method-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.overview-grid { grid-template-columns: 1.2fr 1fr; }
.overview-card, .benefit-panel, .rules-panel, .records-panel { border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 32px; backdrop-filter: blur(20px); box-shadow: 0 16px 40px rgba(18, 56, 94, 0.05), inset 0 1px 2px rgba(255,255,255,1); }
.overview-card { padding: 32px; }
.overview-card--member { background: linear-gradient(135deg, rgba(248,250,255,0.85), rgba(255,255,255,0.7)); }
.overview-card--points { padding: 32px; color: #0f172a; background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); position: relative; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 20px 48px rgba(15, 23, 42, 0.04); }
.overview-card--points::after { content: ''; position: absolute; right: -50px; bottom: -50px; width: 200px; height: 200px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 70%); }
.overview-label, .overview-desc, .section-head p, .method-card p, .record-desc, .record-side span, .dialog-intro p, .rule-card span { color: #64748b; }
.overview-card--points .overview-label, .overview-card--points .overview-desc { color: #475569; }
.overview-value { margin: 12px 0 10px; font-size: 52px; line-height: 1; font-weight: 900; color: #0f172a; letter-spacing: -0.02em; }
.overview-card--points .overview-value { color: #0f172a; }
.points-update-time { margin-top: 10px; font-size: 13px; color: #475569; }
.ghost-btn { align-self: flex-start; padding: 12px 24px; border-radius: 999px; font-weight: 700; background: #fff; color: #1e62c5; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.ghost-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
.ghost-btn--light { background: #fff; border: 1px solid #cbd5e1; color: #334155; }
.ghost-btn--light:hover { background: #f8fafc; color: #0f172a; }
.content-stack { display: flex; flex-direction: column; gap: 32px; }
.section-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 8px; }
.section-head h3 { margin: 0 0 8px; font-size: 22px; color: #0f172a; font-weight: 800; display: flex; align-items: center; gap: 8px; }
.section-head h3::before { content: ''; display: block; width: 4px; height: 20px; border-radius: 2px; background: linear-gradient(180deg, #1677ff, #67b8ff); }
.section-head p, .method-card p, .dialog-intro p { margin: 0; line-height: 1.7; font-size: 14px; }
.text-btn { padding: 0; color: #1677ff; background: transparent; font-weight: 700; }
.plan-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.plan-card, .method-card, .rule-card, .record-item, .benefit-item, .summary-card { border-radius: 28px; border: 1px solid rgba(255, 255, 255, 0.8); background: rgba(255,255,255,0.65); backdrop-filter: blur(16px); box-shadow: 0 8px 24px rgba(15, 23, 42, 0.03), inset 0 1px 2px rgba(255,255,255,0.9); transition: all 0.3s ease; }
.plan-card:hover, .method-card:hover, .record-item:hover, .summary-card:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06), inset 0 1px 2px rgba(255,255,255,1); }
.plan-card { padding: 32px 28px; display: flex; flex-direction: column; }
.plan-card.is-quarterly { position: relative; border-color: rgba(99, 102, 241, 0.3); background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(238,242,255,0.5)); box-shadow: 0 16px 40px rgba(99, 102, 241, 0.08), inset 0 1px 2px rgba(255,255,255,1); }
.plan-card.is-quarterly::before { content: ''; position: absolute; inset: -2px; border-radius: 30px; padding: 2px; background: linear-gradient(135deg, #a855f7, #6366f1); -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); -webkit-mask-composite: xor; mask-composite: exclude; opacity: 0.5; pointer-events: none; }
.plan-card.is-yearly { border-color: rgba(234, 179, 8, 0.3); background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(254,249,195,0.4)); }
.plan-top, .plan-title-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.plan-title-row h4, .method-card h4, .record-title, .insufficient-box h4 { margin: 0; color: #1e293b; font-size: 18px; font-weight: 800; }
.plan-price { font-size: 40px; font-weight: 900; color: #0f172a; margin: 16px 0; letter-spacing: -0.02em; }
.plan-card.is-quarterly .plan-price { background: linear-gradient(135deg, #7e22ce, #4f46e5); -webkit-background-clip: text; background-clip: text; color: transparent; }
.plan-tag { padding: 4px 12px; border-radius: 999px; background: rgba(99,102,241,.1); color: #4f46e5; font-size: 12px; font-weight: 800; }
.plan-card.is-yearly .plan-tag { background: rgba(234,179,8,.15); color: #ca8a04; }
.plan-meta { margin: 0 0 24px 0; padding-left: 0; color: #475569; line-height: 2; list-style: none; flex: 1; }
.plan-meta li { position: relative; padding-left: 24px; font-size: 14px; font-weight: 600; }
.plan-meta li::before { content: '✓'; position: absolute; left: 0; color: #1677ff; font-weight: 900; }
.plan-card.is-quarterly .plan-meta li::before { color: #9333ea; }
.primary-btn { width: 100%; padding: 16px; border-radius: 18px; font-size: 16px; font-weight: 800; }
.plan-card.is-quarterly .primary-btn { background: linear-gradient(135deg, #9333ea, #6366f1); box-shadow: 0 8px 24px rgba(147, 51, 234, 0.3); }
.benefit-panel, .rules-panel, .records-panel { padding: 32px; background: rgba(255,255,255,0.6); }
.benefit-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.benefit-item, .rule-card, .record-item, .method-card, .summary-card { padding: 22px 24px; }
.benefit-item { display: flex; align-items: center; gap: 16px; color: #1e293b; font-weight: 700; font-size: 15px; }
.benefit-item .el-icon, .warning-icon { color: #1677ff; font-size: 20px; }
.method-card { display: flex; flex-direction: column; gap: 12px; }
.method-points { font-size: 32px; font-weight: 900; color: #1677ff; }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.summary-card span, .account-empty { color: #64748b; font-size: 13px; }
.summary-card strong { display: block; margin: 10px 0 8px; color: #0f172a; font-size: 30px; font-weight: 900; }
.summary-card p { margin: 0; color: #475569; line-height: 1.6; font-size: 13px; }
.account-empty { padding: 28px 8px; text-align: center; }
.rule-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.rule-card { display: flex; align-items: center; justify-content: space-between; gap: 12px; font-weight: 600; color: #334155; }
.rule-card strong, .record-side strong { color: #1677ff; font-size: 18px; font-weight: 800; }
.record-list { display: flex; flex-direction: column; gap: 16px; }
.record-item { display: flex; align-items: center; gap: 20px; }
.record-icon { width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; border-radius: 20px; background: linear-gradient(135deg, #e0e7ff, #f3e8ff); color: #6366f1; font-size: 24px; box-shadow: inset 0 2px 4px rgba(255,255,255,0.8); }
.record-main { flex: 1; min-width: 0; }
.record-title { font-size: 16px; margin-bottom: 4px; }
.record-side { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; text-align: right; }
.record-side span { font-size: 12px; }
.dialog-stack, .dialog-method-grid, .insufficient-box { display: flex; flex-direction: column; gap: 24px; }
.plan-grid--dialog, .dialog-method-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.insufficient-box { align-items: center; text-align: center; padding: 20px 0; }
.warning-icon { font-size: 48px; }
.insufficient-box p { margin: 0; color: #64748b; line-height: 1.8; font-size: 15px; max-width: 80%; }
.insufficient-actions { margin-top: 12px; }

/* 支付弹窗样式 */
.pay-dialog-content {
  padding: 20px 0;
}

.pay-pending {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.pay-amount {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.pay-amount-label {
  font-size: 14px;
  color: #64748b;
}

.pay-amount-value {
  font-size: 36px;
  font-weight: 900;
  color: #0f172a;
  background: linear-gradient(135deg, #1677ff, #47a1f5);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.qr-code-box {
  width: 220px;
  height: 220px;
  border-radius: 16px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e2e8f0;
}

.qr-code-wrapper {
  position: relative;
  width: 200px;
  height: 200px;
}

.qr-code-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.qr-code-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.alipay-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #1677ff;
  border-radius: 999px;
  color: white;
  font-size: 12px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.3);
}

.alipay-icon {
  width: 20px;
  height: 20px;
  background: white;
  color: #1677ff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 900;
}

.qr-code-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #64748b;
  font-size: 14px;
}

.loading-icon {
  font-size: 32px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.pay-instructions {
  text-align: center;
}

.pay-instruction-title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.pay-instruction-sub {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.pay-status-bar {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-radius: 12px;
  border: 1px solid #bae6fd;
}

.countdown {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #0369a1;
  font-size: 14px;
  font-weight: 600;
}

.polling-status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #0891b2;
  font-size: 13px;
}

.polling-dot {
  width: 8px;
  height: 8px;
  background: #06b6d4;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.pay-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px 20px;
  gap: 16px;
}

.result-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #10b981, #34d399);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 40px;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
}

.result-icon.failed {
  background: linear-gradient(135deg, #ef4444, #f87171);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.3);
}

.pay-result h4 {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
}

.pay-result p {
  margin: 0;
  color: #64748b;
  font-size: 15px;
}

.result-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

/* 等待支付样式（电脑网站支付） */
.waiting-pay-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 20px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-radius: 16px;
  border: 1px solid #bae6fd;
  margin: 16px 0;
}

.waiting-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #1677ff, #47a1f5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  box-shadow: 0 8px 24px rgba(22, 119, 255, 0.3);
}

.waiting-icon .loading-icon {
  font-size: 32px;
  color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.waiting-title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.waiting-desc {
  margin: 0 0 4px;
  font-size: 14px;
  color: #0369a1;
  font-weight: 600;
}

.waiting-sub {
  margin: 0;
  font-size: 13px;
  color: #64748b;
  text-align: center;
  max-width: 280px;
}

.waiting-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: center;
}

.waiting-actions .ghost-btn,
.waiting-actions .primary-btn {
  padding: 12px 24px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

@media (max-width: 1200px) {
  .overview-grid, .plan-grid, .method-grid, .rule-grid, .benefit-list, .plan-grid--dialog, .dialog-method-grid, .summary-grid { grid-template-columns: 1fr; }
}
</style>
