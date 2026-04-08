<template>
  <div class="page" :class="{ 'has-detail-panel': visible }">
    <section class="hero">
      <div>
        <p class="eyebrow">Career Development Map</p>
        <h1>职业发展路径图谱</h1>
        <p class="desc">
          支持纵向晋升与横向转岗图谱，并直接展示每条路径的推荐原因、岗位差异、技能缺口和行动建议。
        </p>
      </div>
      <div class="actions">
        <el-radio-group v-model="viewType" size="large" @change="handleViewChange">
          <el-radio-button label="vertical">纵向晋升图谱</el-radio-button>
          <el-radio-button label="lateral">横向转岗图谱</el-radio-button>
        </el-radio-group>
        <el-input v-model="keyword" class="search" clearable placeholder="搜索岗位名称" @input="renderChart">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
    </section>

    <section class="stats">
      <div class="stat-card">
        <span>当前起点</span>
        <strong>{{ activeData.startJobName }}</strong>
      </div>
      <div class="stat-card">
        <span>路径数量</span>
        <strong>{{ stats.totalPaths }} 条</strong>
      </div>
      <div class="stat-card">
        <span>目标岗位</span>
        <strong>{{ stats.targetJobs }} 个</strong>
      </div>
      <div class="stat-card">
        <span>平均迁移成本</span>
        <strong>{{ stats.avgCost.toFixed(2) }}</strong>
      </div>
    </section>

    <section class="chart-panel">
      <div class="panel-head">
        <div>
          <h2>{{ viewType === 'vertical' ? '纵向晋升路径图谱' : '横向转岗路径图谱' }}</h2>
          <p>
            {{
              viewType === 'vertical'
                ? '纵向图按照 stepIndex 展示从当前岗位逐级向上的晋升路径。'
                : '横向图围绕当前岗位展开，重点展示不同转岗方向的推荐原因与缺口分析。'
            }}
          </p>
        </div>
        <div class="legend">
          <span><i class="dot start"></i>当前岗位</span>
          <span><i class="dot vertical"></i>纵向节点</span>
          <span><i class="dot lateral"></i>横向节点</span>
        </div>
      </div>
      <div ref="chartRef" v-loading="loading" class="chart"></div>
    </section>

    <section class="route-panel">
      <div class="route-header">
        <h3>{{ viewType === 'vertical' ? '路径明细' : '转岗建议与缺口分析' }}</h3>
        <p>
          {{
            viewType === 'vertical'
              ? '每一步都会展示推荐原因、岗位差异和能力补齐建议。'
              : '每条转岗路线都会展示目标岗位差异、AI 推荐理由、JD 原话和具体行动建议。'
          }}
        </p>
      </div>

      <div class="route-grid">
        <article
          v-for="path in activeData.paths"
          :key="path.pathid"
          class="route-card"
          :class="{ active: selectedPathId === path.pathid }"
          @click="selectPath(path)"
        >
          <div class="route-top">
            <h4>{{ path.pathTitle }}</h4>
            <el-tag :type="path.pathType === 'vertical' ? 'danger' : 'warning'">
              {{ path.pathType === 'vertical' ? '纵向晋升' : '横向转岗' }}
            </el-tag>
          </div>

          <div class="path-overview">
            <div class="box-title">Agent 对整条路线的全局点评与风险提示</div>
            <p class="route-summary">{{ path.overallSummary }}</p>
          </div>

          <div class="route-metrics">
            <span>总步数：{{ path.totalSteps }}</span>
            <span>迁移成本：{{ path.totalRoutingCost.toFixed(2) }}</span>
          </div>

          <div v-for="step in path.steps" :key="`${path.pathid}-${step.stepIndex}-${step.toJobid}`" class="step-card">
            <div class="step-top">
              <strong>{{ step.fromJobName }} → {{ step.toJobName }}</strong>
              <span>第 {{ step.stepIndex }} 步</span>
            </div>

            <div class="job-diff">
              <div class="job-box">
                <span class="job-label">起点岗位</span>
                <strong>{{ step.fromJobName }}</strong>
                <small>ID: {{ step.fromJobid }}</small>
              </div>
              <div class="job-arrow">→</div>
              <div class="job-box target">
                <span class="job-label">目标岗位</span>
                <strong>{{ step.toJobName }}</strong>
                <small>ID: {{ step.toJobid }}</small>
              </div>
            </div>

            <div class="score-row">
              <span>硬技能重合：{{ percent(step.jaccardHigh) }}</span>
              <span>软素质契合：{{ percent(step.cosLow) }}</span>
              <span>薪资增益：{{ salary(step.salaryGain) }}</span>
            </div>

            <div class="analysis-box">
              <div class="box-title">AI 解释：为什么推荐走这一步</div>
              <p>{{ step.transitionReason }}</p>
            </div>

            <div class="analysis-box">
              <div class="box-title">缺失技术 / 技能总览</div>
              <el-empty v-if="!step.skillGaps.length" description="当前步骤暂无明显缺口" />
              <div v-for="(gap, index) in step.skillGaps" :key="`${path.pathid}-${step.stepIndex}-${index}`" class="gap-item">
                <div class="gap-head">
                  <strong>{{ gap.competencyName || '未命名技能' }}</strong>
                  <el-tag size="small" effect="light">{{ gap.category || '未分类' }}</el-tag>
                </div>
                <div class="gap-meta">
                  <span><strong>能力分类：</strong>{{ gap.category || '未分类' }}</span>
                  <span><strong>最低要求评分：</strong>{{ gap.targetScore ?? '-' }}</span>
                </div>
                <div class="gap-section" v-if="gap.originalContext">
                  <div class="gap-section-title">原始 JD 中的技能要求原文</div>
                  <p class="gap-context">{{ gap.originalContext }}</p>
                </div>
                <div class="gap-section">
                  <div class="gap-section-title">可落地的学习建议</div>
                  <p class="gap-advice">{{ gap.actionableAdvice || '暂无行动建议' }}</p>
                </div>
              </div>
            </div>

            <div class="analysis-box" v-if="step.skillGaps.length">
              <div class="box-title">本步学习建议汇总</div>
              <ul class="advice-list">
                <li v-for="(gap, index) in step.skillGaps" :key="`${path.pathid}-${step.stepIndex}-advice-${index}`">
                  <strong>{{ gap.competencyName || '能力补齐' }}：</strong>{{ gap.actionableAdvice || '暂无行动建议' }}
                </li>
              </ul>
            </div>
          </div>
        </article>
      </div>
    </section>

    <transition name="detail-slide">
      <aside v-if="visible" class="detail-panel" aria-label="详情面板">
        <div class="detail-panel__header">
          <div class="detail-panel__title">
            <p class="detail-panel__eyebrow">详情</p>
            <h3>{{ dialogTitle }}</h3>
          </div>
          <button class="detail-panel__close" type="button" @click="visible = false">关闭</button>
        </div>

        <div class="detail-panel__body">
          <template v-if="mode === 'node' && selectedNode">
            <div class="dialog-block">
              <div class="dialog-top">
                <h3>{{ selectedNode.name }}</h3>
                <el-tag :type="selectedNode.category === 'start' ? 'primary' : selectedNode.pathType === 'vertical' ? 'danger' : 'warning'">
                  {{ selectedNode.category === 'start' ? '当前岗位' : selectedNode.pathType === 'vertical' ? '纵向晋升节点' : '横向转岗节点' }}
                </el-tag>
              </div>
              <p><strong>岗位 ID：</strong>{{ selectedNode.jobId }}</p>
              <p><strong>层级说明：</strong>{{ selectedNode.levelText }}</p>
              <p v-if="selectedNode.relatedPathTitles.length">
                <strong>相关路径：</strong>{{ selectedNode.relatedPathTitles.join('、') }}
              </p>
            </div>
          </template>

          <template v-else-if="mode === 'edge' && selectedEdge">
            <div class="dialog-block">
              <div class="dialog-top">
                <h3>{{ selectedEdge.pathTitle }}</h3>
                <el-tag :type="selectedEdge.pathType === 'vertical' ? 'danger' : 'warning'">
                  {{ selectedEdge.pathType === 'vertical' ? '纵向晋升' : '横向转岗' }}
                </el-tag>
              </div>
              <div class="dialog-box">
                <div class="box-title">Agent 对整条路线的全局点评与风险提示</div>
                <p class="dialog-summary">{{ selectedEdge.overallSummary }}</p>
              </div>

              <div class="dialog-job-diff">
                <div class="job-box">
                  <span class="job-label">起点岗位</span>
                  <strong>{{ selectedEdge.fromJobName }}</strong>
                  <small>ID: {{ selectedEdge.source }}</small>
                </div>
                <div class="job-arrow">→</div>
                <div class="job-box target">
                  <span class="job-label">目标岗位</span>
                  <strong>{{ selectedEdge.toJobName }}</strong>
                  <small>ID: {{ selectedEdge.target }}</small>
                </div>
              </div>

              <div class="dialog-metrics">
                <span>总步数：{{ selectedEdge.totalSteps }}</span>
                <span>当前步骤：第 {{ selectedEdge.stepIndex }} 步</span>
                <span>迁移成本：{{ selectedEdge.totalRoutingCost.toFixed(2) }}</span>
                <span>硬技能重合：{{ percent(selectedEdge.jaccardHigh) }}</span>
                <span>软素质契合：{{ percent(selectedEdge.cosLow) }}</span>
                <span>薪资增益：{{ salary(selectedEdge.salaryGain) }}</span>
              </div>

              <div class="dialog-box">
                <div class="box-title">AI 解释：为什么推荐走这一步</div>
                <p>{{ selectedEdge.transitionReason }}</p>
              </div>
            </div>

            <div class="dialog-block">
              <div class="box-title">缺失技术 / 技能</div>
              <el-empty v-if="!selectedEdge.skillGaps.length" description="当前步骤暂无明显缺口" />
              <div
                v-for="(gap, index) in selectedEdge.skillGaps"
                :key="`${selectedEdge.id}-dialog-gap-${index}`"
                class="gap-item"
              >
                <div class="gap-head">
                  <strong>{{ gap.competencyName || '未命名技能' }}</strong>
                  <el-tag size="small" effect="light">{{ gap.category || '未分类' }}</el-tag>
                </div>
                <div class="gap-meta">
                  <span><strong>能力分类：</strong>{{ gap.category || '未分类' }}</span>
                  <span><strong>最低要求评分：</strong>{{ gap.targetScore ?? '-' }}</span>
                </div>
                <div class="gap-section" v-if="gap.originalContext">
                  <div class="gap-section-title">原始 JD 中的技能要求原文</div>
                  <p class="gap-context">{{ gap.originalContext }}</p>
                </div>
                <div class="gap-section">
                  <div class="gap-section-title">可落地的学习建议</div>
                  <p class="gap-advice">{{ gap.actionableAdvice || '暂无行动建议' }}</p>
                </div>
              </div>
            </div>

            <div class="dialog-block" v-if="selectedEdge.skillGaps.length">
              <div class="box-title">学习建议汇总</div>
              <ul class="advice-list">
                <li v-for="(gap, index) in selectedEdge.skillGaps" :key="`${selectedEdge.id}-dialog-advice-${index}`">
                  <strong>{{ gap.competencyName || '能力补齐' }}：</strong>{{ gap.actionableAdvice || '暂无行动建议' }}
                </li>
              </ul>
            </div>
          </template>
        </div>
      </aside>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import { Search } from '@element-plus/icons-vue'

