import type { QuizResponse, OpenEndedScoreResult, BackendPersonData } from '@/types/careerform_question'
import type { Result } from '@/types/type'

// ==================== 素质测评模拟数据 ====================

/** 沟通能力测评题目（19题） */
export const communicationQuestions: BackendPersonData[] = [
  { id: 1, type: 'choice', text: '当你与同事意见不一致时，你通常会：', options: ['A. 坚持己见，试图说服对方', 'B. 避免冲突，选择沉默', 'C. 倾听对方观点，寻找共同点', 'D. 请第三方仲裁'] },
  { id: 2, type: 'choice', text: '在团队会议上，你发现自己不同意大多数人的观点，你会：', options: ['A. 立即提出反对意见', 'B. 会后私下与领导沟通', 'C. 先倾听完所有人的想法，再有条理地表达不同意见', 'D. 选择附和大多数人'] },
  { id: 3, type: 'choice', text: '当客户提出一个你无法立即回答的问题时，你会：', options: ['A. 随口给出一个答案', 'B. 诚实告知需要时间确认，并承诺回复时间', 'C. 转移话题', 'D. 请同事代为回答'] },
  { id: 4, type: 'open_ended', text: '描述一次你成功解决团队冲突的经历。当时是什么情况？你采取了哪些步骤？最终结果如何？', options: null },
  { id: 5, type: 'choice', text: '在书面沟通中（如邮件），你认为最重要的是：', options: ['A. 使用专业术语展示能力', 'B. 简明扼要，清晰表达核心信息', 'C. 详细描述所有细节', 'D. 使用模板化的标准回复'] },
  { id: 6, type: 'choice', text: '当收到批评性反馈时，你的第一反应通常是：', options: ['A. 感到沮丧或愤怒', 'B. 立即辩解', 'C. 冷静分析，提取有价值的建议', 'D. 无视反馈'] },
  { id: 7, type: 'open_ended', text: '请分享一次你需要向非技术人员解释复杂技术问题的经历。你是如何确保对方理解的？', options: null },
  { id: 8, type: 'choice', text: '在跨部门协作中，你认为最有效的沟通方式是：', options: ['A. 正式的会议和邮件', 'B. 非正式的即时通讯工具', 'C. 结合正式和非正式方式，根据情况选择', 'D. 通过各自的领导传达'] },
  { id: 9, type: 'choice', text: '当你需要拒绝他人的请求时，你会：', options: ['A. 直接说"不"', 'B. 找借口推脱', 'C. 解释原因，并提供替代方案', 'D. 拖延不回复'] },
  { id: 10, type: 'choice', text: '在公开演讲或汇报时，你通常会：', options: ['A. 非常紧张，难以表达清楚', 'B. 机械地读稿', 'C. 准备充分，根据听众反应调整表达方式', 'D. 完全即兴发挥'] },
  { id: 11, type: 'open_ended', text: '想象你需要推动一个团队不愿意接受的新流程。你会如何沟通来获得他们的支持？请详细说明你的策略。', options: null },
  { id: 12, type: 'choice', text: '你认为良好的倾听包括：', options: ['A. 保持安静，让对方说完', 'B. 频繁点头表示同意', 'C. 专注理解，适时提问澄清，给予反馈', 'D. 在心里准备自己的回应'] },
  { id: 13, type: 'choice', text: '当沟通出现误解时，你首先会：', options: ['A. 指责对方没有听清楚', 'B. 检查自己的表达是否清晰', 'C. 请其他人评判谁对谁错', 'D. 放弃沟通，自行处理'] },
  { id: 14, type: 'choice', text: '在与上级沟通时，你倾向于：', options: ['A. 只汇报好消息，回避问题', 'B. 事无巨细都汇报', 'C. 主动汇报进展，有问题时带着解决方案沟通', 'D. 等领导问起才汇报'] },
  { id: 15, type: 'open_ended', text: '请描述一次你通过有效沟通挽回一个即将失去的客户或项目的经历。', options: null },
  { id: 16, type: 'choice', text: '你认为非语言沟通（肢体语言、表情等）在沟通中的重要性是：', options: ['A. 不重要，内容才是关键', 'B. 有点重要，但不如语言内容', 'C. 非常重要，往往比语言传达更多信息', 'D. 完全不重要'] },
  { id: 17, type: 'choice', text: '在远程工作环境下，你认为维持有效沟通的关键是：', options: ['A. 增加会议频率', 'B. 完全依赖邮件沟通', 'C. 选择合适的沟通工具，建立清晰的沟通规范', 'D. 减少沟通，各自独立完成工作'] },
  { id: 18, type: 'choice', text: '当团队士气低落时，你会如何沟通来激励大家？', options: ['A. 强调公司的目标和期望', 'B. 分享成功故事，认可每个人的贡献，共情理解困难', 'C. 承诺物质奖励', 'D. 不特别处理，等待自然好转'] },
  { id: 19, type: 'open_ended', text: '回顾你的沟通方式，你认为自己在哪个方面最需要改进？你计划如何提升？', options: null }
]

