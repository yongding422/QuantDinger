import { defineStore } from 'pinia'
import { ref } from 'vue'
import { quickTradeApi, type Balance, type Position, type Order } from '@/api/quickTrade'

export const useQuickTradeStore = defineStore('quickTrade', () => {
  const balances = ref<Balance[]>([])
  const position = ref<Position | null>(null)
  const orders = ref<Order[]>([])
  const totalOrders = ref(0)
  const loading = ref(false)

  async function fetchBalance(exchange: string) {
    loading.value = true
    try {
      const res = await quickTradeApi.getBalance(exchange)
      balances.value = res.data.data?.data ?? []
    } finally {
      loading.value = false
    }
  }

  async function fetchPosition(exchange: string, symbol: string) {
    const res = await quickTradeApi.getPosition(exchange, symbol)
    position.value = res.data.data?.data ?? null
    return position.value
  }

  async function placeOrder(data: Parameters<typeof quickTradeApi.placeOrder>[0]) {
    const res = await quickTradeApi.placeOrder(data)
    const order: Order = res.data.data?.data
    if (order) orders.value.unshift(order)
    return order
  }

  async function closePosition(exchange: string, symbol: string) {
    await quickTradeApi.closePosition(exchange, symbol)
    position.value = null
  }

  async function fetchHistory(params?: { page?: number; pageSize?: number }) {
    loading.value = true
    try {
      const res = await quickTradeApi.getHistory(params)
      const data = res.data.data?.data as { items?: Order[]; total?: number } | null
      orders.value = data?.items ?? []
      totalOrders.value = data?.total ?? 0
    } finally {
      loading.value = false
    }
  }

  return {
    balances, position, orders, totalOrders, loading,
    fetchBalance, fetchPosition, placeOrder, closePosition, fetchHistory,
  }
})
