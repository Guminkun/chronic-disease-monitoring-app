<template>
  <view class="medication-page">
    <PageHeader :title="planId ? '编辑提醒' : (isTemporary ? '添加临时用药' : '添加提醒')" />

    <scroll-view scroll-y class="scroll-content">
      <!-- 药品信息卡片 -->
      <view class="form-card">
        <view class="card-header">
          <text class="card-title">药品信息</text>
        </view>
        
        <button class="scan-btn" @click="openRecognize">
          <text class="scan-btn-icon">📷</text>
          <text class="scan-btn-text">拍照/扫码识别药品</text>
        </button>
        
        <view class="divider">
          <view class="divider-line"></view>
          <text class="divider-text">或手动填写</text>
          <view class="divider-line"></view>
        </view>

        <view class="form-field">
          <text class="field-label">产品名称（通用名称）</text>
          <view class="field-input-wrapper">
            <input 
              class="field-input" 
              v-model="form.generic_name" 
              placeholder="请输入药品通用名称"
              @input="onNameInput" 
              @focus="onNameFocus" 
              @blur="onNameBlur" 
            />
          </view>
          <view v-if="suggestVisible && suggestions.length" class="suggest-list" @touchstart.stop @mousedown.stop>
            <view 
              v-for="item in suggestions" 
              :key="item.id" 
              class="suggest-item"
              @touchstart.stop.prevent="selectMedication(item)"
              @mousedown.stop.prevent="selectMedication(item)"
              @tap.stop="selectMedication(item)"
            >
              <view class="suggest-main">
                <text class="suggest-name">{{ item.generic_name || item.name }}</text>
                <text v-if="item.trade_name" class="suggest-trade">（{{ item.trade_name }}）</text>
              </view>
              <text v-if="item.specification" class="suggest-spec">{{ item.specification }}</text>
            </view>
          </view>
        </view>

        <view class="form-field">
          <text class="field-label">商品名称</text>
          <view class="field-input-wrapper">
            <input class="field-input" v-model="form.trade_name" placeholder="请输入商品名称（选填）" />
          </view>
        </view>

        <view class="form-field">
          <text class="field-label">生产单位</text>
          <view class="field-input-wrapper">
            <input class="field-input" v-model="form.manufacturer" placeholder="生产厂家" />
          </view>
        </view>

        <view class="form-row">
          <view class="form-field half">
            <text class="field-label">性状（剂型）</text>
            <view class="field-input-wrapper">
              <input class="field-input" v-model="form.properties" placeholder="如：片剂" />
            </view>
          </view>
          <view class="form-field half">
            <text class="field-label">规格</text>
            <view class="field-input-wrapper">
              <input class="field-input" v-model="form.specification" placeholder="如：0.25g*24片" />
            </view>
          </view>
        </view>
      </view>

      <!-- 用药类型选择 -->
      <view class="form-card">
        <view class="card-header">
          <text class="card-title">用药类型</text>
        </view>
        <view class="type-selector">
          <view class="type-option temporary" :class="{ active: isTemporary }" @click="setTemporary(true)">
            <text class="type-icon">⏰</text>
            <text class="type-name">临时用药</text>
            <text class="type-desc">短期疗程用药</text>
          </view>
          <view class="type-option" :class="{ active: !isTemporary }" @click="setTemporary(false)">
            <text class="type-icon">💊</text>
            <text class="type-name">长期用药</text>
            <text class="type-desc">慢性病长期服药</text>
          </view>
        </view>
      </view>

      <!-- 用药设置卡片 -->
      <view class="form-card">
        <view class="card-header">
          <text class="card-title">用药设置</text>
        </view>

        <view class="setting-row" @click="openUser">
          <text class="setting-label">用药人</text>
          <view class="setting-value">
            <text class="value-text">本人</text>
            <text class="value-arrow">›</text>
          </view>
        </view>

        <view class="setting-row" @click="openDiagnosis">
          <text class="setting-label">关联诊断</text>
          <view class="setting-value">
            <text class="value-text">{{ pickedDiseaseName || '不关联诊断' }}</text>
            <text class="value-arrow">›</text>
          </view>
        </view>
      </view>

      <!-- 临时用药时间设置 -->
      <view v-if="isTemporary" class="form-card">
        <view class="card-header">
          <text class="card-title">用药周期</text>
          <view class="temporary-badge">
            <text>临时用药</text>
          </view>
        </view>
        
        <view class="quick-duration">
          <view 
            v-for="opt in durationOptions" 
            :key="opt.value" 
            class="duration-chip"
            :class="{ active: quickDuration === opt.value }"
            @click="setQuickDuration(opt.value)"
          >
            <text>{{ opt.label }}</text>
          </view>
        </view>

        <view class="setting-row">
          <text class="setting-label">开始日期</text>
          <picker mode="date" :value="form.start_date" @change="onDateChange">
            <view class="setting-value">
              <text class="value-text">{{ form.start_date }}</text>
              <text class="value-arrow">›</text>
            </view>
          </picker>
        </view>

        <view class="setting-row">
          <text class="setting-label">结束日期</text>
          <picker mode="date" :value="form.end_date" :start="form.start_date" @change="onEndDateChange">
            <view class="setting-value">
              <text class="value-text" :class="{ warning: isEndDateNear }">{{ form.end_date || '选择结束日期' }}</text>
              <text class="value-arrow">›</text>
            </view>
          </picker>
        </view>

        <view v-if="durationDays > 0" class="duration-summary">
          <text class="summary-icon">📅</text>
          <text class="summary-text">共 {{ durationDays }} 天疗程</text>
        </view>
      </view>

      <!-- 用药信息设置卡片 -->
      <view class="form-card">
        <view class="card-header">
          <text class="card-title">用药信息设置</text>
        </view>

        <!-- 单次剂量 -->
        <view class="dose-setting">
          <text class="dose-label">单次剂量</text>
          <view class="dose-input-group">
            <input
              class="dose-input"
              type="digit"
              v-model="form.per_dose"
              placeholder="剂量"
            />
            <picker
              mode="selector"
              :range="doseUnits"
              :value="doseUnitIndex"
              @change="onDoseUnitChange"
            >
              <view class="dose-unit-picker">
                <text>{{ form.unit }}</text>
                <text class="picker-arrow">▾</text>
              </view>
            </picker>
          </view>
        </view>

        <!-- 余量 -->
        <view class="dose-setting">
          <text class="dose-label">余量</text>
          <view class="dose-input-group">
            <input
              class="dose-input"
              type="digit"
              v-model="form.stock"
              placeholder="余量"
            />
            <view class="dose-unit-readonly">
              <text>{{ form.unit }}</text>
            </view>
          </view>
        </view>

        <!-- 用药频率 -->
        <view class="setting-row" @click="openDosePreset">
          <text class="setting-label">用药频率</text>
          <view class="setting-value">
            <text class="value-text">{{ freqLabel }}</text>
            <text class="value-arrow">›</text>
          </view>
        </view>

        <!-- 用药时间 -->
        <view class="time-setting">
          <text class="time-label">用药时间</text>
          <view class="time-chips">
            <picker
              v-for="t in times"
              :key="t"
              mode="time"
              :value="t"
              @change="(e: any) => onEditTime(t, e)"
            >
              <view class="time-chip" :class="{ readonly: times.length <= 1 }">
                <text class="chip-time">{{ t }}</text>
                <text 
                  v-if="times.length > 1" 
                  class="chip-delete" 
                  @click.stop="removeTime(t)"
                >×</text>
              </view>
            </picker>
            <picker mode="time" :value="timePickerValue" @change="onAddTime">
              <view class="time-add-btn">
                <text class="add-icon">+</text>
              </view>
            </picker>
          </view>
        </view>

        <!-- 用药时段 -->
        <view class="setting-row" @click="openMealTime">
          <text class="setting-label">用药时段</text>
          <view class="setting-value">
            <text class="value-text">{{ mealLabel }}</text>
            <text class="value-arrow">›</text>
          </view>
        </view>

        <!-- 疗程 -->
        <view class="setting-row">
          <text class="setting-label">疗程</text>
          <view class="setting-value course-input-wrapper">
            <input
              class="course-input"
              v-model="courseDaysInput"
              type="number"
              placeholder="选填"
              @input="onCourseInput"
            />
            <text class="course-unit">天</text>
          </view>
        </view>
      </view>

      <!-- 提醒设置卡片 -->
      <view class="form-card">
        <view class="card-header">
          <text class="card-title">提醒设置</text>
        </view>

        <view class="setting-row">
          <text class="setting-label">开启用药提醒</text>
          <switch
            class="remind-switch"
            :checked="form.remind === 'on'"
            @change="onRemindSwitch"
            color="#2563eb"
          />
        </view>

        <template v-if="form.remind === 'on'">
          <view class="setting-row" @click="openRingtone">
            <text class="setting-label">提醒铃声</text>
            <view class="setting-value">
              <text class="value-text">{{ ringtone }}</text>
              <text class="value-arrow">›</text>
            </view>
          </view>

          <view class="setting-row" @click="openAdvance">
            <text class="setting-label">提前提醒</text>
            <view class="setting-value">
              <text class="value-text">{{ advanceLabel }}</text>
              <text class="value-arrow">›</text>
            </view>
          </view>
        </template>
      </view>

      <!-- 药品备注卡片 -->
      <view class="form-card">
        <view class="card-header">
          <text class="card-title">药品备注</text>
        </view>
        <textarea
          class="notes-textarea"
          v-model="form.notes_text"
          placeholder="请输入药品备注信息，如不良反应、禁忌症等（选填）"
          :maxlength="300"
          auto-height
        />
      </view>

      <view style="height: 140rpx;"></view>
    </scroll-view>

    <!-- 底部按钮 -->
    <view class="footer-bar">
      <button class="btn-cancel" @click="goBack">取消</button>
      <button class="btn-save" @click="handleConfirm">
        <text class="save-text">{{ planId ? '保存修改' : '保存药品' }}</text>
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'

