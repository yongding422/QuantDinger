<template>
  <div class="strategy-detail-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <a-button @click="$router.push('/strategies')" class="back-btn">
          <template #icon><LeftOutlined /></template>
        </a-button>
        <div>
          <h1 class="strategy-name">{{ store.currentStrategy?.name ?? '—' }}</h1>
          <div class="strategy-meta">
            <a-tag :color="statusColor">{{ store.currentStrategy?.status ?? '—' }}</a-tag>
            <span class="meta-item">
              <span class="meta-label">{{ $t('strategy.exchange') }}:</span>
              {{ store.currentStrategy?.exchange }}
            </span>
            <span class="meta-item">
              <span class="meta-label">{{ $t('strategy.symbol') }}:</span>
              {{ store.currentStrategy?.symbol }}
            </span>
            <span class="meta-item">
              <span class="meta-label">{{ $t('strategy.marketType') }}:</span>
              {{ store.currentStrategy?.marketType }}
            </span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <a-button
          v-if="store.currentStrategy?.status !== 'running'"
          type="primary"
          :loading="actionLoading"
          @click="handleStart"
        >
          <template #icon><PlayCircleOutlined /></template>
          {{ $t('strategy.start') }}
        </a-button>
        <a-button
          v-else
          danger
          :loading="actionLoading"
          @click="handleStop"
        >
          <template #icon><StopOutlined /></template>
          {{ $t('strategy.stop') }}
        </a-button>
        <a-button @click="showEditModal = true">
          <template #icon><EditOutlined /></template>
          {{ $t('common.edit') }}
        </a-button>
      </div>
    </div>

    <!-- Quick stats -->
    <a-row :gutter="[16, 16]" class="stats-row">
      <a-col :xs="12" :sm="6">
        <a-card size="small" class="stat-card">
          <a-statistic title="Total Trades" :value="store.trades.length" />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card size="small" class="stat-card">
          <a-statistic
            title="Win Rate"
            :value="winRate"
            :precision="1"
            suffix="%"
          />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card size="small" class="stat-card">
          <a-statistic
            title="Total P&L"
            :value="totalPnl"
            :precision="2"
            prefix="$"
            :value-style="{ color: totalPnl >= 0 ? '#52c41a' : '#ff4d4f' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="6">
        <a-card size="small" class="stat-card">
          <a-statistic
            title="Backtests"
            :value="store.backtestHistory.length"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- Tabs -->
    <a-tabs v-model:activeKey="activeTab" class="detail-tabs">
      <!-- Overview Tab -->
      <a-tab-pane key="overview" :tab="$t('strategy.performance')">
        <a-card :title="$t('strategy.positionSizing')" size="small" class="section-card">
          <a-descriptions :column="2" size="small" bordered>
            <a-descriptions-item :label="$t('strategy.maxPositions')">
              {{ store.currentStrategy?.config?.maxPositions ?? '—' }}
            </a-descriptions-item>
            <a-descriptions-item :label="$t('strategy.leverage')">
              {{ store.currentStrategy?.config?.leverage ?? '—' }}x
            </a-descriptions-item>
            <a-descriptions-item :label="$t('strategy.amount')">
              {{ store.currentStrategy?.config?.amount ?? '—' }}
            </a-descriptions-item>
            <a-descriptions-item :label="$t('strategy.stopLoss')">
              {{ store.currentStrategy?.config?.stopLoss ?? '—' }}%
            </a-descriptions-item>
            <a-descriptions-item :label="$t('strategy.takeProfit')">
              {{ store.currentStrategy?.config?.takeProfit ?? '—' }}%
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card :title="$t('strategy.indicators')" size="small" class="section-card">
          <a-tag v-for="(ind, i) in (store.currentStrategy?.config?.indicators ?? [])" :key="i" color="blue">
            {{ ind.name ?? ind.type ?? 'indicator' }}
          </a-tag>
          <a-empty v-if="!store.currentStrategy?.config?.indicators?.length" :description="$t('common.noData')" :image="Empty.PRESENTED_IMAGE_SIMPLE" />
        </a-card>

        <a-card :title="$t('strategy.triggers')" size="small" class="section-card">
          <pre class="config-json">{{ JSON.stringify(store.currentStrategy?.config?.triggers ?? {}, null, 2) }}</pre>
          <a-empty v-if="!store.currentStrategy?.config?.triggers" :description="$t('common.noData')" :image="Empty.PRESENTED_IMAGE_SIMPLE" />
        </a-card>
      </a-tab-pane>

      <!-- Backtest Tab -->
      <a-tab-pane key="backtest" :tab="$t('strategy.backtest')">
        <!-- Run backtest form -->
        <a-card size="small" class="section-card">
          <template #title>
            <span>{{ $t('backtest.runBacktest') }}</span>
          </template>
          <a-form layout="inline" :model="backtestForm">
            <a-form-item :label="$t('backtest.startDate')">
              <a-date-picker v-model:value="backtestForm.startDate" />
            </a-form-item>
            <a-form-item :label="$t('backtest.endDate')">
              <a-date-picker v-model:value="backtestForm.endDate" />
            </a-form-item>
            <a-form-item :label="$t('backtest.initialCapital')">
              <a-input-number v-model:value="backtestForm.initialCapital" :min="100" style="width: 160px" />
            </a-form-item>
            <a-form-item>
              <a-button
                type="primary"
                :loading="store.backtestRunning"
                @click="handleRunBacktest"
              >
                {{ store.backtestRunning ? $t('backtest.running') : $t('backtest.runBacktest') }}
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- Backtest results -->
        <a-card :title="$t('backtest.history')" size="small" class="section-card">
          <a-table
            :columns="backtestColumns"
            :data-source="store.backtestHistory"
            :loading="store.loading"
            :pagination="{ pageSize: 5 }"
            row-key="id"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'profit'">
                <span :style="{ color: record.profit >= 0 ? '#52c41a' : '#ff4d4f' }">
                  {{ record.profit >= 0 ? '+' : '' }}{{ record.profit.toFixed(2) }}
                  ({{ record.profitPercent.toFixed(2) }}%)
                </span>
              </template>
              <template v-else-if="column.key === 'winRate'">
                {{ (record.winRate * 100).toFixed(1) }}%
              </template>
              <template v-else-if="column.key === 'maxDrawdown'">
                {{ record.maxDrawdownPercent.toFixed(2) }}%
              </template>
              <template v-else-if="column.key === 'status'">
                <a-tag :color="record.status === 'completed' ? 'green' : record.status === 'running' ? 'blue' : 'red'">
                  {{ record.status }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'actions'">
                <a-button type="link" size="small" @click="selectedBacktest = record; showBacktestDetail = true">
                  {{ $t('common.detail') ?? 'Detail' }}
                </a-button>
              </template>
            </template>
          </a-table>
          <a-empty v-if="!store.loading && store.backtestHistory.length === 0" :description="$t('backtest.noHistory')" />
        </a-card>
      </a-tab-pane>

      <!-- Equity Curve Tab -->
      <a-tab-pane key="equity" :tab="$t('strategy.equityCurve')">
        <a-card size="small" class="section-card">
          <EquityCurveChart :data="store.equityCurve" :loading="store.loading" />
          <a-empty v-if="!store.loading && store.equityCurve.length === 0" :description="$t('common.noData')" />
        </a-card>
      </a-tab-pane>

      <!-- Trades Tab -->
      <a-tab-pane key="trades" :tab="$t('strategy.trades')">
        <a-card size="small" class="section-card">
          <a-table
            :columns="tradeColumns"
            :data-source="store.trades"
            :loading="store.loading"
            :pagination="{ pageSize: 10 }"
            row-key="id"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'side'">
                <a-tag :color="record.side === 'buy' ? 'green' : 'red'">
                  {{ record.side.toUpperCase() }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'pnl'">
                <span v-if="record.pnl !== undefined" :style="{ color: record.pnl >= 0 ? '#52c41a' : '#ff4d4f' }">
                  {{ record.pnl >= 0 ? '+' : '' }}{{ record.pnl.toFixed(2) }}
                </span>
                <span v-else>—</span>
              </template>
            </template>
          </a-table>
          <a-empty v-if="!store.loading && store.trades.length === 0" :description="$t('common.noData')" />
        </a-card>
      </a-tab-pane>
    </a-tabs>

    <!-- Edit Strategy Modal -->
    <a-modal
      v-model:open="showEditModal"
      :title="$t('strategy.editStrategy')"
      @ok="handleUpdate"
      :confirmLoading="actionLoading"
      ok-text="Save"
    >
      <a-form layout="vertical" :model="editForm">
        <a-form-item :label="$t('strategy.strategyName')">
          <a-input v-model:value="editForm.name" />
        </a-form-item>
        <a-form-item :label="$t('strategy.stopLoss')">
          <a-input-number v-model:value="editForm.config.stopLoss" :min="0" :max="100" suffix="%" style="width:100%" />
        </a-form-item>
        <a-form-item :label="$t('strategy.takeProfit')">
          <a-input-number v-model:value="editForm.config.takeProfit" :min="0" :max="100" suffix="%" style="width:100%" />
        </a-form-item>
        <a-form-item :label="$t('strategy.maxPositions')">
          <a-input-number v-model:value="editForm.config.maxPositions" :min="1" style="width:100%" />
        </a-form-item>
        <a-form-item :label="$t('strategy.leverage')">
          <a-input-number v-model:value="editForm.config.leverage" :min="1" :max="125" style="width:100%" />
        </a-form-item>
        <a-form-item :label="$t('strategy.amount')">
          <a-input-number v-model:value="editForm.config.amount" :min="0" style="width:100%" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- Backtest Detail Modal -->
    <a-modal
      v-model:open="showBacktestDetail"
      :title="`Backtest Result — ${selectedBacktest?.id ?? ''}`"
      :footer="null"
      width="700px"
    >
      <a-descriptions :column="2" bordered size="small" v-if="selectedBacktest">
        <a-descriptions-item label="Initial Capital">${{ selectedBacktest.initialCapital.toLocaleString() }}</a-descriptions-item>
        <a-descriptions-item label="Final Capital">${{ selectedBacktest.finalCapital.toLocaleString() }}</a-descriptions-item>
        <a-descriptions-item label="Profit">
          <span :style="{ color: selectedBacktest.profit >= 0 ? '#52c41a' : '#ff4d4f' }">
            {{ selectedBacktest.profit >= 0 ? '+' : '' }}${{ selectedBacktest.profit.toFixed(2) }}
            ({{ selectedBacktest.profitPercent.toFixed(2) }}%)
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="Win Rate">{{ (selectedBacktest.winRate * 100).toFixed(1) }}%</a-descriptions-item>
        <a-descriptions-item label="Sharpe Ratio">{{ selectedBacktest.sharpeRatio.toFixed(3) }}</a-descriptions-item>
        <a-descriptions-item label="Max Drawdown">{{ selectedBacktest.maxDrawdownPercent.toFixed(2) }}%</a-descriptions-item>
        <a-descriptions-item label="Total Trades">{{ selectedBacktest.totalTrades }}</a-descriptions-item>
        <a-descriptions-item label="Profit Factor">{{ selectedBacktest.profitFactor.toFixed(2) }}</a-descriptions-item>
        <a-descriptions-item label="Avg Trade">${{ selectedBacktest.avgTrade.toFixed(2) }}</a-descriptions-item>
        <a-descriptions-item label="Period">{{ selectedBacktest.startDate }} → {{ selectedBacktest.endDate }}</a-descriptions-item>
      </a-descriptions>
      <div v-if="selectedBacktest?.equityCurve?.length" style="margin-top: 16px">
        <EquityCurveChart :data="selectedBacktest.equityCurve" :height="200" />
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Empty } from 'ant-design-vue'
import {
  LeftOutlined,
  PlayCircleOutlined,
  StopOutlined,
  EditOutlined,
} from '@ant-design/icons-vue'
import dayjs, { type Dayjs } from 'dayjs'
import { useStrategiesStore } from '@/stores/strategies'
import type { BacktestResult } from '@/api/strategies'
import EquityCurveChart from './EquityCurveChart.vue'

const route = useRoute()
const router = useRouter()
const store = useStrategiesStore()

const strategyId = computed(() => Number(route.params.id))

const activeTab = ref('overview')
const showEditModal = ref(false)
const showBacktestDetail = ref(false)
const selectedBacktest = ref<BacktestResult | null>(null)
const actionLoading = ref(false)

const backtestForm = ref({
  startDate: null as Dayjs | null,
  endDate: null as Dayjs | null,
  initialCapital: 10000,
})

const editForm = ref({
  name: '',
  config: {
    stopLoss: undefined as number | undefined,
    takeProfit: undefined as number | undefined,
    maxPositions: undefined as number | undefined,
    leverage: undefined as number | undefined,
    amount: undefined as number | undefined,
  },
})

// Sync edit form when modal opens
watch(showEditModal, (open) => {
  if (open && store.currentStrategy) {
    editForm.value = {
      name: store.currentStrategy.name,
      config: {
        stopLoss: store.currentStrategy.config?.stopLoss,
        takeProfit: store.currentStrategy.config?.takeProfit,
        maxPositions: store.currentStrategy.config?.maxPositions,
        leverage: store.currentStrategy.config?.leverage,
        amount: store.currentStrategy.config?.amount,
      },
    }
  }
})

const statusColor = computed(() => {
  const s = store.currentStrategy?.status
  if (s === 'running') return 'green'
  if (s === 'pending') return 'blue'
  return 'default'
})

const totalPnl = computed(() =>
  store.trades.reduce((sum, t) => sum + (t.pnl ?? 0), 0)
)

const winRate = computed(() => {
  const trades = store.trades
  if (!trades.length) return 0
  const wins = trades.filter(t => (t.pnl ?? 0) > 0).length
  return (wins / trades.length) * 100
})

const tradeColumns = [
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Side', key: 'side' },
  { title: 'Price', dataIndex: 'price', key: 'price' },
  { title: 'Qty', dataIndex: 'quantity', key: 'quantity' },
  { title: 'P&L', key: 'pnl' },
  { title: 'Time', dataIndex: 'time', key: 'time' },
]

const backtestColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: 'Period', key: 'period', customRender: ({ record }: { record: BacktestResult }) =>
    `${record.startDate} → ${record.endDate}` },
  { title: 'Initial', dataIndex: 'initialCapital', key: 'initialCapital' },
  { title: 'Final', dataIndex: 'finalCapital', key: 'finalCapital' },
  { title: 'Profit', key: 'profit' },
  { title: 'Win Rate', key: 'winRate' },
  { title: 'Sharpe', dataIndex: 'sharpeRatio', key: 'sharpeRatio' },
  { title: 'Max DD', key: 'maxDrawdown' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions' },
]

