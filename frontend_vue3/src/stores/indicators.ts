import { defineStore } from 'pinia'
import { ref } from 'vue'
import { indicatorApi, type Indicator } from '@/api/indicator'

export const useIndicatorsStore = defineStore('indicators', () => {
  const indicators = ref<Indicator[]>([])
  const loading = ref(false)

  async function fetchIndicators() {
    loading.value = true
    try {
      const res = await indicatorApi.getIndicators()
      indicators.value = res.data.data?.data ?? []
    } finally {
      loading.value = false
    }
  }

  async function saveIndicator(data: Partial<Indicator>) {
    const res = await indicatorApi.saveIndicator(data)
    const saved = res.data.data?.data
    if (saved) {
      const idx = indicators.value.findIndex(i => i.id === saved.id)
      if (idx >= 0) {
        indicators.value[idx] = saved
      } else {
        indicators.value.unshift(saved)
      }
    }
    return saved
  }

  async function deleteIndicator(id: number) {
    await indicatorApi.deleteIndicator(id)
    indicators.value = indicators.value.filter(i => i.id !== id)
  }

  return { indicators, loading, fetchIndicators, saveIndicator, deleteIndicator }
})
