<template>
  <section class="guide-banner guide-banner--job">
    <div class="guide-banner-main">
      <p class="guide-banner-kicker">Job Mode</p>
      <h3>当前以找工作推进为主</h3>
      <p class="guide-banner-desc">
        建议优先完善简历信息、目标岗位和项目经历，继续使用当前的人岗匹配、差距分析和报告导出流程。页面会更强调求职准备相关内容，但原有功能不做变更。
      </p>
    </div>

    <div class="guide-banner-tags">
      <span>简历优化</span>
      <span>岗位匹配</span>
      <span>求职准备</span>
    </div>
  </section>
</template>

<style scoped>
.guide-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 20px;
  border-radius: 18px;
  border: 1px solid rgba(191, 219, 254, 0.6);
}

.guide-banner--job {
  background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
}

.guide-banner-main h3 {
  margin: 0 0 8px;
  color: #1d4ed8;
  font-size: 18px;
}

.guide-banner-kicker {
  margin: 0 0 6px;
  color: #2563eb;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.guide-banner-desc {
  margin: 0;
  color: #4b5563;
  line-height: 1.75;
  font-size: 13px;
}

.guide-banner-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.guide-banner-tags span {
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .guide-banner {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
