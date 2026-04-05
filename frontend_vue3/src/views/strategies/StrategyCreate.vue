<template>
  <div class="strategy-create-page">
    <div class="page-header">
      <h1>{{ isEdit ? $t('strategy.editStrategy') : $t('strategy.createStrategy') }}</h1>
      <a-button @click="$router.back()">{{ $t('common.back') }}</a-button>
    </div>

    <a-spin :spinning="loading">
      <a-form layout="vertical" class="strategy-form" :model="form">
        <!-- Basic info -->
        <a-card :title="$t('strategy.strategyName')" class="form-section">
          <a-form-item :label="$t('strategy.strategyName')" required>
            <a-input v-model:value="form.name" :placeholder="$t('strategy.strategyName')" />
          </a-form-item>
        </a-card>

        <!-- Exchange & Symbol -->
        <a-card :title="$t('strategy.exchange') + ' / ' + $t('strategy.symbol')" class="form-section">
          <a-form-item :label="$t('strategy.exchange')" required>
            <a-select v-model:value="form.exchange" @change="onExchangeChange">
              <a-select-option value="binance">Binance</a-select-option>
              <a-select-option value="okx">OKX</a-select-option>
              <a-select-option value="coinbase">Coinbase</a-select-option>
              <a-select-option value="alpaca">Alpaca</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item :label="$t('strategy.selectSymbol')" required>
            <a-select
              v-model:value="form.symbol"
              show-search
              :disabled="!form.exchange"
              :placeholder="form.exchange ? $t('strategy.selectSymbol') : 'Select exchange first'"
              @focus="loadSymbols"
            >
              <a-select-option v-for="sym in symbols" :key="sym" :value="sym">{{ sym }}</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item :label="$t('strategy.selectMarketType')" required>
            <a-select v-model:value="form.marketType">
              <a-select-option value="spot">{{ $t('portfolio.spot') }}</a-select-option>
              <a-select-option value="margin">{{ $t('portfolio.margin') }}</a-select-option>
              <a-select-option value="futures">{{ $t('portfolio.futures') }}</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="Virtual Position Mode">
            <a-switch v-model:checked="form.virtual" />
            <span style="margin-left: 8px; color: var(--color-text-secondary)">Simulate trades without real orders</span>
          </a-form-item>
        </a-card>

        <!-- Indicators -->
        <a-card :title="$t('strategy.indicators')" class="form-section">
          <div v-for="(ind, idx) in form.indicators" :key="idx" class="indicator-row">
            <a-select v-model:value="ind.name" placeholder="Indicator" style="width: 200px">
              <a-select-option value="RSI">RSI</a-select-option>
              <a-select-option value="MACD">MACD</a-select-option>
              <a-select-option value="SMA">SMA</a-select-option>
              <a-select-option value="EMA">EMA</a-select-option>
              <a-select-option value="BollingerBands">Bollinger Bands</a-select-option>
              <a-select-option value="ATR">ATR</a-select-option>
              <a-select-option value="ADX">ADX</a-select-option>
            </a-select>
            <span v-if="ind.name === 'RSI'" style="margin-left: 8px">
              Period: <a-input-number v-model:value="ind.params.period" :min="1" :max="100" style="width: 80px" />
            </span>
            <a-button type="text" danger @click="removeIndicator(idx)">✕</a-button>
          </div>
          <a-button type="dashed" block @click="addIndicator" style="margin-top: 8px">
            <template #icon><PlusOutlined /></template>
            {{ $t('strategy.addIndicator') }}
          </a-button>
        </a-card>

        <!-- Triggers -->
        <a-card :title="$t('strategy.triggers')" class="form-section">
          <div v-for="(t, idx) in form.triggers" :key="idx" class="trigger-row">
            <a-select v-model:value="t.indicator" placeholder="Indicator" style="width: 160px">
              <a-select-option v-for="ind in form.indicators" :key="ind.name" :value="ind.name">{{ ind.name }}</a-select-option>
            </a-select>
            <a-select v-model:value="t.condition" style="width: 140px; margin-left: 8px">
              <a-select-option value=">">> (above)</a-select-option>
              <a-select-option value="<">< (below)</a-select-option>
              <a-select-option value="crosses_above">crosses above</a-select-option>
              <a-select-option value="crosses_below">crosses below</a-select-option>
            </a-select>
            <a-input-number v-model:value="t.value" style="width: 120px; margin-left: 8px" placeholder="Value" />
            <a-button type="text" danger @click="removeTrigger(idx)">✕</a-button>
          </div>
          <a-button type="dashed" block @click="addTrigger" style="margin-top: 8px">
            <template #icon><PlusOutlined /></template>
            Add Trigger
          </a-button>
        </a-card>

        <!-- Position sizing -->
        <a-card :title="$t('strategy.positionSizing')" class="form-section">
          <a-form-item label="Amount">
            <a-input-number v-model:value="form.amount" :min="0" style="width: 100%" />
          </a-form-item>
          <a-form-item label="Leverage">
            <a-input-number v-model:value="form.leverage" :min="1" :max="125" style="width: 100%" />
          </a-form-item>
        </a-card>

        <!-- Risk control -->
        <a-card :title="$t('strategy.riskControl')" class="form-section">
          <a-form-item :label="$t('strategy.stopLoss')">
            <a-input-number v-model:value="form.stopLoss" :min="0" :max="100" style="width: 100%" />
          </a-form-item>
          <a-form-item :label="$t('strategy.takeProfit')">
            <a-input-number v-model:value="form.takeProfit" :min="0" :max="100" style="width: 100%" />
          </a-form-item>
          <a-form-item :label="$t('strategy.maxPositions')">
            <a-input-number v-model:value="form.maxPositions" :min="1" style="width: 100%" />
          </a-form-item>
        </a-card>

        <!-- Actions -->
        <div class="form-actions">
          <a-button @click="$router.back()">{{ $t('common.cancel') }}</a-button>
          <a-button type="primary" :loading="saving" @click="handleSave">
            {{ $t('common.save') }}
          </a-button>
        </div>
      </a-form>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { useStrategiesStore } from '@/stores/strategies'
