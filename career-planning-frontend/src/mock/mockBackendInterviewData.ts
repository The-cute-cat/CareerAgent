// 后端开发面试结果模拟数据
export const mockBackendInterviewResult = {
  // 综合评分
  overallScore: 78,
  
  // 能力维度评分
  dimensionScores: {
    technical: 80,        // 技术能力
    communication: 75,    // 沟通能力
    logic: 82,            // 逻辑思维
    expression: 76,       // 表达能力
    attitude: 88          // 态度素养
  },
  
  // 技能掌握程度评估 - 后端开发核心技能
  skillAssessment: [
    { name: 'Java核心/集合框架', score: 85, fullMark: 100 },
    { name: 'Spring Boot/Spring Cloud', score: 82, fullMark: 100 },
    { name: 'MySQL/数据库设计', score: 78, fullMark: 100 },
    { name: 'Redis缓存技术', score: 80, fullMark: 100 },
    { name: '消息队列(RocketMQ/Kafka)', score: 70, fullMark: 100 },
    { name: '微服务架构设计', score: 72, fullMark: 100 },
    { name: 'JVM原理与调优', score: 65, fullMark: 100 },
    { name: 'Linux/Shell命令', score: 75, fullMark: 100 },
    { name: '分布式系统设计', score: 68, fullMark: 100 },
    { name: '算法与数据结构', score: 78, fullMark: 100 }
  ],
  
  // 能力短板分析
  weaknessAnalysis: [
    {
      area: 'JVM深度调优与问题排查',
      severity: 'high',
      suggestion: '建议深入学习JVM内存模型、GC算法和调优参数，通过实际案例学习OOM、FullGC等问题的排查方法。推荐《深入理解Java虚拟机》和Arthas工具实践'
    },
    {
      area: '分布式系统设计与实践',
      severity: 'medium',
      suggestion: '建议学习分布式事务(Seata)、分布式锁(Redis/ZK)、分库分表(ShardingSphere)等方案，参与开源项目或搭建Demo环境实践'
    },
    {
      area: '高并发场景实战经验',
      severity: 'medium',
      suggestion: '建议学习限流熔断(Sentinel)、异步处理、池化技术等，可以通过压测工具(JMeter)模拟高并发场景进行实践'
    },
    {
      area: '云原生与容器化技术',
      severity: 'low',
      suggestion: '建议学习Docker、Kubernetes基础使用，了解DevOps流程，尝试将项目容器化部署'
    }
  ],
  
  // 个性化提升建议
  improvementSuggestions: [
    {
      category: '核心技术深化',
      items: [
        '深入学习Java并发编程(JUC包、线程池、锁机制)，掌握高并发编程范式',
        '系统学习Spring源码，理解IOC、AOP、事务传播等核心机制',
        '掌握MySQL索引优化、执行计划分析、慢查询优化等进阶技能',
        '深入学习Redis数据结构与使用场景，掌握缓存设计与一致性方案'
      ]
    },
    {
      category: '分布式与架构能力',
      items: [
        '学习微服务拆分原则，掌握服务注册发现、配置中心、网关等组件',
        '实践分布式事务方案(2PC、TCC、最终一致性)，理解CAP和BASE理论',
        '了解常用设计模式在框架源码中的应用，提升架构设计思维',
        '学习DDD领域驱动设计，掌握分层架构和充血模型设计'
      ]
    },
    {
      category: '工程化与DevOps',
      items: [
        '学习Docker容器化技术，掌握Dockerfile编写和镜像优化',
        '了解CI/CD流程，实践Jenkins/GitLab CI自动化构建部署',
        '掌握Git工作流、代码审查、单元测试(JUnit/Mockito)等工程实践',
        '学习日志收集(ELK)、监控告警(Prometheus/Grafana)等运维技能'
      ]
    },
    {
      category: '软技能提升',
      items: [
        '提升技术方案文档能力，学会画图(架构图、流程图、时序图)表达设计',
        '培养Owner意识，主动推动项目进度，协调跨团队资源',
        '加强业务理解能力，从技术角度思考如何创造业务价值',
        '保持技术敏感度，关注Java生态新趋势(Spring Native、虚拟线程等)'
      ]
    }
  ],
  
  // 面试过程记录
  interviewRecord: {
    totalQuestions: 15,
    answeredQuestions: 14,
    avgResponseTime: 52,
    fluencyScore: 78
  },
  
  // AI面试官评语
  aiFeedback: '整体表现良好，Java基础扎实，对Spring生态有较好的掌握。在数据库设计和Redis使用方面有实践经验。但在JVM调优和分布式系统深度方面还有提升空间。面试过程中思路清晰，表达较为流畅，面对不会的问题能够坦诚承认并尝试分析。建议多参与高并发项目实践，深入理解分布式系统的挑战和解决方案。保持对技术的热情，持续关注云原生等前沿技术。'
}

