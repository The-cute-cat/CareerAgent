<template>
  <div class="career-report-page">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-brand">
        <span class="nav-logo">📊</span>
        <span class="nav-title">Career Planning</span>
      </div>
      <div class="nav-actions">
        <el-button type="primary" :icon="Edit" @click="openEditor(selectedSection)">编辑报告</el-button>
        <el-button :icon="Check" @click="runCompletenessCheck">完整性检查</el-button>
        <el-button :icon="MagicStick" @click="polishAllSections">AI 润色</el-button>
        <el-button :icon="DocumentChecked" @click="handleSave">保存</el-button>
      </div>
    </nav>

    <!-- Hero 区域 -->
    <section class="hero-panel">
      <div class="hero-content">
        <div class="hero-badge">
          <el-icon><Trophy /></el-icon>
          <span>AI 生成报告</span>
        </div>
        <h1>{{ report.target_position || '职业发展报告' }}</h1>
        <p class="hero-desc">
          结构化展示职业目标、能力差距、短中期路径规划与行动建议，支持智能润色和一键导出
        </p>
        <div class="hero-meta">
          <span class="meta-item">
            <el-icon><Calendar /></el-icon>
            {{ new Date().toLocaleDateString('zh-CN') }}
          </span>
          <span class="meta-item">
            <el-icon><Timer /></el-icon>
            完整度 {{ completenessScore }}%
          </span>
        </div>
      </div>

      <div class="hero-export">
        <div class="export-title">导出报告</div>
        <div class="export-actions">
          <el-button type="success" :icon="Document" @click="exportPdf">PDF</el-button>
          <el-button type="warning" :icon="DocumentCopy" @click="exportWord">Word</el-button>
        </div>
      </div>
    </section>

    <!-- 数据概览卡片 -->
    <section class="stats-grid">
      <article class="stat-card stat-card--primary">
        <div class="stat-icon"><el-icon><Flag /></el-icon></div>
        <div class="stat-info">
          <span class="stat-label">短期里程碑</span>
          <strong class="stat-value">{{ report.short_term_plan.milestones.length }}</strong>
        </div>
      </article>
      <article class="stat-card stat-card--success">
        <div class="stat-icon"><el-icon><Aim /></el-icon></div>
        <div class="stat-info">
          <span class="stat-label">中期里程碑</span>
          <strong class="stat-value">{{ report.mid_term_plan.milestones.length }}</strong>
        </div>
      </article>
      <article class="stat-card stat-card--warning">
        <div class="stat-icon"><el-icon><OfficeBuilding /></el-icon></div>
        <div class="stat-info">
          <span class="stat-label">推荐实习</span>
          <strong class="stat-value">{{ report.mid_term_plan.recommended_internships.length }}</strong>
        </div>
      </article>
      <article class="stat-card stat-card--info">
        <div class="stat-icon">
          <el-progress type="circle" :percentage="progressPercent" :width="48" :stroke-width="4" color="#fff" />
        </div>
        <div class="stat-info">
          <span class="stat-label">行动完成度</span>
          <strong class="stat-value">{{ progressPercent }}%</strong>
        </div>
      </article>
    </section>

    <div class="report-layout">
      <main class="report-main">
        <div ref="reportRef" class="report-canvas">
          <section class="report-section section-grid">
            <article class="content-card content-card--wide">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Profile</p>
                  <h2>学生画像摘要</h2>
                </div>
                <el-button text type="primary" @click="openEditor('student_summary')">编辑</el-button>
              </div>
              <div class="rich-preview" v-html="richContent.student_summary" />
            </article>

            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Gap</p>
                  <h2>能力差距分析</h2>
                </div>
                <div class="inline-actions">
                  <el-button text @click="polishOneSection('current_gap')">润色</el-button>
                  <el-button text type="primary" @click="openEditor('current_gap')">编辑</el-button>
                </div>
              </div>
              <div class="rich-preview" v-html="richContent.current_gap" />
            </article>
          </section>

          <section class="report-section">
            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Short Term</p>
                  <h2>短期行动计划</h2>
                  <span class="card-subtitle">{{ report.short_term_plan.duration }}</span>
                </div>
                <div class="inline-actions">
                  <el-button text @click="polishOneSection('short_goal')">润色目标</el-button>
                  <el-button text type="primary" @click="openEditor('short_goal')">编辑目标</el-button>
                </div>
              </div>

              <div class="goal-box">
                <span class="goal-label">阶段目标</span>
                <div class="rich-preview" v-html="richContent.short_goal" />
              </div>

              <div class="chip-block">
                <span class="block-title">重点领域</span>
                <div v-if="report.short_term_plan.focus_areas.length" class="chip-list">
                  <el-tag v-for="item in report.short_term_plan.focus_areas" :key="item" round>
                    {{ item }}
                  </el-tag>
                </div>
                <el-empty v-else description="暂无重点领域" :image-size="60" />
              </div>

              <div class="milestone-block">
                <span class="block-title">短期里程碑</span>
                <div v-if="!report.short_term_plan.milestones.length" class="empty-state">
                  <el-empty description="暂无里程碑数据" :image-size="80">
                    <el-button type="primary" text @click="openEditor('short_goal')">添加目标</el-button>
                  </el-empty>
                </div>
                <div v-else class="milestone-stack">
                  <article
                    v-for="milestone in report.short_term_plan.milestones"
                    :key="milestone.milestone_name"
                    class="milestone-card"
                  >
                    <div class="milestone-head">
                      <div>
                        <h3>{{ milestone.milestone_name }}</h3>
                        <span>{{ milestone.target_date }}</span>
                      </div>
                    </div>

                    <div class="milestone-body">
                      <div class="result-box">
                        <span class="mini-title">关键成果</span>
                        <ul class="plain-list">
                          <li v-for="result in milestone.key_results" :key="result">{{ result }}</li>
                        </ul>
                      </div>

                      <div class="task-grid">
                        <article v-for="task in milestone.tasks" :key="task.task_name" class="task-card">
                          <div class="task-top">
                            <strong>{{ task.task_name }}</strong>
                            <el-tag :type="priorityType(task.priority)" size="small" round>
                              {{ task.priority }}优先级
                            </el-tag>
                          </div>

                          <div class="task-meta">
                            <span>预计时间：{{ task.estimated_time }}</span>
                            <span>目标能力：{{ task.skill_target }}</span>
                          </div>

                          <p class="task-desc">{{ task.description }}</p>

                          <div class="task-bottom">
                            <div>
                              <span class="mini-title">成功标准</span>
                              <p>{{ task.success_criteria }}</p>
                            </div>
                            <el-button
                              v-if="getTaskResources(task).length"
                              size="small"
                              @click="openResourceList(getTaskResources(task))"
                            >
                              查看资源（{{ getTaskResources(task).length }}）
                            </el-button>
                            <el-tag v-else size="small" type="info" round>暂无资源</el-tag>
                          </div>
                        </article>
                      </div>
                    </div>
                  </article>
                </div>
              </div>

              <div class="timeline-block">
                <span class="block-title">快速见效行动</span>
                <el-timeline v-if="report.short_term_plan.quick_wins.length">
                  <el-timeline-item
                    v-for="(item, index) in report.short_term_plan.quick_wins"
                    :key="item"
                    :type="index === 0 ? 'primary' : 'info'"
                    hollow
                  >
                    <span class="timeline-item-text">{{ item }}</span>
                  </el-timeline-item>
                </el-timeline>
                <div v-else class="empty-state">
                  <el-empty description="暂无快速行动" :image-size="60" />
                </div>
              </div>
            </article>
          </section>

          <section class="report-section">
            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Mid Term</p>
                  <h2>中期路径规划</h2>
                  <span class="card-subtitle">{{ report.mid_term_plan.duration }}</span>
                </div>
                <div class="inline-actions">
                  <el-button text @click="polishOneSection('mid_goal')">润色目标</el-button>
                  <el-button text type="primary" @click="openEditor('mid_goal')">编辑目标</el-button>
                </div>
              </div>

              <div class="goal-box">
                <span class="goal-label">阶段目标</span>
                <div class="rich-preview" v-html="richContent.mid_goal" />
              </div>

              <div class="roadmap-block">
                <span class="block-title">技能路线图</span>
                <div v-if="!report.mid_term_plan.skill_roadmap.length" class="empty-state">
                  <el-empty description="暂无技能路线" :image-size="60" />
                </div>
                <div v-else class="roadmap-list">
                  <div
                    v-for="(item, index) in report.mid_term_plan.skill_roadmap"
                    :key="item"
                    class="roadmap-item"
                  >
                    <span class="roadmap-index">{{ index + 1 }}</span>
                    <span class="roadmap-text">{{ item }}</span>
                  </div>
                </div>
              </div>

              <div class="milestone-block">
                <span class="block-title">中期里程碑</span>
                <div v-if="!report.mid_term_plan.milestones.length" class="empty-state">
                  <el-empty description="暂无中期里程碑" :image-size="80">
                    <el-button type="primary" text @click="openEditor('mid_goal')">添加中期目标</el-button>
                  </el-empty>
                </div>
                <div v-else class="milestone-stack">
                  <article
                    v-for="milestone in report.mid_term_plan.milestones"
                    :key="milestone.milestone_name"
                    class="milestone-card"
                  >
                    <div class="milestone-head">
                      <div>
                        <h3>{{ milestone.milestone_name }}</h3>
                        <span>{{ milestone.target_date }}</span>
                      </div>
                    </div>

                    <div class="milestone-body">
                      <div class="result-box">
                        <span class="mini-title">关键成果</span>
                        <ul class="plain-list">
                          <li v-for="result in milestone.key_results" :key="result">{{ result }}</li>
                        </ul>
                      </div>

                      <div v-if="milestone.tasks.length" class="task-grid">
                        <article v-for="task in milestone.tasks" :key="task.task_name" class="task-card">
                          <div class="task-top">
                            <strong>{{ task.task_name }}</strong>
                            <el-tag :type="priorityType(task.priority)" size="small" round>
                              {{ task.priority }}优先级
                            </el-tag>
                          </div>
                          <div class="task-meta">
                            <span>预计时间：{{ task.estimated_time }}</span>
                            <span>目标能力：{{ task.skill_target }}</span>
                          </div>
                          <p class="task-desc">{{ task.description }}</p>
                          <div class="task-bottom">
                            <div>
                              <span class="mini-title">成功标准</span>
                              <p>{{ task.success_criteria }}</p>
                            </div>
                            <el-button
                              v-if="getTaskResources(task).length"
                              size="small"
                              @click="openResourceList(getTaskResources(task))"
                            >
                              查看资源（{{ getTaskResources(task).length }}）
                            </el-button>
                            <el-tag v-else size="small" type="info" round>暂无资源</el-tag>
                          </div>
                        </article>
                      </div>
                    </div>
                  </article>
                </div>
              </div>

              <div class="goal-box">
                <div class="goal-head">
                  <span class="goal-label">职业发展预期</span>
                  <div class="inline-actions">
                    <el-button text @click="polishOneSection('career_progression')">润色</el-button>
                    <el-button text type="primary" @click="openEditor('career_progression')">编辑</el-button>
                  </div>
                </div>
                <div class="rich-preview" v-html="richContent.career_progression" />
              </div>

              <div class="internship-block">
                <span class="block-title">推荐实习岗位</span>
                <div v-if="!report.mid_term_plan.recommended_internships.length" class="empty-state">
                  <el-empty description="暂无推荐实习" :image-size="80">
                    <template #description>
                      <span>暂无推荐实习岗位</span>
                    </template>
                  </el-empty>
                </div>
                <div v-else class="internship-grid">
                  <article
                    v-for="job in report.mid_term_plan.recommended_internships"
                    :key="job.id"
                    class="internship-card"
                  >
                    <div class="internship-top">
                      <div>
                        <h3>{{ job.job_title }}</h3>
                        <p>{{ job.company_name }}</p>
                      </div>
                      <el-tag round>{{ job.city || '待定' }}</el-tag>
                    </div>

                    <div class="internship-meta">
                      <span>{{ job.salary || '薪资面议' }}</span>
                      <span>{{ job.degree || '学历不限' }}</span>
                      <span>{{ job.job_type || '实习' }}</span>
                    </div>

                    <div class="chip-list">
                      <el-tag v-if="job.tech_stack" size="small" round>{{ job.tech_stack }}</el-tag>
                      <el-tag size="small" type="success" round>{{ job.days_per_week }}天/周</el-tag>
                      <el-tag size="small" type="warning" round>{{ job.months }}个月</el-tag>
                    </div>

                    <p class="internship-reason">{{ job.reason }}</p>

                    <div class="internship-actions">
                      <el-button
                        v-if="job.url"
                        size="small"
                        type="primary"
                        plain
                        @click="openLink(job.url)"
                      >
                        查看岗位
                      </el-button>
                      <el-button size="small" @click="openInternshipDetail(job)">查看详情</el-button>
                    </div>
                  </article>
                </div>
              </div>
            </article>
          </section>

          <section class="report-section section-grid">
            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Actions</p>
                  <h2>立即行动清单</h2>
                </div>
                <span class="light-text">{{ checkedActions.length }}/{{ report.action_checklist.length }} 已完成</span>
              </div>

              <el-progress :percentage="progressPercent" :stroke-width="10" class="progress-bar" />

              <div class="checklist-area">
                <el-empty v-if="!report.action_checklist.length" description="暂无行动清单" :image-size="60" />
                <el-checkbox-group v-else v-model="checkedActions">
                  <div v-for="item in report.action_checklist" :key="item" class="check-item">
                    <el-checkbox :label="item">
                      <span class="check-item-text">{{ item }}</span>
                    </el-checkbox>
                  </div>
                </el-checkbox-group>
              </div>
            </article>

            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Tips</p>
                  <h2>学习建议</h2>
                </div>
                <span class="light-text">{{ report.tips.length }} 条</span>
              </div>

              <div class="tips-area">
                <el-empty v-if="!report.tips.length" description="暂无学习建议" :image-size="60" />
                <div v-for="tip in report.tips" :key="tip" class="tip-card">
                  <span class="tip-dot"></span>
                  <span class="tip-text">{{ tip }}</span>
                </div>
              </div>
            </article>
          </section>
        </div>
      </main>

      <aside class="assistant-panel">
        <section class="assistant-card">
          <div class="assistant-title-row">
            <div>
              <p class="card-kicker">Assistant</p>
              <h2>智能润色助手</h2>
              <p class="assistant-subtitle">检查报告完整性，并对关键文本做措辞优化。</p>
            </div>
            <el-tag type="success" round>可接入 AI 接口</el-tag>
          </div>

          <div class="assistant-score">
            <span>报告完整度</span>
            <el-progress type="dashboard" :percentage="completenessScore" />
          </div>

          <div class="tool-block">
            <span class="tool-title">编辑区块</span>
            <el-select v-model="selectedSection">
              <el-option
                v-for="item in editableSections"
                :key="item.key"
                :label="item.label"
                :value="item.key"
              />
            </el-select>
            <div class="tool-actions">
              <el-button @click="openEditor(selectedSection)">打开编辑器</el-button>
              <el-button type="primary" plain @click="polishOneSection(selectedSection)">润色当前区块</el-button>
            </div>
          </div>

          <div class="tool-block">
            <span class="tool-title">内容优化</span>
            <div class="tool-actions">
              <el-button @click="runCompletenessCheck">检查完整性</el-button>
              <el-button type="primary" @click="polishAllSections">润色整份报告</el-button>
            </div>
          </div>

          <div class="tool-block">
            <span class="tool-title">助手建议</span>
            <el-empty v-if="!assistantNotes.length" description="点击上方按钮开始分析" />
            <el-timeline v-else>
              <el-timeline-item
                v-for="(note, index) in assistantNotes"
                :key="`${note.message}-${index}`"
                :type="note.type"
                :timestamp="note.time"
                hollow
              >
                {{ note.message }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </section>
      </aside>
    </div>

    <el-dialog
      v-model="editorVisible"
      :title="`编辑：${sectionLabel(activeSection)}`"
      width="960px"
      top="4vh"
      destroy-on-close
    >
      <div class="editor-dialog">
        <div class="editor-dialog-head">
          <div>
            <p class="card-kicker">Editor</p>
            <h3>{{ sectionLabel(activeSection) }}</h3>
          </div>
          <div class="inline-actions">
            <el-button @click="polishEditorContent">先润色后保存</el-button>
            <el-button type="primary" @click="saveEditorContent">保存修改</el-button>
          </div>
        </div>

        <WangEditor
          v-model="editorContent"
          height="420px"
          placeholder="在这里调整 AI 生成的内容"
        />
      </div>
    </el-dialog>

    <el-drawer v-model="resourceDrawerVisible" title="推荐资源" size="520px">
      <div v-if="currentResources.length" class="resource-list">
        <article v-for="item in currentResources" :key="item.id" class="resource-card">
          <div class="resource-card-top">
            <div>
              <h3 class="resource-title">{{ resourceTitle(item) }}</h3>
              <p class="resource-sub">{{ resourceType(item) }}</p>
            </div>
            <el-tag round>{{ item.reason ? '推荐' : '资源' }}</el-tag>
          </div>

          <p class="resource-text">{{ item.reason || item.description || item.content || '暂无说明' }}</p>

          <el-button v-if="item.url" size="small" type="primary" plain @click="openLink(item.url)">
            打开链接
          </el-button>
        </article>
      </div>
      <el-empty v-else description="暂无资源" />
    </el-drawer>

    <el-drawer v-model="internshipDrawerVisible" title="实习岗位详情" size="560px">
      <div v-if="currentInternship" class="internship-detail">
        <h3>{{ currentInternship.job_title }}</h3>
        <div class="detail-meta">
          <el-tag round>{{ currentInternship.company_name }}</el-tag>
          <el-tag round type="success">{{ currentInternship.city || '待定城市' }}</el-tag>
          <el-tag round type="warning">{{ currentInternship.salary || '薪资面议' }}</el-tag>
        </div>
        <p class="detail-block">{{ currentInternship.reason || '暂无推荐理由' }}</p>
        <p class="detail-block">{{ currentInternship.content || '暂无岗位描述' }}</p>
        <el-button v-if="currentInternship.url" type="primary" @click="openLink(currentInternship.url)">
          前往岗位链接
        </el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Edit,
  Check,
  MagicStick,
  DocumentChecked,
  Document,
  DocumentCopy,
  Trophy,
  Calendar,
  Timer,
  Flag,
  Aim,
  OfficeBuilding,
} from '@element-plus/icons-vue'
import WangEditor from '@/components/Person_Report/WangEditor.vue'
import {
  exportGrowthPlanToWord,
  exportResumePreviewToPdf,
  type GrowthPlanWordExportData,
} from '@/utils/resume-export'