/** 抗压能力测评题目（18题） */
export const stressQuestions: BackendPersonData[] = [
  { id: 1, type: 'choice', text: '当你面临多个紧急截止日期时，你通常会：', options: ['A. 感到不知所措，无法开始', 'B. 随机选择任务开始做', 'C. 评估优先级，制定计划，逐一完成', 'D. 加班到深夜，试图同时处理所有任务'] },
  { id: 2, type: 'choice', text: '在项目关键阶段遇到重大技术难题，你会：', options: ['A. 感到沮丧并考虑放弃', 'B. 立即向领导汇报困难', 'C. 先尝试多种解决方案，必要时寻求帮助', 'D. 绕过这个问题，先做其他部分'] },
  { id: 3, type: 'choice', text: '当你已经连续加班一周，身体感到疲惫时，你会：', options: ['A. 继续硬撑，直到完成所有工作', 'B. 完全停下来休息，不管工作进度', 'C. 调整工作节奏，适当休息，保持工作效率', 'D. 抱怨工作量大，消极怠工'] },
  { id: 4, type: 'open_ended', text: '描述一次你在极度压力下完成重要任务的经历。当时的情况如何？你是如何管理压力的？你从中学到了什么？', options: null },
  { id: 5, type: 'choice', text: '当工作需求突然增加，而你已经在满负荷工作时，你会：', options: ['A. 默默接受，试图独自承担所有工作', 'B. 立即拒绝新的任务', 'C. 与领导沟通，协商优先级和资源', 'D. 拖延处理，希望需求会改变'] },
  { id: 6, type: 'choice', text: '你如何看待工作中的压力？', options: ['A. 完全负面的，应该尽量避免', 'B. 有时会激励我表现得更好', 'C. 适度的压力有助于提高效率，但需要有效管理', 'D. 我不感到任何压力'] },
  { id: 7, type: 'choice', text: '当项目因外部因素（如客户变更需求）需要返工时，你会：', options: ['A. 感到愤怒，抱怨客户', 'B. 接受现实，迅速调整心态，专注于解决问题', 'C. 消极对待，敷衍了事', 'D. 拒绝修改，坚持原方案'] },
  { id: 8, type: 'open_ended', text: '请分享一次你在高压环境下保持冷静并做出正确决策的经历。你是如何做到的？', options: null },
  { id: 9, type: 'choice', text: '当你在工作中犯了严重错误时，你会：', options: ['A. 试图掩盖错误，避免被发现', 'B. 感到恐慌，无法正常工作', 'C. 立即承认错误，分析原因，积极补救', 'D. 推卸责任给他人'] },
  { id: 10, type: 'choice', text: '你通常如何应对工作中的挫折感？', options: ['A. 沉浸在负面情绪中，影响工作', 'B. 通过运动、娱乐等方式释放压力，然后重新投入工作', 'C. 向朋友或同事倾诉，寻求支持', 'D. 完全忽视挫折感，继续工作'] },
  { id: 11, type: 'choice', text: '当团队项目失败或被取消时，你会：', options: ['A. 感到个人失败，失去信心', 'B. 分析失败原因，从中学习，快速调整心态投入新项目', 'C. 责怪团队成员或外部因素', 'D. 考虑换工作或离职'] },
  { id: 12, type: 'open_ended', text: '描述一次你需要在短时间内学习全新技术或工具来完成任务的经历。当时压力有多大？你是如何应对的？', options: null },
  { id: 13, type: 'choice', text: '当面对模糊或不完整的需求时，你会：', options: ['A. 感到焦虑，等待明确指示', 'B. 基于现有信息做出假设并开始工作', 'C. 主动与相关方沟通，澄清需求', 'D. 拒绝开始工作，直到需求完全明确'] },
  { id: 14, type: 'choice', text: '你如何在高压下保持工作与生活的平衡？', options: ['A. 工作优先，牺牲个人时间', 'B. 严格区分工作和个人时间，不因工作牺牲生活质量', 'C. 根据情况灵活调整，但确保有恢复精力的时间', 'D. 没有特别的策略，随波逐流'] },
  { id: 15, type: 'choice', text: '当你感到工作压力影响身心健康时，你会：', options: ['A. 忽视身体信号，继续工作', 'B. 立即辞职', 'C. 寻求专业帮助，调整工作方式', 'D. 抱怨但不做任何改变'] },
  { id: 16, type: 'open_ended', text: '请分享一次你帮助团队成员应对压力或挫折的经历。你采取了什么措施？结果如何？', options: null },
  { id: 17, type: 'choice', text: '你认为自己在压力下的表现通常是：', options: ['A. 明显下降，容易出错', 'B. 与平时一样，不受影响', 'C. 有时会激发更好的表现，取决于压力类型', 'D. 总是表现得更好'] },
  { id: 18, type: 'choice', text: '为了提高自己的抗压能力，你最愿意尝试的方法是：', options: ['A. 增加工作负荷来锻炼自己', 'B. 学习时间管理和压力管理技巧', 'C. 改变对压力的看法，培养积极心态', 'D. 不需要提高，现在的抗压能力已经足够'] }
]

