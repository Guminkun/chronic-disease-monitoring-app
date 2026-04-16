import request from '../utils/request'

export function getOverview() {
  return request({
    url: '/dashboard/overview',
    method: 'get'
  })
}

export function getTrends(days: number = 30) {
  return request({
    url: '/dashboard/trends',
    method: 'get',
    params: { days }
  })
}
