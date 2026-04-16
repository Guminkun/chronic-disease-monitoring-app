import request from '../utils/request'

export function getArticles(params: any) {
  return request({
    url: '/education/articles',
    method: 'get',
    params
  })
}

export function createArticle(data: any) {
  return request({
    url: '/education/articles',
    method: 'post',
    data
  })
}

export function updateArticle(id: number, data: any) {
  return request({
    url: `/education/articles/${id}`,
    method: 'put',
    data
  })
}

export function getCategories() {
    return request({
        url: '/education/categories',
        method: 'get'
    })
}
