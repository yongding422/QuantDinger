<template>
  <div class="ibkr-page">
    <div class="page-header">
      <h1>{{ $t('trading.ibkr.title') }}</h1>
      <div class="header-actions">
        <a-tag v-if="status?.connected" color="green">
          <template #icon><WifiOutlined /></template>
          {{ $t('trading.ibkr.connected') }}
        </a-tag>
        <a-tag v-else color="default">{{ $t('trading.ibkr.disconnected') }}</a-tag>
        <a-button v-if="!status?.connected" type="primary" @click="handleConnect" :loading="loading">
          {{ $t('trading.ibkr.connect') }}
        </a-button>
        <a-button v-else danger @click="handleDisconnect" :loading="loading">
          {{ $t('trading.ibkr.disconnect') }}
        </a-button>
      </div>
    </div>

    <a-spin :spinning="loading">
      <!-- Account summary -->
      <a-row :gutter="16" v-if="status?.connected" class="summary-row">
        <a-col :xs="12" :sm="6">
          <a-statistic title="Equity" :value="account?.equity ?? 0" prefix="$" :precision="2" />
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-statistic title="Buying Power" :value="account?.buyingPower ?? 0" prefix="$" :precision="2" />
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-statistic title="Cash" :value="account?.cash ?? 0" prefix="$" :precision="2" />
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-statistic title="Positions Value" :value="account?.positionsValue ?? 0" prefix="$" :precision="2" />
        </a-col>
      </a-row>

      <!-- Place order -->
      <a-card v-if="status?.connected" :title="$t('trading.ibkr.placeOrder')" class="ibkr-card">
        <a-form layout="inline" :model="orderForm">
          <a-form-item :label="$t('trading.ibkr.symbol')">
            <a-input v-model:value="orderForm.symbol" placeholder="AAPL" style="width: 100px" />
          </a-form-item>
          <a-form-item label="Action">
            <a-radio-group v-model:value="orderForm.action" button-style="solid">
              <a-radio-button value="BUY">{{ $t('quickTrade.buy') }}</a-radio-button>
              <a-radio-button value="SELL">{{ $t('quickTrade.sell') }}</a-radio-button>
            </a-radio-group>
          </a-form-item>
          <a-form-item :label="$t('trading.ibkr.quantity')">
            <a-input-number v-model:value="orderForm.quantity" :min="1" style="width: 100px" />
          </a-form-item>
          <a-form-item :label="$t('trading.ibkr.orderType')">
            <a-select v-model:value="orderForm.orderType" style="width: 100px">
              <a-select-option value="MKT">Market</a-select-option>
              <a-select-option value="LMT">Limit</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item v-if="orderForm.orderType === 'LMT'" :label="$t('quickTrade.price')">
            <a-input-number v-model:value="orderForm.lmtPrice" :min="0" :precision="2" style="width: 100px" />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="handlePlaceOrder" :loading="placing">
              {{ $t('trading.ibkr.placeOrder') }}
            </a-button>
          </a-form-item>
        </a-form>
      </a-card>

      <!-- Positions -->
      <a-card v-if="status?.connected" :title="$t('trading.ibkr.positions')" class="ibkr-card">
        <a-table
          :columns="positionColumns"
          :data-source="positions"
          :pagination="false"
          row-key="symbol"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'unrealizedPnl'">
              <span :style="{ color: record.unrealizedPnl >= 0 ? '#52c41a' : '#ff4d4f' }">
                {{ record.unrealizedPnl >= 0 ? '+' : '' }}{{ record.unrealizedPnl.toFixed(2) }}
              </span>
            </template>
            <template v-if="column.key === 'avgCost'">
              ${{ record.avgCost.toFixed(2) }}
            </template>
            <template v-if="column.key === 'lastPrice'">
              ${{ record.lastPrice.toFixed(2) }}
            </template>
            <template v-if="column.key === 'marketValue'">
              ${{ record.marketValue.toFixed(2) }}
            </template>
          </template>
        </a-table>
        <a-empty v-if="positions.length === 0" :description="$t('common.noData')" />
      </a-card>

      <!-- Orders -->
      <a-card v-if="status?.connected" :title="$t('trading.ibkr.orders')" class="ibkr-card">
        <a-table
          :columns="orderColumns"
          :data-source="orders"
          :pagination="false"
          row-key="id"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-tag :color="record.action === 'BUY' ? 'green' : 'red'">{{ record.action }}</a-tag>
            </template>
            <template v-if="column.key === 'status'">
              <a-tag :color="orderStatusColor(record.status)">{{ record.status }}</a-tag>
            </template>
            <template v-if="column.key === 'actions'">
              <a-popconfirm
                v-if="record.status === 'Submitted' || record.status === 'Pending'"
                :title="$t('common.confirmDelete')"
                @confirm="handleCancelOrder(record.id)"
              >
                <a-button type="link" danger size="small">{{ $t('trading.ibkr.cancelOrder') }}</a-button>
              </a-popconfirm>
            </template>
          </template>
        </a-table>
        <a-empty v-if="orders.length === 0" :description="$t('common.noData')" />
      </a-card>

      <!-- Quote lookup -->
      <a-card v-if="status?.connected" :title="$t('trading.ibkr.quote')" class="ibkr-card">
        <a-form layout="inline" :model="quoteForm">
          <a-form-item :label="$t('trading.ibkr.symbol')">
            <a-input v-model:value="quoteForm.symbol" placeholder="AAPL" style="width: 100px" />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="handleGetQuote" :loading="quoteLoading">
              {{ $t('trading.ibkr.quote') }}
            </a-button>
          </a-form-item>
        </a-form>
        <a-descriptions v-if="quote" :column="4" size="small" style="margin-top: 16px">
          <a-descriptions-item label="Bid">${{ quote.bid.toFixed(2) }}</a-descriptions-item>
          <a-descriptions-item label="Ask">${{ quote.ask.toFixed(2) }}</a-descriptions-item>
          <a-descriptions-item label="Last">${{ quote.last.toFixed(2) }}</a-descriptions-item>
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
import { ibkrApi, type IBKRStatus, type IBKRAccount, type IBKRPosition, type IBKROrder, type IBKRQuote } from '@/api/ibkr'

