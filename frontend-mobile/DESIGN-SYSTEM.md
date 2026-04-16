# 移动端设计系统 - 背景色统一规范

基于 **Frontend Design** 技能，本文档定义了移动端所有页面的背景色统一标准。

## 设计原则

### 1. 视觉层次清晰
使用不同层级的背景色区分内容层次，提升用户体验。

### 2. 一致性
所有页面使用统一的设计令牌（Design Tokens），确保视觉一致性。

### 3. 可访问性
背景色对比度符合 WCAG 标准，确保所有用户都能舒适阅读。

## 背景色系统

### CSS 变量定义

```scss
/* 在全局样式文件中定义 */
--color-bg-base: #F5F7FA;        /* 页面基础背景色 */
--color-bg-elevated: #FFFFFF;    /* 提升层背景色（卡片、导航栏等） */
--color-bg-muted: #F8FAFC;       /* 次要背景色（输入框、禁用状态） */
--color-bg-subtle: #EFF6FF;      /* 柔和背景色（强调区域） */
```

### 使用场景

#### 1. 页面基础背景
**变量**: `var(--color-bg-base)`
**颜色值**: `#F5F7FA`
**使用场景**: 所有页面的根容器

```scss
.page {
  min-height: 100vh;
  background-color: var(--color-bg-base);
}

.container {
  min-height: 100vh;
  background-color: var(--color-bg-base);
}
```

**应用到页面**:
- ✅ 首页 (`/pages/index/index.vue`)
- ✅ 用药页面 (`/pages/medication/index.vue`)
- ✅ 监测页面 (`/pages/monitor/index.vue`)
- ✅ 个人中心 (`/pages/profile/index.vue`)
- ✅ 健康教育 (`/pages/education/index.vue`)
- ✅ 成员管理 (`/pages/member/list.vue`)
- ✅ 病历管理 (`/pages/medical-record/list.vue`)
- ✅ 检查报告 (`/pages/report/report.vue`)

#### 2. 提升层背景（卡片、导航栏）
**变量**: `var(--color-bg-elevated)`
**颜色值**: `#FFFFFF`
**使用场景**: 卡片、导航栏、弹出层、输入框焦点状态

```scss
.card {
  background-color: var(--color-bg-elevated);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.header {
  background-color: var(--color-bg-elevated);
}

.modal {
  background-color: var(--color-bg-elevated);
}
```

**应用到组件**:
- ✅ 所有卡片组件
- ✅ 页面顶部导航栏
- ✅ 弹出层
- ✅ 列表项

#### 3. 次要背景（输入框、禁用状态）
**变量**: `var(--color-bg-muted)`
**颜色值**: `#F8FAFC`
**使用场景**: 输入框默认背景、禁用按钮、分隔区域

```scss
.input {
  background-color: var(--color-bg-muted);
}

.button:disabled {
  background-color: var(--color-bg-muted);
}

.divider-section {
  background-color: var(--color-bg-muted);
}
```

#### 4. 柔和背景（强调区域）
**变量**: `var(--color-bg-subtle)`
**颜色值**: `#EFF6FF`
**使用场景**: 提示区域、标签背景、选中状态

```scss
.alert {
  background-color: var(--color-bg-subtle);
}

.tag {
  background-color: var(--color-bg-subtle);
}

.selected {
  background-color: var(--color-bg-subtle);
}
```

## 实施清单

### 已完成页面

| 页面 | 路径 | 状态 |
|------|------|------|
| 首页 | `/pages/index/index.vue` | ✅ |
| 用药 | `/pages/medication/index.vue` | ✅ |
| 监测 | `/pages/monitor/index.vue` | ✅ |
| 个人中心 | `/pages/profile/index.vue` | ✅ |
| 健康教育 | `/pages/education/index.vue` | ✅ |

### 待更新页面

以下页面需要检查并更新背景色：

- [ ] 登录页 (`/pages/login/login.vue`)
- [ ] 注册页 (`/pages/register/*.vue`)
- [ ] 成员管理 (`/pages/member/*.vue`)
- [ ] 病历管理 (`/pages/medical-record/*.vue`)
- [ ] 检查报告 (`/pages/report/*.vue`)
- [ ] 反馈页面 (`/pages/feedback/*.vue`)
- [ ] 设置页面 (`/pages/settings/*.vue`)

## 更新步骤

### 1. 检查当前背景色
```bash
# 搜索硬编码的背景色
grep -r "background-color.*#" src/pages/
grep -r "background:.*#" src/pages/
```

### 2. 替换为CSS变量
将硬编码的颜色值替换为设计令牌：

```scss
/* ❌ 不推荐 */
.page {
  background-color: #f0f4ff;
}

/* ✅ 推荐 */
.page {
  background-color: var(--color-bg-base);
}
```

### 3. 测试验证
更新后，在以下设备上测试：
- iOS 设备
- Android 设备
- 微信小程序
- 支付宝小程序

确保：
- ✅ 页面背景色统一
- ✅ 卡片、导航栏突出显示
- ✅ 文字可读性良好
- ✅ 深色模式兼容（未来）

## 设计令牌完整列表

### 颜色系统

```scss
/* 背景色 */
--color-bg-base: #F5F7FA;
--color-bg-elevated: #FFFFFF;
--color-bg-muted: #F8FAFC;
--color-bg-subtle: #EFF6FF;

/* 主色 */
--color-primary: #3B82F6;
--color-primary-light: #60A5FA;
--color-primary-dark: #2563EB;

/* 语义色 */
--color-success: #22C55E;
--color-warning: #F97316;
--color-error: #EF4444;
--color-info: #64748B;

/* 文字颜色 */
--color-text-primary: #1E293B;
--color-text-secondary: #64748B;
--color-text-muted: #94A3B8;
--color-text-inverse: #FFFFFF;
```

### 间距系统

```scss
--spacing-xs: 16rpx;
--spacing-sm: 24rpx;
--spacing-md: 32rpx;
--spacing-lg: 48rpx;
--spacing-xl: 64rpx;
```

### 圆角系统

```scss
--radius-sm: 12rpx;
--radius-md: 20rpx;
--radius-lg: 28rpx;
--radius-xl: 36rpx;
```

### 阴影系统

```scss
--shadow-xs: 0 2rpx 8rpx rgba(0, 0, 0, 0.03);
--shadow-sm: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
--shadow-md: 0 8rpx 24rpx rgba(0, 0, 0, 0.06);
--shadow-lg: 0 16rpx 48rpx rgba(0, 0, 0, 0.08);
```

## 最佳实践

### 1. 优先使用设计令牌
始终使用CSS变量，避免硬编码颜色值。

### 2. 保持层次清晰
- 页面背景使用 `--color-bg-base`
- 卡片、导航栏使用 `--color-bg-elevated`
- 输入框、次要元素使用 `--color-bg-muted`

### 3. 阴影增强层次
为提升层元素添加阴影，增强视觉层次：

```scss
.card {
  background-color: var(--color-bg-elevated);
  box-shadow: var(--shadow-sm);
}
```

### 4. 过渡动画
使用统一的时间函数：

```scss
transition: all var(--transition-base);
```

## 兼容性说明

- ✅ iOS Safari 12+
- ✅ Android Chrome 80+
- ✅ 微信小程序
- ✅ 支付宝小程序
- ✅ 百度小程序
- ✅ 字节跳动小程序

## 未来规划

- [ ] 支持深色模式
- [ ] 主题色可配置
- [ ] 自动对比度调整
- [ ] 色盲友好模式
