<script setup>
import { ArrowRight, Plus, Calendar, Timer, Memo, Download } from '@element-plus/icons-vue'

const props = defineProps({
  todayCount: { type: Number, default: 2 },
  ongoingCount: { type: Number, default: 3 },
  reviewedCount: { type: Number, default: 12 },
  nextMeeting: { type: String, default: '14:00 互联网后端面试' }
})

const emit = defineEmits(['action'])

const stats = [
  { label: '今日面试', value: props.todayCount, unit: '场', detail: props.nextMeeting, color: 'blue' },
  { label: '进行中', value: props.ongoingCount, unit: '个', detail: '待面试 / 面试中状态', color: 'orange' },
  { label: '已复盘', value: props.reviewedCount, unit: '次', detail: '累计复盘次数', color: 'green' }
]

const actions = [
  { label: '预约面试', icon: Plus, type: 'primary' },
  { label: '添加复盘', icon: Plus, type: 'success' },
  { label: '导入记录', icon: Download, type: 'info' }
]
</script>

<template>
  <div class="interview-overview">
    <!-- Stat Cards -->
    <div class="stat-grid">
      <div v-for="item in stats" :key="item.label" class="stat-card" :class="item.color">
        <div class="stat-header">
          <span class="stat-label">{{ item.label }}</span>
          <span class="stat-unit">{{ item.unit }}</span>
        </div>
        <div class="stat-value">{{ item.value }}</div>
        <div class="stat-detail">
          <el-icon v-if="item.color === 'blue'"><Timer /></el-icon>
          {{ item.detail }}
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="action-bar">
      <el-button
        v-for="btn in actions"
        :key="btn.label"
        class="custom-action-btn"
        :type="btn.type"
        @click="emit('action', btn.label)"
      >
        <el-icon><component :is="btn.icon" /></el-icon>
        {{ btn.label }}
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.interview-overview {
  margin-bottom: 32px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  padding: 24px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
  }

  .stat-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
  }

  .stat-label {
    font-size: 14px;
    font-weight: 600;
    color: #64748b;
  }

  .stat-unit {
    font-size: 12px;
    color: #94a3b8;
  }

  .stat-value {
    font-size: 32px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1;
    margin-bottom: 12px;
  }

  .stat-detail {
    font-size: 12px;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &.blue {
    border-left: 4px solid #3b82f6;
    .stat-value { color: #1e62c5; }
  }
  &.orange {
    border-left: 4px solid #f97316;
    .stat-value { color: #c2410c; }
  }
  &.green {
    border-left: 4px solid #10b981;
    .stat-value { color: #047857; }
  }
}

.action-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.custom-action-btn {
  height: 44px;
  padding: 0 24px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

  .el-icon {
    font-size: 18px;
  }
}

@media (max-width: 992px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
  .action-bar {
    justify-content: stretch;
    .custom-action-btn {
      flex: 1;
      justify-content: center;
    }
  }
}
</style>
