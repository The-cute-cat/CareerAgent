<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { LoginFormDTO } from '@/types/user'
import { userSendCodeForgetService, userForgetPasswordService } from '@/api/user/user'
import { ArrowRight, Hide, Key, Lock, Message, View } from '@element-plus/icons-vue'

const router = useRouter()
const step = ref(1)
const form = ref<LoginFormDTO>({})
const sending = ref(false)
const resetting = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const sendCode = async () => {
  sending.value = true
  try {
    const res = await userSendCodeForgetService(form.value)
    if (res.data.code !== 200) {
      throw new Error(res.data.msg || '验证码发送失败')
    }
    ElMessage.success('验证码已发送，请前往邮箱查看')
    step.value = 2
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '发送失败'
    ElMessage.error(errorMessage)
  } finally {
    sending.value = false
  }
}

const resetPassword = async () => {
  if (form.value.password !== form.value.passwordConfirm) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  resetting.value = true
  try {
    const res = await userForgetPasswordService(form.value)
    if (res.data.code !== 200) {
      ElMessage.error(res.data.msg || '重置失败')
      return
    }
    ElMessage.success('密码重置成功，请重新登录')
    router.push('/login')
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '重置失败'
    ElMessage.error(errorMessage)
  } finally {
    resetting.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="app-background">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <div class="auth-shell">
      <aside class="auth-aside">
        <div class="aside-top">
          <span class="auth-badge">账号恢复</span>
          <h1>通过邮箱快速找回账号访问权限，让你的成长进度不中断。</h1>
          <p>只需完成身份验证和新密码设置，就能重新进入个人空间，继续之前的职业规划内容。</p>
        </div>

        <div class="aside-card">
          <strong>找回流程</strong>
          <ol>
            <li>输入注册邮箱并发送验证码</li>
            <li>填写验证码与新密码完成重置</li>
          </ol>
        </div>

        <div class="aside-metrics">
          <div class="metric-item">
            <strong>2 步</strong>
            <span>完成身份验证与密码更新</span>
          </div>
          <div class="metric-item">
            <strong>邮箱验证</strong>
            <span>重置动作更安全更清晰</span>
          </div>
          <div class="metric-item">
            <strong>无缝返回</strong>
            <span>恢复后可继续此前的规划进度</span>
          </div>
        </div>
      </aside>

      <main class="auth-main">
        <div class="auth-panel">
          <div class="panel-header">
            <span class="panel-eyebrow">找回密码</span>
            <h2>{{ step === 1 ? '验证身份' : '设置新密码' }}</h2>
            <p>{{ step === 1 ? '先验证你的邮箱身份，再进入密码重置步骤。' : '验证码校验通过后，设置新的登录密码。' }}</p>
          </div>

          <div class="stepper">
            <div class="step-item" :class="{ active: step === 1, done: step === 2 }">
              <span>1</span>
              <strong>验证邮箱</strong>
            </div>
            <div class="step-line"></div>
            <div class="step-item" :class="{ active: step === 2 }">
              <span>2</span>
              <strong>重置密码</strong>
            </div>
          </div>

          <form v-if="step === 1" class="auth-form" @submit.prevent="sendCode">
            <label class="field">
              <span class="field-label">邮箱</span>
              <div class="field-box">
                <el-icon><Message /></el-icon>
                <input v-model="form.email" type="email" placeholder="请输入注册邮箱" required />
              </div>
            </label>

            <button type="submit" class="primary-btn" :disabled="sending">
              <span>{{ sending ? '发送中...' : '发送验证码' }}</span>
              <el-icon><ArrowRight /></el-icon>
            </button>

            <div class="form-row">
              <router-link to="/login" class="text-link">返回登录</router-link>
            </div>
          </form>

          <form v-else class="auth-form" @submit.prevent="resetPassword">
            <label class="field">
              <span class="field-label">验证码</span>
              <div class="field-box">
                <el-icon><Key /></el-icon>
                <input v-model="form.code" type="text" placeholder="请输入邮箱验证码" required />
              </div>
            </label>

            <label class="field">
              <span class="field-label">新密码</span>
              <div class="field-box">
                <el-icon><Lock /></el-icon>
                <input
                  v-model="form.password"
                  :type="showNewPassword ? 'text' : 'password'"
                  placeholder="请输入新密码"
                  minlength="6"
                  required
                />
                <button type="button" class="toggle-btn" @click="showNewPassword = !showNewPassword">
                  <el-icon><component :is="showNewPassword ? Hide : View" /></el-icon>
                </button>
              </div>
            </label>

            <label class="field">
              <span class="field-label">确认新密码</span>
              <div class="field-box">
                <el-icon><Lock /></el-icon>
                <input
                  v-model="form.passwordConfirm"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="请再次输入新密码"
                  required
                />
                <button type="button" class="toggle-btn" @click="showConfirmPassword = !showConfirmPassword">
                  <el-icon><component :is="showConfirmPassword ? Hide : View" /></el-icon>
                </button>
              </div>
            </label>

            <button type="submit" class="primary-btn" :disabled="resetting">
              <span>{{ resetting ? '提交中...' : '确认重置密码' }}</span>
              <el-icon><ArrowRight /></el-icon>
            </button>

            <div class="form-row form-row--between">
              <button type="button" class="text-btn" @click="step = 1">重新发送验证码</button>
              <router-link to="/login" class="text-link">返回登录</router-link>
            </div>
          </form>
        </div>
      </main>
    </div>
  </section>
</template>

<style scoped>
.auth-page {
  --auth-accent: #409EFF;
  --auth-heading: #2c3e50;
  --auth-soft: #606266;
  --auth-input: #303133;
  --auth-placeholder: #a8abb2;
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  overflow: hidden;
  background-color: transparent;
}

.app-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  background-color: #f3f6f9;
  overflow: hidden;
}

.blob {
  position: absolute;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.6;
  border-radius: 50%;
  animation: float 20s infinite ease-in-out alternate;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: #e0c3fc;
  top: -100px;
  left: -100px;
}

.blob-2 {
  width: 500px;
  height: 500px;
  background: #8ec5fc;
  bottom: -150px;
  right: -100px;
  animation-delay: -5s;
}

.blob-3 {
  width: 300px;
  height: 300px;
  background: #b5c6e0;
  top: 40%;
  left: 30%;
  animation-delay: -10s;
}

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(50px, 30px) scale(1.1); }
  100% { transform: translate(-30px, 60px) scale(0.9); }
}

