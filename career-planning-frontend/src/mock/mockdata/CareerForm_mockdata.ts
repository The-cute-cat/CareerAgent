/**
 * CareerForm.vue 模拟数据
 */

/** 选项类型 */
export interface Option {
  label: string
  value: string
  children?: Option[]
}

/** 测评题目选项 */
export interface QuizOption {
  label: string
  value: string
  text: string
}

/** 测评题目 */
export interface QuizQuestion {
  id: number
  question: string
  options: QuizOption[]
  correctAnswer?: string
}

/** 专业选项数据 */
export const majorOptions: Option[] = [
  {
    value: '计算机类',
    label: '计算机类',
    children: [
      { value: '软件工程', label: '软件工程' },
      { value: '计算机科学与技术', label: '计算机科学与技术' },
      { value: '网络工程', label: '网络工程' },
      { value: '信息安全', label: '信息安全' },
      { value: '物联网工程', label: '物联网工程' },
      { value: '数字媒体技术', label: '数字媒体技术' },
      { value: '智能科学与技术', label: '智能科学与技术' },
      { value: '空间信息与数字技术', label: '空间信息与数字技术' },
      { value: '电子与计算机工程', label: '电子与计算机工程' },
      { value: '数据科学与大数据技术', label: '数据科学与大数据技术' },
      { value: '网络空间安全', label: '网络空间安全' },
      { value: '新媒体技术', label: '新媒体技术' },
      { value: '电影制作', label: '电影制作' },
      { value: '保密技术', label: '保密技术' },
      { value: '服务科学与工程', label: '服务科学与工程' },
      { value: '虚拟现实技术', label: '虚拟现实技术' },
      { value: '区块链工程', label: '区块链工程' },
      { value: '密码科学与技术', label: '密码科学与技术' }
    ]
  },
  {
    value: '电子信息类',
    label: '电子信息类',
    children: [
      { value: '电子信息工程', label: '电子信息工程' },
      { value: '电子科学与技术', label: '电子科学与技术' },
      { value: '通信工程', label: '通信工程' },
      { value: '微电子科学与工程', label: '微电子科学与工程' },
      { value: '光电信息科学与工程', label: '光电信息科学与工程' },
      { value: '信息工程', label: '信息工程' },
      { value: '广播电视工程', label: '广播电视工程' },
      { value: '水声工程', label: '水声工程' },
      { value: '电子封装技术', label: '电子封装技术' },
      { value: '集成电路设计与集成系统', label: '集成电路设计与集成系统' },
      { value: '医学信息工程', label: '医学信息工程' },
      { value: '电磁场与无线技术', label: '电磁场与无线技术' },
      { value: '电波传播与天线', label: '电波传播与天线' },
      { value: '电子信息科学与技术', label: '电子信息科学与技术' },
      { value: '电信工程及管理', label: '电信工程及管理' },
      { value: '应用电子技术教育', label: '应用电子技术教育' },
      { value: '人工智能', label: '人工智能' },
      { value: '海洋信息工程', label: '海洋信息工程' },
      { value: '柔性电子学', label: '柔性电子学' },
      { value: '智能测控工程', label: '智能测控工程' }
    ]
  },
  {
    value: '自动化类',
    label: '自动化类',
    children: [
      { value: '自动化', label: '自动化' },
      { value: '轨道交通信号与控制', label: '轨道交通信号与控制' },
      { value: '机器人工程', label: '机器人工程' },
      { value: '邮政工程', label: '邮政工程' },
      { value: '核电技术与控制工程', label: '核电技术与控制工程' },
      { value: '智能装备与系统', label: '智能装备与系统' },
      { value: '工业智能', label: '工业智能' },
      { value: '智能工程与创意设计', label: '智能工程与创意设计' }
    ]
  },
  {
    value: '数学类',
    label: '数学类',
    children: [
      { value: '数学与应用数学', label: '数学与应用数学' },
      { value: '信息与计算科学', label: '信息与计算科学' },
      { value: '数理基础科学', label: '数理基础科学' },
      { value: '数据计算及应用', label: '数据计算及应用' }
    ]
  },
  {
    value: '统计学类',
    label: '统计学类',
    children: [
      { value: '统计学', label: '统计学' },
      { value: '应用统计学', label: '应用统计学' },
      { value: '数据科学', label: '数据科学' },
      { value: '生物统计学', label: '生物统计学' }
    ]
  },
  {
    value: '集成电路科学与工程类',
    label: '集成电路科学与工程类',
    children: [
      { value: '集成电路设计与集成系统', label: '集成电路设计与集成系统' }
    ]
  },
  {
    value: '国家安全学类',
    label: '国家安全学类',
    children: [
      { value: '信息安全', label: '信息安全' }
    ]
  },
  {
    value: '交叉工程类',
    label: '交叉工程类',
    children: [
      { value: '碳中和科学与工程', label: '碳中和科学与工程' },
      { value: '低空技术与工程', label: '低空技术与工程' },
      { value: '智能分子工程', label: '智能分子工程' },
      { value: '时空信息工程', label: '时空信息工程' },
      { value: '智慧应急', label: '智慧应急' },
      { value: '工业软件', label: '工业软件' }
    ]
  },
  {
    value: '管理科学与工程类',
    label: '管理科学与工程类',
    children: [
      { value: '信息管理与信息系统', label: '信息管理与信息系统' },
      { value: '大数据管理与应用', label: '大数据管理与应用' },
      { value: '计算金融', label: '计算金融' }
    ]
  },
  {
    value: '电子商务类',
    label: '电子商务类',
    children: [
      { value: '电子商务', label: '电子商务' },
      { value: '跨境电子商务', label: '跨境电子商务' }
    ]
  },
  {
    value: '物流管理与工程类',
    label: '物流管理与工程类',
    children: [
      { value: '物流工程', label: '物流工程' }
    ]
  }
]

