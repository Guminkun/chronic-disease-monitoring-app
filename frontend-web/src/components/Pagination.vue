<template>
  <div class="pagination-container">
    <div class="pagination-info">
      <span class="total-text">共 <em>{{ total }}</em> 条</span>
      <div class="page-size-selector">
        <select v-model="localPageSize" @change="handlePageSizeChange" class="page-size-select">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">
            {{ size }} 条/页
          </option>
        </select>
      </div>
    </div>

    <div class="pagination-controls">
      <button
        class="page-btn nav-btn"
        :disabled="currentPage === 1"
        @click="goToPage(1)"
        title="首页"
      >
        <svg viewBox="0 0 24 24" class="btn-icon">
          <path d="M18.41 16.59L13.82 12l4.59-4.59L17 6l-6 6 6 6zM6 6h2v12H6z" fill="currentColor"/>
        </svg>
      </button>

      <button
        class="page-btn nav-btn"
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
        title="上一页"
      >
        <svg viewBox="0 0 24 24" class="btn-icon">
          <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" fill="currentColor"/>
        </svg>
      </button>

      <div class="page-numbers">
        <template v-for="(item, index) in displayedPages" :key="index">
          <span v-if="item === '...'" class="page-ellipsis">...</span>
          <button
            v-else
            class="page-btn"
            :class="{ active: item === currentPage }"
            @click="goToPage(item as number)"
          >
            {{ item }}
          </button>
        </template>
      </div>

      <button
        class="page-btn nav-btn"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
        title="下一页"
      >
        <svg viewBox="0 0 24 24" class="btn-icon">
          <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" fill="currentColor"/>
        </svg>
      </button>

      <button
        class="page-btn nav-btn"
        :disabled="currentPage === totalPages"
        @click="goToPage(totalPages)"
        title="末页"
      >
        <svg viewBox="0 0 24 24" class="btn-icon">
          <path d="M5.59 7.41L10.18 12l-4.59 4.59L7 18l6-6-6-6zM16 6h2v12h-2z" fill="currentColor"/>
        </svg>
      </button>
    </div>

    <div class="pagination-jumper">
      <span>跳至</span>
      <input
        type="number"
        v-model.number="jumpPage"
        @keyup.enter="handleJump"
        @blur="handleJumpBlur"
        class="jump-input"
        min="1"
        :max="totalPages"
      />
      <span>页</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  total: number
  currentPage: number
  pageSize: number
  pageSizeOptions?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  total: 0,
  currentPage: 1,
  pageSize: 10,
  pageSizeOptions: () => [10, 25, 50]
})

const emit = defineEmits<{
  (e: 'update:currentPage', page: number): void
  (e: 'update:pageSize', size: number): void
  (e: 'change', page: number, pageSize: number): void
}>()

const localPageSize = ref(props.pageSize)
const jumpPage = ref(props.currentPage)

watch(() => props.pageSize, (val) => {
  localPageSize.value = val
})

watch(() => props.currentPage, (val) => {
  jumpPage.value = val
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(props.total / localPageSize.value))
})

const displayedPages = computed(() => {
  const current = props.currentPage
  const total = totalPages.value
  const pages: (number | string)[] = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    pages.push(1)

    if (current <= 4) {
      for (let i = 2; i <= Math.min(5, total - 1); i++) {
        pages.push(i)
      }
      pages.push('...')
    } else if (current >= total - 3) {
      pages.push('...')
      for (let i = Math.max(2, total - 4); i <= total - 1; i++) {
        pages.push(i)
      }
    } else {
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
    }

    pages.push(total)
  }

  return pages
})

const goToPage = (page: number) => {
  const validPage = Math.max(1, Math.min(page, totalPages.value))
  if (validPage !== props.currentPage) {
    emit('update:currentPage', validPage)
    emit('change', validPage, localPageSize.value)
  }
}

const handlePageSizeChange = () => {
  emit('update:pageSize', localPageSize.value)
  const newTotalPages = Math.ceil(props.total / localPageSize.value)
  const newPage = Math.min(props.currentPage, newTotalPages)
  emit('update:currentPage', newPage)
  emit('change', newPage, localPageSize.value)
}

const handleJump = () => {
  let page = Math.floor(jumpPage.value)
  if (isNaN(page) || page < 1) {
    page = 1
  } else if (page > totalPages.value) {
    page = totalPages.value
  }
  jumpPage.value = page
  goToPage(page)
}

const handleJumpBlur = () => {
  if (!jumpPage.value || isNaN(jumpPage.value)) {
    jumpPage.value = props.currentPage
  }
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  padding: 16px 0;
  font-size: 14px;
  color: #606266;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.total-text {
  color: #909399;
}

.total-text em {
  font-style: normal;
  font-weight: 600;
  color: #409eff;
  margin: 0 2px;
}

.page-size-selector {
  position: relative;
}

.page-size-select {
  appearance: none;
  -webkit-appearance: none;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  padding: 6px 32px 6px 12px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23909399'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 20px;
}

.page-size-select:hover {
  border-color: #409eff;
}

.page-size-select:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.page-btn:hover:not(:disabled):not(.active) {
  color: #409eff;
  border-color: #409eff;
}

.page-btn:disabled {
  color: #c0c4cc;
  border-color: #e4e7ed;
  cursor: not-allowed;
  background: #f5f7fa;
}

.page-btn.active {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
  font-weight: 500;
}

.nav-btn {
  padding: 0;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-ellipsis {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  color: #909399;
}

.pagination-jumper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.jump-input {
  width: 50px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  text-align: center;
  transition: all 0.2s;
}

.jump-input::-webkit-outer-spin-button,
.jump-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.jump-input[type=number] {
  -moz-appearance: textfield;
}

.jump-input:hover {
  border-color: #409eff;
}

.jump-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

@media (max-width: 768px) {
  .pagination-container {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .pagination-info {
    justify-content: space-between;
  }

  .pagination-controls {
    justify-content: center;
    flex-wrap: wrap;
  }

  .pagination-jumper {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .page-numbers {
    gap: 4px;
  }

  .page-btn {
    min-width: 28px;
    height: 28px;
    font-size: 13px;
  }

  .nav-btn .btn-icon {
    width: 14px;
    height: 14px;
  }
}
</style>
