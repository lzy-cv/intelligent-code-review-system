<script setup lang="ts">
import { ref, watch } from 'vue'
import IntroCard from '../components/IntroCard.vue'
import InputPanel from '../components/InputPanel.vue'
import ScanPanel from '../components/ScanPanel.vue'
import ResultPanel from '../components/ResultPanel.vue'
import { getSample } from '../data/samples'
import { reviewCode } from '../api/review'
import { useReviewStore } from '../stores/review'
import { toast } from '../utils/toast'
import type { StartPayload, Defect, RiskFilter } from '../types'

type Phase = 'input' | 'scanning' | 'result'

const phase = ref<Phase>('input')
const resultCode = ref('')
const resultFileName = ref('')
const resultLangLabel = ref('')
const resultRisk = ref<RiskFilter>('all')
const resultDefects = ref<Defect[]>([])

const store = useReviewStore()

async function handleStart(payload: StartPayload) {
  const s = getSample(payload.lang)
  resultCode.value = payload.code
  resultFileName.value = payload.fileName || s.file
  resultLangLabel.value = s.label
  resultRisk.value = payload.risk
  phase.value = 'scanning'

  // 真实审查请求（与扫描动画并行）；结果回来后切换展示
  let defects: Defect[] = s.defects
  let duration = 0
  try {
    const res = await reviewCode(payload.code, payload.lang, 'local', payload.fileName || '')
    if (res) {
      defects = res.defects
      duration = res.duration_ms
      if (duration > 0) toast(`审查完成，耗时 ${(duration / 1000).toFixed(1)}s`, 'success')
    }
  } catch {
    toast('后端未连接，已回退到本地模拟数据', 'warn')
  }

  resultDefects.value = defects
  phase.value = 'result'
}

function handleReset() {
  phase.value = 'input'
}

// 侧边栏「新建审查」触发时，即使已在 /workspace 也重置
watch(
  () => store.refreshKey,
  () => {
    phase.value = 'input'
  },
)
</script>

<template>
  <div>
    <IntroCard v-if="phase === 'input'" />
    <InputPanel v-if="phase === 'input'" @start="handleStart" />
    <ScanPanel v-if="phase === 'scanning'" />
    <ResultPanel
      v-if="phase === 'result'"
      :defects="resultDefects"
      :code="resultCode"
      :file-name="resultFileName"
      :lang-label="resultLangLabel"
      :risk="resultRisk"
      @reset="handleReset"
    />
  </div>
</template>
