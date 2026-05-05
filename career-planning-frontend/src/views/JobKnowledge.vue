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
          <div class="detail-title">
            <p>{{ selectedRole?.trackLabel || '岗位知识图谱' }}</p>
            <h1>{{ selectedRole?.title }}</h1>
          </div>
          <div class="detail-actions">
            <button type="button" class="icon-btn" @click="resetTreeViewport" title="回到中心">
              <el-icon><FullScreen /></el-icon>
            </button>
            <button type="button" class="icon-btn"><el-icon><Share /></el-icon></button>
          </div>
        </header>

        <section class="detail-overview">
          <article class="overview-card overview-card--primary">
            <span>学习周期</span>
            <strong>{{ selectedRole?.cycle || '待补充' }}</strong>
            <p>{{ selectedRole?.description }}</p>
          </article>
          <article class="overview-card">
            <span>核心方向</span>
            <strong>{{ selectedRole?.focus || '待补充' }}</strong>
            <p>围绕当前目标岗位优先拆解核心知识域、阶段任务与项目实践方向。</p>
          </article>
          <article class="overview-card">
            <span>实践建议</span>
            <strong>{{ selectedRole?.projectHint || '待补充' }}</strong>
            <p>点击节点查看详细说明，拖动空白区域可移动整张图谱。</p>
          </article>
        </section>

        <div class="detail-body">
          <div class="tree-stage">
            <div class="tree-toolbar">
              <div class="tree-toolbar__hint">
                <span class="tree-toolbar__dot"></span>
                按住空白区域拖动图谱，点击节点查看详情
              </div>
              <button type="button" class="tree-toolbar__action" @click="resetTreeViewport">重置位置</button>
            </div>

            <div
              ref="treeViewportRef"
              class="tree-viewport"
              :class="{ 'is-dragging': isDraggingTree }"
              @pointerdown="startTreeDrag"
              @pointermove="handleTreeDrag"
              @pointerup="endTreeDrag"
              @pointerleave="endTreeDrag"
              @pointercancel="endTreeDrag"
            >
              <div class="tree-grid"></div>
              <div
                class="tree-scroll"
                :style="{ transform: `translate(${treeOffset.x}px, ${treeOffset.y}px)` }"
              >
                <TreeNode
                  v-if="detailRoot"
                  :node="detailRoot"
                  :active-id="activeKnowledge?.id"
                  @select="handleNodeSelect"
                />
              </div>
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
                <button type="button" class="panel-close" @click="closeKnowledgePanel">
                  <el-icon><Close /></el-icon>
                </button>
              </div>

              <div class="knowledge-panel__tabs">
                <button
                  type="button"
                  class="panel-tab"
                  :class="{ active: panelTab === 'info' }"
                  @click="panelTab = 'info'"
                >知识说明</button>
                <button
                  type="button"
                  class="panel-tab"
                  :class="{ active: panelTab === 'analyze' }"
                  :disabled="aiStreamLoading"
                  @click="handleAnalyzeClick"
                >岗位影响</button>
                <button
                  type="button"
                  class="panel-tab"
                  :class="{ active: panelTab === 'explain' }"
                  :disabled="aiStreamLoading"
                  @click="handleExplainClick"
                >知识精讲</button>
              </div>

              <template v-if="panelTab === 'info'">
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
              </template>

              <template v-else>
                <section class="knowledge-section ai-stream-section">
                  <div v-if="aiStreamLoading && !aiStreamContent" class="ai-stream-loading">
                    <div class="ai-stream-loading__dot"></div>
                    <span>AI 正在思考中...</span>
                  </div>
                  <div v-else-if="aiStreamContent" class="ai-stream-content" v-html="renderMarkdown(aiStreamContent)"></div>
                  <div v-else class="ai-stream-placeholder">
                    <p>点击上方标签页，AI 将为你深度解析该知识点</p>
                  </div>
                  <div v-if="aiStreamLoading" class="ai-stream-cursor">
                    <span class="ai-stream-cursor__bar"></span>
                  </div>
                  <div v-if="aiStreamError" class="ai-stream-error">
                    <p>{{ aiStreamError }}</p>
                    <button type="button" class="retry-btn" @click="retryStream">重试</button>
                  </div>
                </section>
              </template>
            </aside>
          </transition>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { ArrowLeft, Close, FullScreen, Search, Share, Star } from '@element-plus/icons-vue'
import TreeNode, { type KnowledgeTreeNode } from '@/components/JobKnowledge/TreeNode.vue'
import { streamAnalyzeKnowledge, streamExplainKnowledge } from '@/api/knowledge-graph'

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
const treeViewportRef = ref<HTMLElement | null>(null)
const treeOffset = ref({ x: 36, y: 84 })
const dragPointerId = ref<number | null>(null)
const isDraggingTree = ref(false)
const dragStartPoint = ref({ x: 0, y: 0 })
const dragStartOffset = ref({ x: 120, y: 48 })

