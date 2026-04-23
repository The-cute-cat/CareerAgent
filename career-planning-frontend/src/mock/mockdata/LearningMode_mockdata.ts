/**
 * 学习模式（Learning Mode）专属测试数据
 *
 * 核心定位：面向大一至大三、仍处于成长阶段的学生
 * 与就业模式的区别：
 *   - 不是直接找工作，而是帮助用户明确方向、分析能力差距、规划学习路径
 *   - 强调"成长规划"，优先突出方向探索、能力提升建议、学习路径和职业图谱
 *   - 而不是简历优化和岗位匹配
 */

import type { Result } from '@/types/type'
import type { JobMatchItem } from '@/types/job-match'
import type { AxiosResponse } from 'axios'

// ==================== 工具函数 ====================

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

function wrapAsAxiosResponse<T>(result: Result<T>): AxiosResponse<Result<T>> {
  return {
    data: result,
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as any,
  }
}

// ==================== 一、学习画像基础数据 ====================

/** 学习模式下的学生基本信息 */
export interface LearningProfile {
  name: string
  grade: string          // 大一 / 大二 / 大三 / 大四
  major: string[]        // 专业路径
  school: string         // 学校名称
  gpa: string            // GPA 或成绩概况
  interests: string[]    // 兴趣方向标签
  weeklyStudyHours: number // 每周可投入学习时长
  targetDirection: string // 当前目标方向（模糊的，非具体岗位）
  selfEvaluation: string  // 自我评价描述
}

/** 模拟学习画像 */
export const mockLearningProfile: LearningProfile = {
  name: '李明',
  grade: '大二',
  major: ['计算机类', '软件工程'],
  school: '某理工大学',
  gpa: '3.4 / 4.0 （专业前 30%）',
  interests: ['前端开发', 'AI 应用', '产品设计'],
  weeklyStudyHours: 20,
  targetDirection: '',
  selfEvaluation: '对前端和 AI 方向都有兴趣，做过几个小项目但不够系统化，希望能找到更清晰的学习路线。',
}

// ==================== 二、学习模式雷达图维度与分数 ====================

/** 学习模式六维能力评估 —— 维度定义与就业模式不同 */
export interface LearningRadarScores {
  /** 专业基础：课程知识、编程语法、算法数据结构的掌握程度 */
  专业基础: number
  /** 实践动手：项目经验、代码量、工具使用熟练度 */
  实践动手: number
  /** 学习自驱：自学能力、信息检索、时间管理、目标感 */
  学习自驱: number
  /** 表达展示：作品呈现、技术写作、口头表达 */
  表达展示: number
  /** 创新探索：好奇心、尝试新技术、独立思考 */
  创新探索: number
  /** 协作适应：团队合作、沟通协调、抗压韧性 */
  协作适应: number
}

/** 模拟学习模式雷达分数 */
export const mockLearningRadarScores: LearningRadarScores = {
  专业基础: 68,
  实践动手: 55,
  学习自驱: 82,
  表达展示: 48,
  创新探索: 72,
  协作适应: 70,
}

/** 学习模式雷达维度配置（用于 ECharts 等图表组件） */
export const learningRadarIndicator = [
  { name: '专业基础', max: 100 },
  { name: '实践动手', max: 100 },
  { name: '学习自驱', max: 100 },
  { name: '表达展示', max: 100 },
  { name: '创新探索', max: 100 },
  { name: '协作适应', max: 100 },
]

/** 学习模式雷达图完整数据 */
export const learningRadarData = {
  indicator: learningRadarIndicator,
  value: Object.values(mockLearningRadarScores),
  name: '学习能力画像',
}

// ==================== 三、方向推荐数据（替代岗位匹配）====================

/** 推荐的学习方向 */
export interface LearningDirectionItem {
  id: string
  direction: string           // 推荐方向名称（非岗位名）
  matchScore: number          // 匹配度 0-100
  reason: string              // 为什么推荐这个方向
  currentAdvantage: string    // 当前已有的优势
  gaps: string[]              // 需要补齐的能力差距
  suggestedFirstStep: string  // 建议的第一步行动
  difficulty: '容易入门' | '适中' | '有挑战'
  timeToBasic: string         // 达到基础可用所需时间
  relatedCareers: string[]    // 对应的职业方向（远期参考）
  resources: string[]         // 推荐资源
  roadmapSummary: string      // 学习路径概览
}

/** 学习方向推荐列表 */
export const mockLearningDirections: LearningDirectionItem[] = [
  {
    id: 'dir_frontend_ai',
    direction: '前端 + AI 应用开发',
    matchScore: 88,
    reason: '你已有 Vue 基础和 AI 项目经历，且学习自驱力强。这个方向能快速产出可演示的作品，适合比赛和作品集积累。',
    currentAdvantage: 'Vue3 组件化能力扎实，有 AI Agent 项目经验，对新技术保持好奇',
    gaps: ['TypeScript 深度使用还不够', '缺少完整上线的项目案例', '工程化构建工具链不熟'],
    suggestedFirstStep: '用 TypeScript 重构一个已有项目，同时补充项目上线部署经验',
    difficulty: '适中',
    timeToBasic: '2-3 个月',
    relatedCareers: ['前端工程师', 'AI 应用工程师', '全栈工程师'],
    resources: ['Vue 3 官方文档', 'TypeScript Handbook', 'Vite 构建指南', 'AI 工程落地实战'],
    roadmapSummary: 'Vue3 进阶 → TypeScript 深入 → AI 能力接入 → 工程化与部署 → 作品集打磨',
  },
  {
    id: 'dir_data_analysis',
    direction: '数据分析与可视化',
    matchScore: 76,
    reason: '你的数学基础不错，且具备一定的逻辑思维能力。数据分析方向门槛相对友好，能快速产出有价值的分析报告。',
    currentAdvantage: '逻辑思维清晰，有一定统计学基础（课程），对数据敏感',
    gaps: ['Python 数据处理库不熟悉', '缺乏真实数据分析项目', '可视化工具使用经验不足'],
    suggestedFirstStep: '完成一个 Python 数据清洗+可视化的端到端小项目（如校园消费数据分析）',
    difficulty: '容易入门',
    timeToBasic: '1-2 个月',
    relatedCareers: ['数据分析师', 'BI 工程师', '数据产品经理'],
    resources: ['Python 数据分析手册', 'Matplotlib/Seaborn 教程', 'Kaggle 入门赛题', 'SQL 必知必会'],
    roadmapSummary: 'Python 数据处理 → SQL 数据查询 → 可视化图表 → 分析报告撰写 → 真实数据集实战',
  },
  {
    id: 'dir_product_strategy',
    direction: '产品策划与设计思维',
    matchScore: 70,
    reason: '你在团队协作和创新探索维度表现良好，且有跨领域兴趣。产品策划方向看重综合思考能力和表达能力。',
    currentAdvantage: '团队协作意识强，有创新意识，能从用户角度思考问题',
    gaps: ['需求分析方法论缺失', '原型设计工具不熟', '缺少完整的产品方案输出'],
    suggestedFirstStep: '选择一个校园场景（如选课/食堂/社团），做一份完整的产品需求文档（PRD）+ 原型',
    difficulty: '有挑战',
    timeToBasic: '2-3 个月',
    relatedCareers: ['产品经理', '用户体验设计师', '产品运营'],
    resources: ['《人人都是产品经理》', 'Figma 原型教程', 'PRD 写作模板', '用户研究方法'],
    roadmapSummary: '产品思维建立 → 需求分析训练 → 原型设计工具 → 用户研究方法 → 完整方案输出',
  },
  {
    id: 'dir_backend_java',
    direction: 'Java 后端开发',
    matchScore: 62,
    reason: '你目前的技术栈以 JavaScript 为主，Java 方向需要较大的语言切换投入。但如果对服务端架构感兴趣，值得作为备选长期方向。',
    currentAdvantage: '编程基础扎实，有面向对象概念理解，数据库基础知识尚可',
    gaps: ['Java 语言本身需从头学', 'Spring 生态完全陌生', '缺少后端项目经验'],
    suggestedFirstStep: '先用 Java 完成一个控制台 CRUD 小系统，感受后端开发的基本流程',
    difficulty: '有挑战',
    timeToBasic: '3-4 个月',
    relatedCareers: ['Java 开发工程师', 'Java后端工程师', '全栈工程师'],
    resources: ['《Java 核心技术》', 'Spring Boot 入门', 'MySQL 实战45讲', 'LeetCode 刷题'],
    roadmapSummary: 'Java 语言基础 → Spring Boot 入门 → MySQL 实践 → 微服务概念了解 → 分布式基础',
  },
]

