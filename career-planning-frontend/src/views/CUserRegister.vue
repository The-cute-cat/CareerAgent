<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { LoginFormDTO } from '@/types/user'
import { userRegisterService, userSendCodeRegisterService } from '@/api/user/user'
import { useUserStore } from '@/stores'
import { ArrowRight, Hide, Lock, Message, User, View, Key, Ticket } from '@element-plus/icons-vue'

const form = ref<LoginFormDTO>({})
const router = useRouter()
const userStore = useUserStore()
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const codeSending = ref(false)
const codeCountdown = ref(0)
let countdownTimer: number | null = null

const sendVerificationCode = async () => {
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
    const res = await userSendCodeRegisterService(form.value)
    if (res.data.code !== 200) {
      ElMessage.error(res.data.msg || '验证码发送失败')
      return
    }
    ElMessage.success(`验证码已发送至 ${form.value.email}，请查收`)
    codeCountdown.value = 60
    if (countdownTimer) clearInterval(countdownTimer)
    countdownTimer = window.setInterval(() => {
      if (codeCountdown.value > 0) {
        codeCountdown.value--
      } else {
        clearInterval(countdownTimer!)
        countdownTimer = null
      }
    }, 1000)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '验证码发送失败，请重试'
    ElMessage.error(errorMessage)
  } finally {
    codeSending.value = false
  }
}

const handleRegister = async () => {
  if (form.value.password !== form.value.passwordConfirm) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  if (!form.value.code) {
    ElMessage.warning('请输入验证码')
    return
  }

  loading.value = true
  try {
    const res = await userRegisterService(form.value)
    if (res.data.code !== 200) {
      ElMessage.error(res.data.msg || '注册失败')
      return
    }
    userStore.clearUserALLInfo()
    ElMessage.success('注册成功，请登录')
    await new Promise((resolve) => setTimeout(resolve, 1000))
    router.push('/login')
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '注册失败'
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
})
</script>

<template>
  <section class="auth-page">
    <div class="auth-page__glow auth-page__glow--left"></div>
    <div class="auth-page__glow auth-page__glow--right"></div>

    <div class="auth-shell">
      <aside class="auth-aside">
        <span class="auth-badge">新用户加入</span>
        <h1>创建账号后，把职业探索、成长记录和报告内容统一沉淀下来。</h1>
        <p>注册完成后即可开启个人成长档案，持续积累画像、任务轨迹和职业规划结果。</p>

        <div class="aside-card">
          <strong>注册后你可以获得</strong>
          <ul>
            <li>专属账号与职业成长档案</li>
            <li>岗位推荐与能力分析记录</li>
            <li>持续查看报告与发展路径</li>
          </ul>
        </div>
      </aside>

      <main class="auth-main">
        <div class="auth-panel">
          <div class="panel-header">
            <span class="panel-eyebrow">创建账号</span>
            <h2>注册 Career Pilot</h2>
            <p>填写基础账号信息，完成邮箱验证后即可开始使用。</p>
          </div>

          <form class="auth-form" @submit.prevent="handleRegister">
            <label class="field">
              <span class="field-label">昵称</span>
              <div class="field-box">
                <el-icon><User /></el-icon>
                <input v-model="form.username" type="text" placeholder="请输入昵称" required />
              </div>
            </label>

            <label class="field">
              <span class="field-label">邮箱</span>
              <div class="field-box">
                <el-icon><Message /></el-icon>
                <input v-model="form.email" type="email" placeholder="请输入邮箱地址" required />
              </div>
            </label>

            <label class="field">
              <span class="field-label">密码</span>
              <div class="field-box">
                <el-icon><Lock /></el-icon>
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  required
                />
                <button type="button" class="toggle-btn" @click="showPassword = !showPassword">
                  <el-icon><component :is="showPassword ? Hide : View" /></el-icon>
                </button>
              </div>
            </label>

            <label class="field">
              <span class="field-label">确认密码</span>
              <div class="field-box">
                <el-icon><Lock /></el-icon>
                <input
                  v-model="form.passwordConfirm"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="请再次输入密码"
                  required
                />
                <button type="button" class="toggle-btn" @click="showConfirmPassword = !showConfirmPassword">
                  <el-icon><component :is="showConfirmPassword ? Hide : View" /></el-icon>
                </button>
              </div>
            </label>

            <label class="field">
              <span class="field-label">验证码</span>
              <div class="field-box field-box--with-action">
                <div class="field-box__input">
                  <el-icon><Key /></el-icon>
                  <input v-model="form.code" type="text" placeholder="请输入邮箱验证码" required />
                </div>
                <button
                  type="button"
                  class="secondary-btn"
                  @click="sendVerificationCode"
                  :disabled="codeSending || codeCountdown > 0"
                >
                  <span v-if="codeSending">发送中...</span>
                  <span v-else-if="codeCountdown > 0">{{ codeCountdown }}s</span>
                  <span v-else>发送验证码</span>
                </button>
              </div>
            </label>

            <label class="field">
              <span class="field-label">邀请码</span>
              <div class="field-box">
                <el-icon><Ticket /></el-icon>
                <input
                  v-model="form.inviteCode"
                  type="text"
                  placeholder="请输入邀请码（选填）"
                />
              </div>
            </label>

            <button type="submit" class="primary-btn" :disabled="loading">
              <span>{{ loading ? '注册中...' : '注册并开始使用' }}</span>
              <el-icon><ArrowRight /></el-icon>
            </button>
          </form>

          <p class="panel-footer">
            已有账号？
            <router-link to="/login" class="text-link">去登录</router-link>
          </p>
        </div>
      </main>
    </div>
  </section>
