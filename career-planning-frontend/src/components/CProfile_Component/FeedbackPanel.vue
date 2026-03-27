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
      <el-icon class="tip-icon"><InfoFilled /></el-icon>
      <span>您的反馈对我们非常重要，反馈建议一经采纳将赠送 <strong>200 积分</strong>！</span>
    </div>

    <div class="form-card">
      <div class="form-row">
        <div class="form-label">反馈类型</div>
        <el-select v-model="feedbackType" style="width: 100%">
          <el-option
            v-for="opt in typeOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </div>

      <div class="form-row">
        <div class="form-label">反馈内容 <span class="required">*</span></div>
        <el-input
          v-model="feedbackContent"
          type="textarea"
          :rows="5"
          placeholder="请详细描述您的问题或建议，我们非常期待您的声音..."
        />
      </div>

      <div class="form-row">
        <div class="form-label">添加截图 <span class="optional">可选，最多5张</span></div>
        <label class="upload-area">
          <div class="upload-placeholder">
            <el-icon><Picture /></el-icon>
            <span>点击或拖拽添加图片</span>
          </div>
          <input type="file" accept="image/*" multiple class="hidden-input" @change="handleUpload" />
        </label>

        <div v-if="imageList.length" class="preview-grid">
          <div v-for="(item, index) in imageList" :key="index" class="preview-item">
            <img :src="item.url" alt="" />
            <div class="preview-delete" @click="removeImage(index)">
              <el-icon><Delete /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <div class="form-row">
        <div class="form-label">联系方式 <span class="optional">可选</span></div>
        <el-input v-model="feedbackContact" placeholder="邮箱或手机号，方便我们联系您" />
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
  gap: 10px;
  padding: 14px 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, #eef5ff, #e8f4ff);
  border: 1px solid rgba(22, 119, 255, 0.12);
  font-size: 13px;
  color: #4a6fa5;
  line-height: 1.6;

  strong {
    color: #1553c7;
    font-weight: 800;
  }
}

.tip-icon {
  font-size: 18px;
  color: #1677ff;
  flex-shrink: 0;
}

.form-card {
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding: 24px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #e8eef6;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03);
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
  background: #f8fafc;
  border: 1.5px dashed #cbd5e1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
  color: #94a3b8;
  transition: all 0.2s;

  &:hover {
    border-color: #94a3b8;
    background: #f1f5f9;
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
  height: 44px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  background: linear-gradient(135deg, #1677ff, #409eff);
  border: none;
  box-shadow: 0 4px 16px rgba(22, 119, 255, 0.3);
  transition: all 0.25s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(22, 119, 255, 0.35);
  }
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner),
:deep(.el-select__wrapper) {
  border-radius: 14px;
  box-shadow: none;
}
</style>
