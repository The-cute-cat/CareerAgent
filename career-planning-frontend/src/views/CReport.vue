<template>
  <div class="growth-plan-container">
    <div class="max-width-wrapper">
      <!-- Header Section: 目标岗位与核心指标 -->
      <header class="plan-header-section">
        <div class="header-content">
          <div class="position-badge">
            <el-tag size="large" effect="dark" round class="plan-type-tag">
              职业成长计划
            </el-tag>
            <h1 class="position-title">{{ data.target_position }}</h1>
          </div>
          <p class="position-summary">{{ data.target_position_profile_summary }}</p>
          
          <div class="header-stats">
            <div v-for="stat in headerStats" :key="stat.label" class="stat-card">
              <div class="stat-value" :class="stat.type">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </header>

      <!-- 主内容网格 -->
      <div class="main-grid">
        <!-- 左侧：能力分析雷达图 -->
        <div class="left-column">
          <section class="chart-section ability-section">
            <div class="section-header">
              <h3>能力差距分析</h3>
              <el-tooltip content="基于当前技能与目标岗位要求的差距分析">
                <el-icon><Info-Filled /></el-icon>
              </el-tooltip>
            </div>
            <div ref="radarChartRef" class="radar-chart"></div>
            <div class="ability-legend">
              <div class="legend-item">
                <span class="dot current"></span>
                <span>当前水平</span>
              </div>
              <div class="legend-item">
                <span class="dot target"></span>
                <span>目标要求</span>
              </div>
            </div>
          </section>

          <!-- 学生画像卡片 -->
          <section class="info-card profile-card">
            <div class="card-header">
              <el-icon size="20"><User /></el-icon>
              <span>学生画像</span>
            </div>
            <p class="profile-text">{{ data.student_summary }}</p>
          </section>
        </div>

        <!-- 右侧：行动计划与进度 -->
        <div class="right-column">
          <!-- 行动进度圆环 -->
          <section class="progress-section">
            <div class="progress-ring-wrapper">
              <div class="progress-ring" :style="progressStyle">
                <div class="progress-content">
                  <span class="progress-percent">{{ actionProgress }}%</span>
                  <span class="progress-label">行动完成度</span>
                </div>
              </div>
            </div>
            
            <div class="action-preview">
              <div class="preview-header">
                <span>立即行动清单</span>
                <el-button text type="primary" @click="drawerVisible = true">
                  查看全部 {{ data.action_checklist.length }} 项
                  <el-icon class="el-icon--right"><Arrow-Right /></el-icon>
                </el-button>
              </div>
              <div class="action-list-preview">
                <div 
                  v-for="(item, index) in data.action_checklist.slice(0, 3)" 
                  :key="index"
                  class="action-item"
                  :class="{ completed: checkedActions[index] }"
                  @click="toggleAction(index)"
                >
                  <el-checkbox 
                    v-model="checkedActions[index]" 
                    @click.stop
                    size="large"
                  />
                  <span class="action-text">{{ item }}</span>
                </div>
              </div>
            </div>
          </section>

          <!-- 当前差距简要 -->
          <section class="info-card gap-card" @click="gapDialogVisible = true">
            <div class="card-header">
              <el-icon size="20" color="#f56c6c"><Warning /></el-icon>
              <span>能力差距概览</span>
              <el-icon class="arrow-icon"><Arrow-Right /></el-icon>
            </div>
            <div class="gap-brief">
              <div 
                v-for="(gap, idx) in gapBriefs" 
                :key="idx" 
                class="gap-tag"
                :class="`level-${gap.level}`"
              >
                {{ gap.title }}
              </div>
            </div>
          </section>
        </div>
      </div>

      <!-- 阶段切换标签 -->
      <div class="phase-tabs">
        <el-radio-group v-model="activePhase" size="large" fill="#6366f1">
          <el-radio-button label="short">短期计划 (1-3月)</el-radio-button>
          <el-radio-button label="mid">中期计划 (3-12月)</el-radio-button>
          <el-radio-button label="tips">学习建议</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 动态内容区 -->
      <Transition name="slide-fade" mode="out-in">
        <!-- 短期/中期计划 -->
        <div v-if="activePhase === 'short' || activePhase === 'mid'" class="phase-content" :key="activePhase">
          <div class="phase-header-card">
            <div class="phase-title-section">
              <h2>{{ currentPlan.goal }}</h2>
              <div class="phase-meta">
                <el-tag :type="activePhase === 'short' ? 'success' : 'warning'" effect="dark" round>
                  {{ currentPlan.duration }}
                </el-tag>
                <span class="milestone-count">{{ currentPlan.milestones.length }} 个里程碑</span>
              </div>
            </div>
            
            <!-- 技能路线图或重点领域 -->
            <div class="skills-cloud">
              <span 
                v-for="(skill, idx) in activePhase === 'short' ? (currentPlan as ShortTermPlan).focus_areas : (currentPlan as MidTermPlan).skill_roadmap" 
                :key="idx"
                class="skill-item"
                :style="{ animationDelay: `${idx * 0.1}s` }"
              >
                {{ skill }}
              </span>
            </div>
          </div>

          <!-- 里程碑时间线 -->
          <div class="milestones-timeline">
            <el-timeline>
              <el-timeline-item
                v-for="(milestone, idx) in currentPlan.milestones"
                :key="idx"
                :type="activePhase === 'short' ? 'success' : 'warning'"
                :hollow="true"
                placement="top"
              >
                <el-card class="milestone-card" shadow="hover">
                  <template #header>
                    <div class="milestone-header" @click="toggleMilestone(idx)">
                      <div class="milestone-title-wrapper">
                        <h4>{{ milestone.milestone_name }}</h4>
                        <el-tag size="small" effect="plain">{{ milestone.target_date }}</el-tag>
                      </div>
                      <el-icon class="expand-icon" :class="{ expanded: expandedMilestones.includes(idx) }">
                        <Arrow-Down-Bold />
                      </el-icon>
                    </div>
                  </template>
                  
                  <div v-show="expandedMilestones.includes(idx)" class="milestone-body">
                    <!-- 关键成果 -->
                    <div class="key-results">
                      <div class="sub-title">关键成果</div>
                      <ul class="result-list">
                        <li v-for="(kr, kidx) in milestone.key_results" :key="kidx">
                          <el-icon color="#10b981"><Check /></el-icon>
                          <span>{{ kr }}</span>
                        </li>
                      </ul>
                    </div>

                    <!-- 任务列表（横向滚动或弹窗） -->
                    <div class="tasks-section">
                      <div class="sub-title">
                        任务清单
                        <el-button text type="primary" size="small" @click="openTasksDialog(milestone)">
                          查看全部 {{ milestone.tasks.length }} 个任务
                        </el-button>
                      </div>
                      <div class="tasks-preview">
                        <div 
                          v-for="task in milestone.tasks.slice(0, 2)" 
                          :key="task.task_name"
                          class="task-preview-card"
                          @click="openTaskDetail(task)"
                        >
                          <div class="task-header">
                            <span class="task-name">{{ task.task_name }}</span>
                            <el-tag 
                              :type="getPriorityType(task.priority)" 
                              size="small" 
                              effect="dark"
                            >
                              {{ task.priority }}
                            </el-tag>
                          </div>
                          <div class="task-meta">
                            <span><el-icon><Timer /></el-icon> {{ task.estimated_time }}</span>
                            <span v-if="task.resources.length">
                              <el-icon><Document /></el-icon> {{ task.resources.length }} 资源
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>

          <!-- 快速见效或职业预期 -->
          <div v-if="activePhase === 'short'" class="quick-wins-section">
            <h3>快速见效行动</h3>
            <el-row :gutter="16">
              <el-col 
                v-for="(win, idx) in (currentPlan as ShortTermPlan).quick_wins" 
                :key="idx"
                :xs="24" 
                :sm="12" 
                :md="8"
              >
                <div class="quick-win-card" :style="{ animationDelay: `${idx * 0.1}s` }">
                  <div class="win-icon">⚡</div>
                  <div class="win-text">{{ win }}</div>
                </div>
              </el-col>
            </el-row>
          </div>

          <div v-else class="career-preview-section">
            <h3>职业发展预期</h3>
            <el-alert 
              :title="(currentPlan as MidTermPlan).career_progression"
              type="info"
              :closable="false"
              show-icon
              class="career-alert"
            />
            
            <!-- 实习推荐轮播 -->
            <div class="internship-carousel-section">
              <div class="section-header-row">
                <h4>推荐实习岗位</h4>
                <el-button text type="primary" @click="internDialogVisible = true">
                  查看全部
                </el-button>
              </div>
              <el-carousel :interval="5000" type="card" height="280px">
                <el-carousel-item 
                  v-for="job in (currentPlan as MidTermPlan).recommended_internships" 
                  :key="job.id"
                >
                  <div class="intern-card" @click="openInternDetail(job)">
                    <div class="intern-company-header">
                      <div 
                        class="company-logo" 
                        :style="{ backgroundColor: stringToColor(job.company_name) }"
                      >
                        {{ job.company_name.charAt(0) }}
                      </div>
                      <div class="company-info">
                        <div class="job-title">{{ job.job_title }}</div>
                        <div class="company-name">{{ job.company_name }}</div>
                      </div>
                    </div>
                    <div class="job-meta-tags">
                      <el-tag size="small">{{ job.city }}</el-tag>
                      <el-tag size="small" type="warning">{{ job.salary }}</el-tag>
                      <el-tag size="small" type="info">{{ job.job_type }}</el-tag>
                    </div>
                    <div class="job-reason" v-if="job.reason">{{ job.reason }}</div>
                    <div v-if="job.match_score" class="match-badge">
                      匹配度 {{ job.match_score }}%
                    </div>
                  </div>
                </el-carousel-item>
              </el-carousel>
            </div>
          </div>
        </div>

        <!-- 学习建议 -->
        <div v-else class="tips-content" key="tips">
          <el-row :gutter="24">
            <el-col :xs="24" :lg="16">
              <div class="tips-carousel-wrapper">
                <el-carousel direction="vertical" :interval="6000" height="300px" indicator-position="outside">
                  <el-carousel-item v-for="(tip, idx) in data.tips" :key="idx">
                    <div class="tip-card-large">
                      <div class="tip-number">0{{ idx + 1 }}</div>
                      <div class="tip-content">{{ tip }}</div>
                      <div class="tip-decoration">
                        <el-icon :size="60" color="rgba(99, 102, 241, 0.2)"><Chat-Dot-Round /></el-icon>
                      </div>
                    </div>
                  </el-carousel-item>
                </el-carousel>
              </div>
            </el-col>
            <el-col :xs="24" :lg="8">
              <div class="stats-panel">
                <h4>数据统计</h4>
                <div ref="pieChartRef" class="pie-chart"></div>
                <div class="stats-list">
                  <div class="stat-line">
                    <span>总里程碑</span>
                    <span class="value">{{ totalMilestones }}</span>
                  </div>
                  <div class="stat-line">
                    <span>总任务数</span>
                    <span class="value">{{ totalTasks }}</span>
                  </div>
                  <div class="stat-line">
                    <span>学习资源</span>
                    <span class="value">{{ totalResources }}</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </Transition>

      <!-- 行动清单抽屉 -->
      <el-drawer
        v-model="drawerVisible"
        title="全部行动计划"
        size="500px"
        class="action-drawer"
      >
        <div class="drawer-content">
          <el-timeline>
            <el-timeline-item
              v-for="(action, idx) in data.action_checklist"
              :key="idx"
              :type="checkedActions[idx] ? 'success' : 'primary'"
              :icon="checkedActions[idx] ? Check : CircleCheck"
            >
              <el-card 
                :class="{ 'is-checked': checkedActions[idx] }"
                shadow="hover"
                @click="toggleAction(idx)"
              >
                <div class="timeline-action-content">
                  <el-checkbox 
                    v-model="checkedActions[idx]" 
                    size="large"
                    @click.stop
                  >
                    <span :class="{ 'text-checked': checkedActions[idx] }">{{ action }}</span>
                  </el-checkbox>
                  <el-tag v-if="checkedActions[idx]" type="success" effect="dark" round>
                    已完成
                  </el-tag>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-drawer>

      <!-- 任务详情弹窗 -->
      <el-dialog
        v-model="taskDialogVisible"
        :title="selectedMilestone?.milestone_name"
        width="800px"
        class="tasks-dialog"
        destroy-on-close
      >
        <div v-if="selectedMilestone" class="tasks-dialog-content">
          <div class="milestone-summary">
            <el-tag effect="plain">目标时间：{{ selectedMilestone.target_date }}</el-tag>
          </div>
          
          <el-collapse v-model="expandedTasks" class="tasks-collapse">
            <el-collapse-item
              v-for="(task, idx) in selectedMilestone.tasks"
              :key="idx"
              :name="idx"
              class="task-collapse-item"
            >
              <template #title>
                <div class="collapse-title-content">
                  <span class="task-title-text">{{ task.task_name }}</span>
                  <div class="task-badges">
                    <el-tag :type="getPriorityType(task.priority)" size="small" effect="dark">
                      {{ task.priority }}优先级
                    </el-tag>
                    <el-tag type="info" size="small" effect="plain">
                      <el-icon><Timer /></el-icon> {{ task.estimated_time }}
                    </el-tag>
                  </div>
                </div>
              </template>
              
              <div class="task-detail-content">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="任务描述">{{ task.description }}</el-descriptions-item>
                  <el-descriptions-item label="技能目标">{{ task.skill_target }}</el-descriptions-item>
                  <el-descriptions-item label="成功标准">{{ task.success_criteria }}</el-descriptions-item>
                </el-descriptions>
                
                <div v-if="task.resources.length" class="resources-section">
                  <div class="section-title">推荐资源 ({{ task.resources.length }})</div>
                  <div class="resources-grid">
                    <div 
                      v-for="resource in task.resources" 
                      :key="resource.id"
                      class="resource-item"
                      @click="openResource(resource)"
                    >
                      <div class="resource-icon">{{ getResourceIcon(resource) }}</div>
                      <div class="resource-info">
                        <div class="resource-name">{{ getResourceTitle(resource) }}</div>
                        <div class="resource-meta">{{ getResourceMeta(resource) }}</div>
                      </div>
                      <el-icon><Arrow-Right /></el-icon>
                    </div>
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-dialog>

      <!-- 资源详情抽屉 -->
      <el-drawer
        v-model="resourceDrawerVisible"
        :title="currentResource ? getResourceTitle(currentResource) : '资源详情'"
        size="450px"
        class="resource-drawer"
      >
        <div v-if="currentResource" class="resource-detail">
          <div class="resource-type-header" :class="currentResource.type">
            <div class="type-icon">{{ getResourceIcon(currentResource) }}</div>
            <div class="type-label">{{ currentResource.type.toUpperCase() }}</div>
          </div>
          
          <div class="resource-content">
            <h3>{{ getResourceTitle(currentResource) }}</h3>
            <p class="resource-reason" v-if="currentResource.reason">
              <el-icon><Info-Filled /></el-icon>
              {{ currentResource.reason }}
            </p>
            
            <el-descriptions :column="1" border class="resource-meta-list">
              <template v-if="currentResource.type === 'video'">
                <el-descriptions-item label="作者">{{ (currentResource as VideoResource).author }}</el-descriptions-item>
                <el-descriptions-item label="分类">{{ (currentResource as VideoResource).category }}</el-descriptions-item>
                <el-descriptions-item label="发布时间">{{ (currentResource as VideoResource).publish_date }}</el-descriptions-item>
              </template>
              <template v-if="currentResource.type === 'book'">
                <el-descriptions-item label="作者">{{ (currentResource as BookResource).author }}</el-descriptions-item>
                <el-descriptions-item label="出版社">{{ (currentResource as BookResource).publisher }}</el-descriptions-item>
                <el-descriptions-item label="ISBN">{{ (currentResource as BookResource).isbn }}</el-descriptions-item>
              </template>
              <template v-if="currentResource.type === 'project'">
                <el-descriptions-item label="Star数">{{ (currentResource as ProjectResource).stars }}</el-descriptions-item>
                <el-descriptions-item label="语言">{{ (currentResource as ProjectResource).language }}</el-descriptions-item>
                <el-descriptions-item label="难度">{{ (currentResource as ProjectResource).difficulty }}</el-descriptions-item>
              </template>
              <el-descriptions-item label="简介" :span="2">
                <div class="resource-desc-text">{{ currentResource.content }}</div>
              </el-descriptions-item>
            </el-descriptions>
            
            <el-button 
              type="primary" 
              size="large" 
              class="visit-btn"
              @click="openExternalLink(currentResource.url)"
            >
              <el-icon><Link /></el-icon>
              访问资源
            </el-button>
          </div>
        </div>
      </el-drawer>

      <!-- 岗位详情弹窗 -->
      <el-dialog
        v-model="internDetailVisible"
        title="岗位详情"
        width="700px"
        class="intern-dialog"
      >
        <div v-if="selectedIntern" class="intern-detail-content">
          <div class="intern-header-detail">
            <div 
              class="big-logo" 
              :style="{ backgroundColor: stringToColor(selectedIntern.company_name) }"
            >
              {{ selectedIntern.company_name.charAt(0) }}
            </div>
            <div class="header-info">
              <h2>{{ selectedIntern.job_title }}</h2>
              <div class="company-full">{{ selectedIntern.company_name }} · {{ selectedIntern.company_industry }} · {{ selectedIntern.company_scale }}</div>
              <div class="location-salary">
                <span><el-icon><Location /></el-icon> {{ selectedIntern.city }}</span>
                <el-divider direction="vertical" />
                <span><el-icon><Money /></el-icon> {{ selectedIntern.salary }}</span>
              </div>
            </div>
          </div>
          
          <el-descriptions :column="2" border class="intern-meta-table">
            <el-descriptions-item label="学历要求">{{ selectedIntern.degree }}</el-descriptions-item>
            <el-descriptions-item label="实习类型">{{ selectedIntern.job_type }}</el-descriptions-item>
            <el-descriptions-item label="每周天数">{{ selectedIntern.days_per_week }} 天</el-descriptions-item>
            <el-descriptions-item label="实习时长">{{ selectedIntern.months }} 个月</el-descriptions-item>
          </el-descriptions>
          
          <div class="intern-section">
            <h4>技术栈</h4>
            <div class="tech-tags">
              <el-tag 
                v-for="tech in selectedIntern.tech_stack.split(',')" 
                :key="tech"
                size="large"
                effect="dark"
                round
              >
                {{ tech.trim() }}
              </el-tag>
            </div>
          </div>
          
          <div class="intern-section">
            <h4>岗位描述</h4>
            <p class="desc-text">{{ selectedIntern.content }}</p>
          </div>
          
          <div class="intern-section" v-if="selectedIntern.reason">
            <h4>推荐理由</h4>
            <el-alert :title="selectedIntern.reason" type="success" :closable="false" show-icon />
          </div>
          
          <el-button type="primary" size="large" class="apply-btn" @click="openExternalLink(selectedIntern.url)">
            查看投递链接
          </el-button>
        </div>
      </el-dialog>

      <!-- 实习列表弹窗 -->
      <el-dialog
        v-model="internDialogVisible"
        title="全部推荐岗位"
        width="900px"
        class="interns-list-dialog"
      >
        <div class="interns-grid">
          <div 
            v-for="job in allInternships" 
            :key="job.id"
            class="intern-grid-card"
            @click="openInternDetail(job)"
          >
            <div class="card-top">
              <div class="company-tag">{{ job.company_name }}</div>
              <div class="match-tag" v-if="job.match_score">{{ job.match_score }}% 匹配</div>
            </div>
            <div class="job-title-text">{{ job.job_title }}</div>
            <div class="job-brief-meta">
              {{ job.city }} · {{ job.salary }} · {{ job.job_type }}
            </div>
          </div>
        </div>
      </el-dialog>

      <!-- 差距分析弹窗 -->
      <el-dialog
        v-model="gapDialogVisible"
        title="能力差距详细分析"
        width="800px"
        class="gap-dialog"
      >
        <div class="gap-analysis">
          <div ref="gapChartRef" class="gap-chart"></div>
          <div class="gap-list">
            <div 
              v-for="(gap, idx) in parsedGaps" 
              :key="idx"
              class="gap-detail-item"
              :class="`priority-${gap.level}`"
            >
              <div class="gap-header">
                <span class="gap-title">{{ gap.title }}</span>
                <el-tag :type="gap.level === 1 ? 'danger' : gap.level === 2 ? 'warning' : 'info'" size="small" effect="dark">
                  {{ gap.level === 1 ? '高优' : gap.level === 2 ? '重要' : '一般' }}
                </el-tag>
              </div>
              <p class="gap-desc">{{ gap.desc }}</p>
            </div>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  InfoFilled, User, Warning, ArrowRight, ArrowDownBold,
  Check, CircleCheck, Timer, Document, ChatDotRound,
  Link, Location, Money
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== 严格类型定义 ====================

