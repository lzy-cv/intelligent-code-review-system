<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Defect, RiskFilter, RiskLevel } from '../types'

const props = defineProps<{ defects: Defect[]; initialRisk: RiskFilter }>()
const emit = defineEmits<{ (e: 'locate', line: number): void }>()

const filter = ref<RiskFilter>(props.initialRisk)
const expanded = ref<Record<number, boolean>>({})

const LV: Record<RiskLevel, string> = { high: '高危', mid: '中危', low: '低危' }

const visible = computed(() => {
  const all = props.defects.map((d, i) => ({ d, i }))
  return filter.value === 'all' ? all : all.filter((x) => x.d.level === filter.value)
})

function toggle(i: number) {
  expanded.value[i] = !expanded.value[i]
}

function locate(line: number) {
  emit('locate', line)
}
</script>

<template>
  <div class="card animate-fadeInUp" style="animation-delay: 0.12s">
    <div class="flex items-center justify-between px-5 py-4 border-b" style="border-color: var(--border)">
      <div class="text-[14px] font-bold">缺陷列表</div>
      <div class="flex items-center gap-2.5">
        <select v-model="filter" class="select" style="width: auto; padding: 6px 30px 6px 12px; font-size: 12px">
          <option value="all">全部等级</option>
          <option value="high">仅高危</option>
          <option value="mid">仅中危</option>
          <option value="low">仅低危</option>
        </select>
        <span class="text-[12px] font-medium px-2.5 py-1 rounded-full" style="background: var(--brand-soft); color: var(--brand)">{{ visible.length }} 项</span>
      </div>
    </div>

    <div class="p-4 space-y-3" style="max-height: 560px; overflow: auto">
      <div v-for="x in visible" :key="x.i" class="defect-item" :class="{ open: expanded[x.i] }">
        <div class="defect-head px-4 py-3.5" @click="toggle(x.i)">
          <div class="flex items-center gap-2.5">
            <span class="risk-badge" :class="'risk-' + x.d.level"><span class="dot"></span>{{ LV[x.d.level] }}</span>
            <span class="text-[14px] font-semibold flex-1 truncate">{{ x.d.title }}</span>
            <span class="text-[11px] px-2 py-0.5 rounded-full" style="background: var(--surface-2); color: var(--text-2)">{{ x.d.cat }}</span>
            <span v-if="x.d.source" class="text-[10px] px-1.5 py-0.5 rounded font-semibold shrink-0" :style="x.d.source === 'llm' ? 'background:#f5f3ff;color:#7c3aed' : 'background:var(--brand-soft);color:var(--brand)'">{{ x.d.source === 'llm' ? 'LLM' : '规则' }}</span>
            <button class="text-[12px] font-medium px-2.5 py-1 rounded-lg shrink-0" style="color: var(--brand); background: var(--brand-soft)" @click.stop="locate(x.d.line)">
              第 {{ x.d.line }} 行
            </button>
            <svg
              class="shrink-0 transition-transform duration-200"
              :style="{ color: 'var(--text-3)', transform: expanded[x.i] ? 'rotate(180deg)' : '' }"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            ><path d="m6 9 6 6 6-6" /></svg>
          </div>
        </div>
        <div v-show="expanded[x.i]" class="px-4 pb-4">
          <p class="text-[13px] leading-relaxed mb-3" style="color: var(--text-2)">{{ x.d.desc }}</p>
          <div class="defect-fix rounded-xl p-3.5">
            <div class="flex items-center gap-2 mb-2 text-[12px] font-bold" style="color: #16a34a">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5" /></svg>
              修复建议
            </div>
            <p class="text-[13px] leading-relaxed" style="color: var(--text-2)">{{ x.d.fix }}</p>
            <pre v-if="x.d.code" class="mono mt-3">{{ x.d.code }}</pre>
          </div>
        </div>
      </div>

      <div v-if="visible.length === 0" class="text-center py-10 text-[13px]" style="color: var(--text-3)">当前筛选下没有缺陷</div>
    </div>
  </div>
</template>
