<template>
  <div class="job-knowledge-page">
    <section class="hero-panel">
      <div class="hero-copy">
        <div class="hero-kicker">
          <el-icon><Collection /></el-icon>
          岗位知识库
        </div>
        <h1 class="hero-title">按岗位拆解学习路径，把知识点和行动建议串起来</h1>
        <p class="hero-desc">
          围绕典型岗位整理核心能力模块、阶段学习顺序与资源建议，帮助你从“知道要学什么”走到“知道下一步做什么”。
        </p>
        <div class="hero-actions">
          <el-input
            v-model="searchQuery"
            placeholder="搜索岗位、知识点或技能标签"
            clearable
            size="large"
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button size="large" @click="router.push('/development-map')">
            查看发展图谱
          </el-button>
        </div>
      </div>

      <div class="hero-stats">
        <article class="hero-stat-card">
          <span class="stat-label">覆盖岗位</span>
          <strong>{{ filteredRoles.length }}</strong>
          <small>支持按关键词快速筛选</small>
        </article>
        <article class="hero-stat-card accent">
          <span class="stat-label">知识节点</span>
          <strong>{{ knowledgeStats.total }}</strong>
          <small>含基础、框架、项目与工程化</small>
        </article>
        <article class="hero-stat-card">
          <span class="stat-label">已掌握占比</span>
          <strong>{{ knowledgeStats.progress }}%</strong>
          <small>根据当前模拟学习进度生成</small>
        </article>
      </div>
    </section>

    <section class="workspace">
      <aside class="role-panel card-shell">
        <div class="panel-heading">
          <div>
            <div class="panel-eyebrow">岗位导航</div>
            <h2>选择目标岗位</h2>
          </div>
          <el-tag effect="light" round>{{ filteredRoles.length }} 个结果</el-tag>
        </div>

        <div class="role-filter">
          <el-segmented v-model="activeTrack" :options="trackOptions" block />
        </div>

        <div class="role-list">
          <button
            v-for="role in filteredRoles"
            :key="role.id"
            type="button"
            class="role-item"
            :class="{ active: selectedRole?.id === role.id }"
            @click="selectRole(role.id)"
          >
            <div class="role-item__main">
              <span class="role-name">{{ role.title }}</span>
              <span class="role-level">{{ role.level }}</span>
            </div>
            <div class="role-item__meta">
              <span>{{ role.trackLabel }}</span>
              <span>{{ getNodeCount(role.tree) }} 个节点</span>
            </div>
            <p class="role-item__desc">{{ role.description }}</p>
          </button>
        </div>
      </aside>

      <main class="knowledge-panel">
        <section class="overview-card card-shell">
          <div class="overview-header">
            <div>
              <div class="panel-eyebrow">当前岗位</div>
              <h2>{{ selectedRole?.title }}</h2>
              <p>{{ selectedRole?.description }}</p>
            </div>
            <div class="overview-badges">
              <span class="overview-badge">{{ selectedRole?.level }}</span>
              <span class="overview-badge subtle">{{ selectedRole?.trackLabel }}</span>
            </div>
          </div>

          <div class="overview-metrics">
            <article class="metric-card">
              <span>建议学习周期</span>
              <strong>{{ selectedRole?.cycle }}</strong>
            </article>
            <article class="metric-card">
              <span>优先突破</span>
              <strong>{{ selectedRole?.focus }}</strong>
            </article>
            <article class="metric-card">
              <span>推荐项目方向</span>
              <strong>{{ selectedRole?.projectHint }}</strong>
            </article>
          </div>
        </section>

        <section class="tree-card card-shell">
          <div class="panel-heading">
            <div>
              <div class="panel-eyebrow">知识树</div>
              <h2>分阶段掌握核心模块</h2>
            </div>
            <el-progress
              type="circle"
              :percentage="knowledgeStats.progress"
              :width="74"
              :stroke-width="8"
            />
          </div>

          <div class="tree-wrapper">
            <TreeNode
              v-for="node in selectedRole?.tree ?? []"
              :key="node.id"
              :node="node"
              :active-id="activeKnowledge?.id"
              @select="activeKnowledge = $event"
            />
          </div>
        </section>
      </main>

      <aside class="detail-panel card-shell">
        <div class="panel-heading">
          <div>
            <div class="panel-eyebrow">知识详情</div>
            <h2>{{ activeKnowledge?.label }}</h2>
          </div>
          <span class="detail-status" :class="activeKnowledge?.status">
            {{ activeStatusLabel }}
          </span>
        </div>

        <p class="detail-description">
          {{ activeKnowledge?.description }}
        </p>

        <div class="detail-meta-grid">
          <article class="detail-meta-card">
            <span>难度</span>
            <strong>{{ activeKnowledge?.difficulty }}</strong>
          </article>
          <article class="detail-meta-card">
            <span>预计耗时</span>
            <strong>{{ activeKnowledge?.duration }}</strong>
          </article>
        </div>

        <section class="detail-section">
          <div class="section-title">关键标签</div>
          <div class="tag-list">
            <span v-for="tag in activeKnowledge?.tags ?? []" :key="tag" class="tag-chip">
              {{ tag }}
            </span>
          </div>
        </section>

        <section class="detail-section">
          <div class="section-title">推荐资源</div>
          <ul class="plain-list">
            <li v-for="item in activeKnowledge?.resources ?? []" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section class="detail-section">
          <div class="section-title">阶段里程碑</div>
          <ul class="plain-list">
            <li v-for="item in activeKnowledge?.milestones ?? []" :key="item">{{ item }}</li>
          </ul>
        </section>
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Collection, Search } from '@element-plus/icons-vue'
import TreeNode, { type KnowledgeTreeNode } from '@/components/JobKnowledge/TreeNode.vue'

