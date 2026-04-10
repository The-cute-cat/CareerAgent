
<template>
  <div class="report-editor-page">
    <nav class="editor-topbar">
      <div class="editor-brand">
        <p class="editor-kicker">Career Report Editor</p>
        <h1>编辑生涯报告</h1>
        <p class="editor-subtitle">直接维护报告内容结构，保存后会同步到生涯报告页面</p>
        <div class="editor-status-strip">
          <span class="status-chip" :class="`status-chip--${saveState}`">
            {{ hasUnsavedChanges ? '存在未保存修改' : '内容已同步' }}
          </span>
          <span class="status-chip status-chip--focus">当前模块：{{ assistantFocusLabel }}</span>
          <span class="status-text">最近保存：{{ lastSavedAt }}</span>
        </div>
      </div>
      <div class="editor-actions">
        <el-button plain disabled>预览报告</el-button>
        <el-button :icon="ArrowLeft" @click="goBack">返回报告</el-button>
        <el-button type="primary" :icon="Check" @click="saveReport">保存并返回</el-button>
      </div>
    </nav>

    <div class="editor-layout">
      <aside class="editor-sidebar">
        <div class="sidebar-head">
          <p class="editor-kicker">Navigation</p>
          <h2>编辑目录</h2>
          <p class="sidebar-subtitle">按章节快速切换，蓝色表示当前聚焦模块。</p>
        </div>
        <div
          v-for="item in navItems"
          :key="item.key"
          class="nav-group"
          :class="{ 'is-expanded': expandedNavItems[item.key] }"
        >
          <button
            class="nav-button"
            type="button"
            :class="[`nav-button--${getNavState(item.key)}`, { 'has-children': !!item.children }]"
            @click="item.children ? toggleNavItem(item.key) : scrollToSection(item.key)"
          >
            <span class="nav-state-dot" />
            <span class="nav-button-text">{{ item.label }}</span>
            <span class="nav-state-text">{{ navStateLabel(item.key) }}</span>
            <el-icon v-if="item.children" class="nav-expand-icon">
              <ArrowDown v-if="expandedNavItems[item.key]" />
              <ArrowRight v-else />
            </el-icon>
          </button>
          <div v-if="item.children" v-show="expandedNavItems[item.key]" class="nav-children">
            <button
              v-for="child in item.children"
              :key="child.key"
              class="nav-button nav-button--sub"
              type="button"
              :class="`nav-button--${getNavState(child.key)}`"
              @click="scrollToSection(child.key)"
            >
              <span class="nav-state-dot" />
              {{ child.label }}
              <span class="nav-state-text">{{ navStateLabel(child.key) }}</span>
            </button>
          </div>
        </div>
      </aside>

      <main class="editor-content">
        <section class="editor-workbench">
          <div class="workbench-card workbench-card--accent">
            <span class="workbench-label">当前目标岗位</span>
            <strong>{{ form.target_position || '待完善目标岗位' }}</strong>
          </div>
          <div class="workbench-card workbench-card--focus">
            <span class="workbench-label">当前编辑模块</span>
            <strong>{{ assistantFocusLabel }}</strong>
            <span class="workbench-state" :class="`workbench-state--${currentFocusState}`">
              {{ currentFocusStateLabel }}
            </span>
          </div>
          <div class="workbench-card">
            <span class="workbench-label">编辑目标</span>
            <p>{{ currentModuleGoal }}</p>
          </div>
        </section>

        <section :id="sectionIdMap.basic" class="editor-section" :class="{ 'is-focus': activeFocusKey === 'basic' }">
          <div class="section-head">
            <div>
              <h2>基础信息</h2>
              <span class="section-hint">用于统一报告封面信息、周期和目标岗位。</span>
            </div>
            <div class="section-meta">
              <span class="section-count">3 项核心字段</span>
            </div>
          </div>
          <div class="panel-grid panel-grid--two">
            <el-input v-model="form.target_position" placeholder="目标岗位" />
            <el-input v-model="form.short_term_plan.duration" placeholder="短期周期" />
            <el-input v-model="form.mid_term_plan.duration" placeholder="中期周期" />
          </div>
        </section>

        <section :id="sectionIdMap.summary" class="editor-section editor-section--primary" :class="{ 'is-focus': activeFocusKey === 'student_summary' || activeFocusKey === 'current_gap' || activeFocusKey === 'short_goal' || activeFocusKey === 'mid_goal' || activeFocusKey === 'career_progression' }">
          <div class="section-head">
            <div>
              <h2>核心内容</h2>
              <span class="section-hint">报告正文的核心表达区，建议一次只聚焦一个模块深入修改。</span>
            </div>
            <div class="section-head-actions">
              <el-button text type="primary" size="small" @click="toggleAllEditors">
                {{ allEditorsExpanded ? '全部收起' : '全部展开' }}
              </el-button>
              <span class="section-count">{{ filledRichEditorCount }}/5 已形成正文</span>
            </div>
          </div>

          <div class="panel-stack">
            <div
              class="panel-card rich-editor-card"
              :class="{ 'is-collapsed': !expandedEditors.student_summary, 'is-active': assistantFocusKey === 'student_summary' }"
              :id="sectionIdMap.studentSummary"
            >
              <div class="editor-label-bar" @click="toggleEditor('student_summary')">
                <div class="editor-label-left">
                  <label>学生画像摘要</label>
                  <span class="editor-usage">建议写清背景、核心优势、兴趣方向与目标岗位匹配基础。</span>
                  <span class="editor-status-inline" :class="`editor-status-inline--${fieldStatus('student_summary')}`">
                    {{ fieldStatusLabel('student_summary') }}
                  </span>
                  <span v-if="!expandedEditors.student_summary && form.student_summary" class="content-preview">
                    {{ getPreviewText(form.student_summary) }}
                  </span>
                </div>
                <div class="editor-label-actions" v-if="expandedEditors.student_summary" @click.stop>
                  <el-button text type="primary" :icon="MagicStick" size="small" @click="polishContent('student_summary')">
                    AI 润色
                  </el-button>
                </div>
              </div>
              <div v-show="expandedEditors.student_summary" class="editor-content-wrapper">
                <WangEditor v-model="form.student_summary" placeholder="描述学生的专业背景、能力水平、兴趣方向等..." />
              </div>
            </div>

            <div class="panel-card rich-editor-card" :class="{ 'is-collapsed': !expandedEditors.current_gap, 'is-active': assistantFocusKey === 'current_gap' }" :id="sectionIdMap.currentGap">
              <div class="editor-label-bar" @click="toggleEditor('current_gap')">
                <div class="editor-label-left">
                  <label>能力差距分析</label>
                  <span class="editor-usage">先给结论，再拆解硬技能、项目经历和岗位要求差距。</span>
                  <span class="editor-status-inline" :class="`editor-status-inline--${fieldStatus('current_gap')}`">
                    {{ fieldStatusLabel('current_gap') }}
                  </span>
                  <span v-if="!expandedEditors.current_gap && form.current_gap" class="content-preview">
                    {{ getPreviewText(form.current_gap) }}
                  </span>
                </div>
                <div class="editor-label-actions" v-if="expandedEditors.current_gap" @click.stop>
                  <el-button text type="primary" :icon="MagicStick" size="small" @click="polishContent('current_gap')">
                    AI 润色
                  </el-button>
                </div>
              </div>
              <div v-show="expandedEditors.current_gap" class="editor-content-wrapper">
                <WangEditor v-model="form.current_gap" placeholder="分析当前能力与目标岗位要求之间的差距..." />
              </div>
            </div>

            <div class="panel-card rich-editor-card" :class="{ 'is-collapsed': !expandedEditors.short_goal, 'is-active': assistantFocusKey === 'short_goal' }" :id="sectionIdMap.shortGoal">
              <div class="editor-label-bar" @click="toggleEditor('short_goal')">
                <div class="editor-label-left">
                  <label>短期目标</label>
                  <span class="editor-usage">聚焦 1-3 个月内最重要且可衡量的阶段结果。</span>
                  <span class="editor-status-inline" :class="`editor-status-inline--${fieldStatus('short_goal')}`">
                    {{ fieldStatusLabel('short_goal') }}
                  </span>
                  <span v-if="!expandedEditors.short_goal && form.short_term_plan.goal" class="content-preview">
                    {{ getPreviewText(form.short_term_plan.goal) }}
                  </span>
                </div>
                <div class="editor-label-actions" v-if="expandedEditors.short_goal" @click.stop>
                  <el-button text type="primary" :icon="MagicStick" size="small" @click="polishContent('short_goal')">
                    AI 润色
                  </el-button>
                </div>
              </div>
              <div v-show="expandedEditors.short_goal" class="editor-content-wrapper">
                <WangEditor v-model="form.short_term_plan.goal" placeholder="描述 1-3 个月内要达成的具体目标..." />
              </div>
            </div>

            <div class="panel-card rich-editor-card" :class="{ 'is-collapsed': !expandedEditors.mid_goal, 'is-active': assistantFocusKey === 'mid_goal' }" :id="sectionIdMap.midGoal">
              <div class="editor-label-bar" @click="toggleEditor('mid_goal')">
                <div class="editor-label-left">
                  <label>中期目标</label>
                  <span class="editor-usage">明确 3-12 个月的成长路线、阶段成果与发展方向。</span>
                  <span class="editor-status-inline" :class="`editor-status-inline--${fieldStatus('mid_goal')}`">
                    {{ fieldStatusLabel('mid_goal') }}
                  </span>
                  <span v-if="!expandedEditors.mid_goal && form.mid_term_plan.goal" class="content-preview">
                    {{ getPreviewText(form.mid_term_plan.goal) }}
                  </span>
                </div>
                <div class="editor-label-actions" v-if="expandedEditors.mid_goal" @click.stop>
                  <el-button text type="primary" :icon="MagicStick" size="small" @click="polishContent('mid_goal')">
                    AI 润色
                  </el-button>
                </div>
              </div>
              <div v-show="expandedEditors.mid_goal" class="editor-content-wrapper">
                <WangEditor v-model="form.mid_term_plan.goal" placeholder="描述 3-12 个月内要达成的阶段目标..." />
              </div>
            </div>

            <div class="panel-card rich-editor-card" :class="{ 'is-collapsed': !expandedEditors.career_progression, 'is-active': assistantFocusKey === 'career_progression' }" :id="sectionIdMap.careerProgression">
              <div class="editor-label-bar" @click="toggleEditor('career_progression')">
                <div class="editor-label-left">
                  <label>职业发展预期</label>
                  <span class="editor-usage">用于生成最终报告中的中长期发展判断和岗位演进路径。</span>
                  <span class="editor-status-inline" :class="`editor-status-inline--${fieldStatus('career_progression')}`">
                    {{ fieldStatusLabel('career_progression') }}
                  </span>
                  <span v-if="!expandedEditors.career_progression && form.mid_term_plan.career_progression" class="content-preview">
                    {{ getPreviewText(form.mid_term_plan.career_progression) }}
                  </span>
                </div>
                <div class="editor-label-actions" v-if="expandedEditors.career_progression" @click.stop>
                  <el-button text type="primary" :icon="MagicStick" size="small" @click="polishContent('career_progression')">
                    AI 润色
                  </el-button>
                </div>
              </div>
              <div v-show="expandedEditors.career_progression" class="editor-content-wrapper">
                <WangEditor v-model="form.mid_term_plan.career_progression" placeholder="描述长期职业发展路径和阶段预期..." />
              </div>
            </div>
          </div>
        </section>

        <section :id="sectionIdMap.shortPlan" class="editor-section" :class="{ 'is-focus': activeFocusKey === 'short-plan' }">
          <div class="section-head">
            <div>
              <h2>短期计划</h2>
              <span class="section-hint">围绕最近 1-3 个月拆解重点领域、快速行动与里程碑。</span>
            </div>
            <div class="section-head-actions">
              <span class="section-count">{{ form.short_term_plan.milestones.length }} 个里程碑</span>
              <el-button text type="primary" @click="appendString(form.short_term_plan.focus_areas)">新增重点领域</el-button>
            </div>
          </div>

          <div class="panel-card panel-card--soft">
            <label>重点领域</label>
            <div class="inline-list">
              <div v-for="(_, index) in form.short_term_plan.focus_areas" :key="`short-focus-${index}`" class="inline-item">
                <el-input v-model="form.short_term_plan.focus_areas[index]" placeholder="重点领域" />
                <el-button text type="danger" @click="removeAt(form.short_term_plan.focus_areas, index)">删除</el-button>
              </div>
            </div>
          </div>

          <div class="section-head section-head--sub">
            <h3>快速行动</h3>
            <el-button text type="primary" @click="appendString(form.short_term_plan.quick_wins)">新增行动</el-button>
          </div>
          <div class="panel-card panel-card--soft">
            <div class="inline-list">
              <div v-for="(_, index) in form.short_term_plan.quick_wins" :key="`short-win-${index}`" class="inline-item">
                <el-input v-model="form.short_term_plan.quick_wins[index]" placeholder="快速行动" />
                <el-button text type="danger" @click="removeAt(form.short_term_plan.quick_wins, index)">删除</el-button>
              </div>
            </div>
          </div>

          <MilestoneEditor title="短期里程碑" :list="form.short_term_plan.milestones as Milestone[]" @add="addMilestone(form.short_term_plan.milestones as Milestone[])" />
        </section>
        <section :id="sectionIdMap.midPlan" class="editor-section" :class="{ 'is-focus': activeFocusKey === 'mid-plan' }">
          <div class="section-head">
            <div>
              <h2>中期计划</h2>
              <span class="section-hint">延展 3-12 个月的技能路线、阶段里程碑与成长路径。</span>
            </div>
            <div class="section-head-actions">
              <span class="section-count">{{ form.mid_term_plan.skill_roadmap.length }} 条技能路线</span>
              <el-button text type="primary" @click="appendString(form.mid_term_plan.skill_roadmap)">新增技能路线</el-button>
            </div>
          </div>
          <div class="panel-card panel-card--soft">
            <label>技能路线图</label>
            <div class="inline-list">
              <div v-for="(_, index) in form.mid_term_plan.skill_roadmap" :key="`roadmap-${index}`" class="inline-item">
                <el-input v-model="form.mid_term_plan.skill_roadmap[index]" placeholder="技能路线" />
                <el-button text type="danger" @click="removeAt(form.mid_term_plan.skill_roadmap, index)">删除</el-button>
              </div>
            </div>
          </div>

          <MilestoneEditor title="中期里程碑" :list="form.mid_term_plan.milestones as Milestone[]" @add="addMilestone(form.mid_term_plan.milestones as Milestone[])" />
        </section>

        <section :id="sectionIdMap.internship" class="editor-section" :class="{ 'is-focus': activeFocusKey === 'internship' }">
          <div class="section-head">
            <div>
              <h2>推荐实习</h2>
              <span class="section-hint">补充与目标岗位关联度高的实习机会和投递理由。</span>
            </div>
            <div class="section-head-actions">
              <span class="section-count">{{ form.mid_term_plan.recommended_internships.length }} 条记录</span>
              <el-button text type="primary" @click="addInternship">新增实习</el-button>
            </div>
          </div>
          <div v-if="!form.mid_term_plan.recommended_internships.length" class="panel-card panel-card--empty">暂无推荐实习</div>
          <div v-for="(internship, internshipIndex) in form.mid_term_plan.recommended_internships" :key="internship.id" class="editor-block">
            <div class="block-toolbar">
              <strong>实习 {{ internshipIndex + 1 }}</strong>
              <el-button text type="danger" @click="removeAt(form.mid_term_plan.recommended_internships, internshipIndex)">删除</el-button>
            </div>
            <div class="panel-grid panel-grid--two">
              <el-input v-model="internship.job_title" placeholder="岗位名称" />
              <el-input v-model="internship.company_name" placeholder="公司名称" />
              <el-input v-model="internship.city" placeholder="城市" />
              <el-input v-model="internship.salary" placeholder="薪资" />
              <el-input v-model="internship.degree" placeholder="学历要求" />
              <el-input v-model="internship.job_type" placeholder="岗位类型" />
              <el-input v-model="internship.tech_stack" placeholder="技术栈" />
              <el-input v-model="internship.url" placeholder="链接" />
              <el-input-number v-model="internship.days_per_week" :min="0" :max="7" />
              <el-input-number v-model="internship.months" :min="0" :max="24" />
            </div>
            <div class="panel-stack">
              <div class="panel-card">
                <label>推荐理由</label>
                <el-input v-model="internship.reason" type="textarea" :rows="4" />
              </div>
              <div class="panel-card">
                <label>岗位描述</label>
                <el-input v-model="internship.content" type="textarea" :rows="4" />
              </div>
            </div>
          </div>
        </section>

        <section :id="sectionIdMap.checklist" class="editor-section" :class="{ 'is-focus': activeFocusKey === 'checklist' }">
          <div class="section-head">
            <div>
              <h2>行动清单</h2>
              <span class="section-hint">整理导出后可直接执行的行动项，建议控制在 3-8 条。</span>
            </div>
            <div class="section-head-actions">
              <span class="section-count">{{ form.action_checklist.length }} 条行动</span>
              <el-button text type="primary" @click="appendString(form.action_checklist)">新增清单项</el-button>
            </div>
          </div>
          <div class="panel-card panel-card--soft">
            <div class="inline-list">
              <div v-for="(_, index) in form.action_checklist" :key="`check-${index}`" class="inline-item">
                <el-input v-model="form.action_checklist[index]" placeholder="行动项" />
                <el-button text type="danger" @click="removeAt(form.action_checklist, index)">删除</el-button>
              </div>
            </div>
          </div>
        </section>

        <section :id="sectionIdMap.tips" class="editor-section" :class="{ 'is-focus': activeFocusKey === 'tips' }">
          <div class="section-head">
            <div>
              <h2>成长建议</h2>
              <span class="section-hint">保留长期提醒和策略建议，作为报告收尾部分的行动提示。</span>
            </div>
            <div class="section-head-actions">
              <span class="section-count">{{ form.tips.length }} 条建议</span>
              <el-button text type="primary" @click="appendString(form.tips)">新增建议</el-button>
            </div>
          </div>
          <div class="panel-card panel-card--soft">
            <div class="inline-list">
              <div v-for="(_, index) in form.tips" :key="`tip-${index}`" class="inline-item">
                <el-input v-model="form.tips[index]" placeholder="建议内容" />
                <el-button text type="danger" @click="removeAt(form.tips, index)">删除</el-button>
              </div>
            </div>
          </div>
        </section>
      </main>

      <aside class="editor-ai-panel">
        <section class="ai-panel-card">
          <div class="ai-panel-head">
            <div>
              <p class="editor-kicker">AI Assistant</p>
              <h2>模块顾问</h2>
              <p class="ai-panel-desc">围绕当前模块给出润色、诊断和快速跳转支持。</p>
            </div>
            <span class="context-pill">{{ assistantFocusLabel }}</span>
          </div>

          <div class="ai-panel-block ai-panel-block--context">
            <span class="ai-block-title">当前模块</span>
            <div class="ai-focus-card">
              <strong>{{ assistantFocusLabel }}</strong>
              <p>{{ currentModuleGoal }}</p>
              <span class="ai-focus-state" :class="`ai-focus-state--${currentFocusState}`">
                {{ currentFocusStateLabel }}
              </span>
            </div>
            <el-button type="primary" plain @click="scrollToSection(assistantFocusKey)">定位当前模块</el-button>
          </div>

          <div class="ai-panel-block">
            <span class="ai-block-title">当前模块预览</span>
            <div class="context-preview-card">
              <p>{{ currentModulePreview }}</p>
            </div>
          </div>

          <div class="ai-panel-block">
            <span class="ai-block-title">诊断建议</span>
            <div v-if="assistantChecklist.length" class="insight-list">
              <div v-for="item in assistantChecklist" :key="item" class="insight-item">
                <span class="insight-dot" />
                <span>{{ item }}</span>
              </div>
            </div>
            <div v-else class="assistant-good-state">
              <span class="assistant-good-badge">已完整</span>
              <p>当前模块结构完整，可以直接继续精修措辞与表达层次。</p>
            </div>
          </div>

          <div class="ai-panel-block">
            <span class="ai-block-title">快捷操作</span>
            <div class="ai-action-grid">
              <el-button type="primary" @click="polishFocusedContent">优化措辞</el-button>
              <el-button @click="runAssistantCheck">检查完整性</el-button>
              <el-button plain @click="toggleAllEditors">{{ allEditorsExpanded ? '收起编辑器' : '展开编辑器' }}</el-button>
            </div>
          </div>

          <div class="ai-panel-block">
            <span class="ai-block-title">页面操作</span>
            <div class="ai-action-grid ai-action-grid--secondary">
              <el-button @click="goBack">返回报告</el-button>
              <el-button type="primary" plain @click="saveReport">保存修改</el-button>
            </div>
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, nextTick, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowDown, ArrowLeft, ArrowRight, Check, MagicStick } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'

