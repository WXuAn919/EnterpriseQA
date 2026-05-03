<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import {
  getDocumentListApi,
  getKnowledgeBaseListApi,
  reindexDocumentApi,
  uploadDocumentApi,
} from '@/api/knowledge'

const loading = ref(false)
const knowledgeBases = ref([])
const documents = ref([])
const selectedFile = ref(null)
const filters = reactive({
  knowledgeBaseId: '',
})
const uploadForm = reactive({
  title: '',
  knowledgeBaseId: '',
})

const currentKnowledgeBaseName = computed(() => {
  const target = knowledgeBases.value.find((item) => item.id === filters.knowledgeBaseId)
  return target?.name || '全部知识库'
})

/** 加载知识库下拉选项。 */
async function loadKnowledgeBases() {
  const response = await getKnowledgeBaseListApi()
  knowledgeBases.value = response.data
  if (!filters.knowledgeBaseId && knowledgeBases.value.length) {
    filters.knowledgeBaseId = knowledgeBases.value[0].id
    uploadForm.knowledgeBaseId = knowledgeBases.value[0].id
  }
}

/** 加载文档表格数据。 */
async function loadDocuments() {
  loading.value = true
  try {
    const response = await getDocumentListApi({
      knowledgeBaseId: filters.knowledgeBaseId || undefined,
    })
    documents.value = response.data
  } finally {
    loading.value = false
  }
}

/** 监听文件选择事件，仅保存待上传文件。 */
function handleFileChange(uploadFile) {
  selectedFile.value = uploadFile.raw
}

/** 移除已选择文件，避免误传旧文件。 */
function handleFileRemove() {
  selectedFile.value = null
}

/** 上传文档并自动触发切片与向量化。 */
async function handleUpload() {
  if (!uploadForm.knowledgeBaseId) {
    ElMessage.warning('请先选择所属知识库')
    return
  }
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }

  const formData = new FormData()
  formData.append('title', uploadForm.title)
  formData.append('knowledgeBaseId', uploadForm.knowledgeBaseId)
  formData.append('file', selectedFile.value)

  await uploadDocumentApi(formData)
  ElMessage.success('文档上传成功，已完成索引')
  uploadForm.title = ''
  selectedFile.value = null
  loadDocuments()
}

/** 手动重建某个文档的向量索引。 */
async function handleReindex(row) {
  await reindexDocumentApi({ documentId: row.id })
  ElMessage.success('索引重建完成')
  loadDocuments()
}

onMounted(async () => {
  await loadKnowledgeBases()
  await loadDocuments()
})
</script>

<template>
  <section class="document-page">
    <div class="document-page__grid">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <h3>上传知识文档</h3>
            <span>支持 txt、md、pdf、docx，并自动写入 Chroma 向量库</span>
          </div>
        </template>

        <el-form label-position="top">
          <el-form-item label="所属知识库">
            <el-select v-model="uploadForm.knowledgeBaseId" placeholder="请选择知识库">
              <el-option
                v-for="item in knowledgeBases"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="文档标题">
            <el-input v-model="uploadForm.title" placeholder="不填时默认使用文件名" />
          </el-form-item>
          <el-form-item label="选择文件">
            <el-upload
              :auto-upload="false"
              :limit="1"
              drag
              action="#"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
            >
              <el-icon><UploadFilled /></el-icon>
              <div class="el-upload__text">拖拽文件到此处，或点击选择文件</div>
              <template #tip>
                <div class="el-upload__tip">仅支持 txt / md / pdf / docx</div>
              </template>
            </el-upload>
          </el-form-item>
          <el-button type="primary" @click="handleUpload">上传并建立索引</el-button>
        </el-form>
      </el-card>

      <el-card shadow="never">
        <template #header>
          <div class="card-header card-header--split">
            <div>
              <h3>文档列表</h3>
              <span>当前查看：{{ currentKnowledgeBaseName }}</span>
            </div>
            <div class="toolbar">
              <el-select v-model="filters.knowledgeBaseId" clearable placeholder="筛选知识库" style="width: 180px">
                <el-option
                  v-for="item in knowledgeBases"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
              <el-button type="primary" plain @click="loadDocuments">刷新</el-button>
            </div>
          </div>
        </template>

        <el-table v-loading="loading" :data="documents" border>
          <el-table-column prop="id" label="编号" width="80" />
          <el-table-column prop="title" label="文档标题" min-width="150" />
          <el-table-column prop="originalName" label="原文件名" min-width="160" />
          <el-table-column prop="fileType" label="类型" width="100" />
          <el-table-column prop="processStatus" label="处理状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.processStatus === 'processed' ? 'success' : row.processStatus === 'failed' ? 'danger' : 'warning'">
                {{ row.processStatus }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="chunkCount" label="切片数" width="110" />
          <el-table-column prop="createdAt" label="创建时间" min-width="180" />
          <el-table-column label="操作" width="130" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleReindex(row)">重建索引</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </section>
</template>

<style scoped>
.document-page__grid {
  display: grid;
  grid-template-columns: 380px 1fr;
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

.card-header--split,
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-header--split {
  justify-content: space-between;
}

@media (max-width: 1200px) {
  .document-page__grid {
    grid-template-columns: 1fr;
  }

  .card-header--split {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
