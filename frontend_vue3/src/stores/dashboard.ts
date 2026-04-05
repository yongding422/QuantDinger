import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dashboardApi, type DashboardSummary, type Trade, type PendingOrder } from '@/api/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  const summary = ref<DashboardSummary | null>(null)
  const recentTrades = ref<Trade[]>([])
  const pendingOrders = ref<PendingOrder[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [summaryRes, tradesRes, ordersRes] = await Promise.all([
        dashboardApi.getSummary(),
        dashboardApi.getRecentTrades(),
        dashboardApi.getPendingOrders(),
      ])
      summary.value = summaryRes.data.data?.data ?? null
      recentTrades.value = tradesRes.data.data?.data ?? []
      pendingOrders.value = ordersRes.data.data?.data ?? []
    } finally {
      loading.value = false
    }
  }

  async function cancelOrder(orderId: number) {
    await dashboardApi.deletePendingOrder(orderId)
    pendingOrders.value = pendingOrders.value.filter(o => o.id !== orderId)
  }

  return { summary, recentTrades, pendingOrders, loading, fetchAll, cancelOrder }
})
