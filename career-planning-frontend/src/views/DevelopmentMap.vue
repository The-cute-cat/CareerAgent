<template>
  <div class="career-path-page">
    <header class="toolbar">
      <div class="toolbar-left">
        <el-button :icon="ArrowLeft" circle class="back-btn" @click="handleBack" />
        <div class="title-group">
          <h1 class="page-title">{{ pageTitle }}</h1>
          <p class="page-subtitle">支持垂直晋升图谱、横向换岗图谱、节点详情、路径技能差距分析与图谱缩放拖拽</p>
        </div>
      </div>

      <div class="toolbar-right">
        <el-segmented
          v-model="activeGraphType"
          :options="graphTypeOptions"
          class="view-switcher"
        />
        <el-button :icon="RefreshRight" class="reset-btn" @click="fitGraph">重置视图</el-button>
      </div>
    </header>

    <main class="page-body">
      <section class="graph-panel" :class="{ 'graph-panel--full': !activeNode && !activeEdge }">
        <div class="graph-panel-header">
          <div class="panel-meta">
            <div class="meta-badge">{{ activeGraphType === 'promotion' ? 'F-13 垂直晋升图谱' : 'F-14 横向换岗图谱' }}</div>
            <h2 class="panel-title">{{ activeGraphType === 'promotion' ? '岗位晋升流程图' : '岗位换岗关系图' }}</h2>
            <p class="panel-desc">
              {{ activeGraphType === 'promotion'
                ? '从初级工程师到架构/管理角色，展示岗位进阶层级与关键成长阶段。'
                : '展示至少 5 个相关岗位及其迁移关系，点击路径可查看补充技能。' }}
            </p>
          </div>

          <div class="panel-kpis">
            <div class="kpi-card">
              <div class="kpi-label">岗位数</div>
              <div class="kpi-value">{{ currentGraphData.nodes.length }}</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">路径数</div>
              <div class="kpi-value">{{ currentGraphData.edges.length }}</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">当前选中</div>
              <div class="kpi-value kpi-value--small">{{ currentSelectionTitle }}</div>
            </div>
          </div>
        </div>

        <div ref="containerRef" class="graph-container"></div>

        <div class="graph-guide">
          <div class="guide-title">交互说明</div>
          <div class="guide-item">单击节点：查看岗位详情</div>
          <div class="guide-item">单击路径：查看补充技能</div>
          <div class="guide-item">拖拽画布 / Ctrl+滚轮：移动与缩放</div>
        </div>

        <div class="graph-legend">
          <div class="legend-title">图例说明</div>
          <div class="legend-items">
            <div class="legend-item">
              <span class="legend-dot current"></span>
              <span class="legend-text">当前岗位</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot promote"></span>
              <span class="legend-text">晋升岗位</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot transfer"></span>
              <span class="legend-text">换岗岗位</span>
            </div>
            <div class="legend-item">
              <span class="legend-line transfer"></span>
              <span class="legend-text">可迁移路径</span>
            </div>
          </div>
        </div>

        <div class="zoom-controls">
          <el-button :icon="Plus" circle size="small" @click="zoomIn" />
          <el-button :icon="Minus" circle size="small" @click="zoomOut" />
        </div>
      </section>

      <transition name="slide-panel">
        <aside v-if="activeNode || activeEdge" class="detail-panel">
          <div class="detail-header">
            <div>
              <div class="header-chip">F-15 图谱交互</div>
              <h2 class="detail-title">{{ activeNode ? activeNode.name : edgePanelTitle }}</h2>
              <p class="detail-summary">{{ activeNode ? activeNode.summary : edgePanelSummary }}</p>
            </div>
            <el-button text :icon="Close" class="close-btn" @click="closeDetail" />
          </div>

          <el-scrollbar class="detail-scrollbar">
            <div class="detail-content">
              <template v-if="activeNode">
                <div class="overview-card overview-card--node">
                  <div class="overview-top">
                    <div class="node-badge" :class="activeNode.category">{{ activeNode.categoryLabel }}</div>
                    <div class="level-pill">L{{ activeNode.level }}</div>
                  </div>
                  <p class="overview-text">{{ activeNode.description }}</p>
                  <div class="tags-section">
                    <el-tag v-for="tag in activeNode.tags" :key="tag" round effect="light" class="skill-tag">
                      {{ tag }}
                    </el-tag>
                  </div>
                </div>

                <div class="info-grid info-grid--2">
                  <div class="info-card">
                    <div class="card-header">
                      <el-icon class="card-icon"><Trophy /></el-icon>
                      <span class="card-title">核心能力</span>
                    </div>
                    <ul class="feature-list">
                      <li v-for="item in activeNode.skills" :key="item" class="feature-item">
                        <el-icon class="feature-icon"><Check /></el-icon>
                        <span>{{ item }}</span>
                      </li>
                    </ul>
                  </div>

                  <div class="info-card">
                    <div class="card-header">
                      <el-icon class="card-icon"><Aim /></el-icon>
                      <span class="card-title">建议行动</span>
                    </div>
                    <ul class="feature-list action-list">
                      <li v-for="item in activeNode.actions" :key="item" class="feature-item">
                        <el-icon class="feature-icon"><ArrowRight /></el-icon>
                        <span>{{ item }}</span>
                      </li>
                    </ul>
                  </div>
                </div>

                <div class="info-card">
                  <div class="card-header">
                    <el-icon class="card-icon"><Connection /></el-icon>
                    <span class="card-title">可选路径</span>
                  </div>
                  <div class="path-list">
                    <button
                      v-for="edge in relatedEdges"
                      :key="edge.source + edge.target"
                      class="path-chip"
                      @click="selectEdge(edge)"
                    >
                      {{ getNodeName(edge.source) }} → {{ getNodeName(edge.target) }}
                    </button>
                  </div>
                </div>

                <div class="ai-assistant-card">
                  <div class="ai-header">
                    <div class="ai-avatar">
                      <el-icon><ChatDotRound /></el-icon>
                    </div>
                    <div class="ai-info">
                      <div class="ai-name">职业规划 AI 助手</div>
                      <div class="ai-status">
                        <span class="status-dot"></span>
                        在线分析中
                      </div>
                    </div>
                  </div>

                  <div class="ai-intro">我会围绕当前岗位，给出能力差距、项目补强方向和近期行动建议。</div>

                  <div class="ai-questions">
                    <div class="section-label">推荐提问</div>
                    <div class="question-chips">
                      <button
                        v-for="question in aiQuestions"
                        :key="question"
                        class="question-chip"
                        @click="handleQuestionClick(question)"
                      >
                        {{ question }}
                      </button>
                    </div>
                  </div>

                  <div class="ai-response">
                    <div class="response-header">
                      <el-icon><MagicStick /></el-icon>
                      <span>AI 建议</span>
                    </div>
                    <div class="response-content">{{ aiAnswer }}</div>
                  </div>
                </div>
              </template>

              <template v-else-if="activeEdge">
                <div class="overview-card overview-card--edge">
                  <div class="edge-route">
                    <span>{{ getNodeName(activeEdge.source) }}</span>
                    <el-icon><Right /></el-icon>
                    <span>{{ getNodeName(activeEdge.target) }}</span>
                  </div>
                  <p class="overview-text">{{ activeEdge.description }}</p>
                  <div class="edge-badges">
                    <span class="edge-badge">{{ activeEdge.type === 'promotion' ? '晋升路径' : '换岗路径' }}</span>
                    <span class="edge-badge edge-badge--light">{{ activeEdge.label }}</span>
                  </div>
                </div>

                <div class="info-card">
                  <div class="card-header">
                    <el-icon class="card-icon"><Compass /></el-icon>
                    <span class="card-title">所需补充技能</span>
                  </div>
                  <ul class="feature-list">
                    <li v-for="item in activeEdge.requiredSkills" :key="item" class="feature-item">
                      <el-icon class="feature-icon"><Check /></el-icon>
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                </div>

                <div class="info-grid info-grid--2">
                  <div class="info-card">
                    <div class="card-header">
                      <el-icon class="card-icon"><Document /></el-icon>
                      <span class="card-title">建议项目</span>
                    </div>
                    <ul class="feature-list">
                      <li v-for="item in activeEdge.projectSuggestions" :key="item" class="feature-item">
                        <el-icon class="feature-icon"><ArrowRight /></el-icon>
                        <span>{{ item }}</span>
                      </li>
                    </ul>
                  </div>

                  <div class="info-card">
                    <div class="card-header">
                      <el-icon class="card-icon"><Flag /></el-icon>
                      <span class="card-title">迁移提醒</span>
                    </div>
                    <ul class="feature-list">
                      <li v-for="item in activeEdge.risks" :key="item" class="feature-item">
                        <el-icon class="feature-icon"><Warning /></el-icon>
                        <span>{{ item }}</span>
                      </li>
                    </ul>
                  </div>
                </div>

                <div class="ai-assistant-card">
                  <div class="ai-header">
                    <div class="ai-avatar ai-avatar--purple">
                      <el-icon><MagicStick /></el-icon>
                    </div>
                    <div class="ai-info">
                      <div class="ai-name">路径差距分析</div>
                      <div class="ai-status">
                        <span class="status-dot"></span>
                        已生成建议
                      </div>
                    </div>
                  </div>
                  <div class="ai-response ai-response--plain">
                    <div class="response-content">{{ edgeAdvice }}</div>
                  </div>
                </div>
              </template>
            </div>
          </el-scrollbar>
        </aside>
      </transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Graph } from '@antv/x6'
