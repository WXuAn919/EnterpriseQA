import { defineStore } from 'pinia'

import { getProfileApi, loginApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('enterprise-qa-token') || '',
    userInfo: JSON.parse(localStorage.getItem('enterprise-qa-user') || 'null'),
  }),
  getters: {
    isLogin: (state) => Boolean(state.token),
    role: (state) => state.userInfo?.role || '',
  },
  actions: {
    /** 执行登录并缓存用户信息。 */
    async login(form) {
      const response = await loginApi(form)
      this.token = response.data.token
      this.userInfo = response.data.userInfo
      localStorage.setItem('enterprise-qa-token', this.token)
      localStorage.setItem('enterprise-qa-user', JSON.stringify(this.userInfo))
      return response.data
    },
    /** 刷新当前登录用户资料。 */
    async fetchProfile() {
      if (!this.token) return null
      const response = await getProfileApi()
      this.userInfo = response.data
      localStorage.setItem('enterprise-qa-user', JSON.stringify(this.userInfo))
      return response.data
    },
    /** 清空本地登录状态。 */
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('enterprise-qa-token')
      localStorage.removeItem('enterprise-qa-user')
    },
  },
})