type Priority = '高' | '中' | '低'

type ResourceType = 'video' | 'book' | 'project'

interface BaseResource {
  id: string
  type: ResourceType
  reason: string
  content: string
  url: string
}

interface VideoResource extends BaseResource {
  type: 'video'
  title: string
  author: string
  cover_image?: string
  category: string
  category_name?: string
  tags?: string
  play_count?: string
  like_count?: string
  favorite_count?: string
  duration?: string
  publish_date?: string
}

interface BookResource extends BaseResource {
  type: 'book'
  title: string
  author: string
  translator?: string
  publisher?: string
  publish_date?: string
  isbn?: string
  pages?: string
  cover_url?: string
  rating_score?: string
  category?: string
  keyword?: string
}

interface ProjectResource extends BaseResource {
  type: 'project'
  name: string
  description: string
  tech_tags?: string
  use_cases?: string
  difficulty?: '初级' | '进阶'
  stars?: number
  language?: string
}

type ResourceItem = VideoResource | BookResource | ProjectResource

interface TaskItem {
  task_name: string
  description: string
  priority: Priority
  estimated_time: string
  skill_target: string
  success_criteria: string
  resources: ResourceItem[]
}

interface MilestoneItem {
  milestone_name: string
  target_date: string
  key_results: string[]
  tasks: TaskItem[]
}

