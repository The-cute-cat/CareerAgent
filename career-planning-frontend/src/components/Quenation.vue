<template>
  <div class="questionnaire-container">
    <el-card class="questionnaire-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>{{ title }}</h2>
          <el-tag type="info">共5题，请认真填写</el-tag>
        </div>
      </template>

      <!-- 答题表单 -->
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        label-position="top"
        require-asterisk-position="right"
        status-icon
      >
        <!-- 后端数据模式：动态渲染题目 -->
        <template v-if="props.backendData">
          <div
            v-for="(question, index) in props.backendData.questions"
            :key="question.id"
          >
            <!-- 单选题 -->
            <el-form-item
              v-if="question.type === 'choice'"
              :label="`${index + 1}. ${question.content}`"
              :prop="`q_${question.id}`"
              :rules="[{ required: true, message: '请选择答案', trigger: 'change' }]"
            >
              <el-radio-group v-model="formData[`q_${question.id}`]">
                <el-radio
                  v-for="(opt, optIndex) in parseOptions(question.options)"
                  :key="optIndex"
                  :value="opt.value"
                  class="quiz-option"
                >
                  <span class="option-label">{{ opt.label }}</span>
                  <span class="option-text">{{ opt.text }}</span>
                </el-radio>
              </el-radio-group>
              <el-tag
                v-if="question.difficulty"
                :type="getDifficultyType(question.difficulty)"
                size="small"
                class="difficulty-tag"
              >
                {{ getDifficultyText(question.difficulty) }}
              </el-tag>
            </el-form-item>

            <!-- 填空题 -->
            <el-form-item
              v-else-if="question.type === 'fill_in'"
              :label="`${index + 1}. ${parseFillInContent(question.content)}`"
              :prop="`q_${question.id}`"
              :rules="[{ required: true, message: '请填写答案', trigger: 'blur' }]"
            >
              <el-input
                v-model="formData[`q_${question.id}`]"
                :placeholder="'请输入答案'"
                clearable
                maxlength="200"
                show-word-limit
              />
              <el-tag
                v-if="question.difficulty"
                :type="getDifficultyType(question.difficulty)"
                size="small"
                class="difficulty-tag"
              >
                {{ getDifficultyText(question.difficulty) }}
              </el-tag>
            </el-form-item>

            <!-- 问答题 -->
            <el-form-item
              v-else-if="question.type === 'open_ended'"
              :label="`${index + 1}. ${question.content}`"
              :prop="`q_${question.id}`"
              :rules="[{ required: true, message: '请填写答案', trigger: 'blur' }]"
            >
              <el-input
                v-model="formData[`q_${question.id}`]"
                type="textarea"
                :rows="6"
                :placeholder="question.evaluation_criteria ? '请根据评分标准作答...' : '请详细描述...'"
                maxlength="2000"
                show-word-limit
                resize="vertical"
              />
              <div v-if="question.evaluation_criteria" class="evaluation-criteria">
                <div class="criteria-title">评分标准：</div>
                <pre class="criteria-content">{{ question.evaluation_criteria }}</pre>
              </div>
              <el-tag
                v-if="question.difficulty"
                :type="getDifficultyType(question.difficulty)"
                size="small"
                class="difficulty-tag"
              >
                {{ getDifficultyText(question.difficulty) }}
              </el-tag>
            </el-form-item>
          </div>
        </template>

        <!-- 默认模式：使用本地问题集 -->
        <template v-else>
          <!-- 单选题 1 -->
          <el-form-item :label="currentQuestions.single1.label" prop="single1" required>
            <el-radio-group v-model="formData.single1">
              <el-radio
                v-for="opt in currentQuestions.single1.options"
                :key="opt.value"
                :value="opt.value"
              >
                {{ opt.text }}
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 单选题 2 -->
          <el-form-item :label="currentQuestions.single2.label" prop="single2" required>
            <el-radio-group v-model="formData.single2">
              <el-radio
                v-for="opt in currentQuestions.single2.options"
                :key="opt.value"
                :value="opt.value"
              >
                {{ opt.text }}
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 填空题 1 -->
          <el-form-item :label="currentQuestions.fill1.label" prop="fill1" required>
            <el-input
              v-model="formData.fill1"
              :placeholder="currentQuestions.fill1.placeholder"
              clearable
              maxlength="100"
              show-word-limit
            />
            <div v-if="currentQuestions.fill1.tip" class="input-tip">{{ currentQuestions.fill1.tip }}</div>
          </el-form-item>

          <!-- 填空题 2 -->
          <el-form-item :label="currentQuestions.fill2.label" prop="fill2" required>
            <el-input
              v-model="formData.fill2"
              :placeholder="currentQuestions.fill2.placeholder"
              clearable
              maxlength="100"
              show-word-limit
            />
            <div v-if="currentQuestions.fill2.tip" class="input-tip">{{ currentQuestions.fill2.tip }}</div>
          </el-form-item>

          <!-- 问答题 -->
          <el-form-item :label="currentQuestions.essay.label" prop="essay" required>
            <el-input
              v-model="formData.essay"
              type="textarea"
              :rows="6"
              :placeholder="currentQuestions.essay.placeholder"
              maxlength="1000"
              show-word-limit
              resize="vertical"
            />
          </el-form-item>
        </template>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            @click="handleSubmit"
            :disabled="!isFormComplete"
          >
            {{ submitting ? '提交中...' : '提交问卷' }}
          </el-button>
          <el-button size="large" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 提交成功提示 -->
      <el-alert
        v-if="submitSuccess"
        title="提交成功！感谢您的参与"
        type="success"
        :closable="true"
        @close="submitSuccess = false"
        class="success-alert"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== 类型定义 ====================