// ==================== 四、能力短板诊断数据 ====================

/** 能力短板项 */
export interface WeaknessItem {
  dimension: string       // 所属维度
  item: string            // 具体短板项
  level: '严重' | '明显' | '轻微'
  impact: string          // 这个短板会怎么影响发展
  suggestion: string      // 改进建议
  priority: number        // 修复优先级（数字越小越优先）
  estimatedTime: string   // 预计补齐时间
}

/** 能力短板诊断结果 */
export const mockWeaknessDiagnosis: WeaknessItem[] = [
  {
    dimension: '表达展示',
    item: '项目成果呈现不足',
    level: '严重',
    impact: '即使做了好项目也难以在面试/答辩中脱颖而出，影响作品集说服力',
    suggestion: '为每个项目整理 README 文档，录制 2 分钟功能演示视频，练习 STAR 法则讲述项目故事',
    priority: 1,
    estimatedTime: '2 周',
  },
  {
    dimension: '实践动手',
    item: '缺少完整的端到端项目经验',
    level: '明显',
    impact: '当前项目多为课程作业级别，缺少从设计到部署的完整闭环体验',
    suggestion: '挑选一个感兴趣的方向，做一个包含前后端/数据/部署的完整项目',
    priority: 2,
    estimatedTime: '4-6 周',
  },
  {
    dimension: '专业基础',
    item: 'TypeScript 类型系统掌握不深',
    level: '明显',
    impact: '限制了在大型项目和开源协作中的参与深度，也影响代码质量',
    suggestion: '系统学习 TS 类型体操，在现有项目中全面替换为 TypeScript',
    priority: 3,
    estimatedTime: '2-3 周',
  },
  {
    dimension: '实践动手',
    item: '构建工程化工具链不熟悉',
    level: '轻微',
    impact: '项目开发和交付效率较低，不利于团队协作规范',
    suggestion: '学习 Vite/Webpack 配置、ESLint/Prettier 代码规范、Git 工作流',
    priority: 4,
    estimatedTime: '1-2 周',
  },
  {
    dimension: '协作适应',
    item: '技术写作与文档能力待提升',
    level: '轻微',
    impact: '影响开源贡献、技术博客质量和团队知识沉淀',
    suggestion: '开始写技术笔记，每学会一个知识点就输出一篇总结博文',
    priority: 5,
    estimatedTime: '持续',
  },
]

// ==================== 五、学习阶段规划数据（替代职业发展报告）====================

/** 阶段性任务 */
export interface LearningTask {
  taskName: string
  description: string
  priority: '高' | '中' | '低'
  estimatedTime: string
  skillTarget: string
  successCriteria: string
  resources: Array<{ title: string; category: string }>
}

/** 阶段里程碑 */
export interface LearningMilestone {
  milestoneName: string
  targetDate: string
  keyResults: string[]
  tasks: LearningTask[]
}

/** 学习规划数据结构 */
export interface LearningPlanData {
  studentSummary: string                // 学生总体画像概述
  recommendedPrimaryDirection: string   // 主推荐方向
  recommendedSecondaryDirection: string // 备选方向
  currentStageAssessment: string        // 当前所处阶段的判断
  shortTermPlan: {
    duration: string                     // 短期计划周期
    goal: string                         // 短期目标
    focusAreas: string[]                 // 重点聚焦领域
    milestones: LearningMilestone[]
    quickWins: string[]                  // 快速见效的行动
  }
  midTermPlan: {
    duration: string                     // 中期计划周期
    goal: string                         // 中期目标
    skillRoadmap: string[]               // 技能路线图
    milestones: LearningMilestone[]
    nextPhaseHint: string                // 下一阶段过渡提示
  }
  actionChecklist: string[]             // 行动清单
  riskAlerts: string[]                  // 风险提示
  tips: string[]                        // 建议
}

function createLResource(title: string, category = '学习资源') {
  return { title, category }
}

function createLearningTask(
  taskName: string,
  description: string,
  priority: '高' | '中' | '低',
  estimatedTime: string,
  skillTarget: string,
  successCriteria: string,
  resources: Array<{ title: string; category: string }> = [],
): LearningTask {
  return { taskName, description, priority, estimatedTime, skillTarget, successCriteria, resources }
}

