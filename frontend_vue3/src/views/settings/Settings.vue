<template>
  <div class="settings-page">
    <a-card>
      <a-tabs v-model:activeKey="activeTab">
        <!-- Profile Tab -->
        <a-tab-pane key="profile" tab="Profile">
          <a-typography-title level="5">Profile Settings</a-typography-title>
          <a-typography-paragraph type="secondary">
            Manage your account profile information.
          </a-typography-paragraph>
          <a-form layout="vertical" style="max-width: 500px;">
            <a-form-item label="Username">
              <a-input placeholder="Your username" />
            </a-form-item>
            <a-form-item label="Email">
              <a-input type="email" placeholder="your@email.com" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary">Save Profile</a-button>
            </a-form-item>
          </a-form>
        </a-tab-pane>

        <!-- API Keys Tab -->
        <a-tab-pane key="api-keys" tab="API Keys">
          <a-typography-title level="5">API Keys</a-typography-title>
          <a-typography-paragraph type="secondary">
            Manage your API keys for external services.
          </a-typography-paragraph>
          <a-button type="primary">Add API Key</a-button>
        </a-tab-pane>

        <!-- Notifications Tab -->
        <a-tab-pane key="notifications" tab="Notifications">
          <a-typography-title level="5">Notification Settings</a-typography-title>
          <a-typography-paragraph type="secondary">
            Configure how you receive notifications.
          </a-typography-paragraph>
          <a-form layout="vertical">
            <a-form-item label="Email Notifications">
              <a-switch />
            </a-form-item>
            <a-form-item label="Push Notifications">
              <a-switch />
            </a-form-item>
          </a-form>
        </a-tab-pane>

        <!-- Credentials Tab (NEW) -->
        <a-tab-pane key="credentials" tab="Credentials">
          <a-typography-title level="5">Trading Credentials</a-typography-title>
          <a-typography-paragraph type="secondary">
            Connect your broker and exchange accounts. All credentials are encrypted.
          </a-typography-paragraph>

          <a-list :data-source="store.credentials" :loading="store.loading" size="default">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta
                  :title="item.name"
                  :description="item.type.toUpperCase() + ' · ' + (item.isActive ? 'Active' : 'Inactive')"
                >
                  <template #avatar>
                    <a-badge :status="item.isActive ? 'success' : 'default'" />
                  </template>
                </a-list-item-meta>
                <template #actions>
                  <a-button size="small" @click="handleTest(item.id)">Test</a-button>
                  <a-button type="link" size="small" danger @click="handleDelete(item.id)">Delete</a-button>
                </template>
              </a-list-item>
            </template>
          </a-list>

          <a-divider />

          <!-- Add new credential -->
          <a-typography-title level="5">Add Credential</a-typography-title>
          <a-form layout="vertical" :model="credForm" style="max-width: 500px;">
            <a-form-item label="Name">
              <a-input v-model:value="credForm.name" placeholder="My IBKR Account" />
            </a-form-item>
            <a-form-item label="Type">
              <a-select v-model:value="credForm.type" @change="credForm.fields = {}">
                <a-select-option value="ibkr">Interactive Brokers (IBKR)</a-select-option>
                <a-select-option value="mt5">MetaTrader 5 (MT5)</a-select-option>
                <a-select-option value="alpaca">Alpaca</a-select-option>
                <a-select-option value="binance">Binance</a-select-option>
                <a-select-option value="okx">OKX</a-select-option>
                <a-select-option value="polymarket">Polymarket</a-select-option>
                <a-select-option value="telegram">Telegram Bot</a-select-option>
              </a-select>
            </a-form-item>
            <!-- Dynamic fields based on type -->
            <template v-if="credForm.type === 'ibkr'">
              <a-form-item label="IB Gateway Host">
                <a-input v-model:value="credForm.fields.ibHost" placeholder="127.0.0.1" />
              </a-form-item>
              <a-form-item label="IB Gateway Port">
                <a-input-number v-model:value="credForm.fields.ibPort" :min="1" :max="65535" style="width:100%" />
              </a-form-item>
            </template>
            <template v-else-if="credForm.type === 'mt5'">
              <a-form-item label="MT5 Server">
                <a-input v-model:value="credForm.fields.mt5Server" placeholder="localhost:8888" />
              </a-form-item>
              <a-form-item label="Login">
                <a-input v-model:value="credForm.fields.mt5Login" />
              </a-form-item>
              <a-form-item label="Password">
                <a-input-password v-model:value="credForm.fields.mt5Password" />
              </a-form-item>
            </template>
            <template v-else-if="credForm.type === 'alpaca'">
              <a-form-item label="API Key">
                <a-input v-model:value="credForm.fields.apiKey" />
              </a-form-item>
              <a-form-item label="API Secret">
                <a-input-password v-model:value="credForm.fields.apiSecret" />
              </a-form-item>
            </template>
            <template v-else-if="credForm.type === 'binance'">
              <a-form-item label="API Key">
                <a-input v-model:value="credForm.fields.binanceApiKey" />
              </a-form-item>
              <a-form-item label="Secret">
                <a-input-password v-model:value="credForm.fields.binanceSecret" />
              </a-form-item>
            </template>
            <template v-else-if="credForm.type === 'telegram'">
              <a-form-item label="Bot Token">
                <a-input v-model:value="credForm.fields.botToken" />
              </a-form-item>
              <a-form-item label="Chat ID">
                <a-input v-model:value="credForm.fields.chatId" />
              </a-form-item>
            </template>
            <template v-else>
              <a-form-item label="API Key">
                <a-input v-model:value="credForm.fields.apiKey" />
              </a-form-item>
              <a-form-item label="Secret">
                <a-input-password v-model:value="credForm.fields.secret" />
              </a-form-item>
            </template>
            <a-form-item>
              <a-button type="primary" :loading="saving" @click="handleSaveCredential">Save Credential</a-button>
            </a-form-item>
          </a-form>
        </a-tab-pane>

        <!-- Preferences Tab (NEW) -->
        <a-tab-pane key="preferences" tab="Preferences">
          <a-typography-title level="5">Trading Preferences</a-typography-title>
          <a-form layout="vertical" style="max-width: 600px;" :model="prefsForm">
            <a-form-item label="Default Exchange">
              <a-select v-model:value="prefsForm.defaultExchange">
                <a-select-option value="binance">Binance</a-select-option>
                <a-select-option value="okx">OKX</a-select-option>
                <a-select-option value="coinbase">Coinbase</a-select-option>
                <a-select-option value="alpaca">Alpaca</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="Default Order Type">
              <a-select v-model:value="prefsForm.defaultOrderType">
                <a-select-option value="market">Market</a-select-option>
                <a-select-option value="limit">Limit</a-select-option>
                <a-select-option value="stop">Stop</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="Default Position Size ($)">
              <a-input-number v-model:value="prefsForm.defaultPositionSize" :min="0" style="width: 100%" />
            </a-form-item>
            <a-form-item label="Risk Per Trade (%)">
              <a-input-number v-model:value="prefsForm.riskPerTrade" :min="0" :max="100" style="width: 100%" />
            </a-form-item>
            <a-form-item label="Enable Telegram Notifications">
              <a-switch v-model:checked="prefsForm.telegramEnabled" />
            </a-form-item>
            <a-form-item label="Enable Email Alerts">
              <a-switch v-model:checked="prefsForm.emailEnabled" />
            </a-form-item>
            <a-form-item label="Theme">
              <a-select v-model:value="prefsForm.theme">
                <a-select-option value="light">Light</a-select-option>
                <a-select-option value="dark">Dark</a-select-option>
                <a-select-option value="system">System</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-space>
                <a-button type="primary" :loading="savingPrefs" @click="handleSavePrefs">Save Preferences</a-button>
                <a-button @click="loadPrefs">Reset</a-button>
              </a-space>
            </a-form-item>
          </a-form>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useCredentialsStore } from '@/stores/credentials'