interface JobKnowledgeRole {
  id: string
  title: string
  level: string
  track: 'frontend' | 'backend' | 'data' | 'ai'
  trackLabel: string
  description: string
  cycle: string
  focus: string
  projectHint: string
  tree: KnowledgeTreeNode[]
}

const router = useRouter()
const searchQuery = ref('')
const activeTrack = ref<'all' | JobKnowledgeRole['track']>('all')

const trackOptions = [
  { label: '全部', value: 'all' },
  { label: '前端', value: 'frontend' },
  { label: '后端', value: 'backend' },
  { label: '数据', value: 'data' },
  { label: 'AI', value: 'ai' },
]

const roles = ref<JobKnowledgeRole[]>([
  {
    id: 'frontend-engineer',
    title: '前端开发工程师',
    level: '初中级',
    track: 'frontend',
    trackLabel: '前端方向',
    description: '围绕页面开发、组件工程化、性能优化与交互体验构建完整前端能力。',
    cycle: '12-16 周',
    focus: 'JavaScript / Vue3 / 工程化',
    projectHint: '中后台系统 + 落地页双项目组合',
    tree: [
      {
        id: 'fe-basic',
        label: '前端基础',
        summary: '打牢语言和浏览器认知',
        description: '先把 HTML、CSS、JavaScript 与浏览器运行机制学扎实，这是后续框架和工程化的底层支撑。',
        difficulty: '基础',
        duration: '3-4 周',
        status: 'completed',
        tags: ['HTML', 'CSS', 'JavaScript', '浏览器'],
        resources: ['MDN 核心文档', 'JavaScript 高级程序设计', '浏览器渲染流程专题'],
        milestones: ['独立完成响应式页面', '理解作用域、原型链与事件循环'],
        children: [
          {
            id: 'fe-html-css',
            label: 'HTML / CSS',
            summary: '结构化页面与响应式布局',
            description: '掌握语义化标签、Flex/Grid、BFC、动画和常见布局方案，做到可还原设计稿。',
            difficulty: '基础',
            duration: '1-2 周',
            status: 'completed',
            tags: ['语义化', 'Flex', 'Grid', '动画'],
            resources: ['CSS Tricks 布局指南', 'MDN HTML/CSS'],
            milestones: ['完成 2 个静态页面还原', '掌握常用布局与适配'],
            children: [],
          },
          {
            id: 'fe-js',
            label: 'JavaScript 核心',
            summary: '语言能力与异步模型',
            description: '重点掌握闭包、this、原型链、Promise、模块化和常见数组对象处理能力。',
            difficulty: '基础',
            duration: '1-2 周',
            status: 'completed',
            tags: ['闭包', 'Promise', '模块化'],
            resources: ['现代 JavaScript 教程', '手写 Promise 练习'],
            milestones: ['能独立解释事件循环', '完成常见 JS 手写题'],
            children: [],
          },
        ],
      },
      {
        id: 'fe-framework',
        label: 'Vue3 与组件开发',
        summary: '掌握主流前端框架开发方式',
        description: '学习 Composition API、状态管理、组件设计和页面协同，具备独立开发业务模块的能力。',
        difficulty: '进阶',
        duration: '4-5 周',
        status: 'current',
        tags: ['Vue3', 'Pinia', '组件设计'],
        resources: ['Vue 官方文档', 'Element Plus 组件库', '组合式函数实战'],
        milestones: ['封装 3 个可复用业务组件', '完成一个完整 CRUD 模块'],
        children: [
          {
            id: 'fe-vue-core',
            label: 'Composition API',
            summary: '响应式和组合式设计',
            description: '理解 ref/reactive、computed、watch、组件通信和组合式函数拆分方式。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'current',
            tags: ['ref', 'computed', 'watch'],
            resources: ['Vue 深入响应式章节', '组合式函数最佳实践'],
            milestones: ['拆分 2 个 composable', '能清晰处理父子与跨组件状态'],
            children: [],
          },
          {
            id: 'fe-engineering',
            label: '工程化与质量',
            summary: '让代码更稳定可维护',
            description: '掌握 Vite、ESLint、Prettier、Git 协作、接口分层与基础测试思路。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['Vite', 'ESLint', 'Git', '测试'],
            resources: ['Vite 官方文档', '团队规范模板', 'Vitest 入门'],
            milestones: ['建立项目目录规范', '补齐至少 3 个关键测试'],
            children: [],
          },
        ],
      },
      {
        id: 'fe-project',
        label: '项目与性能优化',
        summary: '从会写页面走向能交付产品',
        description: '通过项目实战、性能优化和体验细节打磨，把知识点转成可展示成果。',
        difficulty: '进阶',
        duration: '4-6 周',
        status: 'planned',
        tags: ['项目实战', '性能优化', '部署'],
        resources: ['Lighthouse 指标说明', '性能优化案例库', '前端项目复盘模板'],
        milestones: ['上线 1 个完整项目', '完成首屏与交互优化复盘'],
        children: [],
      },
    ],
  },
  {
    id: 'backend-engineer',
    title: '后端开发工程师',
    level: '初中级',
    track: 'backend',
    trackLabel: '后端方向',
    description: '从语言基础、框架、数据库到服务治理，建立稳定的后端交付能力。',
    cycle: '14-18 周',
    focus: 'Java / Spring Boot / 数据库',
    projectHint: '订单系统或用户中心服务',
    tree: [
      {
        id: 'be-java',
        label: 'Java 基础',
        summary: '语言、集合、并发与 IO',
        description: '理解 Java 语言特性、集合框架、异常处理和基础并发，是后端开发的必修课。',
        difficulty: '基础',
        duration: '3-4 周',
        status: 'completed',
        tags: ['Java', '集合', '并发'],
        resources: ['Java 核心技术', '并发编程入门'],
        milestones: ['能写出清晰的面向对象代码', '掌握线程池和常见集合'],
        children: [],
      },
      {
        id: 'be-framework',
        label: 'Spring Boot 实战',
        summary: '快速搭建可用服务',
        description: '围绕接口设计、分层架构、参数校验、异常处理和权限认证构建业务服务。',
        difficulty: '进阶',
        duration: '4-5 周',
        status: 'current',
        tags: ['Spring Boot', 'RESTful', '认证授权'],
        resources: ['Spring 官方文档', '接口设计规范'],
        milestones: ['完成一个带登录鉴权的服务', '输出 API 文档'],
        children: [],
      },
      {
        id: 'be-data',
        label: '数据库与缓存',
        summary: '提升数据层设计能力',
        description: '掌握 MySQL 建模、索引优化、事务和 Redis 使用场景，具备常见性能优化思路。',
        difficulty: '进阶',
        duration: '3-4 周',
        status: 'planned',
        tags: ['MySQL', 'Redis', '事务'],
        resources: ['高性能 MySQL', 'Redis 实战'],
        milestones: ['完成表结构设计', '定位并优化慢查询'],
        children: [],
      },
    ],
  },
  {
    id: 'data-engineer',
    title: '数据开发工程师',
    level: '中级',
    track: 'data',
    trackLabel: '数据方向',
    description: '围绕数据链路、建模与服务化能力，建立面向分析和决策的数据工程能力。',
    cycle: '12-16 周',
    focus: 'SQL / ETL / 数仓建模',
    projectHint: '用户行为分析链路',
    tree: [
      {
        id: 'data-sql',
        label: 'SQL 与数据处理',
        summary: '查询、聚合和数据清洗',
        description: '重点掌握复杂查询、窗口函数、数据清洗与质量校验。',
        difficulty: '基础',
        duration: '2-3 周',
        status: 'completed',
        tags: ['SQL', '清洗', '窗口函数'],
        resources: ['SQL 必知必会', 'LeetCode SQL 题单'],
        milestones: ['独立完成复杂报表 SQL', '具备基础数据排错能力'],
        children: [],
      },
      {
        id: 'data-warehouse',
        label: '数仓与 ETL',
        summary: '构建稳定的数据链路',
        description: '学习分层建模、指标口径、离线同步和调度编排，搭建完整 ETL 流程。',
        difficulty: '进阶',
        duration: '4-5 周',
        status: 'current',
        tags: ['ETL', '数仓', '调度'],
        resources: ['数据仓库工具箱', 'Airflow 入门'],
        milestones: ['完成一条离线 ETL 链路', '建立指标口径文档'],
        children: [],
      },
      {
        id: 'data-service',
        label: '数据服务化',
        summary: '让数据真正服务业务',
        description: '把指标和数据能力服务化输出，支撑看板、策略和业务系统调用。',
        difficulty: '进阶',
        duration: '3-4 周',
        status: 'planned',
        tags: ['数据 API', '指标服务', '可视化'],
        resources: ['BI 看板案例', '数据接口设计实践'],
        milestones: ['输出一个指标服务接口', '联动业务看板展示'],
        children: [],
      },
    ],
  },
  {
    id: 'ai-engineer',
    title: 'AI 应用工程师',
    level: '中级',
    track: 'ai',
    trackLabel: 'AI 方向',
    description: '面向大模型应用落地，构建 Prompt、RAG、Agent 与业务集成的工程能力。',
    cycle: '10-14 周',
    focus: 'LLM 接入 / Prompt / RAG',
    projectHint: '知识问答或智能助手应用',
    tree: [
      {
        id: 'ai-foundation',
        label: '大模型应用基础',
        summary: '理解模型能力边界与接入方式',
        description: '建立对模型输入输出、上下文限制、提示词设计和评估方式的基础理解。',
        difficulty: '基础',
        duration: '2-3 周',
        status: 'completed',
        tags: ['LLM', 'Prompt', '评测'],
        resources: ['模型接入文档', 'Prompt 案例集'],
        milestones: ['能设计稳定提示词', '理解幻觉与评测基本方法'],
        children: [],
      },
      {
        id: 'ai-rag',
        label: 'RAG 与知识库',
        summary: '把业务知识接进模型',
        description: '学习切片、向量检索、召回重排与答案生成，搭建一个可用的知识问答流程。',
        difficulty: '进阶',
        duration: '3-4 周',
        status: 'current',
        tags: ['RAG', '向量检索', 'Embedding'],
        resources: ['RAG 架构文章', '向量数据库文档'],
        milestones: ['完成一个问答 Demo', '优化召回与答案质量'],
        children: [],
      },
      {
        id: 'ai-agent',
        label: 'Agent 工作流',
        summary: '组织多步骤任务执行',
        description: '围绕工具调用、流程编排、状态管理和安全边界设计业务 Agent。',
        difficulty: '进阶',
        duration: '3-4 周',
        status: 'planned',
        tags: ['Agent', '工具调用', '工作流'],
        resources: ['Agent 设计模式', '多步骤任务案例'],
        milestones: ['设计 1 个可落地业务 Agent', '补齐观测与回退机制'],
        children: [],
      },
    ],
  },
])

