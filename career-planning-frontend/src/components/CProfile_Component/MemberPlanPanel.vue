<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Calendar, Back, Close, Coin, Medal, TrendCharts,
  ArrowRight, Share, ShoppingCart, WarningFilled, Promotion, Reading, Setting, Search, InfoFilled,
  Loading, CircleCheckFilled, CircleCloseFilled
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/modules/user'
import { rechargePointsService, getPackagesByTypeService, type PointsMembershipChangeDTO } from '@/api/points'
import type { AccountPointsData } from '@/api/points'
import alipayIcon from '@/assets/images/alipay.png'
import wechatIcon from '@/assets/images/wechat.png'
import {
  createPaymentService,
  buildAlipayPagePayUrl,
  queryPaymentStatusService
} from '@/api/payment'
import type { PaymentOrderRequest } from '@/api/payment'

// 计划类型定义
interface MemberPlan {
  key: string
  title: string
  duration: string
  price: string
  unit: string
  dailyCost: string
  dailyPoints: number
  totalPoints: number
  tag: string
  badgeClass: string
  color: string
  gradient: string
}

interface PointsPlan {
  key: string
  title: string
  points: number
  price: string
  unit: string
  tag: string
  badgeClass: string
  color: string
  gradient: string
}

const props = defineProps({
  points: { type: Number, default: 0 },
  records: { type: Array, default: () => [] },
  accountPoints: { type: Object as () => AccountPointsData | null, default: null },
  loading: { type: Boolean, default: false },
  inviteCode: { type: String as () => string | null, default: null }
})

const emit = defineEmits(['open-invite'])

const userStore = useUserStore()

// Purchase Center Dialog
const purchaseCenterVisible = ref(false)
const activePurchaseTab = ref<'points' | 'member'>('points')
const selectedMemberPlan = ref<number | string>('quarterly')
const selectedPointsPlan = ref<number | string>('invite')
const payMethodVisible = ref(false)
const currentPayMethod = ref<'alipay' | 'wechat'>('alipay')

const DEFAULT_MEMBER_PLANS = [
  {
    key: 'monthly',
    packageId: 'monthly',
    title: '月度会员',
    duration: '1 个月',
    price: '15',
    points: 10800,
    unit: '/月',
    tag: '尝鲜首选',
    color: '#3b82f6',
    gradient: 'linear-gradient(135deg, #60a5fa, #3b82f6)'
  },
  {
    key: 'quarterly',
    packageId: 'quarterly',
    title: '季度会员',
    duration: '3 个月',
    price: '36',
    points: 10800,
    unit: '/季',
    tag: '性价比之选',
    color: '#6366f1',
    gradient: 'linear-gradient(135deg, #818cf8, #4f46e5)'
  },
  {
    key: 'yearly',
    packageId: 'yearly',
    title: '年度会员',
    duration: '12 个月',
    price: '128',
    points: 131400,
    unit: '/年',
    tag: '最大优惠',
    color: '#a855f7',
    gradient: 'linear-gradient(135deg, #c084fc, #9333ea)'
  }
]

const DEFAULT_POINTS_PLANS = [
  {
    key: 'invite',
    packageId: 'invite',
    title: '免费获取',
    points: 500,
    price: '0.00',
    tag: '免费获取',
    color: '#f59e0b',
    gradient: 'linear-gradient(135deg, #fbbf24, #f59e0b)'
  },
  {
    key: 'basic',
    packageId: 'basic',
    title: '尝鲜首选',
    points: 1000,
    price: '9.90',
    tag: '尝鲜首选',
    color: '#3b82f6',
    gradient: 'linear-gradient(135deg, #60a5fa, #3b82f6)'
  },
  {
    key: 'value',
    packageId: 'value',
    title: '高性价比',
    points: 3000,
    price: '16.60',
    tag: '高性价比',
    color: '#8b5cf6',
    gradient: 'linear-gradient(135deg, #a78bfa, #7c3aed)'
  }
]