/** 按推荐方向生成学习规划 */
export const mockLearningPlans: Record<string, LearningPlanData> = {
  dir_frontend_ai: {
    studentSummary: '你是一名大二软件工程专业学生，已具备 Vue3 基础和初步的 AI 项目经验，学习自驱力强。当前最需要在"项目完整性"和"表达能力"两个方向突破，把零散的知识点串联成可展示的成长轨迹。',
    recommendedPrimaryDirection: '前端 + AI 应用开发',
    recommendedSecondaryDirection: '数据分析与可视化',
    currentStageAssessment: '处于「基础夯实→项目沉淀」的关键过渡期，适合用 1-2 个精品项目打通学习闭环。',
    shortTermPlan: {
      duration: '4-8 周',
      goal: '产出 1 个可线上演示的前端 + AI 融合项目，并形成标准化的项目展示材料。',
      focusAreas: ['TypeScript 深入', '项目工程化', '作品集呈现', 'AI 能力接入'],
      milestones: [
        {
          milestoneName: '完成核心项目开发',
          targetDate: '第 2-4 周',
          keyResults: ['确定项目选题与技术方案', '完成前端界面开发', '接入 AI 功能模块', '基本功能可运行演示'],
          tasks: [
            createLearningTask(
              '确定项目选题与技术栈',
              '选择一个既有实际价值又能展示 AI 能力的题目（如智能学习助手/校园问答机器人），明确技术边界和 MVP 范围。',
              '高',
              '3 天',
              '项目规划能力',
              '输出一页纸的项目方案（功能列表、技术栈、MVP 定义、时间线）。',
              [createLResource('项目选题参考清单', '模板'), createLResource('MVP 思维方法', '方法论')],
            ),
            createLearningTask(
              'TypeScript 全面重构',
              '将现有 Vue 项目或新建项目全程使用 TypeScript，严格类型约束。',
              '高',
              '1 周',
              'TypeScript 实战能力',
              '项目中无 any 类型，核心逻辑有完善的类型定义和接口约束。',
              [createLResource('TS 类型体操入门', '教程'), createLResource('Vue3 + TS 最佳实践', '指南')],
            ),
            createLearningTask(
              'AI 功能模块接入',
              '通过 API 接入 LLM 能力（对话/问答/摘要等），实现至少一个 AI 交互功能。',
              '中',
              '1 周',
              'AI 应用集成能力',
              'AI 功能可正常响应用户输入，有基本的错误处理和 loading 状态。',
              [createLResource('LLM API 接入示例', '代码'), createLResource('Prompt 设计指南', '参考')],
            ),
          ],
        },
      ],
      quickWins: [
        '为现有项目补一份完整的 README',
        '注册 Vercel/Cloudflare Pages 账号，了解部署流程',
        '用 Figma 画一张项目截图用于展示',
      ],
    },
    midTermPlan: {
      duration: '2-4 个月',
      goal: '从前端开发者成长为具备全链路交付能力的"复合型学习者"，形成差异化竞争力。',
      skillRoadmap: ['组件库设计', 'Node.js 辅助', '性能优化', '开源参与', '技术输出'],
      milestones: [
        {
          milestoneName: '形成个人技术品牌',
          targetDate: '第 3 个月',
          keyResults: ['GitHub 绿墙连续提交', '发布 2-3 篇技术文章', '项目获得 Star 或正向反馈'],
          tasks: [
            createLearningTask(
              '搭建个人技术站',
              '用 GitHub Pages 或 Vercel 部署个人主页/技术博客，统一展示项目和文章。',
              '中',
              '1 周',
              '个人品牌建设',
              '站点可公开访问，内容包含项目展示、技术文章和 About Me。',
              [createLResource('GitHub Pages 教程', '教程'), createLResource('技术博客主题模板', '资源')],
            ),
          ],
        },
      ],
      nextPhaseHint: '当积累了 2-3 个完整项目和技术输出后，可以开始关注实习机会或参加高质量的比赛（如互联网+、挑战杯），将学习能力转化为职场竞争力。',
    },
    actionChecklist: [
      '确定一个主攻方向并坚持 2 个月以上',
      '完成 TypeScript 深入学习和项目迁移',
      '产出一个可在线访问的项目 Demo',
      '写第一篇技术博客/学习笔记',
      '加入一个技术社区或开源项目',
    ],
    riskAlerts: [
      '注意避免"方向频繁切换"，每个方向至少坚持 3 个月再评估是否调整',
      '不要陷入"只看不练"，每学一个知识点都要有小项目验证',
      '警惕"完美主义陷阱"，先做出 MVP 再迭代优化',
    ],
    tips: [
      '大二大三是最宝贵的自由探索期，多试错成本最低',
      '项目不在于多而在于精，一个好项目胜过五个半成品',
      '学会记录学习过程，复盘比盲目赶路更有价值',
      '找到志同道合的学习伙伴，互相督促效果更好',
    ],
  },

  dir_data_analysis: {
    studentSummary: '你具备良好的逻辑思维和数学基础，对数据和规律敏感。目前缺少系统的数据分析技能栈和实际项目经验，但这个方向的入门门槛相对友好，非常适合作为快速产出成果的选择。',
    recommendedPrimaryDirection: '数据分析与可视化',
    recommendedSecondaryDirection: '前端 + AI 应用开发',
    currentStageAssessment: '处于「方向探索」的早期阶段，适合先用一个小而完整的数据项目确认兴趣和天赋。',
    shortTermPlan: {
      duration: '3-6 周',
      goal: '用 Python 完成一个端到端的数据分析小项目，覆盖数据获取、清洗、分析和可视化的完整流程。',
      focusAreas: ['Python 数据处理', 'SQL 查询', '数据可视化', '分析报告写作'],
      milestones: [
        {
          milestoneName: '完成首个数据分析项目',
          targetDate: '第 3-5 周',
          keyResults: ['选定数据集并明确分析问题', '完成数据清洗和预处理', '产出 3-5 张有效图表', '撰写分析结论和建议'],
          tasks: [
            createLearningTask(
              'Python 数据分析环境搭建与基础',
              '安装 Anaconda/Miniconda，熟悉 Jupyter Notebook，掌握 Pandas/NumPy 基本操作。',
              '高',
              '1 周',
              'Python 数据处理基础',
              '能用 Pandas 读取 CSV/Excel 并进行基本的数据筛选、分组、聚合操作。',
              [createLResource('Pandas 官方教程', '教程'), createLResource('数据集下载平台（Kaggle/Tianchi）', '资源')],
            ),
            createLearningTask(
              '数据可视化实战',
              '使用 Matplotlib/Seaborn/ECharts 完成至少 5 种不同类型的图表（柱状图/折线图/散点图/热力图/饼图）。',
              '高',
              '1 周',
              '数据可视化能力',
              '图表配色合理、标注完整，能有效传达数据洞察。',
              [createLResource('Seaborn 可视化教程', '教程'), createLResource('数据可视化最佳实践', '指南')],
            ),
          ],
        },
      ],
      quickWins: [
        '找一个感兴趣的开放数据集（如 Kaggle Beginner 级别）',
        '用 Excel 先手动做一遍分析思路，再用代码实现',
        '看看 Tableau/PowerBI 的免费版，了解商业 BI 工具的长处',
      ],
    },
    midTermPlan: {
      duration: '2-3 个月',
      goal: '建立完整的数据分析技能体系，能够独立完成从数据采集到决策建议的全链路工作。',
      skillRoadmap: ['SQL 高级查询', '统计分析方法', '自动化报表', '机器学习入门', '业务理解'],
      milestones: [
        {
          milestoneName: '完成进阶分析项目',
          targetDate: '第 6-8 周',
          keyResults: ['使用 SQL 进行复杂数据查询', '应用统计检验方法', '产出可交互的分析 Dashboard'],
          tasks: [
            createLearningTask(
              'SQL 查询能力提升',
              '掌握多表 JOIN、子查询、窗口函数等高级 SQL 操作，能在真实数据库上进行数据分析。',
              '中',
              '2 周',
              'SQL 数据分析能力',
              '能用 SQL 独立完成多表关联分析和复杂聚合计算。',
              [createLResource('SQL 必知必会', '书籍'), createLResource('SQLZOO 练习平台', '练习')],
            ),
          ],
        },
      ],
      nextPhaseHint: '当掌握了 Python 数据分析和 SQL 之后，可以进一步向数据工程（ETL/数仓）或机器学习方向发展，也可以结合前端技能做数据可视化大屏类项目。',
    },
    actionChecklist: [
      '完成第一个 Python 数据分析项目',
      '掌握 SQL 基础查询（SELECT/WHERE/GROUP BY/HAVING/JOIN）',
      '读一本数据分析入门书籍',
      '参加一次 Kaggle/Tianchi 入门赛',
      '写一篇数据分析报告（可以发博客）',
    ],
    riskAlerts: [
      '不要一开始就陷在数学公式里，先动手跑通代码再补理论',
      '避免"工具收集癖"，精通一种语言/工具比浅尝辄止十个更有价值',
      '注意数据的合规性和隐私保护意识',
    ],
    tips: [
      '数据分析的核心不是工具，而是"从数据中发现问题和答案的思维"',
      '每做一个项目都问自己：这些数据说明了什么？能支撑什么决策？',
      '学会讲故事——数据分析的最终产物是"有洞察的故事"',
    ],
  },

  dir_product_strategy: {
    studentSummary: '你在协作与创新维度表现优秀，具备良好的同理心和用户视角。产品策划方向能发挥你的综合优势，但目前缺少系统的方法论训练和可展示的产品方案作品。',
    recommendedPrimaryDirection: '产品策划与设计思维',
    recommendedSecondaryDirection: '前端 + AI 应用开发',
    currentStageAssessment: '处于「兴趣试探→方法建立」的阶段，适合先通过低成本的产品练习来验证兴趣和能力。',
    shortTermPlan: {
      duration: '4-6 周',
      goal: '围绕一个真实的校园/生活痛点，完成从用户调研到原型设计的完整产品方案输出。',
      focusAreas: ['需求分析方法', '用户调研技巧', '原型设计工具', 'PRD 文档写作'],
      milestones: [
        {
          milestoneName: '产出首份完整产品方案',
          targetDate: '第 4-6 周',
          keyResults: ['完成用户访谈（至少 5 人）', '产出用户旅程地图', '完成高保真交互原型', '撰写 PRD 文档（核心模块）'],
          tasks: [
            createLearningTask(
              '用户调研实践',
              '选择身边的一个痛点（如选课困难/社团管理/二手交易），进行 5-10 人用户访谈，整理用户需求和痛点清单。',
              '高',
              '1-2 周',
              '用户研究能力',
              '产出用户访谈记录、痛点分类矩阵和用户 Persona。',
              [createLResource('用户访谈指南', '方法论'), createLResource('Persona 模板', '模板')],
            ),
            createLearningTask(
              '原型设计与工具掌握',
              '使用 Figma 完成产品的高保真原型（至少包含 8 个核心页面/状态）。',
              '高',
              '2 周',
              '原型设计能力',
              '原型包含完整的交互流程、合理的布局和信息层级。',
              [createLResource('Figma 官方教程', '教程'), createLResource('UI 设计规范参考', '资源')],
            ),
          ],
        },
      ],
      quickWins: [
        '每天用一个 APP 时花 5 分钟分析它的交互设计',
        '关注 3 个产品经理公众号/博主，阅读行业分析文章',
        '画一张自己常用产品的信息架构图',
      ],
    },
    midTermPlan: {
      duration: '2-3 个月',
      goal: '建立完整的产品思维体系，能够独立完成需求分析、方案设计和产品推进。',
      skillRoadmap: ['竞品分析', '数据驱动决策', '项目管理', '技术理解力', '行业认知'],
      milestones: [
        {
          milestoneName: '完成竞品分析与方案迭代',
          targetDate: '第 6-8 周',
          keyResults: ['完成 3 个竞品深度分析', '基于反馈优化产品方案', '形成个人产品方法论笔记'],
          tasks: [
            createLearningTask(
              '竞品分析与差异化定位',
              '选择目标领域的 3-5 个竞品，从功能、体验、商业模式等维度做对比分析。',
              '中',
              '1-2 周',
              '竞品分析能力',
              '产出竞品分析矩阵和差异化定位策略。',
              [createLResource('竞品分析框架模板', '模板'), createLResource('产品分析方法论', '书籍')],
            ),
          ],
        },
      ],
      nextPhaseHint: '产品方向非常依赖实践经验，建议尽早寻找产品实习/运营实习机会，或在校园内承担产品型角色（如学生会数字化负责人、社团产品负责人）。',
    },
    actionChecklist: [
      '完成一次真实用户调研（5 人以上）',
      '用 Figma 做出一个完整的高保真原型',
      '写一份 PRD 文档（核心模块即可）',
      '读 2 本产品相关书籍（《人人都是产品经理》《启示录》）',
      '分析 3 个你喜欢的产品并写出分析笔记',
    ],
    riskAlerts: [
      '产品岗位竞争激烈，建议搭配一项硬技能（如前端/数据）作为"保底"',
      '避免"空谈产品不落地"，尽量推动自己的方案被实际使用',
      '不要忽视技术理解力——懂技术是产品经理的重要优势',
    ],
    tips: [
      '产品思维的核心是"在约束条件下为用户创造最大价值"',
      '最好的产品练习就是解决自己身边的真实问题',
      '学会说"不"——产品经理最重要的能力之一是优先级判断',
    ],
  },
}

