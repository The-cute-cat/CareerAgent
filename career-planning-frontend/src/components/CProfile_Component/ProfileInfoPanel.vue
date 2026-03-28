<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Picture, EditPen, Check, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  userInfo: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update-user'])

const isEditing = ref(false)

const formData = reactive({
  name: '',
  signature: '',
  gender: '',
  education: '',
  experience: '',
  industries: '',
  jobs: '',
  avatar: ''
})

watch(
  () => props.userInfo,
  (val) => {
    if (!val) return
    Object.assign(formData, val)
  },
  { immediate: true, deep: true }
)

const splitTags = (value) => {
  if (!value) return []
  return value
    .split(/[、,，/]/)
    .map(item => item.trim())
    .filter(Boolean)
}

const profileHighlights = computed(() => [
  {
    label: '教育背景',
    value: formData.education || '待完善'
  },
  {
    label: '当前阶段',
    value: formData.experience || '待完善'
  },
  {
    label: '关注行业',
    value: splitTags(formData.industries).length || 0
  },
  {
    label: '目标岗位',
    value: splitTags(formData.jobs).length || 0
  }
])

const basicFields = computed(() => [
  { key: 'name', label: '昵称', type: 'input', placeholder: '请输入昵称' },
  { key: 'signature', label: '个性签名', type: 'input', placeholder: '介绍一下现在的你' },
  {
    key: 'gender',
    label: '性别',
    type: 'select',
    options: ['男', '女', '其他']
  },
  {
    key: 'education',
    label: '教育背景',
    type: 'select',
    options: ['专科', '本科', '硕士', '博士']
  },
  {
    key: 'experience',
    label: '当前阶段',
    type: 'select',
    options: ['在校生', '应届生', '1-3年', '3-5年', '5年以上']
  }
])

const interestBlocks = computed(() => [
  {
    key: 'industries',
    title: '关注行业',
    desc: '把你希望深入发展的行业方向整理出来，方便后续推荐更贴近你的机会。',
    tags: splitTags(formData.industries)
  },
  {
    key: 'jobs',
    title: '目标岗位',
    desc: '明确岗位意向后，系统后续可以更聚焦地呈现能力建议与成长路径。',
    tags: splitTags(formData.jobs)
  }
])

const startEdit = () => {
  isEditing.value = true
}

const cancelEdit = () => {
  Object.assign(formData, props.userInfo)
  isEditing.value = false
}

const saveEdit = () => {
  emit('update-user', { ...formData })
  isEditing.value = false
}

const handleAvatarUpload = (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请上传图片文件')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    formData.avatar = e.target?.result
    ElMessage.success('头像预览已更新')
  }
  reader.readAsDataURL(file)
}
</script>

<template>
  <div class="profile-info-panel">
    <div class="panel-header">
      <div>
        <div class="panel-title">我的职业名片</div>
        <div class="panel-subtitle">把关键信息整理得更清晰，持续完善你的成长画像。</div>
      </div>

      <div class="action-group">
        <template v-if="!isEditing">
          <el-button type="primary" round @click="startEdit">
            <el-icon><EditPen /></el-icon>
            编辑资料
          </el-button>
        </template>

        <template v-else>
          <el-button round @click="cancelEdit">
            <el-icon><Close /></el-icon>
            取消
          </el-button>
          <el-button type="primary" round @click="saveEdit">
            <el-icon><Check /></el-icon>
            保存
          </el-button>
        </template>
      </div>
    </div>

    <div class="hero-card">
      <div class="hero-main">
        <label class="avatar-box">
          <img :src="formData.avatar" class="big-avatar" alt="avatar" />
          <div class="camera-badge">
            <el-icon><Picture /></el-icon>
          </div>
          <input type="file" accept="image/*" class="hidden-input" @change="handleAvatarUpload" />
        </label>

        <div class="hero-copy">
          <div class="name-row">
            <h2>{{ formData.name || '未命名用户' }}</h2>
            <span class="status-chip">{{ formData.experience || '待完善阶段' }}</span>
          </div>
          <p>{{ formData.signature || '这里可以写下你的阶段目标、求职方向或一句让自己保持前进的话。' }}</p>

          <div class="hero-tags">
            <span class="hero-tag">{{ formData.gender || '未设置性别' }}</span>
            <span class="hero-tag">{{ formData.education || '未设置学历' }}</span>
            <span class="hero-tag">{{ splitTags(formData.jobs)[0] || '待设置目标岗位' }}</span>
          </div>
        </div>
      </div>

      <div class="stats-grid">
        <div v-for="item in profileHighlights" :key="item.label" class="stat-card">
          <div class="stat-label">{{ item.label }}</div>
          <div class="stat-value">{{ item.value }}</div>
        </div>
      </div>
    </div>

    <div class="section-title">基础信息</div>
    <div class="base-grid">
      <div v-for="field in basicFields" :key="field.key" class="field-card">
        <div class="field-label">{{ field.label }}</div>

        <template v-if="isEditing && field.type === 'input'">
          <el-input v-model="formData[field.key]" :placeholder="field.placeholder" />
        </template>

        <template v-else-if="isEditing && field.type === 'select'">
          <el-select v-model="formData[field.key]" style="width: 100%">
            <el-option
              v-for="option in field.options"
              :key="option"
              :label="option"
              :value="option"
            />
          </el-select>
        </template>

        <template v-else>
          <div class="field-value">{{ formData[field.key] || '待完善' }}</div>
        </template>
      </div>
    </div>

    <div class="section-title">兴趣与方向</div>
    <div class="interest-grid">
      <div v-for="block in interestBlocks" :key="block.key" class="interest-card">
        <div class="interest-head">
          <div>
            <h3>{{ block.title }}</h3>
            <p>{{ block.desc }}</p>
          </div>
          <div class="interest-count">{{ block.tags.length }}</div>
        </div>

        <template v-if="isEditing">
          <el-input
            v-model="formData[block.key]"
            type="textarea"
            :rows="3"
            placeholder="可使用顿号、逗号或斜杠分隔多个内容"
          />
        </template>

        <template v-else>
          <div v-if="block.tags.length" class="tag-list">
            <span v-for="tag in block.tags" :key="tag" class="tag-pill">{{ tag }}</span>
          </div>
          <div v-else class="empty-text">还没有填写，补充后会让个人中心更完整。</div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.profile-info-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.panel-title {
  font-size: 26px;
  font-weight: 800;
  color: #143250;
}

