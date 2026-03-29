<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Calendar,
  Coin,
  TrendCharts,
  Trophy,
  Opportunity,
  Checked,
  Present,
  ChatDotRound,
  UserFilled,
  Close
} from '@element-plus/icons-vue'

const props = defineProps({
  points: Number,
  records: {
    type: Array,
    default: () => []
  }
})

const iconMap = {
  每日积分: Calendar,
  邀请奖励: Coin
}

const upgradeVisible = ref(false)
const earnPointsVisible = ref(false)
const selectedPlan = ref('advanced')

const membershipPlans = [
  {
    key: 'advanced',
    badge: '热门升级',
    name: '高级会员',
    price: '¥39/月',
    highlight: '每日 300 积分',
    desc: '适合稳定使用职业测评、成长地图和职位匹配能力的用户。',
    perks: ['简历诊断优先体验', '成长任务双倍积分', '专属职业建议周报']
  },
  {
    key: 'pro',
    badge: '成长加速',
    name: '专业会员',
    price: '¥99/季',
    highlight: '每日 600 积分',
    desc: '为高频使用者准备，兼顾积分额度、报告资源和专属服务。',
    perks: ['深度报告生成额度', '优先客服支持', '会员资源库不限次浏览']
  }
]

const pointTasks = [
  {
    title: '完成每日签到',
    reward: '+20',
    status: '今日可领取',
    type: 'primary',
    icon: Calendar,
    desc: '每天登录个人中心签到一次，稳定累计成长积分。'
  },
  {
    title: '邀请好友注册',
    reward: '+200',
    status: '长期有效',
    type: 'success',
    icon: UserFilled,
    desc: '好友通过邀请码注册成功后，双方都可获得奖励。'
  },
  {
    title: '提交反馈建议',
    reward: '+200',
    status: '审核后发放',
    type: 'warning',
    icon: ChatDotRound,
    desc: '提供有价值的产品建议，被采纳后会补充积分到账户。'
  },
  {
    title: '完成成长任务',
    reward: '+80',
    status: '本周剩余 3 次',
    type: 'info',
    icon: Trophy,
    desc: '按阶段完成职业规划任务，可解锁额外积分和资源。'
  }
]

const selectedPlanInfo = computed(() => membershipPlans.find((item) => item.key === selectedPlan.value))

const handleUpgrade = () => {
  ElMessage.success(`已为你选择${selectedPlanInfo.value?.name || '目标套餐'}，后续可接入支付流程`)
  upgradeVisible.value = false
}

const handleTaskAction = (taskTitle) => {
  ElMessage.success(`${taskTitle}入口已准备好，后续可接入真实业务流程`)
}
</script>

