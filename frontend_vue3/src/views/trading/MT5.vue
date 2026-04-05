<template>
  <div class="mt5-page">
    <div class="page-header">
      <h1>{{ $t('trading.mt5.title') }}</h1>
      <div class="header-actions">
        <a-tag v-if="status?.connected" color="green">
          <template #icon><WifiOutlined /></template>
          {{ $t('trading.mt5.connected') }}
        </a-tag>
        <a-tag v-else color="default">{{ $t('trading.mt5.disconnected') }}</a-tag>
        <a-button v-if="!status?.connected" type="primary" @click="handleConnect" :loading="loading">
          {{ $t('trading.mt5.connect') }}
        </a-button>
        <a-button v-else danger @click="handleDisconnect" :loading="loading">
          {{ $t('trading.mt5.disconnect') }}
        </a-button>
      </div>
    </div>

    <a-spin :spinning="loading">
      <!-- Account summary -->
      <a-row :gutter="16" v-if="status?.connected" class="summary-row">
        <a-col :xs="12" :sm="4">
          <a-statistic title="Balance" :value="account?.balance ?? 0" :precision="2" :prefix="account?.currency || '$'" />
        </a-col>
        <a-col :xs="12" :sm="4">
          <a-statistic title="Equity" :value="account?.equity ?? 0" :precision="2" :prefix="account?.currency || '$'" />
        </a-col>
        <a-col :xs="12" :sm="4">
          <a-statistic title="Margin" :value="account?.margin ?? 0" :precision="2" :prefix="account?.currency || '$'" />
        </a-col>
        <a-col :xs="12" :sm="4">
          <a-statistic title="Free Margin" :value="account?.freeMargin ?? 0" :precision="2" :prefix="account?.currency || '$'" />
        </a-col>
        <a-col :xs="12" :sm="4">
          <a-statistic title="Leverage" :value="account?.leverage ?? 0" suffix="x" />
        </a-col>
        <a-col :xs="12" :sm="4">
          <a-statistic :title="$t('portfolio.totalPositions')" :value="positions.length" />
        </a-col>
      </a-row>

      <!-- Place order -->
      <a-card v-if="status?.connected" :title="$t('trading.mt5.placeOrder')" class="mt5-card">
        <a-form layout="inline" :model="orderForm">
          <a-form-item :label="$t('trading.ibkr.symbol')">
            <a-input v-model:value="orderForm.symbol" placeholder="EURUSD" style="width: 120px" />
          </a-form-item>
          <a-form-item label="Action">
            <a-radio-group v-model:value="orderForm.action" button-style="solid">
              <a-radio-button value="buy">{{ $t('quickTrade.buy') }}</a-radio-button>
              <a-radio-button value="sell">{{ $t('quickTrade.sell') }}</a-radio-button>
            </a-radio-group>
          </a-form-item>
          <a-form-item :label="$t('trading.ibkr.quantity')">
            <a-input-number v-model:value="orderForm.volume" :min="0.01" :step="0.01" style="width: 100px" />
          </a-form-item>
          <a-form-item :label="$t('trading.ibkr.orderType')">
            <a-select v-model:value="orderForm.orderType" style="width: 100px">
              <a-select-option value="MARKET">Market</a-select-option>
              <a-select-option value="LIMIT">Limit</a-select-option>
              <a-select-option value="STOP">Stop</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item v-if="orderForm.orderType !== 'MARKET'" :label="$t('quickTrade.price')">
            <a-input-number v-model:value="orderForm.price" :min="0" :precision="5" style="width: 100px" />
          </a-form-item>
          <a-form-item label="SL">
            <a-input-number v-model:value="orderForm.stopLoss" :min="0" :precision="5" style="width: 100px" />
          </a-form-item>
          <a-form-item label="TP">
            <a-input-number v-model:value="orderForm.takeProfit" :min="0" :precision="5" style="width: 100px" />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="handlePlaceOrder" :loading="placing">
              {{ $t('trading.mt5.placeOrder') }}
            </a-button>
          </a-form-item>
        </a-form>
      </a-card>

      <!-- Positions -->
      <a-card v-if="status?.connected" :title="$t('trading.mt5.positions')" class="mt5-card">
        <a-table
          :columns="positionColumns"
          :data-source="positions"
          :pagination="false"
          row-key="ticket"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'type'">
              <a-tag :color="record.type === 'buy' ? 'green' : 'red'">{{ record.type.toUpperCase() }}</a-tag>
            </template>
            <template v-if="column.key === 'profit'">
              <span :style="{ color: record.profit >= 0 ? '#52c41a' : '#ff4d4f' }">
                {{ record.profit >= 0 ? '+' : '' }}{{ record.profit.toFixed(2) }}
              </span>
            </template>
            <template v-if="column.key === 'actions'">
              <a-popconfirm :title="'Close this position?'" @confirm="handleClosePosition(record.ticket)">
                <a-button type="link" danger size="small">{{ $t('trading.mt5.closePosition') }}</a-button>
              </a-popconfirm>
            </template>
          </template>
        </a-table>
        <a-empty v-if="positions.length === 0" :description="$t('common.noData')" />
      </a-card>

      <!-- Pending orders -->
      <a-card v-if="status?.connected" :title="$t('trading.mt5.orders')" class="mt5-card">
        <a-table
          :columns="orderColumns"
          :data-source="orders"
          :pagination="false"
          row-key="ticket"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'type'">
              <a-tag :color="record.type === 'buy' ? 'green' : 'red'">{{ record.type.toUpperCase() }}</a-tag>
            </template>
            <template v-if="column.key === 'status'">
              <a-tag color="blue">{{ record.status }}</a-tag>
            </template>
            <template v-if="column.key === 'actions'">
              <a-popconfirm :title="$t('common.confirmDelete')" @confirm="handleCancelOrder(record.ticket)">
                <a-button type="link" danger size="small">{{ $t('trading.mt5.cancelOrder') }}</a-button>
              </a-popconfirm>
            </template>
          </template>
        </a-table>
        <a-empty v-if="orders.length === 0" :description="$t('common.noData')" />
      </a-card>

      <!-- Symbol watch -->
      <a-card v-if="status?.connected" :title="$t('trading.mt5.symbols')" class="mt5-card">
        <a-form layout="inline" :model="quoteForm">
          <a-form-item :label="$t('trading.ibkr.symbol')">
            <a-input v-model:value="quoteForm.symbol" placeholder="EURUSD" style="width: 120px" />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="handleGetQuote" :loading="quoteLoading">
              {{ $t('trading.mt5.quote') }}
            </a-button>
          </a-form-item>
        </a-form>
        <a-descriptions v-if="quote" :column="4" size="small" style="margin-top: 16px">
          <a-descriptions-item label="Bid">{{ quote.bid.toFixed(quote.digits) }}</a-descriptions-item>
          <a-descriptions-item label="Ask">{{ quote.ask.toFixed(quote.digits) }}</a-descriptions-item>
          <a-descriptions-item label="Last">{{ quote.last.toFixed(quote.digits) }}</a-descriptions-item>
          <a-descriptions-item label="High">{{ quote.high.toFixed(quote.digits) }}</a-descriptions-item>
          <a-descriptions-item label="Low">{{ quote.low.toFixed(quote.digits) }}</a-descriptions-item>
          <a-descriptions-item label="Volume">{{ quote.volume.toLocaleString() }}</a-descriptions-item>
        </a-descriptions>
      </a-card>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { WifiOutlined } from '@ant-design/icons-vue'