.panel-subtitle {
  margin-top: 8px;
  max-width: 640px;
  font-size: 14px;
  line-height: 1.8;
  color: #66788f;
}

.action-group {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.hero-card {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.45), transparent 24%),
    linear-gradient(135deg, #1f77ff 0%, #45b6ff 55%, #78d0c5 100%);
  color: #fff;
  box-shadow: 0 20px 48px rgba(26, 91, 176, 0.2);
}

.hero-card::after {
  content: '';
  position: absolute;
  top: -60px;
  right: -20px;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
}

.hero-main {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-box {
  position: relative;
  width: 104px;
  height: 104px;
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.25s ease;
}

.avatar-box:hover {
  transform: translateY(-2px) scale(1.02);
}

.big-avatar {
  width: 100%;
  height: 100%;
  border-radius: 28px;
  object-fit: cover;
  border: 3px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 12px 32px rgba(9, 37, 92, 0.24);
}

.camera-badge {
  position: absolute;
  right: -4px;
  bottom: -4px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #fff;
  color: #1677ff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 20px rgba(13, 54, 130, 0.18);
}

.hidden-input {
  display: none;
}

.hero-copy {
  position: relative;
  z-index: 1;
  flex: 1;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.name-row h2 {
  margin: 0;
  font-size: 30px;
  line-height: 1.15;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  font-size: 12px;
  font-weight: 700;
}

.hero-copy p {
  margin: 12px 0 0;
  max-width: 640px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.92);
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  font-size: 13px;
  font-weight: 600;
}

.stats-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

.stat-card {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(10px);
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
}

.stat-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 800;
  line-height: 1.2;
}

.section-title {
  margin-top: 8px;
  font-size: 18px;
  font-weight: 800;
  color: #163253;
}

.base-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.field-card,
.interest-card {
  border-radius: 20px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e8eef6;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.field-label {
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 700;
  color: #7a8ca3;
}

.field-value {
  min-height: 24px;
  font-size: 16px;
  font-weight: 700;
  color: #22364d;
}

.interest-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.interest-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.interest-head h3 {
  margin: 0;
  font-size: 18px;
  color: #1f3550;
}

.interest-head p {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.7;
  color: #6b7d93;
}

.interest-count {
  min-width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #edf5ff, #f2fbf7);
  color: #1668dc;
  font-size: 18px;
  font-weight: 800;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: #f2f7ff;
  color: #1f5ec9;
  font-size: 13px;
  font-weight: 700;
}

.empty-text {
  font-size: 13px;
  line-height: 1.7;
  color: #95a1b2;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner),
:deep(.el-select__wrapper) {
  border-radius: 14px;
  box-shadow: none;
}

@media (max-width: 992px) {
  .stats-grid,
  .base-grid,
  .interest-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .panel-header,
  .hero-main {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-group {
    width: 100%;
  }

  .stats-grid,
  .base-grid,
  .interest-grid {
    grid-template-columns: 1fr;
  }

  .hero-card {
    padding: 20px;
  }

  .name-row h2 {
    font-size: 26px;
  }
}
</style>
