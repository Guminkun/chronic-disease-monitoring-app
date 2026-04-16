import request from '@/utils/request'

/**
 * 获取文件临时签名URL
 * @param fileKey 文件key路径
 */
export const getPresignedUrl = (fileKey: string) => {
  return request.get('/files/presigned-url', {
    params: { file_key: fileKey }
  })
}

/**
 * 获取报告图片URL
 * @param reportId 报告ID
 * @param thumbnail 是否获取缩略图（默认false）
 */
export const getReportImageUrl = (reportId: string, thumbnail = false) => {
  return request.get(`/files/report/${reportId}/image`, {
    params: { thumbnail }
  })
}

/**
 * 获取成员头像URL
 * @param memberId 成员ID
 */
export const getMemberAvatarUrl = (memberId: string) => {
  return request.get(`/files/member/${memberId}/avatar`)
}
