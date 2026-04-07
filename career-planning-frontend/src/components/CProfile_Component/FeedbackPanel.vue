<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Picture, InfoFilled, Delete, ChatDotSquare, Timer, List, Promotion, Check, Edit, Close } from '@element-plus/icons-vue'
import { ElMessage, ElLoading } from 'element-plus'
import { submitFeedbackService, getUserFeedbackHistoryService, updateFeedbackService, uploadImageService, type Feedback } from '@/api/feedback'
import { useUserStore } from '@/stores/modules/user'

const userStore = useUserStore()
const activeTab = ref('submit') // 'submit' | 'history'

// 反馈提交相关状态
const feedbackType = ref('功能建议')
const feedbackContent = ref('')
const feedbackContact = ref('')
const imageList = ref<any[]>([])
const isSubmitting = ref(false)

// 编辑相关状态
const isEditing = ref(false)
const editingId = ref<number | null>(null)

// 反馈历史相关状态
const feedbackHistory = ref<Feedback[]>([])
const historyLoading = ref(false)
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)

const typeOptions = [
  { label: '功能建议', value: '功能建议' },
  { label: 'Bug反馈', value: 'Bug反馈' },
  { label: '体验问题', value: '体验问题' },
  { label: '其他', value: '其他' }
]

const handleUpload = (event: any) => {
  const files = Array.from(event.target.files || []) as File[]

  if (!files.length) return

  if (imageList.value.length + files.length > 5) {
    ElMessage.warning('最多上传 5 张截图')
    return
  }

  files.forEach((file) => {
    if (!file.type.startsWith('image/')) return
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.warning(`${file.name} 超过 2MB，请压缩后上传`)
      return
    }

    // 使用 URL.createObjectURL 生成预览链接，性能优于 Base64
    const blobUrl = URL.createObjectURL(file)
    imageList.value.push({
      name: file.name,
      url: blobUrl,
      file: file // 保存原始文件对象用于后续上传
    })
  })
  
  // 清空 input 允许重复选择
  event.target.value = ''
}

const removeImage = (index: number) => {
  const removedImg = imageList.value[index]
  // 如果是本地生成的 blob url，删除时释放内存
  if (removedImg.url.startsWith('blob:')) {
    URL.revokeObjectURL(removedImg.url)
  }
  imageList.value.splice(index, 1)
}

const submitFeedback = async () => {
  if (!feedbackContent.value.trim()) {
    ElMessage.warning('请填写反馈内容')
    return
  }

  if (!userStore.userInfo?.id) {
    ElMessage.error('请先登录后再提交反馈')
    return
  }

  isSubmitting.value = true
  const loading = ElLoading.service({ text: isEditing.value ? '正在保存修改...' : '正在提交您的宝贵建议...' })

  try {
    // 采用“并行快速上传”方案 (Promise.all)
    const uploadTasks = imageList.value.map(async (img) => {
      if (img.file) {
        // 快递员出发：并行发送上传请求
        const res = await uploadImageService(img.file)
        if (res.data.code === 200 || res.data.code === 0) {
          return res.data.data?.url || '' // 从 Result 中提取服务端生成的 URL
        } else {
          throw new Error(`图片 ${img.name} 上传失败: ${res.data.msg}`)
        }
      }
      return img.url // 已经是远程 URL 的直接保留
    })

    // 大管家统一收货：等待所有图片上传完成
    const finalImageUrls = await Promise.all(uploadTasks)
    
    // 过滤掉可能的空值并拼接
    const imageUrlsString = finalImageUrls.filter(url => !!url).join(',')

    const data: Feedback = {
      userId: userStore.userInfo.id,
      type: feedbackType.value,
      content: feedbackContent.value,
      contact: feedbackContact.value,
      images: imageUrlsString
    }

    let res;
    if (isEditing.value && editingId.value) {
      data.id = editingId.value
      res = await updateFeedbackService(data)
    } else {
      res = await submitFeedbackService(data)
    }

    if (res.data.code === 200 || res.data.code === 0) {
      ElMessage.success(isEditing.value ? '修改保存成功！' : '反馈提交成功，感谢您的宝贵建议！')
      resetForm()
      fetchHistory()
      activeTab.value = 'history'
    } else {
      ElMessage.error(res.data.msg || '操作失败，请稍后重试')
    }
  } catch (error: any) {
    console.error('提交/更新反馈失败:', error)
    ElMessage.error(error.message || '操作失败，网络连接异常')
  } finally {
    isSubmitting.value = false
    loading.close()
  }
}

