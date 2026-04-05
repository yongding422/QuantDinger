<template>
  <div class="backtest-page">
    <div class="page-header">
      <h1>{{ $t('backtest.title') }}</h1>
      <a-space>
        <a-button :loading="refreshingPrecision" @click="loadPrecisionInfo">
          <template #icon><ReloadOutlined /></template>
          {{ $t('common.refresh') }}
        </a-button>
      </a-space>
    </div>

    <a-row :gutter="16">
      <!-- Run form -->
      <a-col :xs="24" :lg="12">
        <a-card :title="$t('backtest.runBacktest')" class="run-card">
          <a-form layout="vertical" :model="form">
            <a-form-item :label="$t('indicator.indicatorName')" required>
              <a-select
                v-model:value="form.indicator"
                :placeholder="$t('indicator.selectIndicator') || 'Select indicator'"
                :loading="indicatorsStore.loading"
                show-search
                :filter-option="(input: string, option: any) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())"
              >
                <a-select-option v-for="ind in indicatorsStore.indicators" :key="ind.id" :value="ind.name" :label="ind.name">
                  {{ ind.name }}
                </a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item :label="$t('backtest.symbol')" required>
              <a-input v-model:value="form.symbol" placeholder="BTC, AAPL, etc." />
            </a-form-item>

            <a-form-item label="Exchange">
              <a-select v-model:value="form.exchange" style="width: 100%">
                <a-select-option value="binance">Binance</a-select-option>
                <a-select-option value="okx">OKX</a-select-option>
                <a-select-option value="coinbase">Coinbase</a-select-option>
                <a-select-option value="alpaca">Alpaca</a-select-option>
                <a-select-option value="ibkr">Interactive Brokers</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item :label="$t('backtest.startDate')" required>
              <a-date-picker v-model:value="form.startDate" style="width: 100%" value-format="YYYY-MM-DD" />
            </a-form-item>

            <a-form-item :label="$t('backtest.endDate')" required>
              <a-date-picker v-model:value="form.endDate" style="width: 100%" value-format="YYYY-MM-DD" />
            </a-form-item>

            <a-form-item :label="$t('backtest.initialCapital')">
              <a-input-number v-model:value="form.initialCapital" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>

            <a-form-item>
              <a-button type="primary" block :loading="running" @click="handleRunBacktest">
                {{ $t('backtest.runBacktest') }}
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>

      <!-- Precision info -->
      <a-col :xs="24" :lg="12">
        <a-card :title="$t('backtest.precisionInfo')">
          <template #extra>
            <a-tag :color="precisionInfo.length > 0 ? 'green' : 'default'">
              {{ precisionInfo.length }} indicators
            </a-tag>
          </template>
          <a-table
            :columns="precisionColumns"
            :data-source="precisionInfo"
            :pagination="false"
            :loading="refreshingPrecision"
            row-key="indicator"
            size="small"
            :scroll="{ x: 500 }"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'hitRate'">
                <a-progress
                  :percent="Math.round(record.hitRate * 100)"
                  :stroke-color="record.hitRate > 0.5 ? '#52c41a' : record.hitRate > 0.4 ? '#faad14' : '#ff4d4f'"
                  size="small"
                  style="width: 100px"
                />
                <span style="margin-left: 8px">{{ (record.hitRate * 100).toFixed(1) }}%</span>
              </template>
              <template v-else-if="column.key === 'avgDiff'">
                {{ record.avgDiff.toFixed(4) }}
              </template>
              <template v-else-if="column.key === 'sampleSize'">
                {{ record.sampleSize }}
              </template>
            </template>
          </a-table>
          <a-empty v-if="!refreshingPrecision && precisionInfo.length === 0" description="No precision data yet" />
        </a-card>
      </a-col>
    </a-row>

    <!-- Backtest result -->
    <a-card v-if="lastResult" :title="`${$t('backtest.result')}: ${lastResult.symbol} — ${lastResult.indicator}`" class="result-card" style="margin-top: 16px;">
      <template #extra>
        <a-space>
          <a-button size="small" :loading="aiAnalyzing" @click="handleAiAnalyze">
            <template #icon><RobotOutlined /></template>
            {{ $t('backtest.aiAnalyze') }}
          </a-button>
          <a-tag :color="lastResult.profit >= 0 ? 'success' : 'error'">
            {{ lastResult.profit >= 0 ? '+' : '' }}{{ lastResult.profit.toFixed(2) }}
          </a-tag>
        </a-space>
      </template>

      <a-row :gutter="16">
        <a-col :xs="12" :sm="6">
          <a-statistic
            title="Profit"
            :value="lastResult.profit"
            :precision="2"
            prefix="$"
            :value-style="{ color: lastResult.profit >= 0 ? '#52c41a' : '#ff4d4f' }"
          />
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-statistic
            title="Win Rate"
            :value="lastResult.winRate * 100"
            :precision="1"
            suffix="%"
          />
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-statistic title="Total Trades" :value="lastResult.totalTrades" />
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-statistic
            title="Max Drawdown"
            :value="lastResult.maxDrawdown * 100"
            :precision="2"
            suffix="%"
            :value-style="{ color: '#ff4d4f' }"
          />
        </a-col>
      </a-row>

      <a-divider />

      <a-descriptions :column="{ xs: 1, sm: 2, md: 3 }" size="small">
        <a-descriptions-item label="Initial Capital">${{ lastResult.initialCapital.toLocaleString() }}</a-descriptions-item>
        <a-descriptions-item label="Final Capital">${{ lastResult.finalCapital?.toFixed(2) ?? 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Profit %">{{ lastResult.profitPercent?.toFixed(2) ?? 'N/A' }}%</a-descriptions-item>
        <a-descriptions-item label="Sharpe Ratio">{{ lastResult.sharpeRatio?.toFixed(2) ?? 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Profit Factor">{{ lastResult.profitFactor?.toFixed(2) ?? 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Start Date">{{ lastResult.startDate }}</a-descriptions-item>
        <a-descriptions-item label="End Date">{{ lastResult.endDate }}</a-descriptions-item>
        <a-descriptions-item label="Created">{{ lastResult.createdAt ? new Date(lastResult.createdAt).toLocaleString() : 'N/A' }}</a-descriptions-item>
      </a-descriptions>

      <!-- AI Analysis result -->
      <a-divider v-if="aiResult">AI Analysis</a-divider>
      <a-alert v-if="aiResult" type="info" show-icon>
        <template #message>Analysis</template>
        <template #description>
          <pre style="white-space: pre-wrap; margin: 0; font-size: 13px;">{{ aiResult }}</pre>
        </template>
      </a-alert>
    </a-card>

    <!-- History -->
    <a-card :title="$t('backtest.history')" class="history-card" style="margin-top: 16px;">
      <a-table
        :columns="historyColumns"
        :data-source="history"
        :loading="historyLoading"
        :pagination="{ pageSize: 10, showSizeChanger: true, showTotal: (total: number) => `Total ${total} runs` }"
        row-key="id"
        size="small"
        :scroll="{ x: 700 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'profit'">
            <span :style="{ color: (record.profit ?? 0) >= 0 ? '#52c41a' : '#ff4d4f', fontWeight: 600 }">
              {{ (record.profit ?? 0) >= 0 ? '+' : '' }}${{ (record.profit ?? 0).toFixed(2) }}
            </span>
          </template>
          <template v-else-if="column.key === 'winRate'">
            {{ ((record.winRate ?? 0) * 100).toFixed(1) }}%
          </template>
          <template v-else-if="column.key === 'createdAt'">
            {{ record.createdAt ? new Date(record.createdAt).toLocaleString() : '—' }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" size="small" @click="selectResult(record)">View</a-button>
              <a-button type="link" size="small" danger :loading="aiAnalyzing" @click="handleAiAnalyzeOne(record)">
                AI
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined, RobotOutlined } from '@ant-design/icons-vue'
import { backtestApi, type BacktestResult, type PrecisionInfo } from '@/api/backtest'
import { useIndicatorsStore } from '@/stores/indicators'

const indicatorsStore = useIndicatorsStore()

const running = ref(false)
const historyLoading = ref(false)
const refreshingPrecision = ref(false)
const aiAnalyzing = ref(false)
const lastResult = ref<BacktestResult | null>(null)
const aiResult = ref<string>('')
const history = ref<BacktestResult[]>([])
const precisionInfo = ref<PrecisionInfo[]>([])

const form = reactive({
  indicator: '',
  symbol: '',
  exchange: 'binance',
  startDate: '',
  endDate: '',
  initialCapital: 10000,
})

const historyColumns = [
  { title: 'Indicator', dataIndex: 'indicator', key: 'indicator', fixed: 'left' as const },
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Profit', key: 'profit', width: 110 },
  { title: 'Win Rate', key: 'winRate', width: 90 },
  { title: 'Trades', dataIndex: 'totalTrades', key: 'totalTrades', width: 80 },
  { title: 'Max DD', key: 'maxDrawdown', width: 90, customRender: ({ record }: { record: BacktestResult }) => `${((record.maxDrawdown ?? 0) * 100).toFixed(1)}%` },
  { title: 'Created', key: 'createdAt', width: 170 },
  { title: 'Actions', key: 'actions', width: 110, fixed: 'right' as const },
]

const precisionColumns = [
  { title: 'Indicator', dataIndex: 'indicator', key: 'indicator' },
  { title: 'Avg Diff', key: 'avgDiff', width: 120 },
  { title: 'Hit Rate', key: 'hitRate', width: 180 },
  { title: 'Sample Size', key: 'sampleSize', width: 110 },
]

async function loadHistory() {
  historyLoading.value = true
  try {
    const res = await backtestApi.getHistory({ pageSize: 50 })
    history.value = res.data.data?.items ?? []
  } catch {
    message.error('Failed to load history')
  } finally {
    historyLoading.value = false
  }
}

async function loadPrecisionInfo() {
  refreshingPrecision.value = true
  try {
    const res = await backtestApi.getPrecisionInfo()
    precisionInfo.value = res.data.data?.data ?? []
  } catch {
    message.error('Failed to load precision info')
  } finally {
    refreshingPrecision.value = false
  }
}

async function handleRunBacktest() {
  if (!form.indicator) { message.warning('Please select an indicator'); return }
  if (!form.symbol) { message.warning('Please enter a symbol'); return }
  if (!form.startDate) { message.warning('Please select start date'); return }
  if (!form.endDate) { message.warning('Please select end date'); return }

  running.value = true
  aiResult.value = ''
  try {
    const res = await backtestApi.runBacktest({
      indicator: form.indicator,
      symbol: form.symbol,
      exchange: form.exchange,
      startDate: form.startDate,
      endDate: form.endDate,
      initialCapital: form.initialCapital,
    })
    lastResult.value = res.data.data?.data ?? null
    message.success('Backtest completed')
    loadHistory()
  } catch (e: any) {
    message.error(e.message || 'Backtest failed')
  } finally {
    running.value = false
  }
}

function selectResult(record: BacktestResult) {
  lastResult.value = record
  aiResult.value = ''
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
}

async function handleAiAnalyze() {
  if (!lastResult.value?.id) { message.warning('Run a backtest first'); return }
  aiAnalyzing.value = true
  aiResult.value = ''
  try {
    const res = await backtestApi.aiAnalyze(lastResult.value.id)
    aiResult.value = res.data.data?.analysis ?? ''
    if (!aiResult.value) message.warning('No analysis returned')
  } catch (e: any) {
    message.error(e.message || 'AI analysis failed')
  } finally {
    aiAnalyzing.value = false
  }
}

async function handleAiAnalyzeOne(record: BacktestResult) {
  if (!record.id) return
  aiAnalyzing.value = true
  aiResult.value = ''
  lastResult.value = record
  try {
    const res = await backtestApi.aiAnalyze(record.id)
    aiResult.value = res.data.data?.analysis ?? ''
  } catch (e: any) {
    message.error(e.message || 'AI analysis failed')
  } finally {
    aiAnalyzing.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    indicatorsStore.indicators.length === 0 ? indicatorsStore.fetchIndicators() : Promise.resolve(),
    loadHistory(),
    loadPrecisionInfo(),
  ])
})
</script>

<style scoped>
.backtest-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
}

:deep(.ant-card) {
  border-radius: 8px;
}

:deep(.ant-table) {
  border-radius: 8px;
}
</style>
