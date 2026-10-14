import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('../views/LoginView.vue'), meta: { title: '登录' } },
    { path: '/', redirect: '/workspace' },
    { path: '/workspace', name: 'workspace', component: () => import('../views/WorkspaceView.vue'), meta: { title: '审查工作台' } },
    { path: '/history', name: 'history', component: () => import('../views/HistoryView.vue'), meta: { title: '审查历史' } },
    { path: '/history/:id', name: 'review-detail', component: () => import('../views/ReviewDetailView.vue'), meta: { title: '审查详情' } },
    { path: '/projects', name: 'projects', component: () => import('../views/ProjectsView.vue'), meta: { title: '项目管理' } },
    { path: '/reports', name: 'reports', component: () => import('../views/ReportsView.vue'), meta: { title: '报告中心' } },
    { path: '/settings', name: 'settings', component: () => import('../views/SettingsView.vue'), meta: { title: '设置' } },
  ],
})

// 路由守卫：未登录跳登录页，已登录访问登录页则回工作台
router.beforeEach((to) => {
  const token = localStorage.getItem('cr-token')
  if (to.path !== '/login' && !token) return { path: '/login' }
  if (to.path === '/login' && token) return { path: '/workspace' }
})

export default router