type ViewType = 'vertical' | 'lateral'
type PathType = 'vertical' | 'lateral'
type Mode = 'node' | 'edge'

interface SkillGap {
  actionableAdvice: string
  category: string
  competencyName: string
  originalContext: string
  targetScore?: number
}

interface Step {
  cosLow: number
  fromJobid: string
  fromJobName: string
  jaccardHigh: number
  salaryGain: number
  skillGaps: SkillGap[]
  stepIndex: number
  toJobid: string
  toJobName: string
  transitionReason: string
}

interface Path {
  overallSummary: string
  pathid: string
  pathTitle: string
  pathType: PathType
  steps: Step[]
  totalRoutingCost: number
  totalSteps: number
}

interface CareerData {
  paths: Path[]
  startJobid: string
  startJobName: string
}

interface GraphNodeData {
  id: string
  name: string
  value: string
  jobId: string
  category: 'start' | 'target'
  pathType: PathType
  levelText: string
  relatedPathTitles: string[]
  symbolSize: number
  x: number
  y: number
  itemStyle: Record<string, unknown>
  label: Record<string, unknown>
}

interface GraphEdgeData {
  id: string
  source: string
  target: string
  pathTitle: string
  pathType: PathType
  overallSummary: string
  totalRoutingCost: number
  totalSteps: number
  stepIndex: number
  jaccardHigh: number
  cosLow: number
  salaryGain: number
  transitionReason: string
  skillGaps: SkillGap[]
  fromJobName: string
  toJobName: string
  lineStyle: Record<string, unknown>
  label: Record<string, unknown>
}

