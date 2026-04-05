<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Calendar, Opportunity, Back, Close, Coin, Medal, TrendCharts,
  ArrowRight, Share, ShoppingCart, WarningFilled, Promotion, ChatLineRound, Reading, Setting, MoreFilled, Search, InfoFilled
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/modules/user'
import { rechargePointsService, type PointsMembershipChangeDTO } from '@/api/points'
import type { AccountPointsData } from '@/api/points'

const props = defineProps({
  points: { type: Number, default: 0 },
  records: { type: Array, default: () => [] },
  accountPoints: { type: Object as () => AccountPointsData | null, default: null },
  loading: { type: Boolean, default: false }
})

const userStore = useUserStore()

// Purchase Center Dialog
const purchaseCenterVisible = ref(false)
const activePurchaseTab = ref<'points' | 'member'>('points')
const selectedMemberPlan = ref('quarterly')
const selectedPointsPlan = ref('basic')

const memberType = computed(() => String((userStore.userInfo as any)?.memberType || 'normal').toLowerCase())
const displayPoints = computed(() => Number(props.points || (userStore.userInfo as any)?.points || 0))

const memberPlans = [
  {
    key: 'monthly',
    title: '月度会员',
    duration: '1 个月',
    price: '15',
    unit: '/月',
    dailyCost: '相当于每日 0.50 元',
    dailyPoints: 360,
    totalPoints: 10800,
    tag: '尝鲜首选',
    badgeClass: 'is-monthly',
    color: '#3b82f6',
    gradient: 'linear-gradient(135deg, #60a5fa, #3b82f6)'
  },
  {
    key: 'quarterly',
    title: '季度会员',
    duration: '3 个月',
    price: '36',
    unit: '/季',
    dailyCost: '相当于每日 0.40 元',
    dailyPoints: 120, // Strict adherence to user's requirement
    totalPoints: 10800,
    tag: '性价比之选',
    badgeClass: 'is-quarterly',
    color: '#6366f1',
    gradient: 'linear-gradient(135deg, #818cf8, #4f46e5)'
  },
  {
    key: 'yearly',
    title: '年度会员',
    duration: '12 个月',
    price: '128',
    unit: '/年',
    dailyCost: '相当于每日 0.35 元',
    dailyPoints: 360,
    totalPoints: 131400,
    tag: '最大优惠',
    badgeClass: 'is-yearly',
    color: '#a855f7',
    gradient: 'linear-gradient(135deg, #c084fc, #9333ea)'
  }
]

const pointsPurchasePlans = [
  {
    key: 'invite',
    title: '免费获取',
    points: 500, // Explicitly specified by user requirement (好友500积分一个)
    price: '0.00',
    unit: '',
    tag: '免费获取',
    badgeClass: 'is-free',
    color: '#f59e0b',
    gradient: 'linear-gradient(135deg, #fbbf24, #f59e0b)'
  },
  {
    key: 'basic',
    title: '尝鲜首选',
    points: 1000,
    price: '9.90',
    unit: '',
    tag: '尝鲜首选',
    badgeClass: 'is-basic',
    color: '#3b82f6',
    gradient: 'linear-gradient(135deg, #60a5fa, #3b82f6)'
  },
  {
    key: 'value',
    title: '高性价比',
    points: 3000,
    price: '16.60', // Explicitly specified by user requirement (3000积分16.6元)
    unit: '',
    tag: '高性价比',
    badgeClass: 'is-value',
    color: '#8b5cf6',
    gradient: 'linear-gradient(135deg, #a78bfa, #7c3aed)'
  }
]

const currentSelectedMemberObj = computed(() => {
  const found = memberPlans.find(p => p.key === selectedMemberPlan.value)
  return found || memberPlans[1]!
})