<template>
  <div class="member-panel">
    <div class="overview-grid">
      <div class="member-status-card">
        <div class="status-icon-wrap">
          <div class="status-icon">✓</div>
        </div>
        <div class="status-info">
          <div class="status-label">当前会员</div>
          <div class="status-name">基础会员</div>
          <div class="status-desc">每日100积分（3天试用）</div>
        </div>
        <el-button type="primary" round size="small" plain @click="upgradeVisible = true">
          <el-icon><TrendCharts /></el-icon>
          升级
        </el-button>
      </div>

      <div class="points-overview-card">
        <div class="points-label">可用积分</div>
        <div class="points-number">{{ points }}</div>
        <div class="points-meta">
          <span class="points-trend">+100 今日</span>
          <el-button type="primary" round size="small" @click="earnPointsVisible = true">获取积分</el-button>
        </div>
      </div>
    </div>

    <div class="section-header">
      <div class="section-title">积分明细</div>
      <div class="section-actions">
        <span class="action-link">服务价格</span>
        <span class="action-link">消费记录</span>
      </div>
    </div>

    <div class="records-list">
      <div v-for="item in records" :key="item.id" class="record-item">
        <div class="record-icon-wrap">
          <el-icon><component :is="iconMap[item.type] || Calendar" /></el-icon>
        </div>
        <div class="record-info">
          <div class="record-name">{{ item.type }}</div>
          <div class="record-detail">
            <span>剩余 <strong>{{ item.remain }}</strong></span>
            <span class="record-sep">·</span>
            <span>总计 {{ item.total }}</span>
          </div>
        </div>
        <div class="record-right">
          <div class="record-amount">{{ item.remain }}</div>
          <div v-if="item.expireText" class="record-expire">{{ item.expireText }}</div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="upgradeVisible"
      width="880px"
      class="member-dialog"
      align-center
      destroy-on-close
    >
      <div class="dialog-surface upgrade-surface">
        <button type="button" class="dialog-close" @click="upgradeVisible = false">
          <el-icon><Close /></el-icon>
        </button>
        <div class="dialog-hero">
          <div class="hero-copy">
            <div class="hero-badge">会员升级</div>
            <h3>从基础会员升级到更高等级</h3>
            <p>解锁更多每日积分、优先服务和专属成长资源，让职业规划体验更完整。</p>
          </div>
          <div class="hero-side-card">
            <div class="mini-label">当前状态</div>
            <div class="mini-title">基础会员</div>
            <div class="mini-desc">每日 100 积分，试用剩余 3 天</div>
          </div>
        </div>

        <div class="plan-grid">
          <button
            v-for="plan in membershipPlans"
            :key="plan.key"
            type="button"
            class="plan-card"
            :class="{ active: selectedPlan === plan.key }"
            @click="selectedPlan = plan.key"
          >
            <div class="plan-top">
              <span class="plan-badge">{{ plan.badge }}</span>
              <div class="plan-price">{{ plan.price }}</div>
            </div>
            <div class="plan-name">{{ plan.name }}</div>
            <div class="plan-highlight">{{ plan.highlight }}</div>
            <div class="plan-desc">{{ plan.desc }}</div>
            <div class="plan-perks">
              <div v-for="perk in plan.perks" :key="perk" class="perk-item">
                <el-icon><Checked /></el-icon>
                <span>{{ perk }}</span>
              </div>
            </div>
          </button>
        </div>

        <div class="compare-strip">
          <div class="compare-card current">
            <div class="compare-label">当前基础会员</div>
            <div class="compare-value">100 积分 / 天</div>
            <div class="compare-hint">适合轻度体验用户</div>
          </div>
          <div class="compare-arrow">
            <el-icon><Opportunity /></el-icon>
          </div>
          <div class="compare-card target">
            <div class="compare-label">升级后</div>
            <div class="compare-value">{{ selectedPlanInfo?.highlight }}</div>
            <div class="compare-hint">{{ selectedPlanInfo?.name }}专属权益即时生效</div>
          </div>
        </div>

        <div class="dialog-actions">
          <el-button round @click="upgradeVisible = false">稍后再说</el-button>
          <el-button type="primary" round @click="handleUpgrade">
            立即升级 {{ selectedPlanInfo?.name }}
          </el-button>
        </div>
      </div>
    </el-dialog>

    <el-dialog
      v-model="earnPointsVisible"
      width="920px"
      class="member-dialog"
      align-center
      destroy-on-close
    >
      <div class="dialog-surface points-surface">
        <button type="button" class="dialog-close" @click="earnPointsVisible = false">
          <el-icon><Close /></el-icon>
        </button>
        <div class="dialog-hero points-hero">
          <div class="hero-copy">
            <div class="hero-badge points-badge">获取积分</div>
            <h3>通过任务和互动持续积累积分</h3>
            <p>完成签到、邀请和反馈等动作，就能快速补充账户积分，兑换更多成长服务。</p>
          </div>
          <div class="points-balance-card">
            <div class="mini-label">当前可用</div>
            <div class="balance-number">{{ points }}</div>
            <div class="mini-desc">基础会员今日还可领取 20 积分</div>
          </div>
        </div>

        <div class="task-grid">
          <div v-for="task in pointTasks" :key="task.title" class="task-card">
            <div class="task-icon" :class="task.type">
              <el-icon><component :is="task.icon" /></el-icon>
            </div>
            <div class="task-content">
              <div class="task-head">
                <div>
                  <div class="task-title">{{ task.title }}</div>
                  <div class="task-desc">{{ task.desc }}</div>
                </div>
                <div class="task-reward">{{ task.reward }}</div>
              </div>
              <div class="task-footer">
                <span class="task-status">{{ task.status }}</span>
                <el-button round size="small" type="primary" plain @click="handleTaskAction(task.title)">
                  去完成
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <div class="tips-board">
          <div class="tips-title">
            <el-icon><Present /></el-icon>
            <span>积分使用提醒</span>
          </div>
          <div class="tips-list">
            <div class="tip-item">基础会员每日可领取固定积分，未领取部分不会自动累积到次日。</div>
            <div class="tip-item">邀请奖励和反馈奖励到账后，可用于报告权益、会员兑换和活动参与。</div>
            <div class="tip-item">后续如接入真实接口，这里可以直接跳转到签到、邀请、反馈等业务页面。</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.member-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.overview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.member-status-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px;
  border-radius: 20px;
  background: linear-gradient(135deg, #eef5ff 0%, #e0ecff 100%);
  border: 1px solid rgba(191, 219, 254, 0.6);
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(21, 83, 199, 0.1);
  }
}

