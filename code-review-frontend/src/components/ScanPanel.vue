<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

const progress = ref(0)
const statusText = ref('')
const waiting = ref(false)
const logLines = ref<string[]>([])
const logBox = ref<HTMLElement | null>(null)

const STEPS = [
  { at: 0, text: '正在解析代码结构（tree-sitter AST）…', log: '› 初始化审查引擎，解析 AST 语法树…' },
  { at: 15, text: '运行 Semgrep 规则引擎扫描…', log: '› Semgrep 命中规则：sqli · hardcoded-secret · xss · eval…' },
  { at: 35, text: 'RAG 检索相似缺陷案例…', log: '› 向量检索相似 CWE 案例，附上参考修复…' },
  { at: 55, text: 'LLM 大模型深度分析中…', log: '› 调用大模型做语义分析…' },
  { at: 78, text: '融合结果、生成缺陷报告…', log: '› 合并规则 + LLM 结果，去重分级…' },
]

let timer: number | undefined
let typeTimer: number | undefined
let stepIdx = 0

function type(text: string) {
  statusText.value = ''
  let i = 0
  window.clearInterval(typeTimer)
  typeTimer = window.setInterval(() => {
    i++
    statusText.value = text.slice(0, i)
    if (i >= text.length) window.clearInterval(typeTimer)
  }, 22)
}

onMounted(() => {
  logLines.value = ['$ 启动审查流水线…']
  timer = window.setInterval(() => {
    if (progress.value < 90) {
      progress.value = Math.min(90, progress.value + Math.random() * 1.2 + 0.4)
      const next = STEPS[stepIdx]
      if (next && progress.value >= next.at) {
        stepIdx++
        type(next.text)
        logLines.value.push(next.log)
        void nextTick(() => {
          if (logBox.value) logBox.value.scrollTop = logBox.value.scrollHeight
        })
      }
      if (progress.value >= 90) {
        waiting.value = true
        type('正在等待大模型返回结果…')
      }
    }
  }, 38)
})

onBeforeUnmount(() => {
  window.clearInterval(timer)
  window.clearInterval(typeTimer)
})
</script>

<template>
  <section class="card p-8 mt-5 animate-fadeInUp">
    <div class="flex items-center gap-6">
      <div class="relative w-20 h-20 flex-none">
        <div class="ripple-ring"></div>
        <div class="ripple-ring" style="animation-delay: 0.5s"></div>
        <div class="ripple-ring" style="animation-delay: 1s"></div>
        <div class="absolute inset-0 rounded-full flex items-center justify-center" style="background: linear-gradient(135deg, var(--brand), #3b82f6); color: #fff">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8Z" /></svg>
        </div>
      </div>
      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between mb-2">
          <div class="text-[15px] font-bold">{{ waiting ? '分析中，请稍候' : 'AI 深度审查中' }}</div>
          <div class="text-[13px] font-bold mono" style="color: var(--brand)">{{ Math.floor(progress) }}%</div>
        </div>
        <div class="h-2.5 rounded-full overflow-hidden" style="background: var(--surface-3)">
          <div class="progress-fill h-full rounded-full" :class="{ 'opacity-80': waiting }" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="mt-3 text-[13px]" style="color: var(--text-2)">
          <span>{{ statusText }}</span><span class="caret"></span>
        </div>
      </div>
    </div>

    <div ref="logBox" class="mt-6 p-4 rounded-xl mono text-[12px] leading-relaxed space-y-1.5" style="background: #0f172a; color: #94a3b8; max-height: 180px; overflow: auto">
      <div v-for="(l, i) in logLines" :key="i">{{ l }}</div>
    </div>
  </section>
</template>
