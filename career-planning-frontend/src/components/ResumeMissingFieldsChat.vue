<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ChatDotRound, UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { CareerFormData } from '@/types/careerform_report'
import type { Option } from '@/mock/mockdata/CareerForm_mockdata'

interface MissingFieldItem {
  field: string
  label: string
  step: string
  optional?: boolean
}

interface SavePayload {
  field: string
  value: unknown
}

interface QuizStatus {
  communication: boolean
  stress: boolean
  learning: boolean
}

interface Props {
  modelValue: boolean
  fields: MissingFieldItem[]
  formData: CareerFormData
  majorOptions: Option[]
  quizStatus: QuizStatus
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  save: [payload: SavePayload]
  complete: []
  'step-change': [step: string]
  'open-quiz': [type: 'communication' | 'stress' | 'learning']
  'evaluate-code-ability': [payload: { links: string; useAi: boolean }]
}>()

const currentIndex = ref(0)

const educationValue = ref('')
const majorValue = ref<string[]>([])
const graduationDateValue = ref('')
const languageTypeValue = ref('')
const languageLevelValue = ref('')
const skillInput = ref('')
const skillsValue = ref<string[]>([])
const industryInput = ref('')
const industryValues = ref<string[]>([])
const targetJobValue = ref('')
const codeAbilityLinksValue = ref('')
const codeAbilityUseAiValue = ref(false)
const completedAnswers = ref<Record<string, string>>({})

const educationOptions = ['高中', '大专', '本科', '硕士', '博士', '其他']
const languageTypeOptions = ['英语', '日语', '韩语', '法语', '德语', '其他']
const languageLevelOptions = ['CET-4', 'CET-6', '雅思', '托福', '专业四级', '专业八级', '其他']

const currentField = computed(() => props.fields[currentIndex.value] ?? null)
const progressText = computed(() => `${Math.min(currentIndex.value + 1, props.fields.length)}/${props.fields.length || 1}`)

const assistantPromptMap: Record<string, string> = {
  education: '我先帮你把学历补完整，当前最高学历是什么？',
  major: '接着补专业信息，你学的是什么专业？',
  graduationDate: '再补一下预计毕业时间，选择毕业年月就可以。',
  languages: '简历里还缺外语能力，告诉我语种和水平吧。',
  skills: '还差专业技能。可以输入多个技能，我会帮你逐个记录。',
  targetJob: '你的目标岗位是什么？先写一个最想投递的岗位即可。',
  targetIndustries: '最后补一下期望行业，可以填多个。',
  qualityAssessment: '素质测评暂时还没完成。下面 3 个测试可以帮助系统更准确理解你的沟通、抗压和学习能力。',
  codeAbility: '如果你愿意，我们还可以补充代码仓库并做一次代码能力评估。这一项是可选的，填写后我会帮你直接发起测试。'
}

const quizGuideCards = computed(() => [
  {
    key: 'communication' as const,
    title: '沟通能力测评',
    description: '先做这个，系统会结合你的表达方式、协作偏好和反馈习惯，判断你更适合什么样的团队协作场景。',
    done: props.quizStatus.communication,
    buttonType: props.quizStatus.communication ? 'success' : 'primary'
  },
  {
    key: 'stress' as const,
    title: '抗压能力测评',
    description: '这部分会帮助系统识别你面对压力、截止时间和复杂任务时的应对方式，完善你的工作节奏画像。',
    done: props.quizStatus.stress,
    buttonType: props.quizStatus.stress ? 'success' : 'warning'
  },
  {
    key: 'learning' as const,
    title: '学习能力测评',
    description: '这一项会用来评估你的学习驱动力、知识吸收方式和成长潜力，让推荐岗位更贴近你的发展空间。',
    done: props.quizStatus.learning,
    buttonType: props.quizStatus.learning ? 'success' : 'info'
  }
])

const assistantPrompt = computed(() => {
  if (!currentField.value) {
    return '必填信息已经补充完成。'
  }

  return assistantPromptMap[currentField.value.field] || `请补充${currentField.value.label}。`
})

const closeDialog = () => {
  emit('update:modelValue', false)
}

const normalizeTagValue = (value: string) => value.trim()
const getCodeAbilityUrls = (rawLinks: string) => rawLinks
  .split(/[\n,，]/)
  .map(item => item.trim())
  .filter(Boolean)