/** 学习能力测评题目（18题） */
export const learningQuestions: BackendPersonData[] = [
  { id: 1, type: 'choice', text: '当你需要学习一项全新的技术时，你通常会：', options: ['A. 等待公司组织培训', 'B. 找同事请教基础知识', 'C. 制定学习计划，结合官方文档、在线课程和实践项目系统学习', 'D. 直接开始尝试，边做边学'] },
  { id: 2, type: 'choice', text: '在学习新技术的过程中遇到难以理解的概念时，你会：', options: ['A. 跳过这个部分，学习其他内容', 'B. 反复阅读官方文档直到理解', 'C. 寻找不同的学习资源（视频、博客、示例代码），从多角度理解', 'D. 放弃学习这项技术'] },
  { id: 3, type: 'open_ended', text: '描述一次你成功掌握一项困难技能或技术的经历。你采用了什么学习方法？花了多长时间？', options: null },
  { id: 4, type: 'choice', text: '你更倾向于通过哪种方式学习新知识？', options: ['A. 阅读书籍和文档', 'B. 观看视频教程', 'C. 动手实践和做项目', 'D. 结合多种方式，根据内容选择最适合的方法'] },
  { id: 5, type: 'choice', text: '当你学习完一项新技术后，你会如何巩固所学？', options: ['A. 不再复习，需要时再查文档', 'B. 做笔记并定期回顾', 'C. 立即在实际项目中应用', 'D. 教授给他人，通过教学加深理解'] },
  { id: 6, type: 'choice', text: '你多久会主动学习一项与工作相关但非必需的新技术？', options: ['A. 很少，只在工作需要时学习', 'B. 偶尔，当有热门技术出现时', 'C. 定期，保持对技术趋势的敏感度', 'D. 经常，持续学习是我的习惯'] },
  { id: 7, type: 'open_ended', text: '请分享一次你从失败或错误中学习的经历。发生了什么？你学到了什么？', options: null },
  { id: 8, type: 'choice', text: '当你发现现有的解决方案不是最优时，你会：', options: ['A. 继续使用现有方案，避免风险', 'B. 在业余时间研究更好的方案', 'C. 主动学习新技术，提出改进方案', 'D. 等待其他人提出改进'] },
  { id: 9, type: 'choice', text: '你如何跟踪技术领域的最新发展？', options: ['A. 不主动跟踪，通过工作接触新技术', 'B. 关注技术新闻和博客', 'C. 订阅技术周刊，参加技术社区和会议', 'D. 系统学习，阅读论文和官方文档'] },
  { id: 10, type: 'choice', text: '在学习过程中，你如何处理信息过载的问题？', options: ['A. 感到 overwhelmed，停止学习', 'B. 随机选择部分内容深入学习', 'C. 根据目标和优先级筛选信息，有重点地学习', 'D. 试图学习所有内容'] },
  { id: 11, type: 'open_ended', text: '描述一次你需要快速学习新知识来解决紧急问题的经历。你是如何在时间压力下有效学习的？', options: null },
  { id: 12, type: 'choice', text: '你认为最有效的学习方式是：', options: ['A. 独自安静学习', 'B. 参加结构化课程', 'C. 在实践中学习，通过解决问题来掌握', 'D. 小组讨论和协作学习'] },
  { id: 13, type: 'choice', text: '当你学习的技术很快过时或被替代时，你会：', options: ['A. 感到沮丧，认为学习是浪费', 'B. 继续使用过时的技术', 'C. 分析新技术的优势，快速学习替代方案', 'D. 抱怨技术变化太快'] },
  { id: 14, type: 'choice', text: '你如何将学到的知识分享给团队？', options: ['A. 不主动分享，等别人来问', 'B. 在团队会议上做技术分享', 'C. 编写文档或博客，建立知识库', 'D. 在日常工作中指导他人'] },
  { id: 15, type: 'open_ended', text: '请分享一次你通过阅读源码或深入研究底层原理来解决问题的经历。这个过程给你带来了什么收获？', options: null },
  { id: 16, type: 'choice', text: '当你面对一个完全陌生的领域时，你首先会：', options: ['A. 感到恐惧，避免接触', 'B. 寻找该领域的入门教程和基础概念', 'C. 直接尝试解决具体问题', 'D. 咨询该领域的专家'] },
  { id: 17, type: 'choice', text: '你如何评估自己的学习效果？', options: ['A. 不需要评估，感觉学会了就是学会了', 'B. 通过完成测试或获得证书', 'C. 通过实际应用和项目成果', 'D. 通过教授他人和分享知识'] },
  { id: 18, type: 'choice', text: '为了保持持续学习的动力，你会：', options: ['A. 依赖外部压力（如工作要求）', 'B. 设定明确的学习目标和时间表', 'C. 加入学习小组，互相督促', 'D. 不需要特别措施，学习本身就是动力'] }
]

/** 从数组中随机选取 n 个元素 */
const pickRandom = <T>(arr: T[], n: number): T[] => {
  const shuffled = [...arr].sort(() => Math.random() - 0.5)
  return shuffled.slice(0, n)
}

/** 获取素质测评模拟题目（2道选择题 + 1道问答题） */
export const getPersonMockQuestions = (type: 'communication' | 'stress' | 'learning'): BackendPersonData[] => {
  let pool: BackendPersonData[] = []
  switch (type) {
    case 'communication':
      pool = communicationQuestions
      break
    case 'stress':
      pool = stressQuestions
      break
    case 'learning':
      pool = learningQuestions
      break
    default:
      return []
  }
  const choiceQuestions = pool.filter(q => q.type === 'choice')
  const openEndedQuestions = pool.filter(q => q.type === 'open_ended')
  const selected = [
    ...pickRandom(choiceQuestions, 2),
    ...pickRandom(openEndedQuestions, 1)
  ]
  // 重新编号
  return selected.map((q, i) => ({ ...q, id: i + 1 }))
}

// ==================== 技能/工具测评模拟数据 ====================

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