/** 获取默认学习规划（按最高匹配方向） */
export function getDefaultMockLearningPlan(): LearningPlanData {
  return mockLearningPlans['dir_frontend_ai']!
}

/** 根据方向 ID 获取对应学习规划 */
export function getMockLearningPlanByDirection(directionId?: string): LearningPlanData {
  if (directionId && mockLearningPlans[directionId]) {
    return mockLearningPlans[directionId]
  }
  return getDefaultMockLearningPlan()
}

// ==================== 六、学习发展阶段图谱（替代职业晋升图谱）====================

/** 学习阶段节点 */
export interface LearningGraphNode {
  id: string
  label: string
  x: number
  y: number
  data: Record<string, any>
  color: string
  stroke: string
  textColor?: string
}

/** 学习阶段连线 */
export interface LearningGraphEdge {
  source: string
  target: string
  label: string
  color?: string
}

/** 学习成长阶段数据 */
export const learningGrowthStages = [
  { stage: '大一 · 探索期', level: '广泛接触', score: 50, ability: '方向摸索' },
  { stage: '大二 · 夯实期', level: '基础建设', score: 65, ability: '技能积累' },
  { stage: '大三 · 深耕期', level: '定向突破', score: 80, ability: '能力成型' },
  { stage: '大四 · 过渡期', level: '成果转化', score: 90, ability: '就业/深造准备' },
]

