<template>
  <div class="system-health-page">
    <div class="page-header">
      <h2>System Health</h2>
      <a-space>
        <a-tag :color="statusColor">{{ health?.status ?? 'unknown' }}</a-tag>
        <a-button type="primary" @click="refresh">
          <template #icon><ReloadOutlined /></template>
          {{ $t('common.refresh') }}
        </a-button>
      </a-space>
    </div>

    <!-- Overview cards -->
    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="6">
        <a-card size="small" title="CPU">
          <a-progress
            :percent="health?.cpuPercent ?? 0"
            :color="cpuColor"
            size="small"
          />
          <div class="stat-label">{{ health?.cpuPercent ?? 0 }}%</div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card size="small" title="Memory">
          <a-progress
            :percent="health?.memoryPercent ?? 0"
            :color="memColor"
            size="small"
          />
          <div class="stat-label">{{ health?.memoryPercent ?? 0 }}%</div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card size="small" title="Disk">
          <a-progress
            :percent="health?.diskPercent ?? 0"
            :color="diskColor"
            size="small"
          />
          <div class="stat-label">{{ health?.diskPercent ?? 0 }}%</div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card size="small" title="Active Connections">
          <a-statistic :value="health?.activeConnections ?? 0" />
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="8">
        <a-card size="small" title="Uptime">
          <a-statistic :value="formatUptime(health?.uptime ?? 0)" />
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card size="small" title="Version">
          <a-statistic :value="health?.version ?? 'N/A'" />
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card size="small" title="API Calls (Total)">
          <a-statistic :value="metrics?.totalApiCalls ?? 0" />
        </a-card>
      </a-col>
    </a-row>

    <!-- Services table -->
    <a-card title="Services" style="margin-bottom: 24px">
      <a-table
        :columns="serviceColumns"
        :data-source="health?.services ?? []"
        :loading="adminStore.healthLoading"
        row-key="name"
        size="small"
        :pagination="false"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-badge
              :status="serviceStatusBadge(record.status)"
              :text="record.status"
            />
          </template>
          <template v-else-if="column.key === 'latencyMs'">
            {{ record.latencyMs !== undefined ? `${record.latencyMs} ms` : '-' }}
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- DAU chart -->
    <a-card title="Daily Active Users (Last 14 Days)">
      <div v-if="dailyActiveUsers.length > 0" class="dau-chart">
        <div
          v-for="item in dailyActiveUsers"
          :key="item.date"
          class="dau-bar-wrapper"
        >
          <div class="dau-bar" :style="{ height: barHeight(item.count) + 'px' }">
            <span class="dau-tooltip">{{ item.count }}</span>
          </div>
          <span class="dau-label">{{ shortDate(item.date) }}</span>
        </div>
      </div>
      <a-empty v-else description="No data available" />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useAdminStore } from '@/stores/admin'

const adminStore = useAdminStore()
const autoRefresh = ref(false)
let refreshInterval: ReturnType<typeof setInterval> | null = null

const health = computed(() => adminStore.systemHealth)
const metrics = computed(() => adminStore.systemMetrics)

const dailyActiveUsers = computed(() => metrics.value?.dailyActiveUsers ?? [])
const maxDau = computed(() => Math.max(...dailyActiveUsers.value.map((d) => d.count), 1))

function barHeight(count: number) {
  return Math.max(4, Math.round((count / maxDau.value) * 120))
}

function shortDate(iso: string) {
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function formatUptime(seconds: number) {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`
  return `${Math.floor(seconds / 86400)}d`
}

const statusColor = computed(() => {
  const s = health.value?.status
  if (s === 'healthy') return 'green'
  if (s === 'degraded') return 'orange'
  return 'red'
})

const cpuColor = computed(() => {
  const p = health.value?.cpuPercent ?? 0
  if (p >= 90) return '#ff4d4f'
  if (p >= 70) return '#faad14'
  return '#52c41a'
})

const memColor = computed(() => {
  const p = health.value?.memoryPercent ?? 0
  if (p >= 90) return '#ff4d4f'
  if (p >= 70) return '#faad14'
  return '#52c41a'
})

const diskColor = computed(() => {
  const p = health.value?.diskPercent ?? 0
  if (p >= 90) return '#ff4d4f'
  if (p >= 70) return '#faad14'
  return '#52c41a'
})

function serviceStatusBadge(status: string) {
  if (status === 'up') return 'success'
  if (status === 'degraded') return 'warning'
  return 'error'
}

const serviceColumns = [
  { title: 'Service', dataIndex: 'name', key: 'name' },
  { title: 'Status', dataIndex: 'status', key: 'status' },
  { title: 'Latency', dataIndex: 'latencyMs', key: 'latencyMs' },
]

async function refresh() {
  await adminStore.fetchSystemHealth()
  await adminStore.fetchSystemMetrics()
}

function toggleAutoRefresh() {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    refreshInterval = setInterval(() => refresh(), 30_000)
  } else if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

onMounted(async () => {
  await refresh()
})
</script>

<style scoped>
.system-health-page {
  padding: 24px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.stat-label {
  text-align: center;
  margin-top: 4px;
  font-size: 12px;
  color: #888;
}
.dau-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 160px;
  padding: 16px 0;
}
.dau-bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.dau-bar {
  width: 100%;
  max-width: 40px;
  background: #1890ff;
  border-radius: 4px 4px 0 0;
  min-height: 4px;
  position: relative;
  cursor: pointer;
  transition: opacity 0.2s;
}
.dau-bar:hover {
  opacity: 0.8;
}
.dau-bar .dau-tooltip {
  display: none;
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: #fff;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
}
.dau-bar:hover .dau-tooltip {
  display: block;
}
.dau-label {
  font-size: 11px;
  color: #888;
}
</style>