.status-icon-wrap {
  flex-shrink: 0;
}

.status-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(135deg, #1677ff, #409eff);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.3);
}

.status-info {
  flex: 1;
  min-width: 0;
}

.status-label {
  font-size: 11px;
  font-weight: 700;
  color: #7a9ec9;
  letter-spacing: 0.04em;
}

.status-name {
  margin-top: 4px;
  font-size: 18px;
  font-weight: 800;
  color: #1553c7;
}

.status-desc {
  margin-top: 2px;
  font-size: 12px;
  color: #5d8cc7;
}

.points-overview-card {
  padding: 22px;
  border-radius: 20px;
  background: linear-gradient(135deg, #1677ff 0%, #45b6ff 55%, #67d4c8 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: 0 12px 32px rgba(22, 119, 255, 0.2);
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 40px rgba(22, 119, 255, 0.25);
  }
}

.points-label {
  font-size: 12px;
  font-weight: 600;
  opacity: 0.85;
}

.points-number {
  font-size: 38px;
  font-weight: 800;
  line-height: 1.15;
  margin-top: 4px;
  letter-spacing: -0.02em;
}

.points-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 12px;
}

.points-trend {
  font-size: 12px;
  font-weight: 700;
  opacity: 0.9;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-title {
  font-size: 17px;
  font-weight: 800;
  color: #163253;
}

.section-actions {
  display: flex;
  gap: 16px;
}

.action-link {
  font-size: 13px;
  color: #7a8da3;
  cursor: pointer;
  transition: color 0.2s;

  &:hover {
    color: #1677ff;
  }
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #e8eef6;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03);
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    border-color: #d4e2f5;
  }
}

.record-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, #eef5ff, #f2fbf7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1677ff;
  font-size: 18px;
  flex-shrink: 0;
}

.record-info {
  flex: 1;
  min-width: 0;
}

.record-name {
  font-size: 15px;
  font-weight: 700;
  color: #1f3550;
}

.record-detail {
  margin-top: 4px;
  font-size: 12px;
  color: #7a8da3;
  display: flex;
  align-items: center;
  gap: 6px;

  strong {
    color: #4a6282;
  }
}

.record-sep {
  color: #c5cdd8;
}

.record-right {
  text-align: right;
  flex-shrink: 0;
}

.record-amount {
  font-size: 20px;
  font-weight: 800;
  color: #1677ff;
}

.record-expire {
  margin-top: 4px;
  font-size: 11px;
  color: #9ca3af;
}

:deep(.member-dialog) {
  border-radius: 28px;
  overflow: hidden;
  padding: 0;
}

:deep(.member-dialog .el-dialog__header) {
  display: none;
}

:deep(.member-dialog .el-dialog__body) {
  padding: 0;
}

.dialog-surface {
  position: relative;
  padding: 28px;
  background:
    radial-gradient(circle at top right, rgba(103, 184, 255, 0.16), transparent 24%),
    radial-gradient(circle at left center, rgba(29, 78, 216, 0.08), transparent 22%),
    linear-gradient(180deg, #f8fbff 0%, #f2f7ff 100%);
}

.dialog-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 38px;
  height: 38px;
  border: 1px solid rgba(205, 222, 243, 0.9);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  color: #5e7592;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(22, 52, 92, 0.08);
  transition: all 0.2s ease;

  &:hover {
    color: #1677ff;
    border-color: rgba(22, 119, 255, 0.32);
    transform: translateY(-1px);
  }
}

.dialog-hero {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 22px;
}

.hero-copy h3 {
  margin: 12px 0 8px;
  font-size: 28px;
  line-height: 1.2;
  color: #173a5d;
}

