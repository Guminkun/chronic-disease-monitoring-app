import request from '../utils/request'

export const uploadAvatar = (filePath: string): Promise<{ url: string }> => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    
    uni.uploadFile({
      url: `${baseUrl}/upload/avatar`,
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = JSON.parse(res.data)
          resolve(data)
        } else {
          reject(new Error('Upload failed'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}
