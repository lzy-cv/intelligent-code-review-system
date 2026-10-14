<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { login, register } from '../api/auth'

const router = useRouter()
const auth = useAuthStore()

const mode = ref<'login' | 'register'>('login')
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  if (!username.value.trim() || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const fn = mode.value === 'login' ? login : register
    const { token, user } = await fn(username.value.trim(), password.value)
    auth.setAuth(token, user)
    router.push('/workspace')
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center relative z-10 px-4">
    <div class="w-full max-w-sm">
      <div class="flex flex-col items-center mb-7 animate-fadeInUp">
        <div class="logo-badge" style="width: 56px; height: 56px; border-radius: 16px">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M12 2c3 3 3 6 3 9a3 3 0 1 1-6 0c0-3 0-6 3-9Z" fill="currentColor" />
            <path d="M12 2c-3 3-3 6-3 9a3 3 0 1 0 6 0c0-3 0-6-3-9Z" fill="currentColor" opacity=".55" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold mt-4">智能代码审查</h1>
        <p class="text-[13px] mt-1" style="color: var(--text-3)">AI Code Review · 多用户版</p>
      </div>

      <div class="card p-6 animate-fadeInUp" style="animation-delay: 0.08s">
        <div class="flex gap-2 p-1.5 rounded-xl mb-5" style="background: var(--surface-2)">
          <div class="mode-tab" :class="{ active: mode === 'login' }" @click="mode = 'login'; error = ''">登录</div>
          <div class="mode-tab" :class="{ active: mode === 'register' }" @click="mode = 'register'; error = ''">注册</div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-[13px] font-semibold mb-1.5" style="color: var(--text-2)">用户名</label>
            <input v-model="username" class="input" placeholder="请输入用户名" @keyup.enter="submit" />
          </div>
          <div>
            <label class="block text-[13px] font-semibold mb-1.5" style="color: var(--text-2)">密码</label>
            <input v-model="password" type="password" class="input" placeholder="请输入密码" @keyup.enter="submit" />
          </div>

          <div v-if="error" class="text-[13px] px-3 py-2 rounded-lg" style="background: var(--high-soft); color: #dc2626">{{ error }}</div>

          <button class="btn-primary w-full" :disabled="loading" @click="submit">
            <span v-if="loading" class="spinner"></span>
            {{ mode === 'login' ? '登录' : '注册并登录' }}
          </button>
        </div>

        <div v-if="mode === 'login'" class="text-center text-[12px] mt-4" style="color: var(--text-3)">演示账号：demo / demo123</div>
      </div>
    </div>
  </div>
</template>
