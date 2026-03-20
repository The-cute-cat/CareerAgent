<script setup lang="ts">
import type { UserStuInfo } from '@/types/user'
import { userGetUserBasicFileInfoService } from '@/api/user/user'
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User, School, Reading, Collection, Key, Lock, Unlock,
  Document, Edit, Check, Close, Phone, Link, TrendCharts
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/modules/user'
import {
  educationLevels, graduationYearOptions, profileFormData,
  privacySettingsData, progressColors
} from '@/mock/data'

const userStore = useUserStore()

// 编辑状态
const isEditing = ref(false)

// 个人档案表单
const userInfo = ref<UserStuInfo>({})
userInfo.value = { ...profileFormData }
console.log("userInfo", userInfo.value);

// const userInfo = reactive({ ...profileFormData })

// 原始数据（用于取消编辑）
let originalProfile = { ...userInfo }

// 隐私设置
const privacySettings = reactive({
  ...privacySettingsData,
  // 能力画像可见性
  profileVisibility: 'private' as 'public' | 'private',
  // 职业路径可见性
  careerPathVisibility: 'public' as 'public' | 'private',
  // 允许系统推荐匹配岗位
  allowRecommendations: true,
  // 允许企业查看基础信息
  allowCompanyView: false
})

// 进入编辑模式
const startEdit = () => {
  originalProfile = { ...userInfo }
  isEditing.value = true
}

// 保存个人信息
const saveProfile = () => {
  isEditing.value = false
  ElMessage.success('个人信息已保存')
  // 这里可以调用 API 保存到后端
  console.log('保存的个人档案：', userInfo)
}

// 取消编辑
const cancelEdit = () => {
  Object.assign(userInfo, originalProfile)
  isEditing.value = false
  ElMessage.info('已取消编辑')
}

// 保存隐私设置
const savePrivacy = () => {
  ElMessage.success('隐私设置已保存')
  // 这里可以调用 API 保存到后端
  console.log('保存的隐私设置：', privacySettings)
}

// 获取用户数据
onMounted(async () => {
  const res = await userGetUserBasicFileInfoService()
  if (res.data.code !== 200) {
    throw new Error(res.data.msg || '获取用户信息失败')
  }
  // 如果后端有数据，可以在这里加载
  if (res.data.data) {
    const resData = res.data.data
    userInfo.value = resData
  }
})
</script>

