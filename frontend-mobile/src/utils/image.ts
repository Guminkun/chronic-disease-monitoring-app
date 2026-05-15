/**
 * 将网络图片 URL 下载为本地临时文件路径
 * 解决微信小程序 <image> 组件 ORB 跨域阻止问题
 */
export function resolveImageUrl(url: string): Promise<string> {
  return new Promise((resolve) => {
    if (!url || !url.startsWith('http')) {
      resolve(url || '')
      return
    }
    uni.getImageInfo({
      src: url,
      success: (res) => {
        resolve(res.path)
      },
      fail: () => {
        resolve(url)
      }
    })
  })
}
