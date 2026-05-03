import { createRouter, createWebHistory } from 'vue-router'

import AdminLayout from '@/layouts/AdminLayout.vue'
import LoginView from '@/views/LoginView.vue'
import AdminHomeView from '@/views/admin/AdminHomeView.vue'
import DocumentManageView from '@/views/admin/DocumentManageView.vue'
import KnowledgeManageView from '@/views/admin/KnowledgeManageView.vue'
import UserManageView from '@/views/admin/UserManageView.vue'
import HistoryView from '@/views/user/HistoryView.vue'
import ChatView from '@/views/user/ChatView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'admin/home',
          name: 'admin-home',
          component: AdminHomeView,
          meta: { requiresAuth: true, roles: ['admin'] },
        },
        {
          path: 'admin/users',
          name: 'admin-users',
          component: UserManageView,
          meta: { requiresAuth: true, roles: ['admin'] },
        },
        {
          path: 'admin/knowledge',
          name: 'admin-knowledge',
          component: KnowledgeManageView,
          meta: { requiresAuth: true, roles: ['admin'] },
        },
        {
          path: 'admin/documents',
          name: 'admin-documents',
          component: DocumentManageView,
          meta: { requiresAuth: true, roles: ['admin'] },
        },
        {
          path: 'chat',
          name: 'chat',
          component: ChatView,
          meta: { requiresAuth: true, roles: ['admin', 'user'] },
        },
        {
          path: 'history',
          name: 'history',
          component: HistoryView,
          meta: { requiresAuth: true, roles: ['admin', 'user'] },
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.token) {
    return '/login'
  }

  if (to.path === '/login' && authStore.token) {
    return authStore.role === 'admin' ? '/admin/home' : '/chat'
  }

  if (to.meta.requiresAuth && !authStore.userInfo) {
    try {
      await authStore.fetchProfile()
    } catch {
      authStore.logout()
      return '/login'
    }
  }

  const roles = to.meta.roles || []
  if (roles.length && !roles.includes(authStore.role)) {
    return authStore.role === 'admin' ? '/admin/home' : '/chat'
  }

  return true
})

export default router
