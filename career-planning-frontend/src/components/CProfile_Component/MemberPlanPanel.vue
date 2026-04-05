<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar, Opportunity, WarningFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/modules/user'
import type { AccountPointsData } from '@/api/points'

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
  upgradeVisible.value = true
  ElMessage.success(`已为你打开${memberPlans.find((item) => item.key === planKey)?.title || '会员'}开通面板`)
}

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

@media (max-width: 1200px) {
  .overview-grid, .plan-grid, .method-grid, .rule-grid, .benefit-list, .plan-grid--dialog, .dialog-method-grid, .summary-grid { grid-template-columns: 1fr; }
}
</style>