const isValidCodeProfileUrl = (url: string) => /^https?:\/\/(www\.)?(github\.com|gitee\.com)\/[^/]+\/?$/i.test(url)

const syncDraftFromForm = () => {
  const field = currentField.value?.field
  if (!field) return

  switch (field) {
    case 'education':
      educationValue.value = props.formData.education ? String(props.formData.education) : ''
      break
    case 'major':
      majorValue.value = Array.isArray(props.formData.major) ? [...props.formData.major] : []
      break
    case 'graduationDate':
      graduationDateValue.value = props.formData.graduationDate || ''
      break
    case 'languages': {
      const firstValidLanguage = props.formData.languages.find((item) => item.type || item.level)
      languageTypeValue.value = firstValidLanguage?.type || ''
      languageLevelValue.value = firstValidLanguage?.level || ''
      break
    }
    case 'skills':
      skillsValue.value = props.formData.skills.map((item) => item.name).filter(Boolean)
      skillInput.value = ''
      break
    case 'targetJob':
      targetJobValue.value = props.formData.targetJob || ''
      break
    case 'targetIndustries':
      industryValues.value = [...props.formData.targetIndustries]
      industryInput.value = ''
      break
    case 'codeAbility':
      codeAbilityLinksValue.value = props.formData.codeAbility?.links || ''
      codeAbilityUseAiValue.value = false
      break
    case 'qualityAssessment':
      break
  }
}

const resetConversation = () => {
  currentIndex.value = 0
  completedAnswers.value = {}
  syncDraftFromForm()
}

watch(() => props.modelValue, (visible) => {
  if (visible) {
    resetConversation()
    if (currentField.value) {
      emit('step-change', currentField.value.step)
    }
  }
})

watch(currentField, (field) => {
  syncDraftFromForm()
  if (props.modelValue && field) {
    emit('step-change', field.step)
  }
})

const addSkillTag = () => {
  const value = normalizeTagValue(skillInput.value)
  if (!value || skillsValue.value.includes(value)) return
  skillsValue.value.push(value)
  skillInput.value = ''
}

const removeSkillTag = (index: number) => {
  skillsValue.value.splice(index, 1)
}

const addIndustryTag = () => {
  const value = normalizeTagValue(industryInput.value)
  if (!value || industryValues.value.includes(value)) return
  industryValues.value.push(value)
  industryInput.value = ''
}

const removeIndustryTag = (index: number) => {
  industryValues.value.splice(index, 1)
}

const getFieldAnswer = (field: MissingFieldItem) => {
  switch (field.field) {
    case 'education':
      return educationValue.value || '待填写'
    case 'major':
      return majorValue.value.join(' / ') || '待填写'
    case 'graduationDate':
      return graduationDateValue.value || '待填写'
    case 'languages':
      return [languageTypeValue.value, languageLevelValue.value].filter(Boolean).join(' / ') || '待填写'
    case 'skills':
      return skillsValue.value.join('、') || '待填写'
    case 'targetJob':
      return targetJobValue.value || '待填写'
    case 'targetIndustries':
      return industryValues.value.join('、') || '待填写'
    case 'codeAbility':
      return codeAbilityLinksValue.value.trim()
        ? `${codeAbilityUseAiValue.value ? '已开启深度分析' : '基础评估'}：${codeAbilityLinksValue.value.trim()}`
        : '已跳过'
    case 'qualityAssessment': {
      const finished: string[] = []
      if (props.quizStatus.communication) finished.push('沟通能力')
      if (props.quizStatus.stress) finished.push('抗压能力')
      if (props.quizStatus.learning) finished.push('学习能力')
      return finished.length ? `已完成：${finished.join('、')}` : '待填写'
    }
    default:
      return '待填写'
  }
}

const conversationHistory = computed(() => {
  return props.fields.slice(0, currentIndex.value).map((field) => ({
    label: field.label,
    prompt: assistantPromptMap[field.field] || `请补充${field.label}。`,
    answer: completedAnswers.value[field.field] || '待填写'
  }))
})

