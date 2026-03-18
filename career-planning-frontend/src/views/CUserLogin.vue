<script setup lang="ts">

import { ElNotification } from 'element-plus'

import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { LoginFormDTO } from '@/types/type'
import { userLoginService } from '@/api/user/user'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'

const router = useRouter()   // 等同于以前的 this.$router
// import { useRoute } from 'vue-router'
// const route = useRoute()


// 登录表单数据
const loginform = reactive<LoginFormDTO>({})
const userStore = useUserStore()
const showPassword = ref(false)
const loading = ref(false)
// const rememberMe = ref(false) // 对应“记住我”复选框


const handleLogin = async () => {
  loading.value = true
  try {
    console.log("loginform 参数", loginform);
    const result = await userLoginService(loginform)
    console.log("result 结果", result);

    userStore.setUserALLInfo(
      result.data.data.accessToken,
      result.data.data.refreshToken,
      result.data.data.userInfo
    )

    // sessionStorage.setItem('accessToken', result.data.data.accessToken)
    // sessionStorage.setItem('refreshToken', result.data.data.refreshToken)
    // sessionStorage.setItem('userInfo', JSON.stringify(result.data.data.userInfo))

    // const redirect = (route.query.redirect as string) || '/'
    // router.push(redirect)
    router.push('/')
    showSuccessNotification()
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '登录失败'
    ElMessage.error(errorMessage)
    console.log("登录失败", error);
  } finally {
    loading.value = false
  }
}

// 根据当前时间获取问候语
const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour < 12) return '上午好'
  if (hour < 18) return '下午好'
  return '晚上好'
}


const showSuccessNotification = () => {
  ElNotification({
    title: '登录成功',
    message: `${getGreeting()}，欢迎您, ${loginform.username}`,
    type: 'success',
  })
}


</script>

<template>
  <link href="https://fonts.googleapis.com/css?family=Lato:300,400,700&display=swap" rel="stylesheet">
  <section class="ftco-section">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 text-center mb-5">
          <h2 class="heading-section">职业规划AI智能体</h2>
        </div>
      </div>
      <div class="row justify-content-center">
        <div class="col-md-12 col-lg-10">
          <div class="wrap d-md-flex">
            <div class="img" :style="{ backgroundImage: 'url(/images/bg-1.jpg)' }"></div>
            <div class="login-wrap p-4 p-md-5">
              <div class="d-flex">
                <div class="w-100">
                  <h3 class="mb-4">登录</h3>
                </div>


              </div>
              <form class="signin-form" @submit.prevent="handleLogin">
                <div class="form-group mb-3">
                  <label class="label" for="username">用户名</label>
                  <input type="text" class="form-control" placeholder="请输入邮箱地址" id="username"
                    v-model="loginform.username" required />
                </div>
                <div class="form-group mb-3">
                  <label class="label" for="password">密码</label>
                  <div class="position-relative">
                    <input :type="showPassword ? 'text' : 'password'" class="form-control" placeholder="请输入密码"
                      id="password" v-model="loginform.password" required />
                    <span class="fa fa-fw" :class="showPassword ? 'fa-eye-slash' : 'fa-eye'"
                      @click="showPassword = !showPassword"
                      style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;"></span>
                  </div>
                </div>
                <div class="form-group">
                  <button type="submit" class="form-control btn btn-primary rounded submit px-3" :disabled="loading">
                    {{ loading ? '登录中...' : '登录' }}
                  </button>
                </div>
                <div class="form-group d-md-flex">
                  <div class="w-50 text-left">
                  </div>
                  <div class="w-50 text-md-right">
                    <router-link to="/forgot-password">忘记密码</router-link>
                  </div>
                </div>
              </form>
              <p class="text-center">
                还没有账号?
                <router-link to="/register">注册</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
@import '/css/style.css';

/* 全局居中布局 */
.ftco-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  width: 100vw;
  background: linear-gradient(135deg, #7b7474 0%, #b0b2b4 50%, #7b7d7e 100%);
}

.ftco-section .container {
  width: 100% !important;
  max-width: 1200px !important;
  margin: 0 auto !important;
  padding-left: 20px;
  padding-right: 20px;
}

/* 增大的内容框 */
.wrap {
  min-height: 600px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.wrap .img,
.wrap .login-wrap {
  width: 50%;
}

.wrap .img {
  min-height: 600px;
}

.wrap .login-wrap {
  padding: 50px !important;
}

/* 表单元素增大 */
.form-control {
  height: 54px;
  font-size: 16px;
  padding: 12px 16px;
}

.form-group .label {
  font-size: 14px;
  margin-bottom: 8px;
}

.btn-primary {
  height: 54px;
  font-size: 16px;
  font-weight: 600;
}

h3.mb-4 {
  font-size: 28px;
  margin-bottom: 30px !important;
}

/* 响应式调整 */
@media (max-width: 991.98px) {

  .wrap .img,
  .wrap .login-wrap {
    width: 100%;
  }

  .wrap .img {
    min-height: 200px;
    height: 200px;
  }
}

.heading-section {
  font-size: 30px;
  font-weight: 600;
  color: #201f1f;
  margin-bottom: 20px;
}
</style>