const resetForm = () => {
  // 清理所有产生的 blob urls 释放内存
  imageList.value.forEach(img => {
    if (img.url.startsWith('blob:')) {
      URL.revokeObjectURL(img.url)
    }
  })
  
  feedbackContent.value = ''
  feedbackContact.value = ''
  imageList.value = []
  feedbackType.value = '功能建议'
  isEditing.value = false
  editingId.value = null
}

const cancelEdit = () => {
  resetForm()
  activeTab.value = 'history'
}

const enterEditMode = (item: Feedback) => {
  if (item.status !== 0) {
    ElMessage.warning('该反馈已在处理中，无法修改')
    return
  }
  
  feedbackType.value = item.type
  feedbackContent.value = item.content
  feedbackContact.value = item.contact || ''
  editingId.value = item.id || null
  isEditing.value = true
  
  // 处理图片回填
  imageList.value = []
  if (item.images) {
    item.images.split(',').forEach(url => {
      imageList.value.push({
        url: url,
        name: 'image'
      })
    })
  }
  
  activeTab.value = 'submit'
}

const fetchHistory = async () => {
  if (!userStore.userInfo?.id) return

  historyLoading.value = true
  try {
    const res = await getUserFeedbackHistoryService(userStore.userInfo.id, pageNum.value, pageSize.value)
    if (res.data.code === 200 || res.data.code === 0) {
      const data = res.data.data
      feedbackHistory.value = data.records || data || []
      total.value = data.total || feedbackHistory.value.length
    }
  } catch (error) {
    console.error('获取反馈历史失败:', error)
  } finally {
    historyLoading.value = false
  }
}

const getStatusType = (status?: number) => {
  switch (status) {
    case 0: return 'info'
    case 1: return 'success'
    case 2: return 'warning'
    default: return 'info'
  }
}

const getStatusLabel = (status?: number) => {
  switch (status) {
    case 0: return '待处理'
    case 1: return '已回复'
    case 2: return '已关闭'
    default: return '待处理'
  }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  if (activeTab.value === 'history') {
    fetchHistory()
  }
})
</script>