interface ShortTermPlan {
  duration: string
  goal: string
  focus_areas: string[]
  milestones: MilestoneItem[]
  quick_wins: string[]
}

interface InternshipItem {
  id: string
  job_title: string
  company_name: string
  company_industry: string
  company_scale: string
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
  match_score?: number
}

interface MidTermPlan {
  duration: string
  goal: string
  skill_roadmap: string[]
  milestones: MilestoneItem[]
  career_progression: string
  recommended_internships: InternshipItem[]
}

interface GrowthPlanData {
  student_summary: string
  target_position: string
  target_position_profile_summary: string
  current_gap: string
  short_term_plan: ShortTermPlan
  mid_term_plan: MidTermPlan
  action_checklist: string[]
  tips: string[]
}

// ==================== 数据与状态 ====================

const data = ref<GrowthPlanData>({
  student_summary: '计算机科学与技术专业本科在读，具备Java、MySQL、HTML/CSS/JavaScript基础技能，掌握Git、Maven、IDEA等开发工具。有学生信息管理系统（后端开发）和校园网站（前端开发）项目经验，获蓝桥杯程序设计竞赛省级三等奖。英语能力良好（CET-6 520分），学习能力强（评分4/5），逻辑思维清晰（评分4/5），职业倾向技术型。核心短板：无实习经历，缺乏Spring Boot、MyBatis等企业级框架经验，数据库优化能力薄弱，无分布式系统知识，缺少有竞争力的开源项目。',
  target_position: 'Java后端开发工程师',
  target_position_profile_summary: '负责服务端架构设计与开发，要求精通Spring Boot、MyBatis等主流框架，熟悉MySQL数据库设计与优化，了解分布式系统原理，具备良好的代码规范意识和团队协作能力。',
  current_gap: '1. 企业级框架掌握不足：对Spring Boot、MyBatis等主流框架缺乏系统学习和实战经验；2. 数据库能力薄弱：数据库设计、SQL优化、索引优化等能力不足；3. 分布式微服务知识空白：对分布式系统、微服务架构缺乏了解；4. 项目经验不足：缺少企业级项目开发经验，简历竞争力不够；5. 无实习经历：缺乏实际工作经验和团队协作经验。',
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
          '完成至少1个Spring Boot实战项目（博客系统或商城模块）'
        ],
        tasks: [
          {
            task_name: '学习Spring Boot核心概念与基础开发',
            description: '通过视频教程系统学习Spring Boot框架，包括项目搭建、配置文件、常用注解、依赖注入、AOP等核心概念，理解Spring Boot自动配置原理',
            priority: '高',
            estimated_time: '2周',
            skill_target: 'Spring Boot框架开发能力',
            success_criteria: '能够独立搭建Spring Boot项目，理解IOC容器和AOP原理，掌握常用注解的使用场景',
            resources: [
              {
                id: 'v001',
                type: 'video',
                title: '黑马程序员SpringBoot教程',
                author: '黑马程序员',
                url: 'https://www.bilibili.com/video/BV1Lq4y1J77x',
                category: '后端开发',
                publish_date: '2021-05-04',
                play_count: '125.3万',
                duration: '6:23:45',
                reason: '适合快速入门，覆盖Spring Boot核心知识点',
                content: '6小时快速入门Spring Boot，从基础到实战，适合夯实基础。'
              },
              {
                id: 'b001',
                type: 'book',
                title: 'Spring Boot实战',
                author: '汪云飞',
                publisher: '电子工业出版社',
                isbn: '9787121384321',
                rating_score: '8.5',
                url: 'https://book.douban.com/subject/xxxx',
                reason: '经典入门书籍，理论与实践结合',
                content: '本书从Spring Boot的基础知识讲起，逐步深入到企业级应用开发。'
              }
            ]
          },
          {
            task_name: '完成Spring Boot+Vue前后端分离博客项目',
            description: '跟随实战教程完成一个完整的前后端分离博客系统，包括用户管理、文章发布、评论功能、分类标签等模块。',
            priority: '高',
            estimated_time: '3周',
            skill_target: '企业级项目开发能力、RESTful API设计',
            success_criteria: '完成项目开发并部署运行，能够演示完整功能',
            resources: [
              {
                id: 'p001',
                type: 'project',
                name: 'vue-springboot-blog',
                description: '基于Vue.js和Spring Boot的前后端分离博客系统',
                stars: 1250,
                language: 'Java',
                difficulty: '初级',
                tech_tags: 'Spring Boot,Vue.js,MyBatis,MySQL',
                url: 'https://github.com/example/blog',
                reason: '项目结构清晰，适合作为第一个实战项目',
                content: '完整的博客系统，包含用户认证、文章管理、评论系统等模块。'
              }
            ]
          }
        ]
      },
      {
        milestone_name: 'MySQL数据库设计与优化能力提升',
        target_date: '第2个月末',
        key_results: ['掌握索引、锁机制、执行计划分析', '能够进行SQL性能分析和优化'],
        tasks: [
          {
            task_name: '系统学习MySQL高级知识',
            description: '深入学习索引原理、锁机制、事务隔离级别、执行计划分析、慢查询优化。',
            priority: '高',
            estimated_time: '2周',
            skill_target: 'MySQL数据库优化能力',
            success_criteria: '能够分析执行计划，识别慢查询原因，掌握索引优化策略',
            resources: []
          }
        ]
      }
    ],
    quick_wins: [
      '本周内完成Spring Boot开发环境搭建（JDK 17、Maven 3.8+、IDEA）',
      '注册GitHub账号并Fork mall项目，开始研读项目文档',
      '制定每日学习计划：工作日每天2小时，周末每天6小时'
    ]
  },
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
                id: 'b002',
                type: 'book',
                title: '深入理解分布式系统',
                author: '唐伟志',
                publisher: '机械工业出版社',
                isbn: '9787111681234',
                rating_score: '9.0',
                url: 'https://book.douban.com/subject/35794814/',
                reason: '系统讲解分布式系统原理，为微服务学习打下理论基础',
                content: '全面介绍分布式系统的核心概念、算法和实践。'
              }
            ]
          }
        ]
      }
    ],
    career_progression: '具备1年以上企业级项目开发经验，熟练掌握Spring Boot+MyBatis+Spring Cloud技术栈，能够独立负责模块开发，有大型互联网实习经历。',
    recommended_internships: [
      {
        id: 'i001',
        job_title: 'Java后端开发实习生',
        company_name: '字节跳动',
        company_industry: '互联网',
        company_scale: '10000人以上',
        salary: '400-500元/天',
        city: '北京',
        degree: '本科及以上',
        days_per_week: 4,
        months: 3,
        job_type: '日常实习',
        tech_stack: 'Java,MySQL,Redis,Spring Boot',
        url: 'https://job.bytedance.com/',
        content: '负责抖音电商后台服务开发，参与高并发系统设计与优化。',
        reason: '大厂核心部门，技术氛围好，能接触到高并发场景',
        match_score: 92
      },
      {
        id: 'i002',
        job_title: '后端工程师实习生',
        company_name: '美团',
        company_industry: '生活服务',
        company_scale: '10000人以上',
        salary: '300-400元/天',
        city: '北京',
        degree: '本科',
        days_per_week: 5,
        months: 6,
        job_type: '暑期实习',
        tech_stack: 'Java,MySQL,Kafka,Microservices',
        url: 'https://zhaopin.meituan.com/',
        content: '参与美团外卖后端系统开发，负责订单、配送等核心业务模块。',
        reason: '业务复杂度高，能锻炼系统设计能力，转正机会大',
        match_score: 88
      }
    ]
  },
  action_checklist: [
    '本周内完成Spring Boot开发环境搭建（JDK 17、Maven 3.8+、IDEA）',
    '注册GitHub账号并Fork mall项目，开始研读项目文档',
    '制定每日学习计划：工作日每天2小时，周末每天6小时',
    '准备简历模板，梳理项目经验和技术栈',
    '完成牛客网Java基础100题练习',
    '参加至少一次技术分享会或线上直播'
  ],
  tips: [
    '先掌握Spring Boot单体应用开发，再学习Spring Cloud微服务架构，循序渐进',
    '项目经验是核心竞争力：务必完成2-3个有质量的项目并部署到云服务器',
    '重视Java基础、数据库、计算机网络等底层知识，面试必考',
    '通过博客、GitHub、社区问答建立个人技术影响力，展示学习能力',
    '算法要持续刷题，建议每日LeetCode一题，保持手感'
  ]
})