</template>

<style scoped>
.auth-page {
  --auth-accent: #1668dc;
  --auth-heading: #163253;
  --auth-soft: #6d84a0;
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
    radial-gradient(circle at top left, rgba(97, 154, 255, 0.22), transparent 24%),
    radial-gradient(circle at bottom right, rgba(103, 184, 255, 0.18), transparent 24%),
    linear-gradient(180deg, #f4f8ff 0%, #eef4fb 52%, #f8fbff 100%);
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
  background: rgba(22, 119, 255, 0.18);
}

.auth-page__glow--right {
  width: 360px;
  height: 360px;
  right: -100px;
  bottom: 40px;
  background: rgba(103, 184, 255, 0.16);
}

.auth-shell {
  position: relative;
  z-index: 1;
  width: min(1220px, 100%);
  display: grid;
  grid-template-columns: minmax(320px, 0.95fr) minmax(460px, 0.9fr);
  border-radius: 32px;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.14);
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(24px);
}

.auth-aside {
  padding: 48px;
  background: linear-gradient(160deg, rgba(23, 58, 93, 0.96), rgba(22, 119, 255, 0.82));
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
  color: rgba(241, 245, 249, 0.84);
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

.aside-card ul {
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
  margin-bottom: 28px;
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

.field-box--with-action {
  justify-content: space-between;
  padding-right: 8px;
}

.field-box__input {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.toggle-btn,
.secondary-btn {
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

.secondary-btn {
  min-width: 112px;
  height: 42px;
  padding: 0 14px;
  border-radius: 14px;
  background: rgba(22, 119, 255, 0.1);
  color: var(--auth-accent);
  font-weight: 700;
}

.secondary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

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
  background: linear-gradient(135deg, #1677ff 0%, #67b8ff 100%);
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 18px 30px rgba(22, 119, 255, 0.22);
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.panel-footer {
  margin: 22px 0 0;
  color: var(--auth-soft);
  text-align: center;
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

  .field-box--with-action {
    flex-direction: column;
    align-items: stretch;
    padding: 10px;
  }

  .secondary-btn {
    width: 100%;
  }
}
</style>
