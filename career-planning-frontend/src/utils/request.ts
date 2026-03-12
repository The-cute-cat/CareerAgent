// src/utils/request.ts 导入axios
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/index'
import router from '@/router' // 直接导入实例，不需要 hooks
// 在 request.ts 顶部定义一个标志
let isRefreshing = false

// 创建全局变量地址
// const baseURL ='http://localhsot:8080';
// const instance=axios.create({baseURL})
const baseURL = '/api'
const instance = axios.create({
  baseURL,
  timeout: 10000, // 请求超时时间(毫秒)
})

// 请求拦截器，自动添加token
instance.interceptors.request.use((config) => {
  const userStore = useUserStore()
  const accessToken = userStore.accessToken
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  } /* else{
    const refreshToken = localStorage.getItem('refreshToken');
    if(refreshToken){
      config.headers.Authorization = `Bearer ${refreshToken}`;
    }
    console.log("无无refreshToken");
  } */
  return config
})

//添加响应拦截器
instance.interceptors.response.use(
  (result) => result,
  async (err) => {
    console.log('登录错误', err.response)
    if (err.response.status === 401) {
      // 短token过期，尝试刷新
      const userStore = useUserStore()
      const refreshToken = userStore.refreshToken
      if (!refreshToken) {
        // 无长token，直接跳出 执行登录
        logout()
        console.log('无无无refreshToken')
        return Promise.reject(err)
      }

      // ✅ 核心：如果已经在刷新了，直接返回等待，不要重复发请求
      if (isRefreshing) {
        // 这里其实最好返回一个 Promise 等待刷新结果，但简单做法是直接拒绝，让用户重试
        // 或者你可以用数组队列把请求存起来，这里为了简洁，我们先返回错误
        return Promise.reject(err)
      }

      isRefreshing = true // 开锁

      try {
        // 调用刷新接口获取新的短token
        // const res = await instance.post('/user/refreshToken',
        // 引用上面的错误的instance不对因为上面的短token过期了
        const res = await axios.post(baseURL + '/user/refreshToken', {
          refreshToken,
        })
        console.log('res', res)
        console.log('res', res.data)
        console.log('res', res.data.code)

        if (res.data.code === 200) {
          // 刷新成功，更新短token
          // localStorage.setItem('accessToken', res.data.data.accessToken)
          // localStorage.setItem('refreshToken', res.data.data.refreshToken)
          userStore.setTokens(res.data.data.accessToken, res.data.data.refreshToken)
          // 重试原请求
          console.log('err.config', err.config)
          const originalRequest = err.config
          originalRequest.headers.Authorization = `Bearer ${res.data.data.accessToken}`
          return instance(originalRequest)
        } else {
          // 刷新失败，跳登录
          console.log('res', res)

          // ElMessage.error(res)
          logout()
          return Promise.reject(err)
        }
      } catch (refreshErr) {
        // 刷新接口失败（长token也过期）
        logout()
        return Promise.reject(refreshErr)
      }
    }
    return Promise.reject(err)
  },
)

// 登出清理函数
function logout() {
  // localStorage.removeItem('accessToken')
  // localStorage.removeItem('refreshToken')
  // localStorage.removeItem('userRole') // 清除角色信息
  const userStore = useUserStore()
  userStore.clearUserALLInfo()
  console.log('登录已过期，请重新登录')
  router.push('/login')
}

export default instance