// 状态管理
const activePhase = ref<'short' | 'mid' | 'tips'>('short')
const checkedActions = reactive<Record<number, boolean>>({})
const expandedMilestones = ref<number[]>([0])
const drawerVisible = ref(false)
const taskDialogVisible = ref(false)
const selectedMilestone = ref<MilestoneItem | null>(null)
const expandedTasks = ref<number[]>([0])
const resourceDrawerVisible = ref(false)
const currentResource = ref<ResourceItem | null>(null)
const internDetailVisible = ref(false)
const selectedIntern = ref<InternshipItem | null>(null)
const internDialogVisible = ref(false)
const gapDialogVisible = ref(false)

// 图表Refs
const radarChartRef = ref<HTMLDivElement>()
const pieChartRef = ref<HTMLDivElement>()
const gapChartRef = ref<HTMLDivElement>()
let charts: echarts.ECharts[] = []

// ==================== 计算属性 ====================

const currentPlan = computed<ShortTermPlan | MidTermPlan>(() => {
  return activePhase.value === 'short' ? data.value.short_term_plan : data.value.mid_term_plan
})

const actionProgress = computed(() => {
  const total = data.value.action_checklist.length
  const completed = Object.values(checkedActions).filter(Boolean).length
  return total ? Math.round((completed / total) * 100) : 0
})