const filteredRoles = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase()

  return roles.value.filter((role) => {
    const matchTrack = activeTrack.value === 'all' || role.track === activeTrack.value
    if (!matchTrack) return false
    if (!keyword) return true

    const content = [
      role.title,
      role.description,
      role.focus,
      ...flattenNodes(role.tree).flatMap((node) => [node.label, node.summary, ...node.tags]),
    ]
      .join(' ')
      .toLowerCase()

    return content.includes(keyword)
  })
})

const selectedRoleId = ref(roles.value[0]?.id ?? '')
const selectedRole = computed(
  () => filteredRoles.value.find((role) => role.id === selectedRoleId.value) ?? filteredRoles.value[0] ?? null,
)

const activeKnowledge = ref<KnowledgeTreeNode | null>(null)

const knowledgeStats = computed(() => {
  const nodes = selectedRole.value ? flattenNodes(selectedRole.value.tree) : []
  const total = nodes.length
  const completed = nodes.filter((node) => node.status === 'completed').length
  const progress = total ? Math.round((completed / total) * 100) : 0

  return { total, progress }
})

const activeStatusLabel = computed(() => {
  if (!activeKnowledge.value) return ''
  const map = {
    completed: '已掌握',
    current: '进行中',
    planned: '待学习',
  } satisfies Record<KnowledgeTreeNode['status'], string>

  return map[activeKnowledge.value.status]
})

