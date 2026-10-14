<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchReviewDetail, type ReviewDetail } from '../api/review'
import ReviewResult from '../components/ReviewResult.vue'
import { exportReport } from '../utils/export'
import { langLabel, formatTime } from '../utils/format'

const route = useRoute()
const router = useRouter()
const record = ref<ReviewDetail | null>(null)
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    record.value = await fetchReviewDetail(Number(route.params.id))
  } catch {
    error.value = '加载失败或记录不存在'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.params.id, load)
</script>

<template>
  <!-- 加载中 -->
  <div v-if="loading" class="card py-20 text-center text-[13px] animate-fadeInUp" style="color: var(--text-3)">
    <div class="spinner" style="border-color: rgba(47,107,255,.25); border-top-color: var(--brand); margin: 0 auto 10px"></div>
    加载中…
  </div>

  <!-- 错误 -->
  <div v-else-if="error" class="card py-16 text-center animate-fadeInUp">
    <div class="text-[14px] font-medium mb-4">{{ error }}</div>
    <button class="btn-primary" @click="router.push('/history')">返回审查历史</button>
  </div>

  <div v-else-if="record" class="animate-fadeInUp">
    <!-- 工具条 -->
    <div class="flex items-center justify-between mb-4">
      <button class="btn-ghost" @click="router.back()">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M11 18l-6-6 6-6" /></svg>
        返回历史
      </button>
      <div class="flex gap-2.5">
        <button class="btn-ghost" @click="exportReport('markdown', record.defects)">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12M7 10l5 5 5-5" /><path d="M4 21h16" /></svg>
          导出 Markdown
        </button>
        <button class="btn-ghost" @click="exportReport('html', record.defects)">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12M7 10l5 5 5-5" /><path d="M4 21h16" /></svg>
          导出 HTML
        </button>
        <button class="btn-primary" style="padding: 10px 16px; font-size: 14px" @click="router.push('/workspace')">重新审查</button>
      </div>
    </div>

    <!-- 元信息 -->
    <div class="card px-5 py-4 mb-5 flex items-center gap-4">
      <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-none" style="background: var(--brand-soft); color: var(--brand)">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 6 2 12l6 6M16 6l6 6-6 6" /></svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-[15px] font-bold mono truncate">{{ record.file_name || '代码片段' }}</div>
        <div class="text-[12px]" style="color: var(--text-3)">{{ formatTime(record.created_at) }} · {{ langLabel(record.language) }} · 耗时 {{ (record.duration_ms / 1000).toFixed(1) }}s</div>
      </div>
      <div class="flex items-center gap-2">
        <span class="risk-badge risk-high"><span class="dot"></span>高危 {{ record.high }}</span>
        <span class="risk-badge risk-mid"><span class="dot"></span>中危 {{ record.mid }}</span>
        <span class="risk-badge risk-low"><span class="dot"></span>低危 {{ record.low }}</span>
      </div>
    </div>

    <ReviewResult :defects="record.defects" :code="record.code" :file-name="record.file_name || '代码片段'" :lang-label="langLabel(record.language)" :risk="'all'" />
  </div>
</template>
