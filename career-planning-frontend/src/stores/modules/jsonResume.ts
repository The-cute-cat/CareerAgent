import { defineStore } from 'pinia'
import { ref } from 'vue'

import type { CareerFormData } from '@/types/careerform_report'
import type {
  JsonResume,
  JsonResumeGenerationResult,
  ResumeProfileExtras
} from '@/types/json-resume'
import {
  createDefaultResumeProfileExtras,
  generateJsonResume
} from '@/utils/json-resume'

/**
 * JSON Resume 状态管理。
 * 用于后续模板预览、简历编辑、内容完整性检查以及导出流程复用统一数据源。
 */
export const useJsonResumeStore = defineStore(
  'json-resume',
  () => {
    /** 当前输入的扩展资料。 */
    const profileExtras = ref<ResumeProfileExtras>(createDefaultResumeProfileExtras())

    /** 当前生成结果。 */
    const generationResult = ref<JsonResumeGenerationResult | null>(null)

    /** 当前标准化简历对象。 */
    const resume = ref<JsonResume | null>(null)

    /**
     * 设置额外资料。
     * @param value 额外个人资料字段
     */
    function setProfileExtras(value: ResumeProfileExtras): void {
      profileExtras.value = value
    }

    /**
     * 通过 CareerFormData 生成 JSON Resume。
     * @param careerFormData 现有职业画像表单
     * @returns 生成结果
     */
    function buildFromCareerForm(careerFormData: CareerFormData): JsonResumeGenerationResult {
      const result = generateJsonResume({
        careerFormData,
        profileExtras: profileExtras.value
      })

      generationResult.value = result
      resume.value = result.resume
      return result
    }

    /** 重置状态。 */
    function resetJsonResume(): void {
      profileExtras.value = createDefaultResumeProfileExtras()
      generationResult.value = null
      resume.value = null
    }

    return {
      profileExtras,
      generationResult,
      resume,
      setProfileExtras,
      buildFromCareerForm,
      resetJsonResume
    }
  },
  {
    persist: {
      key: 'career-json-resume-store',
      pick: ['profileExtras']
    }
  }
)