const goBack = () => {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({ url: '/pages/index/index' })
    }
  })
}

import { computed, ref } from 'vue'
import { onShow, onLoad } from '@dcloudio/uni-app'
import { getDiseases } from '@/api/patient'
import * as medApi from '@/api/medication'
import { parseReport } from '@/api/report'
import { searchMedicationDict, type MedicationDictItem, type MedicationDictListResponse } from '@/api/medication_dict'

const isTemporary = ref(true)
const planId = ref<number | null>(null)
const diseaseList = ref<any[]>([])
const existingPlans = ref<any[]>([])
const doseUnits = ['片','粒','支','袋']
const doseUnitIndex = ref(0)
const pickedDiseaseId = ref<number | null>(null)
const pickedDiseaseName = ref('')
const freqType = ref<'daily'|'interval'>('daily')

const quickDuration = ref<number>(7)
const durationOptions = [
  { label: '3天', value: 3 },
  { label: '5天', value: 5 },
  { label: '7天', value: 7 },
  { label: '14天', value: 14 },
  { label: '30天', value: 30 }
]

const setTemporary = (val: boolean) => {
  isTemporary.value = val
  if (val) {
    // 切换到临时用药时，设置默认疗程
    if (!form.value.end_date) {
      setQuickDuration(7)
    }
  } else {
    // 切换到长期用药时，清空结束日期
    form.value.end_date = ''
  }
}

