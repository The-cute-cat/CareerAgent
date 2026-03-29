<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar, Coin, Opportunity, Present, WarningFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/modules/user'

const props = defineProps({
  points: {
    type: Number,
    default: 0
  },
  records: {
    type: Array,
    default: () => []
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
  '积分消耗享受专属折扣',
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
          {{ currentMemberPlan ? `当前享受积分消耗${currentMemberPlan.discount}` : '普通用户按原价消耗积分' }}
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
            <li>功能消耗享受 {{ plan.discount }}</li>
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
            <p>展示当前可用积分来源，便于你判断优先使用哪一类积分。</p>
          </div>
        </div>
        <div class="record-list">
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
              <li>积分消耗 {{ plan.discount }}</li>
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
.member-panel { display: flex; flex-direction: column; gap: 24px; }
.panel-tabs, .overview-grid, .plan-grid, .method-grid, .rule-grid, .overview-actions, .insufficient-actions { display: flex; gap: 16px; }
.panel-tabs { gap: 12px; }
.panel-tab, .ghost-btn, .primary-btn, .text-btn { border: none; cursor: pointer; transition: all .2s ease; }
.panel-tab { padding: 10px 18px; border-radius: 999px; background: #eef4ff; color: #5f7896; font-weight: 700; }
.panel-tab.active, .ghost-btn, .primary-btn { color: #fff; background: linear-gradient(135deg, #2f7df6, #5cc7de); }
.overview-grid, .plan-grid, .method-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.overview-grid { grid-template-columns: 1.15fr 1fr; }
.overview-card, .benefit-panel, .rules-panel, .records-panel { border: 1px solid rgba(210, 225, 244, .9); border-radius: 28px; background: rgba(255,255,255,.82); box-shadow: 0 16px 36px rgba(19, 56, 94, .06); }
.overview-card { padding: 28px; }
.overview-card--member { background: linear-gradient(135deg, rgba(240,246,255,.95), rgba(255,255,255,.92)); }
.overview-card--points { padding: 28px; color: #fff; background: linear-gradient(135deg, #2f7df6, #59c5dc); }
.overview-label, .overview-desc, .section-head p, .method-card p, .record-desc, .record-side span, .dialog-intro p, .rule-card span { color: #70839b; }
.overview-card--points .overview-label, .overview-card--points .overview-desc { color: rgba(255,255,255,.88); }
.overview-value { margin: 10px 0 8px; font-size: 48px; line-height: 1; font-weight: 800; color: #183b61; }
.overview-card--points .overview-value { color: #fff; }
.ghost-btn { align-self: flex-start; padding: 10px 18px; border-radius: 999px; }
.ghost-btn--light { background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.28); }
.content-stack { display: flex; flex-direction: column; gap: 24px; }
.section-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.section-head h3 { margin: 0 0 6px; font-size: 18px; color: #173a5d; }
.section-head p, .method-card p, .dialog-intro p { margin: 0; line-height: 1.7; }
.text-btn { padding: 0; color: #2f7df6; background: transparent; font-weight: 700; }
.plan-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.plan-card, .method-card, .rule-card, .record-item, .benefit-item { border-radius: 24px; border: 1px solid rgba(214, 228, 244, .92); background: rgba(255,255,255,.9); }
.plan-card { padding: 24px; }
.plan-card.is-monthly { box-shadow: inset 0 0 0 1px rgba(47,125,246,.12); }
.plan-card.is-quarterly { box-shadow: inset 0 0 0 1px rgba(123,97,255,.16); }
.plan-card.is-yearly { box-shadow: inset 0 0 0 1px rgba(228,177,42,.2); }
.plan-top, .plan-title-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.plan-title-row h4, .method-card h4, .record-title, .insufficient-box h4 { margin: 0; color: #173a5d; }
.plan-price { font-size: 30px; font-weight: 800; color: #1f6feb; }
.plan-tag { padding: 4px 10px; border-radius: 999px; background: rgba(47,125,246,.1); color: #2f7df6; font-size: 12px; font-weight: 700; }
.plan-meta { margin: 18px 0 20px; padding-left: 18px; color: #60738b; line-height: 1.9; }
.primary-btn { width: 100%; padding: 12px 18px; border-radius: 16px; font-weight: 700; }
.benefit-panel, .rules-panel, .records-panel { padding: 24px; }
.benefit-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.benefit-item, .rule-card, .record-item, .method-card { padding: 18px 20px; }
.benefit-item { display: flex; align-items: center; gap: 12px; color: #274766; }
.benefit-item .el-icon, .warning-icon { color: #2f7df6; }
.method-card { display: flex; flex-direction: column; gap: 10px; }
.method-points { font-size: 24px; font-weight: 800; color: #1f6feb; }
.rule-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.rule-card { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.rule-card strong, .record-side strong { color: #1f6feb; font-size: 16px; }
.record-list { display: flex; flex-direction: column; gap: 14px; }
.record-item { display: flex; align-items: center; gap: 16px; }
.record-icon { width: 52px; height: 52px; display: flex; align-items: center; justify-content: center; border-radius: 18px; background: #edf4ff; color: #2f7df6; font-size: 24px; }
.record-main { flex: 1; min-width: 0; }
.record-side { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; text-align: right; }
.dialog-stack, .dialog-method-grid, .insufficient-box { display: flex; flex-direction: column; gap: 18px; }
.plan-grid--dialog, .dialog-method-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.insufficient-box { align-items: center; text-align: center; padding: 12px 0; }
.warning-icon { font-size: 42px; }
.insufficient-box p { margin: 0; color: #70839b; line-height: 1.8; }

@media (max-width: 1200px) {
  .overview-grid, .plan-grid, .method-grid, .rule-grid, .benefit-list, .plan-grid--dialog, .dialog-method-grid { grid-template-columns: 1fr; }
}
</style>
