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
    <div class="auth-page__glow auth-page__glow--left"></div>
    <div class="auth-page__glow auth-page__glow--right"></div>

    <div class="auth-shell">
      <aside class="auth-aside">
        <span class="auth-badge">账号恢复</span>
        <h1>两步完成密码找回，尽量减少用户中断感。</h1>
        <p>保留原本的邮箱验证码与密码重置流程，只对步骤展示和表单组织方式进行了现代化重构。</p>

        <div class="aside-card">
          <strong>找回流程</strong>
          <ol>
            <li>输入注册邮箱并发送验证码</li>
            <li>填写验证码与新密码完成重置</li>
          </ol>
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
  --auth-accent: #0f766e;
  --auth-heading: #0f172a;
  --auth-soft: #64748b;
  --auth-input: #111827;
  --auth-placeholder: #94a3b8;
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(15, 118, 110, 0.18), transparent 24%),
    radial-gradient(circle at bottom right, rgba(249, 115, 22, 0.14), transparent 24%),
    linear-gradient(180deg, #f4f7f4 0%, #f8f4ee 100%);
}

.auth-page__glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(64px);
  pointer-events: none;
}

.auth-page__glow--left {
  width: 320px;
  height: 320px;
  left: -100px;
  top: 80px;
  background: rgba(20, 184, 166, 0.18);
}

.auth-page__glow--right {
  width: 360px;
  height: 360px;
  right: -100px;
  bottom: 40px;
  background: rgba(251, 146, 60, 0.14);
}

.auth-shell {
  position: relative;
  z-index: 1;
  width: min(1180px, 100%);
  display: grid;
  grid-template-columns: minmax(320px, 0.95fr) minmax(440px, 0.85fr);
  border-radius: 32px;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.14);
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(24px);
}

.auth-aside {
  padding: 48px;
  background: linear-gradient(160deg, rgba(18, 42, 39, 0.96), rgba(15, 118, 110, 0.88));
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 28px;
}

.auth-badge {
  display: inline-flex;
  width: fit-content;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.auth-aside h1 {
  font-size: 40px;
  line-height: 1.15;
  margin: 0;
}

.auth-aside p {
  margin: 0;
  color: rgba(241, 245, 249, 0.82);
  font-size: 15px;
  line-height: 1.9;
}

.aside-card {
  padding: 22px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.aside-card strong {
  display: block;
  margin-bottom: 12px;
  font-size: 16px;
}

.aside-card ol {
  margin: 0;
  padding-left: 18px;
  line-height: 2;
  color: rgba(241, 245, 249, 0.88);
}

.auth-main {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 36px;
}

.auth-panel {
  width: min(500px, 100%);
  padding: 12px 6px;
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
  width: 30px;
  height: 30px;
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
  background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
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
  border-radius: 18px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: rgba(255, 255, 255, 0.86);
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
  border-radius: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 18px 30px rgba(15, 118, 110, 0.22);
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
}

@media (max-width: 640px) {
  .auth-page {
    padding: 14px;
  }

  .auth-main,
  .auth-aside {
    padding: 24px 20px;
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