import {
  Aim,
  ArrowLeft,
  ArrowRight,
  ChatDotRound,
  Check,
  Close,
  Compass,
  Connection,
  Document,
  Flag,
  MagicStick,
  Minus,
  Plus,
  RefreshRight,
  Right,
  Trophy,
  Warning,
} from '@element-plus/icons-vue'

interface CareerNode {
  id: string
  name: string
  level: number
  category: 'current' | 'promotion' | 'transfer'
  categoryLabel: string
  x: number
  y: number
  summary: string
  description: string
  tags: string[]
  skills: string[]
  actions: string[]
}

interface CareerEdge {
  source: string
  target: string
  type: 'promotion' | 'transfer'
  label: string
  description: string
  requiredSkills: string[]
  projectSuggestions: string[]
  risks: string[]
}

const props = withDefaults(
  defineProps<{
    pageTitle?: string
  }>(),
  {
    pageTitle: 'Java 研发工程师职业发展路径图谱',
  },
)

const emit = defineEmits<{
  back: []
}>()

const containerRef = ref<HTMLDivElement>()
const graphRef = ref<Graph>()
const activeGraphType = ref<'promotion' | 'transfer'>('promotion')
const activeNode = ref<CareerNode | null>(null)
const activeEdge = ref<CareerEdge | null>(null)

const graphTypeOptions = [
  { label: '岗位晋升路径', value: 'promotion' },
  { label: '换岗路径', value: 'transfer' },
]