/** 后端返回的题目类型 */
interface BackendQuestion {
  id: number
  type: 'choice' | 'fill_in' | 'open_ended'
  content: string
  options: string[] | null
  correct_answer: string | null
  evaluation_criteria?: string
  difficulty: 'easy' | 'medium' | 'hard'
}

/** 后端返回的问卷数据 */
interface BackendQuizData {
  tool: string
  total_questions: number
  questions: BackendQuestion[]
}

/** 选项 */
interface QuestionOption {
  value: string
  text: string
}

/** 单选题配置 */
interface SingleChoiceQuestion {
  label: string
  options: QuestionOption[]
}

/** 填空题配置 */
interface FillQuestion {
  label: string
  placeholder: string
  tip?: string
}

/** 问答题配置 */
interface EssayQuestion {
  label: string
  placeholder: string
}

/** 问题集 */
interface QuestionSet {
  single1: SingleChoiceQuestion
  single2: SingleChoiceQuestion
  fill1: FillQuestion
  fill2: FillQuestion
  essay: EssayQuestion
}

/** 表单数据类型 */
interface QuestionnaireForm {
  single1: string
  single2: string
  fill1: string
  fill2: string
  essay: string
  [key: string]: string  // 支持动态字段
}

/** 提交给后端的接口数据类型 */
interface SubmitData {
  answers: Record<string, string>
  submitTime: string
  userAgent: string
  quizType: string
  toolName: string
}

// ==================== Props 定义 ====================

interface Props {
  /** 问卷标题 */
  title?: string
  /** 问卷类型 */
  quizType?: string
  /** 自定义问题集（可选，不传则根据quizType使用默认问题） */
  customQuestions?: QuestionSet
  /** 后端返回的问卷数据（优先使用） */
  backendData?: BackendQuizData | null
}

const props = withDefaults(defineProps<Props>(), {
  title: '能力评估问卷',
  quizType: 'general',
  customQuestions: undefined,
  backendData: null
})

// ==================== Emits 定义 ====================

const emit = defineEmits<{
  /** 提交完成事件 */
  submit: [data: SubmitData]
  /** 取消/关闭事件 */
  cancel: []
}>()

// ==================== 问题库定义 ====================

/** 技能测试问题集 */
const skillQuestions: QuestionSet = {
  single1: {
    label: '1. 你使用该技能的年限是？',
    options: [
      { value: 'beginner', text: '1年以下（入门）' },
      { value: 'junior', text: '1-3年（初级）' },
      { value: 'intermediate', text: '3-5年（中级）' },
      { value: 'senior', text: '5年以上（高级）' }
    ]
  },
  single2: {
    label: '2. 你使用该技能完成过多少个项目？',
    options: [
      { value: 'none', text: '还没有实际项目经验' },
      { value: 'few', text: '1-3个小项目' },
      { value: 'some', text: '4-10个中等项目' },
      { value: 'many', text: '10个以上大型项目' }
    ]
  },
  fill1: {
    label: '3. 你最常用的该技能相关框架/库是什么？',
    placeholder: '例如：Spring Boot、React、PyTorch等',
    tip: '填写你最熟悉的相关技术栈'
  },
  fill2: {
    label: '4. 你在该技能领域的认证或培训经历？',
    placeholder: '例如：Oracle认证、AWS认证等，没有填"无"',
    tip: '如有相关证书或培训请填写'
  },
  essay: {
    label: '5. 请描述一个使用该技能解决的最复杂问题',
    placeholder: '详细描述问题背景、你的解决思路、具体方案和最终成果...'
  }
}

