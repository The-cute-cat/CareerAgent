import axios from 'axios'
import { useUserStore } from '@/stores/index'
import router from '@/router'

let isRefreshing = false

const baseURL = '/api'

const instance = axios.create({
  baseURL,
  timeout: 1000000,
})

instance.interceptors.request.use((config) => {
  const userStore = useUserStore()
  const accessToken = userStore.accessToken

  config.headers = config.headers ?? {}

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }

  if (
    ['post', 'put', 'patch'].includes((config.method || '').toLowerCase()) &&
    !(config.data instanceof FormData)
  ) {
    config.headers['Content-Type'] = 'application/json'
  }

  return config
})

instance.interceptors.response.use(
  (result) => result,
  async (err) => {
    console.log('登录错误', err.response)

    if (err.response?.status === 401) {
      const userStore = useUserStore()
      const refreshToken = userStore.refreshToken

      if (!refreshToken) {
        logout()
        return Promise.reject(err)
      }

      if (isRefreshing) {
        return Promise.reject(err)
      }

      isRefreshing = true

      try {
        const res = await axios.post(baseURL + '/user/refreshToken', {
          refreshToken,
        })

        if (res.data.code === 200) {
          userStore.setTokens(res.data.data.accessToken, res.data.data.refreshToken)

          const originalRequest = err.config
          originalRequest.headers = originalRequest.headers ?? {}
          originalRequest.headers.Authorization = `Bearer ${res.data.data.accessToken}`

          return instance(originalRequest)
        }

        logout()
        return Promise.reject(err)
      } catch (refreshErr) {
        logout()
        return Promise.reject(refreshErr)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(err)
  },
)

function logout() {
  const userStore = useUserStore()
  userStore.clearUserALLInfo()
  console.log('登录已过期，请重新登录')
  router.push('/login')
}

export default instance
