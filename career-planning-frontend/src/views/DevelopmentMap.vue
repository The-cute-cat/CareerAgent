<template>
  <div class="page" :class="{ 'has-detail-panel': visible }">
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Career Development Map</p>
        <h1>职业发展路线图谱</h1>
        <p class="desc">
          支持纵向晋升与横向转岗图谱，并完整展示每条路线的 Agent 全局点评、推荐原因、技能缺口、JD 原文和可落地学习建议。
        </p>
        <div class="hero-hints">
          <span>点击节点查看岗位详情</span>
          <span>点击路径查看迁移分析</span>
          <span>滚轮缩放，拖拽查看全图</span>
        </div>
      </div>

      <div class="actions">
        <el-radio-group v-model="viewType" size="large" @change="handleViewChange">
          <el-radio-button label="vertical">纵向晋升图谱</el-radio-button>
          <el-radio-button label="lateral">横向转岗图谱</el-radio-button>
        </el-radio-group>

        <el-input v-model="keyword" class="search" clearable placeholder="搜索岗位名称" @input="renderChart">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </section>

    <section class="stats">
      <div class="stat-card">
        <span>当前起点</span>
        <strong>{{ activeData.startJobName }}</strong>
        <small>当前分析基准岗位</small>
      </div>
      <div class="stat-card">
        <span>路线数量</span>
        <strong>{{ stats.totalPaths }} 条</strong>
        <small>可切换高亮查看</small>
      </div>
      <div class="stat-card">
        <span>目标岗位</span>
        <strong>{{ stats.targetJobs }} 个</strong>
        <small>{{ viewType === 'vertical' ? '覆盖晋升阶段目标' : '覆盖横向发展方向' }}</small>
      </div>
      <div class="stat-card">
        <span>平均迁移成本</span>
        <strong>{{ stats.avgCost.toFixed(2) }}</strong>
        <small>{{ stats.avgCost <= 0.3 ? '迁移成本较低' : '建议分阶段推进' }}</small>
      </div>
    </section>

    <section class="chart-panel">
      <div class="panel-head">
        <div>
          <h2>{{ chartHeadline }}</h2>
          <p>{{ chartDescription }}</p>
        </div>

        <div class="legend">
          <span><i class="dot start"></i>当前岗位</span>
          <span><i class="dot vertical"></i>纵向节点</span>
          <span><i class="dot lateral"></i>横向节点</span>
        </div>
      </div>

      <div class="chart-stage-hints" :class="`chart-stage-hints--${viewType}`">
        <template v-if="viewType === 'vertical'">
          <span>当前岗位</span>
          <span>第一步晋升</span>
          <span>第二步晋升</span>
          <span>目标岗位</span>
        </template>
        <template v-else>
          <span>核心岗位</span>
          <span>相近方向</span>
          <span>潜力方向</span>
          <span>跨度较大方向</span>
        </template>
      </div>

      <div ref="chartRef" v-loading="loading" class="chart"></div>

      <div class="chart-toolbar">
        <div class="chart-toolbar__row">
          <p class="chart-tip">点击节点查看岗位详情，点击路径查看迁移分析；滚轮缩放，拖拽查看全图。</p>
          <div class="chart-tools">
            <button type="button" class="tool-btn" @click="zoomChart(0.12)">放大</button>
            <button type="button" class="tool-btn" @click="zoomChart(-0.12)">缩小</button>
            <button type="button" class="tool-btn" @click="resetChartView">重置视图</button>
            <button type="button" class="tool-btn" @click="focusStartJob">回到起点岗位</button>
            <button type="button" class="tool-btn tool-btn--accent" @click="highlightSelectedPath">高亮当前路径</button>
          </div>
        </div>
        <div class="chart-shortcuts">
          <button
            v-for="path in activeData.paths"
            :key="`${viewType}-${path.pathid}-shortcut`"
            type="button"
            class="shortcut-chip"
            :class="{ active: selectedPathId === path.pathid }"
            @click="selectPath(path)"
          >
            {{ path.pathTitle }}
          </button>
        </div>
      </div>
    </section>

    <section class="route-panel">
      <div class="route-header">
        <div>
          <h3>{{ viewType === 'vertical' ? '路线概览入口' : '转岗路线概览' }}</h3>
          <p>
            {{
              viewType === 'vertical'
                ? '这里仅保留路线概览与选择入口，详细结论请在右侧分析面板查看。'
                : '快速浏览不同转岗方向的成本、步数与一句话结论，深度分析统一收敛到右侧面板。'
            }}
          </p>
        </div>
        <el-tag type="info" effect="plain">当前高亮：{{ selectedPath?.pathTitle || '未选择' }}</el-tag>
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

          <div class="route-metrics">
            <span>总步数：{{ path.totalSteps }}</span>
            <span>迁移成本：{{ path.totalRoutingCost.toFixed(2) }}</span>
            <span>缺口：{{ path.steps.reduce((sum, step) => sum + step.skillGaps.length, 0) }} 项</span>
          </div>

          <div class="path-overview">
            <div class="box-title">路线一句话总结</div>
            <p class="route-summary">{{ path.overallSummary }}</p>
          </div>

          <div class="route-steps-preview">
            <div v-for="step in path.steps" :key="`${path.pathid}-${step.stepIndex}-${step.toJobid}`" class="step-preview">
              <strong>{{ step.fromJobName }} -> {{ step.toJobName }}</strong>
              <span>第 {{ step.stepIndex }} 步</span>
            </div>
          </div>

          <div class="route-footer">
            <span class="route-hint">{{ selectedPathId === path.pathid ? '当前已高亮该路线' : '点击可高亮路线并查看右侧详情' }}</span>
            <el-button size="small" type="primary" plain>查看分析</el-button>
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
          <button class="detail-panel__close" type="button" aria-label="关闭详情面板" @click="closeDetailPanel">×</button>
        </div>

        <div class="detail-panel__body">
          <template v-if="mode === 'node' && selectedNode">
            <div class="dialog-block detail-card detail-card--node">
              <div class="dialog-top">
                <h3>{{ selectedNode.name }}</h3>
                <el-tag :type="selectedNode.category === 'start' ? 'primary' : selectedNode.pathType === 'vertical' ? 'danger' : 'warning'">
                  {{
                    selectedNode.category === 'start'
                      ? '当前岗位'
                      : selectedNode.pathType === 'vertical'
                        ? '纵向晋升节点'
                        : '横向转岗节点'
                  }}
                </el-tag>
              </div>

              <div class="metric-grid metric-grid--node">
                <div class="metric-card">
                  <span>岗位 ID</span>
                  <strong>{{ selectedNode.jobId }}</strong>
                </div>
                <div class="metric-card">
                  <span>当前位置说明</span>
                  <strong>{{ selectedNode.levelText }}</strong>
                </div>
              </div>

              <div class="dialog-box dialog-box--cool">
                <div class="box-title">岗位角色说明</div>
                <p>
                  {{
                    selectedNode.category === 'start'
                      ? '这是当前分析的起点岗位，所有纵向晋升和横向转岗路线都围绕该岗位展开。'
                      : selectedNode.pathType === 'vertical'
                        ? '该岗位处于纵向晋升链路中，用于承接当前岗位的阶段性成长目标。'
                        : '该岗位是横向转岗网络中的一个目标方向，可用于比较迁移成本、技能跨度与发展空间。'
                  }}
                </p>
              </div>

              <div class="dialog-box">
                <div class="box-title">关联路线说明</div>
                <p v-if="selectedNode.relatedPathTitles.length">{{ selectedNode.relatedPathTitles.join('、') }}</p>
                <p v-else>当前节点暂无额外关联路线说明。</p>
              </div>
            </div>
          </template>

          <template v-else-if="mode === 'edge' && selectedEdge">
            <div class="dialog-block detail-card detail-card--hero">
              <div class="dialog-top">
                <h3>{{ selectedEdge.pathTitle }}</h3>
                <el-tag :type="selectedEdge.pathType === 'vertical' ? 'danger' : 'warning'">
                  {{ selectedEdge.pathType === 'vertical' ? '纵向晋升' : '横向转岗' }}
                </el-tag>
              </div>

              <div class="dialog-box dialog-box--warm">
                <div class="box-title">Agent 对整条路线的全局点评与风险提示</div>
                <p class="dialog-summary">{{ selectedEdge.overallSummary }}</p>
              </div>

              <div class="dialog-job-diff">
                <div class="job-box">
                  <span class="job-label">起点岗位</span>
                  <strong>{{ selectedEdge.fromJobName }}</strong>
                  <small>ID: {{ selectedEdge.source }}</small>
                </div>
                <div class="job-arrow">-></div>
                <div class="job-box target">
                  <span class="job-label">目标岗位</span>
                  <strong>{{ selectedEdge.toJobName }}</strong>
                  <small>ID: {{ selectedEdge.target }}</small>
                </div>
              </div>

              <div class="metric-grid">
                <div class="metric-card">
                  <span>总步数</span>
                  <strong>{{ selectedEdge.totalSteps }}</strong>
                </div>
                <div class="metric-card">
                  <span>当前步骤</span>
                  <strong>第 {{ selectedEdge.stepIndex }} 步</strong>
                </div>
                <div class="metric-card">
                  <span>迁移成本</span>
                  <strong>{{ selectedEdge.totalRoutingCost.toFixed(2) }}</strong>
                </div>
                <div class="metric-card">
                  <span>薪资增益</span>
                  <strong>{{ salary(selectedEdge.salaryGain) }}</strong>
                </div>
              </div>

              <div class="dialog-box dialog-box--cool">
                <div class="box-title">关键结论</div>
                <p>
                  这一步迁移的重点在于
                  <strong>{{ percent(selectedEdge.jaccardHigh) }}</strong>
                  的硬技能重合与
                  <strong>{{ percent(selectedEdge.cosLow) }}</strong>
                  的软素质契合度，适合先判断“是否值得走”和“需要补哪些能力”。
                </p>
              </div>
            </div>

            <div class="dialog-block detail-card">
              <div class="section-head">
                <div>
                  <h4>核心指标看板</h4>
                  <p>用图形化视图快速比较能力匹配度和岗位迁移收益。</p>
                </div>
              </div>

              <div class="metric-progress-grid">
                <div class="progress-card">
                  <div class="progress-card__head">
                    <span>硬技能重合</span>
                    <strong>{{ percent(selectedEdge.jaccardHigh) }}</strong>
                  </div>
                  <el-progress :percentage="Math.round(selectedEdge.jaccardHigh * 100)" :stroke-width="10" color="#ef4444" />
                </div>
                <div class="progress-card">
                  <div class="progress-card__head">
                    <span>软素质契合</span>
                    <strong>{{ percent(selectedEdge.cosLow) }}</strong>
                  </div>
                  <el-progress :percentage="Math.round(selectedEdge.cosLow * 100)" :stroke-width="10" color="#f59e0b" />
                </div>
              </div>

              <div ref="detailChartRef" class="detail-metric-chart"></div>
            </div>

            <div class="dialog-block detail-card">
              <div class="dialog-box dialog-box--cool">
                <div class="box-title">AI 推荐原因</div>
                <p>{{ selectedEdge.transitionReason }}</p>
              </div>
            </div>

            <div class="dialog-block detail-card">
              <div class="section-head">
                <div>
                  <h4>缺失技术 / 技能</h4>
                  <p>每个缺口都附带 JD 原文和可执行的学习建议。</p>
                </div>
                <el-tag type="info" effect="plain">共 {{ selectedEdge.skillGaps.length }} 项</el-tag>
              </div>

              <div class="gap-summary-bar">
                <span>缺失技能摘要</span>
                <strong>
                  {{
                    selectedEdge.skillGaps.length
                      ? selectedEdge.skillGaps.slice(0, 2).map((gap) => gap.competencyName || '能力补齐').join('、')
                      : '当前步骤暂无明显技能缺口'
                  }}
                </strong>
              </div>

              <el-empty v-if="!selectedEdge.skillGaps.length" description="当前步骤暂无明显技能缺口" />
              <div v-for="(gap, index) in selectedEdge.skillGaps" :key="`${selectedEdge.id}-dialog-gap-${index}`" class="gap-item">
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

            <div class="dialog-block detail-card" v-if="selectedEdge.skillGaps.length">
              <div class="section-head">
                <div>
                  <h4>行动建议</h4>
                  <p>建议先完成高优先级补齐项，再进入下一阶段路线推进。</p>
                </div>
              </div>
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
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
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
const detailChartRef = ref<HTMLElement | null>(null)
const detailChart = ref<echarts.ECharts | null>(null)
let chartResizeObserver: ResizeObserver | null = null
const loading = ref(false)
const viewType = ref<ViewType>('vertical')
const keyword = ref('')
const visible = ref(false)
const mode = ref<Mode>('node')
const dialogTitle = ref('')
const selectedNode = ref<GraphNodeData | null>(null)
const selectedEdge = ref<GraphEdgeData | null>(null)
const selectedPathId = ref('')
const graphZoom = ref(1)
const graphCenter = ref<[number, number] | null>(null)
const lastScrollY = ref(0)

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
      overallSummary: '这是一条标准的纵向晋升主干路线，风险较低，但需要持续补齐架构抽象、技术方案主导和跨团队影响力。',
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
          transitionReason: '当前岗位与中级前端工程师的核心技能重合度很高，是最自然、学习成本最低的一步晋升。',
          skillGaps: [
            {
              competencyName: '组件库建设',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '参与团队组件库建设与维护，能够沉淀可复用业务组件。',
              actionableAdvice: '独立抽象一组高复用业务组件，补齐文档、示例和发布流程。'
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
          transitionReason: '这一阶段更看重性能优化、复杂业务抽象和跨模块交付能力，需要从“能做”升级为“能主导”。',
          skillGaps: [
            {
              competencyName: '性能优化',
              category: '核心专业技能',
              targetScore: 4,
              originalContext: '掌握性能指标体系与前端性能优化方法，能够推动线上页面性能治理。',
              actionableAdvice: '完成一次性能专项治理，并用首屏时间、交互延迟等指标展示优化成果。'
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
          transitionReason: '从高级工程师进入架构师阶段，关键在于技术方案主导权、系统性架构视角和跨团队协作影响力。',
          skillGaps: [
            {
              competencyName: '微前端架构',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '主导过微前端拆分、落地与治理，并能沉淀统一规范。',
              actionableAdvice: '基于现有系统设计一版微前端拆分方案，并组织评审和小范围试点。'
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
      overallSummary: '这条路线偏向技术管理，成长重点不只是编码能力，还包括带人、技术规划和组织协同。',
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
          transitionReason: '该岗位除了技术能力，也要求你开始承担带教、任务拆解和项目推进职责。',
          skillGaps: [
            {
              competencyName: '团队管理',
              category: '软技能',
              targetScore: 3,
              originalContext: '具备带教新人或小团队协作管理经验，能够推动团队稳定交付。',
              actionableAdvice: '主动承担新人培养、需求拆解和迭代节奏管理，积累小团队协作案例。'
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
          transitionReason: '岗位关注点会从单项目交付转向团队规划、技术治理和资源协调，对战略视角要求更高。',
          skillGaps: [
            {
              competencyName: '技术规划',
              category: '战略能力',
              targetScore: 4,
              originalContext: '能够制定季度或年度技术演进路线，并推动多团队共识和落地。',
              actionableAdvice: '梳理团队技术债，沉淀季度技术演进计划，并输出优先级和推进节奏。'
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
      pathTitle: '前端 -> Node 后端：全栈能力跃迁路线',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.35,
      overallSummary: '这是一条低风险转岗路线，适合希望向全栈发展、并愿意补齐服务端基础设施能力的前端工程师。',
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
          transitionReason: '工程化能力和业务理解可以直接迁移，但服务端缓存、数据库和部署治理仍是主要门槛。',
          skillGaps: [
            {
              competencyName: 'Redis',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '熟练使用 Redis 进行高并发缓存设计，并理解缓存击穿、雪崩与一致性问题。',
              actionableAdvice: '实现一个带缓存层的 Node 服务，补齐缓存淘汰策略和穿透防护。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_002',
      pathTitle: '前端 -> 技术产品经理：需求转译者成长路线',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.75,
      overallSummary: '适合对用户价值、业务需求和跨团队协作更感兴趣的工程师，但需要补齐需求表达和产品方法论。',
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
          transitionReason: '软素质契合度较高，但产品岗位对结构化表达、需求抽象和业务方案设计要求更强。',
          skillGaps: [
            {
              competencyName: 'PRD 编写',
              category: '工具与平台能力',
              targetScore: 4,
              originalContext: '熟练输出高质量 PRD、流程图和高保真原型，能准确表达产品方案。',
              actionableAdvice: '选一个熟悉项目，逆向补齐 PRD、业务流程图和核心页面原型。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_003',
      pathTitle: '前端 -> UI/UX 设计师：体验设计转型路线',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.55,
      overallSummary: '前端对界面实现和交互细节本身就敏感，具备一定的体验设计转型基础，但需要系统补齐设计方法。',
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
          transitionReason: '你对界面实现已有优势，但仍需补齐设计工具、视觉表达和用户研究方法。',
          skillGaps: [
            {
              competencyName: 'Figma',
              category: '设计工具',
              targetScore: 4,
              originalContext: '熟练使用 Figma 完成高保真界面设计、组件规范和协同交付。',
              actionableAdvice: '使用 Figma 重做现有模块界面，并沉淀一套基础设计组件。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_004',
      pathTitle: '前端 -> DevOps 工程师：工程效率优化路线',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.45,
      overallSummary: '这条路线更偏工程基础设施与交付效率，适合对 CI/CD、部署与平台化建设感兴趣的工程师。',
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
          transitionReason: '工程化认知可以迁移，但容器编排、基础设施治理和平台运维能力仍需补齐。',
          skillGaps: [
            {
              competencyName: 'Kubernetes',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '掌握 Kubernetes 容器编排、服务发现和集群基础运维能力。',
              actionableAdvice: '本地搭建最小可运行 K8s 集群，并部署一个演示服务验证发布流程。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_005',
      pathTitle: '前端 -> 数据分析师：数据驱动决策路线',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.65,
      overallSummary: '适合对数据可视化、指标分析和业务决策有兴趣的工程师，但需要补齐分析方法和数据处理能力。',
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
          transitionReason: '可视化表达与业务理解是优势，但 SQL、统计分析和数据清洗能力是核心补差点。',
          skillGaps: [
            {
              competencyName: 'SQL / Python',
              category: '数据处理',
              targetScore: 4,
              originalContext: '能够使用 SQL 和 Python 处理分析型数据，并输出结构化结论。',
              actionableAdvice: '完成一个用户行为分析小项目，输出分析结论、图表和决策建议。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'lateral_006',
      pathTitle: '前端 -> 测试开发工程师：质量保障专家路线',
      pathType: 'lateral',
      totalSteps: 1,
      totalRoutingCost: 0.4,
      overallSummary: '适合关注质量体系、自动化测试和稳定性建设的前端工程师，转型门槛相对可控。',
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
          transitionReason: '代码理解、边界意识和自动化思维让前端具备天然优势，但仍需系统补齐测试工具链能力。',
          skillGaps: [
            {
              competencyName: '自动化测试框架',
              category: '测试技能',
              targetScore: 4,
              originalContext: '掌握 Cypress、Playwright 或 Selenium 等自动化测试工具，并能搭建完整流程。',
              actionableAdvice: '为当前项目搭建一套 E2E 自动化测试流程，并输出可追踪的测试报告。'
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

const selectedPath = computed(() => activeData.value.paths.find((path) => path.pathid === selectedPathId.value) ?? activeData.value.paths[0] ?? null)

const selectedStep = computed(() => {
  if (!selectedPath.value) return null
  if (selectedEdge.value) {
    return (
      selectedPath.value.steps.find(
        (step) => step.stepIndex === selectedEdge.value?.stepIndex && step.toJobid === selectedEdge.value?.target,
      ) ?? selectedPath.value.steps[0] ?? null
    )
  }
  return selectedPath.value.steps[0] ?? null
})

const chartHeadline = computed(() =>
  viewType.value === 'vertical' ? '纵向晋升路线图谱' : '横向转岗路线图谱',
)

const chartDescription = computed(() =>
  viewType.value === 'vertical'
    ? '纵向图按晋升阶段分层展示，重点突出当前岗位、关键跃迁节点和最终目标岗位。'
    : '横向图围绕当前岗位展开，重点对比不同转岗方向的迁移成本、技能跨度与长期发展潜力。',
)

const selectedPathSummary = computed(() => {
  const path = selectedPath.value
  if (!path) {
    return {
      title: '暂无选中路线',
      conclusion: '点击图谱中的节点、路径或下方快捷入口查看详细分析。',
      action: '可通过搜索岗位、切换图谱模式或使用快捷入口快速定位目标路线。',
      missingCount: 0,
      tags: [] as string[],
    }
  }

  const gaps = path.steps.flatMap((step) => step.skillGaps)
  const tags = [
    path.totalRoutingCost <= 0.25 ? '低成本迁移' : path.totalRoutingCost <= 0.45 ? '中等迁移成本' : '技能跨度较大',
    path.pathType === 'vertical' ? '更适合阶段晋升' : path.totalSteps <= 1 ? '快速转岗方向' : '更适合长期发展',
  ]

  return {
    title: path.pathTitle,
    conclusion: path.overallSummary,
    action:
      gaps[0]?.actionableAdvice ||
      '建议先点击右侧分析面板查看关键结论，再结合缺失技能安排下一阶段学习重点。',
    missingCount: gaps.length,
    tags,
  }
})

const percent = (value: number) => `${(value * 100).toFixed(0)}%`
const salary = (value: number) => (value > 0 ? `+${percent(value)}` : percent(value))

function restoreScrollPosition() {
  window.scrollTo({ top: lastScrollY.value, behavior: 'auto' })
}

function renderDetailChart() {
  if (!detailChartRef.value || !selectedEdge.value || mode.value !== 'edge' || !visible.value) {
    detailChart.value?.dispose()
    detailChart.value = null
    return
  }

  if (!detailChart.value) {
    detailChart.value = echarts.init(detailChartRef.value)
  }

  detailChart.value.setOption(
    {
      backgroundColor: 'transparent',
      animationDuration: 280,
      grid: {
        top: 20,
        right: 12,
        bottom: 20,
        left: 12,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['硬技能', '软素质', '薪资增益', '迁移成本'],
        axisTick: { show: false },
        axisLine: { lineStyle: { color: '#dbe3f0' } },
        axisLabel: { color: '#64748b', fontSize: 11 }
      },
      yAxis: {
        type: 'value',
        max: 100,
        splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.16)' } },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        min: 0
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      series: [
        {
          type: 'bar',
          barWidth: 26,
          data: [
            { value: Math.round(selectedEdge.value.jaccardHigh * 100), itemStyle: { color: '#ef4444', borderRadius: [8, 8, 0, 0] } },
            { value: Math.round(selectedEdge.value.cosLow * 100), itemStyle: { color: '#f59e0b', borderRadius: [8, 8, 0, 0] } },
            {
              value: Math.max(0, Math.min(100, Math.round((selectedEdge.value.salaryGain + 0.2) * 100))),
              itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] }
            },
            {
              value: Math.max(0, Math.min(100, Math.round((1 - selectedEdge.value.totalRoutingCost) * 100))),
              itemStyle: { color: '#3b82f6', borderRadius: [8, 8, 0, 0] }
            }
          ],
          label: {
            show: true,
            position: 'top',
            color: '#475569',
            fontSize: 11,
            formatter: '{c}%'
          }
        }
      ]
    } as echarts.EChartsOption,
    true
  )
}

function openEdgeDetail(path: Path, step: Step) {
  lastScrollY.value = window.scrollY
  selectedPathId.value = path.pathid
  mode.value = 'edge'
  selectedNode.value = null
  selectedEdge.value = {
    id: `${path.pathid}-${step.stepIndex}-panel`,
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
    lineStyle: {},
    label: {}
  }
  dialogTitle.value = path.pathTitle
  visible.value = true
}

function openNodeDetail(node: GraphNodeData) {
  lastScrollY.value = window.scrollY
  mode.value = 'node'
  selectedNode.value = node
  selectedEdge.value = null
  dialogTitle.value = node.name
  visible.value = true
}

function selectPath(path: Path) {
  const firstStep = path.steps[0]
  if (!firstStep) return
  openEdgeDetail(path, firstStep)
}

function handleViewChange() {
  selectedPathId.value = activeData.value.paths[0]?.pathid ?? ''
  visible.value = false
  selectedNode.value = null
  selectedEdge.value = null
  renderChart()
}

function closeDetailPanel() {
  lastScrollY.value = window.scrollY
  visible.value = false

  nextTick(() => {
    restoreScrollPosition()
    chart.value?.resize()

    requestAnimationFrame(() => {
      restoreScrollPosition()
      chart.value?.resize()
      renderChart()
    })

    window.setTimeout(() => {
      restoreScrollPosition()
      chart.value?.resize()
      renderChart()
    }, 260)
  })
}

function zoomChart(delta: number) {
  graphZoom.value = Math.max(0.65, Math.min(1.8, Number((graphZoom.value + delta).toFixed(2))))
  renderChart()
}

function resetChartView() {
  graphZoom.value = 1
  graphCenter.value = null
  renderChart()
}

function focusStartJob() {
  graphZoom.value = 1
  graphCenter.value = null
  selectedPathId.value = activeData.value.paths[0]?.pathid ?? ''
  renderChart()
}

function highlightSelectedPath() {
  if (!selectedPathId.value) {
    selectedPathId.value = activeData.value.paths[0]?.pathid ?? ''
  }
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
  const selectedPaths = data.paths.filter((path) => path.pathid === selectedPathId.value)

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
      show: true,
      position: 'bottom',
      distance: 12,
      color: '#0f172a',
      fontSize: 12,
      fontWeight: 'bold',
      width: 108,
      overflow: 'break',
      lineHeight: 16,
      backgroundColor: 'rgba(255, 255, 255, 0.92)',
      borderRadius: 10,
      padding: [6, 8],
      shadowBlur: 10,
      shadowColor: 'rgba(15, 23, 42, 0.08)'
    }
  }

  nodes.push(startNode)
  nodeMap.set(startNode.id, startNode)

  data.paths.forEach((path, pathIndex) => {
    path.steps.forEach((step, stepOrder) => {
      const isSelectedPath = selectedPathId.value === path.pathid

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
          levelText:
            viewType.value === 'vertical'
              ? step.stepIndex === 1
                ? '第一步晋升'
                : step.stepIndex === levels.length
                  ? '目标岗位'
                  : `第 ${step.stepIndex} 级节点`
              : path.totalRoutingCost <= 0.25
                ? '低成本迁移方向'
                : path.totalRoutingCost >= 0.45
                  ? '技能跨度较大'
                  : '横向转岗目标',
          relatedPathTitles: [],
          symbolSize: viewType.value === 'vertical' ? 68 + Math.max(0, levels.length - step.stepIndex) * 2 : 64,
          x: viewType.value === 'vertical' ? 420 + levelIndex * 180 + (pathIndex % 2 === 0 ? -50 : 50) : 460 + Math.cos(angle) * 270,
          y: viewType.value === 'vertical' ? 120 + levelIndex * 120 + (pathIndex % 3) * 24 : 320 + Math.sin(angle) * 200,
          itemStyle: nodeStyle('target', path.pathType),
          label: {
            show: true,
            position: 'bottom',
            distance: 12,
            color: '#0f172a',
            fontSize: 12,
            fontWeight: 'bold',
            width: 108,
            overflow: 'break',
            lineHeight: 16,
            backgroundColor: 'rgba(255, 255, 255, 0.94)',
            borderRadius: 10,
            padding: [6, 8],
            shadowBlur: 10,
            shadowColor: 'rgba(15, 23, 42, 0.08)'
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
          width: isSelectedPath ? 6 : 3,
          type: path.pathType === 'vertical' ? 'solid' : 'dashed',
          opacity: selectedPathId.value ? (isSelectedPath ? 1 : 0.2) : 0.78,
          curveness: viewType.value === 'vertical' ? 0.04 : 0.2
        },
        label: {
          show: true,
          formatter: path.pathType === 'vertical' ? `晋升 ${step.stepIndex}` : '转岗',
          color: isSelectedPath ? '#111827' : '#6b7280',
          fontSize: isSelectedPath ? 12 : 11,
          fontWeight: isSelectedPath ? 'bold' : 'normal',
          backgroundColor: isSelectedPath ? 'rgba(255, 255, 255, 0.92)' : 'transparent',
          padding: isSelectedPath ? [4, 8] : 0,
          borderRadius: isSelectedPath ? 999 : 0
        }
      })
    })
  })

  const text = keyword.value.trim().toLowerCase()
  nodes.forEach((node) => {
    node.relatedPathTitles = [...(pathMap.get(node.id) ?? new Set<string>())]

    const isPathSelected =
      node.id === data.startJobid || selectedPaths.some((path) => path.steps.some((step) => step.toJobid === node.id))

    if (isPathSelected) {
      node.itemStyle = {
        ...node.itemStyle,
        opacity: 1,
        shadowBlur: 24,
        shadowColor:
          node.category === 'start'
            ? 'rgba(29, 78, 216, 0.35)'
            : node.pathType === 'vertical'
              ? 'rgba(239, 68, 68, 0.24)'
              : 'rgba(245, 158, 11, 0.24)'
      }
      node.symbolSize = node.category === 'start' ? 84 : node.symbolSize + 6
    } else if (selectedPathId.value) {
      node.itemStyle = {
        ...node.itemStyle,
        opacity: 0.3
      }
    }

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

  const currentOption = chart.value.getOption() as any
  const currentSeries = currentOption?.series?.[0]

  if (typeof currentSeries?.zoom === 'number') {
    graphZoom.value = currentSeries.zoom
  }

  if (Array.isArray(currentSeries?.center) && currentSeries.center.length === 2) {
    graphCenter.value = [currentSeries.center[0], currentSeries.center[1]]
  }

  const { nodes, edges } = buildGraph(activeData.value)
  chart.value.setOption(
    {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            return `
              <strong>${params.data.name}</strong><br/>
              节点类型：${params.data.category === 'start' ? '当前岗位' : params.data.pathType === 'vertical' ? '晋升节点' : '转岗目标'}<br/>
              所属路线数：${params.data.relatedPathTitles?.length ?? 0}
            `
          }

          return `
            <strong>${params.data.fromJobName} -> ${params.data.toJobName}</strong><br/>
            路径：${params.data.pathTitle}<br/>
            迁移成本：${Number(params.data.totalRoutingCost).toFixed(2)}<br/>
            技能重合：${Math.round((params.data.jaccardHigh || 0) * 100)}%
          `
        }
      },
      series: [
        {
          id: 'career-map-graph',
          type: 'graph',
          layout: 'none',
          roam: true,
          zoom: graphZoom.value,
          center: graphCenter.value ?? undefined,
          draggable: true,
          focusNodeAdjacency: true,
          edgeSymbol: ['none', 'arrow'],
          edgeSymbolSize: 12,
          data: nodes,
          links: edges,
          lineStyle: { opacity: 0.9 },
          emphasis: {
            focus: 'adjacency',
            scale: true,
            lineStyle: { width: 8, opacity: 1 }
          }
        }
      ]
    } as echarts.EChartsOption,
    false
  )
}

function initChart() {
  if (!chartRef.value) return

  chart.value?.dispose()
  chart.value = echarts.init(chartRef.value)
  chart.value.on('graphRoam', () => {
    const option = chart.value?.getOption() as any
    const series = option?.series?.[0]

    if (!series) return

    if (typeof series.zoom === 'number') {
      graphZoom.value = series.zoom
    }

    if (Array.isArray(series.center) && series.center.length === 2) {
      graphCenter.value = [series.center[0], series.center[1]]
    }
  })
  chart.value.on('click', (params: any) => {
    if (params.dataType === 'node') {
      openNodeDetail(params.data as GraphNodeData)
      return
    }

    if (params.dataType === 'edge') {
      const edge = params.data as GraphEdgeData
      const path = activeData.value.paths.find((item) => item.pathTitle === edge.pathTitle)
      const step = path?.steps.find((item) => item.stepIndex === edge.stepIndex && item.toJobid === edge.target)

      if (path && step) {
        openEdgeDetail(path, step)
        return
      }

      selectedPathId.value = path?.pathid ?? selectedPathId.value
      mode.value = 'edge'
      selectedEdge.value = edge
      selectedNode.value = null
      dialogTitle.value = edge.pathTitle
      visible.value = true
      renderChart()
    }
  })

  renderChart()
}

function handleResize() {
  chart.value?.resize()
  detailChart.value?.resize()
}

function scheduleChartResize() {
  nextTick(() => {
    chart.value?.resize()
    detailChart.value?.resize()

    requestAnimationFrame(() => {
      chart.value?.resize()
      detailChart.value?.resize()
    })

    window.setTimeout(() => {
      chart.value?.resize()
      detailChart.value?.resize()
    }, 240)
  })
}

onMounted(() => {
  selectedPathId.value = activeData.value.paths[0]?.pathid ?? ''
  initChart()

  if (chartRef.value && typeof ResizeObserver !== 'undefined') {
    chartResizeObserver = new ResizeObserver(() => {
      chart.value?.resize()
    })
    chartResizeObserver.observe(chartRef.value)
  }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartResizeObserver?.disconnect()
  chart.value?.dispose()
  detailChart.value?.dispose()
})

watch([visible, mode, selectedEdge], async ([isVisible, currentMode, edge]) => {
  if (!isVisible || currentMode !== 'edge' || !edge) {
    detailChart.value?.dispose()
    detailChart.value = null
    return
  }

  await nextTick()
  renderDetailChart()
})

watch(visible, () => {
  scheduleChartResize()
  nextTick(() => {
    restoreScrollPosition()
  })
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
  padding: 22px 24px;
  border-radius: 24px;
  margin-bottom: 18px;
}

.hero-copy {
  display: flex;
  flex-direction: column;
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
  margin: 10px 0 0;
  max-width: 760px;
  color: #4b5563;
  line-height: 1.75;
}

.hero-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.hero-hints span {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: #33517a;
  font-size: 12px;
  font-weight: 600;
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
  padding: 16px 18px;
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

.stat-card small {
  display: block;
  margin-top: 8px;
  color: #94a3b8;
  font-size: 12px;
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

.chart-stage-hints {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.chart-stage-hints span {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0 12px;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(245, 248, 255, 0.98));
  border: 1px solid rgba(219, 231, 245, 0.96);
  color: #4b5563;
  font-size: 13px;
  font-weight: 700;
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

.dot.start {
  background: #1d4ed8;
}

.dot.vertical {
  background: #ef4444;
}

.dot.lateral {
  background: #f59e0b;
}

.chart {
  height: 760px;
  border-radius: 20px;
  background:
    linear-gradient(rgba(148, 163, 184, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.05) 1px, transparent 1px),
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  background-size: 42px 42px, 42px 42px, auto;
  overflow: hidden;
}

.chart-toolbar {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-toolbar__row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.chart-tip {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

.chart-tools {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.tool-btn {
  border: 1px solid #dbe3f0;
  background: #ffffff;
  color: #334155;
  border-radius: 999px;
  padding: 9px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-btn:hover {
  border-color: #93c5fd;
  color: #1d4ed8;
  transform: translateY(-1px);
}

.tool-btn--accent {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

.chart-shortcuts {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.shortcut-chip {
  border: 1px solid #dbe3f0;
  background: #ffffff;
  color: #334155;
  border-radius: 999px;
  padding: 10px 14px;
  font-size: 13px;
  line-height: 1.4;
  cursor: pointer;
  transition: all 0.2s ease;
}

.shortcut-chip:hover {
  border-color: #94a3b8;
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.08);
}

.shortcut-chip.active {
  border-color: #f59e0b;
  background: #fff7ed;
  color: #9a3412;
  box-shadow: 0 10px 24px rgba(245, 158, 11, 0.16);
}

.route-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.route-card {
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 16px;
  background: #ffffff;
  cursor: pointer;
  transition: 0.2s ease;
}

.route-card.active,
.route-card:hover {
  border-color: #f59e0b;
  box-shadow: 0 14px 30px rgba(245, 158, 11, 0.12);
  transform: translateY(-2px);
}

.route-top,
.dialog-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.route-top h4,
.dialog-top h3 {
  margin: 0;
  color: #111827;
}

.path-overview {
  margin-top: 12px;
  padding: 13px 14px;
  background: #f8fbff;
  border: 1px solid #dbeafe;
  border-radius: 16px;
}

.route-summary,
.dialog-summary {
  margin: 0;
  line-height: 1.7;
  color: #475569;
}

.route-metrics,
.score-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  color: #6b7280;
  font-size: 13px;
}

.route-steps-preview {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}

.step-preview {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 11px 12px;
  border-radius: 14px;
  background: #f8fafc;
  color: #475569;
  font-size: 13px;
}

.step-preview strong {
  color: #111827;
  font-size: 13px;
  font-weight: 700;
}

.route-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-top: 14px;
}

.route-hint {
  color: #64748b;
  font-size: 12px;
}

.job-diff,
.dialog-job-diff {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
  align-items: center;
  margin-top: 14px;
}

.job-box {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 14px;
  background: #f8fafc;
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

.gap-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
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

.detail-card {
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
}

.detail-card--hero {
  background:
    radial-gradient(circle at top right, rgba(251, 191, 36, 0.18), transparent 24%),
    linear-gradient(180deg, #ffffff 0%, #fffaf2 100%);
}

.detail-card--node {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.16), transparent 26%),
    linear-gradient(180deg, #ffffff 0%, #f4f9ff 100%);
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.section-head h4 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #0f172a;
}

.section-head p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
  font-size: 13px;
}

.dialog-box--warm {
  background: linear-gradient(180deg, #fff7ed 0%, #fffbf4 100%);
  border: 1px solid #fed7aa;
}

.dialog-box--cool {
  background: linear-gradient(180deg, #f8fbff 0%, #f1f7ff 100%);
  border: 1px solid #dbeafe;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.metric-grid--node {
  margin-top: 16px;
}

.metric-card {
  padding: 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.metric-card span {
  display: block;
  color: #64748b;
  font-size: 12px;
  margin-bottom: 6px;
}

.metric-card strong {
  color: #0f172a;
  font-size: 20px;
}

.metric-progress-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.progress-card {
  padding: 14px;
  border-radius: 16px;
  background: #ffffff;
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.progress-card__head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
  color: #475569;
  font-size: 13px;
}

.progress-card__head strong {
  color: #0f172a;
}

.detail-metric-chart {
  height: 220px;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.9), rgba(255, 255, 255, 0.95));
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.node-descriptions :deep(.el-descriptions__label) {
  width: 88px;
  color: #475569;
  font-weight: 600;
}

.node-descriptions :deep(.el-descriptions__content) {
  color: #0f172a;
}

.detail-panel {
  position: fixed;
  top: 88px;
  right: 20px;
  bottom: 20px;
  width: min(560px, calc(100vw - 32px));
  z-index: 80;
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
  width: 38px;
  height: 38px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(255, 255, 255, 0.9);
  color: #334155;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  cursor: pointer;
  font-size: 24px;
  line-height: 1;
  transition: all 0.2s ease;
}

.detail-panel__close:hover {
  background: #111827;
  color: #ffffff;
  border-color: #111827;
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

.dialog-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #6b7280;
  font-size: 13px;
  margin-top: 14px;
}

.gap-summary-bar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
  padding: 12px 14px;
  border-radius: 14px;
  background: #fffaf0;
  border: 1px solid #fde68a;
}

.gap-summary-bar span {
  color: #92400e;
  font-size: 12px;
  font-weight: 700;
}

.gap-summary-bar strong {
  color: #7c2d12;
  font-size: 13px;
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
  .chart-toolbar__row,
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

  .chart-stage-hints,
  .route-grid {
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

  .chart-stage-hints,
  .route-grid,
  .metric-grid,
  .metric-progress-grid {
    grid-template-columns: 1fr;
  }

  .job-diff,
  .dialog-job-diff {
    grid-template-columns: 1fr;
  }

  .job-arrow {
    display: none;
  }

  .detail-panel {
    top: auto;
    right: 12px;
    bottom: calc(12px + env(safe-area-inset-bottom, 0px));
    left: 12px;
    width: auto;
    max-height: min(68vh, 720px);
    border-radius: 22px;
  }

  .detail-panel__header {
    padding: 16px 16px 12px;
  }

  .detail-panel__title h3 {
    font-size: 18px;
  }

  .detail-panel__body {
    padding: 16px;
  }

  .route-footer,
  .gap-summary-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .detail-slide-enter-from,
  .detail-slide-leave-to {
    opacity: 0;
    transform: translateY(24px);
  }
}
</style>
