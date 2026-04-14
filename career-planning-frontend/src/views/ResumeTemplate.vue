<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  DocumentCopy,
  View,
  Download,
  MagicStick,
  ArrowRight,
  Edit
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

const templates = ref([
  {
    id: 1,
    name: '极简极客风',
    type: '适合研发/后端',
    // preview: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    preview: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    tag: '热门',
    color: '#409eff'
  },
  {
    id: 2,
    name: '专业商务版',
    type: '适合管理/运营',
    preview: 'https://cube.elemecdn.com/6/94/4d3ea53c084bad6931a56d5158a48jpeg.jpeg',
    tag: '经典',
    color: '#67c23a'
  },
  {
    id: 3,
    name: '创意视觉版',
    type: '适合设计/产品',
    preview: 'https://cube.elemecdn.com/9/bb/e27858e973f5d7d3904835f46abbdjpeg.jpeg',
    tag: '新趋势',
    color: '#e6a23c'
  }
])

const handleUse = (name: string) => {
  ElMessage.success(`开始生成「${name}」面试简历...`)
}

const goToResumeEditor = () => {
  router.push('/resume-editor')
}
</script>

<template>
  <div class="resume-template-container">
    <div class="header-section premium-glass">
      <div class="header-content">
        <el-icon class="title-icon"><MagicStick /></el-icon>
        <div class="title-text">
          <h1>简历模板生成</h1>
          <p>基于你的“能力画像”，精选多款由资深猎头推荐的职场黄金模板</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button type="primary" round class="batch-btn">
          一键同步能力画像 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
        <el-button type="success" round class="editor-btn" :icon="Edit" @click="goToResumeEditor">
          编辑简历
        </el-button>
      </div>
    </div>

    <div class="template-grid">
      <div v-for="item in templates" :key="item.id" class="template-card premium-glass">
        <div class="card-badge" :style="{ background: item.color }">{{ item.tag }}</div>
        
        <div class="preview-area">
          <img :src="item.preview" :alt="item.name" />
          <div class="preview-overlay">
            <el-button color="#fff" circle :icon="View" title="预览" />
            <el-button color="#fff" circle :icon="Download" title="下载" />
          </div>
        </div>

        <div class="card-footer">
          <div class="footer-info">
            <h3>{{ item.name }}</h3>
            <span>{{ item.type }}</span>
          </div>
          <el-button 
            type="primary" 
            plain 
            round 
            :icon="DocumentCopy"
            @click="handleUse(item.name)"
          >
            使用该模板
          </el-button>
        </div>
      </div>
    </div>

    <div class="notice-strip premium-glass">
      <div class="notice-icon"><el-icon><MagicStick /></el-icon></div>
      <p><strong>AI 提示：</strong> 简历内容将自动抓取自你在 <strong>“能力画像-我的简历”</strong> 中录入的最新进度和核心技能数据。</p>
    </div>
  </div>
</template>

<style scoped>
.resume-template-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px;
}

.premium-glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
}

.header-section {
  padding: 32px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon {
  font-size: 36px;
  color: #409eff;
  background: rgba(64, 158, 255, 0.1);
  padding: 12px;
  border-radius: 16px;
}

.title-text h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
  color: #1a2a47;
}

.title-text p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.template-card {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 12px;
}

.template-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.5);
}

.card-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 2;
  padding: 4px 12px;
  border-radius: 999px;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.preview-area {
  height: 420px;
  background: #f8fafc;
  border-radius: 14px;
  overflow: hidden;
  position: relative;
}

.preview-area img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  opacity: 0;
  transition: opacity 0.3s;
}

.template-card:hover .preview-overlay {
  opacity: 1;
}

.card-footer {
  padding: 16px 8px 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info h3 {
  margin: 0;
  font-size: 16px;
  color: #1a2a47;
}

.footer-info span {
  font-size: 12px;
  color: #94a3b8;
}

.notice-strip {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-left: 4px solid #409eff;
}

.notice-icon {
  font-size: 20px;
  color: #409eff;
}

.notice-strip p {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    gap: 20px;
    padding: 24px;
    align-items: flex-start;
  }
  .header-actions {
    width: 100%;
    flex-direction: column;
  }
  .batch-btn, .editor-btn { width: 100%; }
}

.editor-btn {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}
</style>