import WangEditor from '@/components/Person_Report/WangEditor.vue'
import { useCareerReportStore } from '@/stores'
import {
  createEmptyCareerReport,
  type EditableSectionKey,
  type GrowthPlanData,
  type InternshipItem,
  type Milestone,
  type PlanTask,
  type ResourceItem,
} from '@/types/career-report'

const route = useRoute()
const router = useRouter()
const reportStore = useCareerReportStore()

const expandedEditors = reactive({
  student_summary: true,
  current_gap: false,
  short_goal: false,
  mid_goal: false,
  career_progression: false,
})

const expandedNavItems = reactive<Record<string, boolean>>({
  summary: true,
})

const assistantFocusKey = ref<string>('student_summary')

const editableFocusLabels: Record<EditableSectionKey, string> = {
  student_summary: '学生画像摘要',
  current_gap: '能力差距分析',
  short_goal: '短期目标',
  mid_goal: '中期目标',
  career_progression: '职业发展预期',
}

type NavItem = {
  key: string
  label: string
  children?: { key: string; label: string }[]
}

const navItems: NavItem[] = [
  { key: 'basic', label: '基础信息' },
  {
    key: 'summary',
    label: '核心内容',
    children: [
      { key: 'student_summary', label: '学生画像' },
      { key: 'current_gap', label: '能力差距' },
      { key: 'short_goal', label: '短期目标' },
      { key: 'mid_goal', label: '中期目标' },
      { key: 'career_progression', label: '职业发展' },
    ],
  },
  { key: 'short-plan', label: '短期计划' },
  { key: 'mid-plan', label: '中期计划' },
  { key: 'internship', label: '推荐实习' },
  { key: 'checklist', label: '行动清单' },
  { key: 'tips', label: '成长建议' },
]

