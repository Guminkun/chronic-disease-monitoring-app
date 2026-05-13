<template>
  <view class="legal-page">
    <PageHeader title="用户协议" />
    <scroll-view scroll-y class="legal-content">
      <view class="section">
        <text class="update-date">更新日期：2026年5月13日</text>
        <text class="intro">欢迎使用慢小二。请您在使用本应用前仔细阅读以下协议条款。</text>
      </view>

      <view class="section">
        <text class="section-title">一、服务说明</text>
        <text class="paragraph">慢小二是面向慢性病患者的健康管理工具，提供检查报告管理、用药提醒、健康指标监测、医患沟通等功能。本应用不提供医疗诊断服务，所有健康建议仅供参考。</text>
      </view>

      <view class="section">
        <text class="section-title">二、用户责任</text>
        <text class="paragraph">1. 您应确保注册信息的真实性，并妥善保管账号。</text>
        <text class="paragraph">2. 您上传的检查报告应为本人或经授权的家庭成员的真实医疗资料。</text>
        <text class="paragraph">3. 您不得利用本应用从事违法违规活动。</text>
      </view>

      <view class="section">
        <text class="section-title">三、免责声明</text>
        <text class="paragraph">1. OCR识别结果可能与原始报告存在偏差，请以医院出具的纸质报告为准。</text>
        <text class="paragraph">2. 用药提醒仅为辅助功能，不替代医生的专业用药指导。</text>
        <text class="paragraph">3. 本应用中的健康趋势分析不构成医疗建议，如有疑问请咨询专业医生。</text>
      </view>

      <view class="section">
        <text class="section-title">四、知识产权</text>
        <text class="paragraph">本应用的界面设计、图标、代码等知识产权归开发者所有。未经授权，不得复制、修改或分发。</text>
      </view>

      <view class="section">
        <text class="section-title">五、协议修改</text>
        <text class="paragraph">我们可能会不定期更新本协议，更新后的协议将在应用内公布。继续使用本应用即表示您同意更新后的条款。</text>
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