const promotionData = {
  nodes: [
    {
      id: 'java-junior',
      name: '初级 Java 工程师',
      level: 1,
      category: 'current',
      categoryLabel: '当前岗位',
      x: 120,
      y: 260,
      summary: '负责接口开发、Bug 修复、基础模块实现与联调。',
      description: '职业起点岗位，重点建立 Java 语言基础、Spring 生态、数据库与工程化协作能力。',
      tags: ['Java 基础', 'Spring Boot', 'MySQL'],
      skills: ['Java 基础与集合', 'Spring Boot / MVC', 'SQL 编写与索引基础', 'Git 协作'],
      actions: ['完成 2 个业务模块', '熟悉接口规范', '沉淀调试排错方法'],
    },
    {
      id: 'java-middle',
      name: '中级 Java 工程师',
      level: 2,
      category: 'promotion',
      categoryLabel: '晋升岗位',
      x: 430,
      y: 170,
      summary: '可独立承担模块设计、开发、联调与质量保障。',
      description: '从执行开发转向模块 owner，需要更强的问题拆解、交付质量和性能意识。',
      tags: ['模块设计', '缓存', '事务'],
      skills: ['模块边界设计', '事务与并发控制', '缓存设计', '日志排查'],
      actions: ['主导核心模块', '建立性能基线', '输出设计文档'],
    },
    {
      id: 'java-senior',
      name: '高级 Java 工程师',
      level: 3,
      category: 'promotion',
      categoryLabel: '晋升岗位',
      x: 760,
      y: 120,
      summary: '承担复杂系统设计、稳定性治理和跨模块协同。',
      description: '需要对系统全链路、服务治理、代码评审和技术方案有更强掌控力。',
      tags: ['系统设计', '微服务', '稳定性'],
      skills: ['分布式系统设计', '服务治理', '代码评审', '容量与压测'],
      actions: ['参与架构评审', '推动稳定性治理', '带教初中级工程师'],
    },
    {
      id: 'tech-lead',
      name: '技术负责人 / TL',
      level: 4,
      category: 'promotion',
      categoryLabel: '晋升岗位',
      x: 1090,
      y: 210,
      summary: '负责技术方案评估、研发节奏把控与团队协作推进。',
      description: '开始从个人贡献者向团队核心负责人升级，需要平衡交付、质量与协作。',
      tags: ['方案设计', '项目推进', '团队协作'],
      skills: ['系统方案设计', '风险管理', '项目推进', '跨团队沟通'],
      actions: ['组织技术评审', '建设研发规范', '培养骨干同学'],
    },
    {
      id: 'architect',
      name: '系统架构师',
      level: 5,
      category: 'promotion',
      categoryLabel: '晋升岗位',
      x: 1420,
      y: 320,
      summary: '统筹系统架构演进、技术选型与平台治理。',
      description: '更关注平台化、可扩展性和长期技术演进，不再局限于单一业务模块交付。',
      tags: ['架构治理', '平台化', '高并发'],
      skills: ['高并发架构', '平台抽象', '容量规划', '技术战略'],
      actions: ['设计统一技术底座', '制定架构原则', '支撑关键业务升级'],
    },
  ] as CareerNode[],
  edges: [
    {
      source: 'java-junior',
      target: 'java-middle',
      type: 'promotion',
      label: '1-2 年',
      description: '从执行型开发转向独立负责模块，需要补强设计、排障与质量意识。',
      requiredSkills: ['模块拆分与接口抽象', '缓存与事务场景', '日志分析与问题定位'],
      projectSuggestions: ['独立负责一个业务模块', '完成一次性能优化或慢 SQL 治理'],
      risks: ['只会 CRUD，缺乏设计沉淀', '对线上问题处理经验不足'],
    },
    {
      source: 'java-middle',
      target: 'java-senior',
      type: 'promotion',
      label: '2-3 年',
      description: '需要从模块视角走向系统视角，重点突破稳定性、复杂业务与服务治理。',
      requiredSkills: ['分布式系统设计', '服务治理与限流熔断', '压测与容量评估'],
      projectSuggestions: ['参与微服务改造', '负责链路治理或稳定性专项'],
      risks: ['方案深度不够', '复杂问题排查依赖他人'],
    },
    {
      source: 'java-senior',
      target: 'tech-lead',
      type: 'promotion',
      label: '业务 + 管理',
      description: '除了技术能力，还需要具备任务拆解、团队协作与交付把控能力。',
      requiredSkills: ['技术方案评审', '风险识别与节奏推进', '带教与协作沟通'],
      projectSuggestions: ['主导一次跨团队项目', '带领 2-3 人完成需求交付'],
      risks: ['只关注编码，不关注推进', '缺乏向上同步能力'],
    },
    {
      source: 'tech-lead',
      target: 'architect',
      type: 'promotion',
      label: '架构演进',
      description: '需要从团队交付负责人进一步升级为技术体系设计者与架构治理者。',
      requiredSkills: ['平台化抽象能力', '高并发架构设计', '技术路线规划'],
      projectSuggestions: ['建设通用中台能力', '主导核心架构升级项目'],
      risks: ['停留在项目级思维', '缺少全局技术视角'],
    },
  ] as CareerEdge[],
}