const sectionIdMap = {
  basic: 'editor-basic',
  summary: 'editor-summary',
  studentSummary: 'editor-student-summary',
  currentGap: 'editor-current-gap',
  shortGoal: 'editor-short-goal',
  midGoal: 'editor-mid-goal',
  careerProgression: 'editor-career-progression',
  shortPlan: 'editor-short-plan',
  midPlan: 'editor-mid-plan',
  internship: 'editor-internship',
  checklist: 'editor-checklist',
  tips: 'editor-tips',
} as const

const form = reactive<GrowthPlanData>(cloneReport(reportStore.ensureReport(createEmptyCareerReport())))
const lastSavedAt = ref<string>('未保存')
const saveState = ref<'idle' | 'saved' | 'dirty'>('idle')
const lastSavedSnapshot = ref('')

const allEditorsExpanded = computed(() => Object.values(expandedEditors).every(Boolean))

const assistantFocusLabel = computed(() => {
  if (assistantFocusKey.value in editableFocusLabels) {
    return editableFocusLabels[assistantFocusKey.value as EditableSectionKey]
  }

  const navLabel = navItems.flatMap(item => [item, ...(item.children || [])]).find(
    item => item.key === assistantFocusKey.value,
  )?.label

  return navLabel || '当前模块'
})

