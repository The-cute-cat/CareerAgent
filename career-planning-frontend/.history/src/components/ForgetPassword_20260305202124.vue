<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { LoginFormDTO } from '@/types/type'
import { sendCodeForget, forgetPassword } from '@/api/user/user'
const router = useRouter()

// 步骤控制
const step = ref(1)

// 发送验证码表单
const form = ref<LoginFormDTO>({})
const sending = ref(false)

// 重置密码表单
const resetForm = reactive({
  code: '',
  newPassword: '',
  confirmPassword: '',
})
const resetting = ref(false)

// 密码可见性
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// 发送验证码
const sendCode = async () => {
  sending.value = true
  try {
    const res = await sendCodeForget(form)
    console.log('发送验证码结果:', res)
    if (res.data.code !== 200) {
      throw new Error(res.data.message || '验证码发送失败')
    }
    step.value = 2
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '注册失败'
    ElMessage.error(errorMessage)
    console.log("注册失败", error);
  } finally {
    sending.value = false
  }
}

// 重置密码
const resetPassword = async () => {
  if (resetForm.newPassword !== resetForm.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  resetting.value = true
  try {
    // 模拟重置密码 API 调用
    // await userStore.resetPassword({ email: form.email, code: resetForm.code, newPassword: resetForm.newPassword })
    alert('密码重置成功，请使用新密码登录')
    router.push('/login')
  } catch (error: any) {
    alert(error.message || '重置失败')
  } finally {
    resetting.value = false
  }
}
</script>

<template>
  <link href="https://fonts.googleapis.com/css?family=Lato:300,400,700&display=swap" rel="stylesheet" />
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
                  <h3 class="mb-4">忘记密码</h3>
                </div>
              </div>

              <!-- 步骤指示器 -->
              <div class="steps d-flex justify-content-around mb-4">
                <span :class="['step', { active: step === 1 }]">1. 验证身份</span>
                <span class="mx-2">→</span>
                <span :class="['step', { active: step === 2 }]">2. 重置密码</span>
              </div>

              <!-- 步骤1：发送验证码 -->
              <form v-if="step === 1" class="signin-form" @submit.prevent="sendCode">
                <div class="form-group mb-3">
                  <label class="label" for="email">用户名</label>
                  <input type="email" class="form-control" placeholder="请输入注册用户名" id="email" v-model="form.username"
                    required />
                </div>
                <div class="form-group mb-3">
                  <label class="label" for="email">邮箱</label>
                  <input type="email" class="form-control" placeholder="请输入注册邮箱" id="email" v-model="form.email"
                    required />
                </div>
                <div class="form-group">
                  <button type="submit" class="form-control btn btn-primary rounded submit px-3" :disabled="sending">
                    {{ sending ? '发送中...' : '发送验证码' }}
                  </button>
                </div>
                <div class="form-group text-center mt-3">
                  <router-link to="/login">返回登录</router-link>
                </div>
              </form>

              <!-- 步骤2：重置密码 -->
              <form v-else class="signin-form" @submit.prevent="resetPassword">
                <div class="form-group mb-3">
                  <label class="label" for="code">验证码</label>
                  <input type="text" class="form-control" placeholder="请输入邮箱收到的验证码" id="code" v-model="resetForm.code"
                    required />
                </div>
                <div class="form-group mb-3">
                  <label class="label" for="newPassword">新密码</label>
                  <div class="position-relative">
                    <input :type="showNewPassword ? 'text' : 'password'" class="form-control" placeholder="至少6位"
                      id="newPassword" v-model="resetForm.newPassword" required minlength="6" />
                    <span class="fa fa-fw" :class="showNewPassword ? 'fa-eye-slash' : 'fa-eye'"
                      @click="showNewPassword = !showNewPassword"
                      style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;"></span>
                  </div>
                </div>
                <div class="form-group mb-3">
                  <label class="label" for="confirmPassword">确认密码</label>
                  <div class="position-relative">
                    <input :type="showConfirmPassword ? 'text' : 'password'" class="form-control" placeholder="再次输入新密码"
                      id="confirmPassword" v-model="resetForm.confirmPassword" required />
                    <span class="fa fa-fw" :class="showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'"
                      @click="showConfirmPassword = !showConfirmPassword"
                      style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;"></span>
                  </div>
                </div>
                <div class="form-group">
                  <button type="submit" class="form-control btn btn-primary rounded submit px-3" :disabled="resetting">
                    {{ resetting ? '提交中...' : '确认重置' }}
                  </button>
                </div>
                <div class="form-group text-center mt-3">
                  <a href="#" @click.prevent="step = 1">重新发送验证码</a>
                  <span class="mx-2">|</span>
                  <router-link to="/login">返回登录</router-link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* 步骤指示器样式 */
.steps {
  font-size: 1rem;
  color: #999;
}

.step.active {
  color: #1089ff;
  font-weight: 600;
}

/* 确保图标字体可用（如果项目未全局引入，可在此补充） */
.fa-eye,
.fa-eye-slash {
  font-family: 'FontAwesome';
}
</style>

<style>
@import '/public/css/style.css';
</style>
