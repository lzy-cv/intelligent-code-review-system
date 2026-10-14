<script setup lang="ts">
import { toast } from '../utils/toast'

const reports = [
  { name: 'user-service-审查报告.md', format: 'Markdown', size: '8.4 KB', time: '2026-10-09 14:35' },
  { name: 'order-api-审查报告.html', format: 'HTML', size: '22.1 KB', time: '2026-10-08 10:20' },
  { name: 'admin-web-审查报告.md', format: 'Markdown', size: '11.2 KB', time: '2026-10-06 09:02' },
]

function download(name: string) {
  toast(`已模拟下载「${name}」`, 'success')
}
</script>

<template>
  <div class="card animate-fadeInUp">
    <div class="flex items-center justify-between px-5 py-4 border-b" style="border-color: var(--border)">
      <div class="text-[14px] font-bold">报告中心</div>
      <span class="text-[12px] font-medium px-2.5 py-1 rounded-full" style="background: var(--brand-soft); color: var(--brand)">{{ reports.length }} 份报告</span>
    </div>

    <div class="divide-y" style="border-color: var(--border)">
      <div v-for="r in reports" :key="r.name" class="flex items-center gap-4 px-5 py-4">
        <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-none" :style="r.format === 'Markdown' ? 'background:#eef7f1;color:#16a34a' : 'background:#fff7ed;color:#c2410c'">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" /><path d="M14 2v6h6" /></svg>
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-[14px] font-semibold mono truncate">{{ r.name }}</div>
          <div class="text-[12px]" style="color: var(--text-3)">{{ r.time }} · {{ r.size }}</div>
        </div>
        <span class="text-[11px] px-2 py-0.5 rounded-full font-medium" style="background: var(--surface-2); color: var(--text-2)">{{ r.format }}</span>
        <button class="btn-ghost" style="padding: 8px 14px; font-size: 13px" @click="download(r.name)">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12M7 10l5 5 5-5" /><path d="M4 21h16" /></svg>
          下载
        </button>
      </div>
    </div>
  </div>
</template>
