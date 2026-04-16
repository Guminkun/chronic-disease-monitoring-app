import request, { BASE_URL } from '@/utils/request'

export const getMyReports = (params?: any) => {
  return request({
    url: '/patients/reports',
    method: 'GET',
    params
  })
}

export const getReportDetail = (id: string) => {
    return request({
        url: `/reports/${id}`,
        method: 'GET'
    })
}

export const uploadReport = (data: any) => {
    return request({
        url: '/patients/reports',
        method: 'POST',
        data
    })
}

export const parseReport = (filePath: string, formData: any = {}) => {
    return new Promise((resolve, reject) => {
        const token = uni.getStorageSync('token')
        let url = `${BASE_URL}/reports/parse`
        // #ifdef MP-WEIXIN
        url = 'http://127.0.0.1:8000/reports/parse'
        // #endif
        // #ifdef APP-PLUS
        url = 'http://192.168.1.100:8000/reports/parse'
        // #endif
        uni.uploadFile({
            url,
            filePath: filePath,
            name: 'file',
            formData: formData,
            timeout: 180000,
            header: {
                'Authorization': token ? `Bearer ${token}` : ''
            },
            success: (uploadFileRes) => {
                console.log('Upload result:', uploadFileRes)
                if (uploadFileRes.statusCode === 200) {
                    try {
                        const data = JSON.parse(uploadFileRes.data)
                        resolve(data)
                    } catch (e) {
                        console.error('JSON Parse error', e)
                        reject(new Error('Failed to parse response'))
                    }
                } else if (uploadFileRes.statusCode === 401 || uploadFileRes.statusCode === 403) {
                    uni.removeStorageSync('token')
                    uni.removeStorageSync('role')
                    uni.showToast({
                        title: '登录已过期',
                        icon: 'none'
                    })
                    setTimeout(() => {
                        uni.reLaunch({
                            url: '/pages/login/login'
                        })
                    }, 1500)
                    reject(new Error('Unauthorized'))
                } else {
                    try {
                        const errObj = JSON.parse(uploadFileRes.data || '{}')
                        const detail = errObj?.detail || `状态码 ${uploadFileRes.statusCode}`
                        reject(new Error(detail))
                    } catch {
                        reject(new Error(`上传失败，状态码 ${uploadFileRes.statusCode}`))
                    }
                }
            },
            fail: (err) => {
                console.error('Upload fail', err)
                reject(err)
            }
        })
    })
}

export const parseImagingReport = (filePath: string, formData: any = {}) => {
    return new Promise((resolve, reject) => {
        const token = uni.getStorageSync('token')
        let url = `${BASE_URL}/reports/parse-imaging`
        // #ifdef MP-WEIXIN
        url = 'http://127.0.0.1:8000/reports/parse-imaging'
        // #endif
        // #ifdef APP-PLUS
        url = 'http://192.168.1.100:8000/reports/parse-imaging'
        // #endif
        uni.uploadFile({
            url,
            filePath: filePath,
            name: 'file',
            formData: formData,
            timeout: 180000,
            header: {
                'Authorization': token ? `Bearer ${token}` : ''
            },
            success: (uploadFileRes) => {
                if (uploadFileRes.statusCode === 200) {
                    try {
                        const data = JSON.parse(uploadFileRes.data)
                        resolve(data)
                    } catch (e) {
                        reject(new Error('Failed to parse response'))
                    }
                } else if (uploadFileRes.statusCode === 401 || uploadFileRes.statusCode === 403) {
                    uni.removeStorageSync('token')
                    uni.removeStorageSync('role')
                    uni.showToast({
                        title: '登录已过期',
                        icon: 'none'
                    })
                    setTimeout(() => {
                        uni.reLaunch({
                            url: '/pages/login/login'
                        })
                    }, 1500)
                    reject(new Error('Unauthorized'))
                } else {
                    try {
                        const errObj = JSON.parse(uploadFileRes.data || '{}')
                        const detail = errObj?.detail || `状态码 ${uploadFileRes.statusCode}`
                        reject(new Error(detail))
                    } catch {
                        reject(new Error(`上传失败，状态码 ${uploadFileRes.statusCode}`))
                    }
                }
            },
            fail: (err) => {
                reject(err)
            }
        })
    })
}

export const updateReport = (id: string, data: any) => {
    return request({
        url: `/reports/${id}`,
        method: 'PUT',
        data
    })
}

export const deleteReport = (id: string) => {
    return request({
        url: `/reports/${id}`,
        method: 'DELETE'
    })
}

export const getTrends = (params?: { report_type?: string, metric_names?: string[], start_date?: string, end_date?: string }) => {
    return request({
        url: '/reports/trends',
        method: 'GET',
        params
    })
}

export const autoClassifyReport = (filePath: string, formData: any = {}) => {
    return new Promise((resolve, reject) => {
        const token = uni.getStorageSync('token')
        let url = `${BASE_URL}/reports/auto-classify`
        // #ifdef MP-WEIXIN
        url = 'http://127.0.0.1:8000/reports/auto-classify'
        // #endif
        // #ifdef APP-PLUS
        url = 'http://192.168.1.100:8000/reports/auto-classify'
        // #endif
        uni.uploadFile({
            url,
            filePath: filePath,
            name: 'file',
            formData: formData,
            timeout: 180000,
            header: {
                'Authorization': token ? `Bearer ${token}` : ''
            },
            success: (uploadFileRes) => {
                if (uploadFileRes.statusCode === 200) {
                    try {
                        const data = JSON.parse(uploadFileRes.data)
                        resolve(data)
                    } catch (e) {
                        reject(new Error('Failed to parse response'))
                    }
                } else if (uploadFileRes.statusCode === 401 || uploadFileRes.statusCode === 403) {
                    uni.removeStorageSync('token')
                    uni.removeStorageSync('role')
                    uni.showToast({
                        title: '登录已过期',
                        icon: 'none'
                    })
                    setTimeout(() => {
                        uni.reLaunch({
                            url: '/pages/login/login'
                        })
                    }, 1500)
                    reject(new Error('Unauthorized'))
                } else {
                    try {
                        const errObj = JSON.parse(uploadFileRes.data || '{}')
                        const detail = errObj?.detail || `状态码 ${uploadFileRes.statusCode}`
                        reject(new Error(detail))
                    } catch {
                        reject(new Error(`上传失败，状态码 ${uploadFileRes.statusCode}`))
                    }
                }
            },
            fail: (err) => {
                reject(err)
            }
        })
    })
}
