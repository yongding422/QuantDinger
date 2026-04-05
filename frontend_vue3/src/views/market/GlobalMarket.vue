<template>
  <div class="global-market-page">
    <div class="page-header">
      <h1>{{ $t('market.title') }}</h1>
      <a-button @click="handleRefresh" :loading="store.loading">
        <template #icon><ReloadOutlined /></template>
        {{ $t('common.refresh') }}
      </a-button>
    </div>

    <a-row :gutter="16">
      <!-- Fear & Greed -->
      <a-col :xs="24" :sm="8">
        <a-card :title="$t('market.fearGreed')" class="market-card">
          <div class="fear-greed-display">
            <a-progress
              type="circle"
              :percent="store.overview?.fearGreed?.value ?? 0"
              :stroke-color="fearGreedColor"
              :format="() => store.overview?.fearGreed?.classification || ''"
              :width="120"
            />
          </div>
        </a-card>
      </a-col>

      <!-- Crypto -->
      <a-col :xs="24" :sm="16">
        <a-card :title="$t('market.crypto')" class="market-card">
          <a-table
            :columns="cryptoColumns"
            :data-source="(store.overview?.crypto ?? []).slice(0, 10)"
            :pagination="false"
            row-key="symbol"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'price'">
                ${{ record.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
              </template>
              <template v-if="column.key === 'change'">
                <span :style="{ color: (record.change24h ?? 0) >= 0 ? '#52c41a' : '#ff4d4f' }">
                  {{ (record.change24h ?? 0) >= 0 ? '+' : '' }}{{ record.change24h?.toFixed(2) }}%
                </span>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>

    <!-- Watchlist -->
    <a-card :title="$t('market.watchlist')" class="market-card" style="margin-top: 16px;">
      <template #extra>
        <a-input-search v-model:value="watchlistSearch" placeholder="Symbol..." style="width: 200px" @search="handleAddToWatchlist" />
      </template>
      <a-table
        :columns="watchlistColumns"
        :data-source="filteredWatchlist"
        :loading="store.loading"
        :pagination="{ pageSize: 20 }"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'symbol'">
            <strong>{{ record.symbol }}</strong>
            <div style="color: var(--color-text-secondary); font-size: 12px;">{{ record.exchange }}</div>
          </template>
          <template v-if="column.key === 'price'">
            ${{ record.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 }) ?? '—' }}
          </template>
          <template v-if="column.key === 'change'">
            <span :style="{ color: (record.changePercent24h ?? 0) >= 0 ? '#52c41a' : '#ff4d4f' }">
              {{ (record.changePercent24h ?? 0) >= 0 ? '+' : '' }}{{ record.changePercent24h?.toFixed(2) ?? '—' }}%
            </span>
          </template>
          <template v-if="column.key === 'actions'">
            <a-popconfirm title="Remove from watchlist?" @confirm="store.removeFromWatchlist(record.symbol, record.exchange)">
              <a-button type="link" danger size="small">✕</a-button>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
      <a-empty v-if="!store.loading && store.watchlist.length === 0" :description="$t('market.noWatchlist')" />
    </a-card>

    <!-- Indices -->
    <a-card v-if="store.overview?.indices?.length" :title="$t('market.indices')" class="market-card" style="margin-top: 16px;">
      <a-row :gutter="[12, 12]">
        <a-col v-for="idx in store.overview.indices" :key="idx.name" :xs="12" :sm="8" :md="6">
          <div class="index-item">
            <div class="index-name">{{ idx.name }}</div>
            <div class="index-value">{{ idx.value?.toLocaleString() }}</div>
            <div class="index-change" :style="{ color: (idx.change ?? 0) >= 0 ? '#52c41a' : '#ff4d4f' }">
              {{ (idx.change ?? 0) >= 0 ? '+' : '' }}{{ idx.change?.toFixed(2) }}%
            </div>
          </div>
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useMarketStore } from '@/stores/market'

const store = useMarketStore()
const watchlistSearch = ref('')

const cryptoColumns = [
  { title: 'Name', dataIndex: 'name', key: 'name' },
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Price', key: 'price' },
  { title: '24h Change', key: 'change' },
]

const watchlistColumns = [
  { title: 'Symbol', key: 'symbol' },
  { title: 'Price', key: 'price' },
  { title: '24h Change', key: 'change' },
  { title: 'Actions', key: 'actions' },
]

const filteredWatchlist = computed(() => {
  if (!watchlistSearch.value) return store.watchlist
  const q = watchlistSearch.value.toLowerCase()
  return store.watchlist.filter(w =>
    w.symbol.toLowerCase().includes(q) || w.exchange.toLowerCase().includes(q)
  )
})

const fearGreedColor = computed(() => {
  const v = store.overview?.fearGreed?.value ?? 50
  if (v < 30) return '#ff4d4f'
  if (v < 70) return '#faad14'
  return '#52c41a'
})

onMounted(async () => {
  await Promise.all([store.fetchOverview(), store.fetchWatchlist()])
})

async function handleRefresh() {
  await Promise.all([store.fetchOverview(), store.fetchWatchlistPrices()])
}

async function handleAddToWatchlist(symbol: string) {
  if (!symbol) return
  try {
    await store.addToWatchlist(symbol.toUpperCase(), 'binance')
    message.success('Added to watchlist')
    watchlistSearch.value = ''
  } catch {
    message.error('Failed to add to watchlist')
  }
}
</script>

<style scoped>
.global-market-page { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h1 { margin: 0; }
.market-card { margin-bottom: 0; }
.fear-greed-display { display: flex; justify-content: center; padding: 16px; }
.index-item {
  background: var(--color-bg-hover);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}
.index-name { font-size: 13px; color: var(--color-text-secondary); }
.index-value { font-size: 18px; font-weight: 600; margin: 4px 0; }
.index-change { font-size: 14px; }
</style>
