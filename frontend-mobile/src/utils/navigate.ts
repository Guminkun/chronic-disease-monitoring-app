/**
 * 导航工具函数
 * 处理页面跳转的各种异常情况
 */

interface NavigateOptions {
  url: string
  type?: 'navigateTo' | 'redirectTo' | 'switchTab' | 'reLaunch'
}

/**
 * 安全的页面跳转
 * 自动处理页面栈溢出、超时等异常
 */
export const safeNavigate = (options: NavigateOptions): Promise<void> => {
  return new Promise((resolve, reject) => {
    const { url, type = 'navigateTo' } = options
    
    const handleSuccess = () => {
      console.log(`[Navigate] ${type} success: ${url}`)
      resolve()
    }
    
    const handleFail = (err: any) => {
      console.error(`[Navigate] ${type} failed:`, err)
      
      // 如果是 navigateTo 失败，尝试 redirectTo
      if (type === 'navigateTo') {
        const pages = getCurrentPages()
        console.log(`[Navigate] Current page stack: ${pages.length}`)
        
        if (pages.length >= 10) {
          console.log('[Navigate] Page stack full, using redirectTo')
          uni.redirectTo({
            url,
            success: handleSuccess,
            fail: (redirectErr) => {
              console.error('[Navigate] redirectTo also failed:', redirectErr)
              // 最后尝试 reLaunch
              uni.reLaunch({
                url,
                success: handleSuccess,
                fail: () => {
                  uni.showToast({
                    title: '页面跳转失败',
                    icon: 'none',
                    duration: 2000
                  })
                  reject(redirectErr)
                }
              })
            }
          })
          return
        }
        
        // 如果不是页面栈问题，尝试延时重试
        if (err.errMsg && err.errMsg.includes('timeout')) {
          console.log('[Navigate] Timeout detected, retrying...')
          setTimeout(() => {
            uni.navigateTo({
              url,
              success: handleSuccess,
              fail: (retryErr) => {
                console.error('[Navigate] Retry failed:', retryErr)
                uni.redirectTo({
                  url,
                  success: handleSuccess,
                  fail: () => {
                    uni.showToast({
                      title: '页面跳转失败，请重试',
                      icon: 'none',
                      duration: 2000
                    })
                    reject(retryErr)
                  }
                })
              }
            })
          }, 500)
          return
        }
      }
      
      uni.showToast({
        title: '页面跳转失败，请重试',
        icon: 'none',
        duration: 2000
      })
      reject(err)
    }
    
    switch (type) {
      case 'navigateTo':
        uni.navigateTo({ url, success: handleSuccess, fail: handleFail })
        break
      case 'redirectTo':
        uni.redirectTo({ url, success: handleSuccess, fail: handleFail })
        break
      case 'switchTab':
        uni.switchTab({ url, success: handleSuccess, fail: handleFail })
        break
      case 'reLaunch':
        uni.reLaunch({ url, success: handleSuccess, fail: handleFail })
        break
      default:
        uni.navigateTo({ url, success: handleSuccess, fail: handleFail })
    }
  })
}

/**
 * 安全返回上一页
 */
export const safeNavigateBack = (delta: number = 1): Promise<void> => {
  return new Promise((resolve) => {
    const pages = getCurrentPages()
    
    if (pages.length <= 1) {
      // 没有上一页，跳转到首页
      uni.switchTab({
        url: '/pages/index/index',
        success: () => resolve(),
        fail: () => {
          uni.reLaunch({
            url: '/pages/index/index',
            success: () => resolve()
          })
        }
      })
    } else {
      uni.navigateBack({
        delta,
        success: () => resolve(),
        fail: () => {
          // 返回失败，跳转到首页
          uni.switchTab({
            url: '/pages/index/index',
            success: () => resolve()
          })
        }
      })
    }
  })
}

/**
 * 检查页面栈并清理
 * 当页面栈接近上限时自动清理
 */
export const checkAndCleanPageStack = () => {
  const pages = getCurrentPages()
  console.log(`[Navigate] Current page stack: ${pages.length}`)
  
  if (pages.length >= 9) {
    console.log('[Navigate] Page stack near limit, consider using redirectTo')
    return false
  }
  
  return true
}
