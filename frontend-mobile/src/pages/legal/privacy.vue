<template>
  <view class="legal-page">
    <PageHeader title="隐私政策" />
    <scroll-view scroll-y class="legal-content">
      <view class="section">
        <text class="update-date">更新日期：2026年5月13日</text>
        <text class="intro">慢小二（以下简称"本应用"）非常重视您的个人信息保护。本隐私政策将向您说明我们如何收集、使用、存储和保护您的个人信息。</text>
      </view>

      <view class="section">
        <text class="section-title">一、信息收集范围</text>
        <text class="paragraph">1. 账号信息：手机号、微信昵称、微信头像（微信登录时）。</text>
        <text class="paragraph">2. 健康档案：姓名、性别、年龄、身高、体重、血型、过敏史、既往病史、家族史。</text>
        <text class="paragraph">3. 医疗数据：检查报告图片、OCR识别的指标数据、用药计划、打卡记录、健康监测数据。</text>
        <text class="paragraph">4. 设备信息：设备型号、操作系统版本（用于兼容性适配）。</text>
      </view>

      <view class="section">
        <text class="section-title">二、信息使用目的</text>
        <text class="paragraph">1. 提供核心服务：慢病管理、用药提醒、报告解析、健康趋势分析。</text>
        <text class="paragraph">2. 医患协作：经您授权后，向绑定的医生展示您的健康数据。</text>
        <text class="paragraph">3. 服务优化：统计分析以改进产品体验（数据脱敏处理）。</text>
      </view>

      <view class="section">
        <text class="section-title">三、信息存储与保护</text>
        <text class="paragraph">1. 数据存储于安全的云服务器，采用加密传输（HTTPS）和加密存储。</text>
        <text class="paragraph">2. 敏感健康数据（身份证号、病史等）采用字段级加密存储。</text>
        <text class="paragraph">3. 未经您的同意，不会向任何第三方披露您的个人健康信息。</text>
      </view>

      <view class="section">
        <text class="section-title">四、您的权利</text>
        <text class="paragraph">1. 查阅与更正：您可随时查看和修改个人档案信息。</text>
        <text class="paragraph">2. 数据导出：您可通过"设置-导出数据"导出您的所有个人数据。</text>
        <text class="paragraph">3. 账号注销：您可通过"设置-注销账号"删除所有个人数据，操作不可逆。</text>
        <text class="paragraph">4. 撤回授权：您可在手机系统设置中撤回相关权限。</text>
      </view>

      <view class="section">
        <text class="section-title">五、联系我们</text>
        <text class="paragraph">如您对本隐私政策有任何疑问，可通过应用内"意见反馈"功能联系我们。</text>
      </view>

      <view class="safe-bottom" />
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
</script>

<style lang="scss" scoped>
.legal-page {
  min-height: 100vh;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
}

.legal-content {
  flex: 1;
  padding: 0 32rpx;
}

.section {
  margin-bottom: 40rpx;
}

.update-date {
  display: block;
  font-size: 24rpx;
  color: #94a3b8;
  margin-bottom: 20rpx;
}

.intro {
  font-size: 28rpx;
  color: #475569;
  line-height: 1.8;
}

.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16rpx;
}

.paragraph {
  display: block;
  font-size: 28rpx;
  color: #475569;
  line-height: 1.8;
  margin-bottom: 12rpx;
}

.safe-bottom {
  height: 120rpx;
}
</style>
