<template>
  <div class="strategy-list-page">
    <div class="page-header">
      <h1>{{ $t('strategy.title') }}</h1>
      <div class="header-actions">
        <a-button v-if="selectedRowKeys.length > 0" @click="handleBatchStart" :loading="actionLoading">
          {{ $t('strategy.batchStart') }}
        </a-button>
        <a-button v-if="selectedRowKeys.length > 0" @click="handleBatchStop" :loading="actionLoading">
          {{ $t('strategy.batchStop') }}
        </a-button>
        <a-button v-if="selectedRowKeys.length > 0" danger @click="handleBatchDelete" :loading="actionLoading">
          {{ $t('strategy.batchDelete') }}
        </a-button>
        <a-button type="primary" @click="$router.push('/strategies/new')">
          <template #icon><PlusOutlined /></template>
          {{ $t('strategy.createStrategy') }}
        </a-button>
      </div>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <a-input-search
        v-model:value="searchText"
        :placeholder="$t('common.search')"
        style="width: 240px"
        @search="onSearch"
      />
      <a-select
        v-model:value="filterStatus"
        :placeholder="$t('strategy.status')"
        allow-clear
        style="width: 120px"
        @change="onSearch"
      >
        <a-select-option value="running">{{ $t('strategy.running') }}</a-select-option>
        <a-select-option value="stopped">{{ $t('strategy.stopped') }}</a-select-option>
      </a-select>
      <a-select
        v-model:value="filterExchange"
        :placeholder="$t('strategy.exchange')"
        allow-clear
        style="width: 140px"
        @change="onSearch"
      >
        <a-select-option value="binance">Binance</a-select-option>
        <a-select-option value="okx">OKX</a-select-option>
        <a-select-option value="coinbase">Coinbase</a-select-option>
        <a-select-option value="alpaca">Alpaca</a-select-option>
      </a-select>
    </div>

    <!-- Table -->
    <a-table
      :columns="columns"
      :data-source="filteredStrategies"
      :loading="store.loading"
      :pagination="{ pageSize: 20 }"
      :row-selection="{ selectedRowKeys, onChange: onSelectChange }"
      row-key="id"
      size="small"
      class="strategy-table"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          <router-link :to="`/strategies/${record.id}`" class="strategy-name-link">
            {{ record.name }}
          </router-link>
          <div class="strategy-meta">
            <a-tag>{{ record.exchange }}</a-tag>
            <a-tag>{{ record.symbol }}</a-tag>
            <a-tag>{{ record.marketType }}</a-tag>
          </div>
        </template>

        <template v-if="column.key === 'status'">
          <a-badge
            :status="record.status === 'running' ? 'success' : record.status === 'error' ? 'error' : 'default'"
            :text="record.status === 'running' ? $t('strategy.running') : record.status === 'error' ? 'Error' : $t('strategy.stopped')"
          />
        </template>

        <template v-if="column.key === 'actions'">
          <a-button
            v-if="record.status !== 'running'"
            type="link"
            size="small"
            @click="handleStart(record.id)"
            :loading="actionLoading"
          >
            {{ $t('strategy.start') }}
          </a-button>
          <a-button
            v-else
            type="link"
            size="small"
            @click="handleStop(record.id)"
            :loading="actionLoading"
          >
            {{ $t('strategy.stop') }}
          </a-button>
          <router-link :to="`/strategies/${record.id}`">
            <a-button type="link" size="small">{{ $t('common.edit') }}</a-button>
          </router-link>
          <a-popconfirm
            :title="$t('strategy.confirmDelete')"
            @confirm="handleDelete(record.id)"
          >
            <a-button type="link" danger size="small">{{ $t('common.delete') }}</a-button>
          </a-popconfirm>
        </template>
      </template>
    </a-table>

    <!-- Empty state -->
    <a-empty
      v-if="!store.loading && store.strategies.length === 0"
      :description="$t('strategy.noStrategies')"
      class="empty-state"
    >
      <a-button type="primary" @click="$router.push('/strategies/new')">
        {{ $t('strategy.createFirst') }}
      </a-button>
    </a-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { useStrategiesStore } from '@/stores/strategies'
import type { Strategy } from '@/api/strategy'

const store = useStrategiesStore()
const searchText = ref('')
const filterStatus = ref<string | undefined>()
const filterExchange = ref<string | undefined>()
const selectedRowKeys = ref<number[]>([])
const actionLoading = ref(false)

const columns = [
  { title: 'Name', key: 'name', width: 300 },
  { title: 'Status', key: 'status', width: 120 },
  { title: 'Created', dataIndex: 'createdAt', key: 'createdAt', width: 160 },
  { title: 'Actions', key: 'actions', width: 280 },
]

const filteredStrategies = computed(() => {
  return store.strategies.filter((s: Strategy) => {
    if (filterStatus.value && s.status !== filterStatus.value) return false
    if (filterExchange.value && s.exchange !== filterExchange.value) return false
    if (searchText.value) {
      const q = searchText.value.toLowerCase()
      if (!s.name.toLowerCase().includes(q) && !s.symbol.toLowerCase().includes(q)) return false
    }
    return true
  })
})

onMounted(() => {
  store.fetchStrategies()
})

function onSelectChange(keys: number[]) {
  selectedRowKeys.value = keys
}

function onSearch() {
  // filtering is computed — just re-apply
}

async function handleStart(id: number) {
  actionLoading.value = true
  try {
    await store.startStrategy(id)
    message.success('Strategy started')
  } catch {
    message.error('Failed to start strategy')
  } finally {
    actionLoading.value = false
  }
}

async function handleStop(id: number) {
  actionLoading.value = true
  try {
    await store.stopStrategy(id)
    message.success('Strategy stopped')
  } catch {
    message.error('Failed to stop strategy')
  } finally {
    actionLoading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await store.deleteStrategy(id)
    message.success('Strategy deleted')
  } catch {
    message.error('Failed to delete strategy')
  }
}

async function handleBatchStart() {
  if (!selectedRowKeys.value.length) return
  actionLoading.value = true
  try {
    await store.batchStart(selectedRowKeys.value)
    message.success(`${selectedRowKeys.value.length} strategies started`)
    selectedRowKeys.value = []
  } catch {
    message.error('Batch start failed')
  } finally {
    actionLoading.value = false
  }
}

async function handleBatchStop() {
  if (!selectedRowKeys.value.length) return
  actionLoading.value = true
  try {
    await store.batchStop(selectedRowKeys.value)
    message.success(`${selectedRowKeys.value.length} strategies stopped`)
    selectedRowKeys.value = []
  } catch {
    message.error('Batch stop failed')
  } finally {
    actionLoading.value = false
  }
}

async function handleBatchDelete() {
  if (!selectedRowKeys.value.length) return
  actionLoading.value = true
  try {
    await store.batchDelete(selectedRowKeys.value)
    message.success(`${selectedRowKeys.value.length} strategies deleted`)
    selectedRowKeys.value = []
  } catch {
    message.error('Batch delete failed')
  } finally {
    actionLoading.value = false
  }
}
</script>

<style scoped>
.strategy-list-page { padding: 16px; }
.page-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;
}
.page-header h1 { margin: 0; }
.header-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.filter-bar { display: flex; gap: 8px; margin-bottom: 16px; align-items: center; }
.strategy-name-link { font-weight: 600; }
.strategy-meta { display: flex; gap: 4px; margin-top: 4px; }
.strategy-table { background: var(--color-bg-card); border-radius: 8px; }
.empty-state { padding: 48px 0; }
</style>