/** 工具测试问题集 */
const toolQuestions: QuestionSet = {
  single1: {
    label: '1. 你对该工具的使用频率是？',
    options: [
      { value: 'rarely', text: '偶尔使用（每月几次）' },
      { value: 'sometimes', text: '有时使用（每周几次）' },
      { value: 'often', text: '经常使用（每天）' },
      { value: 'daily', text: '日常工作必备' }
    ]
  },
  single2: {
    label: '2. 你掌握该工具的深度是？',
    options: [
      { value: 'basic', text: '基础操作（常用命令/功能）' },
      { value: 'intermediate', text: '中级水平（配置优化）' },
      { value: 'advanced', text: '高级应用（复杂场景）' },
      { value: 'expert', text: '专家级（原理理解/二次开发）' }
    ]
  },
  fill1: {
    label: '3. 你在工作中使用该工具的主要场景是什么？',
    placeholder: '例如：代码版本管理、容器化部署等',
    tip: '描述你的主要使用场景'
  },
  fill2: {
    label: '4. 你遇到过该工具的哪些常见问题？',
    placeholder: '例如：冲突解决、性能优化等，没有填"无"',
    tip: '列举你遇到过的典型问题'
  },
  essay: {
    label: '5. 请描述一次使用该工具提升工作效率的经历',
    placeholder: '描述具体场景、你如何使用该工具、带来了什么效果...'
  }
}

/** 代码能力测试问题集 */
const codeQuestions: QuestionSet = {
  single1: {
    label: '1. 你最擅长的编程语言是？',
    options: [
      { value: 'python', text: 'Python' },
      { value: 'java', text: 'Java' },
      { value: 'javascript', text: 'JavaScript/TypeScript' },
      { value: 'cpp', text: 'C/C++' },
      { value: 'other', text: '其他' }
    ]
  },
  single2: {
    label: '2. 你的代码能力自我评估是？',
    options: [
      { value: 'learner', text: '正在学习编程基础' },
      { value: 'junior', text: '能完成基础编码，需要代码审查' },
      { value: 'middle', text: '能独立完成开发任务，代码规范良好' },
      { value: 'senior', text: '能编写高质量代码，熟悉设计模式' }
    ]
  },
  fill1: {
    label: '3. 你的代码仓库地址（GitHub/Gitee等）',
    placeholder: 'https://github.com/username',
    tip: '填写你的代码仓库主页链接'
  },
  fill2: {
    label: '4. 你参与过的开源项目或技术社区活动？',
    placeholder: '例如：Vue贡献者、Apache提交者等，没有填"无"',
    tip: '如有开源贡献请填写'
  },
  essay: {
    label: '5. 请分享你最满意的一个代码项目或技术实现',
    placeholder: '描述项目背景、你的角色、技术选型、遇到的挑战和解决方案...'
  }
}

/** 沟通能力测评问题集 */
const communicationQuestions: QuestionSet = {
  single1: {
    label: '1. 在团队协作中，你通常扮演的角色是？',
    options: [
      { value: 'listener', text: '倾听者（主要听别人讲）' },
      { value: 'participant', text: '参与者（适时发表意见）' },
      { value: 'organizer', text: '组织者（协调大家讨论）' },
      { value: 'leader', text: '主导者（带领团队沟通）' }
    ]
  },
  single2: {
    label: '2. 遇到与他人意见不合时，你通常如何处理？',
    options: [
      { value: 'avoid', text: '避免冲突，选择沉默' },
      { value: 'compromise', text: '适当妥协，寻求折中' },
      { value: 'discuss', text: '积极沟通，理性讨论' },
      { value: 'convince', text: '坚持己见，说服对方' }
    ]
  },
  fill1: {
    label: '3. 你在团队中通常负责什么类型的沟通工作？',
    placeholder: '例如：需求对接、技术方案讲解等',
    tip: '描述你的沟通职责'
  },
  fill2: {
    label: '4. 你认为自己在沟通中需要改进的方面是什么？',
    placeholder: '例如：表达清晰度、倾听耐心等',
    tip: '自我反思沟通中的不足'
  },
  essay: {
    label: '5. 请描述一次成功协调团队分歧的经历',
    placeholder: '描述背景、分歧点、你采取的沟通策略和最终效果...'
  }
}

