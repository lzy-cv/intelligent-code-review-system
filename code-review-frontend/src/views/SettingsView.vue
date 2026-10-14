<script setup lang="ts">
import { reactive, ref } from 'vue'
import { toast } from '../utils/toast'
import { useTheme } from '../composables/useTheme'

const model = ref('deepseek')
const { dark, toggle } = useTheme()

const toggles = reactive([
  { key: 'semgrep', title: 'Semgrep 规则引擎', desc: '确定性规则扫描，快速命中已知漏洞模式', value: true },
  { key: 'rag', title: 'RAG 相似案例检索', desc: '检索 CWE/CVE 语料库，增强修复建议质量', value: true },
  { key: 'autoFix', title: '自动应用修复建议', desc: '审查完成后自动生成可应用补丁（演示）', value: false },
])

function save() {
  toast('设置已保存（模拟）', 'success')
}
</script>

<template>
  <div class="card p-6 animate-fadeInUp">
    <div class="text-[14px] font-bold mb-5">审查引擎设置</div>

    <div class="max-w-xl space-y-5">
      <div>
        <label class="block text-[13px] font-semibold mb-1.5" style="color: var(--text-2)">默认大模型</label>
        <select v-model="model" class="select">
          <option value="deepseek">DeepSeek-V3（推荐）</option>
          <option value="qwen">通义千问 Qwen-Max</option>
          <option value="gpt">OpenAI GPT-4o</option>
        </select>
      </div>

      <div class="divide-y" style="border-color: var(--border)">
        <div v-for="row in toggles" :key="row.key" class="flex items-center justify-between py-4">
          <div class="pr-4">
            <div class="text-[14px] font-semibold">{{ row.title }}</div>
            <div class="text-[12px]" style="color: var(--text-3)">{{ row.desc }}</div>
          </div>
          <button
            class="relative w-11 h-6 rounded-full transition-colors flex-none"
            :class="row.value ? 'bg-[#2f6bff]' : 'bg-slate-300'"
            @click="row.value = !row.value"
          >
            <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform" :class="row.value ? 'translate-x-5' : ''"></span>
          </button>
        </div>

        <!-- 深色模式（真实生效） -->
        <div class="flex items-center justify-between py-4">
          <div class="pr-4">
            <div class="text-[14px] font-semibold">深色模式</div>
            <div class="text-[12px]" style="color: var(--text-3)">切换 IDE 深色主题，偏好会保存在本地</div>
          </div>
          <button
            class="relative w-11 h-6 rounded-full transition-colors flex-none"
            :class="dark ? 'bg-[#2f6bff]' : 'bg-slate-300'"
            @click="toggle"
          >
            <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform" :class="dark ? 'translate-x-5' : ''"></span>
          </button>
        </div>
      </div>

      <button class="btn-primary" @click="save">保存设置</button>
    </div>
  </div>
</template>
