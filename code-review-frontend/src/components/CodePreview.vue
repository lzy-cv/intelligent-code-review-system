<script setup lang="ts">
import { computed, ref } from 'vue'
import { highlightLine } from '../utils/highlight'
import type { Defect } from '../types'

const props = defineProps<{ code: string; fileName: string; langLabel: string; defects: Defect[] }>()

const scrollRef = ref<HTMLElement | null>(null)

const problemLines = computed(() => new Set(props.defects.map((d) => d.line)))

const lines = computed(() =>
  props.code.split('\n').map((ln, i) => {
    const no = i + 1
    return {
      no,
      problem: problemLines.value.has(no),
      html: ln ? highlightLine(ln) : '&nbsp;',
    }
  }),
)

function locate(line: number) {
  const row = scrollRef.value?.querySelector<HTMLElement>(`.code-row[data-line="${line}"]`)
  if (!row) return
  row.scrollIntoView({ behavior: 'smooth', block: 'center' })
  row.classList.remove('flash')
  void row.offsetWidth
  row.classList.add('flash')
}

defineExpose({ locate })
</script>

<template>
  <div class="card animate-fadeInUp" style="animation-delay: 0.18s">
    <div class="flex items-center justify-between px-5 py-3.5 border-b" style="border-color: var(--border)">
      <div class="flex items-center gap-2.5">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--brand)"><path d="M8 6 2 12l6 6M16 6l6 6-6 6" /></svg>
        <span class="mono text-[13px] font-medium">{{ fileName }}</span>
        <span class="text-[11px] px-2 py-0.5 rounded-full font-medium" style="background: var(--surface-2); color: var(--text-2)">{{ langLabel }}</span>
      </div>
      <div class="flex items-center gap-2 text-[11px]" style="color: var(--text-3)">
        <span class="w-3 h-3 rounded-sm inline-block" style="background: #fff1f2; border: 1px solid #fecdd3"></span> 问题行
      </div>
    </div>
    <div ref="scrollRef" class="code-scroll">
      <div v-for="l in lines" :key="l.no" class="code-row" :class="{ problem: l.problem }" :data-line="l.no">
        <span class="gutter">
          <span v-if="l.problem" class="inline-block w-1.5 h-1.5 rounded-full mr-1" style="background: var(--high)"></span>{{ l.no }}
        </span>
        <pre v-html="l.html"></pre>
      </div>
    </div>
  </div>
</template>
