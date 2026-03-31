<script setup lang="ts">
//简历上传，作为能力画像的功能3\组件

import { ref, computed } from 'vue'
import { UploadFilled, Document, MagicStick, Timer, Operation, Check, Close, CircleCloseFilled, Picture, Folder, Warning } from '@element-plus/icons-vue'
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
const emit = defineEmits<{
  close: []
  parsed: [data: any]
}>()


const userStore = useUserStore()
const uploading = ref(false)
const parsing = ref(false)
const uploadProgress = ref(0)
const uploadSpeed = ref('') // 上传速度
const uploadTimeLeft = ref('') // 预计剩余时间
const selectedFile = ref<File | null>(null)
const imagePreview = ref<string>('')
const uploadRef = ref<any>(null)
const abortController = ref<AbortController | null>(null)
const isDragging = ref(false) // 拖拽状态


// 进度条颜色配置
const progressColors = [
  { color: '#409eff', percentage: 0 },
  { color: '#67c23a', percentage: 100 }
]


// 获取文件图标
const getFileIcon = computed(() => {
  if (!selectedFile.value) return Document
  const type = selectedFile.value.type
  if (type.startsWith('image/')) return Picture
  if (type.includes('pdf')) return Document
  return Folder
})


// 获取文件类型标签
const getFileTypeLabel = computed(() => {
  if (!selectedFile.value) return ''
  const type = selectedFile.value.type
  if (type.includes('pdf')) return 'PDF'
  if (type.includes('word') || type.includes('document')) return 'Word'
  if (type.startsWith('image/')) return '图片'
  return '文件'
})


const handleFileChange = (file: UploadFile, fileList: UploadFile[]) => {
  // 处理文件删除情况（fileList为空表示文件被移除）
  if (fileList.length === 0 || !file.raw) {
    clearFile()
    return
  }

  // 文件类型验证
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif'
  ]
  const isAllowedType = allowedTypes.includes(file.raw.type)

  if (!isAllowedType) {
    ElMessage.error('不支持的文件格式，请上传 PDF、Word 或图片文件')
    uploadRef.value?.clearFiles()
    return
  }

  // 文件大小验证 (5MB)
  const maxSize = 5 * 1024 * 1024
  if (file.raw.size > maxSize) {
    ElMessage.error(`文件大小超过 5MB 限制，当前大小: ${formatFileSize(file.raw.size)}`)
    uploadRef.value?.clearFiles()
    return
  }

  // 文件不能为空
  if (file.raw.size === 0) {
    ElMessage.error('文件内容为空，请重新选择')
    uploadRef.value?.clearFiles()
    return
  }

  selectedFile.value = file.raw

  // 图片预览
  if (file.raw.type.startsWith('image/')) {
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.onerror = () => {
      ElMessage.warning('图片预览加载失败')
      imagePreview.value = ''
    }
    reader.readAsDataURL(file.raw)
  } else {
    imagePreview.value = ''
  }
}


const clearFile = () => {
  selectedFile.value = null
  imagePreview.value = ''
  uploadRef.value?.clearFiles()
}


const removeFile = () => {
  if (uploading.value || parsing.value) {
    ElMessage.warning('上传进行中，请先取消上传')
    return
  }
  ElMessageBox.confirm(
    '确定要删除此文件吗？',
    '删除确认',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      clearFile()
      ElMessage({
        type: 'success',
        message: '文件已删除',
      })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除',
      })
    })
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


const showFileRequiredTip = ref(false)