/** 抗压能力测评问题集 */
const stressQuestions: QuestionSet = {
  single1: {
    label: '1. 面对紧急任务和 deadline 压力时，你的反应是？',
    options: [
      { value: 'panic', text: '感到焦虑，不知所措' },
      { value: 'worried', text: '有些紧张，但能应对' },
      { value: 'calm', text: '保持冷静，有序处理' },
      { value: 'motivated', text: '压力转化为动力' }
    ]
  },
  single2: {
    label: '2. 连续加班或高强度工作后，你通常如何调节？',
    options: [
      { value: 'none', text: '不调节，继续工作' },
      { value: 'rest', text: '简单休息，恢复体力' },
      { value: 'exercise', text: '运动或娱乐活动' },
      { value: 'balance', text: '科学安排工作生活平衡' }
    ]
  },
  fill1: {
    label: '3. 你面临过的最大工作压力是什么？',
    placeholder: '例如：项目上线、突发故障等',
    tip: '描述你遇到的压力场景'
  },
  fill2: {
    label: '4. 你平时如何预防和缓解工作压力？',
    placeholder: '例如：时间管理、运动健身等',
    tip: '分享你的压力管理方法'
  },
  essay: {
    label: '5. 请描述一次在高压环境下成功完成任务的经历',
    placeholder: '描述压力来源、你的应对策略、如何保持效率和最终成果...'
  }
}

/** 学习能力测评问题集 */
const learningQuestions: QuestionSet = {
  single1: {
    label: '1. 学习新技术时，你通常采用的方式是？',
    options: [
      { value: 'casual', text: '有空时随便看看' },
      { value: 'project', text: '边做项目边学' },
      { value: 'systematic', text: '系统学习+实践' },
      { value: 'deep', text: '深入原理，全面掌握' }
    ]
  },
  single2: {
    label: '2. 面对陌生的技术领域，你需要多久能上手？',
    options: [
      { value: 'month', text: '需要一个月以上' },
      { value: 'weeks', text: '需要几周时间' },
      { value: 'week', text: '一周左右' },
      { value: 'fast', text: '几天就能入门' }
    ]
  },
  fill1: {
    label: '3. 你最近学习的一项新技术是什么？',
    placeholder: '例如：Rust、K8s、微服务等',
    tip: '填写你最近学习的技术'
  },
  fill2: {
    label: '4. 你常用的学习资源和渠道有哪些？',
    placeholder: '例如：官方文档、技术博客、在线课程等',
    tip: '分享你的学习途径'
  },
  essay: {
    label: '5. 请描述你学习新技术的完整过程和方法',
    placeholder: '描述你学习新技术时的步骤、技巧、如何克服困难和如何验证学习效果...'
  }
}

/** 问题集映射 */
const questionBank: Record<string, QuestionSet> = {
  skill: skillQuestions,
  tool: toolQuestions,
  code: codeQuestions,
  communication: communicationQuestions,
  stress: stressQuestions,
  learning: learningQuestions
}

// ==================== 计算属性 ====================

/** 当前使用的问题集 */
const currentQuestions = computed<QuestionSet>(() => {
  if (props.customQuestions) {
    return props.customQuestions
  }
  return questionBank[props.quizType] || skillQuestions
})

/** 表单是否填写完整 */
const isFormComplete = computed(() => {
  // 后端数据模式
  if (props.backendData) {
    return props.backendData.questions.every(q => {
      const answer = formData[`q_${q.id}`]
      return answer && answer.trim() !== ''
    })
  }
  // 默认模式
  return !!(
    formData.single1 &&
    formData.single2 &&
    formData.fill1.trim() &&
    formData.fill2.trim() &&
    formData.essay.trim()
  )
})

/** 难度标签类型 */
const getDifficultyType = (difficulty: string): 'success' | 'warning' | 'danger' | 'info' => {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    'easy': 'success',
    'medium': 'warning',
    'hard': 'danger'
  }
  return map[difficulty] || 'info'
}

