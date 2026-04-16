import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Member, MemberFormData } from '@/api/member'
import {
  getMembers,
  getMember,
  createMember,
  updateMember,
  deleteMember,
  setCurrentMember,
  getCurrentMember
} from '@/api/member'

export const useMemberStore = defineStore('member', () => {
  const members = ref<Member[]>([])
  const currentMember = ref<Member | null>(null)
  const loading = ref(false)

  const loadMembers = async () => {
    loading.value = true
    try {
      const data: any = await getMembers()
      members.value = Array.isArray(data) ? data : []
      const current = members.value.find(m => m.is_current)
      currentMember.value = current || (members.value.length > 0 ? members.value[0] : null)
    } catch (e) {
      console.error('Failed to load members:', e)
      uni.showToast({
        title: '加载成员列表失败',
        icon: 'none'
      })
    } finally {
      loading.value = false
    }
  }

  const addMember = async (data: MemberFormData) => {
    try {
      console.log('Adding member with data:', JSON.stringify(data))
      const newMember: any = await createMember(data)
      members.value.push(newMember)
      uni.showToast({
        title: '添加成功',
        icon: 'success'
      })
      return newMember
    } catch (e) {
      console.error('Failed to add member:', e)
      uni.showToast({
        title: '添加失败',
        icon: 'none'
      })
      return null
    }
  }

  const editMember = async (id: string, data: Partial<MemberFormData>) => {
    try {
      const updatedMember: any = await updateMember(id, data)
      if (updatedMember) {
        const index = members.value.findIndex(m => m.id === id)
        if (index !== -1) {
          members.value[index] = updatedMember
        }
        if (currentMember.value?.id === id) {
          currentMember.value = updatedMember
        }
        uni.showToast({
          title: '更新成功',
          icon: 'success'
        })
        return updatedMember
      }
      return null
    } catch (e) {
      console.error('Failed to update member:', e)
      uni.showToast({
        title: '更新失败',
        icon: 'none'
      })
      return null
    }
  }

  const removeMember = async (id: string) => {
    try {
      await deleteMember(id)
      members.value = members.value.filter(m => m.id !== id)
      uni.showToast({
        title: '删除成功',
        icon: 'success'
      })
      return true
    } catch (e) {
      console.error('Failed to delete member:', e)
      uni.showToast({
        title: '删除失败',
        icon: 'none'
      })
      return false
    }
  }

  const switchMember = async (id: string) => {
    try {
      await setCurrentMember(id)
      members.value.forEach(m => {
        m.is_current = m.id === id
      })
      currentMember.value = members.value.find(m => m.id === id) || null
      uni.showToast({
        title: '已切换成员',
        icon: 'success'
      })
      return true
    } catch (e) {
      console.error('Failed to switch member:', e)
      uni.showToast({
        title: '切换失败',
        icon: 'none'
      })
      return false
    }
  }

  const loadCurrentMember = async () => {
    try {
      const data: any = await getCurrentMember()
      currentMember.value = data
    } catch (e) {
      console.error('Failed to load current member:', e)
    }
  }

  return {
    members,
    currentMember,
    loading,
    loadMembers,
    addMember,
    editMember,
    removeMember,
    switchMember,
    loadCurrentMember
  }
})