<template>
  <div class="feedback-container">
    <!-- Tab 头部切换 -->
    <div class="tab-header">
      <div 
        class="tab-btn" 
        :class="{ active: activeTab === 'submit' }" 
        @click="activeTab = 'submit'"
      >
        <el-icon v-if="!isEditing"><ChatDotSquare /></el-icon>
        <el-icon v-else><Edit /></el-icon>
        {{ isEditing ? '编辑反馈' : '提交反馈' }}
      </div>
      <div 
        class="tab-btn" 
        :class="{ active: activeTab === 'history' }" 
        @click="activeTab = 'history'; fetchHistory()"
      >
        <el-icon><Timer /></el-icon>
        反馈历史
      </div>
    </div>

    <!-- 提交反馈视图 -->
    <div v-if="activeTab === 'submit'" class="feedback-panel">
      <div class="tip-banner">
        <el-icon class="tip-icon">
          <Check />
        </el-icon>
        <span v-if="!isEditing">您的意见是我们的动力，中肯建议采纳后最高奖励 <strong>200 积分</strong>！</span>
        <span v-else>正在编辑您的建议，完善后点击下方保存按钮即可同步修改。</span>
      </div>

      <div class="form-card">
        <div class="form-row">
          <div class="form-label">反馈类型</div>
          <div class="type-selector">
            <div 
              v-for="opt in typeOptions" 
              :key="opt.value" 
              class="type-item"
              :class="{ active: feedbackType === opt.value }"
              @click="feedbackType = opt.value"
            >
              {{ opt.label }}
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-label">反馈内容 <span class="required">*</span></div>
          <el-input 
            v-model="feedbackContent" 
            type="textarea" 
            :rows="6" 
            placeholder="请详细描述您的问题或建议，也可以输入您的期待，我们非常期待您的声音..." 
          />
        </div>

        <div class="form-row">
          <div class="form-label">添加截图 <span class="optional">可选，最多5张</span></div>
          <div class="upload-container">
            <label class="upload-area">
              <div class="upload-placeholder">
                <el-icon><Picture /></el-icon>
                <span>添加图片</span>
              </div>
              <input type="file" accept="image/*" multiple class="hidden-input" @change="handleUpload" />
            </label>

            <div v-if="imageList.length" class="preview-grid">
              <div v-for="(item, index) in imageList" :key="index" class="preview-item">
                <el-image 
                  :src="item.url" 
                  fit="cover" 
                  class="preview-img"
                  :preview-src-list="imageList.map(i => i.url)"
                  :initial-index="index"
                />
                <div class="preview-delete" @click="removeImage(index)">
                  <el-icon><Delete /></el-icon>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-label">联系方式 <span class="optional">可选</span></div>
          <el-input v-model="feedbackContact" placeholder="邮箱或手机号，方便我们向您反馈处理进度" />
        </div>
      </div>

      <div class="button-group">
        <el-button 
          v-if="isEditing"
          class="cancel-btn"
          @click="cancelEdit"
        >
          取消编辑
        </el-button>
        <el-button 
          type="primary" 
          class="submit-btn" 
          @click="submitFeedback" 
          :loading="isSubmitting"
          :class="{ 'is-editing': isEditing }"
        >
          <el-icon v-if="!isSubmitting"><Promotion /></el-icon>
          {{ isEditing ? '保存修改内容' : '立即提交反馈' }}
        </el-button>
      </div>
    </div>

    <!-- 历史记录视图 -->
    <div v-else class="history-panel" v-loading="historyLoading">
      <div v-if="feedbackHistory.length === 0" class="empty-state">
        <el-icon class="empty-icon"><List /></el-icon>
        <p>暂无反馈记录</p>
        <el-button type="primary" link @click="activeTab = 'submit'">去反馈一条</el-button>
      </div>
      
      <div v-else class="history-list">
        <div v-for="item in feedbackHistory" :key="item.id" class="history-item">
          <div class="hi-header">
            <el-tag :type="getStatusType(item.status)" size="small" effect="plain">
              {{ getStatusLabel(item.status) }}
            </el-tag>
            <span class="hi-type">{{ item.type }}</span>
            <span class="hi-date">{{ formatDate(item.createTime) }}</span>
            
            <!-- 编辑按钮 - 仅待处理可见 -->
            <el-button 
              v-if="item.status === 0"
              link 
              type="primary" 
              class="edit-link"
              @click="enterEditMode(item)"
              :icon="Edit"
            >
              编辑
            </el-button>
          </div>
          <div class="hi-content">{{ item.content }}</div>
          
          <div v-if="item.images" class="hi-images">
            <el-image 
              v-for="(img, idx) in item.images.split(',')" 
              :key="idx" 
              :src="img" 
              class="hi-image"
              :preview-src-list="item.images.split(',')"
              :initial-index="idx"
            />
          </div>

          <div v-if="item.response" class="hi-response">
            <div class="hr-title">
              <el-icon><ChatDotSquare /></el-icon> 官方回复
            </div>
            <div class="hr-text">{{ item.response }}</div>
          </div>
        </div>

        <div class="pagination-container" v-if="total > pageSize">
          <el-pagination
            v-model:current-page="pageNum"
            :page-size="pageSize"
            layout="prev, pager, next"
            :total="total"
            @current-change="fetchHistory"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.feedback-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.tab-header {
  display: flex;
  background: #f1f5f9;
  padding: 4px;
  border-radius: 12px;
  width: fit-content;
  margin-bottom: 8px;
}

.tab-btn {
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    color: #3b82f6;
  }

  &.active {
    background: #ffffff;
    color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  }
}

