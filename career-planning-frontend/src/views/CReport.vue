<template>
  <div class="report-page">
    <div class="header-action">
      <div class="user-info">
        <h2>职业生涯规划报告</h2>
        <span class="sub-title">候选人：李明 | 学校：HX 大学 (985/211)</span>
      </div>
      <div class="header-buttons">
        <el-button class="export-btn" type="primary" @click="exportPDF">
          <el-icon><Download /></el-icon>
          导出 PDF
        </el-button>
        <el-button class="export-btn" type="success" plain @click="exportWord">
          <el-icon><Download /></el-icon>
          导出 Word
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
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

        <el-card class="mb-20 structured-card">
          <template #header>职业目标与路径规划</template>
          <div class="structured-grid">
            <section class="structured-section">
              <div class="section-title">职业目标</div>
              <div class="section-body" v-html="targetContent"></div>
            </section>
            <section class="structured-section">
              <div class="section-title">路径规划</div>
              <div class="section-body" v-html="pathContent"></div>
            </section>
          </div>
        </el-card>

        <el-card class="mb-20 structured-card">
          <template #header>行动计划（短期 / 中期）</template>
          <div class="structured-grid">
            <section class="structured-section">
              <div class="section-title">短期（1-3 个月）</div>
              <div class="section-body" v-html="shortTermContent"></div>
            </section>
            <section class="structured-section">
              <div class="section-title">中期（4-12 个月）</div>
              <div class="section-body" v-html="midTermContent"></div>
            </section>
          </div>
        </el-card>

        <el-card class="mb-20 editor-card">
          <template #header>报告在线编辑</template>
          <div class="editor-grid">
            <div class="editor-block">
              <div class="editor-label">职业目标</div>
              <div class="editor-shell">
                <EditorContent :editor="targetEditor" />
              </div>
            </div>
            <div class="editor-block">
              <div class="editor-label">路径规划</div>
              <div class="editor-shell">
                <EditorContent :editor="pathEditor" />
              </div>
            </div>
            <div class="editor-block">
              <div class="editor-label">短期行动计划</div>
              <div class="editor-shell">
                <EditorContent :editor="shortTermEditor" />
              </div>
            </div>
            <div class="editor-block">
              <div class="editor-label">中期行动计划</div>
              <div class="editor-shell">
                <EditorContent :editor="midTermEditor" />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="mb-20 radar-card">
          <template #header>能力维度雷达</template>
          <div id="radar-chart" class="radar-chart-container"></div>
        </el-card>

        <el-card class="mb-20 polish-card">
          <template #header>智能润色助手</template>
          <div class="polish-body">
            <el-select v-model="activeSection" placeholder="选择润色内容" class="polish-select">
              <el-option label="职业目标" value="target" />
              <el-option label="路径规划" value="path" />
              <el-option label="短期行动计划" value="short" />
              <el-option label="中期行动计划" value="mid" />
            </el-select>
            <div class="polish-actions">
              <el-button type="primary" @click="handlePolish">AI 润色</el-button>
              <el-button type="warning" plain @click="handleCheck">完整性检查</el-button>
            </div>
            <div class="polish-result" v-if="polishMessage">
              <div class="polish-title">润色结果</div>
              <p>{{ polishMessage }}</p>
            </div>
            <div class="polish-result" v-if="checkMessage">
              <div class="polish-title">完整性检查</div>
              <p>{{ checkMessage }}</p>
            </div>
          </div>
        </el-card>

        <el-card>
          <template #header>行动计划 (OKR)</template>
          <el-timeline>
            <el-timeline-item timestamp="第 1-3 个月" placement="top" type="primary">
              <strong>技术深耕</strong><br />
              学习 Spring Cloud 微服务架构，掌握 Redis 高级特性
            </el-timeline-item>
            <el-timeline-item timestamp="第 4-6 个月" placement="top" type="success">
              <strong>项目实战</strong><br />
              独立完成一个前后端分离完整项目，部署上线
            </el-timeline-item>
            <el-timeline-item timestamp="第 7-12 个月" placement="top" type="warning">
              <strong>职业冲刺</strong><br />
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

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import { saveAs } from 'file-saver'
import { Document, HeadingLevel, Packer, Paragraph, TextRun } from 'docx'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { Download, OfficeBuilding, Money, Star, TrendCharts } from '@element-plus/icons-vue'

let radarChartInstance: echarts.ECharts | null = null
let pathChartInstance: echarts.ECharts | null = null

const projects = ref([
  { name: '分布式电商秒杀系统', role: '核心开发', tech: 'Spring Cloud, Redis, MQ' },
  { name: '校园二手交易小程序', role: '全栈开发', tech: 'Vue, Node.js, WebSocket' },
  { name: 'XX 科技权限模块重构', role: '实习生', tech: 'Java, RBAC, JUnit' },
])

