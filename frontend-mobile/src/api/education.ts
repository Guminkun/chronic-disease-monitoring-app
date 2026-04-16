import request from '../utils/request'

export interface ArticleCategory {
  id: number
  name: string
  icon?: string
  sort_order: number
  is_active: boolean
  created_at: string
}

export interface Article {
  id: number
  title: string
  cover_image?: string
  author?: string
  summary?: string
  content?: string
  video_url?: string
  duration?: string
  views: number
  is_recommended: boolean
  is_published: boolean
  published_at: string
  created_at: string
  category?: ArticleCategory
}

// 获取分类列表
export function getArticleCategories() {
  return request({
    url: '/education/categories',
    method: 'GET'
  })
}

// 获取文章列表
export function getArticles(params: {
  category_id?: number
  q?: string
  is_recommended?: boolean
  limit?: number
  skip?: number
}) {
  return request({
    url: '/education/articles',
    method: 'GET',
    data: params
  })
}

// 获取文章详情
export function getArticleDetail(id: number) {
  return request({
    url: `/education/articles/${id}`,
    method: 'GET'
  }) as Promise<Article>
}
