<template>
  <div class="ai-analysis-page">
    <a-row :gutter="16">
      <!-- Chat panel -->
      <a-col :xs="24" :lg="16">
        <a-card title="AI Multi-Agent Chat" class="chat-card">
          <!-- Agent selector -->
          <div class="agent-selector">
            <a-select v-model:value="selectedAgent" style="width: 200px" placeholder="Select agent">
              <a-select-option value="">General</a-select-option>
              <a-select-option value="Investment Director">Investment Director</a-select-option>
              <a-select-option value="Market Analyst">Market Analyst</a-select-option>
              <a-select-option value="Quantitative Expert">Quantitative Expert</a-select-option>
              <a-select-option value="Risk Manager">Risk Manager</a-select-option>
              <a-select-option value="Operations Specialist">Operations Specialist</a-select-option>
            </a-select>
          </div>

          <!-- Messages -->
          <div class="messages" ref="messagesEl">
            <div
              v-for="(msg, idx) in store.messages"
              :key="idx"
              :class="['message', msg.role]"
            >
              <div class="message-role">{{ msg.role === 'user' ? 'You' : (msg.agent || 'AI') }}</div>
              <div class="message-content">{{ msg.content }}</div>
            </div>
            <div v-if="store.loading" class="message assistant">
              <div class="message-role">AI</div>
              <div class="message-content typing">Thinking...</div>
            </div>
          </div>

          <!-- Input -->
          <div class="chat-input">
            <a-input-search
              v-model:value="inputText"
              placeholder="Ask the AI..."
              enter-button="Send"
              @search="handleSend"
              :loading="store.loading"
            />
          </div>
        </a-card>
      </a-col>

      <!-- Sidebar: chat history -->
      <a-col :xs="24" :lg="8">
        <a-card title="Chat History" class="history-card">
          <template #extra>
            <a-button size="small" @click="store.clearMessages()">New Chat</a-button>
          </template>
          <a-list
            :data-source="store.sessions"
            size="small"
            style="max-height: 400px; overflow-y: auto"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta :title="item.name" :description="item.updatedAt" />
              </a-list-item>
            </template>
          </a-list>
          <a-empty v-if="store.sessions.length === 0" description="No chat history" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { useAiChatStore } from '@/stores/aiChat'

const store = useAiChatStore()
const inputText = ref('')
const selectedAgent = ref('')
const messagesEl = ref<HTMLElement>()

onMounted(() => {
  store.fetchHistory()
})

async function handleSend() {
  if (!inputText.value.trim() || store.loading) return
  const text = inputText.value
  inputText.value = ''
  await store.sendMessage(text, selectedAgent.value || undefined)
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}
</script>

<style scoped>
.ai-analysis-page { padding: 16px; }
.chat-card { height: calc(100vh - 180px); display: flex; flex-direction: column; }
.agent-selector { margin-bottom: 12px; }
.messages {
  flex: 1; overflow-y: auto; padding: 8px 0; min-height: 300px; max-height: calc(100vh - 380px);
}
.message { margin-bottom: 12px; }
.message.user { text-align: right; }
.message .message-role { font-size: 11px; color: var(--color-text-secondary); margin-bottom: 2px; }
.message .message-content { display: inline-block; padding: 8px 12px; border-radius: 8px; background: var(--color-bg-hover); max-width: 80%; text-align: left; }
.message.user .message-content { background: #1677ff; color: #fff; }
.chat-input { margin-top: 12px; }
.history-card { height: fit-content; max-height: calc(100vh - 180px); overflow-y: auto; }
</style>
