<template>
  <div class="polymarket-page">
    <div class="page-header">
      <h1>{{ $t('polymarket.title') }}</h1>
      <a-space>
        <a-button :loading="loadingMarkets" @click="loadTrending">
          <template #icon><ReloadOutlined /></template>
          {{ $t('common.refresh') }}
        </a-button>
      </a-space>
    </div>

    <a-row :gutter="16">
      <!-- Analyze form -->
      <a-col :xs="24" :lg="12">
        <a-card :title="$t('polymarket.analyze')">
          <a-form layout="vertical" :model="analyzeForm">
            <a-form-item label="Market ID / URL">
              <a-input v-model:value="analyzeForm.marketId" placeholder="polymarket.com/market/..." />
            </a-form-item>
            <a-form-item label="— or — Question">
              <a-input v-model:value="analyzeForm.question" placeholder="Will BTC reach $100k by end of 2025?" />
            </a-form-item>
            <a-form-item label="Current Probability (%)">
              <a-input-number
                v-model:value="analyzeForm.probability"
                :min="0"
                :max="100"
                :precision="1"
                style="width: 100%"
              />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" block :loading="analyzing" @click="handleAnalyze">
                {{ $t('polymarket.analyze') }}
              </a-button>
            </a-form-item>
          </a-form>

          <!-- Analysis result -->
          <a-divider v-if="analysisResult" orientation="left">Analysis Result</a-divider>
          <a-card v-if="analysisResult" size="small" class="analysis-result">
            <a-descriptions :column="1" size="small" bordered>
              <a-descriptions-item label="Question">{{ analysisResult.question }}</a-descriptions-item>
              <a-descriptions-item label="Yes">
                <a-tag color="green">{{ (analysisResult.probabilityYes * 100).toFixed(1) }}%</a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="No">
                <a-tag color="red">{{ (analysisResult.probabilityNo * 100).toFixed(1) }}%</a-tag>
              </a-descriptions-item>
              <a-descriptions-item v-if="analysisResult.recommendation" label="Recommendation">
                <a-tag :color="recommendationColor">{{ analysisResult.recommendation }}</a-tag>
              </a-descriptions-item>
              <a-descriptions-item v-if="analysisResult.riskLevel" label="Risk Level">
                <a-tag :color="riskColor">{{ analysisResult.riskLevel }}</a-tag>
              </a-descriptions-item>
              <a-descriptions-item v-if="analysisResult.reasoning" label="Reasoning">
                {{ analysisResult.reasoning }}
              </a-descriptions-item>
              <a-descriptions-item v-if="analysisResult.volume" label="Volume">
                ${{ analysisResult.volume.toLocaleString() }}
              </a-descriptions-item>
            </a-descriptions>
          </a-card>
        </a-card>
      </a-col>

      <!-- Trending markets -->
      <a-col :xs="24" :lg="12">
        <a-card title="Trending Markets">
          <template #extra>
            <a-tag color="blue">{{ trendingMarkets.length }} markets</a-tag>
          </template>
          <a-table
            :columns="marketColumns"
            :data-source="trendingMarkets"
            :loading="loadingMarkets"
            :pagination="{ pageSize: 10 }"
            row-key="id"
            size="small"
            :scroll="{ x: 500 }"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'question'">
                <a-tooltip :title="record.question">
                  <span class="question-cell">{{ truncate(record.question, 50) }}</span>
                </a-tooltip>
              </template>
              <template v-else-if="column.key === 'probabilityYes'">
                <a-progress
                  :percent="Math.round(record.probabilityYes * 100)"
                  :stroke-color="record.probabilityYes >= 0.5 ? '#52c41a' : '#ff4d4f'"
                  size="small"
                  style="width: 80px"
                />
                <span style="margin-left: 6px">{{ (record.probabilityYes * 100).toFixed(0) }}%</span>
              </template>
              <template v-else-if="column.key === 'volume'">
                {{ formatVolume(record.volume) }}
              </template>
              <template v-else-if="column.key === 'actions'">
                <a-space size="small">
                  <a-button type="primary" size="small" ghost @click="handleAnalyzeMarket(record)">
                    Analyze
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>
          <a-empty v-if="!loadingMarkets && trendingMarkets.length === 0" description="No trending markets" />
        </a-card>
      </a-col>
    </a-row>

    <!-- Analysis History -->
    <a-card :title="$t('polymarket.history')" style="margin-top: 16px;">
      <a-table
        :columns="historyColumns"
        :data-source="analysisHistory"
        :loading="historyLoading"
        :pagination="{ pageSize: 10, showTotal: (total: number) => `Total ${total}` }"
        row-key="id"
        size="small"
        :scroll="{ x: 600 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'question'">
            <a-tooltip :title="record.question">
              <span class="question-cell">{{ truncate(record.question, 60) }}</span>
            </a-tooltip>
          </template>
          <template v-else-if="column.key === 'probabilityYes'">
            <span :style="{ color: record.probabilityYes >= 0.5 ? '#52c41a' : '#ff4d4f', fontWeight: 600 }">
              {{ (record.probabilityYes * 100).toFixed(1) }}%
            </span>
          </template>
          <template v-else-if="column.key === 'recommendation'">
            <a-tag v-if="record.recommendation" :color="record.recommendation === 'YES' ? 'green' : record.recommendation === 'NO' ? 'red' : 'default'">
              {{ record.recommendation }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'createdAt'">
            {{ record.createdAt ? new Date(record.createdAt).toLocaleString() : '—' }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" size="small" @click="viewAnalysis(record)">View</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { polymarketApi, type PolymarketMarket, type PolymarketAnalysis } from '@/api/polymarket'

const loadingMarkets = ref(false)
const analyzing = ref(false)
const historyLoading = ref(false)
const trendingMarkets = ref<PolymarketMarket[]>([])
const analysisHistory = ref<PolymarketAnalysis[]>([])
const analysisResult = ref<PolymarketAnalysis | null>(null)

const analyzeForm = reactive({
  marketId: '',
  question: '',
  probability: 50,
})

const marketColumns = [
  { title: 'Question', key: 'question', width: 220, ellipsis: true },
  { title: 'Yes %', key: 'probabilityYes', width: 140 },
  { title: 'Volume', key: 'volume', width: 100 },
  { title: 'Resolved', key: 'resolved', width: 90, customRender: ({ record }: { record: PolymarketMarket }) => record.resolved ? '✅' : '—' },
  { title: 'Action', key: 'actions', width: 90 },
]

const historyColumns = [
  { title: 'Question', key: 'question', width: 300, ellipsis: true },
  { title: 'Yes %', key: 'probabilityYes', width: 90 },
  { title: 'No %', key: 'probabilityNo', width: 90, customRender: ({ record }: { record: PolymarketAnalysis }) => record.probabilityNo ? `${(record.probabilityNo * 100).toFixed(1)}%` : '—' },
  { title: 'Recommendation', key: 'recommendation', width: 130 },
  { title: 'Risk', key: 'riskLevel', width: 90 },
  { title: 'Date', key: 'createdAt', width: 170 },
  { title: 'Actions', key: 'actions', width: 80, fixed: 'right' as const },
]

const recommendationColor = computed(() => {
  const r = analysisResult.value?.recommendation
  if (r === 'YES') return 'green'
  if (r === 'NO') return 'red'
  return 'default'
})

const riskColor = computed(() => {
  const r = analysisResult.value?.riskLevel?.toUpperCase()
  if (r === 'LOW') return 'green'
  if (r === 'MEDIUM') return 'orange'
  if (r === 'HIGH') return 'red'
  return 'default'
})

function truncate(str: string, len: number) {
  return str.length > len ? str.slice(0, len) + '…' : str
}

function formatVolume(vol?: number) {
  if (!vol) return '—'
  if (vol >= 1_000_000) return `$${(vol / 1_000_000).toFixed(1)}M`
  if (vol >= 1_000) return `$${(vol / 1_000).toFixed(1)}K`
  return `$${vol.toFixed(0)}`
}

async function loadTrending() {
  loadingMarkets.value = true
  try {
    const res = await polymarketApi.getTrendingMarkets(20)
    const data = res.data.data
    trendingMarkets.value = Array.isArray(data?.data) ? data.data : Array.isArray(data) ? data : []
  } catch {
    trendingMarkets.value = []
    message.error('Failed to load trending markets')
  } finally {
    loadingMarkets.value = false
  }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const res = await polymarketApi.getAnalysisHistory({ pageSize: 50 })
    const data = res.data.data
    analysisHistory.value = Array.isArray(data?.items) ? data.items : Array.isArray(data) ? data : []
  } catch {
    analysisHistory.value = []
    message.error('Failed to load history')
  } finally {
    historyLoading.value = false
  }
}

async function handleAnalyze() {
  if (!analyzeForm.marketId && !analyzeForm.question) {
    message.warning('Enter a market ID or question')
    return
  }
  analyzing.value = true
  analysisResult.value = null
  try {
    const res = await polymarketApi.analyzeMarket({
      marketId: analyzeForm.marketId || undefined,
      question: analyzeForm.question || undefined,
      probability: analyzeForm.probability / 100,
    })
    analysisResult.value = res.data.data?.data ?? null
    if (analysisResult.value) {
      loadHistory()
    }
  } catch (e: any) {
    message.error(e.message || 'Analysis failed')
  } finally {
    analyzing.value = false
  }
}

async function handleAnalyzeMarket(record: PolymarketMarket) {
  analyzing.value = true
  analysisResult.value = null
  try {
    const res = await polymarketApi.analyzeMarket({
      marketId: record.id,
      question: record.question,
      probability: record.probabilityYes,
    })
    analysisResult.value = res.data.data?.data ?? null
  } catch (e: any) {
    message.error(e.message || 'Analysis failed')
  } finally {
    analyzing.value = false
  }
}

function viewAnalysis(record: PolymarketAnalysis) {
  analysisResult.value = record
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  Promise.all([loadTrending(), loadHistory()])
})
</script>

<style scoped>
.polymarket-page {
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

.question-cell {
  cursor: default;
}

:deep(.ant-card) {
  border-radius: 8px;
}

:deep(.ant-table) {
  border-radius: 8px;
}

.analysis-result {
  background: #fafafa;
}
</style>