/** 沟通能力测评题库 */
export const communicationQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: '当团队成员之间产生分歧时，你会如何处理？',
    options: [
      { label: 'A', value: 'A', text: '主动协调，倾听各方意见，寻求共识' },
      { label: 'B', value: 'B', text: '保持中立，让团队自行解决' },
      { label: 'C', value: 'C', text: '支持最有说服力的观点' },
      { label: 'D', value: 'D', text: '向上级汇报，请求决策' }
    ]
  },
  {
    id: 2,
    question: '在跨部门协作中，遇到对方不配合的情况，你会？',
    options: [
      { label: 'A', value: 'A', text: '了解对方需求，寻找双赢方案' },
      { label: 'B', value: 'B', text: '坚持原则，按流程推进' },
      { label: 'C', value: 'C', text: '寻求上级介入协调' },
      { label: 'D', value: 'D', text: '暂时搁置，等待时机' }
    ]
  },
  {
    id: 3,
    question: '向领导汇报工作时，你更倾向于？',
    options: [
      { label: 'A', value: 'A', text: '先说结果，再补充关键细节' },
      { label: 'B', value: 'B', text: '按时间顺序详细描述过程' },
      { label: 'C', value: 'C', text: '准备书面材料，让领导自己看' },
      { label: 'D', value: 'D', text: '等领导询问再回答' }
    ]
  },
  {
    id: 4,
    question: '客户提出不合理需求时，你会如何回应？',
    options: [
      { label: 'A', value: 'A', text: '耐心解释，提供替代方案' },
      { label: 'B', value: 'B', text: '直接拒绝，说明原因' },
      { label: 'C', value: 'C', text: '先答应下来，再内部协商' },
      { label: 'D', value: 'D', text: '请示上级如何处理' }
    ]
  },
  {
    id: 5,
    question: '在会议中，你发现有人误解了你的观点，你会？',
    options: [
      { label: 'A', value: 'A', text: '立即澄清，确保理解一致' },
      { label: 'B', value: 'B', text: '会后单独沟通解释' },
      { label: 'C', value: 'C', text: '通过他人转达正确信息' },
      { label: 'D', value: 'D', text: '不解释，用行动证明' }
    ]
  }
]