const chartRef = ref<HTMLElement | null>(null)
const chart = ref<echarts.ECharts | null>(null)
const loading = ref(false)
const viewType = ref<ViewType>('vertical')
const keyword = ref('')
const visible = ref(false)
const mode = ref<Mode>('node')
const dialogTitle = ref('')
const selectedNode = ref<GraphNodeData | null>(null)
const selectedEdge = ref<GraphEdgeData | null>(null)
const selectedPathId = ref('')

const verticalData: CareerData = {
  startJobid: 'job_002',
  startJobName: '前端开发工程师',
  paths: [
    {
      pathid: 'vertical_001',
      pathTitle: '前端架构跃迁路线：从开发工程师到资深架构师',
      pathType: 'vertical',
      totalSteps: 3,
      totalRoutingCost: 0.15,
      overallSummary: '这是一条标准的纵向晋升主干路线，强调从工程执行到架构决策能力的逐步升级。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_002_mid',
          toJobName: '中级前端工程师',
          jaccardHigh: 0.85,
          cosLow: 0.9,
          salaryGain: 0.2,
          transitionReason: '当前岗位与中级前端工程师的核心技能重合度较高，是最自然的第一步晋升。',
          skillGaps: [
            {
              competencyName: '组件库建设',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '参与团队组件库建设与维护',
              actionableAdvice: '独立抽象高复用业务组件，并补齐文档与示例。'
            }
          ]
        },
        {
          stepIndex: 2,
          fromJobid: 'job_002_mid',
          fromJobName: '中级前端工程师',
          toJobid: 'job_002_senior',
          toJobName: '高级前端工程师',
          jaccardHigh: 0.8,
          cosLow: 0.85,
          salaryGain: 0.3,
          transitionReason: '这一阶段更看重性能优化、复杂业务抽象和跨模块交付能力。',
          skillGaps: [
            {
              competencyName: '性能优化',
              category: '核心专业技能',
              targetScore: 4,
              originalContext: '掌握性能指标与性能优化方法',
              actionableAdvice: '完成一次性能专项治理并给出量化结果。'
            }
          ]
        },
        {
          stepIndex: 3,
          fromJobid: 'job_002_senior',
          fromJobName: '高级前端工程师',
          toJobid: 'job_003',
          toJobName: '资深前端架构师',
          jaccardHigh: 0.75,
          cosLow: 0.9,
          salaryGain: 0.5,
          transitionReason: '从高级工程师进入架构师阶段，关键在于技术方案主导权和系统性架构视角。',
          skillGaps: [
            {
              competencyName: '微前端架构',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '主导过微前端拆分与落地',
              actionableAdvice: '以现有系统为对象做一版微前端拆分方案并组织评审。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'vertical_002',
      pathTitle: '技术管理路线：从开发到前端负责人',
      pathType: 'vertical',
      totalSteps: 2,
      totalRoutingCost: 0.25,
      overallSummary: '偏向管理路线，更强调团队协作、技术规划与跨团队推动能力。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_002_lead',
          toJobName: '前端技术主管',
          jaccardHigh: 0.7,
          cosLow: 0.85,
          salaryGain: 0.35,
          transitionReason: '该岗位除了技术能力，也要求开始承担人员带教和项目协同。',
          skillGaps: [
            {
              competencyName: '团队管理',
              category: '软技能',
              targetScore: 3,
              originalContext: '具备带教或小团队协作管理经验',
              actionableAdvice: '主动承担新人培养、需求分工和项目节奏管理职责。'
            }
          ]
        },
        {
          stepIndex: 2,
          fromJobid: 'job_002_lead',
          fromJobName: '前端技术主管',
          toJobid: 'job_002_director',
          toJobName: '前端技术负责人',
          jaccardHigh: 0.6,
          cosLow: 0.8,
          salaryGain: 0.6,
          transitionReason: '岗位关注点从单项目交付转向团队规划、技术治理与资源协调。',
          skillGaps: [
            {
              competencyName: '技术规划',
              category: '战略能力',
              targetScore: 4,
              originalContext: '能够制定季度或年度技术演进路线',
              actionableAdvice: '梳理团队技术债并沉淀季度技术演进计划。'
            }
          ]
        }
      ]
    }
  ]
}