const validateCurrentField = () => {
  const field = currentField.value?.field
  if (!field) return { valid: false, message: '当前没有可填写的字段' }

  switch (field) {
    case 'education':
      return {
        valid: !!educationValue.value,
        message: '请选择学历',
        value: educationValue.value
      }
    case 'major':
      return {
        valid: Array.isArray(majorValue.value) && majorValue.value.length > 0,
        message: '请选择专业',
        value: majorValue.value
      }
    case 'graduationDate':
      return {
        valid: !!graduationDateValue.value,
        message: '请选择预计毕业日期',
        value: graduationDateValue.value
      }
    case 'languages':
      return {
        valid: !!languageTypeValue.value && !!languageLevelValue.value,
        message: '请补充语种和水平',
        value: [{ type: languageTypeValue.value, level: languageLevelValue.value, other: '' }]
      }
    case 'skills':
      return {
        valid: skillsValue.value.length > 0,
        message: '请至少添加一项技能',
        value: skillsValue.value.map((name) => ({ name, score: 50 }))
      }
    case 'targetJob':
      return {
        valid: !!targetJobValue.value.trim(),
        message: '请输入目标岗位',
        value: targetJobValue.value.trim()
      }
    case 'targetIndustries':
      return {
        valid: industryValues.value.length > 0,
        message: '请至少添加一个期望行业',
        value: industryValues.value
      }
    case 'codeAbility':
      return {
        valid: !!codeAbilityLinksValue.value.trim(),
        message: '请输入至少一个 GitHub 或 Gitee 用户主页链接，如 https://github.com/username',
        value: {
          links: codeAbilityLinksValue.value.trim(),
          useAi: codeAbilityUseAiValue.value
        }
      }
    case 'qualityAssessment':
      return {
        valid: props.quizStatus.communication && props.quizStatus.stress && props.quizStatus.learning,
        message: '请先完成全部素质测评',
        value: null
      }
    default:
      return { valid: false, message: '暂不支持该字段' }
  }
}

const submitCurrentField = () => {
  const result = validateCurrentField()
  if (!currentField.value || !result.valid) return

  if (currentField.value.field === 'codeAbility') {
    const payload = result.value as { links: string; useAi: boolean }
    const invalidUrl = getCodeAbilityUrls(payload.links).find(url => !isValidCodeProfileUrl(url))
    if (invalidUrl) {
      ElMessage.warning(`链接格式不正确，仅支持主页链接如 https://github.com/username：${invalidUrl}`)
      return
    }
  }

  if (currentField.value.field !== 'qualityAssessment') {
    emit('save', {
      field: currentField.value.field,
      value: result.value
    })
  }

  if (currentField.value.field === 'codeAbility' && result.value) {
    const payload = result.value as { links: string; useAi: boolean }
    emit('evaluate-code-ability', payload)
  }

  completedAnswers.value[currentField.value.field] = getFieldAnswer(currentField.value)

  const isLast = currentIndex.value >= props.fields.length - 1
  if (isLast) {
    emit('complete')
    closeDialog()
    return
  }

  currentIndex.value += 1
}

