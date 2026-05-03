<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const menus = computed(() => {
  const commonMenus = [
    { path: '/chat', label: '智能问答' },
    { path: '/history', label: '历史会话' },
  ]

  if (authStore.userInfo?.role === 'admin') {
    return [
      { path: '/admin/home', label: '后台首页' },
      { path: '/admin/users', label: '用户管理' },
      { path: '/admin/knowledge', label: '知识库管理' },
      { path: '/admin/documents', label: '文档处理' },
      ...commonMenus,
    ]
  }

  return commonMenus
})

/** 退出登录并返回登录页。 */
function handleLogout() {
  authStore.logout()
  ElMessage.success('已安全退出登录')
  router.replace('/login')
}
</script>

<template>
  <div class="admin-layout">
    <aside class="admin-layout__aside">
      <div>
        <div class="brand-block">
          <p class="brand-block__eyebrow">LangChain + Ollama</p>
          <h1>企业知识库问答平台</h1>
        </div>

        <nav class="menu-list">
          <button
            v-for="menu in menus"
            :key="menu.path"
            class="menu-item"
            :class="{ 'menu-item--active': route.path === menu.path }"
            @click="router.push(menu.path)"
          >
            {{ menu.label }}
          </button>
        </nav>
      </div>

      <div class="user-card">
        <p class="user-card__name">{{ authStore.userInfo?.realName || '未登录用户' }}</p>
        <p class="user-card__role">
          {{ authStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}
        </p>
        <el-button class="logout-button" @click="handleLogout">退出登录</el-button>
      </div>
    </aside>

    <main class="admin-layout__main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px 1fr;
  background:
    radial-gradient(circle at top left, rgba(147, 197, 253, 0.3), transparent 30%),
    linear-gradient(180deg, #eef4fb 0%, #f8fbff 100%);
}

.admin-layout__aside {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 28px 22px;
  background: rgba(12, 34, 59, 0.95);
  color: #fff;
}

.brand-block {
  margin-bottom: 28px;
}

.brand-block__eyebrow {
  margin: 0 0 8px;
  color: #90cdfb;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1.2px;
}

.brand-block h1 {
  margin: 0;
  font-size: 24px;
  line-height: 1.4;
}

.menu-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.menu-item {
  border: none;
  text-align: left;
  padding: 13px 16px;
  border-radius: 14px;
  background: transparent;
  color: #d7e5f8;
  cursor: pointer;
  transition: all 0.25s ease;
}

.menu-item:hover,
.menu-item--active {
  background: linear-gradient(135deg, #1f5fa6, #3b82f6);
  color: #fff;
}

.user-card {
  padding: 20px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.user-card__name,
.user-card__role {
  margin: 0;
}

.user-card__role {
  margin-top: 6px;
  color: #bcd4ef;
  font-size: 13px;
}

.logout-button {
  width: 100%;
  margin-top: 18px;
}

.admin-layout__main {
  padding: 30px;
}

@media (max-width: 960px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .admin-layout__aside {
    gap: 20px;
  }
}
</style>
