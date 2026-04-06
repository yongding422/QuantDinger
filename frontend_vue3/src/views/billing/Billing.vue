<template>
  <div class="billing-page">
    <a-typography-title>{{ $t('billing.title') }}</a-typography-title>

    <!-- Usage stats -->
    <a-row :gutter="16" style="margin-bottom: 24px;">
      <a-col :xs="24" :sm="8">
        <a-card size="small">
          <a-statistic
            title="API Calls This Month"
            :value="usage.apiCallsUsed"
            :suffix="'/ ' + usage.apiCallsLimit"
          >
            <template #formatter="{ value }">
              <a-progress
                :percent="Math.round((usage.apiCallsUsed / usage.apiCallsLimit) * 100)"
                :stroke-color="usage.apiCallsUsed / usage.apiCallsLimit > 0.8 ? '#ff4d4f' : '#1677ff'"
                size="small"
              />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="8">
        <a-card size="small">
          <a-statistic title="Storage Used" :value="usage.storageUsedMb" suffix="MB" />
          <a-progress :percent="Math.round((usage.storageUsedMb / usage.storageLimitMb) * 100)" size="small" style="margin-top: 8px;" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="8">
        <a-card size="small">
          <a-statistic title="Backtests" :value="usage.backtestsRun" :suffix="'/ ' + usage.backtestsLimit" />
          <a-progress :percent="Math.round((usage.backtestsRun / usage.backtestsLimit) * 100)" size="small" style="margin-top: 8px;" />
        </a-card>
      </a-col>
    </a-row>

    <!-- Plans -->
    <a-typography-title level="4">Plans</a-typography-title>
    <a-row :gutter="16" style="margin-bottom: 24px;">
      <a-col :xs="24" :sm="8" v-for="plan in plans" :key="plan.id">
        <a-card
          :class="['plan-card', { 'current-plan': plan.isCurrentPlan }]"
          size="small"
        >
          <div slot="title">
            {{ plan.name }}
            <a-tag v-if="plan.isCurrentPlan" color="blue" style="float: right;">Current</a-tag>
          </div>
          <div class="plan-price">
            <span class="price-amount">${{ plan.price }}</span>
            <span class="price-interval">/{{ plan.interval }}</span>
          </div>
          <a-divider />
          <ul class="plan-features">
            <li v-for="(f, i) in plan.features" :key="i">{{ f }}</li>
          </ul>
          <a-divider />
          <a-button
            type="primary"
            block
            :disabled="plan.isCurrentPlan"
            :loading="subscribing === plan.id"
            @click="handleSubscribe(plan.id)"
          >
            {{ plan.isCurrentPlan ? 'Current Plan' : 'Subscribe' }}
          </a-button>
        </a-card>
      </a-col>
    </a-row>

    <!-- Invoices -->
    <a-typography-title level="4">Invoice History</a-typography-title>
    <a-card size="small">
      <a-table
        :columns="invoiceColumns"
        :data-source="invoices"
        :loading="invoiceLoading"
        :pagination="{ pageSize: 10 }"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'paid' ? 'green' : record.status === 'pending' ? 'orange' : 'red'">
              {{ record.status }}
            </a-tag>
          </template>
          <template v-if="column.key === 'amount'">
            ${{ record.amount.toFixed(2) }}
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { billingApi, type Plan, type Invoice, type UsageStats } from '@/api/billing'

const plans = ref<Plan[]>([])
const usage = ref<UsageStats>({ apiCallsUsed: 0, apiCallsLimit: 1000, storageUsedMb: 0, storageLimitMb: 5000, backtestsRun: 0, backtestsLimit: 50 })
const invoices = ref<Invoice[]>([])
const invoiceLoading = ref(false)
const subscribing = ref<string | null>(null)

const invoiceColumns = [
  { title: 'Date', dataIndex: 'date', key: 'date' },
  { title: 'Description', dataIndex: 'description', key: 'description' },
  { title: 'Amount', key: 'amount' },
  { title: 'Status', key: 'status' },
]

onMounted(async () => {
  try {
    const [plansRes, usageRes] = await Promise.all([
      billingApi.getPlans(),
      billingApi.getUsage(),
    ])
    plans.value = plansRes.data.data?.data ?? []
    const u = usageRes.data.data?.data
    if (u) usage.value = u
  } catch {}
  invoiceLoading.value = true
  try {
    const res = await billingApi.getInvoices()
    invoices.value = res.data.data?.data?.items ?? []
  } finally {
    invoiceLoading.value = false
  }
})

async function handleSubscribe(planId: string) {
  subscribing.value = planId
  try {
    await billingApi.subscribe(planId)
    message.success('Subscription updated')
    const res = await billingApi.getPlans()
    plans.value = res.data.data?.data ?? []
  } catch { message.error('Subscription failed') }
  finally { subscribing.value = null }
}
</script>

<style scoped>
.billing-page { padding: 16px; }
.plan-card { text-align: center; }
.plan-card.current-plan { border-color: #1677ff; }
.plan-price { font-size: 28px; font-weight: bold; }
.price-amount { color: #1677ff; }
.price-interval { font-size: 14px; color: #999; }
.plan-features { list-style: none; padding: 0; text-align: left; }
.plan-features li { padding: 4px 0; }
.plan-features li::before { content: '✓ '; color: #52c41a; margin-right: 8px; }
</style>