<template>
  <div class="profile-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>个人中心</h2>
      <span class="subtitle">管理您的个人信息和隐私设置</span>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：个人档案 -->
      <el-col :xs="24" :sm="24" :md="16">
        <el-card class="profile-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon :size="20">
                  <User />
                </el-icon>
                <span>个人基础档案</span>
              </div>
              <div class="header-actions" v-if="!isEditing">
                <el-button type="primary" size="small" @click="startEdit">
                  <el-icon>
                    <Edit />
                  </el-icon>
                  编辑
                </el-button>
              </div>
              <div class="header-actions" v-else>
                <el-button type="success" size="small" @click="saveProfile">
                  <el-icon>
                    <Check />
                  </el-icon>
                  保存
                </el-button>
                <el-button size="small" @click="cancelEdit">
                  <el-icon>
                    <Close />
                  </el-icon>
                  取消
                </el-button>
              </div>
            </div>
          </template>

          <el-form :model="userInfo" label-width="100px" class="profile-form" :disabled="!isEditing">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓名">
                  <el-input v-model="userInfo.realName" placeholder="请输入姓名">
                    <template #prefix>
                      <el-icon>
                        <User />
                      </el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="学校">
                  <el-input v-model="userInfo.school" placeholder="请输入学校">
                    <template #prefix>
                      <el-icon>
                        <School />
                      </el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="专业">
                  <el-input v-model="userInfo.major" placeholder="请输入专业">
                    <template #prefix>
                      <el-icon>
                        <Reading />
                      </el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="学历">
                  <el-select v-model="userInfo.education" placeholder="请选择学历" style="width: 100%">
                    <el-option v-for="level in educationLevels" :key="level.value" :label="level.label"
                      :value="level.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="毕业年份">
                  <el-select v-model="userInfo.graduationYear" placeholder="请选择毕业年份" style="width: 100%">
                    <el-option v-for="year in graduationYearOptions" :key="year.value" :label="year.label"
                      :value="year.value" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱">
                  <el-input v-model="userInfo.email" placeholder="请输入邮箱">
                    <template #prefix>
                      <el-icon>
                        <Key />
                      </el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="手机号">
                  <el-input v-model="userInfo.phone" placeholder="请输入手机号">
                    <template #prefix>
                      <el-icon>
                        <Phone />
                      </el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="GitHub">
                  <el-input v-model="userInfo.github" placeholder="请输入 GitHub 地址">
                    <template #prefix>
                      <el-icon>
                        <Link />
                      </el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="个人简介">
              <el-input v-model="userInfo.bio" type="textarea" :rows="3" placeholder="请简单介绍自己，包括学习经历、项目经验、职业规划等" />
            </el-form-item>
          </el-form>

          <div class="form-actions" v-if="isEditing">
            <el-button type="primary" @click="saveProfile">
              <el-icon>
                <Check />
              </el-icon>
              保存修改
            </el-button>
            <el-button @click="cancelEdit">
              <el-icon>
                <Close />
              </el-icon>
              取消
            </el-button>
          </div>
        </el-card>

        <!-- 能力画像展示 -->
        <el-card class="ability-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="20">
                <TrendCharts />
              </el-icon>
              <span>能力画像预览</span>
            </div>
          </template>
          <div class="ability-preview">
            <div class="ability-item">
              <span class="ability-name">Java 基础</span>
              <el-progress :percentage="85" :color="progressColors" />
            </div>
            <div class="ability-item">
              <span class="ability-name">框架应用</span>
              <el-progress :percentage="80" :color="progressColors" />
            </div>
            <div class="ability-item">
              <span class="ability-name">数据库</span>
              <el-progress :percentage="85" :color="progressColors" />
            </div>
            <div class="ability-item">
              <span class="ability-name">算法逻辑</span>
              <el-progress :percentage="90" :color="progressColors" />
            </div>
            <div class="ability-item">
              <span class="ability-name">沟通协作</span>
              <el-progress :percentage="75" :color="progressColors" />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：隐私设置 -->
      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="privacy-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="20">
                <Lock />
              </el-icon>
              <span>隐私设置</span>
            </div>
          </template>

          <div class="privacy-section">
            <h4>简历可见性</h4>
            <el-radio-group v-model="privacySettings.resumeVisibility" class="radio-group">
              <el-radio value="public">
                <el-icon>
                  <Unlock />
                </el-icon>
                公开 - 企业可查看
              </el-radio>
              <el-radio value="private">
                <el-icon>
                  <lock />
                </el-icon>
                私有 - 仅自己可见
              </el-radio>
            </el-radio-group>
            <p class="privacy-tip">控制您的简历是否对招聘企业可见</p>
          </div>

          <el-divider />

          <div class="privacy-section">
            <h4>能力画像可见性</h4>
            <el-radio-group v-model="privacySettings.profileVisibility" class="radio-group">
              <el-radio value="public">
                <el-icon>
                  <Unlock />
                </el-icon>
                公开
              </el-radio>
              <el-radio value="private">
                <el-icon>
                  <lock />
                </el-icon>
                私有
              </el-radio>
            </el-radio-group>
            <p class="privacy-tip">控制您的能力分析结果是否公开</p>
          </div>

          <el-divider />

          <div class="privacy-section">
            <h4>职业路径可见性</h4>
            <el-radio-group v-model="privacySettings.careerPathVisibility" class="radio-group">
              <el-radio value="public">
                <el-icon>
                  <Unlock />
                </el-icon>
                公开
              </el-radio>
              <el-radio value="private">
                <el-icon>
                  <lock />
                </el-icon>
                私有
              </el-radio>
            </el-radio-group>
            <p class="privacy-tip">控制您的职业发展规划是否公开</p>
          </div>

          <el-divider />

          <div class="privacy-section">
            <h4>其他设置</h4>
            <div class="checkbox-item">
              <el-checkbox v-model="privacySettings.allowRecommendations">
                允许系统推荐匹配岗位
              </el-checkbox>
              <p class="privacy-tip">开启后，系统会根据您的画像推荐合适的岗位</p>
            </div>
            <div class="checkbox-item">
              <el-checkbox v-model="privacySettings.allowCompanyView">
                允许企业查看基础信息
              </el-checkbox>
              <p class="privacy-tip">企业可查看您的姓名、学校、专业等基础信息</p>
            </div>
          </div>

          <div class="save-section">
            <el-button type="primary" @click="savePrivacy" style="width: 100%">
              <el-icon>
                <Check />
              </el-icon>
              保存隐私设置
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.profile-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.profile-card,
.ability-card,
.privacy-card,
.security-card {
  border-radius: 12px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.profile-form {
  padding: 10px 0;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.ability-card {
  margin-top: 20px;
}

.ability-preview {
  padding: 10px 0;
}

.ability-item {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.ability-name {
  width: 80px;
  font-size: 14px;
  color: #606266;
  flex-shrink: 0;
}

.ability-item :deep(.el-progress) {
  flex: 1;
}

.privacy-section {
  margin-bottom: 20px;
}

.privacy-section:last-child {
  margin-bottom: 0;
}

.privacy-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 8px;
}

.radio-group :deep(.el-radio) {
  margin-right: 0;
  height: auto;
}

.radio-group :deep(.el-radio__label) {
  display: flex;
  align-items: center;
  gap: 6px;
}

.privacy-tip {
  margin: 8px 0 0 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.checkbox-item {
  margin-bottom: 16px;
}

.checkbox-item:last-child {
  margin-bottom: 0;
}

.save-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.security-info {
  padding: 10px 0;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.security-item:last-child {
  border-bottom: none;
}

.security-item .label {
  font-size: 14px;
  color: #606266;
}

.security-item .value {
  font-size: 14px;
  color: #909399;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 12px;
  }

  .el-row {
    margin: 0 !important;
  }

  .el-col {
    padding: 0 !important;
  }
}
</style>
