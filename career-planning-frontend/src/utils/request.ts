// src/utils/request.ts 导入axios
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建全局变量地址
// const baseURL ='http://localhsot:8080';
// const instance=axios.create({baseURL})
const baseURL = '/api'
const instance = axios.create({
  baseURL,
})

//添加响应拦截器
instance.interceptors.response.use(
  (result) => result,
  async (err) => {
    console.log('登录错误', err.response)
    if (err.response.status === 401) {
      // 短token过期，尝试刷新
      const refreshToken = localStorage.getItem('refreshToken')
      if (!refreshToken) {
        // 无长token，直接跳出 执行登录
        logout()
        console.log('无无无refreshToken')
        return Promise.reject(err)
      }
      try {
        // 调用刷新接口获取新的短token
        const res = await instance.post('/user/refreshToken', {
          refreshToken,
        })
        console.log('res', res)
        console.log('res', res.data)
        console.log('res', res.data.code)

        if (res.data.code === 200) {
          // 刷新成功，更新短token
          localStorage.setItem('accessToken', res.data.data.accessToken)
          localStorage.setItem('refreshToken', res.data.data.refreshToken)
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
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('userRole') // 清除角色信息
  console.log('登录已过期，请重新登录')
  // router.push('/login')
}
instance.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem('accessToken')
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
export default instance
