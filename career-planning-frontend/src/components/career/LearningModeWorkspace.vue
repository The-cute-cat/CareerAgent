<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { Calendar, DataAnalysis, Opportunity, Reading, Trophy } from '@element-plus/icons-vue'

import LearningGuideBanner from '@/components/career/LearningGuideBanner.vue'
import LearningModeFeaturePanel from '@/components/career/LearningModeFeaturePanel.vue'
import {
  completedCourseOptions,
  cyclePlanTemplates,
  foundationBaseScores,
  learningTrackOptions,
  practiceOptions,
  resourcePreferenceOptions,
  toolOptions,
  trackProjectSuggestions,
  trackResources,
  weakPointOptions,
  type LearningCycle,
  type LearningTrack,
} from '@/mock/mockdata/LearningMode_mockdata'

const props = withDefaults(
  defineProps<{
    activeStep?: string
  }>(),
  {
    activeStep: '1',
  },
)

const emit = defineEmits<{
  (e: 'update:activeStep', value: string): void
  (e: 'summary-change', value: {
    progress: number
    profileCompleteness: number
    completedSteps: string[]
    readinessText: string
    readinessHint: string
  }): void
}>()

const learningForm = reactive({
  targetTrack: 'frontend-ai' as LearningTrack,
  currentBackground: '软件工程大三，已有 Vue 项目基础',
  weeklyHours: '10-15 小时',
  stageGoal: '一周内完成学习模式功能闭环，能直接用于初赛视频录制',
  completedCourses: ['JavaScript/TypeScript', 'Vue 3'],
  tools: ['VS Code', 'Git / GitHub', 'ECharts'],
  weakPoints: ['项目表达不清晰', '工程化能力薄弱'],
  practiceExp: ['课程作业项目'],
  expectedOutput: '做一个带学习规划结果展示的智能工作台',
  habitStyle: '任务分块推进',
  reviewFrequency: '每周复盘一次',
  collaborationStyle: '愿意讲解并同步进度',
  growthCase: '在现有职业规划项目中新增学习模式，完善数据并优化功能链路。',
  cycle: '30' as LearningCycle,
  resourcePreferences: ['项目实战', '视频课程'],
})

const selectedTrack = computed(() => {
  const track = learningTrackOptions.find(item => item.value === learningForm.targetTrack)
  if (track) return track
  // 边界保护：确保数组非空且有默认值
  return learningTrackOptions[0] ?? {
    value: 'frontend-ai',
    label: '前端 + AI',
    target: '前端 + AI 应用',
    milestone: '掌握基础',
    output: '可演示作品',
    desc: '前端与AI结合',
    focus: ['前端', 'AI'],
  }
})

const stepCompletedMap = computed<Record<string, boolean>>(() => ({
  '1': Boolean(learningForm.targetTrack && learningForm.currentBackground && learningForm.weeklyHours && learningForm.stageGoal),
  '2': learningForm.completedCourses.length >= 2 && learningForm.tools.length >= 2 && learningForm.weakPoints.length > 0,
  '3': learningForm.practiceExp.length > 0 && Boolean(learningForm.expectedOutput),
  '4': Boolean(learningForm.habitStyle && learningForm.reviewFrequency && learningForm.collaborationStyle && learningForm.growthCase),
  '5': Boolean(learningForm.cycle && learningForm.resourcePreferences.length > 0),
}))

const completedSteps = computed(() => {
  return Object.entries(stepCompletedMap.value)
    .filter(([, done]) => done)
    .map(([step]) => step)
})

const formProgress = computed(() => Math.round((completedSteps.value.length / 5) * 100))

