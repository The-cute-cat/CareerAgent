<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import { Download, OfficeBuilding, Money, Star, TrendCharts } from '@element-plus/icons-vue'

let radarChartInstance: echarts.ECharts | null = null
let pathChartInstance: echarts.ECharts | null = null

// 初始化图表
onMounted(() => {
  initRadar()
  initPath()
  // 监听窗口大小变化，自适应图表
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (radarChartInstance) radarChartInstance.dispose()
  if (pathChartInstance) pathChartInstance.dispose()
})

const handleResize = () => {
  if (radarChartInstance) radarChartInstance.resize()
  if (pathChartInstance) pathChartInstance.resize()
}

const initRadar = () => {
  const dom = document.getElementById('radar-chart')
  if (!dom) return
  // 检查是否已有实例，避免重复初始化
  radarChartInstance = echarts.getInstanceByDom(dom) || echarts.init(dom)
  radarChartInstance.setOption({
    title: { text: '能力维度评估', left: 'center', top: 10 },
    radar: {
      indicator: [
        { name: 'Java 基础', max: 100 },
        { name: '框架应用', max: 100 },
        { name: '数据库', max: 100 },
        { name: '算法逻辑', max: 100 },
        { name: '沟通协作', max: 100 }
      ],
      radius: '55%',
      center: ['50%', '55%'],
      axisName: {
        color: '#606266',
        fontSize: 12,
        fontWeight: 500
      },
      splitArea: {
        areaStyle: {
          color: ['#f8f9fa', '#ffffff', '#f8f9fa', '#ffffff']
        }
      }
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: [85, 80, 85, 90, 75],
          name: '当前能力',
          itemStyle: { color: '#409EFF' },
          areaStyle: { opacity: 0.3 },
          label: {
            show: true,
            formatter: '{c}',
            color: '#409EFF',
            fontSize: 11
          }
        }
      ]
    }],
    legend: {
      bottom: 10,
      data: ['当前能力']
    }
  })
}

const initPath = () => {
  const dom = document.getElementById('path-chart')
  if (!dom) return
  // 检查是否已有实例，避免重复初始化
  pathChartInstance = echarts.getInstanceByDom(dom) || echarts.init(dom)
  pathChartInstance.setOption({
    title: { text: '职业成长路径预测', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['入职 0-1 年', '入职 1-3 年', '入职 3-5 年', '入职 5 年 +']
    },
    yAxis: {
      type: 'value',
      name: '能力指数',
      max: 100
    },
    series: [
      {
        name: '预期成长',
        type: 'line',
        data: [60, 75, 90, 95],
        smooth: true,
        itemStyle: { color: '#67C23A' }
      },
      {
        name: '当前基准',
        type: 'line',
        data: [60, 60, 60, 60],
        lineStyle: { type: 'dashed' },
        itemStyle: { color: '#909399' }
      }
    ]
  })
}

// 导出 PDF 功能
const exportPDF = () => {
  const element = document.querySelector('.report-page') as HTMLElement | null
  if (!element) return

  // 显示加载状态
  const btn = document.querySelector('.export-btn') as HTMLButtonElement | null
  if (!btn) return
  const originalText = btn.innerText
  btn.innerText = '生成中...'
  btn.disabled = true

  html2canvas(element, {
    scale: 2, // 提高清晰度
    useCORS: true,
    backgroundColor: '#ffffff'
  }).then(canvas => {
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')

    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = pdfWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    // 如果内容超过一页，简单处理（实际生产可能需要分页逻辑）
    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pdfHeight

    // 如果有第二页
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pdfHeight
    }

    pdf.save('李明 - 职业生涯规划报告.pdf')

    // 恢复按钮状态
    btn.innerText = originalText
    btn.disabled = false
  }).catch(err => {
    console.error('PDF 生成失败', err)
    btn.innerText = originalText
    btn.disabled = false
    alert('导出失败，请重试')
  })
}
</script>

