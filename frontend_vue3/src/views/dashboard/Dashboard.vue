<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1>{{ $t('dashboard.title') }}</h1>
    </div>

    <!-- Summary cards -->
    <a-row :gutter="[16, 16]" class="summary-cards">
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            :title="$t('dashboard.totalBalance')"
            :value="summary.totalBalance"
            :precision="2"
            prefix="$"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            :title="$t('dashboard.todayPnl')"
            :value="summary.todayPnl"
            :precision="2"
            :value-style="{ color: summary.todayPnl >= 0 ? '#52c41a' : '#ff4d4f' }"
            prefix="$"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            :title="$t('dashboard.totalPnl')"
            :value="summary.totalPnl"
            :precision="2"
            :value-style="{ color: summary.totalPnl >= 0 ? '#52c41a' : '#ff4d4f' }"
            prefix="$"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            :title="$t('dashboard.runningStrategies')"
            :value="summary.runningStrategies"
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
        :data-source="recentTrades"
        :loading="loading"
        :pagination="false"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'pnl'">
            <span :style="{ color: record.pnl >= 0 ? '#52c41a' : '#ff4d4f' }">
              {{ record.pnl >= 0 ? '+' : '' }}{{ record.pnl?.toFixed(2) }}
            </span>
          </template>
          <template v-if="column.key === 'side'">
            <a-tag :color="record.side === 'buy' ? 'green' : 'red'">
              {{ String(record.side || '').toUpperCase() }}
            </a-tag>
          </template>
        </template>
      </a-table>
      <a-empty v-if="!loading && recentTrades.length === 0" :description="$t('dashboard.noTrades')" />
    </a-card>

    <!-- Pending orders -->
    <a-card :title="$t('dashboard.pendingOrders')" class="section-card">
      <template #extra>
        <router-link to="/quick-trade">{{ $t('dashboard.viewAll') }}</router-link>
      </template>
      <a-table
        :columns="orderColumns"
        :data-source="pendingOrders"
        :loading="loading"
        :pagination="false"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'side'">
            <a-tag :color="record.side === 'buy' ? 'green' : 'red'">
              {{ String(record.side || '').toUpperCase() }}
            </a-tag>
          </template>
        </template>
      </a-table>
      <a-empty v-if="!loading && pendingOrders.length === 0" :description="$t('dashboard.noPendingOrders')" />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import request from '@/api/request'

const { t } = useI18n()
const loading = ref(true)

const summary = ref({
  totalBalance: 0,
  todayPnl: 0,
  totalPnl: 0,
  runningStrategies: 0,
})

const recentTrades = ref<Record<string, unknown>[]>([])
const pendingOrders = ref<Record<string, unknown>[]>([])

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
]

onMounted(async () => {
  try {
    const [summaryRes, tradesRes, ordersRes] = await Promise.all([
      request.get('/dashboard/summary'),
      request.get('/dashboard/recentTrades'),
      request.get('/dashboard/pendingOrders'),
    ])
    summary.value = (summaryRes.data as Record<string, unknown>)?.data?.data || summary.value
    recentTrades.value = ((tradesRes.data as Record<string, unknown>)?.data?.data as Record<string, unknown>[]) || []
    pendingOrders.value = ((ordersRes.data as Record<string, unknown>)?.data?.data as Record<string, unknown>[]) || []
  } catch {
    // Silently fail
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard-page {
  padding: 16px;
}

.page-header h1 {
  margin-bottom: 16px;
}

.stat-card {
  text-align: center;
}

.section-card {
  margin-top: 16px;
}
</style>