const profileCompleteness = computed(() => {
  const total = 14
  let done = 0

  if (learningForm.targetTrack) done += 1
  if (learningForm.currentBackground) done += 1
  if (learningForm.weeklyHours) done += 1
  if (learningForm.stageGoal) done += 1
  if (learningForm.completedCourses.length) done += 2
  if (learningForm.tools.length) done += 1
  if (learningForm.weakPoints.length) done += 1
  if (learningForm.practiceExp.length) done += 1
  if (learningForm.expectedOutput) done += 1
  if (learningForm.habitStyle) done += 1
  if (learningForm.reviewFrequency) done += 1
  if (learningForm.collaborationStyle) done += 1
  if (learningForm.growthCase) done += 1
  if (learningForm.resourcePreferences.length) done += 1

  return Math.round((done / total) * 100)
})

const readinessText = computed(() => {
  if (profileCompleteness.value >= 80) return '功能完成度高'
  if (profileCompleteness.value >= 50) return '主要功能已成型'
  return '还需要完善'
})

const readinessHint = computed(() => {
  if (profileCompleteness.value >= 80) return '已经适合直接录制初赛视频，重点再打磨讲解顺序。'
  if (profileCompleteness.value >= 50) return '学习模式主流程已具备，补齐结果页会更有说服力。'
  return '先把方向、项目沉淀和阶段计划三块补齐，展示效果会明显提升。'
})

const foundationScores = computed(() => {
  const scores = foundationBaseScores[learningForm.targetTrack].map(item => ({ ...item }))
  const courseBoost = Math.min(learningForm.completedCourses.length * 3, 12)
  const toolBoost = Math.min(learningForm.tools.length * 2, 8)
  const weaknessPenalty = Math.min(learningForm.weakPoints.length * 2, 8)

  return scores.map((item, index) => ({
    ...item,
    score: Math.max(
      45,
      Math.min(
        98,
        item.score + courseBoost + (index < 2 ? toolBoost : 0) - (index === scores.length - 1 ? weaknessPenalty : 0),
      ),
    ),
  }))
})

const projectSuggestions = computed(() => trackProjectSuggestions[learningForm.targetTrack])
const stagePlans = computed(() => cyclePlanTemplates[learningForm.cycle][learningForm.targetTrack])
const resourceList = computed(() => trackResources[learningForm.targetTrack])

const growthTags = computed(() => {
  return [
    learningForm.habitStyle || '需要建立固定节奏',
    learningForm.reviewFrequency || '需要补复盘习惯',
    learningForm.collaborationStyle || '建议多做表达训练',
  ]
})

const focusConclusion = computed(() => {
  if (learningForm.targetTrack === 'frontend-ai') {
    return '优先把学习模式做成一个能录屏展示的产品功能，而不是继续扩张页面范围。'
  }
  if (learningForm.targetTrack === 'data-analysis') {
    return '优先做“学习画像 + 薄弱点分析 + 阶段建议”三段式结果表达。'
  }
  return '优先把双模式的产品逻辑和用户场景讲清楚，再扩展页面细节。'
})

const stepPreviewTitle = computed(() => {
  const map: Record<string, string> = {
    '1': '方向推荐结果',
    '2': '基础盘点结果',
    '3': '项目沉淀建议',
    '4': '成长潜力判断',
    '5': '阶段学习计划',
  }
  return map[props.activeStep] || '学习模式预览'
})

const canGoPrev = computed(() => Number(props.activeStep) > 1)
const canGoNext = computed(() => Number(props.activeStep) < 5)

const switchStep = (step: number) => {
  // 边界检查：确保步骤在有效范围内
  if (step < 1 || step > 5) return

  // 如果要跳转到后面的步骤，检查前置步骤是否完成
  const currentStep = Number(props.activeStep)
  if (step > currentStep) {
    // 检查从当前步骤到目标步骤之间的所有步骤是否完成
    for (let i = currentStep; i < step; i++) {
      if (!stepCompletedMap.value[String(i)]) {
        // 不能跳过未完成的步骤
        return
      }
    }
  }

  emit('update:activeStep', String(step))
}

const goPrev = () => {
  if (!canGoPrev.value) return
  switchStep(Number(props.activeStep) - 1)
}