/** 学习成长路径节点 —— 以"前端 + AI"方向为例 */
export const learningPathNodes: LearningGraphNode[] = [
  {
    id: 'l1',
    label: '编程基础入门',
    x: 400,
    y: 40,
    data: {
      stage: '大一上',
      desc: '打牢根基',
      requirements: ['掌握一门编程语言基础', '理解基本数据结构', '学会使用 Git'],
      skills: { '编程语法': 50, '数据结构': 40, '工具使用': 55 },
      status: '已完成',
    },
    color: '#F0FDF4',
    stroke: '#22C55E',
  },
  {
    id: 'l2',
    label: 'Web 前端基础',
    x: 400,
    y: 150,
    data: {
      stage: '大一 ~ 大二上',
      desc: '前端三件套',
      requirements: ['HTML/CSS/JS 扎实', '能独立完成静态页面', '了解浏览器基本原理'],
      skills: { 'HTML/CSS': 65, 'JavaScript': 60, '浏览器原理': 45 },
      status: '进行中',
    },
    color: '#DCFCE7',
    stroke: '#22C55E',
  },
  {
    id: 'l3',
    label: '框架与工程化',
    x: 400,
    y: 260,
    data: {
      stage: '大二',
      desc: '现代前端开发',
      requirements: ['掌握 Vue3/React 框架', '理解组件化开发', '会用构建工具（Vite/Webpack）'],
      skills: { 'Vue3/React': 70, '工程化': 50, 'TypeScript': 45 },
      status: '待学习',
    },
    color: '#BBF7D0',
    stroke: '#16A34A',
  },
  {
    id: 'l4',
    label: 'AI 能力融合',
    x: 250,
    y: 380,
    data: {
      stage: '大二下 ~ 大三上',
      desc: 'AI 应用方向',
      requirements: ['了解 LLM 基本概念', '能调用 AI API', '实现 AI 交互功能'],
      skills: { 'Prompt Engineering': 55, 'API 对接': 50, 'RAG 基础': 30 },
      status: '待学习',
    },
    color: '#86EFAC',
    stroke: '#15803D',
  },
  {
    id: 'l5',
    label: '全栈扩展',
    x: 550,
    y: 380,
    data: {
      stage: '大三',
      desc: '全栈能力',
      requirements: ['Node.js 基础', '数据库操作（MySQL/MongoDB）', 'RESTful API 设计'],
      skills: { 'Node.js': 35, '数据库': 40, 'API 设计': 30 },
      status: '待学习',
    },
    color: '#86EFAC',
    stroke: '#15803D',
  },
  {
    id: 'l6',
    label: '作品集与输出',
    x: 250,
    y: 500,
    data: {
      stage: '大三下',
      desc: '成果沉淀',
      requirements: ['2-3 个完整项目', '技术博客/开源', '可演示的在线作品'],
      skills: { '项目完整性': 45, '技术写作': 35, '个人品牌': 25 },
      status: '远期目标',
    },
    color: '#4ADE80',
    stroke: '#166534',
  },
  {
    id: 'l7',
    label: '实习 / 竞赛 / 深造',
    x: 550,
    y: 500,
    data: {
      stage: '大三 ~ 大四',
      desc: '下一步选择',
      requirements: ['实习面试准备', '竞赛参与（互联网+/挑战杯）', '考研/留学规划'],
      skills: { '面试能力': 30, '竞赛经验': 20, '学术能力': 25 },
      status: '远期目标',
    },
    color: '#22C55E',
    stroke: '#166534',
    textColor: '#fff',
  },
]

/** 学习成长路径连线 */
export const learningPathEdges: LearningGraphEdge[] = [
  { source: 'l1', target: 'l2', label: '1学期', color: '#22C55E' },
  { source: 'l2', target: 'l3', label: '1-2学期', color: '#22C55E' },
  { source: 'l3', target: 'l4', label: 'AI 方向', color: '#3B82F6' },
  { source: 'l3', target: 'l5', label: '全栈方向', color: '#F59E0B' },
  { source: 'l4', target: 'l6', label: '成果沉淀', color: '#22C55E' },
  { source: 'l5', target: 'l7', label: '就业/深造', color: '#A855F7' },
  { source: 'l6', target: 'l7', label: '竞争力转化', color: '#EC4899' },
]

// ==================== 七、学习模式首页数据 ====================

/** 学习模式首页雷达图 */
export const learningHomeRadarData = {
  indicator: [
    { name: '专业基础', max: 100 },
    { name: '实践动手', max: 100 },
    { name: '学习自驱', max: 100 },
    { name: '表达展示', max: 100 },
    { name: '创新探索', max: 100 },
    { name: '协作适应', max: 100 },
  ],
  value: Object.values(mockLearningRadarScores),
  name: '学习能力画像',
}

/** 学习模式快捷入口 */
export const learningQuickActions = [
  {
    title: '学习方向',
    icon: 'Reading', // Element Plus 图标引用
    desc: '定位当前最适合投入的学习赛道',
    color: '#14b8a6',
    route: '/career-form',
  },
  {
    title: '能力盘点',
    icon: 'Management',
    desc: '查看基础能力与短板诊断',
    color: '#0ea5e9',
    route: '/career-form',
  },
  {
    title: '项目规划',
    icon: 'Notebook',
    desc: '生成适合演示的作品与项目路线',
    color: '#f59e0b',
    route: '/development-map',
  },
  {
    title: '成长报告',
    icon: 'Opportunity',
    desc: '查看学习路径与阶段建议',
    color: '#6366f1',
    route: '/report',
  },
]

// ==================== 八、学习模式表单默认数据（替代简历填写）====================

/** 学习模式下表单的默认填充数据 */
export const mockLearningFormData = {
  education: '本科',
  major: ['计算机类', '软件工程'],
  graduationDate: '2027-06',
  languages: [
    { type: '英语', level: 'CET-4', other: '' },
  ],
  certificates: [],
  certificateOther: '',
  skills: [
    { name: 'HTML/CSS', credibility: 75 },
    { name: 'JavaScript', credibility: 65 },
    { name: 'Vue 3', credibility: 60 },
    { name: 'Python', credibility: 50 },
    { name: 'Git', credibility: 70 },
  ],
  tools: [
    { name: 'VS Code', proficiency: '熟练' },
    { name: 'Figma', proficiency: '了解' },
    { name: 'Chrome DevTools', proficiency: '一般' },
  ],
  codeAbility: { links: 'https://github.com/learning-student' },
  projects: [
    {
      isCompetition: false,
      name: '校园活动报名小程序',
      desc: '使用 Vue3 + Element Plus 开发的校园活动报名系统，包含活动浏览、报名、签到等功能，作为课程设计项目完成',
    },
    {
      isCompetition: true,
      name: 'AI 校园问答助手',
      desc: '基于 LLM API 的校园信息问答 Demo，获得院级创新创业大赛三等奖',
    },
  ],
  internships: [],  // 学习模式下通常无实习
  innovation: '在课程设计中引入了 AI 问答功能，让传统的信息展示页面具备了智能交互能力',
  targetJob: '',     // 学习模式下不填具体岗位
  targetIndustries: [],
  priorities: [
    { value: 'growth', label: '能力成长' },
    { value: 'interest', label: '兴趣驱动' },
    { value: 'project', label: '项目沉淀' },
  ],
  learningInfo: {
    grade: '大二',
    weeklyHours: 20,
    preferredStyle: '视频课程 + 项目实战',
    weakPoints: ['项目不够完整', '不知道学什么方向', '学了就忘'],
    completedCourses: ['数据结构与算法', '计算机网络', '数据库原理', 'Web 前端开发'],
    interestedTracks: ['前端开发', 'AI 应用', '产品设计'],
  },
}

// ==================== 九、学习模式测评题目（侧重学习场景）====================

/** 测评选项 */
interface QuizOption {
  label: string
  value: string
  text: string
}

/** 测评题目 */
interface QuizQuestion {
  id: number
  question: string
  options: QuizOption[]
  correctAnswer?: string
}

