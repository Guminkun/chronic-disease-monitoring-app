import { useUserStore } from '@/stores/user'

const REDIRECT_URL_KEY = 'login_redirect_url'

export function isLoggedIn(): boolean {
  return !!uni.getStorageSync('token')
}

export function saveRedirectUrl(url: string) {
  uni.setStorageSync(REDIRECT_URL_KEY, url)
}

export function getRedirectUrl(): string {
  return uni.getStorageSync(REDIRECT_URL_KEY) || '/pages/index/index'
}

export function clearRedirectUrl() {
  uni.removeStorageSync(REDIRECT_URL_KEY)
}

export function checkLoginWithRedirect(currentUrl?: string): boolean {
  if (isLoggedIn()) {
    return true
  }
  
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const url = currentUrl || `/${currentPage.route}`
  
  saveRedirectUrl(url)
  
  uni.navigateTo({
    url: '/pages/login/login'
  })
  
  return false
}

export function navigateAfterLogin() {
  const redirectUrl = getRedirectUrl()
  clearRedirectUrl()
  
  const tabBarPages = [
    '/pages/index/index',
    '/pages/medication/index',
    '/pages/monitor/index',
    '/pages/profile/index'
  ]
  
  if (tabBarPages.includes(redirectUrl)) {
    uni.switchTab({ url: redirectUrl })
  } else {
    const urlWithoutQuery = redirectUrl.split('?')[0]
    const tabBarPaths = tabBarPages.map(p => p.split('?')[0])
    
    if (tabBarPaths.includes(urlWithoutQuery)) {
      uni.switchTab({ url: redirectUrl })
    } else {
      uni.redirectTo({ url: redirectUrl, fail: () => {
        uni.switchTab({ url: '/pages/index/index' })
      }})
    }
  }
}