/** 难度文本 */
const getDifficultyText = (difficulty: string): string => {
  const map: Record<string, string> = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难'
  }
  return map[difficulty] || difficulty
}

/** 解析选项 */
const parseOptions = (options: string[] | null): { label: string; value: string; text: string }[] => {
  if (!options) return []
  return options.map(opt => {
    // 格式: "A. 选项内容" 或 "A.选项内容"
    const match = opt.match(/^([A-D])[.．\s]+(.+)$/)
    if (match && match[1] && match[2]) {
      return {
        label: match[1],
        value: match[1],
        text: match[2].trim()
      }
    }
    // 没有前缀的选项
    return {
      label: opt.charAt(0) || '•',
      value: opt,
      text: opt
    }
  })
}

/** 解析填空题内容，移除 {{answer}} 占位符 */
const parseFillInContent = (content: string): string => {
  return content.replace(/\{\{answer\}\}/g, '______')
}

// ==================== 状态定义 ====================

/** 表单引用 */
const formRef = ref<FormInstance>()

/** 表单数据 */
const formData = reactive<QuestionnaireForm>({
  single1: '',
  single2: '',
  fill1: '',
  fill2: '',
  essay: ''
})

/** 提交状态 */
const submitting = ref(false)

/** 提交成功标志 */
const submitSuccess = ref(false)

// ==================== 监听 ====================

/** 监听quizType变化，重置表单 */
watch(() => props.quizType, () => {
  handleReset()
})

/** 监听backendData变化，初始化表单 */
watch(() => props.backendData, () => {
  initFormData()
}, { immediate: true })

// ==================== 表单验证规则 ====================

/** 验证非空字符串（不能只是空格） */
const validateNotEmpty = (rule: any, value: string, callback: any) => {
  if (!value || value.trim() === '') {
    callback(new Error('此字段不能为空'))
  } else {
    callback()
  }
}


