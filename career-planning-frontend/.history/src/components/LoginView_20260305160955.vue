<template>
  <link href="https://fonts.googleapis.com/css?family=Lato:300,400,700&display=swap" rel="stylesheet">
  <section class="ftco-section">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 text-center mb-5">
          <h2 class="heading-section">职业规划</h2>
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
                  <input type="text" class="form-control" placeholder="请输入您的用户名" id="username"
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
                    <label class="checkbox-wrap checkbox-primary mb-0">
                      记住我
                      <input type="checkbox" v-model="loginform.rememberMe" />
                      <span class="checkmark"></span>
                    </label>
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

<script setup>
import { ref, reactive } from 'vue'
// import { useRouter, useRoute } from 'vue-router'
import { LoginFormDTO } from '@/types/type'
import { login } from '@/api/user/user'
// const router = useRouter()
// const route = useRoute()

// 登录表单数据
const loginform = reactive < LoginFormDTO > ({})

const showPassword = ref(false)
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    console.log("loginform 参数", loginform);
    const result = await login(loginform)
    console.log("result 结果", result);
    localStorage.setItem('accessToken', result.data.data.accessToken)
    localStorage.setItem('refreshToken', result.data.data.refreshToken)
    // const redirect = (route.query.redirect as string) || '/'
    // router.push(redirect)
  } catch (error) {
    alert(error.message || 'Login failed')
  } finally {
    loading.value = false
  }
}

</script>

<style>
@import '/public/css/style.css';
</style>
