import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 60000
})

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

function onTokenRefreshed(newToken: string) {
  refreshSubscribers.forEach(cb => cb(newToken))
  refreshSubscribers = []
}

function addRefreshSubscriber(cb: (token: string) => void) {
  refreshSubscribers.push(cb)
}

function parseJwtPayload(token: string): any {
  try {
    const base64 = token.split('.')[1]
    return JSON.parse(atob(base64))
  } catch {
    return null
  }
}

function isTokenExpiringSoon(token: string, bufferMinutes = 5): boolean {
  const payload = parseJwtPayload(token)
  if (!payload?.exp) return false
  const now = Math.floor(Date.now() / 1000)
  return payload.exp - now < bufferMinutes * 60
}

async function refreshToken(): Promise<string | null> {
  const token = localStorage.getItem('token')
  if (!token) return null
  try {
    const res: any = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL || '/api'}/auth/refresh`,
      {},
      { headers: { Authorization: `Bearer ${token}` }, timeout: 10000 }
    )
    const newToken = res.access_token
    localStorage.setItem('token', newToken)
    localStorage.setItem('role', res.role)
    return newToken
  } catch {
    return null
  }
}

service.interceptors.request.use(
  async (config) => {
    let token = localStorage.getItem('token')
    if (token) {
      if (isTokenExpiringSoon(token) && !config.url?.includes('/auth/')) {
        if (!isRefreshing) {
          isRefreshing = true
          const newToken = await refreshToken()
          isRefreshing = false
          if (newToken) {
            onTokenRefreshed(newToken)
            config.headers['Authorization'] = `Bearer ${newToken}`
          } else {
            localStorage.removeItem('token')
            localStorage.removeItem('userRole')
            router.push('/login')
            return Promise.reject(new Error('Token refresh failed'))
          }
        } else {
          return new Promise(resolve => {
            addRefreshSubscriber((newToken: string) => {
              config.headers['Authorization'] = `Bearer ${newToken}`
              resolve(config)
            })
          })
        }
      } else {
        config.headers['Authorization'] = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('userRole')
        ElMessage.error('登录已过期，请重新登录')
        router.push('/login')
        return Promise.reject(error)
      }
      ElMessage.error(data?.detail || `请求失败 (${status})`)
    } else {
      ElMessage.error('网络连接失败，请检查网络')
    }
    return Promise.reject(error)
  }
)

export default service
