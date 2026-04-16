import request from '../utils/request'

export function getReportTypes(params: { q?: string, category?: string }) {
  return request({
    url: '/report-types/',
    method: 'GET',
    data: params
  })
}

export function getReportTypeCategories() {
  return request({
    url: '/report-types/categories',
    method: 'GET'
  })
}

export function getImagingChecks(params: { q?: string, category?: string, part?: string, gender?: string, enhanced?: number, limit?: number }) {
  return request({
    url: '/imaging-checks/',
    method: 'GET',
    data: params
  })
}

export function getImagingCheckCategories() {
  return request({
    url: '/imaging-checks/categories',
    method: 'GET'
  })
}
