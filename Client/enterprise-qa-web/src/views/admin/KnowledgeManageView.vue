<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { createKnowledgeBaseApi, getKnowledgeBaseListApi } from '@/api/knowledge'

const loading = ref(false)
const list = ref([])
const form = reactive({
  name: '',
  description: '',
})

/** 加载知识库列表。 */
async function loadKnowledgeBases() {
  loading.value = true
  try {
    const response = await getKnowledgeBaseListApi()
    list.value = response.data
  } finally {
    loading.value = false
  }
}

/** 创建知识库并刷新列表。 */
async function handleCreate() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }
  await createKnowledgeBaseApi(form)
  ElMessage.success('知识库创建成功')
  form.name = ''
  form.description = ''
  loadKnowledgeBases()
}

onMounted(loadKnowledgeBases)
</script>

<template>
  <section class="knowledge-page">
    <div class="knowledge-page__grid">
      <el-card shadow="never" class="form-card">
        <template #header>
          <div class="card-header">
            <h3>新建知识库</h3>
            <span>管理员用于组织不同业务领域的知识内容</span>
          </div>
        </template>

        <el-form label-position="top">
          <el-form-item label="知识库名称">
            <el-input v-model="form.name" placeholder="例如：人事制度知识库" />
          </el-form-item>
          <el-form-item label="知识库说明">
            <el-input v-model="form.description" :rows="5" placeholder="请输入知识库简介" type="textarea" />
          </el-form-item>
          <el-button type="primary" @click="handleCreate">创建知识库</el-button>
        </el-form>
      </el-card>

      <el-card shadow="never">
        <template #header>
          <div class="card-header card-header--split">
            <div>
              <h3>知识库列表</h3>
              <span>已创建的知识库可供管理员上传文档和普通用户问答</span>
            </div>
            <el-button type="primary" plain @click="loadKnowledgeBases">刷新</el-button>
          </div>
        </template>

        <el-table v-loading="loading" :data="list" border>
          <el-table-column prop="id" label="编号" width="80" />
          <el-table-column prop="name" label="名称" min-width="160" />
          <el-table-column prop="description" label="说明" min-width="240" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag type="success">{{ row.status === 'enabled' ? '启用中' : row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" min-width="180" />
        </el-table>
      </el-card>
    </div>
  </section>
</template>

<style scoped>
.knowledge-page__grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 18px;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-header h3 {
  margin: 0;
  color: #12304c;
}

.card-header span {
  color: #6f8098;
  font-size: 13px;
}

.card-header--split {
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 1100px) {
  .knowledge-page__grid {
    grid-template-columns: 1fr;
  }
}
</style>
