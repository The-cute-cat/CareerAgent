<script setup lang="ts">
import { ElNotification } from 'element-plus'
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { LoginFormDTO } from '@/types/user'
import { userLoginService } from '@/api/user/user'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { ArrowRight, Lock, User, View, Hide } from '@element-plus/icons-vue'

const router = useRouter()
const loginform = reactive<LoginFormDTO>({})
const userStore = useUserStore()
const showPassword = ref(false)
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    const result = await userLoginService(loginform)
    if (result.data.code !== 200) {
      throw new Error(result.data.message || '登录失败')
    }

    userStore.setUserALLInfo(
      result.data.data.accessToken,
      result.data.data.refreshToken,
      result.data.data.userInfo
    )

    router.push('/')
    showSuccessNotification()
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '登录失败'
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour < 12) return '上午好'
  if (hour < 18) return '下午好'
  return '晚上好'
}

const showSuccessNotification = () => {
  ElNotification({
    title: '登录成功',
    message: `${getGreeting()}，欢迎您，${loginform.username}`,
    type: 'success'
  })
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-page__glow auth-page__glow--left"></div>
    <div class="auth-page__glow auth-page__glow--right"></div>

    <div class="auth-shell">
      <aside class="auth-aside">
        <span class="auth-badge">Career Pilot</span>
        <h1>回到你的职业成长空间，继续完成已经开启的规划旅程。</h1>
        <p>登录后可以继续查看职业画像、岗位匹配、发展地图与成长报告，让每一步探索都保持连贯。</p>

        <div class="aside-card">
          <strong>登录后你可以继续</strong>
          <ul>
            <li>完善职业画像与简历信息</li>
            <li>查看岗位匹配与推荐结果</li>
            <li>追踪发展地图与成长报告</li>
          </ul>
        </div>
      </aside>

      <main class="auth-main">
        <div class="auth-panel">
          <div class="panel-header">
            <span class="panel-eyebrow">欢迎回来</span>
            <h2>登录账号</h2>
            <p>输入你的账号信息，继续之前的职业规划进度。</p>
          </div>

          <form class="auth-form" @submit.prevent="handleLogin">
            <label class="field">
              <span class="field-label">用户名</span>
              <div class="field-box">
                <el-icon><User /></el-icon>
                <input v-model="loginform.username" type="text" placeholder="请输入邮箱或用户名" required />
              </div>
            </label>

            <label class="field">
              <span class="field-label">密码</span>
              <div class="field-box">
                <el-icon><Lock /></el-icon>
                <input
                  v-model="loginform.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  required
                />
                <button type="button" class="toggle-btn" @click="showPassword = !showPassword">
                  <el-icon><component :is="showPassword ? Hide : View" /></el-icon>
                </button>
              </div>
            </label>

            <div class="form-row">
              <router-link to="/forgot-password" class="text-link">忘记密码</router-link>
            </div>

            <button type="submit" class="primary-btn" :disabled="loading">
              <span>{{ loading ? '登录中...' : '登录' }}</span>
              <el-icon><ArrowRight /></el-icon>
            </button>
          </form>

          <p class="panel-footer">
            还没有账号？
            <router-link to="/register" class="text-link">立即注册</router-link>
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
  width: min(1180px, 100%);
  display: grid;
  grid-template-columns: minmax(320px, 0.95fr) minmax(420px, 0.85fr);
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
  width: min(460px, 100%);
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
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
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

.toggle-btn {
  border: none;
  background: transparent;
  color: var(--auth-soft);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.form-row {
  display: flex;
  justify-content: flex-end;
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
}
</style>
