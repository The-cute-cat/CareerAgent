<template>
  <div class="job-knowledge-page">
    <template v-if="pageMode === 'list'">
      <section class="list-shell">
        <div class="search-bar">
          <el-icon class="search-icon"><Search /></el-icon>
          <input v-model="searchQuery" class="search-input" placeholder="搜索路径、技能、职位..." />
        </div>

        <div class="category-tabs">
          <button
            v-for="item in trackOptions"
            :key="item.value"
            type="button"
            class="category-chip"
            :class="{ active: activeTrack === item.value }"
            @click="activeTrack = item.value"
          >
            {{ item.label }}
          </button>
        </div>

        <div class="role-cards">
          <button
            v-for="role in filteredRoles"
            :key="role.id"
            type="button"
            class="role-card"
            @click="openRole(role.id)"
          >
            <div class="role-card__icon">{{ role.emoji }}</div>
            <div class="role-card__content">
              <div class="role-card__title">{{ role.title }}</div>
              <div class="role-card__desc">{{ role.description }}</div>
              <div class="role-card__meta">{{ role.stageCount }} 个阶段 · {{ getNodeCount(role.tree) }} 个核心技能</div>
            </div>
          </button>

          <div v-if="!filteredRoles.length" class="empty-block">暂无匹配岗位</div>
        </div>
      </section>
    </template>

    <template v-else>
      <section class="detail-shell">
        <header class="detail-header">
          <button type="button" class="back-btn" @click="pageMode = 'list'">
            <el-icon><ArrowLeft /></el-icon>
          </button>
          <h1>{{ selectedRole?.title }}</h1>
          <div class="detail-actions">
            <button type="button" class="icon-btn"><el-icon><FullScreen /></el-icon></button>
            <button type="button" class="icon-btn"><el-icon><Share /></el-icon></button>
          </div>
        </header>

        <div class="detail-body">
          <div class="tree-stage">
            <div class="tree-scroll">
              <TreeNode
                v-if="detailRoot"
                :node="detailRoot"
                :active-id="activeKnowledge?.id"
                @select="handleNodeSelect"
              />
            </div>
          </div>

          <transition name="panel-slide">
            <aside v-if="activeKnowledge" class="knowledge-panel">
              <div class="knowledge-panel__header">
                <div>
                  <div class="knowledge-panel__eyebrow">{{ activeStatusLabel }}</div>
                  <h2>{{ activeKnowledge.label }}</h2>
                  <p>{{ activeKnowledge.summary }}</p>
                </div>
                <button type="button" class="panel-close" @click="activeKnowledge = null">
                  <el-icon><Close /></el-icon>
                </button>
              </div>

              <div class="knowledge-panel__actions">
                <button type="button" class="text-action"><el-icon><Star /></el-icon> 收藏</button>
                <button type="button" class="text-action"><el-icon><Share /></el-icon> 分享</button>
              </div>

              <section class="knowledge-section">
                <h3>知识说明</h3>
                <p>{{ activeKnowledge.description }}</p>
              </section>

              <section class="meta-grid">
                <article class="meta-card">
                  <span>难度</span>
                  <strong>{{ activeKnowledge.difficulty }}</strong>
                </article>
                <article class="meta-card">
                  <span>预计耗时</span>
                  <strong>{{ activeKnowledge.duration }}</strong>
                </article>
              </section>

              <section class="knowledge-section">
                <h3>关键标签</h3>
                <div class="tag-list">
                  <span v-for="tag in activeKnowledge.tags" :key="tag" class="tag-chip">{{ tag }}</span>
                </div>
              </section>

              <section class="knowledge-section">
                <h3>推荐资源</h3>
                <ul>
                  <li v-for="item in activeKnowledge.resources" :key="item">{{ item }}</li>
                </ul>
              </section>

              <section class="knowledge-section">
                <h3>学习里程碑</h3>
                <ul>
                  <li v-for="item in activeKnowledge.milestones" :key="item">{{ item }}</li>
                </ul>
              </section>
            </aside>
          </transition>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ArrowLeft, Close, FullScreen, Search, Share, Star } from '@element-plus/icons-vue'
import TreeNode, { type KnowledgeTreeNode } from '@/components/JobKnowledge/TreeNode.vue'

interface JobKnowledgeRole {
  id: string
  title: string
  emoji: string
  stageCount: number
  level: string
  track: 'frontend' | 'backend' | 'data' | 'ai'
  trackLabel: string
  description: string
  cycle: string
  focus: string
  projectHint: string
  tree: KnowledgeTreeNode[]
}