import { mt5Api, type MT5Status, type MT5Account, type MT5Position, type MT5Order, type MT5Symbol } from '@/api/mt5'

const loading = ref(false)
const placing = ref(false)
const quoteLoading = ref(false)

const status = ref<MT5Status | null>(null)
const account = ref<MT5Account | null>(null)
const positions = ref<MT5Position[]>([])
const orders = ref<MT5Order[]>([])
const quote = ref<MT5Symbol | null>(null)

const orderForm = reactive({
  symbol: '',
  action: 'buy' as 'buy' | 'sell',
  volume: 0.1,
  orderType: 'MARKET',
  price: undefined as number | undefined,
  stopLoss: undefined as number | undefined,
  takeProfit: undefined as number | undefined,
})

const quoteForm = reactive({
  symbol: '',
})

const positionColumns = [
  { title: 'Ticket', dataIndex: 'ticket', key: 'ticket', width: 80 },
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Type', dataIndex: 'type', key: 'type' },
  { title: 'Volume', dataIndex: 'volume', key: 'volume' },
  { title: 'Open Price', dataIndex: 'openPrice', key: 'openPrice' },
  { title: 'Current', dataIndex: 'currentPrice', key: 'currentPrice' },
  { title: 'SL', dataIndex: 'stopLoss', key: 'stopLoss' },
  { title: 'TP', dataIndex: 'takeProfit', key: 'takeProfit' },
  { title: 'Profit', dataIndex: 'profit', key: 'profit' },
  { title: 'Comment', dataIndex: 'comment', key: 'comment' },
  { title: 'Actions', key: 'actions' },
]

