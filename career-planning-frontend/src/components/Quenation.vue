<template>
  <div class="questionnaire-container">
    <el-card class="questionnaire-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>{{ title }}</h2>
          <el-tag type="info">共{{ totalSteps }}题，请认真填写</el-tag>
        </div>
      </template>

      <!-- 步骤导航栏 - 仅在未提交时显示 -->
      <div v-if="!submitted" class="step-nav">
        <div class="step-header">
          <span class="step-indicator">第 <strong>{{ currentStep }}</strong> / {{ totalSteps }} 题</span>
          <span class="step-type-tag">{{ getStepLabel(currentStep - 1) }}</span>
        </div>
        <div class="step-dots">
          <div v-for="i in totalSteps" :key="i" class="step-dot-wrapper">
            <button
              class="step-dot"
              :class="{
                'is-active': currentStep === i,
                'is-answered': currentStep === i && isStepAnswered(i - 1),
                'is-unanswered': currentStep === i && !isStepAnswered(i - 1)
              }"
              @click="goToStep(i)"
            >
              <span class="step-dot-number">{{ i }}</span>
            </button>
            <span class="step-dot-label">{{ getStepLabel(i - 1) }}</span>
          </div>
        </div>
      </div>

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
        <!-- 后端数据模式：分步渲染题目 -->
        <template v-if="props.backendData">
          <div v-for="(question, index) in props.backendData.questions" :key="question.id" v-show="currentStep === index + 1">
            <!-- 单选题 -->
            <el-form-item
              v-if="question.type === 'choice'"
              :label="`${index + 1}. ${question.content}`"
              :prop="`q_${question.id}`"
              :rules="[{ required: true, message: '', trigger: 'change' }]"
              show-message="false"
              class="quiz-question-item"
              :class="{ 'is-submitted': submitted }"
            >
              <el-radio-group v-model="formData[`q_${question.id}`]" :disabled="submitted">
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
              <!-- 提交后显示结果 -->
              <template v-if="submitted">
                <div class="result-feedback" :class="isChoiceCorrect(question) ? 'is-correct' : 'is-wrong'">
                  <span class="result-icon">{{ isChoiceCorrect(question) ? '✓' : '✗' }}</span>
                  <span class="result-text">{{ isChoiceCorrect(question) ? '回答正确' : '回答错误' }}</span>
                </div>
                <div v-if="!isChoiceCorrect(question)" class="correct-answer-tip">
                  <el-icon><WarningFilled /></el-icon>
                  正确答案：{{ getCorrectChoiceText(question) }}
                </div>
              </template>
              <template v-else>
                <el-tag
                  v-if="question.difficulty"
                  :type="getDifficultyType(question.difficulty)"
                  size="small"
                  class="difficulty-tag"
                >
                  {{ getDifficultyText(question.difficulty) }}
                </el-tag>
              </template>
            </el-form-item>

            <!-- 填空题 -->
            <el-form-item
              v-else-if="question.type === 'fill_in'"
              :label="`${index + 1}. ${parseFillInContent(question.content)}`"
              :prop="`q_${question.id}`"
              :rules="[{ required: true, message: '请填写答案', trigger: 'blur' }]"
              class="quiz-question-item"
              :class="{ 'is-submitted': submitted }"
            >
              <el-input
                v-model="formData[`q_${question.id}`]"
                :placeholder="'请输入答案'"
                clearable
                maxlength="200"
                show-word-limit
                :disabled="submitted"
              />
              <!-- 提交后显示结果 -->
              <template v-if="submitted">
                <div class="result-feedback" :class="isFillInCorrect(question) ? 'is-correct' : 'is-wrong'">
                  <span class="result-icon">{{ isFillInCorrect(question) ? '✓' : '✗' }}</span>
                  <span class="result-text">{{ isFillInCorrect(question) ? '回答正确' : '回答错误' }}</span>
                </div>
                <div v-if="!isFillInCorrect(question)" class="correct-answer-tip">
                  <el-icon><WarningFilled /></el-icon>
                  正确答案：{{ question.correct_answer }}
                </div>
              </template>
              <template v-else>
                <el-tag
                  v-if="question.difficulty"
                  :type="getDifficultyType(question.difficulty)"
                  size="small"
                  class="difficulty-tag"
                >
                  {{ getDifficultyText(question.difficulty) }}
                </el-tag>
              </template>
            </el-form-item>

            <!-- 问答题 -->
            <el-form-item
              v-else-if="question.type === 'open_ended'"
              :label="`${index + 1}. ${question.content}`"
              :prop="`q_${question.id}`"
              :rules="[{ required: true, message: '', trigger: 'blur' }]"
              :show-message="false"
              class="is-open-ended quiz-question-item"
              :class="{ 'is-submitted': submitted }"
            >
              <div v-if="question.evaluation_criteria && !submitted" class="evaluation-criteria">
                <div class="criteria-title">
                  <el-icon><InfoFilled /></el-icon>
                  评分标准
                </div>
                <pre class="criteria-content">{{ question.evaluation_criteria }}</pre>
              </div>
              <el-input
                v-model="formData[`q_${question.id}`]"
                type="textarea"
                :rows="6"
                :placeholder="question.evaluation_criteria ? '请根据评分标准作答...' : '请详细描述...'"
                maxlength="2000"
                show-word-limit
                resize="vertical"
                class="essay-textarea"
                :disabled="submitted"
              />
              <!-- 提交后显示参考答案按钮和评分详情 -->
              <template v-if="submitted">
                <div class="open-ended-actions">
                  <el-button
                    type="primary"
                    link
                    size="small"
                    @click="toggleOpenEndedAnswer(question.id)"
                  >
                    <el-icon><View /></el-icon>
                    {{ showOpenEndedAnswer[question.id] ? '收起参考答案' : '查看参考答案' }}
                  </el-button>
                  <!-- 最后一题（问答题）显示查看评分详情按钮 -->
                  <el-button
                    v-if="props.quizResult && index === (props.backendData?.questions?.length || 0) - 1"
                    type="success"
                    link
                    size="small"
                    @click="showScoreDetails = true"
                  >
                    <el-icon><Trophy /></el-icon>
                    查看评分详情
                  </el-button>
                </div>
                <transition name="el-zoom-in-top">
                  <div v-if="showOpenEndedAnswer[question.id] && question.correct_answer" class="open-ended-answer">
                    <div class="answer-title">参考答案：</div>
                    <div class="answer-content">{{ question.correct_answer }}</div>
                  </div>
                </transition>
              </template>
              <template v-else>
                <el-tag
                  v-if="question.difficulty"
                  :type="getDifficultyType(question.difficulty)"
                  size="small"
                  class="difficulty-tag"
                >
                  {{ getDifficultyText(question.difficulty) }}
                </el-tag>
              </template>
            </el-form-item>
          </div>
        </template>

        <!-- 默认模式：分步渲染 -->
        <template v-else>
          <!-- 第1题：单选题1 -->
          <div v-show="currentStep === 1">
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
          </div>
          <!-- 第2题：单选题2 -->
          <div v-show="currentStep === 2">
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
          </div>
          <!-- 第3题：填空题1 -->
          <div v-show="currentStep === 3">
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
          </div>
          <!-- 第4题：填空题2 -->
          <div v-show="currentStep === 4">
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
          </div>
          <!-- 第5题：问答题 -->
          <div v-show="currentStep === 5">
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
          </div>
        </template>

        <!-- 底部操作按钮 -->
        <el-form-item v-if="!submitted" class="step-actions">
          <div class="step-actions-inner">
            <el-button size="default" @click="handleReset">重置</el-button>
            <div class="step-actions-right">
              <el-button v-if="currentStep > 1" size="default" @click="prevStep">
                上一题
              </el-button>
              <el-button v-if="currentStep < totalSteps" type="primary" size="default" @click="nextStep">
                下一题
              </el-button>
              <el-button
                v-if="currentStep === totalSteps"
                type="primary"
                size="default"
                :loading="submitting"
                @click="handleSubmit"
                :disabled="!isFormComplete"
              >
                {{ submitting ? '提交中...' : '提交问卷' }}
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <!-- 提交成功后的结果导航 -->
      <div v-if="submitted" class="result-nav">
        <div class="result-nav-header">
          <el-icon class="result-success-icon"><SuccessFilled /></el-icon>
          <span class="result-title">提交成功！</span>
          <span class="result-subtitle">点击题号查看答题结果</span>
        </div>
        <div class="result-step-dots">
          <button
            v-for="(question, index) in (props.backendData?.questions || [])"
            :key="question.id"
            class="result-step-dot"
            :class="{
              'is-active': currentStep === index + 1,
              'is-correct-dot': (question.type === 'choice' || question.type === 'fill_in') && (question.type === 'choice' ? isChoiceCorrect(question) : isFillInCorrect(question)),
              'is-wrong-dot': (question.type === 'choice' || question.type === 'fill_in') && (question.type === 'choice' ? !isChoiceCorrect(question) : !isFillInCorrect(question)),
              'is-essay-dot': question.type === 'open_ended'
            }"
            @click="currentStep = index + 1"
          >
            {{ index + 1 }}
          </button>
        </div>
        <div class="result-actions">
          <el-button v-if="currentStep > 1" size="default" @click="prevStep">上一题</el-button>
          <el-button v-if="currentStep < totalSteps" size="default" @click="nextStep">下一题</el-button>
          <el-button type="success" size="default" @click="emit('cancel')">关闭</el-button>
        </div>
      </div>

      <!-- 评分详情弹窗 -->
      <el-dialog
        v-model="showScoreDetails"
        title="测评结果详情"
        width="600px"
        class="score-details-dialog"
        :close-on-click-modal="false"
      >
        <div v-if="props.quizResult" class="score-dialog-content">
          <!-- 总分 -->
          <div class="dialog-total-score">
            <div class="dialog-score-number">{{ props.quizResult.totalScore }}</div>
            <div class="dialog-score-divider">/</div>
            <div class="dialog-score-max">{{ props.quizResult.totalMaxScore }}</div>
            <div class="dialog-score-label">总得分</div>
          </div>

          <!-- 问答题评分 -->
          <div class="dialog-oe-section">
            <div class="dialog-oe-header">
              <el-icon><EditPen /></el-icon>
              <span>问答题评分</span>
            </div>
            <div class="dialog-oe-bar">
              <span class="dialog-oe-text">
                {{ props.quizResult.openEndedDetails.score }} / {{ props.quizResult.openEndedDetails.max_score }} 分
              </span>
              <el-progress
                :percentage="Math.round((props.quizResult.openEndedDetails.score / props.quizResult.openEndedDetails.max_score) * 100)"
                :stroke-width="12"
                :color="getScoreColor(props.quizResult.openEndedDetails.score, props.quizResult.openEndedDetails.max_score)"
              />
            </div>

            <!-- 得分点明细 -->
            <div v-if="props.quizResult.openEndedDetails.score_details?.length" class="dialog-score-points">
              <div
                v-for="(detail, idx) in props.quizResult.openEndedDetails.score_details"
                :key="idx"
                class="dialog-point-item"
              >
                <div class="dialog-point-header">
                  <span class="dialog-point-name">{{ detail.point }}</span>
                  <el-tag
                    :type="detail.earned_score >= detail.max_point_score ? 'success' : 'warning'"
                    size="small"
                  >
                    {{ detail.earned_score }}/{{ detail.max_point_score }}
                  </el-tag>
                </div>
                <div class="dialog-point-reason">{{ detail.reason }}</div>
              </div>
            </div>

            <!-- 评语 -->
            <div v-if="props.quizResult.openEndedDetails.comment" class="dialog-comment-box">
              <div class="dialog-comment-label">
                <el-icon><InfoFilled /></el-icon>
                整体评语
              </div>
              <p class="dialog-comment-text">{{ props.quizResult.openEndedDetails.comment }}</p>
            </div>

            <!-- 建议 -->
            <div v-if="props.quizResult.openEndedDetails.suggestions" class="dialog-suggestions-box">
              <div class="dialog-suggestions-label">
                <el-icon><Warning /></el-icon>
                改进建议
              </div>
              <p class="dialog-suggestions-text">{{ props.quizResult.openEndedDetails.suggestions }}</p>
            </div>
          </div>
        </div>
        <template #footer>
          <el-button type="primary" @click="showScoreDetails = false">知道了</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled, WarningFilled, View, SuccessFilled, Trophy, EditPen, Warning } from '@element-plus/icons-vue'

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