// AI 流式交互状态
const panelTab = ref<'info' | 'analyze' | 'explain'>('info')
const aiStreamContent = ref('')
const aiStreamLoading = ref(false)
const aiStreamError = ref('')
const currentAbortController = ref<AbortController | null>(null)
const currentStreamType = ref<'analyze' | 'explain' | null>(null)

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
            description: '将 AI 概念与时代理解落到项目中，例如知识库问答、智能代码助手、自动化流程等，构建"传统后端 + AI"复合能力。',
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
    description: '面向中级开发者的 Java 全栈进阶路径，深入 JVM、微服务、分布式系统及架构设计能力。',
    cycle: '16-20 周',
    focus: '微服务 / 中间件 / 架构设计',
    projectHint: '分布式高并发项目',
    tree: [
      {
        id: 'jvm-deep-dive',
        label: 'JVM 深入理解',
        summary: '从内存模型到调优实战，掌握 Java 运行时底层原理',
        description: '深入学习 JVM 内存模型、垃圾回收算法、类加载机制、字节码与 JIT 编译，具备线上故障排查与性能调优能力。',
        difficulty: '高级',
        duration: '2-3 周',
        status: 'current',
        tags: ['JVM', 'GC', '内存管理', '性能调优'],
        resources: ['深入理解 Java 虚拟机', 'JVM 源码分析', 'GC 日志解读指南'],
        milestones: ['能独立分析 OOM 问题', '完成一次 GC 参数调优'],
        children: [
          {
            id: 'jvm-memory-model',
            label: '内存模型与垃圾回收',
            summary: '堆、栈、方法区及 GC 算法原理',
            description: '掌握 JVM 内存区域划分、对象创建过程、可达性分析、GC 算法对比（Serial / CMS / G1 / ZGC）及其适用场景。',
            difficulty: '高级',
            duration: '1 周',
            status: 'current',
            tags: ['堆', '栈', 'GC算法'],
            resources: ['GC 手册', 'G1 收集器详解'],
            milestones: ['画出完整 GC 流程图', '解释 G1 与 CMS 差异'],
            children: [],
          },
          {
            id: 'jvm-tuning',
            label: 'JVM 调优实践',
            summary: '参数配置与问题排查方法论',
            description: '学习常用 JVM 参数、监控工具（Arthas / VisualVM）、常见 OOM 场景分析与解决策略，形成调优闭环。',
            difficulty: '高级',
            duration: '1-2 周',
            status: 'planned',
            tags: ['Arthas', 'OOM排查', '参数调优'],
            resources: ['Alibaba Arthas 文档', '生产环境调优案例'],
            milestones: ['用 Arthas 定位一次内存泄漏'],
            children: [],
          },
        ],
      },
      {
        id: 'microservice-architecture',
        label: '微服务体系架构',
        summary: '构建高可用、可扩展的分布式服务系统',
        description: '全面覆盖 Spring Cloud 生态、服务注册发现、熔断降级、网关路由、分布式事务与链路追踪等核心能力。',
        difficulty: '高级',
        duration: '4 周',
        status: 'planned',
        tags: ['Spring Cloud', '微服务', '分布式'],
        resources: ['Spring Cloud 官方文档', '微服务设计模式'],
        milestones: ['搭建一套完整微服务骨架', '实现服务间调用全链路可观测'],
        children: [
          {
            id: 'service-governance',
            label: '服务治理核心组件',
            summary: '注册中心、配置中心与负载均衡',
            description: '掌握 Nacos / Consul 服务注册与配置管理、Ribbon/LoadBalancer 负载均衡策略、健康检查与服务剔除机制。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['Nacos', '负载均衡', '服务发现'],
            resources: ['Nacos 官方文档', '服务治理最佳实践'],
            milestones: ['完成多实例服务注册与动态扩缩容'],
            children: [],
          },
          {
            id: 'circuit-breaker',
            label: '熔断、限流与降级',
            summary: '保障系统稳定性的三大防线',
            description: '学习 Sentinel 熔断规则配置、限流算法（令牌桶 / 滑动窗口）、降级策略与热点防护，防止雪崩效应。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['Sentinel', '熔断', '限流'],
            resources: ['Sentinel Wiki', '分布式系统稳定性模式'],
            milestones: ['配置并验证熔断降级流程'],
            children: [],
          },
          {
            id: 'distributed-transaction',
            label: '分布式事务方案',
            summary: '跨服务数据一致性解决方案',
            description: '理解 CAP 理论与 BASE 理论，掌握 Seata AT/TCC 模式、Saga 模式、消息最终一致性等主流分布式事务方案选型与应用。',
            difficulty: '高级',
            duration: '1-2 周',
            status: 'planned',
            tags: ['Seata', 'TCC', '最终一致性'],
            resources: ['Seata 官方文档', '分布式事务设计模式'],
            milestones: ['实现一个跨服务的 TCC 事务场景'],
            children: [],
          },
        ],
      },
      {
        id: 'middleware-mastery',
        label: '中间件深度应用',
        summary: '消息队列、缓存与数据库中间件的工程化使用',
        description: '深入 Redis、RabbitMQ/Kafka、Elasticsearch 等中间件的原理、集群部署与生产级运维能力。',
        difficulty: '高级',
        duration: '3-4 周',
        status: 'planned',
        tags: ['Redis', 'MQ', 'ES', '中间件'],
        resources: ['Redis 设计与实现', 'Kafka 权威指南'],
        milestones: ['完成中间件集群搭建', '解决一个生产级中间件问题'],
        children: [
          {
            id: 'redis-advanced',
            label: 'Redis 高级特性与集群',
            summary: '数据结构原理、持久化与高可用方案',
            description: '深入 Redis 五大数据结构底层实现、RDB/AOF 持久化、主从复制、Sentinel 哨兵、Cluster 分片与缓存穿透/击穿/雪崩解决方案。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['数据结构', '主从', 'Cluster'],
            resources: ['Redis 实战', '缓存架构设计'],
            milestones: ['搭建 Redis Cluster 集群', '设计多级缓存体系'],
            children: [],
          },
          {
            id: 'message-queue',
            label: '消息队列设计与选型',
            summary: 'RabbitMQ vs Kafka 及其典型应用场景',
            description: '理解 AMQP 协议与 Kafka 架构，掌握消息可靠性投递、顺序消费、延迟消息、死信队列及幂等处理等生产要点。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['RabbitMQ', 'Kafka', '消息可靠投递'],
            resources: ['消息队列实战', 'Kafka 设计解析'],
            milestones: ['基于 Kafka 实现异步解耦场景'],
            children: [],
          },
        ],
      },
      {
        id: 'high-concurrency-design',
        label: '高并发系统设计',
        summary: '应对海量请求的系统架构与优化策略',
        description: '涵盖多线程并发编程、线程池调优、无锁设计、数据库分库分表、读写分离及 CDN / 多级缓存等高并发架构模式。',
        difficulty: '高级',
        duration: '3 周',
        status: 'planned',
        tags: ['高并发', '多线程', '分库分表'],
        resources: ['Java 并发编程实战', '高并发架构设计'],
        milestones: ['设计一个支持 QPS 10万+ 的接口方案'],
        children: [
          {
            id: 'concurrency-primitives',
            label: '并发编程工具箱',
            summary: '锁、CAS、AQS 与并发容器深度剖析',
            description: '掌握 synchronized / ReentrantLock 底层、CAS 与 AQS 原理、ThreadLocal、ConcurrentHashMap、BlockingQueue 等并发工具的正确使用。',
           难度: '高级',
            duration: '1-2 周',
            status: 'planned',
            tags: ['AQS', 'CAS', '并发容器'],
            resources: ['Java 并发编程艺术', 'JUC 源码导读'],
            milestones: ['手写一个简易线程池'],
            children: [],
          },
          {
            id: 'database-sharding',
            label: '数据库分库分表',
            summary: '水平拆分与 ShardingSphere 实践',
            description: '学习分库分表策略（范围取模 / 哈希）、ShardingSphere-JDBC 集成、全局 ID 生成、跨库关联查询与数据迁移方案。',
            difficulty: '高级',
            duration: '1-2 周',
            status: 'planned',
            tags: ['ShardingSphere', '分片策略', '全局ID'],
            resources: ['ShardingSphere 文档', '数据库分库分表实战'],
            milestones: ['基于 ShardingSphere 实现 8 表拆分'],
            children: [],
          },
        ],
      },
      {
        id: 'system-design-patterns',
        label: '系统设计模式',
        summary: '从需求到架构的系统性思维训练',
        description: '培养面向大规模系统的设计能力，包括领域驱动设计（DDD）、事件驱动架构（EDA）、CQRS 及 API 网关设计等。',
        difficulty: '高级',
        duration: '2-3 周',
        status: 'planned',
        tags: ['DDD', 'EDA', 'API设计', '架构模式'],
        resources: ['领域驱动设计精解', '系统设计面试指南'],
        milestones: ['输出一份完整的系统设计方案文档'],
        children: [
          {
            id: 'ddd-practice',
            label: '领域驱动设计（DDD）',
            summary: '以业务为中心的软件设计方法',
            description: '理解限界上下文、聚合根、值对象与领域事件，学会通过事件风暴进行领域建模，将复杂业务转化为清晰的代码边界。',
            difficulty: '高级',
            duration: '1-2 周',
            status: 'planned',
            tags: ['聚合根', '限界上下文', '事件风暴'],
            resources: ['实现领域驱动设计', 'DDD 战略设计'],
            milestones: ['对一个业务模块完成 DDD 建模'],
            children: [],
          },
          {
            id: 'api-gateway-design',
            label: 'API 网关与接口设计',
            summary: '统一入口认证、路由与协议转换',
            description: '设计统一的 API Gateway 层，包含鉴权、限流、日志、协议适配（gRPC / RESTful）及版本管理能力。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['Gateway', 'RESTful', 'gRPC'],
            resources: ['Spring Cloud Gateway', 'API 设计规范'],
            milestones: ['实现统一网关层 + 接口版本管理'],
            children: [],
          },
        ],
      },
      {
        id: 'devops-and-observability',
        label: 'DevOps 与可观测性',
        summary: '从代码交付到线上运维的全链路能力',
        description: '建立 CI/CD 自动化流水线、容器化部署（Docker + K8s）、日志收集（ELK）、指标监控（Prometheus + Grafana）与分布式链路追踪体系。',
        difficulty: '进阶',
        duration: '2-3 周',
        status: 'planned',
        tags: ['CI/CD', 'Docker', 'K8s', '监控'],
        resources: ['Kubernetes 官方教程', 'Prometheus 实战'],
        milestones: ['搭建 K8s 部署流水线', '接入 Prometheus 监控大盘'],
        children: [
          {
            id: 'cicd-pipeline',
            label: 'CI/CD 自动化流水线',
            summary: '从代码提交到自动上线的全流程',
            description: '使用 Jenkins 或 GitLab CI 搭建自动化流水线，集成单元测试、镜像构建、自动化部署与环境管理。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['Jenkins', 'GitLab CI', '自动化部署'],
            resources: ['CI/CD 最佳实践', 'Jenkins Pipeline 教程'],
            milestones: ['完成 Git push 到自动部署的完整链路'],
            children: [],
          },
          {
            id: 'monitoring-system',
            label: '监控告警体系',
            summary: '指标采集、可视化与智能告警',
            description: '构建 Prometheus + Grafana 监控平台，定义关键业务与技术指标，配置分级告警策略与自愈机制。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['Prometheus', 'Grafana', '告警'],
            resources: ['Prometheus 入门', 'Grafana 大盘设计'],
            milestones: ['搭建完整监控告警平台'],
            children: [],
          },
        ],
      },
      {
        id: 'ai-enhanced-development',
        label: 'AI 辅助开发能力',
        summary: '在 Java 开发中融入 AI 工具与方法',
        description: '学习使用 AI 编程助手提升效率、AI Code Review、智能生成测试用例、以及 LLM 在业务系统中的落地方式（知识问答、代码生成助手）。',
        difficulty: '进阶',
        duration: '1-2 周',
        status: 'planned',
        tags: ['AI辅助', 'Code Review', 'LLM集成'],
        resources: ['AI 编程工具对比', '企业级 AI 应用案例'],
        milestones: ['在项目中落地一项 AI 能力'],
        children: [],
      },
    ],
  },
  {
    id: 'java-basic',
    title: 'Java 基础学习路径',
    emoji: '🧑‍💻',
    stageCount: 11,
    level: '初中级',
    track: 'frontend',
    trackLabel: '软件开发',
    description: '从零开始系统学习 Java 语言，涵盖语法基础、面向对象、集合框架、IO 多线程及数据库操作等核心知识。',
    cycle: '10-12 周',
    focus: '语言基础 / 面向对象 / 数据结构',
    projectHint: '管理系统 + 小工具项目',
    tree: [
      {
        id: 'java-basics-foundation',
        label: 'Java 语言基础',
        summary: '语法、数据类型与程序基本结构',
        description: '掌握 Java 基本语法、变量与常量、数据类型转换、运算符、流程控制（if/switch/循环）与方法定义，建立编程思维。',
        difficulty: '基础',
        duration: '1-2 周',
        status: 'completed',
        tags: ['语法', '数据类型', '流程控制'],
        resources: ['《Java核心技术 卷I》', '菜鸟教程 Java'],
        milestones: ['完成 50 道基础练习题', '编写一个计算器小程序'],
        children: [
          {
            id: 'java-variables-types',
            label: '变量与数据类型',
            summary: '8 种基本数据类型与引用类型的区别',
            description: '理解 byte/short/int/long/float/double/char/boolean 的取值范围与使用场景，掌握类型转换规则与自动装箱拆箱。',
            difficulty: '基础',
            duration: '3 天',
            status: 'completed',
            tags: ['基本类型', '包装类', '类型转换'],
            resources: ['Java 类型体系图解', 'Integer 缓存机制解析'],
            milestones: ['能解释 == 和 equals 的区别'],
            children: [],
          },
          {
            id: 'java-control-flow',
            label: '流程控制语句',
            summary: '条件判断、循环与跳转控制',
            description: '熟练使用 if-else、switch 表达式、for/while/do-while 循环以及 break/continue，能处理常见逻辑分支场景。',
            difficulty: '基础',
            duration: '3 天',
            status: 'completed',
            tags: ['if', 'switch', '循环'],
            resources: ['Java 流程控制详解', '循环优化技巧'],
            milestones: ['用嵌套循环打印九九乘法表', '实现一个简单猜数字游戏'],
            children: [],
          },
        ],
      },
      {
        id: 'java-oop-core',
        label: '面向对象编程核心',
        summary: '封装、继承、多态与接口设计',
        description: '深入理解 OOP 三大特性，掌握类与对象的创建、构造方法重载、this/super 关键字、抽象类与接口的区别及应用。',
        difficulty: '进阶',
        duration: '2-3 周',
        status: 'current',
        tags: ['OOP', '封装', '继承', '多态'],
        resources: ['Head First Java', '设计模式之基础'],
        milestones: ['设计一套学生/教师/课程类体系', '完成面向对象综合案例'],
        children: [
          {
            id: 'java-class-object',
            label: '类与对象',
            summary: '类的定义、创建与成员管理',
            description: '学会定义属性与方法、使用访问修饰符（public/private/protected）、理解 static 与实例成员的区别。',
            difficulty: '基础',
            duration: '1 周',
            status: 'completed',
            tags: ['class', 'static', '修饰符'],
            resources: ['类与对象入门', 'static 关键字详解'],
            milestones: ['编写一个图书类并实例化多个对象'],
            children: [],
          },
          {
            id: 'java-inheritance-polymorphism',
            label: '继承与多态',
            summary: '代码复用与动态绑定的核心机制',
            description: '掌握 extends 继承、方法重写 @Override、向上转型与向下转型、instanceof 判断及多态的实际应用场景。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'current',
            tags: ['extends', 'override', '动态绑定'],
            resources: ['Java 继承机制详解', '多态实战案例'],
            milestones: ['用多态实现一个动物叫声模拟器'],
            children: [],
          },
          {
            id: 'java-interface-abstract',
            label: '抽象类与接口',
            summary: '抽象设计与契约编程',
            description: '理解 abstract class 与 interface 的区别与选择策略、default 方法、函数式接口及 Lambda 简化写法。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['abstract', 'interface', 'Lambda'],
            resources: ['接口 vs 抽象类对比', 'Lambda 表达式教程'],
            milestones: ['用接口实现 USB 设备插拔模拟'],
            children: [],
          },
        ],
      },
      {
        id: 'java-collections',
        label: '集合框架体系',
        summary: 'List、Set、Map 及常用算法操作',
        description: '全面掌握 ArrayList、LinkedList、HashSet、HashMap 等核心集合类的底层原理、时间复杂度与适用场景选择。',
        difficulty: '进阶',
        duration: '2 周',
        status: 'planned',
        tags: ['List', 'Set', 'Map', '集合'],
        resources: ['Java 集合源码分析', '集合框架速查表'],
        milestones: ['能手写简易 HashMap', '对比各集合增删改查性能'],
        children: [
          {
            id: 'java-list-set',
            label: 'List 与 Set 集合',
            summary: '有序列表与去重集合的使用',
            description: '掌握 ArrayList 扩容机制、LinkedList 双向链表结构、TreeSet 排序原理及 HashSet 去重逻辑（hashCode/equals）。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['ArrayList', 'LinkedList', 'HashSet'],
            resources: ['ArrayList 源码解读', 'HashMap 底层原理'],
            milestones: ['分析 ArrayList 扩容过程'],
            children: [],
          },
          {
            id: 'java-map-dict',
            label: 'Map 字典结构',
            summary: '键值对存储与哈希表原理',
            description: '深入 HashMap 数组+链表+红黑树结构、put/get 流程、负载因子与扩容、LinkedHashMap 有序性及 TreeMap 排序能力。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['HashMap', '红黑树', '哈希冲突'],
            resources: ['HashMap 1.8 改进详解', '手写 HashMap 教程'],
            milestones: ['手写简化版 HashMap（数组+链表）'],
            children: [],
          },
        ],
      },
      {
        id: 'java-io-nio',
        label: 'IO 与文件操作',
        summary: '输入输出流、NIO 及文件系统操作',
        description: '学习字节流与字符流、缓冲流、序列化、File 类操作、Path/Files API 以及 NIO 的 Buffer 与 Channel 模型。',
        difficulty: '进阶',
        duration: '1-2 周',
        status: 'planned',
        tags: ['IO', 'NIO', '文件读写'],
        resources: ['Java IO/NIO 教程', '文件操作最佳实践'],
        milestones: ['实现文件复制工具', '完成一个简易记事本读写功能'],
        children: [
          {
            id: 'java-stream-io',
            label: '传统 IO 流体系',
            summary: '字节流、字符流与缓冲流',
            description: '掌握 InputStream/OutputStream、Reader/Writer 层次结构、BufferedReader/BufferedWriter 缓冲提升效率及 try-with-resources 自动关闭。',
            difficulty: '基础',
            duration: '1 周',
            status: 'planned',
            tags: ['InputStream', 'Buffered', 'try-with-resources'],
            resources: ['IO 流家族图谱', '资源关闭规范'],
            milestones: ['实现大文件逐行读取与写入'],
            children: [],
          },
        ],
      },
      {
        id: 'java-threading',
        label: '多线程基础',
        summary: '线程创建、同步与并发安全',
        description: '了解 Thread 与 Runnable、synchronized 同步锁、volatile 可见性、线程池基础概念及常见的并发安全问题。',
        difficulty: '进阶',
        duration: '1-2 周',
        status: 'planned',
        tags: ['Thread', 'synchronized', '线程池'],
        resources: ['Java 并发入门', '线程安全指南'],
        milestones: ['实现生产者消费者模型', '解决一个线程安全问题'],
        children: [],
      },
      {
        id: 'java-jdbc-mysql',
        label: '数据库操作（JDBC + MySQL）',
        summary: '连接数据库执行 CRUD 操作',
        description: '掌握 JDBC 连接流程、PreparedStatement 防 SQL 注射、事务管理（ACID）、连接池配置及 MySQL 常用 SQL 语法。',
        difficulty: '进阶',
        duration: '1-2 周',
        status: 'planned',
        tags: ['JDBC', 'MySQL', 'SQL', '事务'],
        resources: ['MySQL 必知必会', 'JDBC 官方教程'],
        milestones: ['搭建 JDBC 工具类', '完成学生信息管理系统 CRUD'],
        children: [
          {
            id: 'java-sql-basics',
            label: 'SQL 语言基础',
            summary: 'DDL、DML 与查询语句',
            description: '学会建表（CREATE TABLE）、增删改（INSERT/UPDATE/DELETE）、多表关联查询（JOIN）、分组聚合（GROUP BY/HAVING）及子查询。',
            difficulty: '基础',
            duration: '1 周',
            status: 'planned',
            tags: ['SELECT', 'JOIN', '聚合查询'],
            resources: ['SQL 入门教程', 'MySQL 实战 45 讲'],
            milestones: ['写出至少 10 种不同场景的 SQL 查询'],
            children: [],
          },
          {
            id: 'java-jdbc-practice',
            label: 'JDBC 编程实践',
            summary: 'Java 程序连接与操作数据库',
            description: '使用 DriverManager 获取连接、PreparedStatement 执行参数化查询、ResultSet 结果遍历及事务手动提交/回滚。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['Connection', 'PreparedStatement', '事务提交'],
            resources: ['JDBC 最佳实践', 'HikariCP 连接池'],
            milestones: ['封装通用 DBUtil 工具类'],
            children: [],
          },
        ],
      },
      {
        id: 'java-exception-utils',
        label: '异常处理与常用工具类',
        summary: '异常体系、日志与开发工具库',
        description: '掌握 try-catch-finally 异常捕获层次、自定义异常、Log4j2/SLF4J 日志记录、Apache Commons/Lombok 等常用工具库。',
        difficulty: '基础',
        duration: '1 周',
        status: 'planned',
        tags: ['Exception', '日志', 'Lombok'],
        resources: ['Java 异常处理规范', 'SLF4J 使用指南'],
        milestones: ['统一封装业务异常类', '在项目中接入 Lombok + SLF4J'],
        children: [],
      },
      {
        id: 'java-gui-console-project',
        label: '综合实践项目',
        summary: '将所学知识融会贯通于实际项目中',
        description: '通过控制台或 Swing GUI 项目整合面向对象、集合、IO、多线程与数据库操作能力，产出完整可运行的软件作品。',
        difficulty: '进阶',
        duration: '2 周',
        status: 'planned',
        tags: ['项目实战', '综合应用'],
        resources: ['Java 项目实战指南', '代码规范手册'],
        milestones: ['完成一个图书/商品管理系统', '撰写项目技术总结文档'],
        children: [
          {
            id: 'console-management-system',
            label: '控制台管理系统',
            summary: '基于控制台的 CRUD 管理应用',
            description: '实现用户登录注册、数据的增删改查、数据持久化到文件或数据库、菜单导航等功能模块。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['控制台交互', '菜单系统', '持久化'],
            resources: ['控制台 UI 设计参考', '项目架构模板'],
            milestones: ['系统可独立运行并演示'],
            children: [],
          },
        ],
      },
      {
        id: 'java-web-intro',
        label: 'Web 开发入门',
        summary: '从控制台走向浏览器端的 Java Web 应用',
        description: '了解 HTTP 协议、Servlet 基础、Tomcat 服务器部署及 JSP/Thymeleaf 页面渲染，为后续 Spring 框架学习打基础。',
        difficulty: '进阶',
        duration: '1-2 周',
        status: 'planned',
        tags: ['HTTP', 'Servlet', 'Tomcat', 'Web'],
        resources: ['HTTP 权威指南', 'Servlet 3.0 规范'],
        milestones: ['部署第一个 Servlet 到 Tomcat'],
        children: [],
      },
      {
        id: 'java-testing-best-practices',
        label: '测试意识与编码规范',
        summary: '单元测试、代码质量与团队协作习惯',
        description: '引入 JUnit 单元测试、了解 TDD 思想、遵循阿里巴巴 Java 开发规范、使用 Maven/Gradle 进行项目管理与依赖构建。',
        difficulty: '基础',
        duration: '1 周',
        status: 'planned',
        tags: ['JUnit', 'Maven', '代码规范'],
        resources: ['阿里巴巴 Java 开发手册', 'JUnit 5 用户指南'],
        milestones: ['为核心业务方法编写单元测试', '通过 Checkstyle 代码检查'],
        children: [],
      },
      {
        id: 'java-next-step-guide',
        label: '下一步方向指引',
        summary: '学完基础后如何继续进阶',
        description: '明确后续学习路径：Spring 全家桶 → MyBatis → 微服务 → 中间件 → 架构设计，形成清晰的职业成长路线图。',
        difficulty: '基础',
        duration: '持续',
        status: 'planned',
        tags: ['学习路线', '职业规划', '进阶指引'],
        resources: ['Java 后端学习路线图', '技术社区推荐'],
        milestones: ['制定个人 6 个月学习计划'],
        children: [],
      },
    ],
  },
  {
    id: 'javascript',
    title: 'JavaScript 编程学习路径',
    emoji: '💛',
    stageCount: 19,
    level: '初中级',
    track: 'frontend',
    trackLabel: '前端方向',
    description: '2025 年系统学习 JavaScript 的完整路径，涵盖语言核心、浏览器 API、ES6+ 新特性、异步编程、DOM 操作、TypeScript 基础及现代前端工程化。',
    cycle: '12-16 周',
    focus: 'JS / 浏览器 / 框架生态',
    projectHint: '交互式 Web 应用项目',
    tree: [
      {
        id: 'js-core-fundamentals',
        label: 'JS 语言核心基础',
        summary: '语法、数据类型与程序基本结构',
        description: '掌握 JavaScript 变量声明（let/const/var）、数据类型（原始类型与引用类型）、运算符、流程控制语句及函数定义与调用。',
        difficulty: '基础',
        duration: '1-2 周',
        status: 'completed',
        tags: ['变量', '数据类型', '函数', '作用域'],
        resources: ['MDN JavaScript 指南', '《JavaScript 高级程序设计》'],
        milestones: ['完成 100 道基础 JS 练习题', '理解变量提升与 TDZ'],
        children: [
          {
            id: 'js-types-coercion',
            label: '数据类型与类型转换',
            summary: '7 种原始类型的特性与隐式转换规则',
            description: '深入理解 undefined/null/string/number/boolean/symbol/bigint 的特点，掌握 == 与 === 的区别、typeof 行为及常见类型转换陷阱。',
            difficulty: '基础',
            duration: '3-5 天',
            status: 'completed',
            tags: ['typeof', '隐式转换', 'NaN'],
            resources: ['JS 类型转换表', '你不知道的 JavaScript（上卷）'],
            milestones: ['能解释 [] == ![] 的结果', '总结 10 条类型转换规则'],
            children: [],
          },
          {
            id: 'js-functions-closures',
            label: '函数与闭包',
            summary: '函数定义方式、作用域链与闭包机制',
            description: '掌握函数表达式、箭头函数、默认参数、rest 参数、词法作用域、闭包原理及其在模块化和数据封装中的实际应用。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'current',
            tags: ['闭包', '作用域', 'this指向'],
            resources: ['闭包详解图解', 'this 绑定规则总结'],
            milestones: ['手写一个简易计数器闭包', '解释 this 四种绑定优先级'],
            children: [],
          },
          {
            id: 'js-prototype-chain',
            label: '原型与原型链',
            summary: '理解 JS 对象继承的底层机制',
            description: '深入 prototype/__proto__ 关系、原型链查找过程、Object.create/new 运算符的工作原理以及 ES6 class 的本质。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['prototype', '__proto__', 'class'],
            resources: ['原型链图解', 'class vs function 对比'],
            milestones: ['画出一组对象的完整原型链图', '用多种方式实现继承'],
            children: [],
          },
        ],
      },
      {
        id: 'js-es6-plus',
        label: 'ES6+ 现代语法',
        summary: '从 ES2015 到 ES2024 的新特性全览',
        description: '系统学习解构赋值、模板字符串、Promise/async-await、展开运算符、可选链、空值合并、迭代器/生成器等现代 JS 特性。',
        difficulty: '进阶',
        duration: '2 周',
        status: 'current',
        tags: ['ES6', 'Promise', 'async/await', '解构'],
        resources: ['ES6 入门教程', 'ECMAScript 新特性速查'],
        milestones: ['用 async/await 重写回调嵌套代码', '熟练使用可选链和空值合并'],
        children: [
          {
            id: 'js-promise-async',
            label: '异步编程演进',
            summary: '从回调到 Promise 到 async/await',
            description: '理解事件循环（Event Loop）宏任务微任务队列、Promise 状态流转、错误捕获链、async/await 底层实现及并发控制模式。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'current',
            tags: ['Event Loop', '宏任务', '微任务'],
            resources: ['Event Loop 可视化', 'Promise A+ 规范解读'],
            milestones: ['能手写简易 Promise', '分析一段异步代码的输出顺序'],
            children: [],
          },
          {
            id: 'js-destructuring-spread',
            label: '解构与展开运算符',
            summary: '简化数据提取与合并操作的语法糖',
            description: '掌握数组/对象解构、剩余参数、展开运算符在数组拷贝、对象合并、函数参数等场景的高效用法。',
            difficulty: '基础',
            duration: '3 天',
            status: 'completed',
            tags: ['解构', '...运算符', '剩余参数'],
            resources: ['解构赋值用法大全', '展开运算符技巧集'],
            milestones: ['用一行代码完成数组去重和扁平化'],
            children: [],
          },
        ],
      },
      {
        id: 'js-dom-manipulation',
        label: 'DOM 操作与事件处理',
        summary: '操作网页元素与响应用户交互',
        description: '学会选择 DOM 元素、修改样式/内容/属性、创建/删除节点、事件监听（冒泡/捕获/委托）、表单处理及常用 DOM API。',
        difficulty: '基础',
        duration: '2 周',
        status: 'current',
        tags: ['DOM', '事件委托', 'BOM', '表单'],
        resources: ['DOM 编程艺术', 'MDN Web APIs'],
        milestones: ['实现一个可拖拽排序列表', '完成事件委托优化的事件管理器'],
        children: [
          {
            id: 'js-dom-api',
            label: 'DOM 核心操作',
            summary: '查询、修改与遍历文档树',
            description: '掌握 querySelector/querySelectorAll、classList/style 属性操作、innerHTML vs textContent 安全性、节点增删改查方法。',
            difficulty: '基础',
            duration: '1 周',
            status: 'completed',
            tags: ['querySelector', 'innerHTML', 'createElement'],
            resources: ['DOM API 速查手册', 'XSS 防护指南'],
            milestones: ['动态渲染一份学生成绩表格'],
            children: [],
          },
          {
            id: 'js-event-system',
            label: '事件机制深度',
            summary: '事件流模型与高级交互模式',
            description: '理解捕获→目标→冒泡三阶段、addEventListener 第三参数含义、阻止冒泡/默认行为、自定义事件及事件总线设计模式。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['事件流', 'preventDefault', 'EventBus'],
            resources: ['事件模型详解', '发布订阅模式实现'],
            milestones: ['实现一个简易 EventBus 发布订阅'],
            children: [],
          },
        ],
      },
      {
        id: 'js-browser-apis',
        label: '浏览器 API 体系',
        summary: 'Web 平台提供的丰富能力接口',
        description: '了解 Fetch/Ajax 网络请求、LocalStorage/SessionStorage 存储、Canvas/SVG 图形绘制、Geolocation 定位、Notification 通知等 Web API。',
        difficulty: '进阶',
        duration: '2 周',
        status: 'planned',
        tags: ['Fetch', 'LocalStorage', 'Canvas', 'WebAPI'],
        resources: ['MDN Web API 参考', 'Can I Use 兼容性查询'],
        milestones: ['封装一个通用 HTTP 请求库', '用 Canvas 实现一个简易画板'],
        children: [
          {
            id: 'js-fetch-network',
            label: '网络请求与数据交互',
            summary: '使用 Fetch API 进行前后端通信',
            description: '掌握 GET/POST/PUT/DELETE 请求、JSON 数据解析、请求头配置、CORS 跨域处理及错误状态码处理策略。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['fetch', 'axios', 'CORS', 'HTTP'],
            resources: ['HTTP 协议入门', 'Axios 使用指南'],
            milestones: ['封装带拦截器的 fetch 工具函数'],
            children: [],
          },
          {
            id: 'js-storage-indexedDB',
            label: '客户端存储方案',
            summary: 'Cookie、LocalStorage 与 IndexedDB 选型',
            description: '对比各存储方案的容量限制与生命周期，重点学习 IndexedDB 的数据库创建、事务操作与索引查询。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['Cookie', 'LocalStorage', 'IndexedDB'],
            resources: ['浏览器存储对比表', 'IndexedDB 实战教程'],
            milestones: ['用 IndexedDB 存储并检索用户数据'],
            children: [],
          },
        ],
      },
      {
        id: 'js-oop-design-patterns',
        label: '面向对象与设计模式',
        summary: '用 OOP 思想组织复杂 JS 应用',
        description: '学习工厂模式、单例模式、观察者模式、策略模式、装饰器模式等经典设计模式在前端场景中的应用实践。',
        difficulty: '进阶',
        duration: '1-2 周',
        status: 'planned',
        tags: ['OOP', '设计模式', 'SOLID原则'],
        resources: ['《JavaScript 设计模式》', '前端设计模式实战'],
        milestones: ['在项目中应用至少 3 种设计模式'],
        children: [],
      },
      {
        id: 'js-functional-programming',
        label: '函数式编程思想',
        summary: '纯函数、不可变性与高阶函数',
        description: '了解函数式编程范式：纯函数副作用、柯里化、组合（compose/pipe）、函子（Functor）概念及 Lodash/Rambda 工具库的使用。',
        difficulty: '进阶',
        duration: '1 周',
        status: 'planned',
        tags: ['纯函数', '柯里化', 'compose', 'immutable'],
        resources: ['JS 函数式编程指南', 'Lodash 文档'],
        milestones: ['手写 compose 和 pipe 函数'],
        children: [],
      },
      {
        id: 'js-typescript-foundation',
        label: 'TypeScript 基础入门',
        summary: '为 JS 添加静态类型安全',
        description: '掌握 TS 类型系统：基础类型注解、接口 interface、泛型、联合/交叉类型、类型守卫、工具类型（Partial/Pick/Omit）及配置文件。',
        difficulty: '进阶',
        duration: '2 周',
        status: 'planned',
        tags: ['TypeScript', '类型系统', '泛型'],
        resources: ['TypeScript 官方手册', 'TS 类型体操入门'],
        milestones: ['将现有 JS 项目迁移为 TS', '编写通用工具类型'],
        children: [
          {
            id: 'ts-type-system',
            label: '类型系统核心',
            summary: '类型注解、接口与类型别名',
            description: '学习基本类型注解、interface 定义对象结构、type 类型别名、字面量类型、联合类型与交叉类型的灵活运用。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['interface', 'type', '联合类型'],
            resources: ['TS 类型推导详解', 'interface vs type 选择指南'],
            milestones: ['为一个 API 响应定义完整类型'],
            children: [],
          },
          {
            id: 'ts-generics',
            label: '泛型编程',
            summary: '写出可复用的类型安全的组件',
            description: '理解泛型函数、泛型接口/类、泛型约束 extends、条件类型 infer 及内置工具类型的实现原理与应用。',
            difficulty: '高级',
            duration: '1 周',
            status: 'planned',
            tags: ['泛型', '条件类型', '工具类型'],
            resources: ['TS 泛型精讲', '类型体操练习集'],
            milestones: ['实现 5 个常用工具类型'],
            children: [],
          },
        ],
      },
      {
        id: 'js-performance-optimization',
        label: '性能优化技巧',
        summary: '让 Web 应用运行更快更流畅',
        description: '学习页面加载优化（资源压缩/懒加载/预加载）、渲染性能优化（重排重绘/虚拟列表）、内存泄漏检测与 V8 引擎工作原理。',
        difficulty: '进阶',
        duration: '1-2 周',
        status: 'planned',
        tags: ['性能优化', 'V8', '懒加载', '虚拟列表'],
        resources: ['Web 性能权威指南', 'Chrome DevTools 性能面板'],
        milestones: ['对目标页面进行一次完整的性能优化', '使用 Performance 面板分析瓶颈'],
        children: [],
      },
      {
        id: 'js-modular-bundling',
        label: '模块化与构建工具',
        summary: 'ES Modules、打包与工程化体系',
        description: '掌握 CommonJS/ESM 模块规范、Webpack/Vite 打包配置、代码分割、Tree Shaking 及 npm 包管理与发布流程。',
        difficulty: '进阶',
        duration: '2 周',
        status: 'planned',
        tags: ['ESM', 'Webpack', 'Vite', 'npm'],
        resources: ['Webpack 配置指南', 'Vite 官方文档'],
        milestones: ['搭建一套完整的前端脚手架', '配置多环境打包与代理'],
        children: [
          {
            id: 'webpack-vite-config',
            label: '打包工具实战',
            summary: 'Webpack/Vite 从零配置到生产就绪',
            description: '学习 loader/plugin 机制、开发服务器配置、环境变量注入、分包策略及 PWA 支持配置。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['loader', 'plugin', 'devServer'],
            resources: ['Webpack 5 进阶', 'Vite 插件开发'],
            milestones: ['配置一套生产级 Vite 构建流程'],
            children: [],
          },
        ],
      },
      {
        id: 'js-testing-debugging',
        label: '测试与调试技能',
        summary: '保证代码质量与快速定位问题',
        description: '掌握 Chrome DevTools 断点调试、Console 面板高级用法、Jest/Vitest 单元测试编写、E2E 测试基础及 CI 中集成测试。',
        difficulty: '进阶',
        duration: '1-2 周',
        status: 'planned',
        tags: ['DevTools', 'Jest', 'Vitest', '单元测试'],
        resources: ['Chrome DevTools 完全指南', 'Jest 测试实战'],
        milestones: ['为核心模块编写测试覆盖率达 80%+', '熟练使用 DevTools 分析问题'],
        children: [],
      },
      {
        id: 'js-security-best-practices',
        label: '前端安全知识',
        summary: '防范常见的 Web 安全攻击',
        description: '了解 XSS/CSRF/点击劫持等攻击手段及防御措施（CSP、Token、SameSite Cookie）、敏感数据处理与 HTTPS 重要性。',
        difficulty: '进阶',
        duration: '1 周',
        status: 'planned',
        tags: ['XSS', 'CSRF', 'CSP', '安全'],
        resources: ['OWASP Top 10', '前端安全白皮书'],
        milestones: ['对项目进行安全审计并修复隐患'],
        children: [],
      },
      {
        id: 'js-project-practice',
        label: '综合项目实战',
        summary: '将所学知识融会贯通于实际项目',
        description: '通过 2-3 个综合项目整合 JS 核心、DOM、异步、网络请求、模块化等全部知识点，产出可展示的作品集。',
        difficulty: '进阶',
        duration: '3-4 周',
        status: 'planned',
        tags: ['项目实战', '作品集', '综合应用'],
        resources: ['前端项目实战案例', 'GitHub Pages 部署指南'],
        milestones: ['完成一个 Todo 应用 + 天气查询 + 个人博客'],
        children: [
          {
            id: 'js-todo-app',
            label: 'Todo 待办事项应用',
            summary: '练手 CRUD 与状态管理的经典项目',
            description: '实现任务的增删改查、筛选（全部/进行中/已完成）、本地持久化存储及动画过渡效果。',
            difficulty: '基础',
            duration: '1 周',
            status: 'planned',
            tags: ['CRUD', 'LocalStorage', 'CSS 动画'],
            resources: ['Todo App 设计参考', 'CSS 过渡动画教程'],
            milestones: ['功能完备且 UI 精美的待办应用'],
            children: [],
          },
          {
            id: 'js-weather-app',
            label: '天气查询应用',
            summary: '接入真实 API 的网络请求项目',
            description: '调用天气 API 获取实时数据、城市搜索切换、未来几天预报展示及错误处理与 loading 状态管理。',
            difficulty: '进阶',
            duration: '1 周',
            status: 'planned',
            tags: ['API对接', '异步数据', '错误处理'],
            resources: ['开放天气 API 文档', 'Loading 状态设计模式'],
            milestones: ['成功对接外部 API 并展示数据'],
            children: [],
          },
          {
            id: 'js-personal-blog',
            label: '个人技术博客',
            summary: '展示个人能力的综合性项目',
            description: '包含文章列表/详情页、分类标签导航、暗色模式切换、响应式布局、Markdown 渲染及评论功能模拟。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['响应式', 'Markdown', '主题切换'],
            resources: ['响应式布局指南', 'marked.js Markdown 解析'],
            milestones: ['部署上线并可公开访问'],
            children: [],
          },
        ],
      },
      {
        id: 'js-framework-prep',
        label: '框架前置准备',
        summary: '为学习 Vue/React 框架打好基础',
        description: '回顾组件化思维、数据驱动视图理念、虚拟 DOM 概念、响应式原理（Object.defineProperty/Proxy），做好进入框架学习的准备。',
        difficulty: '进阶',
        duration: '1 周',
        status: 'planned',
        tags: ['组件化', '虚拟DOM', '响应式'],
        resources: ['Vue/React 学习前导', '框架底层原理浅析'],
        milestones: ['明确下一步要学的框架方向', '阅读框架源码导读文章'],
        children: [],
      },
    ],
  },
  {
    id: 'computer-software',
    title: '计算机软件全栈学习路径',
    emoji: '🧑‍💻',
    stageCount: 15,
    level: '综合',
    track: 'data',
    trackLabel: '综合方向',
    description: '覆盖软件开发全栈知识体系，包含编程基础、前端、后端、数据库、网络、算法、操作系统、软件工程及行业趋势与职业发展的完整路线图。',
    cycle: '长期（6-12 个月）',
    focus: '软件工程 / 全栈基础 / 计算机科学',
    projectHint: '全栈综合项目集',
    tree: [
      {
        id: 'cs-programming-foundation',
        label: '编程语言基础',
        summary: '选择一门主力语言并打牢语法根基',
        description: '从 Python / Java / JavaScript 中选择一门作为入门语言，掌握变量、数据类型、流程控制、函数、基本数据结构与文件操作。',
        difficulty: '基础',
        duration: '3-4 周',
        status: 'completed',
        tags: ['Python', 'Java', 'JavaScript', '编程基础'],
        resources: ['《编程珠玑》', 'CS50 入门课程', 'Codecademy 交互教程'],
        milestones: ['完成一门语言的全部基础练习', '能独立编写解决实际小问题的脚本'],
        children: [
          {
            id: 'cs-lang-choice',
            label: '语言选型与入门',
            summary: '根据目标方向选择第一门编程语言',
            description: '数据分析/AI 选 Python，后端开发选 Java，Web 前端选 JavaScript。了解各语言的生态、就业前景和学习曲线。',
            difficulty: '基础',
            duration: '1 周',
            status: 'completed',
            tags: ['语言对比', '职业规划', '技术选型'],
            resources: ['TIOBE 编程语言排行榜', '2025 技术趋势报告'],
            milestones: ['确定主攻语言并制定学习计划'],
            children: [],
          },
          {
            id: 'cs-data-structures-basic',
            label: '基础数据结构',
            summary: '数组、链表、栈、队列的基本实现与应用',
            description: '理解线性表的顺序与链式存储，掌握栈的后进先出和队列的先进先出特性，能在合适场景中选用正确结构。',
            difficulty: '进阶',
            duration: '2 周',
            status: 'current',
            tags: ['数组', '链表', '栈', '队列'],
            resources: ['《大话数据结构》', 'LeetCode 题单（初级）'],
            milestones: ['手写实现 4 种基本数据结构', '完成 LeetCode 前 30 道简单题'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-algorithms-thinking',
        label: '算法思维训练',
        summary: '培养解决问题的计算思维能力',
        description: '学习排序算法（冒泡/快排/归并）、查找算法（二分/哈希）、递归与回溯、贪心策略及动态规划入门思想。',
        difficulty: '进阶',
        duration: '4-6 周',
        status: 'current',
        tags: ['排序', '二分查找', '递归', '动态规划'],
        resources: ['《算法导论》精简版', 'LeetCode Hot 100', '算法可视化网站'],
        milestones: ['能手写快排和归并排序', '能用 DP 解决背包类问题'],
        children: [
          {
            id: 'cs-sorting-algorithms',
            label: '经典排序算法',
            summary: '8 大排序算法原理与性能对比',
            description: '从 O(n²) 到 O(nlogn) 的排序演进：冒泡、选择、插入、希尔、快速排序、归并排序、堆排序、计数/桶/基数排序。',
            difficulty: '进阶',
            duration: '2 周',
            status: 'current',
            tags: ['时间复杂度', '空间复杂度', '稳定性'],
            resources: ['排序算法动画演示', '各排序适用场景总结'],
            milestones: ['画出所有排序的过程图并分析复杂度'],
            children: [],
          },
          {
            id: 'cs-recursion-backtrack',
            label: '递归与回溯',
            summary: '分解问题与穷举搜索的核心范式',
            description: '理解递归的三要素（终止条件、递归体、返回值），掌握全排列、N皇后、组合求和等经典回溯问题模板。',
            difficulty: '进阶',
            duration: '2 周',
            status: 'planned',
            tags: ['递归', '回溯', '剪枝', '排列组合'],
            resources: ['回溯法解题框架', 'LeetCode 回溯专题'],
            milestones: ['用统一模板解决 10+ 回溯题目'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-web-frontend-basics',
        label: '前端开发基础',
        summary: '构建用户界面的三大件：HTML/CSS/JS',
        description: '学习 HTML5 语义化标签、CSS3 布局（Flexbox/Grid）、响应式设计、JavaScript 核心语法与 DOM 操作，能独立制作静态页面。',
        difficulty: '基础',
        duration: '4-5 周',
        status: 'current',
        tags: ['HTML', 'CSS', 'JavaScript', '前端'],
        resources: ['MDN Web 文档', 'CSS-Tricks', 'freeCodeCamp'],
        milestones: ['高保真还原一个复杂网页', '完成一个带交互的个人主页'],
        children: [
          {
            id: 'cs-html-css-mastery',
            label: 'HTML 与 CSS 深度应用',
            summary: '从页面结构到精美样式的全面掌控',
            description: '掌握语义化 HTML、CSS 选择器优先级、盒模型、定位机制、Flexbox 弹性布局、Grid 网格布局、CSS 动画与过渡效果。',
            difficulty: '基础',
            duration: '2 周',
            status: 'current',
            tags: ['语义化', 'Flexbox', 'Grid', 'CSS动画'],
            resources: ['Flexbox Froggy 游戏', 'CSS Grid 完全指南'],
            milestones: ['仅用 Flexbox + Grid 还原一个 Dashboard 页面'],
            children: [],
          },
          {
            id: 'js-for-cs-students',
            label: 'JavaScript 核心（面向 CS 学生）',
            summary: '以计算机科学视角学习 JS',
            description: '结合 CS 背景，从执行上下文、作用域链、闭包、原型链、事件循环等底层机制入手，建立对 JS 运行时的完整认知。',
            difficulty: '进阶',
            duration: '2-3 周',
            status: 'planned',
            tags: ['执行上下文', '闭包', '原型链', 'EventLoop'],
            resources: ['《你不知道的 JS》系列', 'JS 引擎工作原理'],
            milestones: ['画出一行代码在 V8 中的完整执行过程'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-backend-development',
        label: '后端开发核心',
        summary: '服务端逻辑、数据库与 API 设计',
        description: '学习服务端编程基础（Node.js 或 Java/Spring Boot）、关系型数据库设计与 SQL、RESTful API 规范及身份认证机制。',
        difficulty: '进阶',
        duration: '5-6 周',
        status: 'planned',
        tags: ['Node.js', 'Spring Boot', 'MySQL', 'API设计'],
        resources: ['《HTTP 权威指南》', 'SQL 必知必会', 'RESTful Web Services'],
        milestones: ['搭建一套完整的后端服务', '设计并提供规范的 RESTful 接口文档'],
        children: [
          {
            id: 'cs-database-design',
            label: '数据库设计与 SQL',
            summary: '关系型数据库建模与查询优化',
            description: '掌握 ER 图建模、三范式规范、多表关联查询、索引原理与优化、事务隔离级别及常见存储引擎对比。',
            difficulty: '进阶',
            duration: '2-3 周',
            status: 'planned',
            tags: ['ER建模', '索引优化', '事务', 'MySQL'],
            resources: ['《SQL 性能调优》', 'EXPLAIN 分析指南'],
            milestones: ['为一个电商系统设计完整的数据库 schema'],
            children: [],
          },
          {
            id: 'cs-api-design-auth',
            label: 'API 设计与认证授权',
            summary: '构建安全可靠的接口体系',
            description: '遵循 RESTful 设计规范（资源命名、状态码、版本控制）、实现 JWT/OAuth2 认证鉴权、接口限流与日志记录。',
            difficulty: '进阶',
            duration: '2 周',
            status: 'planned',
            tags: ['RESTful', 'JWT', 'OAuth2', 'Swagger'],
            resources: ['API 设计最佳实践', 'JWT 安全指南'],
            milestones: ['输出一份完整的 OpenAPI 文档', '实现基于 JWT 的登录认证'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-computer-networks',
        label: '计算机网络',
        summary: '互联网运作的底层协议与通信原理',
        description: '从 OSI 七层模型到 TCP/IP 四层协议族，重点理解 HTTP/HTTPS、DNS、TCP 三次握手四次挥手、IP 寻址及 Socket 编程基础。',
        difficulty: '进阶',
        duration: '3-4 周',
        status: 'planned',
        tags: ['TCP/IP', 'HTTP', 'DNS', 'OSI模型'],
        resources: ['《计算机网络：自顶向下方法》', '网络协议图解'],
        milestones: ['用 Wireshark 抓包分析一次 HTTP 请求', '解释从输入 URL 到页面渲染的全过程'],
        children: [
          {
            id: 'cs-http-deep-dive',
            label: 'HTTP 协议深入',
            summary: 'Web 通信的核心协议详解',
            description: '掌握 HTTP 方法/状态码/首部字段、HTTP/1.1 vs HTTP/2 vs HTTP/3 差异、HTTPS 加密流程、Cookie/Session 及缓存策略。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['HTTPS', 'TLS', '缓存', 'HTTP/2'],
            resources: ['HTTP 权威详解', 'MDN HTTP 参考'],
            milestones: ['总结 HTTP 各版本的演进与改进点'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-operating-systems',
        label: '操作系统基础',
        summary: '管理硬件资源的系统软件核心知识',
        description: '了解进程与线程管理、内存管理（虚拟内存/分页分段）、文件系统、I/O 模型（阻塞/非阻塞/多路复用）及 Linux 常用命令。',
        difficulty: '进阶',
        duration: '3-4 周',
        status: 'planned',
        tags: ['进程', '线程', '内存管理', 'Linux'],
        resources: ['《操作系统概念》', 'Linux 命令行速查', '鸟哥的 Linux 私房菜'],
        milestones: ['在 Linux 上完成环境配置与服务部署', '解释进程与线程的本质区别'],
        children: [
          {
            id: 'cs-linux-practice',
            label: 'Linux 操作实践',
            summary: '服务器环境的必备技能',
            description: '熟悉 Shell 常用命令（ls/grep/find/sed/awk）、文件权限管理、进程管理、SSH 远程连接、Vim 编辑器及 Shell 脚本编写。',
            difficulty: '基础',
            duration: '2 周',
            status: 'planned',
            tags: ['Bash', 'Shell脚本', 'Vim', 'SSH'],
            resources: ['Linux 命令大全', 'Shell 编程实战'],
            milestones: ['编写一个自动化部署脚本'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-git-version-control',
        label: 'Git 版本控制与协作',
        summary: '代码管理的标准工具与团队协作流程',
        description: '掌握 Git 基本操作（add/commit/push/pull/branch/merge/rebase）、分支管理策略（Git Flow）、冲突解决及 GitHub/GitLab 协作。',
        difficulty: '基础',
        duration: '1-2 周',
        status: 'completed',
        tags: ['Git', 'GitHub', '版本控制', '协作开发'],
        resources: ['Pro Git 书籍', 'Git 可视化学习网站'],
        milestones: ['熟练使用 Git 管理个人项目', '参与开源项目提交 PR'],
        children: [],
      },
      {
        id: 'cs-software-engineering',
        label: '软件工程方法',
        summary: '规范化软件开发流程与工程素养',
        description: '了解敏捷开发（Scrum/Kanban）、需求分析与 UML 建模、代码评审规范、CI/CD 自动化流水线及技术文档撰写能力。',
        difficulty: '进阶',
        duration: '2-3 周',
        status: 'planned',
        tags: ['敏捷开发', 'UML', '代码审查', 'CI/CD'],
        resources: ['《代码整洁之道》', '敏捷开发实战', 'UML 精要'],
        milestones: ['参与一次完整的代码 Review 流程', '撰写一份高质量的技术设计文档'],
        children: [
          {
            id: 'cs-code-quality',
            label: '代码质量与规范',
            summary: '写出可维护可扩展的高质量代码',
            description: '学习 SOLID 原则、DRY/KISS/YAGNI 原则、命名规范、注释规范、ESLint/Prettier/Checkstyle 工具配置与团队编码规范制定。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['SOLID', 'Lint', '代码风格', '重构'],
            resources: ['《重构》 Martin Fowler', '团队编码规范模板'],
           里程碑: ['对一段遗留代码进行重构优化'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-data-analysis-intro',
        label: '数据分析基础',
        summary: '用数据驱动决策的能力培养',
        description: '使用 Python（NumPy/Pandas/Matplotlib）或 Excel 进行数据清洗、统计分析、可视化图表绘制及基础的数据解读能力。',
        difficulty: '进阶',
        duration: '3-4 周',
        status: 'planned',
        tags: ['Pandas', 'NumPy', '数据可视化', 'Excel'],
        resources: ['《利用 Python 进行数据分析》', 'DataCamp 课程'],
        milestones: ['对一个真实数据集进行完整的分析流程', '产出一份数据分析报告'],
        children: [],
      },
      {
        id: 'cs-devops-cloud-basics',
        label: 'DevOps 与云计算入门',
        summary: '现代软件交付的基础设施知识',
        description: '了解 Docker 容器化、Kubernetes 基础概念、云平台服务（AWS/阿里云/腾讯云）的使用及 Serverless/FaaS 新形态。',
        difficulty: '进阶',
        duration: '2-3 周',
        status: 'planned',
        tags: ['Docker', 'Kubernetes', '云服务', 'Serverless'],
        resources: ['Docker 从入门到实践', 'Kubernetes 官方概念'],
        milestones: ['将一个应用 Docker 化并推送到镜像仓库'],
        children: [
          {
            id: 'cs-docker-containerization',
            label: 'Docker 容器化实践',
            summary: '打包、分发与运行跨平台应用',
            description: '掌握 Dockerfile 编写、镜像分层原理、docker-compose 多容器编排、数据卷挂载及网络配置。',
            difficulty: '进阶',
            duration: '1-2 周',
            status: 'planned',
            tags: ['Dockerfile', 'Compose', '镜像'],
            resources: ['Docker 官方教程', 'Docker 最佳实践'],
            milestones: ['为前后端项目编写完整的 Docker 配置'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-security-awareness',
        label: '信息安全基础',
        summary: '建立安全意识与常见攻击防御',
        description: '了解 OWASP Top 10 安全漏洞（注入/XSS/CSRF）、密码学基础（对称加密/哈希/数字证书）、网络安全防护原则与合规意识。',
        difficulty: '进阶',
        duration: '2 周',
        status: 'planned',
        tags: ['XSS', 'SQL注入', '密码学', '安全合规'],
        resources: ['OWASP 官网', '《白帽子讲 Web 安全》'],
        milestones: ['对自己的项目进行一次安全审计'],
        children: [],
      },
      {
        id: 'cs-fullstack-project',
        label: '全栈综合项目',
        summary: '整合所学知识的综合性实战作品',
        description: '独立完成一个涵盖前端界面、后端 API、数据库设计、部署上线及文档编写的全栈应用项目，如博客系统、电商平台或在线协作工具。',
        difficulty: '高级',
        duration: '4-6 周',
        status: 'planned',
        tags: ['全栈', '项目实战', '作品集', '部署'],
        resources: ['全栈项目案例集', 'GitHub Pages/Vercel 部署指南'],
        milestones: ['完成一个可公开访问的全栈应用', '编写完整的项目 README 和 API 文档'],
        children: [
          {
            id: 'cs-blog-system-project',
            label: '个人博客/内容管理系统',
            summary: '经典全栈练手项目的现代实现',
            description: '实现用户注册登录（JWT 认证）、文章 CRUD、Markdown 编辑器、标签分类、评论功能、搜索及管理员后台。',
            difficulty: '进阶',
            duration: '2-3 周',
            status: 'planned',
            tags: ['CMS', 'Markdown', '评论系统', '后台管理'],
            resources: ['博客系统架构设计参考', '开源 CMS 源码学习'],
            milestones: ['功能完整且 UI 美观的博客系统'],
            children: [],
          },
          {
            id: 'cs-ecommerce-mini',
            label: '迷你电商平台',
            summary: '模拟真实业务逻辑的综合挑战',
            description: '实现商品浏览与搜索、购物车、订单流程（下单→支付→发货→确认收货）、库存管理与简单的推荐模块。',
            difficulty: '高级',
            duration: '3-4 周',
            status: 'planned',
            tags: ['购物车', '订单系统', '支付对接', '库存管理'],
            resources: ['电商系统设计模式', '订单状态机设计'],
            milestones: ['完成完整的购物下单闭环流程'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-ai-ml-overview',
        label: 'AI 与机器学习概览',
        summary: '了解人工智能时代的技术变革方向',
        description: '建立对机器学习、深度学习、大语言模型（LLM）、Prompt Engineering 的基础认识，探索 AI 在软件开发中的辅助角色。',
        difficulty: '进阶',
        duration: '2-3 周',
        status: 'planned',
        tags: ['AI', 'LLM', '机器学习', 'Prompt Engineering'],
        resources: ['吴恩达 ML 课程', 'Prompt Engineering 指南', 'Hugging Face 教程'],
        milestones: ['调用一个大模型 API 实现智能对话功能', '形成对 AI 辅助开发的系统性认知'],
        children: [],
      },
      {
        id: 'cs-career-preparation',
        label: '求职准备与职业发展',
        summary: '从技能到offer的最后一公里',
        description: '完善简历与 GitHub 作品集、准备技术面试（算法题 + 项目深挖 + 系统设计）、模拟面试练习及 offer 选择与薪资谈判技巧。',
        difficulty: '基础',
        duration: '持续',
        status: 'planned',
        tags: ['简历', '面试', 'Offer', '职业规划'],
        resources: ['程序员面试金典', 'LeetCode 刷题计划', '牛客网面试经验'],
        milestones: ['简历投递并获得面试机会', '通过至少一轮技术面试'],
        children: [
          {
            id: 'cs-resume-portfolio',
            label: '简历与作品集打造',
            summary: '展示能力的专业材料准备',
            description: '撰写技术简历（突出项目成果而非职责罗列）、维护 GitHub 提交记录与技术博客、整理项目 Demo 演示链接。',
            difficulty: '基础',
            duration: '1-2 周',
            status: 'planned',
            tags: ['简历写作', 'GitHub', '技术博客', '作品集'],
            resources: ['优秀简历模板', 'GitHub Profile 优化指南'],
            milestones: ['产出中英双语简历 + 个人技术站 + GitHub 绿墙'],
            children: [],
          },
          {
            id: 'cs-interview-prep',
            label: '技术面试准备',
            summary: '算法 + 项目 + 系统设计全方位备战',
            description: '按公司层级分类准备：LeetCode Hot 150 刷题、项目 STAR 法则讲述、常见系统设计方案（短网址/消息队列/分布式缓存）。',
            difficulty: '进阶',
            duration: '3-4 周',
            status: 'planned',
            tags: ['刷题', 'STAR法则', '系统设计', '行为面试'],
            resources: ['《剑指 Offer》', 'System Design Primer', '面试经验汇总'],
            milestones: ['完成 200+ 道算法题', '能流畅讲解 3 个核心项目'],
            children: [],
          },
        ],
      },
      {
        id: 'cs-lifelong-learning',
        label: '终身学习习惯养成',
        summary: '保持技术竞争力的可持续成长路径',
        description: '建立技术阅读习惯、关注社区动态（Hacker News / Reddit / 掘金）、参与技术分享与开源贡献、定期复盘与规划迭代。',
        difficulty: '基础',
        duration: '持续',
        status: 'planned',
        tags: ['技术阅读', '开源贡献', '社区', '成长规划'],
        resources: ['优质技术 RSS 源列表', '开源贡献新手指南'],
        milestones: ['每月至少读一本技术书/文章合集', '年度技术成长复盘与下年规划'],
        children: [],
      },
    ],
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
    resetTreeViewport()
  },
  { immediate: true },
)

// 切换选中节点时，重置 AI 状态回到信息标签页
watch(activeKnowledge, () => {
  cancelStream()
  panelTab.value = 'info'
  aiStreamContent.value = ''
  aiStreamError.value = ''
  currentStreamType.value = null
})

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

function closeKnowledgePanel(): void {
  cancelStream()
  activeKnowledge.value = null
}

function resetTreeViewport(): void {
  treeOffset.value = { x: 36, y: 84 }
}

function isInteractiveElement(target: EventTarget | null): boolean {
  return target instanceof HTMLElement
    && Boolean(target.closest('button, a, input, textarea, select, .tree-node__label, .tree-node__toggle'))
}

function startTreeDrag(event: PointerEvent): void {
  if (isInteractiveElement(event.target)) return

  dragPointerId.value = event.pointerId
  isDraggingTree.value = true
  dragStartPoint.value = { x: event.clientX, y: event.clientY }
  dragStartOffset.value = { ...treeOffset.value }
  treeViewportRef.value?.setPointerCapture(event.pointerId)
}

function handleTreeDrag(event: PointerEvent): void {
  if (!isDraggingTree.value || dragPointerId.value !== event.pointerId) return

  const deltaX = event.clientX - dragStartPoint.value.x
  const deltaY = event.clientY - dragStartPoint.value.y
  treeOffset.value = {
    x: dragStartOffset.value.x + deltaX,
    y: dragStartOffset.value.y + deltaY,
  }
}

function endTreeDrag(event?: PointerEvent): void {
  if (event && dragPointerId.value !== null && dragPointerId.value === event.pointerId) {
    treeViewportRef.value?.releasePointerCapture(event.pointerId)
  }
  isDraggingTree.value = false
  dragPointerId.value = null
}

// ===== AI 流式交互 =====

/** 取消当前正在进行的流式请求 */
function cancelStream(): void {
  if (currentAbortController.value) {
    currentAbortController.value.abort()
    currentAbortController.value = null
  }
  aiStreamLoading.value = false
}

/** 获取当前选中岗位的 jobId（从 roles 中的 id 映射） */
function getCurrentJobId(): string {
  // 使用选中的 role id 作为 jobId，用于匹配 Mock 数据
  return selectedRole.value?.id || 'java-learning-path'
}

/** 发起流式请求 */
async function startStream(type: 'analyze' | 'explain'): Promise<void> {
  if (!activeKnowledge.value) return

  // 取消之前的请求
  cancelStream()

  // 切换标签页并重置状态
  panelTab.value = type
  aiStreamContent.value = ''
  aiStreamError.value = ''
  aiStreamLoading.value = true
  currentStreamType.value = type

  const abortController = new AbortController()
  currentAbortController.value = abortController

  const streamFn = type === 'analyze' ? streamAnalyzeKnowledge : streamExplainKnowledge

  try {
    await streamFn({
      currentNode: activeKnowledge.value.id,
      jobId: getCurrentJobId(),
      signal: abortController.signal,
      onChunk: (chunk: string) => {
        aiStreamContent.value += chunk
        // 滚动到底部
        nextTick(() => {
          const panel = document.querySelector('.ai-stream-section')
          if (panel) panel.scrollTop = panel.scrollHeight
        })
      },
      onDone: () => {
        aiStreamLoading.value = false
        currentAbortController.value = null
      },
      onError: (error: string) => {
        aiStreamError.value = error
        aiStreamLoading.value = false
        currentAbortController.value = null
      },
    })
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      // 用户主动取消，不显示错误
      return
    }
    aiStreamError.value = error instanceof Error ? error.message : '请求失败，请稍后重试'
    aiStreamLoading.value = false
    currentAbortController.value = null
  }
}

/** 点击"岗位影响"标签 */
function handleAnalyzeClick(): void {
  if (aiStreamLoading.value && currentStreamType.value === 'analyze') return
  startStream('analyze')
}

/** 点击"知识精讲"标签 */
function handleExplainClick(): void {
  if (aiStreamLoading.value && currentStreamType.value === 'explain') return
  startStream('explain')
}

/** 重试流式请求 */
function retryStream(): void {
  if (currentStreamType.value) {
    startStream(currentStreamType.value)
  }
}

/** 简易 Markdown 渲染（支持代码块、粗体、换行等基本格式） */
function renderMarkdown(text: string): string {
  if (!text) return ''
  let html = text
  // 转义 HTML
  html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  // 代码块 ```
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="lang-$1">$2</code></pre>')
  // 行内代码 `
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  // 粗体 **
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // 斜体 *
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  // 标题 ###、##、#
  html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>')
  // 无序列表 - 或 *
  html = html.replace(/^[-*] (.+)$/gm, '<li>$1</li>')
  // 换行
  html = html.replace(/\n/g, '<br/>')
  // 清理连续 <li>
  html = html.replace(/(<li>[\s\S]*?<\/li>)/g, (match) => match)
  return html
}
</script>

<style scoped lang="scss">
.job-knowledge-page {
  min-height: 100%;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 24%),
    linear-gradient(180deg, #f7f8fb 0%, #eef2f7 100%);
}

.list-shell {
  max-width: 1060px;
  margin: 0 auto;
  padding: 18px 0 40px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  height: 72px;
  padding: 0 22px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 22px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
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
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(255, 255, 255, 0.78);
  color: #334155;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-chip.active {
  color: #1d4ed8;
  border-color: rgba(37, 99, 235, 0.3);
  background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
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
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
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
  min-height: 100%;
  padding: 16px 18px 24px;
}

.detail-header {
  z-index: 40;
  display: grid;
  grid-template-columns: 48px 1fr auto;
  align-items: center;
  gap: 16px;
  min-height: 84px;
  padding: 12px 18px;
  margin-bottom: 18px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 232, 240, 0.92);
  box-shadow:
    0 10px 24px rgba(15, 23, 42, 0.04),
    0 2px 10px rgba(15, 23, 42, 0.04);
}

.detail-title p {
  margin: 0 0 6px;
  color: #0f766e;
  font-size: 13px;
  font-weight: 700;
  text-align: center;
}

.detail-header h1 {
  margin: 0;
  text-align: center;
  color: #0f172a;
  font-size: 22px;
  font-weight: 800;
}

.back-btn,
.icon-btn,
.panel-close {
  width: 48px;
  height: 48px;
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.96);
  color: #2563eb;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.back-btn:hover,
.icon-btn:hover,
.panel-close:hover {
  transform: translateY(-1px);
  border-color: rgba(191, 219, 254, 0.95);
  box-shadow: 0 12px 22px rgba(37, 99, 235, 0.12);
}

.back-btn {
  font-size: 20px;
}

.detail-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-overview {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 18px 0 20px;
}

.overview-card {
  padding: 18px 20px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
}

.overview-card span {
  display: block;
  margin-bottom: 10px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.overview-card strong {
  display: block;
  color: #0f172a;
  font-size: 18px;
}

.overview-card p {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.75;
  font-size: 14px;
}

.overview-card--primary {
  background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
  border-color: rgba(59, 130, 246, 0.16);
}

.detail-body {
  position: relative;
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 160px);
}

.tree-stage {
  flex: 1;
  min-width: 0;
  display: grid;
  gap: 14px;
}

.tree-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
}

.tree-toolbar__hint {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #475569;
  font-size: 14px;
}

.tree-toolbar__dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #3b82f6;
  box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.14);
}

.tree-toolbar__action {
  min-height: 38px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: #fff;
  color: #1d4ed8;
  font-weight: 700;
  cursor: pointer;
}

.tree-viewport {
  position: relative;
  min-height: calc(100vh - 208px);
  overflow: hidden;
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(248, 250, 252, 0.92)),
    linear-gradient(90deg, rgba(148, 163, 184, 0.08) 1px, transparent 1px),
    linear-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px);
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: 0 24px 50px rgba(15, 23, 42, 0.08);
  cursor: grab;
  user-select: none;
}

.tree-viewport.is-dragging {
  cursor: grabbing;
}

.tree-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(90deg, rgba(148, 163, 184, 0.08) 1px, transparent 1px),
    linear-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px);
  background-size: 28px 28px;
  pointer-events: none;
}

.tree-scroll {
  position: relative;
  min-width: max-content;
  min-height: 100%;
  padding: 54px 72px 72px;
  transform-origin: top left;
  transition: transform 0.08s linear;
  will-change: transform;
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
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.14);
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

.knowledge-panel__tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 18px;
}

.panel-tab {
  flex: 1;
  padding: 10px 8px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(255, 255, 255, 0.78);
  color: #334155;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.panel-tab:hover:not(:disabled) {
  border-color: rgba(59, 130, 246, 0.3);
  color: #1d4ed8;
}

.panel-tab.active {
  color: #1d4ed8;
  border-color: rgba(37, 99, 235, 0.3);
  background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
  font-weight: 700;
}

.panel-tab:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ai-stream-section {
  min-height: 200px;
  position: relative;
}

.ai-stream-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #64748b;
  font-size: 14px;
}

.ai-stream-loading__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3b82f6;
  animation: ai-pulse 1.2s ease-in-out infinite;
}

@keyframes ai-pulse {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

.ai-stream-content {
  color: #374151;
  font-size: 14px;
  line-height: 1.85;
  word-break: break-word;
}

.ai-stream-content :deep(h2) {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  margin: 16px 0 8px;
}

.ai-stream-content :deep(h3) {
  font-size: 15px;
  font-weight: 700;
  color: #1f2937;
  margin: 14px 0 6px;
}

.ai-stream-content :deep(h4) {
  font-size: 14px;
  font-weight: 700;
  color: #374151;
  margin: 12px 0 4px;
}

.ai-stream-content :deep(strong) {
  color: #1f2937;
  font-weight: 700;
}

.ai-stream-content :deep(code) {
  padding: 2px 6px;
  border-radius: 4px;
  background: #f1f5f9;
  font-size: 13px;
  color: #dc2626;
}

.ai-stream-content :deep(pre) {
  margin: 10px 0;
  padding: 12px 14px;
  border-radius: 10px;
  background: #1e293b;
  overflow-x: auto;
}

.ai-stream-content :deep(pre code) {
  background: transparent;
  color: #e2e8f0;
  padding: 0;
  font-size: 13px;
}

.ai-stream-content :deep(li) {
  margin: 4px 0;
  padding-left: 4px;
}

.ai-stream-cursor {
  display: inline-flex;
  align-items: center;
  margin-top: 4px;
}

.ai-stream-cursor__bar {
  display: inline-block;
  width: 2px;
  height: 16px;
  background: #3b82f6;
  animation: cursor-blink 0.8s ease-in-out infinite;
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.ai-stream-placeholder {
  padding: 32px 16px;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}

.ai-stream-error {
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.ai-stream-error p {
  margin: 0 0 8px;
  color: #dc2626;
  font-size: 13px;
  line-height: 1.6;
}

.retry-btn {
  padding: 6px 14px;
  border-radius: 8px;
  border: 1px solid #fca5a5;
  background: #fff;
  color: #dc2626;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background: #fef2f2;
  border-color: #f87171;
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
  .detail-overview {
    grid-template-columns: 1fr;
  }

  .detail-body {
    flex-direction: column;
  }

  .tree-viewport {
    min-height: 560px;
  }

  .tree-scroll {
    padding: 40px 24px 56px;
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
    min-height: 74px;
    padding: 10px 12px;
  }

  .detail-header h1 {
    font-size: 16px;
  }

  .tree-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .tree-toolbar__action {
    width: 100%;
  }
}
</style>
