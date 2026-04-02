<script setup>
import { ref, computed } from 'vue'
import { Calendar as CalendarIcon, ArrowLeft, ArrowRight, Timer } from '@element-plus/icons-vue'

const props = defineProps({
  interviews: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select-date'])

const calendarValue = ref(new Date())

// 获取指定日期是否有面试
const getInterviewsForDate = (dayString) => {
  return props.interviews.filter(item => {
    // 假设 item.time 是 'YYYY-MM-DD HH:mm'
    return item.time.startsWith(dayString)
  })
}

const handleDateClick = (data) => {
  emit('select-date', data.day)
}

const selectDate = (type) => {
  const date = new Date(calendarValue.value)
  if (type === 'prev-month') date.setMonth(date.getMonth() - 1)
  else date.setMonth(date.getMonth() + 1)
  calendarValue.value = date
}
</script>

<template>
  <div class="calendar-view-container">
    <el-calendar v-model="calendarValue" class="custom-calendar">
      <template #header="{ date }">
        <div class="calendar-mini-header">
          <el-icon class="nav-btn" @click="selectDate('prev-month')"><ArrowLeft /></el-icon>
          <div class="current-info">
            <span class="year-month">{{ date }}</span>
            <span class="today-tip">今天 4月1日</span>
          </div>
          <el-icon class="nav-btn" @click="selectDate('next-month')"><ArrowRight /></el-icon>
        </div>
      </template>

      <template #date-cell="{ data }">
        <div class="calendar-cell" :class="{ 'is-selected': data.isSelected }" @click="handleDateClick(data)">
          <div class="day-number">{{ data.day.split('-').slice(2).join('') }}</div>
          
          <!-- 日程打点区 -->
          <div class="dots-area">
            <template v-if="getInterviewsForDate(data.day).length > 0">
              <el-tooltip
                placement="top"
                :content="`${getInterviewsForDate(data.day).length} 场面试安排`"
                effect="light"
              >
                <div class="interview-dot-indicator">
                  <div class="pulse-dot"></div>
                  <span class="dot-count" v-if="getInterviewsForDate(data.day).length > 1">
                    {{ getInterviewsForDate(data.day).length }}
                  </span>
                </div>
              </el-tooltip>
            </template>
          </div>
        </div>
      </template>
    </el-calendar>

    <!-- Legend -->
    <div class="calendar-legend">
      <div class="legend-item">
        <span class="dot blue"></span>
        <span class="text">有面试安排</span>
      </div>
      <div class="legend-item">
        <span class="dot today"></span>
        <span class="text">今日</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.calendar-view-container {
  background: #ffffff;
  padding: 16px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03);
}

.calendar-mini-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0 8px 16px;

  .nav-btn {
    font-size: 14px;
    color: #94a3b8;
    cursor: pointer;
    transition: color 0.2s;
    &:hover { color: #3b82f6; }
  }

  .current-info {
    text-align: center;
    .year-month {
      display: block;
      font-size: 16px;
      font-weight: 800;
      color: #1e293b;
    }
    .today-tip {
      font-size: 11px;
      color: #94a3b8;
      font-weight: 500;
    }
  }
}

.custom-calendar {
  --el-calendar-border: none;
  --el-calendar-cell-width: 1fr;
  
  :deep(.el-calendar-table) {
    thead th {
      color: #94a3b8;
      font-weight: 600;
      font-size: 13px;
      padding-bottom: 12px;
    }
    
    td {
      border: none;
      &.is-today {
        .day-number { background: #1e62c5; color: #fff; border-radius: 8px; }
      }
    }

    .el-calendar-day {
      padding: 0;
      height: 42px;
      transition: all 0.2s;

      &:hover {
        background: #f1f5f9;
        border-radius: 8px;
      }
    }
  }
}

.calendar-cell {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  margin: 1px;
  border-radius: 8px;

  &.is-selected {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
    .day-number { color: #ffffff !important; }
  }
}

.day-number {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dots-area {
  position: absolute;
  bottom: 2px;
}

.pulse-dot {
  width: 4px;
  height: 4px;
  background: #cbd5e1;
  border-radius: 50%;
  
  &.has-interview {
    background: #4f46e5;
  }
}

.is-selected .pulse-dot {
  background: #ffffff !important;
}

.calendar-legend {
  display: none;
}

@media (max-width: 576px) {
  .calendar-view-container { padding: 12px; }
  .custom-calendar :deep(.el-calendar-day) { height: 60px; }
}
</style>
