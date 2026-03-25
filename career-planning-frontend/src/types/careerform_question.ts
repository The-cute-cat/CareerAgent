// ==================== 获取问题类型定义 ====================


/** 通用响应结果 */
import type {  Result } from "./type"


/** 问卷类型 */
export type QuizType = 'skill' | 'tool' | 'code' | 'communication' | 'stress' | 'learning'

/** 基础请求参数 */
export interface GetQuestionsBaseParams {
  /** 问卷类型 */
  quizType: QuizType
}

/** 技能/工具测试参数（必须包含 title，表示技能/工具名称） */
export interface GetQuestionsWithTitleParams extends GetQuestionsBaseParams {
  /** 问卷类型：技能或工具 */
  quizType: 'skill' | 'tool'
  /** 技能/工具名称，如 Java、Python、Git、Docker 等 */
  title: string
}

/** 其他类型参数（不需要 title） */
export interface GetQuestionsWithoutTitleParams extends GetQuestionsBaseParams {
  /** 问卷类型：代码能力或素质测评 */
  quizType: 'code' | 'communication' | 'stress' | 'learning'
  /** 问卷标题（可选，仅用于显示） */
  title?: string
}

/** 获取问题请求参数（联合类型） */
export type GetQuestionsParams = GetQuestionsWithTitleParams | GetQuestionsWithoutTitleParams

/** 后端接收的参数格式 */
export interface GetQuestionsRequest {
  /** 测试类型 */
  type: QuizType
  /** 技能/工具名称（skill 和 tool 类型时必填） */
  name?: string
}


// ==================== 后端返回的题目类型定义 ====================

/** 题目类型：单选题、填空题、问答题 */
export type QuestionType = 'choice' | 'fill_in' | 'open_ended'

/** 素质测评题目类型：单选题、问答题 */
export type PersonQuestionType = 'choice' | 'open_ended'


/** 素质测评/代码能力测评 - 单条题目（新接口返回） */
export interface BackendPersonData {
  /** 题目ID */
  id: number
  /** 题目类型：单选题或问答题 */
  type: PersonQuestionType
  /** 题目内容 */
  text: string
  /** 选择题选项（问答题为 null） */
  options: string[] | null
}

/** 难度级别 */
export type QuestionDifficulty = 'easy' | 'medium' | 'hard'

/** 单选题 */
export interface ChoiceQuestion {
  /** 题目ID */
  id: number
  /** 题目类型：单选题 */
  type: 'choice'
  /** 题目内容 */
  content: string
  /** 选项列表，格式如 ["A. 选项1", "B. 选项2", ...] */
  options: string[]
  /** 正确答案，如 "A", "B", "C", "D" */
  correct_answer: string
  /** 难度：easy-简单, medium-中等, hard-困难 */
  difficulty: QuestionDifficulty
}

/** 填空题 */
export interface FillInQuestion {
  /** 题目ID */
  id: number
  /** 题目类型：填空题 */
  type: 'fill_in'
  /** 题目内容，空白处用 {{answer}} 表示 */
  content: string
  /** 选项（填空题为 null） */
  options: null
  /** 正确答案 */
  correct_answer: string
  /** 难度：easy-简单, medium-中等, hard-困难 */
  difficulty: QuestionDifficulty
}

/** 问答题 */
export interface OpenEndedQuestion {
  /** 题目ID */
  id: number
  /** 题目类型：问答题 */
  type: 'open_ended'
  /** 题目内容 */
  content: string
  /** 选项（问答题为 null） */
  options: null
  /** 正确答案（问答题为 null） */
  correct_answer: null
  /** 评分标准 */
  evaluation_criteria: string
  /** 难度：easy-简单, medium-中等, hard-困难 */
  difficulty: QuestionDifficulty
}

/** 题目联合类型 */
export type Question = ChoiceQuestion | FillInQuestion | OpenEndedQuestion

/** 后端返回的问卷数据 */
export interface QuizResponse {
  /** 工具/技能名称 */
  tool: string
  /** 总题数（固定5道题：2道单选、2道填空、1道问答） */
  total_questions: number
  /** 题目列表 */
  questions: Question[]
}

/** 答案项 */
export interface AnswerItem {
  /** 题目ID */
  questionId: number
  /** 用户答案 */
  answer: string
}



/** 提交问答题请求参数 */
export interface SubmitOpenEndedParams {
  /** 工具/技能名称 */
  name?: string
  /** 测试类型 */
  type: QuizType
  /** 问答题题目内容 */
  questions: string
  /** 用户的回答 */
  studentAnswer: string
  /** 评分标准（可选，用于后端参考） */
  evaluationCriteria?: string
}

/** 问答题得分详情 */
export interface ScoreDetailItem {
  /** 得分点描述 */
  point: string
  /** 该点满分 */
  max_point_score: number
  /** 该点得分 */
  earned_score: number
  /** 得分/扣分原因 */
  reason: string
}

/** 问答题评分结果（后端返回） */
export interface OpenEndedScoreResult {
  /** 问答题得分 */
  score: number
  /** 问答题满分（40分） */
  max_score: number
  /** 问答题详细评分 */
  score_details: ScoreDetailItem[]
  /** 整体评语，指出答案的优点和不足 */
  comment: string
  /** 改进建议，帮助学生提升 */
  suggestions: string
}


// 技能/工具的定义接口（java,90分）
export interface SkillTool {
  name: string
  score: number
}

// ==================== 提交问卷相关类型 ====================

/** 详细答题统计 */
export interface AnswerStats {
  /** 单选题答对数/总数 */
  choice: { correct: number; total: number }
  /** 填空题答对数/总数 */
  fillIn: { correct: number; total: number }
  /** 未答题数量 */
  unanswered: number
}

/**
 * 提交问卷参数
 * - quizType 为 skill/tool 时，name 必填
 * - quizType 为 code/communication/stress/learning 时，name 不需要
 */
export interface SubmitQuizParams {
  /** 问卷类型 */
  quizType: QuizType
  /** 技能/工具名称（skill 和 tool 类型时必填，如 Java、Git） */
  name?: string
  /** 题目列表（包含正确答案） */
  questions: Question[]
  /** 用户答案映射 { questionId: answer } */
  userAnswers: Record<number, string>
}

/**
 * 提交问卷结果（携带 quizType 和 name，便于存储到 CareerFormData 对应位置）
 *
 * 存储映射：
 * - quizType='skill' + name → CareerFormData.skills.push({ name, score: totalScore })
 * - quizType='tool'  + name → CareerFormData.tools.push({ name, score: totalScore })
 * - quizType='code'          → CareerFormData.codeAbility 相关
 * - quizType='communication/stress/learning' → 素质测评，答案存入 quizDetail
 */
export interface SubmitQuizResult {
  /** 问卷类型 */
  quizType: QuizType
  /** 技能/工具名称（skill/tool 时有值） */
  name?: string
  /** 测试总分（选择题 + 填空题 + 问答题） */
  totalScore: number
  /** 总分满分 */
  totalMaxScore: number
  /** 各题型得分明细 */
  scoreDetails: {
    /** 选择题得分（前端判分） */
    choiceScore: number
    /** 填空题得分（前端判分） */
    fillInScore: number
    /** 问答题得分（后端 AI 评分） */
    openEndedScore: number
  }
  /** 答题统计 */
  stats: AnswerStats
  /** 问答题详细评分结果 */
  openEndedDetails: OpenEndedScoreResult
}
