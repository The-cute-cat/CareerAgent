<script setup>
import { Calendar, Coin, TrendCharts } from '@element-plus/icons-vue'

defineProps({
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
        <el-button type="primary" round size="small" plain>
          <el-icon><TrendCharts /></el-icon>
          升级
        </el-button>
      </div>

      <div class="points-overview-card">
        <div class="points-label">可用积分</div>
        <div class="points-number">{{ points }}</div>
        <div class="points-meta">
          <span class="points-trend">+100 今日</span>
          <el-button type="primary" round size="small">获取积分</el-button>
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
      <div
        v-for="item in records"
        :key="item.id"
        class="record-item"
      >
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

@media (max-width: 992px) {
  .overview-grid {
    grid-template-columns: 1fr;
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
}
</style>
