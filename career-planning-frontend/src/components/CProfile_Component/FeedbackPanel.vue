<script setup>
import { ref } from 'vue'
import { Picture, InfoFilled, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const feedbackType = ref('功能建议')
const feedbackContent = ref('')
const feedbackContact = ref('')
const imageList = ref([])

const handleUpload = (event) => {
  const files = Array.from(event.target.files || [])

  if (!files.length) return

  if (imageList.value.length + files.length > 5) {
    ElMessage.warning('最多上传 5 张截图')
    return
  }

  files.forEach((file) => {
    if (!file.type.startsWith('image/')) return

    const reader = new FileReader()
    reader.onload = (e) => {
      imageList.value.push({
        name: file.name,
        url: e.target?.result
      })
    }
    reader.readAsDataURL(file)
  })
}

const removeImage = (index) => {
  imageList.value.splice(index, 1)
}

const submitFeedback = () => {
  if (!feedbackContent.value.trim()) {
    ElMessage.warning('请填写反馈内容')
    return
  }

  ElMessage.success('反馈提交成功，感谢你的宝贵建议！')
  feedbackContent.value = ''
  feedbackContact.value = ''
  imageList.value = []
}

const typeOptions = [
  { label: '功能建议', value: '功能建议' },
  { label: 'Bug反馈', value: 'Bug反馈' },
  { label: '体验问题', value: '体验问题' },
  { label: '其他', value: '其他' }
]
</script>

<template>
  <div class="feedback-panel">
    <div class="tip-banner">
      <el-icon class="tip-icon">
        <InfoFilled />
      </el-icon>
      <span>您的反馈对我们非常重要，反馈建议一经采纳将赠送 <strong>200 积分</strong>！</span>
    </div>

    <div class="form-card">
      <div class="form-row">
        <div class="form-label">反馈类型</div>
        <el-select v-model="feedbackType" style="width: 100%">
          <el-option v-for="opt in typeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
      </div>

      <div class="form-row">
        <div class="form-label">反馈内容 <span class="required">*</span></div>
        <el-input v-model="feedbackContent" type="textarea" :rows="5" placeholder="请详细描述您的问题或建议，我们非常期待您的声音..." />
      </div>

      <div class="form-row">
        <div class="form-label">添加截图 <span class="optional">可选，最多5张</span></div>
        <label class="upload-area">
          <div class="upload-placeholder">
            <el-icon>
              <Picture />
            </el-icon>
            <span>点击或拖拽添加图片</span>
          </div>
          <input type="file" accept="image/*" multiple class="hidden-input" @change="handleUpload" />
        </label>

        <div v-if="imageList.length" class="preview-grid">
          <div v-for="(item, index) in imageList" :key="index" class="preview-item">
            <img :src="item.url" alt="" />
            <div class="preview-delete" @click="removeImage(index)">
              <el-icon>
                <Delete />
              </el-icon>
            </div>
          </div>
        </div>
      </div>

      <div class="form-row">
        <div class="form-label">联系方式 <span class="optional">可选</span></div>
        <el-input v-model="feedbackContact" placeholder="邮箱，方便我们联系您" />
      </div>
    </div>

    <el-button type="primary" class="submit-btn" @click="submitFeedback">
      提交反馈
    </el-button>
  </div>
</template>

<style scoped lang="scss">
.feedback-panel {
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
  background: linear-gradient(135deg, rgba(241, 245, 249, 0.8), rgba(248, 250, 252, 0.5));
  backdrop-filter: blur(12px);
  border: 1px solid #e2e8f0;
  font-size: 14px;
  color: #475569;
  line-height: 1.6;

  strong {
    color: #0f172a;
    font-weight: 800;
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
  padding: 32px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 1);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.03), inset 0 1px 2px rgba(255, 255, 255, 1);
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 700;
  color: #2b3f57;
}

.required {
  color: #f56c6c;
}

.optional {
  font-weight: 400;
  font-size: 12px;
  color: #9ca3af;
  margin-left: 4px;
}

.upload-area {
  cursor: pointer;
}

.upload-placeholder {
  height: 96px;
  border-radius: 16px;
  background: rgba(248, 250, 252, 0.6);
  border: 1.5px dashed rgba(203, 213, 225, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: #64748b;
  transition: all 0.3s ease;

  &:hover {
    border-color: #1677ff;
    background: rgba(238, 245, 255, 0.8);
    color: #1677ff;
  }
}

.hidden-input {
  display: none;
}

.preview-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 4px;
}

.preview-item {
  width: 76px;
  height: 76px;
  border-radius: 14px;
  overflow: hidden;
  position: relative;
  border: 1px solid #e2e8f0;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.preview-delete {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 11px;
  opacity: 0;
  transition: opacity 0.2s;

  .preview-item:hover & {
    opacity: 1;
  }
}

.submit-btn {
  height: 48px;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 800;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(37, 99, 235, 0.35);
  }
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner),
:deep(.el-select__wrapper) {
  border-radius: 16px;
  background: rgba(248, 250, 252, 0.8);
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.02);
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-textarea__inner:focus),
:deep(.el-select__wrapper.is-focus) {
  background: #ffffff;
  border-color: #1677ff;
  box-shadow: 0 0 0 3px rgba(22, 119, 255, 0.1);
}
</style>