type ResourceItem = {
  id: string
  title?: string
  name?: string
  author?: string
  publisher?: string
  isbn?: string
  url?: string
  duration?: string
  content?: string
  description?: string
  stars?: number
  language?: string
  reason?: string
}

type PlanTask = {
  task_name: string
  description: string
  priority: '高' | '中' | '低' | string
  estimated_time: string
  skill_target: string
  success_criteria: string
  resources: ResourceItem[]
}

// Milestone type is used implicitly through GrowthPlanData
interface Milestone {
  milestone_name: string
  target_date: string
  key_results: string[]
  tasks: PlanTask[]
}

type InternshipItem = {
  id: string
  job_title: string
  company_name: string
  salary?: string
  city?: string
  degree?: string
  days_per_week: number
  months: number
  job_type?: string
  tech_stack?: string
  url?: string
  content?: string
  reason?: string
}

type GrowthPlanData = GrowthPlanWordExportData & {
  mid_term_plan: GrowthPlanWordExportData['mid_term_plan'] & {
    recommended_internships: InternshipItem[]
  }
}

type EditableSectionKey =
  | 'student_summary'
  | 'current_gap'
  | 'short_goal'
  | 'mid_goal'
  | 'career_progression'

type AssistantNote = {
  message: string
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  time: string
}

