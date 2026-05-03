<script setup>
import { onMounted, ref } from 'vue'

import { getUsersApi } from '@/api/admin'

const loading = ref(false)
const users = ref([])

/** 获取用户列表数据。 */
async function loadUsers() {
  loading.value = true
  try {
    const response = await getUsersApi()
    users.value = response.data
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)
</script>

<template>
  <section class="table-page">
    <div class="table-page__header">
      <div>
        <h2>用户管理</h2>
        <p>查看系统中的管理员与普通用户账号。</p>
      </div>
      <el-button type="primary" plain @click="loadUsers">刷新列表</el-button>
    </div>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="users" border>
        <el-table-column prop="id" label="编号" width="90" />
        <el-table-column prop="username" label="用户名" min-width="130" />
        <el-table-column prop="realName" label="姓名" min-width="120" />
        <el-table-column prop="role" label="角色" min-width="110">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" min-width="180" />
      </el-table>
    </el-card>
  </section>
</template>

<style scoped>
.table-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.table-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.table-page__header h2 {
  margin: 0;
  color: #12304c;
}

.table-page__header p {
  margin: 8px 0 0;
  color: #708199;
}
</style>
