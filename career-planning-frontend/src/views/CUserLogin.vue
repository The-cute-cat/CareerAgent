<script setup lang="ts">
import { ElNotification, ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
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
    console.log("登录成功", result);

    userStore.setUserALLInfo(
      result.data.data.accessToken,
      result.data.data.refreshToken,
      result.data.data.userInfo
    )

    router.push('/')
    showSuccessNotification()
  } catch (error) {
    console.log(1223, error);

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
    message: `${getGreeting()}，欢迎你，${loginform.username || '用户'}`,
    type: 'success'
  })
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
          <span class="auth-badge">Career Future</span>
          <h2>回到你的职业成长空间，继续完成已经开启的规划旅程。</h2>
          <p>登录后可继续查看职业画像、岗位匹配、发展地图与成长报告，让每一步探索都保持连贯。</p>
        </div>

        <div class="aside-card">
          <strong>登录后你可以继续</strong>
          <ul>
            <li>完善职业画像与简历信息</li>
            <li>查看岗位匹配与推荐结果</li>
            <li>追踪发展地图与成长报告</li>
          </ul>
        </div>

        <div class="aside-metrics">
          <div class="metric-item">
            <strong>24H</strong>
            <span>成长进度随时续接</span>
          </div>
          <div class="metric-item">
            <strong>AI</strong>
            <span>测评与推荐结果同步保留</span>
          </div>
          <div class="metric-item">
            <strong>1v1</strong>
            <span>你的资料与规划记录专属沉淀</span>
          </div>
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
                <el-icon>
                  <User />
                </el-icon>
                <input v-model="loginform.username" type="text" placeholder="请输入邮箱或用户名" required />
              </div>
            </label>

            <label class="field">
              <span class="field-label">密码</span>
              <div class="field-box">
                <el-icon>
                  <Lock />
                </el-icon>
                <input v-model="loginform.password" :type="showPassword ? 'text' : 'password'" placeholder="请输入密码"
                  required />
                <button type="button" class="toggle-btn" @click="showPassword = !showPassword">
                  <el-icon>
                    <component :is="showPassword ? Hide : View" />
                  </el-icon>
                </button>
              </div>
            </label>

            <div class="form-row">
              <router-link to="/forgot-password" class="text-link">忘记密码</router-link>
            </div>

            <button type="submit" class="primary-btn" :disabled="loading">
              <span>{{ loading ? '登录中...' : '登录' }}</span>
              <el-icon>
                <ArrowRight />
              </el-icon>
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
  0% {
    transform: translate(0, 0) scale(1);
  }

  50% {
    transform: translate(50px, 30px) scale(1.1);
  }

  100% {
    transform: translate(-30px, 60px) scale(0.9);
  }
}

.auth-shell {
  position: relative;
  z-index: 1;
  width: min(1180px, 100%);
  display: grid;
  grid-template-columns: minmax(340px, 1fr) minmax(430px, 0.88fr);
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

.aside-top,
.aside-card,
.aside-metrics {
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
  text-transform: uppercase;
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

.aside-card ul {
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
  width: min(468px, 100%);
  padding: 32px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(20px);
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
}
</style>