const memberPlans = ref<any[]>(DEFAULT_MEMBER_PLANS)
const pointsPurchasePlans = ref<any[]>(DEFAULT_POINTS_PLANS)

const memberType = computed(() => String((userStore.userInfo as any)?.memberType || 'normal').toLowerCase())
const displayPoints = computed(() => Number(props.points || (userStore.userInfo as any)?.points || 0))

const fetchPackages = async () => {
  try {
    const [pointsRes, memberRes] = await Promise.all([
      getPackagesByTypeService(1),
      getPackagesByTypeService(2)
    ])

    if (pointsRes.data.code === 200 && pointsRes.data.data) {
      interface ColorTheme { color: string; gradient: string }
      const themes: ColorTheme[] = [
        { color: '#8b5cf6', gradient: 'linear-gradient(135deg, #a78bfa, #7c3aed)' },
        { color: '#3b82f6', gradient: 'linear-gradient(135deg, #60a5fa, #3b82f6)' },
        { color: '#ec4899', gradient: 'linear-gradient(135deg, #f472b6, #db2777)' },
        { color: '#06b6d4', gradient: 'linear-gradient(135deg, #22d3ee, #0891b2)' }
      ]

      const backendPoints = pointsRes.data.data.map((pkg: any, index: number) => {
        const theme = themes[index % themes.length] as ColorTheme
        return {
          packageId: pkg.id,
          key: pkg.id,
          title: pkg.name || pkg.description || `积分方案 ${pkg.id}`,
          points: pkg.points || 0,
          price: (pkg.price || pkg.amount || 0).toFixed(2),
          tag: pkg.description || '推荐',
          color: theme.color,
          gradient: theme.gradient
        }
      })

      pointsPurchasePlans.value = [
        {
          key: 'invite',
          packageId: 'invite',
          title: '免费获取',
          points: 500,
          price: '0.00',
          tag: '免费获取',
          color: '#f59e0b',
          gradient: 'linear-gradient(135deg, #fbbf24, #f59e0b)'
        },
        ...backendPoints
      ]
    }

    if (memberRes.data.code === 200 && memberRes.data.data) {
      memberPlans.value = memberRes.data.data.map((pkg: any) => ({
        packageId: pkg.id,
        key: pkg.id,
        title: pkg.name || pkg.description || '会员套餐',
        duration: pkg.description || '会员',
        price: (pkg.price || pkg.amount || 0).toString(),
        points: pkg.points || 0,
        unit: pkg.description?.includes('年') ? '/年' : pkg.description?.includes('季') ? '/季' : '/月',
        tag: pkg?.status === 1 ? '热门' : '推荐',
        color: pkg?.id === 1 ? '#3b82f6' : pkg?.id === 2 ? '#6366f1' : '#a855f7',
        gradient: 'linear-gradient(135deg, #60a5fa, #3b82f6)'
      }))

      if (memberPlans.value.length > 0) {
        selectedMemberPlan.value = memberPlans.value[0].packageId
      }
    }
  } catch (error) {
    console.error('获取套餐失败:', error)
    ElMessage.error('获取套餐列表失败，请稍后重试')
  }
}

onMounted(() => {
  fetchPackages()
})

const currentSelectedMemberObj = computed(() => {
  const found = memberPlans.value.find(p => p.packageId === selectedMemberPlan.value)
  return found || memberPlans.value[0] || { packageId: 0, price: '0', points: 0, title: '' }
})

const currentSelectedPointsObj = computed(() => {
  const found = pointsPurchasePlans.value.find(p => p.packageId === selectedPointsPlan.value)
  return found || pointsPurchasePlans.value[0] || { packageId: 0, price: '0', points: 0, title: '' }
})

const inviteBenefits = [
  { text: '简历定制及优化 12 次', icon: Reading, color: '#3b82f6' },
  { text: '创建 12 条成效路径', icon: Promotion, color: '#6366f1' },
  { text: '深度搜索 Chat 50 次', icon: Search, color: '#0ea5e9' },
  { text: '分析 16 个目标职位', icon: Setting, color: '#8b5cf6' }
]


