<script setup>

//上传简历页面，包含文件上传组件和步骤条，模拟AI解析过程并跳转到报告页面
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled } from '@element-plus/icons-vue'

const router = useRouter()
const activeStep = ref(0)
const loading = ref(false)
const file = ref(null)


const handleFileChange = (uploadFile) => {
  file.value = uploadFile.raw
}


const startAnalyze = () => {
  if (!file.value) return alert('请先选择文件')
  loading.value = true
  // 模拟后端请求延迟
  setTimeout(() => {
    loading.value = false
    activeStep.value = 1
    setTimeout(() => { activeStep.value = 2 }, 2000)
  }, 1500)
}

const goReport = () => {
  router.push('/report')
}
</script>

<template>
  <div class="upload-page">
    <el-card class="box-card">
      <template #header>上传个人简历</template>
      
      <!-- 步骤条 -->
      <el-steps :active="activeStep" finish-status="success" align-center>
        <el-step title="上传简历" />
        <el-step title="AI 解析" />
        <el-step title="生成报告" />
      </el-steps>

      <div class="upload-area" v-if="activeStep === 0">
        <el-upload drag action="#" :auto-upload="false" :on-change="handleFileChange">
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        </el-upload>
        <el-button type="primary" @click="startAnalyze" :loading="loading" style="margin-top: 20px;">
          开始解析
        </el-button>
      </div>

      <div v-else-if="activeStep === 1" class="loading-area">
        <el-result icon="info" title="AI 正在解析简历..." sub-title="请稍候，预计需要 5 秒"></el-result>
      </div>

      <div v-else-if="activeStep === 2" class="success-area">
        <el-result icon="success" title="解析成功！" sub-title="即将跳转到报告页面">
          <template #extra>
            <el-button type="primary" @click="goReport">查看报告</el-button>
          </template>
        </el-result>
      </div>
    </el-card>
  </div>
</template>