const progressStyle = computed(() => ({
  background: `conic-gradient(#6366f1 ${actionProgress.value * 3.6}deg, #e5e7eb 0deg)`
}))

const headerStats = computed(() => [
  { label: '短期里程碑', value: data.value.short_term_plan.milestones.length, type: 'success' },
  { label: '中期里程碑', value: data.value.mid_term_plan.milestones.length, type: 'warning' },
  { label: '推荐岗位', value: data.value.mid_term_plan.recommended_internships.length, type: 'info' },
  { label: '行动项', value: data.value.action_checklist.length, type: 'primary' }
])

const totalMilestones = computed(() => 
  data.value.short_term_plan.milestones.length + data.value.mid_term_plan.milestones.length
)

const totalTasks = computed(() => {
  let count = 0
  const countTasks = (plan: ShortTermPlan | MidTermPlan) => {
    plan.milestones.forEach(m => { count += m.tasks.length })
  }
  countTasks(data.value.short_term_plan)
  countTasks(data.value.mid_term_plan)
  return count
})

const totalResources = computed(() => {
  let count = 0
  const countRes = (plan: ShortTermPlan | MidTermPlan) => {
    plan.milestones.forEach(m => {
      m.tasks.forEach(t => { count += t.resources.length })
    })
  }
  countRes(data.value.short_term_plan)
  countRes(data.value.mid_term_plan)
  return count
})