const assistantChecklist = computed(() => {
  const focus = assistantFocusKey.value
  const tips: string[] = []

  if (focus === 'student_summary' && !plainText(form.student_summary)) tips.push('补充个人背景、优势能力和目标方向。')
  if (focus === 'current_gap' && !plainText(form.current_gap)) tips.push('补充当前能力差距和待提升项。')
  if (focus === 'short_goal' && !plainText(form.short_term_plan.goal)) tips.push('短期目标建议写清时间节点和可衡量结果。')
  if (focus === 'mid_goal' && !plainText(form.mid_term_plan.goal)) tips.push('中期目标建议补充阶段成果和成长方向。')
  if (focus === 'career_progression' && !plainText(form.mid_term_plan.career_progression)) tips.push('职业发展预期建议补充成长路径和预期岗位。')
  if (focus === 'short-plan' && !form.short_term_plan.milestones.length) tips.push('短期计划建议至少配置一个里程碑。')
  if (focus === 'mid-plan' && !form.mid_term_plan.milestones.length) tips.push('中期计划建议至少配置一个里程碑。')
  if (focus === 'internship' && !form.mid_term_plan.recommended_internships.length) tips.push('可补充 1-3 个目标岗位对应的实习机会。')
  if (focus === 'checklist' && !form.action_checklist.length) tips.push('建议先列出 3 条可以马上执行的行动项。')
  if (focus === 'tips' && !form.tips.length) tips.push('成长建议建议保留 2-5 条长期提醒。')

  return tips
})