<template>
  <div class="report-page">
    <div class="header-action">
      <div class="user-info">
        <h2>职业生涯规划报告</h2>
        <span class="sub-title">候选人：李明 | 学校：XX 大学 (985/211)</span>
      </div>
      <el-button class="export-btn" type="success" @click="exportPDF">
        <el-icon><Download /> </el-icon>
        导出 PDF
      </el-button>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：基本信息 & 匹配度 -->
      <el-col :span="16">
        <el-card class="mb-20">
          <template #header>
            <div class="card-header">
              <span>人岗匹配分析</span>
              <el-tag type="success" effect="plain">匹配度 88%</el-tag>
            </div>
          </template>
          <el-descriptions :column="2" border class="match-descriptions">
            <el-descriptions-item>
              <template #label>
                <div class="desc-label">
                  <el-icon><OfficeBuilding /></el-icon>
                  <span>推荐岗位</span>
                </div>
              </template>
              <el-tag type="primary" effect="light" size="small">Java 后端开发工程师</el-tag>
            </el-descriptions-item>
            <el-descriptions-item>
              <template #label>
                <div class="desc-label">
                  <el-icon><Money /></el-icon>
                  <span>期望薪资</span>
                </div>
              </template>
              <span class="salary-text">面议</span>
            </el-descriptions-item>
            <el-descriptions-item>
              <template #label>
                <div class="desc-label">
                  <el-icon><Star /></el-icon>
                  <span>核心优势</span>
                </div>
              </template>
              <div class="advantage-text">
                985 院校背景，GPA 前 5%，GitHub 活跃 (1000+ commits)，算法基础扎实
              </div>
            </el-descriptions-item>
            <el-descriptions-item>
              <template #label>
                <div class="desc-label">
                  <el-icon><TrendCharts /></el-icon>
                  <span>待提升项</span>
                </div>
              </template>
              <div class="improve-text">
                缺乏高并发生产环境经验，大型分布式系统实战较少
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="mb-20">
          <template #header>发展路径建议</template>
          <div id="path-chart" style="height: 300px;"></div>
        </el-card>
        
        <el-card class="mb-20">
          <template #header>核心项目经历</template>
          <el-table :data="projects" style="width: 100%" size="small">
            <el-table-column prop="name" label="项目名称" />
            <el-table-column prop="role" label="角色" width="100" />
            <el-table-column prop="tech" label="关键技术" />
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：能力雷达图 & 行动计划 -->
      <el-col :span="8">
        <el-card class="mb-20 radar-card">
          <template #header>能力维度雷达</template>
          <div id="radar-chart" class="radar-chart-container"></div>
        </el-card>
        
        <el-card>
          <template #header>行动计划 (OKR)</template>
          <el-timeline>
            <el-timeline-item timestamp="第 1-3 月" placement="top" type="primary">
              <strong>技术深化</strong><br/>
              学习 Spring Cloud 微服务架构，掌握 Redis 高级特性
            </el-timeline-item>
            <el-timeline-item timestamp="第 4-6 月" placement="top" type="success">
              <strong>项目实战</strong><br/>
              独立完成一个前后端分离完整项目，部署上线
            </el-timeline-item>
            <el-timeline-item timestamp="第 7-12 月" placement="top" type="warning">
              <strong>职业冲刺</strong><br/>
              寻找大厂实习机会，参与开源社区贡献
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
    
    <div class="footer-note">
      <p>注：本报告基于简历内容及行业大数据模型生成，仅供参考。</p>
    </div>
  </div>
</template>

<script lang="ts">
// 补充项目数据
export default {
  data() {
    return {
      projects: [
        { name: '分布式电商秒杀系统', role: '核心开发', tech: 'Spring Cloud, Redis, MQ' },
        { name: '校园二手交易小程序', role: '全栈开发', tech: 'Vue, Node.js, WebSocket' },
        { name: 'XX 科技权限模块重构', role: '实习生', tech: 'Java, RBAC, JUnit' }
      ]
    }
  }
}
</script>

<style scoped>
.report-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.header-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}


.user-info h2 {
  margin: 0 0 5px 0;
  color: #303133;
}

.sub-title {
  color: #909399;
  font-size: 14px;
}

.mb-20 {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-note {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin-top: 20px;
}

/* 雷达图容器样式 */
.radar-card {
  overflow: visible;
}

.radar-chart-container {
  height: 380px;
  width: 100%;
}

/* 人岗匹配分析 - Label 样式 */
.match-descriptions :deep(.el-descriptions__label) {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.desc-label {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.desc-label .el-icon {
  font-size: 14px;
  color: #409EFF;
}

.salary-text {
  color: #67C23A;
  font-weight: 500;
}

.advantage-text {
  color: #67C23A;
  line-height: 1.6;
}

.improve-text {
  color: #E6A23C;
  line-height: 1.6;
}

/* PDF 导出时隐藏按钮 */
@media print {
  .export-btn {
    display: none;
  }
}
</style>
