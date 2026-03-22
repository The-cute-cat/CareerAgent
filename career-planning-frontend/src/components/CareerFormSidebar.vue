<script setup lang="ts">
//能力画像板块的侧边栏组件
import { 
  Document,
  DocumentAdd,
  Check,
  School,
  Tools,
  Trophy,
  DataAnalysis,
  Position
} from '@element-plus/icons-vue'


defineProps<{
  modelValue: string
  hasUploaded?: boolean
}>()


defineEmits<{
  'update:modelValue': [value: string]
  'uploadClick': []
}>()
</script>

<template>
  <div class="sidebar-container">
    <div class="sidebar-header">
      <el-icon :size="24" color="#409eff"><Document /></el-icon>
      <h3>就业能力画像</h3>
    </div>
    
    <el-menu
      :default-active="modelValue"
      class="sidebar-menu"
      v-bind="$attrs"
    >
      <el-menu-item index="1">
        <el-icon><School /></el-icon>
        <span>基本信息</span>
      </el-menu-item>
      
      <el-menu-item index="2">
        <el-icon><Tools /></el-icon>
        <span>技能与证书</span>
      </el-menu-item>
      
      <el-menu-item index="3">
        <el-icon><Trophy /></el-icon>
        <span>经历与项目</span>
      </el-menu-item>
      
      <el-menu-item index="4">
        <el-icon><DataAnalysis /></el-icon>
        <span>素质测评</span>
      </el-menu-item>
      
      <el-menu-item index="5">
        <el-icon><Position /></el-icon>
        <span>职业意向</span>
      </el-menu-item>
    </el-menu>
    
    <div class="resume-section">
      <el-button 
        type="primary" 
        plain 
        @click="$emit('uploadClick')"
        :icon="DocumentAdd"
        block
      >
        {{ hasUploaded ? '重新上传' : '上传简历' }}
      </el-button>
      <el-tag v-if="hasUploaded" type="success" size="small">
        <el-icon><Check /></el-icon>
        已上传
      </el-tag>
    </div>
  </div>
</template>


<style scoped>
.sidebar-container {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  padding: 20px 0;
  height: 100%;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px 20px;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 20px;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #7a7e87;
}

.sidebar-menu {
  border-right: none;
}

.resume-section {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  margin-top: 20px;
}
</style>