/** 动态表单验证规则 */
const formRules = computed<FormRules<QuestionnaireForm>>(() => {
  // 后端数据模式：动态生成规则
  if (props.backendData) {
    const rules: FormRules<QuestionnaireForm> = {}
    props.backendData.questions.forEach(q => {
      const key = `q_${q.id}`
      if (q.type === 'choice') {
        rules[key] = [{ required: true, message: '请选择答案', trigger: 'change' }]
      } else if (q.type === 'fill_in') {
        rules[key] = [
          { required: true, validator: validateNotEmpty, trigger: 'blur' },
          { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
        ]
      } else if (q.type === 'open_ended') {
        rules[key] = [
          { required: true, validator: validateNotEmpty, trigger: 'blur' },
          { min: 10, max: 2000, message: '描述至少10个字', trigger: 'blur' }
        ]
      }
    })
    return rules
  }
  // 默认模式
  return {
    single1: [{ required: true, message: '请选择答案', trigger: 'change' }],
    single2: [{ required: true, message: '请选择答案', trigger: 'change' }],
    fill1: [
      { required: true, validator: validateNotEmpty, trigger: 'blur' },
      { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
    ],
    fill2: [
      { required: true, validator: validateNotEmpty, trigger: 'blur' },
      { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
    ],
    essay: [
      { required: true, validator: validateNotEmpty, trigger: 'blur' },
      { min: 10, max: 1000, message: '描述至少10个字', trigger: 'blur' }
    ]
  }
})

// ==================== 方法定义 ====================

/** 提交表单 */
const handleSubmit = async () => {
  if (!formRef.value) return

  // 检查表单是否完整
  if (!isFormComplete.value) {
    ElMessage.warning('请填写完所有题目后再提交')
    return
  }

  // 先验证表单
  await formRef.value.validate(async (valid, fields) => {
    if (!valid) {
      ElMessage.error('请正确填写所有题目')
      console.log('验证失败字段:', fields)
      return
    }

    // 二次确认
    try {
      await ElMessageBox.confirm('确认提交问卷答案吗？', '提交确认', {
        confirmButtonText: '确认提交',
        cancelButtonText: '再检查一下',
        type: 'info'
      })
    } catch {
      return // 用户取消提交
    }

    submitting.value = true

    try {
      // 构造提交数据
      let answers: Record<string, string> = {}
      
      if (props.backendData) {
        // 后端数据模式：收集所有答案
        props.backendData.questions.forEach(q => {
          answers[`q_${q.id}`] = formData[`q_${q.id}`] || ''
        })
      } else {
        // 默认模式
        answers = {
          single1: formData.single1,
          single2: formData.single2,
          fill1: formData.fill1,
          fill2: formData.fill2,
          essay: formData.essay
        }
      }
      
      const submitData: SubmitData = {
        answers,
        submitTime: new Date().toISOString(),
        userAgent: navigator.userAgent,
        quizType: props.quizType,
        toolName: props.backendData?.tool || ''
      }

      console.log('准备提交数据:', submitData)

      // 模拟调用后端API
      const result = await submitToBackend(submitData)
      
      if (result.success) {
        submitSuccess.value = true
        ElMessage.success('提交成功！')
        // 触发提交事件
        emit('submit', submitData)
      } else {
        ElMessage.error('提交失败，请稍后重试')
      }
    } catch (error) {
      console.error('提交出错:', error)
      ElMessage.error('网络错误，提交失败')
    } finally {
      submitting.value = false
    }
  })
}

/** 模拟提交到后端的函数 */
const submitToBackend = (data: SubmitData): Promise<{ success: boolean; id?: string }> => {
  return new Promise((resolve) => {
    // 模拟网络延迟
    setTimeout(() => {
      // 模拟成功响应
      console.log('后端接收到的数据:', data)
      
      // 这里可以替换成真正的axios请求
      // axios.post('/api/questionnaire/submit', data)
      
      resolve({
        success: true,
        id: 'resp_' + Date.now()
      })
    }, 800)
  })
}

/** 重置表单 */
const handleReset = () => {
  // 清空表单数据
  if (props.backendData) {
    // 后端数据模式：清空动态字段
    props.backendData.questions.forEach(q => {
      formData[`q_${q.id}`] = ''
    })
  } else {
    // 默认模式
    formData.single1 = ''
    formData.single2 = ''
    formData.fill1 = ''
    formData.fill2 = ''
    formData.essay = ''
  }
  submitSuccess.value = false
  // 触发表单重置验证
  formRef.value?.resetFields()
}

/** 初始化表单数据（用于后端数据模式） */
const initFormData = () => {
  if (props.backendData) {
    props.backendData.questions.forEach(q => {
      if (!(q.id in formData)) {
        formData[`q_${q.id}`] = ''
      }
    })
  }
}

/** 暴露方法给父组件 */
defineExpose({
  reset: handleReset
})
</script>

<style scoped lang="scss">
.questionnaire-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 0;
}

.questionnaire-card {
  width: 100%;
  max-width: 800px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2) !important;
  
  :deep(.el-card__header) {
    padding: 20px 30px;
    background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    border-bottom: none;
  }
  
  :deep(.el-card__body) {
    padding: 30px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h2 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: #2c3e50;
  }
}

.input-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.success-alert {
  margin-top: 20px;
}

/* 难度标签 */
.difficulty-tag {
  margin-top: 8px;
}

/* 评分标准 */
.evaluation-criteria {
  margin-top: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.criteria-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  font-size: 14px;
}

.criteria-content {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
  font-family: inherit;
}

/* 选项样式 */
:deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

:deep(.el-radio) {
  margin-right: 0;
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s ease;
  height: auto;
  display: flex;
  align-items: center;
}

:deep(.el-radio:hover) {
  border-color: #409eff;
  background: #f5f9ff;
}

:deep(.el-radio.is-checked) {
  border-color: #409eff;
  background: #ecf5ff;
}

:deep(.el-radio__label) {
  padding-left: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-label {
  font-weight: 600;
  color: #409eff;
  min-width: 24px;
}

.option-text {
  color: #303133;
}

:deep(.el-form-item) {
  margin-bottom: 28px;
  
  .el-form-item__label {
    font-weight: 500;
    color: #2c3e50;
    padding-bottom: 8px;
  }
  
  .el-radio-group {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    
    .el-radio {
      margin-right: 0;
    }
  }
  
  .el-textarea {
    .el-textarea__inner {
      font-family: inherit;
      line-height: 1.6;
    }
  }
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 12px 30px;
  font-weight: 500;
  
  &:hover {
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
}

:deep(.el-button--default) {
  padding: 12px 30px;
  font-weight: 500;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .questionnaire-card {
    max-width: 100%;
    
    :deep(.el-card__body) {
      padding: 20px;
    }
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  :deep(.el-radio-group) {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>