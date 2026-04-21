import { computed, ref } from 'vue'
import { addPatientReminder, deleteReminder, updateReminder, getPatientReminders, getMonitoringSubscribeMessageTemplate, confirmMonitoringSubscription, getMonitoringSubscriptionStatus } from '@/api/patient'
import { isLoggedIn, checkLoginWithRedirect } from '@/utils/auth'

export const MONITORING_METRIC_KEYS = [
  'blood_sugar',
  'blood_pressure',
  'heart_rate',
  'weight',
  'blood_lipids',
  'uric_acid'
] as const

export type MonitoringMetricType = (typeof MONITORING_METRIC_KEYS)[number]

export const METRIC_TYPE_LABELS: Record<MonitoringMetricType, string> = {
  blood_sugar: '血糖',
  blood_pressure: '血压',
  heart_rate: '心率',
  weight: '体重',
  blood_lipids: '血脂',
  uric_acid: '尿酸'
}

export function isMonitoringMetricType(s: string): s is MonitoringMetricType {
  return (MONITORING_METRIC_KEYS as readonly string[]).includes(s)
}

/** 与 `/patients/reminders` 列表项一致 */
export interface MonitoringReminderItem {
  id: number
  type: string
  title: string
  schedule_text?: string
  end_date?: string
  is_active: boolean
  patient_disease_id?: number
  created_at?: string
}

