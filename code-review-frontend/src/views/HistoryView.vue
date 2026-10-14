<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchReviews, type ReviewListItem } from '../api/review'
import { langLabel, formatTime } from '../utils/format'

const router = useRouter()
const reviews = ref<ReviewListItem[]>([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    reviews.value = await fetchReviews()
  } catch {
    error.value = '无法连接后端，请确认后端已启动'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="card animate-fadeInUp">
    <div class="flex items-center justify-between px-5 py-4 border-b" style="border-color: var(--border)">
      <div class="text-[14px] font-bold">审查历史</div>
      <span class="text-[12px] font-medium px-2.5 py-1 rounded-full" style="background: var(--brand-soft); color: var(--brand)">{{ reviews.length }} 条记录</span>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="py-16 flex flex-col items-center text-[13px]" style="color: var(--text-3)">
      <div class="spinner" style="border-color: rgba(47,107,255,.25); border-top-color: var(--brand); margin-bottom: 10px"></div>
      加载中…
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="py-16 text-center">
      <div class="text-[14px] font-medium mb-1" style="color: var(--text)">{{ error }}</div>
      <div class="text-[12px] mb-5" style="color: var(--text-3)">请先在 backend 目录运行 python run.py</div>
      <button class="btn-ghost" @click="load">重试</button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="reviews.length === 0" class="py-16 text-center">
      <div class="mx-auto mb-3 w-12 h-12 rounded-xl flex items-center justify-center" style="background: var(--brand-soft); color: var(--brand)">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" /></svg>
      </div>
      <div class="text-[14px] font-medium mb-1">暂无审查记录</div>
      <div class="text-[12px] mb-5" style="color: var(--text-3)">完成一次审查后会自动保存在这里</div>
      <button class="btn-primary" style="padding: 10px 18px; font-size: 14px" @click="router.push('/workspace')">去新建审查</button>
    </div>

    <!-- 记录列表 -->
    <div v-else class="divide-y" style="border-color: var(--border)">
      <div v-for="r in reviews" :key="r.id" class="row-hover flex items-center gap-4 px-5 py-4" @click="router.push('/history/' + r.id)">
        <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-none" style="background: var(--brand-soft); color: var(--brand)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 6 2 12l6 6M16 6l6 6-6 6" /></svg>
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-[14px] font-semibold mono truncate">{{ r.file_name || '代码片段' }}</div>
          <div class="text-[12px]" style="color: var(--text-3)">{{ formatTime(r.created_at) }} · {{ langLabel(r.language) }}</div>
        </div>
        <div class="flex items-center gap-2">
          <span class="risk-badge risk-high"><span class="dot"></span>高危 {{ r.high }}</span>
          <span class="risk-badge risk-mid"><span class="dot"></span>中危 {{ r.mid }}</span>
          <span class="risk-badge risk-low"><span class="dot"></span>低危 {{ r.low }}</span>
          <span class="text-[12px] font-bold px-2.5 py-1 rounded-full" style="background: var(--surface-2); color: var(--text)">共 {{ r.total }} 处</span>
        </div>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--text-3)"><path d="m9 6 6 6-6 6" /></svg>
      </div>
    </div>
  </div>
</template>