const targetEditor = useEditor({
  extensions: [StarterKit],
  content:
    '<p><strong>目标岗位：</strong>Java 后端开发工程师，争取 12 个月内完成从校招岗位到独立负责核心模块的转变。</p><p><strong>关键能力：</strong>提升分布式系统、性能优化和业务建模能力，并保持持续学习与复盘。</p>',
  onUpdate: ({ editor }) => {
    targetContent.value = editor.getHTML()
  },
})

const pathEditor = useEditor({
  extensions: [StarterKit],
  content:
    '<p><strong>阶段一：</strong>3 个月内完成微服务基础与核心中间件学习，搭建可展示的项目。</p><p><strong>阶段二：</strong>6-12 个月强化业务建模与稳定性优化能力，沉淀可复用的工程实践。</p>',
  onUpdate: ({ editor }) => {
    pathContent.value = editor.getHTML()
  },
})

const shortTermEditor = useEditor({
  extensions: [StarterKit],
  content:
    '<ul><li>补齐 Spring Cloud、Nacos、Gateway 的实践经验</li><li>完成一个可演示的电商订单项目</li><li>整理 2 篇技术总结文档</li></ul>',
  onUpdate: ({ editor }) => {
    shortTermContent.value = editor.getHTML()
  },
})

const midTermEditor = useEditor({
  extensions: [StarterKit],
  content:
    '<ul><li>进入真实业务场景参与迭代，积累高并发处理经验</li><li>深入掌握性能诊断与压测方法</li><li>参与开源或技术分享，形成个人影响力</li></ul>',
  onUpdate: ({ editor }) => {
    midTermContent.value = editor.getHTML()
  },
})

const targetContent = ref('')
const pathContent = ref('')
const shortTermContent = ref('')
const midTermContent = ref('')

const activeSection = ref<'target' | 'path' | 'short' | 'mid'>('target')
const polishMessage = ref('')
const checkMessage = ref('')

const handleResize = () => {
  radarChartInstance?.resize()
  pathChartInstance?.resize()
}

const initRadar = () => {
  const dom = document.getElementById('radar-chart')
  if (!dom) return
  radarChartInstance = echarts.getInstanceByDom(dom) || echarts.init(dom)
  radarChartInstance.setOption({
    title: { text: '能力维度评估', left: 'center', top: 10 },
    radar: {
      indicator: [
        { name: 'Java 基础', max: 100 },
        { name: '框架应用', max: 100 },
        { name: '数据库', max: 100 },
        { name: '算法逻辑', max: 100 },
        { name: '沟通协作', max: 100 },
      ],
      radius: '55%',
      center: ['50%', '55%'],
      axisName: {
        color: '#606266',
        fontSize: 12,
        fontWeight: 500,
      },
      splitArea: {
        areaStyle: {
          color: ['#f8f9fa', '#ffffff', '#f8f9fa', '#ffffff'],
        },
      },
    },
    series: [
      {
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
              fontSize: 11,
            },
          },
        ],
      },
    ],
    legend: {
      bottom: 10,
      data: ['当前能力'],
    },
  })
}

const initPath = () => {
  const dom = document.getElementById('path-chart')
  if (!dom) return
  pathChartInstance = echarts.getInstanceByDom(dom) || echarts.init(dom)
  pathChartInstance.setOption({
    title: { text: '职业成长路径预测', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['入职 0-1 年', '入职 1-3 年', '入职 3-5 年', '入职 5 年+'],
    },
    yAxis: {
      type: 'value',
      name: '能力指数',
      max: 100,
    },
    series: [
      {
        name: '预期成长',
        type: 'line',
        data: [60, 75, 90, 95],
        smooth: true,
        itemStyle: { color: '#67C23A' },
      },
      {
        name: '当前基准',
        type: 'line',
        data: [60, 60, 60, 60],
        lineStyle: { type: 'dashed' },
        itemStyle: { color: '#909399' },
      },
    ],
  })
}

const exportPDF = async () => {
  const element = document.querySelector('.report-page') as HTMLElement | null
  const btn = document.querySelector('.export-btn') as HTMLButtonElement | null
  if (!element || !btn) return

  const originalText = btn.innerText
  btn.innerText = '生成中...'
  btn.disabled = true

  try {
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
    })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')

    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = pdfWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pdfHeight

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pdfHeight
    }

    pdf.save('李明 - 职业生涯规划报告.pdf')
  } catch (err) {
    console.error('PDF 生成失败', err)
    alert('导出失败，请重试')
  } finally {
    btn.innerText = originalText
    btn.disabled = false
  }
}