const setQuickDuration = (days: number) => {
  quickDuration.value = days
  const start = new Date(form.value.start_date || new Date())
  const end = new Date(start)
  end.setDate(end.getDate() + days - 1)
  form.value.end_date = end.toISOString().split('T')[0]
}

const onDateChange = (e: any) => {
  form.value.start_date = e.detail.value
  // 如果是临时用药且选择了快速疗程，自动更新结束日期
  if (isTemporary.value && quickDuration.value) {
    const start = new Date(form.value.start_date)
    const end = new Date(start)
    end.setDate(end.getDate() + quickDuration.value - 1)
    form.value.end_date = end.toISOString().split('T')[0]
  }
}

const onEndDateChange = (e: any) => {
  form.value.end_date = e.detail.value
  // 手动修改结束日期时，清除快速疗程选择
  quickDuration.value = 0
}

const durationDays = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 0
  const start = new Date(form.value.start_date)
  const end = new Date(form.value.end_date)
  const diff = Math.ceil((end.getTime() - start.getTime()) / (24 * 60 * 60 * 1000)) + 1
  return diff > 0 ? diff : 0
})

const isEndDateNear = computed(() => {
  if (!form.value.end_date) return false
  const end = new Date(form.value.end_date)
  const now = new Date()
  const diff = Math.ceil((end.getTime() - now.getTime()) / (24 * 60 * 60 * 1000))
  return diff <= 3 && diff >= 0
})

// 提醒设置
const ringtone = ref('默认铃声')
const advanceMinutes = ref(5)
const advanceLabel = computed(() => `${advanceMinutes.value}分钟`)

// 疗程
const courseDays = ref<number | null>(null)
const courseDaysInput = ref('')
const onCourseInput = (e: any) => {
  const v = Number(String(e?.detail?.value ?? '').trim())
  courseDays.value = Number.isFinite(v) && v > 0 ? v : null
}

// 用药时段
const mealOptions = ['饭前30分钟','饭后30分钟','饭中','空腹','不限']
const mealIndex = ref(1)
const mealLabel = computed(() => mealOptions[mealIndex.value])

// 用药频率
const freqOptions = ['每日1次','每日2次','每日3次','每日4次','隔日1次']
const freqIndex = ref(2)
const freqLabel = computed(() => freqOptions[freqIndex.value])

const todayStr = () => new Date().toISOString().split('T')[0]

