<script setup>
import { Calendar, Location, ArrowRight, Edit, Delete, View } from '@element-plus/icons-vue'

const props = defineProps({
  interview: {
    type: Object,
    required: true,
    default: () => ({
      id: 1,
      company: '蚂蚁集团',
      role: 'Java后端工程师',
      time: '2026-04-05 14:00',
      location: '线上面试 (Zoom)',
      type: '技术复面',
      status: 'ongoing', // ongoing, pending, passed, failed
      logo: 'https://img.alicdn.com/tfs/TB1_uT8n6ihY1JjSZFwXXcj3FXa-115-115.png'
    })
  }
})

const statusMap = {
  pending: { text: '待面试', color: 'blue' },
  ongoing: { text: '进行中', color: 'orange' },
  passed: { text: '已通过', color: 'green' },
  failed: { text: '未通过', color: 'gray' }
}

const statusInfo = statusMap[props.interview.status] || statusMap.pending
</script>

<template>
  <div class="interview-card" :class="statusInfo.color">
    <div class="card-left">
      <div class="company-logo">
        <img :src="interview.logo" :alt="interview.company" v-if="interview.logo" />
        <div v-else class="logo-placeholder">{{ interview.company.charAt(0) }}</div>
      </div>
      <div class="role-info">
        <h3>{{ interview.role }}</h3>
        <p class="company-name text-blue">{{ interview.company }}</p>
      </div>
    </div>

    <div class="card-center">
      <div class="info-row">
        <el-icon><Calendar /></el-icon>
        <span>{{ interview.time }}</span>
      </div>
      <div class="info-row">
        <el-icon><Location /></el-icon>
        <span>{{ interview.location }}</span>
      </div>
      <div class="info-row">
        <span class="type-tag">{{ interview.type }}</span>
      </div>
    </div>

    <div class="card-right">
      <span class="status-badge" :class="statusInfo.color">{{ statusInfo.text }}</span>
      <div class="actions">
        <el-tooltip content="编辑" placement="top"><el-icon class="action-icon"><Edit /></el-icon></el-tooltip>
        <el-tooltip content="查看详情" placement="top"><el-icon class="action-icon"><View /></el-icon></el-tooltip>
        <el-tooltip content="删除" placement="top"><el-icon class="action-icon danger"><Delete /></el-icon></el-tooltip>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.interview-card {
  background: #ffffff;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid #edf2f7;
  display: flex;
  align-items: center;
  gap: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 16px;
  
  &:hover {
    transform: translateX(6px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.05);
    border-color: #3b82f644;
  }

  &.blue { border-left: 6px solid #3b82f6; }
  &.orange { border-left: 6px solid #f97316; }
  &.green { border-left: 6px solid #10b981; }
  &.gray { border-left: 6px solid #94a3b8; }
}

.card-left {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 240px;
}

.company-logo {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;

  img { width: 100%; height: 100%; object-fit: contain; }
  .logo-placeholder { font-size: 24px; font-weight: 800; color: #3b82f6; }
}

.role-info {
  min-width: 0;
  h3 { font-size: 16px; font-weight: 700; color: #0f172a; margin: 0 0 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .company-name { font-size: 14px; font-weight: 600; color: #3b82f6; }
}

.card-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;

  .info-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #64748b;
    
    .el-icon { color: #94a3b8; font-size: 16px; }
  }

  .type-tag {
    background: #f1f5f9;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
  }
}

.card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  
  &.blue { background: #eff6ff; color: #3b82f6; }
  &.orange { background: #fff7ed; color: #f97316; }
  &.green { background: #f0fdf4; color: #10b981; }
  &.gray { background: #f8fafc; color: #94a3b8; }
}

.actions {
  display: flex;
  gap: 12px;
  
  .action-icon {
    font-size: 18px;
    color: #94a3b8;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover { color: #3b82f6; transform: scale(1.15); }
    &.danger:hover { color: #ef4444; }
  }
}

@media (max-width: 768px) {
  .interview-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .card-left, .card-center, .card-right {
    width: 100%;
    min-width: 0;
    align-items: flex-start;
  }
  .card-right {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding-top: 12px;
    border-top: 1px solid #f1f5f9;
  }
}
</style>