const transferData = {
  nodes: [
    {
      id: 'java-base',
      name: 'Java 开发工程师',
      level: 1,
      category: 'current',
      categoryLabel: '当前岗位',
      x: 170,
      y: 260,
      summary: '以后端工程能力为基础，可横向迁移到平台、数据、AI、测试等岗位。',
      description: '换岗不是推翻原有积累，而是围绕已有工程能力，延展新的岗位能力栈。',
      tags: ['工程基础', '接口开发', '数据库'],
      skills: ['编码调试', '服务开发', '数据库基础', '协作交付'],
      actions: ['盘点可迁移能力', '定位目标岗位差距', '补齐关键项目经历'],
    },
    {
      id: 'platform-engineer',
      name: '平台工程师',
      level: 2,
      category: 'transfer',
      categoryLabel: '换岗岗位',
      x: 520,
      y: 90,
      summary: '偏基础设施、平台能力建设与研发效能提升。',
      description: '适合对工程效率、中间件与服务治理更感兴趣的开发者。',
      tags: ['DevOps', '平台化', '监控'],
      skills: ['CI/CD', '容器化', '可观测体系', '服务治理'],
      actions: ['补齐 Docker/K8s', '建设脚手架工具', '沉淀监控告警能力'],
    },
    {
      id: 'data-engineer',
      name: '数据开发工程师',
      level: 2,
      category: 'transfer',
      categoryLabel: '换岗岗位',
      x: 610,
      y: 260,
      summary: '偏 ETL、数仓建模、数据链路与数据服务建设。',
      description: '适合对 SQL、数据治理、分析链路更有兴趣的同学。',
      tags: ['ETL', '数仓', '数据服务'],
      skills: ['SQL 优化', '数仓分层', '离线/实时处理', '调度系统'],
      actions: ['实现 ETL 流程', '掌握数据建模', '熟悉 1 种计算引擎'],
    },
    {
      id: 'qa-engineer',
      name: '测试开发工程师',
      level: 2,
      category: 'transfer',
      categoryLabel: '换岗岗位',
      x: 600,
      y: 440,
      summary: '偏自动化测试、测试平台、质量保障与工程提效。',
      description: '适合关注质量体系、自动化和流程优化的开发者。',
      tags: ['自动化测试', '质量平台', '脚本开发'],
      skills: ['测试设计', '自动化脚本', '接口测试', '质量指标'],
      actions: ['建设自动化用例', '搭建质量看板', '接入持续集成测试'],
    },
    {
      id: 'ai-engineer',
      name: 'AI 应用工程师',
      level: 2,
      category: 'transfer',
      categoryLabel: '换岗岗位',
      x: 980,
      y: 130,
      summary: '围绕大模型接入、RAG、Agent 与业务场景落地。',
      description: '适合已有工程经验，希望快速切入 AI 应用落地赛道的开发者。',
      tags: ['LLM', 'Prompt', 'RAG'],
      skills: ['模型接入', 'Prompt 设计', '向量检索', 'AI 工作流'],
      actions: ['做一个 RAG 项目', '沉淀提示词模板', '学习模型评测'],
    },
    {
      id: 'tech-pm',
      name: '技术产品经理',
      level: 2,
      category: 'transfer',
      categoryLabel: '换岗岗位',
      x: 1030,
      y: 370,
      summary: '偏需求分析、产品设计、技术协同与项目推进。',
      description: '适合沟通表达、抽象建模和协同能力较强的开发者。',
      tags: ['需求分析', '产品设计', '协作推进'],
      skills: ['PRD 输出', '原型设计', '需求拆解', '项目推进'],
      actions: ['参与需求评审', '完成竞品分析', '沉淀方案文档'],
    },
  ] as CareerNode[],
  edges: [
    {
      source: 'java-base',
      target: 'platform-engineer',
      type: 'transfer',
      label: '平台化延展',
      description: '沿着服务开发 → 基础设施 → 平台治理方向迁移。',
      requiredSkills: ['Docker / K8s', 'CI/CD 流程', '监控与可观测'],
      projectSuggestions: ['搭建一套部署流水线', '主导一次平台工具建设'],
      risks: ['只懂业务开发，不熟基础设施', '缺少稳定性治理经验'],
    },
    {
      source: 'java-base',
      target: 'data-engineer',
      type: 'transfer',
      label: '数据方向迁移',
      description: '从业务系统开发转向数据链路、建模与数据服务。',
      requiredSkills: ['数仓建模', 'ETL 设计', 'SQL 深度优化'],
      projectSuggestions: ['搭建一条离线 ETL 链路', '完成一次指标体系建模'],
      risks: ['业务建模强但数据建模弱', '缺少实时/离线处理经验'],
    },
    {
      source: 'java-base',
      target: 'qa-engineer',
      type: 'transfer',
      label: '质量保障延展',
      description: '从开发视角迁移到质量保障和自动化体系建设。',
      requiredSkills: ['自动化测试框架', '测试设计方法', '质量度量体系'],
      projectSuggestions: ['建设接口自动化平台', '完善回归测试流程'],
      risks: ['容易把测试简单理解为点点点', '缺少质量体系方法论'],
    },
    {
      source: 'java-base',
      target: 'ai-engineer',
      type: 'transfer',
      label: 'AI 应用融合',
      description: '结合原有工程能力，切入 LLM 应用、RAG 与 Agent 场景。',
      requiredSkills: ['Prompt 设计', '向量检索', '模型接入与评测'],
      projectSuggestions: ['完成一个企业知识库项目', '做一个 Agent 工作流 Demo'],
      risks: ['只会调用 API，不懂场景设计', '缺少模型效果评估意识'],
    },
    {
      source: 'java-base',
      target: 'tech-pm',
      type: 'transfer',
      label: '产品技术协同',
      description: '从研发执行走向需求抽象、方案设计和跨团队协作。',
      requiredSkills: ['需求分析', 'PRD 与原型输出', '项目推进与沟通'],
      projectSuggestions: ['主导一个小型产品方案', '完成用户调研与需求拆解'],
      risks: ['表达不错但缺少产品方法', '容易停留在需求传话层'],
    },
    {
      source: 'platform-engineer',
      target: 'ai-engineer',
      type: 'transfer',
      label: '工程 + AI',
      description: '平台工程能力可进一步叠加 AI 应用编排与推理服务能力。',
      requiredSkills: ['模型服务部署', '推理链路治理', 'AI 工作流编排'],
      projectSuggestions: ['搭建模型网关或推理服务', '建设 AI 能力平台'],
      risks: ['有平台经验但缺 AI 场景认知'],
    },
    {
      source: 'data-engineer',
      target: 'ai-engineer',
      type: 'transfer',
      label: '数据 + AI',
      description: '数据链路能力与知识库、检索增强场景天然衔接。',
      requiredSkills: ['Embedding 与检索机制', '知识库清洗', '模型效果评估'],
      projectSuggestions: ['搭建 RAG 数据处理链路', '完成一套检索评估方案'],
      risks: ['数据能力强但应用落地经验不足'],
    },
    {
      source: 'qa-engineer',
      target: 'tech-pm',
      type: 'transfer',
      label: '质量到方案',
      description: '测试开发对流程和体验敏感，适合延展到产品方案与协同推进。',
      requiredSkills: ['需求建模', '用户视角分析', '方案表达与汇报'],
      projectSuggestions: ['负责一个质量平台需求设计', '主导流程优化方案输出'],
      risks: ['容易只从内部流程角度思考，忽视用户价值'],
    },
  ] as CareerEdge[],
}

