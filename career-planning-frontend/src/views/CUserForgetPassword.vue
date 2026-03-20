<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { LoginFormDTO } from '@/types/user'
import { userSendCodeForgetService, userForgetPasswordService } from '@/api/user/user'
const router = useRouter()

// 步骤控制
const step = ref(1)

// 发送验证码表单
const form = ref<LoginFormDTO>({})

const sending = ref(false)

const resetting = ref(false)



// 密码可见性
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)



// 发送验证码
const sendCode = async () => {
  sending.value = true
  try {
    const res = await userSendCodeForgetService(form.value)
    console.log('发送验证码结果:', res)
    if (res.data.code !== 200) {
      throw new Error(res.data.msg || '验证码发送失败')
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
  if (form.value.password !== form.value.passwordConfirm) {
    alert('两次输入的密码不一致')
    return
  }
  resetting.value = true
  try {
    const res = await userForgetPasswordService(form.value)
    console.log('重置密码结果:', res)
    if (res.data.code !== 200) {
      ElMessage.error(res.data.msg || '重置失败')
    }
    router.push('/login')
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '重置失败'
    ElMessage.error(errorMessage)
    console.log("重置失败", error);
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
                  <label class="label" for="email">邮箱</label>
                  <input
                    type="email"
                    class="form-control"
                    placeholder="请输入注册邮箱"
                    id="email"
                    v-model="form.email"
                    required
                  />
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
                  <input
                    type="text"
                    class="form-control"
                    placeholder="请输入邮箱收到的验证码"
                    id="code"
                    v-model="form.code"
                    required
                  />
                </div>
                <div class="form-group mb-3">
                  <label class="label" for="newPassword">新密码</label>
                  <div class="position-relative">
                    <input
                      :type="showNewPassword ? 'text' : 'password'"
                      class="form-control"
                      placeholder="至少6位"
                      id="newPassword"
                      v-model="form.password"
                      required
                      minlength="6"
                    />
                    <span
                      class="fa fa-fw"
                      :class="showNewPassword ? 'fa-eye-slash' : 'fa-eye'"
                      @click="showNewPassword = !showNewPassword"
                      style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;"
                    ></span>
                  </div>
                </div>
                <div class="form-group mb-3">
                  <label class="label" for="confirmPassword">确认密码</label>
                  <div class="position-relative">
                    <input
                      :type="showConfirmPassword ? 'text' : 'password'"
                      class="form-control"
                      placeholder="再次输入新密码"
                      id="confirmPassword"
                      v-model="form.passwordConfirm"
                      required
                    />
                    <span
                      class="fa fa-fw"
                      :class="showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'"
                      @click="showConfirmPassword = !showConfirmPassword"
                      style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;"
                    ></span>
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

/* 步骤指示器增大 */
.steps {
  font-size: 15px;
  padding: 15px 0;
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