watch(
  filteredRoles,
  (list: JobKnowledgeRole[]) => {
    if (!list.length) {
      selectedRoleId.value = ''
      activeKnowledge.value = null
      return
    }

    if (!list.some((role) => role.id === selectedRoleId.value)) {
      selectedRoleId.value = list[0]!.id
    }
  },
  { immediate: true },
)

watch(
  selectedRole,
  (role) => {
    if (!role) {
      activeKnowledge.value = null
      return
    }

    const nodes = flattenNodes(role.tree)
    if (!activeKnowledge.value || !nodes.some((node) => node.id === activeKnowledge.value?.id)) {
      activeKnowledge.value = nodes[0] ?? null
    }
  },
  { immediate: true },
)

function flattenNodes(nodes: KnowledgeTreeNode[]): KnowledgeTreeNode[] {
  return nodes.flatMap((node) => [node, ...flattenNodes(node.children)])
}

function getNodeCount(nodes: KnowledgeTreeNode[]): number {
  return flattenNodes(nodes).length
}

function selectRole(roleId: string): void {
  selectedRoleId.value = roleId
}
</script>

<style scoped lang="scss">
.job-knowledge-page {
  min-height: calc(100vh - 60px);
  padding: 28px 20px 40px;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.16), transparent 24%),
    radial-gradient(circle at right center, rgba(56, 189, 248, 0.14), transparent 20%),
    linear-gradient(180deg, #f4f8ff 0%, #eef5ff 52%, #f9fbff 100%);
}