const exportWord = async () => {
  const doc = new Document({
    sections: [
      {
        properties: {},
        children: [
          new Paragraph({
            text: '职业生涯规划报告',
            heading: HeadingLevel.TITLE,
          }),
          new Paragraph({
            children: [new TextRun('候选人：李明 | 学校：HX 大学 (985/211)')],
          }),
          new Paragraph({ text: '' }),
          new Paragraph({
            text: '职业目标',
            heading: HeadingLevel.HEADING_1,
          }),
          new Paragraph(targetEditor.value?.getText() || ''),
          new Paragraph({
            text: '路径规划',
            heading: HeadingLevel.HEADING_1,
          }),
          new Paragraph(pathEditor.value?.getText() || ''),
          new Paragraph({
            text: '行动计划（短期）',
            heading: HeadingLevel.HEADING_1,
          }),
          new Paragraph(shortTermEditor.value?.getText() || ''),
          new Paragraph({
            text: '行动计划（中期）',
            heading: HeadingLevel.HEADING_1,
          }),
          new Paragraph(midTermEditor.value?.getText() || ''),
          new Paragraph({ text: '' }),
          new Paragraph({
            text: '项目经历',
            heading: HeadingLevel.HEADING_1,
          }),
          ...projects.value.map(
            (item) =>
              new Paragraph({
                text: `${item.name} | ${item.role} | ${item.tech}`,
              }),
          ),
        ],
      },
    ],
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, '李明 - 职业生涯规划报告.docx')
}

const handlePolish = () => {
  checkMessage.value = ''
  const mapping = {
    target: targetEditor,
    path: pathEditor,
    short: shortTermEditor,
    mid: midTermEditor,
  }
  const editor = mapping[activeSection.value].value
  if (!editor) return

  const text = editor.getText()
  const polished = text
    .replace(/提升/g, '系统提升')
    .replace(/完成/g, '高质量完成')
    .replace(/参与/g, '深度参与')
    .replace(/学习/g, '系统学习')

  if (activeSection.value === 'short' || activeSection.value === 'mid') {
    const items = polished.split(/\n+/).filter(Boolean)
    const listHtml = items.map((item) => `<li>${item}</li>`).join('')
    editor.commands.setContent(`<ul>${listHtml}</ul>`)
  } else {
    editor.commands.setContent(`<p>${polished}</p>`)
  }
  polishMessage.value = '已完成润色，整体语气更专业、更聚焦结果导向。'
}

const handleCheck = () => {
  polishMessage.value = ''
  const content = [
    targetEditor.value?.getText() || '',
    pathEditor.value?.getText() || '',
    shortTermEditor.value?.getText() || '',
    midTermEditor.value?.getText() || '',
  ].join(' ')

  const missing = []
  if (!content.includes('目标')) missing.push('目标明确性')
  if (!content.includes('项目')) missing.push('项目或实践描述')
  if (!content.match(/\d/)) missing.push('时间周期或量化指标')
  if (!content.includes('复盘')) missing.push('复盘或沉淀说明')

  checkMessage.value =
    missing.length === 0
      ? '内容完整性良好，已覆盖目标、行动与时间安排。'
      : `建议补充：${missing.join('、')}`
}

const hydrateContent = () => {
  targetContent.value = targetEditor.value?.getHTML() || ''
  pathContent.value = pathEditor.value?.getHTML() || ''
  shortTermContent.value = shortTermEditor.value?.getHTML() || ''
  midTermContent.value = midTermEditor.value?.getHTML() || ''
}

onMounted(() => {
  initRadar()
  initPath()
  hydrateContent()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  radarChartInstance?.dispose()
  pathChartInstance?.dispose()
  targetEditor.value?.destroy()
  pathEditor.value?.destroy()
  shortTermEditor.value?.destroy()
  midTermEditor.value?.destroy()
})
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

.header-buttons {
  display: flex;
  gap: 10px;
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

.radar-card {
  overflow: visible;
}

.radar-chart-container {
  height: 380px;
  width: 100%;
}

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
  color: #409eff;
}

.salary-text {
  color: #67c23a;
  font-weight: 500;
}

.advantage-text {
  color: #67c23a;
  line-height: 1.6;
}

.improve-text {
  color: #e6a23c;
  line-height: 1.6;
}

.structured-card {
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.structured-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.structured-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 12px 14px;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.section-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.section-body :deep(p),
.section-body :deep(li) {
  margin: 0 0 6px 0;
  color: #5b6b7f;
  line-height: 1.6;
}

.editor-card {
  border: 1px dashed rgba(148, 163, 184, 0.6);
}

.editor-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.editor-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.editor-label {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.editor-shell {
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 8px;
  padding: 10px;
  min-height: 120px;
  background: #fff;
}

.editor-shell :deep(.ProseMirror) {
  min-height: 90px;
  outline: none;
  color: #4b5a6b;
  font-size: 14px;
  line-height: 1.7;
}

.editor-shell :deep(ul) {
  padding-left: 18px;
}

.editor-shell :deep(p) {
  margin: 0 0 8px 0;
}

.polish-card {
  border: 1px solid rgba(226, 232, 240, 0.9);
}

.polish-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.polish-select {
  width: 100%;
}

.polish-actions {
  display: flex;
  gap: 8px;
}

.polish-result {
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px 12px;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.polish-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

@media print {
  .export-btn,
  .polish-card,
  .editor-card {
    display: none;
  }
}
</style>
