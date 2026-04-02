<script setup>
import { Plus, Search, Filter, Reading, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  reviews: {
    type: Array,
    default: () => [
      { id: 101, title: '面试复盘：阿里巴巴 Java 后端面试总结', company: '阿里巴巴', role: 'Java 专家', date: '2026-03-29', tags: ['技术面', 'P7'] },
      { id: 102, title: '面试复盘：字节跳动 前端开发面试记录', company: '字节跳动', role: '前端开发', date: '2026-03-15', tags: ['技术面', 'HR面'] },
      { id: 103, title: '面试复盘：腾讯 全栈开发复盘', company: '腾讯', role: '全栈开发', date: '2026-03-10', tags: ['业务面'] }
    ]
  }
})

const tags = ['技术面', 'HR面', '群面', '业务面']
</script>

<template>
  <div class="interview-review-section">
    <div class="section-header">
      <h3>面试复盘笔记</h3>
      <div class="header-actions">
        <div class="tag-filter">
          <span v-for="t in tags" :key="t" class="h-tag">{{ t }}</span>
        </div>
        <el-button type="primary" :icon="Plus" plain size="small">新建复盘笔记</el-button>
      </div>
    </div>

    <div class="review-grid">
      <div v-for="review in reviews" :key="review.id" class="review-item">
        <div class="review-left">
          <div class="icon-box"><el-icon><Reading /></el-icon></div>
          <div class="review-info">
            <h4>{{ review.title }}</h4>
            <div class="review-meta">
              <span class="company">{{ review.company }}</span>
              <span class="dot">·</span>
              <span class="role">{{ review.role }}</span>
              <span class="dot">·</span>
              <span class="date">{{ review.date }}</span>
            </div>
          </div>
        </div>
        <el-icon class="arrow"><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- Empty and Quick Entry -->
    <div class="review-footer">
      <div class="template-entry">
        <div class="entry-icon">📝</div>
        <div class="entry-text">
          <h5>使用复盘模板</h5>
          <p>导入技术面/HR面常见问题模板，快速记录面试要点</p>
        </div>
        <el-button type="primary" link :icon="ArrowRight">立即使用</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.interview-review-section {
  margin-top: 32px;
  background: #ffffff;
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h3 { font-size: 18px; font-weight: 800; color: #0f172a; margin: 0; }
  .header-actions { display: flex; align-items: center; gap: 16px; }
}

.tag-filter {
  display: flex;
  gap: 8px;
  
  .h-tag {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 6px;
    background: #f1f5f9;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover { background: #e2e8f0; color: #1e62c5; }
  }
}

.review-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.review-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    background: #ffffff;
    box-shadow: 0 4px 12px rgba(30, 98, 197, 0.08);
    border-color: #3b82f644;
    transform: translateX(4px);
  }

  .review-left { display: flex; align-items: center; gap: 16px; }
  
  .icon-box {
    width: 40px;
    height: 40px;
    background: #e0eaff;
    color: #3b82f6;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
  }

  h4 { font-size: 15px; font-weight: 700; color: #1e293b; margin: 0 0 4px; }
  .review-meta {
    font-size: 12px;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .arrow { color: #cbd5e1; font-size: 14px; }
}

.review-footer {
  margin-top: 24px;
}

.template-entry {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(90deg, #f0f7ff 0%, #ffffff 100%);
  border: 1px solid #e0eaff;
  border-radius: 16px;

  .entry-icon { font-size: 24px; }
  .entry-text {
    flex: 1;
    h5 { font-size: 14px; font-weight: 700; color: #1e62c5; margin: 0 0 2px; }
    p { font-size: 12px; color: #64748b; margin: 0; }
  }
}

@media (max-width: 576px) {
  .section-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .header-actions { width: 100%; flex-wrap: wrap; justify-content: space-between; }
}
</style>