const orderColumns = [
  { title: 'Ticket', dataIndex: 'ticket', key: 'ticket', width: 80 },
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Type', dataIndex: 'type', key: 'type' },
  { title: 'Volume', dataIndex: 'volume', key: 'volume' },
  { title: 'Price', dataIndex: 'price', key: 'price' },
  { title: 'Status', dataIndex: 'status', key: 'status' },
  { title: 'Filling', dataIndex: 'typeFilling', key: 'typeFilling' },
  { title: 'Created', dataIndex: 'createdTime', key: 'createdTime' },
  { title: 'Actions', key: 'actions' },
]

async function fetchStatus() {
  loading.value = true
  try {
    const res = await mt5Api.getStatus()
    status.value = res.data.data
    if (status.value?.connected) {
      await Promise.all([fetchAccount(), fetchPositions(), fetchOrders()])
    }
  } catch {
    message.error('Failed to fetch MT5 status')
  } finally {
    loading.value = false
  }
}

async function fetchAccount() {
  try {
    const res = await mt5Api.getAccount()
    account.value = res.data.data
  } catch { /* already handled */ }
}

async function fetchPositions() {
  try {
    const res = await mt5Api.getPositions()
    positions.value = res.data.data
  } catch { /* already handled */ }
}

async function fetchOrders() {
  try {
    const res = await mt5Api.getOrders()
    orders.value = res.data.data
  } catch { /* already handled */ }
}

async function handleConnect() {
  loading.value = true
  try {
    await mt5Api.connect()
    message.success('MT5 connected')
    await fetchStatus()
  } catch (e: any) {
    message.error(e?.response?.data?.message || 'Connection failed')
  } finally {
    loading.value = false
  }
}

async function handleDisconnect() {
  loading.value = true
  try {
    await mt5Api.disconnect()
    message.success('MT5 disconnected')
    status.value = { connected: false }
    account.value = null
    positions.value = []
    orders.value = []
  } catch (e: any) {
    message.error(e?.response?.data?.message || 'Disconnect failed')
  } finally {
    loading.value = false
  }
}

async function handlePlaceOrder() {
  if (!orderForm.symbol.trim()) {
    message.warning('Please enter a symbol')
    return
  }
  placing.value = true
  try {
    await mt5Api.placeOrder({
      symbol: orderForm.symbol.toUpperCase(),
      action: orderForm.action,
      volume: orderForm.volume,
      orderType: orderForm.orderType,
      price: orderForm.orderType !== 'MARKET' ? orderForm.price : undefined,
      stopLoss: orderForm.stopLoss,
      takeProfit: orderForm.takeProfit,
    })
    message.success('Order placed')
    orderForm.symbol = ''
    orderForm.volume = 0.1
    orderForm.orderType = 'MARKET'
    orderForm.price = undefined
    orderForm.stopLoss = undefined
    orderForm.takeProfit = undefined
    await Promise.all([fetchPositions(), fetchOrders()])
  } catch (e: any) {
    message.error(e?.response?.data?.message || 'Order failed')
  } finally {
    placing.value = false
  }
}

async function handleClosePosition(ticket: number) {
  try {
    await mt5Api.closePosition(ticket)
    message.success('Position closed')
    await fetchPositions()
  } catch (e: any) {
    message.error(e?.response?.data?.message || 'Close failed')
  }
}

async function handleCancelOrder(ticket: number) {
  try {
    await mt5Api.cancelOrder(ticket)
    message.success('Order cancelled')
    await fetchOrders()
  } catch (e: any) {
    message.error(e?.response?.data?.message || 'Cancel failed')
  }
}

async function handleGetQuote() {
  if (!quoteForm.symbol.trim()) {
    message.warning('Please enter a symbol')
    return
  }
  quoteLoading.value = true
  try {
    const res = await mt5Api.getQuote(quoteForm.symbol.toUpperCase())
    quote.value = res.data.data
  } catch (e: any) {
    message.error(e?.response?.data?.message || 'Quote failed')
    quote.value = null
  } finally {
    quoteLoading.value = false
  }
}

onMounted(fetchStatus)
</script>

<style scoped>
.mt5-page { padding: 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h1 { margin: 0; font-size: 24px; }
.header-actions { display: flex; align-items: center; gap: 12px; }
.summary-row { margin-bottom: 16px; }
.mt5-card { margin-top: 16px; }
</style>