.hero-panel,
.card-shell {
  position: relative;
  border: 1px solid rgba(218, 230, 244, 0.96);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 24px 60px rgba(28, 74, 127, 0.08);
}

.hero-panel {
  max-width: 1360px;
  margin: 0 auto 24px;
  padding: 32px;
  border-radius: 32px;
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.7fr);
  gap: 24px;
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.22), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(245, 249, 255, 0.94));
}

.hero-kicker,
.panel-eyebrow,
.section-title {
  color: #2563eb;
  font-weight: 700;
}

.hero-kicker,
.panel-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.1);
  font-size: 12px;
}

.hero-title {
  margin: 18px 0 12px;
  color: #173a5d;
  font-size: clamp(30px, 4vw, 42px);
  line-height: 1.15;
  font-weight: 800;
}

.hero-desc {
  max-width: 760px;
  margin: 0;
  color: #617890;
  font-size: 15px;
  line-height: 1.9;
}

.hero-actions {
  margin-top: 22px;
  display: flex;
  gap: 12px;
}

.search-input {
  max-width: 460px;
}

.hero-stats {
  display: grid;
  gap: 14px;
}

.hero-stat-card {
  padding: 20px 22px;
  border-radius: 24px;
  background: linear-gradient(180deg, #f8fbff 0%, #eff6ff 100%);
  border: 1px solid rgba(220, 232, 244, 0.96);
}

.hero-stat-card.accent {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(56, 189, 248, 0.16));
}