const pageMode = ref<'list' | 'detail'>('list')
const searchQuery = ref('')
const activeTrack = ref<'all' | JobKnowledgeRole['track']>('all')
const selectedRoleId = ref('')
const activeKnowledge = ref<KnowledgeTreeNode | null>(null)

const trackOptions = [
  { label: '推荐', value: 'all' },
  { label: '热门职业', value: 'backend' },
  { label: '热门技能', value: 'data' },
  { label: '计算机软件', value: 'frontend' },
  { label: 'Java', value: 'ai' },
] as const

const roles = ref<JobKnowledgeRole[]>([
  {
    id: 'java-learning-path',
    title: 'Java研发工程师学习路径',
    emoji: '🚀',
    stageCount: 5,
    level: '中级',
    track: 'backend',
    trackLabel: '后端方向',
    description: '面向中级 Java 工程师的进阶学习路径，涵盖技术深度、行业趋势、职业发展及 AI 时代技能。',
    cycle: '14-18 周',
    focus: 'Java / Spring Boot / 微服务',
    projectHint: '企业级业务系统 + AI 融合项目',
    tree: [
      {
        id: 'java-core-domain',
        label: '核心知识领域',
        summary: '夯实 Java 工程师的基础知识与系统能力',
        description: '围绕语言基础、框架能力、数据库设计与工程实践，建立稳定且可扩展的 Java 开发知识体系。',
        difficulty: '基础',
        duration: '3-4 周',
        status: 'completed',
        tags: ['Java', 'Spring Boot', 'MySQL', '工程化'],
        resources: ['Java 核心技术', 'Spring Boot 官方文档', '高性能 MySQL'],
        milestones: ['完成一个基础业务服务', '掌握接口分层与异常处理'],
        children: [
          {
            id: 'java-language',
            label: 'Java 语言基础',
            summary: '语法、集合、并发与面向对象设计',
            description: '打牢 Java 语法、集合框架、异常处理、IO 与并发编程基础，是进入企业级后端开发的第一步。',
            difficulty: '基础',
            duration: '1-2 周',
            status: 'completed',
            tags: ['集合', '并发', 'IO'],
            resources: ['Java 基础题库', '并发编程实战'],
            milestones: ['能解释线程池', '掌握常见集合选择'],
            children: [],
          },
          {
            id: 'java-framework',
            label: 'Spring 体系',
            summary: '掌握主流企业级 Java 框架',
            description: '深入理解 Spring、Spring Boot、MVC、事务、校验与鉴权等常见企业级开发能力。',
            difficulty: '进阶',
            duration: '2 周',
            status: 'current',
            tags: ['Spring', '事务', '鉴权'],
            resources: ['Spring 官方文档', '实战项目教程'],
            milestones: ['完成 RESTful 服务', '输出接口设计规范'],
            children: [],
          },
        ],
      },
      {
        id: 'industry-trend',
        label: '行业趋势与技术前沿',
        summary: '理解云原生、AI 融合与新兴方向',
        description: '不仅要会写代码，还要理解行业变化趋势，提升技术判断力和职业持续成长能力。',
        difficulty: '进阶',
        duration: '3 周',
        status: 'current',
        tags: ['云原生', 'AI', '新技术'],
        resources: ['云原生白皮书', 'AI 工程落地案例'],
        milestones: ['能解释云原生架构价值', '形成个人技术雷达'],
        children: [
          {
            id: 'cloud-stack',
            label: '云原生技术栈',
            summary: '容器化、部署与服务治理',
            description: '掌握 Docker、Kubernetes、CI/CD、日志监控与服务治理，提升系统交付能力。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['Docker', 'K8s', 'CI/CD'],
            resources: ['Docker 官方文档', 'K8s 实战'],
            milestones: ['完成服务容器化', '搭建部署流水线'],
            children: [],
          },
          {
            id: 'java-ai',
            label: 'AI 与 Java 融合',
            summary: 'Java 工程师的 AI 能力升级方向',
            description: '理解如何在 Java 业务系统中接入 LLM、RAG、Agent 能力，让传统后端能力与 AI 应用融合。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'current',
            tags: ['LLM', 'RAG', 'Agent'],
            resources: ['RAG 设计资料', '模型接入示例'],
            milestones: ['完成一个知识问答 Demo', '输出 AI 接入设计方案'],
            children: [],
          },
          {
            id: 'new-tech',
            label: '新兴技术方向',
            summary: '跟踪具备长期价值的技术主题',
            description: '关注低代码、边缘计算、可观测性平台、智能运维等方向，拓宽技术视野。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['低代码', '可观测性', '智能运维'],
            resources: ['行业趋势报告', '技术峰会分享'],
            milestones: ['形成 1 份技术趋势笔记'],
            children: [],
          },
        ],
      },
      {
        id: 'career-development',
        label: '职业发展路径',
        summary: '从岗位能力走向职业竞争力',
        description: '围绕技术进阶、认证体系与职业竞争力提升，规划后续成长路线。',
        difficulty: '进阶',
        duration: '2-3 周',
        status: 'planned',
        tags: ['职业规划', '技术进阶', '认证'],
        resources: ['成长路线图模板', '职业复盘模板'],
        milestones: ['明确半年成长目标', '形成阶段学习清单'],
        children: [
          {
            id: 'advance-route',
            label: '技术进阶路线',
            summary: '从开发者走向骨干工程师',
            description: '逐步提升架构设计、性能优化、复杂系统排障和团队协作能力。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['架构', '性能优化', '排障'],
            resources: ['系统设计资料', '性能优化案例'],
            milestones: ['完成一次系统优化复盘'],
            children: [],
          },
          {
            id: 'certification',
            label: '行业认证',
            summary: '利用证书提升履历竞争力',
            description: '结合岗位方向选择云计算、数据库、架构或 AI 类认证，提高求职与晋升竞争力。',
            difficulty: '基础',
            duration: '1 周',
            status: 'planned',
            tags: ['认证', '履历', '晋升'],
            resources: ['认证考试官网', '备考路线'],
            milestones: ['确定 1 个目标认证'],
            children: [],
          },
        ],
      },
      {
        id: 'project-case',
        label: '实践项目与案例',
        summary: '用项目沉淀真实交付经验',
        description: '通过企业项目、系统设计和 AI 融合项目，形成可展示的作品与成果。',
        difficulty: '进阶',
        duration: '4-5 周',
        status: 'current',
        tags: ['项目', '案例', '作品'],
        resources: ['项目复盘模板', '系统设计案例集'],
        milestones: ['完成 2 个可展示项目'],
        children: [
          {
            id: 'enterprise-project',
            label: '企业级项目实战',
            summary: '围绕真实业务场景构建系统',
            description: '完成用户中心、订单系统、报表系统等企业级项目，强化业务理解和工程能力。',
            difficulty: '进阶',
            duration: '2-3 周',
            status: 'current',
            tags: ['订单系统', '用户中心', '报表系统'],
            resources: ['业务系统案例', '接口设计规范'],
            milestones: ['交付一个完整后台服务'],
            children: [],
          },
          {
            id: 'ai-project',
            label: 'AI 融合项目',
            summary: '面向 Java 工程师的 AI 系统梳理',
            description: '将 AI 概念与时代理解落到项目中，例如知识库问答、智能代码助手、自动化流程等，构建“传统后端 + AI”复合能力。',
            difficulty: '进阶',
            duration: '2 周',
            status: 'current',
            tags: ['知识库', '智能助手', '自动化'],
            resources: ['RAG 案例集', 'AI 应用架构示例'],
            milestones: ['完成 1 个 AI 融合项目 Demo', '形成系统设计说明'],
            children: [],
          },
        ],
      },
      {
        id: 'ai-evolution',
        label: 'AI时代技能演进',
        summary: '理解技术角色在 AI 时代的升级方式',
        description: '理解为什么传统工程师需要升级为具备产品理解、流程设计与模型集成能力的复合型人才。',
        difficulty: '进阶',
        duration: '1-2 周',
        status: 'planned',
        tags: ['AI 时代', '复合能力', '岗位升级'],
        resources: ['岗位趋势分析', 'AI 工程实践文章'],
        milestones: ['形成个人岗位升级方案'],
        children: [],
      },
    ],
  },
  {
    id: 'java-advanced',
    title: 'Java进阶学习路径',
    emoji: '☕',
    stageCount: 7,
    level: '中高级',
    track: 'backend',
    trackLabel: '后端方向',
    description: '面向中级开发者的 Java 全栈学习路径，涵盖语言特性、云原生、AI 融合及职业发展。',
    cycle: '16-20 周',
    focus: '微服务 / 中间件 / 架构设计',
    projectHint: '分布式系统项目',
    tree: [],
  },
  {
    id: 'java-basic',
    title: 'Java',
    emoji: '🧑‍💻',
    stageCount: 11,
    level: '初中级',
    track: 'frontend',
    trackLabel: '软件开发',
    description: '从基础到进阶的 Java 开发全流程学习路径。',
    cycle: '10-12 周',
    focus: '语言基础 / 面向对象',
    projectHint: '控制台项目 + Web 项目',
    tree: [],
  },
  {
    id: 'javascript',
    title: 'JavaScript编程',
    emoji: '💛',
    stageCount: 19,
    level: '初中级',
    track: 'frontend',
    trackLabel: '前端方向',
    description: '2025 年学习 JavaScript 的逐步指南。',
    cycle: '12-16 周',
    focus: 'JS / 浏览器 / 框架',
    projectHint: '交互站点项目',
    tree: [],
  },
  {
    id: 'computer-software',
    title: '计算机软件',
    emoji: '🧑‍💻',
    stageCount: 15,
    level: '综合',
    track: 'data',
    trackLabel: '综合方向',
    description: '覆盖软件开发全栈知识体系，包含技术、工具、行业趋势及职业发展路径。',
    cycle: '长期',
    focus: '软件工程 / 全栈基础',
    projectHint: '综合项目集',
    tree: [],
  },
])

