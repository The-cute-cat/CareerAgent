<template>
  <section class="guide-banner guide-banner--learning">
    <div class="guide-banner-main">
      <p class="guide-banner-kicker">Learning Mode</p>
      <h3>当前以学习成长为主</h3>
      <p class="guide-banner-desc">
        你可以先围绕方向探索、能力补齐和发展规划来完善画像。现有的简历解析、岗位匹配和报告功能仍然可继续使用，只是页面会优先给出学习导向的提示。
      </p>
    </div>

    <div class="guide-banner-tags">
      <span>方向探索</span>
      <span>能力提升</span>
      <span>发展规划</span>
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
  border: 1px solid rgba(125, 211, 252, 0.45);
}

.guide-banner--learning {
  background: linear-gradient(135deg, #ecfeff 0%, #f8fafc 100%);
}

.guide-banner-main h3 {
  margin: 0 0 8px;
  color: #164e63;
  font-size: 18px;
}

.guide-banner-kicker {
  margin: 0 0 6px;
  color: #0891b2;
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
  background: rgba(8, 145, 178, 0.08);
  color: #0f766e;
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
