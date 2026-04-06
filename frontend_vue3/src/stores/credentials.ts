import { defineStore } from 'pinia'
import { ref } from 'vue'
import { credentialsApi, type Credential } from '@/api/credentials'

export const useCredentialsStore = defineStore('credentials', () => {
  const credentials = ref<Credential[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const res = await credentialsApi.getAll()
      credentials.value = res.data.data?.data ?? []
    } finally {
      loading.value = false
    }
  }

  async function saveCredential(data: Parameters<typeof credentialsApi.save>[0]) {
    const res = await credentialsApi.save(data)
    const saved = res.data.data?.data
    if (saved) {
      const idx = credentials.value.findIndex(c => c.id === saved.id)
      if (idx >= 0) credentials.value[idx] = saved
      else credentials.value.unshift(saved)
    }
    return saved
  }

  async function deleteCredential(id: number) {
    await credentialsApi.delete(id)
    credentials.value = credentials.value.filter(c => c.id !== id)
  }

  async function testConnection(id: number) {
    const res = await credentialsApi.testConnection(id)
    return res.data.data?.data
  }

  return { credentials, loading, fetchAll, saveCredential, deleteCredential, testConnection }
})
