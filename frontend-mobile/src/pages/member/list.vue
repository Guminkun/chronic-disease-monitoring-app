<template>
  <view class="member-list-page">
    <scroll-view scroll-y class="scroll-container">
      <view class="member-list">
        <view
          v-for="member in memberStore.members"
          :key="member.id"
          class="member-item"
          :class="{ 'is-current': member.is_current }"
          @click="handleMemberClick(member)"
        >
          <view class="member-info">
            <text class="member-nickname">{{ member.nickname }}</text>
            <text class="member-relation">{{ member.relation }}</text>
          </view>
          
          <view class="member-actions">
            <view v-if="member.is_current" class="current-badge">
              <text>当前</text>
            </view>
            <view class="action-btn" @click.stop="handleEdit(member)">
              <text class="action-icon">✏️</text>
            </view>
            <view class="action-btn" @click.stop="handleDelete(member)">
              <text class="action-icon">🗑️</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="add-button-container">
        <view class="add-button" @click="handleAddMember">
          <text class="add-icon">+</text>
          <text class="add-text">新增成员</text>
        </view>
      </view>
      
      <view class="bottom-space"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { onShow } from '@dcloudio/uni-app'
import { useMemberStore } from '@/stores/member'
import { useUserStore } from '@/stores/user'
import type { Member } from '@/api/member'

const memberStore = useMemberStore()
const userStore = useUserStore()

onShow(() => {
  if (!userStore.token) {
    uni.showToast({
      title: '请先登录',
      icon: 'none'
    })
    setTimeout(() => {
      safeNavigate({ url: '/pages/login/login' })
    }, 1500)
    return
  }
  memberStore.loadMembers()
})

const handleMemberClick = async (member: Member) => {
  if (member.is_current) {
    uni.showToast({
      title: '已是当前成员',
      icon: 'none'
    })
    return
  }
  
  await memberStore.switchMember(member.id)
}

const handleEdit = (member: Member) => {
  uni.navigateTo({
    url: `/pages/member/edit?id=${member.id}`
  })
}

const handleDelete = (member: Member) => {
  if (member.is_current) {
    uni.showToast({
      title: '不能删除当前操作的成员',
      icon: 'none',
      duration: 2000
    })
    return
  }
  
  uni.showModal({
    title: '删除成员',
    content: `确定要删除"${member.nickname}"吗？该成员的所有健康数据将被永久删除。`,
    confirmColor: '#ef4444',
    success: async (res) => {
      if (res.confirm) {
        await memberStore.removeMember(member.id)
      }
    }
  })
}

const handleAddMember = () => {
  safeNavigate({ url: '/pages/member/add' })
}
</script>

<style scoped>
.member-list-page {
  min-height: 100vh;
  background: var(--color-bg-base);
}

.scroll-container {
  height: 100vh;
}

.member-list {
  padding: 16px;
  box-sizing: border-box;
}

.member-item {
  background: linear-gradient(180deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08), 0 12rpx 40rpx rgba(0, 0, 0, 0.12), 0 0 0 1rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(120, 130, 150, 0.18);
  transition: all 0.3s;
  box-sizing: border-box;
  overflow: hidden;
}

.member-item.is-current {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border: 2px solid #3b82f6;
}

.member-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.member-nickname {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.member-relation {
  font-size: 14px;
  color: #64748b;
}

.member-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-badge {
  background: #3b82f6;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.action-btn {
  width: 40px;
  height: 40px;
  background: #f1f5f9;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:active {
  transform: scale(0.95);
  background: #e2e8f0;
}

.action-icon {
  font-size: 18px;
}

.add-button-container {
  padding: 16px;
  padding-top: 0;
  box-sizing: border-box;
}

.add-button {
  background: linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.3);
  transition: all 0.3s;
  box-sizing: border-box;
}

.add-button:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.add-icon {
  font-size: 24px;
  color: white;
  font-weight: 300;
}

.add-text {
  font-size: 15px;
  color: white;
  font-weight: 600;
}

.bottom-space {
  height: 40px;
}
</style>
