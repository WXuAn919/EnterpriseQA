<script setup>
import { onMounted, ref } from 'vue'

import { getMessagesApi, getSessionsApi } from '@/api/chat'

const sessions = ref([])
const messages = ref([])
const activeSessionId = ref('')

/** 加载用户历史会话。 */
async function loadSessions() {
  const response = await getSessionsApi()
  sessions.value = response.data
  if (sessions.value.length && !activeSessionId.value) {
    activeSessionId.value = sessions.value[0].id
    loadMessages()
  }
}

/** 加载当前选中会话下的问答记录。 */
async function loadMessages() {
  if (!activeSessionId.value) return
  const response = await getMessagesApi({ sessionId: activeSessionId.value })
  messages.value = response.data
}

onMounted(loadSessions)
</script>

<template>
  <section class="history-page">
    <el-card shadow="never">
      <template #header>
        <div class="history-page__header">
          <div>
            <h2>历史会话记录</h2>
            <p>查看自己在知识库中的提问与回答内容。</p>
          </div>
          <el-select v-model="activeSessionId" placeholder="请选择会话" style="width: 280px" @change="loadMessages">
            <el-option
              v-for="item in sessions"
              :key="item.id"
              :label="`${item.title}（${item.lastQuestionAt}）`"
              :value="item.id"
            />
          </el-select>
        </div>
      </template>

      <el-timeline v-if="messages.length">
        <el-timeline-item
          v-for="item in messages"
          :key="item.id"
          :timestamp="item.createdAt"
          placement="top"
        >
          <div class="timeline-card">
            <h4>问题：{{ item.question }}</h4>
            <p class="timeline-card__answer">回答：{{ item.answer }}</p>
          </div>
        </el-timeline-item>
      </el-timeline>

      <el-empty v-else description="暂无历史问答记录" />
    </el-card>
  </section>
</template>

<style scoped>
.history-page__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.history-page__header h2 {
  margin: 0;
  color: #12304c;
}

.history-page__header p {
  margin: 8px 0 0;
  color: #71829a;
}

.timeline-card {
  padding: 18px;
  border-radius: 16px;
  background: #f6f9fd;
}

.timeline-card h4,
.timeline-card__answer {
  margin: 0;
  color: #29445f;
  line-height: 1.8;
}

.timeline-card__answer {
  margin-top: 10px;
}

@media (max-width: 960px) {
  .history-page__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
