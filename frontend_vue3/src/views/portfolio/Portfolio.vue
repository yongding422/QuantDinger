<template>
  <div class="portfolio-page">
    <div class="page-header">
      <h1>{{ $t('portfolio.title') }}</h1>
      <a-button type="primary" @click="activeTab === 'positions' ? showPositionModal = true : null">
        <template #icon><PlusOutlined /></template>
        {{ activeTab === 'positions' ? $t('portfolio.addPosition') : activeTab === 'alerts' ? $t('portfolio.addAlert') : $t('portfolio.addMonitor') }}
      </a-button>
    </div>

    <!-- Summary bar -->
    <a-row :gutter="16" class="summary-bar" v-if="store.summary">
      <a-col :span="8">
        <a-statistic title="Total Value" :value="store.summary.totalValue" prefix="$" :precision="2" />
      </a-col>
      <a-col :span="8">
        <a-statistic title="Total P&L" :value="store.summary.totalPnl" prefix="$" :precision="2"
          :value-style="{ color: store.summary.totalPnl >= 0 ? '#52c41a' : '#ff4d4f' }" />
      </a-col>
      <a-col :span="8">
        <a-statistic title="Positions" :value="store.summary.totalPositions" />
      </a-col>
    </a-row>

    <!-- Tabs -->
    <a-tabs v-model:activeKey="activeTab" class="portfolio-tabs">
      <a-tab-pane key="positions" :tab="$t('portfolio.positions')">
        <a-table
          :columns="positionColumns"
          :data-source="store.positions"
          :loading="store.loading"
          row-key="id"
          size="small"
          :pagination="{ pageSize: 20 }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'side'">
              <a-tag :color="record.side === 'long' || record.side === 'spot' ? 'green' : 'red'">
                {{ record.side.toUpperCase() }}
              </a-tag>
            </template>
            <template v-if="column.key === 'pnl'">
              <span v-if="record.pnl !== undefined" :style="{ color: record.pnl >= 0 ? '#52c41a' : '#ff4d4f' }">
                {{ record.pnl >= 0 ? '+' : '' }}{{ record.pnl.toFixed(2) }}
                ({{ record.pnlPercent !== undefined ? (record.pnlPercent >= 0 ? '+' : '') + record.pnlPercent.toFixed(2) + '%' : '' }})
              </span>
            </template>
            <template v-if="column.key === 'actions'">
              <a-button type="link" size="small" @click="editPosition(record)">{{ $t('common.edit') }}</a-button>
              <a-popconfirm :title="$t('common.confirmDelete')" @confirm="store.deletePosition(record.id)">
                <a-button type="link" danger size="small">{{ $t('common.delete') }}</a-button>
              </a-popconfirm>
            </template>
          </template>
        </a-table>
        <a-empty v-if="!store.loading && store.positions.length === 0" :description="$t('portfolio.noPositions')" />
      </a-tab-pane>

      <a-tab-pane key="alerts" :tab="$t('portfolio.alerts')">
        <a-table
          :columns="alertColumns"
          :data-source="store.alerts"
          :loading="store.loading"
          row-key="id"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'triggered'">
              <a-badge :status="record.triggered ? 'error' : 'default'" :text="record.triggered ? 'Triggered' : 'Active'" />
            </template>
            <template v-if="column.key === 'actions'">
              <a-popconfirm :title="$t('common.confirmDelete')" @confirm="store.deleteAlert(record.id)">
                <a-button type="link" danger size="small">{{ $t('common.delete') }}</a-button>
              </a-popconfirm>
            </template>
          </template>
        </a-table>
      </a-tab-pane>
    </a-tabs>

    <!-- Position modal (add/edit) -->
    <a-modal v-model:open="showPositionModal" :title="editingPosition ? $t('portfolio.editPosition') : $t('portfolio.addPosition')" @ok="savePosition" :confirm-loading="saving">
      <a-form :model="positionForm" layout="vertical">
        <a-form-item :label="$t('portfolio.positionSymbol')" required>
          <a-input v-model:value="positionForm.symbol" placeholder="BTC, AAPL, etc." />
        </a-form-item>
        <a-form-item :label="$t('strategy.exchange')" required>
          <a-select v-model:value="positionForm.exchange" placeholder="Select exchange">
            <a-select-option value="binance">Binance</a-select-option>
            <a-select-option value="okx">OKX</a-select-option>
            <a-select-option value="coinbase">Coinbase</a-select-option>
            <a-select-option value="alpaca">Alpaca</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item :label="$t('portfolio.positionSide')" required>
          <a-select v-model:value="positionForm.side">
            <a-select-option value="spot">{{ $t('portfolio.spot') }}</a-select-option>
            <a-select-option value="long">{{ $t('portfolio.long') }}</a-select-option>
            <a-select-option value="short">{{ $t('portfolio.short') }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item :label="$t('portfolio.entryPrice')" required>
          <a-input-number v-model:value="positionForm.entryPrice" :min="0" style="width: 100%" />
        </a-form-item>
        <a-form-item :label="$t('portfolio.currentPrice')">
          <a-input-number v-model:value="positionForm.currentPrice" :min="0" style="width: 100%" />
        </a-form-item>
        <a-form-item :label="$t('portfolio.quantity')" required>
          <a-input-number v-model:value="positionForm.quantity" :min="0" style="width: 100%" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { usePortfolioStore, type Position } from '@/stores/portfolio'

const store = usePortfolioStore()
const activeTab = ref('positions')
const showPositionModal = ref(false)
const editingPosition = ref<Position | null>(null)
const saving = ref(false)

const positionForm = reactive({
  symbol: '',
  exchange: '',
  side: 'spot' as 'spot' | 'long' | 'short',
  entryPrice: 0,
  currentPrice: 0,
  quantity: 0,
})

const positionColumns = [
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Exchange', dataIndex: 'exchange', key: 'exchange' },
  { title: 'Side', key: 'side' },
  { title: 'Entry Price', dataIndex: 'entryPrice', key: 'entryPrice' },
  { title: 'Current Price', dataIndex: 'currentPrice', key: 'currentPrice' },
  { title: 'Qty', dataIndex: 'quantity', key: 'quantity' },
  { title: 'P&L', key: 'pnl' },
  { title: 'Actions', key: 'actions' },
]

const alertColumns = [
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Condition', dataIndex: 'condition', key: 'condition' },
  { title: 'Status', key: 'triggered' },
  { title: 'Actions', key: 'actions' },
]

onMounted(() => {
  store.fetchAll()
})

function editPosition(pos: Position) {
  editingPosition.value = pos
  Object.assign(positionForm, {
    symbol: pos.symbol,
    exchange: pos.exchange,
    side: pos.side,
    entryPrice: pos.entryPrice,
    currentPrice: pos.currentPrice ?? 0,
    quantity: pos.quantity,
  })
  showPositionModal.value = true
}

async function savePosition() {
  saving.value = true
  try {
    if (editingPosition.value) {
      await store.updatePosition(editingPosition.value.id, { ...positionForm })
    } else {
      await store.addPosition({ ...positionForm })
    }
    showPositionModal.value = false
    editingPosition.value = null
    message.success('Saved')
  } catch {
    message.error('Failed to save')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.portfolio-page { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h1 { margin: 0; }
.summary-bar { margin-bottom: 16px; background: var(--color-bg-card); padding: 16px; border-radius: 8px; }
.portfolio-tabs { background: var(--color-bg-card); padding: 16px; border-radius: 8px; }
</style>