const props = withDefaults(
  defineProps<{
    data?: GrowthPlanData
  }>(),
  {
    data: undefined,
  },
)

const emit = defineEmits<{
  (e: 'save', data: GrowthPlanData): void
  (e: 'polish-request', payload: { section: EditableSectionKey; content: string }): void
}>()

const emptyReport = (): GrowthPlanData => ({
  student_summary: '',
  target_position: '待生成职业方向',
  current_gap: '',
  short_term_plan: {
    duration: '1-3个月',
    goal: '',
    focus_areas: [],
    milestones: [],
    quick_wins: [],
  },
  mid_term_plan: {
    duration: '3-12个月',
    goal: '',
    skill_roadmap: [],
    milestones: [],
    career_progression: '',
    recommended_internships: [],
  },
  action_checklist: [],
  tips: [],
})

/**
 * 生成模拟数据用于开发和演示
 * 包含完整的职业发展报告数据结构
 */
const generateMockData = (): GrowthPlanData => ({  
  student_summary: '计算机科学专业大三学生，具备扎实的编程基础，熟悉Java和Python语言。在校期间参与了多个项目开发，包括电商网站后端和数据分析工具。对软件架构设计有浓厚兴趣，希望成为一名优秀的后端工程师。',
  target_position: 'Java后端开发工程师',
  current_gap: '1. 缺乏大规模分布式系统实战经验\n2. 微服务架构理解较浅\n3. 性能调优经验不足\n4. 缺少云原生技术栈（Docker/K8s）实践',
  short_term_plan: {
    duration: '1-3个月',
    goal: '夯实Java基础，掌握Spring Boot核心原理，完成一个完整的微服务练手项目',
    focus_areas: ['Java基础强化', 'Spring Boot深入', 'MySQL优化', 'Redis缓存'],
    milestones: [
      {
        milestone_name: 'Java核心技术巩固',
        target_date: '第1个月底',
        key_results: ['完成《Effective Java》阅读', '整理Java并发编程笔记', '完成5道LeetCode困难题'],
        tasks: [
          {
            task_name: '阅读Effective Java',
            description: '系统学习Java最佳实践，重点关注泛型、枚举、注解等特性',
            priority: '高',
            estimated_time: '2周',
            skill_target: 'Java高级特性掌握',
            success_criteria: '整理出30+条实践准则',
            resources: [
              { id: '1', title: 'Effective Java 第3版', author: 'Joshua Bloch', description: 'Java编程经典书籍' },
              { id: '2', title: 'Java核心技术36讲', author: '杨晓峰', description: '极客时间专栏', duration: '20小时' },
            ],
          } as PlanTask,
          {
            task_name: '并发编程实战',
            description: '学习Java并发包，理解线程池、锁机制、原子类',
            priority: '高',
            estimated_time: '1周',
            skill_target: '并发编程能力',
            success_criteria: '实现一个线程池监控工具',
            resources: [
              { id: '3', title: 'Java并发编程实战', author: 'Brian Goetz', description: '并发编程权威指南' },
            ],
          } as PlanTask,
        ],
      },
      {
        milestone_name: 'Spring Boot项目实战',
        target_date: '第2-3个月',
        key_results: ['完成用户中心微服务', '集成Redis缓存', '实现JWT认证', '部署到云服务器'],
        tasks: [
          {
            task_name: '用户中心服务开发',
            description: '开发完整的用户管理微服务，包含注册、登录、权限管理',
            priority: '高',
            estimated_time: '2周',
            skill_target: 'Spring Boot熟练开发',
            success_criteria: 'API测试通过率100%',
            resources: [
              { id: '4', title: 'Spring Boot实战', author: 'Craig Walls', description: 'Spring Boot入门经典' },
              { id: '5', title: 'Spring Security实战', description: '安全框架详解', url: 'https://spring.io/guides' },
            ],
          } as PlanTask,
          {
            task_name: '缓存与性能优化',
            description: '集成Redis缓存，优化数据库查询性能',
            priority: '中',
            estimated_time: '1周',
            skill_target: 'Redis应用能力',
            success_criteria: '接口响应时间<200ms',
            resources: [
              { id: '6', title: 'Redis设计与实现', author: '黄健宏', description: 'Redis源码解析' },
            ],
          } as PlanTask,
        ],
      },
    ],
    quick_wins: [
      '本周内搭建好Spring Boot开发环境',
      '每天刷2道LeetCode算法题',
      '关注3个技术博客获取最新资讯',
      '加入Java技术交流群',
    ],
  },
  mid_term_plan: {
    duration: '3-12个月',
    goal: '深入微服务架构，掌握云原生技术栈，具备独立设计中型系统的能力',
    skill_roadmap: [
      'Spring Cloud Alibaba全家桶（Nacos、Gateway、Sentinel）',
      'Docker容器化与Kubernetes编排',
      'MySQL分库分表与TiDB分布式数据库',
      'RocketMQ消息队列与分布式事务',
      'Prometheus监控与ELK日志分析',
    ],
    milestones: [
      {
        milestone_name: '微服务架构转型',
        target_date: '第6个月',
        key_results: ['完成单体应用拆分', '实现服务注册发现', '配置中心集中管理', 'API网关统一入口'],
        tasks: [
          {
            task_name: 'Spring Cloud微服务改造',
            description: '将用户中心拆分为多个微服务，实现服务治理',
            priority: '高',
            estimated_time: '1个月',
            skill_target: '微服务架构设计',
            success_criteria: '服务调用成功率>99.9%',
            resources: [
              { id: '7', title: 'Spring Cloud微服务实战', description: '微服务架构指南' },
              { id: '8', title: 'Nacos官方文档', url: 'https://nacos.io', description: '服务注册与配置中心' },
            ],
          } as PlanTask,
        ],
      },
      {
        milestone_name: '云原生技术掌握',
        target_date: '第9个月',
        key_results: ['应用容器化部署', 'K8s编排文件编写', 'CI/CD流水线搭建', '自动化运维脚本'],
        tasks: [
          {
            task_name: 'Docker与K8s实战',
            description: '学习容器化技术，在K8s集群部署微服务',
            priority: '高',
            estimated_time: '6周',
            skill_target: '云原生技术栈',
            success_criteria: '实现滚动更新零停机',
            resources: [
              { id: '9', title: 'Docker从入门到实践', description: '容器化技术指南' },
              { id: '10', title: 'Kubernetes权威指南', description: 'K8s学习圣经' },
            ],
          } as PlanTask,
        ],
      },
    ],
    career_progression: '通过系统学习，预计6个月内可达到初级Java工程师水平，能够独立完成模块开发；12个月内达到中级水平，具备系统设计和团队协作能力。建议优先投递互联网中厂实习岗位积累项目经验。',
    recommended_internships: [
      {
        id: 'job-1',
        job_title: 'Java后端开发实习生',
        company_name: '字节跳动',
        salary: '400-500元/天',
        city: '北京',
        degree: '本科及以上',
        days_per_week: 4,
        months: 6,
        job_type: '实习',
        tech_stack: 'Java/Go',
        url: 'https://jobs.bytedance.com',
        reason: '字节跳动技术栈先进，实习经历含金量高，与当前学习方向高度匹配',
        content: '参与抖音电商后端服务开发，接触高并发场景',
      },
      {
        id: 'job-2',
        job_title: '后端开发工程师（实习）',
        company_name: '美团',
        salary: '350-450元/天',
        city: '北京',
        degree: '本科及以上',
        days_per_week: 5,
        months: 3,
        job_type: '实习',
        tech_stack: 'Java',
        url: 'https://zhaopin.meituan.com',
        reason: '美团Java技术栈成熟，有完善的培养体系，适合实习生成长',
        content: '参与外卖业务后端开发，学习分布式系统架构',
      },
      {
        id: 'job-3',
        job_title: 'Java实习生',
        company_name: '阿里巴巴',
        salary: '300-400元/天',
        city: '杭州',
        degree: '本科及以上',
        days_per_week: 4,
        months: 6,
        job_type: '实习',
        tech_stack: 'Java',
        url: 'https://talent.alibaba.com',
        reason: '阿里是国内Java技术标杆，Spring Cloud Alibaba发源地',
        content: '参与淘宝/天猫业务后端开发',
      },
    ],
  },
  action_checklist: [
    '搭建Java开发环境（JDK+IDEA+Maven）',
    '创建个人GitHub仓库并提交第一个项目',
    '制定每周学习计划并坚持执行',
    '整理技术博客记录学习心得',
    '加入至少2个技术社群',
    '投递5份实习简历',
    '准备技术面试常见问题',
    '完成一个完整的练手项目',
  ],
  tips: [
    '坚持每天编码，保持手感，代码量是提升编程能力的基础',
    '多阅读优秀开源项目源码，学习大厂的代码规范和设计思想',
    '重视基础知识，JVM、并发、数据结构是面试重点',
    '培养解决问题的能力，遇到Bug先独立思考再求助',
    '关注行业动态，新技术层出不穷要保持学习热情',
    '建立个人技术品牌，写博客、做分享都是很好的方式',
  ],
})

