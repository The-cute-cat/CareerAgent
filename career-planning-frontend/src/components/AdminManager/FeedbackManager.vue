<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getFeedbackListService, updateFeedbackService, type Feedback } from '@/api/feedback'

const feedbackList = ref<Feedback[]>([])
const loading = ref(false)
const total = ref(0)
const queryParams = ref({
  pageNum: 1,
  pageSize: 10,
  status: undefined as number | undefined
})

const statusOptions = [
  { label: '全部', value: undefined },
  { label: '待处理', value: 0 },
  { label: '已回复', value: 1 },
  { label: '已关闭', value: 2 }
]

const getStatusType = (status?: number) => {
  switch (status) {
    case 0: return 'warning'
    case 1: return 'success'
    case 2: return 'info'
    default: return 'info'
  }
}

const getStatusLabel = (status?: number) => {
  const option = statusOptions.find(o => o.value === status)
  return option ? option.label : '未知'
}

const fetchFeedbackList = async () => {
  loading.value = true
  try {
    const res = await getFeedbackListService(queryParams.value.pageNum, queryParams.value.pageSize, queryParams.value.status)
    if (res.data.code === 200) {
      if (Array.isArray(res.data.data)) {
         feedbackList.value = res.data.data
         total.value = res.data.data.length // 简单处理
      } else {
         feedbackList.value = res.data.data.list || []
         total.value = res.data.data.total || 0
      }
    }
  } catch (error) {
    ElMessage.error('获取反馈列表失败')
  } finally {
    loading.value = false
  }
}

// 回复相关
const replyDialogVisible = ref(false)
const currentFeedback = ref<Feedback | null>(null)
const replyContent = ref('')
const submitting = ref(false)

const handleReply = (row: Feedback) => {
  currentFeedback.value = { ...row }
  replyContent.value = row.response || ''
  replyDialogVisible.value = true
}

const submitReply = async () => {
  if (!currentFeedback.value || !replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }

  submitting.value = true
  try {
    const updateData: Feedback = {
      ...currentFeedback.value,
      response: replyContent.value,
      status: 1 // 设置为已回复
    }
    const res = await updateFeedbackService(updateData)
    if (res.data.code === 200) {
      ElMessage.success('回复成功')
      replyDialogVisible.value = false
      fetchFeedbackList()
    }
  } catch (error) {
    ElMessage.error('回复失败')
  } finally {
    submitting.value = false
  }
}

const handlePageChange = (page: number) => {
  queryParams.value.pageNum = page
  fetchFeedbackList()
}

onMounted(() => {
  fetchFeedbackList()
})
</script>

<template>
  <div class="feedback-manager">
    <div class="filter-bar">
      <el-radio-group v-model="queryParams.status" @change="fetchFeedbackList">
        <el-radio-button v-for="item in statusOptions" :key="item.value" :label="item.value">
          {{ item.label }}
        </el-radio-button>
      </el-radio-group>
      <el-button type="primary" plain @click="fetchFeedbackList">刷新</el-button>
    </div>

    <el-table :data="feedbackList" v-loading="loading" border style="width: 100%" class="admin-table">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="userId" label="用户ID" width="100" />
      <el-table-column prop="type" label="类型" width="120" />
      <el-table-column prop="content" label="反馈内容" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="提交时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" :type="row.status === 0 ? 'primary' : 'default'" @click="handleReply(row)">
            {{ row.status === 0 ? '回复' : '修改回复' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="queryParams.pageNum"
        :page-size="queryParams.pageSize"
        layout="total, prev, pager, next"
        :total="total"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 回复弹窗 -->
    <el-dialog v-model="replyDialogVisible" title="反馈回复" width="500px">
      <div v-if="currentFeedback" class="feedback-detail">
        <div class="detail-item">
          <strong>反馈类型：</strong> {{ currentFeedback.type }}
        </div>
        <div class="detail-item">
          <strong>反馈内容：</strong>
          <p class="content-text">{{ currentFeedback.content }}</p>
        </div>
        <el-divider />
        <el-form label-position="top">
          <el-form-item label="管理员回复">
            <el-input
              v-model="replyContent"
              type="textarea"
              :rows="5"
              placeholder="请输入回复内容..."
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="replyDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitReply">提交回复</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.feedback-manager {
  padding: 20px;
}

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.feedback-detail {
  .detail-item {
    margin-bottom: 12px;
    font-size: 14px;
    strong {
      color: #334155;
    }
  }
  .content-text {
    margin-top: 8px;
    padding: 12px;
    background: #f8fafc;
    border-radius: 8px;
    color: #64748b;
    white-space: pre-wrap;
  }
}
</style>
