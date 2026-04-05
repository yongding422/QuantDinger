import { defineStore } from 'pinia'
import { ref } from 'vue'
import { portfolioApi, type Position, type PortfolioMonitor, type Alert, type PortfolioSummary } from '@/api/portfolio'

export const usePortfolioStore = defineStore('portfolio', () => {
  const positions = ref<Position[]>([])
  const monitors = ref<PortfolioMonitor[]>([])
  const alerts = ref<Alert[]>([])
  const summary = ref<PortfolioSummary | null>(null)
  const loading = ref(false)

  async function fetchPositions() {
    loading.value = true
    try {
      const res = await portfolioApi.getPositions()
      positions.value = res.data.data?.data ?? []
    } finally {
      loading.value = false
    }
  }

  async function fetchAll() {
    loading.value = true
    try {
      const [posRes, monRes, alertRes, sumRes] = await Promise.all([
        portfolioApi.getPositions(),
        portfolioApi.getMonitors(),
        portfolioApi.getAlerts(),
        portfolioApi.getSummary(),
      ])
      positions.value = posRes.data.data?.data ?? []
      monitors.value = monRes.data.data?.data ?? []
      alerts.value = alertRes.data.data?.data ?? []
      summary.value = sumRes.data.data?.data ?? null
    } finally {
      loading.value = false
    }
  }

  async function addPosition(data: Partial<Position>) {
    await portfolioApi.addPosition(data)
    await fetchPositions()
  }

  async function updatePosition(id: number, data: Partial<Position>) {
    await portfolioApi.updatePosition(id, data)
    await fetchPositions()
  }

  async function deletePosition(id: number) {
    await portfolioApi.deletePosition(id)
    positions.value = positions.value.filter(p => p.id !== id)
  }

  async function addAlert(data: Partial<Alert>) {
    await portfolioApi.createAlert(data)
    const res = await portfolioApi.getAlerts()
    alerts.value = res.data.data?.data ?? []
  }

  async function deleteAlert(id: number) {
    await portfolioApi.deleteAlert(id)
    alerts.value = alerts.value.filter(a => a.id !== id)
  }

  return {
    positions, monitors, alerts, summary, loading,
    fetchPositions, fetchAll, addPosition, updatePosition, deletePosition, addAlert, deleteAlert,
  }
})