/** 学习风格测评题库 —— 了解学生的学习偏好 */
export const learningStyleQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: '当你学习一项全新技能时，你更喜欢哪种方式？',
    options: [
      { label: 'A', value: 'A', text: '先看系统性的教程/视频，整体了解后再动手' },
      { label: 'B', value: 'B', text: '直接上手做项目，遇到问题再查资料解决' },
      { label: 'C', value: 'C', text: '找一篇好的博客/文档，跟着一步步实操' },
      { label: 'D', value: 'D', text: '报一门课或训练营，跟着老师系统学习' },
    ],
  },
  {
    id: 2,
    question: '你在学习过程中最容易遇到什么障碍？',
    options: [
      { label: 'A', value: 'A', text: '不知道该学什么，方向太多反而迷茫' },
      { label: 'B', value: 'B', text: '学了后面忘前面，知识不成体系' },
      { label: 'C', value: 'C', text: '只看不练，眼高手低' },
      { label: 'D', value: 'D', text: '遇到难题容易放弃，缺乏持续动力' },
    ],
  },
  {
    id: 3,
    question: '你每周大约能投入多少小时自主学习新技术？',
    options: [
      { label: 'A', value: 'A', text: '少于 5 小时（学业较忙）' },
      { label: 'B', value: 'B', text: '5-10 小时（适度安排）' },
      { label: 'C', value: 'C', text: '10-20 小时（投入较多）' },
      { label: 'D', value: 'D', text: '20 小时以上（几乎全部业余时间）' },
    ],
  },
  {
    id: 4,
    question: '你更倾向于哪种类型的学习项目？',
    options: [
      { label: 'A', value: 'A', text: '模仿经典项目（如博客/商城/Todo）' },
      { label: 'B', value: 'B', text: '解决自己生活中的实际问题' },
      { label: 'C', value: 'C', text: '参加比赛/训练营的任务驱动型项目' },
      { label: 'D', value: 'D', text: '参与开源项目的 Issue/PR 贡献' },
    ],
  },
  {
    id: 5,
    question: '学完一项技能后，你会怎么验证自己真的学会了？',
    options: [
      { label: 'A', value: 'A', text: '能不看文档独立写出来' },
      { label: 'B', value: 'B', text: '能给别人讲解清楚' },
      { label: 'C', value: 'C', text: '能用它做出一个完整的小项目' },
      { label: 'D', value: 'D', text: '通过了相关的考试或认证' },
    ],
  },
]

/** 兴趣方向探索测评 —— 帮助发现潜在方向 */
export const interestExplorationQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: '以下哪类任务让你最有成就感？',
    options: [
      { label: 'A', value: 'A', text: '做出一个漂亮的界面，别人用了都说好看' },
      { label: 'B', value: 'B', text: '从一堆杂乱的数据里找出规律和结论' },
      { label: 'C', value: 'C', text: '设计一个功能，解决了大家的实际困扰' },
      { label: 'D', value: 'D', text: '写出高效优雅的代码，运行速度飞快' },
    ],
  },
  {
    id: 2,
    question: '你平时最关注哪类技术资讯？',
    options: [
      { label: 'A', value: 'A', text: '新的前端框架/UI 趋势/设计灵感' },
      { label: 'B', value: 'B', text: 'AI 新模型/机器学习论文/数据科学应用' },
      { label: 'C', value: 'C', text: '新产品分析/行业动态/创业故事' },
      { label: 'D', value: 'D', text: '底层技术原理/架构设计/性能优化' },
    ],
  },
  {
    id: 3,
    question: '如果给你一周自由时间做一个东西，你会选择？',
    options: [
      { label: 'A', value: 'A', text: '一个精美的个人网站/App' },
      { label: 'B', value: 'B', text: '一个数据分析报告（比如分析自己的消费习惯）' },
      { label: 'C', value: 'C', text: '一个产品原型 + 需求文档' },
      { label: 'D', value: 'D', text: '一个高性能的工具/库/算法实现' },
    ],
  },
  {
    id: 4,
    question: '你在团队项目中通常扮演什么角色？',
    options: [
      { label: 'A', value: 'A', text: '负责界面和交互的实现者' },
      { label: 'B', value: 'B', text: '负责数据分析和决策支持的参谋' },
      { label: 'C', value: 'C', text: '负责统筹规划和需求管理的组织者' },
      { label: 'D', value: 'D', text: '负责核心技术攻坚的实现者' },
    ],
  },
  {
    id: 5,
    question: '你对未来 3 年的职业期待是什么？',
    options: [
      { label: 'A', value: 'A', text: '成为能独立做出优秀产品的前端专家' },
      { label: 'B', value: 'B', text: '成为用数据驱动决策的分析师' },
      { label: 'C', value: 'C', text: '成为能定义和推动产品的产品经理' },
      { label: 'D', value: 'D', text: '成为深耕技术底层的工程师/架构师' },
    ],
  },
]

// ==================== 十、学习模式 API 模拟函数 ====================

/**
 * 模拟获取学习方向推荐
 * 替代就业模式的人岗匹配接口
 */
export async function mockGetLearningDirectionApi(
  delayMs: number = 800
): Promise<AxiosResponse<Result<LearningDirectionItem[]>>> {
  await delay(delayMs)
  return wrapAsAxiosResponse({
    code: 200,
    msg: 'success',
    data: mockLearningDirections,
  })
}

/**
 * 模拟获取学习规划报告
 * 替代就业模式的职业发展报告
 */
export async function mockGetLearningPlanApi(
  directionId?: string,
  delayMs: number = 800
): Promise<AxiosResponse<Result<LearningPlanData>>> {
  await delay(delayMs)
  const plan = getMockLearningPlanByDirection(directionId)
  return wrapAsAxiosResponse({
    code: 200,
    msg: 'success',
    data: plan,
  })
}

/**
 * 模拟获取能力短板诊断
 * 就业模式无此功能，学习模式独有
 */
export async function mockGetWeaknessDiagnosisApi(
  delayMs: number = 600
): Promise<AxiosResponse<Result<WeaknessItem[]>>> {
  await delay(delayMs)
  return wrapAsAxiosResponse({
    code: 200,
    msg: 'success',
    data: mockWeaknessDiagnosis,
  })
}

// ==================== 十一、学习模式人岗匹配数据（面向大二大三学生）====================

