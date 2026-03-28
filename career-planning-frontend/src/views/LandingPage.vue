<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  ArrowRight,
  Compass,
  DataAnalysis,
  DocumentChecked,
  Histogram,
  Opportunity,
  Promotion,
  Switch,
  TrendCharts,
  User,
  Reading,
  Warning,
  Checked,
  Flag,
  List,
  CircleCheck,
  Briefcase
} from '@element-plus/icons-vue'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}

const scrollToSection = (id: string) => {
  const el = document.querySelector(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const navItems = [
  { label: '开启规划', path: '#career' },
  { label: '核心能力', path: '#features' },
  { label: '职业路径', path: '#path' },
  { label: '常见问题', path: '#faq' },
  { label: '关于我们', path: '#about' },
]

const highlights = [
  'AI能力画像分析',
  '真实岗位画像构建',
  '精准人岗匹配',
  '职业路径规划报告'
]

const stats = [
  { value: '10000+', label: '岗位数据支撑' },
  { value: '100+', label: '岗位类型覆盖' },
  { value: '4维', label: '人岗匹配分析' },
  { value: '3阶段', label: '成长行动计划' },
]

const steps = [
  {
    num: '01',
    icon: User,
    title: '自我认知分析',
    desc: '支持简历上传或手动录入，智能拆解技能、证书、项目经历、沟通能力与发展潜力，形成专属就业能力画像。'
  },
  {
    num: '02',
    icon: DataAnalysis,
    title: '岗位智能匹配',
    desc: '基于岗位画像与学生画像进行多维度对比，从基础要求、职业技能、职业素养、发展潜力四个维度给出匹配分析。'
  },
  {
    num: '03',
    icon: Flag,
    title: '职业路径规划',
    desc: '自动生成职业探索报告、目标岗位建议、成长路线与短中期行动计划，让规划真正可执行、可落地。'
  }
]

const features = [
  {
    icon: Briefcase,
    title: '岗位画像构建',
    desc: '提炼专业技能、证书要求、学习能力、抗压能力、沟通能力等关键要求，形成岗位画像。'
  },
  {
    icon: Histogram,
    title: '能力画像分析',
    desc: '对学生就业能力进行完整度与竞争力评估，帮助学生清晰认识自身优势与短板。'
  },
  {
    icon: Switch,
    title: '人岗匹配引擎',
    desc: '通过多维评分模型识别契合项与差距项，让匹配结果更可解释、更具指导意义。'
  },
  {
    icon: Promotion,
    title: '职业路径图谱',
    desc: '支持岗位晋升路径和转岗路径展示，帮助学生看清不同职业方向的发展可能。'
  }
]

const pains = [
  {
    icon: Warning,
    title: '自我认知模糊',
    desc: '不知道自己适合什么方向，能力优势不清晰。',
    solution: '通过AI能力画像，快速识别你的优势与短板。'
  },
  {
    icon: Reading,
    title: '职业信息碎片化',
    desc: '对行业、岗位和能力要求的理解停留在零散信息。',
    solution: '系统解析岗位数据，建立更完整的职业认知。'
  },
  {
    icon: Compass,
    title: '缺少清晰路径',
    desc: '知道想找工作，却不知道从哪一步开始准备。',
    solution: '生成职业路径图谱和阶段化行动计划。'
  },
  {
    icon: Opportunity,
    title: '规划难落地',
    desc: '建议很多，但真正能执行的内容很少。',
    solution: '输出可执行的学习、实践、求职准备方案。'
  }
]

const reportItems = [
  '职业探索与岗位匹配分析',
  '目标岗位能力差距识别',
  '岗位晋升路径与转岗建议',
  '短期 / 中期行动计划',
  '报告润色、检查与导出'
]

const faqs = [
  {
    q: '职引未来适合哪些人使用？',
    a: '面向在校大学生、应届毕业生以及处于职业探索期的青年群体，尤其适合对自我定位、岗位选择和成长路径还不够清晰的用户。'
  },
  {
    q: '系统如何生成职业规划建议？',
    a: '系统会先构建学生能力画像，再结合岗位画像进行多维匹配，最后生成带有目标岗位建议、路径图谱和行动计划的职业规划报告。'
  },
  {
    q: '除了匹配岗位，还能提供什么帮助？',
    a: '还可以提供能力差距分析、学习路径建议、项目/实习建议、阶段性成长任务与职业报告导出等功能。'
  }
]
</script>

<template>
  <div class="landing-page">
    <nav class="landing-nav">
      <div class="nav-container">
        <div class="nav-logo" @click="scrollToSection('#career')">
          <div class="logo-icon">
            <img src="@/assets/1234.png" alt="Logo" class="logo-img" />
          </div>
          <span class="logo-text">职引未来</span>
        </div>
        <div class="nav-links">
          <a v-for="item in navItems" :key="item.label" :href="item.path" class="nav-link">
            {{ item.label }}
          </a>
        </div>
      </div>
    </nav>

    <section id="career" class="hero-section">
      <div class="hero-bg"></div>
      <div class="hero-grid">
        <div class="hero-content">
          <div class="hero-tag">基于 AI 的大学生职业规划智能体</div>
          <h1 class="hero-title">让每一位大学生都拥有清晰的职业方向</h1>
          <p class="hero-subtitle">
            围绕自我认知、岗位认知、人岗匹配与职业路径规划，打造更懂大学生的智能职业发展助手。
          </p>

          <div class="hero-highlights">
            <span v-for="item in highlights" :key="item" class="highlight-pill">{{ item }}</span>
          </div>

          <div class="hero-actions">
            <button class="hero-btn-primary" @click="goToLogin">
              <el-icon><ArrowRight /></el-icon>
              开始职业规划
            </button>
            <button class="hero-btn-secondary" @click="scrollToSection('#features')">
              查看核心能力
            </button>
          </div>
        </div>

        <div class="hero-panel">
          <div class="hero-card main-card">
            <div class="panel-title">AI职业规划报告</div>
            <div class="panel-score-row">
              <div>
                <div class="panel-label">目标岗位</div>
                <div class="panel-value">产品经理 / 数据分析</div>
              </div>
              <div class="score-box">
                <span>匹配度</span>
                <strong>87%</strong>
              </div>
            </div>
            <div class="panel-progress-list">
              <div class="progress-item">
                <span>专业技能</span>
                <div class="progress-bar"><div style="width: 86%"></div></div>
              </div>
              <div class="progress-item">
                <span>通用素养</span>
                <div class="progress-bar"><div style="width: 82%"></div></div>
              </div>
              <div class="progress-item">
                <span>实践经历</span>
                <div class="progress-bar"><div style="width: 74%"></div></div>
              </div>
            </div>
          </div>

          <div class="hero-mini-grid">
            <div class="hero-card mini-card">
              <div class="mini-title">成长建议</div>
              <p>补强数据分析项目经历，优先积累真实业务实践。</p>
            </div>
            <div class="hero-card mini-card">
              <div class="mini-title">路径推荐</div>
              <p>运营助理 → 产品专员 → 产品经理</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="stats-section">
      <div class="container stats-grid">
        <div v-for="item in stats" :key="item.label" class="stat-card">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </div>
    </section>

    <section class="steps-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">三步构建你的专属职业发展路径</h2>
          <p class="section-subtitle">从自我认知到精准匹配，再到职业路径规划，全流程 AI 驱动</p>
        </div>
        <div class="steps-grid">
          <div v-for="(step, index) in steps" :key="index" class="step-card">
            <div class="step-num-badge">{{ step.num }}</div>
            <div class="step-icon-wrapper">
              <el-icon :size="30">
                <component :is="step.icon" />
              </el-icon>
            </div>
            <h3 class="card-title">{{ step.title }}</h3>
            <p class="card-desc">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section id="features" class="features-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">核心能力</h2>
          <p class="section-subtitle">围绕赛题要求构建完整的 AI 职业规划闭环</p>
        </div>
        <div class="features-grid">
          <div v-for="item in features" :key="item.title" class="feature-card">
            <div class="feature-icon">
              <el-icon :size="28">
                <component :is="item.icon" />
              </el-icon>
            </div>
            <h3 class="card-title">{{ item.title }}</h3>
            <p class="card-desc">{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="pain-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">我们在解决什么问题？</h2>
          <p class="section-subtitle">聚焦大学生职业规划中最常见、最真实的核心痛点</p>
        </div>
        <div class="pain-grid">
          <div v-for="item in pains" :key="item.title" class="pain-card">
            <div class="pain-head">
              <div class="pain-icon">
                <el-icon :size="24">
                  <component :is="item.icon" />
                </el-icon>
              </div>
              <h3>{{ item.title }}</h3>
            </div>
            <p class="pain-desc">{{ item.desc }}</p>
            <div class="pain-solution">
              <el-icon><Checked /></el-icon>
              <span>{{ item.solution }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="path" class="path-section">
      <div class="container path-grid">
        <div class="path-content">
          <div class="section-header left">
            <h2 class="section-title">职业路径图谱 + 成长行动计划</h2>
            <p class="section-subtitle">不仅告诉你适合什么，更告诉你下一步该做什么</p>
          </div>
          <div class="path-list">
            <div v-for="item in reportItems" :key="item" class="path-list-item">
              <el-icon><CircleCheck /></el-icon>
              <span>{{ item }}</span>
            </div>
          </div>
        </div>
        <div class="path-card">
          <div class="path-card-title">示例发展路径</div>
          <div class="timeline">
            <div class="timeline-item">
              <span class="dot"></span>
              <div>
                <strong>短期目标</strong>
                <p>完成岗位能力补齐，积累项目与实习经历</p>
              </div>
            </div>
            <div class="timeline-item">
              <span class="dot"></span>
              <div>
                <strong>中期目标</strong>
                <p>进入目标岗位，持续强化业务理解与实战能力</p>
              </div>
            </div>
            <div class="timeline-item">
              <span class="dot"></span>
              <div>
                <strong>长期方向</strong>
                <p>形成职业专长，明确晋升路径或转岗机会</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="faq" class="faq-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">常见问题</h2>
          <p class="section-subtitle">你关心的问题，这里先帮你回答</p>
        </div>
        <div class="faq-list">
          <div v-for="item in faqs" :key="item.q" class="faq-item">
            <h3>{{ item.q }}</h3>
            <p>{{ item.a }}</p>
          </div>
        </div>
      </div>
    </section>

    <section id="about" class="cta-section">
      <div class="container cta-card">
        <div>
          <h2>现在开始，让职业规划从“迷茫”走向“清晰”</h2>
          <p>职引未来，用 AI 帮大学生看见方向、看清差距、看懂路径。</p>
        </div>
        <button class="hero-btn-primary" @click="goToLogin">
          <el-icon><ArrowRight /></el-icon>
          立即体验
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: #f7f9fc;
  color: #1f2a37;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.landing-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 72px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  height: 100%;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.logo-icon {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.logo-text {
  font-size: 22px;
  font-weight: 800;
  color: #1677ff;
  letter-spacing: 0.5px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
}

.nav-link {
  font-size: 14px;
  color: #4b5563;
  text-decoration: none;
  transition: color 0.25s ease;
}

.nav-link:hover {
  color: #1677ff;
}

.hero-section {
  position: relative;
  padding: 126px 24px 60px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 20%, rgba(22, 119, 255, 0.16), transparent 28%),
    radial-gradient(circle at 85% 25%, rgba(64, 150, 255, 0.14), transparent 22%),
    linear-gradient(135deg, #f2f7ff 0%, #eef5ff 45%, #f9fbff 100%);
}

.hero-grid {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 40px;
  align-items: center;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(22, 119, 255, 0.1);
  color: #1677ff;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 18px;
}

.hero-title {
  font-size: 54px;
  line-height: 1.18;
  font-weight: 800;
  color: #101828;
  margin: 0 0 18px;
  letter-spacing: -1.5px;
}

.hero-subtitle {
  font-size: 18px;
  line-height: 1.8;
  color: #5b6472;
  margin: 0 0 24px;
  max-width: 680px;
}

.hero-highlights {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 30px;
}

.highlight-pill {
  display: inline-flex;
  align-items: center;
  height: 38px;
  padding: 0 16px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid #e6eefc;
  color: #334155;
  font-size: 14px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.hero-btn-primary,
.hero-btn-secondary {
  height: 50px;
  padding: 0 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.hero-btn-primary {
  border: none;
  color: #fff;
  background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
  box-shadow: 0 12px 28px rgba(22, 119, 255, 0.28);
}

.hero-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 32px rgba(22, 119, 255, 0.36);
}

.hero-btn-secondary {
  border: 1px solid #d6e4ff;
  background: rgba(255, 255, 255, 0.88);
  color: #1677ff;
}

.hero-btn-secondary:hover {
  background: #fff;
  transform: translateY(-2px);
}

.hero-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero-card {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(22, 119, 255, 0.08);
  border-radius: 20px;
  box-shadow: 0 18px 50px rgba(31, 41, 55, 0.08);
}

.main-card {
  padding: 26px;
}

.panel-title,
.path-card-title,
.mini-title {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
}

.panel-score-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 18px 0 22px;
}

.panel-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}

.panel-value {
  font-size: 22px;
  font-weight: 800;
  color: #111827;
}

.score-box {
  min-width: 110px;
  padding: 14px 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
  color: #fff;
  text-align: center;
}

.score-box span {
  display: block;
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.score-box strong {
  font-size: 28px;
  line-height: 1;
}

.panel-progress-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: #475467;
}

.progress-bar {
  height: 10px;
  border-radius: 999px;
  background: #edf2ff;
  overflow: hidden;
}

.progress-bar > div {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
}

.hero-mini-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.mini-card {
  padding: 20px;
}

.mini-card p {
  margin: 10px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: #5b6472;
}

.stats-section {
  padding: 8px 0 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

.stat-card {
  background: #fff;
  border: 1px solid #eef2f7;
  border-radius: 18px;
  padding: 26px 18px;
  text-align: center;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.04);
}

.stat-value {
  font-size: 30px;
  font-weight: 800;
  color: #1677ff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #667085;
}

.steps-section,
.features-section,
.pain-section,
.path-section,
.faq-section,
.cta-section {
  padding: 88px 0;
}

.features-section,
.faq-section {
  background: #ffffff;
}

.section-header {
  text-align: center;
  margin-bottom: 52px;
}

.section-header.left {
  text-align: left;
  margin-bottom: 28px;
}

.section-title {
  font-size: 36px;
  line-height: 1.25;
  font-weight: 800;
  color: #101828;
  margin: 0 0 14px;
}

.section-subtitle {
  font-size: 16px;
  color: #667085;
  margin: 0;
  line-height: 1.8;
}

.steps-grid,
.features-grid,
.pain-grid,
.faq-list {
  display: grid;
  gap: 24px;
}

.steps-grid,
.features-grid,
.pain-grid {
  grid-template-columns: repeat(3, 1fr);
}

.faq-list {
  grid-template-columns: 1fr;
}

.step-card,
.feature-card,
.pain-card,
.faq-item,
.path-card {
  background: #fff;
  border: 1px solid #edf2f7;
  border-radius: 22px;
  box-shadow: 0 12px 36px rgba(15, 23, 42, 0.05);
}

.step-card,
.feature-card,
.pain-card,
.faq-item {
  padding: 32px 26px;
}

.step-card {
  position: relative;
  transition: all 0.25s ease;
}

.step-card:hover,
.feature-card:hover,
.pain-card:hover,
.faq-item:hover,
.path-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.step-num-badge {
  position: absolute;
  top: -14px;
  left: 24px;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 24px rgba(22, 119, 255, 0.25);
}

.step-icon-wrapper,
.feature-icon,
.pain-icon {
  width: 62px;
  height: 62px;
  border-radius: 18px;
  background: linear-gradient(135deg, #eff6ff 0%, #e6f0ff 100%);
  color: #1677ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-icon-wrapper {
  margin-top: 12px;
}

.feature-icon,
.pain-icon {
  margin-bottom: 18px;
}

.card-title {
  font-size: 20px;
  font-weight: 800;
  color: #111827;
  margin: 18px 0 12px;
}

.card-desc,
.pain-desc,
.faq-item p,
.path-list-item,
.timeline-item p {
  font-size: 15px;
  line-height: 1.8;
  color: #667085;
  margin: 0;
}

.pain-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.pain-head h3,
.faq-item h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #111827;
}

.pain-solution,
.path-list-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pain-solution {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 14px;
  background: #f5faff;
  color: #1677ff;
  font-size: 14px;
  line-height: 1.7;
}

.path-grid {
  display: grid;
  grid-template-columns: 1fr 0.95fr;
  gap: 28px;
  align-items: stretch;
}

.path-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.path-card {
  padding: 28px;
}

.timeline {
  margin-top: 22px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.timeline-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.timeline-item strong {
  display: block;
  font-size: 16px;
  color: #111827;
  margin-bottom: 6px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #1677ff;
  margin-top: 8px;
  box-shadow: 0 0 0 6px rgba(22, 119, 255, 0.12);
  flex-shrink: 0;
}

.faq-item h3 {
  margin-bottom: 10px;
}

.cta-card {
  background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
  border-radius: 28px;
  padding: 40px 36px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  box-shadow: 0 22px 54px rgba(22, 119, 255, 0.28);
}

.cta-card h2 {
  font-size: 32px;
  line-height: 1.3;
  margin: 0 0 10px;
}

.cta-card p {
  margin: 0;
  font-size: 16px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
}

.cta-card .hero-btn-primary {
  background: #fff;
  color: #1677ff;
  box-shadow: none;
}

@media (max-width: 1080px) {
  .hero-grid,
  .path-grid,
  .steps-grid,
  .features-grid,
  .pain-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .hero-title {
    font-size: 42px;
  }
}

@media (max-width: 768px) {
  .landing-nav {
    height: 64px;
  }

  .nav-links {
    display: none;
  }

  .hero-section {
    padding-top: 104px;
  }

  .hero-grid {
    padding: 0 16px;
  }

  .container {
    padding: 0 16px;
  }

  .hero-title {
    font-size: 34px;
    letter-spacing: -0.8px;
  }

  .section-title,
  .cta-card h2 {
    font-size: 28px;
  }

  .hero-mini-grid {
    grid-template-columns: 1fr;
  }

  .cta-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