.feedback-panel, .history-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tip-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(37, 99, 235, 0.03));
  border: 1px solid rgba(191, 219, 254, 0.5);
  font-size: 14px;
  color: #1e40af;
  line-height: 1.6;

  strong {
    color: #ef4444;
    font-weight: 800;
    margin: 0 4px;
  }
}

.tip-icon {
  font-size: 20px;
  color: #3b82f6;
  flex-shrink: 0;
}

.form-card {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 28px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 1);
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.04);
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-label {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
  display: flex;
  align-items: center;
}

.required { color: #f56c6c; margin-left: 2px; }
.optional { font-weight: 400; font-size: 12px; color: #94a3b8; margin-left: 6px; }

.type-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.type-item {
  padding: 8px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }

  &.active {
    background: #eff6ff;
    border-color: #3b82f6;
    color: #3b82f6;
    font-weight: 700;
  }
}

.upload-container {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.upload-area {
  cursor: pointer;
  flex-shrink: 0;
}

.upload-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  background: #f8fafc;
  border: 2px dashed #e2e8f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 12px;
  color: #94a3b8;
  transition: all 0.3s;

  &:hover {
    border-color: #3b82f6;
    background: #f0f7ff;
    color: #3b82f6;
  }
  
  .el-icon { font-size: 20px; }
}

.preview-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.preview-item {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  border: 1px solid #e2e8f0;

  .preview-img { width: 100%; height: 100%; }
}

.preview-delete {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  backdrop-filter: blur(4px);
  transition: transform 0.2s;

  &:hover { transform: scale(1.1); }
}

.button-group {
  display: flex;
  gap: 12px;
  width: 100%;
}

.cancel-btn {
  flex: 1;
  height: 52px;
  border-radius: 18px;
  font-size: 16px;
  font-weight: 700;
  border: 2px solid #e2e8f0;
  color: #64748b;
  background: #fff;
  transition: all 0.3s;

  &:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
    color: #334155;
  }
}

.submit-btn {
  flex: 2;
  height: 52px;
  border-radius: 18px;
  font-size: 16px;
  font-weight: 800;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  border: none;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.25);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;

  &.is-editing {
    background: linear-gradient(135deg, #059669, #10b981);
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.25);
  }

  &:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 12px 30px rgba(37, 99, 235, 0.35);
  }

  &.is-editing:hover {
    box-shadow: 0 12px 30px rgba(16, 185, 129, 0.35);
  }
  
  &:active { transform: translateY(0) scale(1); }
}

// 历史记录样式
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #94a3b8;

  .empty-icon { font-size: 64px; margin-bottom: 16px; opacity: 0.3; }
  p { margin-bottom: 8px; font-size: 15px; }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  background: #ffffff;
  padding: 20px;
  border-radius: 20px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 6px rgba(15, 23, 42, 0.02);
  transition: transform 0.2s;

  &:hover { transform: translateX(4px); }
}

.hi-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.hi-type { font-weight: 700; color: #1e293b; font-size: 14px; }
.hi-date { margin-left: 10px; color: #94a3b8; font-size: 12px; }

.edit-link {
  margin-left: auto;
  font-size: 13px;
  font-weight: 700;
}

.hi-content {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  white-space: pre-wrap;
  margin-bottom: 12px;
}

.hi-images {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.hi-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  border: 1px solid #f1f5f9;
}

.hi-response {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  border-left: 4px solid #3b82f6;

  .hr-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 700;
    color: #1e40af;
    margin-bottom: 6px;
  }

  .hr-text {
    font-size: 13px;
    color: #334155;
    line-height: 1.5;
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.hidden-input { display: none; }

:deep(.el-textarea__inner) {
  border-radius: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 12px 16px;
  transition: all 0.3s;

  &:focus {
    background: #fff;
    border-color: #3b82f6;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  }
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  background: #f8fafc;
  box-shadow: none !important;
  border: 1px solid #e2e8f0;
  
  &.is-focus { border-color: #3b82f6; background: #fff; }
}
</style>