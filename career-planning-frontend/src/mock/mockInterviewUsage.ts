// 使用说明：将以下内容替换到 AIInterviewAvatar.vue 中对应位置

// ============================================
// 1. 导入模拟数据（在 script setup 顶部添加）
// ============================================
/*
import {
  mockInterviewResult,
  mockChatHistory,
  mockInterviewStats
} from '@/mock/mockInterviewData'
*/

// ============================================
// 2. 替换面试结果数据定义部分
// ============================================
/*
// 面试结果数据 - 使用模拟数据
const interviewResult = ref<InterviewResult>(mockInterviewResult)

// 消息列表 - 使用模拟聊天记录
const messages = ref<ChatMessage[]>(mockChatHistory)

// 面试统计数据 - 使用模拟数据
const interviewStats = ref(mockInterviewStats)
*/

// ============================================
// 3. 快速测试面试结果页面的方法
// ============================================
// 在组件挂载后直接跳转到结果页面：
/*
onMounted(() => {
  // 直接显示结果页面（用于测试）
  selectedPosition.value = positions.value[0] // 选择前端开发岗位
  currentStep.value = InterviewStep.RESULT
  nextTick(() => {
    initRadarChart()
    initBarChart()
  })
})
*/

// 或者在面试结束时自动调用 viewResults()：
/*
// 结束面试方法
const endInterview = () => {
  currentTime.value = 900 // 模拟面试进行了15分钟
  currentStep.value = InterviewStep.FINISHED
  stopTimer()
  // 1秒后自动显示结果
  setTimeout(() => {
    viewResults()
  }, 1000)
}
*/

// ============================================
// 4. 不同分数段的测试数据
// ============================================

// 优秀（90-100分）
export const excellentResult = {
  overallScore: 92,
  dimensionScores: { technical: 95, communication: 88, logic: 94, expression: 90, attitude: 96 },
  weaknessAnalysis: [
    { area: '前沿技术跟进', severity: 'low', suggestion: '保持对新技术的关注，如Serverless、WebAssembly等' }
  ]
}

// 良好（80-89分）
export const goodResult = {
  overallScore: 82,
  dimensionScores: { technical: 85, communication: 78, logic: 88, expression: 80, attitude: 92 },
  weaknessAnalysis: [
    { area: '性能优化', severity: 'medium', suggestion: '深入学习性能优化技术' },
    { area: '工程化', severity: 'medium', suggestion: '加强工程化实践' }
  ]
}

// 及格（70-79分）
export const passResult = {
  overallScore: 74,
  dimensionScores: { technical: 75, communication: 72, logic: 78, expression: 70, attitude: 80 },
  weaknessAnalysis: [
    { area: '基础知识', severity: 'high', suggestion: '系统学习JavaScript和框架原理' },
    { area: '项目经验', severity: 'high', suggestion: '多做实际项目练习' },
    { area: '表达能力', severity: 'medium', suggestion: '多练习技术分享和表达' }
  ]
}

// 待提升（60-69分）
export const needImproveResult = {
  overallScore: 65,
  dimensionScores: { technical: 62, communication: 68, logic: 70, expression: 60, attitude: 75 },
  weaknessAnalysis: [
    { area: '技术基础薄弱', severity: 'high', suggestion: '从基础开始系统学习前端知识' },
    { area: '缺乏实战经验', severity: 'high', suggestion: '通过实际项目积累开发经验' },
    { area: '沟通不流畅', severity: 'medium', suggestion: '练习结构化表达' }
  ]
}

// ============================================
// 5. 完整的测试入口
// ============================================
// 在模板中添加测试按钮：
/*
<!-- 开发测试用：快速查看结果 -->
<div class="dev-test-actions" style="position: fixed; bottom: 20px; right: 20px; z-index: 999;">
  <el-button type="danger" @click="showMockResult('excellent')">优秀</el-button>
  <el-button type="warning" @click="showMockResult('good')">良好</el-button>
  <el-button type="info" @click="showMockResult('pass')">及格</el-button>
  <el-button @click="showMockResult('needImprove')">待提升</el-button>
</div>
*/

// 添加测试方法：
/*
const showMockResult = (level: string) => {
  const resultMap = {
    excellent: excellentResult,
    good: goodResult,
    pass: passResult,
    needImprove: needImproveResult
  }
  const selectedResult = resultMap[level]
  
  // 合并模拟数据
  interviewResult.value = {
    ...mockInterviewResult,
    ...selectedResult
  }
  
  selectedPosition.value = positions.value[0]
  selectedType.value = 'technical'
  selectedDifficulty.value = 'medium'
  currentStep.value = InterviewStep.RESULT
  
  nextTick(() => {
    initRadarChart()
    initBarChart()
  })
}
*/
