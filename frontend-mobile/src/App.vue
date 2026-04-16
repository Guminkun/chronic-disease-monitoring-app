<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
onLaunch(() => {
  console.log("App Launch");
});
onShow(() => {
  console.log("App Show");
});
onHide(() => {
  console.log("App Hide");
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
}
</style>
