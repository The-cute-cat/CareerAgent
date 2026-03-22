import request from '@/utils/request'
import type { 
  GetQuestionsParams, 
  GetQuestionsRequest, 
  QuizResponse,
  SubmitOpenEndedParams,
  OpenEndedScoreResult,
  OpenEndedQuestion,
  Question,
  SubmitQuizParams,
  SubmitQuizResult,
  AnswerStats
} from '@/types/careerform_question'
import { 
  mockGetQuestionsResponse, 
  mockSubmitOpenEndedResponse 
} from '@/mock/mockdata/question_mockdata'

/**
 * 测验总分计算结果
 */
export interface QuizTotalResult {
  /** 单选题实际得分 */
  choiceScore: number
  /** 单选题满分 */
  choiceMaxScore: number
  /** 填空题实际得分 */
  fillInScore: number
  /** 填空题满分 */
  fillInMaxScore: number
  /** 问答题实际得分 */
  openEndedScore: number
  /** 问答题满分 */
  openEndedMaxScore: number
  /** 总分 */
  totalScore: number
  /** 总分满分 */
  totalMaxScore: number
  /** 问答题详细评分结果 */
  openEndedDetails: OpenEndedScoreResult
}

/**
 * 获取测试题目
 * 使用模拟数据（开发阶段），生产环境请切换为真实 API
 */
export const getQuestionsApi = (params: GetQuestionsParams) => {
  // 模拟 API 调用
  return new Promise<{ data: any }>((resolve) => {
    setTimeout(() => {
      const response = mockGetQuestionsResponse(
        params.quizType,
        (params.quizType === 'skill' || params.quizType === 'tool') ? params.title : undefined
      )
      resolve({ data: response })
    }, 500)
  })

  // 真实 API（生产环境使用）
  // const requestData: GetQuestionsRequest = {
  //   type: params.quizType,
  //   name: (params.quizType === 'skill' || params.quizType === 'tool') 
  //     ? params.title 
  //     : undefined
  // }
  // return request.get<QuizResponse>('/api/quiz/questions', { params: requestData })
}

/**
 * 提交问答题，获取问答题评分
 * 使用模拟数据（开发阶段），生产环境请切换为真实 API
 */
export const submitOpenEndedApi = (data: SubmitOpenEndedParams) => {
  // 模拟 API 调用
  return new Promise<{ data: any }>((resolve) => {
    setTimeout(() => {
      const response = mockSubmitOpenEndedResponse(data.answer)
      resolve({ data: response })
    }, 800)
  })

  // 真实 API（生产环境使用）
  // return request.post<OpenEndedScoreResult>('/api/quiz/open-ended-score', data)
}


// ==================== 计分配置 ====================

/**
 * 计分配置（可自定义各题型分值）
 */
export interface ScoreConfig {
  /** 单选题每题分值（默认10分） */
  choicePerScore: number
  /** 填空题每题分值（默认20分） */
  fillInPerScore: number
  /** 问答题满分（默认40分） */
  openEndedMaxScore: number
}

/** 默认计分配置 */
const DEFAULT_SCORE_CONFIG: ScoreConfig = {
  choicePerScore: 10,
  fillInPerScore: 20,
  openEndedMaxScore: 40
}

/** 问答题零分默认值（用户未作答时使用） */
const EMPTY_OPEN_ENDED_RESULT: OpenEndedScoreResult = {
  score: 0,
  max_score: 40,
  score_details: [],
  comment: '',
  suggestions: ''
}


// ==================== 前端判分：选择题 + 填空题 ====================

/**
 * 计算选择题和填空题的得分（纯前端逻辑）
 * 单选题：不区分大小写比较
 * 填空题：忽略首尾空格 + 不区分大小写比较
 * @param questions 题目列表
 * @param userAnswers 用户答案 { questionId: answer }
 * @param config 可选的计分配置
 * @returns 选择题和填空题的得分、满分及答题统计
 */
export const calculateObjectiveScore = (
  questions: Question[],
  userAnswers: Record<number, string>,
  config: Partial<ScoreConfig> = {}
) => {
  const finalConfig = { ...DEFAULT_SCORE_CONFIG, ...config }
  let choiceScore = 0
  let fillInScore = 0
  let choiceCorrect = 0
  let choiceTotal = 0
  let fillInCorrect = 0
  let fillInTotal = 0
  let unanswered = 0

  questions.forEach(q => {
    const userAnswer = userAnswers[q.id]?.trim()

    if (!userAnswer) {
      unanswered++
      return
    }

    if (q.type === 'choice') {
      choiceTotal++
      const isCorrect = userAnswer.toUpperCase() === q.correct_answer?.toUpperCase()
      if (isCorrect) {
        choiceScore += finalConfig.choicePerScore
        choiceCorrect++
      }
    } else if (q.type === 'fill_in') {
      fillInTotal++
      const userAns = userAnswer.toLowerCase()
      const correctAns = q.correct_answer?.trim().toLowerCase()
      const isCorrect = userAns === correctAns
      if (isCorrect) {
        fillInScore += finalConfig.fillInPerScore
        fillInCorrect++
      }
    }
  })

  return {
    choiceScore,
    choiceMaxScore: choiceTotal * finalConfig.choicePerScore,
    fillInScore,
    fillInMaxScore: fillInTotal * finalConfig.fillInPerScore,
    stats: {
      choice: { correct: choiceCorrect, total: choiceTotal },
      fillIn: { correct: fillInCorrect, total: fillInTotal },
      unanswered
    } as AnswerStats
  }
}


