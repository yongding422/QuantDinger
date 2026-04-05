import { defineStore } from 'pinia'
import { ref } from 'vue'
import { marketApi, globalMarketApi, type WatchlistItem, type GlobalMarketOverview } from '@/api/market'

export const useMarketStore = defineStore('market', () => {
  const watchlist = ref<WatchlistItem[]>([])
  const overview = ref<GlobalMarketOverview | null>(null)
  const loading = ref(false)

  async function fetchWatchlist() {
    loading.value = true
    try {
      const res = await marketApi.getWatchlist()
      watchlist.value = res.data.data?.data ?? []
      if (watchlist.value.length > 0) {
        await fetchWatchlistPrices()
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchWatchlistPrices() {
    if (watchlist.value.length === 0) return
    const symbols = watchlist.value.map(w => `${w.exchange}:${w.symbol}`)
    try {
      const res = await marketApi.getWatchlistPrices(symbols)
      const prices = res.data.data?.data ?? {}
      watchlist.value = watchlist.value.map(w => ({
        ...w,
        ...(prices[`${w.exchange}:${w.symbol}`] || {}),
      }))
    } catch {}
  }

  async function addToWatchlist(symbol: string, exchange: string) {
    await marketApi.addToWatchlist(symbol, exchange)
    await fetchWatchlist()
  }

  async function removeFromWatchlist(symbol: string, exchange: string) {
    await marketApi.removeFromWatchlist(symbol, exchange)
    watchlist.value = watchlist.value.filter(w => !(w.symbol === symbol && w.exchange === exchange))
  }

  async function fetchOverview() {
    loading.value = true
    try {
      const res = await globalMarketApi.getOverview()
      overview.value = res.data.data?.data ?? null
    } finally {
      loading.value = false
    }
  }

  return {
    watchlist, overview, loading,
    fetchWatchlist, fetchWatchlistPrices, addToWatchlist, removeFromWatchlist, fetchOverview,
  }
})