/**
 * Deep clone using structured clone algorithm (faster, handles more types than JSON)
 * Falls back to JSON method for unsupported environments
 */
function deepClone<T>(data: T): T {
  if (typeof structuredClone === 'function') {
    return structuredClone(data)
  }
  // Fallback: JSON method (has limitations with Dates, undefined, functions, etc.)
  return JSON.parse(JSON.stringify(data))
}

/**
 * Escape HTML entities to prevent XSS attacks
 * Order matters: & must be replaced first to avoid double-escaping
 */
function escapeHtml(str: string): string {
  if (!str) return ''
  return str
    .replace(/&/g, '&amp;')      // Must be first
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function normalizeText(text: string) {
  return text
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function textToHtml(text: string) {
  const source = normalizeText(text)
  if (!source) return '<p>暂无内容</p>'

  return source
    .split('\n')
    .filter(Boolean)
    .map(line => `<p>${escapeHtml(line)}</p>`)
    .join('')
}

/**
 * Convert HTML to plain text safely without executing scripts
 * Uses regex-based stripping instead of innerHTML for XSS safety
 */
function htmlToText(html: string): string {
  if (!html) return ''
  // Remove script/style tags and their contents first (XSS prevention)
  let text = html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')     // Replace remaining tags with space
    .replace(/\s+/g, ' ')          // Collapse whitespace
    .trim()
  return normalizeText(text)
}

function smartPolishHtml(html: string) {
  const text = htmlToText(html)
  if (!text) return '<p>暂无内容</p>'

  const polished = normalizeText(
    text
      .replace(/;/g, '；')
      .replace(/:/g, '：')
      .replace(/\bSpringboot\b/gi, 'Spring Boot')
      .replace(/\bmysql\b/gi, 'MySQL'),
  )

  return textToHtml(polished)
}

const report = ref<GrowthPlanData>(emptyReport())

const richContent = reactive<Record<EditableSectionKey, string>>({
  student_summary: '<p>暂无内容</p>',
  current_gap: '<p>暂无内容</p>',
  short_goal: '<p>暂无内容</p>',
  mid_goal: '<p>暂无内容</p>',
  career_progression: '<p>暂无内容</p>',
})

// 必须在使用前声明，避免 temporal dead zone
const checkedActions = ref<string[]>([])
const checklistStorageKey = computed(
  () => `career-report-checklist:${report.value.target_position || 'default'}`,
)

function syncReport(data?: GrowthPlanData) {
  // 如果没有传入数据且不是生产环境，使用模拟数据
  const useMock = !data && (import.meta.env.DEV || import.meta.env.VITE_USE_MOCK === 'true')
  const value = deepClone(data || (useMock ? generateMockData() : emptyReport()))
  report.value = value
  richContent.student_summary = textToHtml(value.student_summary)
  richContent.current_gap = textToHtml(value.current_gap)
  richContent.short_goal = textToHtml(value.short_term_plan.goal)
  richContent.mid_goal = textToHtml(value.mid_term_plan.goal)
  richContent.career_progression = textToHtml(value.mid_term_plan.career_progression)
  restoreChecklist()
}

watch(
  () => props.data,
  val => {
    syncReport(val)
  },
  { immediate: true, deep: true },
)

const editableSections = [
  { key: 'student_summary' as EditableSectionKey, label: '学生画像摘要' },
  { key: 'current_gap' as EditableSectionKey, label: '能力差距分析' },
  { key: 'short_goal' as EditableSectionKey, label: '短期目标' },
  { key: 'mid_goal' as EditableSectionKey, label: '中期目标' },
  { key: 'career_progression' as EditableSectionKey, label: '职业发展预期' },
]

const selectedSection = ref<EditableSectionKey>('student_summary')
const activeSection = ref<EditableSectionKey>('student_summary')

function sectionLabel(key: EditableSectionKey) {
  return editableSections.find(item => item.key === key)?.label || key
}

function getSectionContent(key: EditableSectionKey) {
  return richContent[key]
}

function setSectionContent(key: EditableSectionKey, value: string) {
  richContent[key] = value
}

const editorVisible = ref(false)
const editorContent = ref('<p>暂无内容</p>')

function openEditor(key: EditableSectionKey) {
  activeSection.value = key
  selectedSection.value = key
  editorContent.value = getSectionContent(key)
  editorVisible.value = true
}

function saveEditorContent() {
  setSectionContent(activeSection.value, editorContent.value || '<p>暂无内容</p>')
  editorVisible.value = false
  handleSave(false)
  ElMessage.success('内容已保存')
}

function polishEditorContent() {
  editorContent.value = smartPolishHtml(editorContent.value || '')
  pushAssistantNote(`已润色「${sectionLabel(activeSection.value)}」编辑内容`, 'success')
  emit('polish-request', {
    section: activeSection.value,
    content: htmlToText(editorContent.value),
  })
}

function polishOneSection(key: EditableSectionKey) {
  const polished = smartPolishHtml(getSectionContent(key))
  setSectionContent(key, polished)
  pushAssistantNote(`已润色「${sectionLabel(key)}」`, 'success')
  emit('polish-request', {
    section: key,
    content: htmlToText(polished),
  })
}

function polishAllSections() {
  editableSections.forEach(item => {
    setSectionContent(item.key, smartPolishHtml(getSectionContent(item.key)))
  })
  pushAssistantNote('已对整份报告的核心文本进行统一润色', 'success')
  ElMessage.success('全文润色完成')
}

function buildSubmitData(): GrowthPlanData {
  const result = deepClone(report.value)
  result.student_summary = htmlToText(richContent.student_summary)
  result.current_gap = htmlToText(richContent.current_gap)
  result.short_term_plan.goal = htmlToText(richContent.short_goal)
  result.mid_term_plan.goal = htmlToText(richContent.mid_goal)
  result.mid_term_plan.career_progression = htmlToText(richContent.career_progression)
  return result
}

function handleSave(showMessage = true) {
  const payload = buildSubmitData()
  emit('save', payload)
  if (showMessage) {
    ElMessage.success('已触发保存事件')
  }
}

/**
 * Safely restore checklist from localStorage with SSR compatibility
 */
function restoreChecklist(): void {
  // Check for SSR environment
  if (typeof window === 'undefined' || !window.localStorage) {
    checkedActions.value = []
    return
  }
  try {
    const raw = localStorage.getItem(checklistStorageKey.value)
    if (raw) {
      const parsed = JSON.parse(raw)
      // Validate that parsed data is an array of strings
      if (Array.isArray(parsed) && parsed.every(item => typeof item === 'string')) {
        checkedActions.value = parsed
      } else {
        checkedActions.value = []
      }
    } else {
      checkedActions.value = []
    }
  } catch {
    checkedActions.value = []
  }
}

/**
 * Safely persist checklist to localStorage with quota handling
 */
function persistChecklist(val: string[]): void {
  if (typeof window === 'undefined' || !window.localStorage) return
  try {
    localStorage.setItem(checklistStorageKey.value, JSON.stringify(val))
  } catch (e) {
    // Handle quota exceeded error
    if (e instanceof DOMException && e.name === 'QuotaExceededError') {
      console.warn('localStorage quota exceeded')
      ElMessage.warning('存储空间不足，无法保存勾选状态')
    }
  }
}

watch(
  checkedActions,
  val => {
    persistChecklist(val)
  },
  { deep: true },
)

const progressPercent = computed(() => {
  const total = report.value.action_checklist.length
  if (!total) return 0
  return Math.round((checkedActions.value.length / total) * 100)
})

function priorityType(priority: string) {
  if (priority === '高') return 'danger'
  if (priority === '中') return 'warning'
  return 'info'
}

/**
 * Safely get task resources with proper type inference
 * Works around Vue template type inference limitations
 * Uses type assertion since Vue template cannot infer nested array types correctly
 */
function getTaskResources(task: unknown): ResourceItem[] {
  const t = task as PlanTask
  return t.resources || []
}

const resourceDrawerVisible = ref(false)
const currentResources = ref<ResourceItem[]>([])

function openResourceList(list: ResourceItem[]) {
  currentResources.value = list || []
  resourceDrawerVisible.value = true
}

function resourceTitle(item: ResourceItem) {
  return item.title || item.name || '未命名资源'
}

function resourceType(item: ResourceItem) {
  if (item.duration) return '视频资源'
  if (item.isbn) return '书籍资源'
  if (typeof item.stars === 'number') return '开源项目'
  return '学习资源'
}

const internshipDrawerVisible = ref(false)
const currentInternship = ref<InternshipItem | null>(null)

function openInternshipDetail(item: InternshipItem) {
  currentInternship.value = item
  internshipDrawerVisible.value = true
}

/**
 * Open URL in new tab with security validation
 * Prevents javascript: protocol XSS attacks
 */
function openLink(url?: string): void {
  if (!url) return
  // Validate URL protocol to prevent XSS via javascript: URLs
  try {
    const parsed = new URL(url, window.location.href)
    // Only allow safe protocols
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      console.warn('Blocked potentially unsafe URL protocol:', parsed.protocol)
      ElMessage.warning('不安全的链接格式')
      return
    }
    window.open(url, '_blank', 'noopener,noreferrer')
  } catch {
    // Invalid URL format
    ElMessage.error('链接格式无效')
  }
}

const assistantNotes = ref<AssistantNote[]>([])

function pushAssistantNote(message: string, type: AssistantNote['type'] = 'primary') {
  assistantNotes.value.unshift({
    message,
    type,
    time: new Date().toLocaleTimeString(),
  })
}

/**
 * Check if HTML content has meaningful text (cached per computation)
 */
function hasMeaningfulContent(html: string): boolean {
  // Quick check: if no text content between tags, skip full parsing
  const textContent = html.replace(/<[^>]*>/g, '').trim()
  if (!textContent) return false
  // Full check with normalization
  return !!htmlToText(html)
}

/**
 * Report completeness score (0-100)
 * Optimized to avoid redundant DOM operations
 */
const completenessScore = computed(() => {
  // Batch text extraction to minimize processing
  const checks = [
    hasMeaningfulContent(richContent.student_summary),
    hasMeaningfulContent(richContent.current_gap),
    hasMeaningfulContent(richContent.short_goal),
    hasMeaningfulContent(richContent.mid_goal),
    hasMeaningfulContent(richContent.career_progression),
    report.value.short_term_plan.focus_areas.length > 0,
    report.value.short_term_plan.milestones.length > 0,
    report.value.mid_term_plan.skill_roadmap.length > 0,
    report.value.mid_term_plan.milestones.length > 0,
    report.value.action_checklist.length > 0,
    report.value.tips.length > 0,
  ]
  const hit = checks.filter(Boolean).length
  return Math.round((hit / checks.length) * 100)
})

function runCompletenessCheck() {
  const warnings: string[] = []

  if (!htmlToText(richContent.student_summary)) warnings.push('缺少学生画像摘要')
  if (!htmlToText(richContent.current_gap)) warnings.push('缺少能力差距分析')
  if (!htmlToText(richContent.short_goal)) warnings.push('缺少短期目标描述')
  if (!htmlToText(richContent.mid_goal)) warnings.push('缺少中期目标描述')
  if (report.value.short_term_plan.focus_areas.length === 0) warnings.push('短期重点领域为空')
  if (report.value.short_term_plan.milestones.length === 0) warnings.push('短期里程碑为空')
  if (report.value.mid_term_plan.skill_roadmap.length === 0) warnings.push('中期技能路线图为空')
  if (report.value.mid_term_plan.milestones.length === 0) warnings.push('中期里程碑为空')
  if (report.value.action_checklist.length === 0) warnings.push('行动清单为空')
  if (report.value.tips.length === 0) warnings.push('学习建议为空')

  if (!warnings.length) {
    pushAssistantNote('完整性检查通过，当前报告核心结构完整', 'success')
    ElMessage.success('完整性检查通过')
    return
  }

  warnings.forEach(item => pushAssistantNote(item, 'warning'))
  ElMessage.warning(`发现 ${warnings.length} 处建议补充的内容`)
}

const reportRef = ref<HTMLElement | null>(null)

async function exportPdf() {
  if (!reportRef.value) return

  try {
    await exportResumePreviewToPdf(reportRef.value, {
      fileName: `${report.value.target_position || 'career-report'}.pdf`,
      margin: 8,
    })
    pushAssistantNote('PDF 导出成功', 'success')
  } catch (error) {
    console.error(error)
    ElMessage.error('PDF 导出失败')
    pushAssistantNote('PDF 导出失败，请检查页面内容是否已渲染完成', 'danger')
  }
}

async function exportWord() {
  try {
    await exportGrowthPlanToWord(buildSubmitData(), {
      fileName: `${report.value.target_position || 'career-report'}.docx`,
    })
    pushAssistantNote('Word 导出成功', 'success')
  } catch (error) {
    console.error(error)
    ElMessage.error('Word 导出失败')
  }
}
</script>

<style scoped>
/* ===== CSS Variables for Design System ===== */
.career-report-page {
  --primary-gradient: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%);
  --card-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
  --card-shadow-hover: 0 24px 48px rgba(15, 23, 42, 0.12);
  --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --border-glow: 0 0 0 3px rgba(59, 130, 246, 0.1);

  min-height: 100vh;
  padding: 0;
  background:
    radial-gradient(circle at top left, rgba(250, 204, 21, 0.18), transparent 24%),
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 26%),
    linear-gradient(180deg, #fffdf8 0%, #f8fbff 100%);
}