const loading = ref(false)
const placing = ref(false)
const quoteLoading = ref(false)

const status = ref<IBKRStatus | null>(null)
const account = ref<IBKRAccount | null>(null)
const positions = ref<IBKRPosition[]>([])
const orders = ref<IBKROrder[]>([])
const quote = ref<IBKRQuote | null>(null)

const orderForm = reactive({
  symbol: '',
  action: 'BUY' as 'BUY' | 'SELL',
  quantity: 1,
  orderType: 'MKT',
  lmtPrice: undefined as number | undefined,
})

const quoteForm = reactive({
  symbol: '',
})

const positionColumns = [
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Description', dataIndex: 'description', key: 'description' },
  { title: 'Exchange', dataIndex: 'exchange', key: 'exchange' },
  { title: 'Qty', dataIndex: 'quantity', key: 'quantity' },
  { title: 'Avg Cost', dataIndex: 'avgCost', key: 'avgCost' },
  { title: 'Last Price', dataIndex: 'lastPrice', key: 'lastPrice' },
  { title: 'Market Value', dataIndex: 'marketValue', key: 'marketValue' },
  { title: 'Unrealized P&L', dataIndex: 'unrealizedPnl', key: 'unrealizedPnl' },
]

const orderColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Action', dataIndex: 'action', key: 'action' },
  { title: 'Type', dataIndex: 'orderType', key: 'orderType' },
  { title: 'Qty', dataIndex: 'quantity', key: 'quantity' },
  { title: 'Lmt Price', dataIndex: 'lmtPrice', key: 'lmtPrice' },
  { title: 'Status', dataIndex: 'status', key: 'status' },
  { title: 'Filled', dataIndex: 'filledQuantity', key: 'filledQuantity' },
  { title: 'Submitted', dataIndex: 'submittedAt', key: 'submittedAt' },
  { title: 'Actions', key: 'actions' },
]

function orderStatusColor(s: string) {
  if (s === 'Filled') return 'green'
  if (s === 'Cancelled' || s === 'Rejected') return 'red'
  if (s === 'Submitted' || s === 'Pending') return 'blue'
  return 'default'
}

async function fetchStatus() {
  loading.value = true
  try {
    const res = await ibkrApi.getStatus()
    status.value = res.data.data
    if (status.value?.connected) {
      await Promise.all([fetchAccount(), fetchPositions(), fetchOrders()])
    }
  } catch {
    message.error('Failed to fetch IBKR status')
  } finally {
    loading.value = false
  }
}

async function fetchAccount() {
  try {
    const res = await ibkrApi.getAccount()
    account.value = res.data.data
  } catch { /* already handled */ }
}

async function fetchPositions() {
  try {
    const res = await ibkrApi.getPositions()
    positions.value = res.data.data
  } catch { /* already handled */ }
}

async function fetchOrders() {
  try {
    const res = await ibkrApi.getOrders()
    orders.value = res.data.data
  } catch { /* already handled */ }
}

async function handleConnect() {
  loading.value = true
  try {
    await ibkrApi.connect()
    message.success('IBKR connected')
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
    await ibkrApi.disconnect()
    message.success('IBKR disconnected')
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
  if (orderForm.quantity < 1) {
    message.warning('Quantity must be at least 1')
    return
  }
  if (orderForm.orderType === 'LMT' && !orderForm.lmtPrice) {
    message.warning('Limit price is required for limit orders')
    return
  }
  placing.value = true
  try {
    await ibkrApi.placeOrder({
      symbol: orderForm.symbol.toUpperCase(),
      action: orderForm.action,
      quantity: orderForm.quantity,
      orderType: orderForm.orderType,
      lmtPrice: orderForm.orderType === 'LMT' ? orderForm.lmtPrice : undefined,
    })
    message.success('Order placed')
    orderForm.symbol = ''
    orderForm.quantity = 1
    orderForm.orderType = 'MKT'
    orderForm.lmtPrice = undefined
    await fetchOrders()
  } catch (e: any) {
    message.error(e?.response?.data?.message || 'Order failed')
  } finally {
    placing.value = false
  }
}

async function handleCancelOrder(orderId: number) {
  try {
    await ibkrApi.cancelOrder(orderId)
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
    const res = await ibkrApi.getQuote(quoteForm.symbol.toUpperCase())
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
.ibkr-page { padding: 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h1 { margin: 0; font-size: 24px; }
.header-actions { display: flex; align-items: center; gap: 12px; }
.summary-row { margin-bottom: 16px; }
.ibkr-card { margin-top: 16px; }
</style>
