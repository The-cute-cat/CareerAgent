/**
 * 人岗匹配模块模拟数据
 * 基于后端返回的字段结构
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
    config: {} as any
  }
}

// ==================== 模拟数据 ====================

/** 模拟人岗匹配结果（后端返回的岗位匹配数组） */
export const mockJobMatchItems: JobMatchItem[] = [
  {
    job_id: "job_002",
    score: 0.8438765406608582,
    raw_data: {
      job_id: "job_002",
      job_name: "前端开发工程师",
      profiles: {
        basic_requirements: {
          degree: "本科",
          major: "不限",
          certificates: "无",
          internship_requirement: "无",
          experience_years: "应届",
          special_requirements: "无"
        },
        professional_skills: {
          core_skills: "Vue3, TypeScript, CSS3",
          tool_capabilities: "Webpack, Vite, Git",
          domain_knowledge: "互联网",
          language_requirements: "CET4",
          project_requirements: "有完整的项目上线经验"
        },
        professional_literacy: {
          communication: "高",
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
          industry: "互联网",
          vertical_promotion_path: "中级前端->资深前端",
          prerequisite_roles: "HTML/JS基础",
          lateral_transfer_directions: "UI设计,产品经理,Node后端",
          social_demand: "高",
          industry_trend: "平稳"
        }
      }
    },
    deep_analysis: {
      can_apply: true,
      score: 92,
      missing_key_skills: [
        "HTML/JS基础（未在技能标签中明确体现，但为岗位前置 prerequisite）",
        "完整的项目上线经验（求职者仅描述'开发了AI职业规划Agent项目'，未说明是否已真实部署上线）"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "本科，应届生，无实习硬性要求，CET-4即可",
          current: "本科软件工程应届生，CET-6（高于要求），实习6个月，符合全部基础门槛",
          gap_analysis: "完全匹配：学历、应届身份、语言证书均达标；实习经历属增值项，不构成门槛差距。"
        },
        {
          dimension: "职业技能",
          required: "Vue3, TypeScript, CSS3, Webpack/Vite/Git",
          current: "熟练掌握Vue3全生态（Composition API、Pinia、VueRouter），TypeScript日常使用，Git版本管理熟练，Vite构建工具熟悉",
          gap_analysis: "高度匹配：核心技能精准覆盖，工具链齐全；仅需在简历中补充CSS3/动画等样式能力的具体案例。"
        },
        {
          dimension: "职业素养",
          required: "沟通能力高、团队协作高、抗压中、逻辑思维中、职业道德高",
          current: "前端校队成员（协作）、6个月实习（抗压）、需求分析课程（逻辑）、AI项目独立完成（责任），综合素养达标",
          gap_analysis: "匹配良好：实习经历验证了抗压与协作能力，项目经验体现责任感。建议面试时用STAR法则展示具体案例。"
        },
        {
          dimension: "发展潜力",
          required: "学习能力高、创新能力中、领导力低、技术取向、适应性高",
          current: "自学Vue3/TypeScript/LLM（学习能力）、AI Agent创新项目（创新能力）、技术博客/开源（技术取向）、快速适应新框架（适应性）",
          gap_analysis: "高度匹配：学习与创新维度甚至超出岗位预期，技术取向明确，是优质前端候选人。"
        }
      ],
      actionable_advice: "在简历和面试中明确补充AI职业规划Agent项目的上线细节：部署平台（如Vercel/云服务）、访问方式、实际用户规模或使用反馈。同时补充1-2个CSS3动画或响应式布局的实战案例，展示综合前端能力。",
      all_analysis: "求职者为优质应届前端候选人：技术栈精准覆盖Vue3全生态，TypeScript与Vite等现代工具链熟练度高。AI职业规划Agent项目展示了独立完成全栈项目的能力和创新思维，是显著加分项。CET-6和6个月实习经历进一步增强了竞争力。建议重点投递，并在面试中突出项目实际部署经验。"
    }
  },
  {
    job_id: "job_001",
    score: 0.8117919564247131,
    raw_data: {
      job_id: "job_001",
      job_name: "高级AI算法工程师",
      profiles: {
        basic_requirements: {
          degree: "硕士",
          major: "计算机/人工智能/数学",
          certificates: "无",
          internship_requirement: "有相关实习经历优先",
          experience_years: "1-3年",
          special_requirements: "有论文发表或竞赛获奖者优先"
        },
        professional_skills: {
          core_skills: "PyTorch, Transformer, LLM, RAG",
          tool_capabilities: "Linux, Docker, CUDA, MLflow",
          domain_knowledge: "自然语言处理, 大模型",
          language_requirements: "CET6",
          project_requirements: "有大型语言模型微调或RAG系统开发经验"
        },
        professional_literacy: {
          communication: "中",
          teamwork: "高",
          stress_management: "高",
          logic_thinking: "高",
          ethics: "高"
        },
        development_potential: {
          learning_ability: "高",
          innovation: "高",
          leadership: "中",
          career_orientation: "技术/研究",
          adaptability: "高"
        },
        job_attributes: {
          salary_competitiveness: "高",
          industry: "互联网/AI",
          vertical_promotion_path: "算法工程师->高级算法工程师->算法负责人",
          prerequisite_roles: "Python编程, 机器学习基础",
          lateral_transfer_directions: "后端开发,数据科学家,AI产品经理",
          social_demand: "极高",
          industry_trend: "快速增长"
        }
      }
    },
    deep_analysis: {
      can_apply: false,
      score: 62,
      missing_key_skills: [
        "PyTorch深度学习框架实战经验",
        "Transformer架构深入理解",
        "大型语言模型微调经验",
        "RAG系统开发经验"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "硕士学历，1-3年经验，有论文发表或竞赛获奖优先",
          current: "本科软件工程应届生，无硕士学历，无论文发表",
          gap_analysis: "存在差距：学历为本科，不符合硕士要求；经验年限不足，缺乏学术研究成果。"
        },
        {
          dimension: "职业技能",
          required: "PyTorch, Transformer, LLM, RAG, CUDA, MLflow",
          current: "了解AI基础知识，有AI Agent项目经验（基于LangChain/LLM API），但未涉及底层模型训练或微调",
          gap_analysis: "差距较大：仅停留在应用层调用，缺乏PyTorch框架使用、模型微调、RAG系统搭建等核心能力。"
        },
        {
          dimension: "职业素养",
          required: "逻辑思维高、抗压高、团队协作高",
          current: "逻辑思维良好（项目开发），抗压能力中等（实习经历），团队协作良好",
          gap_analysis: "基本匹配：软素养维度基本达标，但该岗位对逻辑思维和抗压能力要求更高，需在实际算法调优场景中验证。"
        },
        {
          dimension: "发展潜力",
          required: "学习能力高、创新能力高、研究取向",
          current: "学习能力突出，有AI项目创新经验，但研究方向偏应用而非底层研究",
          gap_analysis: "潜力尚可：学习能力强、有创新意识是优势，但需明确是否愿意深入底层算法研究，建议先从算法实习生做起积累经验。"
        }
      ],
      actionable_advice: "建议作为长期发展方向，短期内不建议直接投递。可先申请算法实习生岗位，同时在读研期间系统学习深度学习课程（如CS231n、CS224n），参与Kaggle竞赛积累实战经验，争取发表论文。",
      all_analysis: "求职者对AI方向有浓厚兴趣并具备一定应用层经验，但该岗位为高级算法岗，要求硕士学历、底层模型训练能力和学术研究背景。建议将此岗位作为长期职业目标，短期内从AI应用开发或算法实习生岗位入手，逐步积累核心竞争力。"
    }
  },
  {
    job_id: "job_003",
    score: 0.7891234567890123,
    raw_data: {
      job_id: "job_003",
      job_name: "全栈开发工程师（校招）",
      profiles: {
        basic_requirements: {
          degree: "本科",
          major: "计算机/软件工程",
          certificates: "无",
          internship_requirement: "有实习经历优先",
          experience_years: "应届",
          special_requirements: "有个人技术博客或开源贡献加分"
        },
        professional_skills: {
          core_skills: "Vue3/React, Node.js/Python, MySQL, RESTful API",
          tool_capabilities: "Git, Docker, Linux, Nginx",
          domain_knowledge: "互联网, SaaS",
          language_requirements: "CET4",
          project_requirements: "有独立完成的Web全栈项目"
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
          career_orientation: "技术",
          adaptability: "高"
        },
        job_attributes: {
          salary_competitiveness: "中",
          industry: "互联网",
          vertical_promotion_path: "初级全栈->高级全栈->技术负责人",
          prerequisite_roles: "前端+后端基础",
          lateral_transfer_directions: "前端专家,后端专家,架构师",
          social_demand: "高",
          industry_trend: "稳步增长"
        }
      }
    },
    deep_analysis: {
      can_apply: true,
      score: 85,
      missing_key_skills: [
        "Node.js后端开发经验（求职者前端为主，后端经验不足）",
        "MySQL数据库设计与优化经验"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "本科计算机相关专业，应届生，有实习优先",
          current: "本科软件工程，应届生，6个月前端实习经历",
          gap_analysis: "匹配良好：学历专业对口，应届身份符合，实习经历满足偏好要求。"
        },
        {
          dimension: "职业技能",
          required: "Vue3/React + Node.js/Python + MySQL + RESTful API + Docker",
          current: "Vue3全生态熟练，TypeScript/CSS3扎实，Git熟练；但Node.js后端开发和MySQL经验不足，Docker仅了解基础",
          gap_analysis: "前端部分高度匹配，后端存在差距。建议快速补充Node.js Express/Koa框架和MySQL基础操作，搭建一个简单的全栈Demo。"
        },
        {
          dimension: "职业素养",
          required: "沟通高、团队协作高、逻辑思维高",
          current: "前端校队成员（协作）、项目开发（逻辑）、实习经历（沟通）",
          gap_analysis: "良好匹配：软素养维度均达标，全栈岗位需要较强的综合沟通能力，已有验证。"
        },
        {
          dimension: "发展潜力",
          required: "学习高、创新高、技术取向",
          current: "自学Vue3/TypeScript/LLM（学习）、AI Agent创新项目（创新）、技术博客/开源（技术取向）",
          gap_analysis: "高度匹配：学习能力和创新意识突出，技术热情高涨，全栈方向非常契合。"
        }
      ],
      actionable_advice: "重点补充Node.js后端开发能力：使用Express/Koa搭建RESTful API服务，连接MySQL实现CRUD操作，完成一个前后端分离的完整项目。同时学习Docker基础使用，将项目容器化部署。",
      all_analysis: "求职者前端能力突出，Vue3全生态熟练，AI Agent项目展示了全栈思维。虽然后端经验相对薄弱，但学习能力强，完全有能力快速补齐。建议投递并在面试中强调学习能力和全栈项目规划能力。"
    }
  },
  {
    job_id: "job_004",
    score: 0.7234567890123456,
    raw_data: {
      job_id: "job_004",
      job_name: "Java后端工程师（校招）",
      profiles: {
        basic_requirements: {
          degree: "本科",
          major: "计算机/软件工程",
          certificates: "无",
          internship_requirement: "无",
          experience_years: "应届",
          special_requirements: "无"
        },
        professional_skills: {
          core_skills: "Java, Spring Boot, MySQL, Redis",
          tool_capabilities: "Git, Maven, Linux",
          domain_knowledge: "互联网",
          language_requirements: "CET4",
          project_requirements: "有后端项目经验"
        },
        professional_literacy: {
          communication: "中",
          teamwork: "高",
          stress_management: "中",
          logic_thinking: "高",
          ethics: "中"
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
          industry: "互联网",
          vertical_promotion_path: "初级开发->中级开发->高级开发->架构师",
          prerequisite_roles: "Java基础, 数据库基础",
          lateral_transfer_directions: "前端开发,大数据开发,技术管理",
          social_demand: "高",
          industry_trend: "平稳"
        }
      }
    },
    deep_analysis: {
      can_apply: true,
      score: 78,
      missing_key_skills: [
        "Java编程语言（求职者技术栈以JavaScript/TypeScript为主）",
        "Spring Boot框架",
        "MySQL/Redis数据库"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "本科，应届生，无特殊要求",
          current: "本科软件工程应届生，满足所有基础门槛",
          gap_analysis: "完全匹配：学历、专业、应届身份均符合，无额外门槛。"
        },
        {
          dimension: "职业技能",
          required: "Java, Spring Boot, MySQL, Redis, Maven",
          current: "核心语言为JavaScript/TypeScript/Vue3，无Java开发经验，缺乏Spring Boot和MySQL实战",
          gap_analysis: "差距较大：技术栈方向不同，从JavaScript转Java需要系统学习。但编程基础扎实（数据结构、算法、Git），转型可行。"
        },
        {
          dimension: "职业素养",
          required: "团队协作高、逻辑思维高",
          current: "实习经历和项目开发验证了团队协作和逻辑思维能力",
          gap_analysis: "匹配良好：软素养与岗位要求一致，编程基础扎实有利于快速学习新技术。"
        },
        {
          dimension: "发展潜力",
          required: "学习能力高、技术取向",
          current: "自学能力强，技术热情高，有快速学习新技术的经历",
          gap_analysis: "潜力良好：学习能力是核心竞争力，建议评估是否有意愿转向Java后端方向。"
        }
      ],
      actionable_advice: "如果有意向Java后端方向，建议系统学习Java基础（集合、多线程、JVM），完成Spring Boot入门项目，掌握MySQL基本操作。可先从前端转全栈路线，逐步积累后端经验。",
      all_analysis: "求职者编程基础扎实，学习能力突出，但技术栈方向为前端而非Java后端。虽然转型可行，但需要较大的学习投入。如果对Java方向感兴趣，建议利用毕业前时间突击学习。否则建议优先投递前端相关岗位。"
    }
  },
  {
    job_id: "job_005",
    score: 0.6543210987654321,
    raw_data: {
      job_id: "job_005",
      job_name: "UI/UX设计师（校招）",
      profiles: {
        basic_requirements: {
          degree: "本科",
          major: "设计/计算机/心理学",
          certificates: "无",
          internship_requirement: "有设计实习优先",
          experience_years: "应届",
          special_requirements: "需提交设计作品集"
        },
        professional_skills: {
          core_skills: "Figma/Sketch, 设计规范, 交互设计, 用户研究",
          tool_capabilities: "Figma, Principle, Adobe XD",
          domain_knowledge: "互联网产品",
          language_requirements: "无",
          project_requirements: "有完整的产品设计项目或作品集"
        },
        professional_literacy: {
          communication: "高",
          teamwork: "高",
          stress_management: "中",
          logic_thinking: "中",
          ethics: "中"
        },
        development_potential: {
          learning_ability: "高",
          innovation: "高",
          leadership: "低",
          career_orientation: "设计",
          adaptability: "高"
        },
        job_attributes: {
          salary_competitiveness: "中",
          industry: "互联网",
          vertical_promotion_path: "初级设计->中级设计->高级设计->设计总监",
          prerequisite_roles: "设计基础, 审美能力",
          lateral_transfer_directions: "产品经理,交互设计,视觉设计",
          social_demand: "中",
          industry_trend: "平稳"
        }
      }
    },
    deep_analysis: {
      can_apply: false,
      score: 45,
      missing_key_skills: [
        "Figma/Sketch等设计工具",
        "设计规范和交互设计理论",
        "用户研究方法论",
        "设计作品集"
      ],
      gap_matrix: [
        {
          dimension: "基础要求",
          required: "本科，需提交设计作品集，有设计实习优先",
          current: "本科软件工程，无设计实习，无设计作品集",
          gap_analysis: "存在差距：专业不对口，缺少设计作品集，这是UI/UX岗位的核心硬性要求。"
        },
        {
          dimension: "职业技能",
          required: "Figma/Sketch, 设计规范, 交互设计, 用户研究",
          current: "前端开发经验使求职者对UI实现有理解，但未使用设计工具，缺乏系统设计训练",
          gap_analysis: "差距较大：前端开发与UI设计虽然相关，但核心技能完全不同，需要系统学习设计方法论。"
        },
        {
          dimension: "职业素养",
          required: "创新能力高、沟通能力高",
          current: "有一定创新能力（AI项目），沟通能力良好",
          gap_analysis: "部分匹配：创新和沟通能力具备，但设计岗位还需要较强的审美能力和用户同理心。"
        },
        {
          dimension: "发展潜力",
          required: "创新高、设计取向",
          current: "技术取向明确，创新能力强，但职业取向为技术而非设计",
          gap_analysis: "方向偏差：求职者职业取向为技术方向，与设计方向有根本性差异，不建议作为转型目标。"
        }
      ],
      actionable_advice: "不建议作为主要投递方向。如果对设计感兴趣，可以从UI开发工程师入手，发挥前端技术优势，同时学习设计工具和理论。但考虑到求职者的技术取向和核心竞争力，建议专注于前端开发方向。",
      all_analysis: "求职者虽然有前端开发经验，对UI实现有一定理解，但UI/UX设计师是独立的专业方向，需要系统的设计理论学习和大量作品积累。求职者的核心竞争力在前端技术而非设计，不建议转向此方向。"
    }
  }
]

/**
 * 模拟获取人岗匹配结果API
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockGetJobMatchResultApi(
  delayMs: number = 800
): Promise<AxiosResponse<Result<JobMatchItem[]>>> {
  await delay(delayMs)
  return wrapAsAxiosResponse({
    code: 200,
    msg: 'success',
    data: mockJobMatchItems
  })
}