const currentGraphData = computed(() => (activeGraphType.value === 'promotion' ? promotionData : transferData))

const currentSelectionTitle = computed(() => {
  if (activeNode.value) return activeNode.value.name
  if (activeEdge.value) return `${getNodeName(activeEdge.value.source)} → ${getNodeName(activeEdge.value.target)}`
  return '未选中'
})

const aiQuestions = computed(() => {
  if (!activeNode.value) return []
  return [
    `我想转到 ${activeNode.value.name}，还差哪些能力？`,
    `${activeNode.value.name} 适合补哪些项目经历？`,
    `${activeNode.value.name} 的 3 个月行动计划怎么定？`,
  ]
})

const aiAnswer = computed(() => {
  if (!activeNode.value) return ''
  return `建议优先把 ${activeNode.value.skills.slice(0, 2).join('、')} 做成可以证明的项目成果，再围绕 ${activeNode.value.actions[0]}、${activeNode.value.actions[1]} 形成阶段计划。岗位竞争力的关键不是“知道很多”，而是“做出可验证成果”。`
})

const edgePanelTitle = computed(() => {
  if (!activeEdge.value) return ''
  return `${getNodeName(activeEdge.value.source)} → ${getNodeName(activeEdge.value.target)}`
})

const edgePanelSummary = computed(() => activeEdge.value?.label ?? '')

const edgeAdvice = computed(() => {
  if (!activeEdge.value) return ''
  return `这条${activeEdge.value.type === 'promotion' ? '晋升' : '换岗'}路径建议先补齐 ${activeEdge.value.requiredSkills.slice(0, 2).join('、')}，再通过 ${activeEdge.value.projectSuggestions[0]} 形成可展示成果。完成“技能补齐 + 项目证明”后，路径切换会更稳。`
})

const relatedEdges = computed(() => {
  if (!activeNode.value) return []
  return currentGraphData.value.edges.filter(
    (edge) => edge.source === activeNode.value?.id || edge.target === activeNode.value?.id,
  )
})

const registeredShapes = new Set<string>()

function registerNodeShape() {
  if (registeredShapes.has('career-node')) return
  registeredShapes.add('career-node')

  Graph.registerNode(
    'career-node',
    {
      inherit: 'rect',
      width: 236,
      height: 96,
      markup: [
        { tagName: 'rect', selector: 'body' },
        { tagName: 'rect', selector: 'bar' },
        { tagName: 'text', selector: 'label' },
        { tagName: 'text', selector: 'meta' },
      ],
      attrs: {
        body: {
          rx: 24,
          ry: 24,
          fill: '#ffffff',
          strokeWidth: 0,
          filter: {
            name: 'dropShadow',
            args: { dx: 0, dy: 8, blur: 24, color: 'rgba(15, 23, 42, 0.12)' },
          },
        },
        bar: {
          x: 0,
          y: 0,
          width: 6,
          height: 96,
          rx: 24,
          ry: 24,
          fill: '#3b82f6',
        },
        label: {
          refX: 24,
          refY: 38,
          fontSize: 16,
          fontWeight: 700,
          fill: '#0f172a',
          textAnchor: 'start',
        },
        meta: {
          refX: 24,
          refY: 66,
          fontSize: 12,
          fontWeight: 500,
          fill: '#64748b',
          textAnchor: 'start',
        },
      },
    },
    true,
  )
}

