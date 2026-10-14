<script setup lang="ts">
import { computed, ref } from 'vue'
import StatCard from './StatCard.vue'
import RiskCharts from './RiskCharts.vue'
import DefectList from './DefectList.vue'
import CodePreview from './CodePreview.vue'
import type { Defect, RiskFilter } from '../types'

const props = defineProps<{
  defects: Defect[]
  code: string
  fileName: string
  langLabel: string
  risk: RiskFilter
}>()

const codePreviewRef = ref<{ locate: (line: number) => void } | null>(null)

const counts = computed(() => ({
  high: props.defects.filter((d) => d.level === 'high').length,
  mid: props.defects.filter((d) => d.level === 'mid').length,
  low: props.defects.filter((d) => d.level === 'low').length,
  total: props.defects.length,
}))

const categories = computed(() => {
  const names = ['安全', '健壮性', '代码质量']
  return names.map((n) => ({ label: n, value: props.defects.filter((d) => d.cat === n).length }))
})

const statCards = computed(() => [
  { label: '问题总数', value: counts.value.total, accent: '#2f6bff', icon: 'M13 2 3 14h7l-1 8 10-12h-7l1-8Z' },
  { label: '高危缺陷', value: counts.value.high, accent: '#ef4444', icon: 'M12 9v4M12 17h.01M10 3h4l7 7-9 9-9-9 7-7Z' },
  { label: '中危缺陷', value: counts.value.mid, accent: '#f59e0b', icon: 'M12 9v4M12 17h.01M10 3h4l7 7-9 9-9-9 7-7Z' },
  { label: '低危缺陷', value: counts.value.low, accent: '#3b82f6', icon: 'M12 9v4M12 17h.01M10 3h4l7 7-9 9-9-9 7-7Z' },
])

function onLocate(line: number) {
  codePreviewRef.value?.locate(line)
}
</script>

<template>
  <div>
    <div class="grid grid-cols-4 gap-4 mb-5">
      <StatCard v-for="s in statCards" :key="s.label" :label="s.label" :value="s.value" :accent="s.accent" :icon="s.icon" />
    </div>
    <RiskCharts :counts="counts" :categories="categories" :total="counts.total" />
    <div class="grid grid-cols-2 gap-5">
      <DefectList :defects="defects" :initial-risk="risk" @locate="onLocate" />
      <CodePreview ref="codePreviewRef" :code="code" :file-name="fileName" :lang-label="langLabel" :defects="defects" />
    </div>
  </div>
</template>