onMounted(async () => {
  if (strategyId.value) {
    await store.loadAll(strategyId.value)
  }
})

async function handleStart() {
  actionLoading.value = true
  try {
    await store.startStrategy(strategyId.value)
    message.success('Strategy started')
  } catch {
    message.error('Failed to start strategy')
  } finally {
    actionLoading.value = false
  }
}

async function handleStop() {
  actionLoading.value = true
  try {
    await store.stopStrategy(strategyId.value)
    message.success('Strategy stopped')
  } catch {
    message.error('Failed to stop strategy')
  } finally {
    actionLoading.value = false
  }
}

async function handleUpdate() {
  actionLoading.value = true
  try {
    await store.updateStrategy(strategyId.value, {
      name: editForm.value.name,
      config: {
        stopLoss: editForm.value.config.stopLoss,
        takeProfit: editForm.value.config.takeProfit,
        maxPositions: editForm.value.config.maxPositions,
        leverage: editForm.value.config.leverage,
        amount: editForm.value.config.amount,
      },
    })
    message.success('Strategy updated')
    showEditModal.value = false
  } catch {
    message.error('Failed to update strategy')
  } finally {
    actionLoading.value = false
  }
}

async function handleRunBacktest() {
  if (!backtestForm.value.startDate || !backtestForm.value.endDate) {
    message.warning('Please select start and end dates')
    return
  }
  actionLoading.value = true
  try {
    await store.runBacktest(strategyId.value, {
      startDate: backtestForm.value.startDate.format('YYYY-MM-DD'),
      endDate: backtestForm.value.endDate.format('YYYY-MM-DD'),
      initialCapital: backtestForm.value.initialCapital,
    })
    message.success('Backtest completed')
    activeTab.value = 'backtest'
  } catch {
    message.error('Backtest failed')
  } finally {
    actionLoading.value = false
  }
}
</script>

<style scoped>
.strategy-detail-page { padding: 16px; }
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 12px;
}
.header-left { display: flex; align-items: flex-start; gap: 12px; }
.back-btn { margin-top: 4px; }
.strategy-name { margin: 0 0 4px; font-size: 20px; line-height: 1.2; }
.strategy-meta { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; font-size: 13px; }
.meta-label { color: #888; }
.header-actions { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.stats-row { margin-bottom: 16px; }
.stat-card { text-align: center; }
.detail-tabs { background: #fff; padding: 0 16px 16px; border-radius: 8px; }
.section-card { margin-bottom: 16px; }
.config-json {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  overflow: auto;
  max-height: 200px;
  margin: 0;
}
</style>
