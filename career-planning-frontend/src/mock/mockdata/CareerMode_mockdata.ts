export interface LearningRoadmapItem {
  stage: string
  title: string
  summary: string
  tags: string[]
}

export interface LearningFocusItem {
  label: string
  value: string
  hint: string
}

export interface JobFocusItem {
  title: string
  summary: string
  status: string
}

export interface JobMilestoneItem {
  title: string
  detail: string
}

export interface LearningModeFeatureItem {
  step: string
  title: string
  summary: string
  inputs: string[]
  outputs: string[]
  demoPoints: string[]
  differentiators: string[]
}

export const learningFocusCards: LearningFocusItem[] = [
  {
    label: '推荐发展方向',
    value: '前端 + AI 应用',
    hint: '适合用于比赛展示，既有技术深度也有作品表达空间',
  },
  {
    label: '建议优先补齐',
    value: '工程化与项目表达',
    hint: '把能力沉淀成可展示项目，比单纯刷知识点更适合短期冲刺',
  },
  {
    label: '下一个演示入口',
    value: '职业发展路径',
    hint: '适合作为视频里从学习阶段过渡到未来就业方向的说明',
  },
]

export const learningRoadmap: LearningRoadmapItem[] = [
  {
    stage: '01',
    title: '先明确主攻方向',
    summary: '围绕兴趣、项目经历和目标岗位，先把“学什么”这件事确定下来。',
    tags: ['方向探索', '目标聚焦'],
  },
  {
    stage: '02',
    title: '用项目补齐能力',
    summary: '优先做 1-2 个可演示的小型作品，把知识点变成可讲述的成果。',
    tags: ['项目沉淀', '能力展示'],
  },
  {
    stage: '03',
    title: '提前连接职业路径',
    summary: '结合系统已有报告能力，提前展示成长路线，而不是等到求职时再思考。',
    tags: ['成长规划', '报告联动'],
  },
]

export const learningModeFeatures: LearningModeFeatureItem[] = [
  {
    step: '1',
    title: '学习方向定位',
    summary: '先判断学生当前更适合投入的主攻赛道，不直接复用求职意向那套岗位填写逻辑。',
    inputs: ['兴趣方向标签', '当前专业/基础课背景', '目标学习方向', '每周可投入时长'],
    outputs: ['推荐主攻方向', '不建议分散投入的方向提醒', '阶段学习主题建议'],
    demoPoints: ['切换到学习模式后默认先看方向卡片', '展示“前端+AI 应用 / 数据分析 / 产品策划”不同推荐结果'],
    differentiators: ['不是填目标岗位，而是填目标学习赛道', '突出学习投入与成长节奏，不强调招聘 JD'],
  },
  {
    step: '2',
    title: '学习基础盘点',
    summary: '围绕课程基础、工具使用、实践熟练度做能力盘点，用 mock 数据给出短板诊断。',
    inputs: ['已掌握课程', '工具与软件熟悉度', '语言/技术基础', '薄弱知识点自评'],
    outputs: ['基础能力雷达', '待补齐能力清单', '优先学习顺序'],
    demoPoints: ['展示基础能力分层标签', '点击卡片即可看到“先补工程化，再补项目表达”等建议'],
    differentiators: ['不是证书优先，而是基础与掌握度优先', '更适合在校阶段，不依赖真实简历解析'],
  },
  {
    step: '3',
    title: '项目实战沉淀',
    summary: '把学习成果沉淀为可展示的小项目、课程设计、比赛作品，强调“学了以后做什么”。',
    inputs: ['课程项目经历', '比赛/训练营经历', '想做的作品类型', '希望补齐的实战经历'],
    outputs: ['推荐项目题目', '作品难度分级', '阶段成果清单'],
    demoPoints: ['演示不同方向对应不同项目建议', '展示“7 天可做 / 30 天可做”的成果路线'],
    differentiators: ['不是工作经历，而是项目练手与作品沉淀', '重点看可展示成果，不看实习时长'],
  },
  {
    step: '4',
    title: '成长潜力评估',
    summary: '通过学习习惯、复盘方式、表达协作等维度生成成长画像，用于视频演示非常直观。',
    inputs: ['学习习惯问卷', '复盘频率', '协作与表达情况', '创新案例'],
    outputs: ['成长潜力画像', '学习风险提示', '适合的训练方式建议'],
    demoPoints: ['展示潜力标签和建议语句自动变化', '把“拖延/执行力/表达”做成可视化提示'],
    differentiators: ['不是面试测评，而是成长性测评', '强调未来提升潜力，不强调录用匹配度'],
  },
  {
    step: '5',
    title: '阶段学习规划',
    summary: '输出 7 天、30 天、90 天的学习计划，形成完整的体验闭环。',
    inputs: ['目标周期', '近期任务优先级', '学习资源偏好', '阶段目标'],
    outputs: ['周计划 / 月计划', '资源推荐清单', '阶段里程碑'],
    demoPoints: ['一键生成阶段计划', '计划卡片、资源卡片和成果节点联动'],
    differentiators: ['不是求职行动清单，而是学习行动路线', '使用本地示例数据，无需等待后端接口'],
  },
]

export const jobFocusCards: JobFocusItem[] = [
  {
    title: '简历信息已可继续完善',
    summary: '保留现有简历上传与解析链路，适合直接演示“上传简历 -> 自动补全”的效果。',
    status: '优先展示',
  },
  {
    title: '岗位匹配与差距分析可直接串联',
    summary: '当前模式会更强调目标岗位、能力差距和行动建议，适合演示完整求职闭环。',
    status: '核心链路',
  },
  {
    title: '报告导出仍是最终成果页',
    summary: '可以继续保留你已有的导出 PDF / Word 演示，不需要额外改后端。',
    status: '结果输出',
  },
]

export const jobMilestones: JobMilestoneItem[] = [
  {
    title: '先补全求职画像',
    detail: '把教育背景、技能、项目和目标岗位补全，保证后续匹配和报告更完整。',
  },
  {
    title: '再进入岗位匹配',
    detail: '使用现有链路生成岗位推荐和差距分析，作为“找工作为主”的核心展示。',
  },
  {
    title: '最后展示报告与导出',
    detail: '把职业分析、建议和导出能力串成一条完整演示链路。',
  },
]
