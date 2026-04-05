<template>
  <div class="quick-trade-page">
    <h1>{{ $t('quickTrade.title') }}</h1>

    <a-row :gutter="16">
      <!-- Left: Order form + Balance -->
      <a-col :xs="24" :md="12">
        <!-- Exchange + Symbol selectors -->
        <a-card title="Trade" class="trade-card">
          <a-form layout="vertical" :model="form">
            <a-form-item :label="$t('strategy.exchange')" required>
              <a-select v-model:value="form.exchange" @change="onExchangeChange">
                <a-select-option value="binance">Binance</a-select-option>
                <a-select-option value="okx">OKX</a-select-option>
                <a-select-option value="coinbase">Coinbase</a-select-option>
                <a-select-option value="alpaca">Alpaca</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item :label="$t('strategy.symbol')" required>
              <a-input v-model:value="form.symbol" placeholder="BTC, AAPL, etc." />
            </a-form-item>
            <a-form-item :label="$t('quickTrade.side')" required>
              <a-radio-group v-model:value="form.side" button-style="solid">
                <a-radio-button value="buy" class="buy-btn">{{ $t('quickTrade.buy') }}</a-radio-button>
                <a-radio-button value="sell" class="sell-btn">{{ $t('quickTrade.sell') }}</a-radio-button>
              </a-radio-group>
            </a-form-item>
            <a-form-item :label="$t('quickTrade.amount')" required>
              <a-input-number v-model:value="form.quantity" :min="0" style="width: 100%" />
            </a-form-item>
            <a-form-item label="Order Type">
              <a-radio-group v-model:value="form.type">
                <a-radio value="market">Market</a-radio>
                <a-radio value="limit">Limit</a-radio>
              </a-radio-group>
            </a-form-item>
            <a-form-item v-if="form.type === 'limit'" :label="$t('quickTrade.price')" required>
              <a-input-number v-model:value="form.price" :min="0" style="width: 100%" />
            </a-form-item>
            <a-form-item>
              <a-button
                type="primary"
                block
                size="large"
                :loading="placing"
                :class="form.side === 'buy' ? 'buy-btn' : 'sell-btn'"
                @click="handlePlaceOrder"
              >
                {{ form.side === 'buy' ? $t('quickTrade.buy') : $t('quickTrade.sell') }} {{ form.symbol || '...' }}
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- Balance -->
        <a-card :title="$t('quickTrade.balance')" class="trade-card" style="margin-top: 16px;">
          <a-table
            :columns="balanceColumns"
            :data-source="store.balances"
            :loading="store.loading"
            :pagination="false"
            row-key="asset"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'asset'">
                <strong>{{ record.asset }}</strong>
              </template>
              <template v-if="column.key === 'free'">
                {{ record.free?.toFixed(6) }}
              </template>
              <template v-if="column.key === 'total'">
                {{ record.total?.toFixed(6) }}
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>

      <!-- Right: Position + Order history -->
      <a-col :xs="24" :md="12">
        <!-- Current position -->
        <a-card :title="$t('quickTrade.position')" class="trade-card">
          <template v-if="store.position">
            <a-descriptions :column="1" bordered size="small">
              <a-descriptions-item label="Side">
                <a-tag :color="store.position.side === 'long' ? 'green' : 'red'">
                  {{ store.position.side.toUpperCase() }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="Size">{{ store.position.size }}</a-descriptions-item>
              <a-descriptions-item label="Entry">{{ store.position.entryPrice }}</a-descriptions-item>
              <a-descriptions-item label="Mark">{{ store.position.markPrice }}</a-descriptions-item>
              <a-descriptions-item label="Unrealized P&L">
                <span :style="{ color: (store.position.unrealizedPnl ?? 0) >= 0 ? '#52c41a' : '#ff4d4f' }">
                  {{ (store.position.unrealizedPnl ?? 0) >= 0 ? '+' : '' }}{{ store.position.unrealizedPnl?.toFixed(2) }}
                </span>
              </a-descriptions-item>
            </a-descriptions>
            <a-button type="primary" danger block style="margin-top: 12px" @click="handleClosePosition">
              {{ $t('quickTrade.closePosition') }}
            </a-button>
          </template>
          <a-empty v-else :description="$t('quickTrade.noPosition')" />
        </a-card>

        <!-- Order history -->
        <a-card :title="$t('quickTrade.orderHistory')" class="trade-card" style="margin-top: 16px;">
          <a-table
            :columns="orderColumns"
            :data-source="store.orders"
            :loading="store.loading"
            :pagination="{ pageSize: 10 }"
            row-key="id"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'side'">
                <a-tag :color="record.side === 'buy' ? 'green' : 'red'">{{ record.side.toUpperCase() }}</a-tag>
              </template>
              <template v-if="column.key === 'status'">
                <a-tag :color="record.status === 'filled' ? 'green' : record.status === 'cancelled' ? 'default' : 'orange'">
                  {{ record.status }}
                </a-tag>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useQuickTradeStore } from '@/stores/quickTrade'

