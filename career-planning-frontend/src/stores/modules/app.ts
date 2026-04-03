import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 匹配系统当前的主题
  const getSystemTheme = () => {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  const isDarkMode = ref(getSystemTheme())

  const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value
  }

  // 监听器：根据 isDarkMode 同步更新 html 上的 dark 类，支持 VueUse/ElementPlus 样式
  watch(
    isDarkMode,
    (val) => {
      if (val) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },
    { immediate: true } // 立即执行，初始化页面状态
  )

  return {
    isDarkMode,
    toggleDarkMode
  }
}, {
  persist: true // 持久化，刷新保持偏好
})