const skipCurrentField = () => {
  if (!currentField.value?.optional) return

  completedAnswers.value[currentField.value.field] = '已跳过'

  const isLast = currentIndex.value >= props.fields.length - 1
  if (isLast) {
    emit('complete')
    closeDialog()
    return
  }

  currentIndex.value += 1
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    width="1100px"
    top="4vh"
    destroy-on-close
    class="resume-missing-fields-chat"
    @close="closeDialog"
  >
    <template #header>
      <div class="dialog-header">
        <div>
          <div class="dialog-title">补全简历关键信息</div>
          <div class="dialog-subtitle">AI 已帮你识别大部分内容，剩下这 {{ fields.length }} 项我们一起补完。</div>
        </div>
        <el-tag type="primary" effect="light" round>进度 {{ progressText }}</el-tag>
      </div>
    </template>

    <div class="chat-shell">
      <div class="chat-history">
        <div class="panel-label">对话引导</div>
        <template v-for="item in conversationHistory" :key="item.label">
          <div class="bubble-row assistant history-row">
            <div class="bubble-avatar assistant-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="bubble assistant-bubble history-bubble">
              <div class="bubble-title">简历助手</div>
              <p>{{ item.prompt }}</p>
            </div>
          </div>

          <div class="bubble-row user history-row">
            <div class="bubble user-bubble">
              <div class="bubble-title">你</div>
              <p>{{ item.answer }}</p>
            </div>
            <div class="bubble-avatar user-avatar">
              <el-icon><UserFilled /></el-icon>
            </div>
          </div>
        </template>

        <div class="bubble-row assistant">
          <div class="bubble-avatar assistant-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="bubble assistant-bubble">
            <div class="bubble-title">简历助手</div>
            <p>{{ assistantPrompt }}</p>
          </div>
        </div>
      </div>

      <div class="composer-card">
        <div class="panel-label">当前填写</div>
        <div class="composer-title-row">
          <div class="composer-title">{{ currentField?.label }}</div>
          <el-tag v-if="currentField?.optional" type="info" effect="light" round>可选</el-tag>
        </div>

        <div v-if="currentField?.field === 'education'" class="composer-body">
          <el-select v-model="educationValue" placeholder="请选择学历" size="large">
            <el-option
              v-for="item in educationOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </div>

        <div v-else-if="currentField?.field === 'major'" class="composer-body">
          <el-cascader
            v-model="majorValue"
            :options="majorOptions"
            placeholder="请选择专业"
            size="large"
            style="width: 100%"
          />
        </div>

        <div v-else-if="currentField?.field === 'graduationDate'" class="composer-body">
          <el-date-picker
            v-model="graduationDateValue"
            type="month"
            value-format="YYYY-MM"
            format="YYYY-MM"
            placeholder="请选择毕业年月"
            size="large"
            style="width: 100%"
          />
        </div>

        <div v-else-if="currentField?.field === 'languages'" class="composer-body two-col">
          <el-select v-model="languageTypeValue" placeholder="语种" size="large">
            <el-option
              v-for="item in languageTypeOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
          <el-select v-model="languageLevelValue" placeholder="水平" size="large">
            <el-option
              v-for="item in languageLevelOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </div>

        <div v-else-if="currentField?.field === 'skills'" class="composer-body">
          <div class="tag-editor">
            <div class="tag-input-row">
              <el-input
                v-model="skillInput"
                placeholder="输入技能后按回车或点击添加"
                size="large"
                @keyup.enter="addSkillTag"
              />
              <el-button type="primary" @click="addSkillTag">添加</el-button>
            </div>

            <div v-if="skillsValue.length" class="tag-list">
              <el-tag
                v-for="(skill, index) in skillsValue"
                :key="`${skill}-${index}`"
                closable
                size="large"
                @close="removeSkillTag(index)"
              >
                {{ skill }}
              </el-tag>
            </div>
          </div>
        </div>

        <div v-else-if="currentField?.field === 'targetJob'" class="composer-body">
          <el-input
            v-model="targetJobValue"
            placeholder="例如：后端工程师 / 产品经理"
            size="large"
          />
        </div>

        <div v-else-if="currentField?.field === 'targetIndustries'" class="composer-body">
          <div class="tag-editor">
            <div class="tag-input-row">
              <el-input
                v-model="industryInput"
                placeholder="输入行业后按回车或点击添加"
                size="large"
                @keyup.enter="addIndustryTag"
              />
              <el-button type="primary" @click="addIndustryTag">添加</el-button>
            </div>

            <div v-if="industryValues.length" class="tag-list">
              <el-tag
                v-for="(industry, index) in industryValues"
                :key="`${industry}-${index}`"
                closable
                size="large"
                type="success"
                @close="removeIndustryTag(index)"
              >
                {{ industry }}
              </el-tag>
            </div>
          </div>
        </div>

        <div v-else-if="currentField?.field === 'codeAbility'" class="composer-body">
          <div class="code-ability-guide">
            <p class="code-ability-guide-text">
              支持填写 GitHub / Gitee 用户主页链接，如 https://github.com/username，多个链接可用换行、英文逗号或中文逗号分隔。提交后会直接打开评估结果。
            </p>
            <el-input
              v-model="codeAbilityLinksValue"
              type="textarea"
              :rows="5"
              resize="none"
              placeholder="例如：https://github.com/user/repo"
            />
            <div class="code-ability-toggle">
              <div>
                <div class="code-ability-toggle-title">AI 深度分析</div>
                <div class="code-ability-toggle-desc">开启后会额外返回 summary、strengths、weaknesses 等内容</div>
              </div>
              <el-switch v-model="codeAbilityUseAiValue" />
            </div>
          </div>
        </div>

        <div v-else-if="currentField?.field === 'qualityAssessment'" class="composer-body">
          <div class="quiz-guide">
            <p class="quiz-guide-text">
              这部分不需要手动输入。完成下方测评后，系统会自动记录结果，并用来完善你的职业画像。
            </p>
            <div class="quiz-action-list">
              <div
                v-for="item in quizGuideCards"
                :key="item.key"
                class="quiz-action-card"
              >
                <div class="quiz-action-content">
                  <div class="quiz-action-title-row">
                    <span class="quiz-action-title">{{ item.title }}</span>
                    <el-tag v-if="item.done" type="success" effect="light" round>已完成</el-tag>
                  </div>
                  <p class="quiz-action-desc">{{ item.description }}</p>
                </div>
                <el-button
                  size="large"
                  :type="item.buttonType"
                  class="quiz-action-btn"
                  @click="emit('open-quiz', item.key)"
                >
                  {{ item.done ? '重新查看测评' : `开始${item.title}` }}
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <div class="composer-footer">
          <div class="composer-hint">
            当前字段会立即回写到表单，你也可以稍后回到表单继续修改。
          </div>
          <div class="composer-actions">
            <el-button @click="closeDialog">稍后填写</el-button>
            <el-button v-if="currentField?.optional" @click="skipCurrentField">跳过此项</el-button>
            <el-button type="primary" @click="submitCurrentField" :disabled="currentField?.field === 'qualityAssessment' && !(quizStatus.communication && quizStatus.stress && quizStatus.learning)">
              {{ currentField?.field === 'codeAbility' ? '填写并测试' : (currentIndex === fields.length - 1 ? '完成补充' : '下一项') }}
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
:deep(.resume-missing-fields-chat) {
  border-radius: 32px;
  overflow: hidden;
}

:deep(.resume-missing-fields-chat .el-dialog) {
  max-width: calc(100vw - 48px);
  border-radius: 32px;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.16), transparent 28%),
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.18);
}

