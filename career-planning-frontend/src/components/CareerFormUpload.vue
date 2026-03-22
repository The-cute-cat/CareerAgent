<script setup lang="ts">
//简历上传，作为能力画像的功能3\组件

import { ref, computed } from 'vue'
import { UploadFilled, Document, MagicStick, Timer, Operation, Check, Close, CircleCloseFilled, Picture, Folder } from '@element-plus/icons-vue'
import { uploadResumeApi } from '@/api/career-form/resume'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/modules/user'
import type { UploadFile } from 'element-plus'


// 定义组件接收的 props
interface Props {
  showClose?: boolean
}


const props = withDefaults(defineProps<Props>(), {
  showClose: false
})

// 定义组件触发的事件
const emit = defineEmits<{ close: [], parsed: [data: any] }>()

const userStore = useUserStore()
const uploading = ref(false)
const parsing = ref(false)
const uploadProgress = ref(0)
const uploadSpeed = ref('') // 上传速度
const uploadTimeLeft = ref('') // 预计剩余时间
const selectedFile = ref<File | null>(null)

// 进度条颜色配置
const progressColors = [
  { color: '#409eff', percentage: 0 },
  { color: '#67c23a', percentage: 100 }
]

const handleFileChange = (file: UploadFile) => {
  selectedFile.value = file.raw || null
}

const beforeUpload = (file: File) => {
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('文件大小不能超过 5MB!')
    return false
  }
  return true
}
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}


// 格式化速度
const formatSpeed = (bytesPerSecond: number) => {
  if (bytesPerSecond === 0) return '0 B/s'
  return formatFileSize(bytesPerSecond) + '/s'
}