/* ===== Top Navigation ===== */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-logo {
  font-size: 24px;
}

.nav-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-actions {
  display: flex;
  gap: 12px;
}

.nav-actions :deep(.el-button) {
  border-radius: 10px;
  font-weight: 500;
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 40px;
  padding: 40px 48px;
  margin: 24px 32px 0;
  border-radius: 24px;
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12);
  position: relative;
  overflow: hidden;
}

.hero-panel::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  pointer-events: none;
}

.hero-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 20px;
}

.hero-content h1 {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.hero-desc {
  font-size: 15px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.85);
  max-width: 600px;
  margin-bottom: 20px;
}

.hero-meta {
  display: flex;
  gap: 24px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.hero-export {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 24px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.export-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.export-actions {
  display: flex;
  gap: 12px;
}

.export-actions :deep(.el-button) {
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
}

.hero-copy {
  max-width: 760px;
}

.eyebrow,
.card-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.hero-copy h1,
.card-head h2,
.assistant-title-row h2,
.editor-dialog-head h3,
.milestone-head h3,
.internship-top h3 {
  margin: 0;
}

.hero-desc {
  margin: 12px 0 0;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.82);
}

.hero-actions,
.inline-actions,
.tool-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-actions :deep(.el-button) {
  border-radius: 10px;
  font-weight: 500;
  transition: var(--transition-smooth);
}

.hero-actions :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.hero-actions :deep(.el-button--primary) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
}

