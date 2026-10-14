<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReviewStore } from '../stores/review'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const store = useReviewStore()
const auth = useAuthStore()

const username = computed(() => auth.user?.username || '未登录')
const initial = computed(() => (username.value[0] || 'U').toUpperCase())

const navItems = [
  { label: '审查工作台', to: '/workspace', icon: 'M11 4a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm-7 16a7 7 0 0 1 14 0' },
  { label: '审查历史', to: '/history', icon: 'M3 5h18M3 12h18M3 19h18' },
  { label: '项目管理', to: '/projects', icon: 'M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z' },
  { label: '报告中心', to: '/reports', icon: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z M14 2v6h6' },
  { label: '设置', to: '/settings', icon: 'M19 12a7 7 0 0 0-.1-1.2l2-1.6-2-3.4-2.4 1a7 7 0 0 0-2-1.2L14 3h-4l-.5 2.6a7 7 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.6A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.6 2 3.4 2.4-1c.6.5 1.3.9 2 1.2L10 21h4l.5-2.6c.7-.3 1.4-.7 2-1.2l2.4 1 2-3.4-2-1.6c.1-.4.1-.8.1-1.2Z' },
]

function go(to: string) {
  router.push(to)
}

function newReview() {
  store.requestNewReview()
  router.push('/workspace')
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <aside class="sidebar">
    <div class="flex items-center gap-3 px-1.5 mb-6">
      <div class="logo-badge">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M12 2c3 3 3 6 3 9a3 3 0 1 1-6 0c0-3 0-6 3-9Z" fill="currentColor" />
          <path d="M12 2c-3 3-3 6-3 9a3 3 0 1 0 6 0c0-3 0-6-3-9Z" fill="currentColor" opacity=".55" />
        </svg>
      </div>
      <div>
        <div class="text-[15px] font-bold leading-tight">智能代码审查</div>
        <div class="text-[11px]" style="color: var(--text-3)">AI Code Review</div>
      </div>
    </div>

    <button class="btn-primary w-full mb-4" @click="newReview">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" /></svg>
      新建审查
    </button>

    <nav class="space-y-1">
      <div
        v-for="item in navItems"
        :key="item.to"
        class="nav-item"
        :class="{ active: route.path === item.to }"
        @click="go(item.to)"
      >
        <svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path :d="item.icon" /></svg>
        {{ item.label }}
      </div>
    </nav>

    <div class="mt-auto pt-4 border-t" style="border-color: var(--border)">
      <div class="flex items-center gap-3 px-1.5">
        <div class="w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold flex-none" style="background: linear-gradient(135deg, #8b5cf6, #ec4899)">{{ initial }}</div>
        <div class="min-w-0 flex-1">
          <div class="text-sm font-semibold truncate">{{ username }}</div>
          <div class="text-[11px] truncate" style="color: var(--text-3)">多用户 · 已登录</div>
        </div>
        <button class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-colors" style="color: var(--text-3)" @click="logout" title="退出登录">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" /></svg>
        </button>
      </div>
    </div>
  </aside>
</template>
