<script setup lang="ts">
import { computed } from 'vue'
import ReviewResult from './ReviewResult.vue'
import { exportReport } from '../utils/export'
import type { Defect, RiskFilter } from '../types'

const props = defineProps<{
  defects: Defect[]
  code: string
  fileName: string
  langLabel: string
  risk: RiskFilter
}>()
const emit = defineEmits<{ (e: 'reset'): void }>()

const total = computed(() => props.defects.length)
</script>

<template>
  <div>
    <!-- 结果工具条 -->
    <div class="flex items-center justify-between mb-4 animate-fadeInUp">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-full flex items-center justify-center" style="background: #eef7f1; color: #16a34a">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M20 6 9 17l-5-5" /></svg>
        </div>
        <div>
          <div class="text-[15px] font-bold">审查完成</div>
          <div class="text-[12px]" style="color: var(--text-3)">双引擎融合 · 共检出 <span class="font-semibold" style="color: var(--text)">{{ total }}</span> 处缺陷</div>
        </div>
      </div>
      <div class="flex gap-2.5">
        <button class="btn-ghost" @click="exportReport('markdown', defects)">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12M7 10l5 5 5-5" /><path d="M4 21h16" /></svg>
          导出 Markdown
        </button>
        <button class="btn-ghost" @click="exportReport('html', defects)">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12M7 10l5 5 5-5" /><path d="M4 21h16" /></svg>
          导出 HTML 报告
        </button>
        <button class="btn-primary" style="padding: 10px 16px; font-size: 14px" @click="emit('reset')">重新审查</button>
      </div>
    </div>

    <ReviewResult :defects="defects" :code="code" :file-name="fileName" :lang-label="langLabel" :risk="risk" />
  </div>
</template>