// ==================== 完整提交流程 ====================

/**
 * 提交问卷并计算总分
 *
 * 完整流程：
 * 1. 前端判分：遍历选择题/填空题，将用户答案与正确答案比对，答对加分
 * 2. 后端判分：提取问答题答案，提交到后端获取 AI 评分
 * 3. 汇总：总分 = 选择题得分 + 填空题得分 + 问答题得分
 *
 * @param params 提交参数（quizType, name, questions, userAnswers）
 * @returns 包含总分、各题型明细和 quizType 信息的结果
 *
 * @example
 * ```ts
 * // 技能测试（需要 name）
 * const result = await submitQuiz({
 *   quizType: 'skill',
 *   name: 'Java',
 *   questions,
 *   userAnswers
 * })
 * // result.totalScore → 存入 CareerFormData.skills: [{ name: 'Java', score: result.totalScore }]
 *
 * // 素质测评（不需要 name）
 * const result = await submitQuiz({
 *   quizType: 'communication',
 *   questions,
 *   userAnswers
 * })
 * // result.totalScore → 存入 CareerFormData.quizScores.communication = result.totalScore
 * ```
 */
export async function submitQuiz(
  params: SubmitQuizParams
): Promise<SubmitQuizResult> {
  const { quizType, name, questions, userAnswers } = params

  // 1. 前端判分：选择题 + 填空题
  const objective = calculateObjectiveScore(questions, userAnswers)

  // 2. 找到问答题，提交到后端获取 AI 评分
  const openEndedQuestion = questions.find(
    (q): q is OpenEndedQuestion => q.type === 'open_ended'
  )

  let openEndedResult: OpenEndedScoreResult = { ...EMPTY_OPEN_ENDED_RESULT }

  if (openEndedQuestion) {
    const userAnswer = userAnswers[openEndedQuestion.id] || ''
    if (userAnswer.trim()) {
      try {
        const response = await submitOpenEndedApi({
          tool: name,
          type: quizType,
          questionId: openEndedQuestion.id,
          answer: userAnswer,
          evaluationCriteria: openEndedQuestion.evaluation_criteria,
          submitTime: new Date().toISOString()
        })
        // 后端返回 Result<OpenEndedScoreResult>，提取 data 字段
        const resultData = response.data as any
        if (resultData?.data && typeof resultData.data.score === 'number') {
          openEndedResult = resultData.data
        } else if (typeof resultData?.score === 'number') {
          openEndedResult = resultData
        }
      } catch (e) {
        console.warn('[submitQuiz] 问答题评分请求失败，该题记0分', e)
      }
    }
  }

  // 3. 汇总总分
  const totalScore = objective.choiceScore + objective.fillInScore + openEndedResult.score
  const totalMaxScore =
    objective.choiceMaxScore +
    objective.fillInMaxScore +
    openEndedResult.max_score

  return {
    quizType,
    name,
    totalScore,
    totalMaxScore,
    scoreDetails: {
      choiceScore: objective.choiceScore,
      fillInScore: objective.fillInScore,
      openEndedScore: openEndedResult.score
    },
    stats: objective.stats,
    openEndedDetails: openEndedResult
  }
}


// ==================== 兼容：旧版 calculateTotalScore ====================

/**
 * 计算测试总分（兼容旧版接口）
 * @deprecated 推荐使用 submitQuiz 完成提交流程，或 calculateObjectiveScore 仅计算客观题得分
 */
export const calculateTotalScore = (
  questions: Question[],
  userAnswers: Record<number, string>,
  openEndedResult: OpenEndedScoreResult,
  config: Partial<ScoreConfig> = {}
): QuizTotalResult & { stats: AnswerStats } => {
  const objective = calculateObjectiveScore(questions, userAnswers, config)
  const openEndedScore = openEndedResult?.score ?? 0
  const totalScore = objective.choiceScore + objective.fillInScore + openEndedScore
  const totalMaxScore =
    objective.choiceMaxScore +
    objective.fillInMaxScore +
    (openEndedResult?.max_score ?? 40)

  return {
    choiceScore: objective.choiceScore,
    choiceMaxScore: objective.choiceMaxScore,
    fillInScore: objective.fillInScore,
    fillInMaxScore: objective.fillInMaxScore,
    openEndedScore,
    openEndedMaxScore: openEndedResult?.max_score ?? 40,
    totalScore,
    totalMaxScore,
    openEndedDetails: openEndedResult,
    stats: objective.stats
  }
}
