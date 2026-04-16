import request from '../utils/request'

export function login(data: any) {
  const formData = new FormData()
  formData.append('username', data.username)
  formData.append('password', data.password)
  
  return request({
    url: '/auth/token',
    method: 'post',
    data: formData
  })
}

export function getUserInfo() {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}