/** 抗压能力测评题库 */
export const stressQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: '面对紧急且困难的任务 deadline，你的应对方式是？',
    options: [
      { label: 'A', value: 'A', text: '立即制定计划，分解任务，加班加点完成' },
      { label: 'B', value: 'B', text: '评估可行性，必要时申请延期或求助' },
      { label: 'C', value: 'C', text: '保持冷静，按部就班推进' },
      { label: 'D', value: 'D', text: '焦虑但强迫自己硬撑完成' }
    ]
  },
  {
    id: 2,
    question: '当工作出现重大失误时，你的第一反应是？',
    options: [
      { label: 'A', value: 'A', text: '立即承认错误，积极寻找补救方案' },
      { label: 'B', value: 'B', text: '分析原因，避免类似问题再次发生' },
      { label: 'C', value: 'C', text: '担心被批评，想办法掩盖' },
      { label: 'D', value: 'D', text: '情绪低落，需要时间恢复' }
    ]
  },
  {
    id: 3,
    question: '连续加班一周后，你会如何调整自己？',
    options: [
      { label: 'A', value: 'A', text: '适当休息，运动放松，保持工作生活平衡' },
      { label: 'B', value: 'B', text: '坚持完成工作，结束后再好好休息' },
      { label: 'C', value: 'C', text: '向领导反映情况，申请调休' },
      { label: 'D', value: 'D', text: '抱怨但继续硬撑' }
    ]
  },
  {
    id: 4,
    question: '面对多方同时施压的情况，你会？',
    options: [
      { label: 'A', value: 'A', text: '按优先级排序，逐一沟通处理' },
      { label: 'B', value: 'B', text: '先处理最紧急的事项' },
      { label: 'C', value: 'C', text: '同时推进所有事项' },
      { label: 'D', value: 'D', text: '感到 overwhelmed，不知从何开始' }
    ]
  },
  {
    id: 5,
    question: '项目失败后，你的态度是？',
    options: [
      { label: 'A', value: 'A', text: '总结经验教训，为下一次做准备' },
      { label: 'B', value: 'B', text: '分析责任归属，明确改进方向' },
      { label: 'C', value: 'C', text: '沮丧一段时间，然后重新振作' },
      { label: 'D', value: 'D', text: '怀疑自己的能力' }
    ]
  }
]

/** 学习能力测评题库 */
export const learningQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: '遇到不熟悉的技术领域需要快速上手，你会怎么做？',
    options: [
      { label: 'A', value: 'A', text: '系统学习基础，边学边实践' },
      { label: 'B', value: 'B', text: '直接找相关项目练手，遇到问题再查资料' },
      { label: 'C', value: 'C', text: '请教有经验的同事，快速入门' },
      { label: 'D', value: 'D', text: '阅读官方文档和优质教程' }
    ]
  },
  {
    id: 2,
    question: '学习新技术时，你更喜欢的方式是？',
    options: [
      { label: 'A', value: 'A', text: '看视频教程，跟着做项目' },
      { label: 'B', value: 'B', text: '阅读书籍和文档，深入理解原理' },
      { label: 'C', value: 'C', text: '参加培训课程，系统学习' },
      { label: 'D', value: 'D', text: '加入技术社区，与他人交流学习' }
    ]
  },
  {
    id: 3,
    question: '当学习遇到瓶颈时，你通常会？',
    options: [
      { label: 'A', value: 'A', text: '换个角度思考，尝试不同方法' },
      { label: 'B', value: 'B', text: '暂时放下，过一段时间再回来' },
      { label: 'C', value: 'C', text: '寻求他人帮助，讨论解决方案' },
      { label: 'D', value: 'D', text: '反复练习，直到突破' }
    ]
  },
  {
    id: 4,
    question: '对于技术更新迭代，你的态度是？',
    options: [
      { label: 'A', value: 'A', text: '保持好奇心，主动学习新技术' },
      { label: 'B', value: 'B', text: '等技术成熟稳定后再学习' },
      { label: 'C', value: 'C', text: '根据工作需求选择性学习' },
      { label: 'D', value: 'D', text: '专注于精通现有技术栈' }
    ]
  },
  {
    id: 5,
    question: '如何检验自己是否真正掌握了一项新技术？',
    options: [
      { label: 'A', value: 'A', text: '能独立完成一个实际项目' },
      { label: 'B', value: 'B', text: '能向他人讲解清楚技术原理' },
      { label: 'C', value: 'C', text: '通过相关认证考试' },
      { label: 'D', value: 'D', text: '能解决实际工作中遇到的问题' }
    ]
  }
]