const pointRecords = computed(() => {
  if ((props.records as any[]).length) return props.records as any[]
  return [
    { id: 1, type: '每日积分', remain: 0, total: 100, expireText: '今日积分已领取' },
    { id: 2, type: '邀请奖励', remain: 0, total: 0, expireText: '暂无邀请奖励' }
  ]
})


const currentMemberText = computed(() => {
  const map: Record<string, string> = {
    normal: '基础会员',
    monthly: '月度会员',
    quarterly: '季度会员',
    quarter: '季度会员',
    yearly: '年度会员',
    annual: '年度会员'
  }
  return map[memberType.value] || '基础会员'
})

const expiryText = computed(() => (userStore.userInfo as any)?.memberExpireAt || '每日 100 积分 (3 天试用)')

const openPurchaseCenter = (tab: 'points' | 'member') => {
  activePurchaseTab.value = tab
  purchaseCenterVisible.value = true
}

const handlePay = async () => {
  const pkg = activePurchaseTab.value === 'points' ? currentSelectedPointsObj.value : currentSelectedMemberObj.value

  if (!pkg.packageId || pkg.packageId === 'invite') {
    if (pkg.packageId === 'invite') handleInvite()
    return
  }

  try {
    const payload: PointsMembershipChangeDTO = {
      packageId: Number(pkg.packageId) || 0,
      name: pkg.title,
      amount: Number(pkg.price),
      points: pkg.points || 0,
      payType: currentPayMethod.value === 'wechat' ? 1 : 2, // 1:微信, 2:支付宝
    }

    // 处理会员等级：如果是会员购买，根据套餐类型设置等级
    if (activePurchaseTab.value === 'member') {
      const pid = String(pkg.packageId).toLowerCase()
      if (pid.includes('monthly') || pkg.packageId === 1) payload.membershipLevel = 1
      else if (pid.includes('quarterly') || pkg.packageId === 2) payload.membershipLevel = 2
      else if (pid.includes('yearly') || pkg.packageId === 3) payload.membershipLevel = 3
      else payload.membershipLevel = 1 // 默认
    }

    if (!userStore.userInfo?.id) {
      ElMessage.error('未获取到用户信息，请重新登录')
      return
    }

    const res = await rechargePointsService(payload)
    if (res.data.code === 200) {
      ElMessage.success('下单成功')
      console.log('下单成功', res.data.data)
      const orderNo = res.data.data;
      // 加上 /api 前缀，让跳转请求被 vite.config.ts 拦截并代理到后端
      window.location.href = `/api/alipay/pay/${orderNo}`;
      purchaseCenterVisible.value = false
    } else {
      ElMessage.error(res.data.msg || '提交支付失败')
    }
  } catch (err: any) {
    ElMessage.error(err.message || '网络或服务器错误，支付请求失败')
  }
}

const handleInvite = () => {
  if (props.inviteCode) {
    const inviteLink = `${window.location.origin}/register?inviteCode=${props.inviteCode}`
    navigator.clipboard.writeText(inviteLink).then(() => {
      ElMessage.success("邀请链接已复制到剪贴板！")
    }).catch(() => {
      ElMessage.error("复制失败，请重试")
    })
  } else {
    ElMessage.warning("您尚未注册为邀请大使，请先完成注册")
    emit('open-invite')
    purchaseCenterVisible.value = false
  }
}

// 组件卸载时清理定时器
onUnmounted(() => {
  clearTimers()
})

</script>