const filteredRoles = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase()

  return roles.value.filter((role) => {
    const trackMatched = activeTrack.value === 'all' || role.track === activeTrack.value
    if (!trackMatched) return false
    if (!keyword) return true

    const content = [role.title, role.description, role.focus, ...flattenNodes(role.tree).map((item) => item.label)]
      .join(' ')
      .toLowerCase()

    return content.includes(keyword)
  })
})

const selectedRole = computed(() => roles.value.find((item) => item.id === selectedRoleId.value) ?? null)

const detailRoot = computed<KnowledgeTreeNode | null>(() => {
  if (!selectedRole.value) return null

  return {
    id: `${selectedRole.value.id}-root`,
    label: selectedRole.value.title,
    summary: selectedRole.value.description,
    description: `${selectedRole.value.description} 建议学习周期：${selectedRole.value.cycle}；优先突破：${selectedRole.value.focus}；推荐项目方向：${selectedRole.value.projectHint}。`,
    difficulty: selectedRole.value.level,
    duration: selectedRole.value.cycle,
    status: 'current',
    tags: [selectedRole.value.trackLabel, selectedRole.value.focus, selectedRole.value.projectHint],
    resources: ['岗位概览', '阶段学习规划', '项目实践建议'],
    milestones: ['选择一个目标岗位方向', '按阶段逐步展开下一级内容'],
    children: selectedRole.value.tree,
  }
})

