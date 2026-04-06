<template>
  <a-layout-sider
    v-model:collapsed="collapsed"
    :trigger="null"
    collapsible
    :width="220"
    :collapsed-width="64"
    class="app-sidebar"
  >
    <!-- Logo -->
    <div class="logo" @click="$router.push('/dashboard')">
      <img v-if="!collapsed" src="/logo.png" alt="QuantDinger" height="32" />
      <span v-if="!collapsed" class="logo-text">QuantDinger</span>
      <span v-else class="logo-collapsed">QD</span>
    </div>

    <!-- Navigation menu -->
    <a-menu
      v-model:selectedKeys="selectedKeys"
      mode="inline"
      theme="dark"
      :inline-collapsed="collapsed"
      @click="handleMenuClick"
    >
      <a-menu-item key="/dashboard">
        <template #icon><DashboardOutlined /></template>
        {{ $t('nav.dashboard') }}
      </a-menu-item>

      <a-menu-item key="/portfolio">
        <template #icon><FundOutlined /></template>
        {{ $t('nav.portfolio') }}
      </a-menu-item>

      <a-menu-item key="/strategies">
        <template #icon><BarChartOutlined /></template>
        {{ $t('nav.strategies') }}
      </a-menu-item>

      <a-menu-item key="/quick-trade">
        <template #icon><ThunderboltOutlined /></template>
        {{ $t('nav.quickTrade') }}
      </a-menu-item>

      <a-menu-divider />

      <a-menu-item key="/market">
        <template #icon><GlobalOutlined /></template>
        {{ $t('nav.market') }}
      </a-menu-item>

      <a-sub-menu key="ai">
        <template #icon><RobotOutlined /></template>
        <template #title>{{ $t('nav.aiAnalysis') }}</template>
        <a-menu-item key="/ai-analysis">{{ $t('aiAnalysis.multiAgent') }}</a-menu-item>
        <a-menu-item key="/indicators">{{ $t('nav.indicators') }}</a-menu-item>
        <a-menu-item key="/backtest">{{ $t('nav.backtest') }}</a-menu-item>
      </a-sub-menu>

      <a-menu-item key="/polymarket">
        <template #icon><FundOutlined /></template>
        {{ $t('nav.polymarket') }}
      </a-menu-item>

      <a-menu-divider />

      <a-menu-item key="/settings">
        <template #icon><SettingOutlined /></template>
        {{ $t('nav.settings') }}
      </a-menu-item>

      <a-menu-item key="/billing">
        <template #icon><CreditCardOutlined /></template>
        {{ $t('nav.billing') }}
      </a-menu-item>

      <a-menu-item key="/community">
        <template #icon><TeamOutlined /></template>
        {{ $t('nav.community') }}
      </a-menu-item>

      <!-- Admin section -->
      <a-menu-divider v-if="isAdmin" />
      <a-sub-menu v-if="isAdmin" key="admin">
        <template #icon><UserOutlined /></template>
        <template #title>{{ $t('nav.admin') }}</template>
        <a-menu-item key="/admin/users">{{ $t('nav.userManagement') }}</a-menu-item>
        <a-menu-item key="/admin/system-health">System Health</a-menu-item>
      </a-sub-menu>

      <!-- Trading platforms -->
      <a-menu-divider />
      <a-sub-menu key="trading">
        <template #icon><LockOutlined /></template>
        <template #title>{{ $t('nav.trading') }}</template>
        <a-menu-item key="/trading/ibkr">{{ $t('nav.ibkr') }}</a-menu-item>
        <a-menu-item key="/trading/mt5">{{ $t('nav.mt5') }}</a-menu-item>
      </a-sub-menu>
    </a-menu>
  </a-layout-sider>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DashboardOutlined,
  GlobalOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  TeamOutlined,
  CreditCardOutlined,
  RobotOutlined,
  BarChartOutlined,
  ExperimentOutlined,
  FundOutlined,
  UserOutlined,
  LockOutlined,
} from '@ant-design/icons-vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ collapsed: boolean }>()
const emit = defineEmits<{ 'update:collapsed': [boolean] }>()

const appStore = useAppStore()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const collapsed = ref(props.collapsed)
const selectedKeys = ref<string[]>([route.path])

const isAdmin = computed(() => authStore.user?.role?.id === 'admin')

watch(
  () => props.collapsed,
  (v) => { collapsed.value = v }
)

watch(
  () => route.path,
  (path) => { selectedKeys.value = [path] }
)

watch(collapsed, (v) => {
  appStore.sidebarCollapsed = v
  emit('update:collapsed', v)
})

function handleMenuClick({ key }: { key: string }) {
  router.push(key)
}
</script>

<style scoped>
.app-sidebar {
  background: #001529 !important;
  overflow-y: auto;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
}

.logo {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  margin-left: 8px;
  white-space: nowrap;
}

.logo-collapsed {
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}
</style>
