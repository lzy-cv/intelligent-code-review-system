<script setup lang="ts">
const projects = [
  { name: 'user-service', desc: '用户登录与查询服务', lang: 'JavaScript', color: '#f59e0b', issues: 9, updated: '2 小时前' },
  { name: 'order-api', desc: '订单查询与结算接口', lang: 'Python', color: '#3b82f6', issues: 8, updated: '1 天前' },
  { name: 'admin-web', desc: '后台管理前端项目', lang: 'TypeScript', color: '#2f6bff', issues: 12, updated: '3 天前' },
  { name: 'payment-gateway', desc: '支付网关服务', lang: 'Java', color: '#ef4444', issues: 5, updated: '1 周前' },
]
</script>

<template>
  <div class="grid grid-cols-2 gap-5">
    <div v-for="p in projects" :key="p.name" class="card card-hover p-5 animate-fadeInUp">
      <div class="flex items-start justify-between mb-4">
        <div class="w-11 h-11 rounded-xl flex items-center justify-center font-bold text-white text-lg" :style="{ background: `linear-gradient(135deg, ${p.color}, ${p.color}cc)` }">
          {{ p.name[0].toUpperCase() }}
        </div>
        <span class="text-[11px] px-2 py-0.5 rounded-full font-medium" style="background: var(--surface-2); color: var(--text-2)">{{ p.lang }}</span>
      </div>
      <div class="text-[15px] font-bold mb-1">{{ p.name }}</div>
      <div class="text-[13px] mb-4" style="color: var(--text-2)">{{ p.desc }}</div>
      <div class="flex items-center justify-between text-[12px]" style="color: var(--text-3)">
        <span>最近审查发现 <b style="color: var(--text)">{{ p.issues }}</b> 处缺陷</span>
        <span>{{ p.updated }}</span>
      </div>
    </div>
  </div>
</template>
