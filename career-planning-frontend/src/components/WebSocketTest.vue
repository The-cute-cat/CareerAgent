<template>
  <div class="ws-test">
    <h2>🔧 WebSocket 连接诊断工具</h2>
    
    <div class="actions">
      <el-button type="primary" @click="runTests" :loading="isRunning" :disabled="isRunning">
        {{ isRunning ? '测试中...' : '开始诊断' }}
      </el-button>
      <el-button type="warning" @click="runSignatureTests" :loading="isRunningSignature" :disabled="isRunning || isRunningSignature">
        测试签名格式
      </el-button>
      <el-button @click="clearResults">清除结果</el-button>
    </div>

    <div class="results" v-if="results.length > 0">
      <div 
        v-for="(result, index) in results" 
        :key="index"
        class="result-item"
        :class="result.status"
      >
        <div class="result-header">
          <span class="icon">{{ result.status === 'success' ? '✅' : result.status === 'error' ? '❌' : '⏳' }}</span>
          <span class="test-name">{{ result.test }}</span>
          <el-tag :type="result.status === 'success' ? 'success' : result.status === 'error' ? 'danger' : 'info'" size="small">
            {{ result.status === 'success' ? '通过' : result.status === 'error' ? '失败' : '进行中' }}
          </el-tag>
        </div>
        <div class="result-message">{{ result.message }}</div>
        <pre v-if="result.details" class="result-details">{{ formatDetails(result.details) }}</pre>
      </div>
    </div>

    <div class="suggestions" v-if="showSuggestions">
      <h3>💡 问题诊断与建议</h3>
      <div class="suggestion-content" v-html="suggestions"></div>
    </div>

    <div class="quick-test">
      <h3>🚀 问题诊断与修复</h3>
      <el-alert type="warning" :closable="false" style="margin-bottom: 15px;">
        <p><strong>当前状态：手机热点 + 基础连接失败</strong></p>
        <p>这说明问题不是网络阻止，而是：</p>
        <ol>
          <li><strong>签名算法不正确</strong> - 点击"测试签名格式"按钮，测试哪种签名格式正确</li>
          <li><strong>API Secret 格式错误</strong> - 请确认讯飞控制台给出的 APISecret 是原始值还是已编码</li>
          <li><strong>账号未开通服务</strong> - 确认已在讯飞控制台开通"虚拟人"服务</li>
        </ol>
      </el-alert>
      
      <el-alert type="info" :closable="false">
        <p><strong>如何确认 API Secret 格式：</strong></p>
        <ol>
          <li>登录讯飞开放平台控制台</li>
          <li>找到虚拟人服务，查看 API 密钥</li>
          <li>APISecret 通常是 32 位随机字符串，如：d180d9f81c3af0b83e39bfd6a7c8e9f2</li>
          <li>如果看到的就是这种格式 → API_SECRET_ENCODING: 'plain'</li>
          <li>如果看到的是 Base64 编码 → API_SECRET_ENCODING: 'base64'</li>
        </ol>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  runAllDiagnostics, 
  testSignatureFormat,
  WebSocketTestResult 
} from '@/composables/use-virtual-human'

const isRunning = ref(false)
const isRunningSignature = ref(false)
const results = ref<WebSocketTestResult[]>([])

const showSuggestions = computed(() => results.value.some(r => r.status === 'error'))

const suggestions = computed(() => {
  const basicTest = results.value.find(r => r.test === '基础 WebSocket 连接测试')
  const authTest = results.value.find(r => r.test === '带鉴权 WebSocket 连接测试')
  const secretTest = results.value.find(r => r.test === 'API Secret 配置检查')
  const signatureTests = results.value.filter(r => r.test.includes('签名格式'))
  
  // 如果有签名格式测试通过
  const passedSignature = signatureTests.find(r => r.status === 'success')
  if (passedSignature) {
    return `
      <p><strong>✅ 找到正确的签名格式！</strong></p>
      <p>${passedSignature.test} 连接成功。</p>
      <p>请修改 use-virtual-human.ts 中的 generateSignedUrl 函数，使用此格式。</p>
    `
  }
  
  // 基础连接失败（即使是手机热点）
  if (basicTest?.status === 'error') {
    return `
      <p><strong>⚠️ 网络层连接失败（手机热点也失败）</strong></p>
      <p>这说明不是网络阻止问题，可能原因：</p>
      <ul>
        <li><strong>讯飞的 WebSocket 服务需要正确的鉴权参数才能建立连接</strong> - 尝试点击"测试签名格式"</li>
        <li>浏览器或系统层面的安全设置阻止了连接</li>
        <li>讯飞服务端针对此 AppID 有特殊限制</li>
      </ul>
      <p style="margin-top:10px"><strong>下一步：</strong>点击"测试签名格式"按钮，测试哪种签名算法是正确的。</p>
    `
  }
  
  if (basicTest?.status === 'success' && authTest?.status === 'error') {
    return `
      <p><strong>鉴权失败</strong> - 网络正常，但参数有问题：</p>
      <ul>
        <li>${secretTest?.details?.suggestion || ''}</li>
        <li>检查 APP_ID、API_KEY、SCENE_ID 是否与讯飞控制台一致</li>
        <li>API Secret 可能需要用原始值（而非 Base64）</li>
        <li>尝试修改 API_SECRET_ENCODING 为 "plain"</li>
        <li>检查系统时间是否与北京时间同步（误差需在 5 分钟内）</li>
      </ul>
    `
  }
  
  if (results.value.every(r => r.status === 'success')) {
    return `<p><strong>✅ 所有测试通过！</strong> 如果 SDK 仍然连接失败，可能是 SDK 版本或初始化参数问题。</p>`
  }
  
  return '<p>请运行测试获取诊断信息</p>'
})

const formatDetails = (details: any): string => {
  if (typeof details === 'string') return details
  return JSON.stringify(details, null, 2)
}

const runTests = async () => {
  isRunning.value = true
  results.value = []
  
  await runAllDiagnostics((result) => {
    results.value.push(result)
  })
  
  isRunning.value = false
}

const runSignatureTests = async () => {
  isRunningSignature.value = true
  
  const signatureResults = await testSignatureFormat()
  results.value.push(...signatureResults)
  
  isRunningSignature.value = false
}

const clearResults = () => {
  results.value = []
}

// 自动运行一次测试
// runTests()
</script>

<style scoped>
.ws-test {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 20px;
}

.actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.results {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.result-item {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 15px;
  background: #fff;
}

.result-item.success {
  border-left: 4px solid #67c23a;
}

.result-item.error {
  border-left: 4px solid #f56c6c;
}

.result-item.pending {
  border-left: 4px solid #909399;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.icon {
  font-size: 18px;
}

.test-name {
  font-weight: 600;
  flex: 1;
}

.result-message {
  color: #606266;
  margin-bottom: 8px;
}

.result-details {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  margin: 0;
}

.suggestions {
  background: #fdf6ec;
  border: 1px solid #f5dab1;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.suggestions h3 {
  margin-top: 0;
  color: #e6a23c;
}

.suggestion-content :deep(ul), .suggestion-content :deep(ol) {
  padding-left: 20px;
}

.suggestion-content :deep(li) {
  margin: 8px 0;
}

.quick-test {
  margin-top: 20px;
}

.quick-test h3 {
  margin-bottom: 15px;
}
</style>