/** 学习模式专属人岗匹配数据 - 5个适合学生阶段投递的岗位 */
export const mockLearningJobMatchItems: JobMatchItem[] = [
  {
    job_id: "job_learn_001",
    score: 0.8654321098765432,
    raw_data: {
      job_id: "job_learn_001",
      job_name: "前端开发实习生",
      profiles: {
        basic_requirements: {
          degree: "本科",
          major: "计算机/软件工程/设计",
          certificates: "无",
          internship_requirement: "无硬性要求",
          experience_years: "应届/在校",
          special_requirements: "有作品集或GitHub项目优先"
        },
        professional_skills: {
          core_skills: "HTML/CSS/JavaScript, Vue/React基础",
          tool_capabilities: "Git, VS Code, Chrome DevTools",
          domain_knowledge: "互联网产品",
          language_requirements: "CET4",
          project_requirements: "有前端项目练习或课程设计"
        },
        professional_literacy: {
          communication: "中",
          teamwork: "高",
          stress_management: "中",
          logic_thinking: "中",
          ethics: "高"
        },
        development_potential: {
          learning_ability: "高",
          innovation: "中",
          leadership: "低",
          career_orientation: "技术",
          adaptability: "高"
        },
        job_attributes: {
          salary_competitiveness: "中",
          industry: "互联网/科技公司",
          vertical_promotion_path: "实习→初级→中级→高级前端工程师",
          prerequisite_roles: "前端基础知识",
          lateral_transfer_directions: "UI开发,全栈开发,移动端开发",
          social_demand: "高",
          industry_trend: "持续增长"
        }
      }
    },
    deep_analysis: {
      can_apply: true,
      score: 88,
      missing_key_skills: [
        "商业级项目经验（目前多为课程作业级别）",
        "前端工程化工具深入使用（Webpack/Vite配置）",
        "性能优化实践经验"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "本科在校生，有基础项目经验",
          current: "大二软件工程专业，有Vue3课程设计和AI项目前端部分",
          gap_analysis: "符合要求：学历专业对口，已有前端项目练习，满足实习生基础门槛。"
        },
        {
          dimension: "职业技能",
          required: "HTML/CSS/JS基础，Vue/React框架入门，Git版本控制",
          current: "Vue3生态熟练，TypeScript日常使用，Git基础操作掌握，有完整组件开发经验",
          gap_analysis: "高度匹配：技能栈精准覆盖岗位要求，AI项目展示了复杂交互实现能力。"
        },
        {
          dimension: "职业素养",
          required: "团队协作意识，学习意愿强",
          current: "前端校队成员，6个月实习经历，AI项目独立完成",
          gap_analysis: "匹配良好：已有协作经验和实习背景，软素养达标。"
        },
        {
          dimension: "发展潜力",
          required: "学习能力强，技术热情高",
          current: "自学Vue3/TypeScript/LLM，技术博客输出，持续学习",
          gap_analysis: "优秀匹配：学习自驱力强，技术取向明确，是理想的实习生人选。"
        }
      ],
      actionable_advice: "整理现有的AI项目和课程设计，制作一个简洁的在线作品集（可用GitHub Pages部署）。补充1-2个响应式布局或CSS动画案例，展示基础功底。投递时强调学习能力和成长潜力。",
      all_analysis: "非常适合投递！前端基础扎实，Vue3生态熟练，有AI项目经验加分。作为大二学生已具备不错的技术储备，建议在毕业前积累2-3段实习经历，毕业后可直接冲击大厂校招。"
    }
  },
  {
    job_id: "job_learn_002",
    score: 0.7987654321098765,
    raw_data: {
      job_id: "job_learn_002",
      job_name: "Python数据分析实习生",
      profiles: {
        basic_requirements: {
          degree: "本科",
          major: "计算机/数学/统计/经济",
          certificates: "无",
          internship_requirement: "无",
          experience_years: "在校/应届",
          special_requirements: "熟悉Python基础，对数据敏感"
        },
        professional_skills: {
          core_skills: "Python, Pandas/NumPy, 数据可视化",
          tool_capabilities: "Jupyter Notebook, Excel, SQL基础",
          domain_knowledge: "数据分析,业务理解",
          language_requirements: "CET4",
          project_requirements: "有数据分析相关课程作业或竞赛"
        },
        professional_literacy: {
          communication: "中",
          teamwork: "中",
          stress_management: "中",
          logic_thinking: "高",
          ethics: "高"
        },
        development_potential: {
          learning_ability: "高",
          innovation: "中",
          leadership: "低",
          career_orientation: "技术/分析",
          adaptability: "高"
        },
        job_attributes: {
          salary_competitiveness: "中",
          industry: "互联网/金融/咨询",
          vertical_promotion_path: "数据分析实习生→数据分析师→高级分析师→数据分析专家",
          prerequisite_roles: "Python基础,逻辑思维",
          lateral_transfer_directions: "数据产品,商业分析,算法工程师",
          social_demand: "高",
          industry_trend: "快速增长"
        }
      }
    },
    deep_analysis: {
      can_apply: true,
      score: 82,
      missing_key_skills: [
        "Pandas/NumPy数据处理库深入使用",
        "SQL数据查询能力",
        "真实业务场景数据分析经验"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "本科在校生，Python基础，对数据敏感",
          current: "软件工程专业，Python课程基础，有AI项目调用LLM API经验",
          gap_analysis: "基本匹配：Python语法熟悉，但缺少数据分析专用库经验。"
        },
        {
          dimension: "职业技能",
          required: "Python数据处理，可视化，SQL查询",
          current: "Python基础良好，但Pandas/NumPy未系统学习，SQL仅课程级别",
          gap_analysis: "存在差距：编程基础可迁移，需快速补充数据分析工具链。"
        },
        {
          dimension: "职业素养",
          required: "逻辑思维强，细心严谨",
          current: "算法课程和项目开发验证了逻辑能力，有数据敏感度",
          gap_analysis: "匹配良好：逻辑思维是优势，适合数据分析工作。"
        },
        {
          dimension: "发展潜力",
          required: "学习能力强，对数据有兴趣",
          current: "学习能力强，但技术栈偏前端，数据分析方向需重新建立",
          gap_analysis: "潜力尚可：学习能力强是优势，但需要评估是否愿意转向数据方向。"
        }
      ],
      actionable_advice: "如果对数据方向感兴趣，建议2-3周内突击学习Pandas（官方10分钟入门+一个Kaggle Titanic入门赛），完成一个校园数据小项目（如食堂消费分析）。可边学边投递，强调学习能力和编程基础。",
      all_analysis: "适合作为拓展方向投递。前端背景不是障碍，反而可以成为数据可视化的优势。数据分析门槛相对友好，且市场需求大。建议先完成一个小项目验证兴趣，再决定是否深入。"
    }
  },
  {
    job_id: "job_learn_003",
    score: 0.7456789012345678,
    raw_data: {
      job_id: "job_learn_003",
      job_name: "产品经理实习生（技术向）",
      profiles: {
        basic_requirements: {
          degree: "本科",
          major: "计算机/软件工程优先",
          certificates: "无",
          internship_requirement: "有产品或技术实习优先",
          experience_years: "在校/应届",
          special_requirements: "需提交产品分析或方案作品"
        },
        professional_skills: {
          core_skills: "需求分析，原型设计，文档写作",
          tool_capabilities: "Figma/Axure，Office，思维导图",
          domain_knowledge: "互联网产品方法论",
          language_requirements: "CET4",
          project_requirements: "有校园产品项目或产品分析报告"
        },
        professional_literacy: {
          communication: "高",
          teamwork: "高",
          stress_management: "中",
          logic_thinking: "高",
          ethics: "中"
        },
        development_potential: {
          learning_ability: "高",
          innovation: "高",
          leadership: "中",
          career_orientation: "产品/综合",
          adaptability: "高"
        },
        job_attributes: {
          salary_competitiveness: "中",
          industry: "互联网/科技公司",
          vertical_promotion_path: "产品实习生→产品专员→产品经理→高级产品经理",
          prerequisite_roles: "产品思维，沟通能力",
          lateral_transfer_directions: "项目经理，运营，创业者",
          social_demand: "高",
          industry_trend: "平稳"
        }
      }
    },
    deep_analysis: {
      can_apply: true,
      score: 78,
      missing_key_skills: [
        "系统化产品方法论",
        "需求分析和用户研究经验",
        "原型设计工具熟练使用",
        "产品文档写作能力"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "本科，技术背景优先，有作品",
          current: "软件工程大二，技术背景符合，但无产品类作品",
          gap_analysis: "存在差距：技术背景是优势，但缺少产品思维和作品证明。"
        },
        {
          dimension: "职业技能",
          required: "需求分析，原型设计，文档写作",
          current: "有项目开发经验，理解技术实现，但产品方法论缺失",
          gap_analysis: "部分匹配：技术理解力是技术向PM的优势，但需补充产品方法论。"
        },
        {
          dimension: "职业素养",
          required: "沟通协调高，逻辑思维高",
          current: "团队协作经验丰富，逻辑清晰，有创新意识",
          gap_analysis: "匹配良好：软素养维度达标，具备PM潜质。"
        },
        {
          dimension: "发展潜力",
          required: "学习高，创新高，综合取向",
          current: "学习能力强，有AI项目创新经验，但职业取向偏技术",
          gap_analysis: "方向待定：能力匹配，但需明确是否愿意转向产品方向。"
        }
      ],
      actionable_advice: "作为技术向PM方向尝试：选择一款常用APP做一份深度分析报告（用户痛点+改进方案），用Figma做一个简单原型。投递时强调技术背景优势——懂技术的产品经理更懂 feasibility。",
      all_analysis: "可作为转型探索方向。技术背景是技术向PM的核心竞争力，但产品方向与开发方向差异较大。建议先通过实习体验确认兴趣，如果不喜欢可以退回技术路线。"
    }
  },
  {
    job_id: "job_learn_004",
    score: 0.6823456789012345,
    raw_data: {
      job_id: "job_learn_004",
      job_name: "AI应用开发实习生",
      profiles: {
        basic_requirements: {
          degree: "本科",
          major: "计算机/人工智能/软件工程",
          certificates: "无",
          internship_requirement: "有AI项目经验优先",
          experience_years: "在校/应届",
          special_requirements: "了解LLM基础，有AI项目实践"
        },
        professional_skills: {
          core_skills: "Python, LLM API调用, Prompt Engineering",
          tool_capabilities: "OpenAI API, LangChain, Git",
          domain_knowledge: "大模型应用,AI产品设计",
          language_requirements: "CET4",
          project_requirements: "有AI应用项目或课程设计"
        },
        professional_literacy: {
          communication: "中",
          teamwork: "高",
          stress_management: "中",
          logic_thinking: "高",
          ethics: "高"
        },
        development_potential: {
          learning_ability: "高",
          innovation: "高",
          leadership: "中",
          career_orientation: "技术/AI",
          adaptability: "高"
        },
        job_attributes: {
          salary_competitiveness: "高",
          industry: "AI/互联网",
          vertical_promotion_path: "AI实习生→AI应用工程师→AI产品经理/技术专家",
          prerequisite_roles: "Python,AI基础",
          lateral_transfer_directions: "算法工程,AI产品,创业",
          social_demand: "极高",
          industry_trend: "爆发式增长"
        }
      }
    },
    deep_analysis: {
      can_apply: true,
      score: 75,
      missing_key_skills: [
        "LangChain等AI应用框架深入使用",
        "RAG系统搭建经验",
        "Prompt Engineering系统化实践"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "本科，有AI项目经验",
          current: "有AI校园问答助手项目（LLM API调用），获院级比赛奖项",
          gap_analysis: "符合要求：已有AI项目经验，满足实习门槛。"
        },
        {
          dimension: "职业技能",
          required: "Python, LLM API, Prompt Engineering",
          current: "有LLM API调用经验，AI Agent项目实践，前端集成能力强",
          gap_analysis: "良好匹配：已有AI应用层经验，但框架使用停留在基础调用。"
        },
        {
          dimension: "职业素养",
          required: "创新意识，学习能力强",
          current: "创新探索维度高分，自学LLM技术，有创新项目",
          gap_analysis: "高度匹配：创新能力和学习热情与AI方向契合。"
        },
        {
          dimension: "发展潜力",
          required: "学习高，创新高，AI方向",
          current: "学习自驱力强，AI项目创新，职业取向技术",
          gap_analysis: "优秀匹配：AI是最契合的发展方向之一。"
        }
      ],
      actionable_advice: "非常适合投递！这是当前最热门的方向。完善AI问答助手项目：补充技术文档、录制演示视频、尝试接入更多功能（如知识库）。深入学习LangChain或LlamaIndex，做一个RAG小Demo。",
      all_analysis: "强烈推荐投递！AI方向与背景高度契合，已有项目经验加分。AI应用开发是近期最火热的赛道，人才缺口大。建议深耕这个方向，毕业后可冲击AI独角兽或大厂的AI部门。"
    }
  },
  {
    job_id: "job_learn_005",
    score: 0.6234567890123456,
    raw_data: {
      job_id: "job_learn_005",
      job_name: "软件测试实习生",
      profiles: {
        basic_requirements: {
          degree: "本科",
          major: "计算机/软件工程",
          certificates: "无",
          internship_requirement: "无",
          experience_years: "在校/应届",
          special_requirements: "细心严谨，有编程基础"
        },
        professional_skills: {
          core_skills: "测试理论，用例设计，Bug追踪",
          tool_capabilities: "Postman, Charles, 数据库工具",
          domain_knowledge: "软件测试流程",
          language_requirements: "CET4",
          project_requirements: "了解测试基本流程"
        },
        professional_literacy: {
          communication: "中",
          teamwork: "中",
          stress_management: "中",
          logic_thinking: "中",
          ethics: "高"
        },
        development_potential: {
          learning_ability: "高",
          innovation: "中",
          leadership: "低",
          career_orientation: "技术",
          adaptability: "高"
        },
        job_attributes: {
          salary_competitiveness: "中",
          industry: "互联网/软件",
          vertical_promotion_path: "测试实习生→测试工程师→高级测试→测试开发/专家",
          prerequisite_roles: "细心,基础测试知识",
          lateral_transfer_directions: "测试开发,开发工程师,产品经理",
          social_demand: "中",
          industry_trend: "自动化测试增长"
        }
      }
    },
    deep_analysis: {
      can_apply: true,
      score: 70,
      missing_key_skills: [
        "系统化测试理论知识",
        "自动化测试工具使用",
        "性能/安全测试基础"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "本科，细心，有编程基础",
          current: "软件工程大二，编程基础扎实，项目经验丰富",
          gap_analysis: "超出要求：学历专业完全符合，技术背景优于一般测试实习生。"
        },
        {
          dimension: "职业技能",
          required: "测试理论，用例设计，工具使用",
          current: "开发能力强，但测试专业知识缺失，未系统学习测试方法",
          gap_analysis: "方向偏差：技术能力可迁移，但需从零学习测试专业领域知识。"
        },
        {
          dimension: "职业素养",
          required: "细心严谨，沟通协作",
          current: "实习经历和项目开发验证了协作能力，代码质量意识好",
          gap_analysis: "匹配良好：软素养适合测试岗位，严谨度足够。"
        },
        {
          dimension: "发展潜力",
          required: "学习能力高，技术取向",
          current: "学习能力强，技术热情高，职业取向技术开发",
          gap_analysis: "方向偏差：能力适合，但测试方向与当前技术追求不完全一致。"
        }
      ],
      actionable_advice: "可作为保底选择投递。测试岗位门槛相对较低，是进入大厂的一条路径。建议投递测试开发方向（需要编码能力），而非纯功能测试。入职后可内部转岗到开发，或走测试开发技术路线。",
      all_analysis: "适合作为保底投递。测试岗位市场需求稳定，且大厂测试岗待遇不错。但考虑到当前前端技能已经比较扎实，建议优先投递前端开发实习。测试可作为保底选项，入职后转向测试开发或内部转岗。"
    }
  }
]

/**
 * 模拟获取学习模式人岗匹配结果API
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockGetLearningJobMatchResultApi(
  delayMs: number = 800
): Promise<AxiosResponse<Result<JobMatchItem[]>>> {
  await delay(delayMs)
  return wrapAsAxiosResponse({
    code: 200,
    msg: 'success',
    data: mockLearningJobMatchItems
  })
}