const form = ref({
  name: '',
  generic_name: '',
  trade_name: '',
  manufacturer: '',
  properties: '',
  specification: '',
  per_day: 3,
  per_dose: 1,
  unit: doseUnits[0],
  route: '内服',
  meal: '饭后',
  start_date: todayStr(),
  end_date: '',
  interval_days: 2,
  stock: 0,
  remind: 'off' as 'on' | 'off',
  doctor: '',
  expiry_date: '',
  notes_text: ''
})

const suggestions = ref<MedicationDictItem[]>([])
const suggestVisible = ref(false)
const searching = ref(false)
const selecting = ref(false)
let searchTimer: number | undefined

const normalizeText = (v: string) => String(v || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()

const extractCandidates = (text: string) => {
  const clean = normalizeText(text)
  const tokens: string[] = []
  const zh = clean.match(/[\u4e00-\u9fa5]{2,20}/g) || []
  const an = clean.match(/[A-Za-z0-9\-\(\)·]{3,30}/g) || []
  tokens.push(...zh, ...an)
  const uniq = Array.from(new Set(tokens.map(t => t.trim()).filter(Boolean)))
  uniq.sort((a, b) => b.length - a.length)
  return uniq.slice(0, 8)
}

const fillFromDict = (item: MedicationDictItem) => {
  form.value.generic_name = item.generic_name || item.name || form.value.generic_name
  form.value.trade_name = item.trade_name || ''
  form.value.name = item.generic_name || item.name || form.value.name
  form.value.manufacturer = item.manufacturer || ''
  form.value.properties = item.properties || ''
  form.value.specification = item.specification || ''
}

const searchDict = async (q: string) => {
  const keyword = String(q || '').trim()
  if (!keyword) { suggestions.value = []; return }
  searching.value = true
  try {
    const result = await searchMedicationDict({ q: keyword, skip: 0, limit: 8 })
    // 后端返回 { items: [], total: number } 格式
    const list = Array.isArray(result) ? result : (result as any)?.items || []
    suggestions.value = list.filter((x: any) => x?.status !== 'inactive')
  } catch { suggestions.value = [] }
  finally { searching.value = false }
}

const onNameInput = (e: any) => {
  const v = String(e?.detail?.value ?? form.value.generic_name ?? '')
  form.value.generic_name = v
  form.value.name = v
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => searchDict(v), 250) as unknown as number
}
const onNameFocus = () => { suggestVisible.value = true; if (form.value.generic_name) searchDict(form.value.generic_name) }
const onNameBlur = () => { setTimeout(() => { if (selecting.value) return; suggestVisible.value = false }, 250) }
const selectMedication = (item: MedicationDictItem) => {
  selecting.value = true
  fillFromDict(item)
  suggestVisible.value = false
  setTimeout(() => { selecting.value = false }, 0)
  uni.showToast({ title: '已从药品库回填', icon: 'none' })
}

const openid = ref('')

const requestSubscribeMessage = async () => {
  // #ifdef MP-WEIXIN
  try {
    const templateRes: any = await medApi.getSubscribeMessageTemplate()
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
                const confirmData: medApi.ConfirmSubscriptionData = {
                  template_id: templateId,
                  code: loginRes.code
                }
                await medApi.confirmSubscription(confirmData)
                uni.showToast({ title: '订阅成功', icon: 'success' })
                resolve(true)
              } else {
                resolve(false)
              }
            } catch (e) {
              console.error('Confirm subscription error:', e)
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
        fail: (err: any) => {
          console.error('Request subscribe message failed:', err)
          uni.showToast({ title: '订阅失败，请稍后重试', icon: 'none' })
          resolve(false)
        }
      })
    })
  } catch (e) {
    console.error('Get template error:', e)
    return false
  }
  // #endif
  
  // #ifndef MP-WEIXIN
  uni.showToast({ title: '仅支持微信小程序', icon: 'none' })
  return false
  // #endif
}

const onRemindSwitch = async (e: any) => {
  const newValue = e?.detail?.value ? 'on' : 'off'
  
  if (newValue === 'on') {
    const subscribed = await requestSubscribeMessage()
    if (subscribed) {
      form.value.remind = 'on'
    } else {
      form.value.remind = 'off'
    }
  } else {
    form.value.remind = 'off'
  }
}


const times = ref<string[]>(['08:00', '12:00', '18:00'])
const timePickerValue = computed(() => times.value[times.value.length - 1] || '08:00')