.auth-shell {
  position: relative;
  z-index: 1;
  width: min(1180px, 100%);
  display: grid;
  grid-template-columns: minmax(340px, 1fr) minmax(440px, 0.9fr);
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 12px 48px rgba(31, 38, 135, 0.08), inset 0 0 0 1px rgba(255, 255, 255, 0.5);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.2));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.auth-aside {
  position: relative;
  overflow: hidden;
  padding: 48px;
  background: linear-gradient(160deg, rgba(240, 245, 255, 0.6), rgba(225, 235, 255, 0.3));
  color: var(--auth-heading);
  display: flex;
  flex-direction: column;
  gap: 28px;
  border-right: 1px solid rgba(255, 255, 255, 0.7);
}

.auth-aside::before {
  content: '';
  position: absolute;
  right: -80px;
  bottom: -80px;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  filter: blur(40px);
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.3), rgba(126, 87, 194, 0.2));
  z-index: 0;
}

.auth-aside::after {
  content: '';
  position: absolute;
  left: -50px;
  top: -50px;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  filter: blur(30px);
  background: linear-gradient(135deg, rgba(255, 186, 115, 0.2), rgba(255, 126, 115, 0.1));
  z-index: 0;
}

.aside-top, .aside-card, .aside-metrics {
  position: relative;
  z-index: 1;
}

.aside-top {
  display: grid;
  gap: 18px;
}

