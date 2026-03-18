/**
 * DevelopmentMap.vue 模拟数据
 */

/** 图谱节点 */
export interface GraphNode {
  id: string
  label: string
  x: number
  y: number
  data: Record<string, any>
  color: string
  stroke: string
  textColor?: string
}

/** 图谱连线 */
export interface GraphEdge {
  source: string
  target: string
  label: string
  color?: string
}

/** 能力评分模拟数据 */
export const abilityScores = {
  programming: 85,
  algorithms: 78,
  systemDesign: 65,
  teamwork: 88,
  communication: 75,
  learning: 90,
  advantages: '985 院校背景，GPA 前 5%，GitHub 活跃 (1000+ commits)，算法基础扎实',
  improvements: '缺乏高并发生产环境经验，大型分布式系统实战较少'
}

/** 职业发展阶段数据 */
export const careerStages = [
  { stage: '入职 0-1 年', level: '初级工程师', score: 60, ability: '基础夯实期' },
  { stage: '入职 1-3 年', level: '中级工程师', score: 75, ability: '快速成长 期' },
  { stage: '入职 3-5 年', level: '高级工程师', score: 90, ability: '核心骨干期' },
  { stage: '入职 5 年+', level: '技术专家/总监', score: 95, ability: '专家深耕期' }
]

/** 垂直晋升路径 - 节点数据 */
export const verticalPathNodes: GraphNode[] = [
  {
    id: '1',
    label: '初级 Java 工程师',
    x: 400,
    y: 40,
    data: {
      stage: '入职 0-1 年',
      desc: '基础夯实期',
      requirements: ['掌握 Java 基础语法', '熟悉 Spring Boot', '了解 MySQL/Redis'],
      skills: { 'Java 基础': 60, '框架应用': 50, '数据库': 55, '算法逻辑': 70 },
      salary: '8-15K',
      difficulty: '入门'
    },
    color: '#E6F7FF',
    stroke: '#1890FF'
  },
  {
    id: '2',
    label: '中级 Java 工程师',
    x: 400,
    y: 160,
    data: {
      stage: '入职 1-3 年',
      desc: '快速成长 期',
      requirements: ['独立完成功能模块', '掌握微服务架构', '具备 SQL 优化能力'],
      skills: { 'Java 基础': 80, '框架应用': 75, '数据库': 80, '算法逻辑': 85 },
      salary: '15-25K',
      difficulty: '初级'
    },
    color: '#BAE7FF',
    stroke: '#1890FF'
  },
  {
    id: '3',
    label: '高级 Java 工程师',
    x: 400,
    y: 280,
    data: {
      stage: '入职 3-5 年',
      desc: '核心骨干期',
      requirements: ['系统架构设计', '技术方案评审', '指导初中级工程师'],
      skills: { 'Java 基础': 90, '框架应用': 90, '数据库': 90, '算法逻辑': 90 },
      salary: '25-40K',
      difficulty: '中级'
    },
    color: '#91D5FF',
    stroke: '#1890FF'
  },
  {
    id: '4',
    label: 'Java 技术专家',
    x: 250,
    y: 420,
    data: {
      stage: '入职 5-8 年',
      desc: '技术深耕路线',
      requirements: ['领域深度钻研', '开源社区贡献', '技术影响力建设'],
      skills: { 'Java 基础': 95, '框架应用': 95, '数据库': 95, '算法逻辑': 95 },
      salary: '40-60K',
      difficulty: '高级'
    },
    color: '#69C0FF',
    stroke: '#096DD9'
  },
  {
    id: '5',
    label: '技术总监',
    x: 550,
    y: 420,
    data: {
      stage: '入职 8 年+',
      desc: '管理转型路线',
      requirements: ['团队管理能力', '技术战略规划', '跨部门协作'],
      skills: { '技术能力': 85, '管理能力': 90, '沟通能力': 95, '战略思维': 90 },
      salary: '60-100K',
      difficulty: '专家'
    },
    color: '#40A9FF',
    stroke: '#096DD9'
  },
  {
    id: '6',
    label: '首席架构师',
    x: 400,
    y: 520,
    data: {
      stage: '入职 10 年+',
      desc: '职业巅峰',
      requirements: ['企业级架构设计', '技术愿景规划', '行业影响力'],
      skills: { '架构能力': 98, '技术深度': 95, '业务理解': 95, '领导力': 95 },
      salary: '100K+',
      difficulty: '顶级'
    },
    color: '#1890FF',
    stroke: '#0050B3',
    textColor: '#fff'
  }
]

