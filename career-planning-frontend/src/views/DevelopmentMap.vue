<template>
  <div class="career-path-graph">
    <!-- 头部控制区 -->
    <div class="header-section">
      <div class="title-area">
        <h2 class="main-title">
          <el-icon><Connection /></el-icon>
          职业发展路径图谱
        </h2>
        <p class="sub-title">智能规划您的职业未来 - 垂直晋升与横向转岗全景视图</p>
      </div>
      
      <div class="controls">
        <el-radio-group v-model="currentView" size="large" @change="handleViewChange">
          <el-radio-button label="vertical">
            <el-icon><Top /></el-icon>
            垂直晋升图谱
          </el-radio-button>
          <el-radio-button label="lateral">
            <el-icon><Switch /></el-icon>
            横向换岗图谱
          </el-radio-button>
        </el-radio-group>
        
        <el-input
          v-model="searchKeyword"
          placeholder="搜索岗位名称"
          class="search-input"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 图谱展示区 -->
      <div class="graph-container" v-loading="loading">
        <div ref="chartRef" class="chart-instance"></div>
        
        <!-- 图谱图例 -->
        <div class="graph-legend">
          <div class="legend-item">
            <span class="legend-dot start-node"></span>
            <span>当前岗位</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot target-node"></span>
            <span>目标岗位</span>
          </div>
          <div class="legend-item">
            <span class="legend-line vertical-line"></span>
            <span>晋升路径</span>
          </div>
          <div class="legend-item">
            <span class="legend-line lateral-line"></span>
            <span>转岗路径</span>
          </div>
        </div>
      </div>

      <!-- 侧边详情面板 -->
      <transition name="slide-fade">
        <div v-if="selectedNode || selectedEdge" class="detail-panel">
          <!-- 节点详情 -->
          <div v-if="selectedNode" class="node-detail">
            <div class="panel-header">
              <h3>{{ selectedNode.name }}</h3>
              <el-tag :type="getNodeType(selectedNode)" size="small">
                {{ getNodeTypeText(selectedNode) }}
              </el-tag>
              <el-button 
                circle 
                size="small" 
                class="close-btn"
                @click="selectedNode = null"
              >
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            
            <div class="panel-content">
              <div class="info-section">
                <h4>岗位信息</h4>
                <p><strong>岗位ID:</strong> {{ selectedNode.jobId }}</p>
                <p v-if="selectedNode.category"><strong>所属类别:</strong> {{ selectedNode.category }}</p>
              </div>
            </div>
          </div>

          <!-- 路径/边详情 -->
          <div v-if="selectedEdge" class="edge-detail">
            <div class="panel-header">
              <h3>{{ selectedEdge.pathTitle }}</h3>
              <el-tag :type="selectedEdge.pathType === 'vertical' ? 'danger' : 'warning'" size="small">
                {{ selectedEdge.pathType === 'vertical' ? '垂直晋升' : '横向转岗' }}
              </el-tag>
              <el-button 
                circle 
                size="small" 
                class="close-btn"
                @click="selectedEdge = null"
              >
                <el-icon><Close /></el-icon>
              </el-button>
            </div>

            <div class="panel-content">
              <div class="summary-section">
                <h4>路径概述</h4>
                <p class="summary-text">{{ selectedEdge.overallSummary }}</p>
              </div>

              <div class="metrics-section">
                <h4>路径指标</h4>
                <div class="metrics-grid">
                  <div class="metric-item">
                    <span class="metric-label">演化阻力</span>
                    <el-progress 
                      :percentage="selectedEdge.totalRoutingCost * 100" 
                      :color="getCostColor(selectedEdge.totalRoutingCost)"
                      :format="() => selectedEdge.totalRoutingCost.toFixed(2)"
                    />
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">步骤数</span>
                    <el-tag type="info">{{ selectedEdge.totalSteps }} 步</el-tag>
                  </div>
                </div>
              </div>

              <div class="transition-section">
                <h4>转换详情</h4>
                <div class="transition-flow">
                  <div class="flow-node">{{ selectedEdge.fromJobName }}</div>
                  <div class="flow-arrow">
                    <el-icon><Right /></el-icon>
                  </div>
                  <div class="flow-node target">{{ selectedEdge.toJobName }}</div>
                </div>
                
                <div class="transition-reason">
                  <el-alert
                    :title="'转换分析'"
                    :description="selectedEdge.transitionReason"
                    type="info"
                    :closable="false"
                    show-icon
                  />
                </div>

                <div class="skills-section">
                  <h4>技能缺口与建议</h4>
                  <div 
                    v-for="(gap, index) in selectedEdge.skillGaps" 
                    :key="index"
                    class="skill-gap-item"
                  >
                    <div class="skill-header">
                      <span class="skill-name">{{ gap.competencyName }}</span>
                      <el-tag size="small" type="warning">{{ gap.category }}</el-tag>
                    </div>
                    <div class="skill-context" v-if="gap.originalContext">
                      <el-text type="info" size="small">要求: {{ gap.originalContext }}</el-text>
                    </div>
                    <div class="skill-advice">
                      <el-icon><InfoFilled /></el-icon>
                      <span>{{ gap.actionableAdvice }}</span>
                    </div>
                    <el-divider v-if="selectedEdge.skillGaps && (index as number) < selectedEdge.skillGaps.length - 1" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 统计信息区 -->
    <div class="stats-section" v-if="currentStats">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="可选路径总数" :value="currentStats.totalPaths">
            <template #suffix>条</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="目标岗位数" :value="currentStats.targetJobs">
            <template #suffix>个</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="平均演化阻力" :value="currentStats.avgCost" :precision="2" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="技能缺口总数" :value="currentStats.totalSkillGaps">
            <template #suffix>项</template>
          </el-statistic>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { 
  Connection, 
  Top, 
  Switch, 
  Search, 
  Close, 
  Right, 
  InfoFilled 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 类型定义（基于文档提供的接口）
interface SkillGap {
  competencyName: string
  category: string
  targetScore?: number
  originalContext?: string
  actionableAdvice: string
}

interface Step {
  stepIndex: number
  fromJobid: string
  fromJobName: string
  toJobid: string
  toJobName: string
  jaccardHigh: number
  cosLow: number
  salaryGain: number
  transitionReason: string
  skillGaps: SkillGap[]
}

interface Path {
  pathid: string
  pathType: 'vertical' | 'lateral'
  pathTitle: string
  totalSteps: number
  totalRoutingCost: number
  overallSummary: string
  steps: Step[]
}

interface CareerData {
  startJobid: string
  startJobName: string
  paths: Path[]
}

// 响应式状态
const chartRef = ref<HTMLElement>()
const chartInstance = ref<echarts.ECharts | null>(null)
const currentView = ref<'vertical' | 'lateral'>('vertical')
const loading = ref(false)
const searchKeyword = ref('')
const selectedNode = ref<any>(null)
const selectedEdge = ref<any>(null)

// 模拟数据 - 垂直晋升路径
const verticalData = ref<CareerData>({
  startJobid: 'job_002',
  startJobName: '前端开发工程师',
  paths: [
    {
      pathid: 'path_001',
      pathType: 'vertical',
      pathTitle: '前端架构跃迁路线：从开发工程师到资深架构师',
      totalSteps: 3,
      totalRoutingCost: 0.15,
      overallSummary: '本路径为纯垂直晋升链，直指高影响力架构角色，体现图谱对真实能力跃迁节奏的精准建模。',
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
          transitionReason: '具备高硬技能重合度与强软素质契合度，是基础晋升通道。',
          skillGaps: [
            {
              competencyName: '组件库建设',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '参与团队组件库建设与维护',
              actionableAdvice: '主导搭建业务组件库，制定开发规范，输出文档。'
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
          transitionReason: '技术深度与业务理解的双重提升，进入核心开发层。',
          skillGaps: [
            {
              competencyName: '性能优化',
              category: '核心专业技能',
              targetScore: 4,
              originalContext: '精通前端性能优化策略与实施',
              actionableAdvice: '完成一次全链路性能优化项目，达成FCP/LCP指标提升50%。'
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
          transitionReason: '具备架构设计能力与技术决策权，是技术线的顶端角色。',
          skillGaps: [
            {
              competencyName: '前端微服务架构',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '主导过前端微服务(Qiankun)拆分与落地',
              actionableAdvice: '独立主导基于Qiankun的微前端落地项目，输出技术方案文档。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'path_002',
      pathType: 'vertical',
      pathTitle: '技术管理路线：从开发到前端负责人',
      totalSteps: 2,
      totalRoutingCost: 0.25,
      overallSummary: '适合具备沟通协调能力的技术人才转向管理赛道。',
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
          transitionReason: '技术能力与管理潜质的结合，开始承担团队协调职责。',
          skillGaps: [
            {
              competencyName: '团队管理',
              category: '软技能',
              targetScore: 3,
              originalContext: '具备3人以上团队管理经验',
              actionableAdvice: '主动申请担任实习生导师，参与招聘面试流程。'
            }
          ]
        },
        {
          stepIndex: 2,
          fromJobid: 'job_002_lead',
          fromJobName: '前端技术主管',
          toJobid: 'job_002_director',
          toJobName: '前端技术总监',
          jaccardHigh: 0.6,
          cosLow: 0.8,
          salaryGain: 0.6,
          transitionReason: '全局技术视野与战略决策能力，负责前端整体技术规划。',
          skillGaps: [
            {
              competencyName: '技术规划',
              category: '战略能力',
              targetScore: 4,
              originalContext: '制定前端技术栈演进路线图',
              actionableAdvice: '撰写团队年度技术规划文档，组织技术分享与架构评审。'
            }
          ]
        }
      ]
    }
  ]
})

// 模拟数据 - 横向换岗路径（满足至少5个岗位，每岗2条路径的要求）
const lateralData = ref<CareerData>({
  startJobid: 'job_002',
  startJobName: '前端开发工程师',
  paths: [
    {
      pathid: 'path_lat_001',
      pathType: 'lateral',
      pathTitle: '前端→Node后端：全栈能力跃迁路线',
      totalSteps: 1,
      totalRoutingCost: 0.35,
      overallSummary: '基于全网数据验证的最优横向路径，仅需补齐一项关键后端中间件能力。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_105',
          toJobName: 'Node后端工程师',
          jaccardHigh: 0.6,
          cosLow: 0.8,
          salaryGain: 0.0,
          transitionReason: '软素质契合度高，硬技能存在可迁移技术基础，属低风险横向演进。',
          skillGaps: [
            {
              competencyName: 'Redis',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '熟练使用Redis进行高并发缓存设计',
              actionableAdvice: '建议搭建带缓存层的Node+Express微服务，实现LRU淘汰与缓存穿透防护。'
            },
            {
              competencyName: '数据库设计',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '熟悉MySQL/PostgreSQL数据库设计与优化',
              actionableAdvice: '完成电商订单系统数据库设计，包含索引优化与分表策略。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'path_lat_002',
      pathType: 'lateral',
      pathTitle: '前端→技术产品经理：需求翻译者成长路线',
      totalSteps: 1,
      totalRoutingCost: 0.75,
      overallSummary: '隐藏的高价值转岗通道，适合具备强沟通意愿与产品敏感度的技术人才。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_201',
          toJobName: '技术产品经理',
          jaccardHigh: 0.2,
          cosLow: 0.85,
          salaryGain: 0.0,
          transitionReason: '跨越技术边界，软素质契合度极高，体现对用户交互与业务逻辑拆解的优势。',
          skillGaps: [
            {
              competencyName: 'Axure/PRD编写',
              category: '工具与平台能力',
              targetScore: 4,
              originalContext: '熟练输出高质量PRD文档及高保真原型',
              actionableAdvice: '以前端项目为蓝本反向重构PRD，使用Axure制作可交互原型。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'path_lat_003',
      pathType: 'lateral',
      pathTitle: '前端→UI/UX设计师：体验设计者转型路线',
      totalSteps: 1,
      totalRoutingCost: 0.55,
      overallSummary: '发挥前端工程师对界面实现的敏感度，转向设计领域。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_301',
          toJobName: 'UI/UX设计师',
          jaccardHigh: 0.4,
          cosLow: 0.75,
          salaryGain: -0.1,
          transitionReason: '具备实现层面的设计认知，能理解设计约束与技术边界。',
          skillGaps: [
            {
              competencyName: 'Figma/Sketch',
              category: '设计工具',
              targetScore: 4,
              originalContext: '精通Figma或Sketch进行界面设计',
              actionableAdvice: '使用Figma重构现有项目UI，建立设计系统Design System。'
            },
            {
              competencyName: '用户研究',
              category: '设计思维',
              targetScore: 3,
              originalContext: '具备用户访谈与可用性测试经验',
              actionableAdvice: '组织一次用户调研，输出用户画像与体验地图。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'path_lat_004',
      pathType: 'lateral',
      pathTitle: '前端→DevOps工程师：工程效能优化路线',
      totalSteps: 1,
      totalRoutingCost: 0.45,
      overallSummary: '基于前端工程化经验，转向运维与工程效能方向。',
      steps: [
        {
          stepIndex: 1,
          fromJobid: 'job_002',
          fromJobName: '前端开发工程师',
          toJobid: 'job_401',
          toJobName: 'DevOps工程师',
          jaccardHigh: 0.5,
          cosLow: 0.7,
          salaryGain: 0.15,
          transitionReason: '前端工程化经验与CI/CD实践为转型提供基础。',
          skillGaps: [
            {
              competencyName: 'Kubernetes',
              category: '核心专业技能',
              targetScore: 3,
              originalContext: '熟悉K8s容器编排与集群管理',
              actionableAdvice: '在本地搭建K8s集群，部署微服务应用并配置自动扩缩容。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'path_lat_005',
      pathType: 'lateral',
      pathTitle: '前端→数据分析师：数据驱动决策路线',
      totalSteps: 1,
      totalRoutingCost: 0.65,
      overallSummary: '利用前端数据可视化经验，转向数据分析领域。',
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
          transitionReason: '具备数据可视化基础与业务理解能力，适合数据驱动型岗位。',
          skillGaps: [
            {
              competencyName: 'SQL/Python',
              category: '数据处理',
              targetScore: 4,
              originalContext: '熟练使用SQL进行数据查询，Python进行数据分析',
              actionableAdvice: '完成SQL进阶课程，使用Pandas完成用户行为数据分析项目。'
            },
            {
              competencyName: '统计学基础',
              category: '专业知识',
              targetScore: 3,
              originalContext: '掌握假设检验、回归分析等统计方法',
              actionableAdvice: '学习统计学基础课程，完成A/B测试实验设计与分析。'
            }
          ]
        }
      ]
    },
    {
      pathid: 'path_lat_006',
      pathType: 'lateral',
      pathTitle: '前端→测试开发工程师：质量保障专家路线',
      totalSteps: 1,
      totalRoutingCost: 0.4,
      overallSummary: '利用前端代码审查经验，转向质量保障领域。',
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
          transitionReason: '代码审查经验与边界情况分析能力有助于发现系统缺陷。',
          skillGaps: [
            {
              competencyName: '自动化测试框架',
              category: '测试技能',
              targetScore: 4,
              originalContext: '精通Selenium/Cypress等自动化测试框架',
              actionableAdvice: '搭建前端自动化测试体系，覆盖E2E与单元测试，产出测试报告。'
            }
          ]
        }
      ]
    }
  ]
})

// 当前显示的统计信息
const currentStats = computed(() => {
  const data = currentView.value === 'vertical' ? verticalData.value : lateralData.value
  const paths = data.paths
  
  return {
    totalPaths: paths.length,
    targetJobs: new Set(paths.flatMap(p => p.steps.map(s => s.toJobid))).size,
    avgCost: paths.reduce((sum, p) => sum + p.totalRoutingCost, 0) / paths.length,
    totalSkillGaps: paths.reduce((sum, p) => sum + p.steps.reduce((sSum, s) => sSum + s.skillGaps.length, 0), 0)
  }
})

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance.value = echarts.init(chartRef.value)
  
  // 响应式处理
  window.addEventListener('resize', handleResize)
  
  // 点击事件
  chartInstance.value.on('click', (params: any) => {
    if (params.dataType === 'node') {
      handleNodeClick(params.data)
    } else if (params.dataType === 'edge') {
      handleEdgeClick(params.data)
    }
  })
  
  renderGraph()
}

// 渲染图谱
const renderGraph = () => {
  if (!chartInstance.value) return
  
  const data = currentView.value === 'vertical' ? verticalData.value : lateralData.value
  const { nodes, links } = convertDataToGraph(data)
  
  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `<div style="padding: 10px;">
            <strong>${params.data.name}</strong><br/>
            <span style="color: #666">${params.data.jobId}</span>
          </div>`
        } else {
          return `<div style="padding: 10px; max-width: 300px;">
            <strong>${params.data.pathTitle}</strong><br/>
            <span style="color: ${params.data.pathType === 'vertical' ? '#f56c6c' : '#e6a23c'}">
              ${params.data.pathType === 'vertical' ? '垂直晋升' : '横向转岗'}
            </span><br/>
            <span>阻力系数: ${params.data.totalRoutingCost}</span>
          </div>`
        }
      }
    },
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        name: '职业路径',
        type: 'graph',
        layout: currentView.value === 'vertical' ? 'none' : 'force',
        data: nodes,
        links: links,
        roam: true, // 支持缩放拖拽
        draggable: true,
        focusNodeAdjacency: true,
        itemStyle: {
          borderWidth: 2,
          borderColor: '#fff',
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.1)'
        },
        label: {
          show: true,
          position: currentView.value === 'vertical' ? 'bottom' : 'inside',
          formatter: '{b}',
          fontSize: 12,
          fontWeight: 'bold',
          color: '#333'
        },
        lineStyle: {
          color: 'source',
          curveness: currentView.value === 'vertical' ? 0 : 0.2,
          width: 3,
          opacity: 0.7
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 5,
            opacity: 1
          }
        },
        force: {
          repulsion: 1000,
          edgeLength: [100, 200],
          gravity: 0.1
        },
        // 垂直布局时自定义位置
        ...(currentView.value === 'vertical' ? {
          left: 'center',
          top: '10%',
          width: '80%',
          height: '80%'
        } : {})
      }
    ]
  }
  
  chartInstance.value.setOption(option, true)
}

// 数据转换为图谱格式
const convertDataToGraph = (data: CareerData) => {
  const nodes: any[] = []
  const links: any[] = []
  const nodeMap = new Map()
  
  // 添加起始节点
  const startNode = {
    id: data.startJobid,
    name: data.startJobName,
    jobId: data.startJobid,
    category: 'current',
    symbolSize: 80,
    itemStyle: {
      color: '#409eff',
      shadowBlur: 20,
      shadowColor: 'rgba(64, 158, 255, 0.5)'
    },
    x: currentView.value === 'vertical' ? 400 : undefined,
    y: currentView.value === 'vertical' ? 50 : undefined
  }
  nodes.push(startNode)
  nodeMap.set(data.startJobid, startNode)
  
  // 处理路径
  data.paths.forEach((path, pathIndex) => {
    path.steps.forEach((step, stepIndex) => {
      // 添加目标节点（如果不存在）
      if (!nodeMap.has(step.toJobid)) {
        const isVertical = currentView.value === 'vertical'
        const node = {
          id: step.toJobid,
          name: step.toJobName,
          jobId: step.toJobid,
          category: 'target',
          symbolSize: 60,
          itemStyle: {
            color: path.pathType === 'vertical' ? '#f56c6c' : '#e6a23c'
          },
          // 垂直布局：按层级排列Y坐标
          x: isVertical ? 400 + (pathIndex * 200 - (data.paths.length - 1) * 100) : undefined,
          y: isVertical ? 150 + stepIndex * 150 : undefined
        }
        nodes.push(node)
        nodeMap.set(step.toJobid, node)
      }
      
      // 添加连线
      links.push({
        source: step.fromJobid,
        target: step.toJobid,
        pathTitle: path.pathTitle,
        pathType: path.pathType,
        totalRoutingCost: path.totalRoutingCost,
        totalSteps: path.totalSteps,
        overallSummary: path.overallSummary,
        transitionReason: step.transitionReason,
        skillGaps: step.skillGaps,
        fromJobName: step.fromJobName,
        toJobName: step.toJobName,
        lineStyle: {
          color: path.pathType === 'vertical' ? '#f56c6c' : '#e6a23c',
          type: path.pathType === 'vertical' ? 'solid' : 'dashed'
        },
        label: {
          show: true,
          formatter: path.pathType === 'vertical' ? '晋升' : '转岗',
          fontSize: 10,
          color: '#666'
        }
      })
    })
  })
  
  return { nodes, links }
}

// 节点点击
const handleNodeClick = (nodeData: any) => {
  selectedNode.value = nodeData
  selectedEdge.value = null
}

// 边点击
const handleEdgeClick = (edgeData: any) => {
  selectedEdge.value = edgeData
  selectedNode.value = null
}

// 视图切换
const handleViewChange = () => {
  selectedNode.value = null
  selectedEdge.value = null
  nextTick(() => {
    renderGraph()
  })
}

// 搜索处理（高亮节点）
const handleSearch = () => {
  if (!chartInstance.value || !searchKeyword.value) {
    renderGraph()
    return
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  const option = chartInstance.value.getOption()
  const series = option.series as any[]
  
  if (series && series[0] && series[0].data) {
    series[0].data.forEach((node: any) => {
      if (node.name.toLowerCase().includes(keyword)) {
        node.itemStyle = {
          ...node.itemStyle,
          borderColor: '#ff0',
          borderWidth: 4,
          shadowBlur: 30,
          shadowColor: '#ff0'
        }
      } else {
        // 恢复原始样式
        node.itemStyle = {
          ...node.itemStyle,
          borderColor: '#fff',
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.1)'
        }
      }
    })
    chartInstance.value.setOption(option)
  }
}

// 获取节点类型样式
const getNodeType = (node: any) => {
  if (node.category === 'current') return 'primary'
  return 'info'
}

const getNodeTypeText = (node: any) => {
  if (node.category === 'current') return '当前岗位'
  return '目标岗位'
}

// 获取阻力颜色
const getCostColor = (cost: number) => {
  if (cost < 0.3) return '#67c23a'
  if (cost < 0.6) return '#e6a23c'
  return '#f56c6c'
}

// 响应式调整
const handleResize = () => {
  chartInstance.value?.resize()
}

// 生命周期
onMounted(() => {
  initChart()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance.value?.dispose()
})
</script>

<style scoped lang="scss">
.career-path-graph {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .header-section {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 20px 30px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 10;

    .title-area {
      .main-title {
        margin: 0;
        font-size: 24px;
        color: #303133;
        display: flex;
        align-items: center;
        gap: 10px;
        
        .el-icon {
          color: #409eff;
          font-size: 28px;
        }
      }
      
      .sub-title {
        margin: 8px 0 0 0;
        font-size: 14px;
        color: #909399;
      }
    }

    .controls {
      display: flex;
      gap: 20px;
      align-items: center;
      
      .search-input {
        width: 240px;
      }
    }
  }

  .main-container {
    flex: 1;
    display: flex;
    position: relative;
    overflow: hidden;

    .graph-container {
      flex: 1;
      position: relative;
      padding: 20px;
      
      .chart-instance {
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      }

      .graph-legend {
        position: absolute;
        bottom: 30px;
        left: 30px;
        background: rgba(255, 255, 255, 0.95);
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        display: flex;
        gap: 20px;

        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #606266;

          .legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            
            &.start-node {
              background: #409eff;
              box-shadow: 0 0 8px rgba(64, 158, 255, 0.5);
            }
            
            &.target-node {
              background: #e6a23c;
            }
          }

          .legend-line {
            width: 20px;
            height: 3px;
            border-radius: 2px;
            
            &.vertical-line {
              background: #f56c6c;
            }
            
            &.lateral-line {
              background: #e6a23c;
              border: 1px dashed #e6a23c;
              height: 0;
            }
          }
        }
      }
    }

    .detail-panel {
      width: 420px;
      background: rgba(255, 255, 255, 0.98);
      border-left: 1px solid #e4e7ed;
      box-shadow: -4px 0 20px rgba(0, 0, 0, 0.08);
      overflow-y: auto;
      padding: 24px;
      
      .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 2px solid #e4e7ed;
        
        h3 {
          margin: 0;
          font-size: 18px;
          color: #303133;
          flex: 1;
        }
        
        .close-btn {
          margin-left: 10px;
        }
      }

      .panel-content {
        h4 {
          color: #303133;
          font-size: 14px;
          margin: 16px 0 12px 0;
          padding-left: 8px;
          border-left: 3px solid #409eff;
        }

        .summary-text {
          color: #606266;
          line-height: 1.8;
          font-size: 13px;
          background: #f5f7fa;
          padding: 12px;
          border-radius: 6px;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-bottom: 16px;
          
          .metric-item {
            background: #f5f7fa;
            padding: 12px;
            border-radius: 6px;
            
            .metric-label {
              display: block;
              font-size: 12px;
              color: #909399;
              margin-bottom: 8px;
            }
          }
        }

        .transition-flow {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          margin: 16px 0;
          padding: 16px;
          background: #f5f7fa;
          border-radius: 8px;
          
          .flow-node {
            padding: 8px 16px;
            background: #409eff;
            color: white;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            
            &.target {
              background: #67c23a;
            }
          }
          
          .flow-arrow {
            color: #909399;
            font-size: 20px;
          }
        }

        .transition-reason {
          margin: 12px 0;
        }

        .skill-gap-item {
          background: #fdf6ec;
          border: 1px solid #f5dab1;
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 12px;
          
          .skill-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            
            .skill-name {
              font-weight: 600;
              color: #e6a23c;
              font-size: 14px;
            }
          }
          
          .skill-context {
            margin-bottom: 8px;
            padding: 6px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 4px;
          }
          
          .skill-advice {
            display: flex;
            gap: 8px;
            color: #606266;
            font-size: 13px;
            line-height: 1.6;
            
            .el-icon {
              color: #409eff;
              margin-top: 2px;
              flex-shrink: 0;
            }
          }
        }
      }
    }
  }

  .stats-section {
    background: rgba(255, 255, 255, 0.95);
    padding: 20px 30px;
    border-top: 1px solid #e4e7ed;
    box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.05);
    
    :deep(.el-statistic__content) {
      color: #409eff;
      font-weight: 600;
    }
    
    :deep(.el-statistic__title) {
      color: #606266;
      font-size: 13px;
    }
  }
}

// 过渡动画
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

// 响应式适配
@media (max-width: 1200px) {
  .career-path-graph {
    .main-container {
      .detail-panel {
        position: absolute;
        right: 0;
        top: 0;
        bottom: 0;
        z-index: 20;
        box-shadow: -8px 0 24px rgba(0, 0, 0, 0.15);
      }
    }
    
    .header-section {
      flex-direction: column;
      gap: 16px;
      align-items: flex-start;
    }
  }
}
</style>