<template>
  <section class="member-panel">
    <!-- 主视图头部 -->
    <div class="panel-header">
      <!-- <el-icon class="back-icon">
        <Back />
      </el-icon> -->
      <h2 class="panel-title">会员积分</h2>
      <!-- <el-icon class="more-icon">
        <MoreFilled />
      </el-icon> -->
    </div>

    <!-- 基础会员卡片 -->
    <div class="member-status-card">
      <div class="ms-left">
        <div class="ms-icon"><el-icon>
            <Medal />
          </el-icon></div>
        <div class="ms-info">
          <h3>{{ currentMemberText }}</h3>
          <p>{{ expiryText }}</p>
        </div>
      </div>
      <button class="ms-btn" @click="openPurchaseCenter('member')">
        <el-icon>
          <TrendCharts />
        </el-icon>
      </button>
    </div>

    <!-- 总可用积分卡片 -->
    <div class="total-points-card">
      <div class="tp-content">
        <h4>总可用积分</h4>
        <div class="tp-value">{{ displayPoints }}</div>
        <div class="tp-desc">邀请好友，免费领会员权益</div>
      </div>
      <button class="tp-btn" @click="openPurchaseCenter('points')">
        <el-icon>
          <ShoppingCart />
        </el-icon> 获取
      </button>
    </div>

    <!-- 积分明细容器 -->
    <div class="points-records-container">
      <div class="pr-header">
        <h3>积分明细</h3>
        <div class="pr-links">
          <span>服务价格</span>
          <span>消费记录</span>
        </div>
      </div>

      <div class="record-list">
        <div v-for="item in pointRecords" :key="item.id" class="record-item">
          <div class="ri-top">
            <div class="ri-title">
              <el-icon :class="item.type === '每日积分' ? 'icon-calendar' : 'icon-invite'">
                <Calendar v-if="item.type === '每日积分'" />
                <Share v-else />
              </el-icon>
              {{ item.type }}
            </div>
          </div>
          <div class="ri-progress">
            <div class="progress-bg">
              <div class="progress-fill" :style="{
                width: (item.remain / item.total * 100) + '%',
                backgroundColor: item.type === '每日积分' ? '#3b82f6' : '#10b981'
              }">
              </div>
            </div>
          </div>
          <div class="ri-bottom">
            <span class="ri-remain">剩余: {{ item.remain }}</span>
            <span class="ri-total">总计: {{ item.total }}</span>
          </div>
          <div class="ri-expire" v-if="item.expireText">{{ item.expireText }}</div>
        </div>
      </div>
    </div>

    <!-- 支付状态弹窗 -->
    <el-dialog v-model="payDialogVisible" :show-close="false" width="420px" class="pay-status-dialog" :close-on-click-modal="false"
      append-to-body>
      <div class="pay-status-content">
        <!-- 支付中状态 -->
        <template v-if="payStatus === 'pending'">
          <div class="pay-status-icon loading">
            <el-icon class="is-loading"><Loading /></el-icon>
          </div>
          <h3 class="pay-status-title">等待支付完成</h3>
          <p class="pay-status-desc">
            请在支付宝页面完成支付<br>
            剩余时间：{{ Math.floor(payCountdown / 60) }}:{{ String(payCountdown % 60).padStart(2, '0') }}
          </p>
          <div class="pay-status-order" v-if="currentOrderId">
            订单号：{{ currentOrderId }}
          </div>
          <div class="pay-status-actions">
            <el-button @click="cancelPayment">取消支付</el-button>
            <el-button type="primary" @click="retryPayment">重新打开支付宝</el-button>
          </div>
        </template>

        <!-- 支付成功状态 -->
        <template v-if="payStatus === 'paid'">
          <div class="pay-status-icon success">
            <el-icon><CircleCheckFilled /></el-icon>
          </div>
          <h3 class="pay-status-title">支付成功！</h3>
          <p class="pay-status-desc">
            {{ activePurchaseTab === 'points' ? '积分已充值到您的账户' : '会员权益已生效' }}
          </p>
          <div class="pay-status-success-detail" v-if="currentPlan">
            <div class="success-item">
              <span class="label">{{ activePurchaseTab === 'points' ? '充值积分' : '会员类型' }}</span>
              <span class="value">
                {{ activePurchaseTab === 'points'
                  ? (currentPlan as PointsPlan).points + ' 积分'
                  : (currentPlan as MemberPlan).title
                }}
              </span>
            </div>
            <div class="success-item">
              <span class="label">支付金额</span>
              <span class="value price">¥{{ currentPlan.price }}</span>
            </div>
          </div>
        </template>

        <!-- 支付失败/取消状态 -->
        <template v-if="payStatus === 'cancelled' || payStatus === 'expired'">
          <div class="pay-status-icon error">
            <el-icon><CircleCloseFilled /></el-icon>
          </div>
          <h3 class="pay-status-title">{{ payStatus === 'expired' ? '支付超时' : '支付未成功' }}</h3>
          <p class="pay-status-desc">
            {{ payStatus === 'expired' ? '支付已超时，请重新下单' : '支付已取消，您可以重新下单' }}
          </p>
          <div class="pay-status-order" v-if="currentOrderId">
            订单号：{{ currentOrderId }}
          </div>
          <div class="pay-status-actions">
            <el-button @click="payDialogVisible = false">关闭</el-button>
            <el-button type="primary" @click="retryPayment" :disabled="payStatus === 'expired'">
              {{ payStatus === 'expired' ? '重新下单' : '重新支付' }}
            </el-button>
          </div>
        </template>
      </div>
    </el-dialog>

    <!-- 统一购买中心弹窗 -->
    <el-dialog v-model="purchaseCenterVisible" :show-close="false" width="700px" class="purchase-dialog"
      :destroy-on-close="true" append-to-body>
      <template #header="{ close }">
        <div class="dialog-custom-header">
          <el-icon class="back-icon" @click="close">
            <Back />
          </el-icon>
          <span class="dialog-title">会员积分</span>
          <el-icon class="close-icon" @click="close">
            <Close />
          </el-icon>
        </div>
      </template>

      <div class="purchase-center-container">
        <!-- Tab 切换 -->
        <div class="tab-switcher">
          <div class="tab-item" :class="{ active: activePurchaseTab === 'points' }"
            @click="activePurchaseTab = 'points'">
            <el-icon>
              <Coin />
            </el-icon> 积分购买
          </div>
          <div class="tab-item" :class="{ active: activePurchaseTab === 'member' }"
            @click="activePurchaseTab = 'member'">
            <el-icon>
              <Medal />
            </el-icon> 订阅会员
          </div>
        </div>

        <div class="banner" :class="{ 'member-banner': activePurchaseTab === 'member' }">
          <el-icon>
            <TrendCharts />
          </el-icon> 投资未来的自己，加速成长的曲线
        </div>

        <!-- =============== 积分购买 Tab =============== -->
        <div v-if="activePurchaseTab === 'points'" class="points-purchase-view">
          <div class="purchase-cards">
            <div v-for="plan in pointsPurchasePlans" :key="plan.key" class="p-card"
              :class="{ 'active': selectedPointsPlan === plan.packageId || selectedPointsPlan === plan.key }"
              @click="selectedPointsPlan = plan.packageId || plan.key" :style="{ '--theme-color': plan.color }">
              <div class="p-card-tag" :style="{ backgroundColor: plan.color }">{{ plan.tag }}</div>
              <div class="p-card-points">{{ plan.points }} 积分</div>
              <div class="p-card-price">
                <template v-if="plan.price === '0.00'">
                  <span class="currency">¥</span><span class="amount">0</span><span class="decimals">.00</span>
                </template>
                <template v-else>
                  <span class="currency">¥</span>
                  <span class="amount">{{ String(plan.price).split('.')[0] }}</span>
                  <span class="decimals">.{{ String(plan.price).split('.')[1] || '00' }}</span>
                </template>
              </div>
            </div>
          </div>

          <div v-if="selectedPointsPlan === 'invite'" class="invite-panel">
            <h4 class="invite-title">邀请好友得积分</h4>
            <div class="invite-benefits">
              <div class="ib-item" v-for="(bene, index) in inviteBenefits" :key="index">
                <el-icon class="ib-icon" :style="{ color: bene.color }">
                  <component :is="bene.icon" />
                </el-icon>
                {{ bene.text }}
              </div>
            </div>
            <div class="invite-footer">
              <el-icon>
                <InfoFilled />
              </el-icon> 邀请好友免费获得积分
            </div>
            <button class="primary-btn invite-btn" @click="handleInvite">
              <el-icon>
                <Share />
              </el-icon> 立即邀请好友领积分
            </button>
          </div>

          <div v-else class="payment-section">
            <div class="order-summary-card" :style="{ backgroundColor: currentSelectedPointsObj.color + '10' }">
              <div class="os-header">订单摘要</div>
              <div class="os-body">
                <div class="os-item">
                  <span class="os-label">充值内容:</span>
                  <span class="os-value highlight" :style="{ color: currentSelectedPointsObj.color }">
                    {{ currentSelectedPointsObj.points }} 积分
                  </span>
                </div>
                <div class="os-item">
                  <span class="os-label">应付金额:</span>
                  <span class="os-value price">¥{{ currentSelectedPointsObj.price }}</span>
                </div>
              </div>
            </div>
            <div class="pay-method">
              <div class="alipay" v-if="currentPayMethod === 'alipay'">
                <img :src="alipayIcon" class="method-img-icon" alt="Alipay" /> 支付宝支付
              </div>
              <div class="wechat" v-else>
                <img :src="wechatIcon" class="method-img-icon" alt="WeChat" /> 微信支付
              </div>
              <div class="more-methods" @click="payMethodVisible = true">
                更多支付方式 <el-icon>
                  <ArrowRight />
                </el-icon>
              </div>
            </div>
            <button class="primary-btn subscribe-btn" @click="handlePay"
              :style="{ backgroundColor: currentSelectedPointsObj.color }">
              <el-icon>
                <ShoppingCart />
              </el-icon>
              确认支付并充值 {{ currentSelectedPointsObj.points }} 积分
            </button>
          </div>
        </div>

        <!-- =============== 订阅会员 Tab =============== -->
        <div v-else class="member-subscribe-view">
          <div class="purchase-cards member-cards">
            <div v-for="plan in memberPlans" :key="plan.packageId" class="m-card"
              :class="{ 'active': selectedMemberPlan === plan.packageId }" @click="selectedMemberPlan = plan.packageId"
              :style="{ '--theme-color': plan.color }">
              <div class="m-card-tag" :style="{ backgroundColor: plan.color }">{{ plan.tag }}</div>
              <div class="m-card-duration">{{ plan.title }}</div>
              <div class="m-card-months"
                :style="{ color: selectedMemberPlan === plan.packageId ? plan.color : '#1e293b' }">
                {{ plan.duration }}
              </div>
              <div class="m-card-price">
                <span class="currency">¥</span>
                <span class="amount">{{ plan.price }}</span>
                <span class="unit">{{ plan.unit }}</span>
              </div>
              <div class="m-card-daily">包含 {{ plan.points }} 积分</div>
            </div>
          </div>

          <div class="member-summary">
            <el-icon>
              <Coin />
            </el-icon> 总计包含 {{ currentSelectedMemberObj.points }} 积分 (购买后一次性发放)
          </div>

          <div class="payment-section">
            <div class="order-summary-card" :style="{ backgroundColor: currentSelectedMemberObj.color + '10' }">
              <div class="os-header">会员订阅摘要</div>
              <div class="os-body">
                <div class="os-item">
                  <span class="os-label">开通档位:</span>
                  <span class="os-value highlight" :style="{ color: currentSelectedMemberObj.color }">
                    {{ currentSelectedMemberObj.title }}
                  </span>
                </div>
                <div class="os-item">
                  <span class="os-label">应付金额:</span>
                  <span class="os-value price">¥{{ currentSelectedMemberObj.price }}</span>
                </div>
              </div>
            </div>
            <div class="pay-method">
              <div class="alipay" v-if="currentPayMethod === 'alipay'">
                <img :src="alipayIcon" class="method-img-icon" alt="Alipay" /> 支付宝支付
              </div>
              <div class="wechat" v-else>
                <img :src="wechatIcon" class="method-img-icon" alt="WeChat" /> 微信支付
              </div>
              <div class="more-methods" @click="payMethodVisible = true">
                更多支付方式 <el-icon>
                  <ArrowRight />
                </el-icon>
              </div>
            </div>
            <button class="primary-btn subscribe-btn" @click="handlePay"
              :style="{ backgroundColor: currentSelectedMemberObj.color }">
              <el-icon>
                <Medal />
              </el-icon>
              确认并支付 ¥{{ currentSelectedMemberObj.price }}
            </button>
          </div>
        </div>
      </div>
    </el-dialog>

  </section>