.stat-label {
  display: block;
  color: #6f879e;
  font-size: 13px;
  font-weight: 700;
}

.hero-stat-card strong {
  display: block;
  margin: 10px 0 6px;
  color: #16324f;
  font-size: 34px;
  font-weight: 800;
}

.hero-stat-card small {
  color: #688096;
  font-size: 13px;
}

.workspace {
  max-width: 1360px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr) 340px;
  gap: 20px;
}

.card-shell {
  border-radius: 28px;
  padding: 24px;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.panel-heading h2 {
  margin: 10px 0 0;
  color: #173a5d;
  font-size: 24px;
  font-weight: 800;
  line-height: 1.2;
}

.role-filter {
  margin-bottom: 16px;
}

.role-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 760px;
  overflow: auto;
}

.role-item {
  padding: 16px 18px;
  border: 1px solid rgba(220, 232, 244, 0.96);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 251, 255, 0.96));
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.role-item:hover,
.role-item.active {
  transform: translateY(-2px);
  border-color: rgba(96, 165, 250, 0.54);
  box-shadow: 0 18px 40px rgba(37, 99, 235, 0.1);
}

.role-item__main,
.role-item__meta {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.role-name {
  color: #173a5d;
  font-size: 16px;
  font-weight: 800;
}

.role-level,
.role-item__meta {
  color: #6f8499;
  font-size: 12px;
  font-weight: 700;
}

.role-item__meta {
  margin-top: 10px;
}

.role-item__desc {
  margin: 10px 0 0;
  color: #5f768e;
  font-size: 13px;
  line-height: 1.7;
}

.knowledge-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.overview-card {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.14), transparent 22%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 250, 255, 0.98));
}

.overview-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.overview-header h2 {
  margin: 10px 0 8px;
  color: #173a5d;
  font-size: 28px;
  font-weight: 800;
}

.overview-header p {
  margin: 0;
  color: #617890;
  font-size: 14px;
  line-height: 1.8;
}

.overview-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.overview-badge {
  min-height: 36px;
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.12);
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
}

.overview-badge.subtle {
  background: rgba(226, 232, 240, 0.72);
  color: #526a83;
}

.overview-metrics {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.metric-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(223, 233, 244, 0.96);
}

.metric-card span {
  display: block;
  color: #7890a7;
  font-size: 13px;
  font-weight: 700;
}

.metric-card strong {
  display: block;
  margin-top: 10px;
  color: #16324f;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.5;
}

.tree-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 760px;
  overflow: auto;
  padding-right: 4px;
}

.detail-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
  background:
    radial-gradient(circle at top left, rgba(56, 189, 248, 0.12), transparent 26%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(247, 251, 255, 0.98));
}

.detail-status {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.detail-status.completed {
  background: rgba(34, 197, 94, 0.12);
  color: #15803d;
}

.detail-status.current {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.detail-status.planned {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.detail-description {
  margin: 0;
  color: #5d748b;
  font-size: 14px;
  line-height: 1.85;
}

.detail-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.detail-meta-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(221, 232, 244, 0.96);
}

.detail-meta-card span {
  display: block;
  color: #758ba1;
  font-size: 12px;
  font-weight: 700;
}

.detail-meta-card strong {
  display: block;
  margin-top: 8px;
  color: #173a5d;
  font-size: 18px;
  font-weight: 800;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-title {
  font-size: 13px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: #285d9a;
  font-size: 12px;
  font-weight: 700;
}

.plain-list {
  margin: 0;
  padding-left: 18px;
  color: #5d748b;
  font-size: 14px;
  line-height: 1.8;
}

@media (max-width: 1240px) {
  .workspace {
    grid-template-columns: 280px minmax(0, 1fr);
  }

  .detail-panel {
    grid-column: 1 / -1;
  }
}

@media (max-width: 980px) {
  .hero-panel,
  .workspace {
    grid-template-columns: 1fr;
  }

  .overview-metrics {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .job-knowledge-page {
    padding: 18px 14px 30px;
  }

  .hero-panel,
  .card-shell {
    padding: 20px 18px;
    border-radius: 24px;
  }

  .hero-actions,
  .overview-header,
  .panel-heading {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-input {
    max-width: none;
    width: 100%;
  }

  .detail-meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
