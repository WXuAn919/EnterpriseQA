<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { askQuestionApi, getMessagesApi, getSessionsApi } from '@/api/chat'
import { getKnowledgeBaseListApi } from '@/api/knowledge'

const loading = ref(false)
const knowledgeBases = ref([])
const sessions = ref([])
const messages = ref([])
const form = reactive({
  knowledgeBaseId: '',
  question: '',
  sessionId: '',
})

/** 加载知识库下拉选项。 */
async function loadKnowledgeBases() {
  const response = await getKnowledgeBaseListApi()
  knowledgeBases.value = response.data
  if (!form.knowledgeBaseId && knowledgeBases.value.length) {
    form.knowledgeBaseId = knowledgeBases.value[0].id
  }
}

/** 拉取当前用户历史会话。 */
async function loadSessions() {
  const response = await getSessionsApi()
  sessions.value = response.data
}

/** 切换会话后加载历史消息。 */
async function loadMessages(sessionId) {
  if (!sessionId) {
    messages.value = []
    return
  }
  const response = await getMessagesApi({ sessionId })
  messages.value = response.data
}

/** 提交问题并将新消息显示在页面上。 */
async function handleAsk() {
  if (!form.knowledgeBaseId) {
    ElMessage.warning('请选择知识库')
    return
  }
  if (!form.question.trim()) {
    ElMessage.warning('请输入问题内容')
    return
  }

  loading.value = true
  try {
    const response = await askQuestionApi({
      knowledgeBaseId: form.knowledgeBaseId,
      sessionId: form.sessionId || null,
      question: form.question,
    })

    form.sessionId = response.data.sessionId
    form.question = ''
    await loadSessions()
    await loadMessages(form.sessionId)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadKnowledgeBases()
  await loadSessions()
})
</script>

<template>
  <section class="chat-page">
    <div class="chat-page__sidebar">
      <div class="chat-panel">
        <div class="chat-panel__header">
          <h3>历史会话</h3>
          <p>按最近提问时间排序</p>
        </div>
        <div class="session-list">
          <button
            v-for="session in sessions"
            :key="session.id"
            class="session-item"
            :class="{ 'session-item--active': String(form.sessionId) === String(session.id) }"
            @click="form.sessionId = session.id; loadMessages(session.id)"
          >
            <strong>{{ session.title }}</strong>
            <span>{{ session.lastQuestionAt }}</span>
          </button>
          <div v-if="!sessions.length" class="empty-text">暂无历史会话</div>
        </div>
      </div>
    </div>

    <div class="chat-page__content">
      <div class="composer-card">
        <div class="composer-card__header">
          <div>
            <p class="eyebrow">智能问答</p>
            <h2>企业知识库 RAG 问答</h2>
          </div>
          <el-select v-model="form.knowledgeBaseId" placeholder="请选择知识库" style="width: 220px">
            <el-option
              v-for="item in knowledgeBases"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </div>

        <el-input
          v-model="form.question"
          :rows="4"
          placeholder="请输入你的问题，例如：公司办公时间是什么？"
          type="textarea"
        />
        <div class="composer-card__footer">
          <span>模型：qwen3:4b，向量库：Chroma</span>
          <el-button type="primary" :loading="loading" @click="handleAsk">提交问题</el-button>
        </div>
      </div>

      <div class="message-list">
        <article v-for="message in messages" :key="message.id" class="message-card">
          <div class="bubble bubble--question">
            <h4>用户问题</h4>
            <p>{{ message.question }}</p>
          </div>

          <div class="bubble bubble--answer">
            <div class="bubble__top">
              <h4>知识库回答</h4>
              <span>{{ message.elapsedMs }} ms</span>
            </div>
            <p>{{ message.answer }}</p>

            <div v-if="message.sources?.length" class="source-box">
              <h5>命中来源</h5>
              <div v-for="(source, index) in message.sources" :key="index" class="source-item">
                <strong>{{ source.documentName }}</strong>
                <p>{{ source.excerpt }}</p>
              </div>
            </div>
          </div>
        </article>

        <div v-if="!messages.length" class="empty-board">
          <h3>开始你的第一轮问答</h3>
          <p>系统会基于知识库检索片段进行回答，并展示引用来源。</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.chat-page {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
}

.chat-panel,
.composer-card,
.message-card,
.empty-board {
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 20px 48px rgba(35, 72, 118, 0.08);
}

.chat-panel {
  padding: 20px;
}

.chat-panel__header h3,
.composer-card__header h2,
.empty-board h3 {
  margin: 0;
  color: #12304c;
}

.chat-panel__header p,
.empty-board p,
.eyebrow {
  color: #71829a;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1.2px;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 18px;
}

.session-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: none;
  border-radius: 16px;
  padding: 14px;
  background: #f4f8fd;
  cursor: pointer;
  text-align: left;
}

.session-item strong {
  color: #193553;
}

.session-item span {
  color: #7d8fa8;
  font-size: 12px;
}

.session-item--active {
  background: linear-gradient(135deg, #dbeafe, #eef6ff);
  outline: 1px solid #8fbcff;
}

.composer-card {
  padding: 24px;
}

.composer-card__header,
.composer-card__footer,
.bubble__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.composer-card__footer {
  margin-top: 14px;
  color: #6e8198;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 20px;
}

.message-card {
  padding: 22px;
}

.bubble h4,
.source-box h5 {
  margin: 0 0 10px;
  color: #12304c;
}

.bubble p,
.source-item p {
  margin: 0;
  color: #395168;
  line-height: 1.8;
}

.bubble--question {
  padding: 16px;
  border-radius: 16px;
  background: #f6f9fd;
}

.bubble--answer {
  margin-top: 16px;
  padding: 18px;
  border-radius: 16px;
  background: linear-gradient(145deg, #f9fbff, #edf5ff);
}

.bubble__top span {
  color: #7e90a8;
  font-size: 12px;
}

.source-box {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed rgba(79, 110, 150, 0.2);
}

.source-item + .source-item {
  margin-top: 14px;
}

.empty-board {
  padding: 42px;
  text-align: center;
}

.empty-text {
  color: #7d8fa8;
  text-align: center;
  padding: 24px 0;
}

@media (max-width: 1100px) {
  .chat-page {
    grid-template-columns: 1fr;
  }
}
</style>
