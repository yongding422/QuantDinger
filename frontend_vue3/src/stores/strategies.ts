import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  strategiesApi,
  type Strategy,
  type Trade,
  type EquityCurvePoint,
  type BacktestResult,
  type BacktestParams,
  type Notification,
  type StrategyUpdatePayload,
} from '@/api/strategies'

export const useStrategiesStore = defineStore('strategies', () => {
  // Current strategy detail
  const currentStrategy = ref<Strategy | null>(null)
  const trades = ref<Trade[]>([])
  const equityCurve = ref<EquityCurvePoint[]>([])
  const backtestHistory = ref<BacktestResult[]>([])
  const notifications = ref<Notification[]>([])

  // Loading states
  const loading = ref(false)
  const backtestRunning = ref(false)

  // Fetch strategy by ID
  async function fetchStrategy(id: number) {
    loading.value = true
    try {
      const res = await strategiesApi.getById(id)
      currentStrategy.value = res.data.data ?? null
    } finally {
      loading.value = false
    }
  }

  // Fetch trades for a strategy
  async function fetchTrades(id: number) {
    const res = await strategiesApi.getTrades(id)
    trades.value = res.data.data ?? []
  }

  // Fetch equity curve
  async function fetchEquityCurve(id: number) {
    const res = await strategiesApi.getEquityCurve(id)
    equityCurve.value = res.data.data ?? []
  }

  // Fetch backtest history
  async function fetchBacktestHistory(id: number) {
    const res = await strategiesApi.getBacktestHistory(id)
    backtestHistory.value = res.data.data ?? []
  }

  // Run backtest
  async function runBacktest(id: number, params: BacktestParams) {
    backtestRunning.value = true
    try {
      const res = await strategiesApi.runBacktest(id, params)
      // Prepend new result to history
      backtestHistory.value.unshift(res.data.data ?? [])
      return res.data.data
    } finally {
      backtestRunning.value = false
    }
  }

  // Start strategy
  async function startStrategy(id: number) {
    const res = await strategiesApi.start(id)
    if (currentStrategy.value?.id === id) {
      currentStrategy.value = res.data.data ?? null
    }
  }

  // Stop strategy
  async function stopStrategy(id: number) {
    const res = await strategiesApi.stop(id)
    if (currentStrategy.value?.id === id) {
      currentStrategy.value = res.data.data ?? null
    }
  }

  // Update strategy
  async function updateStrategy(id: number, data: StrategyUpdatePayload) {
    const res = await strategiesApi.update(id, data)
    currentStrategy.value = res.data.data ?? null
  }

  // Notifications
  async function fetchNotifications() {
    const res = await strategiesApi.getNotifications()
    notifications.value = res.data.data ?? []
  }

  async function markRead(id: number) {
    await strategiesApi.markRead(id)
    const n = notifications.value.find(n => n.id === id)
    if (n) n.read = true
  }

  async function markAllRead() {
    await strategiesApi.markAllRead()
    notifications.value.forEach(n => (n.read = true))
  }

  // Load all detail data for a strategy
  async function loadAll(id: number) {
    loading.value = true
    try {
      await Promise.all([
        fetchStrategy(id),
        fetchTrades(id),
        fetchEquityCurve(id),
        fetchBacktestHistory(id),
      ])
    } finally {
      loading.value = false
    }
  }

  return {
    currentStrategy,
    trades,
    equityCurve,
    backtestHistory,
    notifications,
    loading,
    backtestRunning,
    fetchStrategy,
    fetchTrades,
    fetchEquityCurve,
    fetchBacktestHistory,
    runBacktest,
    startStrategy,
    stopStrategy,
    updateStrategy,
    fetchNotifications,
    markRead,
    markAllRead,
    loadAll,
  }
})
