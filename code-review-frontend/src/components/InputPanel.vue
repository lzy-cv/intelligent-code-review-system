<script setup lang="ts">
import { ref } from 'vue'
import { getSample } from '../data/samples'
import { toast } from '../utils/toast'
import type { RiskFilter, StartPayload } from '../types'

const emit = defineEmits<{ (e: 'start', payload: StartPayload): void }>()

type Mode = 'snippet' | 'file' | 'git'

const mode = ref<Mode>('snippet')
const lang = ref('javascript')
const risk = ref<RiskFilter>('all')
const codeText = ref(getSample('javascript').code)
const fileName = ref('')
const fileCode = ref<string | null>(null)
const gitUrl = ref('')

const snippetPanel = ref<HTMLElement | null>(null)
const gitPanel = ref<HTMLElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const langs = [
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'go', label: 'Go' },
  { value: 'php', label: 'PHP' },
]

function switchMode(m: Mode) {
  mode.value = m
}

function onLangChange() {
  if (mode.value === 'snippet' && !fileCode.value) {
    codeText.value = getSample(lang.value).code
  }
}

function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) readFile(f)
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  const f = e.dataTransfer?.files?.[0]
  if (f) readFile(f)
}

const EXT_LANG: Record<string, string> = {
  js: 'javascript', ts: 'typescript', py: 'python',
  java: 'java', go: 'go', php: 'php', c: 'c', cpp: 'cpp', rb: 'ruby', rs: 'rust',
}

function readFile(f: File) {
  fileName.value = f.name
  // 根据文件扩展名自动识别语言
  const ext = f.name.split('.').pop()?.toLowerCase()
  if (ext && EXT_LANG[ext]) lang.value = EXT_LANG[ext]
  const r = new FileReader()
  r.onload = () => {
    fileCode.value = r.result as string
  }
  r.readAsText(f)
}

function shake(el: HTMLElement | null) {
  el?.animate(
    [
      { transform: 'translateX(0)' },
      { transform: 'translateX(-6px)' },
      { transform: 'translateX(6px)' },
      { transform: 'translateX(-4px)' },
      { transform: 'translateX(4px)' },
      { transform: 'translateX(0)' },
    ],
    { duration: 360 },
  )
}

function start() {
  let code = ''
  if (mode.value === 'snippet') {
    code = codeText.value.trim()
    if (!code) {
      toast('请先粘贴需要审查的代码', 'warn')
      shake(snippetPanel.value)
      return
    }
  } else if (mode.value === 'file') {
    if (!fileCode.value) {
      toast('未选择文件，已使用示例代码演示', 'info')
      code = getSample(lang.value).code
    } else {
      code = fileCode.value
    }
  } else {
    if (!gitUrl.value.trim()) {
      toast('请先输入 Git 仓库地址', 'warn')
      shake(gitPanel.value)
      return
    }
    toast('已模拟拉取仓库 master 分支代码', 'info')
    code = getSample(lang.value).code
  }

  emit('start', { code, lang: lang.value, risk: risk.value, fileName: fileName.value || undefined })
}
</script>

<template>
  <section class="card p-6 animate-fadeInUp" style="animation-delay: 0.08s">
    <!-- 模式切换 -->
    <div class="flex gap-2 p-1.5 rounded-xl mb-5" style="background: var(--surface-2)">
      <div class="mode-tab" :class="{ active: mode === 'snippet' }" @click="switchMode('snippet')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m8 6-6 6 6 6M16 6l6 6-6 6" /></svg>
        代码片段粘贴
      </div>
      <div class="mode-tab" :class="{ active: mode === 'file' }" @click="switchMode('file')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12M7 10l5 5 5-5" /><path d="M4 21h16" /></svg>
        文件上传
      </div>
      <div class="mode-tab" :class="{ active: mode === 'git' }" @click="switchMode('git')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="6" r="2" /><circle cx="18" cy="18" r="2" /><circle cx="18" cy="6" r="2" /><circle cx="6" cy="18" r="2" /><path d="M6 8v8M8 6h8M18 8v8M8 18h8" /></svg>
        Git 仓库地址
      </div>
    </div>

    <!-- 内容区 -->
    <div class="mb-5">
      <div v-show="mode === 'snippet'" ref="snippetPanel">
        <textarea v-model="codeText" class="input code-input" spellcheck="false"></textarea>
      </div>

      <div v-show="mode === 'file'">
        <div
          class="rounded-xl border-2 border-dashed p-10 text-center cursor-pointer transition-all"
          style="border-color: var(--border)"
          @click="fileInput?.click()"
          @dragover.prevent
          @drop.prevent="onDrop"
        >
          <div class="mx-auto mb-3 w-12 h-12 rounded-xl flex items-center justify-center" style="background: var(--brand-soft); color: var(--brand)">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 16V4M7 9l5-5 5 5" /><path d="M4 20h16" /></svg>
          </div>
          <div class="text-[14px] font-medium">
            <template v-if="fileName">已选择：<span class="font-bold" style="color: var(--text)">{{ fileName }}</span></template>
            <template v-else>点击或拖拽上传单个代码文件</template>
          </div>
          <div class="text-[12px] mt-1" style="color: var(--text-3)">支持 .js / .ts / .py / .java / .go 等文本文件</div>
          <input type="file" ref="fileInput" class="hidden" @change="onFileChange" />
        </div>
      </div>

      <div v-show="mode === 'git'" ref="gitPanel">
        <div class="relative">
          <span class="absolute left-3.5 top-1/2 -translate-y-1/2" style="color: var(--text-3)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="6" r="2" /><circle cx="18" cy="18" r="2" /><circle cx="18" cy="6" r="2" /><circle cx="6" cy="18" r="2" /><path d="M6 8v8M8 6h8M18 8v8M8 18h8" /></svg>
          </span>
          <input v-model="gitUrl" class="input mono" style="padding-left: 38px" placeholder="https://github.com/user/repo.git" />
        </div>
        <div class="text-[12px] mt-2" style="color: var(--text-3)">演示环境将模拟拉取仓库 master 分支的最新代码</div>
      </div>
    </div>

    <!-- 配置行 -->
    <div class="grid grid-cols-2 gap-4 mb-6" style="max-width: 520px">
      <div>
        <label class="block text-[13px] font-semibold mb-1.5" style="color: var(--text-2)">编程语言</label>
        <select v-model="lang" class="select" @change="onLangChange">
          <option v-for="l in langs" :key="l.value" :value="l.value">{{ l.label }}</option>
        </select>
      </div>
      <div>
        <label class="block text-[13px] font-semibold mb-1.5" style="color: var(--text-2)">风险等级筛选</label>
        <select v-model="risk" class="select">
          <option value="all">全部等级</option>
          <option value="high">仅高危</option>
          <option value="mid">仅中危</option>
          <option value="low">仅低危</option>
        </select>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <button class="btn-primary" @click="start">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8Z" /></svg>
        开始审查
      </button>
      <span class="text-[12px]" style="color: var(--text-3)">预计耗时 3~5 秒 · 异步流水线</span>
    </div>
  </section>
</template>