const currentModulePreview = computed(() => {
  const focus = normalizeAssistantFocus(assistantFocusKey.value)
  if (focus in editableFocusLabels) {
    return getPreviewText(getFieldValue(focus as EditableSectionKey), 120) || '当前模块还没有形成可预览的正文内容。'
  }
  if (focus === 'short-plan') {
    return form.short_term_plan.quick_wins[0] || form.short_term_plan.focus_areas[0] || '建议先补充一个短期里程碑或快速行动。'
  }
  if (focus === 'mid-plan') {
    return form.mid_term_plan.skill_roadmap[0] || '建议先补充一条中期技能路线。'
  }
  if (focus === 'internship') {
    return form.mid_term_plan.recommended_internships[0]?.job_title || '建议补充目标岗位对应的推荐实习。'
  }
  if (focus === 'checklist') {
    return form.action_checklist[0] || '建议先列出一条本周可执行行动。'
  }
  if (focus === 'tips') {
    return form.tips[0] || '建议补充一条长期成长提醒。'
  }
  return '定位到当前模块后，这里会显示即时预览摘要。'
})

const currentModuleGoal = computed(() => {
  const focus = normalizeAssistantFocus(assistantFocusKey.value)
  if (focus === 'student_summary') return '写清背景、优势、目标方向，形成报告开场。'
  if (focus === 'current_gap') return '先下结论，再说明关键差距与补齐重点。'
  if (focus === 'short_goal') return '明确 1-3 个月内最重要的阶段成果。'
  if (focus === 'mid_goal') return '突出中期成长路径和阶段跃迁方向。'
  if (focus === 'career_progression') return '强调未来岗位发展预期与可达成路径。'
  if (focus === 'short-plan') return '把目标拆成短期里程碑、任务和资源。'
  if (focus === 'mid-plan') return '把中期路线拆成技能路径和阶段性成果。'
  if (focus === 'internship') return '补充与目标岗位高度关联的实习机会。'
  if (focus === 'checklist') return '沉淀马上可执行的行动项。'
  if (focus === 'tips') return '保留能持续提醒自己的成长建议。'
  return '围绕当前模块补充可直接进入最终报告的内容。'
})

const hasUnsavedChanges = computed(() => lastSavedSnapshot.value !== JSON.stringify(form))
const activeFocusKey = computed(() => normalizeAssistantFocus(assistantFocusKey.value))

const filledRichEditorCount = computed(() =>
  (Object.keys(editableFocusLabels) as EditableSectionKey[]).filter(key => hasSectionContent(key)).length,
)

const currentFocusState = computed(() => getNavState(activeFocusKey.value))
const currentFocusStateLabel = computed(() => navStateLabel(activeFocusKey.value))

function hasSectionContent(key: string): boolean {
  if (key === 'basic') {
    return Boolean(form.target_position || form.short_term_plan.duration || form.mid_term_plan.duration)
  }
  if (key === 'summary') {
    return (Object.keys(editableFocusLabels) as EditableSectionKey[]).some(item => hasSectionContent(item))
  }
  if (key === 'student_summary') return Boolean(plainText(form.student_summary))
  if (key === 'current_gap') return Boolean(plainText(form.current_gap))
  if (key === 'short_goal') return Boolean(plainText(form.short_term_plan.goal))
  if (key === 'mid_goal') return Boolean(plainText(form.mid_term_plan.goal))
  if (key === 'career_progression') return Boolean(plainText(form.mid_term_plan.career_progression))
  if (key === 'short-plan') {
    return Boolean(
      form.short_term_plan.focus_areas.length ||
      form.short_term_plan.quick_wins.length ||
      form.short_term_plan.milestones.length,
    )
  }
  if (key === 'mid-plan') {
    return Boolean(form.mid_term_plan.skill_roadmap.length || form.mid_term_plan.milestones.length)
  }
  if (key === 'internship') return Boolean(form.mid_term_plan.recommended_internships.length)
  if (key === 'checklist') return Boolean(form.action_checklist.length)
  if (key === 'tips') return Boolean(form.tips.length)
  return false
}

function isNavCurrent(key: string): boolean {
  if (key === activeFocusKey.value) return true
  if (key === 'summary' && activeFocusKey.value in editableFocusLabels) return true
  return false
}

function getNavState(key: string): 'active' | 'filled' | 'empty' {
  if (isNavCurrent(key)) return 'active'
  return hasSectionContent(key) ? 'filled' : 'empty'
}

function navStateLabel(key: string): string {
  const state = getNavState(key)
  if (state === 'active') return '当前'
  if (state === 'filled') return '已填'
  return '待完善'
}

function fieldStatus(key: EditableSectionKey): 'active' | 'filled' | 'empty' {
  if (assistantFocusKey.value === key) return 'active'
  return hasSectionContent(key) ? 'filled' : 'empty'
}

function fieldStatusLabel(key: EditableSectionKey): string {
  const state = fieldStatus(key)
  if (state === 'active') return '当前编辑'
  if (state === 'filled') return '已填写'
  return '待完善'
}

function cloneReport<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
}

function createId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function createTask(): PlanTask {
  return {
    task_name: '',
    description: '',
    priority: '中',
    estimated_time: '',
    skill_target: '',
    success_criteria: '',
    resources: [],
  }
}

function createMilestone(): Milestone {
  return {
    milestone_name: '',
    target_date: '',
    key_results: [],
    tasks: [],
  }
}

function createResource(): ResourceItem {
  return {
    id: createId('resource'),
    title: '',
    description: '',
    url: '',
    reason: '',
  }
}

function createInternship(): InternshipItem {
  return {
    id: createId('internship'),
    job_title: '',
    company_name: '',
    salary: '',
    city: '',
    degree: '',
    days_per_week: 3,
    months: 3,
    job_type: '实习',
    tech_stack: '',
    url: '',
    content: '',
    reason: '',
  }
}

function toggleEditor(field: keyof typeof expandedEditors): void {
  const nextState = !expandedEditors[field]
  Object.keys(expandedEditors).forEach(key => {
    expandedEditors[key as keyof typeof expandedEditors] = false
  })
  expandedEditors[field] = nextState
  assistantFocusKey.value = field
}

function toggleNavItem(key: string): void {
  expandedNavItems[key] = !expandedNavItems[key]
}

function toggleAllEditors(): void {
  const nextState = !allEditorsExpanded.value
  Object.keys(expandedEditors).forEach(key => {
    expandedEditors[key as keyof typeof expandedEditors] = nextState
  })
}