function createGraph() {
  if (!containerRef.value) return

  registerNodeShape()

  graphRef.value = new Graph({
    container: containerRef.value,
    panning: {
      enabled: true,
      eventTypes: ['leftMouseDown', 'mouseWheel'],
    },
    mousewheel: {
      enabled: true,
      modifiers: ['ctrl', 'meta'],
      minScale: 0.45,
      maxScale: 2.2,
    },
    interacting: {
      nodeMovable: false,
      edgeMovable: false,
      vertexMovable: false,
    },
    connecting: {
      router: 'manhattan',
      connector: 'rounded',
      connectionPoint: 'anchor',
      allowBlank: false,
    },
    background: { color: 'transparent' },
    grid: {
      visible: true,
      type: 'dot',
      size: 20,
      args: {
        color: '#d9e2ef',
        thickness: 1,
      },
    },
  })

  graphRef.value.on('node:click', ({ node }) => {
    const data = node.getData<CareerNode>()
    activeNode.value = data
    activeEdge.value = null
    highlightSelection({ nodeId: data.id })
  })

  graphRef.value.on('edge:click', ({ edge }) => {
    const data = edge.getData<CareerEdge>()
    activeEdge.value = data
    activeNode.value = null
    highlightSelection({ edgeKey: `${data.source}-${data.target}` })
  })

  graphRef.value.on('blank:click', () => {
    activeNode.value = null
    activeEdge.value = null
    clearHighlight()
  })

  renderGraph()
}

function buildNode(node: CareerNode) {
  const styleMap = {
    current: { accent: '#2563eb', fill: '#eff6ff', border: '#93c5fd' },
    promotion: { accent: '#10b981', fill: '#ffffff', border: '#bbf7d0' },
    transfer: { accent: '#8b5cf6', fill: '#faf5ff', border: '#ddd6fe' },
  }

  const style = styleMap[node.category]

  return graphRef.value?.addNode({
    shape: 'career-node',
    id: node.id,
    x: node.x,
    y: node.y,
    attrs: {
      body: {
        fill: style.fill,
        stroke: style.border,
        strokeWidth: 1.5,
      },
      bar: {
        fill: style.accent,
      },
      label: {
        text: node.name,
      },
      meta: {
        text: `${node.categoryLabel} · Level ${node.level}`,
      },
    },
    data: node,
  })
}

function buildEdge(edge: CareerEdge) {
  const isPromotion = edge.type === 'promotion'
  const stroke = isPromotion ? '#22c55e' : '#8b5cf6'

  return graphRef.value?.addEdge({
    id: `${edge.source}-${edge.target}`,
    source: edge.source,
    target: edge.target,
    router: {
      name: 'manhattan',
      args: { padding: 18, step: 20 },
    },
    connector: {
      name: 'rounded',
      args: { radius: 16 },
    },
    attrs: {
      line: {
        stroke,
        strokeWidth: 3,
        strokeDasharray: isPromotion ? '0' : '7 6',
        targetMarker: {
          name: 'block',
          width: 10,
          height: 10,
          fill: stroke,
        },
      },
    },
    labels: [
      {
        attrs: {
          label: {
            text: edge.label,
            fontSize: 11,
            fontWeight: 700,
            fill: isPromotion ? '#15803d' : '#7c3aed',
          },
          body: {
            fill: '#ffffff',
            stroke: isPromotion ? '#bbf7d0' : '#ddd6fe',
            rx: 10,
            ry: 10,
            padding: 6,
          },
        },
        position: {
          distance: 0.52,
          offset: { y: -10 },
        },
      },
    ],
    data: edge,
    zIndex: 0,
  })
}

function renderGraph() {
  const graph = graphRef.value
  if (!graph) return

  graph.clearCells()
  currentGraphData.value.nodes.forEach((node) => buildNode(node))
  currentGraphData.value.edges.forEach((edge) => buildEdge(edge))

  const defaultNode = currentGraphData.value.nodes[0]
  if (!defaultNode) return

  activeNode.value = defaultNode
  activeEdge.value = null

  nextTick(() => {
    highlightSelection({ nodeId: defaultNode.id })
    fitGraph()
  })
}

function highlightSelection(payload: { nodeId?: string; edgeKey?: string }) {
  const graph = graphRef.value
  if (!graph) return

  graph.getNodes().forEach((node) => {
    const data = node.getData<CareerNode>()
    const defaultMap = {
      current: { fill: '#eff6ff', stroke: '#93c5fd', accent: '#2563eb' },
      promotion: { fill: '#ffffff', stroke: '#bbf7d0', accent: '#10b981' },
      transfer: { fill: '#faf5ff', stroke: '#ddd6fe', accent: '#8b5cf6' },
    }
    const style = defaultMap[data.category]
    const isActive = node.id === payload.nodeId

    node.setAttrs({
      body: {
        fill: isActive ? '#ffffff' : style.fill,
        stroke: isActive ? '#0f172a' : style.stroke,
        strokeWidth: isActive ? 2.5 : 1.5,
        filter: {
          name: 'dropShadow',
          args: {
            dx: 0,
            dy: isActive ? 14 : 8,
            blur: isActive ? 30 : 24,
            color: isActive ? 'rgba(37, 99, 235, 0.18)' : 'rgba(15, 23, 42, 0.12)',
          },
        },
      },
      bar: {
        fill: isActive ? '#0f172a' : style.accent,
      },
    })

    if (isActive) node.toFront()
  })

  graph.getEdges().forEach((edge) => {
    const data = edge.getData<CareerEdge>()
    const isPromotion = data.type === 'promotion'
    const baseStroke = isPromotion ? '#22c55e' : '#8b5cf6'
    const isActive = edge.id === payload.edgeKey

    edge.setAttrs({
      line: {
        stroke: isActive ? '#0f172a' : baseStroke,
        strokeWidth: isActive ? 4 : 3,
        strokeDasharray: isPromotion ? '0' : '7 6',
        targetMarker: {
          name: 'block',
          width: 10,
          height: 10,
          fill: isActive ? '#0f172a' : baseStroke,
        },
      },
    })

    if (isActive) edge.toFront()
  })
}

