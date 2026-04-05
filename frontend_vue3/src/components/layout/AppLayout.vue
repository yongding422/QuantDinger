<template>
  <a-layout class="app-layout">
    <!-- Sidebar -->
    <AppSidebar v-model:collapsed="collapsed" />

    <!-- Main content area -->
    <a-layout class="main-layout" :style="{ marginLeft: collapsed ? '64px' : '220px' }">
      <!-- Header -->
      <AppHeader />

      <!-- Page content -->
      <a-layout-content class="main-content">
        <slot />
      </a-layout-content>

      <!-- Footer -->
      <AppFooter />
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import AppFooter from './AppFooter.vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const collapsed = ref(appStore.sidebarCollapsed)

watch(collapsed, (v) => {
  appStore.sidebarCollapsed = v
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.main-layout {
  transition: margin-left 0.2s;
}

.main-content {
  margin: 16px;
  min-height: calc(100vh - 112px);
}
</style>