// Java后端工程师面试聊天记录模拟
export const mockBackendChatHistory = [
  {
    id: '1',
    role: 'ai',
    content: '你好！我是你的AI面试官。今天我们进行Java后端工程师岗位的面试，准备好了吗？',
    timestamp: new Date('2024-01-15 14:00:00'),
    emotion: 'happy'
  },
  {
    id: '2',
    role: 'user',
    content: '你好，我准备好了，请开始吧。',
    timestamp: new Date('2024-01-15 14:00:05')
  },
  {
    id: '3',
    role: 'ai',
    content: '好的，请先做一个简单的自我介绍，重点介绍你的技术栈和项目经验。',
    timestamp: new Date('2024-01-15 14:00:08'),
    emotion: 'encouraging'
  },
  {
    id: '4',
    role: 'user',
    content: '我叫张三，有4年Java后端开发经验。主要技术栈是Spring Boot、Spring Cloud、MySQL、Redis。上一家公司负责电商平台的订单系统开发，参与了微服务架构升级，将单体应用拆分为订单、库存、支付等多个服务。',
    timestamp: new Date('2024-01-15 14:00:35')
  },
  {
    id: '5',
    role: 'ai',
    content: '不错的背景！能详细说说HashMap的原理吗？jdk1.7和1.8有什么区别？',
    timestamp: new Date('2024-01-15 14:00:50'),
    emotion: 'thinking'
  },
  {
    id: '6',
    role: 'user',
    content: 'HashMap底层是数组+链表+红黑树。put时先计算hash值，找到数组下标，如果有冲突就用链表存储。jdk1.8引入了红黑树，当链表长度超过8且数组长度超过64时，链表会转为红黑树，提升查询效率。1.7是头插法，1.8改为尾插法，解决了多线程下的死循环问题。',
    timestamp: new Date('2024-01-15 14:01:25')
  },
  {
    id: '7',
    role: 'ai',
    content: '回答得很好！那你说说Spring的IOC和AOP原理吧。',
    timestamp: new Date('2024-01-15 14:01:40'),
    emotion: 'neutral'
  },
  {
    id: '8',
    role: 'user',
    content: 'IOC是控制反转，通过依赖注入实现。Spring使用反射创建Bean，维护Bean的生命周期，通过三级缓存解决循环依赖。AOP是面向切面编程，底层使用动态代理，JDK代理实现了接口的类，CGLIB代理没有接口的类。主要应用在事务管理、日志记录、权限控制等场景。',
    timestamp: new Date('2024-01-15 14:02:15')
  },
  {
    id: '9',
    role: 'ai',
    content: '很好！你在项目中用过Redis吗？主要用在什么场景？',
    timestamp: new Date('2024-01-15 14:02:35'),
    emotion: 'happy'
  },
  {
    id: '10',
    role: 'user',
    content: '用过，主要用在三个场景：1）缓存热点数据，比如商品详情、用户信息；2）分布式锁，用Redisson实现接口幂等性；3）限流计数，用滑动窗口算法限制接口访问频率。也遇到过缓存穿透问题，后来用布隆过滤器解决了。',
    timestamp: new Date('2024-01-15 14:03:10')
  },
  {
    id: '11',
    role: 'ai',
    content: '不错！那你说说MySQL的索引优化吧，什么时候索引会失效？',
    timestamp: new Date('2024-01-15 14:03:25'),
    emotion: 'thinking'
  },
  {
    id: '12',
    role: 'user',
    content: '索引优化要注意最左前缀原则，查询条件要用到索引的最左列。避免在索引列上做函数计算、类型转换。like模糊查询%在左边会失效。or条件两边都要走索引才能用到。还有 !=、<>、is null等也可能导致索引失效。我通常会用explain分析执行计划。',
    timestamp: new Date('2024-01-15 14:04:05')
  },
  {
    id: '13',
    role: 'ai',
    content: 'MySQL的InnoDB默认隔离级别是什么？如何解决幻读问题？',
    timestamp: new Date('2024-01-15 14:04:20'),
    emotion: 'neutral'
  },
  {
    id: '14',
    role: 'user',
    content: '默认是RR可重复读。解决幻读主要靠MVCC和间隙锁。MVCC通过版本链和ReadView实现快照读，避免看到其他事务的修改。间隙锁会锁住一个范围，防止其他事务插入数据，从而解决当前读的幻读问题。',
    timestamp: new Date('2024-01-15 14:04:55')
  },
  {
    id: '15',
    role: 'ai',
    content: '你们项目是怎么做分布式事务的？能讲讲Seata的原理吗？',
    timestamp: new Date('2024-01-15 14:05:10'),
    emotion: 'thinking'
  },
  {
    id: '16',
    role: 'user',
    content: '我们用的是Seata的AT模式。原理是Seata Server作为协调者，TM负责开启全局事务，RM管理分支事务。执行时先解析SQL生成前后镜像，本地事务提交后向Server注册分支。如果全局提交就异步删除undo_log，如果回滚就用undo_log做补偿。用起来比较简单，只需要加注解和配置数据源代理。',
    timestamp: new Date('2024-01-15 14:06:00')
  },
  {
    id: '17',
    role: 'ai',
    content: '项目有没有遇到过线上问题？你是怎么排查的？',
    timestamp: new Date('2024-01-15 14:06:15'),
    emotion: 'neutral'
  },
  {
    id: '18',
    role: 'user',
    content: '有一次CPU飙高的问题。先用top找到高CPU的进程，然后用jstack打印线程栈，发现是死循环导致的。还有一次FullGC频繁，用jmap生成dump文件，MAT分析发现是大对象进了老年代，调整了新生代大小后解决。平时也会用Arthas做实时诊断。',
    timestamp: new Date('2024-01-15 14:07:00')
  },
  {
    id: '19',
    role: 'ai',
    content: '最后问一个场景题：如果系统突然有大量请求超时，你会怎么排查和处理？',
    timestamp: new Date('2024-01-15 14:07:20'),
    emotion: 'thinking'
  },
  {
    id: '20',
    role: 'user',
    content: '首先看监控，确认是网络、数据库、还是应用本身的问题。如果是数据库慢查询，看是否有大SQL或锁竞争。如果是应用问题，用jstack看是否有线程阻塞，jstat看GC情况。如果是流量突增，考虑限流降级，扩容服务实例。同时保留现场日志和dump文件，方便后续分析。',
    timestamp: new Date('2024-01-15 14:08:10')
  }
]

