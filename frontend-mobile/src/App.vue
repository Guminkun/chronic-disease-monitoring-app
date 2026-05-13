<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();

onLaunch(() => {
  if (import.meta.env.DEV) console.log("App Launch");
  // #ifdef MP-WEIXIN
  // 微信小程序环境：自动检查登录状态
  autoLoginIfNeeded();
  // #endif
});

const autoLoginIfNeeded = async () => {
  const token = uni.getStorageSync('token');
  
  // 如果已有token，直接恢复用户状态
  if (token) {
    try {
      await userStore.fetchUserInfo();
    } catch (e) {
      if (import.meta.env.DEV) console.log('Failed to fetch user info, token may be expired');
      uni.removeStorageSync('token');
    }
    return;
  }
  
  // 如果之前登录过，尝试自动登录
  const hasLoggedInBefore = uni.getStorageSync('hasLoggedInBefore');
  if (hasLoggedInBefore) {
    try {
      await userStore.loginByWechat();
      if (import.meta.env.DEV) console.log('Auto login succeeded');
    } catch (e) {
      console.log('Auto login failed:', e);
      // 自动登录失败，清除标记
      uni.removeStorageSync('hasLoggedInBefore');
    }
  }
};

onShow(() => {
  if (import.meta.env.DEV) console.log("App Show");
});

onHide(() => {
  if (import.meta.env.DEV) console.log("App Hide");
});
</script>
<style>
/* Global CSS Variables for Theme */
:root {
  /* 背景渐变 */
  --bg-gradient-start: #f8fafc;
  --bg-gradient-end: #f6f7fb;

  /* 主色渐变 */
  --primary-start: #2563eb;
  --primary-end: #1e40af;

  /* 表面与边框 */
  --surface-border: #e6e9f2;
  --surface-muted: #f9fafb;

  /* 阴影与圆角 */
  --shadow-card: 0 8px 24px rgba(15, 23, 42, 0.06);
  --radius-card: 18px;
  --radius-pill: 9999px;

  /* 徽章渐变 */
  --badge-stable-start: #dcfce7;
  --badge-stable-end: #bbf7d0;
  --badge-unstable-start: #fef3c7;
  --badge-unstable-end: #fde68a;

  /* 提醒胶囊颜色 */
  --pill-med-bg: #eff6ff;
  --pill-med-fg: #3b82f6;
  --pill-recheck-bg: #fdf2f8;
  --pill-recheck-fg: #ec4899;

  /* 中老年适配 - 字号与触控区域 */
  --font-size-xs: 24rpx;
  --font-size-sm: 26rpx;
  --font-size-base: 30rpx;
  --font-size-lg: 34rpx;
  --font-size-xl: 38rpx;
  --min-touch-target: 88rpx;
}

/* 中老年适配 - 全局最小触控区域 */
button, .btn, [role="button"] {
  min-height: var(--min-touch-target);
}

/* 中老年适配 - 全局输入框 */
input, textarea {
  font-size: var(--font-size-base) !important;
  min-height: var(--min-touch-target);
}
</style>
