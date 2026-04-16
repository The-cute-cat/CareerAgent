<script setup lang="ts">
import { computed, ref } from 'vue'
import type { UploadFile } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Check,
  CircleCloseFilled,
  Close,
  Document,
  Folder,
  MagicStick,
  Operation,
  Picture,
  Timer,
  UploadFilled,
  Warning
} from '@element-plus/icons-vue'

import { uploadProfileFilesApi } from '@/api/career-form/resume'
import { useUserStore } from '@/stores/modules/user'

interface Props {
  showClose?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showClose: false
})

const emit = defineEmits<{
  close: []
  parsed: [data: unknown]
}>()

const userStore = useUserStore()

const MAX_FILE_SIZE = 5 * 1024 * 1024
const MAX_FILE_COUNT = 5
const ALLOWED_TYPES = new Set([
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'image/jpeg',
  'image/jpg',
  'image/png'
])

const uploading = ref(false)
const parsing = ref(false)
const uploadProgress = ref(0)
const uploadSpeed = ref('')
const uploadTimeLeft = ref('')
const selectedFiles = ref<File[]>([])
const uploadRef = ref<any>(null)
const abortController = ref<AbortController | null>(null)
const isDragging = ref(false)
const showFileRequiredTip = ref(false)

const progressColors = [
  { color: '#409eff', percentage: 0 },
  { color: '#67c23a', percentage: 100 }
]

const selectedFileCount = computed(() => selectedFiles.value.length)
const totalFileSize = computed(() => selectedFiles.value.reduce((sum, file) => sum + file.size, 0))

function getFileKey(file: File) {
  return `${file.name}-${file.size}-${file.lastModified}`
}

function formatFileSize(bytes: number) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`
}

function formatSpeed(bytesPerSecond: number) {
  if (bytesPerSecond === 0) return '0 B/s'
  return `${formatFileSize(bytesPerSecond)}/s`
}

function calculateTimeLeft(loaded: number, total: number, speed: number) {
  if (speed === 0) return '计算中...'
  const remaining = total - loaded
  const seconds = Math.ceil(remaining / speed)
  if (seconds < 60) return `${seconds} 秒`
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes} 分 ${secs} 秒`
}

function getFileIcon(file: File) {
  if (file.type.startsWith('image/')) return Picture
  if (file.type.includes('pdf')) return Document
  return Folder
}

function getFileTypeLabel(file: File) {
  if (file.type.includes('pdf')) return 'PDF'
  if (file.type.includes('word') || file.type.includes('document')) return 'Word'
  if (file.type.startsWith('image/')) return '图片'
  return '文件'
}

function validateFile(file: File) {
  if (!ALLOWED_TYPES.has(file.type)) {
    return '不支持的文件格式，请上传 PDF、Word 或 PNG/JPG 图片'
  }

  if (file.size > MAX_FILE_SIZE) {
    return `文件 ${file.name} 超过 5MB 限制`
  }

  if (file.size === 0) {
    return `文件 ${file.name} 内容为空，请重新选择`
  }

  return ''
}

function syncSelectedFiles(fileList: UploadFile[]) {
  const validFiles: File[] = []
  const seen = new Set<string>()

  for (const item of fileList) {
    const raw = item.raw
    if (!raw) continue

    const error = validateFile(raw)
    if (error) {
      ElMessage.error(error)
      continue
    }

    const key = getFileKey(raw)
    if (seen.has(key)) continue
    seen.add(key)
    validFiles.push(raw)

    if (validFiles.length >= MAX_FILE_COUNT) {
      break
    }
  }

  if (fileList.length > MAX_FILE_COUNT || validFiles.length > MAX_FILE_COUNT) {
    ElMessage.warning(`最多上传 ${MAX_FILE_COUNT} 个文件`)
  }

  selectedFiles.value = validFiles.slice(0, MAX_FILE_COUNT)
}

function handleFileChange(_file: UploadFile, fileList: UploadFile[]) {
  if (fileList.length === 0) {
    clearFiles()
    return
  }

  syncSelectedFiles(fileList)
}

function clearFiles() {
  selectedFiles.value = []
  uploadRef.value?.clearFiles()
}

function removeFile(targetFile: File) {
  if (uploading.value || parsing.value) {
    ElMessage.warning('上传进行中，请先取消上传')
    return
  }

  ElMessageBox.confirm(
    `确定要移除资料「${targetFile.name}」吗？`,
    '移除确认',
    {
      confirmButtonText: '确认移除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(() => {
      const targetKey = getFileKey(targetFile)
      selectedFiles.value = selectedFiles.value.filter(file => getFileKey(file) !== targetKey)
      ElMessage.success('资料已移除')
    })
    .catch(() => {
      ElMessage.info('已取消移除')
    })
}

