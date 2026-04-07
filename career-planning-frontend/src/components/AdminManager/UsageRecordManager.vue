<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsageRecordsService, type UsageRecord } from '@/api/admin/usage'

const recordList = ref<UsageRecord[]>([])
const loading = ref(false)
const total = ref(0)
const queryParams = ref({
  pageNum: 1,
  pageSize: 20,
  userId: undefined as number | undefined
})

const fetchRecords = async () => {
  loading.value = true
  try {
    const res = await getUsageRecordsService(queryParams.value.pageNum, queryParams.value.pageSize, queryParams.value.userId)
    if (res.data.code === 200) {
      recordList.value = res.data.data.list || []
      total.value = res.data.data.total || 0
    }
  } catch (error) {
    ElMessage.error('获取使用记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  queryParams.value.pageNum = 1
  fetchRecords()
}

const handlePageChange = (page: number) => {
  queryParams.value.pageNum = page
  fetchRecords()
}

onMounted(() => {
  fetchRecords()
})
</script>

<template>
  <div class="usage-manager">
    <div class="filter-bar">
      <div class="search-box">
        <el-input
          v-model.number="queryParams.userId"
          placeholder="搜索用户ID"
          style="width: 200px"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>
      <el-button type="primary" plain @click="fetchRecords">刷新</el-button>
    </div>

    <el-table :data="recordList" v-loading="loading" border style="width: 100%" class="admin-table">
        <el-table-column prop="id" label="记录ID" width="100" />
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="actionName" label="操作内容" min-width="150" />
        <el-table-column prop="pointsConsumed" label="消耗积分" width="120">
            <template #default="{ row }">
                <span class="points-text">-{{ row.pointsConsumed }}</span>
            </template>
        </el-table-column>
        <el-table-column prop="createTime" label="操作时间" width="200" />
        <el-table-column prop="details" label="详细信息" show-overflow-tooltip />
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
  </div>
</template>

<style scoped lang="scss">
.usage-manager {
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

.points-text {
  color: #f59e0b;
  font-weight: bold;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