// 后端面试统计数据
export const mockBackendInterviewStats = {
  questionsAsked: 15,
  answersGiven: 14,
  fluency: 78,
  technicalScore: 80,
  communicationScore: 75
}

// 面试过程时间轴数据
export const mockBackendTimelineData = [
  { time: '00:00', event: '面试开始', type: 'start' },
  { time: '00:35', event: '自我介绍环节', type: 'normal' },
  { time: '02:15', event: 'Java基础问答', type: 'normal' },
  { time: '05:30', event: 'Spring框架原理', type: 'normal' },
  { time: '08:45', event: 'Redis缓存技术', type: 'normal' },
  { time: '11:20', event: 'MySQL数据库', type: 'highlight' },
  { time: '14:00', event: '分布式事务讨论', type: 'highlight' },
  { time: '16:30', event: '线上问题排查', type: 'normal' },
  { time: '18:45', event: '场景题分析', type: 'normal' },
  { time: '20:00', event: '面试结束', type: 'end' }
]

// 能力变化趋势数据（多次面试对比）
export const mockBackendProgressTrend = [
  { name: '第1次面试', technical: 60, communication: 65, logic: 62 },
  { name: '第2次面试', technical: 68, communication: 68, logic: 70 },
  { name: '第3次面试', technical: 75, communication: 72, logic: 78 },
  { name: '本次面试', technical: 80, communication: 75, logic: 82 }
]

// 技能雷达图对比数据（当前 vs 目标）
export const mockBackendRadarComparison = {
  current: [80, 75, 82, 76, 88],
  target: [90, 85, 90, 85, 90],
  labels: ['技术能力', '沟通能力', '逻辑思维', '表达能力', '态度素养']
}

// 答题情况统计 - 按技术分类
export const mockBackendAnswerStats = {
  categories: ['Java基础', 'Spring框架', '数据库', 'Redis缓存', '分布式', 'JVM调优'],
  correct: [4, 4, 3, 3, 2, 1],
  total: [4, 5, 4, 3, 3, 2],
  avgTime: [35, 45, 50, 40, 70, 60]
}

// 常用词汇分析
export const mockBackendWordAnalysis = [
  { word: 'Spring', count: 10 },
  { word: 'Redis', count: 7 },
  { word: '事务', count: 6 },
  { word: '索引', count: 5 },
  { word: '锁', count: 5 },
  { word: '微服务', count: 4 },
  { word: 'JVM', count: 4 },
  { word: '分布式', count: 4 }
]

// 情感分析数据
export const mockBackendEmotionAnalysis = {
  confidence: 72,
  nervousness: 25,
  enthusiasm: 80,
  pressure: 35,
  overall: 'positive'
}

// 问题分类标签统计
export const mockBackendQuestionTags = [
  { tag: 'Java基础', count: 4, color: '#67C23A' },
  { tag: 'Spring框架', count: 3, color: '#409EFF' },
  { tag: '数据库', count: 3, color: '#E6A23C' },
  { tag: '缓存技术', count: 2, color: '#F56C6C' },
  { tag: '分布式', count: 2, color: '#909399' },
  { tag: '场景题', count: 1, color: '#8E44AD' }
]

// 导出所有后端面试模拟数据
export default {
  mockBackendInterviewResult,
  mockBackendChatHistory,
  mockBackendInterviewStats,
  mockBackendTimelineData,
  mockBackendProgressTrend,
  mockBackendRadarComparison,
  mockBackendAnswerStats,
  mockBackendWordAnalysis,
  mockBackendEmotionAnalysis,
  mockBackendQuestionTags
}