/** 评分详情 */
interface ScoreDetail {
  point: string
  max_point_score: number
  earned_score: number
  reason: string
}

/** 问答题评分结果 */
interface OpenEndedDetails {
  score: number
  max_score: number
  score_details: ScoreDetail[]
  comment: string
  suggestions: string
}

/** 测验结果 */
interface QuizResult {
  totalScore: number
  totalMaxScore: number
  openEndedDetails: OpenEndedDetails
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
  /** 测验结果（提交后传入，用于显示评分详情） */
  quizResult?: QuizResult | null
}

const props = withDefaults(defineProps<Props>(), {
  title: '能力评估问卷',
  quizType: 'general',
  customQuestions: undefined,
  backendData: null,
  quizResult: null
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

// ==================== 步骤导航 ====================

/** 当前步骤（1-based） */
const currentStep = ref(1)

/** 总步骤数 */
const totalSteps = computed(() => {
  if (props.backendData?.questions?.length) {
    return props.backendData.questions.length
  }
  return 5
})

/** 判断某步骤是否已作答 */
const isStepAnswered = (index: number): boolean => {
  if (props.backendData?.questions?.length) {
    const q = props.backendData.questions[index]
    if (!q) return false
    return !!formData[`q_${q.id}`]?.trim()
  }
  // 默认模式
  const keys = ['single1', 'single2', 'fill1', 'fill2', 'essay'] as const
  const key = keys[index]
  return key ? !!formData[key]?.trim() : false
}

/** 获取步骤标签（题目类型简称） */
const getStepLabel = (index: number): string => {
  if (props.backendData?.questions?.length) {
    const q = props.backendData.questions[index]
    if (!q) return ''
    const typeMap: Record<string, string> = {
      choice: '单选',
      fill_in: '填空',
      open_ended: '问答'
    }
    return typeMap[q.type] || `第${index + 1}题`
  }
  const labels = ['单选', '单选', '填空', '填空', '问答']
  return labels[index] || `第${index + 1}题`
}

/** 跳转到指定步骤 */
const goToStep = (step: number) => {
  if (step >= 1 && step <= totalSteps.value) {
    currentStep.value = step
  }
}

/** 上一题 */
const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

/** 下一题 */
const nextStep = () => {
  if (currentStep.value < totalSteps.value) {
    currentStep.value++
  }
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
  if (props.backendData?.questions && Array.isArray(props.backendData.questions)) {
    return props.backendData.questions.every(q => {
      const answer = formData[`q_${q.id}`]
      return answer && answer.trim() !== ''
    })
  }
  // 默认模式
  return !!(
    formData.single1 &&
    formData.single2 &&
    formData.fill1?.trim() &&
    formData.fill2?.trim() &&
    formData.essay?.trim()
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

/** 表单数据 - 使用 Record 类型支持动态字段 */
const formData = reactive<Record<string, string>>({
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

/** 已提交状态 */
const submitted = ref(false)

/** 问答题参考答案显示状态 */
const showOpenEndedAnswer = ref<Record<number, boolean>>({})

/** 评分详情显示状态 */
const showScoreDetails = ref(false)

/** 切换评分详情显示 */
const toggleScoreDetails = () => {
  showScoreDetails.value = !showScoreDetails.value
}

/** 根据得分比例返回颜色 */
const getScoreColor = (score: number, maxScore: number): string => {
  const ratio = score / maxScore
  if (ratio >= 0.8) return '#67c23a'
  if (ratio >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

/** 判断单选题是否正确 */
const isChoiceCorrect = (question: BackendQuestion): boolean => {
  const key = `q_${question.id}`
  const userAnswer = formData[key]?.trim().toUpperCase()
  const correctAnswer = question.correct_answer?.trim().toUpperCase()
  return userAnswer === correctAnswer
}

/** 判断填空题是否正确 */
const isFillInCorrect = (question: BackendQuestion): boolean => {
  const key = `q_${question.id}`
  const userAnswer = formData[key]?.trim()
  const correctAnswer = question.correct_answer?.trim()
  return userAnswer === correctAnswer
}

/** 获取正确选择题答案文本 */
const getCorrectChoiceText = (question: BackendQuestion): string => {
  const correctAnswer = question.correct_answer?.trim().toUpperCase() || ''
  if (!question.options) return correctAnswer
  const opt = question.options.find(o => o.match(new RegExp(`^${correctAnswer}[.．\\s]`)))
  return opt || correctAnswer
}

/** 切换问答题答案显示 */
const toggleOpenEndedAnswer = (questionId: number) => {
  showOpenEndedAnswer.value[questionId] = !showOpenEndedAnswer.value[questionId]
}

// ==================== 监听 ====================

/** 监听quizType变化，重置表单 */
watch(() => props.quizType, () => {
  handleReset()
})

/** 监听backendData变化，初始化表单 */
watch(() => props.backendData, (newVal) => {
  if (newVal) {
    initFormData()
  }
})

/** 组件挂载时初始化表单 */
onMounted(() => {
  if (props.backendData) {
    initFormData()
  }
})

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
const formRules = computed<FormRules>(() => {
  // 后端数据模式：动态生成规则
  if (props.backendData?.questions && Array.isArray(props.backendData.questions)) {
    const rules: FormRules = {}
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

      if (props.backendData?.questions && Array.isArray(props.backendData.questions)) {
        // 后端数据模式：收集所有答案
        props.backendData.questions.forEach(q => {
          answers[`q_${q.id}`] = formData[`q_${q.id}`] || ''
        })
      }
      // 默认模式
      answers = {
        ...answers,
        single1: formData.single1 || '',
        single2: formData.single2 || '',
        fill1: formData.fill1 || '',
        fill2: formData.fill2 || '',
        essay: formData.essay || ''
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
        submitted.value = true
        currentStep.value = 1
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
  if (props.backendData?.questions && Array.isArray(props.backendData.questions)) {
    // 后端数据模式：清空动态字段
    props.backendData.questions.forEach(q => {
      formData[`q_${q.id}`] = ''
    })
  }
  // 默认模式
  formData.single1 = ''
  formData.single2 = ''
  formData.fill1 = ''
  formData.fill2 = ''
  formData.essay = ''

  submitSuccess.value = false
  submitted.value = false
  showOpenEndedAnswer.value = {}
  showScoreDetails.value = false
  currentStep.value = 1
  // 触发表单重置验证
  formRef.value?.resetFields()
}

/** 初始化表单数据（用于后端数据模式） */
const initFormData = () => {
  if (props.backendData?.questions && Array.isArray(props.backendData.questions)) {
    props.backendData.questions.forEach(q => {
      const key = `q_${q.id}`
      if (!(key in formData)) {
        formData[key] = ''
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
  max-width: 720px;
  border-radius: 8px;
  border: 1px solid #ebeef5;

  :deep(.el-card__header) {
    padding: 14px 24px;
    border-bottom: 1px solid #ebeef5;
    background: #fafbfc;
  }

  :deep(.el-card__body) {
    padding: 0;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h2 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }
}

// ==================== 步骤导航栏 ====================

.step-nav {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafbfc;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;

  .step-indicator {
    font-size: 13px;
    color: #909399;

    strong {
      font-size: 16px;
      color: #303133;
      font-weight: 600;
    }
  }

  .step-type-tag {
    font-size: 12px;
    color: #909399;
    background: #f0f2f5;
    padding: 2px 8px;
    border-radius: 10px;
  }
}

.step-dots {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  position: relative;
}

// 连接线
.step-dots::before {
  content: '';
  position: absolute;
  top: 13px;
  left: 20px;
  right: 20px;
  height: 2px;
  background: #e4e7ed;
  z-index: 0;
}

.step-dot-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-dot {
  border: none;
  background: none;
  cursor: pointer;
  padding: 0;
  outline: none;

  .step-dot-number {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 500;
    color: #a8abb2;
    background: #fff;
    border: 2px solid #dcdfe6;
    transition: all 0.2s;
  }

  &:hover .step-dot-number {
    border-color: #409eff;
    color: #409eff;
  }

  // 当前激活
  &.is-active .step-dot-number {
    color: #fff;
    background: #409eff;
    border-color: #409eff;
  }

  // 已回答 + 当前
  &.is-answered.is-active .step-dot-number {
    background: #409eff;
    border-color: #409eff;
  }

  // 已回答 + 非当前
  &.is-answered:not(.is-active) .step-dot-number {
    color: #fff;
    background: #67c23a;
    border-color: #67c23a;
  }
}

.step-dot-label {
  font-size: 11px;
  color: #a8abb2;
  white-space: nowrap;

  .step-dot.is-active ~ &,
  .step-dot-wrapper:has(.is-active) & {
    color: #303133;
  }
}

// ==================== 题目区域 ====================

:deep(.el-form) {
  padding: 24px;
}

:deep(.el-form-item) {
  margin-bottom: 0;

  .el-form-item__label {
    font-size: 15px;
    font-weight: 500;
    color: #1d2129;
    padding-bottom: 16px;
    line-height: 1.6;
    letter-spacing: 0.2px;
  }
}

// 题号高亮
:deep(.el-form-item__label) {
  &::before {
    content: none;
  }
}

.input-tip {
  font-size: 12px;
  color: #86909c;
  margin-top: 6px;
}

.success-alert {
  margin: 0 24px 24px;
}

.difficulty-tag {
  margin-top: 16px;
  display: inline-block;
}

// ==================== 答题结果样式 ====================

.result-feedback {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;

  &.is-correct {
    background: #f0f9eb;
    color: #67c23a;
    border: 1px solid #e1f3d8;
  }

  &.is-wrong {
    background: #fef0f0;
    color: #f56c6c;
    border: 1px solid #fde2e2;
  }

  .result-icon {
    font-size: 18px;
    font-weight: 700;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }

  &.is-correct .result-icon {
    background: #67c23a;
    color: #fff;
  }

  &.is-wrong .result-icon {
    background: #f56c6c;
    color: #fff;
  }
}

.correct-answer-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 8px 14px;
  background: #fdf6ec;
  color: #e6a23c;
  border-radius: 6px;
  border: 1px solid #faecd8;
  font-size: 13px;

  .el-icon {
    font-size: 16px;
    flex-shrink: 0;
  }
}

.open-ended-actions {
  margin-top: 12px;
}

.open-ended-answer {
  margin-top: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f8e0 100%);
  border-radius: 8px;
  border-left: 4px solid #67c23a;

  .answer-title {
    font-weight: 600;
    color: #529b2e;
    margin-bottom: 8px;
    font-size: 14px;
  }

  .answer-content {
    font-size: 14px;
    color: #4e5969;
    line-height: 1.8;
    white-space: pre-wrap;
  }
}

// ==================== 评分详情弹窗 ====================

.score-details-dialog {
  :deep(.el-dialog__header) {
    text-align: center;
    padding-bottom: 0;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
    }
  }

  :deep(.el-dialog__body) {
    padding: 20px 24px;
  }
}

.score-dialog-content {
  max-height: 500px;
  overflow-y: auto;
}

.dialog-total-score {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #ecf5ff 0%, #f5faff 100%);
  border-radius: 12px;

  .dialog-score-number {
    font-size: 48px;
    font-weight: 700;
    color: #409eff;
  }

  .dialog-score-divider {
    font-size: 28px;
    color: #86909c;
  }

  .dialog-score-max {
    font-size: 24px;
    color: #86909c;
  }

  .dialog-score-label {
    margin-left: 8px;
    font-size: 14px;
    color: #4e5969;
  }
}

.dialog-oe-section {
  background: #fafbfc;
  border-radius: 10px;
  padding: 16px;
}

.dialog-oe-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 12px;

  .el-icon {
    color: #409eff;
  }
}

.dialog-oe-bar {
  margin-bottom: 16px;

  .dialog-oe-text {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    color: #4e5969;

    strong {
      color: #409eff;
      font-size: 18px;
    }
  }
}

.dialog-score-points {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.dialog-point-item {
  padding: 12px 14px;
  background: #fff;
  border-radius: 8px;
  border-left: 3px solid #409eff;

  .dialog-point-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }

  .dialog-point-name {
    font-weight: 500;
    color: #1d2129;
    font-size: 14px;
  }

  .dialog-point-reason {
    font-size: 13px;
    color: #86909c;
    line-height: 1.6;
  }
}

.dialog-comment-box {
  margin-bottom: 12px;
  padding: 12px 14px;
  background: #f0f9eb;
  border-radius: 8px;
  border-left: 3px solid #67c23a;

  .dialog-comment-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    color: #529b2e;
    font-size: 13px;
    margin-bottom: 6px;

    .el-icon {
      font-size: 14px;
    }
  }

  .dialog-comment-text {
    margin: 0;
    font-size: 13px;
    color: #4e5969;
    line-height: 1.7;
  }
}

.dialog-suggestions-box {
  padding: 12px 14px;
  background: #fdf6ec;
  border-radius: 8px;
  border-left: 3px solid #e6a23c;

  .dialog-suggestions-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    color: #b88230;
    font-size: 13px;
    margin-bottom: 6px;

    .el-icon {
      font-size: 14px;
    }
  }

  .dialog-suggestions-text {
    margin: 0;
    font-size: 13px;
    color: #4e5969;
    line-height: 1.7;
  }
}

.quiz-question-item.is-submitted {
  :deep(.el-form-item__label) {
    color: #1d2129;
    font-weight: 500;
  }
}

// ==================== 结果导航 ====================

.result-nav {
  margin-top: 20px;
  padding: 20px 24px;
  background: #fafbfc;
  border-radius: 12px;
  border: 1px solid #e5e6eb;
}

.result-nav-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.result-success-icon {
  font-size: 24px;
  color: #67c23a;
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
}

.result-subtitle {
  font-size: 13px;
  color: #86909c;
  margin-left: auto;
}

.result-step-dots {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.result-step-dot {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 2px solid #dcdee0;
  background: #fff;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  color: #4e5969;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    border-color: #a0cfff;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
  }

  &.is-active {
    border-color: #409eff;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
    background: #ecf5ff;
  }

  &.is-correct-dot {
    background: #f0f9eb;
    border-color: #b3e19d;
    color: #529b2e;

    &.is-active {
      background: #e1f3d8;
      border-color: #67c23a;
    }
  }

  &.is-wrong-dot {
    background: #fef0f0;
    border-color: #fab6b6;
    color: #c45656;

    &.is-active {
      background: #fde2e2;
      border-color: #f56c6c;
    }
  }

  &.is-essay-dot {
    background: #fdf6ec;
    border-color: #f3d19e;
    color: #b88230;

    &.is-active {
      background: #faecd8;
      border-color: #e6a23c;
    }
  }
}

.result-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

// ==================== 评分标准 ====================

.evaluation-criteria {
  margin-bottom: 20px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4ff 100%);
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.criteria-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #1a5fb4;
  margin-bottom: 10px;
  font-size: 14px;

  .el-icon {
    font-size: 15px;
  }
}

.criteria-content {
  margin: 0;
  font-size: 13px;
  color: #4e5969;
  line-height: 1.8;
  white-space: pre-wrap;
  font-family: inherit;
}

// ==================== 问答题文本域 ====================

:deep(.el-form-item) {
  &.is-open-ended {
    .el-form-item__label {
      padding-bottom: 20px;
      line-height: 1.8;
    }
  }
}

.essay-textarea {
  margin-top: 8px;

  :deep(.el-textarea__inner) {
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 14px;
    line-height: 1.8;
    background: #fafbfc;
    transition: all 0.3s ease;

    &:hover {
      background: #fff;
    }

    &:focus {
      background: #fff;
      box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
    }
  }

  :deep(.el-input__count) {
    background: transparent;
    color: #86909c;
    font-size: 12px;
  }
}

// ==================== 选项样式 ====================

:deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 100%;
}

:deep(.el-radio) {
  margin-right: 0;
  padding: 0 20px;
  border: 1.5px solid #dcdee0;
  border-radius: 12px;
  height: 60px;
  min-height: 60px;
  width: 100%;
  max-width: 520px;
  display: flex;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: #fafbfc;
  cursor: pointer;
  box-sizing: border-box;
}

:deep(.el-radio:hover) {
  border-color: #a0cfff;
  background: #fff;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.12);
}

:deep(.el-radio.is-checked) {
  border-color: #409eff;
  background: #fff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15), inset 0 0 0 1px rgba(64, 158, 255, 0.1);
}

:deep(.el-radio__input) {
  display: none;
}

:deep(.el-radio__label) {
  padding-left: 14px;
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 15px;
  line-height: 1.5;
  white-space: normal;
  word-wrap: break-word;
  width: 100%;
}

.option-label {
  font-weight: 600;
  color: #8a919c;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #e8eaed;
  border-radius: 8px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

:deep(.el-radio:hover) .option-label {
  background: #d6e9ff;
  color: #5a9bd5;
}

:deep(.el-radio.is-checked) .option-label {
  color: #fff;
  background: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.35);
}

.option-text {
  color: #4e5969;
  font-weight: 400;
  flex: 1;
}

:deep(.el-radio.is-checked) .option-text {
  color: #1a5fb4;
  font-weight: 500;
}

:deep(.el-textarea .el-textarea__inner) {
  font-family: inherit;
  font-size: 14px;
  line-height: 1.7;
}

:deep(.el-input__inner) {
  font-size: 14px;
}

// ==================== 底部操作按钮 ====================

.step-actions {
  margin-top: 32px !important;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  margin-bottom: 0 !important;

  :deep(.el-form-item__content) {
    display: block;
  }
}

.step-actions-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.step-actions-right {
  display: flex;
  gap: 8px;
}

// ==================== 响应式 ====================

@media (max-width: 768px) {
  .questionnaire-card {
    max-width: 100%;
    border-radius: 0;
    border-left: none;
    border-right: none;
  }

  :deep(.el-form) {
    padding: 16px;
  }

  .step-nav {
    padding: 12px 16px;
  }

  .card-header {
    h2 {
      font-size: 15px;
    }
  }

  .step-dot-label {
    font-size: 10px;
  }

  .step-dot-number {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }

  .step-dots::before {
    top: 11px;
    left: 16px;
    right: 16px;
  }

  :deep(.el-radio-group) {
    gap: 6px;
  }

  .step-actions-inner {
    flex-direction: column;
    gap: 8px;
  }

  .step-actions-right {
    width: 100%;

    .el-button {
      flex: 1;
    }
  }
}
</style>
