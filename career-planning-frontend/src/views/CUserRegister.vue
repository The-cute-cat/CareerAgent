<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import type { LoginFormDTO } from '@/types/type'
import { userRegisterService, userSendCodeRegisterService } from '@/api/user/user'
import { useUserStore } from '@/stores'

const form = ref<LoginFormDTO>({})
const router = useRouter()
const userStore = useUserStore()
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
    ElMessage.warning('请输入邮箱地址')
    return
  }
  if (!emailRegex.test(form.value.email)) {
    ElMessage.warning('请输入有效的邮箱格式')
    return
  }

  codeSending.value = true
  try {
    console.log('发送验证码至邮箱:', form.value.email)
    // 模拟API调用发送验证码
    const res = await userSendCodeRegisterService(form.value) // 这里可以调用实际的发送验证码API
    console.log('验证码发送结果:', res)
    if (res.data.code !== 200) {
      ElMessage.error(res.data.message || '验证码发送失败')
    }
    ElMessage.success(`验证码已发送至 ${form.value.email}，请查收`)
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
    }, 1000)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '验证码发送失败，请重试'
    ElMessage.error(`${errorMessage}，你刚刚发送了一次验证码，请稍后再试`)
  } finally {
    codeSending.value = false
  }
}

const handleRegister = async () => {
  // 前端验证：密码一致
  if (form.value.password !== form.value.passwordConfirm) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  // 验证码不能为空
  if (!form.value.code) {
    ElMessage.warning('请输入验证码')
    return
  }

  loading.value = true
  try {
    // 模拟注册请求
    const res = await userRegisterService(form.value)
    console.log('注册结果:', res)
    if (res.data.code !== 200) {
      ElMessage.error(res.data.message || '注册失败')
    }
    userStore.clearUserALLInfo() // 清除用户信息，确保注册流程干净
    ElMessage.success('注册成功，请登录')
    await new Promise(resolve => setTimeout(resolve, 1000))
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
          <h2 class="heading-section">职业规划AI智能体</h2>
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
  min-height: 650px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.wrap .img,
.wrap .login-wrap {
  width: 50%;
}

.wrap .img {
  min-height: 650px;
}

.wrap .login-wrap {
  padding: 45px !important;
}

/* 表单元素增大 */
.form-control {
  height: 52px;
  font-size: 15px;
  padding: 10px 14px;
}

.form-group .label {
  font-size: 13px;
  margin-bottom: 6px;
}

.form-group {
  margin-bottom: 16px !important;
}

.btn-primary {
  height: 52px;
  font-size: 16px;
  font-weight: 600;
}

h3.mb-4 {
  font-size: 26px;
  margin-bottom: 25px !important;
}

/* 响应式调整 */
@media (max-width: 991.98px) {
  .wrap .img,
  .wrap .login-wrap {
    width: 100%;
  }
  
  .wrap .img {
    min-height: 180px;
    height: 180px;
  }
}

.heading-section {
  font-size: 30px;
  font-weight: 600;
  color: #201f1f;
  margin-bottom: 20px;
}

/* 补充样式，确保发送验证码按钮与输入框对齐 */
.d-flex.gap-2 {
  gap: 12px !important;
}

/* 发送验证码按钮样式 */
.btn-outline-secondary {
  height: 52px !important;
  padding: 0 16px;
  background: transparent;
  border: 1px solid #d1d5db !important;
  border-radius: 10px;
  color: #6b7280 !important;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-outline-secondary:hover:not(:disabled) {
  border-color: #9ca3af !important;
  color: #4b5563 !important;
  background: #f9fafb;
}

.btn-outline-secondary:disabled {
  border-color: #e5e7eb !important;
  color: #d1d5db !important;
  cursor: not-allowed;
  background: transparent;
}

/* 保持按钮与输入框高度一致 */
.form-group .btn {
  height: 52px;
  line-height: 1.5;
}
</style>