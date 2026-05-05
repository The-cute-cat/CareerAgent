import type { GrowthPlanData, InternshipItem, PlanTask, ResourceItem } from '@/types/career-report'

function createResource(id: string, title: string, reason: string, category = '学习资源'): ResourceItem {
  return {
    id,
    title,
    category_name: category,
    reason,
  }
}

/** 任务优先级类型 */
type TaskPriority = '高' | '中' | '低'

function createTask(
  task_name: string,
  description: string,
  priority: TaskPriority,
  estimated_time: string,
  skill_target: string,
  success_criteria: string,
  resources: ResourceItem[] = [],
): PlanTask {
  return {
    task_name,
    description,
    priority,
    estimated_time,
    skill_target,
    success_criteria,
    resources,
  }
}

function createInternship(
  id: string,
  job_title: string,
  company_name: string,
  city: string,
  salary: string,
  reason: string,
  tech_stack: string,
): InternshipItem {
  return {
    id,
    job_title,
    company_name,
    company_industry: '互联网',
    company_scale: '100-499人',
    salary,
    city,
    degree: '本科',
    days_per_week: 4,
    months: 3,
    job_type: '实习',
    tech_stack,
    url: '',
    content: `参与${job_title}相关的核心任务，输出阶段性成果并接受导师评审。`,
    reason,
  }
}

