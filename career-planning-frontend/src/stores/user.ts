// src/stores/user.ts（持久化设计）
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore(
  'user',
  () => {
    // 从 localStorage 或 sessionStorage 初始化 token（根据是否勾选“记住我”）
    const token = ref(localStorage.getItem('token') || sessionStorage.getItem('token') || '')
    const userInfo = ref<any>(null)

    const isAuthenticated = computed(() => !!token.value)

    // 登录 action
    async function login(username: string, password: string, rememberMe: boolean) {
      // 这里替换为真实的 API 调用
      // const res = await loginApi({ username, password })
      // 模拟登录成功
      const fakeToken = 'fake-jwt-token-' + Date.now()
      const fakeUser = { username, email: `${username}@example.com` }

      token.value = fakeToken
      userInfo.value = fakeUser

      if (rememberMe) {
        localStorage.setItem('token', fakeToken)
        sessionStorage.removeItem('token')
      } else {
        sessionStorage.setItem('token', fakeToken)
        localStorage.removeItem('token')
      }
    }

    // 登出 action
    function logout() {
      token.value = ''
      userInfo.value = null
      localStorage.removeItem('token')
      sessionStorage.removeItem('token')
    }

    return { token, userInfo, isAuthenticated, login, logout }
  },
  {
    persist: true, // 一键开启持久化（会保存整个 state，但注意 token 我们已经手动管理，这里保存是为了跨页面刷新不丢失）
  }
)