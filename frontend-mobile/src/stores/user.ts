import { defineStore } from 'pinia'
import { login, loginBySms, loginByWechat, getUserInfo } from '../api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    user: null as any,
    role: uni.getStorageSync('role') || ''
  }),
  actions: {
    async login(loginForm: any) {
      const res: any = await login(loginForm)
      this.token = res.access_token
      this.role = res.role
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('role', res.role)
      return res
    },
    async loginBySms(loginForm: { phone: string, code: string }) {
      const res: any = await loginBySms(loginForm)
      this.token = res.access_token
      this.role = res.role
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('role', res.role)
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
              uni.setStorageSync('token', res.access_token)
              uni.setStorageSync('role', res.role)
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
      uni.removeStorageSync('token')
      uni.removeStorageSync('role')
      uni.switchTab({
        url: '/pages/index/index'
      })
    }
  }
})