const currentSelectedPointsObj = computed(() => {
  const found = pointsPurchasePlans.find(p => p.key === selectedPointsPlan.value)
  return found || pointsPurchasePlans[1]!
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
    { id: 1, type: '每日积分', remain: 0, total: 100, expireText: '今日已领取' },
    { id: 2, type: '邀请奖励', remain: 17, total: 200, expireText: '距离到期还有 19 天' }
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
  if (activePurchaseTab.value === 'points') {
    try {
      const payload: PointsMembershipChangeDTO = {
        userId: Number(userStore.userInfo?.id),
        amount: currentSelectedPointsObj.value.points,
        type: 1 // 1:充值
      }
      if (!payload.userId) {
        ElMessage.error('未获取到用户信息')
        return
      }

      // 临时显示loading效果可以通过封装或其他方式，这里先简单调用
      const res = await rechargePointsService(payload)
      if (res.data.code === 200) {
        ElMessage.success('充值成功')
        purchaseCenterVisible.value = false
        // TODO: 可在此处触发父组件刷新积分余额的事件
      } else {
        ElMessage.error(res.data.msg || '充值失败')
      }
    } catch (err: any) {
      ElMessage.error(err.message || '网络或服务器错误，充值请求失败')
    }
  } else {
    // 处理会员购买逻辑
    ElMessage.success(`支付请求已提交（会员）`)
  }
}

const handleInvite = () => {
  ElMessage.success("邀请链接已复制到剪贴板！")
}

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
              :class="{ 'active': selectedPointsPlan === plan.key }" @click="selectedPointsPlan = plan.key"
              :style="{ '--theme-color': plan.color }">
              <div class="p-card-tag" :style="{ backgroundColor: plan.color }">{{ plan.tag }}</div>
              <div class="p-card-points">{{ plan.points }} 积分</div>
              <div class="p-card-price">
                <template v-if="plan.price === '0.00'">
                  <span class="currency">¥</span><span class="amount">0</span><span class="decimals">.00</span>
                </template>
                <template v-else>
                  <span class="currency">¥</span>
                  <span class="amount">{{ plan.price.split('.')[0] }}</span>
                  <span class="decimals">.{{ plan.price.split('.')[1] || '00' }}</span>
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
            <button class="primary-btn invite-btn" @click="handleInvite">邀请好友</button>
          </div>

          <div v-else class="payment-section">
            <div class="pay-info">
              <el-icon>
                <WarningFilled />
              </el-icon> 您已选择：{{ currentSelectedPointsObj.title }}（¥ {{ currentSelectedPointsObj.price }}）
            </div>
            <div class="pay-method">
              <div class="alipay">
                <span class="alipay-icon">支</span> 支付宝支付
              </div>
              <div class="more-methods">
                更多支付方式 <el-icon>
                  <ArrowRight />
                </el-icon>
              </div>
            </div>
            <button class="primary-btn subscribe-btn" @click="handlePay"
              :style="{ backgroundColor: currentSelectedPointsObj.color }">
              立即充值
            </button>
          </div>
        </div>

        <!-- =============== 订阅会员 Tab =============== -->
        <div v-else class="member-subscribe-view">
          <div class="purchase-cards member-cards">
            <div v-for="plan in memberPlans" :key="plan.key" class="m-card"
              :class="{ 'active': selectedMemberPlan === plan.key }" @click="selectedMemberPlan = plan.key"
              :style="{ '--theme-color': plan.color }">
              <div class="m-card-tag" :style="{ backgroundColor: plan.color }">{{ plan.tag }}</div>
              <div class="m-card-duration">{{ plan.title }}</div>
              <div class="m-card-months" :style="{ color: selectedMemberPlan === plan.key ? plan.color : '#1e293b' }">
                {{ plan.duration }}
              </div>
              <div class="m-card-price">
                <span class="currency">¥</span>
                <span class="amount">{{ plan.price }}</span>
                <span class="unit">{{ plan.unit }}</span>
              </div>
              <div class="m-card-daily">{{ plan.dailyCost }}</div>
            </div>
          </div>

          <div class="member-summary">
            <el-icon>
              <Coin />
            </el-icon> 每日 {{ currentSelectedMemberObj.dailyPoints }} 积分，总计 {{ currentSelectedMemberObj.totalPoints }} 积分
          </div>

          <div class="payment-section">
            <div class="pay-info">
              <el-icon>
                <WarningFilled />
              </el-icon> 您已选择：{{ currentSelectedMemberObj.title }}（¥ {{ currentSelectedMemberObj.price }} {{
                currentSelectedMemberObj.unit }}）
            </div>
            <div class="pay-method">
              <div class="alipay">
                <span class="alipay-icon">支</span> 支付宝支付
              </div>
              <div class="more-methods">
                更多支付方式 <el-icon>
                  <ArrowRight />
                </el-icon>
              </div>
            </div>
            <button class="primary-btn subscribe-btn" @click="handlePay"
              :style="{ backgroundColor: currentSelectedMemberObj.color }">
              立即订阅
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
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
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
  background: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
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
</style>
