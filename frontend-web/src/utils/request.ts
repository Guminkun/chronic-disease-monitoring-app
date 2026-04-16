import axios from 'axios'

const service = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000
})

service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
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
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

export default service
