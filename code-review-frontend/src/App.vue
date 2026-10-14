<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import SideNav from './components/SideNav.vue'
import { useTheme } from './composables/useTheme'

const route = useRoute()
const { dark, toggle } = useTheme()
const title = computed(() => (route.meta.title as string) || '智能代码审查')
const isLogin = computed(() => route.path === '/login')
</script>

<template>
  <div class="bg-deco"></div>
  <div class="glow glow-1"></div>
  <div class="glow glow-2"></div>

  <!-- 登录页全屏展示 -->
  <router-view v-if="isLogin" />

  <template v-else>
    <SideNav />

    <main class="relative z-10" style="margin-left: 236px; min-height: 100vh">
      <div class="max-w-5xl mx-auto px-8 py-8">
        <!-- 顶部栏（标题随路由变化） -->
        <div class="flex items-center justify-between mb-6 animate-fadeIn">
          <h1 class="text-xl font-bold">{{ title }}</h1>
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-2 text-[13px] font-medium" style="color: var(--text-2)">
              <span class="status-dot"></span> 引擎在线 · 已就绪
            </div>
            <button class="btn-ghost" style="padding: 8px 10px" @click="toggle" title="切换主题">
              <svg v-if="!dark" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8Z" /></svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
            </button>
          </div>
        </div>

        <!-- 页面切换过渡 -->
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>

        <footer class="text-center text-[12px] py-8" style="color: var(--text-3)">
          智能代码审查平台 · 毕业设计演示 · 多用户版
        </footer>
      </div>
    </main>
  </template>
</template>
