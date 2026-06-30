import { defineStore } from 'pinia'

import { fetchCurrentUser, login, logout, type CurrentUser } from '../api/accounts'

export const useSessionStore = defineStore('session', {
  state: () => ({
    isAuthenticated: false,
    displayName: '',
    user: null as CurrentUser | null,
    loading: false,
    initialized: false,
  }),
  getters: {
    isApproved: (state) => Boolean(state.user?.is_superuser || state.user?.profile?.is_approved),
    hasAnyRole: (state) => (roles: string[]) => {
      if (state.user?.is_superuser) return true
      return roles.some((role) => state.user?.roles.includes(role))
    },
  },
  actions: {
    async login(username: string, password: string) {
      this.loading = true
      try {
        const user = await login(username.trim(), password)
        this.user = user
        this.isAuthenticated = true
        this.displayName = user.profile?.real_name || user.username
        this.initialized = true
      } finally {
        this.loading = false
      }
    },
    async loadCurrentUser() {
      this.loading = true
      try {
        const user = await fetchCurrentUser()
        this.user = user
        this.isAuthenticated = true
        this.displayName = user.profile?.real_name || user.username
      } catch {
        this.user = null
        this.isAuthenticated = false
        this.displayName = ''
      } finally {
        this.loading = false
        this.initialized = true
      }
    },
    async logout() {
      this.loading = true
      try {
        await logout()
      } catch {
        // 前端退出要以本地登录态清理为准；后端会话过期或 CSRF 失效时也应允许用户离开内部平台。
      } finally {
        this.user = null
        this.isAuthenticated = false
        this.displayName = ''
        this.initialized = true
        this.loading = false
      }
    },
  },
})
