<template>
  <div class="fast-analysis-page">
    <h1>{{ $t('aiAnalysis.fastAnalysis') }}</h1>

    <!-- Analyze form -->
    <a-card class="analysis-card">
      <a-form layout="inline" :model="form">
        <a-form-item :label="$t('aiAnalysis.analyzeSymbol')" required>
          <a-input v-model:value="form.symbol" placeholder="BTC, AAPL, etc." style="width: 160px" />
        </a-form-item>
        <a-form-item label="Exchange">
          <a-select v-model:value="form.exchange" style="width: 140px">
            <a-select-option value="binance">Binance</a-select-option>
            <a-select-option value="okx">OKX</a-select-option>
            <a-select-option value="coinbase">Coinbase</a-select-option>
            <a-select-option value="alpaca">Alpaca</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" :loading="analyzing" @click="handleAnalyze">
            {{ $t('aiAnalysis.analyze') }}
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- Result -->
    <a-card v-if="result" class="result-card">
      <div class="result-header">
        <h2>{{ result.symbol }} Analysis</h2>
        <a-tag :color="confidenceColor">{{ result.confidence }}% confidence</a-tag>
        <a-tag :color="confirmationColor">{{ result.confirmation }} confirmation</a-tag>
      </div>
      <a-divider />
      <p class="analysis-text">{{ result.analysis }}</p>
      <a-descriptions :column="2" bordered size="small" v-if="result.entryPrice">
        <a-descriptions-item label="Entry Price">{{ result.entryPrice }}</a-descriptions-item>
        <a-descriptions-item label="Target Price">{{ result.targetPrice }}</a-descriptions-item>
        <a-descriptions-item label="Stop Loss">{{ result.stopLoss }}</a-descriptions-item>
        <a-descriptions-item label="Recommendation">{{ result.recommendation }}</a-descriptions-item>
      </a-descriptions>
      <a-divider />
      <div v-if="result.factors?.length">
        <strong>Key Factors:</strong>
        <ul>
          <li v-for="(f, i) in result.factors" :key="i">{{ f }}</li>
        </ul>
      </div>
    </a-card>

    <!-- History -->
    <a-card title="Analysis History" class="history-card" style="margin-top: 16px;">
      <a-table
        :columns="historyColumns"
        :data-source="history"
        :loading="historyLoading"
        :pagination="{ pageSize: 10 }"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'confidence'">
            <a-progress :percent="record.confidence" :stroke-color="record.confidence >= 70 ? '#52c41a' : record.confidence >= 40 ? '#faad14' : '#ff4d4f'" size="small" />
          </template>
          <template v-if="column.key === 'confirmation'">
            <a-tag :color="record.confirmation === 'high' ? 'green' : record.confirmation === 'medium' ? 'orange' : 'default'">
              {{ record.confirmation }}
            </a-tag>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { fastAnalysisApi, type FastAnalysisResult } from '@/api/fastAnalysis'

const analyzing = ref(false)
const historyLoading = ref(false)
const result = ref<FastAnalysisResult | null>(null)
const history = ref<FastAnalysisResult[]>([])

const form = ref({ symbol: '', exchange: 'binance' })

const historyColumns = [
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Confidence', key: 'confidence' },
  { title: 'Confirmation', key: 'confirmation' },
  { title: 'Recommendation', dataIndex: 'recommendation', key: 'recommendation' },
  { title: 'Date', dataIndex: 'createdAt', key: 'createdAt' },
]

const confidenceColor = computed(() => {
  const c = result.value?.confidence ?? 50
  if (c >= 70) return 'green'
  if (c >= 40) return 'orange'
  return 'red'
})

const confirmationColor = computed(() => {
  const c = result.value?.confirmation
  if (c === 'high') return 'green'
  if (c === 'medium') return 'orange'
  return 'default'
})

onMounted(async () => {
  historyLoading.value = true
  try {
    const res = await fastAnalysisApi.getAllHistory()
    history.value = res.data.data?.data?.items ?? []
  } finally {
    historyLoading.value = false
  }
})

async function handleAnalyze() {
  if (!form.value.symbol) return
  analyzing.value = true
  try {
    const res = await fastAnalysisApi.analyze({ symbol: form.value.symbol.toUpperCase(), exchange: form.value.exchange })
    result.value = res.data.data?.data ?? null
  } finally {
    analyzing.value = false
  }
}
</script>

<style scoped>
.fast-analysis-page { padding: 16px; }
h1 { margin-bottom: 16px; }
.analysis-card { margin-bottom: 16px; }
.result-card { margin-bottom: 16px; }
.result-header { display: flex; align-items: center; gap: 12px; }
.result-header h2 { margin: 0; }
.analysis-text { line-height: 1.6; margin-bottom: 16px; }
.history-card {}
</style>