function cancelUpload() {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }

  uploading.value = false
  parsing.value = false
  uploadProgress.value = 0
  uploadSpeed.value = ''
  uploadTimeLeft.value = ''
  ElMessage.info('已取消上传')
}

async function submitUpload() {
  if (!selectedFiles.value.length) {
    showFileRequiredTip.value = true
    ElMessage.warning('请先上传资料文件，再点击开始智能解析')
    setTimeout(() => {
      showFileRequiredTip.value = false
    }, 3000)
    return
  }

  uploading.value = true
  parsing.value = false
  uploadProgress.value = 0
  uploadSpeed.value = ''
  uploadTimeLeft.value = ''
  abortController.value = new AbortController()

  let lastLoaded = 0
  let lastTime = Date.now()

  try {
    const res = await uploadProfileFilesApi({
      files: selectedFiles.value,
      userId: userStore.userInfo?.id?.toString(),
      overwrite: true,
      onProgress: (progressEvent: any) => {
        if (!progressEvent.total) return

        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        uploadProgress.value = Math.min(percent, 99)

        const currentTime = Date.now()
        const timeDiff = (currentTime - lastTime) / 1000
        if (timeDiff > 0.5) {
          const loadedDiff = progressEvent.loaded - lastLoaded
          const speed = loadedDiff / timeDiff
          uploadSpeed.value = formatSpeed(speed)
          uploadTimeLeft.value = calculateTimeLeft(progressEvent.loaded, progressEvent.total, speed)
          lastLoaded = progressEvent.loaded
          lastTime = currentTime
        }

        if (percent >= 99) {
          parsing.value = true
          uploadSpeed.value = ''
          uploadTimeLeft.value = ''
        }
      }
    }, abortController.value.signal)

    if (res.data?.code === 200) {
      ElMessage.success(`资料解析成功，共处理 ${selectedFileCount.value} 个文件`)
      emit('parsed', res.data.data)
      clearFiles()
      if (props.showClose) {
        emit('close')
      }
      return
    }

    const responseData = res?.data
    const errorMsg = responseData?.msg || `请求失败 (code: ${responseData?.code ?? 'unknown'})`
    ElMessage.error(errorMsg)
  } catch (error: any) {
    if (error.name === 'CanceledError' || error.name === 'AbortError' || error.code === 'ERR_CANCELED') {
      return
    }

    if (error.response) {
      const status = error.response.status
      const msg = error.response.data?.msg

      switch (status) {
        case 400:
          ElMessage.error(msg || '请求参数错误，请检查上传文件格式')
          break
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('无权限执行此操作')
          break
        case 413:
          ElMessage.error('文件过大，请上传小于 5MB 的文件')
          break
        case 429:
          ElMessage.error('操作过于频繁，请稍后再试')
          break
        case 500:
          ElMessage.error('服务器繁忙，请稍后重试')
          break
        case 502:
        case 503:
        case 504:
          ElMessage.error('服务暂不可用，请稍后再试')
          break
        default:
          ElMessage.error(msg || `请求失败 (${status})`)
      }
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      ElMessage.error('上传超时，请检查网络后重试')
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络后重试')
    } else {
      ElMessage.error('资料解析失败，请重试')
    }

    console.error('资料上传错误:', error)
  } finally {
    uploading.value = false
    parsing.value = false
    uploadProgress.value = 0
    uploadSpeed.value = ''
    uploadTimeLeft.value = ''
    abortController.value = null
  }
}

function handleDragEnter() {
  isDragging.value = true
}

function handleDragLeave() {
  isDragging.value = false
}

function handleDrop() {
  isDragging.value = false
}
</script>