export const mockCareerReportByJobId: Record<string, GrowthPlanData> = {
  job_001: {
    student_summary: '你具备前端与 AI 应用开发经验，学习能力强，适合把“AI 应用工程”作为当前阶段的过渡定位，再逐步向算法方向深入。',
    target_position: '高级AI算法工程师',
    target_position_profile_summary: '该岗位强调硕士背景、深度学习框架、Transformer/LLM/RAG 体系理解，以及可落地的模型训练和评估经验。',
    current_gap: '当前最核心的差距不是兴趣，而是底层算法训练经验、研究型经历和系统化的模型实验方法论。',
    short_term_plan: {
      duration: '1-3个月',
      goal: '先从算法基础和 LLM 工程实践补强，建立从“会调用模型”到“理解模型机制”的能力跃迁。',
      focus_areas: ['PyTorch', 'Transformer', '向量检索', '模型评测'],
      milestones: [
        {
          milestone_name: '完成算法基础补课',
          target_date: '第1个月',
          key_results: ['完成一轮深度学习课程学习', '复现一个 Transformer 基础实验', '沉淀实验笔记'],
          tasks: [
            createTask(
              '补齐 PyTorch 与训练流程',
              '梳理张量、反向传播、训练循环、损失函数与评估流程。',
              '高',
              '2周',
              '深度学习基础',
              '能够独立跑通一个文本分类或序列建模实验。',
              [
                createResource('ai-1', 'PyTorch 入门实战', '先把训练流程跑通，建立算法工程基础。', '课程'),
                createResource('ai-2', 'Transformer 结构拆解笔记', '帮助理解自注意力、编码器与解码器结构。', '文档'),
              ],
            ),
          ],
        },
      ],
      quick_wins: ['整理 AI 项目中使用过的提示工程与检索链路', '补充一份算法学习路线图'],
    },
    mid_term_plan: {
      duration: '3-12个月',
      goal: '从 AI 应用开发者升级为具备模型微调、评测和 RAG 系统设计能力的候选人。',
      skill_roadmap: ['LoRA 微调', 'RAG 架构设计', '评测体系', '实验复现'],
      milestones: [
        {
          milestone_name: '完成一个可复用的 RAG 项目',
          target_date: '第6个月',
          key_results: ['完成数据清洗', '接入向量数据库', '建立评测指标'],
          tasks: [
            createTask(
              '搭建 RAG 演示系统',
              '围绕特定行业知识库，完成检索、重排、问答与评测闭环。',
              '中',
              '1个月',
              'LLM 工程实践',
              '系统可稳定演示，且评测指标可解释。',
            ),
          ],
        },
      ],
      career_progression: '建议先争取 AI 应用工程或算法实习岗位，在真实业务中积累模型实验与系统调优经验，再冲击更高阶算法岗。',
      recommended_internships: [
        createInternship('ai-intern-1', 'AI算法实习生', '智识科技', '北京', '6k-8k', '适合作为算法方向切入点，允许边做边补底层能力。', 'PyTorch / LLM'),
      ],
    },
    action_checklist: ['完成一套 PyTorch 训练 Demo', '输出 Transformer 学习笔记', '准备 AI 工程方向简历版本'],
    tips: ['优先争取算法实习而不是直接冲高级算法岗', '每次实验都记录结论与失败原因'],
  },
  job_002: {
    student_summary: '你的前端栈与工程工具链已经很接近岗位要求，当前更像是需要把优势讲清楚、把项目成果展示完整。',
    target_position: '前端开发工程师',
    target_position_profile_summary: '该岗位重视 Vue3、TypeScript、CSS3、构建工具与可交付项目经验，强调协作与上线实践。',
    current_gap: '关键差距集中在“项目上线经历的呈现方式”与“CSS3/交互动效案例的具体说明”，而不是核心技术栈本身。',
    short_term_plan: {
      duration: '1-3个月',
      goal: '把当前已有项目打磨成可投递版本，同时补强响应式布局、动效与性能优化表达。',
      focus_areas: ['Vue3 工程化', 'TypeScript', 'CSS3 动效', '性能优化'],
      milestones: [
        {
          milestone_name: '完成项目包装与投递准备',
          target_date: '第1个月',
          key_results: ['项目 README 完整', '上线地址可访问', '项目亮点清晰'],
          tasks: [
            createTask(
              '整理前端项目展示页',
              '把项目背景、技术选型、难点与上线效果整理成一页作品说明。',
              '高',
              '1周',
              '项目表达能力',
              '项目介绍可以直接用于简历和面试展示。',
              [
                createResource('fe-1', '前端项目案例拆解模板', '方便你提炼项目亮点与结果。', '模板'),
              ],
            ),
          ],
        },
      ],
      quick_wins: ['补充一个响应式布局案例', '优化简历中的项目描述动词'],
    },
    mid_term_plan: {
      duration: '3-12个月',
      goal: '逐步从可胜任前端开发，成长为具备业务抽象与组件体系能力的中高级前端候选人。',
      skill_roadmap: ['组件库设计', '前端性能优化', '可视化', 'Node 辅助能力'],
      milestones: [
        {
          milestone_name: '沉淀一套可复用组件方案',
          target_date: '第5个月',
          key_results: ['提炼公共组件', '形成规范文档', '在项目中复用'],
          tasks: [
            createTask(
              '提炼页面通用组件',
              '把卡片、筛选区、反馈态等 UI 模块提炼成可复用结构。',
              '中',
              '3周',
              '组件抽象能力',
              '至少在两个页面复用同一套组件方案。',
            ),
          ],
        },
      ],
      career_progression: '建议先稳住前端主线，用真实项目逐步补性能、架构和跨端适配能力，再冲更高阶岗位。',
      recommended_internships: [
        createInternship('fe-intern-1', '前端开发实习生', '星河产品', '上海', '5k-7k', '技术栈高度贴合，适合快速产出可展示成果。', 'Vue3 / TypeScript'),
      ],
    },
    action_checklist: ['补齐上线项目链接', '准备 3 个前端项目亮点故事', '输出一版前端专项简历'],
    tips: ['面试回答尽量量化结果', '每个项目至少准备一个“性能优化/协作推进”案例'],
  },
  job_003: {
    student_summary: '你当前最适合把“全栈”当作扩展方向，用现有前端优势带动后端补课，建立完整交付能力。',
    target_position: '全栈开发工程师（校招）',
    target_position_profile_summary: '该岗位要求前后端都能落地，重视 Web 项目完整闭环、接口设计、数据库能力与基础部署经验。',
    current_gap: '前端部分匹配度高，真正的差距在 Node.js 后端、MySQL 设计以及把项目从“前端主导”升级成“全链路交付”。',
    short_term_plan: {
      duration: '1-3个月',
      goal: '完成一个可演示的前后端分离项目，把后端和数据库能力补到可面试状态。',
      focus_areas: ['Node.js', 'RESTful API', 'MySQL', 'Docker'],
      milestones: [
        {
          milestone_name: '交付一个全栈 Demo',
          target_date: '第2个月',
          key_results: ['后端服务可运行', '数据库完成建模', '前后端联调完成'],
          tasks: [
            createTask(
              '搭建 Express + MySQL 项目',
              '围绕用户、内容、权限等模块做一个完整全栈项目。',
              '高',
              '3周',
              '全栈交付能力',
              '项目可本地启动、联调、并具备基础部署说明。',
              [
                createResource('fs-1', 'Node.js REST API 实战', '帮助快速搭建后端基础骨架。', '课程'),
              ],
            ),
          ],
        },
      ],
      quick_wins: ['补一份接口文档', '把 Docker 基础命令跑通'],
    },
    mid_term_plan: {
      duration: '3-12个月',
      goal: '从“会做 Demo”升级到“能独立负责一个完整模块”的全栈候选人。',
      skill_roadmap: ['服务拆分', '部署上线', '权限系统', '日志监控'],
      milestones: [
        {
          milestone_name: '完成一套带部署的全栈作品',
          target_date: '第6个月',
          key_results: ['上线演示环境', '完成权限管理', '沉淀开发文档'],
          tasks: [
            createTask(
              '实现部署与运维闭环',
              '加入 Nginx、Docker 或云平台部署流程，形成完整交付链路。',
              '中',
              '1个月',
              '项目落地能力',
              '可以向面试官完整讲清开发、联调、部署流程。',
            ),
          ],
        },
      ],
      career_progression: '短期更适合以前端优势切入全栈岗，再逐步把后端能力补齐到可独立负责模块的程度。',
      recommended_internships: [
        createInternship('fs-intern-1', '全栈开发实习生', '云帆科技', '杭州', '5k-8k', '适合利用前端优势带动后端补课，形成完整作品集。', 'Vue / Node / MySQL'),
      ],
    },
    action_checklist: ['做一个前后端分离 Demo', '补充数据库设计笔记', '准备全栈项目讲解材料'],
    tips: ['全栈面试重点不是“都懂一点”，而是能讲清完整交付流程', '后端补课时优先做真实可运行项目'],
  },
  job_004: {
    student_summary: '你目前更像是具备转向潜力的前端候选人，而不是已经成熟的 Java 后端候选人，需要明确“是否真的要转型”。',
    target_position: 'Java后端工程师（校招）',
    target_position_profile_summary: '岗位要求 Java、Spring Boot、MySQL、Redis 等基础后端能力，以及清晰的服务端开发思维。',
    current_gap: '最大差距是技术主线不一致，当前需要从语言、框架、数据库到后端工程思维做系统性迁移。',
    short_term_plan: {
      duration: '1-3个月',
      goal: '确认转向意愿，并完成 Java 后端基础入门与一个小型项目实践。',
      focus_areas: ['Java 基础', 'Spring Boot', 'MySQL', 'Redis'],
      milestones: [
        {
          milestone_name: '跑通 Java 入门项目',
          target_date: '第2个月',
          key_results: ['完成 CRUD 服务', '接入数据库', '理解接口分层'],
          tasks: [
            createTask(
              '完成 Java Web 基础项目',
              '实现用户、文章或任务管理等基础业务，理解 Controller-Service-DAO 分层。',
              '高',
              '4周',
              '后端基础能力',
              '能独立讲清请求链路、数据库设计与异常处理。',
              [
                createResource('java-1', 'Spring Boot 入门项目模板', '帮助快速搭建后端项目骨架。', '模板'),
              ],
            ),
          ],
        },
      ],
      quick_wins: ['梳理一张 Java 学习路径图', '先完成数据库基本操作训练'],
    },
    mid_term_plan: {
      duration: '3-12个月',
      goal: '从“技术转型期”过渡到“能够胜任校招后端岗”的阶段，并沉淀至少一套后端作品。',
      skill_roadmap: ['JVM 基础', '事务与索引', '缓存', '后端工程规范'],
      milestones: [
        {
          milestone_name: '完成一套后端作品并准备面试',
          target_date: '第6个月',
          key_results: ['项目功能完整', '数据库设计合理', '形成面试题整理'],
          tasks: [
            createTask(
              '准备 Java 后端面试闭环',
              '围绕项目、八股、数据库与缓存整理一套面试材料。',
              '中',
              '1个月',
              '后端求职准备',
              '可以完成校招后端岗位的基础面试沟通。',
            ),
          ],
        },
      ],
      career_progression: '如果确定转向，建议以“全栈过渡到后端”为主线，不建议完全丢掉前端背景，反而可以形成复合优势。',
      recommended_internships: [
        createInternship('java-intern-1', 'Java后端实习生', '青木软件', '南京', '5k-7k', '适合作为技术转型期的实战入口，帮助积累服务端经验。', 'Java / Spring Boot'),
      ],
    },
    action_checklist: ['确认是否要走 Java 主线', '完成一个 Spring Boot 项目', '开始整理数据库与缓存面试题'],
    tips: ['如果只是“觉得后端更稳”，不一定要彻底转型', '用现有前端经验做全栈过渡通常更现实'],
  },
  job_005: {
    student_summary: '你目前更适合把设计理解当作前端加分项，而不是直接把 UI/UX 作为主要求职方向。',
    target_position: 'UI/UX设计师（校招）',
    target_position_profile_summary: '岗位强调作品集、设计工具、交互规范、用户研究与审美表达，是与前端开发相邻但不同的专业路径。',
    current_gap: '差距集中在设计方法论、工具熟练度、作品集与职业方向一致性上，而不是单纯的页面实现能力。',
    short_term_plan: {
      duration: '1-3个月',
      goal: '把“设计理解”沉淀成前端岗位中的亮点，而不是贸然转到纯设计求职方向。',
      focus_areas: ['界面审美', '设计规范理解', '组件视觉一致性', '用户体验表达'],
      milestones: [
        {
          milestone_name: '补强前端中的设计表达',
          target_date: '第1个月',
          key_results: ['整理设计规范案例', '优化一个高保真页面', '输出体验复盘'],
          tasks: [
            createTask(
              '做一次页面视觉与体验改版',
              '选择一个现有页面，从信息层级、留白、交互反馈三个角度做优化。',
              '中',
              '2周',
              '体验设计表达',
              '能清晰说明改版前后差异与设计依据。',
            ),
          ],
        },
      ],
      quick_wins: ['学习 Figma 基础操作', '复盘一个优秀产品页面'],
    },
    mid_term_plan: {
      duration: '3-12个月',
      goal: '形成“懂设计的前端”优势，在前端开发岗位中体现更强的体验把控能力。',
      skill_roadmap: ['设计系统理解', '组件体验优化', '前端可访问性', '交互动效'],
      milestones: [
        {
          milestone_name: '形成体验型前端作品集',
          target_date: '第5个月',
          key_results: ['展示 2-3 个体验优化案例', '说明设计思路', '体现前端实现能力'],
          tasks: [
            createTask(
              '沉淀体验优化作品集',
              '把设计理解和前端实现结合起来，形成更有差异化的作品集表达。',
              '中',
              '1个月',
              '差异化竞争力',
              '作品既能体现设计审美，也能体现落地实现能力。',
            ),
          ],
        },
      ],
      career_progression: '建议主线仍然放在前端开发，把设计能力作为优势标签，而不是短期内转向纯 UI/UX 岗。',
      recommended_internships: [
        createInternship('ux-intern-1', '体验型前端实习生', '流光互动', '深圳', '5k-7k', '适合强化“懂设计的前端”定位，而不是直接转纯设计。', 'Vue / Figma'),
      ],
    },
    action_checklist: ['完成一个页面体验改版案例', '学习 Figma 基础', '把设计理解写进前端简历亮点'],
    tips: ['把设计理解转化成前端优势，比直接转纯设计更现实', '体验优化案例要讲清“为什么这样改”'],
  },
}

export function getMockCareerReportByJobId(jobId?: string): GrowthPlanData {
  if (jobId && mockCareerReportByJobId[jobId]) {
    return mockCareerReportByJobId[jobId]
  }

  return mockCareerReportByJobId.job_002!
}

export const mockCareerReportData: GrowthPlanData = getMockCareerReportByJobId('job_002')