const allInternships = computed(() => data.value.mid_term_plan.recommended_internships)

const gapBriefs = computed(() => {
  const gaps = data.value.current_gap.split(/;\s*|；/).filter(Boolean).slice(0, 3)
  return gaps.map((g, i) => ({
    title: g.split('：')[0]?.replace(/^\d+\.\s*/, '') || g.slice(0, 20),
    level: i < 2 ? 1 : 2
  }))
})

const parsedGaps = computed(() => {
  return data.value.current_gap.split(/;\s*|；/).filter(Boolean).map(gap => {
    const match = gap.match(/^\d+\.\s*(.+?)[:：](.+)$/)
    if (match) {
      const titleText = match[1]?.trim() ?? ''
      const descText = match[2]?.trim() ?? ''
      return {
        title: titleText,
        desc: descText,
        level: titleText.includes('框架') || titleText.includes('数据库') ? 1 : 2
      }
    }
    return { title: '能力短板', desc: gap, level: 2 }
  })
})

// ==================== 方法 ====================

function toggleAction(index: number): void {
  checkedActions[index] = !checkedActions[index]
}

function toggleMilestone(index: number): void {
  const i = expandedMilestones.value.indexOf(index)
  if (i > -1) {
    expandedMilestones.value.splice(i, 1)
  } else {
    expandedMilestones.value.push(index)
  }
}

function openTasksDialog(milestone: MilestoneItem): void {
  selectedMilestone.value = milestone
  expandedTasks.value = [0]
  taskDialogVisible.value = true
}

function openTaskDetail(task: TaskItem): void {
  const resource = task.resources[0]
  if (resource) {
    openResource(resource)
  }
}

function openResource(resource: ResourceItem): void {
  currentResource.value = resource
  resourceDrawerVisible.value = true
}

function openInternDetail(intern: InternshipItem): void {
  selectedIntern.value = intern
  internDetailVisible.value = true
}

function openExternalLink(url: string): void {
  window.open(url, '_blank')
}

function getPriorityType(priority: Priority): '' | 'danger' | 'warning' | 'info' {
  const map: Record<Priority, '' | 'danger' | 'warning' | 'info'> = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return map[priority] || ''
}

function stringToColor(str: string): string {
  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6']
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash + str.charCodeAt(i)) | 0  // 限制为32位整数
  }
  // 使用无符号右移处理负哈希值，避免 Math.abs(Integer.MIN_VALUE) 问题
  return (colors[(hash >>> 0) % colors.length] ?? colors[0]) as string
}

function getResourceIcon(resource: ResourceItem): string {
  const icons: Record<ResourceType, string> = {
    video: '▶️',
    book: '📚',
    project: '💻'
  }
  return icons[resource.type]
}

function getResourceTitle(resource: ResourceItem): string {
  if (resource.type === 'project') return (resource as ProjectResource).name
  return (resource as VideoResource | BookResource).title
}

function getResourceMeta(resource: ResourceItem): string {
  if (resource.type === 'video') return (resource as VideoResource).author
  if (resource.type === 'book') return (resource as BookResource).author
  return (resource as ProjectResource).language || 'Open Source'
}

// ==================== ECharts ====================

function initRadarChart(): void {
  if (!radarChartRef.value) return
  const chart = echarts.init(radarChartRef.value)
  chart.setOption({
    color: ['#6366f1', '#10b981'],
    radar: {
      indicator: [
        { name: 'Java基础', max: 100 },
        { name: 'Spring生态', max: 100 },
        { name: '数据库', max: 100 },
        { name: '分布式', max: 100 },
        { name: '项目经验', max: 100 },
        { name: '算法', max: 100 }
      ],
      radius: '65%',
      splitNumber: 4,
      axisName: { color: '#6b7280', fontSize: 11 },
      splitLine: { lineStyle: { color: '#e5e7eb' } },
      splitArea: { show: false }
    },
    series: [{
      type: 'radar',
      data: [
        { value: [75, 30, 50, 10, 40, 65], name: '当前水平', areaStyle: { opacity: 0.2 } },
        { value: [85, 90, 85, 80, 85, 80], name: '目标要求', areaStyle: { opacity: 0.2 }, lineStyle: { type: 'dashed' } }
      ]
    }],
    legend: { bottom: 0, data: ['当前水平', '目标要求'], itemGap: 20 }
  })
  charts.push(chart)
}