// 计算预计剩余时间
const calculateTimeLeft = (loaded: number, total: number, speed: number) => {
  if (speed === 0) return '计算中...'
  const remaining = total - loaded
  const seconds = Math.ceil(remaining / speed)
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}分${secs}秒`
}


const cancelUpload = () => {
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


const submitUpload = async () => {
  if (!selectedFile.value) return ElMessage.warning('请先选择文件')

  uploading.value = true
  uploadProgress.value = 0

  try {
    const res = await uploadResumeApi({
      file: selectedFile.value,
      userId: userStore.userInfo?.id?.toString(),
      overwrite: true,
      onProgress: (percent: number) => {
        uploadProgress.value = percent
      }
    })

    if (res.data.code === 200) {
      ElMessage.success('简历解析成功！')
      console.log(res.data.data);
      emit('parsed', res.data.data)

      // 如果 showClose 为 true，说明是弹窗模式，关闭弹窗
      if (props.showClose) {
        emit('close')
      }
    } else {
      ElMessage.error(res.data.msg || '解析失败，请重试')
    }
  } catch (error) {
    ElMessage.error('解析失败，请重试')
    console.error('简历上传错误:', error)
  } finally {
    uploading.value = false
    parsing.value = false
    uploadProgress.value = 0
    uploadSpeed.value = ''
    uploadTimeLeft.value = ''
    abortController.value = null
  }
}


// 拖拽事件处理
const handleDragEnter = () => {
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = () => {
  isDragging.value = false
}
</script>
<template>
  <div class="upload-component-wrapper">
    <!-- 上传卡片 -->
    <el-card class="upload-card" shadow="hover">
      <div class="upload-header">
        <h3>简历上传</h3>
        <el-button v-if="showClose" link type="info" @click="$emit('close')" :icon="Close" circle />
      </div>

      <div class="upload-area">
        <el-upload ref="uploadRef" drag :auto-upload="false" :on-change="handleFileChange" :before-upload="beforeUpload"
          :limit="1" accept=".pdf,.doc,.docx" class="upload-component">
          <el-icon class="upload-icon" :size="48"><upload-filled /></el-icon>
          <div class="upload-text">
            <div class="main-text">拖拽文件到此处或<em>点击上传</em></div>
            <div class="sub-text">
              支持 PDF、Word、图片格式（最大 5MB）
            </div>
          </div>
        </el-upload>

        <!-- 文件信息（选中后显示） -->
        <div v-if="selectedFile" class="file-info">
          <el-icon>
            <Document />
          </el-icon>
          <span class="file-name">{{ selectedFile.name }}</span>
          <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
        </div>

        <!-- 上传按钮 -->
        <el-button type="primary" :loading="uploading" @click="submitUpload" :disabled="!selectedFile"
          class="upload-btn" size="large">
          <el-icon class="btn-icon">
            <MagicStick v-if="!uploading" />
          </el-icon>
          {{ uploading ? 'AI 解析中...' : '开始智能解析' }}
        </el-button>

        <!-- 进度条 -->
        <div v-if="uploading" class="progress-section">
          <div class="progress-header">
            <span>上传进度</span>
            <span class="progress-percent">{{ uploadProgress }}%</span>
          </div>
          <el-progress :percentage="uploadProgress" :stroke-width="20" :color="progressColors" striped striped-flow />
          <div class="progress-tips">
            <el-text type="info" size="small">
              <el-icon>
                <Timer />
              </el-icon>
              AI 正在分析您的简历内容，请稍候...
            </el-text>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 功能说明 -->
    <el-card class="feature-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon>
            <Operation />
          </el-icon>
          <span>AI 解析功能</span>
        </div>
      </template>

      <div class="feature-list">
        <div class="feature-item">
          <el-icon class="feature-icon" color="#67C23A">
            <Check />
          </el-icon>
          <div class="feature-content">
            <div class="feature-title">智能技能提取</div>
            <div class="feature-desc">自动识别简历中的专业技能和工具</div>
          </div>
        </div>

        <div class="feature-item">
          <el-icon class="feature-icon" color="#409EFF">
            <Check />
          </el-icon>
          <div class="feature-content">
            <div class="feature-title">经历分析</div>
            <div class="feature-desc">深度解析项目经验和实习经历</div>
          </div>
        </div>

        <div class="feature-item">
          <el-icon class="feature-icon" color="#E6A23C">
            <Check />
          </el-icon>
          <div class="feature-content">
            <div class="feature-title">能力画像生成</div>
            <div class="feature-desc">生成个性化的职业能力画像</div>
          </div>
        </div>

        <div class="feature-item">
          <el-icon class="feature-icon" color="#F56C6C">
            <Check />
          </el-icon>
          <div class="feature-content">
            <div class="feature-title">发展建议</div>
            <div class="feature-desc">基于画像提供职业发展建议</div>
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

.upload-card {
  border-radius: 12px;
  margin-bottom: 16px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.upload-component {
  width: 100%;
}

:deep(.el-upload-dragger) {
  padding: 24px;
  transition: all 0.3s ease;
  border: 2px dashed #dcdfe6;
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
  font-size: 14px;
  color: #606266;
  margin-bottom: 6px;
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

.image-preview {
  width: 100%;
  max-height: 200px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebeef5;
  background: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

/* 文件信息卡片 */
.file-info-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: linear-gradient(135deg, #f5f9ff 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  width: 100%;
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
  font-weight: 500;
  color: #303133;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.file-type-tag {
  flex-shrink: 0;
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
  flex-shrink: 0;
  margin-left: 12px;
}

/* 操作按钮组 */
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  width: 100%;
}

.upload-btn {
  width: 100%;
  max-width: 200px;
  height: 42px;
  font-size: 15px;
  border-radius: 8px;
}

.upload-btn:disabled {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
  color: #c0c4cc;
}

.cancel-btn {
  width: 100px;
  height: 42px;
  font-size: 15px;
  border-radius: 8px;
}

.btn-icon {
  margin-right: 6px;
}

/* 进度条区域 */
.progress-section {
  width: 100%;
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
  font-weight: 600;
  color: #409eff;
}

.progress-percent.parsing-text {
  color: #67c23a;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
}

.progress-tips {
  margin-top: 12px;
  text-align: center;
}

.progress-tips .el-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.parsing-tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
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

.feature-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
  font-size: 15px;
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
  font-size: 18px;
  margin-top: 2px;
}

.feature-content {
  flex: 1;
}

.feature-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
  font-size: 14px;
}

.feature-desc {
  font-size: 13px;
  color: #909399;
}
</style>
