import request from '../utils/request'

export function login(data: any) {
  return request({
    url: '/auth/token',
    method: 'POST',
    data: data,
    header: {
      'content-type': 'application/x-www-form-urlencoded'
    }
  })
}

export function sendSmsCode(data: { phone: string }) {
  return request({
    url: '/auth/sms/code',
    method: 'POST',
    data: data
  })
}

export function loginBySms(data: { phone: string, code: string }) {
  return request({
    url: '/auth/sms/login',
    method: 'POST',
    data: data
  })
}

export function registerDoctor(data: { user: any, doctor_info: any }) {
  return request({
    url: '/auth/register/doctor',
    method: 'POST',
    data: data
  })
}

export function registerPatient(data: { user: any, patient_info: any }) {
  return request({
    url: '/auth/register/patient',
    method: 'POST',
    data: data
  })
}

export function getUserInfo() {
  return request({
    url: '/auth/me',
    method: 'GET'
  })
}

export function loginByWechat(data: { code: string }) {
  return request({
    url: '/auth/wechat/login',
    method: 'POST',
    data: data
  })
}

export function updateWechatProfile(data: { nickname?: string, avatar?: string }) {
  return request({
    url: '/auth/wechat/update-profile',
    method: 'POST',
    data: data
  })
}