const submitUpload = async () => {
  if (!selectedFile.value) {
    showFileRequiredTip.value = true
    ElMessage.warning('请先上传简历文件，再点击开始智能解析')
    // 3秒后隐藏提示
    setTimeout(() => {
      showFileRequiredTip.value = false
    }, 3000)
    return
  }
  
  // if (!userStore.userInfo?.id) {
  //   ElMessage.error('用户未登录，请先登录')
  //   return
  // }
  
  uploading.value = true
  uploadProgress.value = 0
  uploadSpeed.value = ''
  uploadTimeLeft.value = ''
  parsing.value = false
  
  // 创建新的 AbortController
  abortController.value = new AbortController()
  
  let lastLoaded = 0
  let lastTime = Date.now()
  
  try {
    const res = await uploadResumeApi({
      file: selectedFile.value,
      userId: userStore.userInfo?.id?.toString(),
      overwrite: true,
      onProgress: (progressEvent: any) => {
        if (!progressEvent.total) return
        
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        uploadProgress.value = Math.min(percent, 99) // 最多显示99%，留1%给后端处理
        
        // 计算上传速度
        const currentTime = Date.now()
        const timeDiff = (currentTime - lastTime) / 1000
        if (timeDiff > 0.5) { // 每0.5秒更新一次速度
          const loadedDiff = progressEvent.loaded - lastLoaded
          const speed = loadedDiff / timeDiff
          uploadSpeed.value = formatSpeed(speed)
          uploadTimeLeft.value = calculateTimeLeft(progressEvent.loaded, progressEvent.total, speed)
          lastLoaded = progressEvent.loaded
          lastTime = currentTime
        }
        
        // 上传完成后进入AI解析阶段
        if (percent >= 99) {
          parsing.value = true
          uploadSpeed.value = ''
          uploadTimeLeft.value = ''
        }
      }
    }, abortController.value.signal)
    
    if (res.data?.code === 200) {
      ElMessage.success('简历解析成功！')
      emit('parsed', res.data.data)
      clearFile()
      if (props.showClose) {
        emit('close')
      }
    } else {
      // 处理响应异常：code 非 200 或响应结构不完整
      const responseData = res?.data
      const errorMsg = responseData?.msg || `请求失败 (code: ${responseData?.code ?? 'unknown'})`
      ElMessage.error(errorMsg)
    }
  } catch (error: any) {
    // 处理用户取消上传的情况 (兼容不同 axios 版本)
    if (error.name === 'CanceledError' || error.name === 'AbortError' || error.code === 'ERR_CANCELED') {
      // 用户取消，不显示错误
      return
    }
    
    // 更详细的错误提示
    if (error.response) {
      const status = error.response.status
      const msg = error.response.data?.msg
      
      switch (status) {
        case 400:
          ElMessage.error(msg || '请求参数错误，请检查文件格式')
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
          ElMessage.error('服务器维护中，请稍后重试')
          break
        default:
          ElMessage.error(msg || `请求失败 (${status})`)
      }
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      // 请求超时
      ElMessage.error('上传超时，请检查网络或尝试上传较小的文件')
    } else if (error.request) {
      // 请求发送但没有收到响应
      ElMessage.error('网络连接失败，请检查网络后重试')
    } else {
      ElMessage.error('解析失败，请重试')
    }
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
        <el-button 
          v-if="showClose" 
          link 
          type="info" 
          @click="$emit('close')"
          :icon="Close"
          circle
        />
      </div>
      
      <div class="upload-area">
        <!-- 未选择文件提示 -->
        <div v-if="showFileRequiredTip" class="file-required-tip">
          <el-icon><Warning /></el-icon>
          <span>请先选择或拖拽简历文件到上方区域</span>
        </div>
        <el-upload
          ref="uploadRef"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif"
          class="upload-component"
          :class="{ 'is-dragging': isDragging, 'file-required': showFileRequiredTip }"
          @dragenter="handleDragEnter"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
        >
          <el-icon class="upload-icon" :size="48"><upload-filled /></el-icon>
          <div class="upload-text">
            <div class="main-text">拖拽文件到此处或<em>点击上传</em></div>
            <div class="sub-text">
              支持 PDF、Word、图片格式（最大 5MB）
            </div>
          </div>
        </el-upload>

        <!-- 图片预览（选中图片后显示） -->
        <div v-if="imagePreview" class="image-preview">
          <el-image
            :src="imagePreview"
            :preview-src-list="[imagePreview]"
            fit="contain"
            class="preview-img"
          />
        </div>

        <!-- 文件信息卡片（选中后显示） -->
        <div v-if="selectedFile" class="file-info-card">
          <div class="file-info-main">
            <el-icon class="file-type-icon" :size="32"><component :is="getFileIcon" /></el-icon>
            <div class="file-info-content">
              <div class="file-name-row">
                <span class="file-name" :title="selectedFile.name">{{ selectedFile.name }}</span>
                <el-tag size="small" type="info" class="file-type-tag">{{ getFileTypeLabel }}</el-tag>
              </div>
              <div class="file-meta">
                <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
                <span v-if="!uploading && !parsing" class="file-status ready">就绪</span>
                <span v-else-if="uploading" class="file-status uploading">上传中...</span>
                <span v-else class="file-status parsing">AI解析中...</span>
              </div>
            </div>
          </div>
          <el-button
            v-if="!uploading && !parsing"
            link
            type="danger"
            :icon="CircleCloseFilled"
            @click="removeFile"
            class="remove-btn"
          >
            删除
          </el-button>
        </div>

        <!-- 操作按钮组 -->
        <div class="action-buttons">
          <el-button 
            type="primary" 
            :loading="uploading || parsing" 
            @click="submitUpload"
            :disabled="uploading || parsing"
            class="upload-btn"
            :class="{ 'no-file': !selectedFile }"
            size="large"
          >
            <el-icon class="btn-icon" v-if="!uploading && !parsing"><MagicStick /></el-icon>
            {{ uploading ? '文件上传中...' : parsing ? 'AI 解析中...' : '开始智能解析' }}
          </el-button>
          
          <el-button
            v-if="uploading || parsing"
            @click="cancelUpload"
            class="cancel-btn"
            size="large"
          >
            <el-icon><Close /></el-icon>
            取消
          </el-button>
        </div>

        <!-- 上传进度条 -->
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

        <!-- AI解析进度条 -->
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
            <span>AI 正在深度分析您的简历内容，请稍候...</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 功能说明 -->
    <el-card class="feature-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Operation /></el-icon>
          <span>AI 解析功能</span>
        </div>
      </template>
      
      <div class="feature-list">
        <div class="feature-item">
          <el-icon class="feature-icon" color="#67C23A"><Check /></el-icon>
          <div class="feature-content">
            <div class="feature-title">智能技能提取</div>
            <div class="feature-desc">自动识别简历中的专业技能和工具</div>
          </div>
        </div>
        
        <div class="feature-item">
          <el-icon class="feature-icon" color="#409EFF"><Check /></el-icon>
          <div class="feature-content">
            <div class="feature-title">经历分析</div>
            <div class="feature-desc">深度解析项目经验和实习经历</div>
          </div>
        </div>
        
        <div class="feature-item">
          <el-icon class="feature-icon" color="#E6A23C"><Check /></el-icon>
          <div class="feature-content">
            <div class="feature-title">能力画像生成</div>
            <div class="feature-desc">生成个性化的职业能力画像</div>
          </div>
        </div>
        
        <div class="feature-item">
          <el-icon class="feature-icon" color="#F56C6C"><Check /></el-icon>
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
  gap: 16px;
}

/* 未选择文件提示 */
.file-required-tip {
  display: flex;
  align-items: center;
  gap: 8px;
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
  color: #e6a23c;
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

/* 上传区域需要文件的样式 */
.upload-component.file-required :deep(.el-upload-dragger) {
  border-color: #e6a23c;
  border-style: dashed;
  background-color: #fdf6ec;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-5px); }
  40% { transform: translateX(5px); }
  60% { transform: translateX(-3px); }
  80% { transform: translateX(3px); }
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

.upload-btn.no-file {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
  color: #c0c4cc;
}

.upload-btn.no-file:hover {
  background-color: #e6f2ff;
  border-color: #a0cfff;
  color: #409eff;
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
  0%, 100% {
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
