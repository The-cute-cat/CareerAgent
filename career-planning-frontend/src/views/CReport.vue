<template>
  <div class="growth-plan-page">
    <div class="page-shell">
      <section class="hero-grid">
        <el-card shadow="hover" class="hero-card dark-card">
          <div class="hero-top-tags">
            <el-tag round effect="dark" type="info">成长计划预览</el-tag>
            <el-tag round type="success">目标岗位：{{ data.target_position }}</el-tag>
          </div>

          <h1 class="hero-title">职业成长路径总览</h1>
          <p class="hero-desc">{{ data.student_summary }}</p>

          <div class="hero-stats">
            <div v-for="item in stats" :key="item.label" class="stat-item">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-label">{{ item.label }}</div>
            </div>
          </div>
        </el-card>

        <el-card shadow="hover" class="side-card">
          <template #header>
            <div class="card-header-block">
              <div>
                <div class="card-title">立即行动进度</div>
                <div class="card-subtitle">支持本地勾选，模拟任务进度追踪</div>
              </div>
            </div>
          </template>

          <div class="progress-wrap">
            <div class="progress-row">
              <span>完成度</span>
              <span>{{ actionProgress }}%</span>
            </div>
            <el-progress :percentage="actionProgress" :stroke-width="10" :show-text="false" />
          </div>

          <div class="checklist-wrap">
            <div
              v-for="(item, index) in data.action_checklist"
              :key="item"
              class="check-item"
            >
              <el-checkbox v-model="checkedActions[index]">
                <span :class="{ done: checkedActions[index] }">{{ item }}</span>
              </el-checkbox>
            </div>
          </div>
        </el-card>
      </section>

      <section class="tab-bar">
        <el-segmented v-model="activeTab" :options="tabOptions" />
      </section>

      <template v-if="activeTab === 'overview'">
        <section class="overview-grid top-overview-grid">
          <el-card shadow="hover" class="content-card">
            <template #header>
              <div class="card-header-block">
                <div>
                  <div class="card-title">当前能力差距</div>
                  <div class="card-subtitle">根据目标岗位要求提炼的关键短板</div>
                </div>
              </div>
            </template>
            <div class="gap-panel">{{ data.current_gap }}</div>
          </el-card>

          <el-card shadow="hover" class="content-card">
            <template #header>
              <div class="card-header-block">
                <div>
                  <div class="card-title">阶段路径</div>
                  <div class="card-subtitle">将短期夯实基础与中期进阶串联展示</div>
                </div>
              </div>
            </template>

            <div class="timeline-list">
              <div v-for="(phase, idx) in phaseList" :key="phase.phase" class="timeline-item">
                <div class="timeline-dot">{{ idx + 1 }}</div>
                <div class="timeline-line" v-if="idx !== phaseList.length - 1"></div>
                <div class="timeline-card">
                  <div class="timeline-header">
                    <span class="timeline-phase">{{ phase.phase }}阶段</span>
                    <el-tag round size="small">{{ phase.duration }}</el-tag>
                  </div>
                  <div class="tag-list mt12">
                    <el-tag
                      v-for="item in phase.items"
                      :key="item"
                      round
                      effect="plain"
                      class="mr8 mb8"
                    >
                      {{ item }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </section>

        <section class="overview-grid bottom-overview-grid">
          <PlanPanel
            title="短期计划"
            :plan="data.short_term_plan"
            theme="success"
            @open-resource="openResource"
          />

          <el-card shadow="hover" class="content-card">
            <template #header>
              <div class="card-header-block">
                <div>
                  <div class="card-title">推荐实习岗位</div>
                  <div class="card-subtitle">点击卡片查看详情与推荐理由</div>
                </div>
              </div>
            </template>

            <div class="intern-list">
              <div
                v-for="job in data.mid_term_plan.recommended_internships"
                :key="job.id"
                class="intern-card"
                @click="openIntern(job)"
              >
                <div class="intern-card-top">
                  <div>
                    <div class="intern-title">{{ job.job_title }}</div>
                    <div class="intern-meta">{{ job.company_name }} · {{ job.city }} · {{ job.job_type }}</div>
                  </div>
                  <el-tag size="small">{{ job.salary }}</el-tag>
                </div>

                <div class="tag-list mt12">
                  <el-tag round type="primary">{{ job.tech_stack }}</el-tag>
                  <el-tag round effect="plain">每周{{ job.days_per_week }}天</el-tag>
                  <el-tag round effect="plain">{{ job.months }}个月</el-tag>
                </div>

                <div class="intern-reason">{{ job.reason }}</div>
              </div>
            </div>
          </el-card>
        </section>
      </template>

      <section v-else-if="activeTab === 'short'">
        <PlanPanel
          title="短期计划"
          :plan="data.short_term_plan"
          theme="success"
          @open-resource="openResource"
        />
      </section>

      <section v-else-if="activeTab === 'mid'">
        <PlanPanel
          title="中期计划"
          :plan="data.mid_term_plan"
          theme="warning"
          @open-resource="openResource"
        />
      </section>

      <section v-else class="tips-grid">
        <el-card shadow="hover" class="content-card">
          <template #header>
            <div class="card-header-block">
              <div>
                <div class="card-title">学习建议</div>
                <div class="card-subtitle">适合做成轮播、列表或右侧固定提示区域</div>
              </div>
            </div>
          </template>

          <div class="tips-list">
            <div v-for="(tip, index) in data.tips" :key="tip" class="tip-card">
              <div class="tip-index">TIP {{ index + 1 }}</div>
              <div class="tip-content">{{ tip }}</div>
            </div>
          </div>
        </el-card>

        <el-card shadow="hover" class="content-card">
          <template #header>
            <div class="card-header-block">
              <div>
                <div class="card-title">界面结构建议</div>
                <div class="card-subtitle">适合比赛演示，也方便后续继续扩展</div>
              </div>
            </div>
          </template>

          <div class="structure-list">
            <div class="structure-item">
              <div class="structure-title">主视图</div>
              <div class="structure-text">顶部总览 + 右侧行动进度，让页面一打开就有目标感和完成度反馈。</div>
            </div>
            <div class="structure-item">
              <div class="structure-title">计划区</div>
              <div class="structure-text">里程碑折叠、任务再二级展开，字段多但不会显得拥挤。</div>
            </div>
            <div class="structure-item">
              <div class="structure-title">详情区</div>
              <div class="structure-text">资源和岗位详情统一放抽屉，主界面保持清爽。</div>
            </div>
            <div class="structure-item">
              <div class="structure-title">后续扩展</div>
              <div class="structure-text">可继续接 ECharts 雷达图、AntV X6/G6 图谱、WangEditor 在线编辑与 PDF 导出。</div>
            </div>
          </div>
        </el-card>
      </section>
    </div>

    <el-drawer v-model="resourceDrawerVisible" size="42%" title="资源详情">
      <template v-if="currentResource">
        <div class="drawer-stack">
          <div>
            <div class="drawer-title">{{ currentResource.title || currentResource.name }}</div>
            <div class="drawer-subtitle">{{ currentResource.author || currentResource.category || '推荐资源' }}</div>
          </div>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="发布日期">
              {{ currentResource.publish_date || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="推荐理由">
              {{ currentResource.reason || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="内容简介">
              <div class="multiline-text">{{ currentResource.content || '-' }}</div>
            </el-descriptions-item>
          </el-descriptions>

          <div>
            <el-button type="primary" :href="currentResource.url" target="_blank">
              打开外部链接
            </el-button>
          </div>
        </div>
      </template>
    </el-drawer>

    <el-drawer v-model="internDrawerVisible" size="48%" title="岗位详情">
      <template v-if="currentIntern">
        <div class="drawer-stack">
          <div>
            <div class="drawer-title">{{ currentIntern.job_title }}</div>
            <div class="drawer-subtitle">{{ currentIntern.company_name }} · {{ currentIntern.city }}</div>
          </div>

          <div class="intern-detail-grid">
            <div class="metric-card"><span>薪资</span><strong>{{ currentIntern.salary }}</strong></div>
            <div class="metric-card"><span>学历</span><strong>{{ currentIntern.degree }}</strong></div>
            <div class="metric-card"><span>工作节奏</span><strong>每周{{ currentIntern.days_per_week }}天 / {{ currentIntern.months }}个月</strong></div>
            <div class="metric-card"><span>技术栈</span><strong>{{ currentIntern.tech_stack }}</strong></div>
          </div>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="推荐理由">
              {{ currentIntern.reason }}
            </el-descriptions-item>
            <el-descriptions-item label="岗位内容">
              <div class="multiline-text">{{ currentIntern.content }}</div>
            </el-descriptions-item>
          </el-descriptions>

          <div>
            <el-button type="primary" :href="currentIntern.url" target="_blank">查看原岗位链接</el-button>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, reactive, ref } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'

type ResourceItem = {
  id: string
  title?: string
  name?: string
  author?: string
  url?: string
  category?: string
  publish_date?: string
  reason?: string
  content?: string
}

type TaskItem = {
  task_name: string
  description: string
  priority: '高' | '中' | '低'
  estimated_time: string
  skill_target: string
  success_criteria: string
  resources: ResourceItem[]
}

type MilestoneItem = {
  milestone_name: string
  target_date: string
  key_results: string[]
  tasks: TaskItem[]
}

type ShortTermPlan = {
  duration: string
  goal: string
  focus_areas: string[]
  milestones: MilestoneItem[]
  quick_wins: string[]
}

type InternshipItem = {
  id: string
  job_title: string
  company_name: string
  salary: string
  city: string
  degree: string
  days_per_week: number
  months: number
  job_type: string
  tech_stack: string
  url: string
  content: string
  reason: string
}

type MidTermPlan = {
  duration: string
  goal: string
  skill_roadmap: string[]
  milestones: MilestoneItem[]
  career_progression: string
  recommended_internships: InternshipItem[]
}

const data = {
  student_summary:
    '计算机科学与技术专业本科在读，具备Java、MySQL、HTML/CSS/JavaScript基础技能，掌握Git、Maven、IDEA等开发工具。有学生信息管理系统（后端开发）和校园网站（前端开发）项目经验，获蓝桥杯程序设计竞赛省级三等奖。英语能力良好（CET-6 520分），学习能力强（评分4/5），逻辑思维清晰（评分4/5），职业倾向技术型。核心短板：无实习经历，缺乏Spring Boot、MyBatis等企业级框架经验，数据库优化能力薄弱，无分布式系统知识，缺少有竞争力的开源项目。',
  target_position: 'Java后端开发工程师',
  current_gap:
    '1. 企业级框架掌握不足：对Spring Boot、MyBatis等主流框架缺乏系统学习和实战经验；2. 数据库能力薄弱：数据库设计、SQL优化、索引优化等能力不足；3. 分布式微服务知识空白：对分布式系统、微服务架构缺乏了解；4. 项目经验不足：缺少企业级项目开发经验，简历竞争力不够；5. 无实习经历：缺乏实际工作经验和团队协作经验。',
  short_term_plan: {
    duration: '1-3个月',
    goal: '夯实Java后端基础，掌握Spring Boot+MyBatis主流框架，提升数据库设计与优化能力，完成1-2个企业级项目实战',
    focus_areas: ['Spring Boot框架开发', 'MyBatis持久层框架', 'MySQL数据库设计与优化', 'RESTful API设计'],
    milestones: [
      {
        milestone_name: 'Spring Boot框架入门与实战',
        target_date: '第1个月末',
        key_results: [
          '完成Spring Boot基础学习，理解核心概念（IOC、AOP、自动配置）',
          '掌握Spring Boot项目搭建、配置管理、常用注解',
          '完成至少1个Spring Boot实战项目（博客系统或商城模块）',
        ],
        tasks: [
          {
            task_name: '学习Spring Boot核心概念与基础开发',
            description:
              '通过视频教程系统学习Spring Boot框架，包括项目搭建、配置文件、常用注解、依赖注入、AOP等核心概念，理解Spring Boot自动配置原理',
            priority: '高',
            estimated_time: '2周',
            skill_target: 'Spring Boot框架开发能力',
            success_criteria:
              '能够独立搭建Spring Boot项目，理解IOC容器和AOP原理，掌握常用注解的使用场景',
            resources: [
              {
                id: '27b07',
                title: '黑马程序员SpringBoot教程',
                author: '黑马程序员',
                url: 'https://www.bilibili.com/video/BV1Lq4y1J77x',
                category: '后端开发',
                publish_date: '2021-05-04',
                reason: '适合快速入门，覆盖Spring Boot核心知识点',
                content: '6小时快速入门Spring Boot，适合夯实基础。',
              },
            ],
          },
          {
            task_name: '完成Spring Boot+Vue前后端分离博客项目',
            description:
              '跟随实战教程完成一个完整的前后端分离博客系统，包括用户管理、文章发布、评论功能、分类标签等模块。',
            priority: '高',
            estimated_time: '3周',
            skill_target: '企业级项目开发能力、RESTful API设计',
            success_criteria: '完成项目开发并部署运行，能够演示完整功能',
            resources: [
              {
                id: 'bea55',
                title: 'SpringBoot+Vue项目实战-前后端分离博客项目',
                author: '三更草堂',
                url: 'https://www.bilibili.com/video/BV1hq4y1F7zk',
                category: '后端开发',
                publish_date: '2022-01-31',
                reason: '手把手教学，适合项目实战入门',
                content: '完整博客系统项目，适合用于简历项目包装。',
              },
            ],
          },
        ],
      },
      {
        milestone_name: 'MySQL数据库设计与优化能力提升',
        target_date: '第2个月末',
        key_results: ['掌握索引、锁机制、执行计划分析', '能够进行SQL性能分析和优化'],
        tasks: [
          {
            task_name: '系统学习MySQL高级知识与优化技巧',
            description: '深入学习索引原理、锁机制、事务隔离级别、执行计划分析、慢查询优化。',
            priority: '高',
            estimated_time: '2周',
            skill_target: 'MySQL数据库优化能力',
            success_criteria: '能够分析执行计划，识别慢查询原因，掌握索引优化策略',
            resources: [],
          },
        ],
      },
    ],
    quick_wins: ['本周内完成Spring Boot开发环境搭建', '3天内完成第一个Spring Boot Hello World项目', '1周内完成MySQL索引基础知识学习并输出笔记'],
  } as ShortTermPlan,
  mid_term_plan: {
    duration: '3-12个月',
    goal: '深入掌握分布式微服务架构，积累企业级项目经验，获得实习机会，建立个人技术影响力',
    skill_roadmap: ['Spring Cloud微服务架构', 'Redis缓存技术', '消息队列', 'Docker容器化部署', '分布式系统原理', '高并发系统设计'],
    milestones: [
      {
        milestone_name: '微服务架构学习与实战',
        target_date: '第6个月末',
        key_results: ['掌握Spring Cloud核心组件', '完成微服务项目改造', '掌握Docker容器化部署'],
        tasks: [
          {
            task_name: '学习Spring Cloud微服务架构',
            description: '系统学习Spring Cloud微服务全家桶，包括服务注册发现、服务调用、网关、熔断降级等。',
            priority: '高',
            estimated_time: '4周',
            skill_target: '微服务架构设计与开发能力',
            success_criteria: '能够搭建Spring Cloud微服务项目，理解各组件作用和使用场景',
            resources: [
              {
                id: 'book-1',
                title: '深入理解分布式系统',
                author: '唐伟志',
                url: 'https://book.douban.com/subject/35794814/',
                category: '架构与系统设计',
                publish_date: '2022-3',
                reason: '系统讲解分布式系统原理',
                content: '为微服务学习打下理论基础。',
              },
            ],
          },
        ],
      },
    ],
    career_progression:
      '具备1年以上企业级项目开发经验，熟练掌握Spring Boot+MyBatis+Spring Cloud技术栈，能够独立负责模块开发。',
    recommended_internships: [
      {
        id: 'intern-1',
        job_title: '即梦AI产品实习生-剪映CapCut',
        company_name: '字节跳动',
        salary: '薪资面议',
        city: '北京',
        degree: '本科',
        days_per_week: 4,
        months: 3,
        job_type: '日常实习',
        tech_stack: 'AIGC,GC',
        url: 'https://www.shixiseng.com/intern/inn_2zhheb2ae6bo',
        content: '参与即梦AI多模态创作产品的核心功能建设，关注用户体验优化及留存提升。',
        reason: '适合积累大厂实习经验',
      },
      {
        id: 'intern-2',
        job_title: '国际电商商家端AI Agent产品实习生-TikTok Shop',
        company_name: '字节跳动',
        salary: '薪资面议',
        city: '上海',
        degree: '本科',
        days_per_week: 5,
        months: 6,
        job_type: '日常实习',
        tech_stack: 'LLM,大模型',
        url: 'https://www.shixiseng.com/intern/inn_y5wkw4mxcs6r',
        content: '参与商家端AI Agent产品能力建设，提升智能回答满意度。',
        reason: '适合接触国际化平台与大模型技术',
      },
    ],
  } as MidTermPlan,
  action_checklist: [
    '本周内完成Spring Boot开发环境搭建（JDK 17、Maven 3.8+、IDEA Ultimate）',
    '注册GitHub账号并Fork mall项目，开始研读项目文档',
    '制定每日学习计划：工作日每天2小时，周末每天6小时',
    '准备简历模板，梳理项目经验和技术栈',
  ],
  tips: [
    '先掌握Spring Boot单体应用开发，再学习Spring Cloud微服务架构。',
    '项目经验是核心竞争力：务必完成2-3个有质量的项目。',
    '重视Java基础、数据库、计算机网络等底层知识。',
    '通过博客、GitHub、社区问答建立个人技术影响力。',
  ],
}

const activeTab = ref<'overview' | 'short' | 'mid' | 'tips'>('overview')
const checkedActions = reactive<Record<number, boolean>>({})
const resourceDrawerVisible = ref(false)
const internDrawerVisible = ref(false)
const currentResource = ref<ResourceItem | null>(null)
const currentIntern = ref<InternshipItem | null>(null)

const tabOptions = [
  { label: '概览', value: 'overview' },
  { label: '短期计划', value: 'short' },
  { label: '中期计划', value: 'mid' },
  { label: '学习建议', value: 'tips' },
]

const stats = computed(() => {
  const shortTaskCount = data.short_term_plan.milestones.reduce((sum, item) => sum + item.tasks.length, 0)
  return [
    { label: '短期里程碑', value: data.short_term_plan.milestones.length },
    { label: '短期任务数', value: shortTaskCount },
    { label: '中期里程碑', value: data.mid_term_plan.milestones.length },
    { label: '推荐岗位', value: data.mid_term_plan.recommended_internships.length },
  ]
})

const actionProgress = computed(() => {
  const total = data.action_checklist.length
  const done = Object.values(checkedActions).filter(Boolean).length
  return total ? Math.round((done / total) * 100) : 0
})

const phaseList = computed(() => [
  {
    phase: '短期',
    duration: data.short_term_plan.duration,
    items: data.short_term_plan.focus_areas,
  },
  {
    phase: '中期',
    duration: data.mid_term_plan.duration,
    items: data.mid_term_plan.skill_roadmap,
  },
])

function openResource(resource: ResourceItem) {
  currentResource.value = resource
  resourceDrawerVisible.value = true
}

function openIntern(job: InternshipItem) {
  currentIntern.value = job
  internDrawerVisible.value = true
}

const PlanPanel = defineComponent({
  name: 'PlanPanel',
  props: {
    title: {
      type: String,
      required: true,
    },
    plan: {
      type: Object as () => ShortTermPlan | MidTermPlan,
      required: true,
    },
    theme: {
      type: String,
      default: 'success',
    },
  },
  emits: ['open-resource'],
  setup(props, { emit }) {
    const openedMilestones = reactive<Record<string, boolean>>({})
    const openedTasks = reactive<Record<string, boolean>>({})

    const isShort = computed(() => 'focus_areas' in props.plan)
    const isMid = computed(() => 'skill_roadmap' in props.plan)

    const priorityTypeMap: Record<'高' | '中' | '低', 'danger' | 'warning' | 'info'> = {
      高: 'danger',
      中: 'warning',
      低: 'info',
    }

    const toggleMilestone = (key: string) => {
      openedMilestones[key] = !openedMilestones[key]
    }

    const toggleTask = (key: string) => {
      openedTasks[key] = !openedTasks[key]
    }

    return () =>
      h(
        'div',
        { class: 'plan-panel-wrap' },
        h(
          'div',
          { class: 'el-card is-hover-shadow content-card el-card--default' },
          [
            h('div', { class: 'el-card__header' }, [
              h('div', { class: 'card-header-block' }, [
                h('div', null, [
                  h('div', { class: 'card-title' }, props.title),
                  h('div', { class: 'card-subtitle' }, `${props.plan.duration} · ${props.plan.goal}`),
                ]),
                h('div', null, [h('span', { class: `custom-duration-tag is-${props.theme}` }, props.plan.duration)]),
              ]),
            ]),
            h('div', { class: 'el-card__body plan-body' }, [
              isShort.value
                ? h('div', { class: 'block-section' }, [
                    h('div', { class: 'small-block-title' }, '重点方向'),
                    h(
                      'div',
                      { class: 'tag-list' },
                      (props.plan as ShortTermPlan).focus_areas.map((item) =>
                        h('span', { class: 'simple-tag', key: item }, item),
                      ),
                    ),
                  ])
                : null,

              isMid.value
                ? h('div', { class: 'block-section' }, [
                    h('div', { class: 'small-block-title' }, '技能路线图'),
                    h(
                      'div',
                      { class: 'roadmap-grid' },
                      (props.plan as MidTermPlan).skill_roadmap.map((item, index) =>
                        h('div', { class: 'roadmap-item', key: item }, [
                          h('div', { class: 'roadmap-step' }, `STEP ${index + 1}`),
                          h('div', { class: 'roadmap-text' }, item),
                        ]),
                      ),
                    ),
                  ])
                : null,

              h(
                'div',
                { class: 'milestone-list' },
                props.plan.milestones.map((milestone, mIndex) => {
                  const milestoneKey = `${props.title}-${mIndex}`
                  const milestoneOpen = !!openedMilestones[milestoneKey]

                  return h('div', { class: 'milestone-block', key: milestoneKey }, [
                    h(
                      'div',
                      {
                        class: 'milestone-head',
                        onClick: () => toggleMilestone(milestoneKey),
                      },
                      [
                        h('div', null, [
                          h('div', { class: 'milestone-title' }, milestone.milestone_name),
                          h('div', { class: 'milestone-date' }, `目标时间：${milestone.target_date}`),
                        ]),
                        h('div', { class: 'milestone-action' }, milestoneOpen ? '收起' : '展开'),
                      ],
                    ),

                    milestoneOpen
                      ? h('div', { class: 'milestone-body' }, [
                          h('div', { class: 'block-section' }, [
                            h('div', { class: 'small-block-title' }, '关键结果'),
                            h(
                              'ul',
                              { class: 'result-list' },
                              milestone.key_results.map((result) =>
                                h('li', { key: result }, [
                                  h('span', { class: 'dot' }, '•'),
                                  h('span', null, result),
                                ]),
                              ),
                            ),
                          ]),

                          h(
                            'div',
                            { class: 'task-list' },
                            milestone.tasks.map((task, tIndex) => {
                              const taskKey = `${milestoneKey}-${tIndex}`
                              const taskOpen = !!openedTasks[taskKey]

                              return h('div', { class: 'task-block', key: taskKey }, [
                                h(
                                  'div',
                                  {
                                    class: 'task-head',
                                    onClick: () => toggleTask(taskKey),
                                  },
                                  [
                                    h('div', { class: 'task-head-left' }, [
                                      h('div', { class: 'task-name' }, task.task_name),
                                      h(
                                        'div',
                                        { class: 'task-meta-tags' },
                                        [
                                          h(
                                            'div',
                                            { class: 'inline-tag-wrap' },
                                            h(
                                              resolveComponent('ElTag') as any,
                                              {
                                                type: priorityTypeMap[task.priority],
                                                size: 'small',
                                                round: true,
                                              },
                                              () => `${task.priority}优先级`,
                                            ),
                                          ),
                                          h(
                                            resolveComponent('ElTag') as any,
                                            {
                                              size: 'small',
                                              round: true,
                                              effect: 'plain',
                                            },
                                            () => task.estimated_time,
                                          ),
                                        ],
                                      ),
                                    ]),
                                    h('div', { class: 'task-action' }, taskOpen ? '收起' : '详情'),
                                  ],
                                ),
                                taskOpen
                                  ? h('div', { class: 'task-body' }, [
                                      h('div', { class: 'task-detail-grid' }, [
                                        h('div', { class: 'task-main-info' }, [
                                          h('div', { class: 'task-info-item' }, [
                                            h('div', { class: 'task-info-title' }, '任务描述'),
                                            h('div', { class: 'task-info-text' }, task.description),
                                          ]),
                                          h('div', { class: 'task-info-item' }, [
                                            h('div', { class: 'task-info-title' }, '技能目标'),
                                            h('div', { class: 'task-info-text' }, task.skill_target),
                                          ]),
                                          h('div', { class: 'task-info-item' }, [
                                            h('div', { class: 'task-info-title' }, '成功标准'),
                                            h('div', { class: 'task-info-text' }, task.success_criteria),
                                          ]),
                                        ]),
                                        h('div', { class: 'resource-side' }, [
                                          h('div', { class: 'task-info-title mb12' }, '推荐资源'),
                                          task.resources?.length
                                            ? h(
                                                'div',
                                                { class: 'resource-list' },
                                                task.resources.map((resource) =>
                                                  h(
                                                    'div',
                                                    {
                                                      class: 'resource-card',
                                                      key: resource.id,
                                                      onClick: () => emit('open-resource', resource),
                                                    },
                                                    [
                                                      h('div', { class: 'resource-name' }, resource.title || resource.name),
                                                      h('div', { class: 'resource-meta' }, resource.author || resource.category || '资源详情'),
                                                    ],
                                                  ),
                                                ),
                                              )
                                            : h('div', { class: 'empty-tip' }, '暂无推荐资源'),
                                        ]),
                                      ]),
                                    ])
                                  : null,
                              ])
                            }),
                          ),
                        ])
                      : null,
                  ])
                }),
              ),

              isShort.value
                ? h('div', { class: 'quickwins-box' }, [
                    h('div', { class: 'quickwins-title' }, '快速见效行动'),
                    h(
                      'div',
                      { class: 'quickwins-grid' },
                      (props.plan as ShortTermPlan).quick_wins.map((item) =>
                        h('div', { class: 'quickwin-item', key: item }, item),
                      ),
                    ),
                  ])
                : null,

              isMid.value
                ? h('div', { class: 'career-box' }, [
                    h('div', { class: 'career-title' }, '职业发展预期'),
                    h('div', { class: 'career-text' }, (props.plan as MidTermPlan).career_progression),
                  ])
                : null,
            ]),
          ],
        ),
      )
  },
})
</script>

<script lang="ts">
import { resolveComponent } from 'vue'
export default {}
</script>

<style scoped>
.growth-plan-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f5f7fb 0%, #eef2f7 100%);
  padding: 24px;
  box-sizing: border-box;
}

.page-shell {
  max-width: 1440px;
  margin: 0 auto;
}

.hero-grid,
.top-overview-grid,
.bottom-overview-grid,
.tips-grid {
  display: grid;
  gap: 20px;
}

.hero-grid {
  grid-template-columns: 1.5fr 0.9fr;
  margin-bottom: 20px;
}

.top-overview-grid,
.tips-grid {
  grid-template-columns: 1fr 1fr;
}

.bottom-overview-grid {
  grid-template-columns: 1.1fr 0.9fr;
  margin-top: 20px;
}

.dark-card :deep(.el-card__body) {
  background: linear-gradient(135deg, #111827 0%, #1f2937 45%, #312e81 100%);
  color: #fff;
}

.hero-card,
.side-card,
.content-card {
  border-radius: 24px;
  border: none;
}

.hero-top-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.hero-title {
  margin: 0 0 14px;
  font-size: 34px;
  line-height: 1.2;
  font-weight: 700;
}

.hero-desc {
  margin: 0;
  line-height: 1.9;
  color: rgba(255, 255, 255, 0.86);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

.stat-item {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
}

.stat-label {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.76);
  font-size: 14px;
}

.card-header-block {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.card-subtitle {
  margin-top: 6px;
  color: #6b7280;
  font-size: 13px;
}

.progress-wrap {
  margin-bottom: 18px;
}

.progress-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #6b7280;
  font-size: 14px;
}

.checklist-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.check-item {
  padding: 14px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  background: #fff;
}

.done {
  text-decoration: line-through;
  color: #9ca3af;
}

.tab-bar {
  margin-bottom: 20px;
}

.gap-panel {
  padding: 20px;
  border-radius: 20px;
  background: #fff1f2;
  border: 1px solid #ffe4e6;
  line-height: 1.9;
  color: #475569;
}

.timeline-list {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.timeline-item {
  position: relative;
  padding-left: 42px;
}

.timeline-dot {
  position: absolute;
  left: 0;
  top: 2px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #111827;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  z-index: 2;
}

.timeline-line {
  position: absolute;
  left: 13px;
  top: 34px;
  bottom: -22px;
  width: 2px;
  background: #e5e7eb;
}

.timeline-card {
  padding: 16px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.timeline-phase {
  font-size: 15px;
  font-weight: 700;
  color: #1f2937;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.mt12 {
  margin-top: 12px;
}

.mr8 {
  margin-right: 0;
}

.mb8 {
  margin-bottom: 0;
}

.plan-body {
  padding-top: 4px;
}

.custom-duration-tag {
  display: inline-flex;
  align-items: center;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.custom-duration-tag.is-success {
  background: #ecfdf5;
  color: #047857;
}

.custom-duration-tag.is-warning {
  background: #fffbeb;
  color: #b45309;
}

.block-section {
  margin-bottom: 22px;
}

.small-block-title {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}

.simple-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 13px;
}

.roadmap-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.roadmap-item {
  border: 1px solid #e5e7eb;
  background: #f8fafc;
  border-radius: 18px;
  padding: 16px;
}

.roadmap-step {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 6px;
}

.roadmap-text {
  color: #1f2937;
  font-weight: 600;
}

.milestone-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.milestone-block {
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  overflow: hidden;
  background: #fff;
}

.milestone-head {
  padding: 18px 20px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  cursor: pointer;
}

.milestone-title {
  color: #111827;
  font-size: 16px;
  font-weight: 700;
}

.milestone-date,
.milestone-action,
.task-action,
.resource-meta,
.intern-meta,
.tip-index,
.drawer-subtitle {
  color: #6b7280;
  font-size: 13px;
}

.milestone-date {
  margin-top: 6px;
}

.milestone-body {
  padding: 20px;
}

.result-list {
  padding: 0;
  margin: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #475569;
}

.result-list li {
  display: flex;
  gap: 8px;
  line-height: 1.8;
}

.dot {
  margin-top: 1px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-block {
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  overflow: hidden;
}

.task-head {
  padding: 16px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  background: #fff;
}

.task-head-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.task-name,
.intern-title,
.drawer-title,
.structure-title,
.quickwins-title,
.career-title {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
}

.task-meta-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.task-body {
  padding: 0 18px 18px;
}

.task-detail-grid {
  display: grid;
  grid-template-columns: 1.7fr 0.95fr;
  gap: 18px;
  padding-top: 8px;
}

.task-main-info,
.tips-list,
.structure-list,
.drawer-stack,
.intern-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.task-info-item {
  line-height: 1.85;
}

.task-info-title {
  font-size: 14px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 6px;
}

.task-info-text,
.tip-content,
.structure-text,
.career-text,
.multiline-text,
.intern-reason {
  color: #475569;
  line-height: 1.85;
}

.resource-side {
  padding: 16px;
  border-radius: 18px;
  background: #f8fafc;
}

.resource-card,
.tip-card,
.structure-item,
.quickwin-item,
.metric-card,
.intern-card {
  border-radius: 18px;
  border: 1px solid #e5e7eb;
  background: #fff;
}

.resource-card {
  padding: 14px;
  cursor: pointer;
}

.resource-card:hover,
.intern-card:hover {
  border-color: #cbd5e1;
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

.resource-name {
  font-size: 14px;
  color: #111827;
  font-weight: 600;
  line-height: 1.6;
}

.empty-tip {
  color: #94a3b8;
  font-size: 13px;
}

.quickwins-box {
  margin-top: 20px;
  padding: 18px;
  border-radius: 20px;
  background: #ecfdf5;
  border: 1px solid #d1fae5;
}

.quickwins-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.quickwin-item {
  padding: 14px;
  line-height: 1.75;
  color: #475569;
}

.career-box {
  margin-top: 20px;
  padding: 18px;
  border-radius: 20px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
}

.career-text {
  margin-top: 10px;
}

.intern-card {
  padding: 16px;
  cursor: pointer;
}

.intern-card-top {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.intern-meta,
.intern-reason {
  margin-top: 8px;
}

.tip-card,
.structure-item {
  padding: 18px;
  background: #f8fafc;
}

.intern-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.metric-card {
  padding: 16px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-card span {
  color: #94a3b8;
  font-size: 12px;
}

.metric-card strong {
  color: #111827;
  line-height: 1.6;
}

.drawer-title {
  font-size: 22px;
}

@media (max-width: 1200px) {
  .hero-grid,
  .top-overview-grid,
  .bottom-overview-grid,
  .tips-grid,
  .roadmap-grid,
  .quickwins-grid,
  .task-detail-grid,
  .intern-detail-grid {
    grid-template-columns: 1fr;
  }

  .hero-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .growth-plan-page {
    padding: 14px;
  }

  .hero-title {
    font-size: 26px;
  }

  .hero-stats {
    grid-template-columns: 1fr 1fr;
  }

  .timeline-item {
    padding-left: 36px;
  }

  .task-head,
  .milestone-head,
  .intern-card-top,
  .timeline-header,
  .card-header-block {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