</template>

<style scoped lang="scss">
.member-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  font-family: 'Inter', system-ui, sans-serif;
  background: #f8fafc;
  border-radius: 24px;
  min-height: 100%;
}

.panel-header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 24px;
  color: #0f172a;
}

.back-icon,
.more-icon {
  font-size: 20px;
  cursor: pointer;
  color: #1e293b;
  transition: all 0.2s;
}

.back-icon:hover {
  color: #3b82f6;
}

.panel-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.member-status-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.05);
  border: 1px solid #bfdbfe;
}

.ms-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ms-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.ms-info h3 {
  margin: 0 0 6px 0;
  font-size: 18px;
  color: #1e3a8a;
  font-weight: 800;
}

.ms-info p {
  margin: 0;
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.ms-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transition: transform 0.2s;
}

.ms-btn:hover {
  transform: scale(1.05);
}

.total-points-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, #14b8a6, #0284c7);
  color: #fff;
  box-shadow: 0 8px 24px rgba(2, 132, 199, 0.2);
}

.tp-content h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 500;
  opacity: 0.9;
}

.tp-value {
  font-size: 56px;
  font-weight: 900;
  line-height: 1;
  margin-bottom: 16px;
  letter-spacing: -2px;
}

.tp-desc {
  font-size: 13px;
  opacity: 0.9;
}