.hero-copy p {
  margin: 0;
  max-width: 540px;
  font-size: 14px;
  line-height: 1.75;
  color: #6f8197;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(22, 119, 255, 0.1);
  color: #1668dc;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.hero-side-card,
.points-balance-card {
  min-width: 240px;
  padding: 20px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(205, 222, 243, 0.9);
  box-shadow: 0 14px 32px rgba(22, 52, 92, 0.08);
}

.mini-label {
  font-size: 12px;
  font-weight: 700;
  color: #89a0bd;
}

.mini-title {
  margin-top: 10px;
  font-size: 24px;
  font-weight: 900;
  color: #1d4ed8;
}

.mini-desc {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: #6f8197;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.plan-card {
  text-align: left;
  padding: 20px;
  border-radius: 24px;
  border: 1px solid #dbe6f4;
  background: rgba(255, 255, 255, 0.88);
  cursor: pointer;
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 32px rgba(15, 23, 42, 0.08);
  }

  &.active {
    border-color: rgba(37, 99, 235, 0.5);
    box-shadow: 0 18px 36px rgba(37, 99, 235, 0.14);
    background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
  }
}

.plan-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.plan-badge {
  display: inline-flex;
  min-height: 26px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.1);
  color: #15803d;
  font-size: 12px;
  font-weight: 800;
}

.plan-price {
  font-size: 18px;
  font-weight: 900;
  color: #1e3a8a;
}

.plan-name {
  margin-top: 16px;
  font-size: 22px;
  font-weight: 900;
  color: #173a5d;
}

.plan-highlight {
  margin-top: 6px;
  font-size: 16px;
  font-weight: 800;
  color: #1677ff;
}

.plan-desc {
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.7;
  color: #6f8197;
}

.plan-perks {
  margin-top: 16px;
  display: grid;
  gap: 10px;
}

.perk-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #31475f;
}

.perk-item .el-icon {
  color: #1677ff;
}

.compare-strip {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 14px;
  margin-top: 20px;
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(219, 230, 244, 0.9);
}

.compare-card {
  padding: 18px;
  border-radius: 18px;
}

.compare-card.current {
  background: linear-gradient(135deg, #f8fafc, #eef2ff);
}

.compare-card.target {
  background: linear-gradient(135deg, #eff6ff, #ecfeff);
}

.compare-label {
  font-size: 12px;
  font-weight: 700;
  color: #89a0bd;
}

.compare-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 900;
  color: #173a5d;
}

.compare-hint {
  margin-top: 6px;
  font-size: 13px;
  color: #6f8197;
}

.compare-arrow {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1677ff, #61b2ff);
  color: #fff;
  box-shadow: 0 10px 18px rgba(22, 119, 255, 0.22);
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.points-hero {
  margin-bottom: 18px;
}

.points-badge {
  background: rgba(34, 197, 94, 0.12);
  color: #15803d;
}

.balance-number {
  margin-top: 10px;
  font-size: 38px;
  line-height: 1;
  font-weight: 900;
  color: #1677ff;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.task-card {
  display: flex;
  gap: 14px;
  padding: 20px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #dde8f5;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.task-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.task-icon.primary {
  background: rgba(37, 99, 235, 0.12);
  color: #2563eb;
}

.task-icon.success {
  background: rgba(34, 197, 94, 0.12);
  color: #16a34a;
}

.task-icon.warning {
  background: rgba(245, 158, 11, 0.14);
  color: #d97706;
}

.task-icon.info {
  background: rgba(14, 165, 233, 0.12);
  color: #0284c7;
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.task-title {
  font-size: 16px;
  font-weight: 800;
  color: #173a5d;
}

.task-desc {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.7;
  color: #6f8197;
}

.task-reward {
  font-size: 28px;
  line-height: 1;
  font-weight: 900;
  color: #1677ff;
  flex-shrink: 0;
}

.task-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 18px;
}

.task-status {
  font-size: 12px;
  color: #89a0bd;
}

.tips-board {
  margin-top: 20px;
  padding: 20px;
  border-radius: 22px;
  background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
  border: 1px solid rgba(167, 213, 255, 0.7);
}

.tips-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 800;
  color: #173a5d;
}

.tips-title .el-icon {
  color: #1677ff;
}

.tips-list {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.tip-item {
  font-size: 13px;
  line-height: 1.75;
  color: #53708f;
}

@media (max-width: 992px) {
  .overview-grid,
  .plan-grid,
  .task-grid,
  .compare-strip {
    grid-template-columns: 1fr;
  }

  .compare-arrow {
    margin: 0 auto;
  }

  .dialog-hero {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .member-status-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .record-item {
    flex-wrap: wrap;
  }

  .section-header,
  .points-meta,
  .task-head,
  .task-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .dialog-surface {
    padding: 18px;
  }

  .hero-copy h3 {
    font-size: 24px;
  }
}
</style>