const store = useQuickTradeStore()
const placing = ref(false)

const form = reactive({
  exchange: 'binance',
  symbol: '',
  side: 'buy' as 'buy' | 'sell',
  type: 'market' as 'market' | 'limit',
  quantity: 0,
  price: 0,
})

const balanceColumns = [
  { title: 'Asset', key: 'asset' },
  { title: 'Available', key: 'free' },
  { title: 'Total', key: 'total' },
]

const orderColumns = [
  { title: 'Time', dataIndex: 'createdAt', key: 'createdAt', width: 160 },
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Side', key: 'side' },
  { title: 'Type', dataIndex: 'type', key: 'type' },
  { title: 'Price', dataIndex: 'price', key: 'price' },
  { title: 'Qty', dataIndex: 'quantity', key: 'quantity' },
  { title: 'Status', key: 'status' },
]

onMounted(async () => {
  await store.fetchBalance(form.exchange)
  await store.fetchHistory()
})

async function onExchangeChange() {
  await store.fetchBalance(form.exchange)
  if (form.symbol) {
    await store.fetchPosition(form.exchange, form.symbol)
  }
}

async function handlePlaceOrder() {
  if (!form.symbol || !form.quantity) {
    message.error('Please fill in symbol and quantity')
    return
  }
  if (form.type === 'limit' && !form.price) {
    message.error('Please enter a limit price')
    return
  }
  placing.value = true
  try {
    await store.placeOrder({
      exchange: form.exchange,
      symbol: form.symbol.toUpperCase(),
      side: form.side,
      type: form.type,
      quantity: form.quantity,
      price: form.type === 'limit' ? form.price : undefined,
    })
    message.success('Order placed')
    await store.fetchBalance(form.exchange)
    await store.fetchPosition(form.exchange, form.symbol.toUpperCase())
    await store.fetchHistory()
  } catch (e: unknown) {
    const err = e as { msg?: string }
    message.error(err.msg || 'Failed to place order')
  } finally {
    placing.value = false
  }
}

async function handleClosePosition() {
  if (!form.symbol) return
  try {
    await store.closePosition(form.exchange, form.symbol.toUpperCase())
    message.success('Position closed')
    await store.fetchBalance(form.exchange)
  } catch (e: unknown) {
    const err = e as { msg?: string }
    message.error(err.msg || 'Failed to close position')
  }
}
</script>

<style scoped>
.quick-trade-page { padding: 16px; }
h1 { margin-bottom: 16px; }
.trade-card { margin-bottom: 16px; }
.buy-btn { background: #52c41a; border-color: #52c41a; color: #fff; }
.buy-btn:hover { background: #73d13d; border-color: #73d13d; color: #fff; }
.sell-btn { background: #ff4d4f; border-color: #ff4d4f; color: #fff; }
.sell-btn:hover { background: #ff7875; border-color: #ff7875; color: #fff; }
</style>
