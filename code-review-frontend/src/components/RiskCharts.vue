<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import Chart from 'chart.js/auto'
import type { RiskLevel } from '../types'
import { useTheme } from '../composables/useTheme'

const props = defineProps<{
  counts: Record<RiskLevel, number>
  categories: { label: string; value: number }[]
  total: number
}>()

const { dark } = useTheme()
const donutEl = ref<HTMLCanvasElement | null>(null)
const barEl = ref<HTMLCanvasElement | null>(null)
let donut: Chart | null = null
let bar: Chart | null = null

const legend = computed(() => [
  { label: '高危', color: '#ef4444', value: props.counts.high },
  { label: '中危', color: '#f59e0b', value: props.counts.mid },
  { label: '低危', color: '#3b82f6', value: props.counts.low },
])

function draw() {
  donut?.destroy()
  bar?.destroy()
  const gridColor = dark.value ? '#232a38' : '#f0f2f5'
  const tickColor = dark.value ? '#94a3b8' : '#6b7280'

  if (donutEl.value) {
    donut = new Chart(donutEl.value, {
      type: 'doughnut',
      data: {
        labels: ['高危', '中危', '低危'],
        datasets: [
          {
            data: [props.counts.high, props.counts.mid, props.counts.low],
            backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6'],
            borderWidth: 0,
            hoverOffset: 8,
          },
        ],
      },
      options: {
        cutout: '70%',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    })
  }

  if (barEl.value) {
    bar = new Chart(barEl.value, {
      type: 'bar',
      data: {
        labels: props.categories.map((c) => c.label),
        datasets: [
          {
            data: props.categories.map((c) => c.value),
            backgroundColor: '#2f6bff',
            borderRadius: 8,
            barThickness: 34,
            maxBarThickness: 44,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0, color: tickColor, font: { size: 11 } }, grid: { color: gridColor } },
          x: { grid: { display: false }, ticks: { color: tickColor, font: { size: 12 } } },
        },
      },
    })
  }
}

onMounted(draw)
watch(dark, draw)
onBeforeUnmount(() => {
  donut?.destroy()
  bar?.destroy()
})
</script>

<template>
  <div class="grid grid-cols-2 gap-5 mb-5">
    <div class="card card-hover p-5 animate-fadeInUp">
      <div class="text-[14px] font-bold mb-4">风险等级分布</div>
      <div class="relative mx-auto" style="width: 170px; height: 170px">
        <canvas ref="donutEl"></canvas>
        <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <div class="text-[28px] font-extrabold">{{ total }}</div>
          <div class="text-[11px]" style="color: var(--text-3)">缺陷总数</div>
        </div>
      </div>
      <div class="flex justify-center gap-5 mt-4">
        <div v-for="l in legend" :key="l.label" class="flex items-center gap-1.5 text-[13px]" style="color: var(--text-2)">
          <span class="w-2.5 h-2.5 rounded-full" :style="{ background: l.color }"></span>
          {{ l.label }}
          <span class="font-semibold" style="color: var(--text)">{{ l.value }}</span>
        </div>
      </div>
    </div>

    <div class="card card-hover p-5 animate-fadeInUp" style="animation-delay: 0.08s">
      <div class="text-[14px] font-bold mb-4">缺陷类型分布</div>
      <div style="height: 210px">
        <canvas ref="barEl"></canvas>
      </div>
    </div>
  </div>
</template>
