<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import type { LoginFormDTO } from '@/types/type'
import { register } from '@/api/user/user'

const form = ref<LoginFormDTO>({})
const router = useRouter()

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)

// 验证码相关状态
const codeSending = ref(false)
const codeCountdown = ref(0)
let countdownTimer: number | null = null

// 发送验证码函数
const sendVerificationCode = async () => {
  // 简单的邮箱格式校验
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.value.email) {
    alert('请输入邮箱地址')
    return
  }
  if (!emailRegex.test(form.value.email)) {
    alert('请输入有效的邮箱格式')
    return
  }

  codeSending.value = true
  try {
    console.log('发送验证码至邮箱:', form.value.email)
    // 模拟API调用发送验证码
    await register(from.value) // 这里可以调用实际的发送验证码API

    alert(`验证码已发送至 ${form.value.email} (演示模式，请检查控制台)`)

    // 启动倒计时 60 秒
    codeCountdown.value = 60
    if (countdownTimer) clearInterval(countdownTimer)
    countdownTimer = setInterval(() => {
      if (codeCountdown.value > 0) {
        codeCountdown.value--
      } else {
        if (countdownTimer) {
          clearInterval(countdownTimer)
          countdownTimer = null
        }
      }
    }, 1000) as any
  } catch (error: any) {
    alert(error.message || '验证码发送失败，请重试')
  } finally {
    codeSending.value = false
  }
}

const handleRegister = async () => {
  // 前端验证：密码一致
  if (form.value.password !== form.value.passwordConfirm) {
    alert('两次输入的密码不一致')
    return
  }
  // 验证码不能为空
  if (!form.value.code) {
    alert('请输入验证码')
    return
  }

  loading.value = true
  try {
    // 模拟注册请求
    console.log('注册信息', {
      username: form.value.username,
      email: form.value.email,
      verificationCode: form.value.code,
      password: form.value.password,
    })

    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '注册失败'
    ElMessage.error(errorMessage)
    console.log("注册失败", error);
  } finally {
    loading.value = false
  }
}

// 清理定时器
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
})
</script>

<template>
  <link href="https://fonts.googleapis.com/css?family=Lato:300,400,700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

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
            <!-- 左侧背景图  -->
            <div class="img" :style="{ backgroundImage: 'url(/images/bg-1.jpg)' }"></div>

            <!-- 右侧注册表单  -->
            <div class="login-wrap p-4 p-md-5">
              <div class="d-flex">
                <div class="w-100">
                  <h3 class="mb-4">注册</h3>
                </div>
              </div>

              <form class="signin-form" @submit.prevent="handleRegister">
                <!-- 昵称 -->
                <div class="form-group mb-3">
                  <label class="label" for="username">昵称</label>
                  <input type="text" class="form-control" placeholder="请输入昵称" id="username" v-model="form.username"
                    required />
                </div>

                <!-- 邮箱  -->
                <div class="form-group mb-3">
                  <label class="label" for="email">邮箱</label>
                  <input type="email" class="form-control" placeholder="请输入邮箱地址" id="email" v-model="form.email"
                    required />
                </div>

                <!-- 密码 -->
                <div class="form-group mb-3">
                  <label class="label" for="password">密码</label>
                  <div class="position-relative">
                    <input :type="showPassword ? 'text' : 'password'" class="form-control" placeholder="请输入密码"
                      id="password" v-model="form.password" required />
                    <span class="fa fa-fw" :class="showPassword ? 'fa-eye-slash' : 'fa-eye'"
                      @click="showPassword = !showPassword"
                      style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;"></span>
                  </div>
                </div>

                <!-- 确认密码 (带独立显示切换) -->
                <div class="form-group mb-3">
                  <label class="label" for="password_confirm">确认密码</label>
                  <div class="position-relative">
                    <input :type="showConfirmPassword ? 'text' : 'password'" class="form-control" placeholder="请再次输入密码"
                      id="password_confirm" v-model="form.passwordConfirm" required />
                    <span class="fa fa-fw" :class="showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'"
                      @click="showConfirmPassword = !showConfirmPassword"
                      style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;"></span>
                  </div>
                </div>

                <!-- 验证码输入框 + 发送按钮 (放在最下面，位于同一行) -->
                <div class="form-group mb-3">
                  <label class="label" for="verification_code">验证码</label>
                  <div class="d-flex align-items-center gap-2" style="gap: 8px;">
                    <input type="text" class="form-control" placeholder="请输入邮箱收到的验证码" id="verification_code"
                      v-model="form.code" required style="flex: 1;" />
                    <button type="button" class="btn btn-outline-secondary" style="width: 120px; white-space: nowrap;"
                      @click="sendVerificationCode" :disabled="codeSending || codeCountdown > 0">
                      <span v-if="codeSending">发送中...</span>
                      <span v-else-if="codeCountdown > 0">{{ codeCountdown }}秒后重发</span>
                      <span v-else>发送验证码</span>
                    </button>
                  </div>
                </div>

                <!-- 注册按钮 -->
                <div class="form-group">
                  <button type="submit" class="form-control btn btn-primary rounded submit px-3" :disabled="loading">
                    {{ loading ? '注册中...' : '注册' }}
                  </button>
                </div>
              </form>

              <!-- 登录链接 -->
              <p class="text-center">
                已有账号?
                <router-link to="/login">登录</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style>
@import '/public/css/style.css';

/* 补充样式，确保发送验证码按钮与输入框对齐 */
.d-flex.gap-2 {
  gap: 0.5rem !important;
}

.btn-outline-secondary {
  border-color: #ced4da;
  color: #6c757d;
}

.btn-outline-secondary:hover {
  background-color: #e9ecef;
  color: #343a40;
}

/* 保持按钮与输入框高度一致 */
.form-group .btn {
  height: calc(1.5em + 0.75rem + 2px);
  line-height: 1.5;
}
</style>
