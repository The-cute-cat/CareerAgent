import { defineStore } from 'pinia'
import { ref } from 'vue'

import {
  createEmptyCareerReport,
  type EditableSectionKey,
  type GrowthPlanData,
} from '@/types/career-report'

export const useCareerReportStore = defineStore(
  'career-report',
  () => {
    const report = ref<GrowthPlanData>(createEmptyCareerReport())
    const lastEditedSection = ref<EditableSectionKey>('student_summary')
    const hasHydrated = ref(false)

    function setReport(value: GrowthPlanData): void {
      report.value = JSON.parse(JSON.stringify(value)) as GrowthPlanData
      hasHydrated.value = true
    }

    function ensureReport(fallback?: GrowthPlanData): GrowthPlanData {
      if (!hasHydrated.value && fallback) {
        setReport(fallback)
      }
      return report.value
    }

    function setLastEditedSection(section: EditableSectionKey): void {
      lastEditedSection.value = section
    }

    return {
      report,
      lastEditedSection,
      hasHydrated,
      setReport,
      ensureReport,
      setLastEditedSection,
    }
  },
  {
    persist: {
      key: 'career-report-store',
      pick: ['report', 'lastEditedSection', 'hasHydrated'],
    },
  }
)