const activeStatusLabel = computed(() => {
  if (!activeKnowledge.value) return ''
  const statusMap: Record<KnowledgeTreeNode['status'], string> = {
    completed: '已掌握',
    current: '进行中',
    planned: '待学习',
  }
  return statusMap[activeKnowledge.value.status]
})

watch(
  selectedRole,
  (role) => {
    if (!role) {
      activeKnowledge.value = null
      return
    }
    activeKnowledge.value = detailRoot.value
  },
  { immediate: true },
)

function flattenNodes(nodes: KnowledgeTreeNode[]): KnowledgeTreeNode[] {
  return nodes.flatMap((node) => [node, ...flattenNodes(node.children)])
}

function getNodeCount(nodes: KnowledgeTreeNode[]): number {
  return flattenNodes(nodes).length
}

function openRole(roleId: string): void {
  selectedRoleId.value = roleId
  pageMode.value = 'detail'
}

function handleNodeSelect(node: KnowledgeTreeNode): void {
  activeKnowledge.value = node
}
</script>

<style scoped lang="scss">
.job-knowledge-page {
  min-height: 100%;
  background: #efefef;
}

.list-shell {
  max-width: 1060px;
  margin: 0 auto;
  padding: 14px 0 32px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  height: 72px;
  padding: 0 22px;
  background: rgba(255, 255, 255, 0.68);
  border-radius: 18px;
}

.search-icon {
  font-size: 28px;
  color: #6b7280;
}

.search-input {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: #374151;
  font-size: 18px;
}

.search-input::placeholder {
  color: #6b7280;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin: 24px 6px 22px;
}

