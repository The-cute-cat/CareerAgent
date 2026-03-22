import type { QuizResponse, OpenEndedScoreResult } from '@/types/careerform_question'
import type { Result } from '@/types/type'

/**
 * 生成模拟题目数据
 * @param type - 测试类型
 * @param name - 技能/工具名称（可选）
 * @returns QuizResponse 题目数据
 */
export const generateMockQuestions = (type: string, name?: string): QuizResponse => {
  const displayName = name || type

  return {
    tool: displayName,
    total_questions: 5,
    questions: [
      {
        id: 1,
        type: 'choice',
        content: name
          ? `关于 ${name} 的基础知识，以下哪个选项是正确的？`
          : `这是一道${type}测试题，请选择正确的选项？`,
        options: [
          'A. 这是第一个选项的内容',
          'B. 这是第二个选项的内容',
          'C. 这是第三个选项的内容',
          'D. 这是第四个选项的内容'
        ],
        correct_answer: 'B',
        difficulty: 'easy'
      },
      {
        id: 2,
        type: 'choice',
        content: name
          ? `在使用 ${name} 时，遇到复杂情况应该如何处理？`
          : `在进行${type}测试时，遇到以下情况应该如何应对？`,
        options: [
          'A. 采用方案一进行处理',
          'B. 采用方案二进行处理',
          'C. 采用方案三进行处理',
          'D. 以上都不对'
        ],
        correct_answer: 'C',
        difficulty: 'medium'
      },
      {
        id: 3,
        type: 'fill_in',
        content: name
          ? `在 ${name} 中，使用 {{answer}} 命令可以实现快速创建新项目的功能。`
          : `在该测试中，使用 {{answer}} 方法可以快速解决问题。`,
        options: null,
        correct_answer: 'init',
        difficulty: 'medium'
      },
      {
        id: 4,
        type: 'fill_in',
        content: name
          ? `${name} 的配置文件中，{{answer}} 字段用于指定项目的入口文件。`
          : `配置文件中的 {{answer}} 字段用于指定关键参数。`,
        options: null,
        correct_answer: 'main',
        difficulty: 'hard'
      },
      {
        id: 5,
        type: 'open_ended',
        content: name
          ? `请结合实际项目经验，描述你在使用 ${name} 时遇到的一个复杂问题，以及你是如何分析和解决这个问题的。`
          : `请结合实际情况，描述你在${type}方面的一次具体经历，以及你的应对思路和解决方案。`,
        options: null,
        correct_answer: null,
        evaluation_criteria: `1. 问题描述清晰，背景交代完整（10分）
2. 分析思路合理，逻辑清晰（10分）
3. 解决方案具体可行（10分）
4. 总结反思到位，有借鉴意义（10分）`,
        difficulty: 'hard'
      }
    ]
  }
}

/**
 * 模拟获取题目 API 响应
 * @param type - 测试类型
 * @param name - 技能/工具名称
 * @returns Result<QuizResponse>
 */
export const mockGetQuestionsResponse = (type: string, name?: string): Result<QuizResponse> => {
  return {
    code: 200,
    msg: '获取题目成功',
    data: generateMockQuestions(type, name)
  }
}

/**
 * 模拟问答题评分结果
 * @param answer - 用户答案
 * @returns OpenEndedScoreResult 评分结果
 */
export const mockOpenEndedScoreResult = (answer: string): OpenEndedScoreResult => {
  const answerLength = answer.trim().length

  // 根据答案长度给出不同评分（模拟 AI 评分逻辑）
  let score = 0
  if (answerLength > 200) {
    score = 32 // 优秀
  } else if (answerLength > 100) {
    score = 28 // 良好
  } else if (answerLength > 50) {
    score = 20 // 一般
  } else if (answerLength > 10) {
    score = 12 // 较差
  } else {
    score = 5  // 很差
  }

  return {
    score,
    max_score: 40,
    score_details: [
      {
        point: '问题描述清晰，背景交代完整',
        max_point_score: 10,
        earned_score: Math.floor(score * 0.25),
        reason: answerLength > 100 ? '描述较为清晰' : '描述不够详细，建议补充更多背景信息'
      },
      {
        point: '分析思路合理，逻辑清晰',
        max_point_score: 10,
        earned_score: Math.floor(score * 0.25),
        reason: answerLength > 80 ? '思路较为清晰' : '分析过程可以更加详细'
      },
      {
        point: '解决方案具体可行',
        max_point_score: 10,
        earned_score: Math.floor(score * 0.25),
        reason: answerLength > 60 ? '方案基本可行' : '解决方案需要更具体的描述'
      },
      {
        point: '总结反思到位，有借鉴意义',
        max_point_score: 10,
        earned_score: Math.floor(score * 0.25),
        reason: answerLength > 40 ? '有一定总结' : '缺少总结反思'
      }
    ],
    comment: score >= 32 ? '回答优秀，思路清晰，解决方案具体可行。' :
             score >= 25 ? '回答良好，分析较为全面，方案基本可行。' :
             score >= 18 ? '回答一般，分析不够深入，方案需要完善。' :
             score >= 10 ? '回答较差，内容过于简单，需要详细阐述。' :
                           '回答很不理想，建议认真思考后再作答。',
    suggestions: '建议：1）详细描述问题背景；2）清晰阐述分析过程；3）提供具体可行的解决方案；4）总结经验和教训。'
  }
}

/**
 * 模拟提交问答题评分 API 响应
 * @param answer - 用户答案
 * @returns Result<OpenEndedScoreResult>
 */
export const mockSubmitOpenEndedResponse = (answer: string): Result<OpenEndedScoreResult> => {
  return {
    code: 200,
    msg: '评分成功',
    data: mockOpenEndedScoreResult(answer)
  }
}
