import { defineStore } from 'pinia'
import { ref } from 'vue'

import {
  createEmptyCareerReport,
  normalizeGrowthPlanData,
  type EditableSectionKey,
  type GrowthPlanData,
} from '@/types/career-report'

export const useCareerReportStore = defineStore(
  'career-report',
  () => {
    const report = ref<GrowthPlanData>(createEmptyCareerReport())
    const lastEditedSection = ref<EditableSectionKey>('student_summary')
    const reportsByJobId = ref<Record<string, GrowthPlanData>>({})
    const lastEditedSectionByJobId = ref<Record<string, EditableSectionKey>>({})
    const currentJobId = ref<string>('')
    const hasHydrated = ref(false)

    function setReport(value: GrowthPlanData): void {
      const normalized = normalizeGrowthPlanData(JSON.parse(JSON.stringify(value)) as GrowthPlanData)
      report.value = normalized
      if (currentJobId.value) {
        reportsByJobId.value[currentJobId.value] = normalized
      }
      hasHydrated.value = true
    }

    function ensureReport(fallback?: GrowthPlanData): GrowthPlanData {
      if (!hasHydrated.value && fallback) {
        setReport(fallback)
      }
      return report.value
    }

    function setCurrentJobId(jobId: string): void {
      currentJobId.value = jobId
      if (jobId && reportsByJobId.value[jobId]) {
        report.value = normalizeGrowthPlanData(JSON.parse(JSON.stringify(reportsByJobId.value[jobId])) as GrowthPlanData)
      }
      if (jobId && lastEditedSectionByJobId.value[jobId]) {
        lastEditedSection.value = lastEditedSectionByJobId.value[jobId]
      }
    }

    function setReportForJob(jobId: string, value: GrowthPlanData): void {
      const normalized = normalizeGrowthPlanData(JSON.parse(JSON.stringify(value)) as GrowthPlanData)
      reportsByJobId.value[jobId] = normalized
      currentJobId.value = jobId
      report.value = normalized
      hasHydrated.value = true
    }

    function getReportByJob(jobId: string): GrowthPlanData | null {
      const target = reportsByJobId.value[jobId]
      return target
        ? normalizeGrowthPlanData(JSON.parse(JSON.stringify(target)) as GrowthPlanData)
        : null
    }

    function ensureReportForJob(jobId: string, fallback?: GrowthPlanData): GrowthPlanData {
      const existing = getReportByJob(jobId)
      if (existing) {
        currentJobId.value = jobId
        report.value = existing
        return existing
      }

      if (fallback) {
        setReportForJob(jobId, fallback)
        return report.value
      }

      currentJobId.value = jobId
      report.value = createEmptyCareerReport()
      return report.value
    }

    function setLastEditedSection(section: EditableSectionKey): void {
      lastEditedSection.value = section
      if (currentJobId.value) {
        lastEditedSectionByJobId.value[currentJobId.value] = section
      }
    }

    function getLastEditedSectionByJob(jobId: string): EditableSectionKey {
      return lastEditedSectionByJobId.value[jobId] || 'student_summary'
    }

    return {
      report,
      lastEditedSection,
      reportsByJobId,
      lastEditedSectionByJobId,
      currentJobId,
      hasHydrated,
      setReport,
      ensureReport,
      setCurrentJobId,
      setReportForJob,
      getReportByJob,
      ensureReportForJob,
      setLastEditedSection,
      getLastEditedSectionByJob,
    }
  },
  {
    persist: {
      key: 'career-report-store',
      pick: ['report', 'lastEditedSection', 'reportsByJobId', 'lastEditedSectionByJobId', 'currentJobId', 'hasHydrated'],
    },
  }
)