import { strategyApi } from '@/api/strategy'

const route = useRoute()
const router = useRouter()
const store = useStrategiesStore()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const loading = ref(false)
const symbols = ref<string[]>([])

const form = reactive({
  name: '',
  exchange: '',
  symbol: '',
  marketType: 'spot',
  virtual: false,
  indicators: [] as { name: string; params: Record<string, number> }[],
  triggers: [] as { indicator: string; condition: string; value: number }[],
  amount: 0,
  leverage: 1,
  stopLoss: 0,
  takeProfit: 0,
  maxPositions: 1,
})

onMounted(async () => {
  if (isEdit.value) {
    loading.value = true
    try {
      const strategy = await store.fetchStrategy(Number(route.params.id))
      if (strategy?.config) {
        const c = strategy.config as Record<string, unknown>
        form.name = (strategy as Record<string, unknown>).name as string || ''
        form.exchange = c.exchange as string || ''
        form.symbol = c.symbol as string || ''
        form.marketType = (c.marketType as string) || 'spot'
        form.virtual = (c.virtual as boolean) || false
        form.indicators = (c.indicators as typeof form.indicators) || []
        form.triggers = (c.triggers as typeof form.triggers) || []
        const ps = (c.positionSizing as Record<string, number>) || {}
        form.amount = ps.amount || 0
        form.leverage = ps.leverage || 1
        const rc = (c.riskControl as Record<string, number>) || {}
        form.stopLoss = rc.stopLoss || 0
        form.takeProfit = rc.takeProfit || 0
        form.maxPositions = rc.maxPositions || 1
      }
    } finally {
      loading.value = false
    }
  }
})

function addIndicator() {
  form.indicators.push({ name: 'RSI', params: { period: 14 } })
}

function removeIndicator(idx: number) {
  form.indicators.splice(idx, 1)
}

function addTrigger() {
  form.triggers.push({ indicator: '', condition: '>', value: 0 })
}

function removeTrigger(idx: number) {
  form.triggers.splice(idx, 1)
}

async function onExchangeChange() {
  form.symbol = ''
  symbols.value = []
}

async function loadSymbols() {
  if (!form.exchange || symbols.value.length > 0) return
  try {
    const res = await strategyApi.getSymbols(form.exchange, form.marketType)
    symbols.value = res.data.data?.data ?? []
  } catch {}
}

async function handleSave() {
  if (!form.name || !form.exchange || !form.symbol) {
    message.error('Please fill in name, exchange, and symbol')
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.name,
      exchange: form.exchange,
      symbol: form.symbol,
      marketType: form.marketType,
      virtual: form.virtual,
      indicators: form.indicators,
      triggers: form.triggers,
      positionSizing: { amount: form.amount, leverage: form.leverage, mode: 'fixed' },
      riskControl: {
        stopLoss: form.stopLoss || undefined,
        takeProfit: form.takeProfit || undefined,
        maxPositions: form.maxPositions || undefined,
      },
    }
    if (isEdit.value) {
      await store.updateStrategy(Number(route.params.id), payload as never)
    } else {
      await store.createStrategy(payload as never)
    }
    message.success('Strategy saved')
    router.push('/strategies')
  } catch (e: unknown) {
    const err = e as { msg?: string }
    message.error(err.msg || 'Failed to save strategy')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.strategy-create-page { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h1 { margin: 0; }
.strategy-form { max-width: 800px; }
.form-section { margin-bottom: 16px; }
.indicator-row, .trigger-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.form-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
</style>