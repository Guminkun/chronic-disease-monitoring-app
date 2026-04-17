import { defineStore } from 'pinia'
import { login, loginBySms, loginByWechat, getUserInfo } from '../api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    user: null as any,
    role: uni.getStorageSync('role') || '',
    userId: uni.getStorageSync('userId') || ''
  }),
  actions: {
    async login(loginForm: any) {
      const res: any = await login(loginForm)
      this.token = res.access_token
      this.role = res.role
      this.userId = res.user_id || ''
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('role', res.role)
      uni.setStorageSync('userId', res.user_id || '')
      return res
    },
    async loginBySms(loginForm: { phone: string, code: string }) {
      const res: any = await loginBySms(loginForm)
      this.token = res.access_token
      this.role = res.role
      this.userId = res.user_id || ''
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('role', res.role)
      uni.setStorageSync('userId', res.user_id || '')
      return res
    },
    async loginByWechat() {
      return new Promise((resolve, reject) => {
        uni.login({
          provider: 'weixin',
          success: async (loginRes) => {
            try {
              const res: any = await loginByWechat({ code: loginRes.code })
              this.token = res.access_token
              this.role = res.role
              this.userId = res.user_id || ''
              uni.setStorageSync('token', res.access_token)
              uni.setStorageSync('role', res.role)
              uni.setStorageSync('userId', res.user_id || '')
              resolve(res)
            } catch (error) {
              reject(error)
            }
          },
          fail: (err) => {
            reject(err)
          }
        })
      })
    },
    async fetchUserInfo() {
      const res = await getUserInfo()
      this.user = res
      return res
    },
    logout() {
      this.token = ''
      this.user = null
      this.role = ''
      this.userId = ''
      uni.removeStorageSync('token')
      uni.removeStorageSync('role')
      uni.removeStorageSync('userId')
      uni.removeStorageSync('hasLoggedInBefore')
      uni.switchTab({
        url: '/pages/index/index'
      })
    }
  }
})