.tp-btn {
  padding: 10px 24px;
  border-radius: 20px;
  border: none;
  background: #fff;
  color: #0284c7;
  font-weight: 700;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tp-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.pr-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin: 20px 0 16px;
}

.pr-header h3 {
  margin: 0;
  font-size: 16px;
  color: #1e293b;
  font-weight: 700;
}

.pr-links {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
}

.pr-links span:hover {
  color: #3b82f6;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.record-item {
  background: #fff;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.ri-top {
  display: flex;
  margin-bottom: 20px;
}

.ri-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.icon-calendar {
  color: #3b82f6;
  font-size: 20px;
}

.icon-invite {
  color: #10b981;
  font-size: 20px;
}

.ri-progress {
  margin-bottom: 12px;
}

.progress-bg {
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.ri-bottom {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.ri-expire {
  margin-top: 12px;
  font-size: 12px;
  color: #94a3b8;
  font-style: italic;
}

/* Modal styles based on screenshots 2 and 3 */
::v-deep(.purchase-dialog) {
  border-radius: 20px;
  overflow: hidden;
}

::v-deep(.purchase-dialog .el-dialog__header) {
  display: none;
}

::v-deep(.purchase-dialog .el-dialog__body) {
  padding: 0;
  background: #f8fafc;
}

.dialog-custom-header {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
}

.dialog-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.close-icon,
.back-icon {
  font-size: 20px;
  color: #64748b;
  cursor: pointer;
  transition: color 0.2s;
}

.close-icon:hover {
  color: #ef4444;
}

.tab-switcher {
  display: flex;
  margin: 0 24px 20px;
  background: #fff;
  border-radius: 12px;
  padding: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  border-radius: 8px;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.tab-item.active {
  background: linear-gradient(to right, #eff6ff, #ffffff);
  color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.banner {
  margin: 0 24px 24px;
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  color: #fff;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.banner.member-banner {
  background: linear-gradient(135deg, #818cf8, #4f46e5);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
}

.purchase-cards {
  display: flex;
  gap: 16px;
  padding: 0 24px;
  margin-bottom: 24px;
}

.p-card,
.m-card {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  padding: 24px 16px;
  text-align: center;
  border: 2px solid #f1f5f9;
  cursor: pointer;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.p-card:hover,
.m-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.p-card.active,
.m-card.active {
  border-color: var(--theme-color, #3b82f6);
  border-width: 2.5px;
  background: #fff;
  transform: translateY(-6px) scale(1.03);
  box-shadow:
    0 12px 40px -8px rgba(var(--theme-color-rgb, 59, 130, 246), 0.25),
    0 8px 16px -4px rgba(59, 130, 246, 0.15);
  z-index: 10;
}

/* 选中时的对勾形状 (CSS绘制) */
.p-card.active::before,
.m-card.active::before {
  content: '';
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  background: var(--theme-color, #3b82f6);
  border-radius: 50%;
  z-index: 3;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.p-card.active::after,
.m-card.active::after {
  content: '✓';
  position: absolute;
  top: 9px;
  right: 12px;
  color: #fff;
  font-size: 14px;
  font-weight: 900;
  z-index: 4;
}

.p-card-tag,
.m-card-tag {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 4px 14px;
  border-radius: 12px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.p-card-points {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
  margin: 16px 0 12px;
}

.p-card-price,
.m-card-price {
  color: #94a3b8;
  display: flex;
  justify-content: center;
  align-items: baseline;
  min-height: 38px;
}

.p-card.active .p-card-price,
.m-card.active .m-card-price {
  color: var(--theme-color, #3b82f6);
}

.currency {
  font-size: 14px;
  font-weight: 600;
  margin-right: 2px;
}

.amount {
  font-size: 32px;
  font-weight: 900;
  line-height: 1;
}

.decimals,
.unit {
  font-size: 14px;
  font-weight: 600;
  margin-left: 2px;
}

.m-card-duration {
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
  margin-top: 12px;
}

.m-card-months {
  font-size: 24px;
  font-weight: 900;
  color: #1e293b;
  margin: 8px 0 16px;
  transition: color 0.3s;
}

.m-card-daily {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 16px;
}

.invite-panel {
  background: #fff;
  margin: 0 24px 24px;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.invite-title {
  margin: 0 0 20px;
  font-size: 16px;
  font-weight: 800;
  color: #1e293b;
}

.invite-benefits {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.ib-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #475569;
  font-weight: 500;
}

.ib-icon {
  font-size: 18px;
  background: #f1f5f9;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.invite-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 20px;
}

.primary-btn {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  border: none;
  background: #3b82f6;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.member-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 24px 16px;
  font-size: 14px;
  color: #4f46e5;
  font-weight: 600;
}

.payment-section {
  background: #fff;
  margin: 0 24px 24px;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.order-summary-card {
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px dashed rgba(0, 0, 0, 0.1);
}

.os-header {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  margin-bottom: 12px;
}

.os-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.os-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.os-label {
  font-size: 14px;
  color: #475569;
}

.os-value {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
}

.os-value.highlight {
  font-size: 18px;
}

.os-value.price {
  font-size: 20px;
  color: #ef4444;
}

.pay-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 20px;
}

.pay-method {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.alipay {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.alipay-icon {
  width: 28px;
  height: 28px;
  background: #1677ff;
  color: #fff;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.more-methods {
  font-size: 13px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-weight: 500;
}

.more-methods:hover {
  color: #3b82f6;
}

.subscribe-btn {
  background: #4f46e5;
}

.method-img-icon {
  width: 28px;
  height: 28px;
  object-fit: contain;
  margin-right: 8px;
  border-radius: 4px;
}
</style>