:deep(.resume-missing-fields-chat .el-dialog__header) {
  margin-right: 0;
  padding: 28px 32px 12px;
}

:deep(.resume-missing-fields-chat .el-dialog__body) {
  padding: 12px 32px 32px;
}

:deep(.resume-missing-fields-chat .el-dialog__headerbtn) {
  top: 22px;
  right: 24px;
}

.panel-label {
  margin-bottom: 16px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #3b82f6;
  text-transform: uppercase;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.dialog-title {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;

}

.dialog-subtitle {
  margin-top: 10px;
  font-size: 16px;
  color: #64748b;
  line-height: 1.7;
}

.chat-shell {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(420px, 1.1fr);
  gap: 24px;
  align-items: stretch;
}

.chat-history {
  min-height: 620px;
  padding: 24px;
  border-radius: 28px;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.16), transparent 36%),
    linear-gradient(180deg, #eef5ff 0%, #f8fbff 100%);
  border: 1px solid rgba(147, 197, 253, 0.35);
  overflow-y: auto;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.bubble-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 18px;
}

.bubble-row.user {
  justify-content: flex-end;
}

.bubble-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.assistant-avatar {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #fff;
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.24);
}

.user-avatar {
  background: linear-gradient(135deg, #14b8a6 0%, #6ee7b7 100%);
  color: #fff;
  box-shadow: 0 12px 24px rgba(20, 184, 166, 0.22);
}

.bubble {
  max-width: min(88%, 420px);
  padding: 18px 20px;
  border-radius: 22px;
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
}

.assistant-bubble {
  background: #fff;
  color: #374151;
  border-top-left-radius: 10px;
}

.user-bubble {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  color: #fff;
  border-top-right-radius: 10px;
}

.bubble-title {
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 700;
  opacity: 0.8;
}

.bubble p {
  margin: 0;
  line-height: 1.9;
  font-size: 16px;
}

.history-row {
  margin-top: 12px;
}

.history-bubble {
  opacity: 0.78;
}

.composer-card {
  display: flex;
  flex-direction: column;
  min-height: 620px;
  padding: 28px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(203, 213, 225, 0.7);
  box-shadow: 0 20px 48px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(10px);
}

.composer-title {
  margin-bottom: 18px;
  font-size: 32px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.composer-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.composer-title-row .composer-title {
  margin-bottom: 0;
}

.composer-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.composer-body.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.tag-editor {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.tag-input-row {
  display: flex;
  gap: 10px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.code-ability-guide {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 22px;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(191, 219, 254, 0.28), transparent 32%),
    linear-gradient(180deg, #f8fbff 0%, #f3f8ff 100%);
  border: 1px solid #d8e7fb;
}

.code-ability-guide-text {
  margin: 0;
  font-size: 15px;
  line-height: 1.9;
  color: #475569;
}

.code-ability-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid #e5edf8;
}

.code-ability-toggle-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.code-ability-toggle-desc {
  margin-top: 4px;
  font-size: 13px;
  line-height: 1.7;
  color: #64748b;
}

.composer-footer {
  margin-top: 22px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.composer-hint {
  margin-bottom: 12px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.7;
}

.composer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.quiz-guide {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 22px;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(147, 197, 253, 0.18), transparent 30%),
    linear-gradient(180deg, #f8fbff 0%, #f2f7ff 100%);
  border: 1px solid #d8e7fb;
  min-width: 0;
}

.quiz-guide-text {
  margin: 0;
  font-size: 16px;
  line-height: 1.9;
  color: #475569;
}

.quiz-action-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
}

.quiz-action-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 18px 20px;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid #e5edf8;
  box-shadow: 0 14px 30px rgba(59, 130, 246, 0.06);
  min-width: 0;
}

.quiz-action-content {
  flex: 1;
  min-width: 0;
}

.quiz-action-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.quiz-action-title {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
}

.quiz-action-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.9;
  color: #64748b;
  word-break: break-word;
}

.quiz-action-btn {
  min-width: 188px;
  height: 48px;
  padding: 0 22px;
  border: none;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 700;
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.18);
}