/** 专业技能题库 - Python */
export const pythonQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'Python 中，以下哪个函数用于获取列表的长度？',
    options: [
      { label: 'A', value: 'A', text: 'size()' },
      { label: 'B', value: 'B', text: 'len()' },
      { label: 'C', value: 'C', text: 'length()' },
      { label: 'D', value: 'D', text: 'count()' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 2,
    question: 'Python 中，以下哪个不是可变数据类型？',
    options: [
      { label: 'A', value: 'A', text: 'list' },
      { label: 'B', value: 'B', text: 'dict' },
      { label: 'C', value: 'C', text: 'tuple' },
      { label: 'D', value: 'D', text: 'set' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 3,
    question: 'Python 中，以下哪个关键字用于定义函数？',
    options: [
      { label: 'A', value: 'A', text: 'func' },
      { label: 'B', value: 'B', text: 'def' },
      { label: 'C', value: 'C', text: 'function' },
      { label: 'D', value: 'D', text: 'define' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 4,
    question: 'Python 中，以下哪个方法用于向列表末尾添加元素？',
    options: [
      { label: 'A', value: 'A', text: 'add()' },
      { label: 'B', value: 'B', text: 'append()' },
      { label: 'C', value: 'C', text: 'push()' },
      { label: 'D', value: 'D', text: 'insert()' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 5,
    question: 'Python 中，以下哪个符号用于表示注释？',
    options: [
      { label: 'A', value: 'A', text: '//' },
      { label: 'B', value: 'B', text: '/* */' },
      { label: 'C', value: 'C', text: '#' },
      { label: 'D', value: 'D', text: '--' }
    ],
    correctAnswer: 'C'
  }
]

/** 专业技能题库 - Java */
export const javaQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'Java 中，以下哪个关键字用于创建类的实例？',
    options: [
      { label: 'A', value: 'A', text: 'new' },
      { label: 'B', value: 'B', text: 'create' },
      { label: 'C', value: 'C', text: 'instance' },
      { label: 'D', value: 'D', text: 'make' }
    ],
    correctAnswer: 'A'
  },
  {
    id: 2,
    question: 'Java 中，以下哪个不是访问修饰符？',
    options: [
      { label: 'A', value: 'A', text: 'public' },
      { label: 'B', value: 'B', text: 'private' },
      { label: 'C', value: 'C', text: 'protected' },
      { label: 'D', value: 'D', text: 'static' }
    ],
    correctAnswer: 'D'
  },
  {
    id: 3,
    question: 'Java 中，String 类存储在哪个区域？',
    options: [
      { label: 'A', value: 'A', text: '栈内存' },
      { label: 'B', value: 'B', text: '堆内存' },
      { label: 'C', value: 'C', text: '字符串常量池' },
      { label: 'D', value: 'D', text: '方法区' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 4,
    question: 'Java 中，以下哪个接口用于实现列表数据结构？',
    options: [
      { label: 'A', value: 'A', text: 'Set' },
      { label: 'B', value: 'B', text: 'Map' },
      { label: 'C', value: 'C', text: 'List' },
      { label: 'D', value: 'D', text: 'Queue' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 5,
    question: 'Java 中，以下哪个关键字用于处理异常？',
    options: [
      { label: 'A', value: 'A', text: 'throw' },
      { label: 'B', value: 'B', text: 'try-catch' },
      { label: 'C', value: 'C', text: 'throws' },
      { label: 'D', value: 'D', text: '以上都是' }
    ],
    correctAnswer: 'D'
  }
]

/** 专业技能题库 - C++ */
export const cppQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'C++ 中，以下哪个符号用于表示指针？',
    options: [
      { label: 'A', value: 'A', text: '&' },
      { label: 'B', value: 'B', text: '*' },
      { label: 'C', value: 'C', text: '@' },
      { label: 'D', value: 'D', text: '%' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 2,
    question: 'C++ 中，以下哪个不是构造函数的特性？',
    options: [
      { label: 'A', value: 'A', text: '与类名相同' },
      { label: 'B', value: 'B', text: '没有返回值' },
      { label: 'C', value: 'C', text: '可以被继承' },
      { label: 'D', value: 'D', text: '可以重载' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 3,
    question: 'C++ 中，以下哪个关键字用于动态内存分配？',
    options: [
      { label: 'A', value: 'A', text: 'malloc' },
      { label: 'B', value: 'B', text: 'new' },
      { label: 'C', value: 'C', text: 'alloc' },
      { label: 'D', value: 'D', text: 'create' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 4,
    question: 'C++ 中，以下哪个概念用于实现运行时多态？',
    options: [
      { label: 'A', value: 'A', text: '函数重载' },
      { label: 'B', value: 'B', text: '运算符重载' },
      { label: 'C', value: 'C', text: '虚函数' },
      { label: 'D', value: 'D', text: '模板' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 5,
    question: 'C++ 中，以下哪个容器属于 STL 标准库？',
    options: [
      { label: 'A', value: 'A', text: 'ArrayList' },
      { label: 'B', value: 'B', text: 'vector' },
      { label: 'C', value: 'C', text: 'LinkedList' },
      { label: 'D', value: 'D', text: 'HashMap' }
    ],
    correctAnswer: 'B'
  }
]

/** 工具题库 - Git */
export const gitQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'Git 中，以下哪个命令用于将文件添加到暂存区？',
    options: [
      { label: 'A', value: 'A', text: 'git commit' },
      { label: 'B', value: 'B', text: 'git add' },
      { label: 'C', value: 'C', text: 'git push' },
      { label: 'D', value: 'D', text: 'git pull' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 2,
    question: 'Git 中，以下哪个命令用于创建新的分支？',
    options: [
      { label: 'A', value: 'A', text: 'git branch <branch-name>' },
      { label: 'B', value: 'B', text: 'git checkout <branch-name>' },
      { label: 'C', value: 'C', text: 'git merge <branch-name>' },
      { label: 'D', value: 'D', text: 'git switch <branch-name>' }
    ],
    correctAnswer: 'A'
  },
  {
    id: 3,
    question: 'Git 中，以下哪个命令用于查看当前仓库的状态？',
    options: [
      { label: 'A', value: 'A', text: 'git log' },
      { label: 'B', value: 'B', text: 'git status' },
      { label: 'C', value: 'C', text: 'git diff' },
      { label: 'D', value: 'D', text: 'git show' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 4,
    question: 'Git 中，以下哪个命令用于将本地提交推送到远程仓库？',
    options: [
      { label: 'A', value: 'A', text: 'git commit' },
      { label: 'B', value: 'B', text: 'git merge' },
      { label: 'C', value: 'C', text: 'git push' },
      { label: 'D', value: 'D', text: 'git fetch' }
    ],
    correctAnswer: 'C'
  },
  {
    id: 5,
    question: 'Git 中，以下哪个命令用于切换分支？',
    options: [
      { label: 'A', value: 'A', text: 'git branch' },
      { label: 'B', value: 'B', text: 'git checkout' },
      { label: 'C', value: 'C', text: 'git merge' },
      { label: 'D', value: 'D', text: 'git stash' }
    ],
    correctAnswer: 'B'
  }
]

/** 工具题库 - Docker */
export const dockerQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: 'Docker 中，以下哪个命令用于运行一个容器？',
    options: [
      { label: 'A', value: 'A', text: 'docker build' },
      { label: 'B', value: 'B', text: 'docker run' },
      { label: 'C', value: 'C', text: 'docker create' },
      { label: 'D', value: 'D', text: 'docker start' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 2,
    question: 'Docker 中，以下哪个命令用于查看正在运行的容器？',
    options: [
      { label: 'A', value: 'A', text: 'docker ps' },
      { label: 'B', value: 'B', text: 'docker images' },
      { label: 'C', value: 'C', text: 'docker list' },
      { label: 'D', value: 'D', text: 'docker show' }
    ],
    correctAnswer: 'A'
  },
  {
    id: 3,
    question: 'Docker 中，用于构建镜像的文件通常叫什么名字？',
    options: [
      { label: 'A', value: 'A', text: 'docker.yml' },
      { label: 'B', value: 'B', text: 'Dockerfile' },
      { label: 'C', value: 'C', text: 'docker.conf' },
      { label: 'D', value: 'D', text: 'docker.json' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 4,
    question: 'Docker 中，以下哪个命令用于停止一个正在运行的容器？',
    options: [
      { label: 'A', value: 'A', text: 'docker kill' },
      { label: 'B', value: 'B', text: 'docker stop' },
      { label: 'C', value: 'C', text: 'docker pause' },
      { label: 'D', value: 'D', text: 'docker exit' }
    ],
    correctAnswer: 'B'
  },
  {
    id: 5,
    question: 'Docker 中，以下哪个命令用于从镜像仓库拉取镜像？',
    options: [
      { label: 'A', value: 'A', text: 'docker fetch' },
      { label: 'B', value: 'B', text: 'docker download' },
      { label: 'C', value: 'C', text: 'docker pull' },
      { label: 'D', value: 'D', text: 'docker get' }
    ],
    correctAnswer: 'C'
  }
]

/**
 * 从题库中随机获取一道题目
 * @param questions - 题目数组
 * @returns 随机选中的题目
 */
export const getRandomQuestion = <T extends QuizQuestion>(questions: T[]): T => {
  const randomIndex = Math.floor(Math.random() * questions.length)
  return questions[randomIndex]!
}

// ==================== 能力评估雷达图模拟数据生成 ====================

/** 雷达图分数类型 */
export interface RadarScores {
  专业: number
  创新: number
  学习: number
  抗压: number
  沟通: number
  实习: number
}

/** 表单数据结构（用于模拟计算） */
export interface MockFormData {
  skills: { name: string; credibility?: number }[]
  certificates: string[]
  innovation?: string
  projects: { name?: string; desc?: string }[]
  education: string
  scores: {
    learning: boolean
    communication: boolean
    stress: boolean
  }
  languages: { type?: string; level?: string; other?: string }[]
  internships: { company?: string; role?: string; date?: Date[]; desc?: string }[]
}

/**
 * 模拟计算六维能力分数
 * 基于表单数据计算各项能力得分（前端模拟版本，用于调试预览）
 * @param formData 表单数据
 * @returns 六维能力分数
 */
export const calculateRadarScores = (formData: MockFormData): RadarScores => {
  const scores: RadarScores = {
    专业: 0,
    创新: 0,
    学习: 0,
    抗压: 0,
    沟通: 0,
    实习: 0
  }

  // 1. 专业能力：基于技能熟练度、证书、专业匹配度
  const skillScore = formData.skills.length > 0
    ? formData.skills.reduce((sum, s) => sum + (s.credibility || 0), 0) / formData.skills.length
    : 0
  const certBonus = Math.min(formData.certificates.length * 5, 20) // 证书加分，最多20分
  scores.专业 = Math.min(Math.round(skillScore * 0.6 + certBonus + 40), 100) // 基础分40

  // 2. 创新能力：基于创新案例和项目经历
  const innovationScore = formData.innovation ? 70 : 40
  const projectBonus = Math.min(formData.projects.length * 5, 15)
  scores.创新 = Math.min(innovationScore + projectBonus, 100)

  // 3. 学习能力：基于学历、素质测评完成度
  const eduScoreMap: Record<string, number> = { '专科': 60, '本科': 70, '硕士': 80, '博士': 90, '高中': 40, '其他': 50 }
  const eduScore = eduScoreMap[formData.education] || 50
  const quizBonus = (formData.scores.learning ? 15 : 0) + (formData.scores.communication ? 5 : 0)
  scores.学习 = Math.min(eduScore + quizBonus, 100)

  // 4. 抗压能力：基于素质测评
  scores.抗压 = formData.scores.stress ? 75 : 55

  // 5. 沟通能力：基于素质测评和语言能力
  const langBonus = formData.languages.filter(l => l.level).length * 5
  scores.沟通 = Math.min((formData.scores.communication ? 70 : 50) + langBonus, 100)

  // 6. 实习能力：基于实习经历
  scores.实习 = formData.internships.length > 0
    ? Math.min(50 + formData.internships.length * 15, 95)
    : 45

  return scores
}

/**
 * 模拟生成能力评估报告数据
 * 用于前端调试预览，模拟后端返回的报告数据结构
 * @param formData 表单数据
 * @returns 模拟的报告数据（包含能力分数）
 */
export const generateMockAbilityReport = (formData: MockFormData) => {
  const scores = calculateRadarScores(formData)

  return {
    // 能力评估分数（雷达图数据）
    abilityScores: scores,

    // 总体评价
    overallAssessment: {
      level: scores.专业 >= 80 ? '优秀' : scores.专业 >= 60 ? '良好' : '待提升',
      summary: `综合评估显示，您的专业能力为${scores.专业}分，创新能力为${scores.创新}分，整体${scores.专业 >= 70 ? '具备较强的竞争力' : '还有提升空间'}。`,
      strengths: Object.entries(scores)
        .filter(([, value]) => value >= 75)
        .map(([key]) => key),
      weaknesses: Object.entries(scores)
        .filter(([, value]) => value < 60)
        .map(([key]) => key)
    },

    // 各维度详细分析
    dimensionAnalysis: {
      专业: {
        score: scores.专业,
        analysis: scores.专业 >= 80
          ? '您的专业技能扎实，证书资质完备，在目标岗位竞争中具有明显优势。'
          : scores.专业 >= 60
            ? '您具备一定的专业基础，建议继续深化核心技能，考取相关证书。'
            : '您的专业技能还有较大提升空间，建议制定系统的学习计划。',
        suggestions: ['持续学习新技术', '参与开源项目', '考取行业认证']
      },
      创新: {
        score: scores.创新,
        analysis: scores.创新 >= 75
          ? '您展现出良好的创新思维和项目实践能力。'
          : '建议在项目经历中多体现创新点和解决复杂问题的能力。',
        suggestions: ['培养问题拆解能力', '关注行业前沿技术', '参与创新竞赛']
      },
      学习: {
        score: scores.学习,
        analysis: scores.学习 >= 75
          ? '您具备优秀的学习能力和知识迁移能力。'
          : '建议建立系统化的学习方法，提高知识吸收效率。',
        suggestions: ['制定学习计划', '参与技术社区', '阅读专业书籍']
      },
      抗压: {
        score: scores.抗压,
        analysis: scores.抗压 >= 70
          ? '您展现出良好的抗压能力和情绪管理能力。'
          : '建议学习压力管理技巧，提升在高压环境下的工作效率。',
        suggestions: ['学习时间管理法', '保持运动习惯', '培养兴趣爱好']
      },
      沟通: {
        score: scores.沟通,
        analysis: scores.沟通 >= 70
          ? '您具备良好的沟通协调能力，有利于团队协作。'
          : '建议多参与团队项目，提升沟通表达能力。',
        suggestions: ['主动承担协调工作', '参加演讲培训', '学习书面表达']
      },
      实习: {
        score: scores.实习,
        analysis: scores.实习 >= 70
          ? '您的实习经历丰富，具备良好的职场适应能力。'
          : '建议积极寻找实习机会，积累实际工作经验。',
        suggestions: ['投递实习简历', '参加企业开放日', '寻求导师推荐']
      }
    },

    // 生成时间戳
    generatedAt: new Date().toISOString()
  }
}

/**
 * 模拟异步获取能力评估报告
 * 模拟后端 API 延迟返回报告数据
 * @param formData 表单数据
 * @param delay 模拟延迟时间（毫秒），默认 800ms
 * @returns Promise<模拟报告数据>
 */
export const fetchMockAbilityReport = (
  formData: MockFormData,
  delay: number = 800
): Promise<ReturnType<typeof generateMockAbilityReport>> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const report = generateMockAbilityReport(formData)
      resolve(report)
    }, delay)
  })
}

// ==================== 简历上传能力评估模拟数据（与表单格式一致）====================

/** 简历解析出的模拟画像数据 */
export interface MockResumeProfile {
  name: string
  skills: string[]
  experience: string[]
  education: string
  confidence_score: number
}

/**
 * 根据简历内容生成模拟能力评估分数
 * 与表单提交的 calculateRadarScores 计算逻辑保持一致
 * @param profile 简历解析出的画像数据
 * @returns 六维能力分数
 */
export const calculateResumeRadarScores = (profile: MockResumeProfile): RadarScores => {
  const scores: RadarScores = {
    专业: 0,
    创新: 0,
    学习: 0,
    抗压: 0,
    沟通: 0,
    实习: 0
  }

  // 1. 专业能力：基于技能数量和置信度
  const skillCount = profile.skills.length
  const baseSkillScore = Math.min(skillCount * 10, 50) // 技能加分，最多50分
  const confidenceBonus = Math.round(profile.confidence_score * 30) // 置信度加分
  scores.专业 = Math.min(baseSkillScore + confidenceBonus + 40, 100) // 基础分40

  // 2. 创新能力：基于经历描述中的关键词
  const innovationKeywords = ['创新', '优化', '改进', '设计', '研发', '创造', '突破']
  const innovationCount = profile.experience.reduce((count, exp) => {
    return count + innovationKeywords.filter(keyword => exp.includes(keyword)).length
  }, 0)
  scores.创新 = Math.min(50 + innovationCount * 8, 95)

  // 3. 学习能力：基于学历和技能多样性
  const eduScoreMap: Record<string, number> = {
    '博士': 90, '硕士': 80, '本科': 70, '专科': 60, '高中': 40
  }
  const eduScore = Object.entries(eduScoreMap).find(([key]) =>
    profile.education.includes(key)
  )?.[1] || 50
  const diversityBonus = Math.min(skillCount * 3, 15) // 技能多样性加分
  scores.学习 = Math.min(eduScore + diversityBonus, 100)

  // 4. 抗压能力：基于经历数量和描述长度
  const expCount = profile.experience.length
  const avgDescLength = profile.experience.reduce((sum, exp) => sum + exp.length, 0) /
    (expCount || 1)
  scores.抗压 = Math.min(55 + expCount * 5 + Math.min(avgDescLength / 20, 20), 95)

  // 5. 沟通能力：基于经历中协作相关关键词
  const communicationKeywords = ['团队', '协作', '沟通', '协调', '汇报', '跨部门', '合作']
  const communicationCount = profile.experience.reduce((count, exp) => {
    return count + communicationKeywords.filter(keyword => exp.includes(keyword)).length
  }, 0)
  scores.沟通 = Math.min(55 + communicationCount * 6, 95)

  // 6. 实习能力：基于经历数量
  scores.实习 = expCount > 0
    ? Math.min(50 + expCount * 15, 95)
    : 45

  return scores
}

/**
 * 生成简历上传的模拟解析响应
 * 与表单提交流程返回的 UploadResponse 格式一致
 * @param fileName 文件名
 * @returns 模拟的简历上传响应数据
 */
export const generateMockResumeUploadResponse = (fileName: string) => {
  const taskId = `resume_task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

  // 模拟从简历解析出的画像数据
  const mockProfile: MockResumeProfile = {
    name: '张三',
    skills: ['Java', 'Spring Boot', 'MySQL', 'Redis', 'Vue.js', 'Docker'],
    experience: [
      '负责公司核心业务系统的设计与开发，优化系统性能提升30%',
      '带领5人团队完成电商平台重构项目，按时交付并获得好评',
      '参与跨部门协作，与产品、测试团队紧密配合确保项目质量'
    ],
    education: '本科 / 计算机科学与技术',
    confidence_score: 0.85
  }

  // 计算能力评估分数（与表单提交流程一致）
  const abilityScores = calculateResumeRadarScores(mockProfile)

  // 生成完整的报告数据（与表单提交流程的 CareerReport 格式一致）
  const report = generateMockAbilityReport({
    skills: mockProfile.skills.map(name => ({ name, credibility: 80 })),
    certificates: ['CET-6', '软件设计师'],
    innovation: '优化系统性能提升30%',
    projects: mockProfile.experience.map(desc => ({ desc })),
    education: '本科',
    scores: { learning: true, communication: true, stress: true },
    languages: [{ type: '英语', level: 'CET-6' }],
    internships: [{ company: 'ABC科技', role: 'Java开发工程师' }]
  })

  // 模拟从简历解析出的表单数据（用于自动填充表单）
  const parsedFormData = {
    education: '本科',
    major: ['计算机类', '软件工程'],
    graduationDate: '2025-06',
    languages: [
      { type: '英语', level: 'CET-6', other: '' }
    ],
    certificates: ['CET-6', '软件设计师'],
    skills: [
      { name: 'Java', credibility: 85 },
      { name: 'Spring Boot', credibility: 80 },
      { name: 'MySQL', credibility: 75 },
      { name: 'Redis', credibility: 70 },
      { name: 'Vue.js', credibility: 65 },
      { name: 'Docker', credibility: 60 }
    ],
    tools: [
      { name: 'Git', proficiency: '熟练' },
      { name: 'IntelliJ IDEA', proficiency: '精通' },
      { name: 'VS Code', proficiency: '熟练' }
    ],
    codeAbility: { links: 'https://github.com/zhangsan' },
    projects: [
      {
        isCompetition: false,
        name: '电商平台后端系统',
        desc: '负责订单模块的设计与开发，使用Spring Boot + MySQL + Redis技术栈，支持高并发场景'
      },
      {
        isCompetition: true,
        name: '校园二手交易平台',
        desc: '获得校级创新创业大赛二等奖，负责整体架构设计和核心功能开发'
      }
    ],
    internships: [
      {
        company: 'ABC科技有限公司',
        role: 'Java开发工程师',
        date: [],
        desc: '参与公司核心业务系统开发，负责订单管理模块的设计与实现'
      }
    ],
    innovation: '通过引入Redis缓存和数据库索引优化，将系统查询性能提升30%',
    targetJob: '', // 故意留空，测试必填检测
    targetIndustries: ['互联网', '软件开发'] // 目标行业也留空，测试必填检测
  }

  return {
    code: 200,
    message: '简历上传并解析成功',
    data: {
      file_id: `file_${Date.now()}`,
      parse_status: 'completed' as const,
      task_id: taskId,
      profile: mockProfile,
      // 能力评估分数（与表单提交流程格式一致）
      abilityScores,
      // 完整报告（与表单提交流程格式一致）
      report,
      // AI解析后的表单数据（新增，用于自动填充）
      formData: parsedFormData
    }
  }
}

/**
 * 模拟简历上传并解析
 * 模拟后端 API 延迟返回解析结果
 * @param fileName 文件名
 * @param delay 模拟延迟时间（毫秒），默认 1500ms
 * @returns Promise<模拟上传响应>
 */
export const mockUploadResume = (
  fileName: string,
  delay: number = 1500
): Promise<ReturnType<typeof generateMockResumeUploadResponse>> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const response = generateMockResumeUploadResponse(fileName)
      resolve(response)
    }, delay)
  })
}