function clearHighlight() {
  highlightSelection({})
}

function fitGraph() {
  const graph = graphRef.value
  if (!graph) return
  graph.zoomToFit({
    padding: 70,
    maxScale: 1.1,
  })
  graph.centerContent()
}

function zoomIn() {
  graphRef.value?.zoom(0.2)
}

function zoomOut() {
  graphRef.value?.zoom(-0.2)
}

function closeDetail() {
  activeNode.value = null
  activeEdge.value = null
  clearHighlight()
}

function selectEdge(edge: CareerEdge) {
  activeEdge.value = edge
  activeNode.value = null
  highlightSelection({ edgeKey: `${edge.source}-${edge.target}` })
}

function getNodeName(id: string) {
  return currentGraphData.value.nodes.find((node) => node.id === id)?.name ?? id
}

function handleQuestionClick(question: string) {
  console.log('推荐提问：', question)
}

function handleBack() {
  emit('back')
}

watch(activeGraphType, () => {
  renderGraph()
})

onMounted(() => {
  createGraph()
  window.addEventListener('resize', fitGraph)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', fitGraph)
  graphRef.value?.dispose()
})
</script>

<style scoped lang="scss">
:root {
  --blue: #2563eb;
  --green: #10b981;
  --purple: #8b5cf6;
  --bg: #edf4ff;
  --panel: rgba(255, 255, 255, 0.78);
  --text-1: #0f172a;
  --text-2: #475569;
  --text-3: #94a3b8;
  --line: #dbe7f3;
  --shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

.career-path-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(191, 219, 254, 0.55), transparent 28%),
    radial-gradient(circle at top right, rgba(221, 214, 254, 0.45), transparent 24%),
    linear-gradient(180deg, #f8fbff 0%, #edf4ff 100%);
  overflow: hidden;
}

.toolbar {
  height: 80px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(219, 231, 243, 0.9);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(18px);
  flex-shrink: 0;

  .toolbar-left,
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .back-btn {
    border: 1px solid rgba(219, 231, 243, 0.9);
    background: rgba(255, 255, 255, 0.92);
  }

  .page-title {
    margin: 0;
    font-size: 22px;
    font-weight: 800;
    color: var(--text-1);
  }

  .page-subtitle {
    margin: 4px 0 0;
    font-size: 13px;
    color: var(--text-2);
  }

  .view-switcher {
    padding: 4px;
    background: rgba(241, 245, 249, 0.9);
    border-radius: 14px;
  }

  .reset-btn {
    border-radius: 12px;
    border: 1px solid rgba(219, 231, 243, 0.9);
    background: rgba(255, 255, 255, 0.92);
  }
}

.page-body {
  flex: 1;
  display: flex;
  gap: 18px;
  padding: 18px;
  overflow: hidden;
}

.graph-panel,
.detail-panel {
  border: 1px solid rgba(255, 255, 255, 0.7);
  background: var(--panel);
  backdrop-filter: blur(18px);
  box-shadow: var(--shadow);
}

.graph-panel {
  flex: 1;
  position: relative;
  border-radius: 28px;
  overflow: hidden;

  &--full {
    flex: 1;
  }
}

.graph-panel-header {
  position: absolute;
  top: 18px;
  left: 18px;
  right: 18px;
  z-index: 3;
  display: flex;
  justify-content: space-between;
  gap: 18px;
  pointer-events: none;

  .panel-meta,
  .panel-kpis {
    pointer-events: auto;
  }
}

.meta-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.82);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.panel-title {
  margin: 10px 0 6px;
  font-size: 24px;
  color: var(--text-1);
}

.panel-desc {
  margin: 0;
  max-width: 520px;
  color: var(--text-2);
  font-size: 13px;
  line-height: 1.7;
}

.panel-kpis {
  display: flex;
  gap: 12px;
}

.kpi-card {
  min-width: 96px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(219, 231, 243, 0.92);
}

.kpi-label {
  font-size: 12px;
  color: var(--text-3);
}

.kpi-value {
  margin-top: 6px;
  font-size: 24px;
  font-weight: 800;
  color: var(--text-1);

  &--small {
    font-size: 14px;
    line-height: 1.5;
    max-width: 120px;
  }
}

.graph-container {
  width: 100%;
  height: 100%;
}

.graph-guide,
.graph-legend {
  position: absolute;
  z-index: 3;
  padding: 16px 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(219, 231, 243, 0.9);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.graph-guide {
  top: 116px;
  left: 18px;
  width: 248px;
}

.guide-title,
.legend-title {
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 800;
  color: var(--text-3);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.guide-item {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-2);
}

.graph-legend {
  left: 18px;
  bottom: 18px;
}

.legend-items {
  display: grid;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;

  &.current {
    background: var(--blue);
  }
  &.promote {
    background: var(--green);
  }
  &.transfer {
    background: var(--purple);
  }
}

.legend-line {
  width: 26px;
  height: 0;
  border-top: 3px dashed var(--purple);
}

.legend-text {
  font-size: 13px;
  color: var(--text-2);
}

.zoom-controls {
  position: absolute;
  right: 18px;
  bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 3;

  .el-button {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(219, 231, 243, 0.92);
  }
}

.detail-panel {
  width: 430px;
  border-radius: 28px;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 22px 18px;
  border-bottom: 1px solid rgba(219, 231, 243, 0.9);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(248, 250, 252, 0.92));
}

