import type { AxiosResponse } from 'axios'
import type { CodeAbilityEvaluateData, CodeAbilityEvaluateParams } from '@/types/code-ability'
import type { Result } from '@/types/type'

type CodeAbilityMockResponse = Result<CodeAbilityEvaluateData> & { state?: 'success' | 'error' }

function wrapAsAxiosResponse<T>(result: T): AxiosResponse<T> {
  return {
    data: result,
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as any
  }
}

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const mockCodeAbilityBasicResult: CodeAbilityMockResponse = {
  code: 200,
  state: 'success',
  msg: '代码能力评估完成',
  data: {
    platform: 'github',
    username: 'frontend-dev-student',
    composite_score: 78,
    level: 'B',
    features: {
      composite: {
        total_score: 78,
        level: 'B',
        dimension_scores: {
          project_scale: 76,
          tech_breadth: 82,
          activity: 69,
          engineering: 74,
          community: 58
        },
        weights: {
          project_scale: 25,
          tech_breadth: 15,
          activity: 25,
          engineering: 20,
          community: 15
        },
        max_score: 100
      }
    }
  }
}

export const mockCodeAbilityAiResult: CodeAbilityMockResponse = {
  code: 200,
  state: 'success',
  msg: '代码能力深度分析完成',
  data: {
    platform: 'github',
    username: 'frontend-dev-student',
    composite_score: 84,
    level: 'A',
    features: {
      composite: {
        total_score: 84,
        level: 'A',
        dimension_scores: {
          project_scale: 83,
          tech_breadth: 88,
          activity: 79,
          engineering: 85,
          community: 71
        },
        weights: {
          project_scale: 25,
          tech_breadth: 15,
          activity: 25,
          engineering: 20,
          community: 15
        },
        max_score: 100
      }
    },
    ai_analysis: {
      overall_assessment: {
        summary: '候选人具备较完整的前端工程能力，项目呈现出良好的组件化思维与一定的全栈协作意识。',
        highlights: ['Vue 生态较完整', '项目落地能力较强', '工程规范意识良好'],
        concerns: ['社区影响力偏弱', '持续活跃度还有提升空间', '技术深度集中在前端方向'],
        level: 'A',
        score: 84
      },
      tech_stack_analysis: {
        primary_languages: ['Vue 3', 'TypeScript', 'Vite', 'Element Plus'],
        tech_domains: ['前端开发', 'Node.js', 'Docker'],
        breadth_assessment: '技术栈覆盖现代前端主流方案，能够支持中小型业务项目开发与迭代。',
        depth_assessment: '在前端领域有较深入的理解和实践',
        suggestion: '建议补充自动化测试体系和性能优化实践'
      },
      project_quality_analysis: {
        quality_rating: '代码结构整体清晰，模块职责划分合理，具备可维护性。',
        project_scale: '中等规模项目为主',
        engineering_habits: '有良好的代码规范和工程化意识',
        suggestion: '建议补充单元测试和 CI/CD 流程'
      },
      activity_analysis: {
        consistency: '提交频率较为稳定',
        recent_focus: '近期主要关注前端技术',
        suggestion: '建议保持持续贡献节奏'
      },
      career_alignment: {
        suitable_roles: ['前端工程师', '全栈工程师'],
        skill_gaps: ['系统架构设计', '性能优化'],
        growth_direction: '向前端架构师方向发展'
      },
      actionable_advice: [
        {
          action: '补齐 README 中的部署与运行说明',
          expected_outcome: '提高项目的可维护性和协作效率',
          priority: '高',
          reason: '文档是开源项目的重要组成部分'
        },
        {
          action: '为核心页面增加测试用例',
          expected_outcome: '提高代码质量和稳定性',
          priority: '中',
          reason: '测试是保证代码质量的重要手段'
        },
        {
          action: '输出 1 到 2 个高质量开源项目',
          expected_outcome: '提升个人影响力和技术深度',
          priority: '中',
          reason: '开源贡献是技术成长的重要途径'
        }
      ]
    }
  }
}

export const mockCodeAbilityNotFound: CodeAbilityMockResponse = {
  code: 404,
  state: 'error',
  msg: '用户不存在或仓库不可访问',
  data: null
}

/**
 * 从用户主页 URL 中提取用户名
 * 支持的格式: https://github.com/username 或 https://gitee.com/username
 * @param url - 用户主页链接
 * @returns 提取的用户名，失败返回 null
 */
function extractUsernameFromProfileUrl(url: string): string | null {
  try {
    const urlObj = new URL(url)
    const pathname = urlObj.pathname.replace(/\/+$/, '') // 移除尾部斜杠
    const segments = pathname.split('/').filter(Boolean)

    // 主页 URL 格式: /username，只需要 1 段
    if (segments.length >= 1) {
      return segments[0]! // 第一段是用户名
    }
    return null
  } catch {
    // URL 解析失败，尝试正则匹配
    const match = url.match(/github\.com\/([^\/]+)|gitee\.com\/([^\/]+)/i)
    return (match?.[1] ?? match?.[2]) || null
  }
}

/**
 * 代码能力评估 Mock API
 * 根据参数返回对应的 Mock 数据，支持模拟延迟和错误场景
 *
 * @param params - 评估参数（URL 字符串和是否启用 AI 分析）
 * @param delayMs - 模拟延迟时间（毫秒），默认 1200ms
 * @returns AxiosResponse 包装的 Mock 结果
 */
export async function mockEvaluateCodeAbilityApi(
  params: CodeAbilityEvaluateParams,
  delayMs = 1200
): Promise<AxiosResponse<CodeAbilityMockResponse>> {
  await delay(delayMs)

  // 将 URL 字符串按分隔符分割成列表（支持换行、英文逗号、中文逗号）
  const normalizedUrls = (params.url || '')
    .split(/[\n,，]/)
    .map(url => url.trim())
    .filter(Boolean)

  // 空列表或包含错误标记的 URL 返回 404
  const hasErrorMarker = normalizedUrls.some((url) => {
    const normalized = url.toLowerCase()
    return normalized.includes('not-found') || normalized.includes('404')
  })

  if (!normalizedUrls.length || hasErrorMarker) {
    return wrapAsAxiosResponse(mockCodeAbilityNotFound)
  }

  const baseData = params.use_ai ? mockCodeAbilityAiResult : mockCodeAbilityBasicResult

  // 检测平台：任一 URL 包含 gitee 则认为是 Gitee 平台
  const platform = normalizedUrls.some(url => url.toLowerCase().includes('gitee')) ? 'gitee' : 'github'

  // 提取用户名：尝试从第一个有效 URL 中提取（前面已检查 normalizedUrls 非空）
  const firstUrl = normalizedUrls[0]!
  const username = extractUsernameFromProfileUrl(firstUrl) || baseData.data?.username || 'unknown'

  return wrapAsAxiosResponse({
    ...baseData,
    data: baseData.data
      ? {
          ...baseData.data,
          platform,
          username
        }
      : null
  })
}
