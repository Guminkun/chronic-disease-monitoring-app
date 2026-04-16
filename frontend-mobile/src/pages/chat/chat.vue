<template>
  <view class="container">
    <view class="chat-list" :style="{ paddingBottom: '80px' }">
      <scroll-view 
        scroll-y 
        class="scroll-view" 
        :scroll-into-view="scrollIntoView"
        :scroll-with-animation="true"
        style="height: calc(100vh - 80px);"
      >
        <view v-for="(msg, index) in messages" :key="msg.id" :id="'msg-' + msg.id" class="message-item" :class="{ 'self': isSelf(msg) }">
          <view class="avatar">
            <text>{{ isSelf(msg) ? '我' : otherName[0] }}</text>
          </view>
          <view class="content-wrapper">
            <view class="bubble">
              <text>{{ msg.content }}</text>
            </view>
            <text class="time">{{ formatTime(msg.created_at) }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="input-area">
      <input 
        class="input" 
        v-model="inputContent" 
        type="text" 
        confirm-type="send" 
        placeholder="请输入消息..." 
        @confirm="handleSend"
      />
      <button class="send-btn" @click="handleSend" :disabled="!inputContent.trim()">发送</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { getMessages, sendMessage, type Message } from '@/api/chat'

const userStore = useUserStore()
const messages = ref<Message[]>([])
const inputContent = ref('')
const otherUserId = ref('')
const otherName = ref('对方')
const scrollIntoView = ref('')
let timer: any = null

const isSelf = (msg: Message) => {
  return msg.sender_id === userStore.user?.id
}

const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const fetchMessages = async () => {
  if (!otherUserId.value) return
  try {
    const res: any = await getMessages(otherUserId.value)
    if (res && res.length > 0) {
      // Check if new messages arrived to scroll
      const lastMsg = res[res.length - 1]
      const currentLast = messages.value[messages.value.length - 1]
      
      messages.value = res
      
      if (!currentLast || lastMsg.id !== currentLast.id) {
        scrollToBottom()
      }
    }
  } catch (error) {
    console.error('Fetch messages failed', error)
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messages.value.length > 0) {
      scrollIntoView.value = 'msg-' + messages.value[messages.value.length - 1].id
    }
  })
}

const handleSend = async () => {
  if (!inputContent.value.trim()) return
  
  const content = inputContent.value
  inputContent.value = '' // Optimistic clear
  
  try {
    await sendMessage({
      receiver_id: otherUserId.value,
      content: content
    })
    await fetchMessages()
    scrollToBottom()
  } catch (error) {
    uni.showToast({ title: '发送失败', icon: 'none' })
    inputContent.value = content // Restore on fail
  }
}

onLoad((options: any) => {
  if (options.id) {
    otherUserId.value = options.id
    otherName.value = options.name || '对方'
    uni.setNavigationBarTitle({
      title: otherName.value
    })
    fetchMessages()
    
    // Simple polling
    timer = setInterval(fetchMessages, 3000)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style>
.container {
  background-color: #f5f5f5;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-list {
  flex: 1;
  padding: 10px;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
  flex-direction: row;
}

.message-item.self {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  background-color: #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #64748b;
  flex-shrink: 0;
}

.message-item.self .avatar {
  background-color: #3b82f6;
  color: white;
}

.content-wrapper {
  max-width: 70%;
  margin: 0 10px;
  display: flex;
  flex-direction: column;
}

.message-item.self .content-wrapper {
  align-items: flex-end;
}

.bubble {
  background-color: white;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 16px;
  color: #1e293b;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.message-item.self .bubble {
  background-color: #3b82f6;
  color: white;
}

.time {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.input-area {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: white;
  padding: 10px 16px;
  padding-bottom: calc(10px + constant(safe-area-inset-bottom));
  padding-bottom: calc(10px + env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  border-top: 1px solid #e2e8f0;
}

.input {
  flex: 1;
  background-color: #f1f5f9;
  height: 40px;
  border-radius: 20px;
  padding: 0 16px;
  margin-right: 12px;
  font-size: 16px;
}

.send-btn {
  width: 70px;
  height: 40px;
  background-color: #3b82f6;
  color: white;
  border-radius: 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.send-btn:active {
  background-color: #2563eb;
}

.send-btn[disabled] {
  background-color: #94a3b8;
}
</style>