.header-chip {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.1);
  color: var(--blue);
  font-size: 12px;
  font-weight: 700;
}

.detail-title {
  margin: 12px 0 8px;
  font-size: 24px;
  color: var(--text-1);
}

.detail-summary {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-2);
}

.close-btn {
  height: 36px;
  width: 36px;
  flex-shrink: 0;
}

.detail-scrollbar {
  flex: 1;

  :deep(.el-scrollbar__wrap) {
    overflow-x: hidden;
  }
}

.detail-content {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.overview-card,
.info-card,
.ai-assistant-card {
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(219, 231, 243, 0.9);
}

.overview-card {
  padding: 18px;

  &--node {
    background: linear-gradient(180deg, rgba(239, 246, 255, 0.88), rgba(255, 255, 255, 0.92));
  }

  &--edge {
    background: linear-gradient(180deg, rgba(250, 245, 255, 0.92), rgba(255, 255, 255, 0.92));
  }
}

.overview-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.node-badge,
.level-pill,
.edge-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.node-badge {
  padding: 6px 12px;

  &.current {
    background: rgba(37, 99, 235, 0.12);
    color: var(--blue);
  }
  &.promotion {
    background: rgba(16, 185, 129, 0.12);
    color: var(--green);
  }
  &.transfer {
    background: rgba(139, 92, 246, 0.12);
    color: var(--purple);
  }
}

.level-pill,
.edge-badge {
  padding: 6px 10px;
  background: rgba(15, 23, 42, 0.08);
  color: var(--text-1);

  &--light {
    background: rgba(37, 99, 235, 0.08);
    color: var(--blue);
  }
}

.overview-text {
  margin: 14px 0 0;
  font-size: 14px;
  line-height: 1.75;
  color: var(--text-2);
}

.tags-section,
.edge-badges,
.path-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.skill-tag,
.path-chip {
  border-radius: 999px;
}

.path-chip {
  border: 1px solid rgba(219, 231, 243, 0.9);
  background: rgba(248, 250, 252, 0.95);
  padding: 8px 12px;
  font-size: 12px;
  color: var(--text-2);
  cursor: pointer;
  transition: 0.2s ease;

  &:hover {
    color: var(--blue);
    border-color: rgba(37, 99, 235, 0.3);
    transform: translateY(-1px);
  }
}

.info-grid {
  display: grid;
  gap: 14px;

  &--2 {
    grid-template-columns: 1fr 1fr;
  }
}

.info-card,
.ai-assistant-card {
  padding: 18px;
}

.card-header,
.ai-header,
.response-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header {
  margin-bottom: 14px;
}

.card-icon,
.feature-icon {
  color: var(--blue);
}

.card-icon {
  font-size: 18px;
  padding: 8px;
  border-radius: 12px;
  background: rgba(37, 99, 235, 0.08);
}

.card-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-1);
}

.feature-list {
  padding: 0;
  margin: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-2);
}

.feature-icon {
  margin-top: 2px;
  font-size: 15px;
  flex-shrink: 0;
}

.action-list .feature-icon {
  color: var(--purple);
}

.edge-route {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-1);
}

.ai-avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);

  &--purple {
    background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  }
}

.ai-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-1);
}

.ai-status {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 3px;
  font-size: 12px;
  color: var(--text-3);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--green);
}

.ai-intro,
.response-content {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-2);
}

.ai-intro {
  margin: 14px 0;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(248, 250, 252, 0.95);
}

.ai-questions {
  margin-bottom: 14px;
}

.section-label {
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 800;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.question-chips {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.question-chip {
  text-align: left;
  border: 1px solid rgba(219, 231, 243, 0.9);
  background: #fff;
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 13px;
  color: var(--text-2);
  cursor: pointer;
  transition: 0.2s ease;

  &:hover {
    color: var(--purple);
    border-color: rgba(139, 92, 246, 0.35);
    transform: translateX(2px);
  }
}

.ai-response {
  padding: 14px;
  border-radius: 16px;
  background: rgba(250, 245, 255, 0.92);
  border: 1px solid rgba(221, 214, 254, 0.9);

  &--plain {
    margin-top: 14px;
  }
}

.response-header {
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 700;
  color: var(--purple);
}

.slide-panel-enter-active,
.slide-panel-leave-active {
  transition: all 0.28s ease;
}

.slide-panel-enter-from,
.slide-panel-leave-to {
  opacity: 0;
  transform: translateX(24px);
}

:deep(.el-scrollbar__thumb) {
  background: rgba(148, 163, 184, 0.45);
}

@media (max-width: 1280px) {
  .detail-panel {
    width: 390px;
  }

  .panel-kpis {
    display: none;
  }
}

@media (max-width: 1024px) {
  .page-body {
    flex-direction: column;
  }

  .graph-panel {
    min-height: 560px;
  }

  .detail-panel {
    width: 100%;
    max-height: 48vh;
  }
}

@media (max-width: 768px) {
  .toolbar {
    height: auto;
    padding: 16px;
    flex-direction: column;
    align-items: flex-start;

    .toolbar-right {
      width: 100%;
      justify-content: space-between;
    }
  }

  .graph-panel-header {
    position: static;
    padding: 16px 16px 0;
    display: block;
  }

  .graph-guide,
  .graph-legend {
    display: none;
  }

  .info-grid--2 {
    grid-template-columns: 1fr;
  }
}
</style>