.hero-actions :deep(.el-button--success) {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
}

.hero-actions :deep(.el-button--warning) {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  margin: 24px 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-radius: 20px;
  transition: var(--transition-smooth);
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
}

.stat-card--primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
}

.stat-card--success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
}

.stat-card--warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #fff;
}

.stat-card--info {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  color: #fff;
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  font-size: 24px;
}

.stat-card--info .stat-icon {
  background: transparent;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
  opacity: 0.9;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
}

/* 旧样式兼容 */
.summary-strip {
  display: none;
}

@keyframes countUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.summary-card,
.content-card,
.assistant-card,
.milestone-card,
.task-card,
.internship-card,
.resource-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
}

.summary-card span,
.card-subtitle,
.light-text,
.assistant-subtitle,
.resource-sub,
.internship-top p {
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
}

.report-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 24px;
  margin: 0 32px 32px;
  align-items: start;
}

.report-canvas {
  display: grid;
  gap: 20px;
}

.section-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
  gap: 16px;
}

.content-card {
  padding: 24px;
  transition: var(--transition-smooth);
  position: relative;
  overflow: hidden;
}

.content-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.content-card:hover::before {
  transform: scaleX(1);
}

.content-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}

.content-card--wide {
  min-height: 100%;
}

.card-head,
.assistant-title-row,
.milestone-head,
.task-top,
.internship-top,
.goal-head,
.editor-dialog-head,
.resource-card-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.card-head {
  margin-bottom: 20px;
}

