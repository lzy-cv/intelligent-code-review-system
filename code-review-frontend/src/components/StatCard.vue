<script setup lang="ts">
defineProps<{ label: string; value: number; accent: string; icon: string }>()
</script>

<template>
  <div class="card card-hover stat-card p-4 animate-fadeInUp" :style="{ '--accent': accent }">
    <div class="flex items-center justify-between mb-3">
      <span class="text-[13px] font-medium" style="color: var(--text-2)">{{ label }}</span>
      <span class="w-8 h-8 rounded-lg flex items-center justify-center" :style="{ background: `color-mix(in srgb, ${accent} 12%, transparent)`, color: accent }">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path :d="icon" /></svg>
      </span>
    </div>
    <div class="text-[30px] font-extrabold leading-none" :style="{ color: accent }">{{ value }}</div>
  </div>
</template>
