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
        rank: 'B',
        percentile: 72,
        dimensions: {
          project_scale: 76,
          tech_breadth: 82,
          activity: 69,
          engineering: 74,
          influence: 58
        }
      }
    },
    ai_analysis: null
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
        rank: 'A',
        percentile: 86,
        dimensions: {
          project_scale: 83,
          tech_breadth: 88,
          activity: 79,
          engineering: 85,
          influence: 71
        }
      }
    },
    ai_analysis: {
      overall_assessment: {
        summary: '候选人具备较完整的前端工程能力，项目呈现出良好的组件化思维与一定的全栈协作意识。',
        strengths: ['Vue 生态较完整', '项目落地能力较强', '工程规范意识良好'],
        weaknesses: ['社区影响力偏弱', '持续活跃度还有提升空间', '技术深度集中在前端方向']
      },
      tech_stack_analysis: {
        primary_stack: ['Vue 3', 'TypeScript', 'Vite', 'Element Plus'],
        secondary_stack: ['Node.js', 'Express', 'MySQL', 'Docker'],
        stack_maturity: '技术栈覆盖现代前端主流方案，能够支持中小型业务项目开发与迭代。',
        stack_recommendations: ['补充自动化测试体系', '加强性能优化与监控实践', '增加工程化构建与部署经验']
      },
      project_quality_analysis: {
        code_quality: '代码结构整体清晰，模块职责划分合理，具备可维护性。',
        architecture: '项目以典型前端分层为主，组件复用和状态管理思路较明确。',
        best_practices: ['使用 TypeScript 约束数据结构', '接口层与视图层职责拆分', '表单与弹窗流程较完整'],
        improvement_areas: ['补充单元测试和端到端测试', '强化错误处理和边界状态', '增加 CI/CD 流程说明']
      },
      actionable_advice: {
        short_term: ['补齐 README 中的部署与运行说明', '为核心页面增加测试用例'],
        mid_term: ['输出 1 到 2 个高质量开源项目', '完善项目性能优化与埋点方案'],
        long_term: ['提升开源参与度与社区影响力', '向架构设计和复杂工程治理方向深化']
      }
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
 * 从代码仓库 URL 中提取用户名（仓库所有者）
 * 支持的格式: https://github.com/owner/repo 或 https://gitee.com/owner/repo
 * @param url - 代码仓库链接
 * @returns 提取的用户名，失败返回 null
 */
function extractUsernameFromRepoUrl(url: string): string | null {
  try {
    const urlObj = new URL(url)
    const pathname = urlObj.pathname.replace(/\/+$/, '') // 移除尾部斜杠
    const segments = pathname.split('/').filter(Boolean)

    // 代码仓库 URL 格式: /owner/repo，至少需要 2 段
    if (segments.length >= 2) {
      return segments[0]! // 第一段是仓库所有者
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
 * @param params - 评估参数（URL 列表和是否启用 AI 分析）
 * @param delayMs - 模拟延迟时间（毫秒），默认 1200ms
 * @returns AxiosResponse 包装的 Mock 结果
 */
export async function mockEvaluateCodeAbilityApi(
  params: CodeAbilityEvaluateParams,
  delayMs = 1200
): Promise<AxiosResponse<CodeAbilityMockResponse>> {
  await delay(delayMs)

  // 规范化 URL 列表：去空白、去空值
  const normalizedUrls = (params.urls || [])
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
  const username = extractUsernameFromRepoUrl(firstUrl) || baseData.data?.username || 'unknown'

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
