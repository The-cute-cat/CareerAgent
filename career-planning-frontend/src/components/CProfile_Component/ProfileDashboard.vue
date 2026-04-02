<script setup lang="ts">
import { ref } from 'vue'
import { Plus, ArrowRight, VideoPlay } from '@element-plus/icons-vue'

const banners = [
  { id: 1, title: '探索热门成长路径', image: 'https://picsum.photos/800/300?random=1' }
]

const props = defineProps({
  userInfo: {
    type: Object,
    default: () => ({ name: '职悟用户', avatar: '' })
  }
})

const jobFilters = ['全部', '感兴趣', '已投递', '面试中', 'Offer']
const activeJobFilter = ref('全部')

const pathFilters = ['全部', '我参与的', '我创建的']
const activePathFilter = ref('全部')

const recommendedPaths = [
  { id: 1, title: '物业管理系统学习路...', phases: 10, skills: 30, icon: '🏢' },
  { id: 2, title: 'AI 产品设计学习路径', phases: 5, skills: 15, icon: '🎨' },
  { id: 3, title: '产品设计学习路径', phases: 5, skills: 15, icon: '🎨' }
]
</script>

<template>
  <div class="profile-dashboard">
    <!-- User Greeting -->
    <div class="user-greeting">
      <div class="greeting-text">
        <h1>你好，{{ userInfo.name }} !</h1>
        <p>你的职业成长计划已步入正轨</p>
      </div>
      <div class="progress-ring">
        <el-progress type="circle" :percentage="85" :width="48" :stroke-width="4" />
      </div>
    </div>

    <!-- Top Banner -->
    <div class="banner-container">
      <el-carousel trigger="click" height="160px" arrow="never" class="dashboard-carousel">
        <el-carousel-item v-for="item in banners" :key="item.id">
          <div class="banner-card" :style="{ backgroundImage: `url(${item.image})` }">
            <div class="banner-overlay">
              <h2>{{ item.title }}</h2>
              <div class="carousel-dots">
                <span class="dot active"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>

    <!-- Section: My Target Jobs -->
    <div class="dashboard-section">
      <div class="section-header">
        <h3>我的目标职位</h3>
        <span class="more-link blue">发现更多职位 <el-icon><ArrowRight /></el-icon></span>
      </div>
      <div class="filter-chips">
        <span
          v-for="f in jobFilters"
          :key="f"
          class="chip"
          :class="{ active: activeJobFilter === f }"
          @click="activeJobFilter = f"
        >
          {{ f }}
        </span>
      </div>
      <div class="card-grid">
        <div class="action-card">
          <div class="icon-box"><el-icon><Plus /></el-icon></div>
          <h4>添加目标职位</h4>
          <p>粘贴 JD 或手动创建</p>
        </div>
        <div class="action-card">
          <div class="icon-box"><el-icon><Plus /></el-icon></div>
          <h4>AI职业规划</h4>
          <p>量身定制成长路径</p>
        </div>
      </div>
    </div>

    <!-- Section: My Learning Paths -->
    <div class="dashboard-section">
      <div class="section-header">
        <h3>我的学习路径</h3>
      </div>
      <div class="filter-chips">
        <span
          v-for="f in pathFilters"
          :key="f"
          class="chip"
          :class="{ active: activePathFilter === f }"
          @click="activePathFilter = f"
        >
          {{ f }}
        </span>
      </div>
      <div class="card-grid single">
        <div class="action-card">
          <div class="icon-box"><el-icon><Plus /></el-icon></div>
          <h4>创建学习路径</h4>
          <p>定制你的学习计划</p>
        </div>
      </div>
    </div>

    <!-- Section: Recommended paths -->
    <div class="dashboard-section">
      <div class="section-header">
        <h3>推荐学习路径 <span class="count-badge">8</span></h3>
        <span class="more-link">更多 <el-icon><ArrowRight /></el-icon></span>
      </div>
      <div class="horizontal-scroll">
        <div v-for="path in recommendedPaths" :key="path.id" class="path-card">
          <div class="path-icon">{{ path.icon }}</div>
          <div class="path-info">
            <h4>{{ path.title }}</h4>
            <div class="path-meta">{{ path.phases }}个阶段 · {{ path.skills }}个核心技能</div>
          </div>
          <el-button circle size="small" class="go-btn">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.profile-dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.user-greeting {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 4px;
  
  .greeting-text {
    h1 {
      font-size: 24px;
      font-weight: 900;
      color: #0f172a;
      margin: 0;
    }
    p {
      font-size: 14px;
      color: #64748b;
      margin: 4px 0 0;
    }
  }
}

.banner-container {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.banner-card {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
}

.banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 40%, rgba(0, 0, 0, 0.4));
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.banner-overlay h2 {
  color: #fff;
  font-size: 24px;
  font-weight: 900;
  margin: 0 0 12px;
  letter-spacing: 1px;
}

.carousel-dots {
  display: flex;
  gap: 6px;
  
  .dot {
    width: 16px;
    height: 4px;
    border-radius: 2px;
    background: rgba(255, 255, 255, 0.4);
    
    &.active {
      width: 24px;
      background: #fff;
    }
  }
}

.dashboard-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  h3 {
    font-size: 18px;
    font-weight: 800;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .count-badge {
    background: #eff6ff;
    color: #3b82f6;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 99px;
  }
}

.more-link {
  font-size: 14px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  
  &.blue {
    color: #1e62c5;
    font-weight: 600;
  }
}

.filter-chips {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
  &::-webkit-scrollbar { display: none; }
}

.chip {
  padding: 8px 16px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e2e8f0;
  font-size: 14px;
  color: #475569;
  cursor: pointer;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
  
  &.active {
    background: #e0eaff;
    border-color: #1e62c5;
    color: #1e62c5;
    font-weight: 700;
  }
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  
  &.single {
    grid-template-columns: 1fr 1fr; // Same for alignment
  }
}

.action-card {
  padding: 24px;
  border-radius: 20px;
  background: #fff;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
  }
  
  .icon-box {
    width: 48px;
    height: 48px;
    background: #5fa4f8;
    color: #fff;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 800;
    color: #1e293b;
  }
  
  p {
    margin: 0;
    font-size: 12px;
    color: #94a3b8;
  }
}

.horizontal-scroll {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding: 4px;
  scrollbar-width: none;
  &::-webkit-scrollbar { display: none; }
}

.path-card {
  min-width: 180px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  
  .path-icon {
    font-size: 32px;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 800;
    line-height: 1.4;
    color: #1e293b;
    height: 40px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .path-meta {
    font-size: 11px;
    color: #94a3b8;
  }
  
  .go-btn {
    position: absolute;
    top: 16px;
    right: 16px;
    background: #f1f5f9;
    border: none;
    color: #64748b;
  }
}
</style>