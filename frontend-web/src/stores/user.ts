import { defineStore } from 'pinia'
import { login, getUserInfo } from '../api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as any,
    role: localStorage.getItem('role') || ''
  }),
  actions: {
    async login(loginForm: any) {
      const res: any = await login(loginForm)
      // Backend returns { access_token, token_type, role, user_id, full_name }
      this.token = res.access_token
      this.role = res.role
      localStorage.setItem('token', res.access_token)
      localStorage.setItem('role', res.role)
      return res
    },
    async fetchUserInfo() {
      try {
        const res = await getUserInfo()
        this.user = res
        return res
      } catch (e) {
        this.user = null
        throw e
      }
    },
    logout() {
      this.token = ''
      this.user = null
      this.role = ''
      localStorage.removeItem('token')
      localStorage.removeItem('role')
    }
  }
})