function initPieChart(): void {
  if (!pieChartRef.value) return
  const chart = echarts.init(pieChartRef.value)
  chart.setOption({
    color: ['#6366f1', '#10b981', '#f59e0b', '#ef4444'],
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data: [
        { name: '短期任务', value: 8 },
        { name: '中期任务', value: 4 },
        { name: '已完成', value: 3 },
        { name: '待开始', value: 9 }
      ]
    }]
  })
  charts.push(chart)
}

function initGapChart(): void {
  if (!gapChartRef.value || !gapDialogVisible.value) return
  const chart = echarts.init(gapChartRef.value)
  const gaps = parsedGaps.value.slice(0, 5)
  chart.setOption({
    radar: {
      indicator: gaps.map(g => ({ name: g.title.slice(0, 4), max: 100 })),
      radius: '60%'
    },
    series: [{
      type: 'radar',
      data: [{
        value: gaps.map(g => g.level === 1 ? 90 : 70),
        name: '紧迫度',
        areaStyle: { color: 'rgba(239, 68, 68, 0.2)' },
        lineStyle: { color: '#ef4444' }
      }]
    }]
  })
  charts.push(chart)
}

// ==================== 生命周期 ====================

onMounted(() => {
  nextTick(() => {
    initRadarChart()
    initPieChart()
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach(chart => chart.dispose())
  charts = []
})

function handleResize(): void {
  charts.forEach(chart => chart.resize())
}

watch(gapDialogVisible, (val) => {
  if (val) setTimeout(initGapChart, 100)
})
</script>

<style scoped>
/* ==================== 基础样式 ==================== */
.growth-plan-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 32px 24px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.max-width-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

/* ==================== Header Section ==================== */
.plan-header-section {
  margin-bottom: 32px;
}

.header-content {
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
  border-radius: 24px;
  padding: 40px;
  color: white;
  position: relative;
  overflow: hidden;
}

.header-content::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%);
  border-radius: 50%;
}

