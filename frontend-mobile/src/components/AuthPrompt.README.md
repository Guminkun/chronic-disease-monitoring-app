# AuthPrompt 登录提醒组件

基于 Frontend Design 技能设计的现代化登录提醒组件。

## 设计原则

本组件遵循以下设计原则：

- **视觉层次清晰**：图标、标题、描述、按钮层次分明
- **留白充足**：使用设计令牌定义统一的间距系统
- **一致性**：统一的圆角、阴影、颜色系统
- **可访问性**：支持键盘导航、focus状态、prefers-reduced-motion
- **响应式**：提供多种尺寸变体
- **现代化设计**：渐变背景、柔和阴影、流畅动画、装饰元素

## 使用方法

### 基础用法

```vue
<template>
  <AuthPrompt 
    v-if="!userStore.token"
    title="登录以使用完整功能"
    description="登录后可管理慢病、记录用药、监测健康"
  />
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import AuthPrompt from '@/components/AuthPrompt.vue'

const userStore = useUserStore()
</script>
```

### Props 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | string | '登录以使用完整功能' | 主标题文字 |
| description | string | '登录后可管理慢病、记录用药、监测健康' | 描述文字 |
| buttonText | string | '立即登录' | 按钮文字 |
| icon | string | '🔐' | 图标（emoji或文字） |
| theme | 'primary' \| 'success' \| 'warning' \| 'info' | 'primary' | 主题颜色 |
| size | 'small' \| 'medium' \| 'large' | 'medium' | 尺寸大小 |
| redirectUrl | string | '' | 登录后重定向URL |

### 主题颜色

- **primary**：蓝色主题，适用于通用场景
- **success**：绿色主题，适用于用药等健康相关场景
- **warning**：橙色主题，适用于监测等提醒场景
- **info**：灰色主题，适用于信息展示场景

### 尺寸变体

- **small**：紧凑型，适用于列表项或小卡片
- **medium**：标准型，适用于页面主要内容区
- **large**：大型，适用于重要页面或突出显示

## 使用示例

### 首页

```vue
<AuthPrompt 
  v-if="!userStore.token"
  title="登录以使用完整功能"
  description="登录后可管理慢病、记录用药、监测健康"
  icon="🔐"
  theme="primary"
  size="medium"
/>
```

### 用药页面

```vue
<AuthPrompt 
  v-if="!isLoggedIn()"
  title="登录以管理用药计划"
  description="登录后可添加药品、记录服药情况"
  icon="💊"
  theme="success"
  size="medium"
/>
```

### 监测页面

```vue
<AuthPrompt 
  v-if="!isLoggedIn()"
  title="登录以记录健康数据"
  description="登录后可记录血糖、血压等健康指标"
  icon="❤️"
  theme="warning"
  size="medium"
/>
```

## 设计令牌（Design Tokens）

组件使用CSS变量定义设计令牌，确保一致性和可维护性：

```scss
--spacing-xs: 16rpx;
--spacing-sm: 24rpx;
--spacing-md: 32rpx;
--spacing-lg: 48rpx;
--spacing-xl: 64rpx;

--radius-sm: 12rpx;
--radius-md: 20rpx;
--radius-lg: 28rpx;

--shadow-sm: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
--shadow-md: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
--shadow-lg: 0 16rpx 48rpx rgba(0, 0, 0, 0.12);
```

## 可访问性特性

- ✅ 支持键盘导航（Tab键）
- ✅ Focus状态可见（蓝色轮廓）
- ✅ 支持 prefers-reduced-motion
- ✅ 语义化HTML结构
- ✅ 文本对比度符合WCAG标准

## 动画效果

- 平滑的缩放动画（按下时）
- 按钮箭头滑动效果
- 柔和的阴影变化
- 支持 reduced-motion 媒体查询

## 浏览器兼容性

- iOS Safari 12+
- Android Chrome 80+
- 微信小程序
- 支付宝小程序
- 其他主流小程序平台
