import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export type CareerMode = 'learning' | 'job'

const CAREER_MODE_STORAGE_KEY = 'career-agent-mode'

const isClient = () => typeof window !== 'undefined'

const readStoredMode = (): CareerMode => {
  if (!isClient()) return 'learning'

  const value = window.localStorage.getItem(CAREER_MODE_STORAGE_KEY)
  return value === 'job' ? 'job' : 'learning'
}

export const useCareerModeStore = defineStore('career-mode', () => {
  const mode = ref<CareerMode>('learning')
  const initialized = ref(false)

  const persistMode = (value: CareerMode) => {
    if (!isClient()) return
    window.localStorage.setItem(CAREER_MODE_STORAGE_KEY, value)
  }

  const initMode = () => {
    if (initialized.value) return
    mode.value = readStoredMode()
    initialized.value = true
  }

  const setMode = (value: CareerMode) => {
    mode.value = value
    persistMode(value)
    initialized.value = true
  }

  const isLearningMode = computed(() => mode.value === 'learning')
  const isJobMode = computed(() => mode.value === 'job')

  return {
    mode,
    isLearningMode,
    isJobMode,
    setMode,
    initMode,
  }
})