:deep(.quiz-action-btn.el-button--primary) {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #fff;
}

:deep(.quiz-action-btn.el-button--warning) {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  color: #fff;
}

:deep(.quiz-action-btn.el-button--info) {
  background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
  color: #fff;
}

:deep(.quiz-action-btn.el-button--success) {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  color: #fff;
}

:deep(.composer-card .el-input__wrapper),
:deep(.composer-card .el-select__wrapper),
:deep(.composer-card .el-textarea__inner),
:deep(.composer-card .el-date-editor.el-input__wrapper),
:deep(.composer-card .el-cascader .el-input__wrapper) {
  min-height: 48px;
  border-radius: 16px;
  box-shadow: 0 0 0 1px #dbe5f1 inset;
}

:deep(.composer-card .el-input__wrapper:hover),
:deep(.composer-card .el-select__wrapper:hover),
:deep(.composer-card .el-date-editor.el-input__wrapper:hover),
:deep(.composer-card .el-cascader .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #93c5fd inset;
}

:deep(.composer-card .el-tag) {
  border-radius: 999px;
  padding: 6px 12px;
}

:deep(.composer-actions .el-button) {
  min-width: 120px;
  height: 44px;
  border-radius: 999px;
  font-weight: 700;
}

@media (max-width: 900px) {
  :deep(.resume-missing-fields-chat .el-dialog) {
    max-width: calc(100vw - 20px);
  }

  :deep(.resume-missing-fields-chat .el-dialog__header) {
    padding: 22px 20px 8px;
  }

  :deep(.resume-missing-fields-chat .el-dialog__body) {
    padding: 10px 20px 20px;
  }

  .dialog-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .dialog-title {
    font-size: 24px;
  }

  .dialog-subtitle {
    font-size: 14px;
  }

  .chat-shell {
    grid-template-columns: 1fr;
  }

  .chat-history,
  .composer-card {
    min-height: auto;
  }

  .composer-body.two-col,
  .tag-input-row {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .code-ability-toggle {
    align-items: flex-start;
    flex-direction: column;
  }

  .quiz-action-card {
    grid-template-columns: 1fr;
    align-items: stretch;
  }

  .quiz-action-btn {
    width: 100%;
    min-width: 0;
  }
}
</style>
