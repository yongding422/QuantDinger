import { defineStore } from 'pinia'
import { ref } from 'vue'
import { aiChatApi, type ChatMessage, type ChatSession } from '@/api/aiChat'

export const useAiChatStore = defineStore('aiChat', () => {
  const messages = ref<ChatMessage[]>([])
  const sessions = ref<ChatSession[]>([])
  const loading = ref(false)

  async function sendMessage(text: string, agent?: string) {
    // Add user message
    messages.value.push({ role: 'user', content: text, agent })
    loading.value = true
    try {
      const res = await aiChatApi.sendMessage({ message: text, agent })
      const reply = res.data.data?.data?.reply
      if (reply) {
        messages.value.push({ role: 'assistant', content: reply, agent: res.data.data?.data?.agent })
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory() {
    const res = await aiChatApi.getHistory()
    sessions.value = res.data.data?.data ?? []
  }

  async function saveChat(name: string) {
    await aiChatApi.saveChat({ name, messages: messages.value })
    await fetchHistory()
  }

  function clearMessages() {
    messages.value = []
  }

  return { messages, sessions, loading, sendMessage, fetchHistory, saveChat, clearMessages }
})