function getPreviewText(html: string, maxLength = 60): string {
  const text = plainText(html)
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

function plainText(value: string): string {
  return value.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
}

function textToHtml(text: string): string {
  const source = plainText(text)
  if (!source) return ''
  return source
    .split(/\n+/)
    .filter(Boolean)
    .map(line => `<p>${line}</p>`)
    .join('')
}

function polishHtml(source: string): string {
  const normalized = plainText(source)
    .replace(/\bSpringboot\b/gi, 'Spring Boot')
    .replace(/\bmysql\b/gi, 'MySQL')
    .replace(/\s*([，。；：！？])/g, '$1')
    .replace(/([，。；：！？])(?!\s|$)/g, '$1 ')
    .trim()

  return textToHtml(normalized)
}

function appendString(list: string[]): void {
  list.push('')
}

function removeAt<T>(list: T[], index: number): void {
  list.splice(index, 1)
}

function addMilestone(list: Milestone[]): void {
  list.push(createMilestone())
}

function addTask(list: PlanTask[]): void {
  list.push(createTask())
}

function addResource(list: ResourceItem[]): void {
  list.push(createResource())
}

function addInternship(): void {
  form.mid_term_plan.recommended_internships.push(createInternship())
}

function goBack(): void {
  router.push({ name: 'report' })
}

function saveReport(): void {
  reportStore.setReport(cloneReport(form))

  if (assistantFocusKey.value in editableFocusLabels) {
    reportStore.setLastEditedSection(assistantFocusKey.value as EditableSectionKey)
  }

  ElMessage.success('生涯报告已保存，正在返回报告页...')
  lastSavedSnapshot.value = JSON.stringify(form)
  lastSavedAt.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  saveState.value = 'saved'
  setTimeout(() => {
    router.push({ name: 'report' })
  }, 300)
}

async function scrollToSection(key: string): Promise<void> {
  await nextTick()

  const idMap: Record<string, string> = {
    basic: sectionIdMap.basic,
    summary: sectionIdMap.summary,
    student_summary: sectionIdMap.studentSummary,
    current_gap: sectionIdMap.currentGap,
    short_goal: sectionIdMap.shortGoal,
    mid_goal: sectionIdMap.midGoal,
    career_progression: sectionIdMap.careerProgression,
    'short-plan': sectionIdMap.shortPlan,
    'mid-plan': sectionIdMap.midPlan,
    internship: sectionIdMap.internship,
    checklist: sectionIdMap.checklist,
    tips: sectionIdMap.tips,
  }

  assistantFocusKey.value = normalizeAssistantFocus(key)
  document.getElementById(idMap[key])?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}
function normalizeAssistantFocus(key: string): string {
  if (key in editableFocusLabels) return key
  if (key === 'summary') return 'student_summary'
  if (key === 'short-plan') return 'short-plan'
  if (key === 'mid-plan') return 'mid-plan'
  return key
}

function runAssistantCheck(): void {
  if (!assistantChecklist.value.length) {
    ElMessage.success(`${assistantFocusLabel.value} 当前结构完整`)
    return
  }

  ElMessage.warning(`${assistantFocusLabel.value} 还有 ${assistantChecklist.value.length} 条可完善建议`)
}

function getFieldValue(field: EditableSectionKey): string {
  if (field === 'student_summary') return form.student_summary
  if (field === 'current_gap') return form.current_gap
  if (field === 'short_goal') return form.short_term_plan.goal
  if (field === 'mid_goal') return form.mid_term_plan.goal
  return form.mid_term_plan.career_progression
}

function setFieldValue(field: EditableSectionKey, value: string): void {
  if (field === 'student_summary') form.student_summary = value
  else if (field === 'current_gap') form.current_gap = value
  else if (field === 'short_goal') form.short_term_plan.goal = value
  else if (field === 'mid_goal') form.mid_term_plan.goal = value
  else form.mid_term_plan.career_progression = value
}

function polishContent(field: EditableSectionKey): void {
  setFieldValue(field, polishHtml(getFieldValue(field)))
  assistantFocusKey.value = field
  ElMessage.success(`${editableFocusLabels[field]} 已完成润色`)
}

function polishFocusedContent(): void {
  const focus = normalizeAssistantFocus(assistantFocusKey.value)
  if (focus in editableFocusLabels) {
    polishContent(focus as EditableSectionKey)
    return
  }

  ElMessage.info('当前模块以结构化编辑为主，请直接补充列表和字段内容。')
}

const routeToSection = computed(() => {
  const section = String(route.query.section || '')

  if (['student_summary', 'current_gap', 'short_goal', 'mid_goal', 'career_progression'].includes(section)) {
    return section
  }
  if (section === 'summary') return 'student_summary'
  if (section === 'short-plan') return 'short-plan'
  if (section === 'mid-plan') return 'mid-plan'
  return ''
})

watch(
  routeToSection,
  async value => {
    if (!value) return
    if (value in expandedEditors) {
      expandedEditors[value as keyof typeof expandedEditors] = true
    }
    await scrollToSection(value)
  },
  { immediate: true },
)

lastSavedSnapshot.value = JSON.stringify(form)
saveState.value = 'saved'
lastSavedAt.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })

watch(
  form,
  () => {
    saveState.value = hasUnsavedChanges.value ? 'dirty' : 'saved'
  },
  { deep: true },
)

