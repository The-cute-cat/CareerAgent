// src/stores/user.ts（持久化设计）
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { UserInfo } from '@/types/type'

export const useUserStore = defineStore(
  'user',
  () => {
    // 从 localStorage 或 sessionStorage 初始化 token（根据是否勾选“记住我”）
    // const accessToken = ref(
    //   localStorage.getItem('accessToken') || sessionStorage.getItem('token') || '',
    // )

    //state
    const accessToken = ref<string>('')
    const refreshToken = ref<string>('')
    const userInfo = ref<UserInfo | null>(null)

    // getter - 是否已登录
    const isLoggedIn = computed(() => !!accessToken.value) //登录状态

    // actions
    const setTokens = (access: string, refresh: string) => {
      accessToken.value = access
      refreshToken.value = refresh
    }

    const clearTokens = () => {
      accessToken.value = ''
      refreshToken.value = ''
    }

    // 设置所有用户信息（token + userInfo） - 适用于登录场景
    const setUserALLInfo = (access: string, refresh: string, user: UserInfo) => {
      accessToken.value = access
      refreshToken.value = refresh
      userInfo.value = user
    }

    // 清除所有用户信息（token + userInfo） - 适用于退出场景
    const clearUserALLInfo = () => {
      accessToken.value = ''
      refreshToken.value = ''
      userInfo.value = null
    }

    const clearUserInfo = () => {
      userInfo.value = null
    }

    return {
      accessToken,
      refreshToken,
      userInfo,
      isLoggedIn,
      setTokens,
      clearTokens,
      setUserALLInfo,
      clearUserInfo,
      clearUserALLInfo,
    }
  },
  {
    persist: true, // 一键开启持久化（会保存整个 state，但注意 token 我们已经手动管理，这里保存是为了跨页面刷新不丢失）
  },
)
