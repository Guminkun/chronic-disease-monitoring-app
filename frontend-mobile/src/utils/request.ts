export const BASE_URL = '/api'
// 小程序本地开发直连后端（微信开发者工具需开启"不校验合法域名"）
const MP_BASE_URL = 'http://127.0.0.1:8000'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  params?: Record<string, any>
  header?: any
  timeout?: number
}

const request = (options: RequestOptions) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    
    let finalUrl = BASE_URL + options.url

    // #ifdef MP-WEIXIN
    finalUrl = MP_BASE_URL + options.url
    // #endif

    // #ifdef APP-PLUS
    finalUrl = 'http://192.168.1.100:8000' + options.url // 请替换为您的局域网IP
    // #endif

    let queryStr = ''
    if (options.params) {
      const qs = Object.entries(options.params)
        .filter(([, v]) => v !== undefined && v !== null && v !== '')
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
      if (qs) {
        queryStr = (finalUrl.includes('?') ? '&' : '?') + qs
      }
    }
    
    console.log('[Request]', options.method || 'GET', finalUrl + queryStr)
    
    uni.request({
      url: finalUrl + queryStr,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      timeout: options.timeout || 30000, // 默认30秒超时
      success: (res: any) => {
        console.log('[Response]', res.statusCode, res.data)
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          const hadToken = !!uni.getStorageSync('token')
          uni.removeStorageSync('token')
          if (hadToken) {
            uni.showToast({ title: '登录已过期', icon: 'none' })
          }
          reject(res.data)
        } else {
          uni.showToast({ title: res.data?.detail || '请求失败', icon: 'none' })
          reject(res.data)
        }
      },
      fail: (err: any) => {
        console.error('[Request Failed]', err)
        const errMsg = err.errMsg || '网络请求失败'
        if (errMsg.includes('timeout')) {
          uni.showToast({ title: '请求超时，请检查网络', icon: 'none' })
        } else if (errMsg.includes('fail')) {
          uni.showToast({ title: '连接服务器失败，请确认后端服务已启动', icon: 'none', duration: 3000 })
        } else {
          uni.showToast({ title: errMsg, icon: 'none' })
        }
        reject(err)
      }
    })
  })
}

export default request
