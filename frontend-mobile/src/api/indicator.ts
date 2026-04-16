import request from '../utils/request'

export function getIndicators(params: { q?: string, category?: string }) {
  return request({
    url: '/indicators/',
    method: 'GET',
    data: params
  })
}

export function getIndicatorCategories() {
  return request({
    url: '/indicators/categories',
    method: 'GET'
  })
}