const activeTab = ref('profile')
const store = useCredentialsStore()
const saving = ref(false)
const savingPrefs = ref(false)

const credForm = reactive({
  name: '',
  type: 'ibkr',
  fields: {} as Record<string, string>
})

const defaultPrefs = {
  defaultExchange: 'binance',
  defaultOrderType: 'market',
  defaultPositionSize: 500,
  riskPerTrade: 2,
  telegramEnabled: false,
  emailEnabled: false,
  theme: 'system',
}
const prefsForm = reactive({ ...defaultPrefs })

onMounted(() => {
  store.fetchAll()
  loadPrefs()
})

function loadPrefs() {
  const saved = localStorage.getItem('tradingPrefs')
  if (saved) {
    try { Object.assign(prefsForm, JSON.parse(saved)) } catch {}
  }
}

async function handleSaveCredential() {
  if (!credForm.name) { message.error('Name required'); return }
  saving.value = true
  try {
    await store.saveCredential({ name: credForm.name, type: credForm.type, fields: { ...credForm.fields } })
    message.success('Credential saved')
    Object.assign(credForm, { name: '', type: 'ibkr', fields: {} })
  } finally { saving.value = false }
}

async function handleTest(id: number) {
  try {
    const result = await store.testConnection(id)
    if (result?.ok) message.success('Connection successful')
    else message.error(result?.message || 'Connection failed')
  } catch { message.error('Connection test failed') }
}

async function handleDelete(id: number) {
  try {
    await store.deleteCredential(id)
    message.success('Credential deleted')
  } catch { message.error('Failed to delete') }
}

async function handleSavePrefs() {
  savingPrefs.value = true
  try {
    localStorage.setItem('tradingPrefs', JSON.stringify({ ...prefsForm }))
    message.success('Preferences saved')
  } finally { savingPrefs.value = false }
}
</script>

<style scoped>
.settings-page {
  padding: 24px;
}
</style>