.position-badge {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.plan-type-tag {
  background: rgba(255, 255, 255, 0.2) !important;
  border: none;
  color: white !important;
  font-weight: 600;
}

.position-title {
  font-size: 36px;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(to right, #fff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.position-summary {
  font-size: 16px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  max-width: 600px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.header-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  position: relative;
  z-index: 1;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.15);
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 4px;
}

.stat-value.success { color: #34d399; }
.stat-value.warning { color: #fbbf24; }
.stat-value.info { color: #60a5fa; }
.stat-value.primary { color: #a78bfa; }

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* ==================== 主网格布局 ==================== */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  margin-bottom: 32px;
}

.left-column, .right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ==================== 图表区域 ==================== */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
  font-weight: 700;
}

.radar-chart {
  height: 300px;
  width: 100%;
}

.ability-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6b7280;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.current { background: #6366f1; }
.dot.target { background: #10b981; }

/* ==================== 卡片样式 ==================== */
.info-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  border-color: #e0e7ff;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 12px;
}

.profile-text {
  color: #4b5563;
  line-height: 1.8;
  font-size: 14px;
  margin: 0;
}

.gap-brief {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.gap-tag {
  padding: 6px 12px;
  background: #fef2f2;
  color: #dc2626;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.gap-tag.level-2 {
  background: #fff7ed;
  color: #ea580c;
}

/* ==================== 进度区域 ==================== */
.progress-section {
  background: white;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  display: flex;
  gap: 32px;
  align-items: center;
}

.progress-ring-wrapper {
  flex-shrink: 0;
}

.progress-ring {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.progress-content {
  width: 110px;
  height: 110px;
  background: white;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.progress-percent {
  font-size: 32px;
  font-weight: 800;
  color: #6366f1;
  line-height: 1;
}

.progress-label {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.action-preview {
  flex: 1;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  color: #1f2937;
}

.action-list-preview {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.action-item:hover {
  background: #f3f4f6;
  border-color: #e5e7eb;
}

.action-item.completed {
  background: #ecfdf5;
  opacity: 0.7;
}

.action-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.action-item.completed .action-text {
  text-decoration: line-through;
  color: #9ca3af;
}

/* ==================== 阶段标签 ==================== */
.phase-tabs {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

:deep(.el-radio-button__inner) {
  padding: 12px 32px;
  font-size: 15px;
  font-weight: 600;
}

/* ==================== 阶段内容 ==================== */
.phase-content, .tips-content {
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.phase-header-card {
  background: white;
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.phase-title-section {
  margin-bottom: 24px;
}

.phase-title-section h2 {
  margin: 0 0 12px 0;
  font-size: 22px;
  color: #1f2937;
  font-weight: 700;
  line-height: 1.4;
}

.phase-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.milestone-count {
  color: #6b7280;
  font-size: 14px;
}

.skills-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-item {
  padding: 10px 18px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #3730a3;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 600;
  animation: popIn 0.4s ease backwards;
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

/* ==================== 里程碑时间线 ==================== */
.milestones-timeline {
  margin-bottom: 32px;
}

:deep(.el-timeline-item__node) {
  background-color: #6366f1 !important;
}

.milestone-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  margin-bottom: 8px;
}

.milestone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 4px 0;
}

.milestone-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.milestone-title-wrapper h4 {
  margin: 0;
  font-size: 16px;
  color: #1f2937;
  font-weight: 700;
}

.expand-icon {
  color: #9ca3af;
  transition: transform 0.3s;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.milestone-body {
  padding-top: 20px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.sub-title {
  font-size: 14px;
  font-weight: 700;
  color: #374151;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-list {
  list-style: none;
  padding: 0;
  margin: 0 0 20px 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
}

.tasks-preview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.task-preview-card {
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.task-preview-card:hover {
  border-color: #6366f1;
  background: #f5f3ff;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 8px;
}

.task-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #6b7280;
}

.task-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ==================== 快速见效 ==================== */
.quick-wins-section, .career-preview-section {
  margin-bottom: 32px;
}

.quick-wins-section h3, .career-preview-section h3 {
  font-size: 18px;
  color: #1f2937;
  margin-bottom: 16px;
  font-weight: 700;
}

.quick-win-card {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border: 1px solid #a7f3d0;
  border-radius: 16px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  animation: slideUp 0.4s ease backwards;
}

.win-icon {
  font-size: 24px;
}

.win-text {
  font-size: 14px;
  color: #065f46;
  font-weight: 600;
  line-height: 1.5;
}

.career-alert {
  margin-bottom: 24px;
  border-radius: 12px;
}

/* ==================== 实习轮播 ==================== */
.internship-carousel-section {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header-row h4 {
  margin: 0;
  font-size: 16px;
  color: #1f2937;
  font-weight: 700;
}

.intern-card {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  height: 100%;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.intern-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  border-color: #6366f1;
}

.intern-company-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.company-logo {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  font-weight: 700;
}

.company-info {
  flex: 1;
}

.job-title {
  font-weight: 700;
  color: #1f2937;
  font-size: 16px;
  margin-bottom: 4px;
}

.company-name {
  color: #6b7280;
  font-size: 13px;
}

.job-meta-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.job-reason {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.match-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
}

/* ==================== 学习建议 ==================== */
.tips-carousel-wrapper {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  height: 100%;
}

.tip-card-large {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 16px;
  padding: 32px;
  height: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.tip-number {
  position: absolute;
  top: 20px;
  right: 24px;
  font-size: 72px;
  font-weight: 800;
  color: rgba(0, 0, 0, 0.05);
  line-height: 1;
}

.tip-content {
  font-size: 18px;
  color: #92400e;
  line-height: 1.8;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.tip-decoration {
  position: absolute;
  bottom: 20px;
  right: 24px;
  opacity: 0.3;
}

.stats-panel {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  height: 100%;
}

.stats-panel h4 {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #1f2937;
  font-weight: 700;
}

.pie-chart {
  height: 180px;
  width: 100%;
  margin-bottom: 20px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #4b5563;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.stat-line:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.stat-line .value {
  font-weight: 700;
  color: #1f2937;
}

/* ==================== 抽屉与弹窗 ==================== */
:deep(.action-drawer .el-drawer__body) {
  padding: 20px;
  background: #f9fafb;
}

.timeline-action-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.text-checked {
  text-decoration: line-through;
  color: #9ca3af;
}

.tasks-dialog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.milestone-summary {
  margin-bottom: 20px;
}

.tasks-collapse {
  border: none;
}

.task-collapse-item {
  margin-bottom: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.task-collapse-item :deep(.el-collapse-item__header) {
  padding: 16px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  border-bottom: 1px solid #f3f4f6;
}

.collapse-title-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 20px;
}

.task-title-text {
  flex: 1;
  margin-right: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-badges {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.task-detail-content {
  padding: 20px;
  background: #f9fafb;
}

.resources-section {
  margin-top: 20px;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.resource-item:hover {
  border-color: #6366f1;
  background: #f5f3ff;
}

.resource-icon {
  font-size: 24px;
}

.resource-info {
  flex: 1;
  min-width: 0;
}

.resource-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-meta {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

/* 资源抽屉 */
:deep(.resource-drawer .el-drawer__body) {
  padding: 0;
}

.resource-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.resource-type-header {
  padding: 32px;
  text-align: center;
  color: white;
}

.resource-type-header.video { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
.resource-type-header.book { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.resource-type-header.project { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }

.type-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.type-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  opacity: 0.9;
}

.resource-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.resource-content h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  color: #1f2937;
  line-height: 1.4;
}

.resource-reason {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: #eff6ff;
  border-radius: 8px;
  color: #1e40af;
  font-size: 13px;
  margin-bottom: 20px;
  line-height: 1.5;
}

.resource-meta-list {
  margin-bottom: 24px;
}

.resource-desc-text {
  color: #4b5563;
  line-height: 1.8;
  white-space: pre-wrap;
}

.visit-btn {
  width: 100%;
  margin-top: auto;
}

/* 实习详情弹窗 */
.intern-detail-content {
  padding: 0 4px;
}

.intern-header-detail {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.big-logo {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  font-weight: 700;
  flex-shrink: 0;
}

.header-info h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
  color: #1f2937;
}

.company-full {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 8px;
}

.location-salary {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4b5563;
  font-size: 14px;
}

.intern-meta-table {
  margin-bottom: 24px;
}

.intern-section {
  margin-bottom: 20px;
}

.intern-section h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #1f2937;
  font-weight: 700;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.desc-text {
  color: #4b5563;
  line-height: 1.8;
  margin: 0;
}

.apply-btn {
  width: 100%;
  margin-top: 8px;
}

/* 实习列表弹窗 */
.interns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  max-height: 60vh;
  overflow-y: auto;
  padding: 4px;
}

.intern-grid-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.intern-grid-card:hover {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.company-tag {
  font-weight: 700;
  color: #1f2937;
  font-size: 14px;
}

.match-tag {
  background: #6366f1;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.job-title-text {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
  font-size: 15px;
}

.job-brief-meta {
  font-size: 13px;
  color: #6b7280;
}

/* 差距分析弹窗 */
.gap-analysis {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 24px;
  max-height: 60vh;
}

.gap-chart {
  height: 300px;
}

.gap-list {
  overflow-y: auto;
  padding-right: 8px;
}

.gap-detail-item {
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  margin-bottom: 12px;
  border-left: 4px solid #e5e7eb;
}

.gap-detail-item.priority-1 {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.gap-detail-item.priority-2 {
  background: #fff7ed;
  border-left-color: #f97316;
}

.gap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.gap-title {
  font-weight: 700;
  color: #1f2937;
  font-size: 15px;
}

.gap-desc {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  
  .header-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .gap-analysis {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .header-content {
    padding: 24px;
  }
  
  .position-title {
    font-size: 24px;
  }
  
  .header-stats {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .progress-section {
    flex-direction: column;
    text-align: center;
  }
  
  .tasks-preview {
    grid-template-columns: 1fr;
  }
  
  .interns-grid {
    grid-template-columns: 1fr;
  }
}

/* ==================== 过渡动画 ==================== */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>