<template>
  <div class="upload-component-wrapper">
    <el-card class="upload-card" shadow="hover">
      <div class="upload-header">
        <h3>资料上传</h3>
        <el-button
          v-if="showClose"
          link
          type="info"
          :icon="Close"
          circle
          @click="$emit('close')"
        />
      </div>

      <div class="upload-area">
        <div v-if="showFileRequiredTip" class="file-required-tip">
          <el-icon><Warning /></el-icon>
          <span>请先选择或拖拽资料文件到上方区域</span>
        </div>

        <el-upload
          ref="uploadRef"
          drag
          multiple
          :show-file-list="false"
          :auto-upload="false"
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
          class="upload-component"
          :class="{ 'is-dragging': isDragging, 'file-required': showFileRequiredTip }"
          @change="handleFileChange"
          @dragenter="handleDragEnter"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
        >
          <el-icon class="upload-icon" :size="48"><UploadFilled /></el-icon>
          <div class="upload-text">
            <div class="main-text">拖拽文件到此处或<em>点击上传</em></div>
            <div class="sub-text">
              支持 PDF、Word、PNG/JPG 图片，单个文件不超过 5MB，最多 {{ MAX_FILE_COUNT }} 个
            </div>
          </div>
        </el-upload>

        <div v-if="selectedFiles.length" class="summary-card">
          <div class="summary-item">
            <span class="summary-label">已选资料</span>
            <strong>{{ selectedFileCount }} 个文件</strong>
          </div>
          <div class="summary-item">
            <span class="summary-label">总大小</span>
            <strong>{{ formatFileSize(totalFileSize) }}</strong>
          </div>
        </div>

        <div v-if="selectedFiles.length" class="file-list">
          <div v-for="file in selectedFiles" :key="getFileKey(file)" class="file-info-card">
            <div class="file-info-main">
              <el-icon class="file-type-icon" :size="32"><component :is="getFileIcon(file)" /></el-icon>
              <div class="file-info-content">
                <div class="file-name-row">
                  <span class="file-name" :title="file.name">{{ file.name }}</span>
                  <el-tag size="small" type="info" class="file-type-tag">{{ getFileTypeLabel(file) }}</el-tag>
                </div>
                <div class="file-meta">
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  <span v-if="!uploading && !parsing" class="file-status ready">就绪</span>
                  <span v-else-if="uploading" class="file-status uploading">上传中...</span>
                  <span v-else class="file-status parsing">AI 解析中...</span>
                </div>
              </div>
            </div>
            <el-button
              v-if="!uploading && !parsing"
              link
              type="danger"
              :icon="CircleCloseFilled"
              class="remove-btn"
              @click="removeFile(file)"
            >
              移除
            </el-button>
          </div>
        </div>

        <div class="action-buttons">
          <el-button
            type="primary"
            size="large"
            class="upload-btn"
            :class="{ 'no-file': !selectedFiles.length }"
            :loading="uploading || parsing"
            :disabled="uploading || parsing"
            @click="submitUpload"
          >
            <el-icon v-if="!uploading && !parsing" class="btn-icon"><MagicStick /></el-icon>
            {{ uploading ? '文件上传中...' : parsing ? 'AI 解析中...' : '开始智能解析' }}
          </el-button>

          <el-button
            v-if="uploading || parsing"
            size="large"
            class="cancel-btn"
            @click="cancelUpload"
          >
            <el-icon><Close /></el-icon>
            取消
          </el-button>
        </div>

        <div v-if="uploading && !parsing" class="progress-section">
          <div class="progress-header">
            <span>上传进度</span>
            <span class="progress-percent">{{ uploadProgress }}%</span>
          </div>
          <el-progress
            :percentage="uploadProgress"
            :stroke-width="20"
            :color="progressColors"
            striped
            striped-flow
          />
          <div class="progress-stats">
            <el-text v-if="uploadSpeed" type="info" size="small">速度: {{ uploadSpeed }}</el-text>
            <el-text v-if="uploadTimeLeft" type="info" size="small">预计剩余: {{ uploadTimeLeft }}</el-text>
          </div>
        </div>

        <div v-if="parsing" class="progress-section">
          <div class="progress-header">
            <span>AI 解析进度</span>
            <span class="progress-percent parsing-text">解析中...</span>
          </div>
          <el-progress
            :percentage="100"
            :stroke-width="20"
            status="success"
            :indeterminate="true"
            :duration="2"
          />
          <div class="progress-tips parsing-tips">
            <el-icon class="parsing-icon"><Timer /></el-icon>
            <span>AI 正在综合分析您上传的资料，请稍候...</span>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="feature-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Operation /></el-icon>
          <span>AI 解析能力</span>
        </div>
      </template>

      <div class="feature-list">
        <div class="feature-item">
          <el-icon class="feature-icon" color="#67C23A"><Check /></el-icon>
          <div class="feature-content">
            <div class="feature-title">多资料联合识别</div>
            <div class="feature-desc">支持简历、证书、项目材料等资料一起上传，补足画像信息</div>
          </div>
        </div>

        <div class="feature-item">
          <el-icon class="feature-icon" color="#409EFF"><Check /></el-icon>
          <div class="feature-content">
            <div class="feature-title">经历信息提取</div>
            <div class="feature-desc">自动识别项目、实习、技能和工具等关键经历内容</div>
          </div>
        </div>

        <div class="feature-item">
          <el-icon class="feature-icon" color="#E6A23C"><Check /></el-icon>
          <div class="feature-content">
            <div class="feature-title">多文件结果合并</div>
            <div class="feature-desc">整合多份资料中的有效字段，尽量减少重复填写</div>
          </div>
        </div>

        <div class="feature-item">
          <el-icon class="feature-icon" color="#F56C6C"><Check /></el-icon>
          <div class="feature-content">
            <div class="feature-title">能力画像补全</div>
            <div class="feature-desc">结合已识别内容生成更完整的职业能力画像</div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.upload-component-wrapper {
  width: 100%;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.upload-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.upload-card,
.feature-card {
  border-radius: 12px;
}

.upload-card {
  margin-bottom: 16px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.file-required-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 12px 20px;
  background: linear-gradient(135deg, #fdf6ec 0%, #fef9f0 100%);
  border: 1px solid #f5dab1;
  border-radius: 10px;
  color: #e6a23c;
  font-size: 14px;
  font-weight: 500;
  animation: slideDown 0.3s ease;
}

.file-required-tip .el-icon {
  font-size: 18px;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.upload-component {
  width: 100%;
}

.upload-component.file-required :deep(.el-upload-dragger) {
  border-color: #e6a23c;
  background-color: #fdf6ec;
}

:deep(.el-upload-dragger) {
  width: 100%;
  padding: 24px;
  border: 2px dashed #dcdfe6;
  transition: all 0.3s ease;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background-color: #f5f9ff;
}

.upload-component.is-dragging :deep(.el-upload-dragger) {
  border-color: #409eff;
  background-color: #ecf5ff;
  border-style: solid;
}

.upload-icon {
  color: #409eff;
  margin-bottom: 12px;
}

.upload-text {
  text-align: center;
}

.upload-text .main-text {
  margin-bottom: 6px;
  font-size: 14px;
  color: #606266;
}

.upload-text .main-text em {
  color: #409eff;
  font-style: normal;
  font-weight: 600;
}

.upload-text .sub-text {
  font-size: 13px;
  color: #909399;
}

.summary-card,
.file-list,
.progress-section {
  width: 100%;
}

.summary-card {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.summary-item {
  padding: 14px 16px;
  border: 1px solid #e8eef5;
  border-radius: 12px;
  background: linear-gradient(135deg, #f6f9fe 0%, #ffffff 100%);
}

.summary-label {
  display: block;
  margin-bottom: 6px;
  color: #909399;
  font-size: 12px;
}

.summary-item strong {
  color: #303133;
  font-size: 15px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-info-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: linear-gradient(135deg, #f5f9ff 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.06);
}

.file-info-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.file-type-icon {
  color: #409eff;
  flex-shrink: 0;
}

.file-info-content {
  flex: 1;
  min-width: 0;
}

.file-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.file-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.file-size {
  color: #909399;
}

.file-status {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
}

.file-status.ready {
  color: #67c23a;
  background: #f0f9eb;
}

.file-status.uploading {
  color: #409eff;
  background: #ecf5ff;
}

.file-status.parsing {
  color: #e6a23c;
  background: #fdf6ec;
}

.remove-btn {
  margin-left: 12px;
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  width: 100%;
}

.upload-btn {
  width: 100%;
  max-width: 220px;
  height: 42px;
  font-size: 15px;
  border-radius: 8px;
}

.upload-btn:disabled {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
  color: #c0c4cc;
}

.upload-btn.no-file {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
  color: #c0c4cc;
}

.cancel-btn {
  width: 100px;
  height: 42px;
  border-radius: 8px;
}

.btn-icon {
  margin-right: 6px;
}

.progress-section {
  max-width: 500px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.progress-percent {
  color: #409eff;
  font-weight: 600;
}

.progress-percent.parsing-text {
  color: #67c23a;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
}

.parsing-tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
  color: #67c23a;
  font-size: 13px;
}

.parsing-icon {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
  font-size: 15px;
  font-weight: 600;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.feature-icon {
  margin-top: 2px;
  font-size: 18px;
}

.feature-content {
  flex: 1;
}

.feature-title {
  margin-bottom: 2px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.feature-desc {
  color: #909399;
  font-size: 13px;
}

@media (max-width: 768px) {
  .summary-card {
    grid-template-columns: 1fr;
  }

  .file-info-card,
  .action-buttons,
  .progress-stats {
    flex-direction: column;
    align-items: stretch;
  }

  .remove-btn,
  .upload-btn,
  .cancel-btn {
    width: 100%;
    max-width: none;
    margin-left: 0;
  }
}
</style>
