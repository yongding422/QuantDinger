<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1>{{ $t('dashboard.title') }}</h1>
      <a-button @click="store.fetchAll()" :loading="store.loading">
        <template #icon><ReloadOutlined /></template>
        {{ $t('common.refresh') }}
      </a-button>
    </div>

    <!-- Summary cards -->
    <a-row :gutter="[16, 16]" class="summary-cards">
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            :title="$t('dashboard.totalBalance')"
            :value="store.summary?.totalBalance ?? 0"
            :precision="2"
            prefix="$"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            :title="$t('dashboard.todayPnl')"
            :value="store.summary?.todayPnl ?? 0"
            :precision="2"
            :value-style="{ color: (store.summary?.todayPnl ?? 0) >= 0 ? '#52c41a' : '#ff4d4f' }"
            prefix="$"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            :title="$t('dashboard.totalPnl')"
            :value="store.summary?.totalPnl ?? 0"
            :precision="2"
            :value-style="{ color: (store.summary?.totalPnl ?? 0) >= 0 ? '#52c41a' : '#ff4d4f' }"
            prefix="$"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            :title="$t('dashboard.runningStrategies')"
            :value="store.summary?.runningStrategies ?? 0"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- Recent trades -->
    <a-card :title="$t('dashboard.recentTrades')" class="section-card">
      <template #extra>
        <router-link to="/portfolio">{{ $t('dashboard.viewAll') }}</router-link>
      </template>
      <a-table
        :columns="tradeColumns"
        :data-source="store.recentTrades"
        :loading="store.loading"
        :pagination="{ pageSize: 5 }"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'side'">
            <a-tag :color="record.side === 'buy' ? 'green' : 'red'">{{ record.side.toUpperCase() }}</a-tag>
          </template>
          <template v-if="column.key === 'pnl'">
            <span v-if="record.pnl !== undefined" :style="{ color: record.pnl >= 0 ? '#52c41a' : '#ff4d4f' }">
              {{ record.pnl >= 0 ? '+' : '' }}{{ record.pnl.toFixed(2) }}
            </span>
            <span v-else>—</span>
          </template>
        </template>
      </a-table>
      <a-empty v-if="!store.loading && store.recentTrades.length === 0" :description="$t('dashboard.noTrades')" />
    </a-card>

    <!-- Pending orders -->
    <a-card :title="$t('dashboard.pendingOrders')" class="section-card">
      <template #extra>
        <router-link to="/quick-trade">{{ $t('dashboard.viewAll') }}</router-link>
      </template>
      <a-table
        :columns="orderColumns"
        :data-source="store.pendingOrders"
        :loading="store.loading"
        :pagination="{ pageSize: 5 }"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'side'">
            <a-tag :color="record.side === 'buy' ? 'green' : 'red'">{{ record.side.toUpperCase() }}</a-tag>
          </template>
          <template v-if="column.key === 'actions'">
            <a-popconfirm :title="$t('common.confirmDelete')" @confirm="cancelOrder(record.id)">
              <a-button type="link" danger size="small">{{ $t('common.cancel') }}</a-button>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
      <a-empty v-if="!store.loading && store.pendingOrders.length === 0" :description="$t('dashboard.noPendingOrders')" />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useDashboardStore } from '@/stores/dashboard'

const store = useDashboardStore()

const tradeColumns = [
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Side', key: 'side' },
  { title: 'Price', dataIndex: 'price', key: 'price' },
  { title: 'Qty', dataIndex: 'quantity', key: 'quantity' },
  { title: 'Time', dataIndex: 'time', key: 'time' },
  { title: 'P&L', key: 'pnl' },
]

const orderColumns = [
  { title: 'Symbol', dataIndex: 'symbol', key: 'symbol' },
  { title: 'Side', key: 'side' },
  { title: 'Type', dataIndex: 'type', key: 'type' },
  { title: 'Price', dataIndex: 'price', key: 'price' },
  { title: 'Qty', dataIndex: 'quantity', key: 'quantity' },
  { title: 'Time', dataIndex: 'time', key: 'time' },
  { title: 'Actions', key: 'actions' },
]

onMounted(() => {
  store.fetchAll()
})

async function cancelOrder(orderId: number) {
  try {
    await store.cancelOrder(orderId)
    message.success('Order cancelled')
  } catch {
    message.error('Failed to cancel order')
  }
}
</script>

<style scoped>
.dashboard-page { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h1 { margin: 0; }
.stat-card { text-align: center; }
.section-card { margin-top: 16px; }
</style>
