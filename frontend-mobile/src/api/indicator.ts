import request from '../utils/request'

export function getIndicators(params: { q?: string, category?: string }) {
  return request({
    url: '/indicators/',
    method: 'GET',
    params: params
  })
}

export function getIndicatorCategories() {
  return request({
    url: '/indicators/categories',
    method: 'GET'
  })
}