const onAddTime = (e: any) => {
  const t = String(e.detail.value || '').trim()
  if (!t || times.value.includes(t)) return
  times.value = [...times.value, t].sort()
}
const onEditTime = (oldTime: string, e: any) => {
  if (times.value.length <= 1) return
  const newTime = String(e.detail.value || '').trim()
  if (!newTime || newTime === oldTime) return
  if (times.value.includes(newTime)) {
    uni.showToast({ title: '该时间已存在', icon: 'none' })
    return
  }
  times.value = times.value.map(x => x === oldTime ? newTime : x).sort()
}
const removeTime = (t: string) => {
  if (times.value.length <= 1) return
  times.value = times.value.filter(x => x !== t)
}

const openDosePreset = () => {
  uni.showActionSheet({
    itemList: freqOptions,
    success: (res: any) => { freqIndex.value = res.tapIndex }
  })
}

const onDoseUnitChange = (e: any) => {
  const idx = Number(e.detail.value)
  doseUnitIndex.value = idx
  form.value.unit = doseUnits[idx]
}

const openMealTime = () => {
  uni.showActionSheet({
    itemList: mealOptions,
    success: (res: any) => { mealIndex.value = res.tapIndex }
  })
}

const openRingtone = () => {
  uni.showActionSheet({
    itemList: ['默认铃声','清脆提示音','轻柔提示音'],
    success: (res: any) => {
      ringtone.value = ['默认铃声','清脆提示音','轻柔提示音'][res.tapIndex]
    }
  })
}

const openAdvance = () => {
  uni.showActionSheet({
    itemList: ['5分钟','10分钟','15分钟','30分钟'],
    success: (res: any) => {
      advanceMinutes.value = [5, 10, 15, 30][res.tapIndex]
    }
  })
}

const openDiagnosis = () => {
  const items = ['不关联诊断', ...diseaseList.value.map(d => d?.name).filter(Boolean)]
  uni.showActionSheet({
    itemList: items,
    success: (res: any) => {
      if (res.tapIndex === 0) { pickedDiseaseId.value = null; pickedDiseaseName.value = ''; return }
      const name = items[res.tapIndex]
      const d = diseaseList.value.find(x => x?.name === name)
      pickedDiseaseId.value = d?.id ?? null
      pickedDiseaseName.value = d?.name ?? ''
    }
  })
}

const openUser = () => uni.showToast({ title: '当前仅支持本人', icon: 'none' })

const recognizeFromPhoto = () => {
  uni.chooseImage({
    count: 1, sourceType: ['camera', 'album'],
    success: async (res: any) => {
      const filePath = res?.tempFilePaths?.[0]
      if (!filePath) return
      try {
        uni.showLoading({ title: '识别中' })
        const parsed: any = await parseReport(filePath)
        const summary = normalizeText(parsed?.summary || '')
        const candidates = extractCandidates(summary)
        for (const c of candidates) {
          const result = await searchMedicationDict({ q: c, skip: 0, limit: 5 })
          const list = Array.isArray(result) ? result : result?.items || []
          if (list.length) { fillFromDict(list[0]); uni.showToast({ title: '已识别并回填', icon: 'none' }); return }
        }
        if (candidates.length && !form.value.name) form.value.name = candidates[0]
        uni.showToast({ title: '库中未找到，请手动填写', icon: 'none' })
      } catch { uni.showToast({ title: '识别失败', icon: 'none' }) }
      finally { uni.hideLoading() }
    }
  })
}

const recognizeFromScan = () => {
  uni.scanCode({
    success: async (res: any) => {
      const code = String(res?.result || '').trim()
      if (!code) return
      try {
        uni.showLoading({ title: '查询中' })
        const result = await searchMedicationDict({ q: code, skip: 0, limit: 5 })
        const list = Array.isArray(result) ? result : result?.items || []
        if (list.length) { fillFromDict(list[0]); uni.showToast({ title: '已从药品库回填', icon: 'none' }); return }
        form.value.name = code
        uni.showToast({ title: '库中未找到，请手动填写', icon: 'none' })
      } catch { uni.showToast({ title: '查询失败', icon: 'none' }) }
      finally { uni.hideLoading() }
    },
    fail: () => uni.showToast({ title: '扫码已取消', icon: 'none' })
  })
}

const openRecognize = () => {
  uni.showActionSheet({
    itemList: ['拍照识别', '扫码识别'],
    success: (res: any) => {
      if (res.tapIndex === 0) recognizeFromPhoto()
      if (res.tapIndex === 1) recognizeFromScan()
    }
  })
}

const validate = () => {
  if (!form.value.generic_name && !form.value.name) { uni.showToast({ title: '请输入药品名称', icon: 'none' }); return false }
  if (!times.value.length) { uni.showToast({ title: '请设置用药时间', icon: 'none' }); return false }
  if (!form.value.start_date) { uni.showToast({ title: '请选择开始时间', icon: 'none' }); return false }
  return true
}