export function useMeasurementReminders() {
  const allReminders = ref<MonitoringReminderItem[]>([])
  const reminderPanelVisible = ref(false)
  const reminderType = ref<MonitoringMetricType>('blood_sugar')
  const reminderFormVisible = ref(false)
  const reminderEditTarget = ref<MonitoringReminderItem | null>(null)
  const reminderFormTime = ref('08:00')
  const reminderFormFreq = ref('每天')
  const reminderFormSaving = ref(false)
  const freqOptions = ['每天', '每两天', '每三天', '每周一次', '每周两次'] as const

  const getMetricReminders = (type: MonitoringMetricType) =>
    allReminders.value.filter(
      (r) => r.title.includes(METRIC_TYPE_LABELS[type]) && r.type === 'recheck'
    )

  const hasActiveReminder = (type: MonitoringMetricType) =>
    getMetricReminders(type).some((r) => r.is_active)

  const getReminderSummary = (type: MonitoringMetricType) => {
    const active = getMetricReminders(type).filter((r) => r.is_active)
    if (active.length === 0) return ''
    return active[0].schedule_text || active[0].title
  }

  const reminderPanelReminders = computed(() => getMetricReminders(reminderType.value))

  const loadReminders = async () => {
    if (!isLoggedIn()) {
      allReminders.value = []
      return
    }
    try {
      const res: unknown = await getPatientReminders()
      allReminders.value = Array.isArray(res) ? (res as MonitoringReminderItem[]) : []
    } catch {
      allReminders.value = []
    }
  }

  const openReminderPanel = (type: MonitoringMetricType) => {
    if (!isLoggedIn()) {
      checkLoginWithRedirect('/pages/monitor/index')
      return
    }
    reminderType.value = type
    reminderPanelVisible.value = true
  }

  const closeReminderPanel = () => {
    reminderPanelVisible.value = false
  }

  const openReminderForm = (item?: MonitoringReminderItem) => {
    if (!isLoggedIn()) {
      checkLoginWithRedirect('/pages/monitor/index')
      return
    }
    reminderEditTarget.value = item ?? null
    if (item?.schedule_text) {
      const parts = item.schedule_text.split(' ')
      reminderFormFreq.value = parts[0] || '每天'
      reminderFormTime.value = parts[1] || '08:00'
    } else {
      reminderFormFreq.value = '每天'
      reminderFormTime.value = '08:00'
    }
    reminderFormVisible.value = true
  }

  const closeReminderForm = () => {
    reminderFormVisible.value = false
  }

  const saveReminder = async () => {
    if (!isLoggedIn()) {
      checkLoginWithRedirect('/pages/monitor/index')
      return
    }
    if (reminderFormSaving.value) return
    reminderFormSaving.value = true
    const schedule = `${reminderFormFreq.value} ${reminderFormTime.value}`
    const label = METRIC_TYPE_LABELS[reminderType.value]
    const payload = {
      type: 'recheck' as const,
      title: `${label}测量提醒`,
      schedule_text: schedule,
      is_active: true
    }
    try {
      if (reminderEditTarget.value) {
        await updateReminder(reminderEditTarget.value.id, payload)
      } else {
        await addPatientReminder(payload)
      }
      await loadReminders()
      reminderFormVisible.value = false
      uni.showToast({ title: '提醒已保存', icon: 'success' })
      
      // 新增提醒后，自动请求订阅（如果订阅次数不足）
      if (!reminderEditTarget.value && subscriptionStatus.value.remaining_count <= 3) {
        setTimeout(() => {
          uni.showModal({
            title: '开启提醒通知',
            content: '需要订阅微信消息才能收到提醒，是否立即订阅？',
            confirmText: '立即订阅',
            cancelText: '稍后再说',
            success: async (res) => {
              if (res.confirm) {
                await handleRenew()
              }
            }
          })
        }, 500)
      }
    } catch {
      uni.showToast({ title: '保存失败', icon: 'none' })
    } finally {
      reminderFormSaving.value = false
    }
  }

  const toggleReminderActive = async (item: MonitoringReminderItem) => {
    if (!isLoggedIn()) {
      checkLoginWithRedirect('/pages/monitor/index')
      return
    }
    try {
      await updateReminder(item.id, {
        type: item.type as any,
        title: item.title,
        schedule_text: item.schedule_text,
        is_active: !item.is_active
      })
      await loadReminders()
    } catch {
      uni.showToast({ title: '操作失败', icon: 'none' })
    }
  }

  const removeReminder = (item: MonitoringReminderItem) => {
    if (!isLoggedIn()) {
      checkLoginWithRedirect('/pages/monitor/index')
      return
    }
    uni.showModal({
      title: '删除提醒',
      content: `确认删除「${item.title}」？`,
      success: async (res) => {
        if (!res.confirm) return
        try {
          await deleteReminder(item.id)
          await loadReminders()
          uni.showToast({ title: '已删除', icon: 'success' })
        } catch {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    })
  }

  // --- Subscription Management ---
  
  const subscriptionStatus = ref({
    is_subscribed: false,
    remaining_count: 0
  })

  const loadSubscriptionStatus = async () => {
    if (!isLoggedIn()) {
      subscriptionStatus.value = { is_subscribed: false, remaining_count: 0 }
      return
    }
    try {
      const res: any = await getMonitoringSubscriptionStatus()
      subscriptionStatus.value = {
        is_subscribed: res.is_subscribed || false,
        remaining_count: res.remaining_count || 0
      }
    } catch {
      subscriptionStatus.value = { is_subscribed: false, remaining_count: 0 }
    }
  }

  const requestSubscribeMessage = async (): Promise<boolean> => {
    // #ifdef MP-WEIXIN
    try {
      const templateRes: any = await getMonitoringSubscribeMessageTemplate()
      const templateId = templateRes.template_id
      
      if (!templateId) {
        uni.showToast({ title: '订阅消息模板未配置', icon: 'none' })
        return false
      }
      
      return new Promise((resolve) => {
        (uni as any).requestSubscribeMessage({
          tmplIds: [templateId],
          success: async (res: any) => {
            if (res[templateId] === 'accept') {
              try {
                const loginRes: any = await (uni as any).login()
                if (loginRes.code) {
                  await confirmMonitoringSubscription({
                    template_id: templateId,
                    code: loginRes.code
                  })
                  uni.showToast({ title: '订阅成功', icon: 'success' })
                  resolve(true)
                } else {
                  resolve(false)
                }
              } catch {
                resolve(false)
              }
            } else if (res[templateId] === 'reject') {
              uni.showToast({ title: '您拒绝了订阅', icon: 'none' })
              resolve(false)
            } else {
              uni.showToast({ title: '订阅已取消', icon: 'none' })
              resolve(false)
            }
          },
          fail: () => {
            uni.showToast({ title: '订阅失败，请稍后重试', icon: 'none' })
            resolve(false)
          }
        })
      })
    } catch {
      return false
    }
    // #endif
    
    // #ifndef MP-WEIXIN
    uni.showToast({ title: '仅支持微信小程序', icon: 'none' })
    return false
    // #endif
  }

  const handleRenew = async () => {
    const subscribed = await requestSubscribeMessage()
    if (subscribed) {
      await loadSubscriptionStatus()
    }
  }

  return {
    metricTypeLabel: METRIC_TYPE_LABELS,
    allReminders,
    loadReminders,
    getMetricReminders,
    hasActiveReminder,
    getReminderSummary,
    reminderPanelVisible,
    reminderType,
    reminderPanelReminders,
    reminderFormVisible,
    reminderEditTarget,
    reminderFormTime,
    reminderFormFreq,
    reminderFormSaving,
    freqOptions: [...freqOptions],
    openReminderPanel,
    closeReminderPanel,
    openReminderForm,
    closeReminderForm,
    saveReminder,
    toggleReminderActive,
    removeReminder,
    // Subscription management
    subscriptionStatus,
    loadSubscriptionStatus,
    requestSubscribeMessage,
    handleRenew
  }
}