const lateralData: CareerData = {
  startJobid: 'job_002',
  startJobName: '前端开发工程师',
  paths: [
    {
      pathid: 'lateral_001',
      pathTitle: '前端 → Node 后端：全栈能力跃迁路径',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.35,
      overallSummary: '低风险转岗路径，适合希望走全栈路线的前端工程师。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_105',
          toJobName: 'Node 后端工程师',
          jaccardHigh: 0.6,
          cosLow: 0.8,
          salaryGain: 0,
          transitionReason: '逻辑能力和工程化基础有较强可迁移性，但服务端基础设施能力仍需补齐。',
          skillGaps: [
            {
              competencyName: 'Redis',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '熟练使用 Redis 进行高并发缓存设计',
              actionableAdvice: '实现一个带缓存层的 Node 服务，补齐缓存淘汰和缓存穿透防护。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_002',
      pathTitle: '前端 → 技术产品经理：需求转译者成长路径',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.75,
      overallSummary: '适合对用户价值、业务需求和跨团队协作更感兴趣的工程师。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_201',
          toJobName: '技术产品经理',
          jaccardHigh: 0.2,
          cosLow: 0.85,
          salaryGain: 0,
          transitionReason: '软素质契合度高，但需要补齐文档表达和需求抽象能力。',
          skillGaps: [
            {
              competencyName: 'PRD 编写',
              category: '工具与平台能力',
              targetScore: 4,
              originalContext: '熟练输出高质量 PRD 和高保真原型',
              actionableAdvice: '找一个熟悉项目，逆向补齐 PRD、业务流和页面原型。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_003',
      pathTitle: '前端 → UI/UX 设计师：体验设计转型路径',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.55,
      overallSummary: '前端对界面实现和交互细节敏感，具备向体验设计转型的天然优势。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_301',
          toJobName: 'UI/UX 设计师',
          jaccardHigh: 0.4,
          cosLow: 0.75,
          salaryGain: -0.1,
          transitionReason: '需要系统补齐设计工具使用与用户研究方法。',
          skillGaps: [
            {
              competencyName: 'Figma',
              category: '设计工具',
              targetScore: 4,
              originalContext: '熟练使用 Figma 完成高保真界面设计',
              actionableAdvice: '用 Figma 重做现有模块界面，并沉淀基础设计组件。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_004',
      pathTitle: '前端 → DevOps 工程师：工程效能优化路径',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.45,
      overallSummary: '偏向工程基础设施与交付效率方向。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_401',
          toJobName: 'DevOps 工程师',
          jaccardHigh: 0.5,
          cosLow: 0.7,
          salaryGain: 0.15,
          transitionReason: '工程化、CI/CD 和发布流程认知可以直接迁移，但容器与平台运维能力仍是缺口。',
          skillGaps: [
            {
              competencyName: 'Kubernetes',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '掌握 K8s 容器编排与集群基础运维',
              actionableAdvice: '在本地搭建最小可运行 K8s 集群，并部署一个演示服务。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_005',
      pathTitle: '前端 → 数据分析师：数据驱动决策路径',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.65,
      overallSummary: '适合对数据可视化、指标分析和业务决策有兴趣的前端工程师。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_501',
          toJobName: '数据分析师',
          jaccardHigh: 0.3,
          cosLow: 0.8,
          salaryGain: 0.1,
          transitionReason: '可视化表达与业务理解是优势，但分析方法论和数据处理能力仍需补齐。',
          skillGaps: [
            {
              competencyName: 'SQL/Python',
              category: '数据处理',
              targetScore: 4,
              originalContext: '能够使用 SQL 和 Python 处理分析型数据',
              actionableAdvice: '完成一个用户行为分析小项目，输出分析结论与图表。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_006',
      pathTitle: '前端 → 测试开发工程师：质量保障专家路径',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.4,
      overallSummary: '适合关注质量体系和自动化测试建设的前端工程师。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_601',
          toJobName: '测试开发工程师',
          jaccardHigh: 0.55,
          cosLow: 0.75,
          salaryGain: 0.05,
          transitionReason: '代码理解、边界意识和自动化能力使前端具备天然转测试开发的基础。',
          skillGaps: [
            {
              competencyName: '自动化测试框架',
              category: '测试技能',
              targetScore: 4,
              originalContext: '掌握 Cypress、Playwright 或 Selenium 等工具',
              actionableAdvice: '为当前项目搭建一套 E2E 自动化测试流程并输出测试报告。'
            }
          ]
        }
      ]
    }
  ]
}

const activeData = computed(() => (viewType.value === 'vertical' ? verticalData : lateralData))

const stats = computed(() => ({
  totalPaths: activeData.value.paths.length,
  targetJobs: new Set(activeData.value.paths.flatMap((path) => path.steps.map((step) => step.toJobid))).size,
  avgCost: activeData.value.paths.length
    ? activeData.value.paths.reduce((sum, path) => sum + path.totalRoutingCost, 0) / activeData.value.paths.length
    : 0
}))

const percent = (value: number) => `${(value * 100).toFixed(0)}%`
const salary = (value: number) => (value > 0 ? `+${percent(value)}` : percent(value))

function selectPath(path: Path) {
  selectedPathId.value = path.pathid
  const firstStep = path.steps[0]
  if (!firstStep) return

  mode.value = 'edge'
  selectedNode.value = null
  selectedEdge.value = {
    id: `${path.pathid}-${firstStep.stepIndex}-panel`,
    source: firstStep.fromJobid,
    target: firstStep.toJobid,
    pathTitle: path.pathTitle,
    pathType: path.pathType,
    overallSummary: path.overallSummary,
    totalRoutingCost: path.totalRoutingCost,
    totalSteps: path.totalSteps,
    stepIndex: firstStep.stepIndex,
    jaccardHigh: firstStep.jaccardHigh,
    cosLow: firstStep.cosLow,
    salaryGain: firstStep.salaryGain,
    transitionReason: firstStep.transitionReason,
    skillGaps: firstStep.skillGaps,
    fromJobName: firstStep.fromJobName,
    toJobName: firstStep.toJobName,
    lineStyle: {},
    label: {}
  }
  dialogTitle.value = path.pathTitle
  visible.value = true
}

function handleViewChange() {
  selectedPathId.value = activeData.value.paths[0]?.pathid ?? ''
  renderChart()
}

function nodeStyle(kind: 'start' | 'target', type: PathType) {
  if (kind === 'start') {
    return {
      color: '#1d4ed8',
      borderColor: '#dbeafe',
      borderWidth: 3,
      shadowBlur: 20,
      shadowColor: 'rgba(29, 78, 216, 0.35)'
    }
  }
  if (type === 'vertical') {
    return {
      color: '#ef4444',
      borderColor: '#fee2e2',
      borderWidth: 2,
      shadowBlur: 12,
      shadowColor: 'rgba(239, 68, 68, 0.2)'
    }
  }
  return {
    color: '#f59e0b',
    borderColor: '#fef3c7',
    borderWidth: 2,
    shadowBlur: 12,
    shadowColor: 'rgba(245, 158, 11, 0.2)'
  }
}

function buildGraph(data: CareerData) {
  const nodes: GraphNodeData[] = []
  const edges: GraphEdgeData[] = []
  const nodeMap = new Map<string, GraphNodeData>()
  const pathMap = new Map<string, Set<string>>()
  const levels = [...new Set(data.paths.flatMap((path) => path.steps.map((step) => step.stepIndex)))].sort((a, b) => a - b)

  const startNode: GraphNodeData = {
    id: data.startJobid,
    name: data.startJobName,
    value: data.startJobName,
    jobId: data.startJobid,
    category: 'start',
    pathType: viewType.value,
    levelText: '起点岗位',
    relatedPathTitles: [],
    symbolSize: 78,
    x: viewType.value === 'vertical' ? 180 : 460,
    y: viewType.value === 'vertical' ? 160 : 320,
    itemStyle: nodeStyle('start', viewType.value),
    label: {
      position: viewType.value === 'vertical' ? 'bottom' : 'inside',
      color: '#ffffff',
      fontSize: 12,
      fontWeight: 'bold'
    }
  }

  nodes.push(startNode)
  nodeMap.set(startNode.id, startNode)

  data.paths.forEach((path, pathIndex) => {
    path.steps.forEach((step, stepOrder) => {
      if (!pathMap.has(step.toJobid)) pathMap.set(step.toJobid, new Set())
      pathMap.get(step.toJobid)?.add(path.pathTitle)

      if (!nodeMap.has(step.toJobid)) {
        const levelIndex = levels.indexOf(step.stepIndex)
        const angle = (Math.PI * 2 * pathIndex) / Math.max(data.paths.length, 1)
        const node: GraphNodeData = {
          id: step.toJobid,
          name: step.toJobName,
          value: step.toJobName,
          jobId: step.toJobid,
          category: 'target',
          pathType: path.pathType,
          levelText: viewType.value === 'vertical' ? `第 ${step.stepIndex} 级节点` : '横向转岗目标',
          relatedPathTitles: [],
          symbolSize: 66,
          x: viewType.value === 'vertical' ? 420 + levelIndex * 180 + (pathIndex % 2 === 0 ? -50 : 50) : 460 + Math.cos(angle) * 270,
          y: viewType.value === 'vertical' ? 120 + levelIndex * 120 + (pathIndex % 3) * 24 : 320 + Math.sin(angle) * 200,
          itemStyle: nodeStyle('target', path.pathType),
          label: {
            position: viewType.value === 'vertical' ? 'bottom' : 'inside',
            color: viewType.value === 'vertical' ? '#374151' : '#ffffff',
            fontSize: 12,
            fontWeight: 'bold'
          }
        }
        nodeMap.set(node.id, node)
        nodes.push(node)
      }

      edges.push({
        id: `${path.pathid}-${step.stepIndex}-${stepOrder}`,
        source: step.fromJobid,
        target: step.toJobid,
        pathTitle: path.pathTitle,
        pathType: path.pathType,
        overallSummary: path.overallSummary,
        totalRoutingCost: path.totalRoutingCost,
        totalSteps: path.totalSteps,
        stepIndex: step.stepIndex,
        jaccardHigh: step.jaccardHigh,
        cosLow: step.cosLow,
        salaryGain: step.salaryGain,
        transitionReason: step.transitionReason,
        skillGaps: step.skillGaps,
        fromJobName: step.fromJobName,
        toJobName: step.toJobName,
        lineStyle: {
          color: path.pathType === 'vertical' ? '#ef4444' : '#f59e0b',
          width: 3,
          type: path.pathType === 'vertical' ? 'solid' : 'dashed',
          curveness: viewType.value === 'vertical' ? 0.05 : 0.18
        },
        label: {
          show: true,
          formatter: path.pathType === 'vertical' ? `晋升 ${step.stepIndex}` : '转岗',
          color: '#6b7280',
          fontSize: 11
        }
      })
    })
  })

  const text = keyword.value.trim().toLowerCase()
  nodes.forEach((node) => {
    node.relatedPathTitles = [...(pathMap.get(node.id) ?? new Set<string>())]
    if (text && node.name.toLowerCase().includes(text)) {
      node.itemStyle = {
        ...node.itemStyle,
        borderColor: '#fde047',
        borderWidth: 4,
        shadowBlur: 26,
        shadowColor: 'rgba(253, 224, 71, 0.55)'
      }
    }
  })

  return { nodes, edges }
}

function renderChart() {
  if (!chart.value) return

  const { nodes, edges } = buildGraph(activeData.value)
  chart.value.setOption(
    {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            return `<strong>${params.data.name}</strong><br/>岗位 ID：${params.data.jobId}`
          }
          return `<strong>${params.data.pathTitle}</strong><br/>${params.data.fromJobName} → ${params.data.toJobName}<br/>迁移成本：${Number(params.data.totalRoutingCost).toFixed(2)}`
        }
      },
      series: [
        {
          type: 'graph',
          layout: 'none',
          roam: true,
          draggable: true,
          focusNodeAdjacency: true,
          edgeSymbol: ['none', 'arrow'],
          edgeSymbolSize: 8,
          data: nodes,
          links: edges,
          lineStyle: { opacity: 0.9 },
          emphasis: {
            focus: 'adjacency',
            lineStyle: { width: 5 }
          }
        }
      ]
    } as echarts.EChartsOption,
    true
  )
}

function initChart() {
  if (!chartRef.value) return

  chart.value?.dispose()
  chart.value = echarts.init(chartRef.value)
  chart.value.on('click', (params: any) => {
    if (params.dataType === 'node') {
      mode.value = 'node'
      selectedNode.value = params.data as GraphNodeData
      selectedEdge.value = null
      dialogTitle.value = params.data.name
      visible.value = true
      return
    }
    if (params.dataType === 'edge') {
      mode.value = 'edge'
      selectedEdge.value = params.data as GraphEdgeData
      selectedNode.value = null
      dialogTitle.value = params.data.pathTitle
      visible.value = true
    }
  })

  renderChart()
}

function handleResize() {
  chart.value?.resize()
}

onMounted(() => {
  selectedPathId.value = activeData.value.paths[0]?.pathid ?? ''
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart.value?.dispose()
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  padding: 24px;
  transition: padding-right 0.22s ease;
  background:
    radial-gradient(circle at top left, rgba(253, 224, 71, 0.25), transparent 28%),
    radial-gradient(circle at top right, rgba(56, 189, 248, 0.18), transparent 24%),
    linear-gradient(160deg, #fffaf0 0%, #f8fbff 48%, #eef5ff 100%);
}

.page.has-detail-panel {
  padding-right: min(620px, calc(100vw - 24px));
}

.hero,
.chart-panel,
.route-panel,
.stat-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.08);
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
  border-radius: 24px;
  margin-bottom: 20px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #b45309;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.1;
  color: #111827;
}

.desc {
  margin: 12px 0 0;
  max-width: 760px;
  color: #4b5563;
  line-height: 1.7;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 320px;
}

.search {
  width: 100%;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 18px;
  padding: 18px 20px;
}

.stat-card span {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.stat-card strong {
  font-size: 22px;
  color: #111827;
}

.chart-panel,
.route-panel {
  border-radius: 24px;
  padding: 20px;
  margin-bottom: 20px;
}

.panel-head,
.route-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.panel-head h2,
.route-header h3 {
  margin: 0 0 6px;
  color: #111827;
}

.panel-head p,
.route-header p {
  margin: 0;
  color: #6b7280;
}

.legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  color: #4b5563;
  font-size: 13px;
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-right: 6px;
}

.dot.start { background: #1d4ed8; }
.dot.vertical { background: #ef4444; }
.dot.lateral { background: #f59e0b; }

.chart {
  height: 680px;
  border-radius: 20px;
  background:
    linear-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.08) 1px, transparent 1px),
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  background-size: 36px 36px, 36px 36px, auto;
  overflow: hidden;
}

.route-grid {
  display: grid;
  gap: 16px;
}

.route-card {
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 18px;
  background: #ffffff;
  cursor: pointer;
  transition: 0.2s ease;
}

.route-card.active,
.route-card:hover {
  border-color: #93c5fd;
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.12);
}

.route-top,
.step-top,
.gap-head,
.dialog-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.route-top h4,
.dialog-top h3 {
  margin: 0;
  color: #111827;
}

.route-summary,
.dialog-summary {
  margin: 0;
  line-height: 1.7;
  color: #475569;
}

.path-overview {
  margin: 12px 0;
  padding: 14px 16px;
  border-radius: 14px;
  background: linear-gradient(180deg, #f8fafc 0%, #fefce8 100%);
  border: 1px solid #e5e7eb;
}

.route-metrics,
.score-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 14px;
}

.job-diff {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.job-box {
  padding: 12px;
  border-radius: 14px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
}

.job-box.target {
  background: #fff7ed;
  border-color: #fed7aa;
}

.job-label {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 6px;
}

.job-box strong {
  display: block;
  color: #111827;
  margin-bottom: 4px;
}

.job-box small {
  color: #6b7280;
}

.job-arrow {
  font-size: 24px;
  color: #9ca3af;
}

.step-card {
  border-top: 1px dashed #e5e7eb;
  padding-top: 14px;
  margin-top: 14px;
}

.analysis-box {
  margin-top: 12px;
  padding: 14px;
  border-radius: 14px;
  background: #f8fafc;
}

.box-title {
  font-size: 12px;
  font-weight: 700;
  color: #475569;
  margin-bottom: 8px;
}

.analysis-box p,
.gap-item p {
  margin: 0;
  line-height: 1.7;
  color: #4b5563;
}

.gap-item {
  border: 1px solid #fde68a;
  background: #fffbeb;
  border-radius: 14px;
  padding: 12px;
}

.gap-item + .gap-item {
  margin-top: 10px;
}

.gap-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 8px;
  margin-bottom: 8px;
  color: #6b7280;
  font-size: 13px;
}

.gap-context {
  margin: 0;
  color: #92400e;
}

.gap-advice {
  color: #374151;
}

.gap-section + .gap-section {
  margin-top: 10px;
}

.gap-section-title {
  font-size: 12px;
  font-weight: 700;
  color: #475569;
  margin-bottom: 6px;
}

.advice-list {
  margin: 0;
  padding-left: 18px;
  color: #374151;
}

.advice-list li + li {
  margin-top: 8px;
}

.dialog-block + .dialog-block {
  margin-top: 18px;
}

.detail-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  bottom: 20px;
  width: min(560px, calc(100vw - 32px));
  z-index: 30;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 24px;
  box-shadow: 0 20px 48px rgba(15, 23, 42, 0.16);
  overflow: hidden;
}

.detail-panel__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  padding: 20px 20px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-panel__title h3 {
  margin: 4px 0 0;
  color: #111827;
  font-size: 22px;
}

.detail-panel__eyebrow {
  margin: 0;
  color: #9ca3af;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.detail-panel__close {
  border: 0;
  background: #111827;
  color: #ffffff;
  border-radius: 999px;
  padding: 8px 14px;
  cursor: pointer;
  font-size: 13px;
}

.detail-panel__body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.dialog-box {
  padding: 14px 16px;
  border-radius: 14px;
  background: #f8fafc;
  margin-top: 12px;
}

.dialog-job-diff {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
  align-items: center;
  margin-top: 14px;
}

.dialog-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #6b7280;
  font-size: 13px;
  margin-top: 14px;
}

.detail-slide-enter-active,
.detail-slide-leave-active {
  transition: all 0.22s ease;
}

.detail-slide-enter-from,
.detail-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

@media (max-width: 1100px) {
  .hero,
  .panel-head,
  .route-header {
    flex-direction: column;
  }

  .actions {
    min-width: 0;
    width: 100%;
  }

  .stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .page.has-detail-panel {
    padding-right: 24px;
  }
}

@media (max-width: 720px) {
  .page {
    padding: 14px;
  }

  .page.has-detail-panel {
    padding-right: 14px;
  }

  .stats {
    grid-template-columns: 1fr;
  }

  .chart {
    height: 560px;
  }

  .job-diff {
    grid-template-columns: 1fr;
  }

  .job-arrow {
    display: none;
  }

  .dialog-job-diff {
    grid-template-columns: 1fr;
  }

  .detail-panel {
    top: 12px;
    right: 12px;
    bottom: 12px;
    width: min(520px, calc(100vw - 24px));
  }
}
</style>
