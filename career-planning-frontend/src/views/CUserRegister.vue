<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { LoginFormDTO } from '@/types/user'
import { userRegisterService, userSendCodeRegisterService } from '@/api/user/user'
import { useUserStore } from '@/stores'
import { ArrowRight, Hide, Lock, Message, User, View, Key, Ticket } from '@element-plus/icons-vue'
import { mockRechargePointsApi } from '@/mock/mockdata/Points_mockdata'

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
    const errorMessage = error instanceof Error ? error.message : '验证码发送失败，请稍后重试'
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
    
    // 获取新注册用户ID
    const newUserId = res.data.data?.id || res.data.data?.userId || Date.now()
    
    // 为新用户赠送500积分（模拟）
    await mockRechargePointsApi(newUserId, 500, '新用户注册奖励')
    
    userStore.clearUserALLInfo()
    
    // 设置标志，登录后显示欢迎弹窗
    localStorage.setItem('showWelcomeGift', 'true')
    localStorage.setItem('welcomeGiftPoints', '500')
    
    ElMessage.success('注册成功！已赠送 500 新人积分')
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
    <div class="app-background">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <div class="auth-shell">
      <aside class="auth-aside">
        <div class="aside-top">
          <span class="auth-badge">新用户加入</span>
          <h1>创建账号后，把职业探索、成长记录和报告内容统一沉淀下来。</h1>
          <p>注册完成后即可开启个人成长档案，持续积累画像、任务轨迹和职业规划结果。</p>
        </div>

        <div class="aside-card">
          <span class="aside-card__tag">注册权益</span>
          <strong>注册后你可以获得</strong>
          <ul>
            <li>专属账号与职业成长档案</li>
            <li>岗位推荐与能力分析记录</li>
            <li>持续查看报告与发展路径</li>
          </ul>
        </div>

        <div class="aside-metrics">
          <div class="metric-item">
            <strong>+500</strong>
            <span>注册成功即送新人积分</span>
          </div>
          <div class="metric-item">
            <strong>成长档案</strong>
            <span>资料、报告与路径统一管理</span>
          </div>
          <div class="metric-item">
            <strong>邀请码</strong>
            <span>可填可不填，后续便于邀请协同</span>
          </div>
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
              <span class="field-label">用户名</span>
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
  padding: 18px;
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
  width: min(1080px, 100%);
  display: grid;
  grid-template-columns: minmax(300px, 0.82fr) minmax(430px, 0.9fr);
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
  padding: 34px 32px;
  background: linear-gradient(160deg, rgba(240, 245, 255, 0.6), rgba(225, 235, 255, 0.3));
  color: var(--auth-heading);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 22px;
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
  gap: 12px;
  max-width: 420px;
}

.auth-badge {
  display: inline-flex;
  width: fit-content;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.auth-aside h1 {
  margin: 0;
  max-width: 14ch;
  font-size: clamp(26px, 3vw, 40px);
  line-height: 1.24;
  letter-spacing: -0.02em;
  text-wrap: balance;
  color: #2c3e50;
}

.auth-aside p {
  margin: 0;
  max-width: 420px;
  color: #606266;
  font-size: 14px;
  line-height: 1.7;
}

.aside-card,
.metric-item {
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.4));
  backdrop-filter: blur(12px);
}

.aside-card {
  max-width: 420px;
  padding: 16px 18px;
  border-radius: 18px;
  box-shadow: 0 8px 24px rgba(31, 38, 135, 0.04);
}

.aside-card__tag {
  display: inline-flex;
  margin-bottom: 8px;
  padding: 4px 9px;
  border-radius: 999px;
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
  font-size: 11px;
  font-weight: 700;
}

.aside-card strong {
  display: block;
  margin-bottom: 8px;
  font-size: 16px;
  color: #2c3e50;
}

.aside-card ul {
  margin: 0;
  padding-left: 18px;
  line-height: 1.75;
  font-size: 14px;
  color: #606266;
}

.aside-metrics {
  display: grid;
  max-width: 420px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.metric-item {
  min-height: 96px;
  padding: 14px;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
}

.metric-item strong {
  display: block;
  margin-bottom: 6px;
  font-size: 18px;
  font-weight: 800;
  color: #409EFF;
}

.metric-item span {
  display: block;
  color: #909399;
  font-size: 12px;
  line-height: 1.55;
}

.auth-main {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28px;
}

.auth-panel {
  width: min(460px, 100%);
  padding: 24px;
  border-radius: 20px;
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
  margin-bottom: 8px;
  color: var(--auth-accent);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.panel-header h2 {
  margin: 0 0 8px;
  color: var(--auth-heading);
  font-size: 30px;
  line-height: 1.18;
}

.panel-header p {
  margin: 0;
  color: var(--auth-soft);
  font-size: 14px;
  line-height: 1.7;
}

.auth-form {
  display: grid;
  gap: 16px;
}

.field {
  display: grid;
  gap: 8px;
}

.field-label {
  color: var(--auth-heading);
  font-size: 13px;
  font-weight: 600;
}

.field-box {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 50px;
  padding: 0 14px;
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
  font-size: 17px;
}

.field-box input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  color: var(--auth-input);
  caret-color: var(--auth-input);
  font-size: 14px;
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
  min-width: 108px;
  height: 38px;
  padding: 0 12px;
  border-radius: 12px;
  background: rgba(64, 158, 255, 0.1);
  color: var(--auth-accent);
  font-weight: 700;
  transition: all 0.3s ease;
}

.secondary-btn:hover:not(:disabled) {
  background: rgba(64, 158, 255, 0.2);
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
  min-height: 50px;
  border: none;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, #409EFF 0%, #3a8ee6 100%);
  color: #ffffff;
  font-size: 14px;
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
  margin: 18px 0 0;
  color: var(--auth-soft);
  text-align: center;
  font-size: 14px;
}

@media (max-width: 960px) {
  .auth-shell {
    grid-template-columns: 1fr;
  }

  .auth-aside {
    padding: 28px;
  }

  .auth-aside h1 {
    max-width: none;
    font-size: 28px;
  }

  .aside-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .auth-page {
    padding: 12px;
  }

  .auth-main,
  .auth-aside {
    padding: 22px 18px;
  }

  .auth-panel {
    padding: 20px 18px;
    border-radius: 20px;
  }

  .panel-header h2 {
    font-size: 26px;
  }

  .aside-metrics {
    grid-template-columns: 1fr;
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