/** 垂直晋升路径 - 连线数据 */
export const verticalPathEdges: GraphEdge[] = [
  { source: '1', target: '2', label: '1-2 年', color: '#1890FF' },
  { source: '2', target: '3', label: '2-3 年', color: '#1890FF' },
  { source: '3', target: '4', label: '技术深耕', color: '#52C41A' },
  { source: '3', target: '5', label: '管理转型', color: '#FA8C16' },
  { source: '4', target: '6', label: '专家晋升', color: '#52C41A' },
  { source: '5', target: '6', label: '总监晋升', color: '#FA8C16' }
]

/** 横向换岗路径 - 节点数据 */
export const transferPathNodes: GraphNode[] = [
  {
    id: 'java',
    label: 'Java 后端开发',
    x: 400,
    y: 100,
    data: {
      desc: '当前岗位',
      match: '100%',
      skills: ['Java', 'Spring', 'MySQL'],
      difficulty: '当前'
    },
    color: '#1890FF',
    stroke: '#1890FF',
    textColor: '#fff'
  },
  {
    id: 'fullstack',
    label: '全栈工程师',
    x: 200,
    y: 200,
    data: {
      desc: '前端+后端',
      match: '85%',
      skills: ['Vue/React', 'Node.js', 'Java'],
      difficulty: '较易',
      needSkills: '需补充前端技术栈'
    },
    color: '#52C41A',
    stroke: '#52C41A'
  },
  {
    id: 'bigdata',
    label: '大数据开发',
    x: 600,
    y: 200,
    data: {
      desc: '数据方向',
      match: '75%',
      skills: ['Hadoop', 'Spark', 'Flink'],
      difficulty: '中等',
      needSkills: '需学习大数据生态'
    },
    color: '#722ED1',
    stroke: '#722ED1'
  },
  {
    id: 'architect',
    label: '系统架构师',
    x: 400,
    y: 300,
    data: {
      desc: '架构设计',
      match: '70%',
      skills: ['分布式', '微服务', '云原生'],
      difficulty: '较难',
      needSkills: '需积累架构经验'
    },
    color: '#FA8C16',
    stroke: '#FA8C16'
  },
  {
    id: 'product',
    label: '产品经理',
    x: 200,
    y: 400,
    data: {
      desc: '产品方向',
      match: '60%',
      skills: ['需求分析', '用户研究', '项目管理'],
      difficulty: '较难',
      needSkills: '需培养产品思维'
    },
    color: '#EB2F96',
    stroke: '#EB2F96'
  },
  {
    id: 'devops',
    label: 'DevOps 工程师',
    x: 600,
    y: 400,
    data: {
      desc: '运维开发',
      match: '65%',
      skills: ['Docker', 'K8s', 'CI/CD'],
      difficulty: '中等',
      needSkills: '需掌握运维技术'
    },
    color: '#13C2C2',
    stroke: '#13C2C2'
  }
]

/** 横向换岗路径 - 连线数据 */
export const transferPathEdges: GraphEdge[] = [
  { source: 'java', target: 'fullstack', label: '前端补充' },
  { source: 'java', target: 'bigdata', label: '数据转型' },
  { source: 'java', target: 'architect', label: '架构进阶' },
  { source: 'fullstack', target: 'product', label: '业务转型' },
  { source: 'bigdata', target: 'devops', label: '基础设施' },
  { source: 'architect', target: 'devops', label: '云原生' },
  { source: 'fullstack', target: 'architect', label: '技术深化' }
]
