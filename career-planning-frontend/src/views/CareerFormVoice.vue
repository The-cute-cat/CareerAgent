<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import CareerFormVoice from '@/components/CareerForm_Voice.vue'
import { JOB_MATCH_STORAGE_KEY, loadCareerFormData, saveCareerFormData } from '@/utils/career-runtime'
import type { CareerFormData } from '@/types/careerform_report'
import { buildDemoJobMatchResult, mergeVoiceAnswersToForm, type VoiceCollectedAnswers } from '@/utils/voice-career-demo'
import { useCareerModeStore } from '@/stores/careerMode'

const router = useRouter()
const careerModeStore = useCareerModeStore()
const isLearningMode = computed(() => careerModeStore.isLearningMode)
const cachedFormData = ref<CareerFormData | null>(loadCareerFormData())

const formProgress = computed(() => {
  const formData = cachedFormData.value
  if (!formData) return 0

  let completed = 0
  const total = 5

  if (formData.education) completed++
  if (formData.major.length > 0) completed++
  if (formData.skills.length > 0) completed++
  if (formData.projects.length > 0 || formData.internships.length > 0) completed++
  if (formData.targetJob) completed++

  return Math.round((completed / total) * 100)
})

const hasValidLanguage = (
  languages: Array<{ type: string; level: string }>
) => languages.some(language => !!language.type?.trim() && !!language.level?.trim())

const completedStepCount = computed(() => {
  const formData = cachedFormData.value
  if (!formData) return 0

  return [
    !!(formData.education && formData.major.length > 0),
    hasValidLanguage(formData.languages) && formData.skills.length > 0,
    formData.projects.length > 0 || formData.internships.length > 0,
    !!formData.innovation?.trim(),
    !!(formData.targetJob && formData.targetIndustries.length > 0)
  ].filter(Boolean).length
})

const profileCompleteness = computed(() => {
  const formData = cachedFormData.value
  if (!formData) return 0

  let total = 0
  let completed = 0

  const basicItems = [
    !!formData.education,
    formData.major.length > 0,
    !!formData.graduationDate
  ]
  total += basicItems.length
  completed += basicItems.filter(Boolean).length

  const skillItems = [
    formData.languages.some(language => language.type && language.level),
    formData.certificates.length > 0,
    formData.skills.length > 0,
    formData.tools.length > 0
  ]
  total += skillItems.length
  completed += skillItems.filter(Boolean).length

  const expItems = [
    formData.projects.length > 0,
    formData.internships.length > 0
  ]
  total += expItems.length
  completed += expItems.filter(Boolean).length

  const careerItems = [
    !!formData.targetJob,
    formData.targetIndustries.length > 0
  ]
  total += careerItems.length
  completed += careerItems.filter(Boolean).length

  return total ? Math.round((completed / total) * 100) : 0
})

const formSnapshot = computed(() => {
  const formData = cachedFormData.value
  return {
    education: formData?.education || '',
    major: formData?.major || [],
    targetJob: formData?.targetJob || '',
    targetIndustries: formData?.targetIndustries || [],
    skillNames: formData?.skills?.map(item => item.name).filter(Boolean) || [],
    toolNames: formData?.tools?.map(item => item.name).filter(Boolean) || [],
    projectCount: formData?.projects?.length || 0,
    internshipCount: formData?.internships?.length || 0
  }
})

const resumeUploaded = computed(() => {
  const formData = cachedFormData.value
  if (!formData) return false

  return !!(
    formData.education ||
    formData.major.length ||
    formData.skills.length ||
    formData.projects.length ||
    formData.internships.length
  )
})

function handleBack(): void {
  router.push('/career-form/resume')
}

async function handleSaveToForm(collectedAnswers: VoiceCollectedAnswers): Promise<void> {
  const mergedFormData = mergeVoiceAnswersToForm(collectedAnswers, cachedFormData.value)
  saveCareerFormData(mergedFormData)
  cachedFormData.value = mergedFormData
  ElMessage.success('语音信息已模拟回填到表单')
  await router.push('/career-form/resume')
}

async function handleGenerateMatching(collectedAnswers: VoiceCollectedAnswers): Promise<void> {
  const mergedFormData = mergeVoiceAnswersToForm(collectedAnswers, cachedFormData.value)
  saveCareerFormData(mergedFormData)
  cachedFormData.value = mergedFormData

  const mockMatchResult = await buildDemoJobMatchResult(mergedFormData, isLearningMode.value)
  localStorage.setItem(JOB_MATCH_STORAGE_KEY, JSON.stringify(mockMatchResult))

  ElMessage.success('已根据语音信息生成人岗匹配结果')
  await router.push('/job-matching')
}
</script>

<template>
  <div class="career-form-voice-page">
    <CareerFormVoice
      :form-progress="formProgress"
      :profile-completeness="profileCompleteness"
      :completed-step-count="completedStepCount"
      :resume-uploaded="resumeUploaded"
      :form-snapshot="formSnapshot"
      @back="handleBack"
      @save-to-form="handleSaveToForm"
      @generate-matching="handleGenerateMatching"
    />
  </div>
</template>

<style scoped>
.career-form-voice-page {
  min-height: calc(100vh - 64px);
}
</style>