.auth-badge {
  display: inline-flex;
  width: fit-content;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.auth-aside h1 {
  margin: 0;
  font-size: 40px;
  line-height: 1.15;
  color: #2c3e50;
}

.auth-aside p {
  margin: 0;
  color: #606266;
  font-size: 15px;
  line-height: 1.9;
}

.aside-card,
.metric-item {
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.4));
  backdrop-filter: blur(12px);
}

.aside-card {
  padding: 22px;
  border-radius: 22px;
  box-shadow: 0 8px 24px rgba(31, 38, 135, 0.04);
}

.aside-card strong {
  display: block;
  margin-bottom: 12px;
  font-size: 16px;
  color: #2c3e50;
}

.aside-card ol {
  margin: 0;
  padding-left: 18px;
  line-height: 2;
  color: #606266;
}

.aside-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.metric-item {
  padding: 16px 14px;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
}

.metric-item strong {
  display: block;
  margin-bottom: 8px;
  font-size: 20px;
  font-weight: 800;
  color: #409EFF;
}

.metric-item span {
  display: block;
  color: #909399;
  font-size: 12px;
  line-height: 1.6;
}

.auth-main {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 36px;
}

.auth-panel {
  width: min(500px, 100%);
  padding: 32px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(20px);
}

.panel-header {
  margin-bottom: 22px;
}

.panel-eyebrow {
  display: inline-block;
  margin-bottom: 10px;
  color: var(--auth-accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.panel-header h2 {
  margin: 0 0 10px;
  color: var(--auth-heading);
  font-size: 34px;
  line-height: 1.15;
}

.panel-header p {
  margin: 0;
  color: var(--auth-soft);
  line-height: 1.8;
}

.stepper {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--auth-soft);
}

.step-item span {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(148, 163, 184, 0.18);
  font-weight: 700;
}

.step-item.active,
.step-item.done {
  color: var(--auth-heading);
}

.step-item.active span,
.step-item.done span {
  background: linear-gradient(135deg, #409EFF 0%, #3a8ee6 100%);
  color: #fff;
}

.step-line {
  flex: 1;
  height: 1px;
  background: rgba(148, 163, 184, 0.3);
}

.auth-form {
  display: grid;
  gap: 18px;
}

.field {
  display: grid;
  gap: 10px;
}

.field-label {
  color: var(--auth-heading);
  font-size: 14px;
  font-weight: 600;
}

.field-box {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 56px;
  padding: 0 16px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

.field-box:focus-within {
  border-color: #409EFF;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.1);
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.9);
}

.field-box .el-icon {
  color: var(--auth-soft);
  font-size: 18px;
}

.field-box input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  color: var(--auth-input);
  caret-color: var(--auth-input);
  font-size: 15px;
}

.field-box input::placeholder {
  color: var(--auth-placeholder);
}

.toggle-btn,
.text-btn {
  border: none;
  background: transparent;
  cursor: pointer;
}

.toggle-btn {
  color: var(--auth-soft);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.text-btn,
.text-link {
  color: var(--auth-accent);
  text-decoration: none;
  font-weight: 600;
}

.primary-btn {
  min-height: 56px;
  border: none;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, #409EFF 0%, #3a8ee6 100%);
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.4);
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.form-row {
  display: flex;
  justify-content: flex-end;
}

.form-row--between {
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 960px) {
  .auth-shell {
    grid-template-columns: 1fr;
  }

  .auth-aside {
    padding: 32px;
  }

  .auth-aside h1 {
    font-size: 30px;
  }

  .aside-metrics {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .auth-page {
    padding: 14px;
  }

  .auth-main,
  .auth-aside {
    padding: 24px 20px;
  }

  .auth-panel {
    padding: 24px 20px;
    border-radius: 24px;
  }

  .panel-header h2 {
    font-size: 28px;
  }

  .stepper {
    gap: 10px;
  }

  .step-item strong {
    font-size: 13px;
  }
}
</style>
