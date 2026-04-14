import request from '@/utils/request'
import type { Result } from '@/types/type'
import type { CodeAbilityEvaluateData, CodeAbilityEvaluateParams } from '@/types/code-ability'
import { mockEvaluateCodeAbilityApi } from '@/mock/mockdata/CodeAbility_mockdata'

const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'

export function evaluateCodeAbilityApi(data: CodeAbilityEvaluateParams) {
  if (ENABLE_MOCK) {
    return mockEvaluateCodeAbilityApi(data)
  }

  return request.post<Result<CodeAbilityEvaluateData> & { state?: string }>(
    '/codeAbility/evaluate',
    data
  )
}