.category-chip {
  min-height: 48px;
  padding: 0 24px;
  border-radius: 999px;
  border: 1.5px solid #c9ced6;
  background: #f7f7f7;
  color: #333;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-chip.active {
  color: #1658d3;
  border-color: #1658d3;
  background: #e9f0ff;
  font-weight: 700;
}

.role-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.role-card {
  display: flex;
  align-items: center;
  gap: 18px;
  width: 100%;
  padding: 20px 24px;
  border: none;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.7);
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.role-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.08);
}

.role-card__icon {
  flex: 0 0 54px;
  width: 54px;
  height: 54px;
  border-radius: 14px;
  background: rgba(244, 244, 245, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.role-card__title {
  color: #20242c;
  font-size: 18px;
  font-weight: 800;
}

.role-card__desc {
  margin-top: 8px;
  color: #5f6877;
  font-size: 14px;
  line-height: 1.6;
}

.role-card__meta {
  margin-top: 10px;
  color: #5b6471;
  font-size: 14px;
}

.empty-block {
  padding: 48px 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.7);
  text-align: center;
  color: #6b7280;
}

.detail-shell {
  min-height: 100vh;
  padding: 10px 18px 18px;
}

.detail-header {
  position: sticky;
  top: 0;
  z-index: 12;
  display: grid;
  grid-template-columns: 48px 1fr auto;
  align-items: center;
  gap: 16px;
  height: 54px;
}

.detail-header h1 {
  margin: 0;
  text-align: center;
  color: #1658d3;
  font-size: 18px;
  font-weight: 800;
}

.back-btn,
.icon-btn,
.panel-close {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: #1658d3;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.back-btn {
  font-size: 20px;
}

.detail-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-body {
  position: relative;
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 80px);
}

.tree-stage {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.tree-scroll {
  min-height: calc(100vh - 90px);
  padding: 180px 90px 80px 280px;
  overflow: auto;
}

.knowledge-panel {
  position: sticky;
  top: 84px;
  align-self: flex-start;
  width: 420px;
  max-height: calc(100vh - 110px);
  padding: 26px 24px 24px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.15);
  overflow: auto;
}

.knowledge-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.knowledge-panel__eyebrow {
  color: #1658d3;
  font-size: 13px;
  font-weight: 700;
}

.knowledge-panel__header h2 {
  margin: 6px 0 8px;
  color: #1f2937;
  font-size: 18px;
  font-weight: 800;
}

.knowledge-panel__header p {
  margin: 0;
  color: #667085;
  font-size: 14px;
  line-height: 1.7;
}

.knowledge-panel__actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin: 18px 0 20px;
  padding: 14px 0;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
}

.text-action {
  border: none;
  background: transparent;
  color: #1658d3;
  font-size: 15px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.knowledge-section + .knowledge-section,
.meta-grid + .knowledge-section,
.knowledge-section + .meta-grid {
  margin-top: 18px;
}

.knowledge-section h3 {
  margin: 0 0 10px;
  color: #1f2937;
  font-size: 16px;
}

.knowledge-section p,
.knowledge-section ul {
  margin: 0;
  color: #4b5563;
  line-height: 1.9;
}

.knowledge-section ul {
  padding-left: 18px;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.meta-card {
  padding: 16px;
  border-radius: 18px;
  background: #f8fafc;
}

.meta-card span {
  display: block;
  color: #64748b;
  font-size: 12px;
}

.meta-card strong {
  display: block;
  margin-top: 8px;
  color: #1f2937;
  font-size: 18px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  padding: 6px 12px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1658d3;
  font-size: 13px;
  font-weight: 700;
}

.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: all 0.25s ease;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  transform: translateX(16px);
}

@media (max-width: 1200px) {
  .detail-body {
    flex-direction: column;
  }

  .tree-scroll {
    padding: 90px 24px 40px 24px;
    min-height: auto;
  }

  .knowledge-panel {
    position: static;
    width: 100%;
    max-height: none;
  }
}

@media (max-width: 768px) {
  .list-shell {
    padding: 12px;
  }

  .search-bar {
    height: 62px;
  }

  .category-tabs {
    gap: 10px;
    margin-inline: 0;
  }

  .category-chip {
    min-height: 42px;
    padding-inline: 16px;
    font-size: 14px;
  }

  .role-card {
    padding: 16px;
    align-items: flex-start;
  }

  .detail-shell {
    padding: 8px 10px 16px;
  }

  .detail-header {
    grid-template-columns: 40px 1fr auto;
    gap: 8px;
  }

  .detail-header h1 {
    font-size: 16px;
  }
}
</style>