.card-head h2 {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card-kicker {
  color: #3b82f6;
  font-weight: 600;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.rich-preview {
  line-height: 1.85;
  color: #1e293b;
}

.rich-preview :deep(p) {
  margin: 0 0 10px;
}

.goal-box,
.chip-block,
.milestone-block,
.timeline-block,
.roadmap-block,
.internship-block {
  margin-top: 20px;
}

.goal-box {
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.goal-label,
.block-title,
.tool-title,
.mini-title {
  display: block;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip-list :deep(.el-tag) {
  border-radius: 8px;
  font-weight: 500;
  padding: 4px 12px;
  transition: var(--transition-smooth);
}

.chip-list :deep(.el-tag:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
}

.milestone-stack,
.task-grid,
.internship-grid,
.tips-area,
.resource-list {
  display: grid;
  gap: 16px;
}

.milestone-card {
  padding: 22px;
  transition: var(--transition-smooth);
}

.milestone-card:hover {
  box-shadow: var(--card-shadow-hover);
}

.milestone-head span {
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
}

.milestone-head h3 {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
}

.milestone-body {
  display: grid;
  gap: 16px;
  margin-top: 16px;
}

.result-box {
  padding: 14px 16px;
  border-radius: 16px;
  background: #f8fafc;
}

.plain-list {
  margin: 0;
  padding-left: 18px;
  color: #475569;
  line-height: 1.8;
}

.task-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.task-card {
  padding: 20px;
  transition: var(--transition-smooth);
  border-left: 4px solid transparent;
}

.task-card:hover {
  border-left-color: #3b82f6;
  transform: translateX(4px);
  box-shadow: var(--card-shadow-hover);
}

.task-meta {
  display: grid;
  gap: 6px;
  margin-top: 10px;
  font-size: 13px;
  color: #64748b;
}

.task-desc,
.task-bottom p,
.internship-reason,
.resource-text,
.detail-block {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.75;
}

.task-bottom {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.roadmap-list {
  display: grid;
  gap: 12px;
}

.roadmap-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  transition: var(--transition-smooth);
}

.roadmap-item:hover {
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateX(8px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.roadmap-index,
.tip-dot {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.roadmap-item:hover .roadmap-index {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  transform: scale(1.1);
}

.roadmap-text {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
}

.internship-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.internship-card {
  padding: 22px;
  transition: var(--transition-smooth);
  position: relative;
}

.internship-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 0;
  background: linear-gradient(90deg, #10b981, #3b82f6);
  transition: height 0.3s ease;
}

.internship-card:hover::after {
  height: 3px;
}

.internship-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
}

.internship-meta,
.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
  color: #64748b;
  font-size: 13px;
}

.internship-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.progress-bar {
  margin-bottom: 16px;
}

.checklist-area {
  display: grid;
  gap: 10px;
}

.check-item {
  padding: 14px 18px;
  border-radius: 14px;
  background: #f8fafc;
  transition: var(--transition-smooth);
  border: 2px solid transparent;
}

.check-item:hover {
  background: #ffffff;
  border-color: rgba(59, 130, 246, 0.2);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);
}

.check-item :deep(.el-checkbox) {
  align-items: flex-start;
}

.check-item :deep(.el-checkbox__label) {
  white-space: normal;
  line-height: 1.6;
}

.tip-card {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 16px 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  transition: var(--transition-smooth);
}

.tip-card:hover {
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateX(6px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
}

.tip-dot {
  width: 10px;
  height: 10px;
  margin-top: 6px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 50%;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
}

.tip-text {
  color: #475569;
  line-height: 1.7;
  font-size: 14px;
}

.timeline-item-text {
  color: #475569;
  font-size: 14px;
  line-height: 1.6;
}

.assistant-card {
  padding: 24px;
  position: sticky;
  top: 96px;
  transition: var(--transition-smooth);
}

.assistant-card:hover {
  box-shadow: var(--card-shadow-hover);
}

.assistant-score {
  display: grid;
  justify-items: center;
  gap: 12px;
  margin: 24px 0;
  padding: 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.tool-block {
  padding: 18px;
  margin-top: 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  transition: var(--transition-smooth);
}

.tool-block:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #ffffff 100%);
  border-color: rgba(59, 130, 246, 0.15);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}

.tool-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  margin-bottom: 12px;
}

.tool-actions {
  margin-top: 12px;
}

.editor-dialog {
  display: grid;
  gap: 20px;
  animation: fadeInUp 0.4s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.editor-dialog-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.resource-card {
  padding: 20px;
  transition: var(--transition-smooth);
}

.resource-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--card-shadow-hover);
}

.resource-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.resource-text {
  margin-top: 12px;
  color: #64748b;
  line-height: 1.7;
  font-size: 14px;
}

.internship-detail {
  display: grid;
  gap: 16px;
}

/* ===== Empty States ===== */
.empty-state {
  padding: 40px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-radius: 18px;
  border: 2px dashed rgba(148, 163, 184, 0.3);
}

.empty-state:hover {
  border-color: rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
}

@media (max-width: 1280px) {
  .report-layout {
    grid-template-columns: 1fr;
    margin: 0 24px 24px;
  }

  .assistant-card {
    position: static;
  }

  .hero-panel {
    margin: 20px 24px 0;
    padding: 32px;
  }

  .stats-grid {
    margin: 20px 24px;
  }
}

@media (max-width: 960px) {
  .hero-panel,
  .section-grid {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hero-panel {
    flex-direction: column;
    margin: 16px 20px 0;
    padding: 28px;
  }

  .hero-content h1 {
    font-size: 28px;
  }

  .hero-export {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    margin: 16px 20px;
    gap: 16px;
  }

  .top-nav {
    padding: 12px 20px;
  }

  .nav-title {
    display: none;
  }

  .nav-actions {
    gap: 8px;
  }

  .nav-actions :deep(.el-button span) {
    display: none;
  }
}

@media (max-width: 640px) {
  .career-report-page {
    padding: 0;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    margin: 12px 16px;
  }

  .stat-card {
    padding: 16px 20px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
  }

  .stat-value {
    font-size: 24px;
  }

  .hero-panel {
    margin: 12px 16px 0;
    padding: 24px;
    border-radius: 20px;
  }

  .hero-content h1 {
    font-size: 24px;
  }

  .hero-badge {
    font-size: 12px;
    padding: 6px 12px;
  }

  .hero-desc {
    font-size: 14px;
  }

  .export-actions {
    flex-direction: column;
  }

  .report-layout {
    margin: 0 16px 16px;
  }

  .section-grid {
    grid-template-columns: 1fr;
  }

  .content-card,
  .summary-card,
  .milestone-card,
  .task-card,
  .internship-card {
    border-radius: 18px;
  }

  .roadmap-item:hover {
    transform: translateX(4px);
  }
}

/* ===== Scrollbar Styling ===== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(148, 163, 184, 0.1);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 116, 139, 0.5);
}

/* ===== Focus States for Accessibility ===== */
button:focus-visible,
.el-button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* ===== Selection Color ===== */
::selection {
  background: rgba(59, 130, 246, 0.2);
  color: #1e3a8a;
}
</style>