const goNext = () => {
  if (!canGoNext.value) return
  // 检查当前步骤是否完成
  const currentStep = props.activeStep
  if (!stepCompletedMap.value[currentStep]) {
    // 当前步骤未完成，不能进入下一步
    return
  }
  switchStep(Number(props.activeStep) + 1)
}

// 性能优化：使用单个对象监听，减少触发次数
const summaryData = computed(() => ({
  progress: formProgress.value,
  profileCompleteness: profileCompleteness.value,
  completedSteps: completedSteps.value,
  readinessText: readinessText.value,
  readinessHint: readinessHint.value,
}))

watch(
  summaryData,
  (newVal) => {
    emit('summary-change', newVal)
  },
  { immediate: true, deep: true },
)
</script>

<template>
  <div class="learning-workspace">
    <section class="learning-hero">
      <div>
        <p class="workspace-kicker">Learning Mode</p>
        <h2>学习模式工作台</h2>
        <p class="workspace-summary">
          独立于就业模式的 mock 展示链路，专门用于表现“学习方向定位、能力盘点、项目沉淀、成长评估、阶段规划”。
        </p>
      </div>
      <div class="hero-metrics">
        <article class="metric-card">
          <span>当前主攻方向</span>
          <strong>{{ selectedTrack.label }}</strong>
          <p>{{ selectedTrack.desc }}</p>
        </article>
        <article class="metric-card">
          <span>功能完成度</span>
          <strong>{{ formProgress }}%</strong>
          <p>{{ readinessHint }}</p>
        </article>
      </div>
    </section>

    <div class="workspace-banner-stack">
      <LearningGuideBanner />
      <LearningModeFeaturePanel :active-step="activeStep" />
    </div>

    <section class="workspace-snapshot">
      <article class="snapshot-card">
        <el-icon><Reading /></el-icon>
        <div>
          <span>推荐方向</span>
          <strong>{{ selectedTrack.target }}</strong>
        </div>
      </article>
      <article class="snapshot-card">
        <el-icon><DataAnalysis /></el-icon>
        <div>
          <span>当前里程碑</span>
          <strong>{{ selectedTrack.milestone }}</strong>
        </div>
      </article>
      <article class="snapshot-card">
        <el-icon><Trophy /></el-icon>
        <div>
          <span>阶段输出</span>
          <strong>{{ selectedTrack.output }}</strong>
        </div>
      </article>
      <article class="snapshot-card">
        <el-icon><Calendar /></el-icon>
        <div>
          <span>规划周期</span>
          <strong>{{ learningForm.cycle }} 天</strong>
        </div>
      </article>
    </section>

    <div class="workspace-layout">
      <section class="workspace-panel workspace-panel--form">
        <div class="panel-head">
          <div>
            <p class="panel-kicker">Learning Input</p>
            <h3>学习模式独立表单</h3>
          </div>
          <div class="step-actions">
            <el-button plain :disabled="!canGoPrev" @click="goPrev">上一步</el-button>
            <el-button type="primary" :disabled="!canGoNext" @click="goNext">下一步</el-button>
          </div>
        </div>

        <el-form label-position="top" class="learning-form">
          <template v-if="activeStep === '1'">
            <div class="form-section-title">学习方向定位</div>
            <el-form-item label="主攻学习方向">
              <el-radio-group v-model="learningForm.targetTrack" class="track-radio-group">
                <el-radio-button
                  v-for="item in learningTrackOptions"
                  :key="item.value"
                  :label="item.value"
                >
                  {{ item.label }}
                </el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="当前背景">
              <el-input
                v-model="learningForm.currentBackground"
                type="textarea"
                :rows="3"
                maxlength="500"
                show-word-limit
                placeholder="例如：软件工程大三，做过 2 个 Vue 课程项目，比赛时间只剩一周。"
              />
            </el-form-item>

            <div class="form-grid">
              <el-form-item label="每周可投入时间">
                <el-select v-model="learningForm.weeklyHours" placeholder="请选择">
                  <el-option label="5 小时以内" value="5 小时以内" />
                  <el-option label="5-10 小时" value="5-10 小时" />
                  <el-option label="10-15 小时" value="10-15 小时" />
                  <el-option label="15 小时以上" value="15 小时以上" />
                </el-select>
              </el-form-item>

              <el-form-item label="阶段目标">
                <el-input v-model="learningForm.stageGoal" maxlength="200" show-word-limit placeholder="例如：做完可录屏展示的学习模式作品" />
              </el-form-item>
            </div>
          </template>

          <template v-else-if="activeStep === '2'">
            <div class="form-section-title">学习基础盘点</div>
            <el-form-item label="已掌握课程/知识模块">
              <el-checkbox-group v-model="learningForm.completedCourses" class="check-grid">
                <el-checkbox v-for="item in completedCourseOptions" :key="item" :label="item">{{ item }}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="熟悉工具">
              <el-checkbox-group v-model="learningForm.tools" class="check-grid">
                <el-checkbox v-for="item in toolOptions" :key="item" :label="item">{{ item }}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="当前短板">
              <el-checkbox-group v-model="learningForm.weakPoints" class="check-grid">
                <el-checkbox v-for="item in weakPointOptions" :key="item" :label="item">{{ item }}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </template>

          <template v-else-if="activeStep === '3'">
            <div class="form-section-title">项目实战沉淀</div>
            <el-form-item label="已有实践经历">
              <el-checkbox-group v-model="learningForm.practiceExp" class="check-grid">
                <el-checkbox v-for="item in practiceOptions" :key="item" :label="item">{{ item }}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="希望最终做出的作品">
              <el-input
                v-model="learningForm.expectedOutput"
                type="textarea"
                :rows="3"
                maxlength="500"
                show-word-limit
                placeholder="例如：把现有职业规划系统做成学习/就业双模式展示作品。"
              />
            </el-form-item>
          </template>

          <template v-else-if="activeStep === '4'">
            <div class="form-section-title">成长潜力评估</div>
            <div class="form-grid">
              <el-form-item label="学习习惯">
                <el-select v-model="learningForm.habitStyle" placeholder="请选择">
                  <el-option label="任务分块推进" value="任务分块推进" />
                  <el-option label="先看资料再集中实现" value="先看资料再集中实现" />
                  <el-option label="边做边学" value="边做边学" />
                </el-select>
              </el-form-item>

              <el-form-item label="复盘频率">
                <el-select v-model="learningForm.reviewFrequency" placeholder="请选择">
                  <el-option label="每天简单复盘" value="每天简单复盘" />
                  <el-option label="每周复盘一次" value="每周复盘一次" />
                  <el-option label="很少系统复盘" value="很少系统复盘" />
                </el-select>
              </el-form-item>
            </div>

            <div class="form-grid">
              <el-form-item label="协作/表达风格">
                <el-select v-model="learningForm.collaborationStyle" placeholder="请选择">
                  <el-option label="愿意讲解并同步进度" value="愿意讲解并同步进度" />
                  <el-option label="更擅长独立推进" value="更擅长独立推进" />
                  <el-option label="需要他人推动才会加速" value="需要他人推动才会加速" />
                </el-select>
              </el-form-item>

              <el-form-item label="成长案例">
                <el-input v-model="learningForm.growthCase" maxlength="300" show-word-limit placeholder="填写一个最近的学习突破或项目优化案例" />
              </el-form-item>
            </div>
          </template>

          <template v-else>
            <div class="form-section-title">阶段学习规划</div>
            <div class="form-grid">
              <el-form-item label="规划周期">
                <el-radio-group v-model="learningForm.cycle">
                  <el-radio-button label="7">7 天</el-radio-button>
                  <el-radio-button label="30">30 天</el-radio-button>
                  <el-radio-button label="90">90 天</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="资源偏好">
                <el-checkbox-group v-model="learningForm.resourcePreferences" class="check-grid">
                  <el-checkbox
                    v-for="item in resourcePreferenceOptions"
                    :key="item"
                    :label="item"
                  >
                    {{ item }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </div>
          </template>
        </el-form>
      </section>

      <aside class="workspace-panel workspace-panel--preview">
        <div class="panel-head panel-head--preview">
          <div>
            <p class="panel-kicker">Mock Output</p>
            <h3>{{ stepPreviewTitle }}</h3>
          </div>
          <el-tag type="success" effect="light">本地预览</el-tag>
        </div>

        <div class="preview-top-card">
          <span>系统结论</span>
          <strong>{{ focusConclusion }}</strong>
          <p>{{ readinessHint }}</p>
        </div>

        <template v-if="activeStep === '1'">
          <div class="preview-card">
            <span class="preview-label">推荐主攻方向</span>
            <strong>{{ selectedTrack.label }}</strong>
            <p>{{ selectedTrack.target }}</p>
          </div>
          <div class="tag-list">
            <span v-for="item in selectedTrack.focus" :key="item" class="tag-chip">{{ item }}</span>
          </div>
        </template>

        <template v-else-if="activeStep === '2'">
          <div class="score-stack">
            <div v-for="item in foundationScores" :key="item.label" class="score-item">
              <div class="score-top">
                <span>{{ item.label }}</span>
                <strong>{{ item.score }}</strong>
              </div>
              <el-progress :percentage="item.score" :show-text="false" :stroke-width="10" />
            </div>
          </div>
          <div class="tag-list">
            <span v-for="item in learningForm.weakPoints" :key="item" class="tag-chip tag-chip--warn">{{ item }}</span>
          </div>
        </template>

        <template v-else-if="activeStep === '3'">
          <div class="suggestion-list">
            <article v-for="item in projectSuggestions" :key="item.title" class="suggestion-card">
              <div class="suggestion-head">
                <strong>{{ item.title }}</strong>
                <span>{{ item.level }}</span>
              </div>
              <p>{{ item.highlight }}</p>
              <div class="suggestion-meta">{{ item.duration }}</div>
              <div class="tag-list">
                <span v-for="deliverable in item.deliverables" :key="deliverable" class="tag-chip">
                  {{ deliverable }}
                </span>
              </div>
            </article>
          </div>
        </template>

        <template v-else-if="activeStep === '4'">
          <div class="preview-card preview-card--accent">
            <span class="preview-label">成长潜力标签</span>
            <strong>执行力可塑，适合以作品驱动学习</strong>
            <p>建议继续保持“边做边讲”的节奏，把每个阶段成果都转成可展示内容。</p>
          </div>
          <div class="tag-list">
            <span v-for="item in growthTags" :key="item" class="tag-chip">{{ item }}</span>
          </div>
        </template>

        <template v-else>
          <div class="plan-list">
            <article v-for="item in stagePlans" :key="item.label" class="plan-card">
              <span>{{ item.label }}</span>
              <strong>{{ item.goal }}</strong>
              <ul>
                <li v-for="task in item.tasks" :key="task">{{ task }}</li>
              </ul>
            </article>
          </div>
          <div class="resource-card">
            <div class="resource-head">
              <el-icon><Opportunity /></el-icon>
              <strong>资源推荐</strong>
            </div>
            <div class="tag-list">
              <span v-for="item in resourceList" :key="item" class="tag-chip">{{ item }}</span>
            </div>
          </div>
        </template>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.learning-workspace {
  display: grid;
  gap: 20px;
}

.learning-hero,
.workspace-panel,
.snapshot-card {
  border-radius: 24px;
  border: 1px solid rgba(153, 246, 228, 0.85);
  background: linear-gradient(180deg, rgba(240, 253, 250, 0.98) 0%, #ffffff 100%);
  box-shadow: 0 14px 36px rgba(15, 118, 110, 0.08);
}

.learning-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(340px, 0.8fr);
  gap: 18px;
  padding: 24px;
}

.workspace-kicker,
.panel-kicker {
  margin: 0 0 6px;
  color: #0f766e;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.learning-hero h2,
.panel-head h3 {
  margin: 0;
  color: #134e4a;
  font-size: 24px;
}

.workspace-summary {
  margin: 10px 0 0;
  color: #4b5563;
  line-height: 1.8;
}

.hero-metrics,
.workspace-banner-stack,
.workspace-snapshot,
.workspace-layout,
.learning-form,
.score-stack,
.suggestion-list,
.plan-list {
  display: grid;
  gap: 16px;
}

.hero-metrics {
  grid-template-columns: 1fr;
}

.metric-card,
.preview-top-card,
.preview-card,
.suggestion-card,
.plan-card,
.resource-card {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(153, 246, 228, 0.65);
  background: rgba(255, 255, 255, 0.92);
}

.metric-card span,
.preview-label,
.plan-card span {
  display: block;
  margin-bottom: 8px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
}

.metric-card strong,
.preview-card strong,
.preview-top-card strong,
.plan-card strong {
  display: block;
  margin-bottom: 8px;
  color: #134e4a;
  font-size: 16px;
}

.metric-card p,
.preview-card p,
.preview-top-card p,
.suggestion-card p {
  margin: 0;
  color: #4b5563;
  line-height: 1.75;
  font-size: 13px;
}

.workspace-snapshot {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.snapshot-card {
  display: flex;
  gap: 14px;
  padding: 18px;
  align-items: center;
}

.snapshot-card .el-icon {
  display: inline-flex;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  align-items: center;
  justify-content: center;
  background: rgba(20, 184, 166, 0.12);
  color: #0f766e;
  font-size: 18px;
}

.snapshot-card span {
  display: block;
  color: #6b7280;
  font-size: 12px;
}

.snapshot-card strong {
  color: #134e4a;
  font-size: 15px;
}

.workspace-layout {
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  align-items: start;
}

.workspace-panel {
  padding: 22px;
}

.workspace-panel--preview {
  position: sticky;
  top: 12px;
}

.panel-head,
.step-actions,
.score-top,
.suggestion-head,
.resource-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-head {
  margin-bottom: 18px;
}

.panel-head--preview {
  align-items: flex-start;
}

.form-section-title {
  margin-bottom: 4px;
  color: #134e4a;
  font-size: 18px;
  font-weight: 700;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.track-radio-group,
.check-grid,
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.check-grid :deep(.el-checkbox) {
  margin-right: 0;
}

.preview-top-card {
  margin-bottom: 16px;
}

.preview-card--accent {
  background: linear-gradient(180deg, #f0fdfa 0%, #ffffff 100%);
}

.score-item,
.suggestion-card,
.plan-card {
  display: grid;
  gap: 10px;
}

.score-top span,
.suggestion-meta {
  color: #6b7280;
  font-size: 13px;
}

.score-top strong,
.suggestion-head strong {
  color: #134e4a;
}

.suggestion-head span {
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
}

.tag-chip {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(20, 184, 166, 0.1);
  color: #0f766e;
  font-size: 12px;
  font-weight: 600;
}

.tag-chip--warn {
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
}

.plan-card ul {
  margin: 0;
  padding-left: 18px;
  color: #4b5563;
  line-height: 1.8;
  font-size: 13px;
}

.resource-head {
  justify-content: flex-start;
  margin-bottom: 12px;
  color: #134e4a;
}

@media (max-width: 1280px) {
  .workspace-snapshot,
  .workspace-layout,
  .learning-hero {
    grid-template-columns: 1fr;
  }

  .workspace-panel--preview {
    position: static;
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .panel-head,
  .step-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .snapshot-card {
    align-items: flex-start;
  }
}
</style>