const handleConfirm = async () => {
  if (!validate()) return
  const displayName = form.value.trade_name
    ? `${form.value.generic_name}（${form.value.trade_name}）`
    : form.value.generic_name || form.value.name
  
  // 检查是否已存在相同药品（仅新增时检查，编辑时跳过）
  if (!planId.value) {
    const isDuplicate = existingPlans.value.some((plan: any) => {
      const existingName = plan.name || ''
      return existingName === displayName || 
             existingName === form.value.generic_name ||
             (plan.generic_name && plan.generic_name === form.value.generic_name)
    })
    
    if (isDuplicate) {
      uni.showModal({
        title: '药品已存在',
        content: `药品"${displayName}"已在用药列表中，请勿重复添加。`,
        showCancel: false,
        confirmText: '我知道了'
      })
      return
    }
  }
  
  const payload: medApi.MedicationPlan = {
    name: displayName,
    manufacturer: form.value.manufacturer,
    stock: form.value.stock,
    dosage_amount: form.value.per_dose,
    dosage_unit: form.value.unit,
    frequency_type: freqType.value,
    frequency_value: freqType.value === 'interval' ? String(form.value.interval_days) : undefined,
    taken_times: times.value,
    timing_condition: mealOptions[mealIndex.value],
    start_date: form.value.start_date,
    end_date: form.value.end_date || undefined,
    duration_days: courseDays.value || undefined,
    patient_disease_id: pickedDiseaseId.value || undefined,
    notes: form.value.notes_text || undefined,
    is_temporary: isTemporary.value
  }
  try {
    uni.showLoading({ title: '保存中' })
    if (planId.value) { await medApi.updatePlan(planId.value, payload) }
    else { await medApi.createPlan(payload) }
    uni.hideLoading()
    uni.showToast({ title: '已保存', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack({
        fail: () => {
          uni.redirectTo({ url: '/pages/medication/index' })
        }
      })
    }, 1000)
  } catch (e) {
    uni.hideLoading()
    console.error('保存失败:', e)
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

const loadDiseases = async () => {
  try {
    const list: any = await getDiseases()
    diseaseList.value = Array.isArray(list) ? list : (list?.data || [])
  } catch { diseaseList.value = [] }
}

const loadExistingPlans = async () => {
  try {
    const res: any = await medApi.getPlans()
    existingPlans.value = Array.isArray(res) ? res : (res?.data || [])
  } catch { 
    existingPlans.value = [] 
  }
}

const loadPlanDetails = async (id: number) => {
  try {
    const plans: any = await medApi.getPlans()
    const list = Array.isArray(plans) ? plans : (plans?.data || [])
    const plan = list.find((p: any) => p.id === id)
    if (!plan) return
    
    // 设置用药类型
    isTemporary.value = plan.is_temporary || false
    
    const planName = plan.name || ''
    const match = planName.match(/^(.+?)（(.+?)）$/)
    if (match) {
      form.value.generic_name = match[1]
      form.value.trade_name = match[2]
    } else {
      form.value.generic_name = planName
      form.value.trade_name = ''
    }
    form.value.name = planName
    
    form.value.manufacturer = plan.manufacturer || ''
    form.value.per_dose = plan.dosage_amount
    form.value.unit = plan.dosage_unit
    form.value.start_date = plan.start_date
    form.value.end_date = plan.end_date || ''
    times.value = plan.taken_times || []
    pickedDiseaseId.value = plan.patient_disease_id
    freqType.value = plan.frequency_type === 'interval' ? 'interval' : 'daily'
    form.value.interval_days = plan.frequency_type === 'interval' ? Number(plan.frequency_value) : 2
    form.value.stock = plan.stock || 0
    form.value.notes_text = plan.notes || ''
    const freqMap: Record<number, number> = {1:0, 2:1, 3:2, 4:3}
    freqIndex.value = freqMap[times.value.length] ?? 2
  } catch (e) { console.error('Failed to load plan details', e) }
}

onLoad((options: any) => {
  if (options.id) {
    // 编辑模式：加载药品详情
    planId.value = Number(options.id)
    loadPlanDetails(planId.value)
  } else {
    // 新增模式：默认临时用药，设置默认疗程
    isTemporary.value = true
    if (!form.value.end_date) {
      setQuickDuration(7)
    }
    
    // 从药品说明页传递的参数预填充
    if (options.generic_name) form.value.generic_name = decodeURIComponent(options.generic_name)
    if (options.trade_name) form.value.trade_name = decodeURIComponent(options.trade_name)
    if (options.manufacturer) form.value.manufacturer = decodeURIComponent(options.manufacturer)
    if (options.properties) form.value.properties = decodeURIComponent(options.properties)
    if (options.specification) form.value.specification = decodeURIComponent(options.specification)
    
    // 用法用量和其他重要信息合并到备注
    const notes: string[] = []
    if (options.usage_dosage) notes.push('参考用法：' + decodeURIComponent(options.usage_dosage))
    if (options.adverse_reactions) notes.push('不良反应：' + decodeURIComponent(options.adverse_reactions))
    if (options.precautions) notes.push('注意事项：' + decodeURIComponent(options.precautions))
    if (notes.length > 0) form.value.notes_text = notes.join('\n\n')
  }
  if (options.mode === 'temporary') {
    isTemporary.value = true
    form.value.meal = '不限'
  }
})
onShow(() => {
  loadDiseases()
  loadExistingPlans()
})
</script>

<style lang="scss" scoped>
/* 页面容器 */
.medication-page {
  min-height: 100vh;
  background: #eef2f7;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */






/* 滚动内容 */
.scroll-content {
  flex: 1;
  padding: 24rpx 32rpx;
  box-sizing: border-box;
}

/* 表单卡片 */
.form-card {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.04);
}

.card-header {
  margin-bottom: 28rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0f172a;
}

/* 扫码按钮 */
.scan-btn {
  width: 100%;
  height: 88rpx;
  border-radius: 20rpx;
  background: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
  border: none;
  padding: 0;
  box-shadow: 0 8rpx 24rpx rgba(37, 99, 235, 0.3);
}

.scan-btn::after {
  border: none;
}

.scan-btn-icon {
  font-size: 32rpx;
}

.scan-btn-text {
  color: #ffffff;
  font-weight: 600;
  font-size: 28rpx;
}

/* 分割线 */
.divider {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin: 24rpx 0 16rpx;
}

.divider-line {
  height: 1rpx;
  background: rgba(148, 163, 184, 0.3);
  flex: 1;
}

.divider-text {
  color: #94a3b8;
  font-size: 24rpx;
}

/* 表单字段 */
.form-field {
  margin-top: 20rpx;
  position: relative;
}

.form-field.half {
  flex: 1;
  margin-top: 0;
}

.field-label {
  font-size: 24rpx;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 12rpx;
  display: block;
}

.field-input-wrapper {
  height: 88rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  border-radius: 16rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  transition: all 0.3s;
}

.field-input-wrapper:focus-within {
  border-color: #2563eb;
  background: #ffffff;
  box-shadow: 0 0 0 6rpx rgba(37, 99, 235, 0.1);
}

.field-input {
  flex: 1;
  font-size: 28rpx;
  color: #1e293b;
}

.form-row {
  display: flex;
  gap: 24rpx;
  margin-top: 20rpx;
}

/* 搜索建议 */
.suggest-list {
  position: absolute;
  left: 0;
  right: 0;
  top: 100%;
  background: #ffffff;
  border-radius: 16rpx;
  border: 2rpx solid #e2e8f0;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 20;
  margin-top: 8rpx;
}

.suggest-item {
  padding: 20rpx 24rpx;
  border-top: 1rpx solid #f1f5f9;
}

.suggest-item:first-child {
  border-top: none;
}

.suggest-main {
  display: flex;
  align-items: baseline;
  gap: 8rpx;
}

.suggest-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #1e293b;
}

.suggest-trade {
  font-size: 24rpx;
  color: #2563eb;
}

.suggest-spec {
  font-size: 22rpx;
  color: #64748b;
  margin-top: 6rpx;
  display: block;
}

/* 设置行 */
.setting-row {
  min-height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1rpx solid #f1f5f9;
}

.setting-row:first-of-type {
  border-top: none;
}

.setting-label {
  font-size: 28rpx;
  color: #1e293b;
  font-weight: 500;
}

.setting-value {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.value-text {
  font-size: 28rpx;
  color: #64748b;
  max-width: 320rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.value-arrow {
  font-size: 32rpx;
  color: #cbd5e1;
  line-height: 1;
}

/* 剂量设置 */
.dose-setting {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 88rpx;
  border-top: 1rpx solid #f1f5f9;
}

.dose-setting:first-of-type {
  border-top: none;
}

.dose-label {
  font-size: 28rpx;
  color: #1e293b;
  font-weight: 500;
}

.dose-input-group {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.dose-input {
  width: 140rpx;
  height: 64rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
  text-align: center;
}

.dose-unit-picker {
  height: 64rpx;
  min-width: 100rpx;
  padding: 0 20rpx;
  background: #e2e8f0;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  font-size: 26rpx;
  font-weight: 600;
  color: #64748b;
}

.picker-arrow {
  font-size: 20rpx;
  color: #94a3b8;
}

.dose-unit-readonly {
  height: 64rpx;
  min-width: 100rpx;
  padding: 0 20rpx;
  background: #e2e8f0;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 600;
  color: #64748b;
}

/* 用药时间 */
.time-setting {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 88rpx;
  border-top: 1rpx solid #f1f5f9;
}

.time-label {
  font-size: 28rpx;
  color: #1e293b;
  font-weight: 500;
}

.time-chips {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12rpx;
  justify-content: flex-end;
  flex: 1;
  margin-left: 24rpx;
}

.time-chip {
  height: 56rpx;
  padding: 0 20rpx;
  border-radius: 28rpx;
  background: rgba(37, 99, 235, 0.1);
  border: 2rpx solid rgba(37, 99, 235, 0.3);
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.time-chip.readonly {
  background: #f1f5f9;
  border-color: rgba(148, 163, 184, 0.3);
}

.time-chip.readonly .chip-time {
  color: #64748b;
}

.chip-time {
  font-size: 24rpx;
  font-weight: 600;
  color: #2563eb;
}

.chip-delete {
  font-size: 28rpx;
  color: #94a3b8;
  line-height: 1;
}

.time-add-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 28rpx;
  background: #ffffff;
  border: 2rpx dashed #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-icon {
  font-size: 36rpx;
  color: #94a3b8;
  line-height: 1;
  font-weight: 300;
}

/* 疗程输入 */
.course-input-wrapper {
  gap: 8rpx;
}

.course-input {
  width: 120rpx;
  height: 56rpx;
  border-radius: 12rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  padding: 0 16rpx;
  font-size: 26rpx;
  color: #1e293b;
  text-align: right;
}

.course-unit {
  font-size: 26rpx;
  color: #64748b;
}

/* 提醒开关 */
.remind-switch {
  transform: scale(0.85);
}

/* 备注文本域 */
.notes-textarea {
  width: 100%;
  min-height: 160rpx;
  background: #f8fafc;
  border-radius: 16rpx;
  border: 2rpx solid #e2e8f0;
  padding: 20rpx;
  box-sizing: border-box;
  font-size: 28rpx;
  color: #1e293b;
  line-height: 1.6;
}

/* 底部按钮栏 */
.footer-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 24rpx 32rpx;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20rpx);
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  box-sizing: border-box;
  display: flex;
  gap: 24rpx;
  box-shadow: 0 -8rpx 32rpx rgba(0, 0, 0, 0.08);
}

.btn-cancel {
  flex: 1;
  height: 96rpx;
  border-radius: 20rpx;
  background: #ffffff;
  border: 2rpx solid #e2e8f0;
  color: #64748b;
  font-size: 30rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
}

.btn-cancel::after {
  border: none;
}

.btn-save {
  flex: 2;
  height: 96rpx;
  border-radius: 20rpx;
  background: #2563eb;
  color: #ffffff;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  border: none;
  box-shadow: 0 8rpx 24rpx rgba(37, 99, 235, 0.3);
}

.btn-save::after {
  border: none;
}

.save-text {
  color: #ffffff;
}

/* 用药类型选择 */
.type-selector {
  display: flex;
  gap: 16rpx;
}

.type-option {
  flex: 1;
  padding: 24rpx;
  border-radius: 20rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  transition: all 0.3s;
}

.type-option.active {
  background: #eff6ff;
  border-color: #2563eb;
  box-shadow: 0 8rpx 24rpx rgba(37, 99, 235, 0.15);
}

.type-option.temporary.active {
  background: #fff7ed;
  border-color: #f97316;
  box-shadow: 0 8rpx 24rpx rgba(249, 115, 22, 0.15);
}

.type-icon {
  font-size: 40rpx;
}

.type-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #1e293b;
}

.type-desc {
  font-size: 22rpx;
  color: #64748b;
}

.temporary-badge {
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  background: #fff7ed;
  border: 1rpx solid rgba(249, 115, 22, 0.3);
}

.temporary-badge text {
  font-size: 22rpx;
  font-weight: 600;
  color: #f97316;
}

/* 快速选择疗程 */
.quick-duration {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.duration-chip {
  padding: 16rpx 28rpx;
  border-radius: 16rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  font-size: 26rpx;
  font-weight: 600;
  color: #64748b;
  transition: all 0.3s;
}

.duration-chip.active {
  background: #fff7ed;
  border-color: #f97316;
  color: #f97316;
}

/* 疗程摘要 */
.duration-summary {
  margin-top: 20rpx;
  padding: 20rpx 24rpx;
  background: #fff7ed;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.summary-icon {
  font-size: 28rpx;
}

.summary-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #f97316;
}

.value-text.warning {
  color: #f97316;
  font-weight: 600;
}
</style>
