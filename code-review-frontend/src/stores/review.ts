import { defineStore } from 'pinia'

// 仅用于「新建审查」强制重置工作台的信号；审查历史已改存后端数据库
export const useReviewStore = defineStore('review', {
  state: () => ({ refreshKey: 0 }),
  actions: {
    requestNewReview() {
      this.refreshKey++
    },
  },
})