const MilestoneEditor = defineComponent({
  name: 'MilestoneEditor',
  props: {
    title: { type: String, required: true },
    list: { type: Array, required: true },
  },
  emits: ['add'],
  setup() {
    return {
      appendString,
      removeAt,
      addTask,
      addResource,
    }
  },
  template: `
    <div class="milestone-editor">
      <div class="section-head section-head--sub">
        <h3>{{ title }}</h3>
        <el-button text type="primary" @click="$emit('add')">新增里程碑</el-button>
      </div>

      <div v-if="!list.length" class="panel-card panel-card--empty">暂无里程碑</div>

      <div v-for="(milestone, milestoneIndex) in list" :key="\`\${title}-\${milestoneIndex}\`" class="editor-block">
        <div class="block-toolbar">
          <strong>{{ title }} {{ milestoneIndex + 1 }}</strong>
          <el-button text type="danger" @click="removeAt(list, milestoneIndex)">删除</el-button>
        </div>

        <div class="panel-grid panel-grid--two">
          <el-input v-model="milestone.milestone_name" placeholder="里程碑名称" />
          <el-input v-model="milestone.target_date" placeholder="目标日期" />
        </div>

        <div class="panel-card">
          <div class="mini-toolbar">
            <label>关键成果</label>
            <el-button text type="primary" @click="appendString(milestone.key_results)">新增成果</el-button>
          </div>
          <div class="inline-list">
            <div v-for="(_, resultIndex) in milestone.key_results" :key="\`result-\${resultIndex}\`" class="inline-item">
              <el-input v-model="milestone.key_results[resultIndex]" placeholder="关键成果" />
              <el-button text type="danger" @click="removeAt(milestone.key_results, resultIndex)">删除</el-button>
            </div>
          </div>
        </div>

        <div class="panel-card">
          <div class="mini-toolbar">
            <label>任务列表</label>
            <el-button text type="primary" @click="addTask(milestone.tasks)">新增任务</el-button>
          </div>
          <div v-if="!milestone.tasks.length" class="panel-card panel-card--empty panel-card--inner">暂无任务</div>

          <div v-for="(task, taskIndex) in milestone.tasks" :key="\`task-\${taskIndex}\`" class="task-editor">
            <div class="block-toolbar">
              <strong>任务 {{ taskIndex + 1 }}</strong>
              <el-button text type="danger" @click="removeAt(milestone.tasks, taskIndex)">删除</el-button>
            </div>

            <div class="panel-grid panel-grid--two">
              <el-input v-model="task.task_name" placeholder="任务名称" />
              <el-select v-model="task.priority" placeholder="优先级">
                <el-option label="高" value="高" />
                <el-option label="中" value="中" />
                <el-option label="低" value="低" />
              </el-select>
              <el-input v-model="task.estimated_time" placeholder="预计时间" />
              <el-input v-model="task.skill_target" placeholder="目标能力" />
            </div>

            <div class="panel-stack">
              <el-input v-model="task.description" type="textarea" :rows="3" placeholder="任务描述" />
              <el-input v-model="task.success_criteria" type="textarea" :rows="3" placeholder="成功标准" />
            </div>

            <div class="panel-card panel-card--inner">
              <div class="mini-toolbar">
                <label>资源列表</label>
                <el-button text type="primary" @click="addResource(task.resources)">新增资源</el-button>
              </div>

              <div v-if="!task.resources.length" class="panel-card panel-card--empty panel-card--inner">暂无资源</div>

              <div v-for="(resource, resourceIndex) in task.resources" :key="resource.id || resourceIndex" class="resource-editor">
                <div class="block-toolbar">
                  <strong>资源 {{ resourceIndex + 1 }}</strong>
                  <el-button text type="danger" @click="removeAt(task.resources, resourceIndex)">删除</el-button>
                </div>

                <div class="panel-grid panel-grid--two">
                  <el-input v-model="resource.title" placeholder="资源标题" />
                  <el-input v-model="resource.author" placeholder="作者" />
                  <el-input v-model="resource.url" placeholder="链接" />
                  <el-input v-model="resource.duration" placeholder="时长/类型说明" />
                </div>

                <div class="panel-stack">
                  <el-input v-model="resource.description" type="textarea" :rows="2" placeholder="资源描述" />
                  <el-input v-model="resource.reason" type="textarea" :rows="2" placeholder="推荐理由" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
})
</script>

<style scoped>
.report-editor-page {
  --surface-bg: rgba(255, 255, 255, 0.92);
  --card-shadow: 0 16px 36px rgba(15, 23, 42, 0.08);
  --card-shadow-soft: 0 10px 22px rgba(15, 23, 42, 0.05);
  --card-border: 1px solid rgba(148, 163, 184, 0.14);
  --radius-lg: 22px;
  --radius-md: 18px;
  --transition-smooth: all 0.28s ease;

  min-height: 100vh;
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(250, 204, 21, 0.14), transparent 28%),
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.1), transparent 30%),
    linear-gradient(180deg, #fffdf8 0%, #f8fbff 100%);
}

.editor-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
  margin-bottom: 28px;
  border-radius: var(--radius-lg);
  border: var(--card-border);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 251, 255, 0.92));
  backdrop-filter: blur(18px);
  box-shadow: var(--card-shadow);
}

.editor-brand,
.editor-content,
.ai-panel-card,
.panel-stack,
.inline-list,
.ai-action-grid,
.insight-list {
  display: grid;
  gap: 14px;
}

.editor-kicker {
  margin: 0;
  font-size: 11px;
  line-height: 1;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #2563eb;
}

.editor-brand h1,
.ai-panel-head h2,
.section-head h2 {
  margin: 0;
  color: #0f172a;
}

.editor-subtitle,
.ai-panel-desc,
.section-hint,
.ai-context-copy {
  margin: 0;
  color: #475569;
}

.editor-brand h1 {
  font-size: 28px;
}

.editor-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.editor-status-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-chip--idle,
.status-chip--saved {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.status-chip--dirty {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.status-chip--focus {
  background: rgba(37, 99, 235, 0.1);
  color: #1d4ed8;
}

.status-text {
  color: #64748b;
  font-size: 13px;
}

.editor-layout {
  display: grid;
  grid-template-columns: 208px minmax(0, 1.2fr) 292px;
  gap: 20px;
  align-items: start;
}

.editor-sidebar,
.editor-ai-panel,
.editor-content {
  min-width: 0;
}

.editor-sidebar,
.ai-panel-card,
.editor-section,
.editor-block,
.panel-card {
  border-radius: var(--radius-lg);
  border: var(--card-border);
  background: var(--surface-bg);
  box-shadow: var(--card-shadow-soft);
}

.editor-sidebar {
  position: sticky;
  top: 20px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.88);
}

.sidebar-head {
  padding: 10px 10px 14px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  margin-bottom: 10px;
}

.sidebar-head h2 {
  margin: 6px 0 4px;
  font-size: 18px;
  color: #0f172a;
}

.sidebar-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.6;
}

.nav-group + .nav-group {
  margin-top: 10px;
}

.nav-button,
.section-head,
.block-toolbar,
.mini-toolbar,
.editor-label-bar,
.ai-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.nav-button {
  width: 100%;
  padding: 12px 12px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: #1e293b;
  cursor: pointer;
  transition: var(--transition-smooth);
  text-align: left;
  position: relative;
}

.nav-button:hover,
.nav-button--sub:hover {
  background: rgba(37, 99, 235, 0.08);
}

.nav-button-text {
  flex: 1;
  font-weight: 600;
}

.nav-state-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.6);
  flex-shrink: 0;
}

.nav-state-text {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
}

.nav-button--active {
  background: rgba(37, 99, 235, 0.1);
  color: #1d4ed8;
  box-shadow: inset 3px 0 0 #2563eb;
}

.nav-button--active .nav-button-text {
  font-weight: 700;
}

.nav-button--active .nav-state-dot {
  background: #2563eb;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.14);
}

.nav-button--active .nav-state-text {
  color: #2563eb;
}

.nav-button--filled .nav-state-dot {
  background: #10b981;
}

.nav-button--filled .nav-state-text {
  color: #059669;
}

.nav-button--empty .nav-state-dot {
  background: #cbd5e1;
}

.nav-children {
  display: grid;
  gap: 6px;
  margin-top: 8px;
  padding-left: 14px;
  border-left: 1px dashed rgba(148, 163, 184, 0.2);
}

.nav-button--sub {
  font-size: 13px;
  color: #475569;
  padding-left: 10px;
}

.editor-section,
.editor-block,
.ai-panel-card,
.panel-card {
  padding: 22px;
}

.editor-content {
  gap: 18px;
}

.editor-workbench {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.workbench-card {
  padding: 16px 18px;
  border-radius: 18px;
  background: linear-gradient(135deg, #f8fbff 0%, #ffffff 100%);
  border: var(--card-border);
  box-shadow: var(--card-shadow-soft);
}

.workbench-label {
  display: block;
  margin-bottom: 8px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.workbench-card strong {
  display: block;
  color: #0f172a;
  font-size: 18px;
}

.workbench-card p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
  font-size: 14px;
}

.workbench-card--accent {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(255, 255, 255, 0.98));
}

.workbench-card--focus {
  border-color: rgba(37, 99, 235, 0.2);
}

.workbench-state {
  display: inline-flex;
  width: fit-content;
  margin-top: 10px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.workbench-state--active {
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
}

.workbench-state--filled {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
}

.workbench-state--empty {
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
}

.editor-section {
  position: relative;
  transition: var(--transition-smooth);
}

.editor-section:hover {
  box-shadow: var(--card-shadow);
}

.editor-section.is-focus {
  border-color: rgba(37, 99, 235, 0.22);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08), var(--card-shadow);
}

.editor-section--primary {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 251, 255, 0.94));
}

.section-head {
  margin-bottom: 18px;
}

.section-head--sub {
  margin-top: 20px;
}

.section-head-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-head h2,
.section-head h3 {
  margin: 0;
}

.section-meta,
.section-count {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.04);
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.panel-grid {
  display: grid;
  gap: 14px;
}

.panel-grid--two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.inline-item,
.task-editor,
.resource-editor {
  display: grid;
  gap: 12px;
}

.panel-card--empty {
  text-align: center;
  color: #64748b;
}

.panel-card--soft {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.92), rgba(255, 255, 255, 0.98));
}

.panel-card--inner {
  background: rgba(248, 250, 252, 0.88);
  box-shadow: none;
}

.editor-block {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(249, 251, 255, 0.95));
}

.rich-editor-card {
  overflow: hidden;
  padding: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.99), rgba(248, 251, 255, 0.95));
  border-color: rgba(148, 163, 184, 0.18);
}

.rich-editor-card.is-active {
  border-color: rgba(37, 99, 235, 0.28);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08), var(--card-shadow);
}

.rich-editor-card.is-collapsed .editor-content-wrapper {
  display: none;
}

.editor-label-bar {
  padding: 18px 20px 16px;
  cursor: pointer;
  align-items: flex-start;
}

.editor-label-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.editor-label-left label {
  font-size: 17px;
}

.editor-usage {
  color: #64748b;
  font-size: 12px;
  line-height: 1.6;
}

.editor-status-inline {
  display: inline-flex;
  width: fit-content;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.editor-status-inline--active {
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
}

.editor-status-inline--filled {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
}

.editor-status-inline--empty {
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
}

.editor-label-left label,
.panel-card label,
.mini-toolbar label,
.ai-block-title {
  font-weight: 600;
  color: #0f172a;
}

.content-preview,
.context-pill {
  color: #475569;
  font-size: 13px;
}

.content-preview {
  display: block;
  margin-top: 4px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.04);
  line-height: 1.7;
}

.editor-content-wrapper {
  padding: 0 18px 18px;
  border-top: 1px solid rgba(148, 163, 184, 0.12);
  background: linear-gradient(180deg, rgba(248, 251, 255, 0.4), rgba(255, 255, 255, 0.96));
}

.editor-ai-panel {
  position: sticky;
  top: 20px;
}

.ai-panel-card {
  background: rgba(255, 255, 255, 0.9);
}

.context-pill {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: #1d4ed8;
  font-weight: 600;
}

.ai-panel-block {
  display: grid;
  gap: 12px;
  padding-top: 18px;
  border-top: 1px solid rgba(148, 163, 184, 0.14);
}

.ai-focus-card {
  display: grid;
  gap: 8px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(255, 255, 255, 0.98));
  border: 1px solid rgba(37, 99, 235, 0.12);
}

.ai-focus-card strong {
  color: #0f172a;
  font-size: 18px;
}

.ai-focus-card p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
  font-size: 14px;
}

.ai-focus-state {
  display: inline-flex;
  width: fit-content;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.ai-focus-state--active {
  background: rgba(37, 99, 235, 0.12);
  color: #1d4ed8;
}

.ai-focus-state--filled {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.ai-focus-state--empty {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.context-preview-card {
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.context-preview-card p {
  margin: 0;
  color: #334155;
  line-height: 1.8;
  font-size: 14px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.14);
  color: #334155;
}

.insight-dot {
  width: 8px;
  height: 8px;
  margin-top: 7px;
  border-radius: 999px;
  background: #f59e0b;
  flex-shrink: 0;
}

.assistant-good-state {
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.12);
}

.assistant-good-state p {
  margin: 8px 0 0;
  color: #475569;
  line-height: 1.7;
  font-size: 14px;
}

.assistant-good-badge {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
  font-size: 11px;
  font-weight: 700;
}

.ai-action-grid--secondary :deep(.el-button) {
  background: rgba(248, 250, 252, 0.8);
}

.inline-item {
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(248, 250, 252, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.task-editor {
  padding: 16px;
  border-radius: 16px;
  background: rgba(248, 250, 252, 0.68);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.resource-editor {
  padding: 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.block-toolbar strong,
.mini-toolbar label {
  color: #0f172a;
}

:deep(.w-e-text-container),
:deep(.w-e-bar) {
  border-radius: 14px;
}

:deep(.el-input-number) {
  width: 100%;
}

@media (max-width: 1180px) {
  .editor-layout {
    grid-template-columns: 208px minmax(0, 1fr);
  }

  .editor-workbench {
    grid-template-columns: 1fr;
  }

  .editor-ai-panel {
    grid-column: 1 / -1;
    position: static;
  }
}

@media (max-width: 900px) {
  .report-editor-page {
    padding: 18px;
  }

  .editor-topbar,
  .section-head,
  .block-toolbar,
  .mini-toolbar,
  .editor-label-bar,
  .ai-panel-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .editor-layout {
    grid-template-columns: 1fr;
  }

  .editor-sidebar {
    position: static;
  }

  .editor-ai-panel {
    position: static;
  }

  .panel-grid--two {
    grid-template-columns: 1fr;
  }
}
</style>
